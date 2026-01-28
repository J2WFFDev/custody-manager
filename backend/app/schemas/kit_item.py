from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.kit_item import ItemStatus, ItemType, KitItemStatus  # Import both for backward compatibility


class ItemBase(BaseModel):
    """Base item schema"""
    item_type: str = Field(..., description="Type of item (firearm, optic, case, magazine, tool, accessory, other)")
    make: Optional[str] = Field(None, description="Manufacturer/brand")
    model: Optional[str] = Field(None, description="Model name/number")
    friendly_name: Optional[str] = Field(None, description="User-friendly name for identification")
    photo_url: Optional[str] = Field(None, description="URL to item photo")
    quantity: Optional[int] = Field(1, description="Quantity (for accessories/magazines)")
    notes: Optional[str] = Field(None, description="Additional notes")


class ItemCreate(ItemBase):
    """Schema for creating a new item"""
    serial_number: Optional[str] = Field(None, description="Serial number (encrypted in database)")
    current_kit_id: Optional[int] = Field(None, description="Optional kit to assign item to on creation")


class ItemUpdate(BaseModel):
    """Schema for updating an existing item"""
    item_type: Optional[str] = Field(None, description="Type of item")
    make: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = Field(None, description="Serial number (encrypted in database)")
    friendly_name: Optional[str] = None
    photo_url: Optional[str] = None
    quantity: Optional[int] = None
    status: Optional[ItemStatus] = None
    notes: Optional[str] = None


class ItemResponse(ItemBase):
    """Schema for item API responses"""
    id: int
    current_kit_id: Optional[int] = Field(None, description="ID of kit this item is assigned to (null if unassigned)")
    serial_number: Optional[str] = Field(None, description="Serial number (decrypted)")
    status: ItemStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ItemAssignRequest(BaseModel):
    """Schema for assigning an item to a kit"""
    kit_id: int = Field(..., description="ID of kit to assign item to")
    notes: Optional[str] = Field(None, description="Optional notes about the assignment")


# Backward compatibility aliases
KitItemBase = ItemBase
KitItemCreate = ItemCreate
KitItemUpdate = ItemUpdate
KitItemResponse = ItemResponse
