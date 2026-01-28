from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Literal

from app.database import get_db
from app.models.kit import Kit
from app.models.kit_item import KitItem
from app.schemas.kit import KitCreate, KitResponse
from app.schemas.kit_item import KitItemCreate, KitItemUpdate, KitItemResponse
from app.services.qr_service import create_qr_image
from app.services.warnings_service import calculate_kit_warnings

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
        description=kit_data.description,
        serial_number=kit_data.serial_number  # Automatically encrypted by EncryptedString type
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
    List all kits with warning information.
    
    Implements CUSTODY-008, CUSTODY-014, and MAINT-002:
    - Calculates soft warnings for overdue returns and extended custody
    - Calculates soft warnings for overdue maintenance
    - Warnings are non-blocking and informational only
    """
    kits = db.query(Kit).offset(skip).limit(limit).all()
    
    # Add warning information to each kit
    kit_responses = []
    for kit in kits:
        kit_dict = {
            "id": kit.id,
            "code": kit.code,
            "name": kit.name,
            "description": kit.description,
            "status": kit.status,
            "serial_number": kit.serial_number,  # Will be decrypted by hybrid property
            "current_custodian_id": kit.current_custodian_id,
            "current_custodian_name": kit.current_custodian_name,
            "serial_number": kit.serial_number,  # Automatically decrypted by EncryptedString type
            "next_maintenance_date": kit.next_maintenance_date,
            "created_at": kit.created_at,
            "updated_at": kit.updated_at
        }
        
        # Calculate warnings
        warnings = calculate_kit_warnings(kit, db)
        kit_dict.update({
            "has_warning": warnings["has_warning"],
            "overdue_return": warnings["overdue_return"],
            "extended_custody": warnings["extended_custody"],
            "days_overdue": warnings["days_overdue"],
            "days_checked_out": warnings["days_checked_out"],
            "expected_return_date": warnings["expected_return_date"],
            "overdue_maintenance": warnings["overdue_maintenance"],
            "days_maintenance_overdue": warnings["days_maintenance_overdue"]
        })
        
        kit_responses.append(KitResponse(**kit_dict))
    
    return kit_responses

@router.get("/{kit_id}", response_model=KitResponse)
def get_kit(kit_id: int, db: Session = Depends(get_db)):
    """
    Get a specific kit by ID with warning information.
    """
    kit = db.query(Kit).filter(Kit.id == kit_id).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    
    # Build response with warnings
    kit_dict = {
        "id": kit.id,
        "code": kit.code,
        "name": kit.name,
        "description": kit.description,
        "status": kit.status,
        "serial_number": kit.serial_number,  # Will be decrypted by hybrid property
        "current_custodian_id": kit.current_custodian_id,
        "current_custodian_name": kit.current_custodian_name,
        "serial_number": kit.serial_number,  # Automatically decrypted by EncryptedString type
        "next_maintenance_date": kit.next_maintenance_date,
        "created_at": kit.created_at,
        "updated_at": kit.updated_at
    }
    
    # Calculate warnings
    warnings = calculate_kit_warnings(kit, db)
    kit_dict.update({
        "has_warning": warnings["has_warning"],
        "overdue_return": warnings["overdue_return"],
        "extended_custody": warnings["extended_custody"],
        "days_overdue": warnings["days_overdue"],
        "days_checked_out": warnings["days_checked_out"],
        "expected_return_date": warnings["expected_return_date"],
        "overdue_maintenance": warnings["overdue_maintenance"],
        "days_maintenance_overdue": warnings["days_maintenance_overdue"]
    })
    
    return KitResponse(**kit_dict)

@router.get("/code/{code}", response_model=KitResponse)
def get_kit_by_code(code: str, db: Session = Depends(get_db)):
    """
    Get a specific kit by code with warning information.
    
    This supports QR-002 and QR-003: Scan QR code to check out/in kits.
    """
    kit = db.query(Kit).filter(Kit.code == code).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    
    # Build response with warnings
    kit_dict = {
        "id": kit.id,
        "code": kit.code,
        "name": kit.name,
        "description": kit.description,
        "status": kit.status,
        "serial_number": kit.serial_number,  # Will be decrypted by hybrid property
        "current_custodian_id": kit.current_custodian_id,
        "current_custodian_name": kit.current_custodian_name,
        "serial_number": kit.serial_number,  # Automatically decrypted by EncryptedString type
        "next_maintenance_date": kit.next_maintenance_date,
        "created_at": kit.created_at,
        "updated_at": kit.updated_at
    }
    
    # Calculate warnings
    warnings = calculate_kit_warnings(kit, db)
    kit_dict.update({
        "has_warning": warnings["has_warning"],
        "overdue_return": warnings["overdue_return"],
        "extended_custody": warnings["extended_custody"],
        "days_overdue": warnings["days_overdue"],
        "days_checked_out": warnings["days_checked_out"],
        "expected_return_date": warnings["expected_return_date"],
        "overdue_maintenance": warnings["overdue_maintenance"],
        "days_maintenance_overdue": warnings["days_maintenance_overdue"]
    })
    
    return KitResponse(**kit_dict)

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


# Kit Items Endpoints

@router.get("/{kit_id}/items", response_model=List[KitItemResponse])
def list_kit_items(
    kit_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List all items in a kit.
    
    This enables viewing all components within a kit for granular inventory tracking.
    """
    # Verify kit exists
    kit = db.query(Kit).filter(Kit.id == kit_id).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    
    # Get items for this kit
    items = db.query(KitItem).filter(KitItem.kit_id == kit_id).offset(skip).limit(limit).all()
    
    return items


