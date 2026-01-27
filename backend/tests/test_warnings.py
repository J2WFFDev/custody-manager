"""
Tests for the warnings service - soft warnings for custody events

Implements tests for CUSTODY-008 and CUSTODY-014:
- Test overdue return warnings
- Test extended custody warnings
- Verify warnings are non-blocking
"""

import pytest
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session

from app.models.kit import Kit, KitStatus
from app.models.custody_event import CustodyEvent, CustodyEventType
from app.models.user import User, UserRole
from app.services.warnings_service import calculate_kit_warnings, get_all_kits_with_warnings
from app.constants import EXTENDED_CUSTODY_WARNING_DAYS, OVERDUE_RETURN_WARNING_DAYS


def test_no_warnings_for_available_kit(db_session: Session):
    """Test that available kits have no warnings"""
    # Create a kit that's available
    kit = Kit(
        code="TEST-001",
        name="Test Kit",
        status=KitStatus.available
    )
    db_session.add(kit)
    db_session.commit()
    
    # Calculate warnings
    warnings = calculate_kit_warnings(kit, db_session)
    
    # Should have no warnings
    assert warnings["has_warning"] is False
    assert warnings["overdue_return"] is False
    assert warnings["extended_custody"] is False


def test_overdue_return_warning(db_session: Session):
    """Test that overdue returns trigger warnings"""
    # Create a user
    user = User(
        email="test@example.com",
        name="Test User",
        oauth_provider="google",
        oauth_id="test-123",
        role=UserRole.coach
    )
    db_session.add(user)
    db_session.commit()
    
    # Create a kit
    kit = Kit(
        code="TEST-002",
        name="Test Kit Overdue",
        status=KitStatus.checked_out,
        current_custodian_name="John Doe"
    )
    db_session.add(kit)
    db_session.commit()
    
    # Create a custody event with expected return date in the past
    past_date = date.today() - timedelta(days=5)
    checkout_event = CustodyEvent(
        event_type=CustodyEventType.checkout_onprem,
        kit_id=kit.id,
        initiated_by_id=user.id,
        initiated_by_name=user.name,
        custodian_name="John Doe",
        location_type="on_premises",
        expected_return_date=past_date
    )
    db_session.add(checkout_event)
    db_session.commit()
    
    # Calculate warnings
    warnings = calculate_kit_warnings(kit, db_session)
    
    # Should have overdue warning
    assert warnings["has_warning"] is True
    assert warnings["overdue_return"] is True
    assert warnings["days_overdue"] == 5
    assert warnings["expected_return_date"] == past_date


def test_extended_custody_warning(db_session: Session):
    """Test that extended custody triggers warnings"""
    # Create a user
    user = User(
        email="test@example.com",
        name="Test User",
        oauth_provider="google",
        oauth_id="test-123",
        role=UserRole.coach
    )
    db_session.add(user)
    db_session.commit()
    
    # Create a kit
    kit = Kit(
        code="TEST-003",
        name="Test Kit Extended",
        status=KitStatus.checked_out,
        current_custodian_name="Jane Doe"
    )
    db_session.add(kit)
    db_session.commit()
    
    # Create a custody event from more than EXTENDED_CUSTODY_WARNING_DAYS ago
    # Manipulate created_at by creating the event and then updating it
    checkout_event = CustodyEvent(
        event_type=CustodyEventType.checkout_offsite,
        kit_id=kit.id,
        initiated_by_id=user.id,
        initiated_by_name=user.name,
        custodian_name="Jane Doe",
        location_type="off_site"
    )
    db_session.add(checkout_event)
    db_session.flush()
    
    # Update created_at to simulate old checkout
    old_date = datetime.now() - timedelta(days=EXTENDED_CUSTODY_WARNING_DAYS + 1)
    checkout_event.created_at = old_date
    db_session.commit()
    
    # Calculate warnings
    warnings = calculate_kit_warnings(kit, db_session)
    
    # Should have extended custody warning
    assert warnings["has_warning"] is True
    assert warnings["extended_custody"] is True
    assert warnings["days_checked_out"] >= EXTENDED_CUSTODY_WARNING_DAYS


