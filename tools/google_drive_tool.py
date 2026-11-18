"""
Google Drive Tool for Hospital Management System
Manages document storage, organization, and sharing for patient records
"""

import os
import pickle
import io
from typing import Optional, Type, List, Dict
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from pydantic import BaseModel, Field
from langchain.tools import BaseTool


# ==================== GOOGLE DRIVE SCOPES ====================
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets'
]


# ==================== AUTHENTICATION ====================

def authenticate_drive(credentials_file: str = 'credentials/client_secret.json', 
                       token_file: str = 'drive_token.pickle'):
    """Authenticate with Google Drive API"""
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

class DriveToolBase:
    """Base class for Google Drive tools"""
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'drive_token.pickle'):
        creds = authenticate_drive(credentials_file, token_file)
        self.service = build('drive', 'v3', credentials=creds)


# ==================== INPUT SCHEMAS ====================

class CreateFolderInput(BaseModel):
    """Input for creating Drive folders."""
    folder_name: str = Field(description="Name of the folder to create")
    parent_folder_id: Optional[str] = Field(default=None, description="Parent folder ID (optional)")


class UploadFileInput(BaseModel):
    """Input for uploading files to Drive."""
    file_path: str = Field(description="Local path to the file to upload")
    folder_id: Optional[str] = Field(default=None, description="Destination folder ID (optional)")
    file_name: Optional[str] = Field(default=None, description="Custom file name (optional)")


class ShareFileInput(BaseModel):
    """Input for sharing files/folders."""
    file_id: str = Field(description="File or folder ID to share")
    email: str = Field(description="Email address to share with")
    role: str = Field(default="reader", description="Permission role: reader, writer, or commenter")


class ListFilesInput(BaseModel):
    """Input for listing files."""
    folder_id: Optional[str] = Field(default=None, description="Folder ID to list files from")
    max_results: int = Field(default=10, description="Maximum number of files to return")


class DeleteFileInput(BaseModel):
    """Input for deleting files."""
    file_id: str = Field(description="File or folder ID to delete")


# ==================== DRIVE TOOLS ====================

class CreatePatientFolderTool(BaseTool, DriveToolBase):
    """Tool for creating patient folders in Google Drive."""
    
    name: str = "create_patient_folder"
    description: str = """Create a dedicated folder for patient documents in Google Drive. 
    Organizes all patient documents in one place."""
    args_schema: Type[BaseModel] = CreateFolderInput
    
    service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'drive_token.pickle'):
        BaseTool.__init__(self)
        DriveToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, folder_name: str, parent_folder_id: Optional[str] = None) -> str:
        try:
            # Prepare folder metadata
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            # Add parent folder if specified
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            
            # Create folder
            folder = self.service.files().create(
                body=file_metadata,
                fields='id, name, webViewLink'
            ).execute()
            
            folder_id = folder.get('id')
            folder_link = folder.get('webViewLink')
            
            # Create subfolders for organization (numbered for clarity)
            subfolders = [
                '1_Medical_History',
                '2_Essential_Documents',  # Aadhaar, PAN, Insurance, ID proofs
                '3_Lab_Reports',
                '4_Prescriptions',
                '5_Consultation_Notes'
            ]
            
            created_subfolders = []
            subfolder_ids = {}  # Store folder IDs for later use
            
            for subfolder_name in subfolders:
                subfolder_metadata = {
                    'name': subfolder_name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [folder_id]
                }
                subfolder = self.service.files().create(
                    body=subfolder_metadata,
                    fields='id, name, webViewLink'
                ).execute()
                
                created_subfolders.append(subfolder['name'])
                subfolder_ids[subfolder_name] = {
                    'id': subfolder['id'],
                    'link': subfolder.get('webViewLink', '')
                }
            
            # Build detailed response with subfolder links
            subfolder_details = "\n".join([
                f"  • {sf} - {subfolder_ids[sf]['link']}" 
                for sf in created_subfolders
            ])
            
            return f"""✅ Patient Folder Created Successfully!

📁 Main Folder:
- Name: {folder_name}
- Folder ID: {folder_id}
- Link: {folder_link}

📂 Subfolders Created :
{subfolder_details}

"""
        
        except Exception as e:
            return f"❌ Error creating folder: {str(e)}"
    
    async def _arun(self, folder_name: str, parent_folder_id: Optional[str] = None) -> str:
        return self._run(folder_name, parent_folder_id)


