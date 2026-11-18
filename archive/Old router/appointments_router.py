"""Appointments Management Router - API Endpoints
==================================================

This router provides comprehensive appointment management functionality:
- Check doctor availability and view available time slots
- Schedule new appointments with conflict detection
- Reschedule existing appointments
- Cancel appointments with reason tracking
- Get patient appointment history
- Get doctor schedules
- Send appointment reminders via email
- Get appointment statistics and analytics

All endpoints are protected with role-based access control.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import os
from api.auth import get_current_user, require_admin, require_doctor, require_staff

# Import appointment management tools
from tools.appointment_tool import (
    CheckDoctorAvailabilityTool,
    ScheduleAppointmentTool,
    RescheduleAppointmentTool,
    CancelAppointmentTool,
    GetPatientAppointmentsTool,
    GetDoctorScheduleTool,
    SendAppointmentReminderTool,
    GetAppointmentStatisticsTool
)

router = APIRouter()

# Initialize tools
check_availability_tool = CheckDoctorAvailabilityTool()
schedule_tool = ScheduleAppointmentTool()
reschedule_tool = RescheduleAppointmentTool()
cancel_tool = CancelAppointmentTool()
get_patient_appointments_tool = GetPatientAppointmentsTool()
get_doctor_schedule_tool = GetDoctorScheduleTool()
send_reminder_tool = SendAppointmentReminderTool()
get_stats_tool = GetAppointmentStatisticsTool()

# =====================================================
# Pydantic Models
# =====================================================

class ScheduleAppointmentRequest(BaseModel):
    """Request model for scheduling a new appointment"""
    patient_id: str = Field(..., description="Patient ID (e.g., REG2025123456)")
    doctor_id: str = Field(..., description="Doctor ID (e.g., DOC001)")
    appointment_date: str = Field(..., description="Appointment date in YYYY-MM-DD format")
    appointment_time: str = Field(..., description="Appointment time in HH:MM format (24-hour)")
    appointment_type: str = Field(..., description="Type: Consultation, Follow-up, Procedure, Check-up, Emergency")
    reason: str = Field(..., description="Reason for appointment")
    notes: Optional[str] = Field(None, description="Additional notes or special instructions")

class RescheduleAppointmentRequest(BaseModel):
    """Request model for rescheduling an appointment"""
    new_date: str = Field(..., description="New appointment date (YYYY-MM-DD)")
    new_time: str = Field(..., description="New appointment time (HH:MM)")
    reason: str = Field(..., description="Reason for rescheduling")

class CancelAppointmentRequest(BaseModel):
    """Request model for cancelling an appointment"""
    reason: str = Field(..., description="Reason for cancellation")

class SendReminderRequest(BaseModel):
    """Request model for sending appointment reminder"""
    appointment_id: str = Field(..., description="Appointment ID to send reminder for")

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
async def appointments_info(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get information about the Appointments API
    
    Returns list of available endpoints and their descriptions.
    """
    return {
        "success": True,
        "data": {
            "endpoints": [
                "GET / - API information",
                "GET /availability - Check doctor availability",
                "POST /schedule - Schedule new appointment",
                "PUT /{appointment_id}/reschedule - Reschedule appointment",
                "DELETE /{appointment_id} - Cancel appointment",
                "GET /patient/{patient_id} - Get patient appointments",
                "GET /doctor/{doctor_id} - Get doctor schedule",
                "POST /reminder - Send appointment reminder",
                "GET /stats - Get appointment statistics"
            ],
            "tools_available": 8,
            "description": "Comprehensive appointment management with conflict detection and email reminders"
        },
        "message": "Appointments Management API",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/availability", response_model=APIResponse)
async def check_doctor_availability(
    doctor_id: str = Query(..., description="Doctor ID (e.g., DOC001)"),
    date: str = Query(..., description="Date to check (YYYY-MM-DD)"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Check doctor's availability and view available time slots
    
    **Access:** All authenticated users
    
    **Parameters:**
    - doctor_id: Doctor ID to check
    - date: Date in YYYY-MM-DD format
    
    **Returns:** Available time slots and booked appointments
    """
    try:
        result = check_availability_tool._run(
            doctor_id=doctor_id,
            date=date
        )
        
        return {
            "success": True,
            "data": {"availability_info": result},
            "message": "Doctor availability retrieved successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check availability: {str(e)}"
        )


@router.post("/schedule", response_model=APIResponse)
async def schedule_appointment(
    request: ScheduleAppointmentRequest,
    current_user: Dict = Depends(require_staff)
):
    """
    Schedule a new appointment with conflict detection
    
    **Access:** Staff, Doctor, Admin
    
    **Parameters:**
    - patient_id: Patient ID
    - doctor_id: Doctor ID
    - appointment_date: Date (YYYY-MM-DD)
    - appointment_time: Time (HH:MM)
    - appointment_type: Consultation, Follow-up, Procedure, Check-up, Emergency
    - reason: Reason for appointment
    - notes: Additional notes (optional)
    
    **Returns:** Appointment confirmation with details
    """
    try:
        result = schedule_tool._run(
            patient_id=request.patient_id,
            doctor_id=request.doctor_id,
            appointment_date=request.appointment_date,
            appointment_time=request.appointment_time,
            appointment_type=request.appointment_type,
            reason=request.reason,
            notes=request.notes
        )
        
        # Check if scheduling failed
        if "❌" in result or "Error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result
            )
        
        return {
            "success": True,
            "data": {"appointment_details": result},
            "message": "Appointment scheduled successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule appointment: {str(e)}"
        )


@router.put("/{appointment_id}/reschedule", response_model=APIResponse)
async def reschedule_appointment(
    appointment_id: str,
    request: RescheduleAppointmentRequest,
    current_user: Dict = Depends(require_staff)
):
    """
    Reschedule an existing appointment to a new date/time
    
    **Access:** Staff, Doctor, Admin
    
    **Parameters:**
    - appointment_id: Appointment ID to reschedule
    - new_date: New date (YYYY-MM-DD)
    - new_time: New time (HH:MM)
    - reason: Reason for rescheduling
    
    **Returns:** Updated appointment details
    """
    try:
        result = reschedule_tool._run(
            appointment_id=appointment_id,
            new_date=request.new_date,
            new_time=request.new_time,
            reason=request.reason
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
            "data": {"rescheduled_appointment": result},
            "message": "Appointment rescheduled successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reschedule appointment: {str(e)}"
        )


@router.delete("/{appointment_id}", response_model=APIResponse)
async def cancel_appointment(
    appointment_id: str,
    request: CancelAppointmentRequest,
    current_user: Dict = Depends(require_staff)
):
    """
    Cancel an existing appointment
    
    **Access:** Staff, Doctor, Admin
    
    **Parameters:**
    - appointment_id: Appointment ID to cancel
    - reason: Reason for cancellation
    
    **Returns:** Cancellation confirmation
    """
    try:
        result = cancel_tool._run(
            appointment_id=appointment_id,
            reason=request.reason
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
            "data": {"cancellation_details": result},
            "message": "Appointment cancelled successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel appointment: {str(e)}"
        )


@router.get("/patient/{patient_id}", response_model=APIResponse)
async def get_patient_appointments(
    patient_id: str,
    status_filter: Optional[str] = Query(None, description="Filter by status (Scheduled, Confirmed, Cancelled, etc.)"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get all appointments for a specific patient
    
    **Access:** All authenticated users
    
    **Parameters:**
    - patient_id: Patient ID
    - status_filter: Optional status filter (Scheduled, Confirmed, Cancelled, Completed, No-Show)
    
    **Returns:** List of patient appointments
    """
    try:
        # Read appointments database directly
        appointments_file = "data/appointments_database.json"
        if os.path.exists(appointments_file):
            with open(appointments_file, 'r') as f:
                data = json.load(f)
                appointments = data.get('appointments', [])
        else:
            appointments = []
        
        # Filter by patient_id
        patient_appointments = [apt for apt in appointments if apt.get('patient_id') == patient_id]
        
        # Filter by status if provided
        if status_filter:
            patient_appointments = [apt for apt in patient_appointments if apt.get('status', '').lower() == status_filter.lower()]
        
        return {
            "success": True,
            "data": {"appointments": patient_appointments},
            "message": f"Found {len(patient_appointments)} appointments",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get patient appointments: {str(e)}"
        )


@router.get("/doctor/{doctor_id}", response_model=APIResponse)
async def get_doctor_schedule(
    doctor_id: str,
    date: Optional[str] = Query(None, description="Date to get schedule for (YYYY-MM-DD)"),
    current_user: Dict = Depends(get_current_user)  # Changed from require_doctor to get_current_user
):
    """
    Get all appointments for a specific doctor
    
    **Access:** Any authenticated user
    
    **Parameters:**
    - doctor_id: Doctor ID
    - date: Optional date filter (YYYY-MM-DD)
    
    **Returns:** Doctor's schedule and appointments
    """
    try:
        # Load appointments directly from database
        from tools.appointment_tool import APPOINTMENTS_DB_FILE, load_db, DOCTORS_DATABASE
        
        # Validate doctor
        if doctor_id not in DOCTORS_DATABASE:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Doctor ID '{doctor_id}' not found"
            )
        
        doctor = DOCTORS_DATABASE[doctor_id]
        appointments_db = load_db(APPOINTMENTS_DB_FILE)
        
        # Filter appointments for this doctor
        doctor_appointments = [a for a in appointments_db if a.get("doctor_id") == doctor_id]
        
        if date:
            doctor_appointments = [a for a in doctor_appointments if a.get("appointment_date") == date]
        else:
            # Only show future and today's appointments
            today = datetime.now().date()
            doctor_appointments = [a for a in doctor_appointments 
                                  if datetime.strptime(a.get("appointment_date", "2000-01-01"), "%Y-%m-%d").date() >= today]
        
        # Sort by date and time
        doctor_appointments.sort(key=lambda x: (x.get("appointment_date", ""), x.get("appointment_time", "")))
        
        return {
            "success": True,
            "data": {
                "doctor": doctor,
                "appointments": doctor_appointments,
                "count": len(doctor_appointments)
            },
            "message": "Doctor schedule retrieved successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get doctor schedule: {str(e)}"
        )


@router.post("/reminder", response_model=APIResponse)
async def send_appointment_reminder(
    request: SendReminderRequest,
    current_user: Dict = Depends(require_staff)
):
    """
    Send appointment reminder email to patient
    
    **Access:** Staff, Doctor, Admin
    
    **Parameters:**
    - appointment_id: Appointment ID to send reminder for
    
    **Returns:** Email sending confirmation
    """
    try:
        result = send_reminder_tool._run(
            appointment_id=request.appointment_id
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
            "data": {"reminder_status": result},
            "message": "Appointment reminder sent successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send reminder: {str(e)}"
        )


@router.get("/stats", response_model=APIResponse)
async def get_appointment_statistics(
    start_date: Optional[str] = Query(None, description="Start date for statistics (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date for statistics (YYYY-MM-DD)"),
    current_user: Dict = Depends(require_admin)
):
    """
    Get appointment statistics and analytics
    
    **Access:** Admin only
    
    **Parameters:**
    - start_date: Optional start date (YYYY-MM-DD)
    - end_date: Optional end date (YYYY-MM-DD)
    
    **Returns:** Comprehensive appointment analytics including:
    - Total appointments by status
    - Appointments by type
    - Most booked doctors
    - Busiest days/times
    - Cancellation rates
    """
    try:
        result = get_stats_tool._run(
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "success": True,
            "data": {"statistics": result},
            "message": "Appointment statistics retrieved successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )
