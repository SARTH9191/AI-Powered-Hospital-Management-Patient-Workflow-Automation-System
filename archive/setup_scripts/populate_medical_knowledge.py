"""
Populate Medical Knowledge Base with Sample Data
Creates comprehensive medical knowledge + patient records for RAG system
"""

import os
import sys
from datetime import datetime, timedelta
from tools.vector_search_tool import IndexMedicalRecordTool, get_all_collection_stats

# ============================================================================
# MEDICAL KNOWLEDGE DATA (General Medical Information)
# ============================================================================

MEDICAL_KNOWLEDGE = [
    {
        "text": """Diabetes Mellitus Type 2: A chronic metabolic disorder characterized by insulin resistance and relative insulin deficiency.

Symptoms:
- Increased thirst and frequent urination
- Extreme hunger
- Unexplained weight loss
- Fatigue and irritability
- Blurred vision
- Slow-healing sores
- Frequent infections

Diagnostic Criteria:
- Fasting blood glucose ≥126 mg/dL
- HbA1c ≥6.5%
- Random blood glucose ≥200 mg/dL with symptoms
- 2-hour glucose ≥200 mg/dL during OGTT

Treatment Protocol:
1. Lifestyle modifications (diet, exercise)
2. Metformin (first-line medication)
3. Additional agents: Sulfonylureas, DPP-4 inhibitors, SGLT2 inhibitors, GLP-1 agonists, Insulin
4. Regular monitoring of blood glucose and HbA1c
5. Screen for complications (retinopathy, nephropathy, neuropathy)

Complications: Cardiovascular disease, kidney disease, nerve damage, eye damage, foot problems.""",
        "metadata": {
            "category": "endocrinology",
            "disease": "diabetes_type2",
            "source": "medical_textbook",
            "last_updated": "2024-01-15"
        }
    },
    {
        "text": """Hypertension (High Blood Pressure): A condition where blood pressure is persistently elevated.

Classification:
- Normal: <120/80 mmHg
- Elevated: 120-129/<80 mmHg
- Stage 1: 130-139/80-89 mmHg
- Stage 2: ≥140/90 mmHg
- Hypertensive Crisis: >180/120 mmHg

Symptoms:
Most patients are asymptomatic. Severe cases may have:
- Headaches
- Shortness of breath
- Nosebleeds
- Chest pain
- Visual changes

Risk Factors:
- Age >40 years
- Family history
- Obesity
- High salt intake
- Sedentary lifestyle
- Stress
- Smoking and alcohol

Treatment Guidelines:
1. Lifestyle modifications: Weight loss, DASH diet, reduce sodium, exercise, limit alcohol
2. Pharmacotherapy:
   - First-line: ACE inhibitors (Lisinopril), ARBs (Losartan), CCBs (Amlodipine), Thiazide diuretics
   - Combination therapy for Stage 2
3. Target BP: <130/80 mmHg for most patients
4. Monitor kidney function and electrolytes

Complications: Stroke, heart attack, heart failure, kidney disease, vision loss.""",
        "metadata": {
            "category": "cardiology",
            "disease": "hypertension",
            "source": "AHA_guidelines",
            "last_updated": "2024-02-10"
        }
    },
    {
        "text": """Pneumonia: Acute infection of the lung parenchyma caused by bacteria, viruses, or fungi.

Types:
1. Community-Acquired Pneumonia (CAP) - Most common pathogens: S. pneumoniae, H. influenzae, Mycoplasma
2. Hospital-Acquired Pneumonia (HAP) - Pseudomonas, MRSA, Klebsiella
3. Aspiration Pneumonia - Anaerobes
4. Viral Pneumonia - Influenza, RSV, COVID-19

Clinical Presentation:
- Fever and chills
- Productive cough with purulent sputum
- Shortness of breath
- Pleuritic chest pain
- Tachypnea and tachycardia
- Crackles on auscultation

Diagnostic Tests:
- Chest X-ray (infiltrates)
- CBC (elevated WBC)
- Blood cultures (if severe)
- Sputum culture and Gram stain
- Procalcitonin (bacterial vs viral)

Treatment:
CAP (Outpatient):
- Amoxicillin 1g TID OR
- Azithromycin 500mg once, then 250mg daily OR
- Doxycycline 100mg BID

CAP (Inpatient):
- Ceftriaxone 1-2g IV daily PLUS Azithromycin 500mg IV daily OR
- Fluoroquinolone (Levofloxacin 750mg daily)

HAP:
- Broad-spectrum: Piperacillin-tazobactam + Vancomycin + Azithromycin

Duration: 5-7 days for CAP, 7-14 days for HAP

Monitoring: Clinical improvement within 48-72 hours, repeat X-ray in 6 weeks.""",
        "metadata": {
            "category": "pulmonology",
            "disease": "pneumonia",
            "source": "IDSA_guidelines",
            "last_updated": "2024-03-05"
        }
    },
    {
        "text": """Metformin (Glucophage): First-line medication for Type 2 Diabetes Mellitus.

Mechanism: Decreases hepatic glucose production, increases insulin sensitivity, decreases intestinal glucose absorption.

Indications:
- Type 2 Diabetes Mellitus
- Prediabetes (off-label)
- Polycystic Ovary Syndrome (off-label)

Dosage:
- Starting: 500mg once or twice daily with meals
- Maintenance: 1000-2000mg daily in divided doses
- Maximum: 2550mg/day (IR), 2000mg/day (XR)
- Titrate every 1-2 weeks based on glucose levels

Contraindications:
- eGFR <30 mL/min (absolute)
- eGFR 30-45 mL/min (use with caution, reduce dose)
- Severe hepatic disease
- Heart failure requiring pharmacologic treatment
- Acute/chronic metabolic acidosis

Side Effects:
- GI upset (nausea, diarrhea, abdominal pain) - Most common, usually transient
- Vitamin B12 deficiency (long-term use)
- Lactic acidosis (rare but serious - 0.03 cases/1000 patient-years)

Drug Interactions:
- Contrast dye: Hold 48 hours before/after procedure if eGFR <60
- Alcohol: Increases lactic acidosis risk
- Cimetidine: Decreases metformin clearance

Monitoring:
- HbA1c every 3 months initially, then every 6 months when stable
- eGFR annually (more frequent if CKD)
- Vitamin B12 every 1-2 years

Patient Counseling:
- Take with meals to reduce GI side effects
- Do not crush or chew extended-release tablets
- Report persistent GI symptoms, unusual muscle pain, dizziness
- Avoid excessive alcohol consumption.""",
        "metadata": {
            "category": "pharmacology",
            "drug_name": "metformin",
            "drug_class": "biguanide",
            "source": "drug_database",
            "last_updated": "2024-01-20"
        }
    },
    {
        "text": """Lisinopril: ACE Inhibitor used for hypertension and heart failure.

Mechanism: Inhibits Angiotensin-Converting Enzyme, reducing Angiotensin II production, leading to vasodilation and decreased blood pressure.

Indications:
- Hypertension (first-line)
- Heart failure with reduced ejection fraction
- Post-myocardial infarction
- Diabetic nephropathy

Dosage:
Hypertension:
- Initial: 10mg once daily
- Maintenance: 20-40mg once daily
- Maximum: 80mg once daily

Heart Failure:
- Initial: 2.5-5mg once daily
- Target: 20-40mg once daily

Contraindications:
- History of angioedema
- Pregnancy (Category D)
- Bilateral renal artery stenosis
- Concurrent use with aliskiren in diabetics

Side Effects:
- Dry cough (10-20% of patients) - Most common reason for discontinuation
- Hyperkalemia
- Dizziness and hypotension
- Angioedema (rare but serious - 0.1-0.5%)
- Acute kidney injury (especially with NSAIDs, diuretics)

Drug Interactions:
- NSAIDs: Reduce antihypertensive effect, increase AKI risk
- Potassium-sparing diuretics/supplements: Hyperkalemia
- Lithium: Increased lithium levels

Monitoring:
- Blood pressure: Weekly initially, then monthly
- Creatinine and potassium: Baseline, 1-2 weeks after initiation, then periodically
- Check potassium if adding diuretics or potassium supplements

Patient Counseling:
- May cause dizziness, especially when starting - rise slowly from sitting/lying
- Avoid NSAIDs (ibuprofen, naproxen) - use acetaminophen instead
- Report swelling of face, lips, tongue immediately (angioedema)
- Use contraception if female of childbearing age
- Do not stop suddenly without consulting doctor.""",
        "metadata": {
            "category": "pharmacology",
            "drug_name": "lisinopril",
            "drug_class": "ace_inhibitor",
            "source": "drug_database",
            "last_updated": "2024-02-15"
        }
    },
    {
        "text": """Chest Pain Assessment and Management Protocol

INITIAL ASSESSMENT (OPQRST):
- Onset: When did it start? Sudden or gradual?
- Provocation: What makes it better/worse?
- Quality: Sharp, dull, crushing, burning?
- Radiation: Does it spread? (arm, jaw, back)
- Severity: 0-10 scale
- Time: How long? Constant or intermittent?

RED FLAGS (IMMEDIATE ED/Cardiology):
- Crushing/pressure sensation
- Radiation to left arm, jaw, or back
- Associated with dyspnea, diaphoresis, nausea
- History of CAD, diabetes, hypertension
- New ST-segment changes on ECG
- Elevated troponin

DIFFERENTIAL DIAGNOSIS:
1. Cardiac:
   - Acute Coronary Syndrome (ACS)
   - Stable angina
   - Pericarditis
   - Myocardial infarction

2. Pulmonary:
   - Pulmonary embolism
   - Pneumothorax
   - Pneumonia
   - Pleuritis

3. GI:
   - GERD
   - Esophageal spasm
   - Peptic ulcer disease
   - Pancreatitis

4. Musculoskeletal:
   - Costochondritis
   - Muscle strain
   - Rib fracture

WORKUP:
- ECG (within 10 minutes of presentation)
- Troponin (baseline, 3-6 hours)
- CBC, BMP, lipid panel
- Chest X-ray
- D-dimer if PE suspected
- Consider: Echo, stress test, CT angiography

MANAGEMENT:
If ACS suspected (MONA):
- Morphine (pain control)
- Oxygen (if SpO2 <90%)
- Nitroglycerin (sublingual or spray)
- Aspirin 325mg chewed

Disposition:
- Admit: Confirmed ACS, unstable vitals, high-risk features
- Observation: Atypical presentation, borderline troponin
- Discharge: Clear non-cardiac cause, normal ECG/troponin, low risk score

Follow-up: All patients with chest pain should have cardiology follow-up within 2 weeks.""",
        "metadata": {
            "category": "emergency_medicine",
            "topic": "chest_pain_protocol",
            "source": "hospital_protocol",
            "last_updated": "2024-03-01"
        }
    },
    {
        "text": """Complete Blood Count (CBC) - Normal Values and Interpretation

Normal Ranges (Adults):
- WBC: 4,500-11,000 cells/mcL
- RBC: Males 4.7-6.1 million/mcL, Females 4.2-5.4 million/mcL
- Hemoglobin: Males 13.5-17.5 g/dL, Females 12.0-15.5 g/dL
- Hematocrit: Males 38.8-50%, Females 34.9-44.5%
- Platelets: 150,000-400,000/mcL
- MCV: 80-100 fL
- MCH: 27-33 pg
- MCHC: 32-36 g/dL

White Blood Cell (WBC) Differential:
- Neutrophils: 40-70% (2,500-7,500/mcL)
- Lymphocytes: 20-40% (1,500-4,000/mcL)
- Monocytes: 2-8% (200-800/mcL)
- Eosinophils: 1-4% (50-400/mcL)
- Basophils: 0-2% (25-100/mcL)

CLINICAL INTERPRETATION:

Elevated WBC (Leukocytosis):
- Infection (bacterial > viral)
- Inflammation
- Stress, trauma, burns
- Leukemia
- Medications (steroids)

Low WBC (Leukopenia):
- Viral infections
- Autoimmune disorders
- Bone marrow failure
- Chemotherapy
- Severe infections (sepsis)

Elevated Neutrophils:
- Bacterial infection
- Acute inflammation
- Stress, exercise

Elevated Lymphocytes:
- Viral infections (EBV, CMV)
- Chronic infections (TB)
- Leukemia/lymphoma

Elevated Eosinophils:
- Allergies
- Parasitic infections
- Asthma
- Drug reactions

Low Hemoglobin (Anemia):
- Iron deficiency (low MCV)
- B12/folate deficiency (high MCV)
- Chronic disease
- Blood loss
- Hemolysis

High Hemoglobin (Polycythemia):
- Dehydration
- COPD, smoking
- Polycythemia vera
- High altitude

Low Platelets (Thrombocytopenia):
- ITP (immune thrombocytopenia)
- Medications (heparin)
- Sepsis, DIC
- Bone marrow disorders
- Hypersplenism

High Platelets (Thrombocytosis):
- Reactive (infection, inflammation, blood loss)
- Myeloproliferative disorders
- Post-splenectomy""",
        "metadata": {
            "category": "laboratory",
            "test_name": "cbc",
            "source": "lab_manual",
            "last_updated": "2024-01-10"
        }
    }
]

