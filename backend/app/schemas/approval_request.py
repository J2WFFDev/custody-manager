from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.approval_request import ApprovalStatus

class OffSiteCheckoutRequest(BaseModel):
    """Request schema for off-site checkout approval request"""
    kit_code: str = Field(..., description="Kit code (scanned from QR or manually entered)")
    custodian_name: str = Field(..., description="Name of person receiving custody (e.g., athlete/child)")
    custodian_id: Optional[int] = Field(None, description="User ID if custodian is in system")
    notes: Optional[str] = Field(None, description="Optional notes about the request")

class ApprovalDecisionRequest(BaseModel):
    """Request schema for approving/denying an off-site checkout request"""
    approval_request_id: int = Field(..., description="ID of the approval request")
    approve: bool = Field(..., description="True to approve, False to deny")
    denial_reason: Optional[str] = Field(None, description="Reason for denial (required if approve=False)")

class ApprovalRequestResponse(BaseModel):
    """Response schema for approval requests"""
    id: int
    kit_id: int
    kit_name: str
    kit_code: str
    requester_id: int
    requester_name: str
    custodian_id: Optional[int]
    custodian_name: str
    status: ApprovalStatus
    approver_id: Optional[int]
    approver_name: Optional[str]
    approver_role: Optional[str]
    notes: Optional[str]
    denial_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class OffSiteCheckoutResponse(BaseModel):
    """Response schema for off-site checkout request submission"""
    message: str
    approval_request: ApprovalRequestResponse

class ApprovalDecisionResponse(BaseModel):
    """Response schema for approval decision"""
    message: str
    approval_request: ApprovalRequestResponse
    custody_event: Optional[dict] = None  # Present if approved and custody transferred
