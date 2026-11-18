"""
Patients Router for Hospital Management AI Agent
Handles patient-related API endpoints including stats, records, and profile management
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import os

from api.auth import get_current_user
from tools.patient_registration_tool import SearchPatientTool, GetPatientDetailsTool
from tools.database_tool import load_db, save_db, PATIENTS_DB_FILE

# Router setup
router = APIRouter()

# Models
class PatientStats(BaseModel):
    patient_id: str
    name: str
    email: str
    total_appointments: int
    last_visit: Optional[str]
    current_stage: Optional[str]
    health_status: str
    created_at: str

class PatientProfile(BaseModel):
    patient_id: str
    name: str
    email: str
    phone: str
    date_of_birth: Optional[str]
    gender: Optional[str]
    address: Optional[str]
    medical_conditions: List[str] = []
    allergies: List[str] = []
    emergency_contact: Optional[dict] = None

class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[dict] = None

# ==================== PATIENT STATS ENDPOINTS ====================

@router.get("/api/patients/{patient_identifier}/stats", response_model=PatientStats)
async def get_patient_stats(
    patient_identifier: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get patient statistics and dashboard data
    Supports patient_id, email, or generated identifiers like 'patient_samarth'
    """
    try:
        # Load patient database (returns dict with patient_id as keys)
        patients_db = load_db(PATIENTS_DB_FILE)
        
        # Find patient by various identifiers
        patient = None
        
        # Try exact patient_id match (direct dict lookup)
        if patient_identifier in patients_db:
            patient = patients_db[patient_identifier]
        
        # Try email match (search through values)
        if not patient:
            for patient_record in patients_db.values():
                if patient_record.get('email') == patient_identifier:
                    patient = patient_record
                    break
        
        # Try generated identifier match (e.g., patient_samarth)
        if not patient and patient_identifier.startswith('patient_'):
            name_part = patient_identifier.replace('patient_', '').replace('_', ' ')
            for patient_record in patients_db.values():
                if name_part.lower() in patient_record.get('full_name', '').lower():
                    patient = patient_record
                    break
        
        # Try current user match
        if not patient and current_user:
            for patient_record in patients_db.values():
                if patient_record.get('email') == current_user.get('email'):
                    patient = patient_record
                    break
        
        if not patient:
            # Create a default patient record for new users
            if current_user:
                patient_id = f"patient_{current_user['email'].split('@')[0]}"
                patient = {
                    'patient_id': patient_id,
                    'full_name': current_user.get('name', current_user['email'].split('@')[0].title()),
                    'email': current_user['email'],
                    'phone': '',
                    'created_at': datetime.now().isoformat(),
                    'medical_conditions': [],
                    'allergies': [],
                    'appointments': []
                }
                # Save new patient (add to dict)
                patients_db[patient_id] = patient
                save_db(PATIENTS_DB_FILE, patients_db)
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Patient not found: {patient_identifier}"
                )
        
        # Calculate stats
        appointments = patient.get('appointments', [])
        last_visit = None
        if appointments:
            last_visit = max(appointments, key=lambda x: x.get('date', ''))['date']
        
        # Determine health status
        conditions = patient.get('medical_conditions', [])
        if any('critical' in str(c).lower() for c in conditions):
            health_status = "Critical"
        elif any('chronic' in str(c).lower() for c in conditions):
            health_status = "Needs Monitoring"
        elif conditions:
            health_status = "Stable"
        else:
            health_status = "Healthy"
        
        return PatientStats(
            patient_id=patient['patient_id'],
            name=patient.get('full_name', 'Unknown'),
            email=patient['email'],
            total_appointments=len(appointments),
            last_visit=last_visit,
            current_stage=patient.get('current_stage', 'registered'),
            health_status=health_status,
            created_at=patient.get('created_at', datetime.now().isoformat())
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get patient stats: {str(e)}"
        )

@router.get("/api/patients/me/stats")
async def get_my_stats(current_user: dict = Depends(get_current_user)):
    """
    Get current user's patient statistics
    """
    return await get_patient_stats(current_user['email'], current_user)

