import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models import Kit, KitItem  # Import from app.models to ensure all models are loaded

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_kit_items.db"

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
def sample_kit(client):
    """Create a sample kit for testing"""
    response = client.post(
        "/api/v1/kits/",
        json={
            "code": "TEST-KIT-001",
            "name": "Test Kit",
            "description": "A test kit for item testing"
        }
    )
    return response.json()


def test_create_kit_item(client, sample_kit):
    """Test creating a new kit item"""
    kit_id = sample_kit["id"]
    
    response = client.post(
        f"/api/v1/kits/{kit_id}/items",
        json={
            "item_type": "firearm",
            "make": "Ruger",
            "model": "10/22",
            "serial_number": "SN-12345",
            "friendly_name": "Rifle #1",
            "quantity": 1,
            "notes": "Primary firearm"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["item_type"] == "firearm"
    assert data["make"] == "Ruger"
    assert data["model"] == "10/22"
    assert data["serial_number"] == "SN-12345"
    assert data["friendly_name"] == "Rifle #1"
    assert data["quantity"] == 1
    assert data["status"] == "in_kit"
    assert data["kit_id"] == kit_id
    assert "id" in data
    assert "created_at" in data


def test_list_kit_items(client, sample_kit):
    """Test listing all items in a kit"""
    kit_id = sample_kit["id"]
    
    # Create multiple items
    client.post(
        f"/api/v1/kits/{kit_id}/items",
        json={"item_type": "firearm", "make": "Ruger", "model": "10/22"}
    )
    client.post(
        f"/api/v1/kits/{kit_id}/items",
        json={"item_type": "optic", "make": "Vortex", "model": "Crossfire"}
    )
    client.post(
        f"/api/v1/kits/{kit_id}/items",
        json={"item_type": "case", "make": "Pelican", "model": "1750"}
    )
    
    # List all items
    response = client.get(f"/api/v1/kits/{kit_id}/items")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    
    # Verify item types
    item_types = [item["item_type"] for item in data]
    assert "firearm" in item_types
    assert "optic" in item_types
    assert "case" in item_types


def test_get_kit_item(client, sample_kit):
    """Test getting a specific kit item"""
    kit_id = sample_kit["id"]
    
    # Create an item
    create_response = client.post(
        f"/api/v1/kits/{kit_id}/items",
        json={
            "item_type": "magazine",
            "make": "Ruger",
            "model": "BX-25",
            "quantity": 3
        }
    )
    item_id = create_response.json()["id"]
    
    # Get the item
    response = client.get(f"/api/v1/kits/{kit_id}/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert data["item_type"] == "magazine"
    assert data["quantity"] == 3


def test_update_kit_item(client, sample_kit):
    """Test updating a kit item"""
    kit_id = sample_kit["id"]
    
    # Create an item
    create_response = client.post(
        f"/api/v1/kits/{kit_id}/items",
        json={
            "item_type": "optic",
            "make": "Generic",
            "model": "Old Model"
        }
    )
    item_id = create_response.json()["id"]
    
    # Update the item
    response = client.put(
        f"/api/v1/kits/{kit_id}/items/{item_id}",
        json={
            "make": "Vortex",
            "model": "Crossfire II",
            "notes": "Upgraded optic"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["make"] == "Vortex"
    assert data["model"] == "Crossfire II"
    assert data["notes"] == "Upgraded optic"
    assert data["item_type"] == "optic"  # Unchanged


def test_update_kit_item_status(client, sample_kit):
    """Test updating kit item status"""
    kit_id = sample_kit["id"]
    
    # Create an item
    create_response = client.post(
        f"/api/v1/kits/{kit_id}/items",
        json={"item_type": "tool", "make": "Craftsman"}
    )
    item_id = create_response.json()["id"]
    
    # Update status to lost
    response = client.put(
        f"/api/v1/kits/{kit_id}/items/{item_id}",
        json={"status": "lost"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "lost"


def test_delete_kit_item(client, sample_kit):
    """Test deleting a kit item"""
    kit_id = sample_kit["id"]
    
    # Create an item
    create_response = client.post(
        f"/api/v1/kits/{kit_id}/items",
        json={"item_type": "accessory", "make": "Generic"}
    )
    item_id = create_response.json()["id"]
    
    # Delete the item
    response = client.delete(f"/api/v1/kits/{kit_id}/items/{item_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/api/v1/kits/{kit_id}/items/{item_id}")
    assert get_response.status_code == 404


def test_kit_item_encryption(client, sample_kit):
    """Test that serial numbers are encrypted/decrypted properly"""
    kit_id = sample_kit["id"]
    
    test_serial = "SECRET-SERIAL-123"
    
    # Create item with serial number
    create_response = client.post(
        f"/api/v1/kits/{kit_id}/items",
        json={
            "item_type": "firearm",
            "serial_number": test_serial
        }
    )
    
    assert create_response.status_code == 201
    data = create_response.json()
    
    # Serial number should be returned decrypted
    assert data["serial_number"] == test_serial
    
    # Retrieve item again
    item_id = data["id"]
    get_response = client.get(f"/api/v1/kits/{kit_id}/items/{item_id}")
    assert get_response.status_code == 200
    assert get_response.json()["serial_number"] == test_serial


def test_kit_not_found_for_items(client):
    """Test that operations fail gracefully when kit doesn't exist"""
    nonexistent_kit_id = 99999
    
    # List items
    response = client.get(f"/api/v1/kits/{nonexistent_kit_id}/items")
    assert response.status_code == 404
    
    # Create item
    response = client.post(
        f"/api/v1/kits/{nonexistent_kit_id}/items",
        json={"item_type": "firearm"}
    )
    assert response.status_code == 404
    
    # Get item
    response = client.get(f"/api/v1/kits/{nonexistent_kit_id}/items/1")
    assert response.status_code == 404


def test_kit_item_not_found(client, sample_kit):
    """Test that operations fail gracefully when item doesn't exist"""
    kit_id = sample_kit["id"]
    nonexistent_item_id = 99999
    
    # Get item
    response = client.get(f"/api/v1/kits/{kit_id}/items/{nonexistent_item_id}")
    assert response.status_code == 404
    
    # Update item
    response = client.put(
        f"/api/v1/kits/{kit_id}/items/{nonexistent_item_id}",
        json={"make": "Test"}
    )
    assert response.status_code == 404
    
    # Delete item
    response = client.delete(f"/api/v1/kits/{kit_id}/items/{nonexistent_item_id}")
    assert response.status_code == 404


def test_multiple_items_same_type(client, sample_kit):
    """Test that a kit can have multiple items of the same type"""
    kit_id = sample_kit["id"]
    
    # Create multiple magazines
    for i in range(3):
        response = client.post(
            f"/api/v1/kits/{kit_id}/items",
            json={
                "item_type": "magazine",
                "make": "Ruger",
                "model": "BX-25",
                "friendly_name": f"Magazine #{i+1}",
                "serial_number": f"MAG-{i+1:03d}"
            }
        )
        assert response.status_code == 201
    
    # List all items
    response = client.get(f"/api/v1/kits/{kit_id}/items")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    
    # All should be magazines
    for item in data:
        assert item["item_type"] == "magazine"
