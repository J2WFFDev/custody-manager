from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class KitBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    serial_number: Optional[str] = None

class KitCreate(KitBase):
    """Schema for creating a new kit"""
    pass

class KitUpdate(BaseModel):
    """Schema for updating an existing kit"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    serial_number: Optional[str] = None

class KitResponse(KitBase):
    """Schema for kit response"""
    id: int
    qr_code: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
