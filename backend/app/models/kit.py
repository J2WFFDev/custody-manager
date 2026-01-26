from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Kit(BaseModel):
    __tablename__ = "kits"
    
    qr_code = Column(String(255), unique=True, nullable=False, index=True)
    serial_number_encrypted = Column(Text)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), nullable=False, default='available', index=True)
    location = Column(String(255))
    current_custodian_id = Column(Integer, ForeignKey('users.id'), index=True)
    
    # Relationships
    current_custodian = relationship("User", foreign_keys=[current_custodian_id])
    
    def __repr__(self):
        return f"<Kit {self.name} ({self.qr_code}) - {self.status}>"
