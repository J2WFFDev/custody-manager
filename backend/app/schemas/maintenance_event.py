from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MaintenanceOpenRequest(BaseModel):
    """Schema for opening maintenance on a kit"""
    kit_code: str = Field(..., description="Kit code to put into maintenance")
    notes: Optional[str] = Field(None, description="Notes about the maintenance")
    parts_replaced: Optional[str] = Field(None, description="Parts that need to be replaced")
    round_count: Optional[int] = Field(None, description="Round count at maintenance start")


class MaintenanceCloseRequest(BaseModel):
    """Schema for closing maintenance on a kit"""
    kit_code: str = Field(..., description="Kit code to close maintenance on")
    notes: Optional[str] = Field(None, description="Notes about the maintenance completion")
    parts_replaced: Optional[str] = Field(None, description="Parts that were replaced")
    round_count: Optional[int] = Field(None, description="Round count at maintenance completion")


class MaintenanceEventResponse(BaseModel):
    """Schema for maintenance event response"""
    id: int
    kit_id: int
    opened_by_id: int
    opened_by_name: str
    closed_by_id: Optional[int] = None
    closed_by_name: Optional[str] = None
    notes: Optional[str] = None
    parts_replaced: Optional[str] = None
    round_count: Optional[int] = None
    is_open: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MaintenanceOpenResponse(BaseModel):
    """Response for opening maintenance"""
    message: str
    event: MaintenanceEventResponse
    kit_name: str
    kit_code: str


class MaintenanceCloseResponse(BaseModel):
    """Response for closing maintenance"""
    message: str
    event: MaintenanceEventResponse
    kit_name: str
    kit_code: str
