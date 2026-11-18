"""
Google Calendar Tool for Hospital Management System
Manages doctor appointments, reminders, and scheduling

Features:
- Create appointments with doctors
- Check doctor availability
- Update/reschedule appointments
- Cancel appointments
- List upcoming appointments
- Send appointment reminders
- Integration with hospital workflow stages

Author: Hospital Management AI System
"""

import os
import pickle
from typing import Optional, Type, List, Dict, Any
from datetime import datetime, timedelta
import pytz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from pydantic import BaseModel, Field
from langchain.tools import BaseTool


# ==================== CALENDAR SCOPES ====================
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]


# ==================== INPUT SCHEMAS ====================

class CreateAppointmentInput(BaseModel):
    """Input schema for creating appointments."""
    patient_name: str = Field(description="Patient's full name")
    patient_email: str = Field(description="Patient's email address")
    doctor_name: str = Field(description="Doctor's name")
    doctor_email: str = Field(description="Doctor's email address")
    appointment_date: str = Field(description="Appointment date (YYYY-MM-DD)")
    appointment_time: str = Field(description="Appointment time (HH:MM)")
    duration_minutes: int = Field(default=30, description="Appointment duration in minutes")
    appointment_type: str = Field(default="Consultation", description="Type of appointment")
    notes: Optional[str] = Field(default=None, description="Additional notes")


class CheckAvailabilityInput(BaseModel):
    """Input schema for checking availability."""
    doctor_email: str = Field(description="Doctor's email address")
    date: str = Field(description="Date to check (YYYY-MM-DD)")
    start_time: str = Field(default="09:00", description="Start time (HH:MM)")
    end_time: str = Field(default="17:00", description="End time (HH:MM)")


class UpdateAppointmentInput(BaseModel):
    """Input schema for updating appointments."""
    event_id: str = Field(description="Google Calendar event ID")
    new_date: Optional[str] = Field(default=None, description="New date (YYYY-MM-DD)")
    new_time: Optional[str] = Field(default=None, description="New time (HH:MM)")
    new_duration: Optional[int] = Field(default=None, description="New duration in minutes")
    new_notes: Optional[str] = Field(default=None, description="Updated notes")


class CancelAppointmentInput(BaseModel):
    """Input schema for canceling appointments."""
    event_id: str = Field(description="Google Calendar event ID")
    cancellation_reason: str = Field(description="Reason for cancellation")
    notify_attendees: bool = Field(default=True, description="Send cancellation notification")


class ListAppointmentsInput(BaseModel):
    """Input schema for listing appointments."""
    calendar_id: str = Field(default="primary", description="Calendar ID to query")
    start_date: Optional[str] = Field(default=None, description="Start date filter (YYYY-MM-DD)")
    end_date: Optional[str] = Field(default=None, description="End date filter (YYYY-MM-DD)")
    max_results: int = Field(default=10, description="Maximum number of results")


class SendReminderInput(BaseModel):
    """Input schema for sending appointment reminders."""
    event_id: str = Field(description="Google Calendar event ID")
    reminder_type: str = Field(default="email", description="Reminder type: email, sms, both")
    hours_before: int = Field(default=24, description="Hours before appointment to send reminder")


# ==================== BASE CLASS ====================

