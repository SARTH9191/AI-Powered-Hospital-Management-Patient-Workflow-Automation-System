"""
Patient Management Router - API Endpoints
Exposes patient management tools as REST API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

# Import authentication
from api.auth import get_current_user, require_admin, require_doctor, require_staff

# Import patient tools
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.patient_registration_tool import (
    RegisterPatientTool,
    GetPatientDetailsTool,
    UpdatePatientInfoTool,
    SearchPatientTool,
    ListAllPatientsTool
)

from tools.medical_records_tool import (
    GetMedicalHistoryTool,
    UpdateDiagnosisTool,
    AddAllergyTool,
    AddChronicConditionTool
)

# Create router
router = APIRouter()

# Initialize tools
register_tool = RegisterPatientTool()
get_details_tool = GetPatientDetailsTool()
update_info_tool = UpdatePatientInfoTool()
search_tool = SearchPatientTool()
list_tool = ListAllPatientsTool()
get_history_tool = GetMedicalHistoryTool()
update_diagnosis_tool = UpdateDiagnosisTool()
add_allergy_tool = AddAllergyTool()
add_condition_tool = AddChronicConditionTool()


# ==================== REQUEST/RESPONSE MODELS ====================

class RegisterPatientRequest(BaseModel):
    """Request model for patient registration"""
    name: str = Field(..., description="Patient full name")
    age: int = Field(..., ge=0, le=150, description="Patient age")
    gender: str = Field(..., description="Gender: Male, Female, Other")
    phone: str = Field(..., description="Contact phone number")
    email: Optional[str] = Field(None, description="Email address")
    address: Optional[str] = Field(None, description="Home address")
    emergency_contact: Optional[str] = Field(None, description="Emergency contact name")
    emergency_phone: Optional[str] = Field(None, description="Emergency contact phone")
    blood_group: Optional[str] = Field(None, description="Blood group (A+, B-, O+, etc.)")
    has_insurance: Optional[bool] = Field(False, description="Has insurance coverage")
    insurance_details: Optional[Dict] = Field(None, description="Insurance provider details")


class UpdatePatientRequest(BaseModel):
    """Request model for updating patient info"""
    phone: Optional[str] = Field(None, description="New phone number")
    email: Optional[str] = Field(None, description="New email address")
    address: Optional[str] = Field(None, description="New address")
    emergency_contact: Optional[str] = Field(None, description="New emergency contact")
    emergency_phone: Optional[str] = Field(None, description="New emergency phone")
    insurance_details: Optional[Dict] = Field(None, description="Updated insurance details")


class SearchPatientRequest(BaseModel):
    """Request model for patient search"""
    query: str = Field(..., description="Search query (name, ID, or phone)")


class UpdateMedicalHistoryRequest(BaseModel):
    """Request model for medical history update"""
    diagnosis: Optional[str] = Field(None, description="New diagnosis")
    notes: Optional[str] = Field(None, description="Additional notes")
    allergy: Optional[str] = Field(None, description="New allergy to add")
    chronic_condition: Optional[str] = Field(None, description="New chronic condition")


class APIResponse(BaseModel):
    """Standard API response"""
    success: bool
    data: Any
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# ==================== API ENDPOINTS ====================

@router.get("/")
async def patients_root(current_user: Dict = Depends(get_current_user)):
    """
    Patient Management API Information
    
    **Available Endpoints:**
    - POST /register - Register new patient
    - GET /{patient_id} - Get patient details
    - PUT /{patient_id} - Update patient information
    - DELETE /{patient_id} - Delete patient record
    - GET /search - Search patients by name/ID/phone
    - GET /list - List all patients
    - GET /{patient_id}/history - Get medical history
    - PUT /{patient_id}/history - Update medical history
    """
    return {
        "message": "Patient Management API",
        "version": "1.0.0",
        "endpoints": 8,
        "tools": [
            "RegisterPatientTool",
            "GetPatientDetailsTool", 
            "UpdatePatientInfoTool",
            "SearchPatientTool",
            "ListAllPatientsTool",
            "GetMedicalHistoryTool",
            "UpdateDiagnosisTool"
        ],
        "total_tools": 7
    }


@router.post("/register", response_model=APIResponse)
async def register_patient(
    request: RegisterPatientRequest,
    current_user: Dict = Depends(require_staff)
):
    """
    Register a new patient in the system
    
    **Permissions:** Admin, Doctor, Staff
    
    **Required Fields:**
    - name, age, gender, phone
    
    **Optional Fields:**
    - email, address, emergency contacts, insurance details
    
    **Returns:**
    - Patient ID (auto-generated)
    - Registration timestamp
    - Patient folder path
    """
    try:
        result = register_tool._run(
            name=request.name,
            age=request.age,
            gender=request.gender,
            phone=request.phone,
            email=request.email,
            address=request.address,
            emergency_contact=request.emergency_contact,
            emergency_phone=request.emergency_phone,
            blood_group=request.blood_group,
            has_insurance=request.has_insurance,
            insurance_details=request.insurance_details
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"Patient registered successfully: {request.name}",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register patient: {str(e)}"
        )


@router.get("/{patient_id}", response_model=APIResponse)
async def get_patient(
    patient_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get patient details by ID
    
    **Permissions:** All authenticated users
    
    **Returns:**
    - Complete patient profile
    - Demographics
    - Contact information
    - Insurance details
    - Registration date
    """
    try:
        result = get_details_tool._run(patient_id=patient_id)
        
        # Check if patient exists
        if "error" in result.lower() or "not found" in result.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient not found: {patient_id}"
            )
        
        return {
            "success": True,
            "data": result,
            "message": "Patient details retrieved successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get patient details: {str(e)}"
        )


