from sqlalchemy import Column, String, Text
from app.models.base import BaseModel

class Kit(BaseModel):
    __tablename__ = "kits"
    
    # QR code (unique alphanumeric identifier, not exposing serial numbers per QR-004)
    qr_code = Column(String(50), unique=True, nullable=False, index=True)
    
    # Optional fields for kit details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Serial number should be encrypted per AUDIT-003 (not implemented yet)
    # For now, we store it as a regular field
    serial_number = Column(String(255), nullable=True)
