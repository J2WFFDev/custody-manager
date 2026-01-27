"""
Approval service - handles off-site checkout approval logic
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional, List

from app.models.approval_request import ApprovalRequest, ApprovalStatus
from app.models.custody_event import CustodyEvent, CustodyEventType
from app.models.kit import Kit, KitStatus
from app.models.user import User


def create_offsite_checkout_request(
    db: Session,
    kit_code: str,
    custodian_name: str,
    requester_user: User,
    custodian_id: Optional[int] = None,
    notes: Optional[str] = None
) -> tuple[ApprovalRequest, Kit]:
    """
    Create an off-site checkout approval request.
    
    Implements CUSTODY-011:
    - As a Parent, I want to check out a kit for my child to take off-site
    
    Args:
        db: Database session
        kit_code: Kit code (from QR scan or manual entry)
        custodian_name: Name of person receiving custody
        requester_user: User requesting the checkout (must have verified_adult flag)
        custodian_id: Optional user ID if custodian is in system
        notes: Optional notes
        
    Returns:
        Tuple of (approval_request, kit)
        
    Raises:
        HTTPException: If kit not found, already checked out, or user not verified adult
    """
    # Verify requester has verified_adult flag (AUTH-002)
    if not requester_user.verified_adult:
        raise HTTPException(
            status_code=403,
            detail="Only verified adults can request off-site checkout. Please contact an administrator."
        )
    
    # Find kit by code
    kit = db.query(Kit).filter(Kit.code == kit_code).first()
    if not kit:
        raise HTTPException(status_code=404, detail=f"Kit with code '{kit_code}' not found")
    
    # Check kit status - must be available
    if kit.status != KitStatus.available:
        raise HTTPException(
            status_code=400,
            detail=f"Kit is currently {kit.status} and cannot be requested for off-site checkout"
        )
    
    # Check if there's already a pending approval request for this kit
    existing_request = db.query(ApprovalRequest).filter(
        ApprovalRequest.kit_id == kit.id,
        ApprovalRequest.status == ApprovalStatus.pending
    ).first()
    
    if existing_request:
        raise HTTPException(
            status_code=400,
            detail=f"There is already a pending approval request for this kit"
        )
    
    # Create approval request
    approval_request = ApprovalRequest(
        kit_id=kit.id,
        requester_id=requester_user.id,
        requester_name=requester_user.name,
        custodian_id=custodian_id,
        custodian_name=custodian_name,
        notes=notes,
        status=ApprovalStatus.pending
    )
    
    # Save to database
    db.add(approval_request)
    db.commit()
    db.refresh(approval_request)
    
    return approval_request, kit


def approve_or_deny_offsite_request(
    db: Session,
    approval_request_id: int,
    approver_user: User,
    approve: bool,
    denial_reason: Optional[str] = None
) -> tuple[ApprovalRequest, Optional[CustodyEvent], Optional[Kit]]:
    """
    Approve or deny an off-site checkout request.
    
    Implements CUSTODY-002 and CUSTODY-003:
    - As an Armorer, I want to approve off-site checkout requests
    - As a Coach, I want to approve off-site checkout requests
    
    Args:
        db: Database session
        approval_request_id: ID of the approval request
        approver_user: User approving/denying (must be Armorer or Coach)
        approve: True to approve, False to deny
        denial_reason: Reason for denial (required if approve=False)
        
    Returns:
        Tuple of (approval_request, custody_event, kit)
        custody_event is None if request was denied
        
    Raises:
        HTTPException: If request not found, already processed, or user lacks permission
    """
    # Verify permissions - only Armorer or Coach can approve/deny
    allowed_roles = ["armorer", "coach", "admin"]
    if approver_user.role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail=f"Only Armorer or Coach can approve/deny off-site checkout requests"
        )
    
    # Find approval request
    approval_request = db.query(ApprovalRequest).filter(
        ApprovalRequest.id == approval_request_id
    ).first()
    
    if not approval_request:
        raise HTTPException(
            status_code=404,
            detail=f"Approval request with ID {approval_request_id} not found"
        )
    
    # Check if request is still pending
    if approval_request.status != ApprovalStatus.pending:
        raise HTTPException(
            status_code=400,
            detail=f"This request has already been {approval_request.status}"
        )
    
    # Get the kit
    kit = db.query(Kit).filter(Kit.id == approval_request.kit_id).first()
    if not kit:
        raise HTTPException(
            status_code=404,
            detail=f"Kit not found for this approval request"
        )
    
    custody_event = None
    
    if approve:
        # Verify kit is still available
        if kit.status != KitStatus.available:
            raise HTTPException(
                status_code=400,
                detail=f"Kit is no longer available (current status: {kit.status})"
            )
        
        # Update approval request
        approval_request.status = ApprovalStatus.approved
        approval_request.approver_id = approver_user.id
        approval_request.approver_name = approver_user.name
        approval_request.approver_role = approver_user.role
        
        # Create custody event for off-site checkout
        custody_event = CustodyEvent(
            event_type=CustodyEventType.checkout_offsite,
            kit_id=kit.id,
            initiated_by_id=approval_request.requester_id,
            initiated_by_name=approval_request.requester_name,
            custodian_id=approval_request.custodian_id,
            custodian_name=approval_request.custodian_name,
            notes=f"Approved by {approver_user.name} ({approver_user.role}). " + (approval_request.notes or ""),
            location_type="off_site"
        )
        
        # Update kit status
        kit.status = KitStatus.checked_out
        kit.current_custodian_id = approval_request.custodian_id
        kit.current_custodian_name = approval_request.custodian_name
        
        db.add(custody_event)
    else:
        # Deny the request
        if not denial_reason:
            raise HTTPException(
                status_code=400,
                detail="Denial reason is required when denying a request"
            )
        
        approval_request.status = ApprovalStatus.denied
        approval_request.approver_id = approver_user.id
        approval_request.approver_name = approver_user.name
        approval_request.approver_role = approver_user.role
        approval_request.denial_reason = denial_reason
    
    # Save to database
    db.commit()
    db.refresh(approval_request)
    
    if custody_event:
        db.refresh(custody_event)
        db.refresh(kit)
    
    return approval_request, custody_event, kit


def get_pending_approvals(
    db: Session,
    approver_user: User
) -> List[ApprovalRequest]:
    """
    Get all pending approval requests.
    
    Args:
        db: Database session
        approver_user: User requesting the list (must be Armorer or Coach)
        
    Returns:
        List of pending approval requests
        
    Raises:
        HTTPException: If user lacks permission
    """
    # Verify permissions - only Armorer or Coach can see pending approvals
    allowed_roles = ["armorer", "coach", "admin"]
    if approver_user.role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail=f"Only Armorer or Coach can view pending approvals"
        )
    
    # Get all pending approval requests
    pending_requests = db.query(ApprovalRequest).filter(
        ApprovalRequest.status == ApprovalStatus.pending
    ).order_by(ApprovalRequest.created_at.desc()).all()
    
    return pending_requests
