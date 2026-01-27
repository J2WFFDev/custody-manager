import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models.kit import Kit, KitStatus
from app.models.user import User
from app.models.custody_event import CustodyEvent, CustodyEventType

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_transfer_custody.db"

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
def sample_checked_out_kit(db_setup):
    """Create a sample checked out kit for testing"""
    db = TestingSessionLocal()
    kit = Kit(
        code="TEST-TRANSFER-001",
        name="Test Transfer Kit",
        description="A kit for testing transfer",
        status=KitStatus.checked_out,
        current_custodian_name="John Athlete",
        current_custodian_id=None
    )
    db.add(kit)
    db.commit()
    db.refresh(kit)
    db.close()
    return kit

@pytest.fixture
def sample_available_kit(db_setup):
    """Create a sample available kit for testing"""
    db = TestingSessionLocal()
    kit = Kit(
        code="TEST-AVAILABLE-001",
        name="Test Available Kit",
        description="An available kit",
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
        role="coach",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

def test_transfer_kit_success(client, sample_checked_out_kit, sample_coach):
    """Test successful kit custody transfer"""
    response = client.post(
        "/api/v1/custody/transfer",
        json={
            "kit_code": "TEST-TRANSFER-001",
            "new_custodian_name": "Jane Athlete",
            "notes": "Transferring to practice partner"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify response structure
    assert "message" in data
    assert "event" in data
    assert "kit_name" in data
    assert "kit_code" in data
    assert "previous_custodian" in data
    assert "new_custodian" in data
    
    # Verify response content
    assert data["kit_code"] == "TEST-TRANSFER-001"
    assert data["kit_name"] == "Test Transfer Kit"
    assert data["previous_custodian"] == "John Athlete"
    assert data["new_custodian"] == "Jane Athlete"
    assert "John Athlete" in data["message"]
    assert "Jane Athlete" in data["message"]
    
    # Verify event details
    event = data["event"]
    assert event["event_type"] == "transfer"
    assert event["custodian_name"] == "Jane Athlete"
    assert event["notes"] == "Transferring to practice partner"
    assert event["location_type"] == "on_premises"

def test_transfer_kit_not_found(client):
    """Test transfer with non-existent kit code"""
    response = client.post(
        "/api/v1/custody/transfer",
        json={
            "kit_code": "NONEXISTENT",
            "new_custodian_name": "Jane Athlete"
        }
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_transfer_kit_not_checked_out(client, sample_available_kit):
    """Test transfer when kit is not checked out"""
    response = client.post(
        "/api/v1/custody/transfer",
        json={
            "kit_code": "TEST-AVAILABLE-001",
            "new_custodian_name": "Jane Athlete"
        }
    )
    
    assert response.status_code == 400
    assert "must be checked out" in response.json()["detail"].lower()

def test_transfer_creates_event_record(client, sample_checked_out_kit):
    """Test that transfer creates a custody event record"""
    response = client.post(
        "/api/v1/custody/transfer",
        json={
            "kit_code": "TEST-TRANSFER-001",
            "new_custodian_name": "Jane Athlete"
        }
    )
    
    assert response.status_code == 201
    
    # Verify event was created in database
    db = TestingSessionLocal()
    event = db.query(CustodyEvent).filter(
        CustodyEvent.kit_id == sample_checked_out_kit.id,
        CustodyEvent.event_type == CustodyEventType.transfer
    ).first()
    
    assert event is not None
    assert event.event_type == CustodyEventType.transfer
    assert event.custodian_name == "Jane Athlete"
    db.close()

def test_transfer_updates_kit_custodian(client, sample_checked_out_kit):
    """Test that transfer updates kit custodian"""
    response = client.post(
        "/api/v1/custody/transfer",
        json={
            "kit_code": "TEST-TRANSFER-001",
            "new_custodian_name": "Jane Athlete"
        }
    )
    
    assert response.status_code == 201
    
    # Verify kit custodian was updated
    db = TestingSessionLocal()
    kit = db.query(Kit).filter(Kit.id == sample_checked_out_kit.id).first()
    
    assert kit.status == KitStatus.checked_out
    assert kit.current_custodian_name == "Jane Athlete"
    db.close()

def test_transfer_with_custodian_id(client, sample_checked_out_kit):
    """Test transfer with custodian_id provided"""
    response = client.post(
        "/api/v1/custody/transfer",
        json={
            "kit_code": "TEST-TRANSFER-001",
            "new_custodian_name": "Jane Athlete",
            "new_custodian_id": 42
        }
    )
    
    assert response.status_code == 201
    
    # Verify custodian_id was stored
    db = TestingSessionLocal()
    kit = db.query(Kit).filter(Kit.id == sample_checked_out_kit.id).first()
    
    assert kit.current_custodian_id == 42
    assert kit.current_custodian_name == "Jane Athlete"
    db.close()