class CalendarToolBase:
    """Base class with Google Calendar API connection."""
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'calendar_token.pickle'):
        """Initialize Calendar service."""
        try:
            # Load credentials
            creds = None
            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    creds = pickle.load(token)
            
            # If no valid credentials, authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials
                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)
            
            self.service = build('calendar', 'v3', credentials=creds)
            print(f"✅ Google Calendar service initialized")
            
        except Exception as e:
            print(f"❌ Error initializing Calendar service: {e}")
            self.service = None
    
    def _parse_datetime(self, date_str: str, time_str: str, timezone: str = "Asia/Kolkata") -> str:
        """Parse date and time strings into ISO format."""
        try:
            print(f"🔍 DEBUG _parse_datetime: date_str='{date_str}', time_str='{time_str}'")
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            # Use pytz for better Windows compatibility
            tz = pytz.timezone(timezone)
            dt = tz.localize(dt)
            result = dt.isoformat()
            print(f"✅ Parsed datetime: {result}")
            return result
        except Exception as e:
            print(f"❌ Datetime parsing error: {e}")
            raise ValueError(f"Invalid date/time format: {e}")
    
    def _format_appointment_summary(self, patient_name: str, doctor_name: str, 
                                  appointment_type: str) -> str:
        """Format appointment summary."""
        return f"🩺 {appointment_type}: {patient_name} with Dr. {doctor_name}"
    
    def _create_appointment_description(self, patient_name: str, patient_email: str,
                                      appointment_type: str, notes: str = None) -> str:
        """Create detailed appointment description."""
        description = f"""📋 APPOINTMENT DETAILS

👤 Patient: {patient_name}
📧 Email: {patient_email}
🩺 Type: {appointment_type}

🏥 Hospital Management System
"""
        if notes:
            description += f"\n📝 Notes:\n{notes}"
        
        return description


# ==================== LANGCHAIN TOOLS ====================

class CreateAppointmentTool(BaseTool, CalendarToolBase):
    """Tool for creating doctor appointments."""
    
    name: str = "create_appointment"
    description: str = """Create a doctor appointment in Google Calendar. 
    Schedules appointment, sends invites to patient and doctor, sets reminders."""
    args_schema: Type[BaseModel] = CreateAppointmentInput
    
    service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'calendar_token.pickle'):
        BaseTool.__init__(self)
        CalendarToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, patient_name: str, patient_email: str, doctor_name: str, 
             doctor_email: str, appointment_date: str, appointment_time: str,
             duration_minutes: int = 30, appointment_type: str = "Consultation",
             notes: Optional[str] = None) -> str:
        
        if not self.service:
            return "❌ Error: Calendar service not initialized."
        
        try:
            # Parse start and end times
            start_time = self._parse_datetime(appointment_date, appointment_time)
            
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = start_dt + timedelta(minutes=duration_minutes)
            end_time = end_dt.isoformat()
            
            # Create event
            event = {
                'summary': self._format_appointment_summary(patient_name, doctor_name, appointment_type),
                'description': self._create_appointment_description(
                    patient_name, patient_email, appointment_type, notes
                ),
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'Asia/Kolkata',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'Asia/Kolkata',
                },
                'attendees': [
                    {'email': patient_email, 'displayName': patient_name},
                    {'email': doctor_email, 'displayName': f'Dr. {doctor_name}'},
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 24 hours
                        {'method': 'email', 'minutes': 60},       # 1 hour
                        {'method': 'popup', 'minutes': 15},       # 15 minutes
                    ],
                },
                'colorId': '2',  # Green color for medical appointments
                'location': 'City Hospital, Main Building',
                'status': 'confirmed'
            }
            
            # Insert event
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event,
                sendUpdates='all'
            ).execute()
            
            event_id = created_event.get('id')
            event_link = created_event.get('htmlLink')
            
            return f"""✅ **Appointment Created Successfully!**

📅 **Appointment Details:**
• **Patient:** {patient_name}
• **Doctor:** Dr. {doctor_name}
• **Date:** {appointment_date}
• **Time:** {appointment_time}
• **Duration:** {duration_minutes} minutes
• **Type:** {appointment_type}

🔗 **Calendar Link:** {event_link}
📧 **Event ID:** {event_id}

✅ **Notifications Sent:**
• Invitation sent to {patient_email}
• Invitation sent to {doctor_email}
• Reminders set: 24h, 1h, 15min before

📍 **Location:** City Hospital, Main Building"""
            
        except Exception as e:
            return f"❌ Error creating appointment: {str(e)}"
    
    async def _arun(self, patient_name: str, patient_email: str, doctor_name: str, 
                    doctor_email: str, appointment_date: str, appointment_time: str,
                    duration_minutes: int = 30, appointment_type: str = "Consultation",
                    notes: Optional[str] = None) -> str:
        return self._run(patient_name, patient_email, doctor_name, doctor_email, 
                        appointment_date, appointment_time, duration_minutes, 
                        appointment_type, notes)


