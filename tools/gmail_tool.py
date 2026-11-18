"""
Complete Gmail Tool for Hospital Management System
Uses OAuth 2.0 for hospital Gmail account (pawarsamarth786@gmail.com)
Sends and receives emails for all patients
"""

import os
import pickle
import base64
from typing import Optional, Type, List, Dict
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from pydantic import BaseModel, Field
from langchain.tools import BaseTool


# ==================== GMAIL SCOPES ====================
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]


# ==================== AUTHENTICATION ====================

def authenticate_gmail(credentials_file: str = 'credentials\client_secret.json', 
                       token_file: str = 'token.pickle'):
    """
    Authenticate hospital Gmail account.
    Run this ONCE to set up authentication.
    
    Steps:
    1. Place your client_secret.json (downloaded from Google Cloud Console) in project root
    2. Run this function
    3. Browser will open for Gmail login
    4. Login with pawarsamarth786@gmail.com
    5. Grant permissions
    6. token.pickle will be created and saved
    
    Returns:
        credentials object for Gmail API
    """
    creds = None
    
    # Check if token already exists
    if os.path.exists(token_file):
        print("📂 Loading saved credentials...")
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("🔐 Starting OAuth authentication...")
            print("📧 Please login with: pawarsamarth786@gmail.com")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
            print("✅ Authentication successful!")
        
        # Save credentials for future use
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
            print(f"💾 Credentials saved to {token_file}")
    
    return creds


# ==================== INPUT SCHEMAS ====================

class GmailSendInput(BaseModel):
    """Input schema for sending basic Gmail."""
    to: str = Field(description="Recipient email address")
    subject: str = Field(description="Email subject line")
    message: str = Field(description="Email message body (can include HTML)")
    cc: Optional[str] = Field(default=None, description="CC email address")


class ReadEmailsInput(BaseModel):
    """Input for reading emails."""
    folder: str = Field(default="INBOX", description="Email folder to read")
    unread_only: bool = Field(default=True, description="Only fetch unread emails")
    limit: int = Field(default=10, description="Maximum number of emails to fetch")


class SearchEmailsInput(BaseModel):
    """Input for searching emails."""
    from_email: Optional[str] = Field(default=None, description="Filter by sender email")
    subject_contains: Optional[str] = Field(default=None, description="Search in subject")
    limit: int = Field(default=10, description="Maximum results")


class LabTestEmailInput(BaseModel):
    """Input for lab test emails."""
    to: str = Field(description="Patient email address")
    patient_name: str = Field(description="Patient full name")
    tests: List[str] = Field(description="List of tests to be conducted")
    appointment_date: str = Field(description="Appointment date")
    appointment_time: str = Field(description="Appointment time")
    location: str = Field(description="Lab location")


class ResultsEmailInput(BaseModel):
    """Input for test results emails."""
    to: str = Field(description="Patient email address")
    patient_name: str = Field(description="Patient full name")
    test_date: str = Field(description="Date tests were conducted")
    results_summary: str = Field(description="Summary of test results")
    is_normal: bool = Field(description="Whether results are normal or require attention")
    doctor_notes: Optional[str] = Field(default=None, description="Doctor's additional notes")


class AdmissionEmailInput(BaseModel):
    """Input for admission details emails."""
    to: str = Field(description="Patient email address")
    patient_name: str = Field(description="Patient full name")
    admission_date: str = Field(description="Scheduled admission date")
    room_number: str = Field(description="Assigned room number")
    doctor_name: str = Field(description="Assigned doctor name")
    estimated_cost: float = Field(description="Estimated total cost")
    room_type: str = Field(description="Type of room (General/ICU/Private)")


class DischargeEmailInput(BaseModel):
    """Input for discharge summary emails."""
    to: str = Field(description="Patient email address")
    patient_name: str = Field(description="Patient full name")
    discharge_date: str = Field(description="Discharge date")
    diagnosis: str = Field(description="Final diagnosis")
    treatment_summary: str = Field(description="Summary of treatment received")
    medications: List[str] = Field(description="List of prescribed medications")
    followup_date: Optional[str] = Field(default=None, description="Follow-up appointment date")
    special_instructions: Optional[str] = Field(default=None, description="Special care instructions")


class FollowupEmailInput(BaseModel):
    """Input for follow-up appointment emails."""
    to: str = Field(description="Patient email address")
    patient_name: str = Field(description="Patient full name")
    followup_date: str = Field(description="Follow-up appointment date")
    followup_time: str = Field(description="Follow-up appointment time")
    doctor_name: str = Field(description="Doctor name for follow-up")
    reason: str = Field(description="Reason for follow-up")


class FeedbackEmailInput(BaseModel):
    """Input for feedback request emails."""
    to: str = Field(description="Patient email address")
    patient_name: str = Field(description="Patient full name")
    discharge_date: str = Field(description="Date of discharge")
    form_link: Optional[str] = Field(default="https://forms.google.com/feedback", description="Feedback form URL")


