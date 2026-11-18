"""Laboratory Management Router - API Endpoints
=================================================

This router provides comprehensive laboratory test management functionality:
- Order lab tests for patients
- Update test status (Sample Collected, In Progress, Completed)
- Add test results and values
- Get test results and reports
- Generate lab reports
- Get critical/abnormal results
- Track sample status
- Get lab statistics and analytics
- Schedule lab appointments
- Get patient lab history

All endpoints are protected with role-based access control.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from api.auth import get_current_user, require_admin, require_doctor, require_staff
import json
import os

# Import lab management tools
from tools.lab_management_tool import (
    OrderLabTestTool,
    UpdateTestStatusTool,
    AddTestResultsTool,
    GetTestResultsTool,
    GenerateLabReportTool,
    GetCriticalResultsTool,
    TrackSampleTool,
    GetLabStatisticsTool,
    ScheduleLabAppointmentTool,
    GetPatientLabHistoryTool
)

router = APIRouter()

# Initialize tools
order_test_tool = OrderLabTestTool()
update_status_tool = UpdateTestStatusTool()
add_results_tool = AddTestResultsTool()
get_results_tool = GetTestResultsTool()
generate_report_tool = GenerateLabReportTool()
get_critical_tool = GetCriticalResultsTool()
track_sample_tool = TrackSampleTool()
get_stats_tool = GetLabStatisticsTool()
schedule_appointment_tool = ScheduleLabAppointmentTool()
get_history_tool = GetPatientLabHistoryTool()

# =====================================================
# Pydantic Models
# =====================================================

class OrderLabTestRequest(BaseModel):
    """Request model for ordering a lab test"""
    patient_id: str = Field(..., description="Patient ID (e.g., REG2025123456)")
    test_name: str = Field(..., description="Name of lab test (e.g., Complete Blood Count, Lipid Panel)")
    ordered_by: str = Field(..., description="Doctor ID who ordered the test")
    priority: str = Field("Normal", description="Priority: Routine, Urgent, STAT")
    notes: Optional[str] = Field(None, description="Additional notes or instructions")

class UpdateTestStatusRequest(BaseModel):
    """Request model for updating test status"""
    new_status: str = Field(..., description="New status: Sample Collected, In Progress, Completed, Cancelled")
    notes: Optional[str] = Field(None, description="Notes about status update")

class AddTestResultsRequest(BaseModel):
    """Request model for adding test results"""
    test_parameters: List[Dict[str, Any]] = Field(..., description="List of test parameters with values and ranges")
    interpretation: Optional[str] = Field(None, description="Doctor's interpretation of results")
    notes: Optional[str] = Field(None, description="Additional notes")

class ScheduleLabAppointmentRequest(BaseModel):
    """Request model for scheduling lab appointment"""
    patient_id: str = Field(..., description="Patient ID")
    test_name: str = Field(..., description="Test name")
    appointment_date: str = Field(..., description="Date (YYYY-MM-DD)")
    appointment_time: str = Field(..., description="Time (HH:MM)")
    notes: Optional[str] = Field(None, description="Additional notes")

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
async def labs_info(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get information about the Lab Management API
    
    Returns list of available endpoints and their descriptions.
    """
    return {
        "success": True,
        "data": {
            "endpoints": [
                "GET / - API information",
                "POST /order - Order new lab test",
                "PUT /{test_id}/status - Update test status",
                "POST /{test_id}/results - Add test results",
                "GET /{test_id}/results - Get test results",
                "GET /{test_id}/report - Generate lab report",
                "GET /critical - Get critical/abnormal results",
                "GET /{test_id}/track - Track sample status",
                "GET /stats - Get lab statistics",
                "POST /schedule - Schedule lab appointment",
                "GET /patient/{patient_id}/history - Get patient lab history"
            ],
            "tools_available": 10,
            "description": "Comprehensive lab test management with result tracking and analytics"
        },
        "message": "Laboratory Management API",
        "timestamp": datetime.now().isoformat()
    }


