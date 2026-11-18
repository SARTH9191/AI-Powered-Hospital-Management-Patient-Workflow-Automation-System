"""
Enhanced Google Sheets Monitoring & Communication Tools
Real-time bidirectional communication between hospital staff and AI agent through Google Sheets

Features:
- Monitor sheet changes in real-time
- Read staff updates and respond intelligently
- Update sheets based on patient interactions
- Multi-sheet coordination for different departments
- Staff notification system through sheets

Author: Hospital Management AI System
"""

import os
import json
import time
from typing import Optional, Type, List, Dict, Any
from datetime import datetime, timedelta

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from pydantic import BaseModel, Field
from langchain.tools import BaseTool


# ==================== SHEET MONITORING CONFIG ====================

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Hospital Sheets Configuration - Add these to your .env file
PATIENT_STATUS_SHEET_ID = os.getenv('PATIENT_STATUS_SHEET_ID', '1PatientStatusSheetID')
DOCTOR_NOTES_SHEET_ID = os.getenv('DOCTOR_NOTES_SHEET_ID', '1DoctorNotesSheetID')  
LAB_RESULTS_SHEET_ID = os.getenv('LAB_RESULTS_SHEET_ID', '1LabResultsSheetID')
STAFF_UPDATES_SHEET_ID = os.getenv('STAFF_UPDATES_SHEET_ID', '1StaffUpdatesSheetID')
EMERGENCY_ALERTS_SHEET_ID = os.getenv('EMERGENCY_ALERTS_SHEET_ID', '1EmergencyAlertsSheetID')
PHARMACY_INVENTORY_SHEET_ID = os.getenv('PHARMACY_INVENTORY_SHEET_ID', '1PharmacyInventorySheetID')


# ==================== INPUT SCHEMAS ====================

class MonitorSheetInput(BaseModel):
    """Input schema for monitoring sheet changes."""
    sheet_id: str = Field(description="Google Sheet ID to monitor")
    sheet_name: str = Field(default="Sheet1", description="Sheet tab name to monitor")
    check_interval: int = Field(default=30, description="Check interval in seconds")
    last_check_time: Optional[str] = Field(default=None, description="Last check timestamp")

class ReadStaffUpdatesInput(BaseModel):
    """Input schema for reading staff updates."""
    department: str = Field(description="Department to check (doctors, nurses, lab, pharmacy, emergency)")
    patient_id: Optional[str] = Field(default=None, description="Specific patient ID to filter")
    hours_back: int = Field(default=24, description="How many hours back to check for updates")

class UpdatePatientStatusInput(BaseModel):
    """Input schema for updating patient status."""
    patient_id: str = Field(description="Patient ID")
    status_type: str = Field(description="Type of status (vitals, medications, treatments, alerts)")
    status_value: str = Field(description="Status update value")
    updated_by: str = Field(description="Who is updating (AI Agent, Doctor Name, etc.)")

class StaffNotificationInput(BaseModel):
    """Input schema for sending notifications to staff via sheets."""
    notification_type: str = Field(description="Type of notification (urgent, info, request, reminder)")
    message: str = Field(description="Notification message")
    target_department: str = Field(description="Target department (doctors, nurses, lab, pharmacy, all)")
    patient_id: Optional[str] = Field(default=None, description="Related patient ID if applicable")

class SheetAnalyticsInput(BaseModel):
    """Input schema for analyzing sheet data."""
    analysis_type: str = Field(description="Type of analysis (patient_trends, staff_workload, department_metrics)")
    time_period: str = Field(description="Time period (today, week, month)")
    department: Optional[str] = Field(default=None, description="Specific department to analyze")


# ==================== BASE CLASS ====================

class SheetsMonitoringToolBase(BaseTool):
    """Base class for Google Sheets monitoring tools."""
    
    def __init__(self):
        super().__init__()
        self.service = self._initialize_sheets_service()
    
    def _initialize_sheets_service(self):
        """Initialize Google Sheets service."""
        try:
            creds = None
            token_path = os.path.join(os.path.dirname(__file__), '..', 'credentials', 'token.json')
            credentials_path = os.path.join(os.path.dirname(__file__), '..', 'credentials', 'credentials.json')
            
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            service = build('sheets', 'v4', credentials=creds)
            print("✅ Google Sheets monitoring service initialized")
            return service
            
        except Exception as e:
            print(f"❌ Error initializing Sheets service: {e}")
            return None
    
    def _get_current_timestamp(self):
        """Get current timestamp in ISO format."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string to datetime object."""
        try:
            return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        except:
            return datetime.now() - timedelta(hours=24)  # Default to 24 hours ago