class WelcomeEmailInput(BaseModel):
    """Input for sending welcome email to new patient."""
    to: str = Field(description="Patient email address")
    patient_name: str = Field(description="Patient's full name")
    registration_id: str = Field(description="Registration ID assigned to patient")


class MissingDocumentsEmailInput(BaseModel):
    """Input for requesting missing documents."""
    to: str = Field(description="Patient email address")
    patient_name: str = Field(description="Patient's full name")
    missing_docs: List[str] = Field(description="List of missing document names")
    deadline: str = Field(description="Deadline for document submission")


class LabTestEmailInput(BaseModel):
    """Input for sending lab test information."""
    to: str = Field(description="Patient email address")
    patient_name: str = Field(description="Patient's full name")
    tests_required: List[str] = Field(description="List of tests required")
    lab_type: str = Field(description="'internal' or 'external'")
    appointment_details: Optional[Dict] = Field(default=None, description="Appointment details if internal")
    external_labs: Optional[List[Dict]] = Field(default=None, description="External labs list")


class AdmissionDetailsEmailInput(BaseModel):
    """Input for sending admission details."""
    to: str = Field(description="Patient email address")
    patient_name: str = Field(description="Patient's full name")
    admission_date: str = Field(description="Scheduled admission date")
    room_number: str = Field(description="Assigned room/bed number")
    doctor_name: str = Field(description="Assigned doctor's name")
    estimated_cost: float = Field(description="Estimated total cost")
    insurance_coverage: Optional[float] = Field(default=None, description="Insurance coverage amount")


# ==================== BASE CLASS ====================

class GmailToolBase:
    """Base class with Gmail API connection."""
    
    def __init__(self, credentials_file: str = 'client_secret.json', 
                 token_file: str = 'token.pickle'):
        """Initialize Gmail service."""
        try:
            # Load credentials
            if not os.path.exists(token_file):
                print("⚠️  No token found. Running authentication...")
                creds = authenticate_gmail(credentials_file, token_file)
            else:
                with open(token_file, 'rb') as token:
                    creds = pickle.load(token)
                
                # Refresh if expired
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    with open(token_file, 'wb') as token:
                        pickle.dump(creds, token)
            
            self.service = build('gmail', 'v1', credentials=creds)
            self.sender_email = self._get_user_email()
            print(f"✅ Gmail service initialized for {self.sender_email}")
            
        except Exception as e:
            print(f"❌ Error initializing Gmail service: {e}")
            self.service = None
            self.sender_email = None
    
    def _get_user_email(self):
        """Get authenticated user's email address."""
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return profile.get('emailAddress')
        except:
            return "unknown@gmail.com"
    
    def send_email(self, to: str, subject: str, body: str, cc: str = None, is_html: bool = True) -> str:
        """Send an email using Gmail API."""
        if not self.service:
            return "❌ Error: Gmail service not initialized."
        
        try:
            # Create message
            if is_html:
                message = MIMEMultipart("alternative")
                message.attach(MIMEText(body, "html"))
            else:
                message = MIMEText(body)
            
            message["to"] = to
            message["from"] = self.sender_email
            message["subject"] = subject
            if cc:
                message["cc"] = cc
            
            # Encode message
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            body_data = {"raw": raw}
            
            # Send message
            sent_message = self.service.users().messages().send(
                userId="me", 
                body=body_data
            ).execute()
            
            return f"✅ Email sent to {to}! Message ID: {sent_message.get('id')}"
        
        except Exception as e:
            return f"❌ Error sending email: {str(e)}"
    
    def read_emails(self, folder: str = "INBOX", unread_only: bool = True, limit: int = 10) -> str:
        """Read emails from Gmail."""
        if not self.service:
            return "❌ Error: Gmail service not initialized."
        
        try:
            # Build query
            query = "is:unread" if unread_only else ""
            
            # Get messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=limit,
                labelIds=[folder]
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return "📭 No emails found."
            
            emails_data = []
            
            for msg in messages:
                msg_data = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                # Extract headers
                headers = msg_data['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
                
                # Extract body
                body = ""
                if 'parts' in msg_data['payload']:
                    for part in msg_data['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            if 'data' in part['body']:
                                body = base64.urlsafe_b64decode(part['body']['data']).decode()
                                break
                elif 'body' in msg_data['payload'] and 'data' in msg_data['payload']['body']:
                    body = base64.urlsafe_b64decode(msg_data['payload']['body']['data']).decode()
                
                emails_data.append({
                    'id': msg['id'],
                    'from': from_email,
                    'subject': subject,
                    'date': date,
                    'body': body[:500]  # Truncate long emails
                })
            
            # Format response
            result = f"📬 Found {len(emails_data)} email(s):\n\n"
            for idx, email_info in enumerate(emails_data, 1):
                result += f"--- Email {idx} ---\n"
                result += f"From: {email_info['from']}\n"
                result += f"Subject: {email_info['subject']}\n"
                result += f"Date: {email_info['date']}\n"
                result += f"Preview: {email_info['body'][:200]}...\n\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error reading emails: {str(e)}"


# ==================== LANGCHAIN TOOLS ====================

class SendGmailTool(BaseTool, GmailToolBase):
    """General purpose Gmail sending tool."""
    
    name: str = "send_gmail"
    description: str = """Send a general email through Gmail. Use this for any email that doesn't fit other specialized tools."""
    args_schema: Type[BaseModel] = GmailSendInput
    
    service: Optional[object] = Field(default=None, exclude=True)
    sender_email: Optional[str] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'client_secret.json', token_file: str = 'token.pickle'):
        BaseTool.__init__(self)
        GmailToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, to: str, subject: str, message: str, cc: Optional[str] = None) -> str:
        return self.send_email(to, subject, message, cc, is_html=False)
    
    async def _arun(self, to: str, subject: str, message: str, cc: Optional[str] = None) -> str:
        return self._run(to, subject, message, cc)


