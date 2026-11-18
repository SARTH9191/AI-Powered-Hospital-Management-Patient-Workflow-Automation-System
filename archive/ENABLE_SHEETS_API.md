# 🔴 URGENT: Enable Google Sheets API

## Issue
The Google Sheets API is not enabled in your Google Cloud project.

## Error Message
```
Google Sheets API has not been used in project 138139771025 before or it is disabled.
```

---

## ✅ Solution

### Step 1: Enable Sheets API

**Click this link:**
https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=138139771025

**Then:**
1. Click **"ENABLE"** button
2. Wait ~1 minute for activation

### Step 2: Re-authenticate

After enabling the API, re-run authentication:

```powershell
python authenticate_google.py
```

This will refresh your token with Sheets permissions.

### Step 3: Create Tracking Spreadsheet

```powershell
python setup_tracking_sheet.py
```

You should see:
```
✅ SUCCESS!
📊 SPREADSHEET ID: 1xBCnXGHt...
```

### Step 4: Set Environment Variable

Copy the spreadsheet ID and run:

```powershell
$env:PATIENT_TRACKING_SHEET_ID="YOUR_SPREADSHEET_ID_HERE"
```

---

## 📋 APIs Required for Full Functionality

| API | Status | Enable Link |
|-----|--------|-------------|
| Gmail API | ✅ Enabled | - |
| Drive API | ✅ Enabled | - |
| Sheets API | 🔴 **NEED TO ENABLE** | [Enable Now](https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=138139771025) |
| Calendar API | ⚠️ May need | [Enable](https://console.developers.google.com/apis/api/calendar-json.googleapis.com/overview?project=138139771025) |
| Docs API | ⚠️ May need | [Enable](https://console.developers.google.com/apis/api/docs.googleapis.com/overview?project=138139771025) |

---

## 🚀 Quick Setup Commands (After Enabling API)

```powershell
# 1. Re-authenticate
python authenticate_google.py

# 2. Create spreadsheet
python setup_tracking_sheet.py

# 3. Copy the spreadsheet ID and set it
$env:PATIENT_TRACKING_SHEET_ID="<PASTE_ID_HERE>"

# 4. Test workflow
# Open: http://localhost:3000/loginPage
# Login and start registration
```

---

## ✅ Verification

After setup, test registration:
1. Go to frontend chat
2. Type "restart"
3. Complete registration
4. Check:
   - ✅ Email received?
   - ✅ Drive folder created?
   - ✅ Spreadsheet updated?

Check spreadsheet:
- Login to Google Sheets with `pawarsamarth786@gmail.com`
- Open "City_Hospital_Patient_Tracking"
- Should see patient data in "Patient Records" tab

---

**Next:** After enabling Sheets API, run `python authenticate_google.py` again!
