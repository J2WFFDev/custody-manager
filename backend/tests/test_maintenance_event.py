"""Tests for MaintenanceEvent model"""
import pytest
from datetime import date, datetime
from app.models.maintenance_event import MaintenanceEvent
from app.models.kit import Kit, KitStatus
from app.models.user import User, UserRole


def test_create_maintenance_event(db_session):
    """Test creating a maintenance event (open)"""
    # Create a user first
    user = User(
        email="armorer@example.com",
        name="Test Armorer",
        oauth_provider="google",
        oauth_id="test_oauth_id",
        role=UserRole.armorer
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
    
    # Create a maintenance event (open)
    maintenance_event = MaintenanceEvent(
        kit_id=kit.id,
        opened_by_id=user.id,
        opened_by_name=user.name,
        round_count=1000,
        parts_replaced="Magazine spring, firing pin",
        notes="Routine inspection after 1000 rounds",
        next_maintenance_date=date(2026, 3, 1),
        is_open=1
    )
    db_session.add(maintenance_event)
    db_session.commit()
    
    # Verify the maintenance event was created
    assert maintenance_event.id is not None
    assert maintenance_event.kit_id == kit.id
    assert maintenance_event.opened_by_id == user.id
    assert maintenance_event.opened_by_name == "Test Armorer"
    assert maintenance_event.is_open == 1
    assert maintenance_event.round_count == 1000
    assert maintenance_event.parts_replaced == "Magazine spring, firing pin"
    assert maintenance_event.notes == "Routine inspection after 1000 rounds"
    assert maintenance_event.next_maintenance_date == date(2026, 3, 1)
    assert maintenance_event.created_at is not None
    assert maintenance_event.updated_at is not None


def test_close_maintenance_event(db_session):
    """Test closing a maintenance event"""
    # Create users
    armorer1 = User(
        email="armorer1@example.com",
        name="Armorer One",
        oauth_provider="google",
        oauth_id="armorer1_oauth_id",
        role=UserRole.armorer
    )
    armorer2 = User(
        email="armorer2@example.com",
        name="Armorer Two",
        oauth_provider="google",
        oauth_id="armorer2_oauth_id",
        role=UserRole.armorer
    )
    db_session.add_all([armorer1, armorer2])
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
    
    # Create and open maintenance event
    event = MaintenanceEvent(
        kit_id=kit.id,
        opened_by_id=armorer1.id,
        opened_by_name=armorer1.name,
        notes="Opening for maintenance",
        is_open=1
    )
    db_session.add(event)
    db_session.commit()
    
    # Close the event
    event.closed_by_id = armorer2.id
    event.closed_by_name = armorer2.name
    event.is_open = 0
    event.notes = f"{event.notes}\n\nClosed: Maintenance complete"
    db_session.commit()
    
    # Verify the event was closed
    assert event.is_open == 0
    assert event.closed_by_id == armorer2.id
    assert event.closed_by_name == "Armorer Two"


def test_maintenance_event_optional_fields(db_session):
    """Test maintenance event with minimal fields"""
    # Create a user
    user = User(
        email="armorer@example.com",
        name="Test Armorer",
        oauth_provider="google",
        oauth_id="test_oauth_id",
        role=UserRole.armorer
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
        kit_id=kit.id,
        opened_by_id=user.id,
        opened_by_name=user.name,
        is_open=1
    )
    db_session.add(maintenance_event)
    db_session.commit()
    
    # Verify optional fields are None
    assert maintenance_event.id is not None
    assert maintenance_event.round_count is None
    assert maintenance_event.parts_replaced is None
    assert maintenance_event.notes is None
    assert maintenance_event.next_maintenance_date is None
    assert maintenance_event.closed_by_id is None
    assert maintenance_event.closed_by_name is None
