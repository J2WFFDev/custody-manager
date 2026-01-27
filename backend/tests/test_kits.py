import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models.kit import Kit

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

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

def test_create_kit(client):
    """Test creating a new kit with QR code generation"""
    response = client.post(
        "/api/v1/kits/",
        json={
            "code": "TEST-001",
            "name": "Test Kit 1",
            "description": "A test kit",
            "serial_number": "SN-12345"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "TEST-001"
    assert data["name"] == "Test Kit 1"
    assert data["description"] == "A test kit"
    assert data["serial_number"] == "SN-12345"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_list_kits(client):
    """Test listing kits"""
    # Create a kit first
    client.post(
        "/api/v1/kits/",
        json={"code": "KIT-001", "name": "Kit 1", "description": "First kit"}
    )
    client.post(
        "/api/v1/kits/",
        json={"code": "KIT-002", "name": "Kit 2", "description": "Second kit"}
    )
    
    response = client.get("/api/v1/kits/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Kit 1"
    assert data[1]["name"] == "Kit 2"

def test_get_kit_by_id(client):
    """Test getting a kit by ID"""
    # Create a kit
    create_response = client.post(
        "/api/v1/kits/",
        json={"code": "TEST-KIT", "name": "Test Kit", "description": "Test"}
    )
    kit_id = create_response.json()["id"]
    
    # Get the kit
    response = client.get(f"/api/v1/kits/{kit_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == kit_id
    assert data["name"] == "Test Kit"

def test_get_kit_by_qr_code(client):
    """Test getting a kit by QR code"""
    # Create a kit
    create_response = client.post(
        "/api/v1/kits/",
        json={"code": "QR-TEST-001", "name": "Test Kit", "description": "Test"}
    )
    code = create_response.json()["code"]
    
    # Get the kit by code
    response = client.get(f"/api/v1/kits/code/{code}")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == code
    assert data["name"] == "Test Kit"

def test_update_kit(client):
    """Test updating a kit"""
    # Create a kit
    create_response = client.post(
        "/api/v1/kits/",
        json={"code": "UPDATE-TEST", "name": "Original Name", "description": "Original"}
    )
    kit_id = create_response.json()["id"]
    
    # Update the kit
    response = client.put(
        f"/api/v1/kits/{kit_id}",
        json={"name": "Updated Name", "description": "Updated"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["description"] == "Updated"

def test_delete_kit(client):
    """Test deleting a kit"""
    # Create a kit
    create_response = client.post(
        "/api/v1/kits/",
        json={"code": "DELETE-TEST", "name": "To Delete", "description": "Delete me"}
    )
    kit_id = create_response.json()["id"]
    
    # Delete the kit
    response = client.delete(f"/api/v1/kits/{kit_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/api/v1/kits/{kit_id}")
    assert get_response.status_code == 404

def test_get_qr_image_png(client):
    """Test getting QR code image as PNG"""
    # Create a kit
    create_response = client.post(
        "/api/v1/kits/",
        json={"code": "PNG-TEST", "name": "Test Kit", "description": "Test"}
    )
    kit_id = create_response.json()["id"]
    
    # Get QR image as PNG
    response = client.get(f"/api/v1/kits/{kit_id}/qr-image?format=png")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert len(response.content) > 0

def test_get_qr_image_svg(client):
    """Test getting QR code image as SVG"""
    # Create a kit
    create_response = client.post(
        "/api/v1/kits/",
        json={"code": "SVG-TEST", "name": "Test Kit", "description": "Test"}
    )
    kit_id = create_response.json()["id"]
    
    # Get QR image as SVG
    response = client.get(f"/api/v1/kits/{kit_id}/qr-image?format=svg")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/svg+xml"
    assert len(response.content) > 0

def test_qr_code_uniqueness(client):
    """Test that QR codes are unique"""
    # Create multiple kits
    codes = set()
    for i in range(10):
        response = client.post(
            "/api/v1/kits/",
            json={"code": f"KIT-{i:03d}", "name": f"Kit {i}", "description": f"Kit number {i}"}
        )
        assert response.status_code == 201
        code = response.json()["code"]
        codes.add(code)
    
    # All codes should be unique
    assert len(codes) == 10

def test_kit_not_found(client):
    """Test 404 error when kit is not found"""
    response = client.get("/api/v1/kits/999")
    assert response.status_code == 404
    
    response = client.get("/api/v1/kits/code/NONEXISTENT")
    assert response.status_code == 404
    
    response = client.get("/api/v1/kits/999/qr-image")
    assert response.status_code == 404
