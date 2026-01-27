from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    oauth_provider: str
    oauth_id: str
    role: UserRole = UserRole.parent  # Default role

class UserResponse(UserBase):
    id: int
    role: UserRole
    verified_adult: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
        use_enum_values = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class UserUpdate(BaseModel):
    role: Optional[UserRole] = None
    verified_adult: Optional[bool] = None
