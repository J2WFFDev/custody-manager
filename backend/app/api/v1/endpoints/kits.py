from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Literal

from app.database import get_db
from app.models.kit import Kit
from app.schemas.kit import KitCreate, KitResponse, KitUpdate
from app.services.qr_service import generate_qr_code, create_qr_image

router = APIRouter(prefix="/kits", tags=["kits"])

@router.post("/", response_model=KitResponse, status_code=201)
def create_kit(kit_data: KitCreate, db: Session = Depends(get_db)):
    """
    Create a new kit and generate QR code.
    
    This implements QR-001: Register new kits and generate QR codes.
    """
    # Generate unique QR code
    qr_code = generate_qr_code()
    
    # Ensure QR code is unique
    max_attempts = 10
    for _ in range(max_attempts):
        existing = db.query(Kit).filter(Kit.qr_code == qr_code).first()
        if not existing:
            break
        qr_code = generate_qr_code()
    else:
        raise HTTPException(status_code=500, detail="Failed to generate unique QR code")
    
    # Create kit
    kit = Kit(
        qr_code=qr_code,
        name=kit_data.name,
        description=kit_data.description,
        serial_number=kit_data.serial_number
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

@router.get("/qr/{qr_code}", response_model=KitResponse)
def get_kit_by_qr(qr_code: str, db: Session = Depends(get_db)):
    """
    Get a specific kit by QR code.
    
    This supports QR-002 and QR-003: Scan QR code to check out/in kits.
    """
    kit = db.query(Kit).filter(Kit.qr_code == qr_code).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    return kit

@router.put("/{kit_id}", response_model=KitResponse)
def update_kit(kit_id: int, kit_data: KitUpdate, db: Session = Depends(get_db)):
    """
    Update a kit.
    """
    kit = db.query(Kit).filter(Kit.id == kit_id).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    
    # Update fields
    if kit_data.name is not None:
        kit.name = kit_data.name
    if kit_data.description is not None:
        kit.description = kit_data.description
    if kit_data.serial_number is not None:
        kit.serial_number = kit_data.serial_number
    
    db.commit()
    db.refresh(kit)
    
    return kit

@router.delete("/{kit_id}", status_code=204)
def delete_kit(kit_id: int, db: Session = Depends(get_db)):
    """
    Delete a kit.
    """
    kit = db.query(Kit).filter(Kit.id == kit_id).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    
    db.delete(kit)
    db.commit()
    
    return None

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
    
    # Generate QR code image
    image_format = format.upper()
    image_bytes = create_qr_image(kit.qr_code, image_format)
    
    # Set appropriate content type
    media_type = "image/svg+xml" if image_format == "SVG" else "image/png"
    
    return Response(content=image_bytes, media_type=media_type)
