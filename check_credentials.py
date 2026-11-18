"""
🔍 CREDENTIALS CHECKER
Verifies all required credentials and tokens are in place
"""

import os
from pathlib import Path

def check_file(path, description):
    """Check if a file exists"""
    if os.path.exists(path):
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ MISSING {description}: {path}")
        return False

def main():
    print("\n" + "="*80)
    print("🔍 CREDENTIALS CHECKER")
    print("="*80 + "\n")
    
    base_dir = os.path.dirname(__file__)
    all_ok = True
    
    print("📁 CHECKING CREDENTIALS FOLDER:")
    print("-"*80)
    
    # Check credentials folder
    cred_files = [
        ('credentials/client_secret.json', 'OAuth2 Client Secret'),
        ('credentials/token.pickle', 'General Token (optional)'),
        ('credentials/docs_token.pickle', 'Google Docs Token'),
    ]
    
    for file_path, desc in cred_files:
        full_path = os.path.join(base_dir, file_path)
        if not check_file(full_path, desc):
            if 'optional' not in desc:
                all_ok = False
    
    print("\n📁 CHECKING ROOT FOLDER TOKENS:")
    print("-"*80)
    
    # Check root tokens
    root_tokens = [
        ('calendar_token.pickle', 'Calendar API Token'),
        ('sheets_token.pickle', 'Sheets API Token (optional)'),
        ('drive_token.pickle', 'Drive API Token (optional)'),
        ('docs_token.pickle', 'Docs API Token (alternative location)'),
    ]
    
    for file_path, desc in root_tokens:
        full_path = os.path.join(base_dir, file_path)
        if not check_file(full_path, desc):
            if 'optional' not in desc:
                all_ok = False
    
    print("\n" + "="*80)
    if all_ok:
        print("✅ ALL REQUIRED CREDENTIALS FOUND!")
        print("🚀 Ready to run workflow test!")
    else:
        print("⚠️ SOME CREDENTIALS MISSING!")
        print("\n💡 SOLUTIONS:")
        print("   1. If token.pickle files are missing, they will be generated")
        print("      on first use (requires browser authentication)")
        print("   2. Make sure client_secret.json exists in credentials/")
        print("   3. Run the test - it will prompt for authentication if needed")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