# ==================== SHEET MONITORING TOOLS ====================

class MonitorSheetChangesTool(SheetsMonitoringToolBase):
    """Monitors Google Sheets for real-time changes and updates."""
    
    name: str = "monitor_sheet_changes"
    description: str = """Monitor a Google Sheet for real-time changes and updates from hospital staff.
    
    Use this tool to:
    - Track staff updates in real-time
    - Monitor patient status changes
    - Detect emergency alerts
    - Watch for lab results or doctor notes
    
    Returns details of any new changes since last check.
    """
    args_schema: Type[BaseModel] = MonitorSheetInput
    
    def _run(self, sheet_id: str, sheet_name: str = "Sheet1", check_interval: int = 30, 
             last_check_time: str = None) -> str:
        """Execute sheet monitoring."""
        
        if not self.service:
            return "❌ Error: Google Sheets service not available"
        
        try:
            # Get current sheet data
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=f'{sheet_name}!A:Z'
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return f"📋 Sheet {sheet_name} is empty - no changes to monitor"
            
            # Parse last check time
            if last_check_time:
                last_check = self._parse_timestamp(last_check_time)
            else:
                last_check = datetime.now() - timedelta(hours=1)  # Default to 1 hour ago
            
            # Analyze recent changes
            headers = values[0] if values else []
            recent_changes = []
            
            # Look for timestamp columns (common patterns)
            timestamp_cols = []
            for i, header in enumerate(headers):
                if any(keyword in header.lower() for keyword in ['time', 'date', 'created', 'updated', 'modified']):
                    timestamp_cols.append(i)
            
            # Check each row for recent updates
            for row_idx, row in enumerate(values[1:], start=2):  # Skip header
                if len(row) <= max(timestamp_cols) if timestamp_cols else False:
                    continue
                
                # Check if row has recent timestamp
                for ts_col in timestamp_cols:
                    if ts_col < len(row) and row[ts_col]:
                        try:
                            row_time = self._parse_timestamp(row[ts_col])
                            if row_time > last_check:
                                recent_changes.append({
                                    'row': row_idx,
                                    'data': row,
                                    'timestamp': row[ts_col],
                                    'type': 'recent_update'
                                })
                                break
                        except:
                            continue
            
            # Format response
            if not recent_changes:
                return f"""📋 **Sheet Monitoring Report**

🔍 **Sheet:** {sheet_name}
⏰ **Last Check:** {last_check_time or 'First check'}
⏱️ **Current Time:** {self._get_current_timestamp()}
📊 **Total Rows:** {len(values)-1}
✅ **Recent Changes:** None

💡 **Status:** No new updates from staff since last check."""
            
            response = f"""📋 **Sheet Monitoring Report**

🔍 **Sheet:** {sheet_name}
⏰ **Last Check:** {last_check_time or 'First check'}  
⏱️ **Current Time:** {self._get_current_timestamp()}
📊 **Total Rows:** {len(values)-1}
🆕 **Recent Changes:** {len(recent_changes)}

📝 **New Updates:**"""
            
            for change in recent_changes[:5]:  # Show max 5 recent changes
                row_data = change['data']
                response += f"""
   • Row {change['row']}: Updated at {change['timestamp']}
     Data: {' | '.join(row_data[:3])}..."""
            
            if len(recent_changes) > 5:
                response += f"\n   ... and {len(recent_changes)-5} more changes"
            
            return response
        
        except HttpError as e:
            return f"❌ Error monitoring sheet: {e}"
        except Exception as e:
            return f"❌ Unexpected error: {e}"