# ============================================================================
# PATIENT MEDICAL RECORDS (Sample Cases)
# ============================================================================

PATIENT_RECORDS = [
    {
        "text": """Patient: REG2025001 (John Doe)
Date: 2024-12-15
Chief Complaint: Increased thirst and frequent urination for 3 weeks

History of Present Illness:
45-year-old male presents with polyuria, polydipsia, and fatigue for the past 3 weeks. Reports increased hunger despite eating more. Noticed blurred vision recently. Weight loss of 8 kg over 2 months despite increased appetite. No fever, no chest pain, no shortness of breath.

Past Medical History:
- Hypertension (diagnosed 2 years ago, controlled on Lisinopril 10mg)
- Obesity (BMI 32)
- Hyperlipidemia

Family History:
- Father: Type 2 Diabetes, Hypertension
- Mother: Hypertension, Stroke at age 65

Social History:
- Non-smoker
- Occasional alcohol (social drinker)
- Sedentary lifestyle, office job

Physical Examination:
- BP: 142/88 mmHg
- HR: 82 bpm
- Weight: 95 kg, Height: 172 cm, BMI: 32.1
- General: Obese, fatigued appearance
- HEENT: Dry mucous membranes
- Cardiovascular: RRR, no murmurs
- Respiratory: CTAB
- Abdomen: Soft, obese, non-tender
- Extremities: No edema

Laboratory Results:
- Fasting Glucose: 245 mg/dL (Normal: <100)
- HbA1c: 8.9% (Normal: <5.7%)
- Random Glucose: 312 mg/dL
- Creatinine: 1.1 mg/dL (Normal: 0.7-1.3)
- eGFR: 78 mL/min
- Lipid Panel: Total Cholesterol 220, LDL 145, HDL 38, Triglycerides 285

Assessment:
Type 2 Diabetes Mellitus (newly diagnosed)
Hypertension (uncontrolled)
Dyslipidemia

Plan:
1. Start Metformin 500mg BID, titrate to 1000mg BID over 2 weeks
2. Increase Lisinopril to 20mg daily
3. Start Atorvastatin 40mg daily
4. Diabetes education and dietary counseling
5. Encourage exercise (30 min daily walking)
6. Home glucose monitoring - fasting and 2-hour post-meal
7. Follow-up in 2 weeks for glucose review
8. HbA1c in 3 months
9. Ophthalmology referral for diabetic retinopathy screening
10. Annual foot examination""",
        "metadata": {
            "patient_id": "REG2025001",
            "date": "2024-12-15",
            "doctor_id": "DR001",
            "diagnosis": "type2_diabetes",
            "age": 45,
            "gender": "male"
        }
    },
    {
        "text": """Patient: REG2025002 (Jane Smith)
Date: 2024-12-20
Chief Complaint: Cough with fever for 5 days

History of Present Illness:
32-year-old female presents with productive cough with yellow-green sputum, fever (101-102°F), and shortness of breath for 5 days. Also reports chills, body aches, and pleuritic right-sided chest pain. Initially thought it was a cold, but symptoms worsened. Denies recent travel, sick contacts with COVID-19. Denies nausea, vomiting, or diarrhea.

Past Medical History:
- Asthma (well-controlled on Albuterol PRN)
- Seasonal allergies

Medications:
- Albuterol inhaler PRN
- Loratadine 10mg daily

Allergies: Penicillin (rash)

Social History:
- Non-smoker
- Lives with husband and 2 children (ages 5 and 7)
- Children recently had upper respiratory infections

Physical Examination:
- Temp: 101.4°F (38.6°C)
- BP: 118/76 mmHg
- HR: 98 bpm
- RR: 22/min
- SpO2: 94% on room air
- General: Ill-appearing, mild respiratory distress
- HEENT: Pharynx erythematous, no exudates
- Cardiovascular: Tachycardic, RRR
- Respiratory: Decreased breath sounds right lower lobe, crackles, dullness to percussion
- Abdomen: Soft, non-tender

Laboratory Results:
- WBC: 14,500/mcL (elevated)
- Neutrophils: 82% (elevated)
- CRP: 45 mg/L (elevated)
- Procalcitonin: 2.1 ng/mL (elevated - suggests bacterial infection)

Imaging:
- Chest X-ray: Right lower lobe infiltrate consistent with pneumonia

Assessment:
Community-Acquired Pneumonia (CAP), moderate severity
CURB-65 score: 1 (confusion=0, urea=0, RR=1, BP=0, age=0) - Outpatient treatment

Plan:
1. Azithromycin 500mg PO day 1, then 250mg daily for 4 more days (total 5 days)
   - Chosen due to penicillin allergy
   - Alternative: Doxycycline 100mg BID for 7 days OR Levofloxacin 750mg daily for 5 days
2. Supportive care:
   - Rest and hydration
   - Acetaminophen 650mg q6h PRN fever/pain
   - Guaifenesin for cough
3. Continue Albuterol for bronchospasm
4. Strict return precautions: Worsening SOB, high fever >103°F, confusion, inability to tolerate PO
5. Follow-up call in 48 hours to ensure clinical improvement
6. Office follow-up in 1 week if not improving
7. Repeat chest X-ray in 6 weeks if not improving""",
        "metadata": {
            "patient_id": "REG2025002",
            "date": "2024-12-20",
            "doctor_id": "DR002",
            "diagnosis": "pneumonia",
            "age": 32,
            "gender": "female"
        }
    },
    {
        "text": """Patient: REG2025003 (Robert Johnson)
Date: 2025-01-05
Chief Complaint: Chest pain for 2 hours

History of Present Illness:
58-year-old male presents with acute onset of substernal chest pressure starting 2 hours ago while shoveling snow. Describes pain as "heavy pressure" 8/10 severity, radiating to left arm and jaw. Associated with dyspnea, diaphoresis, and nausea. No relief with rest. Wife called 911, patient brought in by EMS.

Past Medical History:
- Hypertension (10 years)
- Hyperlipidemia
- Type 2 Diabetes (5 years)
- Current smoker (30 pack-years)

Medications:
- Lisinopril 20mg daily
- Atorvastatin 40mg daily
- Metformin 1000mg BID
- Aspirin 81mg daily

Family History:
- Father: MI at age 52, deceased
- Brother: CABG at age 55

Social History:
- Smokes 1 PPD for 30 years
- Denies alcohol or drug use
- Sedentary lifestyle

Physical Examination:
- Temp: 98.2°F
- BP: 168/95 mmHg
- HR: 102 bpm
- RR: 22/min
- SpO2: 96% on 2L NC
- General: Anxious, diaphoretic, in moderate distress
- Cardiovascular: Tachycardic, S4 gallop, no murmurs
- Respiratory: Mild crackles bilaterally at bases
- Extremities: Cool, diaphoretic

EMS Report:
- Initial BP: 180/100 mmHg
- Given: Aspirin 325mg chewed, Nitroglycerin SL x2 (minimal relief), Morphine 4mg IV

Emergency Department Workup:
- ECG: ST-segment elevation 2mm in leads II, III, aVF (INFERIOR STEMI)
- Troponin I: 0.8 ng/mL (elevated, rising)
- CBC, BMP: Pending
- Chest X-ray: Mild pulmonary congestion

Assessment:
**ACUTE ST-ELEVATION MYOCARDIAL INFARCTION (STEMI) - INFERIOR WALL**
Cardiogenic shock risk

IMMEDIATE MANAGEMENT (Door-to-Balloon <90 minutes):
1. **ACTIVATE CATH LAB** - Primary PCI
2. Medications:
   - Aspirin 325mg (already given)
   - Clopidogrel 600mg loading dose
   - Heparin IV bolus 60 units/kg, then infusion
   - Nitroglycerin IV drip for BP control
   - Morphine 2-4mg IV PRN pain
   - Metoprolol 25mg PO (hold if hypotensive)
3. Cardiology consulted - Dr. Anderson to perform emergent cardiac catheterization
4. ICU bed reserved
5. Patient and family counseled on procedure, risks, and prognosis

Door-to-Balloon Time Target: <60 minutes
Patient transported to cath lab at 14:35 (55 minutes from arrival)

Cath Lab Findings:
- 95% occlusion of right coronary artery (RCA)
- Drug-eluting stent placed successfully
- TIMI flow grade 3 restored
- No complications

Post-PCI Plan:
1. ICU admission for monitoring
2. Dual antiplatelet therapy: Aspirin 81mg + Clopidogrel 75mg daily for 12 months minimum
3. High-intensity statin: Atorvastatin 80mg daily
4. Beta-blocker: Metoprolol 25mg BID, uptitrate as tolerated
5. ACE inhibitor: Continue Lisinopril 20mg
6. Cardiac rehabilitation referral
7. Smoking cessation counseling - CRITICAL
8. Echocardiogram in AM to assess LV function
9. Lipid panel fasting
10. Diabetes management optimization

Prognosis: Good outcome with timely intervention. Emphasize medication compliance and lifestyle modifications.""",
        "metadata": {
            "patient_id": "REG2025003",
            "date": "2025-01-05",
            "doctor_id": "DR003",
            "diagnosis": "stemi",
            "age": 58,
            "gender": "male",
            "emergency": True
        }
    }
]

