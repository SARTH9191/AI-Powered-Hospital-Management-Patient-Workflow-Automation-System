# 🚀 QUICK COMMAND REFERENCE

## Enable APIs & Setup (One-time)

```powershell
# 1. Enable Sheets API
# Open: https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=138139771025
# Click: ENABLE

# 2. Re-authenticate
python authenticate_google.py

# 3. Create tracking spreadsheet
python setup_tracking_sheet.py

# 4. Set environment variable (replace with your ID)
$env:PATIENT_TRACKING_SHEET_ID="1xBCnXGHtYz9sZqL3vW8jR4kP2mN0oA5"
```

---

## Start Application

```powershell
# Terminal 1: Backend API
cd "d:\ai agent by myself\ai agent"
uvicorn main:app --reload

# Terminal 2: Frontend
cd "d:\ai agent by myself\ai agent\frontend"
npm run dev
```

---

## Test Workflow

**Open:** http://localhost:3000/loginPage

**Reset workflow:**
```
Type: "restart"
```

**Complete registration:**
```
1. Name: Samarth Pawar
2. Phone: +91-7447444532
3. DOB: 2006-08-07
4. Gender: Male
5. Address: Pune
6. Confirm: yes
```

**Check results:**
- ✅ Email: iamsamarth786@gmail.com
- ✅ Drive: pawarsamarth786@gmail.com
- ✅ Sheets: pawarsamarth786@gmail.com

---

## Verification Links

**Gmail (Patient):** https://mail.google.com/mail/u/0/#inbox
**Drive (Hospital):** https://drive.google.com/drive/my-drive
**Sheets (Hospital):** https://docs.google.com/spreadsheets/

---

## Chat Commands

| Command | Action |
|---------|--------|
| `restart` | Reset to Stage 1 |
| `reset` | Reset to Stage 1 |
| `start over` | Reset to Stage 1 |
| `done` | Mark current stage complete |
| `yes` | Confirm action |
| `no` | Cancel action |

---

## Troubleshooting

**Sheets API Error:**
```powershell
python authenticate_google.py
python setup_tracking_sheet.py
```

**Reset Not Working:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/ai-chat/reset" -Method POST
```

**Check Backend Logs:**
```powershell
# Look at terminal running uvicorn
# Check for error messages
```

---

## Files You May Need

| File | Purpose |
|------|---------|
| `token.pickle` | Google authentication |
| `credentials/client_secret.json` | OAuth credentials |
| `.env` | Environment variables |
| `data/workflow_states.json` | Workflow persistence |

---

**Need Help?** Check: `THREE_ISSUES_FIXED.md`
