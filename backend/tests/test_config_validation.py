import pytest
import os
from unittest.mock import patch


def test_secret_key_validation_production_missing():
    """Test that missing SECRET_KEY raises error in production"""
    with patch.dict(os.environ, {"RAILWAY_ENVIRONMENT": "production", "SECRET_KEY": ""}):
        # Clear the module cache to force reload
        import sys
        if 'app.config' in sys.modules:
            del sys.modules['app.config']
        
        with pytest.raises(ValueError, match="SECRET_KEY must be set in environment variables"):
            from app.config import settings


def test_secret_key_validation_too_short():
    """Test that short SECRET_KEY raises error"""
    with patch.dict(os.environ, {"SECRET_KEY": "short"}):
        # Clear the module cache to force reload
        import sys
        if 'app.config' in sys.modules:
            del sys.modules['app.config']
        
        with pytest.raises(ValueError, match="SECRET_KEY must be at least 32 characters long"):
            from app.config import settings


def test_secret_key_validation_valid():
    """Test that valid SECRET_KEY passes validation"""
    valid_key = "a" * 32  # 32 character key
    with patch.dict(os.environ, {"SECRET_KEY": valid_key}):
        # Clear the module cache to force reload
        import sys
        if 'app.config' in sys.modules:
            del sys.modules['app.config']
        
        from app.config import settings
        assert settings.SECRET_KEY == valid_key


def test_secret_key_auto_generated_in_development():
    """Test that SECRET_KEY is auto-generated in development when missing"""
    with patch.dict(os.environ, {"RAILWAY_ENVIRONMENT": "development", "SECRET_KEY": ""}):
        # Clear the module cache to force reload
        import sys
        if 'app.config' in sys.modules:
            del sys.modules['app.config']
        
        from app.config import settings
        # Should auto-generate a key in development
        assert len(settings.SECRET_KEY) >= 32