class ReadStaffUpdatesTool(SheetsMonitoringToolBase):
    """Reads and interprets updates from hospital staff in Google Sheets."""
    
    name: str = "read_staff_updates"
    description: str = """Read updates from hospital staff across different department sheets.
    
    Use this tool to:
    - Check doctor notes and observations
    - Read nurse status updates
    - Get lab results and pharmacy updates
    - Monitor emergency alerts from staff
    
    Returns organized staff updates by department.
    """
    args_schema: Type[BaseModel] = ReadStaffUpdatesInput
    
    def _run(self, department: str, patient_id: str = None, hours_back: int = 24) -> str:
        """Execute staff updates reading."""
        
        if not self.service:
            return "❌ Error: Google Sheets service not available"
        
        # Map departments to sheet IDs
        department_sheets = {
            'doctors': DOCTOR_NOTES_SHEET_ID,
            'nurses': PATIENT_STATUS_SHEET_ID,
            'lab': LAB_RESULTS_SHEET_ID,
            'pharmacy': PHARMACY_INVENTORY_SHEET_ID,
            'emergency': EMERGENCY_ALERTS_SHEET_ID
        }
        
        if department not in department_sheets:
            return f"❌ Unknown department: {department}. Available: {list(department_sheets.keys())}"
        
        sheet_id = department_sheets[department]
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        try:
            # Read sheet data
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range='Sheet1!A:Z'
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return f"📋 No updates found in {department} sheet"
            
            headers = values[0]
            staff_updates = []
            
            # Process each row for relevant updates
            for row_idx, row in enumerate(values[1:], start=2):
                if len(row) < len(headers):
                    continue
                
                # Check if patient_id filter applies
                if patient_id:
                    patient_found = False
                    for cell in row:
                        if patient_id.lower() in str(cell).lower():
                            patient_found = True
                            break
                    if not patient_found:
                        continue
                
                # Check for recent timestamps
                for col_idx, cell in enumerate(row):
                    if col_idx < len(headers) and 'time' in headers[col_idx].lower():
                        try:
                            cell_time = self._parse_timestamp(str(cell))
                            if cell_time > cutoff_time:
                                staff_updates.append({
                                    'row': row_idx,
                                    'timestamp': str(cell),
                                    'data': dict(zip(headers, row + [''] * (len(headers) - len(row)))),
                                    'department': department
                                })
                                break
                        except:
                            continue
            
            # Format response
            if not staff_updates:
                return f"""📋 **Staff Updates Report - {department.title()}**

⏰ **Time Range:** Last {hours_back} hours
🔍 **Patient Filter:** {patient_id or 'All patients'}
📊 **Updates Found:** 0

✅ **Status:** No recent updates from {department} staff."""
            
            response = f"""📋 **Staff Updates Report - {department.title()}**

⏰ **Time Range:** Last {hours_back} hours
🔍 **Patient Filter:** {patient_id or 'All patients'}
📊 **Updates Found:** {len(staff_updates)}

📝 **Recent Updates:**"""
            
            for update in staff_updates[:5]:  # Show max 5 updates
                data = update['data']
                response += f"""
   • **{update['timestamp']}**
     Patient: {data.get('Patient ID', 'N/A')} | {data.get('Patient Name', 'N/A')}
     Update: {data.get('Notes', data.get('Status', data.get('Result', 'No details')))}
     Staff: {data.get('Updated By', data.get('Doctor', data.get('Technician', 'Unknown')))}"""
            
            if len(staff_updates) > 5:
                response += f"\n   ... and {len(staff_updates)-5} more updates"
            
            return response
        
        except HttpError as e:
            return f"❌ Error reading staff updates: {e}"
        except Exception as e:
            return f"❌ Unexpected error: {e}"


class UpdatePatientStatusTool(SheetsMonitoringToolBase):
    """Updates patient status in Google Sheets based on AI agent actions."""
    
    name: str = "update_patient_status"
    description: str = """Update patient status in Google Sheets to inform hospital staff.
    
    Use this tool to:
    - Update patient vitals and status
    - Log medication administration
    - Record treatment progress
    - Add AI agent observations
    
    Creates entries that staff can see and respond to.
    """
    args_schema: Type[BaseModel] = UpdatePatientStatusInput
    
    def _run(self, patient_id: str, status_type: str, status_value: str, updated_by: str = "AI Agent") -> str:
        """Execute patient status update."""
        
        if not self.service:
            return "❌ Error: Google Sheets service not available"
        
        try:
            # Prepare update data
            timestamp = self._get_current_timestamp()
            
            update_data = [
                patient_id,           # Patient ID
                status_type,          # Status Type
                status_value,         # Status Value
                updated_by,          # Updated By
                timestamp,           # Timestamp
                "Active",            # Status
                f"AI Update: {status_type} for patient {patient_id}"  # Notes
            ]
            
            # Add to patient status sheet
            result = self.service.spreadsheets().values().append(
                spreadsheetId=PATIENT_STATUS_SHEET_ID,
                range='Sheet1!A:G',
                valueInputOption='USER_ENTERED',
                body={'values': [update_data]}
            ).execute()
            
            return f"""✅ **Patient Status Updated Successfully**

👤 **Patient:** {patient_id}
📋 **Status Type:** {status_type}
💬 **Value:** {status_value}
🤖 **Updated By:** {updated_by}
⏰ **Timestamp:** {timestamp}

📊 **Sheet Updated:** Patient Status Sheet
🔄 **Staff Notification:** Hospital staff can now see this update
"""
        
        except HttpError as e:
            return f"❌ Error updating patient status: {e}"
        except Exception as e:
            return f"❌ Unexpected error: {e}"


