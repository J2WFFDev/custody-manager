import pytest
from datetime import datetime, timezone, timedelta
from app.core.security import create_access_token, verify_token


def test_create_access_token():
    """Test JWT token creation."""
    data = {"sub": "123", "email": "test@example.com"}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_token_valid():
    """Test JWT token verification with valid token."""
    data = {"sub": "123", "email": "test@example.com"}
    token = create_access_token(data)
    
    payload = verify_token(token)
    
    assert payload is not None
    assert payload["sub"] == "123"
    assert payload["email"] == "test@example.com"
    assert "exp" in payload


def test_verify_token_invalid():
    """Test JWT token verification with invalid token."""
    invalid_token = "invalid.token.here"
    
    payload = verify_token(invalid_token)
    
    assert payload is None


def test_create_access_token_with_custom_expiry():
    """Test JWT token creation with custom expiration time."""
    data = {"sub": "123"}
    expires_delta = timedelta(minutes=60)
    
    token = create_access_token(data, expires_delta=expires_delta)
    payload = verify_token(token)
    
    assert payload is not None
    assert payload["sub"] == "123"
    # Verify expiration is set
    assert "exp" in payload
    
    # Expiration should be roughly 60 minutes from now
    exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)
    time_diff = (exp_time - now).total_seconds()
    
    # Allow some tolerance (55-65 minutes)
    assert 55 * 60 <= time_diff <= 65 * 60
