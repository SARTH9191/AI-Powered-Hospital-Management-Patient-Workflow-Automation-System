"""
Google Sheets Tool for Hospital Management System
Tracks billing, lab results, patient statistics, and schedules
"""

import os
import pickle
from typing import Optional, Type, List, Dict, Any
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pydantic import BaseModel, Field
from langchain.tools import BaseTool


# ==================== GOOGLE SHEETS SCOPES ====================
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file'
]


# ==================== AUTHENTICATION ====================

def authenticate_sheets(credentials_file: str = 'credentials/client_secret.json', 
                       token_file: str = 'sheets_token.pickle'):
    """Authenticate with Google Sheets API"""
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

class SheetsToolBase:
    """Base class for Google Sheets tools"""
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'sheets_token.pickle'):
        creds = authenticate_sheets(credentials_file, token_file)
        self.sheets_service = build('sheets', 'v4', credentials=creds)
        self.drive_service = build('drive', 'v3', credentials=creds)


# ==================== INPUT SCHEMAS ====================

class CreateBillingSheetInput(BaseModel):
    """Input for creating billing tracking sheet."""
    patient_name: str = Field(description="Patient name for billing sheet")
    patient_id: str = Field(description="Patient registration ID")


class AddBillingChargeInput(BaseModel):
    """Input for adding billing charges."""
    spreadsheet_id: str = Field(description="Google Sheet ID")
    date: str = Field(description="Charge date")
    description: str = Field(description="Service or item description")
    quantity: int = Field(description="Quantity")
    unit_price: float = Field(description="Price per unit")
    category: str = Field(description="Billing category: Consultation, Lab Tests, Procedures, Medications, Room Charges, etc.")


class CreateLabResultsSheetInput(BaseModel):
    """Input for creating lab results tracking sheet."""
    sheet_name: str = Field(default="Lab Results Tracker", description="Name for the sheet")


class AddLabResultInput(BaseModel):
    """Input for adding lab test results."""
    spreadsheet_id: str = Field(description="Google Sheet ID")
    patient_name: str = Field(description="Patient name")
    patient_id: str = Field(description="Patient ID")
    test_name: str = Field(description="Name of the lab test")
    result: str = Field(description="Test result value")
    reference_range: str = Field(description="Normal reference range")
    status: str = Field(description="Normal, Abnormal, or Critical")
    test_date: str = Field(description="Date test was performed")


class CreatePatientStatsSheetInput(BaseModel):
    """Input for creating patient statistics dashboard."""
    sheet_name: str = Field(default="Patient Statistics Dashboard", description="Dashboard name")


class AddPatientRecordInput(BaseModel):
    """Input for adding patient records."""
    spreadsheet_id: str = Field(description="Google Sheet ID")
    patient_id: str = Field(description="Patient registration ID")
    patient_name: str = Field(description="Patient name")
    age: int = Field(description="Patient age")
    admission_date: str = Field(description="Date of admission")
    diagnosis: str = Field(description="Primary diagnosis")
    status: str = Field(description="Current status: Admitted, Discharged, Under Treatment")


class AddLabQueueRowInput(BaseModel):
    """Input for adding lab appointment to queue sheet."""
    patient_id: str = Field(description="Patient registration ID")
    patient_name: str = Field(description="Patient name")
    email: str = Field(description="Patient email")
    phone: str = Field(description="Patient phone number")
    test_names: str = Field(description="Comma-separated list of lab tests ordered")
    appointment_date: str = Field(description="Lab appointment date and time")
    doc_link: str = Field(description="Link to patient's workflow Google Doc")


class ReadSheetDataInput(BaseModel):
    """Input for reading sheet data."""
    spreadsheet_id: str = Field(description="Google Sheet ID")
    range_name: str = Field(description="Range to read (e.g., 'Sheet1!A1:F10')")


class ShareSheetInput(BaseModel):
    """Input for sharing sheets."""
    spreadsheet_id: str = Field(description="Google Sheet ID to share")
    email: str = Field(description="Email address to share with")
    role: str = Field(default="reader", description="Permission: reader, writer, or commenter")


# ==================== SHEETS TOOLS ====================

