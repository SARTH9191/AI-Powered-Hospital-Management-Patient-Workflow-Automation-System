"""
Script to create Lab Results Master Sheet for all patients
This sheet will be used by lab technicians to enter test results
AI Agent will read from this sheet to answer patient queries

Usage:
    python scripts/create_lab_results_sheet.py
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file'
]

def get_credentials():
    """Get Google credentials"""
    creds = None
    token_path = 'credentials/token.pickle'
    
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
    
    return creds

def create_lab_results_sheet():
    """Create the master Lab Results sheet"""
    print("\n🔬 CREATING LAB RESULTS MASTER SHEET")
    print("=" * 60)
    
    creds = get_credentials()
    sheets_service = build('sheets', 'v4', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    
    # Create spreadsheet
    spreadsheet = {
        'properties': {
            'title': '🏥 Hospital Lab Results Database - Master Sheet',
            'locale': 'en_US',
            'timeZone': 'Asia/Kolkata'
        },
        'sheets': [{
            'properties': {
                'title': 'Lab Results',
                'gridProperties': {
                    'rowCount': 1000,
                    'columnCount': 12,
                    'frozenRowCount': 1  # Freeze header row
                }
            }
        }]
    }
    
    result = sheets_service.spreadsheets().create(body=spreadsheet).execute()
    spreadsheet_id = result['spreadsheetId']
    spreadsheet_url = result['spreadsheetUrl']
    
    # Get the actual sheet ID (not spreadsheet ID)
    sheet_id = result['sheets'][0]['properties']['sheetId']
    
    print(f"\n✅ Created spreadsheet: {spreadsheet_id}")
    print(f"📊 URL: {spreadsheet_url}")
    print(f"📋 Sheet ID: {sheet_id}")
    
    # Format header row
    header_data = [[
        "Patient ID",      # A - REG2025001
        "Patient Name",    # B - John Doe
        "Test Name",       # C - CBC, Glucose, etc.
        "Result",          # D - 12.5
        "Unit",            # E - g/dL
        "Normal Range",    # F - 12-16
        "Status",          # G - Pending/Complete/Review
        "Test Date",       # H - 2025-10-21
        "Ordered Date",    # I - 2025-10-20
        "Technician",      # J - Tech-John
        "Notes",           # K - Any observations
        "Last Updated"     # L - Auto timestamp
    ]]
    
    # Write headers
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range='Lab Results!A1:L1',
        valueInputOption='RAW',
        body={'values': header_data}
    ).execute()
    
    print("✅ Added headers")
    
    # Format the sheet
    requests = [
        # Header row formatting
        {
            'repeatCell': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': 0,
                    'endRowIndex': 1
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
                        'textFormat': {
                            'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                            'fontSize': 11,
                            'bold': True
                        },
                        'horizontalAlignment': 'CENTER',
                        'verticalAlignment': 'MIDDLE'
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)'
            }
        },
        # Set column widths
        {
            'updateDimensionProperties': {
                'range': {'sheetId': sheet_id, 'dimension': 'COLUMNS', 'startIndex': 0, 'endIndex': 1},
                'properties': {'pixelSize': 120},
                'fields': 'pixelSize'
            }
        },
        {
            'updateDimensionProperties': {
                'range': {'sheetId': sheet_id, 'dimension': 'COLUMNS', 'startIndex': 1, 'endIndex': 2},
                'properties': {'pixelSize': 150},
                'fields': 'pixelSize'
            }
        },
        {
            'updateDimensionProperties': {
                'range': {'sheetId': sheet_id, 'dimension': 'COLUMNS', 'startIndex': 2, 'endIndex': 3},
                'properties': {'pixelSize': 150},
                'fields': 'pixelSize'
            }
        },
        {
            'updateDimensionProperties': {
                'range': {'sheetId': sheet_id, 'dimension': 'COLUMNS', 'startIndex': 6, 'endIndex': 7},
                'properties': {'pixelSize': 120},
                'fields': 'pixelSize'
            }
        },
        # Add data validation for Status column (G)
        {
            'setDataValidation': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': 1,
                    'endRowIndex': 1000,
                    'startColumnIndex': 6,
                    'endColumnIndex': 7
                },
                'rule': {
                    'condition': {
                        'type': 'ONE_OF_LIST',
                        'values': [
                            {'userEnteredValue': 'Pending'},
                            {'userEnteredValue': 'In Progress'},
                            {'userEnteredValue': 'Complete'},
                            {'userEnteredValue': 'Review Required'},
                            {'userEnteredValue': 'Cancelled'}
                        ]
                    },
                    'showCustomUi': True,
                    'strict': True
                }
            }
        },
        # Add alternating row colors
        {
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [{
                        'sheetId': sheet_id,
                        'startRowIndex': 1,
                        'endRowIndex': 1000
                    }],
                    'booleanRule': {
                        'condition': {
                            'type': 'CUSTOM_FORMULA',
                            'values': [{'userEnteredValue': '=ISEVEN(ROW())'}]
                        },
                        'format': {
                            'backgroundColor': {'red': 0.95, 'green': 0.95, 'blue': 0.95}
                        }
                    }
                },
                'index': 0
            }
        }
    ]
    
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()
    
    print("✅ Applied formatting")
    
    # Add sample data for reference
    sample_data = [
        [
            "REG2025SAMPLE",
            "Sample Patient",
            "Complete Blood Count (CBC)",
            "12.5",
            "g/dL",
            "12-16",
            "Complete",
            "2025-10-21",
            "2025-10-20",
            "Lab-Tech-Demo",
            "Normal range - No action needed",
            "2025-10-21 14:30"
        ],
        [
            "REG2025SAMPLE",
            "Sample Patient",
            "Blood Glucose (Fasting)",
            "95",
            "mg/dL",
            "70-110",
            "Complete",
            "2025-10-21",
            "2025-10-20",
            "Lab-Tech-Demo",
            "Fasting sample - Normal",
            "2025-10-21 14:35"
        ]
    ]
    
    sheets_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range='Lab Results!A2:L3',
        valueInputOption='RAW',
        body={'values': sample_data}
    ).execute()
    
    print("✅ Added sample data (2 rows)")
    
    # Share with yourself (make sure you can edit)
    try:
        drive_service.permissions().create(
            fileId=spreadsheet_id,
            body={
                'type': 'user',
                'role': 'writer',
                'emailAddress': os.getenv('GMAIL_USER', 'pawarsamarth786@gmail.com')
            },
            fields='id'
        ).execute()
        print(f"✅ Shared with {os.getenv('GMAIL_USER')}")
    except Exception as e:
        print(f"⚠️ Sharing note: {e}")
    
    # Update .env file
    print("\n" + "=" * 60)
    print("🎯 IMPORTANT: Add this to your .env file:")
    print("=" * 60)
    print(f"LAB_RESULTS_SHEET_ID={spreadsheet_id}")
    print("=" * 60)
    
    print("\n✅ Lab Results Master Sheet created successfully!")
    print(f"\n📊 Open it here: {spreadsheet_url}")
    print("\n📋 What lab technicians should do:")
    print("   1. Open this sheet")
    print("   2. Find patient by Patient ID (REG2025XXX)")
    print("   3. Fill in test results")
    print("   4. Set Status to 'Complete'")
    print("   5. AI will read this data automatically!")
    
    return {
        'spreadsheet_id': spreadsheet_id,
        'spreadsheet_url': spreadsheet_url
    }

if __name__ == "__main__":
    try:
        result = create_lab_results_sheet()
        print("\n🎉 SUCCESS! Lab Results sheet is ready for use!")
        print(f"📋 Sheet ID: {result['spreadsheet_id']}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
