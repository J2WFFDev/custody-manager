"""
Custody service - handles custody event logic and validation
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional
from datetime import date

from app.models.custody_event import CustodyEvent, CustodyEventType
from app.models.kit import Kit, KitStatus
from app.models.user import User, UserRole


def checkout_kit_onprem(
    db: Session,
    kit_code: str,
    custodian_name: str,
    initiated_by_user: User,
    custodian_id: Optional[int] = None,
    notes: Optional[str] = None,
    expected_return_date: Optional[date] = None
) -> tuple[CustodyEvent, Kit]:
    """
    Check out a kit on-premises to a custodian.
    
    Implements CUSTODY-001 and QR-002:
    - As a Coach, I want to check out a kit on-premises to an athlete
    - As a Coach, I want to scan a QR code to check out a kit on-premises
    
    Args:
        db: Database session
        kit_code: Kit code (from QR scan or manual entry)
        custodian_name: Name of person receiving custody
        initiated_by_user: User performing the checkout (must be Coach or Armorer)
        custodian_id: Optional user ID if custodian is in system
        notes: Optional notes
        
    Returns:
        Tuple of (custody_event, kit)
        
    Raises:
        HTTPException: If kit not found, already checked out, or user lacks permission
    """
    # Verify permissions - only Coach, Armorer, or Admin can checkout kits
    allowed_roles = [UserRole.coach, UserRole.armorer, UserRole.admin]
    if initiated_by_user.role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail=f"Only {', '.join([r.value for r in allowed_roles])} can check out kits"
        )
    
    # Find kit by code
    kit = db.query(Kit).filter(Kit.code == kit_code).first()
    if not kit:
        raise HTTPException(status_code=404, detail=f"Kit with code '{kit_code}' not found")
    
    # Check kit status - must be available
    if kit.status != KitStatus.available:
        raise HTTPException(
            status_code=400,
            detail=f"Kit is currently {kit.status} and cannot be checked out"
        )
    
    # Create custody event
    custody_event = CustodyEvent(
        event_type=CustodyEventType.checkout_onprem,
        kit_id=kit.id,
        initiated_by_id=initiated_by_user.id,
        initiated_by_name=initiated_by_user.name,
        custodian_id=custodian_id,
        custodian_name=custodian_name,
        notes=notes,
        location_type="on_premises",
        expected_return_date=expected_return_date
    )
    
    # Update kit status
    kit.status = KitStatus.checked_out
    kit.current_custodian_id = custodian_id
    kit.current_custodian_name = custodian_name
    
    # Save to database
    db.add(custody_event)
    db.commit()
    db.refresh(custody_event)
    db.refresh(kit)
    
    return custody_event, kit


def transfer_kit_custody(
    db: Session,
    kit_code: str,
    new_custodian_name: str,
    initiated_by_user: User,
    new_custodian_id: Optional[int] = None,
    notes: Optional[str] = None
) -> tuple[CustodyEvent, Kit, str]:
    """
    Transfer custody of a kit from current custodian to a new custodian.
    
    Implements CUSTODY-005:
    - As a Coach, I want to transfer custody of a kit to another user, so that handoffs are documented.
    
    Args:
        db: Database session
        kit_code: Kit code (from QR scan or manual entry)
        new_custodian_name: Name of person receiving custody
        initiated_by_user: User performing the transfer (must be Coach, Armorer, or Admin)
        new_custodian_id: Optional user ID if new custodian is in system
        notes: Optional notes about the transfer
        
    Returns:
        Tuple of (custody_event, kit, previous_custodian_name)
        
    Raises:
        HTTPException: If kit not found, not checked out, or user lacks permission
    """
    # Verify permissions - only Coach, Armorer, or Admin can transfer kits
    allowed_roles = [UserRole.coach, UserRole.armorer, UserRole.admin]
    if initiated_by_user.role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail=f"Only {', '.join(allowed_roles)} can transfer kit custody"
            detail=f"Only {', '.join([r.value for r in allowed_roles])} can transfer kit custody"
        )
    
    # Find kit by code
    kit = db.query(Kit).filter(Kit.code == kit_code).first()
    if not kit:
        raise HTTPException(status_code=404, detail=f"Kit with code '{kit_code}' not found")
    
    # Check kit status - must be checked out to be transferred
    if kit.status != KitStatus.checked_out:
        raise HTTPException(
            status_code=400,
            detail=f"Kit must be checked out to transfer custody. Current status: {kit.status}"
        )
    
    # Store previous custodian for response
    previous_custodian = kit.current_custodian_name or "Unknown"
    
    # Create custody event
    custody_event = CustodyEvent(
        event_type=CustodyEventType.transfer,
        kit_id=kit.id,
        initiated_by_id=initiated_by_user.id,
        initiated_by_name=initiated_by_user.name,
        custodian_id=new_custodian_id,
        custodian_name=new_custodian_name,
        notes=notes,
        location_type="on_premises"  # Transfer is assumed to be on-premises
    )
    
    # Update kit custodian
    kit.current_custodian_id = new_custodian_id
    kit.current_custodian_name = new_custodian_name
    
    # Save to database
    db.add(custody_event)
    db.commit()
    db.refresh(custody_event)
    db.refresh(kit)
    
    return custody_event, kit, previous_custodian


def report_kit_lost(
    db: Session,
    kit_code: str,
    initiated_by_user: User,
    notes: Optional[str] = None
) -> tuple[CustodyEvent, Kit]:
    """
    Report a kit as lost.
    
    Implements CUSTODY-007:
    - As an Armorer, I want to report a kit as lost, so that everyone knows it's missing
    
    Args:
        db: Database session
        kit_code: Kit code (from QR scan or manual entry)
        initiated_by_user: User reporting the kit as lost (must be Armorer or Admin)
        notes: Optional notes about circumstances
        
    Returns:
        Tuple of (custody_event, kit)
        
    Raises:
        HTTPException: If kit not found, already lost, or user lacks permission
    """
    # Verify permissions - only Armorer or Admin can report kits as lost
    allowed_roles = ["armorer", "admin"]
    if initiated_by_user.role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail=f"Only {', '.join(allowed_roles)} can report kits as lost"
    allowed_roles = [UserRole.armorer, UserRole.admin]
    if initiated_by_user.role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail=f"Only {', '.join([r.value for r in allowed_roles])} can report kits as lost"
        )
    
    # Find kit by code
    kit = db.query(Kit).filter(Kit.code == kit_code).first()
    if not kit:
        raise HTTPException(status_code=404, detail=f"Kit with code '{kit_code}' not found")
    
    # Check kit status - cannot report as lost if already lost
    if kit.status == KitStatus.lost:
        raise HTTPException(
            status_code=400,
            detail=f"Kit is already marked as lost"
        )
    
    # Create custody event
    custody_event = CustodyEvent(
        event_type=CustodyEventType.lost,
        kit_id=kit.id,
        initiated_by_id=initiated_by_user.id,
        initiated_by_name=initiated_by_user.name,
        custodian_id=kit.current_custodian_id,
        custodian_name=kit.current_custodian_name or "Unknown",
        notes=notes,
        location_type="unknown"
    )
    
    # Update kit status
    kit.status = KitStatus.lost
    # Keep custodian info to track who had it last
    
    # Save to database
    db.add(custody_event)
    db.commit()
    db.refresh(custody_event)
    db.refresh(kit)
    
    return custody_event, kit


def report_kit_found(
    db: Session,
    kit_code: str,
    initiated_by_user: User,
    notes: Optional[str] = None
) -> tuple[CustodyEvent, Kit]:
    """
    Report a kit as found (recovered).
    
    Implements CUSTODY-007:
    - As an Armorer, I want to mark a kit as found when it's recovered
    
    Args:
        db: Database session
        kit_code: Kit code (from QR scan or manual entry)
        initiated_by_user: User reporting the kit as found (must be Armorer or Admin)
        notes: Optional notes about recovery circumstances
        
    Returns:
        Tuple of (custody_event, kit)
        
    Raises:
        HTTPException: If kit not found, not currently lost, or user lacks permission
    """
    # Verify permissions - only Armorer or Admin can report kits as found
    allowed_roles = [UserRole.armorer, UserRole.admin]
    if initiated_by_user.role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail=f"Only {', '.join([r.value for r in allowed_roles])} can report kits as found"
        )
    
    # Find kit by code
    kit = db.query(Kit).filter(Kit.code == kit_code).first()
    if not kit:
        raise HTTPException(status_code=404, detail=f"Kit with code '{kit_code}' not found")
    
    # Check kit status - must be lost to mark as found
    if kit.status != KitStatus.lost:
        raise HTTPException(
            status_code=400,
            detail=f"Kit is currently {kit.status} and is not lost"
        )
    
    # Create custody event
    custody_event = CustodyEvent(
        event_type=CustodyEventType.found,
        kit_id=kit.id,
        initiated_by_id=initiated_by_user.id,
        initiated_by_name=initiated_by_user.name,
        custodian_id=None,
        custodian_name="System",
        notes=notes,
        location_type="on_premises"
    )
    
    # Update kit status to available and clear custodian info
    kit.status = KitStatus.available
    kit.current_custodian_id = None
    kit.current_custodian_name = None
    
    # Save to database
    db.add(custody_event)
    db.commit()
    db.refresh(custody_event)
    db.refresh(kit)
    
    return custody_event, kit