class CreateBillingSheetTool(BaseTool, SheetsToolBase):
    """Tool for creating billing tracking sheets."""
    
    name: str = "create_billing_sheet"
    description: str = """Create a new billing tracking sheet for patient charges. 
    Includes headers for date, description, quantity, price, category, and total."""
    args_schema: Type[BaseModel] = CreateBillingSheetInput
    
    sheets_service: Optional[object] = Field(default=None, exclude=True)
    drive_service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'sheets_token.pickle'):
        BaseTool.__init__(self)
        SheetsToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, patient_name: str, patient_id: str) -> str:
        try:
            # Create spreadsheet
            spreadsheet = {
                'properties': {
                    'title': f'Billing - {patient_name} ({patient_id})'
                },
                'sheets': [
                    {
                        'properties': {
                            'title': 'Charges',
                            'gridProperties': {
                                'frozenRowCount': 1
                            }
                        }
                    }
                ]
            }
            
            sheet = self.sheets_service.spreadsheets().create(
                body=spreadsheet
            ).execute()
            
            spreadsheet_id = sheet.get('spreadsheetId')
            
            # Add headers and formatting
            headers = [
                ['Date', 'Description', 'Quantity', 'Unit Price', 'Category', 'Total Amount']
            ]
            
            # Write headers
            self.sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='Charges!A1:F1',
                valueInputOption='RAW',
                body={'values': headers}
            ).execute()
            
            # Format headers (bold, background color)
            requests = [
                {
                    'repeatCell': {
                        'range': {
                            'sheetId': 0,
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
                                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                    }
                },
                # Auto-resize columns
                {
                    'autoResizeDimensions': {
                        'dimensions': {
                            'sheetId': 0,
                            'dimension': 'COLUMNS',
                            'startIndex': 0,
                            'endIndex': 6
                        }
                    }
                }
            ]
            
            self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'requests': requests}
            ).execute()
            
            # Get sheet URL
            sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
            
            return f"""✅ Billing Sheet Created Successfully!

📊 Sheet Details:
- Title: Billing - {patient_name}
- Patient ID: {patient_id}
- Spreadsheet ID: {spreadsheet_id}
- Link: {sheet_url}

✅ Sheet includes columns:
  • Date
  • Description
  • Quantity
  • Unit Price
  • Category
  • Total Amount

📝 Use 'add_billing_charge' tool to add charges to this sheet.
"""
        
        except Exception as e:
            return f"❌ Error creating billing sheet: {str(e)}"
    
    async def _arun(self, patient_name: str, patient_id: str) -> str:
        return self._run(patient_name, patient_id)


class AddBillingChargeTool(BaseTool, SheetsToolBase):
    """Tool for adding billing charges to sheet."""
    
    name: str = "add_billing_charge"
    description: str = """Add a new billing charge to patient's billing sheet. 
    Automatically calculates total amount (quantity × unit price)."""
    args_schema: Type[BaseModel] = AddBillingChargeInput
    
    sheets_service: Optional[object] = Field(default=None, exclude=True)
    drive_service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'sheets_token.pickle'):
        BaseTool.__init__(self)
        SheetsToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, spreadsheet_id: str, date: str, description: str, 
             quantity: int, unit_price: float, category: str) -> str:
        try:
            # Calculate total
            total = quantity * unit_price
            
            # Prepare row data
            row_data = [[date, description, quantity, unit_price, category, total]]
            
            # Append to sheet
            self.sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range='Charges!A:F',
                valueInputOption='USER_ENTERED',
                body={'values': row_data}
            ).execute()
            
            # Get current data to calculate grand total
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range='Charges!F:F'
            ).execute()
            
            values = result.get('values', [])
            grand_total = 0
            for row in values[1:]:  # Skip header
                if row and row[0]:
                    try:
                        grand_total += float(row[0])
                    except:
                        pass
            
            return f"""✅ Billing Charge Added Successfully!

💰 Charge Details:
- Date: {date}
- Description: {description}
- Quantity: {quantity}
- Unit Price: ₹{unit_price:,.2f}
- Category: {category}
- Total: ₹{total:,.2f}

📊 Current Grand Total: ₹{grand_total:,.2f}

🔗 View sheet: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit
"""
        
        except Exception as e:
            return f"❌ Error adding billing charge: {str(e)}"
    
    async def _arun(self, spreadsheet_id: str, date: str, description: str, 
                    quantity: int, unit_price: float, category: str) -> str:
        return self._run(spreadsheet_id, date, description, quantity, unit_price, category)


