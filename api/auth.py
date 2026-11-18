"""
Authentication & Security Module
JWT token management, password hashing, user verification
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import json
from pathlib import Path

# Security configuration
SECRET_KEY = "your-secret-key-here-change-in-production-use-openssl-rand-hex-32"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Database paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
USERS_DB_FILE = DATA_DIR / "users_database.json"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str) -> Dict:
    """Verify JWT token and extract payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def load_users():
    """Load users from database"""
    if USERS_DB_FILE.exists():
        with open(USERS_DB_FILE, 'r') as f:
            return json.load(f)
    return []


def get_user_by_username(username: str) -> Optional[Dict]:
    """Get user by username"""
    users = load_users()
    return next((u for u in users if u.get('username') == username), None)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """Get current authenticated user from JWT token"""
    payload = verify_token(token)
    username = payload.get("sub")
    
    # Check if user_info is embedded in the token (from auth router)
    user_info = payload.get("user_info")
    if user_info:
        # Token has embedded user info (from Google OAuth or direct login)
        return {
            "user_id": user_info.get("google_id", username),
            "username": username,
            "email": user_info["email"],
            "name": user_info.get("name", username.split("@")[0]),
            "role": user_info.get("role", "patient"),
            "picture": user_info.get("picture"),
            "verified_email": user_info.get("verified_email", True),
            "login_method": user_info.get("login_method", "oauth")
        }
    
    # Fallback to database lookup (legacy users)
    user = get_user_by_username(username)
    
    if user is None:
        # If no database user found, create from email (for new users)
        if "@" in username:
            return {
                "user_id": username,
                "username": username,
                "email": username,
                "name": username.split("@")[0].replace(".", " ").title(),
                "role": "patient",
                "picture": None,
                "verified_email": True,
                "login_method": "email"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    if not user.get('is_active', True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Return user without password hash
    return {
        "user_id": user['user_id'],
        "username": user['username'],
        "email": user['email'],
        "name": user.get('full_name', ''),
        "role": user.get('role', 'patient'),
        "is_active": user.get('is_active', True)
    }


# ==================== ROLE-BASED ACCESS CONTROL ====================

class RoleChecker:
    """Dependency for role-based access control"""
    
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: Dict = Depends(get_current_user)):
        user_role = current_user.get('role', 'patient')
        
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(self.allowed_roles)}"
            )
        
        return current_user


# Role dependency instances
require_admin = RoleChecker(["admin"])
require_doctor = RoleChecker(["admin", "doctor"])
require_staff = RoleChecker(["admin", "doctor", "staff"])
require_patient = RoleChecker(["admin", "doctor", "staff", "patient"])


# ==================== PERMISSION HELPERS ====================

def check_permission(user_role: str, required_permission: str) -> bool:
    """
    Check if user role has required permission
    
    Permission hierarchy:
    - admin: All permissions
    - doctor: Clinical operations, view all
    - staff: Operations, view assigned
    - patient: View own data only
    """
    
    permissions_map = {
        "admin": [
            "manage_users", "manage_system", "view_all", "edit_all", "delete_all",
            "manage_billing", "manage_insurance", "approve_actions", "view_analytics"
        ],
        "doctor": [
            "view_patients", "edit_medical_records", "order_tests", "prescribe_medications",
            "view_lab_results", "schedule_appointments", "view_analytics"
        ],
        "staff": [
            "view_patients", "schedule_appointments", "manage_inventory",
            "process_billing", "send_notifications", "view_assigned"
        ],
        "patient": [
            "view_own_data", "schedule_own_appointments", "view_own_results",
            "pay_bills", "update_preferences"
        ]
    }
    
    user_permissions = permissions_map.get(user_role, [])
    
    # Admin has all permissions
    if user_role == "admin":
        return True
    
    return required_permission in user_permissions


def has_permission(required_permission: str):
    """Decorator for permission-based access control"""
    
    async def permission_checker(current_user: Dict = Depends(get_current_user)):
        user_role = current_user.get('role', 'patient')
        
        if not check_permission(user_role, required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {required_permission}"
            )
        
        return current_user
    
    return permission_checker
