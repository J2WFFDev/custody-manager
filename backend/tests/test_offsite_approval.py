import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
from app.database import Base, get_db
from app.main import app
from app.models.kit import Kit, KitStatus
from app.models.user import User, UserRole
from app.models.approval_request import ApprovalRequest, ApprovalStatus
from app.models.custody_event import CustodyEvent, CustodyEventType
from app.constants import ATTESTATION_TEXT

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_offsite_approval.db"

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
        code="TEST-OFFSITE-001",
        name="Test Offsite Kit",
        description="A kit for testing off-site checkout",
        status=KitStatus.available
    )
    db.add(kit)
    db.commit()
    db.refresh(kit)
    db.close()
    return kit

@pytest.fixture
def verified_parent(db_setup):
    """Create a verified parent user for testing"""
    db = TestingSessionLocal()
    user = User(
        email="parent@test.com",
        name="Test Parent",
        oauth_provider="google",
        oauth_id="test-parent-123",
        role=UserRole.parent,
        verified_adult=True,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

@pytest.fixture
def unverified_parent(db_setup):
    """Create an unverified parent user for testing"""
    db = TestingSessionLocal()
    user = User(
        email="unverified@test.com",
        name="Unverified Parent",
        oauth_provider="google",
        oauth_id="test-unverified-123",
        role=UserRole.parent,
        verified_adult=False,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

@pytest.fixture
def armorer(db_setup):
    """Create an armorer user for testing"""
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

@pytest.fixture
def coach(db_setup):
    """Create a coach user for testing"""
    db = TestingSessionLocal()
    user = User(
        email="coach@test.com",
        name="Test Coach",
        oauth_provider="google",
        oauth_id="test-coach-offsite-123",
        role=UserRole.coach,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


# Tests for off-site checkout request creation
def test_offsite_request_success_verified_parent(client, sample_kit, verified_parent):
    """Test successful off-site checkout request by verified parent"""
    # Override get_current_user to return verified parent
    from app.api.v1.endpoints.custody import get_current_user
    app.dependency_overrides[get_current_user] = lambda: verified_parent
    
    response = client.post(
        "/api/v1/custody/offsite-request",
        json={
            "kit_code": "TEST-OFFSITE-001",
            "custodian_name": "Child Athlete",
            "notes": "For weekend practice",
            "attestation_signature": "Test Parent",
            "attestation_accepted": True
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify response structure
    assert "message" in data
    assert "approval_request" in data
    assert "awaiting approval" in data["message"].lower()
    
    # Verify approval request details
    approval = data["approval_request"]
    assert approval["status"] == "pending"
    assert approval["requester_name"] == "Test Parent"
    assert approval["custodian_name"] == "Child Athlete"
    assert approval["kit_code"] == "TEST-OFFSITE-001"
    assert approval["notes"] == "For weekend practice"

def test_offsite_request_denied_unverified_parent(client, sample_kit, unverified_parent):
    """Test off-site checkout request denied for unverified parent"""
    # Override get_current_user to return unverified parent
    from app.api.v1.endpoints.custody import get_current_user
    app.dependency_overrides[get_current_user] = lambda: unverified_parent
    
    response = client.post(
        "/api/v1/custody/offsite-request",
        json={
            "kit_code": "TEST-OFFSITE-001",
            "custodian_name": "Child Athlete",
            "attestation_signature": "Unverified Parent",
            "attestation_accepted": True
        }
    )
    
    assert response.status_code == 403
    assert "verified adult" in response.json()["detail"].lower()

def test_offsite_request_kit_not_found(client, verified_parent):
    """Test off-site checkout request with non-existent kit"""
    from app.api.v1.endpoints.custody import get_current_user
    app.dependency_overrides[get_current_user] = lambda: verified_parent
    
    response = client.post(
        "/api/v1/custody/offsite-request",
        json={
            "kit_code": "NONEXISTENT",
            "custodian_name": "Child Athlete",
            "attestation_signature": "Test Parent",
            "attestation_accepted": True
        }
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_offsite_request_kit_not_available(client, sample_kit, verified_parent):
    """Test off-site checkout request when kit is already checked out"""
    # First, mark the kit as checked out
    db = TestingSessionLocal()
    kit = db.query(Kit).filter(Kit.id == sample_kit.id).first()
    kit.status = KitStatus.checked_out
    db.commit()
    db.close()
    
    from app.api.v1.endpoints.custody import get_current_user
    app.dependency_overrides[get_current_user] = lambda: verified_parent
    
    response = client.post(
        "/api/v1/custody/offsite-request",
        json={
            "kit_code": "TEST-OFFSITE-001",
            "custodian_name": "Child Athlete",
            "attestation_signature": "Test Parent",
            "attestation_accepted": True
        }
    )
    
    assert response.status_code == 400
    assert "checked_out" in response.json()["detail"]


# Tests for approval/denial
def test_approve_offsite_request_by_armorer(client, sample_kit, verified_parent, armorer):
    """Test approval of off-site request by armorer"""
    # First, create an approval request
    db = TestingSessionLocal()
    approval_request = ApprovalRequest(
        kit_id=sample_kit.id,
        requester_id=verified_parent.id,
        requester_name=verified_parent.name,
        custodian_name="Child Athlete",
        notes="For weekend practice",
        status=ApprovalStatus.pending,
        # Attestation fields
        attestation_text=ATTESTATION_TEXT,
        attestation_signature="Test Parent",
        attestation_timestamp=datetime.now(timezone.utc)
    )
    db.add(approval_request)
    db.commit()
    db.refresh(approval_request)
    request_id = approval_request.id
    db.close()
    
    # Now approve it as armorer
    from app.api.v1.endpoints.custody import get_current_user
    app.dependency_overrides[get_current_user] = lambda: armorer
    
    response = client.post(
        "/api/v1/custody/offsite-approve",
        json={
            "approval_request_id": request_id,
            "approve": True
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response
    assert "approved" in data["message"].lower()
    assert data["approval_request"]["status"] == "approved"
    assert data["approval_request"]["approver_name"] == "Test Armorer"
    assert data["approval_request"]["approver_role"] == "armorer"
    assert data["custody_event"] is not None
    assert data["custody_event"]["event_type"] == "checkout_offsite"
    
    # Verify kit status updated
    db = TestingSessionLocal()
    kit = db.query(Kit).filter(Kit.id == sample_kit.id).first()
    assert kit.status == KitStatus.checked_out
    assert kit.current_custodian_name == "Child Athlete"
    db.close()
    
    # Verify custody event created
    db = TestingSessionLocal()
    event = db.query(CustodyEvent).filter(
        CustodyEvent.kit_id == sample_kit.id
    ).first()
    assert event is not None
    assert event.event_type == CustodyEventType.checkout_offsite
    assert event.location_type == "off_site"
    db.close()

def test_approve_offsite_request_by_coach(client, sample_kit, verified_parent, coach):
    """Test approval of off-site request by coach"""
    # First, create an approval request
    db = TestingSessionLocal()
    approval_request = ApprovalRequest(
        kit_id=sample_kit.id,
        requester_id=verified_parent.id,
        requester_name=verified_parent.name,
        custodian_name="Child Athlete",
        status=ApprovalStatus.pending,
        attestation_text=ATTESTATION_TEXT,
        attestation_signature="Test Parent",
        attestation_timestamp=datetime.now(timezone.utc)
    )
    db.add(approval_request)
    db.commit()
    db.refresh(approval_request)
    request_id = approval_request.id
    db.close()
    
    # Now approve it as coach
    from app.api.v1.endpoints.custody import get_current_user
    app.dependency_overrides[get_current_user] = lambda: coach
    
    response = client.post(
        "/api/v1/custody/offsite-approve",
        json={
            "approval_request_id": request_id,
            "approve": True
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["approval_request"]["status"] == "approved"
    assert data["approval_request"]["approver_role"] == "coach"

def test_deny_offsite_request(client, sample_kit, verified_parent, armorer):
    """Test denial of off-site request"""
    # First, create an approval request
    db = TestingSessionLocal()
    approval_request = ApprovalRequest(
        kit_id=sample_kit.id,
        requester_id=verified_parent.id,
        requester_name=verified_parent.name,
        custodian_name="Child Athlete",
        status=ApprovalStatus.pending,
        attestation_text=ATTESTATION_TEXT,
        attestation_signature="Test Parent",
        attestation_timestamp=datetime.now(timezone.utc)
    )
    db.add(approval_request)
    db.commit()
    db.refresh(approval_request)
    request_id = approval_request.id
    db.close()
    
    # Now deny it
    from app.api.v1.endpoints.custody import get_current_user
    app.dependency_overrides[get_current_user] = lambda: armorer
    
    response = client.post(
        "/api/v1/custody/offsite-approve",
        json={
            "approval_request_id": request_id,
            "approve": False,
            "denial_reason": "Kit needs maintenance"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["approval_request"]["status"] == "denied"
    assert data["approval_request"]["denial_reason"] == "Kit needs maintenance"
    assert data["custody_event"] is None
    
    # Verify kit is still available
    db = TestingSessionLocal()
    kit = db.query(Kit).filter(Kit.id == sample_kit.id).first()
    assert kit.status == KitStatus.available
    db.close()

def test_deny_requires_reason(client, sample_kit, verified_parent, armorer):
    """Test that denial requires a reason"""
    # First, create an approval request
    db = TestingSessionLocal()
    approval_request = ApprovalRequest(
        kit_id=sample_kit.id,
        requester_id=verified_parent.id,
        requester_name=verified_parent.name,
        custodian_name="Child Athlete",
        status=ApprovalStatus.pending,
        attestation_text=ATTESTATION_TEXT,
        attestation_signature="Test Parent",
        attestation_timestamp=datetime.now(timezone.utc)
    )
    db.add(approval_request)
    db.commit()
    db.refresh(approval_request)
    request_id = approval_request.id
    db.close()
    
    from app.api.v1.endpoints.custody import get_current_user
    app.dependency_overrides[get_current_user] = lambda: armorer
    
    response = client.post(
        "/api/v1/custody/offsite-approve",
        json={
            "approval_request_id": request_id,
            "approve": False
        }
    )
    
    assert response.status_code == 400
    assert "denial reason" in response.json()["detail"].lower()

def test_approve_unauthorized_user(client, sample_kit, verified_parent):
    """Test that non-armorer/coach cannot approve"""
    # First, create an approval request
    db = TestingSessionLocal()
    approval_request = ApprovalRequest(
        kit_id=sample_kit.id,
        requester_id=verified_parent.id,
        requester_name=verified_parent.name,
        custodian_name="Child Athlete",
        status=ApprovalStatus.pending,
        attestation_text=ATTESTATION_TEXT,
        attestation_signature="Test Parent",
        attestation_timestamp=datetime.now(timezone.utc)
    )
    db.add(approval_request)
    db.commit()
    db.refresh(approval_request)
    request_id = approval_request.id
    db.close()
    
    # Try to approve as parent (not allowed)
    from app.api.v1.endpoints.custody import get_current_user
    app.dependency_overrides[get_current_user] = lambda: verified_parent
    
    response = client.post(
        "/api/v1/custody/offsite-approve",
        json={
            "approval_request_id": request_id,
            "approve": True
        }
    )
    
    assert response.status_code == 403
    assert "armorer or coach" in response.json()["detail"].lower()


# Tests for listing pending approvals
def test_list_pending_approvals(client, sample_kit, verified_parent, armorer):
    """Test listing pending approvals"""
    # Create multiple approval requests
    db = TestingSessionLocal()
    
    approval1 = ApprovalRequest(
        kit_id=sample_kit.id,
        requester_id=verified_parent.id,
        requester_name=verified_parent.name,
        custodian_name="Child 1",
        status=ApprovalStatus.pending,
        attestation_text=ATTESTATION_TEXT,
        attestation_signature="Test Parent",
        attestation_timestamp=datetime.now(timezone.utc)
    )
    db.add(approval1)
    
    # Create another kit and request
    kit2 = Kit(
        code="TEST-OFFSITE-002",
        name="Test Kit 2",
        status=KitStatus.available
    )
    db.add(kit2)
    db.commit()
    db.refresh(kit2)
    
    approval2 = ApprovalRequest(
        kit_id=kit2.id,
        requester_id=verified_parent.id,
        requester_name=verified_parent.name,
        custodian_name="Child 2",
        status=ApprovalStatus.pending,
        attestation_text=ATTESTATION_TEXT,
        attestation_signature="Test Parent",
        attestation_timestamp=datetime.now(timezone.utc)
    )
    db.add(approval2)
    
    # Create an approved request (should not be in list)
    approval3 = ApprovalRequest(
        kit_id=sample_kit.id,
        requester_id=verified_parent.id,
        requester_name=verified_parent.name,
        custodian_name="Child 3",
        status=ApprovalStatus.approved
    )
    db.add(approval3)
    
    db.commit()
    db.close()
    
    # List pending approvals as armorer
    from app.api.v1.endpoints.custody import get_current_user
    app.dependency_overrides[get_current_user] = lambda: armorer
    
    response = client.get("/api/v1/custody/pending-approvals")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should have 2 pending requests
    assert len(data) == 2
    assert all(req["status"] == "pending" for req in data)
    
    # Verify details
    custodian_names = [req["custodian_name"] for req in data]
    assert "Child 1" in custodian_names
    assert "Child 2" in custodian_names
    assert "Child 3" not in custodian_names

def test_list_pending_approvals_unauthorized(client, verified_parent):
    """Test that parent cannot list pending approvals"""
    from app.api.v1.endpoints.custody import get_current_user
    app.dependency_overrides[get_current_user] = lambda: verified_parent
    
    response = client.get("/api/v1/custody/pending-approvals")
    
    assert response.status_code == 403
    assert "armorer or coach" in response.json()["detail"].lower()


# Tests for attestation functionality (CUSTODY-012)
def test_get_attestation_text(client):
    """Test retrieving attestation text"""
    response = client.get("/api/v1/custody/attestation-text")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "attestation_text" in data
    assert "RESPONSIBILITY ATTESTATION" in data["attestation_text"]
    assert "CUSTODY RESPONSIBILITY" in data["attestation_text"]
    assert "SAFE STORAGE" in data["attestation_text"]
    assert "LEGAL COMPLIANCE" in data["attestation_text"]


def test_offsite_request_with_attestation(client, sample_kit, verified_parent):
    """Test off-site checkout request with attestation"""
    from app.api.v1.endpoints.custody import get_current_user
    app.dependency_overrides[get_current_user] = lambda: verified_parent
    
    response = client.post(
        "/api/v1/custody/offsite-request",
        json={
            "kit_code": sample_kit.code,
            "custodian_name": "Child Athlete",
            "notes": "Competition this weekend",
            "attestation_signature": "Test Parent",
            "attestation_accepted": True
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    
    assert "approval_request" in data
    approval = data["approval_request"]
    
    # Verify attestation data is stored
    assert approval["attestation_text"] is not None
    assert "RESPONSIBILITY ATTESTATION" in approval["attestation_text"]
    assert approval["attestation_signature"] == "Test Parent"
    assert approval["attestation_timestamp"] is not None
    assert approval["status"] == "pending"


def test_offsite_request_without_attestation_signature(client, sample_kit, verified_parent):
    """Test that off-site checkout request fails without signature"""
    from app.api.v1.endpoints.custody import get_current_user
    app.dependency_overrides[get_current_user] = lambda: verified_parent
    
    response = client.post(
        "/api/v1/custody/offsite-request",
        json={
            "kit_code": sample_kit.code,
            "custodian_name": "Child Athlete",
            "attestation_signature": "",
            "attestation_accepted": True
        }
    )
    
    assert response.status_code == 400
    assert "signature" in response.json()["detail"].lower()


def test_offsite_request_without_attestation_acceptance(client, sample_kit, verified_parent):
    """Test that off-site checkout request fails without acceptance"""
    from app.api.v1.endpoints.custody import get_current_user
    app.dependency_overrides[get_current_user] = lambda: verified_parent
    
    response = client.post(
        "/api/v1/custody/offsite-request",
        json={
            "kit_code": sample_kit.code,
            "custodian_name": "Child Athlete",
            "attestation_signature": "Test Parent",
            "attestation_accepted": False
        }
    )
    
    assert response.status_code == 400
    assert "accept the responsibility attestation" in response.json()["detail"].lower()


def test_attestation_stored_in_approval_request(client, sample_kit, verified_parent, armorer):
    """Test that attestation data is preserved through approval workflow"""
    from app.api.v1.endpoints.custody import get_current_user
    
    # Step 1: Parent submits request with attestation
    app.dependency_overrides[get_current_user] = lambda: verified_parent
    
    response = client.post(
        "/api/v1/custody/offsite-request",
        json={
            "kit_code": sample_kit.code,
            "custodian_name": "Child Athlete",
            "attestation_signature": "Test Parent",
            "attestation_accepted": True
        }
    )
    
    assert response.status_code == 201
    approval_request_id = response.json()["approval_request"]["id"]
    original_signature = response.json()["approval_request"]["attestation_signature"]
    original_timestamp = response.json()["approval_request"]["attestation_timestamp"]
    
    # Step 2: Armorer approves the request
    app.dependency_overrides[get_current_user] = lambda: armorer
    
    response = client.post(
        "/api/v1/custody/offsite-approve",
        json={
            "approval_request_id": approval_request_id,
            "approve": True
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify attestation data is preserved
    assert data["approval_request"]["attestation_signature"] == original_signature
    assert data["approval_request"]["attestation_timestamp"] == original_timestamp
    assert data["approval_request"]["attestation_text"] is not None


def test_attestation_visible_to_approvers(client, sample_kit, verified_parent, armorer):
    """Test that approvers can view attestation data when reviewing requests"""
    from app.api.v1.endpoints.custody import get_current_user
    
    # Parent submits request with attestation
    app.dependency_overrides[get_current_user] = lambda: verified_parent
    
    client.post(
        "/api/v1/custody/offsite-request",
        json={
            "kit_code": sample_kit.code,
            "custodian_name": "Child Athlete",
            "attestation_signature": "Test Parent",
            "attestation_accepted": True
        }
    )
    
    # Armorer lists pending approvals
    app.dependency_overrides[get_current_user] = lambda: armorer
    
    response = client.get("/api/v1/custody/pending-approvals")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 1
    approval = data[0]
    
    # Verify attestation data is visible to approver
    assert approval["attestation_signature"] == "Test Parent"
    assert approval["attestation_text"] is not None
    assert approval["attestation_timestamp"] is not None
    assert "RESPONSIBILITY ATTESTATION" in approval["attestation_text"]