class CreateLabResultsSheetTool(BaseTool, SheetsToolBase):
    """Tool for creating lab results tracking sheet."""
    
    name: str = "create_lab_results_sheet"
    description: str = """Create a new lab results tracking sheet. 
    Tracks patient test results with reference ranges and status indicators."""
    args_schema: Type[BaseModel] = CreateLabResultsSheetInput
    
    sheets_service: Optional[object] = Field(default=None, exclude=True)
    drive_service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'sheets_token.pickle'):
        BaseTool.__init__(self)
        SheetsToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, sheet_name: str = "Lab Results Tracker") -> str:
        try:
            # Create spreadsheet
            spreadsheet = {
                'properties': {
                    'title': sheet_name
                },
                'sheets': [
                    {
                        'properties': {
                            'title': 'Test Results',
                            'gridProperties': {
                                'frozenRowCount': 1
                            }
                        }
                    }
                ]
            }
            
            sheet = self.sheets_service.spreadsheets().create(
                body=spreadsheet
            ).execute()
            
            spreadsheet_id = sheet.get('spreadsheetId')
            
            # Add headers
            headers = [
                ['Patient ID', 'Patient Name', 'Test Name', 'Result', 'Reference Range', 'Status', 'Test Date', 'Notes']
            ]
            
            self.sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='Test Results!A1:H1',
                valueInputOption='RAW',
                body={'values': headers}
            ).execute()
            
            # Format headers
            requests = [
                {
                    'repeatCell': {
                        'range': {
                            'sheetId': 0,
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {'red': 0.1, 'green': 0.7, 'blue': 0.4},
                                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                    }
                },
                {
                    'autoResizeDimensions': {
                        'dimensions': {
                            'sheetId': 0,
                            'dimension': 'COLUMNS',
                            'startIndex': 0,
                            'endIndex': 8
                        }
                    }
                }
            ]
            
            self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'requests': requests}
            ).execute()
            
            sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
            
            return f"""✅ Lab Results Sheet Created Successfully!

🔬 Sheet Details:
- Title: {sheet_name}
- Spreadsheet ID: {spreadsheet_id}
- Link: {sheet_url}

✅ Sheet includes columns:
  • Patient ID
  • Patient Name
  • Test Name
  • Result
  • Reference Range
  • Status (Normal/Abnormal/Critical)
  • Test Date
  • Notes

📝 Use 'add_lab_result' tool to add test results to this sheet.
"""
        
        except Exception as e:
            return f"❌ Error creating lab results sheet: {str(e)}"
    
    async def _arun(self, sheet_name: str = "Lab Results Tracker") -> str:
        return self._run(sheet_name)