# ============================================================================
# LAB RESULTS
# ============================================================================

LAB_RESULTS = [
    {
        "text": """Patient: REG2025001 (John Doe)
Date: 2024-12-15
Test: Complete Metabolic Panel + HbA1c

GLUCOSE METABOLISM:
- Fasting Glucose: 245 mg/dL ↑ (Normal: 70-100)
- HbA1c: 8.9% ↑ (Normal: <5.7%, Prediabetes: 5.7-6.4%, Diabetes: ≥6.5%)
- Random Glucose: 312 mg/dL ↑

KIDNEY FUNCTION:
- BUN: 18 mg/dL (Normal: 7-20)
- Creatinine: 1.1 mg/dL (Normal: 0.7-1.3)
- eGFR: 78 mL/min/1.73m² (Normal: >90)
- BUN/Creatinine Ratio: 16.4 (Normal: 10-20)

ELECTROLYTES:
- Sodium: 142 mEq/L (Normal: 136-145)
- Potassium: 4.2 mEq/L (Normal: 3.5-5.0)
- Chloride: 103 mEq/L (Normal: 98-107)
- CO2: 25 mEq/L (Normal: 23-29)

LIVER FUNCTION:
- AST: 32 U/L (Normal: 10-40)
- ALT: 38 U/L (Normal: 7-56)
- Total Bilirubin: 0.8 mg/dL (Normal: 0.1-1.2)
- Alkaline Phosphatase: 72 U/L (Normal: 44-147)

LIPID PANEL:
- Total Cholesterol: 220 mg/dL ↑ (Desirable: <200)
- LDL: 145 mg/dL ↑ (Optimal: <100, Desirable: <130)
- HDL: 38 mg/dL ↓ (Desirable: >40 males, >50 females)
- Triglycerides: 285 mg/dL ↑ (Normal: <150)
- VLDL: 57 mg/dL (calculated)

INTERPRETATION:
1. **Newly diagnosed Type 2 Diabetes Mellitus** - HbA1c 8.9% and fasting glucose 245 mg/dL confirm diagnosis
2. **Dyslipidemia** - Elevated LDL, low HDL, elevated triglycerides (atherogenic dyslipidemia pattern common in diabetes)
3. **Mild kidney dysfunction** - eGFR 78 (Stage 2 CKD), likely early diabetic nephropathy
4. Normal liver function and electrolytes

RECOMMENDATIONS:
1. Start Metformin (check eGFR - OK to use with eGFR >30)
2. Start statin therapy for LDL >100 in diabetic patient (Atorvastatin 40mg)
3. Lifestyle modifications: Diet (low carb, low fat), exercise, weight loss goal 10%
4. Recheck HbA1c in 3 months (target <7%)
5. Annual microalbumin screening for nephropathy
6. Monitor kidney function every 6-12 months""",
        "metadata": {
            "patient_id": "REG2025001",
            "test_type": "metabolic_panel",
            "date": "2024-12-15",
            "ordered_by": "DR001"
        }
    }
]

