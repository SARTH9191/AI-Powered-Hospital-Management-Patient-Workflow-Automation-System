"""
Notification System Tools
Handles email, SMS, and in-app notifications with templates and user preferences
"""

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from datetime import datetime, timedelta
import json
import os

# Database file paths
NOTIFICATIONS_DB_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'notifications_database.json')
NOTIFICATION_PREFERENCES_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'notification_preferences.json')
PATIENTS_DB_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'patients_database.json')

# Notification templates
NOTIFICATION_TEMPLATES = {
    'appointment_reminder': {
        'subject': '🏥 Appointment Reminder - {hospital_name}',
        'body': """
Dear {patient_name},

This is a friendly reminder about your upcoming appointment:

📅 Date: {appointment_date}
🕐 Time: {appointment_time}
👨‍⚕️ Doctor: Dr. {doctor_name}
🏥 Specialty: {specialty}
📍 Location: {location}

Please arrive 15 minutes early for check-in.

If you need to reschedule or cancel, please contact us at least 24 hours in advance.

Thank you,
{hospital_name}
        """,
        'priority': 'medium'
    },
    'critical_results': {
        'subject': '🚨 URGENT: Critical Lab Results - Immediate Attention Required',
        'body': """
CRITICAL ALERT

Patient: {patient_name}
Patient ID: {patient_id}

Critical lab results detected that require immediate attention:

Test: {test_name}
Results: {critical_values}
Status: 🚨 CRITICAL

Action Required:
- Doctor has been notified
- Please contact your doctor immediately
- Follow-up appointment may be scheduled

For urgent matters, please visit the emergency department.

Hospital Contact: {hospital_contact}
        """,
        'priority': 'urgent'
    },
    'approval_request': {
        'subject': '⚠️ Action Required: Approval Request - {request_type}',
        'body': """
Dear Admin,

A new approval request requires your attention:

Request Type: {request_type}
Priority: {priority}
Requested By: {requester}
Date: {request_date}

Details:
{request_details}

Please review and approve/reject this request in the admin dashboard.

Login to dashboard: {dashboard_url}

Thank you,
Hospital Management System
        """,
        'priority': 'high'
    },
    'billing_reminder': {
        'subject': '💰 Payment Reminder - Invoice Due',
        'body': """
Dear {patient_name},

This is a reminder about your outstanding invoice:

Invoice ID: {invoice_id}
Amount Due: ${amount_due}
Due Date: {due_date}
Days Overdue: {days_overdue}

Please make payment at your earliest convenience.

Payment Methods:
- Online: {payment_url}
- Phone: {hospital_phone}
- In-person: Visit our billing department

If you have already made payment, please disregard this notice.

Thank you,
Billing Department
{hospital_name}
        """,
        'priority': 'medium'
    },
    'prescription_refill': {
        'subject': '💊 Prescription Refill Reminder',
        'body': """
Dear {patient_name},

Your prescription is due for a refill soon:

Medication: {medication_name}
Dosage: {dosage}
Refills Remaining: {refills_remaining}
Last Fill Date: {last_fill_date}

Please contact your pharmacy or doctor to arrange a refill.

If no refills remain, you may need to schedule an appointment with your doctor.

Hospital Pharmacy: {pharmacy_phone}

Stay healthy,
{hospital_name}
        """,
        'priority': 'low'
    },
    'appointment_confirmation': {
        'subject': '✅ Appointment Confirmed - {hospital_name}',
        'body': """
Dear {patient_name},

Your appointment has been confirmed:

📅 Date: {appointment_date}
🕐 Time: {appointment_time}
👨‍⚕️ Doctor: Dr. {doctor_name}
📋 Appointment ID: {appointment_id}

We look forward to seeing you!

{hospital_name}
        """,
        'priority': 'medium'
    },
    'test_results_ready': {
        'subject': '📋 Lab Results Available',
        'body': """
Dear {patient_name},

Your lab test results are now available:

Test: {test_name}
Test Date: {test_date}
Status: {status}

You can view your results by:
- Logging into the patient portal
- Calling our office at {hospital_phone}
- Scheduling a follow-up appointment

{hospital_name}
        """,
        'priority': 'medium'
    },
    'welcome': {
        'subject': '🎉 Welcome to {hospital_name}',
        'body': """
Dear {patient_name},

Welcome to {hospital_name}! We're glad to have you as a patient.

Your registration is complete:
Patient ID: {patient_id}
Registration Date: {registration_date}

You can now:
✅ Schedule appointments online
✅ View your medical records
✅ Access lab results
✅ Request prescription refills

Patient Portal: {portal_url}

If you have any questions, please don't hesitate to contact us.

Best regards,
{hospital_name}
        """,
        'priority': 'low'
    }
}