class AddLabResultTool(BaseTool, SheetsToolBase):
    """Tool for adding lab test results."""
    
    name: str = "add_lab_result"
    description: str = """Add lab test result to tracking sheet. 
    Includes patient info, test details, results, and status."""
    args_schema: Type[BaseModel] = AddLabResultInput
    
    sheets_service: Optional[object] = Field(default=None, exclude=True)
    drive_service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'sheets_token.pickle'):
        BaseTool.__init__(self)
        SheetsToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, spreadsheet_id: str, patient_name: str, patient_id: str, 
             test_name: str, result: str, reference_range: str, 
             status: str, test_date: str) -> str:
        try:
            # First, get sheet info to check available sheets
            sheet_metadata = self.sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheets = sheet_metadata.get('sheets', [])
            
            # Find a suitable sheet name
            sheet_name = None
            for sheet in sheets:
                title = sheet.get('properties', {}).get('title', '')
                # Look for sheets with "Lab", "Test", or "Results" in the name
                if any(keyword in title.lower() for keyword in ['lab', 'test', 'result']):
                    sheet_name = title
                    break
            
            # If no suitable sheet found, use the first sheet
            if not sheet_name and sheets:
                sheet_name = sheets[0].get('properties', {}).get('title', 'Sheet1')
            elif not sheet_name:
                # Default fallback
                sheet_name = 'Sheet1'
            
            print(f"🔧 DEBUG: Using sheet: {sheet_name}")
            
            # Prepare row data
            row_data = [[patient_id, patient_name, test_name, result, reference_range, status, test_date, '']]
            
            # Append to sheet
            self.sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f'{sheet_name}!A:H',
                valueInputOption='USER_ENTERED',
                body={'values': row_data}
            ).execute()
            
            # Get row number for conditional formatting
            result_range = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f'{sheet_name}!A:A'
            ).execute()
            
            row_count = len(result_range.get('values', []))
            
            # Get sheet ID for formatting
            sheet_id = 0
            for sheet in sheets:
                if sheet.get('properties', {}).get('title') == sheet_name:
                    sheet_id = sheet.get('properties', {}).get('sheetId', 0)
                    break
            
            # Apply color coding based on status
            color = {'red': 0.9, 'green': 0.9, 'blue': 0.9}  # Default gray
            if status.lower() == 'normal':
                color = {'red': 0.85, 'green': 0.95, 'blue': 0.85}  # Light green
            elif status.lower() == 'abnormal':
                color = {'red': 1, 'green': 0.95, 'blue': 0.8}  # Light yellow
            elif status.lower() == 'critical':
                color = {'red': 1, 'green': 0.85, 'blue': 0.85}  # Light red
            
            requests = [{
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': row_count - 1,
                        'endRowIndex': row_count,
                        'startColumnIndex': 5,
                        'endColumnIndex': 6
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': color,
                            'textFormat': {'bold': True}
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            }]
            
            self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'requests': requests}
            ).execute()
            
            status_emoji = '✅' if status.lower() == 'normal' else ('⚠️' if status.lower() == 'abnormal' else '🚨')
            
            return f"""{status_emoji} Lab Result Added Successfully!

🔬 Test Details:
- Patient: {patient_name} ({patient_id})
- Test: {test_name}
- Result: {result}
- Reference Range: {reference_range}
- Status: {status}
- Date: {test_date}

🔗 View sheet: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit
"""
        
        except Exception as e:
            return f"❌ Error adding lab result: {str(e)}"
    
    async def _arun(self, spreadsheet_id: str, patient_name: str, patient_id: str, 
                    test_name: str, result: str, reference_range: str, 
                    status: str, test_date: str) -> str:
        return self._run(spreadsheet_id, patient_name, patient_id, test_name, 
                        result, reference_range, status, test_date)


class CreatePatientStatsSheetTool(BaseTool, SheetsToolBase):
    """Tool for creating patient statistics dashboard."""
    
    name: str = "create_patient_stats_sheet"
    description: str = """Create patient statistics dashboard. 
    Tracks patient records, admissions, and status."""
    args_schema: Type[BaseModel] = CreatePatientStatsSheetInput
    
    sheets_service: Optional[object] = Field(default=None, exclude=True)
    drive_service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'sheets_token.pickle'):
        BaseTool.__init__(self)
        SheetsToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, sheet_name: str = "Patient Statistics Dashboard") -> str:
        try:
            # Create spreadsheet
            spreadsheet = {
                'properties': {
                    'title': sheet_name
                },
                'sheets': [
                    {
                        'properties': {
                            'title': 'Patient Records',
                            'gridProperties': {
                                'frozenRowCount': 1
                            }
                        }
                    }
                ]
            }
            
            sheet = self.sheets_service.spreadsheets().create(
                body=spreadsheet
            ).execute()
            
            spreadsheet_id = sheet.get('spreadsheetId')
            # Get the actual sheet ID from the created spreadsheet
            sheet_id = sheet.get('sheets', [{}])[0].get('properties', {}).get('sheetId', 0)
            
            # Add headers
            headers = [
                ['Patient ID', 'Patient Name', 'Age', 'Admission Date', 'Diagnosis', 'Status', 'Days in Hospital']
            ]
            
            self.sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='Patient Records!A1:G1',
                valueInputOption='RAW',
                body={'values': headers}
            ).execute()
            
            # Format headers
            requests = [
                {
                    'repeatCell': {
                        'range': {
                            'sheetId': sheet_id,
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {'red': 0.6, 'green': 0.2, 'blue': 0.8},
                                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                    }
                },
                {
                    'autoResizeDimensions': {
                        'dimensions': {
                            'sheetId': sheet_id,
                            'dimension': 'COLUMNS',
                            'startIndex': 0,
                            'endIndex': 7
                        }
                    }
                }
            ]
            
            self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'requests': requests}
            ).execute()
            
            sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
            
            return f"""✅ Patient Statistics Dashboard Created Successfully!

📊 Dashboard Details:
- Title: {sheet_name}
- Spreadsheet ID: {spreadsheet_id}
- Link: {sheet_url}

✅ Dashboard includes columns:
  • Patient ID
  • Patient Name
  • Age
  • Admission Date
  • Diagnosis
  • Status (Admitted/Discharged/Under Treatment)
  • Days in Hospital

📝 Use 'add_patient_record' tool to add patient data.
"""
        
        except Exception as e:
            return f"❌ Error creating patient stats sheet: {str(e)}"
    
    async def _arun(self, sheet_name: str = "Patient Statistics Dashboard") -> str:
        return self._run(sheet_name)


