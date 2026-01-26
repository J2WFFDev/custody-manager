from sqlalchemy import Column, String, Boolean
from app.models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    oauth_provider = Column(String, nullable=False)  # 'google' or 'microsoft'
    oauth_id = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False, default="parent")  # 'admin', 'armorer', 'coach', 'parent'
    verified_adult = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
