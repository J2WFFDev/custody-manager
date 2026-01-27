import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models.kit import Kit, KitStatus
from app.models.user import User, UserRole
from app.models.custody_event import CustodyEvent, CustodyEventType

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_custody.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def db_setup():
    """Create tables before each test and drop them after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_setup):
    """Create a test client"""
    return TestClient(app)

@pytest.fixture
def sample_kit(db_setup):
    """Create a sample kit for testing"""
    db = TestingSessionLocal()
    kit = Kit(
        code="TEST-001",
        name="Test Kit",
        description="A kit for testing",
        status=KitStatus.available
    )
    db.add(kit)
    db.commit()
    db.refresh(kit)
    db.close()
    return kit

@pytest.fixture
def sample_coach(db_setup):
    """Create a sample coach user for testing"""
    db = TestingSessionLocal()
    user = User(
        email="coach@test.com",
        name="Test Coach",
        oauth_provider="google",
        oauth_id="test-coach-123",
        role=UserRole.coach,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

def test_checkout_kit_success(client, sample_kit, sample_coach):
    """Test successful kit checkout"""
    response = client.post(
        "/api/v1/custody/checkout",
        json={
            "kit_code": "TEST-001",
            "custodian_name": "John Athlete",
            "notes": "Practice session"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify response structure
    assert "message" in data
    assert "event" in data
    assert "kit_name" in data
    assert "kit_code" in data
    
    # Verify response content
    assert data["kit_code"] == "TEST-001"
    assert data["kit_name"] == "Test Kit"
    assert "John Athlete" in data["message"]
    
    # Verify event details
    event = data["event"]
    assert event["event_type"] == "checkout_onprem"
    assert event["custodian_name"] == "John Athlete"
    assert event["notes"] == "Practice session"
    assert event["location_type"] == "on_premises"

def test_checkout_kit_not_found(client):
    """Test checkout with non-existent kit code"""
    response = client.post(
        "/api/v1/custody/checkout",
        json={
            "kit_code": "NONEXISTENT",
            "custodian_name": "John Athlete"
        }
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_checkout_kit_already_checked_out(client, sample_kit):
    """Test checkout when kit is already checked out"""
    # First checkout
    client.post(
        "/api/v1/custody/checkout",
        json={
            "kit_code": "TEST-001",
            "custodian_name": "John Athlete"
        }
    )
    
    # Second checkout attempt should fail
    response = client.post(
        "/api/v1/custody/checkout",
        json={
            "kit_code": "TEST-001",
            "custodian_name": "Jane Athlete"
        }
    )
    
    assert response.status_code == 400
    assert "checked_out" in response.json()["detail"]

def test_checkout_creates_event_record(client, sample_kit):
    """Test that checkout creates a custody event record"""
    response = client.post(
        "/api/v1/custody/checkout",
        json={
            "kit_code": "TEST-001",
            "custodian_name": "John Athlete"
        }
    )
    
    assert response.status_code == 201
    
    # Verify event was created in database
    db = TestingSessionLocal()
    event = db.query(CustodyEvent).filter(
        CustodyEvent.kit_id == sample_kit.id
    ).first()
    
    assert event is not None
    assert event.event_type == CustodyEventType.checkout_onprem
    assert event.custodian_name == "John Athlete"
    db.close()

def test_checkout_updates_kit_status(client, sample_kit):
    """Test that checkout updates kit status"""
    response = client.post(
        "/api/v1/custody/checkout",
        json={
            "kit_code": "TEST-001",
            "custodian_name": "John Athlete"
        }
    )
    
    assert response.status_code == 201
    
    # Verify kit status was updated
    db = TestingSessionLocal()
    kit = db.query(Kit).filter(Kit.id == sample_kit.id).first()
    
    assert kit.status == KitStatus.checked_out
    assert kit.current_custodian_name == "John Athlete"
    db.close()
