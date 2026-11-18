"""
Enhanced Google Sheets Monitoring Tools
Real-time bidirectional communication between hospital staff and AI agent

These tools enable:
1. Staff update Google Sheets → AI reads and responds
2. AI updates Google Sheets → Staff sees real-time status
3. Continuous monitoring of all hospital operations via Google Sheets

Author: Hospital Management AI System
"""

import os
import pickle
import json
from typing import Optional, Type, List, Dict, Any
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from pydantic import BaseModel, Field
from langchain.tools import BaseTool


# ==================== GOOGLE SHEETS SCOPES ====================
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Environment variables for monitoring sheet IDs
PATIENT_STATUS_SHEET_ID = os.getenv('PATIENT_STATUS_SHEET_ID', '')
DOCTOR_NOTES_SHEET_ID = os.getenv('DOCTOR_NOTES_SHEET_ID', '')
LAB_RESULTS_SHEET_ID = os.getenv('LAB_RESULTS_SHEET_ID', '')
STAFF_UPDATES_SHEET_ID = os.getenv('STAFF_UPDATES_SHEET_ID', '')
EMERGENCY_ALERTS_SHEET_ID = os.getenv('EMERGENCY_ALERTS_SHEET_ID', '')
PHARMACY_INVENTORY_SHEET_ID = os.getenv('PHARMACY_INVENTORY_SHEET_ID', '')


# ==================== INPUT SCHEMAS ====================

class ReadPatientStatusInput(BaseModel):
    """Input schema for reading patient status updates."""
    patient_id: Optional[str] = Field(default=None, description="Specific patient ID to check")
    status_type: Optional[str] = Field(default="all", description="Type of status to read (all, critical, stable, discharged)")
    limit: int = Field(default=10, description="Maximum number of records to return")

class UpdatePatientStatusInput(BaseModel):
    """Input schema for updating patient status."""
    patient_id: str = Field(description="Patient ID")
    status: str = Field(description="Patient status (Stable, Critical, Recovering, Discharged)")
    notes: str = Field(description="Status update notes")
    updated_by: str = Field(description="Staff member name updating the status")

class ReadDoctorNotesInput(BaseModel):
    """Input schema for reading doctor notes."""
    patient_id: Optional[str] = Field(default=None, description="Specific patient ID")
    doctor_name: Optional[str] = Field(default=None, description="Specific doctor name")
    date_from: Optional[str] = Field(default=None, description="Start date (YYYY-MM-DD)")
    limit: int = Field(default=10, description="Maximum number of notes to return")

class AddDoctorNoteInput(BaseModel):
    """Input schema for adding doctor notes."""
    patient_id: str = Field(description="Patient ID")
    doctor_name: str = Field(description="Doctor name")
    note_type: str = Field(description="Type of note (Observation, Diagnosis, Treatment, Prescription)")
    note_content: str = Field(description="Detailed note content")
    priority: str = Field(default="Normal", description="Priority level (Normal, High, Urgent)")

class ReadLabResultsInput(BaseModel):
    """Input schema for reading lab results."""
    patient_id: Optional[str] = Field(default=None, description="Specific patient ID")
    test_type: Optional[str] = Field(default=None, description="Type of test")
    status: Optional[str] = Field(default="all", description="Result status (all, pending, completed, abnormal)")
    limit: int = Field(default=10, description="Maximum number of results to return")

class UpdateLabResultInput(BaseModel):
    """Input schema for updating lab results."""
    patient_id: str = Field(description="Patient ID")
    test_name: str = Field(description="Name of the test")
    result_value: str = Field(description="Test result value")
    normal_range: str = Field(description="Normal range for the test")
    status: str = Field(description="Result status (Normal, Abnormal, Critical)")
    technician_name: str = Field(description="Lab technician name")

class ReadStaffUpdatesInput(BaseModel):
    """Input schema for reading staff updates."""
    department: Optional[str] = Field(default=None, description="Specific department")
    priority: Optional[str] = Field(default="all", description="Priority level (all, normal, high, urgent)")
    unread_only: bool = Field(default=True, description="Only show unread updates")
    limit: int = Field(default=10, description="Maximum number of updates to return")

