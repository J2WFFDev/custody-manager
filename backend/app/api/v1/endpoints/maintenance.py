from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User, UserRole
from app.models.kit import Kit
from app.models.maintenance_event import MaintenanceEvent
from app.schemas.maintenance_event import (
    MaintenanceOpenRequest,
    MaintenanceOpenResponse,
    MaintenanceCloseRequest,
    MaintenanceCloseResponse,
    MaintenanceEventResponse
)
from app.services.maintenance_service import open_maintenance, close_maintenance

router = APIRouter()


# Dependency to get current user - using same mock as custody endpoints
# SECURITY WARNING: This is mock authentication for development/testing only
# TODO: Replace with real JWT authentication before production deployment
async def get_current_user(db: Session = Depends(get_db)) -> User:
    """
    Get current authenticated user.
    
    IMPORTANT: This is a MOCK implementation for development/testing.
    In production, this MUST verify JWT tokens and return the authenticated user.
    
    Returns a mock armorer user to allow testing of the maintenance flow.
    """
    # TODO: Replace with real JWT authentication
    # For development/testing, return a mock armorer user
    user = db.query(User).filter(User.role == UserRole.armorer).first()
    if not user:
        # Create a mock armorer user if none exists
        user = User(
            email="armorer@example.com",
            name="Test Armorer",
            oauth_provider="google",
            oauth_id="test-armorer-oauth-id",
            role="armorer",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.post("/open", response_model=MaintenanceOpenResponse, status_code=201)
def open_maintenance_endpoint(
    request: MaintenanceOpenRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Open maintenance on a kit, making it unavailable.
    
    Implements MAINT-001:
    - As an Armorer, I want to log maintenance events (open/close, parts replaced, round count)
    
    This endpoint:
    - Verifies the user has permission (Armorer or Admin)
    - Checks that the kit is not already in maintenance
    - Creates a maintenance event record
    - Updates kit status to in_maintenance
    """
    # Open maintenance
    maintenance_event, kit = open_maintenance(
        db=db,
        kit_code=request.kit_code,
        opened_by_user=current_user,
        notes=request.notes,
        parts_replaced=request.parts_replaced,
        round_count=request.round_count
    )
    
    return MaintenanceOpenResponse(
        message=f"Maintenance opened for kit '{kit.name}'. Kit is now unavailable.",
        event=MaintenanceEventResponse.model_validate(maintenance_event),
        kit_name=kit.name,
        kit_code=kit.code
    )


@router.post("/close", response_model=MaintenanceCloseResponse, status_code=200)
def close_maintenance_endpoint(
    request: MaintenanceCloseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Close maintenance on a kit, making it available again.
    
    Implements MAINT-001:
    - As an Armorer, I want to log maintenance events (open/close, parts replaced, round count)
    
    This endpoint:
    - Verifies the user has permission (Armorer or Admin)
    - Checks that the kit is in maintenance
    - Updates the maintenance event with close information
    - Updates kit status to available
    """
    # Close maintenance
    maintenance_event, kit = close_maintenance(
        db=db,
        kit_code=request.kit_code,
        closed_by_user=current_user,
        notes=request.notes,
        parts_replaced=request.parts_replaced,
        round_count=request.round_count
    )
    
    return MaintenanceCloseResponse(
        message=f"Maintenance closed for kit '{kit.name}'. Kit is now available.",
        event=MaintenanceEventResponse.model_validate(maintenance_event),
        kit_name=kit.name,
        kit_code=kit.code
    )


@router.get("/kits/{kit_id}/history", response_model=List[MaintenanceEventResponse])
def get_kit_maintenance_history(
    kit_id: int,
    db: Session = Depends(get_db)
):
    """
    Get maintenance history for a specific kit.
    
    This endpoint returns all maintenance events (open and closed) for a kit,
    ordered by creation date (most recent first).
    """
    # Verify kit exists
    kit = db.query(Kit).filter(Kit.id == kit_id).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    
    # Get all maintenance events for this kit
    events = db.query(MaintenanceEvent).filter(
        MaintenanceEvent.kit_id == kit_id
    ).order_by(MaintenanceEvent.created_at.desc()).all()
    
    return [MaintenanceEventResponse.model_validate(event) for event in events]
