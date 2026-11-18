"""
Create Patient Tracking Spreadsheet for City Hospital

This script creates a Google Sheet for tracking patient records.
Run this once to get the spreadsheet ID.

Usage:
    python setup_tracking_sheet.py
"""

import os
import sys
from tools.google_sheets_tool import CreatePatientStatsSheetTool

def main():
    print("=" * 60)
    print("🏥 CITY HOSPITAL - PATIENT TRACKING SHEET SETUP")
    print("=" * 60)
    print()
    
    # Check authentication
    if not os.path.exists("token.pickle"):
        print("❌ ERROR: token.pickle not found!")
        print()
        print("Please run authentication first:")
        print("  python authenticate_google.py")
        print()
        return 1
    
    print("📋 Creating Patient Tracking Spreadsheet...")
    print()
    
    try:
        tool = CreatePatientStatsSheetTool()
        result = tool._run(sheet_name="City_Hospital_Patient_Tracking")
        
        print("✅ SUCCESS!")
        print()
        print(result)
        print()
        
        # Extract spreadsheet ID
        if "spreadsheet/d/" in result:
            spreadsheet_id = result.split("spreadsheet/d/")[1].split("/")[0]
            print("=" * 60)
            print("📊 SPREADSHEET ID:")
            print(f"   {spreadsheet_id}")
            print("=" * 60)
            print()
            print("💡 TO USE THIS SPREADSHEET:")
            print()
            print("Option 1: Set Environment Variable (PowerShell)")
            print(f'   $env:PATIENT_TRACKING_SHEET_ID="{spreadsheet_id}"')
            print()
            print("Option 2: Add to .env file")
            print(f'   PATIENT_TRACKING_SHEET_ID={spreadsheet_id}')
            print()
            print("Option 3: Run this command to set permanently:")
            print(f'   [System.Environment]::SetEnvironmentVariable("PATIENT_TRACKING_SHEET_ID", "{spreadsheet_id}", "User")')
            print()
            
            # Save to .env file
            try:
                with open(".env", "a") as f:
                    f.write(f"\n# Patient Tracking Spreadsheet\n")
                    f.write(f"PATIENT_TRACKING_SHEET_ID={spreadsheet_id}\n")
                print("✅ Added to .env file")
                print()
            except:
                pass
                
        return 0
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print()
        print("💡 Troubleshooting:")
        print("1. Make sure you ran: python authenticate_google.py")
        print("2. Check that Sheets API is enabled in Google Console")
        print("3. Make sure token.pickle has correct permissions")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
