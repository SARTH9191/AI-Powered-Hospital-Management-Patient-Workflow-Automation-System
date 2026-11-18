# Stage 7→11→12 Complete Workflow Test Guide

## ✅ ALL FIXES COMPLETED

### What Was Fixed:
1. ✅ **Section 6 Template** - Clear doctor fields with checkbox format
2. ✅ **Section 7 Template** - Numbered prescription list + follow-up instructions
3. ✅ **Prescription PDF Generation** - Automatic PDF creation and Drive upload
4. ✅ **Date Parsing** - Fixed "in 10 days" → correct 2025 date
5. ✅ **Medication Display** - Clean numbered list format
6. ✅ **Stage 12 Completion** - Workflow loop ready (visit_complete=True, next_stage=2)
7. ✅ **Document Formatting** - Professional, doctor-friendly templates

---

## 🧪 Complete Test Flow

### Prerequisites:
- Backend running: `python main.py`
- Frontend running: `cd frontend && npm start`
- Patient at Stage 7 with lab results complete

---

### Test Steps:

#### **STEP 1: Doctor Updates Section 6 (Google Docs)**
Open patient's workflow document and fill:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👨‍⚕️ SECTION 6: POST-LAB DOCTOR CONSULTATION (Stage 7)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👨‍⚕️ DIAGNOSIS:
• Uncontrolled Type 2 Diabetes Mellitus
• Stage 2 Hypertension
• Dyslipidemia (High cholesterol)

✅ DECISION:
☑ NO ADMISSION - Outpatient treatment (→ proceeds to Stage 11: Follow-up)
□ HOSPITAL ADMISSION REQUIRED (→ proceeds to Stage 8: Admission Planning)

📋 Treatment Plan:
• Increase Metformin to 1000mg twice daily
• Start Amlodipine 5mg once daily for blood pressure
• Start Atorvastatin 20mg once daily for cholesterol
• Lifestyle modifications: Low-salt, low-sugar diet
• Regular exercise: 30 minutes daily walking
• Weight management counseling
```

**Expected Result:** Section 6 updated with diagnosis and NO ADMISSION decision

---

#### **STEP 2: Patient Types "check"**
In browser chat, type:
```
check
```

**Expected Output:**
```
✅ DOCTOR CONSULTATION COMPLETE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👨‍⚕️ DIAGNOSIS: 
• Uncontrolled Type 2 Diabetes Mellitus
• Stage 2 Hypertension
• Dyslipidemia (High cholesterol)

✅ DECISION: OUTPATIENT TREATMENT

📋 Treatment Plan:
• Increase Metformin to 1000mg twice daily
• Start Amlodipine 5mg once daily for blood pressure
...

Type "continue" to proceed with prescription and follow-up planning...
```

**Validation:**
- ✅ Diagnosis parsed correctly
- ✅ NO ADMISSION detected
- ✅ Treatment plan displayed
- ✅ ChromaDB indexing (check console logs)

---

#### **STEP 3: Doctor Updates Section 7 (Google Docs)**
Fill prescription and follow-up:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💊 SECTION 7: PRESCRIPTION & FOLLOW-UP (Stage 11)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💊 YOUR PRESCRIPTION

Metformin 1000mg - Take twice daily with meals
Amlodipine 5mg - Take once daily in morning
Atorvastatin 20mg - Take once daily at bedtime

📅 FOLLOW-UP APPOINTMENT

• Recheck blood glucose and BP in 2 weeks
• Repeat full lab panel in 3 months
• Monitor BP at home daily
• Next consultation: 2 weeks
```

---

#### **STEP 4: Patient Types "continue"**
In browser chat, type:
```
continue
```

**Expected Output:**
```
✅ PRESCRIPTION AND FOLLOW-UP PLAN

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💊 YOUR PRESCRIPTION

1. Metformin 1000mg - Take twice daily with meals
2. Amlodipine 5mg - Take once daily in morning
3. Atorvastatin 20mg - Take once daily at bedtime

📅 FOLLOW-UP INSTRUCTIONS
• Recheck blood glucose and BP in 2 weeks
• Repeat full lab panel in 3 months
• Monitor BP at home daily
• Next consultation: 2 weeks

📄 PRESCRIPTION PDF (Auto-generated for your convenience):
   [Download your prescription](https://drive.google.com/...)
   • Location: 4_Prescriptions folder in your Google Drive

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Type "complete" to finish your healthcare journey!
```

**Validation:**
- ✅ 3 medications displayed (numbered list)
- ✅ Follow-up instructions shown (4 bullet points)
- ✅ PDF link present (check Drive folder)
- ✅ No tool call errors in console

