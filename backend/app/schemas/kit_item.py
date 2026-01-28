from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.kit_item import KitItemStatus


class KitItemBase(BaseModel):
    """Base kit item schema"""
    item_type: str = Field(..., description="Type of item (firearm, optic, case, magazine, tool, etc.)")
    make: Optional[str] = Field(None, description="Manufacturer/brand")
    model: Optional[str] = Field(None, description="Model name/number")
    friendly_name: Optional[str] = Field(None, description="User-friendly name for identification")
    photo_url: Optional[str] = Field(None, description="URL to item photo")
    quantity: Optional[int] = Field(1, description="Quantity (for accessories/magazines)")
    notes: Optional[str] = Field(None, description="Additional notes")


class KitItemCreate(KitItemBase):
    """Schema for creating a new kit item"""
    serial_number: Optional[str] = Field(None, description="Serial number (encrypted in database)")


class KitItemUpdate(BaseModel):
    """Schema for updating an existing kit item"""
    item_type: Optional[str] = Field(None, description="Type of item")
    make: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = Field(None, description="Serial number (encrypted in database)")
    friendly_name: Optional[str] = None
    photo_url: Optional[str] = None
    quantity: Optional[int] = None
    status: Optional[KitItemStatus] = None
    notes: Optional[str] = None


class KitItemResponse(KitItemBase):
    """Schema for kit item API responses"""
    id: int
    kit_id: int
    serial_number: Optional[str] = Field(None, description="Serial number (decrypted)")
    status: KitItemStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
