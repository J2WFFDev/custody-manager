import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.core.security import create_access_token, create_refresh_token
from app.models.user import User
from app.api.v1.endpoints.auth import state_serializer
from datetime import datetime, timezone
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from unittest.mock import patch, MagicMock

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


# Stateless OAuth State Token Tests
def test_state_token_generation():
    """Test that state tokens are generated and can be validated"""
    state_data = {
        "provider": "google",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    state_token = state_serializer.dumps(state_data)
    
    # Token should be a non-empty string
    assert isinstance(state_token, str)
    assert len(state_token) > 0
    
    # Token should be decodable
    decoded_data = state_serializer.loads(state_token)
    assert decoded_data["provider"] == "google"
    assert "timestamp" in decoded_data


def test_state_token_validation_success():
    """Test successful state token validation"""
    state_data = {
        "provider": "microsoft",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    state_token = state_serializer.dumps(state_data)
    
    # Validate with 600 second max age (same as in production)
    decoded_data = state_serializer.loads(state_token, max_age=600)
    assert decoded_data["provider"] == "microsoft"


def test_state_token_tampering_detection():
    """Test that tampered state tokens are rejected"""
    state_data = {
        "provider": "google",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    state_token = state_serializer.dumps(state_data)
    
    # Tamper with the token
    tampered_token = state_token[:-5] + "XXXXX"
    
    # Should raise BadSignature
    with pytest.raises(BadSignature):
        state_serializer.loads(tampered_token)


def test_state_token_expiration():
    """Test that expired state tokens are rejected"""
    state_data = {
        "provider": "google",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    state_token = state_serializer.dumps(state_data)
    
    # Use negative max_age to test expiration instantly
    with pytest.raises(SignatureExpired):
        state_serializer.loads(state_token, max_age=-1)


def test_google_login_redirects_to_google(client):
    """Test that /auth/google/login redirects to Google OAuth"""
    response = client.get("/api/v1/auth/google/login", follow_redirects=False)
    
    assert response.status_code == 307  # Redirect status
    assert "location" in response.headers
    
    location = response.headers["location"]
    assert "accounts.google.com" in location
    assert "client_id" in location
    assert "redirect_uri" in location
    assert "state" in location
    assert "scope=openid" in location


def test_microsoft_login_redirects_to_microsoft(client):
    """Test that /auth/microsoft/login redirects to Microsoft OAuth"""
    response = client.get("/api/v1/auth/microsoft/login", follow_redirects=False)
    
    assert response.status_code == 307  # Redirect status
    assert "location" in response.headers
    
    location = response.headers["location"]
    assert "login.microsoftonline.com" in location
    assert "client_id" in location
    assert "redirect_uri" in location
    assert "state" in location
    assert "scope=openid" in location


def test_google_callback_missing_code(client):
    """Test that callback fails without code parameter"""
    state_data = {
        "provider": "google",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    state_token = state_serializer.dumps(state_data)
    
    response = client.get(f"/api/v1/auth/google/callback?state={state_token}")
    assert response.status_code == 400
    assert "Missing code or state parameter" in response.json()["detail"]


def test_google_callback_missing_state(client):
    """Test that callback fails without state parameter"""
    response = client.get("/api/v1/auth/google/callback?code=test_code")
    assert response.status_code == 400
    assert "Missing code or state parameter" in response.json()["detail"]


def test_google_callback_invalid_state(client):
    """Test that callback fails with invalid state"""
    response = client.get("/api/v1/auth/google/callback?code=test_code&state=invalid_state")
    assert response.status_code == 400
    assert "Invalid state" in response.json()["detail"]


def test_google_callback_expired_state(client):
    """Test that callback fails with expired state"""
    state_data = {
        "provider": "google",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    state_token = state_serializer.dumps(state_data)
    
    # Mock the state_serializer.loads to raise SignatureExpired
    with patch('app.api.v1.endpoints.auth.state_serializer.loads') as mock_loads:
        mock_loads.side_effect = SignatureExpired("Signature expired")
        
        response = client.get(f"/api/v1/auth/google/callback?code=test_code&state={state_token}")
        assert response.status_code == 400
        assert "State expired" in response.json()["detail"]


def test_google_callback_wrong_provider_in_state(client):
    """Test that callback fails when state contains wrong provider"""
    state_data = {
        "provider": "microsoft",  # Wrong provider
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    state_token = state_serializer.dumps(state_data)
    
    # Mock successful token exchange to isolate state validation test
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"access_token": "mock_token"}
    
    with patch('requests.post', return_value=mock_response):
        response = client.get(f"/api/v1/auth/google/callback?code=test_code&state={state_token}")
        assert response.status_code == 400
        assert "Invalid state parameter - provider mismatch" in response.json()["detail"]


def test_microsoft_callback_missing_parameters(client):
    """Test that Microsoft callback fails without required parameters"""
    response = client.get("/api/v1/auth/microsoft/callback")
    assert response.status_code == 400
    assert "Missing code or state parameter" in response.json()["detail"]


def test_oauth_error_parameter(client):
    """Test that OAuth errors are handled properly"""
    state_data = {
        "provider": "google",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    state_token = state_serializer.dumps(state_data)
    
    response = client.get(f"/api/v1/auth/google/callback?error=access_denied&state={state_token}")
    assert response.status_code == 400
    assert "OAuth error: access_denied" in response.json()["detail"]
