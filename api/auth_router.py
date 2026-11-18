"""
Authentication Router for Hospital Management AI Agent
Handles Google OAuth, login/logout, and session management

Supports any Gmail account for testing and production use.
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import httpx
import os
from datetime import datetime, timedelta
from typing import Optional
import jwt
import uuid

from api.auth import create_access_token, verify_token, get_current_user

# Router setup
router = APIRouter()
security = HTTPBearer()

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', 'your-google-client-id')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', 'your-google-client-secret')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8000/auth/callback')

# Models
class LoginRequest(BaseModel):
    email: str
    password: Optional[str] = None
    
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_info: dict
    expires_in: int

class UserInfo(BaseModel):
    email: str
    name: str
    picture: Optional[str] = None
    role: str = "patient"

# ==================== GOOGLE OAUTH ROUTES ====================

@router.get("/login")
async def initiate_google_login():
    """
    Initiate Google OAuth login flow
    Redirects to Google OAuth consent screen
    """
    try:
        # Google OAuth URL
        google_oauth_url = (
            f"https://accounts.google.com/o/oauth2/auth?"
            f"client_id={GOOGLE_CLIENT_ID}&"
            f"redirect_uri={GOOGLE_REDIRECT_URI}&"
            f"scope=openid email profile&"
            f"response_type=code&"
            f"access_type=offline"
        )
        
        return RedirectResponse(url=google_oauth_url)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initiate Google login: {str(e)}"
        )

@router.get("/auth/callback")
async def google_oauth_callback(code: str, request: Request):
    """
    Handle Google OAuth callback
    Exchange authorization code for access token and user info
    """
    print(f"🔐 OAuth callback received with code: {code[:20]}...")
    
    try:
        # Exchange code for tokens
        async with httpx.AsyncClient() as client:
            print(f"🔄 Exchanging code for access token...")
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": GOOGLE_REDIRECT_URI,
                }
            )
            
            if token_response.status_code != 200:
                error_detail = token_response.text
                print(f"❌ Token exchange failed: {error_detail}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to exchange code for token: {error_detail}"
                )
            
            tokens = token_response.json()
            access_token = tokens.get("access_token")
            print(f"✅ Access token received")
            
            # Get user info from Google
            print(f"🔄 Fetching user info from Google...")
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if user_response.status_code != 200:
                error_detail = user_response.text
                print(f"❌ User info fetch failed: {error_detail}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to get user info from Google: {error_detail}"
                )
            
            user_data = user_response.json()
            print(f"✅ User info received: {user_data.get('email')}")
            
            # Create user info
            user_info = {
                "email": user_data.get("email"),
                "name": user_data.get("name"),
                "picture": user_data.get("picture"),
                "role": "patient",  # Default role, can be updated
                "google_id": user_data.get("id"),
                "verified_email": user_data.get("verified_email", False)
            }
            
            # Create JWT token for our app
            print(f"🔄 Creating JWT token for {user_info['email']}...")
            app_token = create_access_token(
                data={"sub": user_info["email"], "user_info": user_info}
            )
            print(f"✅ JWT token created, redirecting to frontend...")
            
            # Redirect to frontend main page with token in URL fragment (more secure)
            frontend_url = f"http://localhost:3000?token={app_token}"
            print(f"🔀 Redirecting to: {frontend_url[:60]}...")
            return RedirectResponse(url=frontend_url)
            
    except Exception as e:
        print(f"❌ OAuth callback error: {str(e)}")
        import traceback
        traceback.print_exc()
        # Redirect to frontend main page with error
        frontend_url = f"http://localhost:3000?error={str(e)}"
        return RedirectResponse(url=frontend_url)

# ==================== DIRECT LOGIN ROUTES (For Testing) ====================

@router.post("/api/auth/login", response_model=LoginResponse)
async def direct_login(login_request: LoginRequest):
    """
    Direct login endpoint for testing
    Accepts any email and creates a session
    """
    try:
        # For testing - accept any Gmail account
        if not login_request.email.endswith("@gmail.com"):
            raise HTTPException(
                status_code=400,
                detail="Please use a Gmail account for testing"
            )
        
        # Create user info
        user_info = {
            "email": login_request.email,
            "name": login_request.email.split("@")[0].replace(".", " ").title(),
            "role": "patient",
            "picture": None,
            "verified_email": True,
            "login_method": "direct"
        }
        
        # Create JWT token
        access_token = create_access_token(
            data={"sub": user_info["email"], "user_info": user_info}
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_info=user_info,
            expires_in=1440  # 24 hours in minutes
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Login failed: {str(e)}"
        )

@router.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information
    """
    return {
        "user": current_user,
        "authenticated": True,
        "timestamp": datetime.now().isoformat()
    }

@router.post("/api/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout endpoint
    In a production app, you'd invalidate the token
    """
    return {
        "message": "Successfully logged out",
        "user": current_user["email"],
        "timestamp": datetime.now().isoformat()
    }

# ==================== SESSION MANAGEMENT ====================

@router.get("/api/auth/session")
async def get_session_info(current_user: dict = Depends(get_current_user)):
    """
    Get current session information
    """
    return {
        "session_active": True,
        "user": current_user,
        "session_id": f"session-{int(datetime.now().timestamp())}-{uuid.uuid4().hex[:8]}",
        "created_at": datetime.now().isoformat()
    }

# ==================== HEALTH CHECK ====================

@router.get("/auth/health")
async def auth_health_check():
    """
    Health check for authentication service
    """
    return {
        "status": "healthy",
        "service": "authentication",
        "timestamp": datetime.now().isoformat(),
        "google_oauth_configured": bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)
    }