---

#### **STEP 5: Schedule Follow-up**
System should ask for follow-up scheduling. Type:
```
in 10 days
```

**Expected Output:**
```
✅ Follow-Up Scheduling Complete!

📅 Follow-up appointment created:
• Date: 2025-11-27 2:00 PM  ← MUST BE 2025, NOT 2024!
• Type: Post-discharge follow-up
...
```

**Validation:**
- ✅ Date is 2025-11-27 (NOT 2024-06-29)
- ✅ Calendar event created
- ✅ Email notification sent

---

#### **STEP 6: Complete Workflow**
Type:
```
complete
```

**Expected Output:**
```
🎉 Healthcare Journey Successfully Completed! 🎉

✅ Stage 1: Registration
✅ Stage 2: Document Upload  
✅ Stage 3: Medical History
...
✅ Stage 12: Journey Completion ⭐

📅 Visit #1 Complete ✅

🔄 Ready for Your Next Visit?
When you return for your next appointment, your complete medical history will be ready. 
You can start your next visit anytime by typing "new visit"

🌟 Current Status:
• ✅ Your profile is saved
• ✅ Medical history recorded
• ✅ Past prescriptions archived
• ✅ Ready for Visit #2 whenever you need us
```

**Validation:**
- ✅ All 12 stages marked complete
- ✅ Visit #1 shown as complete
- ✅ Ready for Visit #2 message
- ✅ Section 8 updated in Google Doc
- ✅ WhatsApp/SMS sent (check console)

---

#### **STEP 7: Test Workflow Loop (Optional)**
Type:
```
new visit
```

**Expected Behavior:**
- ✅ Workflow resets to Stage 2 (not Stage 1!)
- ✅ Visit number increments to 2
- ✅ At Stage 3, past medical history from ChromaDB shown
- ✅ Patient profile preserved

---

## 🐛 Known Issues (Fixed):
- ❌ ~~Medications showing 0 items~~ → ✅ FIXED: Regex pattern updated
- ❌ ~~Date showing 2024-06-29~~ → ✅ FIXED: Added explicit date parsing
- ❌ ~~CheckAvailabilityTool error~~ → ✅ FIXED: Changed to doctor_email parameter
- ❌ ~~SendNotificationTool error~~ → ✅ FIXED: Replaced with SendGmailTool
- ❌ ~~IndexMedicalRecordTool not defined~~ → ✅ FIXED: Import added

---

## 📊 Backend Console Validation

During testing, watch for these logs:

**Stage 7 "check":**
```
✅ User confirmed - transitioning to Stage 11
📋 Reading prescription details from Section 7...
✅ Parsed prescription:
   Medications: 3 items  ← MUST BE 3, NOT 0!
   Follow-up instructions: 4 items
📊 Indexing prescriptions to ChromaDB...
✅ Prescriptions indexed to ChromaDB: [record_id]
```

**Stage 11 "continue":**
```
📝 Generating prescription PDF...
✅ Prescription PDF generated: https://drive.google.com/...
✅ Prescription content formatted: 3 medication(s)
```

**Stage 12 "complete":**
```
✅ Section 8 (Completion) updated in unified workflow document
✅ Congratulatory WhatsApp message sent successfully
```

---

## 🎯 Success Criteria

✅ **All checkboxes must pass:**
- [ ] Section 6 diagnosis parsed correctly
- [ ] NO ADMISSION decision routes to Stage 11
- [ ] 3 medications displayed in numbered list
- [ ] Follow-up instructions (4 items) shown
- [ ] PDF generated and uploaded to Drive
- [ ] Date calculation: "in 10 days" = 2025-11-27
- [ ] No tool call errors in console
- [ ] Stage 12 shows Visit #1 complete
- [ ] Ready for Visit #2 message displayed
- [ ] Section 8 updated in Google Doc

---

## 🚀 Next Steps After Testing

1. **If all tests pass:**
   - Mark todo #8 as completed
   - Test with second patient (different email)
   - Test "new visit" workflow loop
   - Test WITH admission (HOSPITAL ADMISSION REQUIRED)

2. **If any test fails:**
   - Check backend console for errors
   - Verify Google Doc formatting matches template
   - Restart backend if needed
   - Clear cache: `python clear_all_caches.py`

---

## 📞 Support

If you encounter issues:
1. Check backend console logs
2. Verify Google Drive folder structure
3. Confirm GeneratePrescriptionPDFTool has access to prescriptions folder ID
4. Ensure all environment variables are set (.env file)

---

**Last Updated:** November 17, 2025
**Status:** ✅ READY FOR TESTING
