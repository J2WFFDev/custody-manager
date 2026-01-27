import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from app.database import Base, get_db
from app.main import app
from app.models.kit import Kit, KitStatus
from app.models.user import User, UserRole
from app.models.custody_event import CustodyEvent, CustodyEventType

# Use file-based SQLite for testing with proper cleanup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_events.db"

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
def sample_data(db_setup):
    """Create sample data for testing"""
    db = TestingSessionLocal()
    
    # Create users
    coach = User(
        email="coach@test.com",
        name="Test Coach",
        oauth_provider="google",
        oauth_id="test-coach-123",
        role=UserRole.coach,
        is_active=True
    )
    athlete = User(
        email="athlete@test.com",
        name="Test Athlete",
        oauth_provider="google",
        oauth_id="test-athlete-123",
        role=UserRole.parent,
        is_active=True
    )
    db.add(coach)
    db.add(athlete)
    db.commit()
    db.refresh(coach)
    db.refresh(athlete)
    
    # Store IDs before creating other objects
    coach_id = coach.id
    athlete_id = athlete.id
    
    # Create kits
    kit1 = Kit(
        code="TEST-001",
        name="Test Kit 1",
        description="First test kit",
        status=KitStatus.available
    )
    kit2 = Kit(
        code="TEST-002",
        name="Test Kit 2",
        description="Second test kit",
        status=KitStatus.available
    )
    db.add(kit1)
    db.add(kit2)
    db.commit()
    db.refresh(kit1)
    db.refresh(kit2)
    
    # Store IDs
    kit1_id = kit1.id
    kit2_id = kit2.id
    
    # Create custody events with different timestamps
    now = datetime.utcnow()
    
    # Event 1: Coach checks out kit1 to athlete (3 days ago)
    event1 = CustodyEvent(
        event_type=CustodyEventType.checkout_onprem,
        kit_id=kit1_id,
        initiated_by_id=coach_id,
        initiated_by_name=coach.name,
        custodian_id=athlete_id,
        custodian_name=athlete.name,
        notes="Practice session",
        location_type="on_premises"
    )
    event1.created_at = now - timedelta(days=3)
    db.add(event1)
    
    # Event 2: Athlete checks in kit1 (2 days ago)
    event2 = CustodyEvent(
        event_type=CustodyEventType.checkin,
        kit_id=kit1_id,
        initiated_by_id=athlete_id,
        initiated_by_name=athlete.name,
        custodian_id=coach_id,
        custodian_name=coach.name,
        notes="Returned after practice",
        location_type="on_premises"
    )
    event2.created_at = now - timedelta(days=2)
    db.add(event2)
    
    # Event 3: Coach checks out kit1 to athlete off-site (1 day ago)
    event3 = CustodyEvent(
        event_type=CustodyEventType.checkout_offsite,
        kit_id=kit1_id,
        initiated_by_id=coach_id,
        initiated_by_name=coach.name,
        custodian_id=athlete_id,
        custodian_name=athlete.name,
        notes="Competition",
        location_type="off_site"
    )
    event3.created_at = now - timedelta(days=1)
    db.add(event3)
    
    # Event 4: Coach checks out kit2 to athlete (5 hours ago)
    event4 = CustodyEvent(
        event_type=CustodyEventType.checkout_onprem,
        kit_id=kit2_id,
        initiated_by_id=coach_id,
        initiated_by_name=coach.name,
        custodian_id=athlete_id,
        custodian_name=athlete.name,
        notes="Training",
        location_type="on_premises"
    )
    event4.created_at = now - timedelta(hours=5)
    db.add(event4)
    
    db.commit()
    db.close()
    
    return {
        "coach_id": coach_id,
        "athlete_id": athlete_id,
        "kit1_id": kit1_id,
        "kit2_id": kit2_id
    }


