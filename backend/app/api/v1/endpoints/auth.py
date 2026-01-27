from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.oauth import oauth
from app.services.user_service import get_or_create_user
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.schemas.user import UserResponse, Token
from app.config import settings
from app.models.user import User
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Google OAuth
@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info from Google")
        
        # Get or create user
        user = get_or_create_user(
            db=db,
            provider="google",
            oauth_id=user_info['sub'],
            email=user_info['email'],
            name=user_info.get('name', user_info['email'])
        )
        
        # Create JWT tokens
        access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
        refresh_token = create_refresh_token(data={"sub": str(user.id), "email": user.email})
        
        # Redirect to frontend with tokens in URL fragment (more secure than query param)
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/auth/callback#access_token={access_token}&refresh_token={refresh_token}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google authentication failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Authentication failed")

# Microsoft OAuth
@router.get("/microsoft/login")
async def microsoft_login(request: Request):
    redirect_uri = settings.MICROSOFT_REDIRECT_URI
    return await oauth.microsoft.authorize_redirect(request, redirect_uri)

@router.get("/microsoft/callback")
async def microsoft_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.microsoft.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info from Microsoft")
        
        # Get or create user
        user = get_or_create_user(
            db=db,
            provider="microsoft",
            oauth_id=user_info['sub'],
            email=user_info['email'],
            name=user_info.get('name', user_info['email'])
        )
        
        # Create JWT tokens
        access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
        refresh_token = create_refresh_token(data={"sub": str(user.id), "email": user.email})
        
        # Redirect to frontend with tokens in URL fragment (more secure than query param)
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/auth/callback#access_token={access_token}&refresh_token={refresh_token}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Microsoft authentication failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Authentication failed")

# Get current user from JWT
@router.get("/me", response_model=UserResponse)
async def get_current_user(request: Request, db: Session = Depends(get_db)):
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

# Refresh access token using refresh token
@router.post("/refresh", response_model=Token)
async def refresh_access_token(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    refresh_token = auth_header.replace("Bearer ", "")
    payload = verify_token(refresh_token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    
    # Verify it's a refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create new access token
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    
    return Token(access_token=access_token, token_type="bearer", user=user)