class ReadEmailsTool(BaseTool, GmailToolBase):
    """Tool to read incoming emails."""
    
    name: str = "read_emails"
    description: str = """Read incoming emails from hospital inbox. Returns list of emails with sender, subject, and preview."""
    args_schema: Type[BaseModel] = ReadEmailsInput
    
    service: Optional[object] = Field(default=None, exclude=True)
    sender_email: Optional[str] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'client_secret.json', token_file: str = 'token.pickle'):
        BaseTool.__init__(self)
        GmailToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, folder: str = "INBOX", unread_only: bool = True, limit: int = 10) -> str:
        return self.read_emails(folder, unread_only, limit)
    
    async def _arun(self, folder: str = "INBOX", unread_only: bool = True, limit: int = 10) -> str:
        return self._run(folder, unread_only, limit)


class SendWelcomeEmailTool(BaseTool, GmailToolBase):
    """Tool for sending welcome email to new patients."""
    
    name: str = "send_welcome_email"
    description: str = """Send a welcome email to newly registered patient with registration details."""
    args_schema: Type[BaseModel] = WelcomeEmailInput
    
    service: Optional[object] = Field(default=None, exclude=True)
    sender_email: Optional[str] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'client_secret.json', token_file: str = 'token.pickle'):
        BaseTool.__init__(self)
        GmailToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, to: str, patient_name: str, registration_id: str) -> str:
        subject = "Welcome to Our Hospital - Registration Confirmed"
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2c5aa0;">Welcome to Our Hospital! 🏥</h2>
            <p>Dear {patient_name},</p>
            <p>Thank you for choosing our hospital. Your registration has been successfully completed.</p>
            
            <div style="background-color: #f4f4f4; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="color: #2c5aa0;">Your Registration Details:</h3>
                <p><strong>Registration ID:</strong> {registration_id}</p>
                <p><strong>Registration Date:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
            </div>
            
            <p><strong>Next Steps:</strong></p>
            <ul>
                <li>Keep your Registration ID for future reference</li>
                <li>You will receive further communications about document submission</li>
                <li>Our team will contact you regarding your medical assessment</li>
            </ul>
            
            <p>Best regards,<br><strong>Hospital Administration Team</strong></p>
        </body>
        </html>
        """
        return self.send_email(to, subject, body)
    
    async def _arun(self, to: str, patient_name: str, registration_id: str) -> str:
        return self._run(to, patient_name, registration_id)


class SendMissingDocumentsEmailTool(BaseTool, GmailToolBase):
    """Tool for requesting missing documents."""
    
    name: str = "send_missing_documents_email"
    description: str = """Request missing documents from patient."""
    args_schema: Type[BaseModel] = MissingDocumentsEmailInput
    
    service: Optional[object] = Field(default=None, exclude=True)
    sender_email: Optional[str] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'client_secret.json', token_file: str = 'token.pickle'):
        BaseTool.__init__(self)
        GmailToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, to: str, patient_name: str, missing_docs: List[str], deadline: str) -> str:
        subject = "Action Required: Missing Documents"
        docs_list = "".join([f"<li>{doc}</li>" for doc in missing_docs])
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #d9534f;">📋 Missing Documents Required</h2>
            <p>Dear {patient_name},</p>
            <p>We need the following documents to complete your medical records:</p>
            
            <div style="background-color: #fff3cd; padding: 15px; margin: 20px 0;">
                <h3>Required Documents:</h3>
                <ul>{docs_list}</ul>
            </div>
            
            <p><strong>⏰ Deadline:</strong> {deadline}</p>
            <p>Please submit these documents by replying to this email with attachments.</p>
            
            <p>Best regards,<br><strong>Document Processing Team</strong></p>
        </body>
        </html>
        """
        return self.send_email(to, subject, body)
    
    async def _arun(self, to: str, patient_name: str, missing_docs: List[str], deadline: str) -> str:
        return self._run(to, patient_name, missing_docs, deadline)


