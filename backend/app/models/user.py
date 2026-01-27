from sqlalchemy import Column, String, Boolean, Enum as SQLEnum
from app.models.base import BaseModel
import enum

class UserRole(str, enum.Enum):
    """User role enum for access control (AUTH-001)"""
    admin = "admin"
    armorer = "armorer"
    coach = "coach"
    volunteer = "volunteer"
    parent = "parent"

class User(BaseModel):
    """
    User model for OAuth authentication and role-based access control.
    
    Implements:
    - AUTH-001: Role assignment for access control
    - AUTH-002: Verified adult flag for off-site custody authorization
    
    Fields:
        id (int): Primary key, auto-generated (inherited from BaseModel)
        email (str): User's email address, unique and indexed
        name (str): User's full name from OAuth provider
        oauth_provider (str): OAuth provider ('google' or 'microsoft')
        oauth_id (str): OAuth provider's unique user ID, indexed
        role (UserRole): User's role (admin, armorer, coach, volunteer, parent)
        verified_adult (bool): Flag indicating if user is verified adult for off-site custody
        is_active (bool): Flag indicating if user account is active
        created_at (datetime): Timestamp when user was created (inherited from BaseModel)
        updated_at (datetime): Timestamp when user was last updated (inherited from BaseModel)
    """
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    oauth_provider = Column(String, nullable=False)  # 'google' or 'microsoft'
    oauth_id = Column(String, nullable=False, index=True)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.parent)
    verified_adult = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