# ============================================================================
# TREATMENT PROTOCOLS
# ============================================================================

TREATMENT_PROTOCOLS = [
    {
        "text": """Type 2 Diabetes Management Protocol - Stepwise Approach

STEP 1: LIFESTYLE MODIFICATIONS (All patients)
- Medical Nutrition Therapy: Carbohydrate counting, portion control, Mediterranean diet
- Physical Activity: 150 min/week moderate intensity (walking, cycling)
- Weight Loss: Target 5-10% if overweight/obese
- Smoking cessation if applicable
- Blood pressure control (<130/80 mmHg)
- Lipid management (statin therapy)

STEP 2: METFORMIN (First-line pharmacotherapy)
Initiation:
- Start: Metformin 500mg once or twice daily with meals
- Titrate: Increase by 500mg weekly to maintenance dose
- Maintenance: 1000-2000mg daily in divided doses
- Maximum: 2550mg/day (IR), 2000mg/day (XR)
- Target HbA1c: <7% for most, <6.5% if low hypoglycemia risk, <8% if elderly/comorbidities

Monitoring:
- HbA1c every 3 months until goal, then every 6 months
- eGFR before starting, annually thereafter
- B12 levels every 1-2 years

STEP 3: ADD SECOND AGENT (If HbA1c >7% after 3 months on Metformin)

ASCVD/CKD/HF Present:
- **GLP-1 RA** (Ozempic, Trulicity) - Preferred if ASCVD or need weight loss
- **SGLT2i** (Jardiance, Farxiga) - Preferred if CKD or HF

NO ASCVD/CKD/HF:
- **GLP-1 RA** - If weight loss needed
- **DPP-4i** (Januvia, Tradjenta) - Weight neutral
- **Sulfonylurea** (Glipizide) - Low cost option, but hypoglycemia risk
- **Thiazolidinedione** (Pioglitazone) - Avoid if HF

STEP 4: TRIPLE THERAPY (If HbA1c still >7%)
- Metformin + GLP-1 RA + SGLT2i (preferred)
- OR Add basal insulin (Glargine, Degludec)

STEP 5: INSULIN INTENSIFICATION
Basal Insulin:
- Start: Glargine 10 units SC daily at bedtime
- Titrate: Increase by 2 units every 3 days based on fasting glucose
- Target fasting glucose: 80-130 mg/dL

If inadequate control, add:
- Basal-Bolus: Add rapid-acting insulin (Lispro, Aspart) before meals
- Starting dose: 4 units or 10% of basal dose per meal
- Adjust based on pre-meal and 2-hour post-meal glucose

MONITORING TARGETS:
- Fasting/Pre-meal: 80-130 mg/dL
- 2-hour Post-meal: <180 mg/dL
- HbA1c: <7% (individualized)
- Blood pressure: <130/80 mmHg
- LDL: <100 mg/dL (statin therapy)

ANNUAL SCREENING:
- HbA1c: Every 3-6 months
- Lipid panel: Annually
- Microalbumin/Creatinine ratio: Annually
- Dilated eye exam: Annually
- Foot examination: Annually
- Flu vaccine: Annually
- Pneumococcal vaccine: Once

REFERRALS:
- Endocrinology: If unable to achieve goals, considering insulin pump
- Ophthalmology: Annual dilated eye exams
- Podiatry: If foot complications
- Nephrology: If eGFR <30 or worsening proteinuria
- Cardiology: If ASCVD present""",
        "metadata": {
            "protocol_type": "treatment_algorithm",
            "condition": "type2_diabetes",
            "source": "ADA_guidelines_2024",
            "last_updated": "2024-01-01"
        }
    }
]

