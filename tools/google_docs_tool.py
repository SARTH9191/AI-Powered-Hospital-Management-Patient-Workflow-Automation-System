"""
Google Docs Tool for Hospital Management System
Generates medical reports, discharge summaries, doctor notes, and treatment plans
"""

import os
import pickle
from typing import Optional, Type, List, Dict
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pydantic import BaseModel, Field
from langchain.tools import BaseTool


# ==================== GOOGLE DOCS SCOPES ====================
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive'
]


# ==================== AUTHENTICATION ====================

def authenticate_docs(credentials_file: str = 'credentials/client_secret.json', 
                      token_file: str = 'docs_token.pickle'):
    """Authenticate with Google Docs API using dedicated docs token"""
    creds = None
    
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds


# ==================== BASE CLASS ====================

class DocsToolBase:
    """Base class for Google Docs tools"""
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'token.pickle'):
        creds = authenticate_docs(credentials_file, token_file)
        self.docs_service = build('docs', 'v1', credentials=creds)
        self.drive_service = build('drive', 'v3', credentials=creds)


# ==================== INPUT SCHEMAS ====================

class CreateDischargeSummaryInput(BaseModel):
    """Input for creating discharge summary."""
    patient_name: str = Field(description="Patient full name")
    patient_id: str = Field(description="Patient registration ID")
    admission_date: str = Field(description="Admission date")
    discharge_date: str = Field(description="Discharge date")
    diagnosis: str = Field(description="Final diagnosis")
    treatment_summary: str = Field(description="Summary of treatment provided")
    medications: List[str] = Field(description="List of prescribed medications")
    doctor_name: str = Field(description="Attending doctor name")
    followup_instructions: Optional[str] = Field(default=None, description="Follow-up care instructions")


class CreateMedicalReportInput(BaseModel):
    """Input for creating medical reports."""
    report_title: str = Field(description="Report title")
    patient_name: str = Field(description="Patient name")
    patient_id: str = Field(description="Patient ID")
    report_date: str = Field(description="Report date")
    medical_history: str = Field(description="Patient medical history")
    current_condition: str = Field(description="Current medical condition")
    lab_results: Optional[str] = Field(default=None, description="Lab test results")
    doctor_notes: Optional[str] = Field(default=None, description="Doctor's notes and observations")


class CreateDoctorNotesInput(BaseModel):
    """Input for creating doctor consultation notes."""
    patient_name: str = Field(description="Patient name")
    consultation_date: str = Field(description="Consultation date")
    chief_complaint: str = Field(description="Patient's main complaint")
    examination_findings: str = Field(description="Physical examination findings")
    diagnosis: str = Field(description="Doctor's diagnosis")
    treatment_plan: str = Field(description="Recommended treatment plan")
    doctor_name: str = Field(description="Doctor's name")


class CreateTreatmentPlanInput(BaseModel):
    """Input for creating treatment plans."""
    patient_name: str = Field(description="Patient name")
    diagnosis: str = Field(description="Medical diagnosis")
    treatment_goals: List[str] = Field(description="Treatment objectives")
    medications: List[Dict[str, str]] = Field(description="Medications with dosage and frequency")
    lifestyle_changes: Optional[List[str]] = Field(default=None, description="Recommended lifestyle modifications")
    follow_up_schedule: str = Field(description="Follow-up appointment schedule")


class ShareDocumentInput(BaseModel):
    """Input for sharing documents."""
    document_id: str = Field(description="Google Doc ID to share")
    email: str = Field(description="Email address to share with")
    role: str = Field(default="reader", description="Permission: reader, writer, or commenter")


# ==================== DOCS TOOLS ====================

