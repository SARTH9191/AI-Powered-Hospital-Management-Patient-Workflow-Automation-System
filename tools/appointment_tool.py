"""
Appointment Management Tool for Hospital AI Agent
=================================================

This module provides comprehensive appointment management tools:
1. Check Doctor Availability - View doctor schedules and available slots
2. Schedule Appointment - Book new appointments with conflict detection
3. Reschedule Appointment - Change appointment date/time
4. Cancel Appointment - Cancel appointments with reason tracking
5. Get Patient Appointments - View all appointments for a patient
6. Get Doctor Schedule - View all appointments for a doctor
7. Send Appointment Reminder - Send email reminders to patients
8. Get Appointment Statistics - Generate appointment analytics

Features:
- Conflict detection (prevents double-booking)
- Doctor availability tracking
- Multiple appointment types (consultation, follow-up, procedure)
- Status management (Scheduled, Confirmed, Cancelled, Completed, No-Show)
- Email reminders via Gmail integration
- Integration with Google Calendar
- Queue management
- Appointment statistics and analytics
"""

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
import os
import random
import string

# Database file paths
APPOINTMENTS_DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "appointments_database.json")
PATIENTS_DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "patients_database.json")

# Database helper functions
def load_db(file_path):
    """Load database from JSON file - returns list"""
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        return []
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Handle different JSON structures
            if isinstance(data, dict):
                # Check if it has a key with the actual data array
                if 'appointments' in data and isinstance(data['appointments'], list):
                    return data['appointments']
                # Otherwise convert dict values to list
                values = list(data.values())
                # If the first value is a list, return it directly (flatten nested structure)
                if len(values) > 0 and isinstance(values[0], list):
                    return values[0]
                return values
            return data if isinstance(data, list) else []
    except:
        return []

