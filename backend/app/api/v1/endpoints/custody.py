from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.user import User, UserRole
from app.models.kit import Kit
from app.schemas.custody_event import (
    CustodyCheckoutRequest,
    CustodyCheckoutResponse,
    CustodyEventResponse,
    CustodyTransferRequest,
    CustodyTransferResponse,
    LostFoundRequest,
    LostFoundResponse
)
from app.schemas.approval_request import (
    OffSiteCheckoutRequest,
    OffSiteCheckoutResponse,
    ApprovalDecisionRequest,
    ApprovalDecisionResponse,
    ApprovalRequestResponse
)
from app.services.custody_service import (
    checkout_kit_onprem,
    transfer_kit_custody,
    report_kit_lost,
    report_kit_found
)
from app.services.approval_service import (
    create_offsite_checkout_request,
    approve_or_deny_offsite_request,
    get_pending_approvals
)
from app.services.export_service import (
    export_custody_events_to_csv,
    export_custody_events_to_json
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
    
    Returns a mock user for testing. Prioritizes admin for export endpoints.
    """
    # TODO: Replace with real JWT authentication
    # For development/testing, return a mock user
    # First try to find an admin user (needed for export endpoints)
    user = db.query(User).filter(User.role == UserRole.admin).first()
    if not user:
        # Fall back to coach user
        user = db.query(User).filter(User.role == UserRole.coach).first()
    if not user:
        # Create a mock coach user if none exists
        user = User(
            email="coach@example.com",
            name="Test Coach",
            oauth_provider="google",
            oauth_id="test-oauth-id",
            role=UserRole.coach,
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
        notes=request.notes,
        expected_return_date=request.expected_return_date
    )
    
    return CustodyCheckoutResponse(
        message=f"Kit '{kit.name}' successfully checked out to {request.custodian_name}",
        event=CustodyEventResponse.model_validate(custody_event),
        kit_name=kit.name,
        kit_code=kit.code
    )


@router.post("/transfer", response_model=CustodyTransferResponse, status_code=201)
def transfer_kit(
    request: CustodyTransferRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Transfer custody of a kit from current custodian to a new custodian.
    
    Implements:
    - CUSTODY-005: As a Coach, I want to transfer custody of a kit to another user, so that handoffs are documented.
    
    This endpoint:
    - Verifies the user has permission (Coach, Armorer, or Admin)
    - Checks that the kit is currently checked out
    - Creates an immutable custody transfer event
    - Updates kit custodian information
    """
    # Perform transfer
    custody_event, kit, previous_custodian = transfer_kit_custody(
        db=db,
        kit_code=request.kit_code,
        new_custodian_name=request.new_custodian_name,
        initiated_by_user=current_user,
        new_custodian_id=request.new_custodian_id,
        notes=request.notes
    )
    
    return CustodyTransferResponse(
        message=f"Kit '{kit.name}' custody transferred from {previous_custodian} to {request.new_custodian_name}",
        event=CustodyEventResponse.model_validate(custody_event),
        kit_name=kit.name,
        kit_code=kit.code,
        previous_custodian=previous_custodian,
        new_custodian=request.new_custodian_name
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
        request_ip=None,  # TODO: Extract from request headers in production
        expected_return_date=request.expected_return_date
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
        expected_return_date=approval_request.expected_return_date,
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
            expected_return_date=approval_request.expected_return_date,
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
    - No authentication required (public endpoint) - Users need to review terms
      before requesting checkout, and the text itself is not sensitive
    """
    return {
        "attestation_text": ATTESTATION_TEXT
    }


@router.get("/export", status_code=200)
def export_custody_events(
    format: str = Query(..., description="Export format: 'csv' or 'json'"),
    start_date: Optional[str] = Query(None, description="Start date (ISO 8601 format, e.g., 2024-01-01T00:00:00)"),
    end_date: Optional[str] = Query(None, description="End date (ISO 8601 format, e.g., 2024-12-31T23:59:59)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export custody events to CSV or JSON format.
    
    Implements AUDIT-001:
    - As an Admin, I want to export complete audit logs as CSV/JSON,
      so that I can respond to incidents or compliance requests.
    
    This endpoint:
    - Verifies the user is an Admin
    - Exports all custody events in the specified format
    - Supports optional date range filtering
    - Returns file download response
    
    Query Parameters:
    - format: 'csv' or 'json'
    - start_date: Optional ISO 8601 datetime (e.g., 2024-01-01T00:00:00)
    - end_date: Optional ISO 8601 datetime (e.g., 2024-12-31T23:59:59)
    """
    # Verify user is admin
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=403,
            detail="Only admins can export audit logs"
        )
    
    # Validate format
    if format.lower() not in ["csv", "json"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid format. Must be 'csv' or 'json'"
        )
    
    # Parse dates if provided
    start_datetime = None
    end_datetime = None
    
    if start_date:
        try:
            start_datetime = datetime.fromisoformat(start_date)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid start_date format. Use ISO 8601 format (e.g., 2024-01-01T00:00:00)"
            )
    
    if end_date:
        try:
            end_datetime = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid end_date format. Use ISO 8601 format (e.g., 2024-12-31T23:59:59)"
            )
    
    # Validate date range
    if start_datetime and end_datetime and start_datetime > end_datetime:
        raise HTTPException(
            status_code=400,
            detail="start_date must be before end_date"
        )
    
    # Export based on format
    if format.lower() == "csv":
        content = export_custody_events_to_csv(
            db=db,
            start_date=start_datetime,
            end_date=end_datetime
        )
        media_type = "text/csv"
        filename = f"custody_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    else:  # json
        content = export_custody_events_to_json(
            db=db,
            start_date=start_datetime,
            end_date=end_datetime
        )
        media_type = "application/json"
        filename = f"custody_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # Return file download response
    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.post("/lost", response_model=LostFoundResponse, status_code=201)
def report_lost(
    request: LostFoundRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Report a kit as lost.
    
    Implements CUSTODY-007:
    - As an Armorer, I want to report a kit as lost, so that everyone knows it's missing
    
    This endpoint:
    - Verifies the user has permission (Armorer or Admin)
    - Checks that the kit exists and is not already lost
    - Creates an immutable custody event
    - Updates kit status to lost
    - Logs the event with notes about circumstances
    """
    # Perform lost report
    custody_event, kit = report_kit_lost(
        db=db,
        kit_code=request.kit_code,
        initiated_by_user=current_user,
        notes=request.notes
    )
    
    return LostFoundResponse(
        message=f"Kit '{kit.name}' has been reported as lost",
        event=CustodyEventResponse.model_validate(custody_event),
        kit_name=kit.name,
        kit_code=kit.code
    )


@router.post("/report-found", response_model=LostFoundResponse, status_code=201)
def report_found(
    request: LostFoundRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Report a kit as found (recovered).
    
    Implements CUSTODY-007:
    - As an Armorer, I want to mark a kit as found when it's recovered
    
    This endpoint:
    - Verifies the user has permission (Armorer or Admin)
    - Checks that the kit exists and is currently lost
    - Creates an immutable custody event
    - Updates kit status to available
    - Clears custodian information
    - Logs the event with notes about recovery circumstances
    """
    # Perform found report
    custody_event, kit = report_kit_found(
        db=db,
        kit_code=request.kit_code,
        initiated_by_user=current_user,
        notes=request.notes
    )
    
    return LostFoundResponse(
        message=f"Kit '{kit.name}' has been recovered and is now available",
        event=CustodyEventResponse.model_validate(custody_event),
        kit_name=kit.name,
        kit_code=kit.code
    )
