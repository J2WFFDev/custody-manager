from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.custody_event import (
    CustodyCheckoutRequest,
    CustodyCheckoutResponse,
    CustodyEventResponse
)
from app.services.custody_service import checkout_kit_onprem

router = APIRouter()


# Dependency to get current user - simplified for now
# In production, this would verify JWT token
async def get_current_user(db: Session = Depends(get_db)) -> User:
    """
    Get current authenticated user.
    
    For now, this returns a mock user for testing.
    In production, this would verify JWT token and fetch real user.
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
