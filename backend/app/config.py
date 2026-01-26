from pydantic_settings import BaseSettings
from typing import List
import secrets

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "WilcoSS Custody Manager API"
    DEBUG: bool = True  # Default to development mode, set to False in production
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # Database
    DATABASE_URL: str = "postgresql://localhost/custody_manager"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)  # Auto-generate if not provided
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS - Allow production frontend
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://custody-manager.vercel.app",  # Add your Vercel domain
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
    
    # OAuth - Google
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
    
    # OAuth - Microsoft
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    MICROSOFT_TENANT_ID: str = "common"  # 'common', 'organizations', 'consumers', or tenant GUID
    MICROSOFT_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/microsoft/callback"
    
    # Frontend URL for redirect after auth
    FRONTEND_URL: str = "http://localhost:5173"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def get_microsoft_metadata_url(self) -> str:
        """Get Microsoft OAuth metadata URL with validated tenant ID."""
        tenant_id = self.MICROSOFT_TENANT_ID or "common"
        return f'https://login.microsoftonline.com/{tenant_id}/v2.0/.well-known/openid-configuration'

settings = Settings()
