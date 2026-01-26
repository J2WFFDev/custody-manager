from sqlalchemy import Column, Integer, String, Boolean
from app.models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    oauth_provider = Column(String(50), nullable=False)
    oauth_id = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, index=True)
    verified_adult = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