class AddStaffUpdateInput(BaseModel):
    """Input schema for adding staff updates."""
    staff_name: str = Field(description="Staff member name")
    department: str = Field(description="Department name")
    update_type: str = Field(description="Type of update (Info, Request, Alert, Reminder)")
    message: str = Field(description="Update message content")
    priority: str = Field(default="Normal", description="Priority level (Normal, High, Urgent)")

class ReadEmergencyAlertsInput(BaseModel):
    """Input schema for reading emergency alerts."""
    status: Optional[str] = Field(default="active", description="Alert status (active, resolved, all)")
    priority: Optional[str] = Field(default="all", description="Priority level")
    limit: int = Field(default=20, description="Maximum number of alerts to return")

class CreateEmergencyAlertInput(BaseModel):
    """Input schema for creating emergency alerts."""
    alert_type: str = Field(description="Type of emergency (Medical, Fire, Security, Equipment)")
    location: str = Field(description="Location of emergency")
    description: str = Field(description="Detailed description of the emergency")
    severity: str = Field(description="Severity level (Low, Medium, High, Critical)")
    reported_by: str = Field(description="Person reporting the emergency")


# ==================== BASE CLASS ====================

class SheetsMonitoringToolBase(BaseTool):
    """Base class for Google Sheets monitoring tools."""
    
    # Define service as a class variable to avoid Pydantic field validation
    service: Any = None
    
    def __init__(self):
        super().__init__()
        # Use object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, 'service', self._initialize_sheets_service())
    
    def _initialize_sheets_service(self):
        """Initialize Google Sheets service using existing credentials."""
        try:
            creds = None
            # Use dedicated sheets_token.pickle file in project root
            token_path = os.path.join(os.path.dirname(__file__), '..', 'sheets_token.pickle')
            credentials_path = os.path.join(os.path.dirname(__file__), '..', 'credentials', 'client_secret.json')
            
            if os.path.exists(token_path):
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next run  
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
            
            service = build('sheets', 'v4', credentials=creds)
            print("✅ Google Sheets monitoring service initialized")
            return service
            
        except Exception as e:
            print(f"❌ Error initializing Sheets service: {e}")
            return None
    
    def _get_current_timestamp(self):
        """Get current timestamp in readable format."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _read_sheet_data(self, sheet_id: str, range_name: str = "A:Z") -> List[List]:
        """Read data from a Google Sheet."""
        if not self.service:
            return []
        
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            return values
        except HttpError as e:
            print(f"❌ Error reading sheet data: {e}")
            return []
    
    def _append_to_sheet(self, sheet_id: str, values: List[List], range_name: str = "A:Z") -> bool:
        """Append data to a Google Sheet."""
        if not self.service:
            return False
        
        try:
            result = self.service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body={'values': values}
            ).execute()
            return True
        except HttpError as e:
            print(f"❌ Error appending to sheet: {e}")
            return False
    
    def _update_sheet_cell(self, sheet_id: str, cell_range: str, value: str) -> bool:
        """Update a specific cell in Google Sheet."""
        if not self.service:
            return False
        
        try:
            result = self.service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=cell_range,
                valueInputOption='USER_ENTERED',
                body={'values': [[value]]}
            ).execute()
            return True
        except HttpError as e:
            print(f"❌ Error updating sheet cell: {e}")
            return False


# ==================== PATIENT STATUS MONITORING ====================

class ReadPatientStatusTool(SheetsMonitoringToolBase):
    """Reads patient status updates from Google Sheets."""
    
    name: str = "read_patient_status"
    description: str = """Read real-time patient status updates from the Patient Status Sheet.
    
    Use this tool to:
    - Check current status of all patients
    - Monitor critical or recovering patients
    - Get latest nursing observations
    - Track patient progress over time
    
    Hospital staff update this sheet throughout the day with patient observations.
    """
    args_schema: Type[BaseModel] = ReadPatientStatusInput
    
    def _run(self, patient_id: str = None, status_type: str = "all", limit: int = 10) -> str:
        """Execute the patient status reading."""
        
        if not PATIENT_STATUS_SHEET_ID:
            return "❌ Patient Status Sheet ID not configured. Please set PATIENT_STATUS_SHEET_ID in .env"
        
        if not self.service:
            return "❌ Google Sheets service not available"
        
        try:
            # Read patient status data
            values = self._read_sheet_data(PATIENT_STATUS_SHEET_ID)
            
            if not values:
                return "📋 No patient status updates found"
            
            # Parse headers and data
            headers = values[0] if values else []
            data_rows = values[1:] if len(values) > 1 else []
            
            if not data_rows:
                return "📋 No patient status data available"
            
            # Filter data based on criteria
            filtered_data = []
            for row in data_rows[:limit]:
                if len(row) < len(headers):
                    continue
                
                # Create row dict
                row_data = {headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))}
                
                # Apply filters
                if patient_id and row_data.get('Patient ID', '').lower() != patient_id.lower():
                    continue
                
                if status_type != "all" and row_data.get('Status', '').lower() != status_type.lower():
                    continue
                
                filtered_data.append(row_data)
            
            if not filtered_data:
                return f"📋 No patient status updates found matching criteria"
            
            # Format response
            response = f"👥 **Patient Status Updates** ({len(filtered_data)} records)\n\n"
            
            for data in filtered_data:
                patient_name = data.get('Patient ID', 'Unknown')
                status = data.get('Status', 'Unknown')
                notes = data.get('Notes', 'No notes')
                updated_by = data.get('Updated By', 'Unknown')
                timestamp = data.get('Timestamp', 'Unknown')
                
                status_emoji = "🔴" if status.lower() == "critical" else "🟡" if status.lower() == "stable" else "🟢"
                
                response += f"""
{status_emoji} **{patient_name}**
   • Status: {status}
   • Notes: {notes}
   • Updated by: {updated_by}
   • Time: {timestamp}