def test_get_kit_events_success(client, sample_data):
    """Test successful retrieval of kit events"""
    kit_id = sample_data["kit1_id"]
    
    response = client.get(f"/api/v1/events/kit/{kit_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "events" in data
    assert "total" in data
    assert "kit_id" in data
    assert "kit_name" in data
    assert "kit_code" in data
    
    # Verify kit info
    assert data["kit_id"] == kit_id
    assert data["kit_name"] == "Test Kit 1"
    assert data["kit_code"] == "TEST-001"
    
    # Verify events
    assert data["total"] == 3  # kit1 has 3 events
    assert len(data["events"]) == 3
    
    # Verify events are sorted by timestamp descending (default)
    timestamps = [event["created_at"] for event in data["events"]]
    assert timestamps == sorted(timestamps, reverse=True)
    
    # Verify event details
    for event in data["events"]:
        assert "id" in event
        assert "event_type" in event
        assert "kit_id" in event
        assert "initiated_by_id" in event
        assert "initiated_by_name" in event
        assert "custodian_name" in event
        assert "created_at" in event
        assert event["kit_id"] == kit_id


def test_get_kit_events_not_found(client, sample_data):
    """Test getting events for non-existent kit"""
    response = client.get("/api/v1/events/kit/9999")
    
    assert response.status_code == 404
    assert "Kit not found" in response.json()["detail"]


def test_get_kit_events_with_event_type_filter(client, sample_data):
    """Test filtering kit events by event type"""
    kit_id = sample_data["kit1_id"]
    
    # Filter for checkout_onprem events
    response = client.get(
        f"/api/v1/events/kit/{kit_id}",
        params={"event_type": "checkout_onprem"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should only have 1 checkout_onprem event for kit1
    assert data["total"] == 1
    assert len(data["events"]) == 1
    assert data["events"][0]["event_type"] == "checkout_onprem"


def test_get_kit_events_with_sorting(client, sample_data):
    """Test sorting kit events"""
    kit_id = sample_data["kit1_id"]
    
    # Test ascending order
    response = client.get(
        f"/api/v1/events/kit/{kit_id}",
        params={"sort_order": "asc"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify events are sorted ascending
    timestamps = [event["created_at"] for event in data["events"]]
    assert timestamps == sorted(timestamps)


def test_get_kit_events_with_pagination(client, sample_data):
    """Test pagination of kit events"""
    kit_id = sample_data["kit1_id"]
    
    # Get first page with limit 2
    response = client.get(
        f"/api/v1/events/kit/{kit_id}",
        params={"skip": 0, "limit": 2}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] == 3  # Total is 3
    assert len(data["events"]) == 2  # But we only get 2 results
    
    # Get second page
    response2 = client.get(
        f"/api/v1/events/kit/{kit_id}",
        params={"skip": 2, "limit": 2}
    )
    
    assert response2.status_code == 200
    data2 = response2.json()
    
    assert data2["total"] == 3
    assert len(data2["events"]) == 1  # Only 1 result left


def test_get_user_events_success(client, sample_data):
    """Test successful retrieval of user events"""
    athlete_id = sample_data["athlete_id"]
    
    response = client.get(f"/api/v1/events/user/{athlete_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "events" in data
    assert "total" in data
    assert "user_id" in data
    assert "user_name" in data
    
    # Verify user info
    assert data["user_id"] == athlete_id
    assert data["user_name"] == "Test Athlete"
    
    # Verify events
    # Athlete is custodian in 3 events and initiator in 1 event = 4 total
    assert data["total"] == 4
    assert len(data["events"]) == 4
    
    # Verify events are sorted by timestamp descending (default)
    timestamps = [event["created_at"] for event in data["events"]]
    assert timestamps == sorted(timestamps, reverse=True)


def test_get_user_events_not_found(client, sample_data):
    """Test getting events for non-existent user"""
    response = client.get("/api/v1/events/user/9999")
    
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


def test_get_user_events_as_coach(client, sample_data):
    """Test retrieving events for a coach user"""
    coach_id = sample_data["coach_id"]
    
    response = client.get(f"/api/v1/events/user/{coach_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Coach initiated 3 events and is custodian in 1 event = 4 total
    assert data["total"] == 4
    assert data["user_id"] == coach_id
    assert data["user_name"] == "Test Coach"


def test_get_user_events_with_filters(client, sample_data):
    """Test filtering user events"""
    athlete_id = sample_data["athlete_id"]
    
    # Filter for checkout_offsite events only
    response = client.get(
        f"/api/v1/events/user/{athlete_id}",
        params={"event_type": "checkout_offsite"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should only have 1 checkout_offsite event
    assert data["total"] == 1
    assert len(data["events"]) == 1
    assert data["events"][0]["event_type"] == "checkout_offsite"
