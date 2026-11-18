#!/usr/bin/env python3
"""
Regenerate Google Sheets API Token
Creates sheets_token.pickle with proper scopes
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

def regenerate_sheets_token():
    """Regenerate Google Sheets API token with proper scopes"""
    
    print("🔧 Regenerating Google Sheets API Token")
    print("=" * 50)
    
    # Delete old token if exists
    token_file = "sheets_token.pickle"
    if os.path.exists(token_file):
        os.remove(token_file)
        print(f"🗑️ Removed old token: {token_file}")
    
    try:
        from tools.google_sheets_tool import authenticate_sheets
        
        print("\n📋 Required scopes:")
        print("   • https://www.googleapis.com/auth/spreadsheets")
        print("   • https://www.googleapis.com/auth/drive.file")
        
        print("\n🔓 Starting OAuth flow...")
        print("   A browser window will open for authentication")
        print("   Please login and authorize the application")
        
        # This will create sheets_token.pickle automatically
        creds = authenticate_sheets(
            credentials_file="credentials/client_secret.json",
            token_file="sheets_token.pickle"
        )
        
        if creds and creds.valid:
            print("\n✅ Google Sheets token generated successfully!")
            print("📁 Token saved as: sheets_token.pickle")
            
            # Test the token by creating a simple service
            from googleapiclient.discovery import build
            service = build('sheets', 'v4', credentials=creds)
            
            print("🧪 Testing API access...")
            
            # Try to create a test spreadsheet
            spreadsheet = {
                'properties': {
                    'title': 'Test Spreadsheet - Please Delete'
                }
            }
            
            result = service.spreadsheets().create(body=spreadsheet).execute()
            spreadsheet_id = result.get('spreadsheetId')
            
            print(f"✅ Test spreadsheet created successfully!")
            print(f"📊 Spreadsheet ID: {spreadsheet_id}")
            
            # Clean up - delete the test spreadsheet
            try:
                from googleapiclient.discovery import build as build_drive
                drive_service = build_drive('drive', 'v3', credentials=creds)
                drive_service.files().delete(fileId=spreadsheet_id).execute()
                print("🗑️ Test spreadsheet deleted")
            except Exception as e:
                print(f"⚠️ Test spreadsheet created but couldn't delete (manual cleanup needed): {e}")
            
            print("\n🎉 Google Sheets API is ready for use!")
            print("\n✅ You can now run: python main.py")
            
        else:
            print("❌ Failed to generate valid credentials")
            
    except Exception as e:
        print(f"❌ Error generating token: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    regenerate_sheets_token()
