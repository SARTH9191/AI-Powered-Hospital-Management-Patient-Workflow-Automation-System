"""
Setup Billing Sheets for Hospital Management System
Creates Google Sheets for billing, invoicing, and payment tracking
"""

import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def initialize_sheets_service():
    """Initialize Google Sheets service."""
    try:
        creds = None
        token_path = os.path.join(os.path.dirname(__file__), 'credentials', 'token.json')
        credentials_path = os.path.join(os.path.dirname(__file__), 'credentials', 'credentials.json')
        
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        service = build('sheets', 'v4', credentials=creds)
        print("✅ Google Sheets service initialized")
        return service
        
    except Exception as e:
        print(f"❌ Error initializing Sheets service: {e}")
        return None

def create_billing_master_sheet(service):
    """Create the master billing tracking sheet."""
    try:
        # Create new spreadsheet
        spreadsheet_body = {
            'properties': {
                'title': 'Hospital Billing Master Sheet'
            },
            'sheets': [{
                'properties': {
                    'title': 'Billing Records'
                }
            }]
        }
        
        spreadsheet = service.spreadsheets().create(body=spreadsheet_body).execute()
        sheet_id = spreadsheet['spreadsheetId']
        
        # Set up headers
        headers = [
            'Record ID', 'Patient ID', 'Patient Name', 'Patient Email',
            'Service Type', 'Service Name', 'Original Amount', 'Insurance Coverage',
            'Final Amount', 'Payment Status', 'Service Date', 'Created At',
            'Notes', 'Payment Method', 'Payment Amount', 'Payment Date'
        ]
        
        # Add headers and format
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range='A1:P1',
            valueInputOption='RAW',
            body={'values': [headers]}
        ).execute()
        
        # Format headers (bold, background color)
        service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body={
                'requests': [{
                    'repeatCell': {
                        'range': {
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'textFormat': {'bold': True},
                                'backgroundColor': {'red': 0.8, 'green': 0.9, 'blue': 1.0}
                            }
                        },
                        'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                    }
                }]
            }
        ).execute()
        
        print(f"✅ Billing Master Sheet created: {sheet_id}")
        print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
        return sheet_id
        
    except HttpError as e:
        print(f"❌ Error creating billing sheet: {e}")
        return None

def create_invoice_sheet(service):
    """Create the invoice tracking sheet."""
    try:
        spreadsheet_body = {
            'properties': {
                'title': 'Hospital Invoice Tracking'
            },
            'sheets': [{
                'properties': {
                    'title': 'Invoices'
                }
            }]
        }
        
        spreadsheet = service.spreadsheets().create(body=spreadsheet_body).execute()
        sheet_id = spreadsheet['spreadsheetId']
        
        headers = [
            'Invoice ID', 'Patient ID', 'Invoice Date', 'Due Date',
            'Subtotal', 'Insurance Discount', 'Final Total', 'Status',
            'Line Items (JSON)', 'Created At'
        ]
        
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range='A1:J1',
            valueInputOption='RAW',
            body={'values': [headers]}
        ).execute()
        
        # Format headers
        service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body={
                'requests': [{
                    'repeatCell': {
                        'range': {
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'textFormat': {'bold': True},
                                'backgroundColor': {'red': 0.9, 'green': 1.0, 'blue': 0.8}
                            }
                        },
                        'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                    }
                }]
            }
        ).execute()
        
        print(f"✅ Invoice Sheet created: {sheet_id}")
        print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
        return sheet_id
        
    except HttpError as e:
        print(f"❌ Error creating invoice sheet: {e}")
        return None

def create_payment_tracking_sheet(service):
    """Create the payment tracking sheet.""" 
    try:
        spreadsheet_body = {
            'properties': {
                'title': 'Hospital Payment Tracking'
            },
            'sheets': [{
                'properties': {
                    'title': 'Payments'
                }
            }]
        }
        
        spreadsheet = service.spreadsheets().create(body=spreadsheet_body).execute()
        sheet_id = spreadsheet['spreadsheetId']
        
        headers = [
            'Payment ID', 'Invoice ID', 'Patient ID', 'Patient Name',
            'Amount', 'Payment Method', 'Payment Date', 'Status',
            'Transaction ID', 'Notes', 'Created At'
        ]
        
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range='A1:K1',
            valueInputOption='RAW',
            body={'values': [headers]}
        ).execute()
        
        # Format headers
        service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body={
                'requests': [{
                    'repeatCell': {
                        'range': {
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'textFormat': {'bold': True},
                                'backgroundColor': {'red': 1.0, 'green': 0.9, 'blue': 0.8}
                            }
                        },
                        'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                    }
                }]
            }
        ).execute()
        
        print(f"✅ Payment Tracking Sheet created: {sheet_id}")
        print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
        return sheet_id
        
    except HttpError as e:
        print(f"❌ Error creating payment tracking sheet: {e}")
        return None