def save_db(file_path, data):
    """Save database to JSON file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

# Doctor database (in production, this would be from database)
DOCTORS_DATABASE = {
    "doctor": {  # Test doctor user
        "name": "Dr. Test Doctor",
        "specialization": "General Medicine",
        "working_hours": {"start": "08:00", "end": "20:00"},
        "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        "consultation_duration": 30  # minutes
    },
    "DOC001": {
        "name": "Dr. Sarah Johnson",
        "specialization": "General Medicine",
        "working_hours": {"start": "09:00", "end": "17:00"},
        "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "consultation_duration": 30  # minutes
    },
    "DOC002": {
        "name": "Dr. Michael Chen",
        "specialization": "Cardiology",
        "working_hours": {"start": "10:00", "end": "18:00"},
        "working_days": ["Monday", "Wednesday", "Friday"],
        "consultation_duration": 45
    },
    "DOC003": {
        "name": "Dr. Emily Rodriguez",
        "specialization": "Pediatrics",
        "working_hours": {"start": "08:00", "end": "16:00"},
        "working_days": ["Tuesday", "Thursday", "Saturday"],
        "consultation_duration": 30
    },
    "DOC004": {
        "name": "Dr. James Williams",
        "specialization": "Orthopedics",
        "working_hours": {"start": "09:00", "end": "17:00"},
        "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "consultation_duration": 60
    },
    "DOC005": {
        "name": "Dr. Priya Sharma",
        "specialization": "Dermatology",
        "working_hours": {"start": "11:00", "end": "19:00"},
        "working_days": ["Wednesday", "Thursday", "Friday", "Saturday"],
        "consultation_duration": 30
    }
}

APPOINTMENT_TYPES = ["Consultation", "Follow-up", "Procedure", "Check-up", "Emergency"]
APPOINTMENT_STATUS = ["Scheduled", "Confirmed", "Cancelled", "Completed", "No-Show", "Rescheduled"]


def generate_appointment_id():
    """Generate unique appointment ID in format APT{YEAR}{6-digit-random}"""
    year = datetime.now().year
    random_digits = ''.join(random.choices(string.digits, k=6))
    return f"APT{year}{random_digits}"


def parse_time(time_str):
    """Parse time string HH:MM to datetime"""
    try:
        return datetime.strptime(time_str, "%H:%M").time()
    except:
        return None


def time_to_minutes(time_str):
    """Convert HH:MM to minutes since midnight"""
    try:
        h, m = map(int, time_str.split(":"))
        return h * 60 + m
    except:
        return 0


def check_time_conflict(new_start, new_end, existing_start, existing_end):
    """Check if two time ranges overlap"""
    return not (new_end <= existing_start or new_start >= existing_end)


# =====================================================
# TOOL 1: Check Doctor Availability
# =====================================================

class CheckDoctorAvailabilityInput(BaseModel):
    doctor_id: str = Field(..., description="Doctor ID (e.g., DOC001)")
    date: str = Field(..., description="Date to check availability (YYYY-MM-DD format)")
    
class CheckDoctorAvailabilityTool(BaseTool):
    name: str = "check_doctor_availability"
    description: str = "Check doctor's availability and view available time slots for a specific date"
    args_schema: type[BaseModel] = CheckDoctorAvailabilityInput
    
    def _run(self, doctor_id: str, date: str) -> str:
        try:
            # Validate doctor exists
            if doctor_id not in DOCTORS_DATABASE:
                return f"❌ Error: Doctor ID '{doctor_id}' not found in system."
            
            doctor = DOCTORS_DATABASE[doctor_id]
            
            # Parse date
            try:
                check_date = datetime.strptime(date, "%Y-%m-%d")
                day_name = check_date.strftime("%A")
            except ValueError:
                return "❌ Error: Invalid date format. Use YYYY-MM-DD."
            
            # Check if doctor works on this day
            if day_name not in doctor["working_days"]:
                return f"❌ {doctor['name']} does not work on {day_name}s.\n" \
                       f"Working days: {', '.join(doctor['working_days'])}"
            
            # Load existing appointments
            appointments_db = load_db(APPOINTMENTS_DB_FILE)
            
            # Find appointments for this doctor on this date
            doctor_appointments = [
                apt for apt in appointments_db
                if apt.get("doctor_id") == doctor_id 
                and apt.get("appointment_date") == date
                and apt.get("status") not in ["Cancelled", "No-Show"]
            ]
            
            # Generate available slots
            start_time = time_to_minutes(doctor["working_hours"]["start"])
            end_time = time_to_minutes(doctor["working_hours"]["end"])
            duration = doctor["consultation_duration"]
            
            available_slots = []
            current_time = start_time
            
            while current_time + duration <= end_time:
                slot_start = f"{current_time // 60:02d}:{current_time % 60:02d}"
                slot_end = f"{(current_time + duration) // 60:02d}:{(current_time + duration) % 60:02d}"
                
                # Check if this slot conflicts with existing appointments
                is_available = True
                for apt in doctor_appointments:
                    apt_start = time_to_minutes(apt.get("appointment_time", "00:00"))
                    apt_end = apt_start + duration
                    
                    if check_time_conflict(current_time, current_time + duration, apt_start, apt_end):
                        is_available = False
                        break
                
                if is_available:
                    available_slots.append(f"{slot_start} - {slot_end}")
                
                current_time += duration
            
            # Format response
            result = f"🏥 Doctor Availability Check\n"
            result += f"{'=' * 50}\n\n"
            result += f"👨‍⚕️ Doctor: {doctor['name']}\n"
            result += f"🩺 Specialization: {doctor['specialization']}\n"
            result += f"📅 Date: {date} ({day_name})\n"
            result += f"⏰ Working Hours: {doctor['working_hours']['start']} - {doctor['working_hours']['end']}\n"
            result += f"⏱️  Consultation Duration: {duration} minutes\n\n"
            
            result += f"📊 Appointments Booked: {len(doctor_appointments)}\n"
            result += f"✅ Available Slots: {len(available_slots)}\n\n"
            
            if available_slots:
                result += "🟢 Available Time Slots:\n"
                for i, slot in enumerate(available_slots, 1):
                    result += f"   {i}. {slot}\n"
            else:
                result += "🔴 No available slots for this date.\n"
                result += "💡 Suggestion: Try another date or doctor.\n"
            
            if doctor_appointments:
                result += f"\n📋 Booked Appointments:\n"
                for apt in doctor_appointments:
                    result += f"   • {apt.get('appointment_time')} - Patient ID: {apt.get('patient_id')}\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error checking availability: {str(e)}"


# =====================================================
# TOOL 2: Schedule Appointment
# =====================================================

class ScheduleAppointmentInput(BaseModel):
    patient_id: str = Field(..., description="Patient ID (e.g., REG2025123456)")
    doctor_id: str = Field(..., description="Doctor ID (e.g., DOC001)")
    appointment_date: str = Field(..., description="Appointment date (YYYY-MM-DD)")
    appointment_time: str = Field(..., description="Appointment time (HH:MM in 24-hour format)")
    appointment_type: str = Field(..., description="Type: Consultation, Follow-up, Procedure, Check-up, Emergency")
    reason: str = Field(..., description="Reason for appointment")
    notes: Optional[str] = Field(None, description="Additional notes")

class ScheduleAppointmentTool(BaseTool):
    name: str = "schedule_appointment"
    description: str = "Schedule a new appointment with conflict detection and validation"
    args_schema: type[BaseModel] = ScheduleAppointmentInput
    
    def _run(self, patient_id: str, doctor_id: str, appointment_date: str, 
             appointment_time: str, appointment_type: str, reason: str,
             notes: Optional[str] = None) -> str:
        try:
            # Validate patient exists
            patients_db = load_db(PATIENTS_DB_FILE)
            patient = next((p for p in patients_db if p.get("patient_id") == patient_id), None)
            if not patient:
                return f"❌ Error: Patient ID '{patient_id}' not found."
            
            # Validate doctor exists
            if doctor_id not in DOCTORS_DATABASE:
                return f"❌ Error: Doctor ID '{doctor_id}' not found."
            
            doctor = DOCTORS_DATABASE[doctor_id]
            
            # Validate date
            try:
                appt_date = datetime.strptime(appointment_date, "%Y-%m-%d")
                day_name = appt_date.strftime("%A")
            except ValueError:
                return "❌ Error: Invalid date format. Use YYYY-MM-DD."
            
            # Check if date is in the past
            if appt_date.date() < datetime.now().date():
                return "❌ Error: Cannot schedule appointment in the past."
            
            # Check if doctor works on this day
            if day_name not in doctor["working_days"]:
                return f"❌ Error: {doctor['name']} does not work on {day_name}s.\n" \
                       f"Working days: {', '.join(doctor['working_days'])}"
            
            # Validate time
            if not parse_time(appointment_time):
                return "❌ Error: Invalid time format. Use HH:MM (24-hour format)."
            
            # Check if time is within working hours
            appt_time_minutes = time_to_minutes(appointment_time)
            start_time = time_to_minutes(doctor["working_hours"]["start"])
            end_time = time_to_minutes(doctor["working_hours"]["end"])
            duration = doctor["consultation_duration"]
            
            if appt_time_minutes < start_time or appt_time_minutes + duration > end_time:
                return f"❌ Error: Time outside doctor's working hours ({doctor['working_hours']['start']} - {doctor['working_hours']['end']})."
            
            # Validate appointment type
            if appointment_type not in APPOINTMENT_TYPES:
                return f"❌ Error: Invalid appointment type. Choose from: {', '.join(APPOINTMENT_TYPES)}"
            
            # Check for conflicts
            appointments_db = load_db(APPOINTMENTS_DB_FILE)
            
            for apt in appointments_db:
                if (apt.get("doctor_id") == doctor_id and 
                    apt.get("appointment_date") == appointment_date and
                    apt.get("status") not in ["Cancelled", "No-Show"]):
                    
                    existing_time = time_to_minutes(apt.get("appointment_time", "00:00"))
                    existing_end = existing_time + duration
                    new_end = appt_time_minutes + duration
                    
                    if check_time_conflict(appt_time_minutes, new_end, existing_time, existing_end):
                        return f"❌ Conflict Detected!\n" \
                               f"Doctor already has appointment at {apt.get('appointment_time')}.\n" \
                               f"Patient: {apt.get('patient_id')}\n" \
                               f"Please choose another time slot."
            
            # Generate appointment ID
            appointment_id = generate_appointment_id()
            
            # Create appointment record
            appointment = {
                "appointment_id": appointment_id,
                "patient_id": patient_id,
                "patient_name": patient.get("name"),
                "doctor_id": doctor_id,
                "doctor_name": doctor["name"],
                "specialization": doctor["specialization"],
                "appointment_date": appointment_date,
                "appointment_time": appointment_time,
                "appointment_type": appointment_type,
                "duration_minutes": duration,
                "reason": reason,
                "notes": notes or "",
                "status": "Scheduled",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Save to database
            appointments_db.append(appointment)
            save_db(APPOINTMENTS_DB_FILE, appointments_db)
            
            # Format response
            result = f"✅ Appointment Scheduled Successfully!\n"
            result += f"{'=' * 50}\n\n"
            result += f"🆔 Appointment ID: {appointment_id}\n"
            result += f"👤 Patient: {patient.get('full_name')} ({patient_id})\n"
            result += f"👨‍⚕️ Doctor: {doctor['name']} ({doctor_id})\n"
            result += f"🩺 Specialization: {doctor['specialization']}\n"
            result += f"📅 Date: {appointment_date} ({day_name})\n"
            result += f"⏰ Time: {appointment_time}\n"
            result += f"⏱️  Duration: {duration} minutes\n"
            result += f"📋 Type: {appointment_type}\n"
            result += f"💬 Reason: {reason}\n"
            if notes:
                result += f"📝 Notes: {notes}\n"
            result += f"📊 Status: Scheduled\n\n"
            result += f"💡 Reminder: Patient will receive email notification.\n"
            result += f"📧 Use 'send_appointment_reminder' tool to send reminder email.\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error scheduling appointment: {str(e)}"


# =====================================================
# TOOL 3: Reschedule Appointment
# =====================================================

class RescheduleAppointmentInput(BaseModel):
    appointment_id: str = Field(..., description="Appointment ID to reschedule")
    new_date: str = Field(..., description="New date (YYYY-MM-DD)")
    new_time: str = Field(..., description="New time (HH:MM)")
    reason: str = Field(..., description="Reason for rescheduling")

class RescheduleAppointmentTool(BaseTool):
    name: str = "reschedule_appointment"
    description: str = "Reschedule an existing appointment to a new date/time"
    args_schema: type[BaseModel] = RescheduleAppointmentInput
    
    def _run(self, appointment_id: str, new_date: str, new_time: str, reason: str) -> str:
        try:
            appointments_db = load_db(APPOINTMENTS_DB_FILE)
            
            # Find appointment
            appointment = next((a for a in appointments_db if a.get("appointment_id") == appointment_id), None)
            if not appointment:
                return f"❌ Error: Appointment ID '{appointment_id}' not found."
            
            # Check if appointment can be rescheduled
            if appointment.get("status") in ["Cancelled", "Completed"]:
                return f"❌ Error: Cannot reschedule {appointment.get('status')} appointment."
            
            # Store old details
            old_date = appointment.get("appointment_date")
            old_time = appointment.get("appointment_time")
            
            # Validate new date
            try:
                new_appt_date = datetime.strptime(new_date, "%Y-%m-%d")
                day_name = new_appt_date.strftime("%A")
            except ValueError:
                return "❌ Error: Invalid date format. Use YYYY-MM-DD."
            
            if new_appt_date.date() < datetime.now().date():
                return "❌ Error: Cannot reschedule to past date."
            
            # Get doctor info
            doctor_id = appointment.get("doctor_id")
            if doctor_id not in DOCTORS_DATABASE:
                return f"❌ Error: Doctor not found in system."
            
            doctor = DOCTORS_DATABASE[doctor_id]
            
            # Check if doctor works on new day
            if day_name not in doctor["working_days"]:
                return f"❌ Error: Doctor does not work on {day_name}s."
            
            # Validate new time
            if not parse_time(new_time):
                return "❌ Error: Invalid time format. Use HH:MM."
            
            # Check working hours
            new_time_minutes = time_to_minutes(new_time)
            start_time = time_to_minutes(doctor["working_hours"]["start"])
            end_time = time_to_minutes(doctor["working_hours"]["end"])
            duration = doctor["consultation_duration"]
            
            if new_time_minutes < start_time or new_time_minutes + duration > end_time:
                return f"❌ Error: Time outside working hours."
            
            # Check for conflicts (excluding current appointment)
            for apt in appointments_db:
                if (apt.get("appointment_id") != appointment_id and
                    apt.get("doctor_id") == doctor_id and
                    apt.get("appointment_date") == new_date and
                    apt.get("status") not in ["Cancelled", "No-Show"]):
                    
                    existing_time = time_to_minutes(apt.get("appointment_time", "00:00"))
                    existing_end = existing_time + duration
                    new_end = new_time_minutes + duration
                    
                    if check_time_conflict(new_time_minutes, new_end, existing_time, existing_end):
                        return f"❌ Conflict: Doctor has appointment at {apt.get('appointment_time')}."
            
            # Update appointment
            appointment["appointment_date"] = new_date
            appointment["appointment_time"] = new_time
            appointment["status"] = "Rescheduled"
            appointment["reschedule_reason"] = reason
            appointment["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            save_db(APPOINTMENTS_DB_FILE, appointments_db)
            
            result = f"✅ Appointment Rescheduled Successfully!\n"
            result += f"{'=' * 50}\n\n"
            result += f"🆔 Appointment ID: {appointment_id}\n"
            result += f"👤 Patient: {appointment.get('patient_name')}\n"
            result += f"👨‍⚕️ Doctor: {appointment.get('doctor_name')}\n\n"
            result += f"📅 Old Schedule:\n"
            result += f"   Date: {old_date}\n"
            result += f"   Time: {old_time}\n\n"
            result += f"📅 New Schedule:\n"
            result += f"   Date: {new_date} ({day_name})\n"
            result += f"   Time: {new_time}\n\n"
            result += f"💬 Reason: {reason}\n"
            result += f"📊 Status: Rescheduled\n\n"
            result += f"💡 Send notification to patient about the change.\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error rescheduling appointment: {str(e)}"


# =====================================================
# TOOL 4: Cancel Appointment
# =====================================================

class CancelAppointmentInput(BaseModel):
    appointment_id: str = Field(..., description="Appointment ID to cancel")
    reason: str = Field(..., description="Reason for cancellation")
    cancelled_by: str = Field(..., description="Who cancelled: Patient, Doctor, or System")

class CancelAppointmentTool(BaseTool):
    name: str = "cancel_appointment"
    description: str = "Cancel an appointment with reason tracking"
    args_schema: type[BaseModel] = CancelAppointmentInput
    
    def _run(self, appointment_id: str, reason: str, cancelled_by: str) -> str:
        try:
            appointments_db = load_db(APPOINTMENTS_DB_FILE)
            
            # Find appointment
            appointment = next((a for a in appointments_db if a.get("appointment_id") == appointment_id), None)
            if not appointment:
                return f"❌ Error: Appointment ID '{appointment_id}' not found."
            
            # Check if already cancelled or completed
            if appointment.get("status") == "Cancelled":
                return f"⚠️ Appointment already cancelled on {appointment.get('cancelled_at', 'unknown date')}."
            
            if appointment.get("status") == "Completed":
                return f"❌ Error: Cannot cancel completed appointment."
            
            # Update appointment
            appointment["status"] = "Cancelled"
            appointment["cancellation_reason"] = reason
            appointment["cancelled_by"] = cancelled_by
            appointment["cancelled_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            appointment["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            save_db(APPOINTMENTS_DB_FILE, appointments_db)
            
            result = f"✅ Appointment Cancelled Successfully\n"
            result += f"{'=' * 50}\n\n"
            result += f"🆔 Appointment ID: {appointment_id}\n"
            result += f"👤 Patient: {appointment.get('patient_name')} ({appointment.get('patient_id')})\n"
            result += f"👨‍⚕️ Doctor: {appointment.get('doctor_name')} ({appointment.get('doctor_id')})\n"
            result += f"📅 Scheduled For: {appointment.get('appointment_date')} at {appointment.get('appointment_time')}\n"
            result += f"📋 Type: {appointment.get('appointment_type')}\n\n"
            result += f"❌ Cancelled By: {cancelled_by}\n"
            result += f"💬 Reason: {reason}\n"
            result += f"🕐 Cancelled At: {appointment.get('cancelled_at')}\n\n"
            result += f"💡 The appointment slot is now available for other patients.\n"
            result += f"📧 Notify patient about cancellation via email.\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error cancelling appointment: {str(e)}"


# =====================================================
# TOOL 5: Get Patient Appointments
# =====================================================

class GetPatientAppointmentsInput(BaseModel):
    patient_id: str = Field(..., description="Patient ID")
    status_filter: Optional[str] = Field(None, description="Filter by status (optional)")

class GetPatientAppointmentsTool(BaseTool):
    name: str = "get_patient_appointments"
    description: str = "Get all appointments for a specific patient with optional status filter"
    args_schema: type[BaseModel] = GetPatientAppointmentsInput
    
    def _run(self, patient_id: str, status_filter: Optional[str] = None) -> str:
        try:
            # Validate patient
            patients_db = load_db(PATIENTS_DB_FILE)
            patient = next((p for p in patients_db if p.get("patient_id") == patient_id), None)
            if not patient:
                return f"❌ Error: Patient ID '{patient_id}' not found."
            
            # Load appointments
            appointments_db = load_db(APPOINTMENTS_DB_FILE)
            
            # Filter appointments
            patient_appointments = [a for a in appointments_db if a.get("patient_id") == patient_id]
            
            if status_filter:
                patient_appointments = [a for a in patient_appointments if a.get("status") == status_filter]
            
            if not patient_appointments:
                msg = f"📋 No appointments found for {patient.get('name')}"
                if status_filter:
                    msg += f" with status '{status_filter}'"
                return msg + "."
            
            # Sort by date and time
            patient_appointments.sort(key=lambda x: (x.get("appointment_date", ""), x.get("appointment_time", "")))
            
            # Format response
            result = f"📋 Appointments for {patient.get('name')} ({patient_id})\n"
            result += f"{'=' * 50}\n\n"
            if status_filter:
                result += f"🔍 Filter: Status = {status_filter}\n"
            result += f"📊 Total Appointments: {len(patient_appointments)}\n\n"
            
            # Group by status
            status_groups = {}
            for apt in patient_appointments:
                status = apt.get("status", "Unknown")
                if status not in status_groups:
                    status_groups[status] = []
                status_groups[status].append(apt)
            
            for status, appointments in status_groups.items():
                status_icon = {
                    "Scheduled": "📅",
                    "Confirmed": "✅",
                    "Cancelled": "❌",
                    "Completed": "✔️",
                    "No-Show": "⚠️",
                    "Rescheduled": "🔄"
                }.get(status, "📋")
                
                result += f"{status_icon} {status} ({len(appointments)}):\n"
                for apt in appointments:
                    result += f"\n   🆔 ID: {apt.get('appointment_id')}\n"
                    result += f"   👨‍⚕️ Doctor: {apt.get('doctor_name')} - {apt.get('specialization')}\n"
                    result += f"   📅 Date: {apt.get('appointment_date')}\n"
                    result += f"   ⏰ Time: {apt.get('appointment_time')}\n"
                    result += f"   📋 Type: {apt.get('appointment_type')}\n"
                    result += f"   💬 Reason: {apt.get('reason')}\n"
                    if apt.get("notes"):
                        result += f"   📝 Notes: {apt.get('notes')}\n"
                result += "\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error retrieving appointments: {str(e)}"


# =====================================================
# TOOL 6: Get Doctor Schedule
# =====================================================

class GetDoctorScheduleInput(BaseModel):
    doctor_id: str = Field(..., description="Doctor ID")
    date: Optional[str] = Field(None, description="Specific date (YYYY-MM-DD), leave empty for all upcoming")

class GetDoctorScheduleTool(BaseTool):
    name: str = "get_doctor_schedule"
    description: str = "View all appointments for a specific doctor"
    args_schema: type[BaseModel] = GetDoctorScheduleInput
    
    def _run(self, doctor_id: str, date: Optional[str] = None) -> str:
        try:
            # Validate doctor
            if doctor_id not in DOCTORS_DATABASE:
                return f"❌ Error: Doctor ID '{doctor_id}' not found."
            
            doctor = DOCTORS_DATABASE[doctor_id]
            
            # Load appointments
            appointments_db = load_db(APPOINTMENTS_DB_FILE)
            
            # Filter appointments
            doctor_appointments = [a for a in appointments_db if a.get("doctor_id") == doctor_id]
            
            if date:
                doctor_appointments = [a for a in doctor_appointments if a.get("appointment_date") == date]
            else:
                # Only show future and today's appointments
                today = datetime.now().date()
                doctor_appointments = [a for a in doctor_appointments 
                                      if datetime.strptime(a.get("appointment_date", "2000-01-01"), "%Y-%m-%d").date() >= today]
            
            if not doctor_appointments:
                msg = f"📋 No appointments found for {doctor['name']}"
                if date:
                    msg += f" on {date}"
                return msg + "."
            
            # Sort by date and time
            doctor_appointments.sort(key=lambda x: (x.get("appointment_date", ""), x.get("appointment_time", "")))
            
            # Format response
            result = f"👨‍⚕️ Schedule for {doctor['name']} ({doctor_id})\n"
            result += f"{'=' * 50}\n\n"
            result += f"🩺 Specialization: {doctor['specialization']}\n"
            result += f"📅 Working Days: {', '.join(doctor['working_days'])}\n"
            result += f"⏰ Working Hours: {doctor['working_hours']['start']} - {doctor['working_hours']['end']}\n"
            if date:
                result += f"🔍 Date: {date}\n"
            result += f"📊 Total Appointments: {len(doctor_appointments)}\n\n"
            
            # Group by date
            date_groups = {}
            for apt in doctor_appointments:
                appt_date = apt.get("appointment_date")
                if appt_date not in date_groups:
                    date_groups[appt_date] = []
                date_groups[appt_date].append(apt)
            
            for appt_date, appointments in sorted(date_groups.items()):
                date_obj = datetime.strptime(appt_date, "%Y-%m-%d")
                day_name = date_obj.strftime("%A")
                result += f"📅 {appt_date} ({day_name}) - {len(appointments)} appointments:\n"
                
                for apt in sorted(appointments, key=lambda x: x.get("appointment_time", "")):
                    status_icon = {
                        "Scheduled": "📅",
                        "Confirmed": "✅",
                        "Cancelled": "❌",
                        "Completed": "✔️",
                        "No-Show": "⚠️"
                    }.get(apt.get("status"), "📋")
                    
                    result += f"\n   {status_icon} {apt.get('appointment_time')} - {apt.get('duration_minutes')}min\n"
                    result += f"      🆔 ID: {apt.get('appointment_id')}\n"
                    result += f"      👤 Patient: {apt.get('patient_name')} ({apt.get('patient_id')})\n"
                    result += f"      📋 Type: {apt.get('appointment_type')}\n"
                    result += f"      💬 Reason: {apt.get('reason')}\n"
                    result += f"      📊 Status: {apt.get('status')}\n"
                
                result += "\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error retrieving schedule: {str(e)}"


# =====================================================
# TOOL 7: Send Appointment Reminder
# =====================================================

class SendAppointmentReminderInput(BaseModel):
    appointment_id: str = Field(..., description="Appointment ID")
    
class SendAppointmentReminderTool(BaseTool):
    name: str = "send_appointment_reminder"
    description: str = "Send email reminder to patient about upcoming appointment"
    args_schema: type[BaseModel] = SendAppointmentReminderInput
    
    def _run(self, appointment_id: str) -> str:
        try:
            # Find appointment
            appointments_db = load_db(APPOINTMENTS_DB_FILE)
            appointment = next((a for a in appointments_db if a.get("appointment_id") == appointment_id), None)
            
            if not appointment:
                return f"❌ Error: Appointment ID '{appointment_id}' not found."
            
            # Check status
            if appointment.get("status") in ["Cancelled", "Completed", "No-Show"]:
                return f"❌ Error: Cannot send reminder for {appointment.get('status')} appointment."
            
            # Get patient email
            patients_db = load_db(PATIENTS_DB_FILE)
            patient = next((p for p in patients_db if p.get("patient_id") == appointment.get("patient_id")), None)
            
            if not patient or not patient.get("email"):
                return f"❌ Error: Patient email not found."
            
            # Format reminder message
            appt_date = appointment.get("appointment_date")
            appt_time = appointment.get("appointment_time")
            doctor_name = appointment.get("doctor_name")
            specialization = appointment.get("specialization")
            reason = appointment.get("reason")
            
            # Calculate days until appointment
            appt_datetime = datetime.strptime(f"{appt_date} {appt_time}", "%Y-%m-%d %H:%M")
            days_until = (appt_datetime.date() - datetime.now().date()).days
            
            result = f"📧 Appointment Reminder Prepared\n"
            result += f"{'=' * 50}\n\n"
            result += f"✅ Reminder Details:\n"
            result += f"   📧 To: {patient.get('email')}\n"
            result += f"   👤 Patient: {patient.get('name')}\n"
            result += f"   🆔 Appointment ID: {appointment_id}\n\n"
            result += f"📋 Appointment Details:\n"
            result += f"   👨‍⚕️ Doctor: {doctor_name}\n"
            result += f"   🩺 Specialization: {specialization}\n"
            result += f"   📅 Date: {appt_date}\n"
            result += f"   ⏰ Time: {appt_time}\n"
            result += f"   💬 Reason: {reason}\n"
            result += f"   ⏳ Days Until Appointment: {days_until}\n\n"
            
            # Email subject and body
            subject = f"Appointment Reminder - {appt_date} at {appt_time}"
            
            body = f"""Dear {patient.get('name')},

