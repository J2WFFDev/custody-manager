from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models.custody_event import CustodyEvent, CustodyEventType
from app.models.kit import Kit
from app.models.user import User
from app.schemas.custody_event import EventTimelineResponse, CustodyEventResponse

router = APIRouter()


@router.get("/kit/{kit_id}", response_model=EventTimelineResponse)
def get_kit_events(
    kit_id: int,
    event_type: Optional[CustodyEventType] = Query(None, description="Filter by event type"),
    start_date: Optional[datetime] = Query(None, description="Filter events after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter events before this date"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order for timestamps"),
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get complete event timeline for a specific kit.
    
    Implements AUDIT-005: View complete custody and maintenance history for any kit.
    
    Query Parameters:
    - event_type: Filter by specific event type (optional)
    - start_date: Filter events after this date (optional)
    - end_date: Filter events before this date (optional)
    - sort_order: Sort by timestamp (asc or desc, default: desc)
    - skip: Pagination offset (default: 0)
    - limit: Maximum results (default: 100, max: 1000)
    
    Returns:
    - List of all custody events for the kit
    - Includes timestamps and actor information
    - Supports filtering and sorting
    """
    # Verify kit exists
    kit = db.query(Kit).filter(Kit.id == kit_id).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    
    # Build query
    query = db.query(CustodyEvent).filter(CustodyEvent.kit_id == kit_id)
    
    # Apply filters
    if event_type:
        query = query.filter(CustodyEvent.event_type == event_type)
    if start_date:
        query = query.filter(CustodyEvent.created_at >= start_date)
    if end_date:
        query = query.filter(CustodyEvent.created_at <= end_date)
    
    # Get total count before pagination
    total = query.count()
    
    # Apply sorting
    if sort_order == "asc":
        query = query.order_by(CustodyEvent.created_at.asc())
    else:
        query = query.order_by(CustodyEvent.created_at.desc())
    
    # Apply pagination
    events = query.offset(skip).limit(limit).all()
    
    # Convert to response models
    event_responses = [CustodyEventResponse.model_validate(event) for event in events]
    
    return EventTimelineResponse(
        events=event_responses,
        total=total,
        kit_id=kit.id,
        kit_name=kit.name,
        kit_code=kit.code
    )


@router.get("/user/{user_id}", response_model=EventTimelineResponse)
def get_user_events(
    user_id: int,
    event_type: Optional[CustodyEventType] = Query(None, description="Filter by event type"),
    start_date: Optional[datetime] = Query(None, description="Filter events after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter events before this date"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order for timestamps"),
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get complete event timeline for a specific user.
    
    Includes events where the user was either:
    - The initiator (e.g., Coach checking out kit)
    - The custodian (e.g., Athlete receiving kit)
    
    Query Parameters:
    - event_type: Filter by specific event type (optional)
    - start_date: Filter events after this date (optional)
    - end_date: Filter events before this date (optional)
    - sort_order: Sort by timestamp (asc or desc, default: desc)
    - skip: Pagination offset (default: 0)
    - limit: Maximum results (default: 100, max: 1000)
    
    Returns:
    - List of all custody events involving the user
    - Includes timestamps and actor information
    - Supports filtering and sorting
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Build query - include events where user was initiator OR custodian
    query = db.query(CustodyEvent).filter(
        or_(
            CustodyEvent.initiated_by_id == user_id,
            CustodyEvent.custodian_id == user_id
        )
    )
    
    # Apply filters
    if event_type:
        query = query.filter(CustodyEvent.event_type == event_type)
    if start_date:
        query = query.filter(CustodyEvent.created_at >= start_date)
    if end_date:
        query = query.filter(CustodyEvent.created_at <= end_date)
    
    # Get total count before pagination
    total = query.count()
    
    # Apply sorting
    if sort_order == "asc":
        query = query.order_by(CustodyEvent.created_at.asc())
    else:
        query = query.order_by(CustodyEvent.created_at.desc())
    
    # Apply pagination
    events = query.offset(skip).limit(limit).all()
    
    # Convert to response models
    event_responses = [CustodyEventResponse.model_validate(event) for event in events]
    
    return EventTimelineResponse(
        events=event_responses,
        total=total,
        user_id=user.id,
        user_name=user.name
    )
