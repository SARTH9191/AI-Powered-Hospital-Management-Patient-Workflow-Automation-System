"""
Check Token Scopes
Verify that all token files have the correct scopes
"""

import os
import pickle

def check_token(token_file, expected_scopes):
    """Check if token has required scopes"""
    if not os.path.exists(token_file):
        print(f"❌ {token_file} - NOT FOUND")
        return False
    
    try:
        with open(token_file, 'rb') as f:
            creds = pickle.load(f)
        
        # Check if credentials are valid
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print(f"⚠️ {token_file} - EXPIRED (has refresh token)")
            else:
                print(f"❌ {token_file} - INVALID")
            return False
        
        # Check scopes
        actual_scopes = creds.scopes if hasattr(creds, 'scopes') else []
        print(f"\n✅ {token_file}")
        print(f"   Scopes: {actual_scopes}")
        
        # Check if all expected scopes are present
        missing_scopes = []
        for scope in expected_scopes:
            # Check if any actual scope contains the expected scope
            if not any(scope in actual for actual in actual_scopes):
                missing_scopes.append(scope)
        
        if missing_scopes:
            print(f"   ⚠️ Missing scopes: {missing_scopes}")
            return False
        else:
            print(f"   ✅ All required scopes present")
            return True
            
    except Exception as e:
        print(f"❌ {token_file} - ERROR: {e}")
        return False

print("=" * 70)
print("TOKEN SCOPE VERIFICATION")
print("=" * 70)

# Check each token file
tokens_ok = True

print("\n1. DOCS TOKEN (docs_token.pickle)")
docs_scopes = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive'
]
if not check_token('docs_token.pickle', docs_scopes):
    tokens_ok = False
    print("   💡 Regenerate: python generate_docs_token.py")

print("\n2. DRIVE TOKEN (drive_token.pickle)")
drive_scopes = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file'
]
if not check_token('drive_token.pickle', drive_scopes):
    tokens_ok = False
    print("   💡 Regenerate: python generate_drive_token.py")

print("\n3. SHEETS TOKEN (sheets_token.pickle)")
sheets_scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file'
]
if not check_token('sheets_token.pickle', sheets_scopes):
    tokens_ok = False
    print("   💡 Regenerate: python generate_sheets_token.py")

print("\n4. GENERAL TOKEN (token.pickle)")
general_scopes = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/gmail.send'
]
check_token('token.pickle', general_scopes)

print("\n" + "=" * 70)
if tokens_ok:
    print("✅ ALL TOKENS VALID - Ready to test tools")
else:
    print("⚠️ SOME TOKENS NEED REGENERATION")
    print("\nQuick fix:")
    print("1. Delete the invalid token file(s)")
    print("2. Run the tool again - it will prompt for re-authentication")
    print("3. Or run the generate_*_token.py script for that token")

print("=" * 70)
