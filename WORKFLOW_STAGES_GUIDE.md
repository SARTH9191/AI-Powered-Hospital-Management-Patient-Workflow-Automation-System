# 🏥 Hospital AI Agent - Workflow Stages Guide

## Simple Overview: What Each Stage Does

---

## 📝 **Stage 1: Patient Registration**

**What it does:**
- Collects your basic information (name, email, phone, age, address)
- Creates your patient ID
- **Automatically creates 5 organized folders in Google Drive** for your documents
- Creates your workflow tracking document in Google Docs
- Creates your lab monitoring dashboard in Google Sheets

**What you get:**
- ✅ Patient ID assigned
- 📂 5 Drive folders: Medical History, Essential Documents, Lab Reports, Prescriptions, Consultation Notes
- 📄 Personal Google Doc for tracking your care journey
- 📊 Personal Google Sheet for lab results

**Calendar Event:** ❌ None

---

## 📄 **Stage 2: Document Upload**

**What it does:**
- Shows you the link to upload essential documents (Aadhaar, PAN, Insurance, etc.)
- **Verifies you uploaded ID proof** before letting you continue
- Guides you to the correct Drive folder

**What you need:**
- ⚠️ **MANDATORY**: At least one ID proof document (Aadhaar/PAN/Driver's License)
- Optional: Insurance, medical cards, other documents

**What you get:**
- ✅ Documents safely stored in your Google Drive
- ✅ ID verification complete

**Calendar Event:** ❌ None

---

## 🩺 **Stage 3: Medical History**

**What it does:**
- Asks about your current symptoms and health concerns
- Collects your medical history (past illnesses, surgeries, allergies, medications)
- **Optional**: Upload previous medical records to Medical History folder
- AI analyzes your symptoms and recommends which lab tests you might need
- Creates a Doctor Review Sheet in Google Sheets

**What you provide:**
- Current symptoms and health concerns
- Past medical history
- Allergies and current medications

**What you get:**
- ✅ AI analysis of your symptoms
- ✅ Recommended lab tests
- 📋 Doctor Review Sheet created (for doctor to approve tests)

**Calendar Event:** ❌ None

---

## 🔬 **Stage 4: Test Determination** 

**What it does:**
- Doctor reviews your medical history and AI recommendations
- Doctor updates the Review Sheet with approved/modified tests
- AI waits for doctor's decision
- You can type "check" to see if doctor has reviewed

**What happens:**
- Doctor logs in separately and reviews your case
- Doctor approves, modifies, or adds lab tests
- System detects doctor's update automatically

**What you get:**
- ✅ Final list of lab tests approved by doctor
- 📋 Personalized test plan

**Calendar Event:** ❌ None

---

## 📅 **Stage 5: Lab Appointment Scheduling**

**What it does:**
- Schedules your lab test appointment
- Shows you available dates and times
- **Creates Google Calendar event** for your appointment
- Shows you the link to Lab Reports folder (where results will be uploaded)
- Sends confirmation email

**What you provide:**
- Preferred date and time for lab tests

**What you get:**
- ✅ Lab appointment confirmed
- 📅 **Calendar event created** (with lab location, time, contact info)
- 📧 Confirmation email sent
- 🔗 Lab Reports folder link shared

**Calendar Event:** ✅ **YES** - Lab appointment

---

## 🧪 **Stage 6: Lab Results Analysis & Doctor Meeting Scheduling**

**What it does:**
- **Real-time monitoring** of your lab results in Google Sheets
- AI automatically detects when lab uploads your results
- AI analyzes results and flags any abnormal values
- Reads doctor's notes if available
- **Schedules meeting with doctor** to discuss your results
- **Creates Google Calendar event** for doctor consultation
- Sends results email to you

**What happens:**
- Lab technicians upload results to your Google Sheet
- AI detects and analyzes results automatically
- System asks you to confirm doctor meeting
- Meeting scheduled once you say "yes"

**What you get:**
- ✅ Lab results with AI analysis
- ⚠️ Flagged abnormal values (if any)
- 👨‍⚕️ Doctor's assessment (if available)
- 📅 **Calendar event for doctor meeting created**
- 📧 Results email sent

**Calendar Event:** ✅ **YES** - Doctor consultation meeting

---

## 👨‍⚕️ **Stage 7: Doctor Consultation**

**What it does:**
- Doctor reviews your lab results
- Doctor updates the workflow document (Section 3) with decision:
  - **Option A**: Admission needed for procedure/surgery
  - **Option B**: Prescription + follow-up (no admission)
- You wait and can type "check" to see if doctor has decided

**What happens:**
- Doctor meets with you (in-person or via the scheduled meeting)
- Doctor updates decision in your Google Doc
- AI detects doctor's decision automatically

**What you get:**
- ✅ Doctor's diagnosis
- ✅ Treatment decision (admission vs outpatient)

**Calendar Event:** ❌ None (but you attend the meeting scheduled in Stage 6)

---

## 🏥 **Stage 8: Admission Planning** (If admission needed)

**What it does:**
- Plans your hospital admission if doctor decided you need it
- Collects admission preferences (date, room type, insurance)
- Coordinates with hospital admission department
- Updates your workflow document with admission details

**What you provide:**
- Preferred admission date
- Room preferences (general/semi-private/private)
- Insurance information

**What you get:**
- ✅ Admission planned and coordinated
- 📋 Admission details documented

**Calendar Event:** ❌ None

**Note:** Skipped if doctor chose Option B (no admission)

---

## 🔍 **Stage 9: Pre-Operative Assessment** (If surgery needed)

**What it does:**
- Conducts pre-surgery health assessment
- Reviews fitness for anesthesia and procedure
- Documents pre-op instructions
- Coordinates with surgical team

**What you provide:**
- Pre-op health information
- Consent for procedure

**What you get:**
- ✅ Pre-op clearance
- 📋 Surgery preparation instructions

**Calendar Event:** ❌ None

**Note:** Skipped if no surgery needed

---

## 🗓️ **Stage 10: Procedure Scheduling** (If surgery needed)

**What it does:**
- Schedules your surgery/procedure date and time
- Assigns surgical team
- Books operation theater
- Provides pre-surgery instructions

**What you provide:**
- Preferred surgery date (subject to availability)

**What you get:**
- ✅ Surgery scheduled
- 📅 Surgery date and time confirmed
- 👥 Surgical team assigned
- 📋 Pre-surgery instructions

**Calendar Event:** ❌ None (though could be added in future)

**Note:** Skipped if no surgery needed

---

## 💊 **Stage 11: Post-Treatment Care**

**What it does:**
- Doctor writes prescription in your Google Doc (Section 7)
- **AI automatically reads prescription and generates beautiful PDF**
- **PDF auto-uploaded to your Prescriptions folder** in Drive
- Schedules follow-up appointment
- **Creates Google Calendar event** for follow-up
- Sends prescription link to you

**What doctor provides:**
- Prescription details in Google Doc

**What you get:**
- ✅ **Professional prescription PDF** (auto-generated)
- 📂 PDF saved in Drive Prescriptions folder
- 🔗 Downloadable prescription link
- 📅 **Calendar event for follow-up appointment**
- 📧 Prescription email

**Calendar Event:** ✅ **YES** - Follow-up appointment

---

## 🏠 **Stage 12: Discharge & Summary**

**What it does:**
- Prepares comprehensive discharge summary document
- Documents entire treatment journey
- Provides home care instructions
- Shares final documents with you
- Marks workflow as complete

**What you get:**
- ✅ **Discharge Summary PDF** (professional document)
- ✅ Complete treatment record
- ✅ Home care instructions
- ✅ All documents in your Google Drive
- ✅ Workflow completed

**Calendar Event:** ❌ None

---

## 📊 **Quick Reference Table**

| Stage | Name | What Happens | Calendar Event | Documents Created |
|-------|------|--------------|----------------|-------------------|
| **1** | Registration | Basic info + folders created | ❌ | Drive folders, Doc, Sheet |
| **2** | Document Upload | Upload ID proof (mandatory) | ❌ | - |
| **3** | Medical History | Symptoms + AI analysis | ❌ | Doctor Review Sheet |
| **4** | Test Determination | Doctor approves tests | ❌ | - |
| **5** | Lab Appointment | Schedule lab tests | ✅ Lab | - |
| **6** | Results Analysis | Get results + schedule doctor meeting | ✅ Doctor Meeting | - |
| **7** | Doctor Consultation | Doctor decides treatment path | ❌ | Treatment decision |
| **8** | Admission Planning | Plan hospital admission (if needed) | ❌ | Admission details |
| **9** | Pre-Op Assessment | Pre-surgery checkup (if needed) | ❌ | Pre-op clearance |
| **10** | Procedure Scheduling | Schedule surgery (if needed) | ❌ | Surgery schedule |
| **11** | Post-Treatment | **Auto-generate prescription PDF** + follow-up | ✅ Follow-up | **Prescription PDF** |
| **12** | Discharge | Final summary + complete | ❌ | Discharge Summary |

---

## 🎯 **Key Features Summary**

### 📅 **3 Calendar Events Created:**
1. **Stage 5**: Lab test appointment
2. **Stage 6**: Doctor meeting (to discuss lab results)
3. **Stage 11**: Follow-up appointment

### 📂 **5 Drive Folders Created:**
1. **1_Medical_History** - Previous medical records
2. **2_Essential_Documents** - ID proofs, insurance (mandatory)
3. **3_Lab_Reports** - Lab test results
4. **4_Prescriptions** - Auto-generated prescription PDFs
5. **5_Consultation_Notes** - Doctor notes and consultations

### 📄 **Documents Auto-Created:**
- Google Doc: Workflow tracking (Stages 1-12)
- Google Sheet: Lab results monitoring + Doctor Review
- Prescription PDF: Auto-generated from doctor's notes
- Discharge Summary: Final treatment record

### 🔐 **Login System:**
- ✅ Any user can login with **any Google account**
- ✅ Google OAuth 2.0 authentication
- ✅ Secure session management
- ✅ State persistence per user

### 💾 **State Persistence:**
- ✅ Logout and resume anytime
- ✅ All data saved (Redis + PostgreSQL)
- ✅ Resume from exact stage where you left

---

## 🚀 **Workflow Paths**

### **Path A: Admission + Surgery**
```
Stages: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12
        Register → Upload → History → Tests → Lab → Results → Doctor → Admit → Pre-Op → Surgery → Treatment → Discharge
```

### **Path B: Outpatient (No Admission)**
```
Stages: 1 → 2 → 3 → 4 → 5 → 6 → 7 → [Skip 8,9,10] → 11 → 12
        Register → Upload → History → Tests → Lab → Results → Doctor → Treatment → Discharge
```

---

## ✨ **Special AI Features**

1. **🤖 Smart Symptom Analysis** (Stage 3)
   - AI analyzes your symptoms
   - Recommends appropriate lab tests
   - Creates personalized test plan

2. **🔄 Real-Time Lab Monitoring** (Stage 6)
   - AI watches Google Sheets for results
   - Automatically detects when results uploaded
   - Flags abnormal values instantly

3. **📄 Auto-Prescription PDF** (Stage 11)
   - AI reads doctor's prescription from Google Doc
   - Generates professional PDF automatically
   - Uploads to Drive and shares link

4. **💬 Natural Conversation** (All Stages)
   - Chat naturally with AI agent
   - AI guides you through each step
   - Ask questions anytime

---

## 🎉 **Summary**

**12 Stages** from registration to discharge  
**3 Calendar Events** for appointments  
**5 Drive Folders** for organized documents  
**100% State Persistence** - resume anytime  
**Any Google Account** can login and start  

**Your complete healthcare journey, managed by AI! 🏥**

---

*Hospital Management System • AI-Powered Patient Care*