# ==================== LAB TEST EMAIL TOOL ====================

class SendLabTestEmailTool(BaseTool, GmailToolBase):
    """Tool for sending lab test appointment details."""
    
    name: str = "send_lab_test_email"
    description: str = """Send lab test appointment details to patient including tests, date, time, and location."""
    args_schema: Type[BaseModel] = LabTestEmailInput
    
    service: Optional[object] = Field(default=None, exclude=True)
    sender_email: Optional[str] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', token_file: str = 'token.pickle'):
        BaseTool.__init__(self)
        GmailToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, to: str, patient_name: str, tests: List[str], appointment_date: str, 
             appointment_time: str, location: str) -> str:
        subject = f"🧪 Lab Test Appointment Scheduled - {appointment_date}"
        tests_list = "".join([f"<li>{test}</li>" for test in tests])
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2c5aa0;">🧪 Your Lab Tests are Scheduled</h2>
            <p>Dear {patient_name},</p>
            <p>Your laboratory tests have been scheduled. Please find the details below:</p>
            
            <div style="background-color: #e8f4f8; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #2c5aa0;">Appointment Details:</h3>
                <p><strong>📅 Date:</strong> {appointment_date}</p>
                <p><strong>🕒 Time:</strong> {appointment_time}</p>
                <p><strong>📍 Location:</strong> {location}</p>
            </div>
            
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3>Tests to be Conducted:</h3>
                <ul>{tests_list}</ul>
            </div>
            
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3>⚠️ Preparation Instructions:</h3>
                <ul>
                    <li>Fasting required: 8-12 hours before the test</li>
                    <li>Bring your ID and registration documents</li>
                    <li>Arrive 15 minutes early</li>
                    <li>Wear comfortable clothing</li>
                </ul>
            </div>
            
            <p>If you need to reschedule, please reply to this email or call us.</p>
            <p>Best regards,<br><strong>Lab Coordination Team</strong></p>
        </body>
        </html>
        """
        return self.send_email(to, subject, body)
    
    async def _arun(self, to: str, patient_name: str, tests: List[str], appointment_date: str, 
                    appointment_time: str, location: str) -> str:
        return self._run(to, patient_name, tests, appointment_date, appointment_time, location)


# ==================== TEST RESULTS EMAIL TOOL ====================

class SendResultsEmailTool(BaseTool, GmailToolBase):
    """Tool for sending test results to patients."""
    
    name: str = "send_results_email"
    description: str = """Send laboratory test results to patient. Indicate if results are normal or require attention."""
    args_schema: Type[BaseModel] = ResultsEmailInput
    
    service: Optional[object] = Field(default=None, exclude=True)
    sender_email: Optional[str] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', token_file: str = 'token.pickle'):
        BaseTool.__init__(self)
        GmailToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, to: str, patient_name: str, test_date: str, results_summary: str, 
             is_normal: bool, doctor_notes: Optional[str] = None) -> str:
        
        if is_normal:
            subject = "✅ Your Test Results - All Normal"
            status_color = "#28a745"
            status_text = "✅ All Results Normal"
            status_message = "Great news! Your test results are within normal ranges. Continue maintaining your healthy lifestyle."
        else:
            subject = "⚠️ Your Test Results - Doctor Review Recommended"
            status_color = "#dc3545"
            status_text = "⚠️ Attention Required"
            status_message = "Some results require doctor consultation. Please review the recommendations below carefully."
        
        # Format doctor notes section with proper HTML
        doctor_section = ""
        if doctor_notes:
            # Escape and format doctor notes properly
            formatted_notes = doctor_notes.replace('\n', '<br>')
            doctor_section = f"""
            <div style="background-color: #e8f5e9; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #4caf50;">
                <h3 style="color: #2e7d32; margin-top: 0;">👨‍⚕️ Doctor's Assessment</h3>
                <div style="font-size: 14px; line-height: 1.8; white-space: pre-wrap;">
{formatted_notes}
                </div>
            </div>
            """
        
        # Format results summary with better styling
        formatted_results = results_summary.replace('\n', '<br>')
        
        body = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, {status_color} 0%, {status_color}dd 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
                <h1 style="margin: 0; font-size: 28px;">📊 Your Lab Test Results</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Hospital Management System</p>
            </div>
            
            <p style="font-size: 16px;">Dear <strong>{patient_name}</strong>,</p>
            <p style="font-size: 15px;">Your laboratory test results are now available. Please review them carefully below.</p>
            
            <div style="background-color: {status_color}; color: white; padding: 20px; border-radius: 8px; margin: 25px 0; text-align: center;">
                <h2 style="color: white; margin: 0 0 10px 0; font-size: 22px;">{status_text}</h2>
                <p style="color: white; margin: 0; font-size: 15px; opacity: 0.95;">{status_message}</p>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 25px; border-radius: 8px; margin: 25px 0; border-left: 4px solid #007bff;">
                <h3 style="color: #007bff; margin-top: 0;">📋 Test Results Summary</h3>
                <p style="margin: 5px 0 15px 0;"><strong>Test Date:</strong> {test_date}</p>
                <div style="font-size: 14px; line-height: 1.8;">
{formatted_results}
                </div>
            </div>
            
            {doctor_section}
            
            <div style="background-color: #fff3cd; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 4px solid #ffc107;">
                <h3 style="color: #856404; margin-top: 0;">🎯 Next Steps</h3>
                <ul style="margin: 10px 0; padding-left: 20px; font-size: 14px;">
                    {"<li>Continue maintaining your healthy lifestyle habits</li>" if is_normal else "<li><strong>Schedule an appointment with your doctor to discuss results</strong></li>"}
                    <li>Keep this report for your medical records</li>
                    {"<li>Regular health checkups recommended every 6 months</li>" if is_normal else "<li>Follow all doctor's instructions carefully</li>"}
                    {"<li>Contact us if you have any questions about your results</li>" if is_normal else "<li>Contact us immediately if you experience any concerning symptoms</li>"}
                </ul>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 25px 0; text-align: center; border-top: 3px solid #dee2e6;">
                <p style="margin: 5px 0; font-size: 14px; color: #666;">📞 Questions? Contact us at <strong>hospital@example.com</strong> or call <strong>+91-9876543210</strong></p>
                <p style="margin: 10px 0 5px 0; font-size: 13px; color: #999;">This is an automated report generated by our Hospital Management System</p>
            </div>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; text-align: center;">
                <p style="font-size: 16px; margin: 0;">Best regards,</p>
                <p style="font-size: 18px; font-weight: bold; color: #2c5aa0; margin: 5px 0;">🏥 Hospital Medical Team</p>
            </div>
        </body>
        </html>
        """
        return self.send_email(to, subject, body)
    
    async def _arun(self, to: str, patient_name: str, test_date: str, results_summary: str, 
                    is_normal: bool, doctor_notes: Optional[str] = None) -> str:
        return self._run(to, patient_name, test_date, results_summary, is_normal, doctor_notes)


