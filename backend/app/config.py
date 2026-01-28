from pydantic_settings import BaseSettings
from typing import List
import secrets
import os
import base64
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "WilcoSS Custody Manager API"
    DEBUG: bool = False  # Default to production mode
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("RAILWAY_ENVIRONMENT", "development")
    
    # Database
    DATABASE_URL: str = "postgresql://localhost/custody_manager"
    
    # Security
    SECRET_KEY: str = ""  # Must be set via environment variable
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Field-level encryption (AUDIT-003)
    ENCRYPTION_KEY: str = secrets.token_urlsafe(32)  # Auto-generate if not provided
    # Field Encryption - for sensitive database fields (AUDIT-003)
    ENCRYPTION_KEY: str = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()  # Auto-generate if not provided
    
    # Frontend URL
    FRONTEND_URL: str = "http://localhost:5173"
    
    # CORS - Will be built dynamically from FRONTEND_URL
    BACKEND_CORS_ORIGINS: List[str] = []
    
    # OAuth - Google
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:5173/auth/google/callback"
    
    # OAuth - Microsoft
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    MICROSOFT_TENANT_ID: str = "common"
    MICROSOFT_REDIRECT_URI: str = "http://localhost:5173/auth/microsoft/callback"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def get_cors_origins(self) -> List[str]:
        """Build comprehensive CORS origins list including frontend URL and development URLs."""
        # Start with base development origins
        allowed_origins = [
            "http://localhost:5173",  # Vite dev server
            "http://localhost:3000",  # Alternative dev port
        ]
        
        # Add production frontend URL if set and not already in list
        if self.FRONTEND_URL and self.FRONTEND_URL not in allowed_origins:
            allowed_origins.append(self.FRONTEND_URL)
        
        # Add any CORS origins from environment variable
        if self.BACKEND_CORS_ORIGINS:
            for origin in self.BACKEND_CORS_ORIGINS:
                if origin and origin not in allowed_origins:
                    allowed_origins.append(origin)
        
        # Filter out empty strings and None values
        allowed_origins = [origin for origin in allowed_origins if origin]
        
        logger.info(f"CORS allowed origins: {allowed_origins}")
        return allowed_origins
    
    def get_microsoft_metadata_url(self) -> str:
        """Get Microsoft OAuth metadata URL with validated tenant ID."""
        tenant_id = self.MICROSOFT_TENANT_ID or "common"
        return f'https://login.microsoftonline.com/{tenant_id}/v2.0/.well-known/openid-configuration'
    
    def validate_secret_key(self) -> None:
        """Validate that SECRET_KEY is properly configured for OAuth session security."""
        if not self.SECRET_KEY:
            # For development, auto-generate but warn
            if self.ENVIRONMENT == "development":
                self.SECRET_KEY = secrets.token_urlsafe(32)
                logger.warning("Using auto-generated SECRET_KEY for development. Set SECRET_KEY in .env for production.")
            else:
                raise ValueError(
                    "SECRET_KEY must be set in environment variables for production. "
                    "OAuth session management requires a persistent SECRET_KEY. "
                    "Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                )
        
        # Validate minimum length (32 characters recommended)
        if len(self.SECRET_KEY) < 32:
            raise ValueError(
                f"SECRET_KEY must be at least 32 characters long (current: {len(self.SECRET_KEY)}). "
                "Generate a secure key with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )

settings = Settings()
# Validate SECRET_KEY on startup
settings.validate_secret_key()