class AddPatientRecordTool(BaseTool, SheetsToolBase):
    """Tool for adding patient records to statistics sheet."""
    
    name: str = "add_patient_record"
    description: str = """Add patient admission record to statistics dashboard. 
    Automatically calculates days in hospital."""
    args_schema: Type[BaseModel] = AddPatientRecordInput
    
    sheets_service: Optional[object] = Field(default=None, exclude=True)
    drive_service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'sheets_token.pickle'):
        BaseTool.__init__(self)
        SheetsToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, spreadsheet_id: str, patient_id: str, patient_name: str, 
             age: int, admission_date: str, diagnosis: str, status: str) -> str:
        try:
            # Calculate days in hospital
            try:
                admission_dt = datetime.strptime(admission_date, '%Y-%m-%d')
                today = datetime.now()
                days_in_hospital = (today - admission_dt).days
            except:
                days_in_hospital = 0
            
            # Prepare row data
            row_data = [[patient_id, patient_name, age, admission_date, diagnosis, status, days_in_hospital]]
            
            # Append to sheet
            self.sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range='Patient Records!A:G',
                valueInputOption='USER_ENTERED',
                body={'values': row_data}
            ).execute()
            
            return f"""✅ Patient Record Added Successfully!

👤 Patient Details:
- ID: {patient_id}
- Name: {patient_name}
- Age: {age}
- Admission Date: {admission_date}
- Diagnosis: {diagnosis}
- Status: {status}
- Days in Hospital: {days_in_hospital}

🔗 View dashboard: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit
"""
        
        except Exception as e:
            return f"❌ Error adding patient record: {str(e)}"
    
    async def _arun(self, spreadsheet_id: str, patient_id: str, patient_name: str, 
                    age: int, admission_date: str, diagnosis: str, status: str) -> str:
        return self._run(spreadsheet_id, patient_id, patient_name, age, 
                        admission_date, diagnosis, status)


class ReadSheetDataTool(BaseTool, SheetsToolBase):
    """Tool for reading data from sheets."""
    
    name: str = "read_sheet_data"
    description: str = """Read data from Google Sheet. 
    Specify range like 'Sheet1!A1:F10' to read specific cells."""
    args_schema: Type[BaseModel] = ReadSheetDataInput
    
    sheets_service: Optional[object] = Field(default=None, exclude=True)
    drive_service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'sheets_token.pickle'):
        BaseTool.__init__(self)
        SheetsToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, spreadsheet_id: str, range_name: str) -> str:
        try:
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                return "📭 No data found in the specified range."
            
            # Format data as table
            output = f"✅ Sheet Data Retrieved Successfully!\n\n"
            output += f"📊 Range: {range_name}\n"
            output += f"📝 Rows: {len(values)}\n\n"
            output += "Data:\n"
            output += "="*80 + "\n"
            
            for i, row in enumerate(values, 1):
                output += f"Row {i}: {' | '.join(str(cell) for cell in row)}\n"
            
            output += "="*80 + "\n"
            output += f"\n🔗 View sheet: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
            
            return output
        
        except Exception as e:
            return f"❌ Error reading sheet data: {str(e)}"
    
    async def _arun(self, spreadsheet_id: str, range_name: str) -> str:
        return self._run(spreadsheet_id, range_name)