# ==================== ADMISSION DETAILS EMAIL TOOL ====================

class SendAdmissionDetailsEmailTool(BaseTool, GmailToolBase):
    """Tool for sending admission details."""
    
    name: str = "send_admission_details_email"
    description: str = """Send complete admission details including date, room, doctor, and estimated cost."""
    args_schema: Type[BaseModel] = AdmissionEmailInput
    
    service: Optional[object] = Field(default=None, exclude=True)
    sender_email: Optional[str] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', token_file: str = 'token.pickle'):
        BaseTool.__init__(self)
        GmailToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, to: str, patient_name: str, admission_date: str, room_number: str, 
             doctor_name: str, estimated_cost: float, room_type: str) -> str:
        subject = f"🏥 Admission Confirmed - {admission_date}"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2c5aa0;">🏥 Your Admission is Confirmed</h2>
            <p>Dear {patient_name},</p>
            <p>Your hospital admission has been scheduled. Please review the details below:</p>
            
            <div style="background-color: #e8f4f8; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #2c5aa0;">Admission Details:</h3>
                <p><strong>📅 Admission Date:</strong> {admission_date}</p>
                <p><strong>🛏️ Room Number:</strong> {room_number}</p>
                <p><strong>🏠 Room Type:</strong> {room_type}</p>
                <p><strong>👨‍⚕️ Assigned Doctor:</strong> Dr. {doctor_name}</p>
            </div>
            
            <div style="background-color: #fff8e1; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>💰 Financial Information:</h3>
                <p><strong>Estimated Total Cost:</strong> ₹{estimated_cost:,.2f}</p>
                <p><em>Note: This is an estimate. Final bill will be provided at discharge.</em></p>
            </div>
            
            <div style="background-color: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>📋 What to Bring:</h3>
                <ul>
                    <li>Government-issued ID</li>
                    <li>Insurance documents (if applicable)</li>
                    <li>Previous medical records</li>
                    <li>List of current medications</li>
                    <li>Personal items (toiletries, comfortable clothing)</li>
                </ul>
            </div>
            
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3>⚠️ Important Instructions:</h3>
                <ul>
                    <li>Report to admissions desk 2 hours before scheduled time</li>
                    <li>Fasting may be required - follow pre-admission instructions</li>
                    <li>Arrange for a family member to accompany you</li>
                </ul>
            </div>
            
            <p>For any questions or to reschedule, please contact us immediately.</p>
            <p>Best regards,<br><strong>Admission Planning Team</strong></p>
        </body>
        </html>
        """
        return self.send_email(to, subject, body)
    
    async def _arun(self, to: str, patient_name: str, admission_date: str, room_number: str, 
                    doctor_name: str, estimated_cost: float, room_type: str) -> str:
        return self._run(to, patient_name, admission_date, room_number, doctor_name, estimated_cost, room_type)


# ==================== DISCHARGE SUMMARY EMAIL TOOL ====================

class SendDischargeEmailTool(BaseTool, GmailToolBase):
    """Tool for sending discharge summary."""
    
    name: str = "send_discharge_email"
    description: str = """Send discharge summary with diagnosis, treatment, medications, and follow-up instructions."""
    args_schema: Type[BaseModel] = DischargeEmailInput
    
    service: Optional[object] = Field(default=None, exclude=True)
    sender_email: Optional[str] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', token_file: str = 'token.pickle'):
        BaseTool.__init__(self)
        GmailToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, to: str, patient_name: str, discharge_date: str, diagnosis: str, 
             treatment_summary: str, medications: List[str], followup_date: Optional[str] = None,
             special_instructions: Optional[str] = None) -> str:
        subject = f"🏠 Discharge Summary - {discharge_date}"
        
        medications_list = "".join([f"<li>{med}</li>" for med in medications])
        
        followup_section = ""
        if followup_date:
            followup_section = f"""
            <div style="background-color: #e8f4f8; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3>📅 Follow-up Appointment:</h3>
                <p><strong>Date:</strong> {followup_date}</p>
                <p>Please mark this date in your calendar. You will receive a reminder.</p>
            </div>
            """
        
        special_section = ""
        if special_instructions:
            special_section = f"""
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3>⚠️ Special Care Instructions:</h3>
                <p>{special_instructions}</p>
            </div>
            """
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #28a745;">🏠 Discharge Summary</h2>
            <p>Dear {patient_name},</p>
            <p>You have been successfully discharged from our hospital. Here is your discharge summary:</p>
            
            <div style="background-color: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>Medical Information:</h3>
                <p><strong>Discharge Date:</strong> {discharge_date}</p>
                <p><strong>Diagnosis:</strong> {diagnosis}</p>
                <p><strong>Treatment Summary:</strong></p>
                <p>{treatment_summary}</p>
            </div>
            
            <div style="background-color: #e8f5e9; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>💊 Prescribed Medications:</h3>
                <ul>{medications_list}</ul>
                <p><em>Take medications as prescribed by your doctor.</em></p>
            </div>
            
            {followup_section}
            {special_section}
            
            <div style="background-color: #ffebee; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3>🚨 Emergency Signs - Seek Immediate Help If:</h3>
                <ul>
                    <li>Severe pain or discomfort</li>
                    <li>High fever (above 101°F)</li>
                    <li>Difficulty breathing</li>
                    <li>Unusual bleeding</li>
                    <li>Any concerning symptoms</li>
                </ul>
            </div>
            
            <p>Wishing you a speedy recovery!</p>
            <p>Best regards,<br><strong>Hospital Medical Team</strong></p>
        </body>
        </html>
        """
        return self.send_email(to, subject, body)
    
    async def _arun(self, to: str, patient_name: str, discharge_date: str, diagnosis: str, 
                    treatment_summary: str, medications: List[str], followup_date: Optional[str] = None,
                    special_instructions: Optional[str] = None) -> str:
        return self._run(to, patient_name, discharge_date, diagnosis, treatment_summary, 
                        medications, followup_date, special_instructions)


