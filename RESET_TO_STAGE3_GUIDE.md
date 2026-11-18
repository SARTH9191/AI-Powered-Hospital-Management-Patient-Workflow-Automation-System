# 🔄 HOW TO RESET TO STAGE 3 & TEST

## ✅ Important URLs ARE Preserved!

The filter now **KEEPS** patient-facing URLs:
- ✅ Drive folder links (for document upload)
- ✅ Calendar appointment links
- ✅ Prescription download links
- ✅ Test result links

**Filters OUT**:
- ❌ Backend Google Docs/Sheets URLs
- ❌ Technical IDs and internal links
- ❌ Doctor collaboration tool URLs

---

## 🔧 RESET TO STAGE 3: Step-by-Step

### **Step 1: Run Reset Script**

```powershell
python reset_to_stage3.py
```

**You'll be asked**: "Proceed with reset? (yes/no)"
- Type: `yes`
- Press Enter

**What it does**:
1. Finds patient PAT20251113001842 (iamsamarth786@gmail.com)
2. Updates PostgreSQL to Stage 3
3. Clears all Redis cache for that patient
4. Shows confirmation with patient details

---

### **Step 2: Clear Frontend localStorage**

**In the browser (where frontend is running):**

1. Press `F12` to open Developer Tools
2. Click the **Console** tab
3. Type this command:
   ```javascript
   localStorage.clear()
   ```
4. Press **Enter**
5. **Refresh the page** (F5 or Ctrl+R)

**Why?**: Frontend stores session ID in localStorage. Clearing it forces a fresh login and session.

---

### **Step 3: Login Again**

1. Go to frontend: http://localhost:3000 (or your frontend URL)
2. Click "Login" or "Sign In"
3. Enter email: `iamsamarth786@gmail.com`
4. Complete login process

**Expected Result**: You should now see **"Stage 3/12: Medical History Collection"**

---

### **Step 4: Test Stage 3**

In the chat, type:

```
I have diabetes and high blood pressure. Currently taking metformin. 
I'm having severe stomach pain and vomiting for 2 days.
```

**What to verify**:
- ✅ AI asks follow-up questions about symptoms
- ✅ Clean completion message (no technical details)
- ✅ Document created with YOUR NAME (not "Unknown Patient")
- ✅ No datetime errors in backend logs
- ✅ Only patient-relevant info shown

---

## 📋 Expected Stage 3 Completion Message

```
✅ All actions completed successfully!

✅ Information recorded successfully

---

Stage Complete: Medical History Collection ✨

Next Stage: Lab Test Approval & Scheduling

Ready to continue? (yes/no)
```

**What you WON'T see** (filtered out):
- ❌ Document URLs
- ❌ "Shared with pawarsamarth786@gmail.com"
- ❌ "Section 3"
- ❌ Google Sheets/Docs mentions
- ❌ "Workflow document created"

---

## 🔍 Verify in Backend Logs

Look for these in terminal:

```
✅ Found existing patient by email: PAT20251113001842
✅ Restored session from PostgreSQL: PAT20251113001842 at Stage 3
📋 Creating document for patient: Samarth Pawar
✅ Created workflow document: [DOC_ID]
```

---

## ⚠️ Troubleshooting

### **Problem**: "Still showing Stage 2 or Stage 7"
**Solution**: 
1. Make sure you cleared localStorage
2. Logout completely
3. Close all browser tabs
4. Re-run reset script
5. Login again

### **Problem**: "Document still says Unknown Patient"
**Solution**: Database may not have full_name. The script should have fixed this, but if not:
```python
python fix_patient_name.py  # (script to be created if needed)
```

### **Problem**: "Backend not starting"
**Solution**:
```powershell
taskkill /F /IM python.exe
& "D:/ai agent by myself/ai agent/.venv/Scripts/Activate.ps1"
python main.py
```

---

## ✅ Ready to Test!

Once you complete the reset:
1. Run: `python reset_to_stage3.py`
2. Clear browser localStorage
3. Login with iamsamarth786@gmail.com
4. Test Stage 3 with medical history input
5. Verify clean patient messages
6. Check document has correct name

**Let me know what you see!** 🚀
