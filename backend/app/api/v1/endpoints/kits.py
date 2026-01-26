from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.kit import KitLookupResponse
from app.services.kit_service import KitService

router = APIRouter()

@router.get("/lookup", response_model=KitLookupResponse)
async def lookup_kit(
    code: str = Query(..., description="Kit code from QR scan or manual entry"),
    db: Session = Depends(get_db)
):
    """
    Lookup a kit by its code (QR or manual entry)
    
    Returns kit details including:
    - Kit information (code, name, description)
    - Current status (available, checked_out, in_maintenance, lost)
    - Current custodian (if checked out)
    """
    kit = KitService.lookup_by_code(db, code)
    
    if not kit:
        raise HTTPException(status_code=404, detail=f"Kit with code '{code}' not found")
    
    return kit
