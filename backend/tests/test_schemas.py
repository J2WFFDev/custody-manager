import pytest
from app.schemas.user import UserBase, UserCreate, UserResponse, Token
from datetime import datetime


def test_user_base_schema():
    """Test UserBase schema validation."""
    user_data = {
        "email": "test@example.com",
        "name": "Test User"
    }
    
    user = UserBase(**user_data)
    
    assert user.email == "test@example.com"
    assert user.name == "Test User"


def test_user_create_schema():
    """Test UserCreate schema validation."""
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "oauth_provider": "google",
        "oauth_id": "123456789"
    }
    
    user = UserCreate(**user_data)
    
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.oauth_provider == "google"
    assert user.oauth_id == "123456789"
    assert user.role == "parent"  # Default role


def test_user_create_schema_custom_role():
    """Test UserCreate schema with custom role."""
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "oauth_provider": "microsoft",
        "oauth_id": "987654321",
        "role": "coach"
    }
    
    user = UserCreate(**user_data)
    
    assert user.role == "coach"


def test_user_response_schema():
    """Test UserResponse schema."""
    user_data = {
        "id": 1,
        "email": "test@example.com",
        "name": "Test User",
        "role": "parent",
        "verified_adult": False,
        "is_active": True,
        "created_at": datetime.now()
    }
    
    user = UserResponse(**user_data)
    
    assert user.id == 1
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.role == "parent"
    assert user.verified_adult is False
    assert user.is_active is True


def test_token_schema():
    """Test Token schema."""
    user_data = {
        "id": 1,
        "email": "test@example.com",
        "name": "Test User",
        "role": "parent",
        "verified_adult": False,
        "is_active": True,
        "created_at": datetime.now()
    }
    
    token_data = {
        "access_token": "sample.jwt.token",
        "user": user_data
    }
    
    token = Token(**token_data)
    
    assert token.access_token == "sample.jwt.token"
    assert token.token_type == "bearer"
    assert token.user.email == "test@example.com"


def test_invalid_email():
    """Test that invalid email raises validation error."""
    with pytest.raises(Exception):  # Pydantic ValidationError
        UserBase(email="invalid-email", name="Test User")