"""
            
            return response
        
        except Exception as e:
            return f"❌ Error reading patient status: {e}"


class UpdatePatientStatusTool(SheetsMonitoringToolBase):
    """Updates patient status in Google Sheets."""
    
    name: str = "update_patient_status"
    description: str = """Update patient status in the Patient Status Sheet.
    
    Use this tool to:
    - Record new patient status updates
    - Log nursing observations
    - Update patient condition changes
    - Notify staff of patient progress
    
    This creates a permanent record that all staff can see.
    """
    args_schema: Type[BaseModel] = UpdatePatientStatusInput
    
    def _run(self, patient_id: str, status: str, notes: str, updated_by: str) -> str:
        """Execute the patient status update."""
        
        if not PATIENT_STATUS_SHEET_ID:
            return "❌ Patient Status Sheet ID not configured. Please set PATIENT_STATUS_SHEET_ID in .env"
        
        if not self.service:
            return "❌ Google Sheets service not available"
        
        try:
            # Prepare new row data
            timestamp = self._get_current_timestamp()
            new_row = [
                patient_id,           # Patient ID
                status,               # Status
                notes,                # Notes
                updated_by,           # Updated By
                timestamp,            # Timestamp
                "Active"              # Record Status
            ]
            
            # Append to sheet
            success = self._append_to_sheet(PATIENT_STATUS_SHEET_ID, [new_row])
            
            if success:
                return f"""✅ Patient Status Updated Successfully!

📋 **Update Details:**
   • Patient ID: {patient_id}
   • Status: {status}
   • Notes: {notes}
   • Updated by: {updated_by}
   • Time: {timestamp}

