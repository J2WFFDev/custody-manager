from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.core.security import verify_token

router = APIRouter()

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Get current user from JWT token in Authorization header"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = auth_header.replace("Bearer ", "")
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

def verify_admin(user: User):
    """Verify that the user has admin role"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

@router.get("/", response_model=List[UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all users (Admin only)"""
    verify_admin(current_user)
    
    users = db.query(User).all()
    return users

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user role and verified adult status (Admin only)"""
    verify_admin(current_user)
    
    # Find the user to update
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields if provided
    if user_update.role is not None:
        # Validate role
        valid_roles = ["admin", "armorer", "coach", "volunteer", "parent"]
        if user_update.role not in valid_roles:
            raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        user.role = user_update.role
    
    if user_update.verified_adult is not None:
        user.verified_adult = user_update.verified_adult
    
    db.commit()
    db.refresh(user)
    return user