class CheckAvailabilityTool(BaseTool, CalendarToolBase):
    """Tool for checking doctor availability."""
    
    name: str = "check_availability"
    description: str = """Check doctor's availability on a specific date and time range. 
    Returns free time slots and existing appointments."""
    args_schema: Type[BaseModel] = CheckAvailabilityInput
    
    service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'calendar_token.pickle'):
        BaseTool.__init__(self)
        CalendarToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, doctor_email: str, date: str, start_time: str = "09:00", 
             end_time: str = "17:00") -> str:
        
        if not self.service:
            return "❌ Error: Calendar service not initialized."
        
        try:
            # Parse date range
            start_datetime = self._parse_datetime(date, start_time)
            end_datetime = self._parse_datetime(date, end_time)
            
            # Get busy times using freebusy query
            freebusy_request = {
                'timeMin': start_datetime,
                'timeMax': end_datetime,
                'items': [{'id': doctor_email}]
            }
            
            freebusy_result = self.service.freebusy().query(body=freebusy_request).execute()
            busy_times = freebusy_result['calendars'].get(doctor_email, {}).get('busy', [])
            
            # Also get actual events for more details
            events_result = self.service.events().list(
                calendarId=doctor_email,
                timeMin=start_datetime,
                timeMax=end_datetime,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Calculate free slots
            free_slots = self._calculate_free_slots(start_datetime, end_datetime, busy_times)
            
            # Format response
            response = f"""📅 **Availability for {date}**
👨‍⚕️ **Doctor:** {doctor_email}
🕒 **Time Range:** {start_time} - {end_time}

"""
            
            if busy_times:
                response += "🔴 **Busy Times:**\n"
                for busy in busy_times:
                    start_busy = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                    end_busy = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                    response += f"• {start_busy.strftime('%H:%M')} - {end_busy.strftime('%H:%M')}\n"
                response += "\n"
            
            if events:
                response += "📋 **Scheduled Appointments:**\n"
                for event in events:
                    event_start = event['start'].get('dateTime', event['start'].get('date'))
                    if event_start:
                        start_dt = datetime.fromisoformat(event_start.replace('Z', '+00:00'))
                        response += f"• {start_dt.strftime('%H:%M')} - {event.get('summary', 'No title')}\n"
                response += "\n"
            
            if free_slots:
                response += "✅ **Available Time Slots:**\n"
                for slot in free_slots:
                    response += f"• {slot}\n"
            else:
                response += "❌ **No available slots in the requested time range.**\n"
            
            return response
            
        except Exception as e:
            return f"❌ Error checking availability: {str(e)}"
    
    def _calculate_free_slots(self, start_datetime: str, end_datetime: str, 
                            busy_times: List[Dict]) -> List[str]:
        """Calculate free time slots based on busy times."""
        try:
            start_dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
            
            # Convert busy times to datetime objects
            busy_periods = []
            for busy in busy_times:
                busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                busy_periods.append((busy_start, busy_end))
            
            # Sort busy periods
            busy_periods.sort(key=lambda x: x[0])
            
            # Find free slots
            free_slots = []
            current_time = start_dt
            
            for busy_start, busy_end in busy_periods:
                if current_time < busy_start:
                    # Free slot before busy period
                    free_slots.append(f"{current_time.strftime('%H:%M')} - {busy_start.strftime('%H:%M')}")
                current_time = max(current_time, busy_end)
            
            # Check for free time after last busy period
            if current_time < end_dt:
                free_slots.append(f"{current_time.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}")
            
            return free_slots
            
        except Exception as e:
            return [f"Error calculating slots: {str(e)}"]
    
    async def _arun(self, doctor_email: str, date: str, start_time: str = "09:00", 
                    end_time: str = "17:00") -> str:
        return self._run(doctor_email, date, start_time, end_time)


class UpdateAppointmentTool(BaseTool, CalendarToolBase):
    """Tool for updating/rescheduling appointments."""
    
    name: str = "update_appointment"
    description: str = """Update or reschedule an existing appointment. 
    Can change date, time, duration, or notes."""
    args_schema: Type[BaseModel] = UpdateAppointmentInput
    
    service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'calendar_token.pickle'):
        BaseTool.__init__(self)
        CalendarToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, event_id: str, new_date: Optional[str] = None, 
             new_time: Optional[str] = None, new_duration: Optional[int] = None,
             new_notes: Optional[str] = None) -> str:
        
        if not self.service:
            return "❌ Error: Calendar service not initialized."
        
        try:
            # Get existing event
            event = self.service.events().get(calendarId='primary', eventId=event_id).execute()
            
            original_summary = event.get('summary', 'Unknown')
            changes_made = []
            
            # Update date and time if provided
            if new_date and new_time:
                new_start_time = self._parse_datetime(new_date, new_time)
                
                # Calculate duration from original event
                original_start = event['start']['dateTime']
                original_end = event['end']['dateTime']
                original_start_dt = datetime.fromisoformat(original_start.replace('Z', '+00:00'))
                original_end_dt = datetime.fromisoformat(original_end.replace('Z', '+00:00'))
                duration = (original_end_dt - original_start_dt).total_seconds() / 60
                
                if new_duration:
                    duration = new_duration
                
                new_start_dt = datetime.fromisoformat(new_start_time.replace('Z', '+00:00'))
                new_end_dt = new_start_dt + timedelta(minutes=int(duration))
                
                event['start']['dateTime'] = new_start_time
                event['end']['dateTime'] = new_end_dt.isoformat()
                
                changes_made.append(f"Date/Time: {new_date} at {new_time}")
            
            # Update duration only if new date/time not provided
            elif new_duration and not (new_date and new_time):
                original_start = event['start']['dateTime']
                start_dt = datetime.fromisoformat(original_start.replace('Z', '+00:00'))
                new_end_dt = start_dt + timedelta(minutes=new_duration)
                event['end']['dateTime'] = new_end_dt.isoformat()
                changes_made.append(f"Duration: {new_duration} minutes")
            
            # Update notes
            if new_notes:
                current_description = event.get('description', '')
                if "📝 Notes:" in current_description:
                    # Replace existing notes
                    parts = current_description.split("📝 Notes:")
                    event['description'] = parts[0].strip() + f"\n\n📝 Notes:\n{new_notes}"
                else:
                    # Add new notes
                    event['description'] = current_description + f"\n\n📝 Notes:\n{new_notes}"
                changes_made.append("Notes updated")
            
            # Update the event
            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event,
                sendUpdates='all'
            ).execute()
            
            return f"""✅ **Appointment Updated Successfully!**

📅 **Event:** {original_summary}
🔗 **Event ID:** {event_id}

📝 **Changes Made:**
{chr(10).join([f'• {change}' for change in changes_made])}

✅ **All attendees have been notified of the changes.**
🔗 **Updated Link:** {updated_event.get('htmlLink')}"""
            
        except HttpError as e:
            if e.resp.status == 404:
                return f"❌ Appointment not found with ID: {event_id}"
            return f"❌ Error updating appointment: {str(e)}"
        except Exception as e:
            return f"❌ Error updating appointment: {str(e)}"
    
    async def _arun(self, event_id: str, new_date: Optional[str] = None, 
                    new_time: Optional[str] = None, new_duration: Optional[int] = None,
                    new_notes: Optional[str] = None) -> str:
        return self._run(event_id, new_date, new_time, new_duration, new_notes)


