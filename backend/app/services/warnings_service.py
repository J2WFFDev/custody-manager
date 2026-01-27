"""
Warnings service - calculates soft warnings for custody events

Implements CUSTODY-008 and CUSTODY-014:
- As an Armorer, I want to see soft warnings (overdue return, extended custody)
- As a Parent, I want to receive soft warnings if a return is overdue
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict, List, Any
from datetime import date, datetime, timedelta

from app.models.kit import Kit, KitStatus
from app.models.custody_event import CustodyEvent, CustodyEventType
from app.constants import EXTENDED_CUSTODY_WARNING_DAYS, OVERDUE_RETURN_WARNING_DAYS


def calculate_kit_warnings(kit: Kit, db: Session) -> Dict[str, Any]:
    """
    Calculate warnings for a checked-out kit.
    
    Returns dictionary with warning information:
    {
        "has_warning": bool,
        "overdue_return": bool,
        "extended_custody": bool,
        "days_overdue": int or None,
        "days_checked_out": int or None,
        "expected_return_date": date or None,
        "checkout_date": datetime or None
    }
    """
    warnings = {
        "has_warning": False,
        "overdue_return": False,
        "extended_custody": False,
        "days_overdue": None,
        "days_checked_out": None,
        "expected_return_date": None,
        "checkout_date": None
    }
    
    # Only check warnings for checked-out kits
    if kit.status != KitStatus.checked_out:
        return warnings
    
    # Get the most recent checkout event for this kit
    latest_checkout = db.query(CustodyEvent).filter(
        CustodyEvent.kit_id == kit.id,
        CustodyEvent.event_type.in_([
            CustodyEventType.checkout_onprem,
            CustodyEventType.checkout_offsite
        ])
    ).order_by(CustodyEvent.created_at.desc()).first()
    
    if not latest_checkout:
        return warnings
    
    # Store checkout date
    warnings["checkout_date"] = latest_checkout.created_at
    
    # Calculate days checked out
    today = date.today()
    checkout_date = latest_checkout.created_at.date()
    days_checked_out = (today - checkout_date).days
    warnings["days_checked_out"] = days_checked_out
    
    # Check for overdue return
    if latest_checkout.expected_return_date:
        warnings["expected_return_date"] = latest_checkout.expected_return_date
        
        if today > latest_checkout.expected_return_date:
            # Kit is overdue
            days_overdue = (today - latest_checkout.expected_return_date).days
            if days_overdue >= OVERDUE_RETURN_WARNING_DAYS:
                warnings["overdue_return"] = True
                warnings["days_overdue"] = days_overdue
                warnings["has_warning"] = True
    
    # Check for extended custody (no expected return date or has been out too long)
    if days_checked_out >= EXTENDED_CUSTODY_WARNING_DAYS:
        warnings["extended_custody"] = True
        warnings["has_warning"] = True
    
    return warnings


def get_all_kits_with_warnings(db: Session) -> List[Dict[str, Any]]:
    """
    Get all kits that have warnings.
    
    Returns list of dictionaries with kit info and warnings:
    [
        {
            "kit_id": int,
            "kit_code": str,
            "kit_name": str,
            "custodian_name": str,
            "warnings": {...}  # Output from calculate_kit_warnings
        }
    ]
    """
    kits_with_warnings = []
    
    # Get all checked-out kits
    checked_out_kits = db.query(Kit).filter(
        Kit.status == KitStatus.checked_out
    ).all()
    
    for kit in checked_out_kits:
        warnings = calculate_kit_warnings(kit, db)
        
        if warnings["has_warning"]:
            kits_with_warnings.append({
                "kit_id": kit.id,
                "kit_code": kit.code,
                "kit_name": kit.name,
                "custodian_name": kit.current_custodian_name,
                "warnings": warnings
            })
    
    return kits_with_warnings