def add_sample_data(service, billing_sheet_id, invoice_sheet_id, payment_sheet_id):
    """Add sample data to the sheets for testing."""
    try:
        # Sample billing data
        billing_sample = [
            ['BILL_REG2025001_20251029120000', 'REG2025001', 'John Doe', 'john.doe@email.com',
             'Consultation', 'General Medicine Consultation', 500.0, '70%', 150.0, 'Pending', 
             '2025-10-29', '2025-10-29 12:00:00', 'Initial consultation'],
            ['BILL_REG2025001_20251029120100', 'REG2025001', 'John Doe', 'john.doe@email.com',
             'Lab Test', 'Complete Blood Count', 200.0, '80%', 40.0, 'Pending',
             '2025-10-29', '2025-10-29 12:01:00', 'Ordered during consultation'],
            ['BILL_REG2025002_20251029120200', 'REG2025002', 'Jane Smith', 'jane.smith@email.com',
             'Procedure', 'X-Ray Chest', 800.0, '60%', 320.0, 'Paid',
             '2025-10-28', '2025-10-29 12:02:00', 'Emergency procedure']
        ]
        
        service.spreadsheets().values().append(
            spreadsheetId=billing_sheet_id,
            range='A:P',
            valueInputOption='USER_ENTERED',
            body={'values': billing_sample}
        ).execute()
        
        # Sample invoice data
        invoice_sample = [
            ['INV_REG2025001_20251029120300', 'REG2025001', '2025-10-29', '2025-11-28',
             700.0, 560.0, 190.0, 'Generated', 
             '[{"service": "Consultation", "amount": 150}, {"service": "Lab Test", "amount": 40}]',
             '2025-10-29 12:03:00']
        ]
        
        service.spreadsheets().values().append(
            spreadsheetId=invoice_sheet_id,
            range='A:J',
            valueInputOption='USER_ENTERED',
            body={'values': invoice_sample}
        ).execute()
        
        # Sample payment data
        payment_sample = [
            ['PAY_001', 'INV_REG2025002_20251028', 'REG2025002', 'Jane Smith',
             320.0, 'UPI', '2025-10-29', 'Completed', 'TXN123456789',
             'Payment via Google Pay', '2025-10-29 11:30:00']
        ]
        
        service.spreadsheets().values().append(
            spreadsheetId=payment_sheet_id,
            range='A:K',
            valueInputOption='USER_ENTERED',
            body={'values': payment_sample}
        ).execute()
        
        print("✅ Sample data added to all sheets")
        
    except HttpError as e:
        print(f"❌ Error adding sample data: {e}")

def main():
    """Main function to set up all billing sheets."""
    print("🏥 Setting up Hospital Billing Sheets...")
    print("=" * 50)
    
    # Initialize service
    service = initialize_sheets_service()
    if not service:
        print("❌ Failed to initialize Google Sheets service")
        return
    
    # Create sheets
    billing_sheet_id = create_billing_master_sheet(service)
    invoice_sheet_id = create_invoice_sheet(service)
    payment_sheet_id = create_payment_tracking_sheet(service)
    
    if billing_sheet_id and invoice_sheet_id and payment_sheet_id:
        print("\n✅ All sheets created successfully!")
        print("\n🔧 Next Steps:")
        print("1. Add these IDs to your .env file:")
        print(f"   BILLING_SHEET_ID={billing_sheet_id}")
        print(f"   INVOICE_SHEET_ID={invoice_sheet_id}")
        print(f"   PAYMENT_TRACKING_SHEET_ID={payment_sheet_id}")
        print("\n2. Share sheets with hospital staff")
        print("3. Test the billing tools")
        
        # Add sample data
        print("\n📊 Adding sample data for testing...")
        add_sample_data(service, billing_sheet_id, invoice_sheet_id, payment_sheet_id)
        
        print("\n🎉 Billing sheets setup complete!")
    else:
        print("❌ Failed to create some sheets")

if __name__ == "__main__":
    main()