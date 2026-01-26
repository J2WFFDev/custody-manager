from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class KitBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    serial_number: Optional[str] = None
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.kit import KitStatus

class KitBase(BaseModel):
    """Base kit schema"""
    code: str = Field(..., description="Unique kit code (QR code or manual entry)")
    name: str = Field(..., description="Kit name")
    description: Optional[str] = Field(None, description="Kit description")

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
class KitResponse(KitBase):
    """Schema for kit API responses"""
    id: int
    status: KitStatus
    current_custodian_id: Optional[int] = None
    current_custodian_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class KitLookupResponse(BaseModel):
    """Schema for kit lookup endpoint response"""
    id: int
    code: str
    name: str
    description: Optional[str] = None
    status: KitStatus
    custodian: Optional[str] = Field(None, description="Current custodian name if checked out")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
