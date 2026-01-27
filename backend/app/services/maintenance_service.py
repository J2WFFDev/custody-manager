"""
Maintenance service - handles maintenance event logic and validation
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional

from app.models.maintenance_event import MaintenanceEvent
from app.models.kit import Kit, KitStatus
from app.models.user import User, UserRole


def open_maintenance(
    db: Session,
    kit_code: str,
    opened_by_user: User,
    notes: Optional[str] = None,
    parts_replaced: Optional[str] = None,
    round_count: Optional[int] = None
) -> tuple[MaintenanceEvent, Kit]:
    """
    Open maintenance on a kit, making it unavailable.
    
    Implements MAINT-001:
    - As an Armorer, I want to log maintenance events (open/close, parts replaced, round count)
    
    Args:
        db: Database session
        kit_code: Kit code to put into maintenance
        opened_by_user: User opening the maintenance (must be Armorer or Admin)
        notes: Optional notes about the maintenance
        parts_replaced: Optional description of parts to be replaced
        round_count: Optional round count at maintenance start
        
    Returns:
        Tuple of (maintenance_event, kit)
        
    Raises:
        HTTPException: If kit not found, already in maintenance, or user lacks permission
    """
    # Verify permissions - only Armorer or Admin can open maintenance
    allowed_roles = [UserRole.armorer, UserRole.admin]
    if opened_by_user.role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail=f"Only {', '.join([r.value for r in allowed_roles])} can open maintenance"
        )
    
    # Get kit by code
    kit = db.query(Kit).filter(Kit.code == kit_code).first()
    if not kit:
        raise HTTPException(status_code=404, detail=f"Kit with code '{kit_code}' not found")
    
    # Check if kit is already in maintenance
    if kit.status == KitStatus.in_maintenance:
        raise HTTPException(
            status_code=400,
            detail=f"Kit '{kit.name}' is already in maintenance"
        )
    
    # Create maintenance event
    maintenance_event = MaintenanceEvent(
        kit_id=kit.id,
        opened_by_id=opened_by_user.id,
        opened_by_name=opened_by_user.name,
        notes=notes,
        parts_replaced=parts_replaced,
        round_count=round_count,
        is_open=1
    )
    
    # Update kit status to in_maintenance
    kit.status = KitStatus.in_maintenance
    
    db.add(maintenance_event)
    db.commit()
    db.refresh(maintenance_event)
    db.refresh(kit)
    
    return maintenance_event, kit


def close_maintenance(
    db: Session,
    kit_code: str,
    closed_by_user: User,
    notes: Optional[str] = None,
    parts_replaced: Optional[str] = None,
    round_count: Optional[int] = None
) -> tuple[MaintenanceEvent, Kit]:
    """
    Close maintenance on a kit, making it available again.
    
    Implements MAINT-001:
    - As an Armorer, I want to log maintenance events (open/close, parts replaced, round count)
    
    Args:
        db: Database session
        kit_code: Kit code to close maintenance on
        closed_by_user: User closing the maintenance (must be Armorer or Admin)
        notes: Optional notes about the maintenance completion
        parts_replaced: Optional description of parts that were replaced
        round_count: Optional round count at maintenance completion
        
    Returns:
        Tuple of (maintenance_event, kit)
        
    Raises:
        HTTPException: If kit not found, not in maintenance, or user lacks permission
    """
    # Verify permissions - only Armorer or Admin can close maintenance
    allowed_roles = [UserRole.armorer, UserRole.admin]
    if closed_by_user.role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail=f"Only {', '.join([r.value for r in allowed_roles])} can close maintenance"
        )
    
    # Get kit by code
    kit = db.query(Kit).filter(Kit.code == kit_code).first()
    if not kit:
        raise HTTPException(status_code=404, detail=f"Kit with code '{kit_code}' not found")
    
    # Check if kit is in maintenance
    if kit.status != KitStatus.in_maintenance:
        raise HTTPException(
            status_code=400,
            detail=f"Kit '{kit.name}' is not in maintenance"
        )
    
    # Find the open maintenance event
    open_event = db.query(MaintenanceEvent).filter(
        MaintenanceEvent.kit_id == kit.id,
        MaintenanceEvent.is_open == 1
    ).first()
    
    if not open_event:
        raise HTTPException(
            status_code=400,
            detail=f"No open maintenance event found for kit '{kit.name}'"
        )
    
    # Update maintenance event with close information
    open_event.closed_by_id = closed_by_user.id
    open_event.closed_by_name = closed_by_user.name
    open_event.is_open = 0
    
    # Update notes, parts_replaced, and round_count if provided
    if notes:
        # Append to existing notes if any
        if open_event.notes:
            open_event.notes = f"{open_event.notes}\n\nClose Notes: {notes}"
        else:
            open_event.notes = notes
    
    if parts_replaced:
        # Append to existing parts_replaced if any
        if open_event.parts_replaced:
            open_event.parts_replaced = f"{open_event.parts_replaced}\n\n{parts_replaced}"
        else:
            open_event.parts_replaced = parts_replaced
    
    if round_count is not None:
        open_event.round_count = round_count
    
    # Update kit status to available
    kit.status = KitStatus.available
    kit.current_custodian_id = None
    kit.current_custodian_name = None
    
    db.commit()
    db.refresh(open_event)
    db.refresh(kit)
    
    return open_event, kit