💡 **Status visible to all hospital staff in real-time**
"""
            else:
                return "❌ Failed to update patient status sheet"
        
        except Exception as e:
            return f"❌ Error updating patient status: {e}"


# ==================== DOCTOR NOTES MONITORING ====================

class ReadDoctorNotesTool(SheetsMonitoringToolBase):
    """Reads doctor notes from Google Sheets."""
    
    name: str = "read_doctor_notes"
    description: str = """Read doctor notes and observations from the Doctor Notes Sheet.
    
    Use this tool to:
    - Get latest doctor observations for patients
    - Read diagnoses and treatment plans
    - Check prescription updates
    - Review doctor recommendations
    
    Doctors add notes here throughout their shifts.
    """
    args_schema: Type[BaseModel] = ReadDoctorNotesInput
    
    def _run(self, patient_id: str = None, doctor_name: str = None, 
             date_from: str = None, limit: int = 10) -> str:
        """Execute the doctor notes reading."""
        
        if not DOCTOR_NOTES_SHEET_ID:
            return "❌ Doctor Notes Sheet ID not configured. Please set DOCTOR_NOTES_SHEET_ID in .env"
        
        if not self.service:
            return "❌ Google Sheets service not available"
        
        try:
            # Read doctor notes data
            values = self._read_sheet_data(DOCTOR_NOTES_SHEET_ID)
            
            if not values:
                return "📋 No doctor notes found"
            
            # Parse headers and data
            headers = values[0] if values else []
            data_rows = values[1:] if len(values) > 1 else []
            
            if not data_rows:
                return "📋 No doctor notes data available"
            
            # Filter and format data
            filtered_data = []
            for row in data_rows[:limit]:
                if len(row) < len(headers):
                    continue
                
                # Create row dict
                row_data = {headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))}
                
                # Apply filters
                if patient_id and row_data.get('Patient ID', '').lower() != patient_id.lower():
                    continue
                
                if doctor_name and doctor_name.lower() not in row_data.get('Doctor Name', '').lower():
                    continue
                
                if date_from and row_data.get('Date', '') < date_from:
                    continue
                
                filtered_data.append(row_data)
            
            if not filtered_data:
                return f"📋 No doctor notes found matching criteria"
            
            # Format response
            response = f"👨‍⚕️ **Doctor Notes** ({len(filtered_data)} records)\n\n"
            
            for data in filtered_data:
                patient = data.get('Patient ID', 'Unknown')
                doctor = data.get('Doctor Name', 'Unknown')
                note_type = data.get('Note Type', 'General')
                content = data.get('Note Content', 'No content')
                priority = data.get('Priority', 'Normal')
                timestamp = data.get('Timestamp', 'Unknown')
                
                priority_emoji = "🚨" if priority.lower() == "urgent" else "⚠️" if priority.lower() == "high" else "📝"
                
                response += f"""
{priority_emoji} **{note_type}** - {patient}
   • Doctor: Dr. {doctor}
   • Priority: {priority}
   • Notes: {content}
   • Time: {timestamp}
"""
            
            return response
        
        except Exception as e:
            return f"❌ Error reading doctor notes: {e}"


class AddDoctorNoteTool(SheetsMonitoringToolBase):
    """Adds doctor notes to Google Sheets."""
    
    name: str = "add_doctor_note"
    description: str = """Add a new doctor note to the Doctor Notes Sheet.
    
    Use this tool to:
    - Record doctor observations
    - Log diagnoses and treatments
    - Add prescription notes
    - Document patient interactions
    
    Creates a permanent record that all medical staff can access.
    """
    args_schema: Type[BaseModel] = AddDoctorNoteInput
    
    def _run(self, patient_id: str, doctor_name: str, note_type: str, 
             note_content: str, priority: str = "Normal") -> str:
        """Execute the doctor note addition."""
        
        if not DOCTOR_NOTES_SHEET_ID:
            return "❌ Doctor Notes Sheet ID not configured. Please set DOCTOR_NOTES_SHEET_ID in .env"
        
        if not self.service:
            return "❌ Google Sheets service not available"
        
        try:
            # Prepare new row data
            timestamp = self._get_current_timestamp()
            new_row = [
                patient_id,           # Patient ID
                doctor_name,          # Doctor Name
                note_type,            # Note Type
                note_content,         # Note Content
                priority,             # Priority
                timestamp,            # Timestamp
                "Active"              # Record Status
            ]
            
            # Append to sheet
            success = self._append_to_sheet(DOCTOR_NOTES_SHEET_ID, [new_row])
            
            if success:
                return f"""✅ Doctor Note Added Successfully!

