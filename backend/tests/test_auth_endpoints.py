import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.core.security import create_access_token, create_refresh_token
from app.models.user import User

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(client):
    """Create a test user in the database"""
    db = TestingSessionLocal()
    user = User(
        email="test@example.com",
        name="Test User",
        oauth_provider="google",
        oauth_id="test123",
        role="parent",
        verified_adult=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.close()


def test_get_current_user_with_valid_token(client, test_user):
    """Test /auth/me endpoint with valid access token"""
    access_token = create_access_token(data={"sub": str(test_user.id), "email": test_user.email})
    
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["name"] == test_user.name
    assert data["role"] == test_user.role


def test_get_current_user_without_token(client):
    """Test /auth/me endpoint without authentication"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_current_user_with_invalid_token(client):
    """Test /auth/me endpoint with invalid token"""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_refresh_access_token_success(client, test_user):
    """Test /auth/refresh endpoint with valid refresh token"""
    refresh_token = create_refresh_token(data={"sub": str(test_user.id), "email": test_user.email})
    
    response = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == test_user.email


def test_refresh_with_access_token_fails(client, test_user):
    """Test /auth/refresh endpoint rejects access tokens"""
    access_token = create_access_token(data={"sub": str(test_user.id), "email": test_user.email})
    
    response = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 401
    assert "Invalid token type" in response.json()["detail"]


def test_refresh_without_token(client):
    """Test /auth/refresh endpoint without token"""
    response = client.post("/api/v1/auth/refresh")
    assert response.status_code == 401


def test_refresh_with_invalid_token(client):
    """Test /auth/refresh endpoint with invalid token"""
    response = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
