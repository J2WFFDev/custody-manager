from pydantic_settings import BaseSettings
from typing import List
import secrets
import os
import base64

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "WilcoSS Custody Manager API"
    DEBUG: bool = False  # Default to production mode
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("RAILWAY_ENVIRONMENT", "development")
    
    # Database
    DATABASE_URL: str = "postgresql://localhost/custody_manager"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)  # Auto-generate if not provided
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Field-level encryption (AUDIT-003)
    ENCRYPTION_KEY: str = secrets.token_urlsafe(32)  # Auto-generate if not provided
    # Field Encryption - for sensitive database fields (AUDIT-003)
    ENCRYPTION_KEY: str = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()  # Auto-generate if not provided
    
    # CORS - Allow production frontend
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://custody-manager.vercel.app",
        "https://*.vercel.app",  # Allow Vercel preview deployments
    ]
    
    # OAuth - Google
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:5173/auth/google/callback"
    
    # OAuth - Microsoft
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    MICROSOFT_TENANT_ID: str = "common"
    MICROSOFT_REDIRECT_URI: str = "http://localhost:5173/auth/microsoft/callback"
    
    # Frontend URL
    FRONTEND_URL: str = "http://localhost:5173"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def get_microsoft_metadata_url(self) -> str:
        """Get Microsoft OAuth metadata URL with validated tenant ID."""
        tenant_id = self.MICROSOFT_TENANT_ID or "common"
        return f'https://login.microsoftonline.com/{tenant_id}/v2.0/.well-known/openid-configuration'

settings = Settings()