class UploadDocumentTool(BaseTool, DriveToolBase):
    """Tool for uploading documents to Google Drive."""
    
    name: str = "upload_document_to_drive"
    description: str = """Upload patient documents (reports, scans, IDs) to Google Drive. 
    Stores files securely in patient folders."""
    args_schema: Type[BaseModel] = UploadFileInput
    
    service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'drive_token.pickle'):
        BaseTool.__init__(self)
        DriveToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, file_path: str, folder_id: Optional[str] = None, 
             file_name: Optional[str] = None) -> str:
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return f"❌ Error: File not found at {file_path}"
            
            # Use provided name or extract from path
            upload_name = file_name or os.path.basename(file_path)
            
            # Prepare file metadata
            file_metadata = {'name': upload_name}
            
            # Add to folder if specified
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Detect MIME type
            mime_types = {
                '.pdf': 'application/pdf',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.doc': 'application/msword',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.txt': 'text/plain'
            }
            
            file_ext = os.path.splitext(file_path)[1].lower()
            mime_type = mime_types.get(file_ext, 'application/octet-stream')
            
            # Upload file
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            uploaded_file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink, size, createdTime'
            ).execute()
            
            file_id = uploaded_file.get('id')
            file_link = uploaded_file.get('webViewLink')
            file_size = int(uploaded_file.get('size', 0)) / 1024  # Convert to KB
            
            return f"""✅ Document Uploaded Successfully!

📄 File Details:
- Name: {upload_name}
- File ID: {file_id}
- Size: {file_size:.2f} KB
- Type: {mime_type}
- Link: {file_link}

✅ Document is now securely stored in Google Drive
"""
        
        except Exception as e:
            return f"❌ Error uploading file: {str(e)}"
    
    async def _arun(self, file_path: str, folder_id: Optional[str] = None, 
                    file_name: Optional[str] = None) -> str:
        return self._run(file_path, folder_id, file_name)


class ShareFileTool(BaseTool, DriveToolBase):
    """Tool for sharing files and folders."""
    
    name: str = "share_drive_file"
    description: str = """Share files or folders with patients or medical staff. 
    Set permissions: reader (view only), writer (edit), or commenter."""
    args_schema: Type[BaseModel] = ShareFileInput
    
    service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'drive_token.pickle'):
        BaseTool.__init__(self)
        DriveToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, file_id: str, email: str, role: str = "reader") -> str:
        try:
            # Validate role
            if role not in ['reader', 'writer', 'commenter']:
                return "❌ Error: Invalid role. Use 'reader', 'writer', or 'commenter'"
            
            # Create permission
            permission = {
                'type': 'user',
                'role': role,
                'emailAddress': email
            }
            
            # Share the file
            self.service.permissions().create(
                fileId=file_id,
                body=permission,
                sendNotificationEmail=True,
                emailMessage=f"A document has been shared with you from Hospital Management System"
            ).execute()
            
            # Get file details
            file_info = self.service.files().get(
                fileId=file_id,
                fields='name, webViewLink'
            ).execute()
            
            role_descriptions = {
                'reader': 'Can view only',
                'writer': 'Can edit',
                'commenter': 'Can comment'
            }
            
            return f"""✅ File Shared Successfully!

📤 Share Details:
- File: {file_info.get('name', 'Unknown')}
- Shared with: {email}
- Permission: {role_descriptions.get(role, role)}
- Link: {file_info.get('webViewLink')}

📧 Email notification sent to {email}
"""
        
        except Exception as e:
            return f"❌ Error sharing file: {str(e)}"
    
    async def _arun(self, file_id: str, email: str, role: str = "reader") -> str:
        return self._run(file_id, email, role)


