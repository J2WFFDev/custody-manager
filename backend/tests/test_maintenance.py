import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models.kit import Kit, KitStatus
from app.models.user import User, UserRole

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_maintenance.db"

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
        code="TEST-KIT-001",
        name="Test Maintenance Kit",
        description="A kit for testing maintenance",
        status=KitStatus.available
    )
    db.add(kit)
    db.commit()
    db.refresh(kit)
    db.close()
    return kit


@pytest.fixture
def sample_armorer(db_setup):
    """Create a sample armorer user for testing"""
    db = TestingSessionLocal()
    user = User(
        email="armorer@test.com",
        name="Test Armorer",
        oauth_provider="google",
        oauth_id="test-armorer-123",
        role=UserRole.armorer,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


def test_open_maintenance_success(client, sample_kit, sample_armorer):
    """Test successfully opening maintenance on a kit"""
    response = client.post(
        "/api/v1/maintenance/open",
        json={
            "kit_code": sample_kit.code,
            "notes": "Replacing trigger assembly",
            "parts_replaced": "Trigger, spring",
            "round_count": 5000
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "Maintenance opened" in data["message"]
    assert data["kit_code"] == sample_kit.code
    assert data["event"]["notes"] == "Replacing trigger assembly"
    assert data["event"]["parts_replaced"] == "Trigger, spring"
    assert data["event"]["round_count"] == 5000
    assert data["event"]["is_open"] == 1


def test_open_maintenance_kit_not_found(client, sample_armorer):
    """Test opening maintenance on a non-existent kit"""
    response = client.post(
        "/api/v1/maintenance/open",
        json={
            "kit_code": "NONEXISTENT",
            "notes": "Test"
        }
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_open_maintenance_already_in_maintenance(client, sample_kit, sample_armorer):
    """Test opening maintenance on a kit that's already in maintenance"""
    # First, open maintenance
    client.post(
        "/api/v1/maintenance/open",
        json={
            "kit_code": sample_kit.code,
            "notes": "Initial maintenance"
        }
    )
    
    # Try to open again
    response = client.post(
        "/api/v1/maintenance/open",
        json={
            "kit_code": sample_kit.code,
            "notes": "Second maintenance"
        }
    )
    
    assert response.status_code == 400
    assert "already in maintenance" in response.json()["detail"]


def test_close_maintenance_success(client, sample_kit, sample_armorer):
    """Test successfully closing maintenance on a kit"""
    # First, open maintenance
    client.post(
        "/api/v1/maintenance/open",
        json={
            "kit_code": sample_kit.code,
            "notes": "Starting maintenance"
        }
    )
    
    # Now close it
    response = client.post(
        "/api/v1/maintenance/close",
        json={
            "kit_code": sample_kit.code,
            "notes": "Maintenance complete",
            "parts_replaced": "Trigger replaced",
            "round_count": 6000
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "Maintenance closed" in data["message"]
    assert data["kit_code"] == sample_kit.code
    assert data["event"]["is_open"] == 0
    assert data["event"]["closed_by_name"] is not None
    
    # Verify kit is back to available
    kit_response = client.get(f"/api/v1/kits/code/{sample_kit.code}")
    assert kit_response.json()["status"] == "available"


def test_close_maintenance_not_in_maintenance(client, sample_kit, sample_armorer):
    """Test closing maintenance on a kit that's not in maintenance"""
    response = client.post(
        "/api/v1/maintenance/close",
        json={
            "kit_code": sample_kit.code,
            "notes": "Close maintenance"
        }
    )
    
    assert response.status_code == 400
    assert "not in maintenance" in response.json()["detail"]


def test_close_maintenance_kit_not_found(client, sample_armorer):
    """Test closing maintenance on a non-existent kit"""
    response = client.post(
        "/api/v1/maintenance/close",
        json={
            "kit_code": "NONEXISTENT",
            "notes": "Test"
        }
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_get_maintenance_history(client, sample_kit, sample_armorer):
    """Test getting maintenance history for a kit"""
    # Open and close maintenance
    client.post(
        "/api/v1/maintenance/open",
        json={
            "kit_code": sample_kit.code,
            "notes": "First maintenance"
        }
    )
    
    client.post(
        "/api/v1/maintenance/close",
        json={
            "kit_code": sample_kit.code,
            "notes": "Completed first maintenance"
        }
    )
    
    # Get history
    response = client.get(f"/api/v1/maintenance/kits/{sample_kit.id}/history")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["kit_id"] == sample_kit.id
    assert data[0]["is_open"] == 0


def test_get_maintenance_history_kit_not_found(client):
    """Test getting maintenance history for a non-existent kit"""
    response = client.get("/api/v1/maintenance/kits/999/history")
    
    assert response.status_code == 404


def test_kit_status_transitions(client, sample_kit, sample_armorer):
    """Test that kit status transitions correctly through maintenance workflow"""
    # Initial status should be available
    kit_response = client.get(f"/api/v1/kits/code/{sample_kit.code}")
    assert kit_response.json()["status"] == "available"
    
    # Open maintenance - kit should be in_maintenance
    client.post(
        "/api/v1/maintenance/open",
        json={
            "kit_code": sample_kit.code,
            "notes": "Maintenance start"
        }
    )
    
    kit_response = client.get(f"/api/v1/kits/code/{sample_kit.code}")
    assert kit_response.json()["status"] == "in_maintenance"
    
    # Close maintenance - kit should be available again
    client.post(
        "/api/v1/maintenance/close",
        json={
            "kit_code": sample_kit.code,
            "notes": "Maintenance complete"
        }
    )
    
    kit_response = client.get(f"/api/v1/kits/code/{sample_kit.code}")
    assert kit_response.json()["status"] == "available"