class CreateDischargeSummaryTool(BaseTool, DocsToolBase):
    """Tool for creating discharge summaries."""
    
    name: str = "create_discharge_summary"
    description: str = """Create a professional discharge summary document for patient. 
    Includes diagnosis, treatment, medications, and follow-up instructions."""
    args_schema: Type[BaseModel] = CreateDischargeSummaryInput
    
    docs_service: Optional[object] = Field(default=None, exclude=True)
    drive_service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'token.pickle'):
        BaseTool.__init__(self)
        DocsToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, patient_name: str, patient_id: str, admission_date: str, 
             discharge_date: str, diagnosis: str, treatment_summary: str, 
             medications: List[str], doctor_name: str, 
             followup_instructions: Optional[str] = None) -> str:
        try:
            # Create a new document
            doc = self.docs_service.documents().create(
                body={'title': f'Discharge Summary - {patient_name} ({patient_id})'}
            ).execute()
            
            document_id = doc.get('documentId')
            
            # Prepare content
            medications_text = '\n'.join([f'  • {med}' for med in medications])
            followup_text = followup_instructions or "Follow-up as advised by your doctor."
            
            # Build document content with beautiful formatting
            content_text = f"""DISCHARGE SUMMARY

Hospital Management System

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 PATIENT INFORMATION

Patient Name: {patient_name}
Patient ID: {patient_id}
Admission Date: {admission_date}
Discharge Date: {discharge_date}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔬 DIAGNOSIS

{diagnosis}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💊 TREATMENT SUMMARY

{treatment_summary}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💉 PRESCRIBED MEDICATIONS

{medications_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 FOLLOW-UP INSTRUCTIONS

{followup_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👨‍⚕️ ATTENDING PHYSICIAN

Dr. {doctor_name}
Date of Report: {discharge_date}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚕️ IMPORTANT NOTICE

This is an official medical document. Please keep it for your records.
For any questions or concerns, please contact the hospital.

Hospital Management System • Patient Care Excellence
"""
            
            requests = [
                {
                    'insertText': {
                        'location': {'index': 1},
                        'text': content_text
                    }
                },
                # Format title as large centered heading with color
                {
                    'updateParagraphStyle': {
                        'range': {'startIndex': 1, 'endIndex': 18},
                        'paragraphStyle': {
                            'namedStyleType': 'HEADING_1',
                            'alignment': 'CENTER'
                        },
                        'fields': 'namedStyleType,alignment'
                    }
                },
                # Format subtitle (Hospital Management System)
                {
                    'updateParagraphStyle': {
                        'range': {'startIndex': 19, 'endIndex': 48},
                        'paragraphStyle': {
                            'namedStyleType': 'SUBTITLE',
                            'alignment': 'CENTER'
                        },
                        'fields': 'namedStyleType,alignment'
                    }
                },
                # Make section headers bold and blue
                {
                    'updateTextStyle': {
                        'range': {'startIndex': 1, 'endIndex': len(content_text)},
                        'textStyle': {
                            'weightedFontFamily': {'fontFamily': 'Calibri'},
                            'fontSize': {'magnitude': 11, 'unit': 'PT'}
                        },
                        'fields': 'weightedFontFamily,fontSize'
                    }
                }
            ]
            
            # Update the document
            self.docs_service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            # Get document link
            doc_info = self.drive_service.files().get(
                fileId=document_id,
                fields='webViewLink'
            ).execute()
            
            doc_link = doc_info.get('webViewLink')
            
            return f"""✅ Discharge Summary Created Successfully!

📄 Document Details:
- Title: Discharge Summary - {patient_name}
- Patient ID: {patient_id}
- Document ID: {document_id}
- Link: {doc_link}

✅ Document includes:
  • Patient information
  • Diagnosis
  • Treatment summary
  • Prescribed medications
  • Follow-up instructions
  • Doctor's signature

🔗 Share this document with patient or medical staff as needed.
"""
        
        except Exception as e:
            return f"❌ Error creating discharge summary: {str(e)}"
    
    async def _arun(self, patient_name: str, patient_id: str, admission_date: str, 
                    discharge_date: str, diagnosis: str, treatment_summary: str, 
                    medications: List[str], doctor_name: str, 
                    followup_instructions: Optional[str] = None) -> str:
        return self._run(patient_name, patient_id, admission_date, discharge_date, 
                        diagnosis, treatment_summary, medications, doctor_name, followup_instructions)


