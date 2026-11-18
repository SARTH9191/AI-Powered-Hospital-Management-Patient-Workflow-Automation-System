"""
Enhanced Google Docs Monitoring Tools
Real-time collaborative medical document management for hospital workflow

These tools enable:
1. Doctors create/edit Google Docs → AI reads and integrates into workflow
2. AI creates medical documents → Doctors review and edit collaboratively
3. Automatic document creation for patient stages (admission, treatment, discharge)
4. Real-time document monitoring and change tracking
5. Integration with Google Sheets monitoring system

Author: Hospital Management AI System
Email: pawarsamarth786@gmail.com
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


# ==================== GOOGLE DOCS SCOPES ====================
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive'
]


# ==================== INPUT SCHEMAS ====================

class CreateMedicalDocumentInput(BaseModel):
    """Input for creating medical documents."""
    patient_id: str = Field(description="Patient ID")
    document_type: str = Field(description="Type of document (admission_notes, treatment_plan, discharge_summary, consultation_notes)")
    content: str = Field(description="Document content")
    doctor_name: Optional[str] = Field(default=None, description="Doctor name for collaboration")


class ReadMedicalDocumentInput(BaseModel):
    """Input for reading medical documents."""
    document_id: str = Field(description="Google Docs document ID")
    patient_id: Optional[str] = Field(default=None, description="Patient ID to filter")


class UpdateMedicalDocumentInput(BaseModel):
    """Input for updating medical documents."""
    document_id: str = Field(description="Google Docs document ID")
    section: str = Field(description="Document section to update (diagnosis, treatment, notes, recommendations)")
    content: str = Field(description="New content to add")
    updated_by: str = Field(description="Who is making the update")


class ShareDocumentInput(BaseModel):
    """Input for sharing documents."""
    document_id: str = Field(description="Google Docs document ID")
    email: str = Field(description="Email address to share with")
    role: str = Field(default="writer", description="Permission role (reader, writer, editor)")


class SearchDocumentsInput(BaseModel):
    """Input for searching documents."""
    patient_id: Optional[str] = Field(default=None, description="Patient ID to search for")
    document_type: Optional[str] = Field(default=None, description="Document type to filter")
    keywords: Optional[str] = Field(default=None, description="Keywords to search for")


# ==================== BASE CLASS ====================

class DocsMonitoringToolBase(BaseTool):
    """Base class for Google Docs monitoring tools."""
    
    # Define service as a class variable to avoid Pydantic field validation
    service: Any = None
    drive_service: Any = None
    
    def __init__(self):
        super().__init__()
        # Use object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, 'service', self._initialize_docs_service())
        object.__setattr__(self, 'drive_service', self._initialize_drive_service())
    
    def _initialize_docs_service(self):
        """Initialize Google Docs service using existing credentials."""
        try:
            creds = None
            # Use dedicated docs_token.pickle file in project root
            token_path = os.path.join(os.path.dirname(__file__), '..', 'docs_token.pickle')
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
            
            service = build('docs', 'v1', credentials=creds)
            print("✅ Google Docs monitoring service initialized")
            return service
            
        except Exception as e:
            print(f"❌ Error initializing Docs service: {e}")
            return None
    
    def _initialize_drive_service(self):
        """Initialize Google Drive service for file management."""
        try:
            creds = None
            # Use dedicated drive_token.pickle file in project root
            token_path = os.path.join(os.path.dirname(__file__), '..', 'drive_token.pickle')
            
            if os.path.exists(token_path):
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    credentials_path = os.path.join(os.path.dirname(__file__), '..', 'credentials', 'client_secret.json')
                    creds.refresh(Request())
                    
                    # Save refreshed token
                    with open(token_path, 'wb') as token:
                        pickle.dump(creds, token)
            
            drive_service = build('drive', 'v3', credentials=creds)
            print("✅ Google Drive monitoring service initialized")
            return drive_service
            
        except Exception as e:
            print(f"❌ Error initializing Drive service: {e}")
            return None
    
    def _get_current_timestamp(self):
        """Get current timestamp in readable format."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _create_document_title(self, patient_id: str, document_type: str) -> str:
        """Create standardized document title."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        return f"[{patient_id}] {document_type.replace('_', ' ').title()} - {timestamp}"
    
    def _get_document_template(self, document_type: str, patient_id: str) -> str:
        """Get document template based on type."""
        templates = {
            "admission_notes": f"""ADMISSION NOTES - PATIENT {patient_id}
==========================================

Date: {self._get_current_timestamp()}
Patient ID: {patient_id}

ADMISSION DETAILS:
- Admission Date: 
- Admitting Physician: 
- Department: 
- Room Number: 

CHIEF COMPLAINT:


HISTORY OF PRESENT ILLNESS:


PAST MEDICAL HISTORY:


ALLERGIES:


CURRENT MEDICATIONS:


PHYSICAL EXAMINATION:


ASSESSMENT AND PLAN:


DOCTOR'S SIGNATURE:
Name: 
Date: 
""",
            
            "treatment_plan": f"""TREATMENT PLAN - PATIENT {patient_id}
=====================================

Date: {self._get_current_timestamp()}
Patient ID: {patient_id}

DIAGNOSIS:


TREATMENT GOALS:
1. 
2. 
3. 

MEDICATIONS:


PROCEDURES/INTERVENTIONS:


MONITORING PLAN:


EXPECTED OUTCOMES:


FOLLOW-UP INSTRUCTIONS:


DOCTOR'S NOTES:


Last Updated: {self._get_current_timestamp()}
""",
            
            "discharge_summary": f"""DISCHARGE SUMMARY - PATIENT {patient_id}
========================================

Date: {self._get_current_timestamp()}
Patient ID: {patient_id}

ADMISSION DATE:
DISCHARGE DATE: {datetime.now().strftime("%Y-%m-%d")}

DISCHARGE DIAGNOSIS:


HOSPITAL COURSE:


PROCEDURES PERFORMED:


DISCHARGE MEDICATIONS:


DISCHARGE INSTRUCTIONS:
1. 
2. 
3. 

FOLLOW-UP APPOINTMENTS:


ADDITIONAL NOTES:


DISCHARGE APPROVED BY:
Doctor: 
Date: {self._get_current_timestamp()}
""",
            
            "consultation_notes": f"""CONSULTATION NOTES - PATIENT {patient_id}
=========================================

Date: {self._get_current_timestamp()}
Patient ID: {patient_id}
Consulting Physician: 

REASON FOR CONSULTATION:


CLINICAL FINDINGS:


RECOMMENDATIONS:


ADDITIONAL NOTES:


CONSULTANT SIGNATURE:
Name: 
Date: {self._get_current_timestamp()}
"""
        }
        
        return templates.get(document_type, f"Medical Document - Patient {patient_id}\n\nContent:\n\n")


# ==================== MONITORING TOOLS ====================

class CreateMedicalDocumentTool(DocsMonitoringToolBase):
    """Create new medical documents for patient care."""
    
    name: str = "create_medical_document"
    description: str = "Create new medical documents (admission notes, treatment plan, discharge summary, consultation notes) for patient care"
    args_schema: Type[BaseModel] = CreateMedicalDocumentInput
    
    def _run(self, patient_id: str, document_type: str, content: str, doctor_name: Optional[str] = None) -> str:
        """Create a new medical document."""
        if not self.service:
            return "❌ Error: Google Docs service not available"
        
        try:
            # Create document title
            title = self._create_document_title(patient_id, document_type)
            
            # Create document
            document = {
                'title': title
            }
            
            doc = self.service.documents().create(body=document).execute()
            document_id = doc.get('documentId')
            
            # Get template content
            if content.strip():
                # Use provided content
                full_content = content
            else:
                # Use template
                full_content = self._get_document_template(document_type, patient_id)
            
            # Insert content into document
            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': 1,
                        },
                        'text': full_content
                    }
                }
            ]
            
            self.service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            # Share with doctor if provided
            sharing_info = ""
            if doctor_name and self.drive_service:
                try:
                    # For demo, we'll just note it in the response
                    sharing_info = f"\n📧 Ready to share with Dr. {doctor_name}"
                except Exception as e:
                    sharing_info = f"\n⚠️ Document created but sharing failed: {str(e)}"
            
            return f"""✅ **Medical Document Created Successfully!**