@router.put("/{patient_id}", response_model=APIResponse)
async def update_patient(
    patient_id: str,
    request: UpdatePatientRequest,
    current_user: Dict = Depends(require_staff)
):
    """
    Update patient information
    
    **Permissions:** Admin, Doctor, Staff
    
    **Updatable Fields:**
    - Contact information (phone, email, address)
    - Emergency contacts
    - Insurance details
    
    **Returns:**
    - Updated patient record
    - Update timestamp
    """
    try:
        # Build updates dict from provided fields only
        updates = {}
        if request.phone:
            updates["phone"] = request.phone
        if request.email:
            updates["email"] = request.email
        if request.address:
            updates["address"] = request.address
        if request.emergency_contact:
            updates["emergency_contact"] = request.emergency_contact
        if request.emergency_phone:
            updates["emergency_phone"] = request.emergency_phone
        if request.insurance_details:
            updates["insurance_details"] = request.insurance_details
        
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
        
        result = update_info_tool._run(
            patient_id=patient_id,
            updates=updates
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"Patient {patient_id} updated successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update patient: {str(e)}"
        )


@router.delete("/{patient_id}", response_model=APIResponse)
async def delete_patient(
    patient_id: str,
    current_user: Dict = Depends(require_admin)
):
    """
    Delete patient record (Admin only)
    
    **Permissions:** Admin only
    
    **Warning:** This is a permanent action
    
    **Returns:**
    - Deletion confirmation
    - Archived data location
    """
    try:
        # Load patients database
        from tools.patient_registration_tool import load_patients_db, save_patients_db
        
        db = load_patients_db()
        
        if patient_id not in db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient not found: {patient_id}"
            )
        
        # Archive patient data before deletion
        archived_data = db[patient_id].copy()
        archived_data["deleted_at"] = datetime.now().isoformat()
        archived_data["deleted_by"] = current_user.get("username", "admin")
        
        # Remove from active database
        del db[patient_id]
        save_patients_db(db)
        
        return {
            "success": True,
            "data": {
                "patient_id": patient_id,
                "archived_data": archived_data
            },
            "message": f"Patient {patient_id} deleted successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete patient: {str(e)}"
        )


@router.get("/search/query", response_model=APIResponse)
async def search_patients(
    query: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Search patients by name, ID, or phone number
    
    **Permissions:** All authenticated users
    
    **Search By:**
    - Patient name (partial match)
    - Patient ID (exact match)
    - Phone number (partial match)
    
    **Returns:**
    - List of matching patients
    - Patient count
    """
    try:
        result = search_tool._run(query=query)
        
        return {
            "success": True,
            "data": result,
            "message": f"Search completed for: {query}",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/list/all", response_model=APIResponse)
async def list_all_patients(
    current_user: Dict = Depends(require_staff)
):
    """
    List all registered patients
    
    **Permissions:** Admin, Doctor, Staff
    
    **Returns:**
    - Complete patient list
    - Total count
    - Summary statistics
    """
    try:
        result = list_tool._run()
        
        return {
            "success": True,
            "data": result,
            "message": "All patients retrieved successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list patients: {str(e)}"
        )


@router.get("/{patient_id}/history", response_model=APIResponse)
async def get_medical_history(
    patient_id: str,
    current_user: Dict = Depends(require_doctor)
):
    """
    Get patient's complete medical history
    
    **Permissions:** Admin, Doctor
    
    **Returns:**
    - Chronic conditions
    - Allergies
    - Past diagnoses
    - Current medications
    - Treatment timeline
    - Past procedures
    """
    try:
        result = get_history_tool._run(patient_id=patient_id)
        
        if "error" in result.lower() or "not found" in result.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medical history not found for patient: {patient_id}"
            )
        
        return {
            "success": True,
            "data": result,
            "message": f"Medical history retrieved for patient {patient_id}",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get medical history: {str(e)}"
        )


@router.put("/{patient_id}/history", response_model=APIResponse)
async def update_medical_history(
    patient_id: str,
    request: UpdateMedicalHistoryRequest,
    current_user: Dict = Depends(require_doctor)
):
    """
    Update patient's medical history
    
    **Permissions:** Admin, Doctor
    
    **Updatable Fields:**
    - Diagnosis
    - Allergies
    - Chronic conditions
    - Clinical notes
    
    **Returns:**
    - Updated medical record
    - Update timestamp
    """
    try:
        results = []
        
        # Update diagnosis if provided
        if request.diagnosis:
            diagnosis_result = update_diagnosis_tool._run(
                patient_id=patient_id,
                new_diagnosis=request.diagnosis,
                notes=request.notes or ""
            )
            results.append({"diagnosis": diagnosis_result})
        
        # Add allergy if provided
        if request.allergy:
            allergy_result = add_allergy_tool._run(
                patient_id=patient_id,
                allergy_name=request.allergy,
                severity="Unknown",
                notes=request.notes or ""
            )
            results.append({"allergy": allergy_result})
        
        # Add chronic condition if provided
        if request.chronic_condition:
            condition_result = add_condition_tool._run(
                patient_id=patient_id,
                condition_name=request.chronic_condition,
                diagnosed_date=datetime.now().strftime("%Y-%m-%d"),
                notes=request.notes or ""
            )
            results.append({"chronic_condition": condition_result})
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No updates provided for medical history"
            )
        
        return {
            "success": True,
            "data": results,
            "message": f"Medical history updated for patient {patient_id}",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update medical history: {str(e)}"
        )