👨‍⚕️ **Note Details:**
   • Patient ID: {patient_id}
   • Doctor: Dr. {doctor_name}
   • Type: {note_type}
   • Priority: {priority}
   • Content: {note_content}
   • Time: {timestamp}

💡 **Note is now visible to all medical staff**
"""
            else:
                return "❌ Failed to add doctor note to sheet"
        
        except Exception as e:
            return f"❌ Error adding doctor note: {e}"


# ==================== LAB RESULTS MONITORING ====================

class ReadLabResultsTool(SheetsMonitoringToolBase):
    """Reads lab results from Google Sheets."""
    
    name: str = "read_lab_results"
    description: str = """Read laboratory test results from the Lab Results Sheet.
    
    Use this tool to:
    - Check latest lab test results
    - Monitor pending tests
    - Review abnormal results
    - Track test completion status
    
    Lab technicians update this sheet with test results.
    """
    args_schema: Type[BaseModel] = ReadLabResultsInput
    
    def _run(self, patient_id: str = None, test_type: str = None, 
             status: str = "all", limit: int = 10) -> str:
        """Execute the lab results reading."""
        
        if not LAB_RESULTS_SHEET_ID:
            return "❌ Lab Results Sheet ID not configured. Please set LAB_RESULTS_SHEET_ID in .env"
        
        if not self.service:
            return "❌ Google Sheets service not available"
        
        try:
            # Read lab results data
            values = self._read_sheet_data(LAB_RESULTS_SHEET_ID)
            
            if not values:
                return "🧪 No lab results found"
            
            # Parse and filter data
            headers = values[0] if values else []
            data_rows = values[1:] if len(values) > 1 else []
            
            if not data_rows:
                return "🧪 No lab results data available"
            
            filtered_data = []
            for row in data_rows[:limit]:
                if len(row) < len(headers):
                    continue
                
                row_data = {headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))}
                
                # Apply filters
                if patient_id and row_data.get('Patient ID', '').lower() != patient_id.lower():
                    continue
                
                if test_type and test_type.lower() not in row_data.get('Test Name', '').lower():
                    continue
                
                if status != "all" and row_data.get('Status', '').lower() != status.lower():
                    continue
                
                filtered_data.append(row_data)
            
            if not filtered_data:
                return f"🧪 No lab results found matching criteria"
            
            # Format response
            response = f"🧪 **Lab Results** ({len(filtered_data)} records)\n\n"
            
            for data in filtered_data:
                patient = data.get('Patient ID', 'Unknown')
                test_name = data.get('Test Name', 'Unknown')
                result = data.get('Result Value', 'Pending')
                normal_range = data.get('Normal Range', 'N/A')
                status = data.get('Status', 'Unknown')
                technician = data.get('Technician Name', 'Unknown')
                timestamp = data.get('Timestamp', 'Unknown')
                
                status_emoji = "🔴" if status.lower() == "critical" else "🟡" if status.lower() == "abnormal" else "🟢"
                
                response += f"""
{status_emoji} **{test_name}** - {patient}
   • Result: {result} (Normal: {normal_range})
   • Status: {status}
   • Technician: {technician}
   • Time: {timestamp}
"""
            
            return response
        
        except Exception as e:
            return f"❌ Error reading lab results: {e}"


class UpdateLabResultTool(SheetsMonitoringToolBase):
    """Updates lab results in Google Sheets."""
    
    name: str = "update_lab_result"
    description: str = """Update laboratory test results in the Lab Results Sheet.
    
    Use this tool to:
    - Record new test results
    - Update test status
    - Log abnormal findings
    - Complete pending tests
    
    Creates a permanent record accessible to all medical staff.
    """
    args_schema: Type[BaseModel] = UpdateLabResultInput
    
    def _run(self, patient_id: str, test_name: str, result_value: str, 
             normal_range: str, status: str, technician_name: str) -> str:
        """Execute the lab result update."""
        
        if not LAB_RESULTS_SHEET_ID:
            return "❌ Lab Results Sheet ID not configured. Please set LAB_RESULTS_SHEET_ID in .env"
        
        if not self.service:
            return "❌ Google Sheets service not available"
        
        try:
            # Prepare new row data
            timestamp = self._get_current_timestamp()
            new_row = [
                patient_id,           # Patient ID
                test_name,            # Test Name
                result_value,         # Result Value
                normal_range,         # Normal Range
                status,               # Status
                technician_name,      # Technician Name
                timestamp,            # Timestamp
                "Complete"            # Record Status
            ]
            
            # Append to sheet
            success = self._append_to_sheet(LAB_RESULTS_SHEET_ID, [new_row])
            
            if success:
                return f"""✅ Lab Result Updated Successfully!