class CancelAppointmentTool(BaseTool, CalendarToolBase):
    """Tool for canceling appointments."""
    
    name: str = "cancel_appointment"
    description: str = """Cancel an existing appointment. 
    Sends cancellation notifications to all attendees."""
    args_schema: Type[BaseModel] = CancelAppointmentInput
    
    service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'calendar_token.pickle'):
        BaseTool.__init__(self)
        CalendarToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, event_id: str, cancellation_reason: str, 
             notify_attendees: bool = True) -> str:
        
        if not self.service:
            return "❌ Error: Calendar service not initialized."
        
        try:
            # Get event details before canceling
            event = self.service.events().get(calendarId='primary', eventId=event_id).execute()
            
            event_summary = event.get('summary', 'Unknown Event')
            event_start = event['start'].get('dateTime', event['start'].get('date'))
            attendees = event.get('attendees', [])
            
            # Update event with cancellation info
            event['summary'] = f"[CANCELLED] {event_summary}"
            event['description'] = event.get('description', '') + f"""

🚫 **APPOINTMENT CANCELLED**
📝 Reason: {cancellation_reason}
🕒 Cancelled on: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Please contact the hospital to reschedule if needed.
"""
            event['status'] = 'cancelled'
            event['colorId'] = '4'  # Red color for cancelled
            
            # Update the event first (to add cancellation info)
            self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event,
                sendUpdates='all' if notify_attendees else 'none'
            ).execute()
            
            # Format start time for display
            if event_start:
                start_dt = datetime.fromisoformat(event_start.replace('Z', '+00:00'))
                formatted_time = start_dt.strftime('%Y-%m-%d at %H:%M')
            else:
                formatted_time = "Unknown time"
            
            # Get attendee list
            attendee_list = ", ".join([att.get('email', 'Unknown') for att in attendees])
            
            return f"""✅ **Appointment Cancelled Successfully!**

📅 **Cancelled Event:** {event_summary}
🕒 **Original Time:** {formatted_time}
📝 **Reason:** {cancellation_reason}
🔗 **Event ID:** {event_id}

{'✅ **Cancellation notifications sent to all attendees:**' if notify_attendees else '❌ **No notifications sent (as requested):**'}
{attendee_list}

💡 **The appointment has been marked as cancelled in the calendar.**
📞 **Attendees can contact the hospital to reschedule if needed.**"""
            
        except HttpError as e:
            if e.resp.status == 404:
                return f"❌ Appointment not found with ID: {event_id}"
            return f"❌ Error cancelling appointment: {str(e)}"
        except Exception as e:
            return f"❌ Error cancelling appointment: {str(e)}"
    
    async def _arun(self, event_id: str, cancellation_reason: str, 
                    notify_attendees: bool = True) -> str:
        return self._run(event_id, cancellation_reason, notify_attendees)


