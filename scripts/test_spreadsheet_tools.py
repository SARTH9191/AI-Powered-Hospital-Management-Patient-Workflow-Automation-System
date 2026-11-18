#!/usr/bin/env python3

"""
Test script for Google Sheets tools after updating to use sheets_token.pickle
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.google_sheets_tool import CreatePatientStatsSheetTool

def test_create_patient_stats_sheet():
    """Test creating a patient stats sheet with new authentication."""
    print("🧪 Testing Google Sheets authentication with sheets_token.pickle...")
    
    try:
        # Initialize the tool
        sheets_tool = CreatePatientStatsSheetTool()
        
        # Try to create a test sheet
        result = sheets_tool._run("Test Patient Stats Dashboard")
        
        print("✅ Success! Spreadsheet created successfully:")
        print(f"   {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating patient stats sheet: {e}")
        
        # Check if it's an authentication error
        if "insufficient authentication scopes" in str(e):
            print("\n🔧 Need to authenticate Google Sheets API with proper scopes:")
            print("   1. Create sheets_token.pickle with Sheets API scopes")
            print("   2. Ensure scopes include: https://www.googleapis.com/auth/spreadsheets")
            print("   3. Run Google OAuth flow for Sheets API specifically")
            
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 GOOGLE SHEETS AUTHENTICATION TEST")
    print("=" * 60)
    
    success = test_create_patient_stats_sheet()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed! Sheets integration is working.")
    else:
        print("⚠️  Authentication setup needed for Sheets API.")
    print("=" * 60)