🧪 **Result Details:**
   • Patient ID: {patient_id}
   • Test: {test_name}
   • Result: {result_value} (Normal: {normal_range})
   • Status: {status}
   • Technician: {technician_name}
   • Time: {timestamp}

💡 **Result is now available to all medical staff**
"""
            else:
                return "❌ Failed to update lab result sheet"
        
        except Exception as e:
            return f"❌ Error updating lab result: {e}"


# ==================== STAFF COMMUNICATION MONITORING ====================

class ReadStaffUpdatesTool(SheetsMonitoringToolBase):
    """Reads staff updates and communications from Google Sheets."""
    
    name: str = "read_staff_updates"
    description: str = """Read staff updates and communications from the Staff Updates Sheet.
    
    Use this tool to:
    - Check latest staff announcements
    - Read department updates
    - Monitor urgent communications
    - Track staff requests and alerts
    
    All hospital departments use this for general communication.
    """
    args_schema: Type[BaseModel] = ReadStaffUpdatesInput
    
    def _run(self, department: str = None, priority: str = "all", 
             unread_only: bool = True, limit: int = 10) -> str:
        """Execute the staff updates reading."""
        
        if not STAFF_UPDATES_SHEET_ID:
            return "❌ Staff Updates Sheet ID not configured. Please set STAFF_UPDATES_SHEET_ID in .env"
        
        if not self.service:
            return "❌ Google Sheets service not available"
        
        try:
            # Read staff updates data
            values = self._read_sheet_data(STAFF_UPDATES_SHEET_ID)
            
            if not values:
                return "📢 No staff updates found"
            
            # Parse and filter data
            headers = values[0] if values else []
            data_rows = values[1:] if len(values) > 1 else []
            
            if not data_rows:
                return "📢 No staff updates data available"
            
            filtered_data = []
            for row in data_rows[:limit]:
                if len(row) < len(headers):
                    continue
                
                row_data = {headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))}
                
                # Apply filters
                if department and department.lower() not in row_data.get('Department', '').lower():
                    continue
                
                if priority != "all" and row_data.get('Priority', '').lower() != priority.lower():
                    continue
                
                if unread_only and row_data.get('Status', '').lower() == 'read':
                    continue
                
                filtered_data.append(row_data)
            
            if not filtered_data:
                return f"📢 No staff updates found matching criteria"
            
            # Format response
            response = f"📢 **Staff Updates** ({len(filtered_data)} records)\n\n"
            
            for data in filtered_data:
                staff = data.get('Staff Name', 'Unknown')
                dept = data.get('Department', 'Unknown')
                update_type = data.get('Update Type', 'Info')
                message = data.get('Message', 'No message')
                priority = data.get('Priority', 'Normal')
                timestamp = data.get('Timestamp', 'Unknown')
                
                priority_emoji = "🚨" if priority.lower() == "urgent" else "⚠️" if priority.lower() == "high" else "📝"
                
                response += f"""
{priority_emoji} **{update_type}** - {dept}
   • From: {staff}
   • Priority: {priority}
   • Message: {message}
   • Time: {timestamp}
