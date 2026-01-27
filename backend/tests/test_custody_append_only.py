"""
Tests for custody_events append-only model (CUSTODY-015).

This test suite verifies that:
1. Custody events can be created successfully
2. Custody events cannot be updated once created
3. Custody events cannot be deleted
4. All required fields are present in the model
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from app.database import Base
from app.models.custody_event import CustodyEvent, CustodyEventType
from app.models.kit import Kit, KitStatus
from app.models.user import User, UserRole

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_setup():
    """Create tables before each test and drop them after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_setup):
    """Create a database session for testing"""
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing"""
    user = User(
        email="test@example.com",
        name="Test User",
        oauth_provider="google",
        oauth_id="test-123",
        role=UserRole.coach,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_kit(db_session):
    """Create a sample kit for testing"""
    kit = Kit(
        code="TEST-001",
        name="Test Kit",
        description="A kit for testing",
        status=KitStatus.available
    )
    db_session.add(kit)
    db_session.commit()
    db_session.refresh(kit)
    return kit


def test_create_custody_event_success(db_session, sample_kit, sample_user):
    """Test that custody events can be created successfully"""
    event = CustodyEvent(
        event_type=CustodyEventType.checkout_onprem,
        kit_id=sample_kit.id,
        initiated_by_id=sample_user.id,
        initiated_by_name=sample_user.name,
        custodian_id=sample_user.id,
        custodian_name=sample_user.name,
        notes="Test checkout",
        location_type="on_premises"
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    
    assert event.id is not None
    assert event.event_type == CustodyEventType.checkout_onprem
    assert event.kit_id == sample_kit.id
    assert event.initiated_by_id == sample_user.id
    assert event.notes == "Test checkout"


def test_create_custody_event_with_approved_by(db_session, sample_kit, sample_user):
    """Test creating custody event with approved_by field"""
    event = CustodyEvent(
        event_type=CustodyEventType.checkout_offsite,
        kit_id=sample_kit.id,
        initiated_by_id=sample_user.id,
        initiated_by_name=sample_user.name,
        custodian_id=sample_user.id,
        custodian_name=sample_user.name,
        approved_by_id=sample_user.id,
        approved_by_name=sample_user.name,
        notes="Off-site checkout",
        location_type="off_site"
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    
    assert event.approved_by_id == sample_user.id
    assert event.approved_by_name == sample_user.name


def test_create_custody_event_with_attestation(db_session, sample_kit, sample_user):
    """Test creating custody event with attestation fields"""
    from datetime import datetime, timezone
    
    event = CustodyEvent(
        event_type=CustodyEventType.checkout_offsite,
        kit_id=sample_kit.id,
        initiated_by_id=sample_user.id,
        initiated_by_name=sample_user.name,
        custodian_id=sample_user.id,
        custodian_name=sample_user.name,
        attestation_text="I agree to take responsibility...",
        attestation_signature="Test User",
        attestation_timestamp=datetime.now(timezone.utc),
        attestation_ip_address="127.0.0.1",
        notes="Off-site checkout with attestation",
        location_type="off_site"
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    
    assert event.attestation_text == "I agree to take responsibility..."
    assert event.attestation_signature == "Test User"
    assert event.attestation_timestamp is not None
    assert event.attestation_ip_address == "127.0.0.1"


def test_update_custody_event_fails(db_session, sample_kit, sample_user):
    """Test that updating a custody event raises an exception (CUSTODY-015)"""
    event = CustodyEvent(
        event_type=CustodyEventType.checkout_onprem,
        kit_id=sample_kit.id,
        initiated_by_id=sample_user.id,
        initiated_by_name=sample_user.name,
        custodian_id=sample_user.id,
        custodian_name=sample_user.name,
        notes="Original notes",
        location_type="on_premises"
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    
    # Try to update the event - should raise ValueError
    with pytest.raises(ValueError, match="Cannot update custody events"):
        event.notes = "Modified notes"
        db_session.commit()


def test_delete_custody_event_fails(db_session, sample_kit, sample_user):
    """Test that deleting a custody event raises an exception (CUSTODY-015)"""
    event = CustodyEvent(
        event_type=CustodyEventType.checkout_onprem,
        kit_id=sample_kit.id,
        initiated_by_id=sample_user.id,
        initiated_by_name=sample_user.name,
        custodian_id=sample_user.id,
        custodian_name=sample_user.name,
        notes="To be deleted",
        location_type="on_premises"
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    
    # Try to delete the event - should raise ValueError
    with pytest.raises(ValueError, match="Cannot delete custody events"):
        db_session.delete(event)
        db_session.commit()


def test_all_event_types_supported(db_session, sample_kit, sample_user):
    """Test that all custody event types can be created"""
    event_types = [
        CustodyEventType.checkout_onprem,
        CustodyEventType.checkout_offsite,
        CustodyEventType.checkin,
        CustodyEventType.transfer,
        CustodyEventType.lost,
        CustodyEventType.found
    ]
    
    for event_type in event_types:
        event = CustodyEvent(
            event_type=event_type,
            kit_id=sample_kit.id,
            initiated_by_id=sample_user.id,
            initiated_by_name=sample_user.name,
            custodian_id=sample_user.id,
            custodian_name=sample_user.name,
            notes=f"Test {event_type}",
            location_type="on_premises"
        )
        db_session.add(event)
        db_session.commit()
        db_session.refresh(event)
        
        assert event.event_type == event_type
        
        # Clear for next iteration
        db_session.expunge(event)


def test_custody_event_timestamps(db_session, sample_kit, sample_user):
    """Test that created_at and updated_at timestamps are set correctly"""
    event = CustodyEvent(
        event_type=CustodyEventType.checkout_onprem,
        kit_id=sample_kit.id,
        initiated_by_id=sample_user.id,
        initiated_by_name=sample_user.name,
        custodian_id=sample_user.id,
        custodian_name=sample_user.name,
        notes="Test timestamps",
        location_type="on_premises"
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    
    assert event.created_at is not None
    assert event.updated_at is not None
    assert event.created_at == event.updated_at  # Should be same on creation
