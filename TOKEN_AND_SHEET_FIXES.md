# Token and Sheet Configuration Fixes

## Issues Found in test_individual_tools.py

### Issue 1: ❌ Google Docs Token Scope Error
```
HttpError 403: Request had insufficient authentication scopes
ACCESS_TOKEN_SCOPE_INSUFFICIENT
```

**Root Cause:** 
- `docs_monitoring_tools.py` was using `token.pickle` (general token)
- Should use `docs_token.pickle` (has proper Docs API scopes)

**Fix Applied:**
Changed `_initialize_docs_service()` and `_initialize_drive_service()` to use dedicated tokens:
- `docs_token.pickle` for Google Docs API
- `drive_token.pickle` for Google Drive API

### Issue 2: ❌ Google Sheets Range Error
```
HttpError 400: Unable to parse range: Test Results!A:H
```

**Root Cause:**
- Sheet doesn't have a tab named "Test Results"
- Code was hardcoded to use "Test Results!A:H"

**Fix Applied:**
Made `AddLabResultTool._run()` dynamic:
- Fetches sheet metadata to get available tabs
- Searches for tabs with "lab", "test", or "result" in name
- Falls back to first sheet if no match found
- Uses correct sheet name dynamically

## Files Modified

### 1. `tools/docs_monitoring_tools.py`

**Changed:**
```python
# BEFORE
token_path = os.path.join(os.path.dirname(__file__), '..', 'token.pickle')

# AFTER - Docs Service
token_path = os.path.join(os.path.dirname(__file__), '..', 'docs_token.pickle')

# AFTER - Drive Service  
token_path = os.path.join(os.path.dirname(__file__), '..', 'drive_token.pickle')
```

### 2. `tools/google_sheets_tool.py`

**Changed:**
```python
# BEFORE - Hardcoded sheet name
range='Test Results!A:H'

# AFTER - Dynamic sheet detection
sheet_metadata = self.sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
sheets = sheet_metadata.get('sheets', [])
# Find sheet with "lab", "test", or "result" in name
range=f'{sheet_name}!A:H'
```

## Testing Tools Created

### 1. `check_token_scopes.py` - NEW
Verifies all token files have correct scopes:
```bash
python check_token_scopes.py
```

Checks:
- ✅ docs_token.pickle (Docs + Drive scopes)
- ✅ drive_token.pickle (Drive scopes)
- ✅ sheets_token.pickle (Sheets scopes)
- ✅ token.pickle (General scopes)

## How to Fix Token Issues

### Option 1: Let Tool Re-authenticate
```bash
# Delete the invalid token
rm docs_token.pickle

# Run tool - it will prompt for re-auth
python test_individual_tools.py
```

### Option 2: Use Existing generate_docs_token.py
```bash
python generate_docs_token.py
```

This should regenerate `docs_token.pickle` with correct scopes.

## Expected Test Results After Fixes

### Test 1: CreateMedicalDocumentTool
```
✅ Google Docs monitoring service initialized
✅ Google Drive monitoring service initialized
✅ Medical Document Created Successfully!
📄 Document ID: [real_document_id]
```

### Test 2: ShareMedicalDocumentTool
```
✅ Document Shared Successfully!
📧 Notification sent to [email]
```

### Test 3: SendNotificationTool
```
⚠️ Expected: Recipient not found (normal if patient doesn't exist in DB)
```

### Test 4: AddLabResultTool
```
🔧 DEBUG: Using sheet: [detected_sheet_name]
✅ Lab result added to row [row_number]
```

## Next Steps

1. **Check token scopes:**
   ```bash
   python check_token_scopes.py
   ```

2. **If tokens invalid, regenerate:**
   ```bash
   python generate_docs_token.py
   ```

3. **Run tests again:**
   ```bash
   python test_individual_tools.py
   ```

4. **Verify in Google:**
   - Check Google Drive for test document
   - Check Google Sheets for test lab result
   - Delete test data if needed

## Summary of Token Usage

| Tool | Token File | Required Scopes |
|------|-----------|-----------------|
| CreateMedicalDocumentTool | docs_token.pickle | documents, drive.file, drive |
| ShareMedicalDocumentTool | drive_token.pickle | drive, drive.file |
| AddLabResultTool | sheets_token.pickle | spreadsheets, drive.file |
| SendNotificationTool | (No token needed) | Uses email config |

## What's Fixed Now

✅ **docs_monitoring_tools.py** - Using correct token files
✅ **google_sheets_tool.py** - Dynamic sheet name detection
✅ **AddLabResultTool** - Finds correct sheet automatically
✅ **Token scope issues** - Each tool uses dedicated token

---

**Status:** Ready for testing
**Run:** `python check_token_scopes.py` then `python test_individual_tools.py`