@router.post("/order", response_model=APIResponse)
async def order_lab_test(
    request: OrderLabTestRequest,
    current_user: Dict = Depends(require_doctor)
):
    """
    Order a new lab test for a patient
    
    **Access:** Doctor, Admin
    
    **Parameters:**
    - patient_id: Patient ID
    - test_name: Name of lab test
    - ordered_by: Doctor ID
    - priority: Routine, Urgent, or STAT
    - notes: Additional instructions (optional)
    
    **Returns:** Test order confirmation with test ID
    """
    try:
        result = order_test_tool._run(
            patient_id=request.patient_id,
            test_name=request.test_name,
            ordered_by=request.ordered_by,
            priority=request.priority,
            notes=request.notes
        )
        
        # Check for errors
        if "❌" in result or "Error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result
            )
        
        return {
            "success": True,
            "data": {"order_details": result},
            "message": "Lab test ordered successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to order lab test: {str(e)}"
        )


@router.put("/{test_id}/status", response_model=APIResponse)
async def update_test_status(
    test_id: str,
    request: UpdateTestStatusRequest,
    current_user: Dict = Depends(require_staff)
):
    """
    Update status of a lab test
    
    **Access:** Staff, Doctor, Admin
    
    **Parameters:**
    - test_id: Lab test ID
    - new_status: Sample Collected, In Progress, Completed, Cancelled
    - notes: Status update notes (optional)
    
    **Returns:** Updated test status
    """
    try:
        result = update_status_tool._run(
            test_id=test_id,
            new_status=request.new_status,
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
            "data": {"status_update": result},
            "message": "Test status updated successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update test status: {str(e)}"
        )


@router.post("/{test_id}/results", response_model=APIResponse)
async def add_test_results(
    test_id: str,
    request: AddTestResultsRequest,
    current_user: Dict = Depends(require_doctor)
):
    """
    Add results to a lab test
    
    **Access:** Doctor, Admin (Lab technicians in production)
    
    **Parameters:**
    - test_id: Lab test ID
    - test_parameters: List of parameters with values and normal ranges
    - interpretation: Doctor's interpretation (optional)
    - notes: Additional notes (optional)
    
    **Returns:** Test results confirmation
    """
    try:
        result = add_results_tool._run(
            test_id=test_id,
            test_parameters=request.test_parameters,
            interpretation=request.interpretation,
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
            "data": {"results_added": result},
            "message": "Test results added successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add test results: {str(e)}"
        )


@router.get("/{test_id}/results", response_model=APIResponse)
async def get_test_results(
    test_id: str,
    current_user: Dict = Depends(require_doctor)
):
    """
    Get results for a specific lab test
    
    **Access:** Doctor, Admin
    
    **Parameters:**
    - test_id: Lab test ID
    
    **Returns:** Complete test results with parameters and interpretation
    """
    try:
        result = get_results_tool._run(test_id=test_id)
        
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
            "data": {"test_results": result},
            "message": "Test results retrieved successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get test results: {str(e)}"
        )


@router.get("/{test_id}/report", response_model=APIResponse)
async def generate_lab_report(
    test_id: str,
    include_header: bool = Query(True, description="Include hospital header in report"),
    current_user: Dict = Depends(require_doctor)
):
    """
    Generate formatted lab report
    
    **Access:** Doctor, Admin
    
    **Parameters:**
    - test_id: Lab test ID
    - include_header: Include hospital information in header
    
    **Returns:** Formatted lab report ready for printing/email
    """
    try:
        result = generate_report_tool._run(
            test_id=test_id,
            include_header=include_header
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
            "data": {"lab_report": result},
            "message": "Lab report generated successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate lab report: {str(e)}"
        )