class CreateMedicalReportTool(BaseTool, DocsToolBase):
    """Tool for creating medical reports."""
    
    name: str = "create_medical_report"
    description: str = """Create comprehensive medical report for patient. 
    Includes history, current condition, lab results, and doctor's observations."""
    args_schema: Type[BaseModel] = CreateMedicalReportInput
    
    docs_service: Optional[object] = Field(default=None, exclude=True)
    drive_service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'token.pickle'):
        BaseTool.__init__(self)
        DocsToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, report_title: str, patient_name: str, patient_id: str, 
             report_date: str, medical_history: str, current_condition: str,
             lab_results: Optional[str] = None, doctor_notes: Optional[str] = None) -> str:
        try:
            # Create document
            doc = self.docs_service.documents().create(
                body={'title': f'{report_title} - {patient_name}'}
            ).execute()
            
            document_id = doc.get('documentId')
            
            # Build content
            lab_section = f"\nLABORATORY RESULTS\n{lab_results}\n\n{'='*60}\n" if lab_results else ""
            notes_section = f"\nDOCTOR'S NOTES\n{doctor_notes}\n\n{'='*60}\n" if doctor_notes else ""
            
            content = f"""{report_title}

Hospital Management System
{"="*60}

PATIENT INFORMATION
Name: {patient_name}
Patient ID: {patient_id}
Report Date: {report_date}

{"="*60}

MEDICAL HISTORY
{medical_history}

{"="*60}

CURRENT CONDITION
{current_condition}

{"="*60}
{lab_section}{notes_section}
This is a confidential medical document.

Date: {report_date}
"""
            
            # Insert content
            requests = [{
                'insertText': {
                    'location': {'index': 1},
                    'text': content
                }
            }]
            
            self.docs_service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            # Get link
            doc_info = self.drive_service.files().get(
                fileId=document_id,
                fields='webViewLink'
            ).execute()
            
            return f"""✅ Medical Report Created Successfully!

📄 Report: {report_title}
👤 Patient: {patient_name} ({patient_id})
📅 Date: {report_date}
🔗 Link: {doc_info.get('webViewLink')}

✅ Report includes all medical details and observations.
"""
        
        except Exception as e:
            return f"❌ Error creating medical report: {str(e)}"
    
    async def _arun(self, report_title: str, patient_name: str, patient_id: str, 
                    report_date: str, medical_history: str, current_condition: str,
                    lab_results: Optional[str] = None, doctor_notes: Optional[str] = None) -> str:
        return self._run(report_title, patient_name, patient_id, report_date, 
                        medical_history, current_condition, lab_results, doctor_notes)


