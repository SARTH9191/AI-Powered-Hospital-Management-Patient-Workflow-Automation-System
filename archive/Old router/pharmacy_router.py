"""Pharmacy Management Router - API Endpoints
===============================================

This router provides comprehensive pharmacy management functionality:
- Dispense medications with prescription validation
- Check drug inventory and stock levels
- Update inventory (add stock, remove expired items)
- Get medication information and usage guidelines
- Process prescription refill requests
- Get dispensing history for patients
- Check drug interactions and contraindications
- Get pharmacy statistics and analytics

All endpoints are protected with role-based access control.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import os
from api.auth import get_current_user, require_admin, require_doctor, require_staff

# Import pharmacy management tools
from tools.pharmacy_tool import (
    DispenseMedicationTool,
    CheckDrugInventoryTool,
    UpdateInventoryTool,
    GetMedicationInfoTool,
    ProcessRefillRequestTool,
    GetDispensingHistoryTool,
    CheckDrugInteractionsTool,
    GetPharmacyStatisticsTool
)

router = APIRouter()

# Initialize tools
dispense_tool = DispenseMedicationTool()
check_inventory_tool = CheckDrugInventoryTool()
update_inventory_tool = UpdateInventoryTool()
get_med_info_tool = GetMedicationInfoTool()
process_refill_tool = ProcessRefillRequestTool()
get_history_tool = GetDispensingHistoryTool()
check_interactions_tool = CheckDrugInteractionsTool()
get_stats_tool = GetPharmacyStatisticsTool()

# =====================================================
# Pydantic Models
# =====================================================

class DispenseMedicationRequest(BaseModel):
    """Request model for dispensing medication"""
    prescription_id: str = Field(..., description="Prescription ID")
    patient_id: str = Field(..., description="Patient ID")
    medication_name: str = Field(..., description="Medication name")
    quantity: int = Field(..., description="Quantity to dispense", gt=0)
    pharmacist_id: str = Field(..., description="Pharmacist ID dispensing the medication")
    notes: Optional[str] = Field(None, description="Dispensing notes")

class UpdateInventoryRequest(BaseModel):
    """Request model for updating inventory"""
    medication_name: str = Field(..., description="Medication name")
    action: str = Field(..., description="Action: add_stock, remove_stock, mark_expired")
    quantity: int = Field(..., description="Quantity to add/remove", gt=0)
    batch_number: Optional[str] = Field(None, description="Batch/lot number")
    expiry_date: Optional[str] = Field(None, description="Expiry date (YYYY-MM-DD)")
    notes: Optional[str] = Field(None, description="Update notes")

class ProcessRefillRequest(BaseModel):
    """Request model for processing refill"""
    prescription_id: str = Field(..., description="Prescription ID to refill")
    patient_id: str = Field(..., description="Patient ID")
    requested_quantity: Optional[int] = Field(None, description="Requested quantity")
    notes: Optional[str] = Field(None, description="Refill notes")

class CheckInteractionsRequest(BaseModel):
    """Request model for checking drug interactions"""
    medications: List[str] = Field(..., description="List of medication names to check interactions")
    patient_id: Optional[str] = Field(None, description="Patient ID for personalized check")

class APIResponse(BaseModel):
    """Standard API response format"""
    success: bool
    data: Any
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# =====================================================
# Endpoints
# =====================================================

@router.get("/", response_model=APIResponse)
async def pharmacy_info(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get information about the Pharmacy Management API
    
    Returns list of available endpoints and their descriptions.
    """
    return {
        "success": True,
        "data": {
            "endpoints": [
                "GET / - API information",
                "POST /dispense - Dispense medication",
                "GET /inventory/{medication_name} - Check drug inventory",
                "PUT /inventory - Update inventory",
                "GET /medication/{medication_name}/info - Get medication info",
                "POST /refill - Process refill request",
                "GET /patient/{patient_id}/history - Get dispensing history",
                "POST /interactions - Check drug interactions",
                "GET /stats - Get pharmacy statistics"
            ],
            "tools_available": 8,
            "description": "Comprehensive pharmacy management with inventory and safety checks"
        },
        "message": "Pharmacy Management API",
        "timestamp": datetime.now().isoformat()
    }