@router.post("/{kit_id}/items", response_model=KitItemResponse, status_code=201)
def create_kit_item(
    kit_id: int,
    item_data: KitItemCreate,
    db: Session = Depends(get_db)
):
    """
    Add a new item to a kit.
    
    This allows adding individual components (firearm, optic, case, etc.) to a kit
    for granular tracking and management.
    """
    # Verify kit exists
    kit = db.query(Kit).filter(Kit.id == kit_id).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    
    # Create kit item
    kit_item = KitItem(
        kit_id=kit_id,
        item_type=item_data.item_type,
        make=item_data.make,
        model=item_data.model,
        serial_number=item_data.serial_number,
        friendly_name=item_data.friendly_name,
        photo_url=item_data.photo_url,
        quantity=item_data.quantity,
        notes=item_data.notes
    )
    
    db.add(kit_item)
    db.commit()
    db.refresh(kit_item)
    
    return kit_item


@router.get("/{kit_id}/items/{item_id}", response_model=KitItemResponse)
def get_kit_item(
    kit_id: int,
    item_id: int,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific item in a kit.
    """
    # Verify kit exists
    kit = db.query(Kit).filter(Kit.id == kit_id).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    
    # Get the item
    item = db.query(KitItem).filter(
        KitItem.id == item_id,
        KitItem.kit_id == kit_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Kit item not found")
    
    return item


@router.put("/{kit_id}/items/{item_id}", response_model=KitItemResponse)
def update_kit_item(
    kit_id: int,
    item_id: int,
    item_data: KitItemUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing item in a kit.
    
    This enables modifying item details, swapping components, or updating status.
    """
    # Verify kit exists
    kit = db.query(Kit).filter(Kit.id == kit_id).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    
    # Get the item
    item = db.query(KitItem).filter(
        KitItem.id == item_id,
        KitItem.kit_id == kit_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Kit item not found")
    
    # Update fields
    update_data = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    
    return item


@router.delete("/{kit_id}/items/{item_id}", status_code=204)
def delete_kit_item(
    kit_id: int,
    item_id: int,
    db: Session = Depends(get_db)
):
    """
    Remove an item from a kit.
    
    This enables removing lost, broken, or replaced components from inventory.
    """
    # Verify kit exists
    kit = db.query(Kit).filter(Kit.id == kit_id).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    
    # Get the item
    item = db.query(KitItem).filter(
        KitItem.id == item_id,
        KitItem.kit_id == kit_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Kit item not found")
    
    db.delete(item)
    db.commit()
    
    return None

