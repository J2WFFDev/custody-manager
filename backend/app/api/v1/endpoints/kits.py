from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Literal

from app.database import get_db
from app.models.kit import Kit
from app.schemas.kit import KitCreate, KitResponse
from app.services.qr_service import create_qr_image

router = APIRouter()

@router.post("/", response_model=KitResponse, status_code=201)
def create_kit(kit_data: KitCreate, db: Session = Depends(get_db)):
    """
    Create a new kit.
    
    This implements QR-001: Register new kits and generate QR codes.
    """
    # Check if code already exists
    existing = db.query(Kit).filter(Kit.code == kit_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Kit with code '{kit_data.code}' already exists")
    
    # Create kit
    kit = Kit(
        code=kit_data.code,
        name=kit_data.name,
        description=kit_data.description
    )
    
    db.add(kit)
    db.commit()
    db.refresh(kit)
    
    return kit

@router.get("/", response_model=List[KitResponse])
def list_kits(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List all kits.
    """
    kits = db.query(Kit).offset(skip).limit(limit).all()
    return kits

@router.get("/{kit_id}", response_model=KitResponse)
def get_kit(kit_id: int, db: Session = Depends(get_db)):
    """
    Get a specific kit by ID.
    """
    kit = db.query(Kit).filter(Kit.id == kit_id).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    return kit

@router.get("/code/{code}", response_model=KitResponse)
def get_kit_by_code(code: str, db: Session = Depends(get_db)):
    """
    Get a specific kit by code.
    
    This supports QR-002 and QR-003: Scan QR code to check out/in kits.
    """
    kit = db.query(Kit).filter(Kit.code == code).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    return kit

@router.get("/{kit_id}/qr-image")
def get_qr_image(
    kit_id: int,
    format: Literal["png", "svg"] = Query("png", description="Image format"),
    db: Session = Depends(get_db)
):
    """
    Get QR code image for a kit as PNG or SVG.
    
    This endpoint serves QR codes as images for printing or display.
    """
    kit = db.query(Kit).filter(Kit.id == kit_id).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    
    # Generate QR code image from kit code
    image_format = format.upper()
    image_bytes = create_qr_image(kit.code, image_format)
    
    # Set appropriate content type
    media_type = "image/svg+xml" if image_format == "SVG" else "image/png"
    
    return Response(content=image_bytes, media_type=media_type)