class ListFilesTool(BaseTool, DriveToolBase):
    """Tool for listing files in Google Drive."""
    
    name: str = "list_drive_files"
    description: str = """List files and folders in Google Drive. 
    Can list all files or files in a specific folder."""
    args_schema: Type[BaseModel] = ListFilesInput
    
    service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'drive_token.pickle'):
        BaseTool.__init__(self)
        DriveToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, folder_id: Optional[str] = None, max_results: int = 10) -> str:
        try:
            # Build query
            query = "trashed = false"
            if folder_id:
                query += f" and '{folder_id}' in parents"
            
            # List files
            results = self.service.files().list(
                q=query,
                pageSize=max_results,
                fields='files(id, name, mimeType, size, createdTime, webViewLink)',
                orderBy='createdTime desc'
            ).execute()
            
            files = results.get('files', [])
            
            if not files:
                return "📭 No files found."
            
            response = f"📁 Found {len(files)} file(s):\n\n"
            
            for i, file in enumerate(files, 1):
                name = file.get('name')
                file_id = file.get('id')
                mime_type = file.get('mimeType', '')
                size = int(file.get('size', 0)) / 1024 if 'size' in file else 0
                created = file.get('createdTime', 'Unknown')
                link = file.get('webViewLink', 'N/A')
                
                # Determine type icon
                if 'folder' in mime_type:
                    icon = '📁'
                elif 'pdf' in mime_type:
                    icon = '📄'
                elif 'image' in mime_type:
                    icon = '🖼️'
                elif 'document' in mime_type:
                    icon = '📝'
                elif 'spreadsheet' in mime_type:
                    icon = '📊'
                else:
                    icon = '📎'
                
                response += f"{i}. {icon} {name}\n"
                response += f"   ID: {file_id}\n"
                if size > 0:
                    response += f"   Size: {size:.2f} KB\n"
                response += f"   Created: {created[:10]}\n"
                response += f"   Link: {link}\n\n"
            
            return response
        
        except Exception as e:
            return f"❌ Error listing files: {str(e)}"
    
    async def _arun(self, folder_id: Optional[str] = None, max_results: int = 10) -> str:
        return self._run(folder_id, max_results)


class DeleteFileTool(BaseTool, DriveToolBase):
    """Tool for deleting files from Google Drive."""
    
    name: str = "delete_drive_file"
    description: str = """Delete files or folders from Google Drive. 
    Use with caution - deleted files go to trash."""
    args_schema: Type[BaseModel] = DeleteFileInput
    
    service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'drive_token.pickle'):
        BaseTool.__init__(self)
        DriveToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, file_id: str) -> str:
        try:
            # Get file details before deletion
            file_info = self.service.files().get(
                fileId=file_id,
                fields='name, mimeType'
            ).execute()
            
            file_name = file_info.get('name', 'Unknown')
            mime_type = file_info.get('mimeType', '')
            file_type = 'Folder' if 'folder' in mime_type else 'File'
            
            # Delete the file (moves to trash)
            self.service.files().delete(fileId=file_id).execute()
            
            return f"""✅ {file_type} Deleted Successfully!

🗑️ Deleted Item:
- Name: {file_name}
- Type: {file_type}
- File ID: {file_id}

📝 Note: File moved to trash. Can be restored within 30 days.
"""
        
        except Exception as e:
            return f"❌ Error deleting file: {str(e)}"
    
    async def _arun(self, file_id: str) -> str:
        return self._run(file_id)


# ==================== PRESCRIPTION PDF INPUT SCHEMA ====================

class GeneratePrescriptionPDFInput(BaseModel):
    """Input for generating prescription PDF."""
    workflow_doc_id: str = Field(description="Google Docs workflow document ID")
    patient_id: str = Field(description="Patient ID")
    patient_name: str = Field(description="Patient name")
    prescriptions_folder_id: str = Field(description="Prescriptions folder ID (4_Prescriptions)")


# ==================== PRESCRIPTION PDF GENERATOR ====================