# ==================== FOLLOW-UP EMAIL TOOL ====================

class SendFollowupEmailTool(BaseTool, GmailToolBase):
    """Tool for sending follow-up appointment details."""
    
    name: str = "send_followup_email"
    description: str = """Send follow-up appointment confirmation with date, time, doctor, and reason."""
    args_schema: Type[BaseModel] = FollowupEmailInput
    
    service: Optional[object] = Field(default=None, exclude=True)
    sender_email: Optional[str] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', token_file: str = 'token.pickle'):
        BaseTool.__init__(self)
        GmailToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, to: str, patient_name: str, followup_date: str, followup_time: str, 
             doctor_name: str, reason: str) -> str:
        subject = f"📅 Follow-up Appointment Scheduled - {followup_date}"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2c5aa0;">📅 Your Follow-up Appointment</h2>
            <p>Dear {patient_name},</p>
            <p>Your follow-up appointment has been scheduled. Please find the details below:</p>
            
            <div style="background-color: #e8f4f8; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #2c5aa0;">Appointment Details:</h3>
                <p><strong>📅 Date:</strong> {followup_date}</p>
                <p><strong>🕒 Time:</strong> {followup_time}</p>
                <p><strong>👨‍⚕️ Doctor:</strong> Dr. {doctor_name}</p>
                <p><strong>📋 Reason:</strong> {reason}</p>
            </div>
            
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3>📋 What to Bring:</h3>
                <ul>
                    <li>Previous medical records</li>
                    <li>Current medications list</li>
                    <li>Any questions or concerns you want to discuss</li>
                    <li>Insurance card (if applicable)</li>
                </ul>
            </div>
            
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3>⚠️ Important Notes:</h3>
                <ul>
                    <li>Arrive 10 minutes early for registration</li>
                    <li>If you need to reschedule, please inform us 24 hours in advance</li>
                    <li>Bring a list of any new symptoms or concerns</li>
                </ul>
            </div>
            
            <p>A reminder will be sent 1 day before your appointment.</p>
            <p>Best regards,<br><strong>Hospital Scheduling Team</strong></p>
        </body>
        </html>
        """
        return self.send_email(to, subject, body)
    
    async def _arun(self, to: str, patient_name: str, followup_date: str, followup_time: str, 
                    doctor_name: str, reason: str) -> str:
        return self._run(to, patient_name, followup_date, followup_time, doctor_name, reason)


# ==================== FEEDBACK REQUEST TOOL ====================

class SendFeedbackEmailTool(BaseTool, GmailToolBase):
    """Tool for sending feedback form requests."""
    
    name: str = "send_feedback_email"
    description: str = """Send feedback form request to patient after discharge (typically 3 days later)."""
    args_schema: Type[BaseModel] = FeedbackEmailInput
    
    service: Optional[object] = Field(default=None, exclude=True)
    sender_email: Optional[str] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', token_file: str = 'token.pickle'):
        BaseTool.__init__(self)
        GmailToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, to: str, patient_name: str, discharge_date: str, 
             form_link: str = "https://forms.google.com/feedback") -> str:
        subject = "📝 We Value Your Feedback"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2c5aa0;">📝 Share Your Experience</h2>
            <p>Dear {patient_name},</p>
            <p>We hope you are recovering well after your discharge on {discharge_date}.</p>
            
            <p>Your feedback is valuable to us and helps us improve our services. We would appreciate if you could take a few minutes to share your experience.</p>
            
            <div style="background-color: #e8f4f8; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center;">
                <h3 style="color: #2c5aa0;">Rate Your Experience</h3>
                <p>Please rate the following aspects:</p>
                <ul style="text-align: left;">
                    <li>Quality of medical care</li>
                    <li>Staff behavior and professionalism</li>
                    <li>Cleanliness and facilities</li>
                    <li>Communication and information provided</li>
                    <li>Overall experience</li>
                </ul>
                <br>
                <a href="{form_link}" style="display: inline-block; background-color: #2c5aa0; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Complete Feedback Form
                </a>
            </div>
            
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <p><strong>⏱️ Takes only 3-5 minutes</strong></p>
                <p>Your responses are confidential and will help us serve patients better.</p>
            </div>
            
            <p>Thank you for choosing our hospital. We wish you continued good health!</p>
            <p>Best regards,<br><strong>Hospital Administration</strong></p>
        </body>
        </html>
        """
        return self.send_email(to, subject, body)
    
    async def _arun(self, to: str, patient_name: str, discharge_date: str, form_link: str) -> str:
        return self._run(to, patient_name, discharge_date, form_link)