class CreateDoctorNotesTool(BaseTool, DocsToolBase):
    """Tool for creating doctor consultation notes."""
    
    name: str = "create_doctor_notes"
    description: str = """Create doctor's consultation notes after patient examination. 
    Documents chief complaint, findings, diagnosis, and treatment plan."""
    args_schema: Type[BaseModel] = CreateDoctorNotesInput
    
    docs_service: Optional[object] = Field(default=None, exclude=True)
    drive_service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'token.pickle'):
        BaseTool.__init__(self)
        DocsToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, patient_name: str, consultation_date: str, chief_complaint: str,
             examination_findings: str, diagnosis: str, treatment_plan: str, 
             doctor_name: str) -> dict:
        try:
            # Create document
            doc = self.docs_service.documents().create(
                body={'title': f'Consultation Notes - {patient_name} - {consultation_date}'}
            ).execute()
            
            document_id = doc.get('documentId')
            
            content = f"""DOCTOR'S CONSULTATION NOTES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 CONSULTATION DETAILS

Patient Name: {patient_name}
Consultation Date: {consultation_date}
Attending Physician: Dr. {doctor_name}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🗣️ CHIEF COMPLAINT

{chief_complaint}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 EXAMINATION FINDINGS

{examination_findings}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔬 CLINICAL DIAGNOSIS

{diagnosis}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💊 TREATMENT PLAN & RECOMMENDATIONS

{treatment_plan}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👨‍⚕️ PHYSICIAN ATTESTATION

Physician's Signature: Dr. {doctor_name}
Consultation Date: {consultation_date}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔒 CONFIDENTIALITY NOTICE

This document contains confidential medical information protected by patient privacy laws.
Unauthorized access, use, or disclosure is strictly prohibited.

Hospital Management System • Confidential Medical Record
"""
            
            requests = [
                {
                    'insertText': {
                        'location': {'index': 1},
                        'text': content
                    }
                },
                # Format title as large centered heading
                {
                    'updateParagraphStyle': {
                        'range': {'startIndex': 1, 'endIndex': 30},
                        'paragraphStyle': {
                            'namedStyleType': 'HEADING_1',
                            'alignment': 'CENTER'
                        },
                        'fields': 'namedStyleType,alignment'
                    }
                },
                # Apply professional font
                {
                    'updateTextStyle': {
                        'range': {'startIndex': 1, 'endIndex': len(content)},
                        'textStyle': {
                            'weightedFontFamily': {'fontFamily': 'Calibri'},
                            'fontSize': {'magnitude': 11, 'unit': 'PT'}
                        },
                        'fields': 'weightedFontFamily,fontSize'
                    }
                }
            ]
            
            self.docs_service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            doc_info = self.drive_service.files().get(
                fileId=document_id,
                fields='webViewLink'
            ).execute()
            
            doc_url = doc_info.get('webViewLink')
            
            # Return structured data for programmatic use
            return {
                'success': True,
                'document_id': document_id,
                'document_url': doc_url,
                'patient_name': patient_name,
                'consultation_date': consultation_date,
                'message': f"✅ Doctor's Notes Created Successfully! Link: {doc_url}"
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"❌ Error creating doctor's notes: {str(e)}"
            }
    
    async def _arun(self, patient_name: str, consultation_date: str, chief_complaint: str,
                    examination_findings: str, diagnosis: str, treatment_plan: str, 
                    doctor_name: str) -> dict:
        return self._run(patient_name, consultation_date, chief_complaint, 
                        examination_findings, diagnosis, treatment_plan, doctor_name)


class CreateTreatmentPlanTool(BaseTool, DocsToolBase):
    """Tool for creating detailed treatment plans."""
    
    name: str = "create_treatment_plan"
    description: str = """Create comprehensive treatment plan for patient. 
    Includes goals, medications, lifestyle changes, and follow-up schedule."""
    args_schema: Type[BaseModel] = CreateTreatmentPlanInput
    
    docs_service: Optional[object] = Field(default=None, exclude=True)
    drive_service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'token.pickle'):
        BaseTool.__init__(self)
        DocsToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, patient_name: str, diagnosis: str, treatment_goals: List[str],
             medications: List[Dict[str, str]], follow_up_schedule: str,
             lifestyle_changes: Optional[List[str]] = None) -> str:
        try:
            # Create document
            doc = self.docs_service.documents().create(
                body={'title': f'Treatment Plan - {patient_name}'}
            ).execute()
            
            document_id = doc.get('documentId')
            
            # Format treatment goals
            goals_text = '\n'.join([f'{i}. {goal}' for i, goal in enumerate(treatment_goals, 1)])
            
            # Format medications
            meds_text = '\n'.join([
                f'  • {med.get("name", "Unknown")}\n'
                f'    Dosage: {med.get("dosage", "As prescribed")}\n'
                f'    Frequency: {med.get("frequency", "As directed")}\n'
                for med in medications
            ])
            
            # Format lifestyle changes
            lifestyle_section = ""
            if lifestyle_changes:
                lifestyle_text = '\n'.join([f'  • {change}' for change in lifestyle_changes])
                lifestyle_section = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏃 LIFESTYLE MODIFICATIONS