def load_db(file_path):
    """Load database from JSON file"""
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict) and 'data' in data:
                return data['data']
            return data if isinstance(data, list) else []
    return []

def save_db(file_path, data):
    """Save database to JSON file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def generate_notification_id():
    """Generate unique notification ID"""
    import random
    return f"NOTIF{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100, 999)}"

# ==================== TOOL 1: Send Notification ====================

class SendNotificationInput(BaseModel):
    recipient_id: str = Field(description="Patient ID or user ID to send notification to")
    notification_type: Literal["appointment_reminder", "critical_results", "approval_request", 
                               "billing_reminder", "prescription_refill", "appointment_confirmation",
                               "test_results_ready", "welcome", "custom"] = Field(description="Type of notification")
    channel: List[Literal["email", "sms", "in_app"]] = Field(description="Notification channels to use")
    template_data: dict = Field(description="Data to fill in the template (e.g., {'patient_name': 'John', 'appointment_date': '2025-10-20'})")
    custom_subject: Optional[str] = Field(default=None, description="Custom subject (for custom notifications)")
    custom_body: Optional[str] = Field(default=None, description="Custom body (for custom notifications)")
    priority: Optional[Literal["low", "medium", "high", "urgent"]] = Field(default=None, description="Override default priority")

class SendNotificationTool(BaseTool):
    name: str = "send_notification"
    description: str = """Send a notification to a patient or user via email, SMS, or in-app channels. 
    Uses pre-defined templates for common notification types or allows custom messages."""
    args_schema: type[BaseModel] = SendNotificationInput
    
    def _run(self, recipient_id: str, notification_type: str, channel: List[str], 
             template_data: dict, custom_subject: Optional[str] = None, 
             custom_body: Optional[str] = None, priority: Optional[str] = None) -> dict:
        """Send notification to recipient"""
        
        try:
            # Load databases
            patients = load_db(PATIENTS_DB_FILE)
            notifications = load_db(NOTIFICATIONS_DB_FILE)
            preferences = load_db(NOTIFICATION_PREFERENCES_FILE)
            
            # Find recipient
            recipient = next((p for p in patients if p.get('patient_id') == recipient_id), None)
            if not recipient:
                return {'success': False, 'message': f'Recipient {recipient_id} not found'}
            
            # Check user preferences
            user_prefs = next((p for p in preferences if p.get('user_id') == recipient_id), None)
            if user_prefs:
                # Filter channels based on user preferences
                allowed_channels = []
                if user_prefs.get('email_enabled', True) and 'email' in channel:
                    allowed_channels.append('email')
                if user_prefs.get('sms_enabled', True) and 'sms' in channel:
                    allowed_channels.append('sms')
                if user_prefs.get('in_app_enabled', True) and 'in_app' in channel:
                    allowed_channels.append('in_app')
                channel = allowed_channels if allowed_channels else ['in_app']  # Default to in-app if all disabled
            
            # Get template or use custom
            if notification_type == 'custom':
                if not custom_subject or not custom_body:
                    return {'success': False, 'message': 'Custom notifications require subject and body'}
                subject = custom_subject
                body = custom_body
                default_priority = priority or 'medium'
            else:
                template = NOTIFICATION_TEMPLATES.get(notification_type)
                if not template:
                    return {'success': False, 'message': f'Unknown notification type: {notification_type}'}
                
                # Fill in template with data
                try:
                    subject = template['subject'].format(**template_data)
                    body = template['body'].format(**template_data)
                    default_priority = priority or template['priority']
                except KeyError as e:
                    return {'success': False, 'message': f'Missing template data: {str(e)}'}
            
            # Create notification record
            notification = {
                'notification_id': generate_notification_id(),
                'recipient_id': recipient_id,
                'recipient_name': recipient.get('name', 'Unknown'),
                'recipient_email': recipient.get('email', ''),
                'recipient_phone': recipient.get('phone', ''),
                'notification_type': notification_type,
                'channels': channel,
                'subject': subject,
                'body': body,
                'priority': default_priority,
                'status': 'sent',
                'sent_date': datetime.now().strftime('%Y-%m-%d'),
                'sent_time': datetime.now().strftime('%H:%M:%S'),
                'sent_timestamp': datetime.now().isoformat(),
                'delivery_status': {},
                'template_data': template_data,
                'created_at': datetime.now().isoformat()
            }
            
            # Simulate sending through each channel
            delivery_results = []
            
            if 'email' in channel and recipient.get('email'):
                # In real system, integrate with Gmail API
                notification['delivery_status']['email'] = 'delivered'
                delivery_results.append(f"✅ Email sent to {recipient.get('email')}")
            
            if 'sms' in channel and recipient.get('phone'):
                # In real system, integrate with SMS service (Twilio, etc.)
                notification['delivery_status']['sms'] = 'delivered'
                delivery_results.append(f"✅ SMS sent to {recipient.get('phone')}")
            
            if 'in_app' in channel:
                notification['delivery_status']['in_app'] = 'delivered'
                delivery_results.append(f"✅ In-app notification created")
            
            # Save notification
            notifications.append(notification)
            save_db(NOTIFICATIONS_DB_FILE, notifications)
            
            # Format output
            priority_emoji = {
                'low': '🔵',
                'medium': '🟡',
                'high': '🟠',
                'urgent': '🔴'
            }
            
            output = f"\n{'='*60}\n"
            output += f"📧 NOTIFICATION SENT\n"
            output += f"{'='*60}\n\n"
            output += f"🆔 Notification ID: {notification['notification_id']}\n"
            output += f"👤 Recipient: {notification['recipient_name']} ({recipient_id})\n"
            output += f"📋 Type: {notification_type}\n"
            output += f"{priority_emoji.get(default_priority, '⚪')} Priority: {default_priority.upper()}\n"
            output += f"📅 Sent: {notification['sent_date']} {notification['sent_time']}\n"
            output += f"\n{'='*60}\n"
            output += f"DELIVERY STATUS\n"
            output += f"{'='*60}\n\n"
            
            for result in delivery_results:
                output += f"{result}\n"
            
            output += f"\n{'='*60}\n"
            output += f"MESSAGE PREVIEW\n"
            output += f"{'='*60}\n\n"
            output += f"Subject: {subject}\n\n"
            output += f"{body[:200]}{'...' if len(body) > 200 else ''}\n"
            output += f"{'='*60}\n"
            
            return {
                'success': True,
                'message': output,
                'notification': notification
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error sending notification: {str(e)}'}

# ==================== TOOL 2: Send Bulk Notification ====================

class SendBulkNotificationInput(BaseModel):
    recipient_ids: List[str] = Field(description="List of patient/user IDs to send notification to")
    notification_type: Literal["appointment_reminder", "billing_reminder", "prescription_refill", 
                               "test_results_ready", "welcome", "custom"] = Field(description="Type of notification")
    channel: List[Literal["email", "sms", "in_app"]] = Field(description="Notification channels to use")
    template_data_list: List[dict] = Field(description="List of template data for each recipient (must match recipient_ids order)")
    custom_subject: Optional[str] = Field(default=None, description="Custom subject (for custom notifications)")
    custom_body: Optional[str] = Field(default=None, description="Custom body template (for custom notifications)")

class SendBulkNotificationTool(BaseTool):
    name: str = "send_bulk_notification"
    description: str = """Send notifications to multiple recipients at once. Useful for appointment reminders, 
    billing reminders, or announcements. Each recipient can have personalized template data."""
    args_schema: type[BaseModel] = SendBulkNotificationInput
    
    def _run(self, recipient_ids: List[str], notification_type: str, channel: List[str], 
             template_data_list: List[dict], custom_subject: Optional[str] = None, 
             custom_body: Optional[str] = None) -> dict:
        """Send bulk notifications"""
        
        try:
            if len(recipient_ids) != len(template_data_list):
                return {'success': False, 'message': 'Number of recipients must match number of template data items'}
            
            # Use the single notification tool for each recipient
            send_tool = SendNotificationTool()
            
            results = {
                'total': len(recipient_ids),
                'successful': 0,
                'failed': 0,
                'notifications': []
            }
            
            for i, recipient_id in enumerate(recipient_ids):
                result = send_tool._run(
                    recipient_id=recipient_id,
                    notification_type=notification_type,
                    channel=channel,
                    template_data=template_data_list[i],
                    custom_subject=custom_subject,
                    custom_body=custom_body
                )
                
                if result['success']:
                    results['successful'] += 1
                    results['notifications'].append(result['notification']['notification_id'])
                else:
                    results['failed'] += 1
            
            # Format output
            output = f"\n{'='*60}\n"
            output += f"📢 BULK NOTIFICATION SENT\n"
            output += f"{'='*60}\n\n"
            output += f"📋 Type: {notification_type}\n"
            output += f"📊 Total Recipients: {results['total']}\n"
            output += f"✅ Successful: {results['successful']}\n"
            output += f"❌ Failed: {results['failed']}\n"
            output += f"📱 Channels: {', '.join(channel)}\n"
            output += f"⏰ Sent: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            output += f"\n{'='*60}\n"
            output += f"NOTIFICATION IDS\n"
            output += f"{'='*60}\n\n"
            
            for notif_id in results['notifications'][:10]:  # Show first 10
                output += f"• {notif_id}\n"
            
            if len(results['notifications']) > 10:
                output += f"... and {len(results['notifications']) - 10} more\n"
            
            output += f"\n{'='*60}\n"
            
            success_rate = (results['successful'] / results['total'] * 100) if results['total'] > 0 else 0
            output += f"📊 Success Rate: {success_rate:.1f}%\n"
            output += f"{'='*60}\n"
            
            return {
                'success': True,
                'message': output,
                'results': results
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error sending bulk notifications: {str(e)}'}

# ==================== TOOL 3: Get Notification History ====================

class GetNotificationHistoryInput(BaseModel):
    recipient_id: Optional[str] = Field(default=None, description="Filter by recipient ID (patient/user)")
    notification_type: Optional[str] = Field(default=None, description="Filter by notification type")
    channel: Optional[str] = Field(default=None, description="Filter by channel (email, sms, in_app)")
    priority: Optional[str] = Field(default=None, description="Filter by priority")
    days: int = Field(default=30, description="Number of days to look back (default 30)")
    limit: int = Field(default=50, description="Maximum number of notifications to return")

class GetNotificationHistoryTool(BaseTool):
    name: str = "get_notification_history"
    description: str = """Retrieve notification history with optional filters. Shows sent notifications, 
    delivery status, and allows filtering by recipient, type, channel, priority, and date range."""
    args_schema: type[BaseModel] = GetNotificationHistoryInput
    
    def _run(self, recipient_id: Optional[str] = None, notification_type: Optional[str] = None, 
             channel: Optional[str] = None, priority: Optional[str] = None, 
             days: int = 30, limit: int = 50) -> dict:
        """Get notification history with filters"""
        
        try:
            # Load notifications
            notifications = load_db(NOTIFICATIONS_DB_FILE)
            
            if not notifications:
                return {
                    'success': True,
                    'message': 'No notifications found in history.',
                    'notifications': []
                }
            
            # Calculate date cutoff
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # Filter notifications
            filtered = [n for n in notifications if n.get('sent_date', '9999-99-99') >= cutoff_date]
            
            if recipient_id:
                filtered = [n for n in filtered if n.get('recipient_id') == recipient_id]
            
            if notification_type:
                filtered = [n for n in filtered if n.get('notification_type') == notification_type]
            
            if channel:
                filtered = [n for n in filtered if channel in n.get('channels', [])]
            
            if priority:
                filtered = [n for n in filtered if n.get('priority') == priority]
            
            # Sort by date (most recent first)
            filtered.sort(key=lambda x: x.get('sent_timestamp', ''), reverse=True)
            
            # Limit results
            filtered = filtered[:limit]
            
            # Calculate statistics
            total_count = len(filtered)
            type_counts = {}
            channel_counts = {}
            priority_counts = {}
            
            for notif in filtered:
                # Count by type
                ntype = notif.get('notification_type', 'unknown')
                type_counts[ntype] = type_counts.get(ntype, 0) + 1
                
                # Count by channel
                for ch in notif.get('channels', []):
                    channel_counts[ch] = channel_counts.get(ch, 0) + 1
                
                # Count by priority
                prio = notif.get('priority', 'unknown')
                priority_counts[prio] = priority_counts.get(prio, 0) + 1
            
            # Format output
            output = f"\n{'='*60}\n"
            output += f"📜 NOTIFICATION HISTORY\n"
            output += f"{'='*60}\n\n"
            output += f"📅 Period: Last {days} days\n"
            output += f"📊 Total Notifications: {total_count}\n"
            
            if recipient_id:
                output += f"👤 Filtered by Recipient: {recipient_id}\n"
            if notification_type:
                output += f"📋 Filtered by Type: {notification_type}\n"
            if channel:
                output += f"📱 Filtered by Channel: {channel}\n"
            if priority:
                output += f"⚡ Filtered by Priority: {priority}\n"
            
            output += f"\n{'='*60}\n"
            output += f"STATISTICS\n"
            output += f"{'='*60}\n\n"
            
            output += "By Type:\n"
            for ntype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_count * 100) if total_count > 0 else 0
                output += f"  • {ntype}: {count} ({percentage:.1f}%)\n"
            
            output += "\nBy Channel:\n"
            for ch, count in sorted(channel_counts.items(), key=lambda x: x[1], reverse=True):
                output += f"  • {ch}: {count}\n"
            
            output += "\nBy Priority:\n"
            priority_order = ['urgent', 'high', 'medium', 'low']
            for prio in priority_order:
                if prio in priority_counts:
                    count = priority_counts[prio]
                    percentage = (count / total_count * 100) if total_count > 0 else 0
                    emoji = {'urgent': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🔵'}.get(prio, '⚪')
                    output += f"  {emoji} {prio}: {count} ({percentage:.1f}%)\n"
            
            output += f"\n{'='*60}\n"
            output += f"RECENT NOTIFICATIONS (Showing {min(10, total_count)})\n"
            output += f"{'='*60}\n\n"
            
            for notif in filtered[:10]:
                priority_emoji = {
                    'low': '🔵',
                    'medium': '🟡',
                    'high': '🟠',
                    'urgent': '🔴'
                }.get(notif.get('priority', 'medium'), '⚪')
                
                output += f"{priority_emoji} {notif.get('notification_id')}\n"
                output += f"   To: {notif.get('recipient_name', 'Unknown')} ({notif.get('recipient_id', 'N/A')})\n"
                output += f"   Type: {notif.get('notification_type')} | Channels: {', '.join(notif.get('channels', []))}\n"
                output += f"   Sent: {notif.get('sent_date')} {notif.get('sent_time')}\n"
                output += f"   Subject: {notif.get('subject', 'N/A')[:50]}...\n\n"
            
            if total_count > 10:
                output += f"... and {total_count - 10} more notifications\n\n"
            
            output += f"{'='*60}\n"
            
            return {
                'success': True,
                'message': output,
                'statistics': {
                    'total_count': total_count,
                    'type_counts': type_counts,
                    'channel_counts': channel_counts,
                    'priority_counts': priority_counts
                },
                'notifications': filtered
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error retrieving notification history: {str(e)}'}

# ==================== TOOL 4: Update Notification Preferences ====================

class UpdateNotificationPreferencesInput(BaseModel):
    user_id: str = Field(description="Patient/user ID to update preferences for")
    email_enabled: Optional[bool] = Field(default=None, description="Enable/disable email notifications")
    sms_enabled: Optional[bool] = Field(default=None, description="Enable/disable SMS notifications")
    in_app_enabled: Optional[bool] = Field(default=None, description="Enable/disable in-app notifications")
    appointment_reminders: Optional[bool] = Field(default=None, description="Enable/disable appointment reminders")
    billing_reminders: Optional[bool] = Field(default=None, description="Enable/disable billing reminders")
    lab_results: Optional[bool] = Field(default=None, description="Enable/disable lab result notifications")
    prescription_refills: Optional[bool] = Field(default=None, description="Enable/disable prescription refill reminders")
    quiet_hours_start: Optional[str] = Field(default=None, description="Quiet hours start time (HH:MM format, e.g., '22:00')")
    quiet_hours_end: Optional[str] = Field(default=None, description="Quiet hours end time (HH:MM format, e.g., '08:00')")

class UpdateNotificationPreferencesTool(BaseTool):
    name: str = "update_notification_preferences"
    description: str = """Update user's notification preferences. Allows users to control which channels they receive 
    notifications through, what types of notifications they want, and set quiet hours."""
    args_schema: type[BaseModel] = UpdateNotificationPreferencesInput
    
    def _run(self, user_id: str, email_enabled: Optional[bool] = None, sms_enabled: Optional[bool] = None,
             in_app_enabled: Optional[bool] = None, appointment_reminders: Optional[bool] = None,
             billing_reminders: Optional[bool] = None, lab_results: Optional[bool] = None,
             prescription_refills: Optional[bool] = None, quiet_hours_start: Optional[str] = None,
             quiet_hours_end: Optional[str] = None) -> dict:
        """Update notification preferences for a user"""
        
        try:
            # Load preferences
            preferences = load_db(NOTIFICATION_PREFERENCES_FILE)
            
            # Find or create user preferences
            user_prefs = next((p for p in preferences if p.get('user_id') == user_id), None)
            
            if not user_prefs:
                # Create new preferences with defaults
                user_prefs = {
                    'user_id': user_id,
                    'email_enabled': True,
                    'sms_enabled': True,
                    'in_app_enabled': True,
                    'appointment_reminders': True,
                    'billing_reminders': True,
                    'lab_results': True,
                    'prescription_refills': True,
                    'quiet_hours_start': None,
                    'quiet_hours_end': None,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                preferences.append(user_prefs)
            
            # Update preferences (only update provided values)
            updates = []
            
            if email_enabled is not None:
                user_prefs['email_enabled'] = email_enabled
                updates.append(f"Email: {'Enabled' if email_enabled else 'Disabled'}")
            
            if sms_enabled is not None:
                user_prefs['sms_enabled'] = sms_enabled
                updates.append(f"SMS: {'Enabled' if sms_enabled else 'Disabled'}")
            
            if in_app_enabled is not None:
                user_prefs['in_app_enabled'] = in_app_enabled
                updates.append(f"In-App: {'Enabled' if in_app_enabled else 'Disabled'}")
            
            if appointment_reminders is not None:
                user_prefs['appointment_reminders'] = appointment_reminders
                updates.append(f"Appointment Reminders: {'Enabled' if appointment_reminders else 'Disabled'}")
            
            if billing_reminders is not None:
                user_prefs['billing_reminders'] = billing_reminders
                updates.append(f"Billing Reminders: {'Enabled' if billing_reminders else 'Disabled'}")
            
            if lab_results is not None:
                user_prefs['lab_results'] = lab_results
                updates.append(f"Lab Results: {'Enabled' if lab_results else 'Disabled'}")
            
            if prescription_refills is not None:
                user_prefs['prescription_refills'] = prescription_refills
                updates.append(f"Prescription Refills: {'Enabled' if prescription_refills else 'Disabled'}")
            
            if quiet_hours_start is not None:
                user_prefs['quiet_hours_start'] = quiet_hours_start
                updates.append(f"Quiet Hours Start: {quiet_hours_start}")
            
            if quiet_hours_end is not None:
                user_prefs['quiet_hours_end'] = quiet_hours_end
                updates.append(f"Quiet Hours End: {quiet_hours_end}")
            
            user_prefs['updated_at'] = datetime.now().isoformat()
            
            # Save preferences
            save_db(NOTIFICATION_PREFERENCES_FILE, preferences)
            
            # Format output
            output = f"\n{'='*60}\n"
            output += f"⚙️ NOTIFICATION PREFERENCES UPDATED\n"
            output += f"{'='*60}\n\n"
            output += f"👤 User ID: {user_id}\n"
            output += f"📅 Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            output += f"\n{'='*60}\n"
            output += f"UPDATED SETTINGS\n"
            output += f"{'='*60}\n\n"
            
            for update in updates:
                output += f"✅ {update}\n"
            
            output += f"\n{'='*60}\n"
            output += f"CURRENT PREFERENCES\n"
            output += f"{'='*60}\n\n"
            
            output += "Channels:\n"
            output += f"  📧 Email: {'✅ Enabled' if user_prefs['email_enabled'] else '❌ Disabled'}\n"
            output += f"  📱 SMS: {'✅ Enabled' if user_prefs['sms_enabled'] else '❌ Disabled'}\n"
            output += f"  🔔 In-App: {'✅ Enabled' if user_prefs['in_app_enabled'] else '❌ Disabled'}\n"
            
            output += "\nNotification Types:\n"
            output += f"  📅 Appointment Reminders: {'✅ Enabled' if user_prefs['appointment_reminders'] else '❌ Disabled'}\n"
            output += f"  💰 Billing Reminders: {'✅ Enabled' if user_prefs['billing_reminders'] else '❌ Disabled'}\n"
            output += f"  🧪 Lab Results: {'✅ Enabled' if user_prefs['lab_results'] else '❌ Disabled'}\n"
            output += f"  💊 Prescription Refills: {'✅ Enabled' if user_prefs['prescription_refills'] else '❌ Disabled'}\n"
            
            if user_prefs['quiet_hours_start'] or user_prefs['quiet_hours_end']:
                output += "\nQuiet Hours:\n"
                output += f"  🌙 Start: {user_prefs['quiet_hours_start'] or 'Not set'}\n"
                output += f"  🌅 End: {user_prefs['quiet_hours_end'] or 'Not set'}\n"
            
            output += f"\n{'='*60}\n"
            
            return {
                'success': True,
                'message': output,
                'preferences': user_prefs
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error updating notification preferences: {str(e)}'}

# Export all tools
__all__ = [
    'SendNotificationTool',
    'SendBulkNotificationTool',
    'GetNotificationHistoryTool',
    'UpdateNotificationPreferencesTool'
]
