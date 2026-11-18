flowchart TD
    %% START - Circle
    START((🏥 Patient Arrives))
    
    %% REGISTRATION PHASE - Rectangle Agents, Diamond Decisions
    START --> REG_AGENT[📝 Registration Agent]
    REG_AGENT --> NEW_PATIENT{Is New Patient?}
    
    NEW_PATIENT -->|YES| FULL_REG[Full Registration Form<br/>📋 Name, Phone, Address<br/>🆔 ID Verification<br/>📄 Emergency Contact]
    NEW_PATIENT -->|NO| FETCH_REC[Fetch Existing Records<br/>🔍 Search by Phone/ID<br/>📊 Load Medical History<br/>✅ Verify Identity]
    
    FULL_REG --> DOC_COLLECT[📂 Document Collection]
    FETCH_REC --> DOC_COLLECT
    
    DOC_COLLECT --> UPLOAD_DRIVE[☁️ Upload to Google Drive<br/>📁 Create Patient Folder<br/>🔒 Set Permissions<br/>📝 Log Upload Activity]
    
    %% DOCUMENT PROCESSING PHASE
    UPLOAD_DRIVE --> DOC_AGENT[🤖 Document Processing Agent]
    DOC_AGENT --> DOC_COMPLETE{All Documents<br/>Complete?}
    
    DOC_COMPLETE -->|NO| MISSING_DOCS[📨 Request Missing Documents<br/>📧 Email Template<br/>📱 SMS Alert<br/>⏰ Set Follow-up Timer]
    MISSING_DOCS --> WAIT_DOCS[⏳ Wait for Documents<br/>🔔 Send Reminders<br/>📅 Track Submission]
    WAIT_DOCS --> DOC_COMPLETE
    
    DOC_COMPLETE -->|YES| EXTRACT_INFO[🔍 Extract Information<br/>📊 OCR Processing<br/>🏷️ Categorize Documents<br/>💾 Structure Data]
    EXTRACT_INFO --> UPDATE_DB[(💾 Update Database<br/>✍️ Patient Record<br/>🏥 Medical History<br/>💳 Insurance Info)]
    
    %% MEDICAL HISTORY ANALYSIS
    UPDATE_DB --> MED_AGENT[🩺 Medical History Agent]
    MED_AGENT --> VECTOR_QUERY[🔍 Query Vector Database<br/>🧠 Semantic Search<br/>📈 Pattern Matching<br/>🔄 Similarity Analysis]
    
    VECTOR_QUERY --> PAST_ISSUES{Past Medical<br/>Issues Found?}
    
    PAST_ISSUES -->|YES| ANALYZE_CONDITIONS[🔬 Analyze Conditions<br/>⚠️ Risk Assessment<br/>🧬 Complication Check<br/>📊 Severity Rating]
    PAST_ISSUES -->|NO| BASIC_CHECK[✅ Basic Health Check<br/>📏 Standard Screening<br/>🎂 Age-based Tests<br/>⚖️ BMI Calculation]
    
    ANALYZE_CONDITIONS --> LLM_TESTS[🤖 LLM Determines Tests<br/>🧪 AI Recommendation<br/>📋 Test Priority<br/>⏰ Urgency Level]
    BASIC_CHECK --> LLM_TESTS
    
    %% LAB COORDINATION PHASE
    LLM_TESTS --> TESTS_REQ{Tests Required?}
    
    TESTS_REQ -->|YES| LAB_AGENT[🧪 Lab Coordination Agent]
    TESTS_REQ -->|NO| SKIP_TO_ADM[⏭️ Skip to Admission Planning]
    
    LAB_AGENT --> PAT_PREF{Patient Lab<br/>Preference?}
    
    PAT_PREF -->|Hospital Lab| INTERNAL_SCHED[🏥 Check Internal Schedule<br/>📅 Available Slots<br/>👨‍⚕️ Technician Availability<br/>🏠 Room Assignment]
    PAT_PREF -->|External Lab| EXTERNAL_LIST[📋 Generate Test List<br/>📍 Nearby Labs<br/>💰 Cost Comparison<br/>📄 Test Instructions]
    
    INTERNAL_SCHED --> BOOK_APPT[📅 Book Appointment<br/>🕒 Time Slot<br/>📍 Location Details<br/>⏰ Preparation Time]
    EXTERNAL_LIST --> SEND_LIST[📤 Send List to Patient<br/>📧 Email with Details<br/>📱 SMS Backup<br/>🔗 Online Links]
    
    BOOK_APPT --> CONFIRM_SMS[📱 Send Confirmation<br/>📧 Email + SMS<br/>📅 Calendar Invite<br/>🔔 Reminder Setup]
    SEND_LIST --> WAIT_EXT[⏳ Wait for External Results<br/>📬 Monitor Uploads<br/>📞 Follow-up Calls<br/>⏰ Deadline Tracking]
    
    CONFIRM_SMS --> PAT_CONFIRM{Patient<br/>Confirms?}
    
    PAT_CONFIRM -->|NO| RESCHEDULE[🔄 Reschedule Appointment<br/>📅 New Time Slots<br/>📞 Call Patient<br/>✅ Reconfirm]
    PAT_CONFIRM -->|YES| WAIT_TEST[⏳ Wait for Test Date<br/>📅 Day Before Reminder<br/>📋 Preparation Check<br/>🚗 Direction Info]
    
    RESCHEDULE --> BOOK_APPT
    
    WAIT_TEST --> TEST_DONE[✅ Test Completed<br/>🧪 Sample Collected<br/>⏰ Processing Time<br/>📊 Results Expected]
    WAIT_EXT --> UPLOAD_RES[📤 Upload Results<br/>📁 Digital Files<br/>🔍 Quality Check<br/>📝 Metadata Tags]
    TEST_DONE --> UPLOAD_RES
    
    %% RESULTS ANALYSIS PHASE
    UPLOAD_RES --> RES_AGENT[📊 Results Analysis Agent]
    RES_AGENT --> RES_NORMAL{Results<br/>Normal?}
    
    RES_NORMAL -->|NO| FLAG_DOC[🚨 Flag for Doctor Review<br/>⚠️ Priority Alert<br/>📞 Notify Doctor<br/>📋 Summary Report]
    RES_NORMAL -->|YES| PROCEED_ADM[✅ Proceed to Admission<br/>✔️ Clear for Surgery<br/>📝 Results Summary<br/>👍 Doctor Approval]
    
    FLAG_DOC --> DOC_REVIEW[👨‍⚕️ Doctor Reviews<br/>🔍 Clinical Analysis<br/>📞 Patient Consultation<br/>💊 Treatment Decision]
    DOC_REVIEW --> APPROVE_ADM{Doctor Approves<br/>Admission?}
    
    APPROVE_ADM -->|NO| ADD_TREATMENT[🏥 Additional Treatment<br/>💊 Medication Plan<br/>🧪 More Tests<br/>📅 Follow-up Schedule]
    APPROVE_ADM -->|YES| PROCEED_ADM
    
    ADD_TREATMENT --> LAB_AGENT
    
    %% ADMISSION PLANNING PHASE
    PROCEED_ADM --> SKIP_TO_ADM
    SKIP_TO_ADM --> ADM_AGENT[🏥 Admission Planning Agent]
    ADM_AGENT --> BED_AVAIL{Beds<br/>Available?}
    
    BED_AVAIL -->|NO| WAITING_LIST[📋 Add to Waiting List<br/>📞 Notify Position<br/>⏰ Estimated Wait<br/>📱 Update Alerts]
    BED_AVAIL -->|YES| RESERVE_BED[🛏️ Reserve Bed<br/>🏠 Room Assignment<br/>👨‍⚕️ Doctor Assignment<br/>📅 Admission Date]
    
    WAITING_LIST --> NOTIFY_AVAIL[🔔 Notify When Available<br/>📞 Priority Call<br/>📧 Email Alert<br/>⏰ Response Deadline]
    NOTIFY_AVAIL --> BED_AVAIL
    
    RESERVE_BED --> CALC_COST[💰 Calculate Estimated Cost<br/>🛏️ Room Charges<br/>👨‍⚕️ Doctor Fees<br/>🏥 Facility Charges]
    
    CALC_COST --> INSURANCE{Insurance<br/>Coverage?}
    
    INSURANCE -->|YES| CHECK_COV[🔍 Check Coverage<br/>📄 Policy Verification<br/>💳 Benefits Analysis<br/>📊 Coverage Percentage]
    INSURANCE -->|NO| FULL_PAY[💰 Full Payment Required<br/>💳 Payment Options<br/>📊 Cost Breakdown<br/>📅 Payment Plan]
    
    CHECK_COV --> CALC_COPAY[🧮 Calculate Co-payment<br/>💰 Patient Portion<br/>📊 Insurance Portion<br/>📄 Authorization]
    FULL_PAY --> GEN_EST[📊 Generate Cost Estimate<br/>💰 Total Amount<br/>📋 Itemized Bill<br/>📅 Payment Terms]
    CALC_COPAY --> GEN_EST
    
    %% ADMISSION CONFIRMATION
    GEN_EST --> SEND_DETAILS[📤 Send Admission Details<br/>📧 Email Package<br/>📱 SMS Summary<br/>📄 PDF Documents]
    SEND_DETAILS --> PAT_CONFIRM_ADM{Patient Confirms<br/>Admission?}
    
    PAT_CONFIRM_ADM -->|NO| CANCEL_RESC[❌ Cancel/Reschedule<br/>📅 New Dates<br/>🔄 Restart Process<br/>📞 Follow-up Call]
    PAT_CONFIRM_ADM -->|YES| CONFIRM_ADM[✅ Confirm Admission<br/>📅 Fixed Schedule<br/>🎯 Final Preparations<br/>📋 Checklist Ready]
    
    CANCEL_RESC --> ADM_AGENT
    
    %% PRE-ADMISSION PHASE
    CONFIRM_ADM --> PRE_ADM_AGENT[📋 Pre-Admission Agent]
    PRE_ADM_AGENT --> GEN_SUMMARY[📄 Generate Doctor Summary<br/>🩺 Medical History<br/>🧪 Test Results<br/>⚠️ Risk Factors]
    
    GEN_SUMMARY --> CREATE_DOC[📝 Create Google Doc<br/>🔗 Shareable Link<br/>👥 Access Permissions<br/>📊 Structured Format]
    CREATE_DOC --> SHARE_DOC[📤 Share with Doctor<br/>📧 Email Notification<br/>🔔 Mobile Alert<br/>📅 Review Deadline]
    SHARE_DOC --> PREP_INST[📋 Send Prep Instructions<br/>🚫 Fasting Guidelines<br/>💊 Medication Changes<br/>📅 Arrival Time]
    
    %% ADMISSION DAY PHASE
    PREP_INST --> CHECKIN_AGENT[🏥 Check-in Agent]
    CHECKIN_AGENT --> VERIFY_DOCS[✅ Verify Documents<br/>🆔 ID Check<br/>📄 Insurance Cards<br/>📝 Consent Forms]
    
    VERIFY_DOCS --> ASSIGN_ROOM[🏠 Assign Room<br/>🛏️ Bed Number<br/>🔑 Access Cards<br/>📍 Location Map]
    ASSIGN_ROOM --> START_BILLING[💰 Start Billing Meter<br/>⏰ Check-in Time<br/>📊 Rate Structure<br/>💾 Database Entry]
    
    %% DURING STAY PHASE
    START_BILLING --> DAILY_AGENT[📊 Daily Tracking Agent]
    DAILY_AGENT --> ROOM_CHARGES[🏠 Room Charges<br/>🛏️ Accommodation<br/>❄️ AC/Utilities<br/>🍽️ Food Services]
    
    ROOM_CHARGES --> MEDICINE_Q{Medicines from<br/>Hospital?}
    
    MEDICINE_Q -->|YES| ADD_MED_CHARGES[💊 Add Medicine Charges<br/>💰 Pharmacy Bills<br/>📋 Dosage Records<br/>⏰ Time Stamps]
    MEDICINE_Q -->|NO| SKIP_MED[⏭️ Skip Medicine Billing<br/>📝 Patient Provided<br/>✅ Record Decision]
    
    ADD_MED_CHARGES --> UPDATE_DAILY[📊 Update Daily Bill<br/>💰 Running Total<br/>📈 Cost Tracking<br/>📄 Daily Summary]
    SKIP_MED --> UPDATE_DAILY
    
    UPDATE_DAILY --> PROCEDURES_Q{Procedures<br/>Done Today?}
    
    PROCEDURES_Q -->|YES| ADD_PROC_COST[🏥 Add Procedure Costs<br/>💰 Operation Charges<br/>👨‍⚕️ Doctor Fees<br/>🧪 Lab Charges]
    PROCEDURES_Q -->|NO| CONTINUE_TRACK[⏭️ Continue Tracking<br/>📊 Monitor Status<br/>⏰ Daily Review<br/>📋 Update Records]
    
    ADD_PROC_COST --> CONTINUE_TRACK
    CONTINUE_TRACK --> READY_DISCHARGE{Ready for<br/>Discharge?}
    
    READY_DISCHARGE -->|NO| ROOM_CHARGES
    READY_DISCHARGE -->|YES| DISCHARGE_AGENT[🏠 Discharge Agent]
    
    %% DISCHARGE PHASE
    DISCHARGE_AGENT --> STOP_BILLING[🛑 Stop Billing Meter<br/>⏰ Discharge Time<br/>📊 Final Calculation<br/>💾 Close Billing]
    
    STOP_BILLING --> GEN_FINAL_BILL[📄 Generate Final Bill<br/>💰 Total Charges<br/>📋 Itemized List<br/>📊 Cost Breakdown]
    GEN_FINAL_BILL --> APPLY_INS[📊 Apply Insurance<br/>💳 Coverage Deduction<br/>🧮 Co-pay Calculation<br/>📄 Claim Processing]
    
    APPLY_INS --> PAT_PAYMENT[💰 Patient Payment<br/>💳 Payment Methods<br/>🧾 Receipt Generation<br/>📄 Payment Record]
    PAT_PAYMENT --> PAYMENT_COMPLETE{Payment<br/>Complete?}
    
    PAYMENT_COMPLETE -->|NO| PAYMENT_PLAN[📅 Setup Payment Plan<br/>💰 Installment Options<br/>📋 Agreement Terms<br/>⏰ Payment Schedule]
    PAYMENT_COMPLETE -->|YES| DISCHARGE_SUMMARY[📄 Generate Discharge Summary<br/>🩺 Treatment Summary<br/>💊 Medicine List<br/>📅 Follow-up Plan]
    
    PAYMENT_PLAN --> DISCHARGE_SUMMARY
    
    %% FOLLOW-UP PHASE
    DISCHARGE_SUMMARY --> FOLLOWUP_AGENT[📞 Follow-up Agent]
    FOLLOWUP_AGENT --> SCHEDULE_FOLLOWUP[📅 Schedule Follow-up<br/>👨‍⚕️ Doctor Appointment<br/>📞 Booking Confirmation<br/>🔔 Reminder Setup]
    
    SCHEDULE_FOLLOWUP --> CARE_INST[📋 Send Care Instructions<br/>💊 Medication Schedule<br/>🚫 Activity Restrictions<br/>⚠️ Warning Signs]
    CARE_INST --> MED_REMIND[💊 Set Medicine Reminders<br/>⏰ Daily Alerts<br/>📱 Mobile Notifications<br/>📊 Adherence Tracking]
    
    MED_REMIND --> WAIT_3DAYS[⏳ Wait 3 Days<br/>📅 Recovery Period<br/>📞 Check-in Calls<br/>🔍 Monitor Progress]
    WAIT_3DAYS --> FEEDBACK_FORM[📝 Send Feedback Form<br/>⭐ Service Rating<br/>💬 Comments Section<br/>📊 Satisfaction Score]
    
    FEEDBACK_FORM --> COLLECT_FEEDBACK[📊 Collect Feedback<br/>📈 Analytics Dashboard<br/>📋 Improvement Areas<br/>🏆 Success Metrics]
    
    %% END - Circle
    COLLECT_FEEDBACK --> END((🎯 Journey Complete<br/>✅ All Tasks Done<br/>📊 Data Recorded<br/>🔄 Ready for Next))
    
    %% STYLING
    classDef agentClass fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef decisionClass fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    classDef processClass fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    classDef startEndClass fill:#e8f5e8,stroke:#1b5e20,stroke-width:3px,color:#000
    classDef databaseClass fill:#fff8e1,stroke:#f57f17,stroke-width:2px,color:#000
    
    class REG_AGENT,DOC_AGENT,MED_AGENT,LAB_AGENT,RES_AGENT,ADM_AGENT,PRE_ADM_AGENT,CHECKIN_AGENT,DAILY_AGENT,DISCHARGE_AGENT,FOLLOWUP_AGENT agentClass
    class NEW_PATIENT,DOC_COMPLETE,PAST_ISSUES,TESTS_REQ,PAT_PREF,PAT_CONFIRM,RES_NORMAL,APPROVE_ADM,BED_AVAIL,INSURANCE,PAT_CONFIRM_ADM,MEDICINE_Q,PROCEDURES_Q,READY_DISCHARGE,PAYMENT_COMPLETE decisionClass
    class START,END startEndClass
    class UPDATE_DB databaseClass