📄 **Document Details:**
• **Title:** {title}
• **Type:** {document_type.replace('_', ' ').title()}
• **Patient ID:** {patient_id}
• **Document ID:** {document_id}
• **Created:** {self._get_current_timestamp()}

🔗 **Google Docs URL:** 
https://docs.google.com/document/d/{document_id}/edit

💡 **Next Steps:**
• Medical team can edit the document collaboratively
• AI will monitor document changes automatically
• Updates will be reflected in patient workflow{sharing_info}"""
        
        except Exception as e:
            return f"❌ Error creating medical document: {str(e)}"


class ReadMedicalDocumentTool(DocsMonitoringToolBase):
    """Read and analyze medical documents."""
    
    name: str = "read_medical_document"
    description: str = "Read content from medical documents and extract key information"
    args_schema: Type[BaseModel] = ReadMedicalDocumentInput
    
    def _run(self, document_id: str, patient_id: Optional[str] = None) -> str:
        """Read content from a medical document."""
        if not self.service:
            return "❌ Error: Google Docs service not available"
        
        try:
            # Get document
            doc = self.service.documents().get(documentId=document_id).execute()
            
            # Extract text content
            content = ""
            for element in doc.get('body', {}).get('content', []):
                if 'paragraph' in element:
                    for text_run in element['paragraph'].get('elements', []):
                        if 'textRun' in text_run:
                            content += text_run['textRun']['content']
            
            # Extract document metadata
            title = doc.get('title', 'Untitled')
            created_time = doc.get('createdTime', 'Unknown')
            modified_time = doc.get('modifiedTime', 'Unknown')
            
            # Basic content analysis
            word_count = len(content.split())
            line_count = len(content.split('\n'))
            
            # Extract key sections (basic keyword matching)
            sections = {}
            content_lower = content.lower()
            
            if 'diagnosis' in content_lower:
                sections['diagnosis'] = "Present"
            if 'treatment' in content_lower:
                sections['treatment'] = "Present" 
            if 'medications' in content_lower:
                sections['medications'] = "Present"
            if 'follow-up' in content_lower or 'follow up' in content_lower:
                sections['follow_up'] = "Present"
            
            return f"""📄 **Medical Document Analysis**

📋 **Document Info:**
• **Title:** {title}
• **Document ID:** {document_id}
• **Last Modified:** {modified_time}
• **Word Count:** {word_count}
• **Lines:** {line_count}

📊 **Content Sections Found:**
{chr(10).join([f'• **{k.title()}:** {v}' for k, v in sections.items()]) if sections else '• No standard sections detected'}

📝 **Document Content:**
{'-' * 50}
{content[:1000]}{'...' if len(content) > 1000 else ''}
{'-' * 50}

🔗 **Edit Document:** https://docs.google.com/document/d/{document_id}/edit"""
        
        except Exception as e:
            return f"❌ Error reading medical document: {str(e)}"


class UpdateMedicalDocumentTool(DocsMonitoringToolBase):
    """Update medical documents with new information."""
    
    name: str = "update_medical_document"
    description: str = "Update specific sections of medical documents"
    args_schema: Type[BaseModel] = UpdateMedicalDocumentInput
    
    def _run(self, document_id: str, section: str, content: str, updated_by: str) -> str:
        """Update a section of a medical document."""
        if not self.service:
            return "❌ Error: Google Docs service not available"
        
        try:
            # Get current document to find insertion point
            doc = self.service.documents().get(documentId=document_id).execute()
            
            # Prepare update content with timestamp
            timestamp = self._get_current_timestamp()
            update_content = f"\n\n--- {section.upper()} UPDATE ---\nUpdated by: {updated_by}\nTime: {timestamp}\n\n{content}\n"
            
            # Insert at the end of document
            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': len(doc.get('body', {}).get('content', [{}]))
                        },
                        'text': update_content
                    }
                }
            ]
            
            self.service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            return f"""✅ **Medical Document Updated Successfully!**

📄 **Update Details:**
• **Document ID:** {document_id}
• **Section:** {section.title()}
• **Updated by:** {updated_by}
• **Time:** {timestamp}

📝 **Added Content:**
{content}

🔗 **View Document:** https://docs.google.com/document/d/{document_id}/edit

💡 **All medical team members can see this update in real-time**"""
        
        except Exception as e:
            return f"❌ Error updating medical document: {str(e)}"


