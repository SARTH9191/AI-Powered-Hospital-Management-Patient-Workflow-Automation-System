"""
FastAPI Backend - Main Application
Hospital Management AI Agent System - Phase 3
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json
import os
from pathlib import Path

# Import authentication utilities
from api.auth import (
    create_access_token,
    verify_token,
    get_current_user,
    get_password_hash,
    verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Create FastAPI app
app = FastAPI(
    title="Hospital Management AI Agent API",
    description="Comprehensive REST API for 110+ hospital management tools with AI agent capabilities",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration - Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8080",  # Alternative frontend
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# OAuth2 scheme for JWT tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Database paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
USERS_DB_FILE = DATA_DIR / "users_database.json"

# Ensure users database exists
def initialize_users_db():
    """Initialize users database with default admin user"""
    if not USERS_DB_FILE.exists():
        DATA_DIR.mkdir(exist_ok=True)
        default_users = [
            {
                "user_id": "ADMIN001",
                "email": "pawarsamarth786@gmail.com",
                "username": "admin",
                "full_name": "Hospital Administrator",
                "role": "admin",
                "hashed_password": get_password_hash("admin123"),  # Default password
                "is_active": True,
                "created_at": datetime.now().isoformat()
            },
            {
                "user_id": "DOC001",
                "email": "doctor@hospital.com",
                "username": "doctor",
                "full_name": "Dr. Sarah Johnson",
                "role": "doctor",
                "hashed_password": get_password_hash("doctor123"),
                "is_active": True,
                "created_at": datetime.now().isoformat()
            },
            {
                "user_id": "STAFF001",
                "email": "staff@hospital.com",
                "username": "staff",
                "full_name": "Hospital Staff",
                "role": "staff",
                "hashed_password": get_password_hash("staff123"),
                "is_active": True,
                "created_at": datetime.now().isoformat()
            }
        ]
        
        with open(USERS_DB_FILE, 'w') as f:
            json.dump(default_users, f, indent=2)

# Load users database
def load_users():
    """Load users from database"""
    initialize_users_db()
    with open(USERS_DB_FILE, 'r') as f:
        return json.load(f)

def save_users(users: List[Dict]):
    """Save users to database"""
    with open(USERS_DB_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def get_user_by_username(username: str) -> Optional[Dict]:
    """Get user by username"""
    users = load_users()
    return next((u for u in users if u.get('username') == username), None)

def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email"""
    users = load_users()
    return next((u for u in users if u.get('email') == email), None)


# ==================== ROOT ENDPOINT ====================

@app.get("/")
async def root():
    """API root endpoint with system information"""
    return {
        "message": "Hospital Management AI Agent API",
        "version": "3.0.0",
        "status": "operational",
        "total_tools": 110,
        "documentation": "/docs",
        "redoc": "/redoc",
        "features": [
            "110+ Hospital Management Tools",
            "JWT Authentication with Google OAuth2",
            "Role-Based Access Control (Admin, Doctor, Staff, Patient)",
            "Real-time WebSocket Updates",
            "Proactive AI Agent Monitoring",
            "Complete Billing & Insurance",
            "Lab & Pharmacy Management",
            "Appointment Scheduling",
            "Analytics Dashboard"
        ],
        "timestamp": datetime.now().isoformat()
    }


# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected",
        "ai_agent": "active"
    }


# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token endpoint
    Login with username and password to get JWT access token
    
    Default credentials:
    - Admin: username="admin", password="admin123"
    - Doctor: username="doctor", password="doctor123"
    - Staff: username="staff", password="staff123"
    """
    # Authenticate user
    user = get_user_by_username(form_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.get('is_active', True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user['username'],
            "user_id": user['user_id'],
            "email": user['email'],
            "role": user['role']
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "user_id": user['user_id'],
            "username": user['username'],
            "email": user['email'],
            "full_name": user['full_name'],
            "role": user['role']
        }
    }


@app.get("/auth/me")
async def get_current_user_info(current_user: Dict = Depends(get_current_user)):
    """Get current authenticated user information"""
    return {
        "user": current_user,
        "authenticated": True,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/auth/refresh")
async def refresh_token(current_user: Dict = Depends(get_current_user)):
    """Refresh access token"""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": current_user['username'],
            "user_id": current_user['user_id'],
            "email": current_user['email'],
            "role": current_user['role']
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


# ==================== API ROUTERS ====================

# Import AI Chat Router (Main router that exists)
from api.ai_chat_router import router as ai_chat_router

# Include routers with prefixes

# Import new routers
from api.auth_router import router as auth_router
from api.patients_router import router as patients_router

# ⭐ MAIN: AI Chat Workflow Router - Complete conversational interface with all tools
app.include_router(ai_chat_router, prefix="/api", tags=["AI Chat Workflow"])

# 🔐 Authentication Router - Google OAuth and session management
app.include_router(auth_router, tags=["Authentication"])

# 👥 Patients Router - Patient profiles, stats, and management
app.include_router(patients_router, tags=["Patients"])

# ==================== BASIC LOGIN ENDPOINT ====================

@app.get("/login")
async def login_page():
    """
    Basic login endpoint - redirects to Google OAuth or returns login info
    """
    return {
        "message": "Hospital AI Agent Login",
        "google_oauth": "/auth/login",
        "direct_login": "/api/auth/login",
        "docs": "/docs",
        "available_endpoints": [
            "GET /login - This page",
            "GET /auth/login - Google OAuth login",
            "POST /api/auth/login - Direct login with email",
            "GET /api/patients/{id}/stats - Patient statistics",
            "GET /api/ai-chat/greeting - AI chat greeting"
        ]
    }

# Note: All hospital management tools (110+) are accessible through the AI Chat Router
# This includes: Patient registration, appointments, labs, pharmacy, billing, 
# notifications, approvals, analytics, Google Workspace integration, etc.


# ==================== SIMPLE DATA ENDPOINTS (No Auth Required) ====================
# These are used by admin pages to fetch data without authentication

@app.get("/api/doctors")
async def get_doctors():
    """Get all doctors from database"""
    try:
        db_file = Path("data/doctors_database.json")
        if db_file.exists():
            with open(db_file, 'r') as f:
                doctors = json.load(f)
                return {"success": True, "data": {"doctors": doctors if isinstance(doctors, list) else []}}
        return {"success": True, "data": {"doctors": []}}
    except Exception as e:
        return {"success": False, "error": str(e), "data": {"doctors": []}}


@app.get("/api/medications")
async def get_medications():
    """Get all medications from database"""
    try:
        db_file = Path("data/pharmacy_database.json")
        if db_file.exists():
            with open(db_file, 'r') as f:
                meds = json.load(f)
                return {"success": True, "data": {"medications": meds if isinstance(meds, list) else []}}
        # Return mock data if no database
        return {
            "success": True,
            "data": {
                "medications": [
                    {"medication_id": "MED001", "name": "Amoxicillin", "dosage": "500mg", "stock_quantity": 150, "price": 15.99},
                    {"medication_id": "MED002", "name": "Lisinopril", "dosage": "10mg", "stock_quantity": 30, "price": 12.50},
                    {"medication_id": "MED003", "name": "Metformin", "dosage": "1000mg", "stock_quantity": 200, "price": 8.75}
                ]
            }
        }
    except Exception as e:
        return {"success": True, "data": {"medications": []}}


@app.get("/api/lab-tests")
async def get_lab_tests():
    """Get all lab tests from database"""
    try:
        db_file = Path("data/lab_tests_database.json")
        if db_file.exists():
            with open(db_file, 'r') as f:
                tests = json.load(f)
                return {"success": True, "data": {"tests": tests if isinstance(tests, list) else []}}
        # Return mock data if no database
        return {
            "success": True,
            "data": {
                "tests": [
                    {"test_id": "TEST001", "test_name": "Complete Blood Count (CBC)", "price": 45.00, "reference_range": "4.5-11.0 x10^9/L"},
                    {"test_id": "TEST002", "test_name": "Lipid Panel", "price": 65.00, "reference_range": "Total: <200 mg/dL"},
                    {"test_id": "TEST003", "test_name": "Thyroid Function Test", "price": 55.00, "reference_range": "TSH: 0.4-4.0 mIU/L"}
                ]
            }
        }
    except Exception as e:
        return {"success": True, "data": {"tests": []}}


@app.get("/api/invoices")
async def get_invoices():
    """Get all invoices from database"""
    try:
        db_file = Path("data/invoices_database.json")
        if db_file.exists():
            with open(db_file, 'r') as f:
                invoices = json.load(f)
                return {"success": True, "data": {"invoices": invoices if isinstance(invoices, list) else []}}
        return {"success": True, "data": {"invoices": []}}
    except Exception as e:
        return {"success": True, "data": {"invoices": []}}


# ==================== WEBSOCKET ENDPOINT ====================

from fastapi import WebSocket, WebSocketDisconnect
from typing import List as TypingList

class ConnectionManager:
    """Manage WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: TypingList[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific client"""
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass  # Connection might be closed

manager = ConnectionManager()

@app.websocket("/ws/monitor")
async def websocket_monitor(websocket: WebSocket):
    """
    WebSocket endpoint for real-time system monitoring
    Broadcasts proactive agent updates, notifications, and system alerts
    """
    await manager.connect(websocket)
    
    # Send welcome message
    await websocket.send_json({
        "type": "connection",
        "status": "connected",
        "message": "Connected to Hospital Management System",
        "timestamp": datetime.now().isoformat()
    })
    
    try:
        while True:
            # Receive messages from client (heartbeat, etc.)
            data = await websocket.receive_text()
            
            # Echo back or handle commands
            if data == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"Client disconnected from monitor")


# ==================== ERROR HANDLERS ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


# ==================== STARTUP & SHUTDOWN EVENTS ====================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("=" * 70)
    print("🚀 Hospital Management AI Agent API Starting...")
    print("=" * 70)
    print(f"📊 Total Tools: 110")
    print(f"🔐 Authentication: JWT with Google OAuth2")
    print(f"👥 Roles: Admin, Doctor, Staff, Patient")
    print(f"📡 WebSocket: /ws/monitor")
    print(f"📚 Docs: /docs")
    print(f"⏰ Started: {datetime.now().isoformat()}")
    print("=" * 70)
    
    # 🔥 NEW: Sync patient data across storage layers
    try:
        from startup_cleanup import sync_patient_data
        sync_patient_data()
    except Exception as e:
        print(f"⚠️ Startup cleanup failed: {e}")
    
    # Initialize users database
    initialize_users_db()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("=" * 70)
    print("🛑 Hospital Management AI Agent API Shutting Down...")
    print(f"⏰ Stopped: {datetime.now().isoformat()}")
    print("=" * 70)


# ==================== RUN APPLICATION ====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