@router.post("/dispense", response_model=APIResponse)
async def dispense_medication(
    request: DispenseMedicationRequest,
    current_user: Dict = Depends(require_staff)
):
    """
    Dispense medication with prescription validation
    
    **Access:** Staff (Pharmacists), Admin
    
    **Parameters:**
    - prescription_id: Valid prescription ID
    - patient_id: Patient ID
    - medication_name: Name of medication
    - quantity: Quantity to dispense
    - pharmacist_id: Pharmacist dispensing the medication
    - notes: Dispensing notes (optional)
    
    **Returns:** Dispensing confirmation with details
    """
    try:
        result = dispense_tool._run(
            prescription_id=request.prescription_id,
            patient_id=request.patient_id,
            medication_name=request.medication_name,
            quantity=request.quantity,
            pharmacist_id=request.pharmacist_id,
            notes=request.notes
        )
        
        # Check for errors
        if "❌" in result or "Error" in result:
            if "not found" in result or "Invalid" in result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result
                )
            if "Insufficient" in result or "out of stock" in result:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=result
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result
            )
        
        return {
            "success": True,
            "data": {"dispensing_details": result},
            "message": "Medication dispensed successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to dispense medication: {str(e)}"
        )


@router.get("/inventory/{medication_name}", response_model=APIResponse)
async def check_drug_inventory(
    medication_name: str,
    current_user: Dict = Depends(require_staff)
):
    """
    Check inventory status for a medication
    
    **Access:** Staff, Doctor, Admin
    
    **Parameters:**
    - medication_name: Name of medication to check
    
    **Returns:** Current stock level, expiry dates, and reorder alerts
    """
    try:
        result = check_inventory_tool._run(medication_name=medication_name)
        
        # Check for errors
        if "❌" in result or "Error" in result:
            if "not found" in result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result
            )
        
        return {
            "success": True,
            "data": {"inventory_status": result},
            "message": "Inventory checked successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check inventory: {str(e)}"
        )


@router.put("/inventory", response_model=APIResponse)
async def update_inventory(
    request: UpdateInventoryRequest,
    current_user: Dict = Depends(require_staff)
):
    """
    Update medication inventory
    
    **Access:** Staff (Pharmacists), Admin
    
    **Parameters:**
    - medication_name: Medication name
    - action: add_stock, remove_stock, or mark_expired
    - quantity: Quantity to add/remove
    - batch_number: Batch/lot number (optional)
    - expiry_date: Expiry date for new stock (optional)
    - notes: Update notes (optional)
    
    **Returns:** Updated inventory status
    """
    try:
        result = update_inventory_tool._run(
            medication_name=request.medication_name,
            action=request.action,
            quantity=request.quantity,
            batch_number=request.batch_number,
            expiry_date=request.expiry_date,
            notes=request.notes
        )
        
        # Check for errors
        if "❌" in result or "Error" in result:
            if "not found" in result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result
            )
        
        return {
            "success": True,
            "data": {"inventory_update": result},
            "message": "Inventory updated successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update inventory: {str(e)}"
        )