# ==================== PATIENT PROFILE ENDPOINTS ====================

@router.get("/api/patients/{patient_identifier}/profile", response_model=PatientProfile)
async def get_patient_profile(
    patient_identifier: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed patient profile information
    """
    try:
        # Use search tool to find patient
        search_tool = SearchPatientTool()
        search_result = search_tool._run(query=patient_identifier)
        
        if "not found" in search_result.lower():
            raise HTTPException(
                status_code=404,
                detail=f"Patient profile not found: {patient_identifier}"
            )
        
        # Get detailed info
        details_tool = GetPatientDetailsTool()
        details_result = details_tool._run(patient_id=patient_identifier)
        
        # Parse the results (tools return formatted strings)
        # In a real implementation, tools would return structured data
        
        # Load from database for structured data
        patients_db = load_db(PATIENTS_DB_FILE)
        patient = None
        
        # Search in the dictionary values
        if patient_identifier in patients_db:
            patient = patients_db[patient_identifier]
        else:
            for patient_record in patients_db.values():
                if (patient_record.get('patient_id') == patient_identifier or
                    patient_record.get('email') == patient_identifier):
                    patient = patient_record
                    break
        
        if not patient:
            raise HTTPException(
                status_code=404,
                detail="Patient profile not found"
            )
        
        return PatientProfile(
            patient_id=patient['patient_id'],
            name=patient.get('full_name', ''),
            email=patient['email'],
            phone=patient.get('phone', ''),
            date_of_birth=patient.get('date_of_birth'),
            gender=patient.get('gender'),
            address=patient.get('address'),
            medical_conditions=patient.get('medical_conditions', []),
            allergies=patient.get('allergies', []),
            emergency_contact=patient.get('emergency_contact')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get patient profile: {str(e)}"
        )

@router.put("/api/patients/me/profile")
async def update_my_profile(
    update_request: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update current user's patient profile
    """
    try:
        # Load patients database
        patients_db = load_db(PATIENTS_DB_FILE)
        
        # Find current user's patient record
        patient_id = None
        for pid, patient_record in patients_db.items():
            if patient_record.get('email') == current_user['email']:
                patient_id = pid
                break
        
        if patient_id is None:
            raise HTTPException(
                status_code=404,
                detail="Patient profile not found"
            )
        
        # Update fields
        if update_request.name:
            patients_db[patient_id]['full_name'] = update_request.name
        if update_request.phone:
            patients_db[patient_id]['phone'] = update_request.phone
        if update_request.address:
            patients_db[patient_id]['address'] = update_request.address
        if update_request.emergency_contact:
            patients_db[patient_id]['emergency_contact'] = update_request.emergency_contact
        
        patients_db[patient_id]['updated_at'] = datetime.now().isoformat()
        
        # Save updated data
        save_db(PATIENTS_DB_FILE, patients_db)
        
        return {
            "message": "Profile updated successfully",
            "patient_id": patients_db[patient_id]['patient_id'],
            "updated_at": patients_db[patient_id]['updated_at']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update profile: {str(e)}"
        )

# ==================== PATIENT SEARCH ENDPOINTS ====================

@router.get("/api/patients/search")
async def search_patients(
    q: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Search for patients (for authorized users)
    """
    try:
        # Check if user has search permissions (doctors, staff, admin)
        user_role = current_user.get('role', 'patient')
        if user_role == 'patient':
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions to search patients"
            )
        
        # Use search tool
        search_tool = SearchPatientTool()
        result = search_tool._run(query=q)
        
        return {
            "query": q,
            "results": result,
            "searched_by": current_user['email'],
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

# ==================== HEALTH CHECK ====================

@router.get("/api/patients/health")
async def patients_health_check():
    """
    Health check for patients service
    """
    try:
        # Check database connectivity
        patients = load_db(PATIENTS_DB_FILE)
        patient_count = len(patients)
        
        return {
            "status": "healthy",
            "service": "patients",
            "patient_count": patient_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "patients",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }