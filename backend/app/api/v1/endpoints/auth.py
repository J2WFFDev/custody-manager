from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.user_service import get_or_create_user
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.schemas.user import UserResponse, Token
from app.config import settings
from app.models.user import User
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from datetime import datetime, timezone
from urllib.parse import urlencode
import logging
import requests

router = APIRouter()
logger = logging.getLogger(__name__)

# Create state serializer (uses SECRET_KEY for encryption and signing)
state_serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

# Google OAuth
@router.get("/google/login")
async def google_login(request: Request):
    """Initiate Google OAuth flow with stateless encrypted state token"""
    # Generate encrypted state token with timestamp for validation
    state_data = {
        "provider": "google",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    state = state_serializer.dumps(state_data)
    
    # Build OAuth URL manually with state parameter
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state
    }
    oauth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    
    logger.info(f"Initiating Google OAuth flow with state token")
    return RedirectResponse(url=oauth_url)

@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: str = None,
    state: str = None,
    error: str = None,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback with stateless state validation"""
    # Check for OAuth errors
    if error:
        logger.error(f"Google OAuth error: {error}")
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    
    if not code or not state:
        logger.error("Missing code or state parameter in callback")
        raise HTTPException(status_code=400, detail="Missing code or state parameter")
    
    try:
        # Validate encrypted state (max_age=600 seconds = 10 minutes)
        state_data = state_serializer.loads(state, max_age=600)
        
        if state_data.get("provider") != "google":
            logger.error(f"Invalid provider in state: {state_data.get('provider')}")
            raise HTTPException(status_code=400, detail="Invalid state parameter - provider mismatch")
        
        logger.info("State validated successfully")
        
        # Exchange code for token manually (no session needed)
        token_response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code"
            },
            timeout=10
        )
        
        if token_response.status_code != 200:
            logger.error(f"Token exchange failed: {token_response.text}")
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")
        
        token_data = token_response.json()
        oauth_access_token = token_data.get("access_token")
        
        if not oauth_access_token:
            logger.error("No access token in response")
            raise HTTPException(status_code=400, detail="No access token received")
        
        # Get user info from Google
        user_info_response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {oauth_access_token}"},
            timeout=10
        )
        
        if user_info_response.status_code != 200:
            logger.error(f"Failed to get user info: {user_info_response.text}")
            raise HTTPException(status_code=400, detail="Failed to get user info from Google")
        
        user_info = user_info_response.json()
        
        if not user_info or not user_info.get('sub') or not user_info.get('email'):
            logger.error(f"Invalid user info received: {user_info}")
            raise HTTPException(status_code=400, detail="Invalid user info from Google")
        
        logger.info(f"User info retrieved for: {user_info.get('email')}")
        
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
    except SignatureExpired:
        logger.error("State token expired")
        raise HTTPException(status_code=400, detail="State expired - please try logging in again")
    except BadSignature:
        logger.error("Invalid state signature - possible CSRF attack")
        raise HTTPException(status_code=400, detail="Invalid state - possible CSRF attack")
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during OAuth: {str(e)}")
        raise HTTPException(status_code=503, detail="Network error - please try again")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google authentication failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Authentication failed")

# Microsoft OAuth
@router.get("/microsoft/login")
async def microsoft_login(request: Request):
    """Initiate Microsoft OAuth flow with stateless encrypted state token"""
    # Generate encrypted state token with timestamp for validation
    state_data = {
        "provider": "microsoft",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    state = state_serializer.dumps(state_data)
    
    # Build OAuth URL manually with state parameter
    redirect_uri = settings.MICROSOFT_REDIRECT_URI
    tenant_id = settings.MICROSOFT_TENANT_ID or "common"
    params = {
        "client_id": settings.MICROSOFT_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state
    }
    oauth_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize?{urlencode(params)}"
    
    logger.info(f"Initiating Microsoft OAuth flow with state token")
    return RedirectResponse(url=oauth_url)

@router.get("/microsoft/callback")
async def microsoft_callback(
    request: Request,
    code: str = None,
    state: str = None,
    error: str = None,
    db: Session = Depends(get_db)
):
    """Handle Microsoft OAuth callback with stateless state validation"""
    # Check for OAuth errors
    if error:
        logger.error(f"Microsoft OAuth error: {error}")
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    
    if not code or not state:
        logger.error("Missing code or state parameter in callback")
        raise HTTPException(status_code=400, detail="Missing code or state parameter")
    
    try:
        # Validate encrypted state (max_age=600 seconds = 10 minutes)
        state_data = state_serializer.loads(state, max_age=600)
        
        if state_data.get("provider") != "microsoft":
            logger.error(f"Invalid provider in state: {state_data.get('provider')}")
            raise HTTPException(status_code=400, detail="Invalid state parameter - provider mismatch")
        
        logger.info("State validated successfully")
        
        # Exchange code for token manually (no session needed)
        tenant_id = settings.MICROSOFT_TENANT_ID or "common"
        token_response = requests.post(
            f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
            data={
                "code": code,
                "client_id": settings.MICROSOFT_CLIENT_ID,
                "client_secret": settings.MICROSOFT_CLIENT_SECRET,
                "redirect_uri": settings.MICROSOFT_REDIRECT_URI,
                "grant_type": "authorization_code"
            },
            timeout=10
        )
        
        if token_response.status_code != 200:
            logger.error(f"Token exchange failed: {token_response.text}")
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")
        
        token_data = token_response.json()
        oauth_access_token = token_data.get("access_token")
        
        if not oauth_access_token:
            logger.error("No access token in response")
            raise HTTPException(status_code=400, detail="No access token received")
        
        # Get user info from Microsoft Graph API
        user_info_response = requests.get(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {oauth_access_token}"},
            timeout=10
        )
        
        if user_info_response.status_code != 200:
            logger.error(f"Failed to get user info: {user_info_response.text}")
            raise HTTPException(status_code=400, detail="Failed to get user info from Microsoft")
        
        user_info = user_info_response.json()
        
        # Microsoft Graph API returns 'id' instead of 'sub' and 'userPrincipalName' or 'mail' for email
        oauth_id = user_info.get('id')
        email = user_info.get('mail') or user_info.get('userPrincipalName')
        
        if not oauth_id or not email:
            logger.error(f"Invalid user info received: {user_info}")
            raise HTTPException(status_code=400, detail="Invalid user info from Microsoft")
        
        logger.info(f"User info retrieved for: {email}")
        
        # Get or create user
        user = get_or_create_user(
            db=db,
            provider="microsoft",
            oauth_id=oauth_id,
            email=email,
            name=user_info.get('displayName', email)
        )
        
        # Create JWT tokens
        access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
        refresh_token = create_refresh_token(data={"sub": str(user.id), "email": user.email})
        
        # Redirect to frontend with tokens in URL fragment (more secure than query param)
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/auth/callback#access_token={access_token}&refresh_token={refresh_token}"
        )
    except SignatureExpired:
        logger.error("State token expired")
        raise HTTPException(status_code=400, detail="State expired - please try logging in again")
    except BadSignature:
        logger.error("Invalid state signature - possible CSRF attack")
        raise HTTPException(status_code=400, detail="Invalid state - possible CSRF attack")
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during OAuth: {str(e)}")
        raise HTTPException(status_code=503, detail="Network error - please try again")
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
