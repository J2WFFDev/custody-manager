from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.kit import Kit
from app.models.kit_item import Item, ItemStatus, ItemType
from app.schemas.kit_item import ItemCreate, ItemUpdate, ItemResponse, ItemAssignRequest

router = APIRouter()


@router.get("/", response_model=List[ItemResponse])
def list_items(
    status: Optional[ItemStatus] = Query(None, description="Filter by status"),
    item_type: Optional[ItemType] = Query(None, description="Filter by item type"),
    assigned: Optional[bool] = Query(None, description="Filter by assignment status: true=assigned, false=unassigned"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List all items in master inventory.
    
    This endpoint enables viewing all inventory items regardless of kit assignment.
    
    Query parameters:
    - status: Filter by status (available, assigned, checked_out, lost, maintenance)
    - item_type: Filter by type (firearm, optic, case, magazine, tool, accessory, other)
    - assigned: true = only assigned items, false = only unassigned items
    - skip: Number of items to skip for pagination
    - limit: Maximum number of items to return
    """
    query = db.query(Item)
    
    if status:
        query = query.filter(Item.status == status)
    if item_type:
        query = query.filter(Item.item_type == item_type)
    if assigned is not None:
        if assigned:
            query = query.filter(Item.current_kit_id.isnot(None))
        else:
            query = query.filter(Item.current_kit_id.is_(None))
    
    items = query.offset(skip).limit(limit).all()
    return items


@router.post("/", response_model=ItemResponse, status_code=201)
def create_item(item_data: ItemCreate, db: Session = Depends(get_db)):
    """
    Create a new item in master inventory.
    
    Item starts as 'available' (unassigned to any kit) unless current_kit_id is provided.
    If current_kit_id is provided, the item is created with 'assigned' status.
    
    This enables adding equipment to inventory before assigning it to a kit.
    """
    # Determine initial status based on whether kit is assigned
    initial_status = ItemStatus.available
    if item_data.current_kit_id:
        # Verify kit exists
        kit = db.query(Kit).filter(Kit.id == item_data.current_kit_id).first()
        if not kit:
            raise HTTPException(status_code=404, detail="Kit not found")
        initial_status = ItemStatus.assigned
    
    # Create item
    item = Item(
        item_type=item_data.item_type,
        make=item_data.make,
        model=item_data.model,
        serial_number=item_data.serial_number,
        friendly_name=item_data.friendly_name,
        photo_url=item_data.photo_url,
        quantity=item_data.quantity or 1,
        status=initial_status,
        current_kit_id=item_data.current_kit_id,
        notes=item_data.notes
    )
    
    db.add(item)
    db.commit()
    db.refresh(item)
    
    return item


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """
    Get details of a specific item.
    
    Returns item information including current kit assignment (if any).
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item_data: ItemUpdate, db: Session = Depends(get_db)):
    """
    Update item attributes.
    
    This allows modifying item details like make, model, serial number, etc.
    Note: To change kit assignment, use the assign/unassign endpoints instead.
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Update fields
    update_data = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    
    return item


@router.post("/{item_id}/assign", response_model=ItemResponse)
def assign_item_to_kit(
    item_id: int,
    assign_data: ItemAssignRequest,
    db: Session = Depends(get_db)
):
    """
    Assign an item to a kit.
    
    The item must be in 'available' status to be assigned.
    After assignment, the item status changes to 'assigned'.
    
    This enables moving items between kits or assigning unassigned items to kits.
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check if item can be assigned
    if item.status != ItemStatus.available:
        raise HTTPException(
            status_code=400,
            detail=f"Item is currently '{item.status}' and cannot be assigned. Only 'available' items can be assigned."
        )
    
    # Verify kit exists
    kit = db.query(Kit).filter(Kit.id == assign_data.kit_id).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    
    # Assign item to kit
    item.current_kit_id = assign_data.kit_id
    item.status = ItemStatus.assigned
    
    # Optional: Update notes if provided
    if assign_data.notes:
        if item.notes:
            item.notes = f"{item.notes}\n[Assignment] {assign_data.notes}"
        else:
            item.notes = f"[Assignment] {assign_data.notes}"
    
    db.commit()
    db.refresh(item)
    
    return item


@router.post("/{item_id}/unassign", response_model=ItemResponse)
def unassign_item_from_kit(item_id: int, db: Session = Depends(get_db)):
    """
    Remove item from its current kit.
    
    The item becomes 'available' again and can be assigned to a different kit.
    
    This enables item reassignment and return to unassigned inventory.
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if not item.current_kit_id:
        raise HTTPException(status_code=400, detail="Item is not assigned to any kit")
    
    # Unassign item
    item.current_kit_id = None
    item.status = ItemStatus.available
    
    db.commit()
    db.refresh(item)
    
    return item


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """
    Delete an item from inventory.
    
    Only allowed if item is not assigned to a kit (current_kit_id must be NULL).
    Items must be unassigned before they can be deleted.
    
    This prevents accidental deletion of items that are part of active kits.
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if item.current_kit_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete item that is assigned to a kit. Unassign it first using POST /items/{item_id}/unassign"
        )
    
    db.delete(item)
    db.commit()
    
    return None
