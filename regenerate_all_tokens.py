#!/usr/bin/env python3
"""
Regenerate All Google API Tokens
Creates all required token files with proper scopes
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

def regenerate_all_tokens():
    """Regenerate all Google API tokens"""
    
    print("🔧 Regenerating All Google API Tokens")
    print("=" * 60)
    
    # List of tokens to regenerate
    tokens = [
        {
            'name': 'Gmail',
            'file': 'token.pickle',
            'module': 'gmail_tool',
            'function': 'authenticate_gmail',
            'scopes': ['gmail.send', 'gmail.readonly']
        },
        {
            'name': 'Google Docs',
            'file': 'docs_token.pickle',
            'module': 'google_docs_tool',
            'function': 'authenticate_docs',
            'scopes': ['documents', 'drive.file', 'drive']
        },
        {
            'name': 'Google Calendar',
            'file': 'calendar_token.pickle',
            'module': 'google_calendar_tool',
            'function': 'authenticate_calendar',
            'scopes': ['calendar', 'calendar.events']
        },
        {
            'name': 'Google Sheets',
            'file': 'sheets_token.pickle',
            'module': 'google_sheets_tool',
            'function': 'authenticate_sheets',
            'scopes': ['spreadsheets', 'drive.file']
        },
        {
            'name': 'Google Drive',
            'file': 'drive_token.pickle',
            'module': 'google_drive_tool',
            'function': 'authenticate_drive',
            'scopes': ['drive', 'drive.file']
        }
    ]
    
    print("\n📋 This script will regenerate the following tokens:")
    for token in tokens:
        print(f"   • {token['name']}: {token['file']}")
    
    print("\n⚠️  You will need to authenticate each service in your browser")
    print("   Please login with the same Google account for all services")
    print()
    
    input("Press Enter to continue...")
    
    results = []
    
    for i, token_info in enumerate(tokens, 1):
        print("\n" + "=" * 60)
        print(f"[{i}/{len(tokens)}] Regenerating {token_info['name']} Token")
        print("=" * 60)
        
        # Delete old token if exists
        token_file = token_info['file']
        if os.path.exists(token_file):
            try:
                os.remove(token_file)
                print(f"🗑️  Removed old token: {token_file}")
            except Exception as e:
                print(f"⚠️  Could not remove old token: {e}")
        
        try:
            # Import the authentication function
            module = __import__(f"tools.{token_info['module']}", fromlist=[token_info['function']])
            auth_function = getattr(module, token_info['function'])
            
            print(f"\n📋 Required scopes:")
            for scope in token_info['scopes']:
                print(f"   • https://www.googleapis.com/auth/{scope}")
            
            print(f"\n🔓 Starting OAuth flow for {token_info['name']}...")
            print("   A browser window will open for authentication")
            
            # Authenticate
            if token_info['name'] == 'Gmail':
                creds = auth_function(
                    credentials_file="credentials/client_secret.json",
                    token_file=token_file
                )
            else:
                creds = auth_function(
                    credentials_file="credentials/client_secret.json",
                    token_file=token_file
                )
            
            if creds and creds.valid:
                print(f"✅ {token_info['name']} token generated successfully!")
                print(f"📁 Token saved as: {token_file}")
                results.append({'name': token_info['name'], 'status': 'SUCCESS'})
            else:
                print(f"❌ Failed to generate valid credentials for {token_info['name']}")
                results.append({'name': token_info['name'], 'status': 'FAILED'})
                
        except Exception as e:
            print(f"❌ Error generating {token_info['name']} token: {e}")
            results.append({'name': token_info['name'], 'status': 'ERROR', 'error': str(e)})
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 REGENERATION SUMMARY")
    print("=" * 60)
    
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    
    for result in results:
        status_emoji = "✅" if result['status'] == 'SUCCESS' else "❌"
        print(f"{status_emoji} {result['name']}: {result['status']}")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    
    print(f"\n📈 Success Rate: {success_count}/{len(tokens)}")
    
    if success_count == len(tokens):
        print("\n🎉 All tokens regenerated successfully!")
        print("✅ You can now run: python main.py")
    else:
        print("\n⚠️  Some tokens failed to regenerate")
        print("   Please check the errors above and try again")

if __name__ == "__main__":
    try:
        regenerate_all_tokens()
    except KeyboardInterrupt:
        print("\n\n⚠️  Token regeneration cancelled by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