@router.get("/medication/{medication_name}/info", response_model=APIResponse)
async def get_medication_info(
    medication_name: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get detailed medication information
    
    **Access:** All authenticated users
    
    **Parameters:**
    - medication_name: Name of medication
    
    **Returns:** Medication details including:
    - Generic and brand names
    - Dosage forms and strengths
    - Indications and contraindications
    - Side effects and warnings
    - Storage requirements
    """
    try:
        result = get_med_info_tool._run(medication_name=medication_name)
        
        # Check for errors
        if "❌" in result or "Error" in result:
            if "not found" in result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result
            )
        
        return {
            "success": True,
            "data": {"medication_info": result},
            "message": "Medication information retrieved successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get medication info: {str(e)}"
        )


@router.post("/refill", response_model=APIResponse)
async def process_refill_request(
    request: ProcessRefillRequest,
    current_user: Dict = Depends(require_staff)
):
    """
    Process prescription refill request
    
    **Access:** Staff (Pharmacists), Doctor, Admin
    
    **Parameters:**
    - prescription_id: Prescription ID to refill
    - patient_id: Patient ID
    - requested_quantity: Quantity requested (optional)
    - notes: Refill notes (optional)
    
    **Returns:** Refill approval/denial with reasons
    """
    try:
        result = process_refill_tool._run(
            prescription_id=request.prescription_id,
            patient_id=request.patient_id,
            requested_quantity=request.requested_quantity,
            notes=request.notes
        )
        
        # Check for errors
        if "❌" in result or "Error" in result:
            if "not found" in result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result
                )
            if "denied" in result or "cannot be refilled" in result:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=result
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result
            )
        
        return {
            "success": True,
            "data": {"refill_details": result},
            "message": "Refill processed successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process refill: {str(e)}"
        )


@router.get("/patient/{patient_id}/history", response_model=APIResponse)
async def get_dispensing_history(
    patient_id: str,
    medication_name: Optional[str] = Query(None, description="Filter by medication name"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: Dict = Depends(require_doctor)
):
    """
    Get patient's medication dispensing history
    
    **Access:** Doctor, Admin
    
    **Parameters:**
    - patient_id: Patient ID
    - medication_name: Filter by medication (optional)
    - start_date: Filter start date (optional)
    - end_date: Filter end date (optional)
    
    **Returns:** Complete dispensing history with dates, quantities, pharmacists
    """
    try:
        result = get_history_tool._run(
            patient_id=patient_id,
            medication_name=medication_name,
            start_date=start_date,
            end_date=end_date
        )
        
        # Check for errors
        if "❌" in result or "Error" in result:
            if "not found" in result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result
            )
        
        return {
            "success": True,
            "data": {"dispensing_history": result},
            "message": "Dispensing history retrieved successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dispensing history: {str(e)}"
        )


@router.post("/interactions", response_model=APIResponse)
async def check_drug_interactions(
    request: CheckInteractionsRequest,
    current_user: Dict = Depends(require_doctor)
):
    """
    Check for drug interactions and contraindications
    
    **Access:** Doctor, Admin
    
    **Parameters:**
    - medications: List of medication names
    - patient_id: Patient ID for personalized check (optional)
    
    **Returns:** Interaction warnings with severity levels and recommendations
    """
    try:
        result = check_interactions_tool._run(
            medications=request.medications,
            patient_id=request.patient_id
        )
        
        return {
            "success": True,
            "data": {"interaction_check": result},
            "message": "Drug interactions checked successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check drug interactions: {str(e)}"
        )


@router.get("/stats", response_model=APIResponse)
async def get_pharmacy_statistics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: Dict = Depends(require_admin)
):
    """
    Get pharmacy statistics and analytics
    
    **Access:** Admin only
    
    **Parameters:**
    - start_date: Start date for statistics (optional)
    - end_date: End date for statistics (optional)
    
    **Returns:** Comprehensive pharmacy analytics including:
    - Total prescriptions dispensed
    - Most dispensed medications
    - Inventory turnover
    - Low stock alerts
    - Refill request statistics
    """
    try:
        result = get_stats_tool._run(
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "success": True,
            "data": {"statistics": result},
            "message": "Pharmacy statistics retrieved successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pharmacy statistics: {str(e)}"
        )


# =====================================================
# NEW ENDPOINT: Get Patient Prescriptions (for frontend)
# =====================================================

@router.get("/patient/{patient_id}/prescriptions", response_model=APIResponse)
async def get_patient_prescriptions(
    patient_id: str,
    status_filter: Optional[str] = Query(None, description="Filter by status: active, completed, cancelled, expired"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get all prescriptions for a patient (returns JSON array for frontend)
    
    **Access:** Patient (own data), Doctor, Staff, Admin
    
    **Parameters:**
    - patient_id: Patient ID
    - status_filter: Optional status filter
    
    **Returns:** JSON array of prescriptions
    """
    try:
        # Patients can only access their own prescriptions
        user_role = current_user.get('role')
        user_id = current_user.get('user_id')
        
        if user_role == 'patient' and user_id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Patients can only access their own prescriptions"
            )
        
        # Read prescriptions database directly
        db_path = os.path.join('data', 'prescriptions_database.json')
        
        if not os.path.exists(db_path):
            return {
                "success": True,
                "data": {"prescriptions": []},
                "message": "No prescriptions found",
                "timestamp": datetime.now().isoformat()
            }
        
        with open(db_path, 'r') as f:
            prescriptions_data = json.load(f)
        
        # Get all prescriptions from the nested structure
        all_prescriptions = prescriptions_data.get('prescriptions', [])
        
        # Filter by patient_id
        patient_prescriptions = [
            prescription for prescription in all_prescriptions
            if prescription.get('patient_id') == patient_id
        ]
        
        # Apply status filter if provided
        if status_filter:
            patient_prescriptions = [
                prescription for prescription in patient_prescriptions
                if prescription.get('status') == status_filter
            ]
        
        return {
            "success": True,
            "data": {"prescriptions": patient_prescriptions},
            "message": f"Found {len(patient_prescriptions)} prescriptions",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get patient prescriptions: {str(e)}"
        )
