"""
Unified Patient Document Tool
Creates and manages a SINGLE Google Doc for the entire patient workflow
Both AI Agent and Doctor can read and update this document bidirectionally
"""

from typing import Dict, Any, Optional, List
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import json
import pickle
from datetime import datetime

# Google API scopes
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file'
]

DOCTOR_EMAIL = "pawarsamarth786@gmail.com"


class UnifiedPatientDocumentTool:
    """
    Manages a single Google Doc for the entire patient workflow
    - Creates doc at Stage 3
    - AI Agent updates doc with analysis
    - Doctor reviews and updates decisions
    - AI Agent reads doctor's decisions
    - Continues throughout all stages
    """
    
    def __init__(self):
        self.creds = self._get_credentials()
        self.docs_service = build('docs', 'v1', credentials=self.creds)
        self.drive_service = build('drive', 'v3', credentials=self.creds)
    
    def _get_credentials(self):
        """Get Google API credentials using service account or OAuth"""
        from google.oauth2 import service_account
        
        # Try service account first (optional, for production deployments)
        service_account_file = 'credentials/service_account.json'
        
        if os.path.exists(service_account_file):
            try:
                creds = service_account.Credentials.from_service_account_file(
                    service_account_file,
                    scopes=SCOPES
                )
                print("✅ Using service account credentials for Google Docs")
                return creds
            except Exception as sa_err:
                print(f"⚠️ Service account failed: {sa_err}, falling back to OAuth")
                import traceback
                traceback.print_exc()
        
        # Use OAuth tokens (client_secret.json) - standard for development
        print("✅ Using OAuth credentials (client_secret.json + docs_token.pickle)")
        creds = None
        token_path = 'credentials/docs_token.pickle'
        
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"❌ Token refresh failed: {e}")
                    print("\n💡 SOLUTION: Run this command to regenerate OAuth token:")
                    print("   python generate_docs_token.py\n")
                    # Delete invalid token
                    if os.path.exists(token_path):
                        os.remove(token_path)
                    raise
            else:
                # Try both possible credential file names
                cred_file = 'credentials/client_secret.json'
                if not os.path.exists(cred_file):
                    cred_file = 'credentials/credentials.json'
                
                flow = InstalledAppFlow.from_client_secrets_file(cred_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        return creds
    
    def create_patient_workflow_doc(
        self,
        patient_id: str,
        patient_name: str,
        patient_email: str,
        medical_history: str,
        ai_analysis: str,
        recommended_tests: List[str]
    ) -> Dict[str, Any]:
        """
        Create the unified workflow document for patient
        This doc will be used throughout the entire workflow
        """
        
        try:
            # Create document title
            doc_title = f"Patient Workflow - {patient_name} ({patient_id})"
            
            # Create the document
            document = self.docs_service.documents().create(
                body={'title': doc_title}
            ).execute()
            
            doc_id = document.get('documentId')
            
            print(f"✅ Created workflow document: {doc_id}")
            
            # Build initial content
            content = self._build_initial_content(
                patient_id=patient_id,
                patient_name=patient_name,
                patient_email=patient_email,
                medical_history=medical_history,
                ai_analysis=ai_analysis,
                recommended_tests=recommended_tests,
                visit_number=1  # Default to visit 1 for new workflow docs
            )
            
            # Insert content into document
            requests = [
                {
                    'insertText': {
                        'location': {'index': 1},
                        'text': content
                    }
                }
            ]
            
            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            
            print(f"✅ Added initial content to document")
            
            # Share with doctor
            self._share_doc_with_doctor(doc_id)
            
            doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
            
            return {
                'success': True,
                'doc_id': doc_id,
                'doc_url': doc_url,
                'message': 'Workflow document created and shared with doctor',
                'shared_with': DOCTOR_EMAIL
            }
            
        except Exception as e:
            print(f"❌ Error creating workflow document: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_initial_content(
        self,
        patient_id: str,
        patient_name: str,
        patient_email: str,
        medical_history: str,
        ai_analysis: str,
        recommended_tests: List[str],
        visit_number: int = 1
    ) -> str:
        """Build initial document content"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PATIENT WORKFLOW DOCUMENT
City Hospital - AI-Assisted Healthcare
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 PATIENT INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Patient ID: {patient_id}
Patient Name: {patient_name}
Email: {patient_email}
Document Created: {timestamp}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 SECTION 1: MEDICAL HISTORY (Stage 3)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Patient's Medical History:
{medical_history}

Updated by: AI Agent
Last Updated: {timestamp}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 SECTION 2: AI ANALYSIS (Stage 3)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AI Medical Analysis:
{ai_analysis}

Recommended Tests:
{self._format_test_list(recommended_tests)}

Updated by: AI Agent
Last Updated: {timestamp}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👨‍⚕️ SECTION 3: DOCTOR'S DECISION (Stage 4)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ DOCTOR: PLEASE UPDATE THIS SECTION ⚠️

Doctor's Decision: [PENDING - Please write: APPROVE / MODIFY / REJECT]

Approved Tests: [PENDING - List approved tests, one per line]

Additional Tests Required: [Optional - Add any additional tests needed]

Doctor's Assessment: [PENDING - Your medical opinion]

⚠️ IMPORTANT: AI Agent is waiting for your decision to proceed ⚠️

Updated by: [PENDING]
Last Updated: [PENDING]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧪 SECTION 4: LAB TEST SCHEDULING (Stage 5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Will be updated by AI Agent after doctor approval]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 SECTION 5: LAB RESULTS (Stage 6)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Will be updated with lab results]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👨‍⚕️ SECTION 6: POST-LAB DOCTOR CONSULTATION (Stage 7)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ DOCTOR: Please complete the fields below after reviewing lab results ⚠️
💡 IMPORTANT: Replace ALL placeholder text with actual patient information

👨‍⚕️ DIAGNOSIS:
[Write primary diagnosis - DO NOT leave this placeholder, write actual diagnosis]
Example: "Type 2 Diabetes Mellitus with poor glycemic control" or "Normal - No abnormalities detected"


✅ DECISION: (Choose ONE by marking ✓ or X - This determines next workflow stage)
☐ NO ADMISSION - Outpatient treatment (→ proceeds to Stage 11: Prescription & Follow-up)
☐ HOSPITAL ADMISSION REQUIRED (→ proceeds to Stage 8: Admission Planning)


📋 Treatment Plan:
[Write detailed treatment plan - DO NOT leave placeholder]
Include: medications, lifestyle changes, monitoring requirements, diet modifications
If no treatment needed, write: "NO TREATMENT REQUIRED - Continue regular health monitoring"


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💊 SECTION 7: PRESCRIPTION & FOLLOW-UP (Stage 11)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ DOCTOR: Complete this section after consultation ⚠️
💡 IMPORTANT: If no prescription needed, write "NO PRESCRIPTION NEEDED" or "NO MEDICATIONS"
💡 If no follow-up needed, write "NO FOLLOW-UP REQUIRED"

💊 MEDICATIONS PRESCRIBED:
(If NO medications needed, write: "NO PRESCRIPTION NEEDED - Outpatient care only")

1. [Medication name] - [Dosage, frequency, duration]
   Example: Metformin 1000mg - Take twice daily with meals for 3 months
2. [Medication name] - [Dosage, frequency, duration]
3. [Medication name] - [Dosage, frequency, duration]

📅 FOLLOW-UP APPOINTMENT
(Specify when patient should return for review, or write "NO FOLLOW-UP REQUIRED")

• Date: [Specify date - e.g., 2025-12-15 or "2 weeks from today"]
• Purpose: [Reason for follow-up - e.g., "Recheck blood glucose and BP"]
• Tests Required: [Any tests needed - e.g., "Repeat HbA1c, Lipid Profile" or "None"]
• Location: [Where to come - e.g., "City Hospital Outpatient Clinic"]


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ SECTION 8: WORKFLOW COMPLETION (Stage 12)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 AI AGENT: This section auto-updates when workflow completes

Status: PENDING
Completion Date: [Auto-filled on completion]
Visit Number: {visit_number}
Next Visit: Patient can type "new visit" to start another consultation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
END OF DOCUMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return content
    
    def _format_test_list(self, tests: List[str]) -> str:
        """Format test list"""
        if not tests:
            return "No tests recommended"
        return "\n".join([f"  • {test}" for test in tests])
    
    def _share_doc_with_doctor(self, doc_id: str):
        """Share document with doctor"""
        try:
            permission = {
                'type': 'user',
                'role': 'writer',
                'emailAddress': DOCTOR_EMAIL
            }
            
            self.drive_service.permissions().create(
                fileId=doc_id,
                body=permission,
                fields='id',
                sendNotificationEmail=True
            ).execute()
            
            print(f"✅ Shared document with {DOCTOR_EMAIL}")
            
        except Exception as e:
            print(f"⚠️ Error sharing document: {e}")
    
    def read_doctor_decision(self, doc_id: str) -> Dict[str, Any]:
        """
        Read doctor's decision from Section 3 of the document
        Checks if doctor has updated their decision
        """
        try:
            # Get document content
            document = self.docs_service.documents().get(
                documentId=doc_id
            ).execute()
            
            content = document.get('body').get('content')
            full_text = self._extract_text_from_document(content)
            
            # Extract Section 3 content - try multiple formats
            section3 = None
            possible_markers = [
                "SECTION 3: DOCTOR'S DECISION",
                "3: DOCTOR'S DECISION",
                "👨‍⚕️ SECTION 3:",
                "SECTION 3: DOCTOR"
            ]
            
            for marker in possible_markers:
                section3 = self._extract_section(full_text, marker)
                if section3:
                    break
            
            if not section3:
                return {
                    'success': False,
                    'error': 'Could not find Section 3 in document'
                }
            
            # Parse doctor's decision
            decision = self._parse_doctor_decision(section3)
            
            # Check if doctor has updated
            if decision.get('doctor_decision') == '[PENDING':
                return {
                    'success': False,
                    'pending': True,
                    'message': 'Doctor has not yet updated their decision'
                }
            
            return {
                'success': True,
                'decision': decision.get('doctor_decision', ''),
                'approved_tests': decision.get('approved_tests', []),
                'additional_tests': decision.get('additional_tests', []),
                'doctor_assessment': decision.get('doctor_assessment', ''),
                'updated_by': decision.get('updated_by', ''),
                'last_updated': decision.get('last_updated', '')
            }
            
        except Exception as e:
            print(f"❌ Error reading doctor decision: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_text_from_document(self, content: List[Dict]) -> str:
        """Extract plain text from document content"""
        text = ""
        for element in content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                for text_run in paragraph.get('elements', []):
                    if 'textRun' in text_run:
                        text += text_run['textRun']['content']
        return text
    
    def _extract_section(self, full_text: str, section_header: str) -> str:
        """Extract content of a specific section"""
        try:
            start_marker = section_header
            end_marker = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            
            start_idx = full_text.find(start_marker)
            if start_idx == -1:
                return ""
            
            # Find next section divider after this section
            next_section_idx = full_text.find(end_marker, start_idx + len(start_marker) + 50)
            if next_section_idx == -1:
                section_content = full_text[start_idx:]
            else:
                section_content = full_text[start_idx:next_section_idx]
            
            return section_content
            
        except Exception as e:
            print(f"⚠️ Error extracting section: {e}")
            return ""
    
    def _parse_doctor_decision(self, section_text: str) -> Dict[str, Any]:
        """Parse doctor's decision from section text"""
        decision_data = {}
        
        # Extract doctor's decision
        if "Doctor's Decision:" in section_text:
            lines = section_text.split('\n')
            for i, line in enumerate(lines):
                if "Doctor's Decision:" in line:
                    decision_data['doctor_decision'] = line.split(':', 1)[1].strip()
                
                elif "Approved Tests:" in line:
                    # Collect approved tests (next few lines until we hit another field)
                    tests = []
                    j = i + 1
                    while j < len(lines) and not any(marker in lines[j] for marker in ['Additional Tests', 'Doctor\'s Assessment', 'Updated by', '━━━']):
                        test_line = lines[j].strip()
                        if test_line and test_line != '[PENDING - List approved tests, one per line]':
                            # Remove bullet points or dashes
                            test_line = test_line.lstrip('•-– ').strip()
                            if test_line and not test_line.startswith('['):
                                tests.append(test_line)
                        j += 1
                    decision_data['approved_tests'] = tests
                
                elif "Additional Tests Required:" in line:
                    additional = line.split(':', 1)[1].strip()
                    if additional and not additional.startswith('['):
                        decision_data['additional_tests'] = [additional]
                    else:
                        decision_data['additional_tests'] = []
                
                elif "Doctor's Assessment:" in line:
                    assessment = line.split(':', 1)[1].strip()
                    decision_data['doctor_assessment'] = assessment
                
                elif "Updated by:" in line:
                    updated_by = line.split(':', 1)[1].strip()
                    decision_data['updated_by'] = updated_by
                
                elif "Last Updated:" in line:
                    last_updated = line.split(':', 1)[1].strip()
                    decision_data['last_updated'] = last_updated
        
        return decision_data
    
    def update_section(
        self,
        doc_id: str,
        section_name: str,
        content: str,
        updated_by: str = "AI Agent"
    ) -> Dict[str, Any]:
        """
        Update a specific section of the document
        Used by AI Agent to update sections throughout workflow
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Get current document
            document = self.docs_service.documents().get(
                documentId=doc_id
            ).execute()
            
            full_content = document.get('body').get('content')
            full_text = self._extract_text_from_document(full_content)
            
            # Find section location
            section_header = f"SECTION {section_name}"
            section_start = full_text.find(section_header)
            
            if section_start == -1:
                return {
                    'success': False,
                    'error': f'Section {section_name} not found'
                }
            
            # Find next section divider
            divider = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            next_divider = full_text.find(divider, section_start + len(section_header) + 50)
            
            if next_divider == -1:
                return {
                    'success': False,
                    'error': 'Could not find section boundaries'
                }
            
            # Calculate character positions for deletion and insertion
            # Note: Google Docs API uses character indices starting from 1
            delete_start = section_start + len(section_header) + 1
            delete_end = next_divider
            
            # Build new content with metadata
            new_content = f"\n\n{content}\n\nUpdated by: {updated_by}\nLast Updated: {timestamp}\n\n"
            
            # Perform update: delete old content, insert new content
            requests = [
                {
                    'deleteContentRange': {
                        'range': {
                            'startIndex': delete_start,
                            'endIndex': delete_end
                        }
                    }
                },
                {
                    'insertText': {
                        'location': {'index': delete_start},
                        'text': new_content
                    }
                }
            ]
            
            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            
            print(f"✅ Updated {section_name} in document")
            
            return {
                'success': True,
                'message': f'Section {section_name} updated successfully'
            }
            
        except Exception as e:
            print(f"❌ Error updating section: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Standalone functions for easy import
def create_workflow_doc(
    patient_id: str,
    patient_name: str,
    patient_email: str,
    medical_history: str,
    ai_analysis: str,
    recommended_tests: List[str]
) -> Dict[str, Any]:
    """Create workflow document"""
    tool = UnifiedPatientDocumentTool()
    return tool.create_patient_workflow_doc(
        patient_id=patient_id,
        patient_name=patient_name,
        patient_email=patient_email,
        medical_history=medical_history,
        ai_analysis=ai_analysis,
        recommended_tests=recommended_tests
    )


def read_doctor_decision(doc_id: str) -> Dict[str, Any]:
    """Read doctor's decision from document"""
    tool = UnifiedPatientDocumentTool()
    return tool.read_doctor_decision(doc_id)


def update_doc_section(
    doc_id: str,
    section_name: str,
    content: str,
    updated_by: str = "AI Agent"
) -> Dict[str, Any]:
    """Update a section of the document"""
    tool = UnifiedPatientDocumentTool()
    return tool.update_section(doc_id, section_name, content, updated_by)


def read_doctor_consultation(doc_id: str) -> Dict[str, Any]:
    """
    Read Section 6 (POST-LAB CONSULTATION) from unified workflow document
    Parses doctor's consultation notes, diagnosis, and treatment decision
    """
    try:
        tool = UnifiedPatientDocumentTool()
        
        # Get document content
        doc = tool.docs_service.documents().get(documentId=doc_id).execute()
        content = doc.get('body', {}).get('content', [])
        
        # Extract full text
        full_text = ""
        for element in content:
            if 'paragraph' in element:
                for text_run in element['paragraph'].get('elements', []):
                    if 'textRun' in text_run:
                        full_text += text_run['textRun'].get('content', '')
        
        # Find Section 6 - try multiple formats
        possible_markers = [
            "6: POST-LAB CONSULTATION",
            "SECTION 6: POST-LAB",
            "👨‍⚕️ SECTION 6:",
            "6: POST-LAB DOCTOR CONSULTATION"
        ]
        
        section_6_marker = None
        for marker in possible_markers:
            if marker in full_text:
                section_6_marker = marker
                break
        
        if not section_6_marker:
            return {
                'success': False,
                'error': 'Section 6 not found in document'
            }
        
        # Find Section 7 - try multiple formats
        possible_end_markers = [
            "7: PRESCRIPTION",
            "SECTION 7:",
            "💊 SECTION 7:",
            "7: PRESCRIPTION & FOLLOW-UP"
        ]
        
        section_7_marker = None
        start_idx = full_text.find(section_6_marker)
        
        for marker in possible_end_markers:
            if marker in full_text[start_idx:]:
                section_7_marker = marker
                break
        
        # Extract Section 6 content
        end_idx = full_text.find(section_7_marker, start_idx) if section_7_marker else -1
        
        if end_idx == -1:
            section_6_text = full_text[start_idx:]
        else:
            section_6_text = full_text[start_idx:end_idx]
        
        print(f"📄 Section 6 content:\n{section_6_text[:500]}...")
        
        # Check if doctor has updated (look for pending indicators)
        pending_indicators = [
            "Doctor will update below",
            "pending",
            "Scheduling in progress",
            "waiting for doctor"
        ]
        
        is_pending = any(indicator in section_6_text.lower() for indicator in pending_indicators)
        
        if is_pending:
            return {
                'success': False,
                'pending': True,
                'message': 'Doctor has not completed consultation yet'
            }
        
        # Parse doctor's updates
        diagnosis = ""
        treatment_decision = ""
        treatment_plan = ""
        requires_admission = False
        requires_prescription = False
        requires_followup = False
        additional_notes = ""
        
        # Extract diagnosis - support multiple formats
        diagnosis_markers = ["DOCTOR'S DIAGNOSIS:", "Primary Diagnosis:", "DIAGNOSIS:", "📋 DIAGNOSIS:"]
        for marker in diagnosis_markers:
            if marker in section_6_text:
                diag_start = section_6_text.find(marker) + len(marker)
                # Find end - look for next section
                diag_end = section_6_text.find("\n\n", diag_start)
                if diag_end == -1:
                    for end_marker in ["TREATMENT DECISION:", "Treatment Plan:", "Hospital Admission Required:", "TREATMENT PLAN:"]:
                        temp_end = section_6_text.find(end_marker, diag_start)
                        if temp_end != -1:
                            diag_end = temp_end
                            break
                diagnosis = section_6_text[diag_start:diag_end].strip() if diag_end != -1 else section_6_text[diag_start:diag_start+500].strip()
                break
        
        # Extract treatment decision
        decision_markers = ["TREATMENT DECISION:", "Treatment Plan:", "TREATMENT PLAN:"]
        for marker in decision_markers:
            if marker in section_6_text:
                dec_start = section_6_text.find(marker) + len(marker)
                dec_end = section_6_text.find("\n\n", dec_start)
                if dec_end == -1:
                    for end_marker in ["TREATMENT PLAN:", "Hospital Admission Required:", "ADDITIONAL NOTES:", "Prescriptions:"]:
                        temp_end = section_6_text.find(end_marker, dec_start)
                        if temp_end != -1:
                            dec_end = temp_end
                            break
                treatment_decision = section_6_text[dec_start:dec_end].strip() if dec_end != -1 else section_6_text[dec_start:dec_start+500].strip()
                treatment_plan = treatment_decision  # In new format, Treatment Plan contains the plan
                break
        
        # Extract additional notes
        if "ADDITIONAL NOTES:" in section_6_text:
            notes_start = section_6_text.find("ADDITIONAL NOTES:") + len("ADDITIONAL NOTES:")
            notes_end = section_6_text.find("PRESCRIPTION REQUIRED:", notes_start)
            if notes_end == -1:
                notes_end = section_6_text.find("\n\nUpdated by:", notes_start)
            additional_notes = section_6_text[notes_start:notes_end].strip()
        
        # Check admission requirement - support multiple formats including new checkbox format
        admission_markers = [
            "☑ HOSPITAL ADMISSION REQUIRED",
            "☑ NO ADMISSION",
            "Hospital Admission Required: NO",
            "Hospital Admission Required: YES",
            "HOSPITAL ADMISSION REQUIRED",
            "NO ADMISSION - Outpatient treatment"
        ]
        
        # Check for checkbox format (☑ means checked/selected)
        if "☑ HOSPITAL ADMISSION REQUIRED" in section_6_text:
            requires_admission = True
        elif "☑ NO ADMISSION" in section_6_text or "☑ NO ADMISSION - Outpatient treatment" in section_6_text:
            requires_admission = False
        elif "Hospital Admission Required: NO" in section_6_text or "NO ADMISSION" in section_6_text:
            requires_admission = False
        elif "Hospital Admission Required: YES" in section_6_text:
            requires_admission = True
        else:
            # Default: no admission
            requires_admission = False
        
        # Check prescription required
        if "PRESCRIPTION REQUIRED:" in section_6_text:
            presc_line_start = section_6_text.find("PRESCRIPTION REQUIRED:")
            presc_line_end = section_6_text.find("\n", presc_line_start)
            presc_line = section_6_text[presc_line_start:presc_line_end]
            requires_prescription = "☑ Yes" in presc_line or "YES" in presc_line
        
        # Check if prescriptions are listed (alternative format)
        if "Prescriptions:" in section_6_text or "YOUR PRESCRIPTION" in section_6_text:
            presc_start = section_6_text.find("Prescriptions:") if "Prescriptions:" in section_6_text else section_6_text.find("YOUR PRESCRIPTION")
            presc_section = section_6_text[presc_start:presc_start+300]
            # If there's actual prescription content after "Prescriptions:", mark as required
            if any(med in presc_section.lower() for med in ["metformin", "amlodipine", "atorvastatin", "mg", "tablet", "capsule"]):
                requires_prescription = True
        
        # Check follow-up required
        if "FOLLOW-UP REQUIRED:" in section_6_text:
            follow_line_start = section_6_text.find("FOLLOW-UP REQUIRED:")
            follow_line_end = section_6_text.find("\n", follow_line_start)
            follow_line = section_6_text[follow_line_start:follow_line_end]
            requires_followup = "☑ Yes" in follow_line or "YES" in follow_line
        
        # Check if follow-up instructions exist (alternative format)
        if "Follow-up Instructions:" in section_6_text:
            followup_start = section_6_text.find("Follow-up Instructions:")
            followup_section = section_6_text[followup_start:followup_start+300]
            # If there's actual follow-up content, mark as required
            if any(word in followup_section.lower() for word in ["recheck", "repeat", "weeks", "months", "consultation"]):
                requires_followup = True
        
        print(f"✅ Parsed consultation:")
        print(f"   Diagnosis: {diagnosis[:50]}...")
        print(f"   Admission: {requires_admission}")
        print(f"   Prescription: {requires_prescription}")
        print(f"   Follow-up: {requires_followup}")
        
        return {
            'success': True,
            'pending': False,
            'diagnosis': diagnosis,
            'treatment_decision': treatment_decision,
            'treatment_plan': treatment_plan,
            'requires_admission': requires_admission,
            'requires_prescription': requires_prescription,
            'requires_followup': requires_followup,
            'additional_notes': additional_notes
        }
        
    except Exception as e:
        print(f"❌ Error reading doctor consultation: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def read_prescription_details(doc_id: str) -> Dict[str, Any]:
    """
    Read Section 7 (PRESCRIPTION & FOLLOW-UP) from unified workflow document
    Parses doctor's prescription details, medications, and follow-up schedule
    """
    try:
        tool = UnifiedPatientDocumentTool()
        
        # Get document content
        doc = tool.docs_service.documents().get(documentId=doc_id).execute()
        content = doc.get('body', {}).get('content', [])
        
        # Extract full text
        full_text = ""
        for element in content:
            if 'paragraph' in element:
                for text_run in element['paragraph'].get('elements', []):
                    if 'textRun' in text_run:
                        full_text += text_run['textRun'].get('content', '')
        
        # Find Section 7
        section_7_marker = "7: PRESCRIPTION & FOLLOW-UP"
        section_8_marker = "8: WORKFLOW COMPLETION"
        
        if section_7_marker not in full_text:
            return {
                'success': False,
                'error': 'Section 7 not found in document'
            }
        
        # Extract Section 7 content
        start_idx = full_text.find(section_7_marker)
        end_idx = full_text.find(section_8_marker, start_idx)
        
        if end_idx == -1:
            section_7_text = full_text[start_idx:]
        else:
            section_7_text = full_text[start_idx:end_idx]
        
        print(f"📄 Section 7 content:\n{section_7_text[:500]}...")
        
        # Check if doctor has updated (look for pending indicators OR template placeholders)
        pending_indicators = [
            "Doctor will update",
            "pending",
            "waiting for prescription"
        ]
        
        template_indicators = [
            "[Write medication name]",
            "[Specify dosage]",
            "[Doctor to complete]",
            "DOCTOR:",
            "⚠️",
            "e.g.,",
            "(Choose ONE)"
        ]
        
        is_pending = any(indicator in section_7_text.lower() for indicator in pending_indicators)
        has_templates = any(template in section_7_text for template in template_indicators)
        
        if is_pending or has_templates or len(section_7_text) < 200:  # Very short = not updated
            return {
                'success': False,
                'pending': True,
                'message': 'Doctor has not completed prescription yet'
            }
        
        # Parse medications - support multiple formats
        medications = []
        
        # Format 1: MEDICATIONS PRESCRIBED: (numbered list)
        med_section_start = section_7_text.find("MEDICATIONS PRESCRIBED:")
        if med_section_start != -1:
            med_section_end = section_7_text.find("SAFETY MEASURES", med_section_start)
            if med_section_end == -1:
                med_section_end = section_7_text.find("DIETARY INSTRUCTIONS", med_section_start)
            if med_section_end == -1:
                med_section_end = section_7_text.find("📅 FOLLOW-UP APPOINTMENT", med_section_start)
            if med_section_end == -1:
                med_section_end = section_7_text.find("FOLLOW-UP APPOINTMENT", med_section_start)
            
            if med_section_end != -1:
                med_section = section_7_text[med_section_start:med_section_end]
                
                # Parse each medication (look for numbered items)
                import re
                med_blocks = re.split(r'\n\d+\.\s+', med_section)[1:]  # Split by "1. ", "2. ", etc.
                
                for block in med_blocks:
                    med = {}
                    lines = block.strip().split('\n')
                    
                    # First line is medication name
                    if lines:
                        med['name'] = lines[0].strip()
                    
                    # Parse other fields
                    for line in lines[1:]:
                        if 'Dosage:' in line:
                            med['dosage'] = line.split('Dosage:')[1].strip()
                        elif 'Timing:' in line:
                            med['timing'] = line.split('Timing:')[1].strip()
                        elif 'Duration:' in line:
                            med['duration'] = line.split('Duration:')[1].strip()
                        elif 'Purpose:' in line:
                            med['purpose'] = line.split('Purpose:')[1].strip()
                    
                    if med.get('name'):
                        medications.append(med)
        
        # Format 2: Prescriptions: (simple line format like "Metformin 1000mg - Take twice daily")
        if not medications and "Prescriptions:" in section_7_text:
            presc_start = section_7_text.find("Prescriptions:")
            presc_end = section_7_text.find("Follow-up Instructions:", presc_start)
            if presc_end == -1:
                presc_end = section_7_text.find("FOLLOW-UP", presc_start)
            
            if presc_end != -1:
                presc_section = section_7_text[presc_start:presc_end]
                import re
                # Match lines like "Metformin 1000mg - Take twice daily with meals"
                # Pattern: Capital letter, lowercase letters, space, numbers, lowercase letters (mg/ml/etc), space, dash, rest of line
                med_lines = re.findall(r'([A-Z][a-zA-Z]+\s+\d+[a-z]+)\s*-\s*(.+)', presc_section, re.MULTILINE)
                
                for med_name_dose, instructions in med_lines:
                    instructions_clean = instructions.strip()
                    # Skip if it's not actually a prescription line
                    if instructions_clean and not instructions_clean.startswith('━'):
                        med = {
                            'name': med_name_dose.strip(),
                            'instructions': instructions_clean,
                            'dosage': med_name_dose.strip(),
                            'timing': instructions_clean
                        }
                        medications.append(med)
        
        # Parse safety measures
        safety_measures = []
        if "SAFETY MEASURES & PRECAUTIONS:" in section_7_text:
            safety_start = section_7_text.find("SAFETY MEASURES & PRECAUTIONS:") + len("SAFETY MEASURES & PRECAUTIONS:")
            safety_end = section_7_text.find("DIETARY INSTRUCTIONS:", safety_start)
            if safety_end == -1:
                safety_end = section_7_text.find("FOLLOW-UP SCHEDULE:", safety_start)
            
            if safety_end != -1:
                safety_section = section_7_text[safety_start:safety_end]
                # Extract lines starting with ⚠️ or •
                for line in safety_section.split('\n'):
                    line = line.strip()
                    if line.startswith('⚠️') or line.startswith('•'):
                        safety_measures.append(line.replace('⚠️', '').replace('•', '').strip())
        
        # Parse dietary instructions
        dietary_instructions = []
        if "DIETARY INSTRUCTIONS:" in section_7_text:
            diet_start = section_7_text.find("DIETARY INSTRUCTIONS:") + len("DIETARY INSTRUCTIONS:")
            diet_end = section_7_text.find("FOLLOW-UP SCHEDULE:", diet_start)
            
            if diet_end != -1:
                diet_section = section_7_text[diet_start:diet_end]
                for line in diet_section.split('\n'):
                    line = line.strip()
                    if line.startswith('•'):
                        dietary_instructions.append(line.replace('•', '').strip())
        
        # Parse follow-up details - support multiple formats
        follow_up_date = ""
        follow_up_tests = []
        follow_up_location = ""
        follow_up_instructions = []
        
        # Format 1: FOLLOW-UP SCHEDULE: (structured)
        if "FOLLOW-UP SCHEDULE:" in section_7_text:
            followup_start = section_7_text.find("FOLLOW-UP SCHEDULE:") + len("FOLLOW-UP SCHEDULE:")
            followup_end = section_7_text.find("EMERGENCY CONTACT:", followup_start)
            if followup_end == -1:
                followup_end = section_7_text.find("PRESCRIPTION VALID UNTIL:", followup_start)
            
            if followup_end != -1:
                followup_section = section_7_text[followup_start:followup_end]
                
                # Extract next appointment date
                if "Next Appointment:" in followup_section:
                    date_line_start = followup_section.find("Next Appointment:") + len("Next Appointment:")
                    date_line_end = followup_section.find("\n", date_line_start)
                    date_line = followup_section[date_line_start:date_line_end].strip()
                    # Extract date (format: 2024-02-15 or other formats)
                    import re
                    date_match = re.search(r'\d{4}-\d{2}-\d{2}', date_line)
                    if date_match:
                        follow_up_date = date_match.group()
                
                # Extract tests required
                if "Tests Required:" in followup_section:
                    tests_line_start = followup_section.find("Tests Required:") + len("Tests Required:")
                    tests_line_end = followup_section.find("\n", tests_line_start)
                    tests_line = followup_section[tests_line_start:tests_line_end].strip()
                    follow_up_tests = [t.strip() for t in tests_line.split(',')]
                
                # Extract location
                if "Location:" in followup_section:
                    loc_line_start = followup_section.find("Location:") + len("Location:")
                    loc_line_end = followup_section.find("\n", loc_line_start)
                    follow_up_location = followup_section[loc_line_start:loc_line_end].strip()
        
        # Format 2: Follow-up Instructions: (bullet list)
        if "Follow-up Instructions:" in section_7_text:
            followup_start = section_7_text.find("Follow-up Instructions:")
            followup_end = section_7_text.find("━━━", followup_start)
            if followup_end == -1:
                followup_end = section_7_text.find("SECTION 8:", followup_start)
            
            if followup_end != -1:
                followup_section = section_7_text[followup_start:followup_end]
                # Extract bullet points
                import re
                bullets = re.findall(r'•\s*(.+?)(?=\n|$)', followup_section)
                follow_up_instructions = [b.strip() for b in bullets if b.strip()]
                
                # Try to extract next consultation timing
                for instruction in follow_up_instructions:
                    if 'weeks' in instruction.lower() or 'months' in instruction.lower() or 'consultation' in instruction.lower():
                        follow_up_date = instruction  # Store as text if no specific date
        
        print(f"✅ Parsed prescription:")
        print(f"   Medications: {len(medications)} items")
        print(f"   Safety measures: {len(safety_measures)} items")
        print(f"   Follow-up instructions: {len(follow_up_instructions)} items")
        print(f"   Follow-up date: {follow_up_date}")
        
        return {
            'success': True,
            'pending': False,
            'medications': medications,
            'safety_measures': safety_measures,
            'dietary_instructions': dietary_instructions,
            'follow_up_date': follow_up_date,
            'follow_up_tests': follow_up_tests,
            'follow_up_location': follow_up_location,
            'follow_up_instructions': follow_up_instructions
        }
        
    except Exception as e:
        print(f"❌ Error reading prescription details: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def read_lab_results(doc_id: str) -> Dict[str, Any]:
    """
    Read Section 5 (LAB RESULTS) from unified workflow document
    Parses test results, statuses, and AI analysis
    
    Returns:
        Dict with:
        - pending: bool (True if doctor hasn't added results yet)
        - tests: List of test results with name, result, range, status
        - normal_count: int
        - abnormal_count: int
        - ai_analysis: str
        - success: bool
    """
    try:
        # Use same credentials as other functions
        creds = None
        token_path = 'credentials/docs_token.pickle'
        
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials/client_secret.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        docs_service = build('docs', 'v1', credentials=creds)
        
        # Read the document
        document = docs_service.documents().get(documentId=doc_id).execute()
        content = document.get('body', {}).get('content', [])
        
        # Extract full text
        full_text = ""
        for element in content:
            if 'paragraph' in element:
                for text_run in element['paragraph'].get('elements', []):
                    if 'textRun' in text_run:
                        full_text += text_run['textRun'].get('content', '')
        
        # Find Section 5 content
        # Try multiple possible markers
        possible_markers = [
            "5: LAB RESULTS",
            "SECTION 5: LAB RESULTS",
            "📊 SECTION 5: LAB RESULTS"
        ]
        
        section_marker = None
        for marker in possible_markers:
            if marker in full_text:
                section_marker = marker
                break
        
        if not section_marker:
            return {
                'success': False,
                'pending': True,
                'error': 'Section 5 not found in document'
            }
        
        # Find section end markers
        possible_end_markers = [
            "6: POST-LAB",
            "SECTION 6:",
            "👨‍⚕️ SECTION 6:"
        ]
        
        section_end_marker = None
        start_idx = full_text.find(section_marker)
        
        for marker in possible_end_markers:
            if marker in full_text[start_idx:]:
                section_end_marker = marker
                break
        
        # Extract Section 5 content
        if section_end_marker:
            end_idx = full_text.find(section_end_marker, start_idx)
            section_content = full_text[start_idx:end_idx]
        else:
            section_content = full_text[start_idx:start_idx+2000]  # Get next 2000 chars
        
        # Check if pending (doctor hasn't added results yet)
        pending_indicators = [
            "pending",
            "will be updated",
            "awaiting",
            "not yet available",
            "doctor will add"
        ]
        
        if any(indicator in section_content.lower() for indicator in pending_indicators):
            return {
                'success': True,
                'pending': True,
                'message': 'Lab results not yet added by medical staff'
            }
        
        # Parse results
        tests = []
        normal_count = 0
        abnormal_count = 0
        ai_analysis = ""
        
        # Extract results summary counts
        if "Normal:" in section_content:
            import re
            normal_match = re.search(r'Normal:\s*(\d+)\s*test', section_content)
            abnormal_match = re.search(r'Abnormal:\s*(\d+)\s*test', section_content)
            
            if normal_match:
                normal_count = int(normal_match.group(1))
            if abnormal_match:
                abnormal_count = int(abnormal_match.group(1))
        
        # Extract detailed results (numbered list format)
        # Format: 1. Test Name\n   Result: value\n   Normal Range: range\n   Status: status
        import re
        test_pattern = r'(\d+)\.\s+([^\n]+)\n\s+Result:\s+([^\n]+)\n\s+Normal Range:\s+([^\n]+)\n\s+Status:\s+([^\n]+)'
        
        matches = re.findall(test_pattern, section_content)
        for match in matches:
            test_num, test_name, result, normal_range, status = match
            
            # Determine if normal or abnormal
            is_normal = '✅' in status or 'NORMAL' in status.upper()
            
            tests.append({
                'test_name': test_name.strip(),
                'result': result.strip(),
                'normal_range': normal_range.strip(),
                'status': 'NORMAL' if is_normal else 'ABNORMAL',
                'status_icon': '✅' if is_normal else '⚠️'
            })
        
        # Extract AI analysis
        if "AI ANALYSIS:" in section_content:
            analysis_start = section_content.find("AI ANALYSIS:")
            analysis_end = section_content.find("Updated by:", analysis_start)
            
            if analysis_end == -1:
                ai_analysis = section_content[analysis_start + len("AI ANALYSIS:"):].strip()
            else:
                ai_analysis = section_content[analysis_start + len("AI ANALYSIS:"):analysis_end].strip()
        
        return {
            'success': True,
            'pending': False,
            'tests': tests,
            'normal_count': normal_count,
            'abnormal_count': abnormal_count,
            'ai_analysis': ai_analysis,
            'total_tests': len(tests)
        }
        
    except Exception as e:
        print(f"❌ Error reading lab results: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