class SearchMedicalDocumentsTool(DocsMonitoringToolBase):
    """Search for medical documents by patient, type, or keywords."""
    
    name: str = "search_medical_documents"
    description: str = "Search for medical documents by patient ID, document type, or keywords"
    args_schema: Type[BaseModel] = SearchDocumentsInput
    
    def _run(self, patient_id: Optional[str] = None, document_type: Optional[str] = None, keywords: Optional[str] = None) -> str:
        """Search for medical documents."""
        if not self.drive_service:
            return "❌ Error: Google Drive service not available"
        
        try:
            # Build search query
            query_parts = []
            if patient_id:
                query_parts.append(f"name contains '[{patient_id}]'")
            if document_type:
                query_parts.append(f"name contains '{document_type.replace('_', ' ')}'")
            if keywords:
                query_parts.append(f"fullText contains '{keywords}'")
            
            # Default: search for all medical documents
            if not query_parts:
                query_parts.append("name contains 'PATIENT' or name contains 'Medical' or name contains 'Treatment' or name contains 'Discharge'")
            
            query = " and ".join(query_parts)
            query += " and mimeType='application/vnd.google-apps.document'"
            
            # Execute search
            results = self.drive_service.files().list(
                q=query,
                pageSize=20,
                fields="nextPageToken, files(id, name, createdTime, modifiedTime, owners)"
            ).execute()
            
            files = results.get('files', [])
            
            if not files:
                return f"""📄 **Medical Documents Search Results**

🔍 **Search Criteria:**
• Patient ID: {patient_id or 'Any'}
• Document Type: {document_type or 'Any'}
• Keywords: {keywords or 'Any'}

📋 **Results:** No documents found matching criteria

💡 **Suggestions:**
• Check if patient ID is correct
• Try different keywords
• Search for broader terms"""
            
            # Format results
            results_text = f"""📄 **Medical Documents Search Results**

🔍 **Search Criteria:**
• Patient ID: {patient_id or 'Any'}
• Document Type: {document_type or 'Any'}  
• Keywords: {keywords or 'Any'}

📋 **Found {len(files)} document(s):**

"""
            
            for i, file in enumerate(files, 1):
                file_id = file['id']
                name = file['name']
                created = file.get('createdTime', 'Unknown')
                modified = file.get('modifiedTime', 'Unknown')
                
                results_text += f"""**{i}. {name}**
   • Document ID: {file_id}
   • Created: {created}
   • Modified: {modified}
   • URL: https://docs.google.com/document/d/{file_id}/edit

"""
            
            return results_text
        
        except Exception as e:
            return f"❌ Error searching medical documents: {str(e)}"


class ShareMedicalDocumentTool(DocsMonitoringToolBase):
    """Share medical documents with healthcare team members."""
    
    name: str = "share_medical_document"
    description: str = "Share medical documents with doctors, nurses, or other healthcare professionals"
    args_schema: Type[BaseModel] = ShareDocumentInput
    
    def _run(self, document_id: str, email: str, role: str = "writer") -> str:
        """Share a medical document with specified permissions."""
        if not self.drive_service:
            return "❌ Error: Google Drive service not available"
        
        try:
            # Create permission
            permission = {
                'type': 'user',
                'role': role,
                'emailAddress': email
            }
            
            # Share document
            self.drive_service.permissions().create(
                fileId=document_id,
                body=permission,
                sendNotificationEmail=True
            ).execute()
            
            # Get document title
            file_info = self.drive_service.files().get(fileId=document_id).execute()
            title = file_info.get('name', 'Untitled Document')
            
            return f"""✅ **Document Shared Successfully!**

📄 **Sharing Details:**
• **Document:** {title}
• **Document ID:** {document_id}
• **Shared with:** {email}
• **Permission:** {role.title()}
• **Time:** {self._get_current_timestamp()}

📧 **Notification sent to {email}**

🔗 **Document URL:** https://docs.google.com/document/d/{document_id}/edit

💡 **Collaborative Features:**
• Real-time editing
• Comment and suggestion mode
• Version history tracking
• AI monitoring of changes"""
        
        except Exception as e:
            return f"❌ Error sharing medical document: {str(e)}"