class ShareSheetTool(BaseTool, SheetsToolBase):
    """Tool for sharing Google Sheets."""
    
    name: str = "share_google_sheet"
    description: str = """Share Google Sheet with staff or patients. 
    Set permissions: reader (view only), writer (edit), or commenter."""
    args_schema: Type[BaseModel] = ShareSheetInput
    
    sheets_service: Optional[object] = Field(default=None, exclude=True)
    drive_service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'sheets_token.pickle'):
        BaseTool.__init__(self)
        SheetsToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, spreadsheet_id: str, email: str, role: str = "reader") -> str:
        try:
            if role not in ['reader', 'writer', 'commenter']:
                return "❌ Error: Invalid role. Use 'reader', 'writer', or 'commenter'"
            
            # Share sheet
            permission = {
                'type': 'user',
                'role': role,
                'emailAddress': email
            }
            
            self.drive_service.permissions().create(
                fileId=spreadsheet_id,
                body=permission,
                sendNotificationEmail=True
            ).execute()
            
            # Get sheet info
            sheet_info = self.drive_service.files().get(
                fileId=spreadsheet_id,
                fields='name, webViewLink'
            ).execute()
            
            return f"""✅ Sheet Shared Successfully!

📊 Sheet: {sheet_info.get('name')}
📧 Shared with: {email}
🔐 Permission: {role}
🔗 Link: {sheet_info.get('webViewLink')}

✅ Email notification sent to recipient.
"""
        
        except Exception as e:
            return f"❌ Error sharing sheet: {str(e)}"
    
    async def _arun(self, spreadsheet_id: str, email: str, role: str = "reader") -> str:
        return self._run(spreadsheet_id, email, role)


# ==================== HELPER FUNCTION ====================

def get_all_sheets_tools():
    """Get all Google Sheets tools for the agent"""
    return [
        CreateBillingSheetTool(),
        AddBillingChargeTool(),
        CreateLabResultsSheetTool(),
        AddLabResultTool(),
        CreatePatientStatsSheetTool(),
        AddPatientRecordTool(),
        ReadSheetDataTool(),
        ShareSheetTool()
    ]


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("📊 GOOGLE SHEETS TOOLS - Hospital Management")
    print("="*70)
    
    # Example 1: Create billing sheet
    print("\n1️⃣ Creating Billing Sheet...")
    tool1 = CreateBillingSheetTool()
    result1 = tool1._run(
        patient_name="Samarth Pawar",
        patient_id="REG2025001"
    )
    print(result1)
    
    # Extract spreadsheet ID from result (in real use, parse this)
    # For demo, using placeholder
    print("\n💡 Note: Use the spreadsheet ID from above to add charges.")
    
    print("\n" + "="*70)
    print("✅ Sheets Tools Test Complete!")
    print("="*70)


# ==================== LAB QUEUE TOOLS ====================

class AddLabQueueRowTool(BaseTool, SheetsToolBase):
    """Tool for adding lab appointment to Lab Queue sheet (for lab techs to track)."""
    
    name: str = "add_lab_queue_row"
    description: str = """Add a new lab appointment to the Lab Queue tracking sheet.
    Lab technicians will see this in their queue and update results when completed.
    Creates a row with status='PENDING' for lab staff to process."""
    args_schema: Type[BaseModel] = AddLabQueueRowInput
    
    sheets_service: Optional[object] = Field(default=None, exclude=True)
    drive_service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'sheets_token.pickle'):
        BaseTool.__init__(self)
        SheetsToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, patient_id: str, patient_name: str, email: str, phone: str,
             test_names: str, appointment_date: str, doc_link: str) -> str:
        try:
            # Get Sheet ID from environment
            spreadsheet_id = os.getenv('LAB_RESULTS_MONITORING_SHEET_ID')
            
            if not spreadsheet_id:
                return "❌ Error: LAB_RESULTS_MONITORING_SHEET_ID not found in .env file"
            
            # Get current timestamp
            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Prepare row data
            # Columns: Patient ID | Patient Name | Email | Phone | Test Names | Appointment Date | Status | Lab Results | Doc Link | Created At | Updated At
            row_data = [[
                patient_id,
                patient_name,
                email,
                phone,
                test_names,
                appointment_date,
                'PENDING',  # Initial status
                '',  # Lab results (empty, will be filled by lab tech)
                doc_link,
                created_at,
                created_at  # Updated at initially same as created at
            ]]
            
            # Append to Lab Queue sheet
            self.sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range='Lab Queue!A:K',  # A-K covers all 11 columns
                valueInputOption='USER_ENTERED',
                body={'values': row_data}
            ).execute()
            
            return f"""✅ Lab appointment added to queue!

📊 Lab Queue Details:
- Patient: {patient_name} ({patient_id})
- Tests: {test_names}
- Appointment: {appointment_date}
- Status: PENDING

🔬 Lab technicians can now:
  1. View this in Lab Queue sheet
  2. Update status to IN_PROGRESS when starting
  3. Add lab results when completed
  4. Update status to COMPLETED when done

📄 Doc Link: {doc_link}
"""
        
        except Exception as e:
            return f"❌ Error adding lab queue row: {str(e)}"
    
    async def _arun(self, patient_id: str, patient_name: str, email: str, phone: str,
                   test_names: str, appointment_date: str, doc_link: str) -> str:
        return self._run(patient_id, patient_name, email, phone, test_names, 
                        appointment_date, doc_link)


