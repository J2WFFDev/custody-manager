"""
Test suite for Items API endpoints (item-first architecture)

This tests the new /api/v1/items endpoints that enable master inventory management.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models import Kit, Item

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_items.db"

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


def test_create_unassigned_item(client):
    """Test creating a new unassigned item in master inventory"""
    response = client.post(
        "/api/v1/items/",
        json={
            "item_type": "firearm",
            "make": "Ruger",
            "model": "10/22",
            "serial_number": "SN-UNASSIGNED-001",
            "friendly_name": "Rifle #1",
            "quantity": 1,
            "notes": "Unassigned firearm in inventory"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["item_type"] == "firearm"
    assert data["make"] == "Ruger"
    assert data["model"] == "10/22"
    assert data["status"] == "available"  # New items start as available
    assert data["current_kit_id"] is None  # Not assigned to any kit
    assert "id" in data


def test_create_item_assigned_to_kit(client, sample_kit):
    """Test creating an item that is immediately assigned to a kit"""
    kit_id = sample_kit["id"]
    
    response = client.post(
        "/api/v1/items/",
        json={
            "item_type": "optic",
            "make": "Vortex",
            "model": "Strike Eagle",
            "current_kit_id": kit_id,
            "friendly_name": "Optic #1"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["item_type"] == "optic"
    assert data["status"] == "assigned"  # Assigned status when created with kit
    assert data["current_kit_id"] == kit_id


def test_list_all_items(client):
    """Test listing all items in master inventory"""
    # Create several items
    client.post("/api/v1/items/", json={"item_type": "firearm", "make": "AR-15"})
    client.post("/api/v1/items/", json={"item_type": "optic", "make": "Vortex"})
    client.post("/api/v1/items/", json={"item_type": "magazine", "quantity": 5})
    
    response = client.get("/api/v1/items/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_filter_items_by_assigned_status(client, sample_kit):
    """Test filtering items by assigned/unassigned status"""
    kit_id = sample_kit["id"]
    
    # Create unassigned item
    client.post("/api/v1/items/", json={"item_type": "firearm", "make": "Unassigned"})
    
    # Create assigned item
    client.post("/api/v1/items/", json={
        "item_type": "optic",
        "make": "Assigned",
        "current_kit_id": kit_id
    })
    
    # Get unassigned items
    response = client.get("/api/v1/items/?assigned=false")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["make"] == "Unassigned"
    assert data[0]["current_kit_id"] is None
    
    # Get assigned items
    response = client.get("/api/v1/items/?assigned=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["make"] == "Assigned"
    assert data[0]["current_kit_id"] == kit_id


def test_assign_item_to_kit(client, sample_kit):
    """Test assigning an available item to a kit"""
    kit_id = sample_kit["id"]
    
    # Create unassigned item
    create_response = client.post(
        "/api/v1/items/",
        json={"item_type": "magazine", "make": "Magpul", "quantity": 3}
    )
    item_id = create_response.json()["id"]
    
    # Assign it to a kit
    response = client.post(
        f"/api/v1/items/{item_id}/assign",
        json={"kit_id": kit_id, "notes": "Assigned to primary kit"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "assigned"
    assert data["current_kit_id"] == kit_id
    assert "Assigned to primary kit" in data["notes"]


def test_unassign_item_from_kit(client, sample_kit):
    """Test removing an item from its kit"""
    kit_id = sample_kit["id"]
    
    # Create item assigned to kit
    create_response = client.post(
        "/api/v1/items/",
        json={"item_type": "case", "make": "Pelican", "current_kit_id": kit_id}
    )
    item_id = create_response.json()["id"]
    
    # Unassign it
    response = client.post(f"/api/v1/items/{item_id}/unassign")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "available"
    assert data["current_kit_id"] is None


def test_cannot_assign_non_available_item(client, sample_kit):
    """Test that only 'available' items can be assigned"""
    kit_id = sample_kit["id"]
    
    # Create item assigned to kit
    create_response = client.post(
        "/api/v1/items/",
        json={"item_type": "tool", "make": "Gerber", "current_kit_id": kit_id}
    )
    item_id = create_response.json()["id"]
    
    # Try to assign it again (should fail since it's already assigned)
    response = client.post(
        f"/api/v1/items/{item_id}/assign",
        json={"kit_id": kit_id}
    )
    
    assert response.status_code == 400
    assert "cannot be assigned" in response.json()["detail"].lower()


def test_delete_unassigned_item(client):
    """Test deleting an unassigned item"""
    # Create unassigned item
    create_response = client.post(
        "/api/v1/items/",
        json={"item_type": "accessory", "make": "Generic"}
    )
    item_id = create_response.json()["id"]
    
    # Delete it
    response = client.delete(f"/api/v1/items/{item_id}")
    
    assert response.status_code == 204
    
    # Verify it's gone
    get_response = client.get(f"/api/v1/items/{item_id}")
    assert get_response.status_code == 404


def test_cannot_delete_assigned_item(client, sample_kit):
    """Test that assigned items cannot be deleted"""
    kit_id = sample_kit["id"]
    
    # Create assigned item
    create_response = client.post(
        "/api/v1/items/",
        json={"item_type": "firearm", "make": "Springfield", "current_kit_id": kit_id}
    )
    item_id = create_response.json()["id"]
    
    # Try to delete it (should fail)
    response = client.delete(f"/api/v1/items/{item_id}")
    
    assert response.status_code == 400
    assert "assigned to a kit" in response.json()["detail"].lower()


def test_update_item(client):
    """Test updating an item's attributes"""
    # Create item
    create_response = client.post(
        "/api/v1/items/",
        json={"item_type": "firearm", "make": "OldMake", "model": "OldModel"}
    )
    item_id = create_response.json()["id"]
    
    # Update it
    response = client.put(
        f"/api/v1/items/{item_id}",
        json={"make": "NewMake", "model": "NewModel", "friendly_name": "Updated"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["make"] == "NewMake"
    assert data["model"] == "NewModel"
    assert data["friendly_name"] == "Updated"


def test_get_kit_items_endpoint(client, sample_kit):
    """Test the backward-compatible /kits/{kit_id}/items endpoint"""
    kit_id = sample_kit["id"]
    
    # Create items assigned to this kit using new endpoint
    client.post("/api/v1/items/", json={
        "item_type": "firearm",
        "make": "Item1",
        "current_kit_id": kit_id
    })
    client.post("/api/v1/items/", json={
        "item_type": "optic",
        "make": "Item2",
        "current_kit_id": kit_id
    })
    
    # Get kit items using old endpoint
    response = client.get(f"/api/v1/kits/{kit_id}/items")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # All items should belong to this kit
    assert all(item["current_kit_id"] == kit_id for item in data)


def test_item_reassignment_workflow(client):
    """Test complete workflow: create → assign → unassign → reassign"""
    # Create two kits
    kit1 = client.post("/api/v1/kits/", json={
        "code": "KIT-1",
        "name": "Kit 1"
    }).json()
    kit2 = client.post("/api/v1/kits/", json={
        "code": "KIT-2",
        "name": "Kit 2"
    }).json()
    
    # Create unassigned item
    item = client.post("/api/v1/items/", json={
        "item_type": "firearm",
        "make": "Movable Item"
    }).json()
    item_id = item["id"]
    
    # Verify it's available
    assert item["status"] == "available"
    assert item["current_kit_id"] is None
    
    # Assign to Kit 1
    response = client.post(f"/api/v1/items/{item_id}/assign", json={"kit_id": kit1["id"]})
    assert response.json()["current_kit_id"] == kit1["id"]
    assert response.json()["status"] == "assigned"
    
    # Unassign from Kit 1
    response = client.post(f"/api/v1/items/{item_id}/unassign")
    assert response.json()["current_kit_id"] is None
    assert response.json()["status"] == "available"
    
    # Assign to Kit 2
    response = client.post(f"/api/v1/items/{item_id}/assign", json={"kit_id": kit2["id"]})
    assert response.json()["current_kit_id"] == kit2["id"]
    assert response.json()["status"] == "assigned"
