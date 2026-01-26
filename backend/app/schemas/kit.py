from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class KitStatus(str, Enum):
    """Kit status enum for API responses"""
    AVAILABLE = "available"
    CHECKED_OUT = "checked_out"
    IN_MAINTENANCE = "in_maintenance"
    LOST = "lost"

class KitBase(BaseModel):
    """Base kit schema"""
    code: str = Field(..., description="Unique kit code (QR code or manual entry)")
    name: str = Field(..., description="Kit name")
    description: Optional[str] = Field(None, description="Kit description")

class KitCreate(KitBase):
    """Schema for creating a new kit"""
    pass

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
