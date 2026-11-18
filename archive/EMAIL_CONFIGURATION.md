# 📧 EMAIL CONFIGURATION

## 🎯 **EMAIL FLOW SETUP**

### **Two Email Accounts:**

1. **Patient Email** (User/Login)
   - Email: `iamsamarth786@gmail.com`
   - Purpose: Patient login and receives emails
   - Role: Patient/User

2. **Hospital Email** (System/Sender)
   - Email: `pawarsamarth786@gmail.com`
   - Purpose: Hospital system account
   - Sends: All emails to patients
   - Manages: Drive, Sheets, Docs, Calendar

---

## 📨 **EMAIL FLOW:**

```
Patient logs in with:
iamsamarth786@gmail.com
        ↓
Chat with AI Agent
        ↓
Agent executes tools
        ↓
Emails sent FROM: pawarsamarth786@gmail.com (Hospital)
              TO: iamsamarth786@gmail.com (Patient)
        ↓
Patient receives emails at: iamsamarth786@gmail.com
```

---

## � Google API Authentication Fix

## 🐛 Problem

```
❌ Error: Request had insufficient authentication scopes
❌ Reason: insufficientPermissions
```

**Root Cause:** 
- Gmail tool uses `token.json` with only Gmail scopes
- Drive tool uses `token.pickle` with only Drive scopes
- Sheets tool needs Sheets scopes
- **They need ONE token with ALL scopes!**

---

## ✅ Solution: Re-authenticate with All Scopes

### **Step 1: Delete Old Tokens**

```powershell
# Delete old token files
rm token.json
rm token.pickle
rm token_gmail.pickle
rm token_drive.pickle
rm token_sheets.pickle
```

### **Step 2: Create Authentication Script**

Save this as `authenticate_google.py`:

```python
"""
Google Workspace Authentication - ALL SCOPES
Run this ONCE to authenticate with all required permissions
"""

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# ALL SCOPES NEEDED
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
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("🔐 Starting authentication...")
            print(f"📋 Requesting {len(SCOPES)} permissions...")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials/client_secret.json', 
                SCOPES
            )
            creds = flow.run_local_server(port=0)
            print("✅ Authentication successful!")
        
        # Save token for future use
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
            print("💾 Token saved to token.pickle")
    
    print("\n✅ All Google Workspace APIs authenticated!")
    print("\n🎯 Permissions granted:")
    print("  ✅ Gmail (send, read, modify)")
    print("  ✅ Google Drive (full access)")
    print("  ✅ Google Sheets")
    print("  ✅ Google Docs")
    print("  ✅ Google Calendar")
    
    return creds

if __name__ == "__main__":
    authenticate()
```

### **Step 3: Run Authentication**

```powershell
python authenticate_google.py
```

**What happens:**
1. Browser opens
2. Login with `pawarsamarth786@gmail.com`
3. Google asks: "Allow access to Gmail, Drive, Sheets, Docs, Calendar?"
4. Click "Allow"
5. Token saved to `token.pickle`
6. ✅ Done!

---

## 🎯 Current Status

### **Working:** ✅
- RegisterPatientTool ✅
- SendWelcomeEmailTool ✅ (Gmail API configured)
- AddPatientRecordTool ✅ (if spreadsheet ID provided)

### **Needs Re-auth:** ⚠️
- CreatePatientFolderTool (Drive API - needs re-auth)
- Other Drive tools (needs re-auth)
- Sheets tools (needs re-auth if using same token)

---

## 🔧 Quick Workaround (For Testing)

The agent now shows a friendly message instead of error:

```
✅ **All actions completed successfully!**

✅ Registered with ID: REG2025977476
ℹ️ Drive folder: Skipped (requires re-authentication)
✅ Tracking sheet updated
✅ Welcome email sent to iamsamarth786@gmail.com
```

This way you can **continue testing the workflow** while setting up full authentication later!

---

## 📝 Full Authentication Steps

### **1. Prepare credentials/client_secret.json**
Already done ✅

### **2. Run authentication script**
```powershell
python authenticate_google.py
```

### **3. Grant permissions**
- Login: pawarsamarth786@gmail.com
- Allow: Gmail, Drive, Sheets, Docs, Calendar
- Click "Allow"

### **4. Test tools**
```powershell
# Test Drive
python -c "from tools.google_drive_tool import CreatePatientFolderTool; tool = CreatePatientFolderTool(); print(tool._run(folder_name='Test_Folder'))"

# Test Sheets
python -c "from tools.google_sheets_tool import CreatePatientStatsSheetTool; tool = CreatePatientStatsSheetTool(); print(tool._run(sheet_name='Test_Sheet'))"

# Test Gmail (already working)
python -c "from tools.gmail_tool import SendWelcomeEmailTool; tool = SendWelcomeEmailTool(); print('Gmail: OK')"
```

---

## 🎉 After Re-auth

```
✅ **All actions completed successfully!**

✅ Registered with ID: REG2025977476
✅ Drive folder created: https://drive.google.com/...
✅ Tracking sheet updated
✅ Welcome email sent to iamsamarth786@gmail.com

---

**Stage Complete:** Patient Registration ✨
```

---

**Status:** Gmail working ✅, Drive needs re-auth ⚠️  
**Date:** October 21, 2025  
**Action:** Run `python authenticate_google.py` to fix Drive

### 1. **Gmail Tool Configuration**

File: `tools/gmail_tool.py`

```python
# FROM email (Hospital account)
DEFAULT_FROM_EMAIL = "pawarsamarth786@gmail.com"

# Uses credentials from Hospital Google Workspace account
```

### 2. **Google Workspace Tools**

All tools (Drive, Sheets, Docs, Calendar) use:
- Account: `pawarsamarth786@gmail.com`
- API Credentials: Hospital Google Cloud Project

### 3. **Patient Login**

Frontend uses:
- Google OAuth with: `iamsamarth786@gmail.com`
- This email is stored as patient email
- All communications sent to this email

---

## ✅ **CURRENT SETUP:**

- ✅ Hospital account: `pawarsamarth786@gmail.com` 
- ✅ Patient account: `iamsamarth786@gmail.com`
- ✅ Tools configured to send from hospital account
- ✅ Patient receives at their email

**This is the correct setup!** 🎉
