"""
Setup Billing Sheets with Proper Headers
=========================================
Adds professional headers to billing, invoice, and payment tracking sheets
"""

import os
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_sheets_service():
    """Initialize Google Sheets service"""
    creds = None
    token_path = 'sheets_token.pickle'
    credentials_path = 'credentials/client_secret.json'
    
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('sheets', 'v4', credentials=creds)

def setup_billing_sheet(service, sheet_id):
    """Setup Billing Records Sheet with headers"""
    
    headers = [
        [
            "Billing Record ID",
            "Patient ID",
            "Patient Name",
            "Patient Email",
            "Service Type",
            "Service Name",
            "Original Amount",
            "Insurance Coverage",
            "Final Amount",
            "Payment Status",
            "Service Date",
            "Created At",
            "Notes"
        ]
    ]
    
    # Clear existing content
    service.spreadsheets().values().clear(
        spreadsheetId=sheet_id,
        range='Sheet1!A:M'
    ).execute()
    
    # Add headers
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range='Sheet1!A1:M1',
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
                        'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 1.0},
                        'textFormat': {
                            'bold': True,
                            'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}
                        },
                        'horizontalAlignment': 'CENTER'
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
            }
        },
        {
            'autoResizeDimensions': {
                'dimensions': {
                    'sheetId': 0,
                    'dimension': 'COLUMNS',
                    'startIndex': 0,
                    'endIndex': 13
                }
            }
        }
    ]
    
    service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={'requests': requests}
    ).execute()
    
    print(f"✅ Billing sheet headers setup complete!")

def setup_invoice_sheet(service, sheet_id):
    """Setup Invoice Sheet with headers"""
    
    headers = [
        [
            "Invoice ID",
            "Patient ID",
            "Patient Name",
            "Invoice Date",
            "Due Date",
            "Services",
            "Subtotal",
            "Tax",
            "Total Amount",
            "Status"
        ]
    ]
    
    # Clear existing content
    service.spreadsheets().values().clear(
        spreadsheetId=sheet_id,
        range='Sheet1!A:J'
    ).execute()
    
    # Add headers
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range='Sheet1!A1:J1',
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
                        'backgroundColor': {'red': 0.0, 'green': 0.8, 'blue': 0.4},
                        'textFormat': {
                            'bold': True,
                            'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}
                        },
                        'horizontalAlignment': 'CENTER'
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
            }
        },
        {
            'autoResizeDimensions': {
                'dimensions': {
                    'sheetId': 0,
                    'dimension': 'COLUMNS',
                    'startIndex': 0,
                    'endIndex': 10
                }
            }
        }
    ]
    
    service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={'requests': requests}
    ).execute()
    
    print(f"✅ Invoice sheet headers setup complete!")

def setup_payment_tracking_sheet(service, sheet_id):
    """Setup Payment Tracking Sheet with headers"""
    
    headers = [
        [
            "Payment ID",
            "Invoice ID",
            "Patient ID",
            "Patient Name",
            "Amount",
            "Payment Method",
            "Payment Status",
            "Payment Date",
            "Transaction ID",
            "Notes",
            "Created At"
        ]
    ]
    
    # Clear existing content
    service.spreadsheets().values().clear(
        spreadsheetId=sheet_id,
        range='Sheet1!A:K'
    ).execute()
    
    # Add headers
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range='Sheet1!A1:K1',
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
                        'backgroundColor': {'red': 1.0, 'green': 0.6, 'blue': 0.0},
                        'textFormat': {
                            'bold': True,
                            'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}
                        },
                        'horizontalAlignment': 'CENTER'
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
            }
        },
        {
            'autoResizeDimensions': {
                'dimensions': {
                    'sheetId': 0,
                    'dimension': 'COLUMNS',
                    'startIndex': 0,
                    'endIndex': 11
                }
            }
        }
    ]
    
    service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={'requests': requests}
    ).execute()
    
    print(f"✅ Payment tracking sheet headers setup complete!")

def main():
    print("=" * 80)
    print("BILLING SHEETS SETUP - ADDING HEADERS")
    print("=" * 80)
    print()
    
    # Get sheet IDs from environment
    billing_sheet_id = os.getenv('BILLING_SHEET_ID')
    invoice_sheet_id = os.getenv('INVOICE_SHEET_ID')
    payment_sheet_id = os.getenv('PAYMENT_TRACKING_SHEET_ID')
    
    print(f"📋 Billing Sheet ID: {billing_sheet_id}")
    print(f"📄 Invoice Sheet ID: {invoice_sheet_id}")
    print(f"💳 Payment Sheet ID: {payment_sheet_id}")
    print()
    
    # Initialize service
    print("🔧 Initializing Google Sheets service...")
    service = get_sheets_service()
    print("✅ Service initialized!")
    print()
    
    # Setup each sheet
    print("📋 Setting up Billing Records Sheet...")
    setup_billing_sheet(service, billing_sheet_id)
    print(f"🔗 View: https://docs.google.com/spreadsheets/d/{billing_sheet_id}")
    print()
    
    print("📄 Setting up Invoice Sheet...")
    setup_invoice_sheet(service, invoice_sheet_id)
    print(f"🔗 View: https://docs.google.com/spreadsheets/d/{invoice_sheet_id}")
    print()
    
    print("💳 Setting up Payment Tracking Sheet...")
    setup_payment_tracking_sheet(service, payment_sheet_id)
    print(f"🔗 View: https://docs.google.com/spreadsheets/d/{payment_sheet_id}")
    print()
    
    print("=" * 80)
    print("✅ ALL BILLING SHEETS SETUP COMPLETE!")
    print("=" * 80)
    print()
    print("📊 Header Colors:")
    print("   • Billing Records: Blue (Professional)")
    print("   • Invoices: Green (Financial)")
    print("   • Payment Tracking: Orange (Alert/Action)")
    print()
    print("🎯 Next Step: Run 'python test_all_workflow_tools.py' to verify 100% success!")

if __name__ == "__main__":
    main()
