"""Tests for MaintenanceEvent model"""
import pytest
from datetime import date, datetime
from app.models.maintenance_event import MaintenanceEvent, MaintenanceEventType
from app.models.kit import Kit, KitStatus
from app.models.user import User


def test_create_maintenance_event(db_session):
    """Test creating a maintenance event"""
    # Create a user first
    user = User(
        email="armorer@example.com",
        name="Test Armorer",
        oauth_provider="google",
        oauth_id="test_oauth_id",
        role="armorer"
    )
    db_session.add(user)
    db_session.commit()
    
    # Create a kit
    kit = Kit(
        code="KIT-001",
        name="Test Kit",
        description="A test kit",
        status=KitStatus.in_maintenance
    )
    db_session.add(kit)
    db_session.commit()
    
    # Create a maintenance event
    maintenance_event = MaintenanceEvent(
        event_type=MaintenanceEventType.inspection,
        kit_id=kit.id,
        performed_by_id=user.id,
        performed_by_name=user.name,
        round_count=1000,
        parts_replaced="Magazine spring, firing pin",
        notes="Routine inspection after 1000 rounds",
        next_maintenance_date=date(2026, 3, 1)
    )
    db_session.add(maintenance_event)
    db_session.commit()
    
    # Verify the maintenance event was created
    assert maintenance_event.id is not None
    assert maintenance_event.event_type == MaintenanceEventType.inspection
    assert maintenance_event.kit_id == kit.id
    assert maintenance_event.performed_by_id == user.id
    assert maintenance_event.performed_by_name == "Test Armorer"
    assert maintenance_event.round_count == 1000
    assert maintenance_event.parts_replaced == "Magazine spring, firing pin"
    assert maintenance_event.notes == "Routine inspection after 1000 rounds"
    assert maintenance_event.next_maintenance_date == date(2026, 3, 1)
    assert maintenance_event.created_at is not None
    assert maintenance_event.updated_at is not None


def test_maintenance_event_types(db_session):
    """Test all maintenance event types"""
    # Create a user
    user = User(
        email="armorer@example.com",
        name="Test Armorer",
        oauth_provider="google",
        oauth_id="test_oauth_id",
        role="armorer"
    )
    db_session.add(user)
    db_session.commit()
    
    # Create a kit
    kit = Kit(
        code="KIT-002",
        name="Test Kit 2",
        description="Another test kit",
        status=KitStatus.in_maintenance
    )
    db_session.add(kit)
    db_session.commit()
    
    # Test each event type
    for event_type in MaintenanceEventType:
        event = MaintenanceEvent(
            event_type=event_type,
            kit_id=kit.id,
            performed_by_id=user.id,
            performed_by_name=user.name,
            notes=f"Testing {event_type.value} event type"
        )
        db_session.add(event)
        db_session.commit()
        
        assert event.id is not None
        assert event.event_type == event_type


def test_maintenance_event_optional_fields(db_session):
    """Test maintenance event with minimal fields"""
    # Create a user
    user = User(
        email="armorer@example.com",
        name="Test Armorer",
        oauth_provider="google",
        oauth_id="test_oauth_id",
        role="armorer"
    )
    db_session.add(user)
    db_session.commit()
    
    # Create a kit
    kit = Kit(
        code="KIT-003",
        name="Test Kit 3",
        description="Yet another test kit",
        status=KitStatus.in_maintenance
    )
    db_session.add(kit)
    db_session.commit()
    
    # Create maintenance event with only required fields
    maintenance_event = MaintenanceEvent(
        event_type=MaintenanceEventType.open,
        kit_id=kit.id,
        performed_by_id=user.id,
        performed_by_name=user.name
    )
    db_session.add(maintenance_event)
    db_session.commit()
    
    # Verify optional fields are None
    assert maintenance_event.id is not None
    assert maintenance_event.round_count is None
    assert maintenance_event.parts_replaced is None
    assert maintenance_event.notes is None
    assert maintenance_event.next_maintenance_date is None
