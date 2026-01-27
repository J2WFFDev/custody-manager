import pytest
from app.models.kit import Kit, KitStatus
from app.models.user import User
from app.models.custody_event import CustodyEvent, CustodyEventType
from app.main import app


@pytest.fixture
def sample_kit(db_session):
    """Create a sample kit for testing"""
    kit = Kit(
        code="TEST-LOST-001",
        name="Test Lost Kit",
        description="A kit for testing lost/found",
        status=KitStatus.available
    )
    db_session.add(kit)
    db_session.commit()
    db_session.refresh(kit)
    return kit


@pytest.fixture
def lost_kit(db_session):
    """Create a sample kit already marked as lost"""
    kit = Kit(
        code="TEST-LOST-002",
        name="Already Lost Kit",
        description="A kit already marked as lost",
        status=KitStatus.lost,
        current_custodian_name="John Doe"
    )
    db_session.add(kit)
    db_session.commit()
    db_session.refresh(kit)
    return kit


@pytest.fixture
def sample_armorer(db_session):
    """Create a sample armorer user for testing"""
    user = User(
        email="armorer@test.com",
        name="Test Armorer",
        oauth_provider="google",
        oauth_id="test-armorer-123",
        role="armorer",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_report_kit_lost_success(client, sample_kit, sample_armorer, db_session):
    """Test successfully reporting a kit as lost"""
    # Override get_current_user to return armorer
    from app.api.v1.endpoints.custody import get_current_user
    app.dependency_overrides[get_current_user] = lambda: sample_armorer
    
    response = client.post(
        "/api/v1/custody/report-lost",
        json={
            "kit_code": "TEST-LOST-001",
            "notes": "Kit missing after practice"
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
    assert data["kit_code"] == "TEST-LOST-001"
    assert data["kit_name"] == "Test Lost Kit"
    assert "reported as lost" in data["message"]
    
    # Verify event details
    event = data["event"]
    assert event["event_type"] == "lost"
    assert event["initiated_by_name"] == "Test Armorer"
    
    # Verify kit status was updated in database
    db_session.expire_all()
    kit = db_session.query(Kit).filter(Kit.code == "TEST-LOST-001").first()
    assert kit.status == KitStatus.lost
    
    # Clean up override
    app.dependency_overrides.clear()


def test_report_kit_lost_already_lost(client, lost_kit, sample_armorer, db_session):
    """Test that reporting an already lost kit returns an error"""
    # Override get_current_user to return armorer
    from app.api.v1.endpoints.custody import get_current_user
    app.dependency_overrides[get_current_user] = lambda: sample_armorer
    
    response = client.post(
        "/api/v1/custody/report-lost",
        json={
            "kit_code": "TEST-LOST-002",
            "notes": "Attempting to report as lost again"
        }
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "already marked as lost" in data["detail"]
    
    # Clean up override
    app.dependency_overrides.clear()


def test_report_kit_lost_not_found(client, sample_armorer, db_session):
    """Test that reporting a non-existent kit returns 404"""
    # Override get_current_user to return armorer
    from app.api.v1.endpoints.custody import get_current_user
    app.dependency_overrides[get_current_user] = lambda: sample_armorer
    
    response = client.post(
        "/api/v1/custody/report-lost",
        json={
            "kit_code": "NONEXISTENT",
            "notes": "This kit doesn't exist"
        }
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"]
    
    # Clean up override
    app.dependency_overrides.clear()


def test_report_kit_found_success(client, lost_kit, sample_armorer, db_session):
    """Test successfully reporting a kit as found"""
    # Override get_current_user to return armorer
    from app.api.v1.endpoints.custody import get_current_user
    app.dependency_overrides[get_current_user] = lambda: sample_armorer
    
    response = client.post(
        "/api/v1/custody/report-found",
        json={
            "kit_code": "TEST-LOST-002",
            "notes": "Found in storage room"
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
    assert data["kit_code"] == "TEST-LOST-002"
    assert data["kit_name"] == "Already Lost Kit"
    assert "recovered" in data["message"]
    assert "available" in data["message"]
    
    # Verify event details
    event = data["event"]
    assert event["event_type"] == "found"
    assert event["initiated_by_name"] == "Test Armorer"
    
    # Verify kit status was updated in database
    db_session.expire_all()
    kit = db_session.query(Kit).filter(Kit.code == "TEST-LOST-002").first()
    assert kit.status == KitStatus.available
    assert kit.current_custodian_id is None
    assert kit.current_custodian_name is None
    
    # Clean up override
    app.dependency_overrides.clear()


def test_report_kit_found_not_lost(client, sample_kit, sample_armorer, db_session):
    """Test that reporting a non-lost kit as found returns an error"""
    # Override get_current_user to return armorer
    from app.api.v1.endpoints.custody import get_current_user
    app.dependency_overrides[get_current_user] = lambda: sample_armorer
    
    response = client.post(
        "/api/v1/custody/report-found",
        json={
            "kit_code": "TEST-LOST-001",
            "notes": "This kit isn't lost"
        }
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "is not lost" in data["detail"]
    
    # Clean up override
    app.dependency_overrides.clear()


def test_report_kit_found_not_found(client, sample_armorer, db_session):
    """Test that reporting a non-existent kit as found returns 404"""
    # Override get_current_user to return armorer
    from app.api.v1.endpoints.custody import get_current_user
    app.dependency_overrides[get_current_user] = lambda: sample_armorer
    
    response = client.post(
        "/api/v1/custody/report-found",
        json={
            "kit_code": "NONEXISTENT",
            "notes": "This kit doesn't exist"
        }
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"]
    
    # Clean up override
    app.dependency_overrides.clear()


def test_custody_event_created_on_lost(client, sample_kit, sample_armorer, db_session):
    """Test that custody event is created when kit is reported lost"""
    # Override get_current_user to return armorer
    from app.api.v1.endpoints.custody import get_current_user
    app.dependency_overrides[get_current_user] = lambda: sample_armorer
    
    response = client.post(
        "/api/v1/custody/report-lost",
        json={
            "kit_code": "TEST-LOST-001",
            "notes": "Kit missing"
        }
    )
    
    assert response.status_code == 201
    
    # Verify custody event was created in database
    db_session.expire_all()
    kit = db_session.query(Kit).filter(Kit.code == "TEST-LOST-001").first()
    events = db_session.query(CustodyEvent).filter(CustodyEvent.kit_id == kit.id).all()
    
    assert len(events) == 1
    assert events[0].event_type == CustodyEventType.lost
    assert events[0].notes == "Kit missing"
    
    # Clean up override
    app.dependency_overrides.clear()


def test_custody_event_created_on_found(client, lost_kit, sample_armorer, db_session):
    """Test that custody event is created when kit is reported found"""
    # Override get_current_user to return armorer
    from app.api.v1.endpoints.custody import get_current_user
    app.dependency_overrides[get_current_user] = lambda: sample_armorer
    
    response = client.post(
        "/api/v1/custody/report-found",
        json={
            "kit_code": "TEST-LOST-002",
            "notes": "Found in storage"
        }
    )
    
    assert response.status_code == 201
    
    # Verify custody event was created in database
    db_session.expire_all()
    kit = db_session.query(Kit).filter(Kit.code == "TEST-LOST-002").first()
    events = db_session.query(CustodyEvent).filter(CustodyEvent.kit_id == kit.id).all()
    
    assert len(events) == 1
    assert events[0].event_type == CustodyEventType.found
    assert events[0].notes == "Found in storage"
    
    # Clean up override
    app.dependency_overrides.clear()
