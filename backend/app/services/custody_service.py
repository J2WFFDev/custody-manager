"""
Custody service - handles custody event logic and validation
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional

from app.models.custody_event import CustodyEvent, CustodyEventType
from app.models.kit import Kit, KitStatus
from app.models.user import User


def checkout_kit_onprem(
    db: Session,
    kit_code: str,
    custodian_name: str,
    initiated_by_user: User,
    custodian_id: Optional[int] = None,
    notes: Optional[str] = None
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
    allowed_roles = ["coach", "armorer", "admin"]
    if initiated_by_user.role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail=f"Only {', '.join(allowed_roles)} can check out kits"
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
        location_type="on_premises"
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
