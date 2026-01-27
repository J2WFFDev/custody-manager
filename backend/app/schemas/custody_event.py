from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.custody_event import CustodyEventType

class CustodyCheckoutRequest(BaseModel):
    """Request schema for checking out a kit"""
    kit_code: str = Field(..., description="Kit code (scanned from QR or manually entered)")
    custodian_name: str = Field(..., description="Name of person receiving custody")
    custodian_id: Optional[int] = Field(None, description="User ID if custodian is in system")
    notes: Optional[str] = Field(None, description="Optional notes")

class CustodyEventResponse(BaseModel):
    """Response schema for custody events"""
    id: int
    event_type: CustodyEventType
    kit_id: int
    initiated_by_id: int
    initiated_by_name: str
    custodian_id: Optional[int]
    custodian_name: str
    notes: Optional[str]
    location_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class CustodyCheckoutResponse(BaseModel):
    """Response schema for successful checkout"""
    message: str
    event: CustodyEventResponse
    kit_name: str
    kit_code: str

class CustodyTransferRequest(BaseModel):
    """Request schema for transferring custody of a kit"""
    kit_code: str = Field(..., description="Kit code (scanned from QR or manually entered)")
    new_custodian_name: str = Field(..., description="Name of person receiving custody")
    new_custodian_id: Optional[int] = Field(None, description="User ID if new custodian is in system")
    notes: Optional[str] = Field(None, description="Optional notes about the transfer")

class CustodyTransferResponse(BaseModel):
    """Response schema for successful custody transfer"""
    message: str
    event: CustodyEventResponse
    kit_name: str
    kit_code: str
    previous_custodian: str
    new_custodian: str
