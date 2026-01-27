from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.kit import Kit
from app.schemas.custody_event import (
    CustodyCheckoutRequest,
    CustodyCheckoutResponse,
    CustodyEventResponse
)
from app.schemas.approval_request import (
    OffSiteCheckoutRequest,
    OffSiteCheckoutResponse,
    ApprovalDecisionRequest,
    ApprovalDecisionResponse,
    ApprovalRequestResponse
)
from app.services.custody_service import checkout_kit_onprem
from app.services.approval_service import (
    create_offsite_checkout_request,
    approve_or_deny_offsite_request,
    get_pending_approvals
)
from app.constants import ATTESTATION_TEXT

router = APIRouter()


# Dependency to get current user - simplified for now
# SECURITY WARNING: This is mock authentication for development/testing only
# TODO: Replace with real JWT authentication before production deployment
async def get_current_user(db: Session = Depends(get_db)) -> User:
    """
    Get current authenticated user.
    
    IMPORTANT: This is a MOCK implementation for development/testing.
    In production, this MUST verify JWT tokens and return the authenticated user.
    
    Returns a mock coach user to allow testing of the checkout flow.
    """
    # TODO: Replace with real JWT authentication
    # For development/testing, return a mock coach user
    user = db.query(User).filter(User.role == "coach").first()
    if not user:
        # Create a mock coach user if none exists
        user = User(
            email="coach@example.com",
            name="Test Coach",
            oauth_provider="google",
            oauth_id="test-oauth-id",
            role="coach",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.post("/checkout", response_model=CustodyCheckoutResponse, status_code=201)
def checkout_kit(
    request: CustodyCheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check out a kit on-premises.
    
    Implements:
    - CUSTODY-001: As a Coach, I want to check out a kit on-premises to an athlete
    - QR-002: As a Coach, I want to scan a QR code to check out a kit on-premises
    
    This endpoint:
    - Verifies the user has permission (Coach, Armorer, or Admin)
    - Checks that the kit is available
    - Creates an immutable custody event
    - Updates kit status to checked_out
    """
    # Perform checkout
    custody_event, kit = checkout_kit_onprem(
        db=db,
        kit_code=request.kit_code,
        custodian_name=request.custodian_name,
        initiated_by_user=current_user,
        custodian_id=request.custodian_id,
        notes=request.notes
    )
    
    return CustodyCheckoutResponse(
        message=f"Kit '{kit.name}' successfully checked out to {request.custodian_name}",
        event=CustodyEventResponse.model_validate(custody_event),
        kit_name=kit.name,
        kit_code=kit.code
    )


@router.post("/offsite-request", response_model=OffSiteCheckoutResponse, status_code=201)
def request_offsite_checkout(
    request: OffSiteCheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Request off-site checkout approval for a kit with responsibility attestation.
    
    Implements:
    - CUSTODY-011: As a Parent, I want to check out a kit for my child to take off-site
    - CUSTODY-012: As a Parent, I want to acknowledge responsibility via a clear attestation statement
    - AUTH-002: Verify user has verified_adult flag
    
    This endpoint:
    - Verifies the user is a verified adult
    - Validates attestation signature and acceptance
    - Checks that the kit is available
    - Creates an approval request that requires Armorer or Coach approval
    - Stores attestation for audit trail
    - Does NOT immediately check out the kit
    """
    # Create approval request with attestation
    approval_request, kit = create_offsite_checkout_request(
        db=db,
        kit_code=request.kit_code,
        custodian_name=request.custodian_name,
        requester_user=current_user,
        attestation_signature=request.attestation_signature,
        attestation_accepted=request.attestation_accepted,
        custodian_id=request.custodian_id,
        notes=request.notes,
        request_ip=None  # TODO: Extract from request headers in production
    )
    
    # Build response
    approval_response = ApprovalRequestResponse(
        id=approval_request.id,
        kit_id=kit.id,
        kit_name=kit.name,
        kit_code=kit.code,
        requester_id=approval_request.requester_id,
        requester_name=approval_request.requester_name,
        custodian_id=approval_request.custodian_id,
        custodian_name=approval_request.custodian_name,
        status=approval_request.status,
        approver_id=approval_request.approver_id,
        approver_name=approval_request.approver_name,
        approver_role=approval_request.approver_role,
        notes=approval_request.notes,
        denial_reason=approval_request.denial_reason,
        created_at=approval_request.created_at,
        updated_at=approval_request.updated_at,
        attestation_text=approval_request.attestation_text,
        attestation_signature=approval_request.attestation_signature,
        attestation_timestamp=approval_request.attestation_timestamp,
        attestation_ip_address=approval_request.attestation_ip_address
    )
    
    return OffSiteCheckoutResponse(
        message=f"Off-site checkout request for kit '{kit.name}' submitted successfully. Awaiting approval from Armorer or Coach.",
        approval_request=approval_response
    )


@router.post("/offsite-approve", response_model=ApprovalDecisionResponse, status_code=200)
def approve_offsite_checkout(
    request: ApprovalDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Approve or deny an off-site checkout request.
    
    Implements:
    - CUSTODY-002: As an Armorer, I want to approve off-site checkout requests
    - CUSTODY-003: As a Coach, I want to approve off-site checkout requests
    
    This endpoint:
    - Verifies the user is an Armorer or Coach
    - Approves or denies the request
    - If approved, creates a custody event and checks out the kit off-site
    - If denied, records the denial reason
    """
    # Process approval/denial
    approval_request, custody_event, kit = approve_or_deny_offsite_request(
        db=db,
        approval_request_id=request.approval_request_id,
        approver_user=current_user,
        approve=request.approve,
        denial_reason=request.denial_reason
    )
    
    # Build response
    approval_response = ApprovalRequestResponse(
        id=approval_request.id,
        kit_id=kit.id,
        kit_name=kit.name,
        kit_code=kit.code,
        requester_id=approval_request.requester_id,
        requester_name=approval_request.requester_name,
        custodian_id=approval_request.custodian_id,
        custodian_name=approval_request.custodian_name,
        status=approval_request.status,
        approver_id=approval_request.approver_id,
        approver_name=approval_request.approver_name,
        approver_role=approval_request.approver_role,
        notes=approval_request.notes,
        denial_reason=approval_request.denial_reason,
        created_at=approval_request.created_at,
        updated_at=approval_request.updated_at,
        attestation_text=approval_request.attestation_text,
        attestation_signature=approval_request.attestation_signature,
        attestation_timestamp=approval_request.attestation_timestamp,
        attestation_ip_address=approval_request.attestation_ip_address
    )
    
    custody_event_dict = None
    if custody_event:
        custody_event_dict = {
            "id": custody_event.id,
            "event_type": custody_event.event_type.value,
            "kit_id": custody_event.kit_id,
            "initiated_by_id": custody_event.initiated_by_id,
            "initiated_by_name": custody_event.initiated_by_name,
            "custodian_id": custody_event.custodian_id,
            "custodian_name": custody_event.custodian_name,
            "notes": custody_event.notes,
            "location_type": custody_event.location_type,
            "created_at": custody_event.created_at.isoformat()
        }
    
    if request.approve:
        message = f"Off-site checkout request approved. Kit '{kit.name}' has been checked out to {approval_request.custodian_name}."
    else:
        message = f"Off-site checkout request denied. Reason: {approval_request.denial_reason}"
    
    return ApprovalDecisionResponse(
        message=message,
        approval_request=approval_response,
        custody_event=custody_event_dict
    )


@router.get("/pending-approvals", response_model=List[ApprovalRequestResponse], status_code=200)
def list_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all pending off-site checkout approval requests.
    
    Implements:
    - CUSTODY-002: As an Armorer, I want to approve off-site checkout requests
    - CUSTODY-003: As a Coach, I want to approve off-site checkout requests
    
    This endpoint:
    - Verifies the user is an Armorer or Coach
    - Returns all pending approval requests with attestation data
    """
    # Get pending approvals
    pending_requests = get_pending_approvals(
        db=db,
        approver_user=current_user
    )
    
    # Build response list
    response_list = []
    for approval_request in pending_requests:
        # Get kit details
        kit = db.query(Kit).filter(Kit.id == approval_request.kit_id).first()
        
        response_list.append(ApprovalRequestResponse(
            id=approval_request.id,
            kit_id=kit.id,
            kit_name=kit.name,
            kit_code=kit.code,
            requester_id=approval_request.requester_id,
            requester_name=approval_request.requester_name,
            custodian_id=approval_request.custodian_id,
            custodian_name=approval_request.custodian_name,
            status=approval_request.status,
            approver_id=approval_request.approver_id,
            approver_name=approval_request.approver_name,
            approver_role=approval_request.approver_role,
            notes=approval_request.notes,
            denial_reason=approval_request.denial_reason,
            created_at=approval_request.created_at,
            updated_at=approval_request.updated_at,
            attestation_text=approval_request.attestation_text,
            attestation_signature=approval_request.attestation_signature,
            attestation_timestamp=approval_request.attestation_timestamp,
            attestation_ip_address=approval_request.attestation_ip_address
        ))
    
    return response_list


@router.get("/attestation-text", status_code=200)
def get_attestation_text():
    """
    Get the responsibility attestation text for off-site custody.
    
    Implements CUSTODY-012:
    - Display attestation text in UI
    
    This endpoint:
    - Returns the standard attestation text that users must review and accept
    - No authentication required (public endpoint for displaying terms)
    """
    return {
        "attestation_text": ATTESTATION_TEXT
    }