# ==================== READ UNREAD EMAILS TOOL ====================

class ReadUnreadEmailsTool(BaseTool, GmailToolBase):
    """Tool for reading unread emails from hospital inbox."""
    
    name: str = "read_unread_emails"
    description: str = """Read unread emails from hospital inbox. Useful for checking patient responses and hospital-related communications."""
    args_schema: Type[BaseModel] = ReadEmailsInput
    
    service: Optional[object] = Field(default=None, exclude=True)
    sender_email: Optional[str] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', token_file: str = 'token.pickle'):
        BaseTool.__init__(self)
        GmailToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, folder: str = "INBOX", unread_only: bool = True, limit: int = 10) -> str:
        try:
            # Build query
            query = ""
            if unread_only:
                query = "is:unread"
            
            # Fetch messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=limit,
                labelIds=[folder]
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return "📭 No unread emails found."
            
            emails_info = []
            for msg in messages:
                # Get full message
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                # Extract headers
                headers = message['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
                
                # Extract body (simplified)
                body = ""
                if 'parts' in message['payload']:
                    for part in message['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                            break
                elif 'body' in message['payload'] and 'data' in message['payload']['body']:
                    body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
                
                emails_info.append({
                    'id': msg['id'],
                    'from': from_email,
                    'subject': subject,
                    'date': date,
                    'snippet': message['snippet'][:100]
                })
            
            # Format output
            output = f"📧 Found {len(emails_info)} unread email(s):\n\n"
            for i, email in enumerate(emails_info, 1):
                output += f"{i}. From: {email['from']}\n"
                output += f"   Subject: {email['subject']}\n"
                output += f"   Date: {email['date']}\n"
                output += f"   Preview: {email['snippet']}...\n\n"
            
            return output
            
        except Exception as e:
            return f"❌ Error reading emails: {str(e)}"
    
    async def _arun(self, folder: str = "INBOX", unread_only: bool = True, limit: int = 10) -> str:
        return self._run(folder, unread_only, limit)


# ==================== SEARCH EMAILS TOOL ====================

class SearchEmailsTool(BaseTool, GmailToolBase):
    """Tool for searching hospital emails."""
    
    name: str = "search_emails"
    description: str = """Search emails in hospital inbox by sender, subject, or keywords. Useful for finding specific patient communications."""
    args_schema: Type[BaseModel] = SearchEmailsInput
    
    service: Optional[object] = Field(default=None, exclude=True)
    sender_email: Optional[str] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', token_file: str = 'token.pickle'):
        BaseTool.__init__(self)
        GmailToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, from_email: Optional[str] = None, subject_contains: Optional[str] = None, limit: int = 10) -> str:
        try:
            # Build search query
            query_parts = []
            if from_email:
                query_parts.append(f"from:{from_email}")
            if subject_contains:
                query_parts.append(f"subject:{subject_contains}")
            
            query = " ".join(query_parts) if query_parts else ""
            
            # Search messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=limit
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return f"📭 No emails found matching the search criteria."
            
            emails_info = []
            for msg in messages:
                # Get message details
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['Subject', 'From', 'Date']
                ).execute()
                
                headers = message['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                from_addr = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
                
                emails_info.append({
                    'from': from_addr,
                    'subject': subject,
                    'date': date,
                    'snippet': message['snippet'][:100]
                })
            
            # Format output
            output = f"🔍 Found {len(emails_info)} email(s):\n\n"
            for i, email in enumerate(emails_info, 1):
                output += f"{i}. From: {email['from']}\n"
                output += f"   Subject: {email['subject']}\n"
                output += f"   Date: {email['date']}\n"
                output += f"   Preview: {email['snippet']}...\n\n"
            
            return output
            
        except Exception as e:
            return f"❌ Error searching emails: {str(e)}"
    
    async def _arun(self, from_email: Optional[str] = None, subject_contains: Optional[str] = None, limit: int = 10) -> str:
        return self._run(from_email, subject_contains, limit)


# ==================== HELPER FUNCTION ====================

def get_all_gmail_tools(credentials_file: str = 'client_secret.json', 
                       token_file: str = 'token.pickle') -> List[BaseTool]:
    """Get all Gmail tools for hospital workflow."""
    return [
        SendGmailTool(credentials_file, token_file),
        ReadEmailsTool(credentials_file, token_file),
        SendWelcomeEmailTool(credentials_file, token_file),
        SendMissingDocumentsEmailTool(credentials_file, token_file),
        SendLabTestEmailTool(credentials_file, token_file),
        SendResultsEmailTool(credentials_file, token_file),
        SendAdmissionDetailsEmailTool(credentials_file, token_file),
        SendDischargeEmailTool(credentials_file, token_file),
        SendFollowupEmailTool(credentials_file, token_file),
        SendFeedbackEmailTool(credentials_file, token_file),
        ReadUnreadEmailsTool(credentials_file, token_file),
        SearchEmailsTool(credentials_file, token_file),
    ]


# ==================== TESTING ====================

if __name__ == "__main__":
    print("=" * 60)
    print("GMAIL TOOL TESTING")
    print("=" * 60)
    
    # Step 1: Authenticate (run once)
    print("\n📝 Step 1: Authenticating Gmail...")
    creds = authenticate_gmail()
    
    # Step 2: Test sending email
    print("\n📧 Step 2: Testing email send...")
    send_tool = SendGmailTool()
    
    result = send_tool._run(
        to="samarth.pawar243@vit.edu",
        subject="Test Email from Hospital AI Agent",
        message="Hello! This is a test email from the hospital management AI agent."
    )
    print(result)
    
    # Step 3: Test welcome email
    print("\n🎉 Step 3: Testing welcome email...")
    welcome_tool = SendWelcomeEmailTool()
    
    result = welcome_tool._run(
        to="samarth.pawar243@vit.edu",
        patient_name="Samarth Pawar",
        registration_id="REG2025001"
    )
    print(result)
    
    # Step 4: Test reading emails
    print("\n📬 Step 4: Testing email reading...")
    read_tool = ReadEmailsTool()
    
    result = read_tool._run(unread_only=False, limit=5)
    print(result)
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 60)