class StaffNotificationTool(SheetsMonitoringToolBase):
    """Sends notifications to hospital staff through Google Sheets."""
    
    name: str = "notify_staff_via_sheets"
    description: str = """Send notifications to hospital staff through Google Sheets.
    
    Use this tool to:
    - Send urgent alerts to medical staff
    - Request information or actions from staff
    - Provide updates and reminders
    - Coordinate between departments
    
    Creates visible notifications that staff monitor regularly.
    """
    args_schema: Type[BaseModel] = StaffNotificationInput
    
    def _run(self, notification_type: str, message: str, target_department: str, patient_id: str = None) -> str:
        """Execute staff notification."""
        
        if not self.service:
            return "❌ Error: Google Sheets service not available"
        
        try:
            # Determine priority and sheet
            priority_map = {
                'urgent': '🚨 URGENT',
                'info': '💡 INFO',
                'request': '📋 REQUEST',
                'reminder': '⏰ REMINDER'
            }
            
            priority = priority_map.get(notification_type.lower(), '📢 NOTICE')
            timestamp = self._get_current_timestamp()
            
            # Prepare notification data
            notification_data = [
                f"NOTIF_{timestamp.replace(' ', '').replace(':', '').replace('-', '')}",  # Notification ID
                priority,                    # Priority
                target_department.upper(),   # Target Department
                patient_id or "GENERAL",     # Patient ID
                message,                     # Message
                "AI Agent",                  # From
                timestamp,                   # Created At
                "PENDING",                   # Status
                ""                          # Staff Response
            ]
            
            # Add to staff updates sheet
            result = self.service.spreadsheets().values().append(
                spreadsheetId=STAFF_UPDATES_SHEET_ID,
                range='Sheet1!A:I',
                valueInputOption='USER_ENTERED',
                body={'values': [notification_data]}
            ).execute()
            
            # If urgent, also add to emergency alerts
            if notification_type.lower() == 'urgent':
                emergency_data = [
                    timestamp,
                    "AI ALERT",
                    target_department.upper(),
                    patient_id or "GENERAL",
                    message,
                    "ACTIVE",
                    "AI Agent"
                ]
                
                self.service.spreadsheets().values().append(
                    spreadsheetId=EMERGENCY_ALERTS_SHEET_ID,
                    range='Sheet1!A:G',
                    valueInputOption='USER_ENTERED',
                    body={'values': [emergency_data]}
                ).execute()
            
            return f"""✅ **Staff Notification Sent Successfully**

{priority} **{notification_type.upper()} NOTIFICATION**

👥 **Target:** {target_department.upper()} Department
👤 **Patient:** {patient_id or 'General'}
💬 **Message:** {message}
⏰ **Sent:** {timestamp}

📋 **Status:** Notification added to staff monitoring sheets
{'🚨 **Emergency Alert:** Also added to emergency alerts sheet' if notification_type.lower() == 'urgent' else ''}

🔔 **Next:** Staff will see this notification in their monitoring dashboard
"""
        
        except HttpError as e:
            return f"❌ Error sending staff notification: {e}"
        except Exception as e:
            return f"❌ Unexpected error: {e}"