{lifestyle_text}
"""
            
            content = f"""COMPREHENSIVE TREATMENT PLAN

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 PATIENT INFORMATION

Patient Name: {patient_name}
Plan Created: {follow_up_schedule.split()[0] if follow_up_schedule else 'Today'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔬 DIAGNOSIS

{diagnosis}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 TREATMENT GOALS

{goals_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💊 PRESCRIBED MEDICATIONS

{meds_text}
{lifestyle_section}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 FOLLOW-UP SCHEDULE

{follow_up_schedule}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ IMPORTANT PATIENT GUIDELINES

• ✅ Take all medications exactly as prescribed
• ❌ Do not discontinue medication without consulting your doctor
• 📞 Report any side effects or adverse reactions immediately
• 📆 Attend all scheduled follow-up appointments
• 💪 Maintain prescribed lifestyle changes consistently
• 📝 Keep track of your symptoms and progress

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 PERSONALIZED CARE NOTE

This comprehensive treatment plan has been specifically tailored for {patient_name}.
Please follow the plan carefully and consult your healthcare provider for any concerns.

Hospital Management System • Quality Patient Care
"""
            
            requests = [
                {
                    'insertText': {
                        'location': {'index': 1},
                        'text': content
                    }
                },
                # Format title as large centered heading
                {
                    'updateParagraphStyle': {
                        'range': {'startIndex': 1, 'endIndex': 30},
                        'paragraphStyle': {
                            'namedStyleType': 'HEADING_1',
                            'alignment': 'CENTER'
                        },
                        'fields': 'namedStyleType,alignment'
                    }
                },
                # Apply professional font
                {
                    'updateTextStyle': {
                        'range': {'startIndex': 1, 'endIndex': len(content)},
                        'textStyle': {
                            'weightedFontFamily': {'fontFamily': 'Calibri'},
                            'fontSize': {'magnitude': 11, 'unit': 'PT'}
                        },
                        'fields': 'weightedFontFamily,fontSize'
                    }
                }
            ]
            
            self.docs_service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            doc_info = self.drive_service.files().get(
                fileId=document_id,
                fields='webViewLink'
            ).execute()
            
            return f"""✅ Treatment Plan Created Successfully!

📋 Treatment Plan - {patient_name}
🩺 Diagnosis: {diagnosis}
💊 Medications: {len(medications)} prescribed
🎯 Goals: {len(treatment_goals)} treatment objectives
🔗 Link: {doc_info.get('webViewLink')}

✅ Comprehensive treatment plan ready for patient.
"""
        
        except Exception as e:
            return f"❌ Error creating treatment plan: {str(e)}"
    
    async def _arun(self, patient_name: str, diagnosis: str, treatment_goals: List[str],
                    medications: List[Dict[str, str]], follow_up_schedule: str,
                    lifestyle_changes: Optional[List[str]] = None) -> str:
        return self._run(patient_name, diagnosis, treatment_goals, medications, 
                        follow_up_schedule, lifestyle_changes)


class ShareDocumentTool(BaseTool, DocsToolBase):
    """Tool for sharing Google Docs."""
    
    name: str = "share_google_doc"
    description: str = """Share Google Doc with patients or medical staff. 
    Set permissions: reader (view only), writer (edit), or commenter."""
    args_schema: Type[BaseModel] = ShareDocumentInput
    
    docs_service: Optional[object] = Field(default=None, exclude=True)
    drive_service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'token.pickle'):
        BaseTool.__init__(self)
        DocsToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, document_id: str, email: str, role: str = "reader") -> str:
        try:
            if role not in ['reader', 'writer', 'commenter']:
                return "❌ Error: Invalid role. Use 'reader', 'writer', or 'commenter'"
            
            # Share document
            permission = {
                'type': 'user',
                'role': role,
                'emailAddress': email
            }
            
            self.drive_service.permissions().create(
                fileId=document_id,
                body=permission,
                sendNotificationEmail=True
            ).execute()
            
            # Get document info
            doc_info = self.drive_service.files().get(
                fileId=document_id,
                fields='name, webViewLink'
            ).execute()
            
            return f"""✅ Document Shared Successfully!

📄 Document: {doc_info.get('name')}
📧 Shared with: {email}
🔐 Permission: {role}
🔗 Link: {doc_info.get('webViewLink')}

✅ Email notification sent to recipient.
"""
        
        except Exception as e:
            return f"❌ Error sharing document: {str(e)}"
    
    async def _arun(self, document_id: str, email: str, role: str = "reader") -> str:
        return self._run(document_id, email, role)


# ==================== READ DOCTOR NOTES TOOL ====================

class ReadDoctorNotesInput(BaseModel):
    """Input for reading doctor notes from Google Doc."""
    document_id: str = Field(description="Google Doc ID containing doctor notes")
    patient_id: Optional[str] = Field(default=None, description="Patient ID for context")


class ReadDoctorNotesTool(BaseTool, DocsToolBase):
    """
    Tool for reading doctor notes from Google Docs.
    
    Workflow:
    1. Doctor opens patient's Medical History Doc (created in Stage 3)
    2. Doctor adds diagnosis, treatment plan, prescriptions
    3. AI reads the document when patient asks about doctor's recommendations
    
    This enables doctors to use familiar Google Docs interface while AI provides
    the information to patients in a friendly, conversational way.
    """
    
    name: str = "read_doctor_notes"
    description: str = """Read doctor's notes, diagnosis, and treatment plan from a Google Doc.
    
    Use this when:
    - Patient asks: "What did the doctor say?"
    - Patient asks: "What's my diagnosis?"
    - Patient asks: "What treatment did the doctor recommend?"
    - Patient asks: "What medications did the doctor prescribe?"
    - You need to retrieve doctor's consultation notes
    
    Input: document_id (Google Doc ID)
    Output: Full text content of the doctor's notes
    """
    args_schema: Type[BaseModel] = ReadDoctorNotesInput
    
    docs_service: Optional[object] = Field(default=None, exclude=True)
    drive_service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'token.pickle'):
        BaseTool.__init__(self)
        DocsToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, document_id: str, patient_id: Optional[str] = None) -> Dict[str, any]:
        """
        Read doctor notes from Google Doc
        
        Args:
            document_id: Google Doc ID
            patient_id: Optional patient ID for context
        
        Returns:
            Dictionary with doctor notes content and metadata
        """
        try:
            # Get the document
            doc = self.docs_service.documents().get(documentId=document_id).execute()
            
            # Get document metadata
            doc_title = doc.get('title', 'Untitled')
            revision_id = doc.get('revisionId', 'Unknown')
            
            # Extract text content from the document
            content = doc.get('body', {}).get('content', [])
            
            # Build full text
            full_text = []
            for element in content:
                if 'paragraph' in element:
                    paragraph_elements = element.get('paragraph', {}).get('elements', [])
                    for para_element in paragraph_elements:
                        if 'textRun' in para_element:
                            text_content = para_element.get('textRun', {}).get('content', '')
                            if text_content.strip():  # Skip empty lines
                                full_text.append(text_content)
            
            # Join all text
            doctor_notes = ''.join(full_text)
            
            if not doctor_notes.strip():
                return {
                    "success": False,
                    "document_id": document_id,
                    "document_title": doc_title,
                    "message": "Doctor has not yet added notes to this document",
                    "notes": "",
                    "is_empty": True
                }
            
            # Try to parse sections (diagnosis, treatment, prescriptions)
            sections = self._parse_sections(doctor_notes)
            
            # Get last modified info from Drive API
            try:
                file_info = self.drive_service.files().get(
                    fileId=document_id,
                    fields='modifiedTime, lastModifyingUser'
                ).execute()
                
                last_modified = file_info.get('modifiedTime', 'Unknown')
                last_modifier = file_info.get('lastModifyingUser', {}).get('displayName', 'Unknown')
            except:
                last_modified = 'Unknown'
                last_modifier = 'Unknown'
            
            return {
                "success": True,
                "document_id": document_id,
                "document_title": doc_title,
                "patient_id": patient_id,
                "doctor_notes": doctor_notes,
                "sections": sections,
                "last_modified": last_modified,
                "last_modified_by": last_modifier,
                "revision_id": revision_id,
                "message": f"Successfully retrieved doctor notes from: {doc_title}",
                "is_empty": False
            }
            
        except Exception as e:
            return {
                "success": False,
                "document_id": document_id,
                "error": str(e),
                "message": f"Error reading doctor notes: {str(e)}",
                "is_empty": True
            }
    
    def _parse_sections(self, text: str) -> Dict[str, str]:
        """
        Parse common sections from doctor notes
        
        Looks for sections like:
        - Diagnosis
        - Treatment Plan
        - Prescriptions
        - Follow-up
        - Notes
        """
        sections = {}
        
        # Common section headers (case-insensitive)
        section_keywords = {
            'diagnosis': ['diagnosis', 'diagnosed with', 'condition'],
            'treatment': ['treatment plan', 'treatment', 'recommended treatment'],
            'prescriptions': ['prescription', 'medications', 'medicine'],
            'followup': ['follow-up', 'follow up', 'next visit'],
            'notes': ['doctor notes', 'observations', 'notes']
        }
        
        text_lower = text.lower()
        
        # Try to extract each section
        for section_name, keywords in section_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Find the keyword position
                    start_idx = text_lower.find(keyword)
                    
                    # Find the next section or end of text
                    end_idx = len(text)
                    for other_section, other_keywords in section_keywords.items():
                        if other_section != section_name:
                            for other_keyword in other_keywords:
                                other_idx = text_lower.find(other_keyword, start_idx + len(keyword))
                                if other_idx != -1 and other_idx < end_idx:
                                    end_idx = other_idx
                    
                    # Extract section content
                    section_content = text[start_idx:end_idx].strip()
                    sections[section_name] = section_content
                    break
        
        return sections
    
    async def _arun(self, document_id: str, patient_id: Optional[str] = None) -> Dict[str, any]:
        """Async version"""
        return self._run(document_id, patient_id)


# ==================== HELPER FUNCTION ====================

def get_all_docs_tools():
    """Get all Google Docs tools for the agent"""
    return [
        CreateDischargeSummaryTool(),
        CreateMedicalReportTool(),
        CreateDoctorNotesTool(),
        CreateTreatmentPlanTool(),
        ShareDocumentTool(),
        ReadDoctorNotesTool()  # NEW: Added reading tool
    ]


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("📄 GOOGLE DOCS TOOLS - Hospital Management")
    print("="*70)
    
    # Example: Create discharge summary
    print("\n1️⃣ Creating Discharge Summary...")
    tool1 = CreateDischargeSummaryTool()
    result1 = tool1._run(
        patient_name="Samarth Pawar",
        patient_id="REG2025001",
        admission_date="2025-10-15",
        discharge_date="2025-10-25",
        diagnosis="Successful surgical procedure completed",
        treatment_summary="Patient underwent planned surgical intervention. Post-operative recovery was excellent.",
        medications=["Aspirin 75mg - Once daily", "Vitamin D - Once daily", "Pain relief as needed"],
        doctor_name="Dr. Smith",
        followup_instructions="Follow-up appointment in 2 weeks. Avoid heavy lifting for 4 weeks."
    )
    print(result1)
    
    print("\n" + "="*70)
    print("✅ Docs Tools Test Complete!")
    print("="*70)
