"""
Doctor Review Sheet Tool
Creates a Google Sheet for doctor to review patient medical history and suggest tests
"""

import os
from typing import Optional, Type
from datetime import datetime
from pydantic import BaseModel, Field
from langchain.tools import BaseTool

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tools.google_sheets_tool import authenticate_sheets


class CreateDoctorReviewSheetInput(BaseModel):
    """Input schema for creating doctor review sheet"""
    patient_id: str = Field(description="Patient ID")
    patient_name: str = Field(description="Patient's full name")
    medical_history: str = Field(description="Complete medical history summary")
    current_symptoms: str = Field(description="Current symptoms/chief complaint")


class CreateDoctorReviewSheetTool(BaseTool):
    """Tool for creating a Google Sheet for doctor to review patient and suggest tests"""
    
    name: str = "create_doctor_review_sheet"
    description: str = """Create a Google Sheet for doctor to review patient medical history,
    write assessment, and suggest lab tests. Returns the sheet URL."""
    args_schema: Type[BaseModel] = CreateDoctorReviewSheetInput
    
    def _run(self, patient_id: str, patient_name: str, medical_history: str, 
             current_symptoms: str) -> str:
        
        try:
            # Authenticate with Google Sheets API
            creds = authenticate_sheets(
                credentials_file="credentials/client_secret.json",
                token_file="sheets_token.pickle"
            )
            
            service = build('sheets', 'v4', credentials=creds)
            
            # Create new spreadsheet
            spreadsheet_title = f"Doctor Review - {patient_name} ({patient_id})"
            spreadsheet = {
                'properties': {
                    'title': spreadsheet_title
                },
                'sheets': [
                    {
                        'properties': {
                            'title': 'Patient Medical Review',
                            'gridProperties': {
                                'rowCount': 50,
                                'columnCount': 10
                            }
                        }
                    }
                ]
            }
            
            result = service.spreadsheets().create(body=spreadsheet).execute()
            spreadsheet_id = result['spreadsheetId']
            spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
            
            # Prepare data for the sheet
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            values = [
                # Header
                ["DOCTOR REVIEW SHEET"],
                [""],
                # Patient Information Section
                ["PATIENT INFORMATION"],
                ["Patient ID:", patient_id],
                ["Patient Name:", patient_name],
                ["Review Date:", timestamp],
                [""],
                # Medical History Section
                ["MEDICAL HISTORY (Past + Current)"],
                ["", medical_history],
                [""],
                # Current Symptoms Section
                ["CURRENT SYMPTOMS / CHIEF COMPLAINT"],
                ["", current_symptoms],
                [""],
                [""],
                # Doctor Assessment Section (EDITABLE BY DOCTOR)
                ["━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"],
                ["DOCTOR'S ASSESSMENT (Please fill below)"],
                ["━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"],
                [""],
                ["Initial Assessment:", ""],
                [""],
                ["Preliminary Diagnosis:", ""],
                [""],
                ["Risk Assessment:", ""],
                [""],
                [""],
                # Recommended Tests Section (EDITABLE BY DOCTOR)
                ["━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"],
                ["RECOMMENDED LAB TESTS (Please list tests)"],
                ["━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"],
                ["Test Name", "Priority", "Reason"],
                ["1.", "", ""],
                ["2.", "", ""],
                ["3.", "", ""],
                ["4.", "", ""],
                ["5.", "", ""],
                [""],
                # Treatment Suggestions Section
                ["━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"],
                ["INITIAL TREATMENT SUGGESTIONS"],
                ["━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"],
                ["Medication/Intervention", "Dosage/Details"],
                ["1.", ""],
                ["2.", ""],
                ["3.", ""],
                [""],
                # Additional Notes
                ["━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"],
                ["ADDITIONAL NOTES / SPECIAL INSTRUCTIONS"],
                ["━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"],
                [""],
                [""],
                [""],
                # Doctor Signature
                [""],
                ["Doctor Name:", ""],
                ["Doctor Signature:", ""],
                ["Review Completed Date:", ""]
            ]
            
            # Write data to sheet
            body = {
                'values': values
            }
            
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='A1',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            # Format the sheet for better readability
            requests = [
                # Make header row bold and large
                {
                    'repeatCell': {
                        'range': {
                            'sheetId': 0,
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'textFormat': {
                                    'bold': True,
                                    'fontSize': 16
                                },
                                'backgroundColor': {
                                    'red': 0.2,
                                    'green': 0.6,
                                    'blue': 0.9
                                }
                            }
                        },
                        'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                    }
                },
                # Make section headers bold
                {
                    'repeatCell': {
                        'range': {
                            'sheetId': 0,
                            'startRowIndex': 2,
                            'endRowIndex': 3
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'textFormat': {
                                    'bold': True,
                                    'fontSize': 12
                                },
                                'backgroundColor': {
                                    'red': 0.9,
                                    'green': 0.9,
                                    'blue': 0.9
                                }
                            }
                        },
                        'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                    }
                },
                # Merge cells for headers
                {
                    'mergeCells': {
                        'range': {
                            'sheetId': 0,
                            'startRowIndex': 0,
                            'endRowIndex': 1,
                            'startColumnIndex': 0,
                            'endColumnIndex': 5
                        },
                        'mergeType': 'MERGE_ALL'
                    }
                },
                # Set column widths
                {
                    'updateDimensionProperties': {
                        'range': {
                            'sheetId': 0,
                            'dimension': 'COLUMNS',
                            'startIndex': 0,
                            'endIndex': 1
                        },
                        'properties': {
                            'pixelSize': 200
                        },
                        'fields': 'pixelSize'
                    }
                },
                {
                    'updateDimensionProperties': {
                        'range': {
                            'sheetId': 0,
                            'dimension': 'COLUMNS',
                            'startIndex': 1,
                            'endIndex': 5
                        },
                        'properties': {
                            'pixelSize': 400
                        },
                        'fields': 'pixelSize'
                    }
                }
            ]
            
            body = {
                'requests': requests
            }
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            
            return f"""✅ Doctor Review Sheet Created Successfully!

📊 **Sheet Details:**
• Title: {spreadsheet_title}
• URL: {spreadsheet_url}
• Patient: {patient_name} ({patient_id})

📝 **Sheet Contains:**
✅ Complete medical history (past + current)
✅ Current symptoms/chief complaint
✅ Section for doctor's assessment (editable)
✅ Section for recommended lab tests (editable)
✅ Section for treatment suggestions (editable)
✅ Space for doctor's notes and signature

👨‍⚕️ **Next Steps:**
1. Doctor will review the medical history
2. Doctor will write assessment in the designated section
3. Doctor will suggest lab tests in the tests section
4. Tests will be forwarded to next stage automatically

🔗 **Access Link:** {spreadsheet_url}"""
            
        except HttpError as error:
            return f"❌ Error creating doctor review sheet: {error}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not supported")