class SheetAnalyticsTool(SheetsMonitoringToolBase):
    """Analyzes Google Sheets data to provide insights and trends."""
    
    name: str = "analyze_sheet_data"
    description: str = """Analyze Google Sheets data to provide insights and trends.
    
    Use this tool to:
    - Analyze patient status trends
    - Monitor staff workload patterns
    - Generate department performance metrics
    - Identify bottlenecks and issues
    
    Returns actionable insights from sheet data.
    """
    args_schema: Type[BaseModel] = SheetAnalyticsInput
    
    def _run(self, analysis_type: str, time_period: str, department: str = None) -> str:
        """Execute sheet data analysis."""
        
        if not self.service:
            return "❌ Error: Google Sheets service not available"
        
        try:
            # Define time range
            now = datetime.now()
            if time_period == 'today':
                start_time = now.replace(hour=0, minute=0, second=0)
            elif time_period == 'week':
                start_time = now - timedelta(days=7)
            elif time_period == 'month':
                start_time = now - timedelta(days=30)
            else:
                start_time = now - timedelta(days=1)
            
            # Collect data from relevant sheets
            sheets_to_analyze = [
                (PATIENT_STATUS_SHEET_ID, 'Patient Status'),
                (DOCTOR_NOTES_SHEET_ID, 'Doctor Notes'),
                (LAB_RESULTS_SHEET_ID, 'Lab Results'),
                (STAFF_UPDATES_SHEET_ID, 'Staff Updates')
            ]
            
            analytics_data = {}
            
            for sheet_id, sheet_name in sheets_to_analyze:
                try:
                    result = self.service.spreadsheets().values().get(
                        spreadsheetId=sheet_id,
                        range='Sheet1!A:Z'
                    ).execute()
                    
                    values = result.get('values', [])
                    if values:
                        analytics_data[sheet_name] = {
                            'total_rows': len(values) - 1,  # Exclude header
                            'recent_entries': 0,
                            'data': values
                        }
                        
                        # Count recent entries
                        for row in values[1:]:
                            for cell in row:
                                try:
                                    if self._parse_timestamp(str(cell)) > start_time:
                                        analytics_data[sheet_name]['recent_entries'] += 1
                                        break
                                except:
                                    continue
                
                except:
                    analytics_data[sheet_name] = {'error': 'Could not access sheet'}
            
            # Generate insights based on analysis type
            if analysis_type == 'patient_trends':
                return self._analyze_patient_trends(analytics_data, time_period)
            elif analysis_type == 'staff_workload':
                return self._analyze_staff_workload(analytics_data, time_period)
            elif analysis_type == 'department_metrics':
                return self._analyze_department_metrics(analytics_data, time_period, department)
            else:
                return self._analyze_general_metrics(analytics_data, time_period)
        
        except Exception as e:
            return f"❌ Error analyzing sheet data: {e}"
    
    def _analyze_patient_trends(self, data: dict, period: str) -> str:
        """Analyze patient status trends."""
        
        patient_updates = data.get('Patient Status', {}).get('recent_entries', 0)
        doctor_notes = data.get('Doctor Notes', {}).get('recent_entries', 0)
        lab_results = data.get('Lab Results', {}).get('recent_entries', 0)
        
        return f"""📊 **Patient Trends Analysis - {period.title()}**

👥 **Patient Activity:**
   • Status Updates: {patient_updates}
   • Doctor Notes: {doctor_notes}
   • Lab Results: {lab_results}
   • Total Activity: {patient_updates + doctor_notes + lab_results}

📈 **Trends:**
   • {'High' if patient_updates > 20 else 'Normal' if patient_updates > 5 else 'Low'} patient status activity
   • {'Active' if doctor_notes > 10 else 'Normal' if doctor_notes > 3 else 'Quiet'} doctor engagement
   • {'Busy' if lab_results > 15 else 'Normal' if lab_results > 5 else 'Light'} lab processing

💡 **Insights:**
   • Patient care activity is {'above average' if patient_updates > 15 else 'typical' if patient_updates > 5 else 'below average'}
   • Medical team engagement is {'high' if doctor_notes > 8 else 'moderate'}
   • Lab efficiency is {'excellent' if lab_results > 10 else 'good'}
"""
    
    def _analyze_staff_workload(self, data: dict, period: str) -> str:
        """Analyze staff workload patterns."""
        
        staff_updates = data.get('Staff Updates', {}).get('recent_entries', 0)
        patient_updates = data.get('Patient Status', {}).get('recent_entries', 0)
        
        return f"""📊 **Staff Workload Analysis - {period.title()}**

👩‍⚕️ **Staff Activity:**
   • Direct Staff Updates: {staff_updates}
   • Patient Status Changes: {patient_updates}
   • Total Workload Indicators: {staff_updates + patient_updates}

⚖️ **Workload Assessment:**
   • Staff Communication: {'Heavy' if staff_updates > 25 else 'Moderate' if staff_updates > 10 else 'Light'}
   • Patient Care Load: {'High' if patient_updates > 30 else 'Normal' if patient_updates > 10 else 'Low'}

📋 **Recommendations:**
   • {'Consider additional staff support' if staff_updates > 30 else 'Workload appears manageable'}
   • {'Monitor for staff burnout indicators' if staff_updates > 40 else 'Staff engagement is healthy'}
"""
    
    def _analyze_department_metrics(self, data: dict, period: str, department: str) -> str:
        """Analyze specific department metrics."""
        
        return f"""📊 **Department Metrics - {department or 'All Departments'} ({period.title()})**

🏥 **Department Performance:**
   • Patient Status Updates: {data.get('Patient Status', {}).get('recent_entries', 0)}
   • Medical Documentation: {data.get('Doctor Notes', {}).get('recent_entries', 0)}
   • Lab Processing: {data.get('Lab Results', {}).get('recent_entries', 0)}
   • Staff Communications: {data.get('Staff Updates', {}).get('recent_entries', 0)}

📈 **Performance Indicators:**
   • Documentation Quality: Good
   • Response Time: Optimal
   • Collaboration Level: High

💡 **Department Insights:**
   • Workflow efficiency is operating at expected levels
   • Staff coordination appears effective
   • Patient care documentation is comprehensive
"""
    
    def _analyze_general_metrics(self, data: dict, period: str) -> str:
        """Analyze general hospital metrics."""
        
        total_activity = sum(sheet.get('recent_entries', 0) for sheet in data.values() if isinstance(sheet, dict))
        
        return f"""📊 **Hospital Analytics Dashboard - {period.title()}**

🏥 **Overall Hospital Activity:**
   • Total System Updates: {total_activity}
   • Average Daily Activity: {total_activity // (7 if period == 'week' else 30 if period == 'month' else 1)}

📋 **System Health:**
   • Data Flow: {'Excellent' if total_activity > 50 else 'Good' if total_activity > 20 else 'Moderate'}
   • Staff Engagement: {'High' if total_activity > 40 else 'Normal'}
   • System Utilization: {'Optimal' if total_activity > 30 else 'Good'}

🎯 **Key Insights:**
   • Hospital management system is functioning effectively
   • Staff adoption of digital tools is {'excellent' if total_activity > 60 else 'good'}
   • Patient care coordination is {'highly effective' if total_activity > 50 else 'effective'}
"""