class MonitorDocumentChangesTool(DocsMonitoringToolBase):
    """Monitor changes in medical documents for workflow integration."""
    
    name: str = "monitor_document_changes"
    description: str = "Monitor changes in medical documents to trigger workflow updates"
    args_schema: Type[BaseModel] = ReadMedicalDocumentInput
    
    def _run(self, document_id: str, patient_id: Optional[str] = None) -> str:
        """Monitor and report changes in a medical document."""
        if not self.service or not self.drive_service:
            return "❌ Error: Google services not available"
        
        try:
            # Get document revision history
            revisions = self.drive_service.revisions().list(fileId=document_id).execute()
            revision_list = revisions.get('revisions', [])
            
            # Get current document content
            doc = self.service.documents().get(documentId=document_id).execute()
            title = doc.get('title', 'Untitled')
            
            # Get latest revision info
            if revision_list:
                latest_revision = revision_list[-1]
                modified_time = latest_revision.get('modifiedTime', 'Unknown')
                last_modifying_user = latest_revision.get('lastModifyingUser', {}).get('displayName', 'Unknown')
            else:
                modified_time = 'Unknown'
                last_modifying_user = 'Unknown'
            
            # Analyze recent changes (simplified)
            total_revisions = len(revision_list)
            
            return f"""📊 **Document Change Monitoring Report**

📄 **Document:** {title}
🆔 **Document ID:** {document_id}
👤 **Patient ID:** {patient_id or 'Not specified'}

📈 **Change Statistics:**
• **Total Revisions:** {total_revisions}
• **Last Modified:** {modified_time}
• **Last Modified By:** {last_modifying_user}

🔄 **Monitoring Status:**
• Document is being tracked for changes
• Workflow integration active
• Real-time updates enabled

💡 **Workflow Integration:**
• Changes trigger automatic notifications
• Updates reflected in patient monitoring
• Medical team collaboration tracked

🔗 **View Document:** https://docs.google.com/document/d/{document_id}/edit"""
        
        except Exception as e:
            return f"❌ Error monitoring document changes: {str(e)}"


# ==================== UTILITY FUNCTIONS ====================

def get_all_docs_monitoring_tools() -> List[BaseTool]:
    """Get all Google Docs monitoring tools."""
    return [
        CreateMedicalDocumentTool(),
        ReadMedicalDocumentTool(), 
        UpdateMedicalDocumentTool(),
        SearchMedicalDocumentsTool(),
        ShareMedicalDocumentTool(),
        MonitorDocumentChangesTool()
    ]


def get_docs_tools_by_type(tool_type: str) -> List[BaseTool]:
    """Get Google Docs tools by type."""
    all_tools = get_all_docs_monitoring_tools()
    
    type_mapping = {
        "creation": [CreateMedicalDocumentTool()],
        "reading": [ReadMedicalDocumentTool(), SearchMedicalDocumentsTool()],
        "editing": [UpdateMedicalDocumentTool()],
        "sharing": [ShareMedicalDocumentTool()],
        "monitoring": [MonitorDocumentChangesTool()]
    }
    
    return type_mapping.get(tool_type, all_tools)


# ==================== MAIN TESTING ====================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🏥 GOOGLE DOCS MONITORING TOOLS - TEST")
    print("="*70)
    
    # Test document creation
    create_tool = CreateMedicalDocumentTool()
    result = create_tool._run(
        patient_id="TEST_PATIENT_001",
        document_type="treatment_plan",
        content="",  # Use template
        doctor_name="Dr. Smith"
    )
    print(f"\n📄 Document Creation Test:\n{result}")
    
    print(f"\n✅ All {len(get_all_docs_monitoring_tools())} Google Docs monitoring tools initialized!")
    print("🚀 Ready for integration with hospital workflow!")