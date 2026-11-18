#!/usr/bin/env python3
"""
Generate Google Calendar Token
"""

import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# Calendar scopes
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]

def generate_calendar_token():
    """Generate calendar token"""
    
    print("🔧 Generating Google Calendar Token")
    print("=" * 60)
    
    credentials_file = "credentials/client_secret.json"
    token_file = "calendar_token.pickle"
    
    # Delete old token if exists
    if os.path.exists(token_file):
        os.remove(token_file)
        print(f"🗑️  Removed old token: {token_file}")
    
    print(f"\n📋 Required scopes:")
    for scope in SCOPES:
        print(f"   • {scope}")
    
    print(f"\n🔓 Starting OAuth flow...")
    print("   A browser window will open for authentication")
    
    try:
        # Run OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Save credentials
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
        
        print(f"\n✅ Google Calendar token generated successfully!")
        print(f"📁 Token saved as: {token_file}")
        
        # Test the token
        from googleapiclient.discovery import build
        service = build('calendar', 'v3', credentials=creds)
        
        print("🧪 Testing API access...")
        calendar_list = service.calendarList().list(maxResults=1).execute()
        
        print(f"✅ Calendar API test successful!")
        print(f"\n🎉 You can now run: python main.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_calendar_token()