# ============================================================================
# POPULATE FUNCTION
# ============================================================================

def populate_all_data():
    """Populate all collections with sample data"""
    
    print("=" * 80)
    print("🏥 POPULATING MEDICAL KNOWLEDGE BASE")
    print("=" * 80)
    print()
    
    index_tool = IndexMedicalRecordTool()
    total_indexed = 0
    
    # 1. INDEX MEDICAL KNOWLEDGE
    print("📚 Indexing Medical Knowledge...")
    for i, knowledge in enumerate(MEDICAL_KNOWLEDGE, 1):
        result = index_tool._run(
            collection="medical_knowledge",
            text=knowledge["text"],
            metadata=knowledge["metadata"]
        )
        if result.get("success"):
            print(f"   ✅ {i}/{len(MEDICAL_KNOWLEDGE)}: {knowledge['metadata'].get('category', 'N/A')}")
            total_indexed += 1
        else:
            print(f"   ❌ {i}/{len(MEDICAL_KNOWLEDGE)}: {result.get('error')}")
    
    print()
    
    # 2. INDEX PATIENT RECORDS
    print("📋 Indexing Patient Medical Records...")
    for i, record in enumerate(PATIENT_RECORDS, 1):
        result = index_tool._run(
            collection="medical_records",
            text=record["text"],
            metadata=record["metadata"]
        )
        if result.get("success"):
            print(f"   ✅ {i}/{len(PATIENT_RECORDS)}: Patient {record['metadata']['patient_id']}")
            total_indexed += 1
        else:
            print(f"   ❌ {i}/{len(PATIENT_RECORDS)}: {result.get('error')}")
    
    print()
    
    # 3. INDEX LAB RESULTS
    print("🧪 Indexing Lab Results...")
    for i, lab in enumerate(LAB_RESULTS, 1):
        result = index_tool._run(
            collection="lab_results",
            text=lab["text"],
            metadata=lab["metadata"]
        )
        if result.get("success"):
            print(f"   ✅ {i}/{len(LAB_RESULTS)}: {lab['metadata']['test_type']}")
            total_indexed += 1
        else:
            print(f"   ❌ {i}/{len(LAB_RESULTS)}: {result.get('error')}")
    
    print()
    
    # 4. INDEX TREATMENT PROTOCOLS
    print("💊 Indexing Treatment Protocols...")
    for i, protocol in enumerate(TREATMENT_PROTOCOLS, 1):
        result = index_tool._run(
            collection="treatments",
            text=protocol["text"],
            metadata=protocol["metadata"]
        )
        if result.get("success"):
            print(f"   ✅ {i}/{len(TREATMENT_PROTOCOLS)}: {protocol['metadata']['condition']}")
            total_indexed += 1
        else:
            print(f"   ❌ {i}/{len(TREATMENT_PROTOCOLS)}: {result.get('error')}")
    
    print()
    print("=" * 80)
    print(f"✅ INDEXING COMPLETE! Total: {total_indexed} records")
    print("=" * 80)
    print()
    
    # Show collection stats
    print("📊 COLLECTION STATISTICS:")
    stats = get_all_collection_stats()
    for stat in stats:
        if "error" not in stat:
            print(f"   📁 {stat['collection']}: {stat['total_records']} records")
    
    print()
    print("🎉 Medical knowledge base is ready for RAG queries!")
    print()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    try:
        populate_all_data()
        
        print("💡 Next Steps:")
        print("   1. Test semantic search: python -c \"from tools.vector_search_tool import SemanticSearchTool; tool = SemanticSearchTool(); print(tool._run('diabetes symptoms', 'medical_knowledge'))\"")
        print("   2. Test RAG queries: python test_rag_system.py")
        print("   3. Integrate into workflow_chat_agent.py for context-aware Q&A")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
