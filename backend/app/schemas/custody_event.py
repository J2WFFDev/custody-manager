from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from app.models.custody_event import CustodyEventType

class CustodyCheckoutRequest(BaseModel):
    """Request schema for checking out a kit"""
    kit_code: str = Field(..., description="Kit code (scanned from QR or manually entered)")
    custodian_name: str = Field(..., description="Name of person receiving custody")
    custodian_id: Optional[int] = Field(None, description="User ID if custodian is in system")
    notes: Optional[str] = Field(None, description="Optional notes")
    expected_return_date: Optional[date] = Field(None, description="Expected return date for soft warnings")

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
    expected_return_date: Optional[date]
    created_at: datetime
    
    class Config:
        from_attributes = True

class CustodyCheckoutResponse(BaseModel):
    """Response schema for successful checkout"""
    message: str
    event: CustodyEventResponse
    kit_name: str
    kit_code: str

class EventTimelineResponse(BaseModel):
    """Response schema for event timeline queries"""
    events: List[CustodyEventResponse]
    total: int
    kit_id: Optional[int] = None
    kit_name: Optional[str] = None
    kit_code: Optional[str] = None
    user_id: Optional[int] = None
    user_name: Optional[str] = None

class LostFoundRequest(BaseModel):
    """Request schema for reporting a kit as lost or found"""
    kit_code: str = Field(..., description="Kit code (scanned from QR or manually entered)")
    notes: Optional[str] = Field(None, description="Optional notes about circumstances")


class LostFoundResponse(BaseModel):
    """Response schema for lost/found operations"""
    message: str
    event: CustodyEventResponse
    kit_name: str
    kit_code: str
