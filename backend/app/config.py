from pydantic_settings import BaseSettings
from typing import Optional
import secrets
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "WilcoSS Custody Manager API"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # Database - Set via DATABASE_URL environment variable
    # Default is for local development only
    DATABASE_URL: str = "postgresql://localhost/custody_manager"
    
    # Security - Auto-generates secure key if not set
    # IMPORTANT: Set SECRET_KEY environment variable in production
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
