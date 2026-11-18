"""
Google Workspace Authentication - ALL SCOPES
Run this ONCE to authenticate with all required permissions

Usage:
    python authenticate_google.py
"""

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# ALL SCOPES NEEDED FOR HOSPITAL MANAGEMENT
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',           # Send emails
    'https://www.googleapis.com/auth/gmail.readonly',       # Read emails
    'https://www.googleapis.com/auth/gmail.modify',         # Modify emails
    'https://www.googleapis.com/auth/drive',                # Drive full access
    'https://www.googleapis.com/auth/drive.file',           # Drive files
    'https://www.googleapis.com/auth/spreadsheets',         # Sheets
    'https://www.googleapis.com/auth/documents',            # Docs
    'https://www.googleapis.com/auth/calendar',             # Calendar
]

def authenticate():
    """Authenticate with all Google Workspace APIs"""
    
    creds = None
    
    # Check for existing token
    if os.path.exists('token.pickle'):
        print("📁 Found existing token...")
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            try:
                creds.refresh(Request())
                print("✅ Token refreshed successfully!")
            except Exception as e:
                print(f"⚠️ Refresh failed: {e}")
                print("🔐 Starting fresh authentication...")
                creds = None
        
        if not creds:
            print("\n🔐 Starting authentication flow...")
            print(f"📋 Requesting {len(SCOPES)} permissions for:")
            print("   • Gmail (send, read, modify)")
            print("   • Google Drive (full access)")
            print("   • Google Sheets")
            print("   • Google Docs")
            print("   • Google Calendar")
            print("\n🌐 Opening browser for authentication...")
            
            if not os.path.exists('credentials/client_secret.json'):
                print("\n❌ ERROR: credentials/client_secret.json not found!")
                print("📝 Please download OAuth 2.0 credentials from Google Cloud Console")
                return None
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials/client_secret.json', 
                    SCOPES
                )
                creds = flow.run_local_server(port=0)
                print("\n✅ Authentication successful!")
            except Exception as e:
                print(f"\n❌ Authentication failed: {e}")
                return None
        
        # Save token for future use
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
            print("💾 Token saved to token.pickle")
    else:
        print("✅ Using existing valid token")
    
    print("\n" + "="*50)
    print("✅ All Google Workspace APIs authenticated!")
    print("="*50)
    print("\n🎯 Permissions granted:")
    print("  ✅ Gmail (send, read, modify)")
    print("  ✅ Google Drive (full access)")
    print("  ✅ Google Sheets")
    print("  ✅ Google Docs")
    print("  ✅ Google Calendar")
    print("\n📧 Account: pawarsamarth786@gmail.com")
    print("\n🎉 You can now use all hospital management tools!")
    
    return creds

if __name__ == "__main__":
    print("="*50)
    print("Google Workspace Authentication")
    print("Hospital Management System")
    print("="*50)
    print()
    
    creds = authenticate()
    
    if creds:
        print("\n✅ Setup complete! Run your application now.")
    else:
        print("\n❌ Authentication failed. Please check your credentials and try again.")
