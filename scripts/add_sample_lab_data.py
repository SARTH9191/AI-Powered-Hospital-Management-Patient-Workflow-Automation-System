"""
Add sample lab results data to the sheet
Run this to populate the sheet with test data
"""

import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import pickle
from datetime import datetime

def get_credentials():
    """Get Google credentials"""
    with open('credentials/token.pickle', 'rb') as token:
        return pickle.load(token)

def add_sample_data():
    """Add sample lab results"""
    print("\n📊 ADDING SAMPLE LAB RESULTS DATA")
    print("=" * 60)
    
    sheet_id = os.getenv('LAB_RESULTS_SHEET_ID')
    if not sheet_id:
        print("❌ LAB_RESULTS_SHEET_ID not found in .env")
        return
    
    print(f"✅ Sheet ID: {sheet_id}")
    
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)
    
    # Sample data for testing
    today = datetime.now().strftime("%Y-%m-%d")
    
    sample_data = [
        [
            "REG2025SAMPLE",
            "Sample Patient",
            "Complete Blood Count (CBC)",
            "12.5",
            "g/dL",
            "12-16",
            "Complete",
            today,
            today,
            "Lab-Tech-John",
            "Normal range - No action needed",
            f"{today} 14:30"
        ],
        [
            "REG2025SAMPLE",
            "Sample Patient",
            "Blood Glucose (Fasting)",
            "95",
            "mg/dL",
            "70-110",
            "Complete",
            today,
            today,
            "Lab-Tech-John",
            "Fasting sample - Normal",
            f"{today} 14:35"
        ],
        [
            "REG2025SAMPLE",
            "Sample Patient",
            "Lipid Profile - Total Cholesterol",
            "185",
            "mg/dL",
            "<200",
            "Complete",
            today,
            today,
            "Lab-Tech-Mary",
            "Within normal limits",
            f"{today} 15:00"
        ],
        [
            "REG2025TEST",
            "Test Patient",
            "Hemoglobin",
            "14.2",
            "g/dL",
            "13-17",
            "Complete",
            today,
            today,
            "Lab-Tech-John",
            "Normal",
            f"{today} 15:30"
        ],
        [
            "REG2025TEST",
            "Test Patient",
            "Platelet Count",
            "",
            "cells/mcL",
            "150,000-450,000",
            "Pending",
            "",
            today,
            "Lab-Tech-Mary",
            "Sample processing",
            f"{today} 16:00"
        ]
    ]
    
    # Add data to sheet
    result = service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range='Lab Results!A2:L100',
        valueInputOption='RAW',
        body={'values': sample_data}
    ).execute()
    
    print(f"✅ Added {len(sample_data)} lab result records!")
    print(f"   Updated range: {result.get('updates', {}).get('updatedRange', 'N/A')}")
    
    print("\n📋 Sample Data Summary:")
    print("   • REG2025SAMPLE - 3 tests (all complete)")
    print("   • REG2025TEST - 2 tests (1 complete, 1 pending)")
    
    print("\n✅ Sheet is ready for testing!")
    print(f"🔗 View sheet: https://docs.google.com/spreadsheets/d/{sheet_id}/edit")

if __name__ == "__main__":
    try:
        add_sample_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
