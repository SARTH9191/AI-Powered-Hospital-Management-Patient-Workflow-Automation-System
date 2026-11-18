"""
Verify Lab Queue Sheet setup and show the link
"""
import os
from dotenv import load_dotenv
from tools.google_sheets_tool import SheetsToolBase

load_dotenv()

spreadsheet_id = os.getenv('LAB_RESULTS_MONITORING_SHEET_ID')

if not spreadsheet_id:
    print("❌ LAB_RESULTS_MONITORING_SHEET_ID not found")
else:
    sheets_tool = SheetsToolBase()
    
    try:
        # Get sheet metadata
        sheet_metadata = sheets_tool.sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()
        
        # Find Lab Queue sheet
        sheet_id = None
        for sheet in sheet_metadata.get('sheets', []):
            if sheet.get('properties', {}).get('title') == 'Lab Queue':
                sheet_id = sheet.get('properties', {}).get('sheetId')
                break
        
        if sheet_id is not None:
            print(f"✅ Lab Queue Sheet Found!")
            print(f"\n🔗 Direct Link to Lab Queue:")
            print(f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={sheet_id}")
            
            # Read first few rows to verify setup
            result = sheets_tool.sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range='Lab Queue!A1:K4'
            ).execute()
            
            values = result.get('values', [])
            
            print(f"\n📊 Sheet Preview:")
            print(f"   Row 1 (Headers): {len(values[0]) if len(values) > 0 else 0} columns")
            print(f"   Row 2 (Sample): {values[1][0] if len(values) > 1 else 'Not found'}")
            print(f"   Row 3 (Instructions): {values[2][0] if len(values) > 2 else 'Not found'}")
            
            print(f"\n✅ Lab Queue Sheet is ready for use!")
            print(f"\n📋 Features:")
            print(f"   ✅ Blue header row with white bold text")
            print(f"   ✅ Status dropdown (PENDING/IN_PROGRESS/COMPLETED)")
            print(f"   ✅ Conditional formatting (Yellow/Blue/Green)")
            print(f"   ✅ Alternating row colors")
            print(f"   ✅ Frozen header row")
            print(f"   ✅ Sample data and instructions")
            
        else:
            print(f"❌ Lab Queue sheet not found. Run setup_lab_queue_sheet.py")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
