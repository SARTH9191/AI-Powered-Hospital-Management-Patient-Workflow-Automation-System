# 🔐 Google OAuth Setup Guide - Fix "OAuth client was not found" Error

## ❌ **Problem:**
```
Access blocked: Authorization Error
Error 401: invalid_client
The OAuth client was not found.
```

This error occurs because the Google OAuth credentials are not configured in your `.env` file.

---

## ✅ **Solution: Configure Google OAuth 2.0**

Follow these steps to set up Google OAuth for your application:

---

## 📋 **Step 1: Create Google Cloud Project**

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/

2. **Create New Project (or use existing):**
   - Click "Select a project" at the top
   - Click "New Project"
   - Name: `Hospital AI Agent` (or any name)
   - Click "Create"

3. **Select Your Project:**
   - Make sure your new project is selected in the top dropdown

---

## 🔧 **Step 2: Enable Google+ API (Required for OAuth)**

1. **Go to API Library:**
   - In left menu: APIs & Services → Library
   - Or visit: https://console.cloud.google.com/apis/library

2. **Search and Enable:**
   - Search for "Google+ API"
   - Click on it
   - Click "ENABLE"

3. **Also Enable (Optional but recommended):**
   - Google Drive API (already enabled if using Drive)
   - Google Calendar API (for appointments)
   - Google Docs API (for documents)
   - Google Sheets API (for tracking)

---

## 🎫 **Step 3: Create OAuth 2.0 Credentials**

1. **Go to Credentials Page:**
   - Left menu: APIs & Services → Credentials
   - Or visit: https://console.cloud.google.com/apis/credentials

2. **Configure OAuth Consent Screen** (REQUIRED FIRST TIME):
   
   a. Click "Configure Consent Screen"
   
   b. Choose **"External"** (allows any Google account)
      - Click "Create"
   
   c. **Fill in App Information:**
      ```
      App name: Hospital AI Agent
      User support email: pawarsamarth786@gmail.com
      Developer contact: pawarsamarth786@gmail.com
      ```
   
   d. **Scopes** (Click "Add or Remove Scopes"):
      - Select these scopes:
        ✅ .../auth/userinfo.email
        ✅ .../auth/userinfo.profile
        ✅ openid
      - Click "Update"
   
   e. **Test Users** (Important for development):
      - Click "Add Users"
      - Add your email: `sampawar76@gmail.com`
      - Add any other test emails you'll use
      - Click "Save and Continue"
   
   f. Click "Save and Continue" through remaining pages
   
   g. Click "Back to Dashboard"

3. **Create OAuth Client ID:**
   
   a. Click "Create Credentials" → "OAuth client ID"
   
   b. Choose **"Web application"**
   
   c. **Configure Application:**
      ```
      Name: Hospital AI Agent Web Client
      
      Authorized JavaScript origins:
      - http://localhost:3000
      - http://localhost:8000
      
      Authorized redirect URIs:
      - http://localhost:8000/auth/callback
      - http://localhost:3000/auth/success
      ```
   
   d. Click "Create"

4. **Save Your Credentials:**
   - A popup will show your credentials:
     - **Client ID**: Something like `123456789-abcdef.apps.googleusercontent.com`
     - **Client Secret**: Something like `GOCSPX-abcdef123456`
   - **IMPORTANT**: Copy these immediately!
   - Download the JSON file as backup (optional)

---

## 📝 **Step 4: Add Credentials to .env File**

1. **Open your `.env` file:**
   ```
   d:\ai agent by myself\ai agent\.env
   ```

2. **Add these lines** (after line 50, before Database Configuration):

```env
# 🔐 Google OAuth 2.0 Configuration (for user login)
GOOGLE_CLIENT_ID=YOUR_CLIENT_ID_HERE.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
```

3. **Replace with your actual values:**
   ```env
   # Example (use YOUR values from Google Cloud Console):
   GOOGLE_CLIENT_ID=123456789-abc123xyz.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=GOCSPX-your_secret_here_abc123
   GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
   ```

4. **Save the file**

---

## 🚀 **Step 5: Restart Your Backend**

1. **Stop the running backend** (Ctrl+C in terminal)

2. **Restart it:**
   ```powershell
   cd "d:\ai agent by myself\ai agent"
   .\.venv\Scripts\python.exe main.py
   ```

3. **The backend will now load the OAuth credentials**

---

## 🔍 **Step 6: Test the Login**

1. **Start Frontend** (if not running):
   ```powershell
   cd frontend
   npm run dev
   ```

