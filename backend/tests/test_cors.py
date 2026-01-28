import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


class TestCORSConfiguration:
    """Test CORS configuration for frontend requests"""
    
    def test_cors_preflight_request_from_production_frontend(self, monkeypatch):
        """Test that get_cors_origins includes production frontend URL when set via environment"""
        # Set production frontend URL via environment variable
        monkeypatch.setenv("FRONTEND_URL", "https://custody-mgr-fe-production.up.railway.app")
        
        # Create new settings instance to pick up the environment variable
        from app.config import Settings
        test_settings = Settings()
        test_settings.validate_secret_key()
        
        # Verify the production URL is in the CORS origins
        origins = test_settings.get_cors_origins()
        assert "https://custody-mgr-fe-production.up.railway.app" in origins
        
        # Verify localhost is still included for development
        assert "http://localhost:5173" in origins
        
        # Note: We only test the get_cors_origins() logic here, not the actual HTTP request
        # because the test client's app instance was created before we set the environment
        # variable. In production, FRONTEND_URL is set before the app starts.
    
    def test_cors_preflight_request_from_localhost(self, client):
        """Test that OPTIONS preflight request from localhost is allowed"""
        response = client.options(
            "/api/v1/auth/me",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization",
            }
        )
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-credentials"] == "true"
    
    def test_cors_actual_request_with_authorization(self, client):
        """Test that actual GET request with Authorization header includes CORS headers"""
        response = client.get(
            "/api/v1/auth/me",
            headers={
                "Origin": "http://localhost:5173",
                "Authorization": "Bearer fake-token-for-cors-test",
            }
        )
        
        # Even though auth might fail, CORS headers should be present
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-credentials" in response.headers
    
    def test_get_cors_origins_includes_frontend_url(self):
        """Test that get_cors_origins method includes FRONTEND_URL"""
        origins = settings.get_cors_origins()
        
        # Should include localhost for development
        assert "http://localhost:5173" in origins
        assert "http://localhost:3000" in origins
        
        # Should include FRONTEND_URL if set
        if settings.FRONTEND_URL:
            assert settings.FRONTEND_URL in origins
    
    def test_get_cors_origins_no_duplicates(self):
        """Test that get_cors_origins doesn't include duplicates"""
        origins = settings.get_cors_origins()
        
        # Check for duplicates
        assert len(origins) == len(set(origins))
    
    def test_get_cors_origins_no_empty_strings(self):
        """Test that get_cors_origins filters out empty strings"""
        origins = settings.get_cors_origins()
        
        # No empty strings or None values
        assert all(origin for origin in origins)
        assert None not in origins
        assert "" not in origins
    
    def test_cors_headers_on_health_endpoint(self, client):
        """Test that CORS headers are present on health check endpoint"""
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:5173"}
        )
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
    
    def test_cors_preflight_with_multiple_headers(self, client):
        """Test preflight request with multiple headers"""
        response = client.options(
            "/api/v1/auth/me",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "authorization, content-type",
            }
        )
        
        assert response.status_code == 200
        assert "access-control-allow-headers" in response.headers
        
        # Should allow all headers (*)
        allowed_headers = response.headers["access-control-allow-headers"].lower()
        # FastAPI/Starlette might return * or the specific headers
        assert "*" in allowed_headers or "authorization" in allowed_headers