@router.get("/critical", response_model=APIResponse)
async def get_critical_results(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: Dict = Depends(require_doctor)
):
    """
    Get all critical/abnormal lab results
    
    **Access:** Doctor, Admin
    
    **Parameters:**
    - start_date: Filter by start date (optional)
    - end_date: Filter by end date (optional)
    
    **Returns:** List of tests with critical/abnormal values
    """
    try:
        result = get_critical_tool._run(
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "success": True,
            "data": {"critical_results": result},
            "message": "Critical results retrieved successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get critical results: {str(e)}"
        )


@router.get("/{test_id}/track", response_model=APIResponse)
async def track_sample(
    test_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Track sample status and history
    
    **Access:** All authenticated users
    
    **Parameters:**
    - test_id: Lab test ID
    
    **Returns:** Sample tracking information with status history
    """
    try:
        result = track_sample_tool._run(test_id=test_id)
        
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
            "data": {"sample_tracking": result},
            "message": "Sample tracking retrieved successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track sample: {str(e)}"
        )


@router.get("/stats", response_model=APIResponse)
async def get_lab_statistics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: Dict = Depends(require_admin)
):
    """
    Get lab statistics and analytics
    
    **Access:** Admin only
    
    **Parameters:**
    - start_date: Start date for statistics (optional)
    - end_date: End date for statistics (optional)
    
    **Returns:** Comprehensive lab analytics including:
    - Total tests by status
    - Tests by type
    - Average turnaround time
    - Critical results count
    - Most ordered tests
    """
    try:
        result = get_stats_tool._run(
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "success": True,
            "data": {"statistics": result},
            "message": "Lab statistics retrieved successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get lab statistics: {str(e)}"
        )


@router.post("/schedule", response_model=APIResponse)
async def schedule_lab_appointment(
    request: ScheduleLabAppointmentRequest,
    current_user: Dict = Depends(require_staff)
):
    """
    Schedule a lab test appointment
    
    **Access:** Staff, Doctor, Admin
    
    **Parameters:**
    - patient_id: Patient ID
    - test_name: Test name
    - appointment_date: Date (YYYY-MM-DD)
    - appointment_time: Time (HH:MM)
    - notes: Additional notes (optional)
    
    **Returns:** Lab appointment confirmation
    """
    try:
        result = schedule_appointment_tool._run(
            patient_id=request.patient_id,
            test_name=request.test_name,
            appointment_date=request.appointment_date,
            appointment_time=request.appointment_time,
            notes=request.notes
        )
        
        # Check for errors
        if "❌" in result or "Error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result
            )
        
        return {
            "success": True,
            "data": {"appointment_details": result},
            "message": "Lab appointment scheduled successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule lab appointment: {str(e)}"
        )


@router.get("/patient/{patient_id}/history", response_model=APIResponse)
async def get_patient_lab_history(
    patient_id: str,
    test_type: Optional[str] = Query(None, description="Filter by test type"),
    current_user: Dict = Depends(get_current_user)  # Changed from require_doctor to allow patients
):
    """
    Get complete lab test history for a patient
    
    **Access:** All authenticated users (patients can view their own labs)
    
    **Parameters:**
    - patient_id: Patient ID
    - test_type: Filter by test type (optional)
    
    **Returns:** Complete lab history with all tests and results
    """
    try:
        # Read labs database directly
        labs_file = "data/labs_database.json"
        if os.path.exists(labs_file):
            with open(labs_file, 'r') as f:
                data = json.load(f)
                tests = data.get('tests', [])
        else:
            tests = []
        
        # Filter by patient_id
        patient_tests = [test for test in tests if test.get('patient_id') == patient_id]
        
        # Filter by test_type if provided
        if test_type:
            patient_tests = [test for test in patient_tests if test.get('test_type') == test_type]
        
        return {
            "success": True,
            "data": {"lab_history": patient_tests},
            "message": f"Found {len(patient_tests)} lab tests",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get lab history: {str(e)}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get lab history: {str(e)}"
        )