class ReadLabQueueResultsTool(BaseTool, SheetsToolBase):
    """Tool for reading lab results from Lab Queue sheet (when lab tech marks COMPLETED)."""
    
    name: str = "read_lab_queue_results"
    description: str = """Read lab results from Lab Queue sheet for a specific patient.
    Checks if lab tech has marked the status as COMPLETED and retrieves the results.
    Returns results if found, or indicates if still PENDING/IN_PROGRESS."""
    args_schema: Type[BaseModel] = Field(default=None)
    
    sheets_service: Optional[object] = Field(default=None, exclude=True)
    drive_service: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, credentials_file: str = 'credentials/client_secret.json', 
                 token_file: str = 'sheets_token.pickle'):
        BaseTool.__init__(self)
        SheetsToolBase.__init__(self, credentials_file, token_file)
    
    def _run(self, patient_id: str) -> str:
        try:
            # Get Sheet ID from environment
            spreadsheet_id = os.getenv('LAB_RESULTS_MONITORING_SHEET_ID')
            
            if not spreadsheet_id:
                return "❌ Error: LAB_RESULTS_MONITORING_SHEET_ID not found in .env file"
            
            # Read all data from Lab Queue sheet
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range='Lab Queue!A:K'
            ).execute()
            
            values = result.get('values', [])
            
            if not values or len(values) < 2:  # No data (just headers or empty)
                return f"❌ No lab appointments found for patient {patient_id}"
            
            # Headers: Patient ID | Patient Name | Email | Phone | Test Names | Appointment Date | Status | Lab Results | Doc Link | Created At | Updated At
            headers = values[0] if values else []
            
            # Find patient's row (most recent if multiple)
            patient_row = None
            for i in range(len(values) - 1, 0, -1):  # Start from end (most recent)
                row = values[i]
                if len(row) > 0 and row[0] == patient_id:
                    patient_row = row
                    break
            
            if not patient_row:
                return f"❌ No lab appointment found for patient {patient_id}"
            
            # Extract data
            patient_name = patient_row[1] if len(patient_row) > 1 else "Unknown"
            test_names = patient_row[4] if len(patient_row) > 4 else "Unknown"
            appointment_date = patient_row[5] if len(patient_row) > 5 else "Unknown"
            status = patient_row[6] if len(patient_row) > 6 else "PENDING"
            lab_results = patient_row[7] if len(patient_row) > 7 else ""
            
            if status == "COMPLETED" and lab_results:
                return f"""✅ Lab Results Available!

📊 Patient: {patient_name} ({patient_id})
🔬 Tests: {test_names}
📅 Appointment: {appointment_date}
✅ Status: {status}

📋 Lab Results:
{lab_results}

💡 These results have been retrieved from the Lab Queue sheet.
The AI will now analyze them and update the workflow document.
"""
            elif status == "IN_PROGRESS":
                return f"""⏳ Lab tests in progress...

📊 Patient: {patient_name} ({patient_id})
🔬 Tests: {test_names}
📅 Appointment: {appointment_date}
🔄 Status: IN_PROGRESS

💡 Lab technician is currently processing the tests.
Please wait for them to complete and update the status to COMPLETED.
"""
            else:  # PENDING
                return f"""⏳ Lab tests pending...

📊 Patient: {patient_name} ({patient_id})
🔬 Tests: {test_names}
📅 Appointment: {appointment_date}
⏰ Status: PENDING

💡 Waiting for lab technician to process the tests.
The patient should attend their appointment on {appointment_date}.
"""
        
        except Exception as e:
            return f"❌ Error reading lab queue results: {str(e)}"
    
    async def _arun(self, patient_id: str) -> str:
        return self._run(patient_id)