class GeneratePrescriptionPDFTool(BaseTool, DriveToolBase):
    """Tool for generating prescription PDF from Doc Section 7 and uploading to Prescriptions folder."""
    
    name: str = "generate_prescription_pdf"
    description: str = """Generate a professional prescription PDF from Google Docs Section 7 (doctor's prescription), 
    then upload it to the patient's Prescriptions folder in Google Drive."""
    args_schema: Type[BaseModel] = GeneratePrescriptionPDFInput
    
    service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'drive_token.pickle'):
        BaseTool.__init__(self)
        DriveToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, workflow_doc_id: str, patient_id: str, patient_name: str, 
             prescriptions_folder_id: str) -> str:
        try:
            # Step 1: Read Section 7 from the unified workflow document
            from tools.unified_workflow_doc_tool import read_doc_content
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            from datetime import datetime
            import tempfile
            import re
            
            print(f"📄 Reading prescription from Doc Section 7...")
            doc_content = read_doc_content(workflow_doc_id)
            
            if not doc_content or 'error' in doc_content:
                return f"❌ Error reading document: {doc_content.get('error', 'Unknown error')}"
            
            # Extract Section 7 content
            full_text = doc_content.get('content', '')
            section_7_match = re.search(r'7: PRESCRIPTION.*?\n(.*?)(?=\n\n━|$)', full_text, re.DOTALL)
            
            if not section_7_match:
                return "❌ Section 7 (PRESCRIPTION) not found in document. Doctor may not have added prescription yet."
            
            prescription_text = section_7_match.group(1).strip()
            
            if not prescription_text or len(prescription_text) < 20:
                return "❌ Prescription section is empty. Doctor needs to fill in the prescription first."
            
            print(f"✅ Prescription text extracted ({len(prescription_text)} characters)")
            
            # Step 2: Parse prescription information
            # Extract medications, dosages, instructions
            medications = []
            lines = prescription_text.split('\n')
            current_med = {}
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('━') or line.startswith('Updated'):
                    continue
                
                # Look for medication patterns
                if 'Medicine:' in line or 'Drug:' in line or line.startswith('•'):
                    if current_med:
                        medications.append(current_med)
                    current_med = {'name': line.replace('•', '').replace('Medicine:', '').replace('Drug:', '').strip()}
                elif 'Dosage:' in line or 'Dose:' in line:
                    current_med['dosage'] = line.replace('Dosage:', '').replace('Dose:', '').strip()
                elif 'Frequency:' in line or 'Times:' in line:
                    current_med['frequency'] = line.replace('Frequency:', '').replace('Times:', '').strip()
                elif 'Duration:' in line or 'Days:' in line:
                    current_med['duration'] = line.replace('Duration:', '').replace('Days:', '').strip()
                elif 'Instructions:' in line or 'Notes:' in line:
                    current_med['instructions'] = line.replace('Instructions:', '').replace('Notes:', '').strip()
                elif current_med and 'name' in current_med and len(line) > 5:
                    # Additional info for current medication
                    if 'instructions' not in current_med:
                        current_med['instructions'] = line
                    else:
                        current_med['instructions'] += f" {line}"
            
            if current_med:
                medications.append(current_med)
            
            # If parsing failed, use the full text as-is
            if not medications:
                medications = [{'name': 'See prescription details below', 'instructions': prescription_text}]
            
            # Step 3: Generate PDF using reportlab
            print(f"📝 Generating PDF with {len(medications)} medication(s)...")
            
            # Create temporary PDF file
            temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            pdf_path = temp_pdf.name
            temp_pdf.close()
            
            # Create PDF document
            doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                                   rightMargin=0.75*inch, leftMargin=0.75*inch,
                                   topMargin=0.75*inch, bottomMargin=0.75*inch)
            
            # Define styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a73e8'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#1a73e8'),
                spaceAfter=12
            )
            normal_style = styles['Normal']
            
            # Build PDF content
            story = []
            
            # Header
            story.append(Paragraph("🏥 MEDICAL PRESCRIPTION", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Patient Information Box
            patient_data = [
                ['Patient Name:', patient_name],
                ['Patient ID:', patient_id],
                ['Date:', datetime.now().strftime('%B %d, %Y')],
                ['Prescription ID:', f"RX-{patient_id}-{datetime.now().strftime('%Y%m%d')}"]
            ]
            
            patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
            patient_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0fe')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#1a73e8')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(patient_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Medications Section
            story.append(Paragraph("💊 PRESCRIBED MEDICATIONS", heading_style))
            story.append(Spacer(1, 0.1*inch))
            
            for i, med in enumerate(medications, 1):
                # Medication header
                med_name = med.get('name', 'Unknown Medication')
                story.append(Paragraph(f"<b>{i}. {med_name}</b>", normal_style))
                
                # Medication details table
                med_details = []
                if med.get('dosage'):
                    med_details.append(['Dosage:', med['dosage']])
                if med.get('frequency'):
                    med_details.append(['Frequency:', med['frequency']])
                if med.get('duration'):
                    med_details.append(['Duration:', med['duration']])
                if med.get('instructions'):
                    med_details.append(['Instructions:', med['instructions']])
                
                if med_details:
                    med_table = Table(med_details, colWidths=[1.5*inch, 4.5*inch])
                    med_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                        ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.grey),
                    ]))
                    story.append(med_table)
                
                story.append(Spacer(1, 0.15*inch))
            
            # Footer with important notes
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("📋 IMPORTANT NOTES:", heading_style))
            story.append(Paragraph("• Take medications exactly as prescribed by your doctor", normal_style))
            story.append(Paragraph("• Do not stop or change medications without consulting your doctor", normal_style))
            story.append(Paragraph("• Store medications in a cool, dry place away from children", normal_style))
            story.append(Paragraph("• Contact your doctor if you experience any side effects", normal_style))
            
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph(f"<i>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>", 
                                 ParagraphStyle('Footer', parent=normal_style, fontSize=8, textColor=colors.grey)))
            
            # Build PDF
            doc.build(story)
            print(f"✅ PDF generated at {pdf_path}")
            
            # Step 4: Upload PDF to Prescriptions folder
            print(f"📤 Uploading PDF to Prescriptions folder...")
            
            pdf_filename = f"Prescription_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            file_metadata = {
                'name': pdf_filename,
                'parents': [prescriptions_folder_id]
            }
            
            media = MediaFileUpload(pdf_path, mimetype='application/pdf', resumable=True)
            uploaded_file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink, webContentLink'
            ).execute()
            
            file_id = uploaded_file.get('id')
            web_view_link = uploaded_file.get('webViewLink')
            download_link = uploaded_file.get('webContentLink')
            
            # Clean up temporary file
            os.remove(pdf_path)
            
            print(f"✅ PDF uploaded successfully!")
            
            return f"""✅ Prescription PDF Generated Successfully!

📄 PDF Details:
- Filename: {pdf_filename}
- Medications: {len(medications)} item(s)
- File ID: {file_id}

🔗 Links:
- View Online: {web_view_link}
- Download: {download_link}

📂 Location: 4_Prescriptions folder

✅ Patient can now access their prescription PDF from Google Drive!"""
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"❌ Error generating prescription PDF: {error_details}")
            return f"❌ Error generating prescription PDF: {str(e)}"
    
    async def _arun(self, workflow_doc_id: str, patient_id: str, patient_name: str, 
                    prescriptions_folder_id: str) -> str:
        return self._run(workflow_doc_id, patient_id, patient_name, prescriptions_folder_id)


# ==================== HELPER FUNCTION ====================

def get_all_drive_tools():
    """Get all Drive tools for the agent"""
    return [
        CreatePatientFolderTool(),
        UploadDocumentTool(),
        ShareFileTool(),
        ListFilesTool(),
        DeleteFileTool(),
        GeneratePrescriptionPDFTool()  # NEW
    ]


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("📁 GOOGLE DRIVE TOOLS - Hospital Management")
    print("="*70)
    
    # Example 1: Create patient folder
    print("\n1️⃣ Creating Patient Folder...")
    tool1 = CreatePatientFolderTool()
    result1 = tool1._run(folder_name="Patient_Samarth_Pawar_REG2025001")
    print(result1)
    
    # Example 2: List files
    print("\n2️⃣ Listing Files...")
    tool2 = ListFilesTool()
    result2 = tool2._run(max_results=10)
    print(result2)
    
    print("\n" + "="*70)
    print("✅ Drive Tools Test Complete!")
    print("="*70)