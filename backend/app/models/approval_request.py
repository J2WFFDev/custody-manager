from sqlalchemy import Column, String, Integer, ForeignKey, Enum as SQLEnum, Boolean
from app.models.base import BaseModel
import enum

class ApprovalStatus(str, enum.Enum):
    """Approval request status"""
    pending = "pending"
    approved = "approved"
    denied = "denied"

class ApprovalRequest(BaseModel):
    __tablename__ = "approval_requests"
    
    # Kit being requested for off-site checkout
    kit_id = Column(Integer, ForeignKey("kits.id"), nullable=False, index=True)
    
    # User requesting the off-site checkout (e.g., Parent)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    requester_name = Column(String(200), nullable=False)
    
    # User who will have custody (e.g., athlete/child)
    custodian_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    custodian_name = Column(String(200), nullable=False)
    
    # Approval status
    status = Column(SQLEnum(ApprovalStatus), nullable=False, default=ApprovalStatus.pending)
    
    # Who approved/denied (Armorer or Coach)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approver_name = Column(String(200), nullable=True)
    approver_role = Column(String(50), nullable=True)  # Track which role approved
    
    # Request details
    notes = Column(String(1000), nullable=True)
    denial_reason = Column(String(500), nullable=True)