2. **Open Browser:**
   - Go to: http://localhost:3000

3. **Click "Sign in with Google"**

4. **You should see:**
   - Google OAuth consent screen
   - "Hospital AI Agent wants to access your Google Account"
   - Your test email (sampawar76@gmail.com) should work
   - Click "Continue" or "Allow"

5. **Success!**
   - You'll be redirected back to the app
   - Logged in with your Google account

---

## ⚠️ **Common Issues & Solutions**

### **Issue 1: "Access blocked: This app's request is invalid"**
**Solution:**
- Make sure "Authorized redirect URIs" includes:
  - `http://localhost:8000/auth/callback`
- No trailing slashes!
- Use exact URL including protocol (http://)

### **Issue 2: "OAuth client was not found"**
**Solution:**
- Double-check CLIENT_ID and CLIENT_SECRET in `.env`
- Make sure there are no extra spaces
- Restart backend after changing `.env`

### **Issue 3: "Access blocked: Authorization Error - This app hasn't been verified"**
**Solution:**
- Go to OAuth consent screen → Publishing status
- It will say "Testing" - this is fine for development
- Add your email to "Test users" list
- Only test users can sign in during development

### **Issue 4: "redirect_uri_mismatch"**
**Solution:**
- The redirect URI in your code must EXACTLY match the one in Google Console
- Check `GOOGLE_REDIRECT_URI` in `.env`
- Check "Authorized redirect URIs" in Google Console
- They must be identical (including http:// and no trailing /)

---

## 🔒 **Security Notes**

### **For Development:**
- ✅ Use `http://localhost` (fine for testing)
- ✅ App status: "Testing" (only test users can access)
- ✅ Keep credentials in `.env` (gitignored)

### **For Production:**
- ⚠️ Change to `https://yourdomain.com`
- ⚠️ Update redirect URIs to production URLs
- ⚠️ Submit app for verification (if needed)
- ⚠️ Use environment variables (never commit credentials)

---

## 📋 **Quick Checklist**

Before testing, verify:

- [ ] Google Cloud project created
- [ ] OAuth consent screen configured
- [ ] OAuth Client ID created
- [ ] CLIENT_ID added to `.env`
- [ ] CLIENT_SECRET added to `.env`
- [ ] REDIRECT_URI added to `.env` (http://localhost:8000/auth/callback)
- [ ] Authorized redirect URIs configured in Google Console
- [ ] Test user email added (sampawar76@gmail.com)
- [ ] Backend restarted
- [ ] `.env` file saved

---

## 🎯 **Final .env Configuration**

Your `.env` should have these lines (with your actual values):

```env
# 🔐 Google OAuth 2.0 Configuration (for user login)
GOOGLE_CLIENT_ID=123456789-abc123xyz.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback

# 🔒 Google Cloud Service Account (JSON file path) - Already exists
GOOGLE_SERVICE_ACCOUNT_FILE=credentials/google-service-account.json
```

**Note:** You have TWO different Google auth methods:
1. **Service Account** (for Drive, Sheets, Docs APIs) - ✅ Already working
2. **OAuth 2.0** (for user login) - ❌ This is what you need to set up

---

## 🆘 **Still Having Issues?**

1. **Check Backend Logs:**
   ```
   Look for errors when starting: python main.py
   ```

2. **Verify Environment Variables Loaded:**
   - Backend should print OAuth config on startup
   - Check for "GOOGLE_CLIENT_ID" in logs

3. **Test OAuth Flow:**
   - Visit: http://localhost:8000/auth/login
   - Should redirect to Google
   - If shows error, check redirect URI mismatch

4. **Clear Browser Cache:**
   - Sometimes old OAuth attempts are cached
   - Try incognito/private window

---

## 📞 **Need Help?**

If you're still stuck:

1. **Share the exact error message** from Google
2. **Check Google Console** → APIs & Services → Credentials
3. **Verify OAuth consent screen** is configured
4. **Confirm test user** is added
5. **Double-check redirect URIs** match exactly

---

## ✅ **Success Indicators**

You'll know it's working when:

1. ✅ Backend starts without OAuth errors
2. ✅ Clicking "Sign in with Google" redirects to Google
3. ✅ Google shows "Hospital AI Agent wants to access..."
4. ✅ After clicking "Allow", you're redirected back
5. ✅ You're logged into the app
6. ✅ Can start the workflow

---

*Remember: OAuth setup is one-time only! Once configured, all users can sign in with any Google account (if published) or test users (if in testing mode).*

**Good luck! 🚀**