def test_no_warning_for_recent_checkout(db_session: Session):
    """Test that recent checkouts without expected return have no warnings"""
    # Create a user
    user = User(
        email="test@example.com",
        name="Test User",
        oauth_provider="google",
        oauth_id="test-123",
        role=UserRole.coach
    )
    db_session.add(user)
    db_session.commit()
    
    # Create a kit
    kit = Kit(
        code="TEST-004",
        name="Test Kit Recent",
        status=KitStatus.checked_out,
        current_custodian_name="Bob Smith"
    )
    db_session.add(kit)
    db_session.commit()
    
    # Create a recent custody event (today)
    checkout_event = CustodyEvent(
        event_type=CustodyEventType.checkout_onprem,
        kit_id=kit.id,
        initiated_by_id=user.id,
        initiated_by_name=user.name,
        custodian_name="Bob Smith",
        location_type="on_premises"
    )
    db_session.add(checkout_event)
    db_session.commit()
    
    # Calculate warnings
    warnings = calculate_kit_warnings(kit, db_session)
    
    # Should have no warnings (not overdue, not extended yet)
    assert warnings["has_warning"] is False
    assert warnings["overdue_return"] is False
    assert warnings["extended_custody"] is False


def test_get_all_kits_with_warnings(db_session: Session):
    """Test getting all kits with warnings"""
    # Create a user
    user = User(
        email="test@example.com",
        name="Test User",
        oauth_provider="google",
        oauth_id="test-123",
        role=UserRole.coach
    )
    db_session.add(user)
    db_session.commit()
    
    # Create multiple kits
    kit1 = Kit(code="TEST-005", name="Kit 1", status=KitStatus.available)
    kit2 = Kit(code="TEST-006", name="Kit 2 Overdue", status=KitStatus.checked_out, current_custodian_name="Alice")
    kit3 = Kit(code="TEST-007", name="Kit 3 Extended", status=KitStatus.checked_out, current_custodian_name="Bob")
    db_session.add_all([kit1, kit2, kit3])
    db_session.commit()
    
    # Create overdue checkout for kit2
    past_date = date.today() - timedelta(days=3)
    checkout2 = CustodyEvent(
        event_type=CustodyEventType.checkout_onprem,
        kit_id=kit2.id,
        initiated_by_id=user.id,
        initiated_by_name=user.name,
        custodian_name="Alice",
        expected_return_date=past_date
    )
    db_session.add(checkout2)
    
    # Create extended checkout for kit3
    checkout3 = CustodyEvent(
        event_type=CustodyEventType.checkout_offsite,
        kit_id=kit3.id,
        initiated_by_id=user.id,
        initiated_by_name=user.name,
        custodian_name="Bob"
    )
    db_session.add(checkout3)
    db_session.flush()
    
    # Make kit3 checkout old enough for extended warning
    old_date = datetime.now() - timedelta(days=EXTENDED_CUSTODY_WARNING_DAYS + 1)
    checkout3.created_at = old_date
    db_session.commit()
    
    # Get all kits with warnings
    kits_with_warnings = get_all_kits_with_warnings(db_session)
    
    # Should have 2 kits with warnings (kit2 and kit3)
    assert len(kits_with_warnings) == 2
    
    # Verify warning details
    kit_ids_with_warnings = {k["kit_id"] for k in kits_with_warnings}
    assert kit2.id in kit_ids_with_warnings
    assert kit3.id in kit_ids_with_warnings


def test_future_expected_return_no_warning(db_session: Session):
    """Test that future expected return dates don't trigger overdue warnings"""
    # Create a user
    user = User(
        email="test@example.com",
        name="Test User",
        oauth_provider="google",
        oauth_id="test-123",
        role=UserRole.coach
    )
    db_session.add(user)
    db_session.commit()
    
    # Create a kit
    kit = Kit(
        code="TEST-008",
        name="Test Kit Future Return",
        status=KitStatus.checked_out,
        current_custodian_name="Carol"
    )
    db_session.add(kit)
    db_session.commit()
    
    # Create a custody event with expected return date in the future
    future_date = date.today() + timedelta(days=3)
    checkout_event = CustodyEvent(
        event_type=CustodyEventType.checkout_onprem,
        kit_id=kit.id,
        initiated_by_id=user.id,
        initiated_by_name=user.name,
        custodian_name="Carol",
        expected_return_date=future_date
    )
    db_session.add(checkout_event)
    db_session.commit()
    
    # Calculate warnings
    warnings = calculate_kit_warnings(kit, db_session)
    
    # Should not have overdue warning (future date)
    assert warnings["overdue_return"] is False
    assert warnings["expected_return_date"] == future_date