"""
            
            return response
        
        except Exception as e:
            return f"❌ Error reading staff updates: {e}"


class AddStaffUpdateTool(SheetsMonitoringToolBase):
    """Adds staff updates to Google Sheets."""
    
    name: str = "add_staff_update"
    description: str = """Add a new staff update to the Staff Updates Sheet.
    
    Use this tool to:
    - Post department announcements
    - Send staff communications
    - Share important updates
    - Request assistance or resources
    
    Visible to all hospital staff immediately.
    """
    args_schema: Type[BaseModel] = AddStaffUpdateInput
    
    def _run(self, staff_name: str, department: str, update_type: str, 
             message: str, priority: str = "Normal") -> str:
        """Execute the staff update addition."""
        
        if not STAFF_UPDATES_SHEET_ID:
            return "❌ Staff Updates Sheet ID not configured. Please set STAFF_UPDATES_SHEET_ID in .env"
        
        if not self.service:
            return "❌ Google Sheets service not available"
        
        try:
            # Prepare new row data
            timestamp = self._get_current_timestamp()
            new_row = [
                staff_name,           # Staff Name
                department,           # Department
                update_type,          # Update Type
                message,              # Message
                priority,             # Priority
                timestamp,            # Timestamp
                "Unread"              # Status
            ]
            
            # Append to sheet
            success = self._append_to_sheet(STAFF_UPDATES_SHEET_ID, [new_row])
            
            if success:
                return f"""✅ Staff Update Posted Successfully!

📢 **Update Details:**
   • From: {staff_name} ({department})
   • Type: {update_type}
   • Priority: {priority}
   • Message: {message}
   • Time: {timestamp}

💡 **Update is now visible to all hospital staff**
"""
            else:
                return "❌ Failed to add staff update to sheet"
        
        except Exception as e:
            return f"❌ Error adding staff update: {e}"


# ==================== EMERGENCY ALERTS MONITORING ====================

class ReadEmergencyAlertsTool(SheetsMonitoringToolBase):
    """Reads emergency alerts from Google Sheets."""
    
    name: str = "read_emergency_alerts"
    description: str = """Read emergency alerts from the Emergency Alerts Sheet.
    
    Use this tool to:
    - Check active emergency situations
    - Monitor critical alerts
    - Review emergency response status
    - Track safety incidents
    
    Critical for hospital safety and emergency management.
    """
    args_schema: Type[BaseModel] = ReadEmergencyAlertsInput
    
    def _run(self, status: str = "active", priority: str = "all", limit: int = 20) -> str:
        """Execute the emergency alerts reading."""
        
        if not EMERGENCY_ALERTS_SHEET_ID:
            return "❌ Emergency Alerts Sheet ID not configured. Please set EMERGENCY_ALERTS_SHEET_ID in .env"
        
        if not self.service:
            return "❌ Google Sheets service not available"
        
        try:
            # Read emergency alerts data
            values = self._read_sheet_data(EMERGENCY_ALERTS_SHEET_ID)
            
            if not values:
                return "🚨 No emergency alerts found"
            
            # Parse and filter data
            headers = values[0] if values else []
            data_rows = values[1:] if len(values) > 1 else []
            
            if not data_rows:
                return "🚨 No emergency alerts data available"
            
            filtered_data = []
            for row in data_rows[:limit]:
                if len(row) < len(headers):
                    continue
                
                row_data = {headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))}
                
                # Apply filters
                if status != "all" and row_data.get('Status', '').lower() != status.lower():
                    continue
                
                if priority != "all" and row_data.get('Severity', '').lower() != priority.lower():
                    continue
                
                filtered_data.append(row_data)
            
            if not filtered_data:
                return f"🚨 No emergency alerts found matching criteria"
            
            # Format response
            response = f"🚨 **Emergency Alerts** ({len(filtered_data)} records)\n\n"
            
            for data in filtered_data:
                alert_type = data.get('Alert Type', 'Unknown')
                location = data.get('Location', 'Unknown')
                description = data.get('Description', 'No description')
                severity = data.get('Severity', 'Unknown')
                reported_by = data.get('Reported By', 'Unknown')
                timestamp = data.get('Timestamp', 'Unknown')
                status = data.get('Status', 'Unknown')
                
                severity_emoji = "🚨" if severity.lower() == "critical" else "⚠️" if severity.lower() == "high" else "🟨"
                
                response += f"""
{severity_emoji} **{alert_type}** - {location}
   • Severity: {severity}
   • Status: {status}
   • Description: {description}
   • Reported by: {reported_by}
   • Time: {timestamp}
