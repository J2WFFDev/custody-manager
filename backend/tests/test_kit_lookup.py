import pytest
from app.models.kit import Kit, KitStatus
from app.schemas.kit import KitLookupResponse

def test_lookup_kit_success(client, db_session):
    """Test successful kit lookup by code"""
    # Create a test kit
    test_kit = Kit(
        code="TEST001",
        name="Test Kit",
        description="A test kit for unit testing",
        status=KitStatus.AVAILABLE,
        current_custodian_name=None
    )
    db_session.add(test_kit)
    db_session.commit()
    
    # Lookup the kit
    response = client.get("/api/v1/kits/lookup?code=TEST001")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "TEST001"
    assert data["name"] == "Test Kit"
    assert data["description"] == "A test kit for unit testing"
    assert data["status"] == "available"
    assert data["custodian"] is None

def test_lookup_kit_with_custodian(client, db_session):
    """Test kit lookup when checked out to a custodian"""
    # Create a checked out kit
    test_kit = Kit(
        code="TEST002",
        name="Checked Out Kit",
        description="A kit that is checked out",
        status=KitStatus.CHECKED_OUT,
        current_custodian_name="John Doe"
    )
    db_session.add(test_kit)
    db_session.commit()
    
    # Lookup the kit
    response = client.get("/api/v1/kits/lookup?code=TEST002")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "TEST002"
    assert data["status"] == "checked_out"
    assert data["custodian"] == "John Doe"

def test_lookup_kit_in_maintenance(client, db_session):
    """Test kit lookup when in maintenance"""
    # Create a kit in maintenance
    test_kit = Kit(
        code="TEST003",
        name="Maintenance Kit",
        description="A kit in maintenance",
        status=KitStatus.IN_MAINTENANCE,
        current_custodian_name=None
    )
    db_session.add(test_kit)
    db_session.commit()
    
    # Lookup the kit
    response = client.get("/api/v1/kits/lookup?code=TEST003")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_maintenance"
    assert data["custodian"] is None

def test_lookup_kit_not_found(client):
    """Test kit lookup with non-existent code"""
    response = client.get("/api/v1/kits/lookup?code=NONEXISTENT")
    
    # Assertions
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()

def test_lookup_kit_missing_code_parameter(client):
    """Test kit lookup without providing code parameter"""
    response = client.get("/api/v1/kits/lookup")
    
    # Assertions
    assert response.status_code == 422  # Unprocessable Entity

def test_lookup_kit_manual_entry(client, db_session):
    """Test kit lookup with manual code entry (supports both QR and manual)"""
    # Create a kit with a manually entered code
    test_kit = Kit(
        code="MANUAL-123",
        name="Manual Entry Kit",
        description="A kit entered manually",
        status=KitStatus.AVAILABLE
    )
    db_session.add(test_kit)
    db_session.commit()
    
    # Lookup the kit
    response = client.get("/api/v1/kits/lookup?code=MANUAL-123")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "MANUAL-123"
    assert data["name"] == "Manual Entry Kit"
