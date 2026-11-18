"""
AI Chat Router - Workflow Chat Agent Endpoint
Handles conversational workflow through all 11 stages
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import uuid

# Import authentication
from api.auth import get_current_user

# Import Workflow Chat Agent
from src.workflow_chat_agent import WorkflowChatAgent, WORKFLOW_STAGES

# Import database managers
from database.redis_cache import cache
from database.db_manager import WorkflowStateDB, PatientDB

# Constants
PATIENT_EMAIL = "iamsamarth786@gmail.com"  # For testing

# Create router
router = APIRouter(
    prefix="/ai-chat",
    tags=["AI Chat"],
    responses={404: {"description": "Not found"}},
)

# ==================== REQUEST/RESPONSE MODELS ====================

class ChatMessage(BaseModel):
    """Chat message model"""
    message: str
    session_id: Optional[str] = None
    patient_id: Optional[str] = None  # For session restoration


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    stage: int
    stage_name: str
    stage_title: str
    stage_complete: bool
    next_stage: Optional[int] = None
    next_stage_title: Optional[str] = None
    awaiting_confirmation: bool = False
    tools_executed: List[str] = []
    patient_id: Optional[str] = None
    timestamp: str


class WorkflowStatus(BaseModel):
    """Workflow status model"""
    patient_id: Optional[str]
    current_stage: int
    stage_name: str
    stage_title: str
    stage_description: str
    progress_percentage: int
    stages_completed: List[str]
    stages_remaining: List[str]
    started_at: str
    last_updated_at: str


# ==================== SESSION MANAGEMENT ====================

chat_sessions = {}  # In-memory cache for active sessions

def generate_session_id() -> str:
    """Generate unique session ID"""
    return str(uuid.uuid4())


def get_or_create_agent(
    user_email: str, 
    session_id: Optional[str] = None,
    patient_id: Optional[str] = None
) -> tuple[WorkflowChatAgent, str]:
    """
    Get existing agent from session or create new one
    
    Session restoration priority:
    1. Check in-memory cache (fastest)
    2. Check Redis cache (fast)
    3. Check PostgreSQL (persistent)
    4. Create new agent
    
    Returns:
        tuple: (agent, session_id)
    """
    
    # Generate session_id if not provided
    if not session_id:
        session_id = generate_session_id()
    
    # Try in-memory cache first (current session)
    if session_id in chat_sessions:
        return chat_sessions[session_id], session_id
    
    # Try Redis cache (fast restore from previous session)
    cached_state = cache.get_session(session_id)
    if cached_state:
        print(f"✅ Restored session from Redis: {session_id}")
        agent = WorkflowChatAgent(
            patient_email=cached_state.get("patient_email", user_email),
            patient_id=cached_state.get("patient_id")
        )
        agent.state = cached_state
        chat_sessions[session_id] = agent
        return agent, session_id
    
    # Try PostgreSQL (persistent restore - user closed browser days ago)
    if not patient_id:
        # Try to find existing patient by EXACT email match
        try:
            patient_db = PatientDB()
            existing_patient = patient_db.get_patient_by_email(user_email)  # EXACT match, not ILIKE
            if existing_patient:
                patient_id = existing_patient.get('patient_id')
                print(f"✅ Found existing patient by email: {patient_id} ({user_email})")
        except Exception as e:
            print(f"⚠️ Could not search for existing patient: {e}")
    
    if patient_id:
        workflow_db = WorkflowStateDB()
        db_state = workflow_db.load_state(patient_id)
        if db_state:
            print(f"✅ Restored session from PostgreSQL: {patient_id} at Stage {db_state.get('current_stage', 1)}")
            agent = WorkflowChatAgent(
                patient_email=db_state.get("email", user_email),
                patient_id=patient_id
            )
            # 🔥 FIX: Merge PostgreSQL state with agent's loaded state (preserves workflow_doc_id from JSON/Redis)
            # Agent already loaded state in __init__ from JSON/Redis which may have additional fields
            agent.state.update(db_state)  # Update with PostgreSQL fields but keep existing ones
            chat_sessions[session_id] = agent
            
            # Cache in Redis for fast future access
            cache.set_session(session_id, db_state, ttl=7200)  # 2 hours
            
            return agent, session_id
    
    # Create new agent
    print(f"✅ Created new session: {session_id}")
    agent = WorkflowChatAgent(
        patient_email=user_email,
        patient_id=patient_id
    )
    chat_sessions[session_id] = agent
    
    # Cache in Redis
    cache.set_session(session_id, agent.state, ttl=7200)
    
    return agent, session_id


# ==================== ENDPOINTS ====================

@router.post("/chat", response_model=ChatResponse)
async def chat_with_workflow_agent(
    message: ChatMessage,
    current_user: dict = Depends(get_current_user)  # ✅ FIXED: Get from auth token
):
    """
    Main chat endpoint for workflow agent
    
    Patient chats with AI agent, which guides them through:
    1. Registration
    2. Document Upload
    3. Medical History
    4. Test Determination
    5. Lab Coordination
    6. Results Analysis
    7. Admission Planning
    8. Treatment Monitoring
    9. Discharge
    10. Analytics
    11. Follow-up
    
    Agent collects info, confirms actions, and executes tools autonomously.
    """
    
    try:
        # ✅ FIXED: Get email from authenticated user, not hardcoded
        user_email = current_user.get('email') or current_user.get('sub', PATIENT_EMAIL)
        print(f"🔑 Chat request from authenticated user: {user_email}")
        
        # Get or restore agent from session
        agent, session_id = get_or_create_agent(
            user_email=user_email,
            session_id=message.session_id,
            patient_id=message.patient_id
        )
        
        # Process message
        result = agent.process_message(message.message)
        
        # Update Redis cache with latest state
        cache.set_session(session_id, agent.state, ttl=7200)  # 2 hours
        
        # Get stage info
        stage_num = result.get("stage", agent.state["current_stage"])
        stage_info = WORKFLOW_STAGES.get(stage_num, {})
        
        next_stage_num = result.get("next_stage")
        next_stage_info = WORKFLOW_STAGES.get(next_stage_num, {}) if next_stage_num else {}
        
        # Build response with session_id
        response = ChatResponse(
            response=result.get("response", ""),
            stage=stage_num,
            stage_name=stage_info.get("name", "unknown"),
            stage_title=stage_info.get("title", "Unknown Stage"),
            stage_complete=result.get("stage_complete", False),
            next_stage=next_stage_num,
            next_stage_title=next_stage_info.get("title") if next_stage_info else None,
            awaiting_confirmation=result.get("awaiting_confirmation", False),
            tools_executed=result.get("tools_executed", []),
            patient_id=agent.patient_id,
            timestamp=datetime.now().isoformat()
        )
        
        # Add session_id to response headers for frontend to store
        return JSONResponse(
            content=response.dict(),
            headers={"X-Session-ID": session_id}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat error: {str(e)}"
        )


@router.get("/greeting")
async def get_greeting(
    session_id: Optional[str] = None,
    patient_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)  # ✅ FIXED: Get from auth token
):
    """
    Get initial greeting message for the chat
    Supports session restoration if session_id or patient_id provided
    """
    
    try:
        # ✅ FIXED: Get email from authenticated user, not hardcoded
        user_email = current_user.get('email') or current_user.get('sub', PATIENT_EMAIL)
        print(f"🔑 Greeting request from authenticated user: {user_email}")
        
        agent, returned_session_id = get_or_create_agent(
            user_email=user_email,
            session_id=session_id,
            patient_id=patient_id
        )
        greeting = agent.get_greeting_message()
        
        stage_info = agent.get_current_stage_info()
        
        return JSONResponse(
            content={
                "greeting": greeting,
                "stage": agent.state["current_stage"],
                "stage_name": stage_info.get("name", "unknown"),
                "stage_title": stage_info.get("title", "Unknown"),
                "patient_id": agent.patient_id
            },
            headers={"X-Session-ID": returned_session_id}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Greeting error: {str(e)}"
        )


@router.get("/status", response_model=WorkflowStatus)
async def get_workflow_status(
    session_id: Optional[str] = None,
    patient_id: Optional[str] = None,
    # TODO: Re-enable after testing: current_user: dict = Depends(get_current_user)
):
    """
    Get current workflow status and progress
    Supports session restoration if session_id or patient_id provided
    """
    
    try:
        user_email = PATIENT_EMAIL  # For testing
        
        agent, returned_session_id = get_or_create_agent(
            user_email=user_email,
            session_id=session_id,
            patient_id=patient_id
        )
        
        current_stage = agent.state["current_stage"]
        stage_info = WORKFLOW_STAGES.get(current_stage, {})
        
        # Calculate progress
        total_stages = len(WORKFLOW_STAGES)
        progress_percentage = int((current_stage - 1) / total_stages * 100)
        
        # Get completed and remaining stages
        stages_completed = [
            WORKFLOW_STAGES[i]["title"]
            for i in range(1, current_stage)
        ]
        
        stages_remaining = [
            WORKFLOW_STAGES[i]["title"]
            for i in range(current_stage + 1, total_stages + 1)
        ]
        
        status_response = WorkflowStatus(
            patient_id=agent.patient_id,
            current_stage=current_stage,
            stage_name=stage_info.get("name", "unknown"),
            stage_title=stage_info.get("title", "Unknown"),
            stage_description=stage_info.get("description", ""),
            progress_percentage=progress_percentage,
            stages_completed=stages_completed,
            stages_remaining=stages_remaining,
            started_at=agent.state.get("workflow_started_at", ""),
            last_updated_at=agent.state.get("last_updated_at", "")
        )
        
        return status_response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Status error: {str(e)}"
        )


@router.post("/reset")
async def reset_workflow(
    # TODO: Re-enable after testing: current_user: dict = Depends(get_current_user)
):
    """
    Reset workflow for current user (start over)
    """
    
    try:
        user_email = PATIENT_EMAIL  # For testing
        patient_id = None
        
        session_key = f"{user_email}_{patient_id or 'new'}"
        
        # Remove existing session
        if session_key in chat_sessions:
            del chat_sessions[session_key]
        
        # Create new agent
        agent = get_or_create_agent(user_email, None)  # Start fresh
        
        return {
            "success": True,
            "message": "Workflow reset successfully",
            "new_stage": agent.state["current_stage"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reset error: {str(e)}"
        )


@router.get("/stages")
async def get_all_stages():
    """
    Get information about all workflow stages
    """
    
    stages_list = []
    
    for stage_num, stage_info in WORKFLOW_STAGES.items():
        stages_list.append({
            "stage_number": stage_num,
            "name": stage_info.get("name"),
            "title": stage_info.get("title"),
            "description": stage_info.get("description"),
            "required_info": stage_info.get("required_info", [])
        })
    
    return {
        "total_stages": len(WORKFLOW_STAGES),
        "stages": stages_list
    }


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "AI Chat Workflow Agent",
        "active_sessions": len(chat_sessions),
        "timestamp": datetime.now().isoformat()
    }


@router.post("/admin/clear-cache")
async def clear_all_caches(current_user: dict = Depends(get_current_user)):
    """
    Admin endpoint to clear all caches (in-memory, Redis, PostgreSQL workflow states)
    Use this to reset a patient to Stage 1
    """
    try:
        # Get patient email from request
        user_email = current_user.get('email')
        
        # Clear in-memory cache
        cleared_sessions = len(chat_sessions)
        chat_sessions.clear()
        
        # Clear Redis cache
        redis_cleared = 0
        try:
            if cache.is_available():
                keys = cache._redis_client.keys('session:*')
                if keys:
                    cache._redis_client.delete(*keys)
                    redis_cleared = len(keys)
        except Exception as e:
            print(f"Redis clear error: {e}")
        
        # Clear PostgreSQL workflow state for this user
        postgres_cleared = False
        try:
            patient_db = PatientDB()
            patient = patient_db.get_patient_by_email(user_email)
            if patient:
                workflow_db = WorkflowStateDB()
                workflow_db.db.execute_query(
                    "DELETE FROM workflow_states WHERE patient_id = %s",
                    (patient['patient_id'],),
                    fetch="none"
                )
                postgres_cleared = True
        except Exception as e:
            print(f"PostgreSQL clear error: {e}")
        
        return {
            "success": True,
            "message": "All caches cleared successfully",
            "details": {
                "in_memory_sessions_cleared": cleared_sessions,
                "redis_keys_cleared": redis_cleared,
                "postgres_workflow_cleared": postgres_cleared,
                "user_email": user_email
            },
            "next_action": "Refresh frontend (Ctrl+Shift+R) or logout/login to start at Stage 1"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cache clear error: {str(e)}"
        )