"""
            
            return response
        
        except Exception as e:
            return f"❌ Error reading emergency alerts: {e}"


class CreateEmergencyAlertTool(SheetsMonitoringToolBase):
    """Creates emergency alerts in Google Sheets."""
    
    name: str = "create_emergency_alert"
    description: str = """Create a new emergency alert in the Emergency Alerts Sheet.
    
    Use this tool to:
    - Report emergency situations
    - Alert security and safety teams
    - Document critical incidents
    - Trigger emergency response protocols
    
    CRITICAL: Use only for genuine emergencies.
    """
    args_schema: Type[BaseModel] = CreateEmergencyAlertInput
    
    def _run(self, alert_type: str, location: str, description: str, 
             severity: str, reported_by: str) -> str:
        """Execute the emergency alert creation."""
        
        if not EMERGENCY_ALERTS_SHEET_ID:
            return "❌ Emergency Alerts Sheet ID not configured. Please set EMERGENCY_ALERTS_SHEET_ID in .env"
        
        if not self.service:
            return "❌ Google Sheets service not available"
        
        try:
            # Prepare new row data
            timestamp = self._get_current_timestamp()
            alert_id = f"ALERT_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            new_row = [
                alert_id,             # Alert ID
                alert_type,           # Alert Type
                location,             # Location
                description,          # Description
                severity,             # Severity
                reported_by,          # Reported By
                timestamp,            # Timestamp
                "Active"              # Status
            ]
            
            # Append to sheet
            success = self._append_to_sheet(EMERGENCY_ALERTS_SHEET_ID, [new_row])
            
            if success:
                return f"""🚨 EMERGENCY ALERT CREATED!

🚨 **Alert Details:**
   • Alert ID: {alert_id}
   • Type: {alert_type}
   • Location: {location}
   • Severity: {severity}
   • Description: {description}
   • Reported by: {reported_by}
   • Time: {timestamp}

⚠️ **IMMEDIATE ACTION REQUIRED**
💡 **Alert broadcast to all emergency response teams**
"""
            else:
                return "❌ Failed to create emergency alert"
        
        except Exception as e:
            return f"❌ Error creating emergency alert: {e}"


# ==================== HELPER FUNCTIONS ====================

def get_all_monitoring_tools() -> List[BaseTool]:
    """Get all Google Sheets monitoring tools."""
    return [
        ReadPatientStatusTool(),
        UpdatePatientStatusTool(),
        ReadDoctorNotesTool(),
        AddDoctorNoteTool(),
        ReadLabResultsTool(),
        UpdateLabResultTool(),
        ReadStaffUpdatesTool(),
        AddStaffUpdateTool(),
        ReadEmergencyAlertsTool(),
        CreateEmergencyAlertTool()
    ]


def get_monitoring_tools_by_category(category: str) -> List[BaseTool]:
    """Get monitoring tools by category."""
    categories = {
        "patient": [ReadPatientStatusTool(), UpdatePatientStatusTool()],
        "doctor": [ReadDoctorNotesTool(), AddDoctorNoteTool()],
        "lab": [ReadLabResultsTool(), UpdateLabResultTool()],
        "staff": [ReadStaffUpdatesTool(), AddStaffUpdateTool()],
        "emergency": [ReadEmergencyAlertsTool(), CreateEmergencyAlertTool()]
    }
    
    return categories.get(category.lower(), [])


# ==================== TESTING ====================

if __name__ == "__main__":
    print("=" * 70)
    print("🏥 GOOGLE SHEETS MONITORING TOOLS TESTING")
    print("=" * 70)
    
    # Test patient status reading
    print("\n📋 Testing Patient Status Reading...")
    patient_tool = ReadPatientStatusTool()
    result = patient_tool._run()
    print(result)
    
    # Test staff updates reading
    print("\n📢 Testing Staff Updates Reading...")
    staff_tool = ReadStaffUpdatesTool()
    result = staff_tool._run()
    print(result)
    
    print("\n" + "=" * 70)
    print("✅ MONITORING TOOLS TESTING COMPLETED!")
    print("=" * 70)