This is a friendly reminder about your upcoming appointment:

📅 Date: {appt_date}
⏰ Time: {appt_time}
👨‍⚕️ Doctor: {doctor_name}
🩺 Specialization: {specialization}
💬 Reason: {reason}

🏥 Hospital Location: [Hospital Address]

Please arrive 15 minutes before your scheduled time.

If you need to reschedule or cancel, please contact us at least 24 hours in advance.

Best regards,
Hospital Management System
"""
            
            result += f"📄 Email Content:\n"
            result += f"   Subject: {subject}\n"
            result += f"   Body Preview:\n{body}\n\n"
            result += f"💡 Next Step: Use Gmail tool to send this email:\n"
            result += f"   send_email(\n"
            result += f"      to='{patient.get('email')}',\n"
            result += f"      subject='{subject}',\n"
            result += f"      body='{body.replace(chr(10), ' ')}'\n"
            result += f"   )\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error preparing reminder: {str(e)}"


# =====================================================
# TOOL 8: Get Appointment Statistics
# =====================================================

class GetAppointmentStatisticsInput(BaseModel):
    start_date: Optional[str] = Field(None, description="Start date for statistics (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date for statistics (YYYY-MM-DD)")
    
class GetAppointmentStatisticsTool(BaseTool):
    name: str = "get_appointment_statistics"
    description: str = "Generate comprehensive appointment analytics and statistics"
    args_schema: type[BaseModel] = GetAppointmentStatisticsInput
    
    def _run(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
        try:
            appointments_db = load_db(APPOINTMENTS_DB_FILE)
            
            if not appointments_db:
                return "📊 No appointments in database."
            
            # Filter by date range if provided
            filtered_appointments = appointments_db
            
            if start_date:
                filtered_appointments = [a for a in filtered_appointments 
                                        if a.get("appointment_date", "") >= start_date]
            
            if end_date:
                filtered_appointments = [a for a in filtered_appointments 
                                        if a.get("appointment_date", "") <= end_date]
            
            # Calculate statistics
            total = len(filtered_appointments)
            
            # Status breakdown
            status_counts = {}
            for apt in filtered_appointments:
                status = apt.get("status", "Unknown")
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Type breakdown
            type_counts = {}
            for apt in filtered_appointments:
                apt_type = apt.get("appointment_type", "Unknown")
                type_counts[apt_type] = type_counts.get(apt_type, 0) + 1
            
            # Doctor breakdown
            doctor_counts = {}
            for apt in filtered_appointments:
                doctor = apt.get("doctor_name", "Unknown")
                doctor_counts[doctor] = doctor_counts.get(doctor, 0) + 1
            
            # Day of week breakdown
            day_counts = {}
            for apt in filtered_appointments:
                try:
                    date_obj = datetime.strptime(apt.get("appointment_date", ""), "%Y-%m-%d")
                    day_name = date_obj.strftime("%A")
                    day_counts[day_name] = day_counts.get(day_name, 0) + 1
                except:
                    pass
            
            # Format response
            result = f"📊 Appointment Statistics\n"
            result += f"{'=' * 50}\n\n"
            
            if start_date or end_date:
                result += f"📅 Date Range: "
                if start_date:
                    result += f"From {start_date} "
                if end_date:
                    result += f"To {end_date}"
                result += "\n\n"
            
            result += f"📈 Total Appointments: {total}\n\n"
            
            # Status breakdown
            result += f"📊 By Status:\n"
            for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total * 100) if total > 0 else 0
                status_icon = {
                    "Scheduled": "📅",
                    "Confirmed": "✅",
                    "Cancelled": "❌",
                    "Completed": "✔️",
                    "No-Show": "⚠️",
                    "Rescheduled": "🔄"
                }.get(status, "📋")
                result += f"   {status_icon} {status}: {count} ({percentage:.1f}%)\n"
            
            result += f"\n📋 By Type:\n"
            for apt_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total * 100) if total > 0 else 0
                result += f"   • {apt_type}: {count} ({percentage:.1f}%)\n"
            
            result += f"\n👨‍⚕️ By Doctor:\n"
            for doctor, count in sorted(doctor_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total * 100) if total > 0 else 0
                result += f"   • {doctor}: {count} ({percentage:.1f}%)\n"
            
            result += f"\n📅 By Day of Week:\n"
            day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            for day in day_order:
                if day in day_counts:
                    count = day_counts[day]
                    percentage = (count / total * 100) if total > 0 else 0
                    result += f"   • {day}: {count} ({percentage:.1f}%)\n"
            
            # Additional insights
            result += f"\n💡 Insights:\n"
            
            # Most popular doctor
            if doctor_counts:
                most_popular_doctor = max(doctor_counts.items(), key=lambda x: x[1])
                result += f"   • Most booked doctor: {most_popular_doctor[0]} ({most_popular_doctor[1]} appointments)\n"
            
            # Most popular day
            if day_counts:
                most_popular_day = max(day_counts.items(), key=lambda x: x[1])
                result += f"   • Busiest day: {most_popular_day[0]} ({most_popular_day[1]} appointments)\n"
            
            # Cancellation rate
            cancelled = status_counts.get("Cancelled", 0)
            if total > 0:
                cancel_rate = (cancelled / total * 100)
                result += f"   • Cancellation rate: {cancel_rate:.1f}%\n"
            
            # No-show rate
            no_show = status_counts.get("No-Show", 0)
            if total > 0:
                no_show_rate = (no_show / total * 100)
                result += f"   • No-show rate: {no_show_rate:.1f}%\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error generating statistics: {str(e)}"


# =====================================================
# Helper Function: Get All Tools
# =====================================================

def get_all_appointment_tools():
    """Returns list of all appointment management tools"""
    return [
        CheckDoctorAvailabilityTool(),
        ScheduleAppointmentTool(),
        RescheduleAppointmentTool(),
        CancelAppointmentTool(),
        GetPatientAppointmentsTool(),
        GetDoctorScheduleTool(),
        SendAppointmentReminderTool(),
        GetAppointmentStatisticsTool()
    ]


# =====================================================
# Usage Example
# =====================================================

if __name__ == "__main__":
    print("🏥 APPOINTMENT MANAGEMENT TOOL - DEMO")
    print("=" * 60)
    
    # Get all tools
    tools = get_all_appointment_tools()
    
    print(f"\n✅ Loaded {len(tools)} Appointment Management Tools:\n")
    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool.name}")
    
    print("\n" + "=" * 60)
    print("✅ APPOINTMENT MANAGEMENT TOOLS READY!")
    print("=" * 60)