class ListAppointmentsTool(BaseTool, CalendarToolBase):
    """Tool for listing upcoming appointments."""
    
    name: str = "list_appointments"
    description: str = """List upcoming appointments from Google Calendar. 
    Can filter by date range and limit results."""
    args_schema: Type[BaseModel] = ListAppointmentsInput
    
    service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'calendar_token.pickle'):
        BaseTool.__init__(self)
        CalendarToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, calendar_id: str = "primary", start_date: Optional[str] = None,
             end_date: Optional[str] = None, max_results: int = 10) -> str:
        
        if not self.service:
            return "❌ Error: Calendar service not initialized."
        
        try:
            # Set default time range if not provided
            if not start_date:
                start_date = datetime.now().strftime('%Y-%m-%d')
            
            if not end_date:
                end_dt = datetime.now() + timedelta(days=30)
                end_date = end_dt.strftime('%Y-%m-%d')
            
            # Parse date range
            time_min = self._parse_datetime(start_date, "00:00")
            time_max = self._parse_datetime(end_date, "23:59")
            
            # Get events
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                return f"""📅 **No appointments found**

🔍 **Search Criteria:**
• Calendar: {calendar_id}
• Date Range: {start_date} to {end_date}
• Max Results: {max_results}

💡 **Try expanding the date range or checking a different calendar.**"""
            
            # Format response
            response = f"""📅 **Upcoming Appointments**

🔍 **Search Criteria:**
• Date Range: {start_date} to {end_date}
• Total Found: {len(events)}

📋 **Appointment List:**

"""
            
            for i, event in enumerate(events, 1):
                # Get event details
                summary = event.get('summary', 'No Title')
                event_id = event.get('id', 'Unknown')
                
                # Get start time
                start = event['start'].get('dateTime', event['start'].get('date'))
                if start:
                    if 'T' in start:  # DateTime format
                        start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                        formatted_start = start_dt.strftime('%Y-%m-%d at %H:%M')
                    else:  # Date only format
                        formatted_start = f"{start} (All day)"
                else:
                    formatted_start = "Unknown time"
                
                # Get end time
                end = event['end'].get('dateTime', event['end'].get('date'))
                if end and 'T' in end:
                    end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                    duration = end_dt - datetime.fromisoformat(start.replace('Z', '+00:00'))
                    duration_mins = int(duration.total_seconds() / 60)
                    duration_text = f" ({duration_mins} min)"
                else:
                    duration_text = ""
                
                # Get attendees
                attendees = event.get('attendees', [])
                attendee_count = len(attendees)
                
                # Get status
                status = event.get('status', 'confirmed')
                status_emoji = {
                    'confirmed': '✅',
                    'tentative': '⏳',
                    'cancelled': '❌'
                }.get(status, '❓')
                
                response += f"""**{i}. {summary}**
   📅 {formatted_start}{duration_text}
   👥 {attendee_count} attendee(s)
   {status_emoji} Status: {status.title()}
   🔗 ID: {event_id}

"""
            
            return response.strip()
            
        except Exception as e:
            return f"❌ Error listing appointments: {str(e)}"
    
    async def _arun(self, calendar_id: str = "primary", start_date: Optional[str] = None,
                    end_date: Optional[str] = None, max_results: int = 10) -> str:
        return self._run(calendar_id, start_date, end_date, max_results)


# ==================== HELPER FUNCTIONS ====================

def get_all_calendar_tools(credentials_file: str = 'credentials/client_secret.json', 
                          token_file: str = 'calendar_token.pickle') -> List[BaseTool]:
    """Get all Calendar tools for hospital workflow."""
    return [
        CreateAppointmentTool(credentials_file, token_file),
        CheckAvailabilityTool(credentials_file, token_file),
        UpdateAppointmentTool(credentials_file, token_file),
        CancelAppointmentTool(credentials_file, token_file),
        ListAppointmentsTool(credentials_file, token_file),
    ]


# ==================== TESTING ====================

if __name__ == "__main__":
    print("=" * 60)
    print("GOOGLE CALENDAR TOOL TESTING")
    print("=" * 60)
    
    # Test 1: Create appointment
    print("\n📅 Test 1: Creating appointment...")
    create_tool = CreateAppointmentTool()
    
    # Test with sample data
    result = create_tool._run(
        patient_name="Alice Johnson",
        patient_email="alice@example.com",
        doctor_name="Sarah Williams",
        doctor_email="doctor@hospital.com",
        appointment_date="2025-10-30",
        appointment_time="14:00",
        duration_minutes=45,
        appointment_type="Follow-up Consultation",
        notes="Patient needs to discuss test results and medication adjustment."
    )
    print(result)
    
    # Test 2: Check availability
    print("\n🔍 Test 2: Checking availability...")
    availability_tool = CheckAvailabilityTool()
    
    result = availability_tool._run(
        doctor_email="doctor@hospital.com",
        date="2025-10-30",
        start_time="09:00",
        end_time="17:00"
    )
    print(result)
    
    # Test 3: List appointments
    print("\n📋 Test 3: Listing appointments...")
    list_tool = ListAppointmentsTool()
    
    result = list_tool._run(
        start_date="2025-10-29",
        end_date="2025-11-05",
        max_results=5
    )
    print(result)
    
    print("\n" + "=" * 60)
    print("✅ CALENDAR TOOL TESTING COMPLETED!")
    print("=" * 60)