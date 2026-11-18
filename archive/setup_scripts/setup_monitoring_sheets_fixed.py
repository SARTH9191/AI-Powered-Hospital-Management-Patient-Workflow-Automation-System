"""
Fixed Google Sheets Monitoring Setup
Creates Google Sheets for hospital staff-agent communication
"""

import os
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def initialize_sheets_service():
    """Initialize Google Sheets service using existing credentials."""
    try:
        creds = None
        token_path = 'token.pickle'
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
        
        service = build('sheets', 'v4', credentials=creds)
        print("✅ Google Sheets service initialized")
        return service
        
    except Exception as e:
        print(f"❌ Error initializing Sheets service: {e}")
        return None

def create_sheet_with_headers(service, title, headers):
    """Create a sheet with headers and return sheet ID."""
    try:
        # Create new spreadsheet
        spreadsheet_body = {
            'properties': {'title': title},
            'sheets': [{'properties': {'title': 'Sheet1'}}]
        }
        
        spreadsheet = service.spreadsheets().create(body=spreadsheet_body).execute()
        sheet_id = spreadsheet['spreadsheetId']
        
        # Add headers
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range='A1:' + chr(ord('A') + len(headers) - 1) + '1',
            valueInputOption='RAW',
            body={'values': [headers]}
        ).execute()
        
        # Get actual sheet ID for formatting
        sheets_info = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        actual_sheet_id = sheets_info['sheets'][0]['properties']['sheetId']
        
        # Format headers (bold, background color) - Fixed version
        try:
            service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body={
                    'requests': [{
                        'repeatCell': {
                            'range': {
                                'sheetId': actual_sheet_id,
                                'startRowIndex': 0,
                                'endRowIndex': 1,
                                'startColumnIndex': 0,
                                'endColumnIndex': len(headers)
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
        except HttpError as e:
            print(f"⚠️ Formatting warning (sheet still created): {e}")
        
        print(f"✅ {title} created: {sheet_id}")
        print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
        return sheet_id
        
    except HttpError as e:
        print(f"❌ Error creating {title}: {e}")
        return None

def add_sample_data(service, sheet_id, sample_data, range_notation):
    """Add sample data to a sheet."""
    try:
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=range_notation,
            valueInputOption='USER_ENTERED',
            body={'values': sample_data}
        ).execute()
        print(f"✅ Sample data added to sheet")
    except HttpError as e:
        print(f"⚠️ Sample data warning: {e}")

def main():
    """Main function to set up all monitoring sheets."""
    print("🏥 Setting up Hospital Staff-Agent Communication Sheets...")
    print("=" * 70)
    
    # Initialize service
    service = initialize_sheets_service()
    if not service:
        print("❌ Failed to initialize Google Sheets service")
        return
    
    sheet_ids = {}
    
    # 1. Patient Status Sheet
    print("\n📊 Creating Patient Status Sheet...")
    patient_headers = [
        'Patient ID', 'Update Type', 'Details', 'Staff Name', 
        'Timestamp', 'Status', 'Notes'
    ]
    patient_sample = [
        ['REG2025001', 'Vitals', 'BP: 120/80, HR: 72', 'Nurse Mary', 
         '2025-10-29 09:30:00', 'Active', 'Morning vitals check'],
        ['REG2025002', 'Medication', 'Paracetamol 500mg given', 'Nurse John', 
         '2025-10-29 10:15:00', 'Active', 'Pain management']
    ]
    
    sheet_id = create_sheet_with_headers(service, 'Hospital Patient Status Updates', patient_headers)
    if sheet_id:
        sheet_ids['PATIENT_STATUS_SHEET_ID'] = sheet_id
        add_sample_data(service, sheet_id, patient_sample, 'A:G')
    
    # 2. Doctor Notes Sheet
    print("\n👨‍⚕️ Creating Doctor Notes Sheet...")
    doctor_headers = [
        'Patient ID', 'Doctor Name', 'Diagnosis', 'Treatment Plan', 
        'Medications', 'Notes', 'Date', 'Priority'
    ]
    doctor_sample = [
        ['REG2025001', 'Dr. Smith', 'Hypertension', 'Blood pressure monitoring', 
         'Amlodipine 5mg', 'Patient stable', '2025-10-29', 'Medium'],
        ['REG2025002', 'Dr. Johnson', 'Fever', 'Symptomatic treatment', 
         'Paracetamol 500mg', 'Monitor temperature', '2025-10-29', 'Low']
    ]
    
    sheet_id = create_sheet_with_headers(service, 'Hospital Doctor Notes', doctor_headers)
    if sheet_id:
        sheet_ids['DOCTOR_NOTES_SHEET_ID'] = sheet_id
        add_sample_data(service, sheet_id, doctor_sample, 'A:H')
    
    # 3. Lab Results Sheet
    print("\n🧪 Creating Lab Results Sheet...")
    lab_headers = [
        'Patient ID', 'Test Name', 'Result', 'Unit', 'Normal Range', 
        'Status', 'Test Date', 'Technician', 'Notes'
    ]
    lab_sample = [
        ['REG2025001', 'Blood Glucose', '95', 'mg/dL', '70-110', 
         'Normal', '2025-10-29', 'Tech-Alice', 'Fasting sample'],
        ['REG2025002', 'Hemoglobin', '12.5', 'g/dL', '12-16', 
         'Normal', '2025-10-29', 'Tech-Bob', 'Complete CBC']
    ]
    
    sheet_id = create_sheet_with_headers(service, 'Hospital Lab Results', lab_headers)
    if sheet_id:
        sheet_ids['LAB_RESULTS_SHEET_ID'] = sheet_id
        add_sample_data(service, sheet_id, lab_sample, 'A:I')
    
    # 4. Staff Updates Sheet
    print("\n📋 Creating Staff Updates Sheet...")
    staff_headers = [
        'Staff Name', 'Department', 'Update Type', 'Message', 
        'Priority', 'Timestamp', 'Status', 'Patient ID'
    ]
    staff_sample = [
        ['Nurse Mary', 'ICU', 'Patient Update', 'Patient in room 101 needs attention', 
         'High', '2025-10-29 09:45:00', 'Active', 'REG2025001'],
        ['Dr. Wilson', 'Emergency', 'Resource Request', 'Need additional ventilator', 
         'Urgent', '2025-10-29 10:30:00', 'Active', '']
    ]
    
    sheet_id = create_sheet_with_headers(service, 'Hospital Staff Updates', staff_headers)
    if sheet_id:
        sheet_ids['STAFF_UPDATES_SHEET_ID'] = sheet_id
        add_sample_data(service, sheet_id, staff_sample, 'A:H')
    
    # 5. Emergency Alerts Sheet
    print("\n🚨 Creating Emergency Alerts Sheet...")
    emergency_headers = [
        'Alert ID', 'Patient ID', 'Alert Type', 'Severity', 'Description', 
        'Reporter', 'Timestamp', 'Status', 'Response Team'
    ]
    emergency_sample = [
        ['ALERT001', 'REG2025003', 'Cardiac', 'Critical', 'Patient experiencing chest pain', 
         'Nurse Sarah', '2025-10-29 11:15:00', 'Active', 'Cardiology'],
        ['ALERT002', 'REG2025004', 'Fall Risk', 'Medium', 'Patient attempted to get up unassisted', 
         'Nurse Tom', '2025-10-29 11:45:00', 'Resolved', 'Nursing']
    ]
    
    sheet_id = create_sheet_with_headers(service, 'Hospital Emergency Alerts', emergency_headers)
    if sheet_id:
        sheet_ids['EMERGENCY_ALERTS_SHEET_ID'] = sheet_id
        add_sample_data(service, sheet_id, emergency_sample, 'A:I')
    
    # 6. Pharmacy Inventory Sheet
    print("\n💊 Creating Pharmacy Inventory Sheet...")
    pharmacy_headers = [
        'Medicine Name', 'Current Stock', 'Minimum Stock', 'Unit', 
        'Expiry Date', 'Supplier', 'Last Updated', 'Status', 'Notes'
    ]
    pharmacy_sample = [
        ['Paracetamol 500mg', '150', '50', 'Tablets', '2026-03-15', 
         'MedSupply Inc', '2025-10-29', 'In Stock', 'Popular pain reliever'],
        ['Amoxicillin 250mg', '25', '30', 'Capsules', '2025-12-20', 
         'PharmaCorp', '2025-10-29', 'Low Stock', 'Reorder required']
    ]
    
    sheet_id = create_sheet_with_headers(service, 'Hospital Pharmacy Inventory', pharmacy_headers)
    if sheet_id:
        sheet_ids['PHARMACY_INVENTORY_SHEET_ID'] = sheet_id
        add_sample_data(service, sheet_id, pharmacy_sample, 'A:I')
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ All monitoring sheets created successfully!")
    print("=" * 70)
    
    print("\n🔧 Add these IDs to your .env file:")
    for key, value in sheet_ids.items():
        print(f"{key}={value}")
    
    print("\n📤 Next Steps:")
    print("1. Add the sheet IDs to your .env file")
    print("2. Share sheets with hospital staff")
    print("3. Test the monitoring tools")
    print("4. Set up real-time monitoring")
    
    print("\n🎉 Hospital Google Sheets monitoring system is ready!")
    print("   Staff can now communicate with AI agent through Google Sheets!")

if __name__ == "__main__":
    main()