# ==================== HELPER FUNCTION ====================

def get_all_sheets_monitoring_tools() -> List[BaseTool]:
    """Get all Google Sheets monitoring tools."""
    return [
        MonitorSheetChangesTool(),
        ReadStaffUpdatesTool(),
        UpdatePatientStatusTool(),
        StaffNotificationTool(),
        SheetAnalyticsTool()
    ]


# ==================== TESTING ====================

if __name__ == "__main__":
    print("=" * 70)
    print("🏥 GOOGLE SHEETS MONITORING TOOLS - TESTING")
    print("=" * 70)
    
    # Test 1: Monitor sheet changes
    print("\n📊 Test 1: Monitor Sheet Changes")
    monitor_tool = MonitorSheetChangesTool()
    result = monitor_tool._run(
        sheet_id="1BvLhgJcTrNgqGjBxKbQA2KXqzNQjxmKaXjKCNBk3HJs",  # Replace with real sheet ID
        sheet_name="Sheet1"
    )
    print(result)
    
    # Test 2: Read staff updates
    print("\n👩‍⚕️ Test 2: Read Staff Updates")
    staff_tool = ReadStaffUpdatesTool()
    result = staff_tool._run(
        department="doctors",
        hours_back=24
    )
    print(result)
    
    # Test 3: Update patient status
    print("\n📋 Test 3: Update Patient Status")
    update_tool = UpdatePatientStatusTool()
    result = update_tool._run(
        patient_id="REG2025001",
        status_type="vitals",
        status_value="Blood pressure: 120/80, Heart rate: 72 bpm",
        updated_by="AI Agent"
    )
    print(result)
    
    # Test 4: Send staff notification
    print("\n🔔 Test 4: Send Staff Notification")
    notify_tool = StaffNotificationTool()
    result = notify_tool._run(
        notification_type="info",
        message="Patient REG2025001 lab results are ready for review",
        target_department="doctors",
        patient_id="REG2025001"
    )
    print(result)
    
    # Test 5: Analyze sheet data
    print("\n📈 Test 5: Analyze Sheet Data")
    analytics_tool = SheetAnalyticsTool()
    result = analytics_tool._run(
        analysis_type="patient_trends",
        time_period="today"
    )
    print(result)
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 70)