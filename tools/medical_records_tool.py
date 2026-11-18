"""
Medical Records Tool for Hospital Management System
Manages patient medical history, prescriptions, allergies, diagnoses, and treatment timeline
"""

import json
from typing import Optional, Type, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from langchain.tools import BaseTool

# Import database tools for integration
from tools.database_tool import load_db, save_db, PATIENTS_DB_FILE, MEDICAL_RECORDS_DB_FILE, PRESCRIPTIONS_DB_FILE


# ==================== DRUG INTERACTION DATABASE (Simplified) ====================

DRUG_INTERACTIONS = {
    "Aspirin": ["Warfarin", "Ibuprofen", "Naproxen"],
    "Warfarin": ["Aspirin", "Vitamin K", "Green Tea"],
    "Metformin": ["Alcohol", "Contrast Dye"],
    "Lisinopril": ["Potassium Supplements", "Spironolactone"],
    "Simvastatin": ["Grapefruit Juice", "Cyclosporine"],
    "Amoxicillin": ["Probenecid", "Methotrexate"],
    "Ciprofloxacin": ["Antacids", "Dairy Products", "Caffeine"],
    "Prednisone": ["NSAIDs", "Vaccines", "Grapefruit"],
    "Insulin": ["Alcohol", "Beta Blockers"],
    "Levothyroxine": ["Calcium", "Iron", "Antacids"]
}

COMMON_ALLERGIES = [
    "Penicillin", "Sulfa drugs", "Aspirin", "NSAIDs", "Latex",
    "Peanuts", "Tree nuts", "Shellfish", "Eggs", "Milk",
    "Iodine", "Contrast dye", "Local anesthetics"
]


# ==================== INPUT SCHEMAS ====================

class GetMedicalHistoryInput(BaseModel):
    """Input for getting patient medical history."""
    patient_id: str = Field(description="Patient registration ID")


class AddPrescriptionInput(BaseModel):
    """Input for adding prescription to medical record."""
    patient_id: str = Field(description="Patient registration ID")
    medication_name: str = Field(description="Name of medication")
    dosage: str = Field(description="Dosage (e.g., 500mg, 10ml)")
    frequency: str = Field(description="Frequency (e.g., Twice daily, Every 8 hours)")
    duration: str = Field(description="Duration (e.g., 7 days, 2 weeks)")
    instructions: Optional[str] = Field(default=None, description="Special instructions")
    doctor_name: str = Field(description="Prescribing doctor name")


class AddAllergyInput(BaseModel):
    """Input for adding allergy to patient record."""
    patient_id: str = Field(description="Patient registration ID")
    allergen: str = Field(description="Substance causing allergy")
    reaction: str = Field(description="Type of allergic reaction")
    severity: str = Field(description="Severity: Mild, Moderate, Severe, Life-threatening")


class UpdateDiagnosisInput(BaseModel):
    """Input for updating patient diagnosis."""
    patient_id: str = Field(description="Patient registration ID")
    diagnosis: str = Field(description="Medical diagnosis")
    diagnosis_date: str = Field(description="Date of diagnosis (YYYY-MM-DD)")
    doctor_name: str = Field(description="Diagnosing doctor name")
    notes: Optional[str] = Field(default=None, description="Additional notes")


class AddChronicConditionInput(BaseModel):
    """Input for adding chronic condition."""
    patient_id: str = Field(description="Patient registration ID")
    condition: str = Field(description="Chronic condition name")
    diagnosed_date: str = Field(description="Date diagnosed (YYYY-MM-DD)")
    treatment_status: str = Field(description="Treatment status: Controlled, Uncontrolled, Monitoring")


class CheckDrugInteractionInput(BaseModel):
    """Input for checking drug interactions."""
    current_medications: List[str] = Field(description="List of current medications")
    new_medication: str = Field(description="New medication to check")


class GetTreatmentTimelineInput(BaseModel):
    """Input for getting treatment timeline."""
    patient_id: str = Field(description="Patient registration ID")


# ==================== MEDICAL RECORDS TOOLS ====================

class GetMedicalHistoryTool(BaseTool):
    """Tool for retrieving complete medical history."""
    
    name: str = "get_medical_history"
    description: str = """Get complete medical history for a patient. 
    Returns all medical records, prescriptions, allergies, chronic conditions, and diagnoses."""
    args_schema: Type[BaseModel] = GetMedicalHistoryInput
    
    def _run(self, patient_id: str) -> str:
        try:
            # Load patient database
            patients_db = load_db(PATIENTS_DB_FILE)
            
            if patient_id not in patients_db:
                return f"❌ Patient not found with ID: {patient_id}"
            
            patient = patients_db[patient_id]
            
            # Load medical records
            medical_records_db = load_db(MEDICAL_RECORDS_DB_FILE)
            patient_records = [record for record in medical_records_db.values() 
                             if record.get('patient_id') == patient_id]
            
            # Load prescriptions
            prescriptions_db = load_db(PRESCRIPTIONS_DB_FILE)
            patient_prescriptions = [rx for rx in prescriptions_db.values() 
                                   if rx.get('patient_id') == patient_id]
            
            # Format medical history
            result = f"""✅ Medical History Retrieved

{'='*70}
PATIENT INFORMATION
{'='*70}

🆔 Patient ID: {patient_id}
👤 Name: {patient['full_name']}
📅 Date of Birth: {patient['date_of_birth']} (Age: {patient.get('age', 'N/A')})
🩸 Blood Group: {patient.get('blood_group', 'Not recorded')}

{'='*70}
ALLERGIES
{'='*70}

"""
            
            # Display allergies
            if patient.get('allergies'):
                for i, allergy in enumerate(patient['allergies'], 1):
                    if isinstance(allergy, dict):
                        result += f"{i}. {allergy.get('allergen', 'Unknown')}\n"
                        result += f"   Reaction: {allergy.get('reaction', 'Not specified')}\n"
                        result += f"   Severity: {allergy.get('severity', 'Not specified')}\n\n"
                    else:
                        result += f"{i}. {allergy}\n"
            else:
                result += "No known allergies recorded.\n"
            
            result += f"\n{'='*70}\nCHRONIC CONDITIONS\n{'='*70}\n\n"
            
            # Display chronic conditions
            if patient.get('chronic_conditions'):
                for i, condition in enumerate(patient['chronic_conditions'], 1):
                    if isinstance(condition, dict):
                        result += f"{i}. {condition.get('condition', 'Unknown')}\n"
                        result += f"   Diagnosed: {condition.get('diagnosed_date', 'Not recorded')}\n"
                        result += f"   Status: {condition.get('treatment_status', 'Not specified')}\n\n"
                    else:
                        result += f"{i}. {condition}\n"
            else:
                result += "No chronic conditions recorded.\n"
            
            result += f"\n{'='*70}\nMEDICAL RECORDS\n{'='*70}\n\n"
            
            # Display medical records
            if patient_records:
                for i, record in enumerate(patient_records, 1):
                    result += f"""Record {i}:
  📅 Visit Date: {record.get('visit_date', 'Not recorded')}
  👨‍⚕️ Doctor: {record.get('doctor_name', 'Not recorded')}
  🏥 Chief Complaint: {record.get('chief_complaint', 'Not recorded')}
  🩺 Diagnosis: {record.get('diagnosis', 'Not recorded')}
  💊 Treatment: {record.get('treatment_plan', 'Not recorded')}
  
  Vitals:
    • Blood Pressure: {record.get('blood_pressure', 'N/A')}
    • Heart Rate: {record.get('heart_rate', 'N/A')} bpm
    • Temperature: {record.get('temperature', 'N/A')}°F
    • Weight: {record.get('weight', 'N/A')} kg
    • BMI: {record.get('bmi', 'N/A')}

"""
            else:
                result += "No medical records found.\n"
            
            result += f"\n{'='*70}\nACTIVE PRESCRIPTIONS\n{'='*70}\n\n"
            
            # Display active prescriptions
            active_prescriptions = [rx for rx in patient_prescriptions 
                                  if rx.get('status') == 'Active']
            
            if active_prescriptions:
                for i, rx in enumerate(active_prescriptions, 1):
                    result += f"""Prescription {i}: {rx.get('prescription_id', 'N/A')}
  📅 Prescribed: {rx.get('prescription_date', 'Not recorded')}
  👨‍⚕️ Doctor: {rx.get('doctor_name', 'Not recorded')}
  
  Medications:
"""
                    for med in rx.get('medications', []):
                        result += f"""    • {med.get('name', 'Unknown')}
      Dosage: {med.get('dosage', 'Not specified')}
      Frequency: {med.get('frequency', 'Not specified')}
      Duration: {med.get('duration', 'Not specified')}
      Instructions: {med.get('instructions', 'None')}

"""
            else:
                result += "No active prescriptions.\n"
            
            result += f"{'='*70}\n"
            result += f"\n📊 Summary:\n"
            result += f"  • Medical Records: {len(patient_records)}\n"
            result += f"  • Total Prescriptions: {len(patient_prescriptions)}\n"
            result += f"  • Active Prescriptions: {len(active_prescriptions)}\n"
            result += f"  • Allergies: {len(patient.get('allergies', []))}\n"
            result += f"  • Chronic Conditions: {len(patient.get('chronic_conditions', []))}\n"
            
            return result
        
        except Exception as e:
            return f"❌ Error retrieving medical history: {str(e)}"
    
    async def _arun(self, patient_id: str) -> str:
        return self._run(patient_id)


class AddPrescriptionTool(BaseTool):
    """Tool for adding prescription to patient record."""
    
    name: str = "add_prescription"
    description: str = """Add a new prescription to patient's medical record. 
    Includes medication name, dosage, frequency, duration, and instructions."""
    args_schema: Type[BaseModel] = AddPrescriptionInput
    
    def _run(self, patient_id: str, medication_name: str, dosage: str,
             frequency: str, duration: str, doctor_name: str,
             instructions: Optional[str] = None) -> str:
        try:
            # Load patient database
            patients_db = load_db(PATIENTS_DB_FILE)
            
            if patient_id not in patients_db:
                return f"❌ Patient not found with ID: {patient_id}"
            
            patient = patients_db[patient_id]
            
            # Check drug interactions
            current_meds = []
            prescriptions_db = load_db(PRESCRIPTIONS_DB_FILE)
            for rx in prescriptions_db.values():
                if rx.get('patient_id') == patient_id and rx.get('status') == 'Active':
                    for med in rx.get('medications', []):
                        current_meds.append(med.get('name', ''))
            
            interactions = []
            if medication_name in DRUG_INTERACTIONS:
                for med in current_meds:
                    if med in DRUG_INTERACTIONS[medication_name]:
                        interactions.append(med)
            
            # Check allergies
            allergy_warning = ""
            patient_allergies = patient.get('allergies', [])
            for allergy in patient_allergies:
                allergen = allergy if isinstance(allergy, str) else allergy.get('allergen', '')
                if allergen.lower() in medication_name.lower():
                    allergy_warning = f"\n⚠️ WARNING: Patient has allergy to {allergen}!"
            
            # Generate prescription ID
            import random, string
            prescription_id = f"RX{datetime.now().year}{''.join(random.choices(string.digits, k=6))}"
            
            # Create prescription record
            prescription = {
                "prescription_id": prescription_id,
                "patient_id": patient_id,
                "doctor_name": doctor_name,
                "prescription_date": datetime.now().strftime('%Y-%m-%d'),
                "valid_until": "",  # Can be calculated based on duration
                "medications": [
                    {
                        "name": medication_name,
                        "dosage": dosage,
                        "frequency": frequency,
                        "duration": duration,
                        "instructions": instructions or "Take as directed"
                    }
                ],
                "special_instructions": instructions or "",
                "warnings": "",
                "status": "Active",
                "dispensed": False,
                "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Save prescription
            prescriptions_db[prescription_id] = prescription
            save_db(PRESCRIPTIONS_DB_FILE, prescriptions_db)
            
            # Update patient record
            if 'prescriptions' not in patient:
                patient['prescriptions'] = []
            patient['prescriptions'].append(prescription_id)
            patients_db[patient_id] = patient
            save_db(PATIENTS_DB_FILE, patients_db)
            
            interaction_warning = ""
            if interactions:
                interaction_warning = f"\n⚠️ DRUG INTERACTIONS DETECTED:\n"
                for med in interactions:
                    interaction_warning += f"   • {medication_name} interacts with {med}\n"
                interaction_warning += "   Consult with doctor before proceeding!\n"
            
            return f"""✅ Prescription Added Successfully!

🆔 Prescription ID: {prescription_id}
👤 Patient: {patient['full_name']} ({patient_id})
📅 Date: {prescription['prescription_date']}
👨‍⚕️ Doctor: {doctor_name}

💊 Medication Details:
   • Name: {medication_name}
   • Dosage: {dosage}
   • Frequency: {frequency}
   • Duration: {duration}
   • Instructions: {instructions or 'Take as directed'}

✅ Status: Active
{allergy_warning}{interaction_warning}
📋 Prescription has been added to patient's medical record.
"""
        
        except Exception as e:
            return f"❌ Error adding prescription: {str(e)}"
    
    async def _arun(self, patient_id: str, medication_name: str, dosage: str,
                    frequency: str, duration: str, doctor_name: str,
                    instructions: Optional[str] = None) -> str:
        return self._run(patient_id, medication_name, dosage, frequency, 
                        duration, doctor_name, instructions)


class AddAllergyTool(BaseTool):
    """Tool for adding allergy to patient record."""
    
    name: str = "add_allergy"
    description: str = """Add allergy to patient's medical record. 
    Records allergen, reaction type, and severity for safety checks."""
    args_schema: Type[BaseModel] = AddAllergyInput
    
    def _run(self, patient_id: str, allergen: str, reaction: str, severity: str) -> str:
        try:
            # Load patient database
            patients_db = load_db(PATIENTS_DB_FILE)
            
            if patient_id not in patients_db:
                return f"❌ Patient not found with ID: {patient_id}"
            
            patient = patients_db[patient_id]
            
            # Initialize allergies list if not exists
            if 'allergies' not in patient:
                patient['allergies'] = []
            
            # Check if allergy already exists
            for allergy in patient['allergies']:
                if isinstance(allergy, dict):
                    if allergy.get('allergen', '').lower() == allergen.lower():
                        return f"⚠️ Allergy to {allergen} already recorded for this patient."
            
            # Add allergy
            allergy_entry = {
                "allergen": allergen,
                "reaction": reaction,
                "severity": severity,
                "recorded_date": datetime.now().strftime('%Y-%m-%d'),
                "recorded_by": "System"
            }
            
            patient['allergies'].append(allergy_entry)
            patient['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Save database
            patients_db[patient_id] = patient
            save_db(PATIENTS_DB_FILE, patients_db)
            
            severity_emoji = "⚠️" if severity.lower() == "mild" else ("🚨" if severity.lower() in ["severe", "life-threatening"] else "⚠️")
            
            return f"""✅ Allergy Added to Medical Record!

👤 Patient: {patient['full_name']} ({patient_id})
{severity_emoji} Allergen: {allergen}
💥 Reaction: {reaction}
📊 Severity: {severity}
📅 Recorded: {allergy_entry['recorded_date']}

⚠️ This allergy will be checked against all future prescriptions!

📋 Total Allergies: {len(patient['allergies'])}
"""
        
        except Exception as e:
            return f"❌ Error adding allergy: {str(e)}"
    
    async def _arun(self, patient_id: str, allergen: str, reaction: str, severity: str) -> str:
        return self._run(patient_id, allergen, reaction, severity)


class UpdateDiagnosisTool(BaseTool):
    """Tool for updating patient diagnosis."""
    
    name: str = "update_diagnosis"
    description: str = """Update or add new diagnosis to patient's medical record. 
    Records diagnosis, date, doctor, and notes."""
    args_schema: Type[BaseModel] = UpdateDiagnosisInput
    
    def _run(self, patient_id: str, diagnosis: str, diagnosis_date: str,
             doctor_name: str, notes: Optional[str] = None) -> str:
        try:
            # Load patient database
            patients_db = load_db(PATIENTS_DB_FILE)
            
            if patient_id not in patients_db:
                return f"❌ Patient not found with ID: {patient_id}"
            
            patient = patients_db[patient_id]
            
            # Initialize medical history if not exists
            if 'medical_history' not in patient:
                patient['medical_history'] = []
            
            # Create diagnosis entry
            diagnosis_entry = {
                "diagnosis": diagnosis,
                "diagnosis_date": diagnosis_date,
                "doctor_name": doctor_name,
                "notes": notes or "",
                "recorded_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            patient['medical_history'].append(diagnosis_entry)
            patient['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Save database
            patients_db[patient_id] = patient
            save_db(PATIENTS_DB_FILE, patients_db)
            
            return f"""✅ Diagnosis Updated Successfully!

👤 Patient: {patient['full_name']} ({patient_id})
🩺 Diagnosis: {diagnosis}
📅 Diagnosis Date: {diagnosis_date}
👨‍⚕️ Doctor: {doctor_name}
📝 Notes: {notes or 'None'}

📋 Total Diagnoses: {len(patient['medical_history'])}
✅ Diagnosis has been added to medical history.
"""
        
        except Exception as e:
            return f"❌ Error updating diagnosis: {str(e)}"
    
    async def _arun(self, patient_id: str, diagnosis: str, diagnosis_date: str,
                    doctor_name: str, notes: Optional[str] = None) -> str:
        return self._run(patient_id, diagnosis, diagnosis_date, doctor_name, notes)


class AddChronicConditionTool(BaseTool):
    """Tool for adding chronic condition to patient record."""
    
    name: str = "add_chronic_condition"
    description: str = """Add chronic condition to patient's medical record. 
    Records condition name, diagnosis date, and treatment status."""
    args_schema: Type[BaseModel] = AddChronicConditionInput
    
    def _run(self, patient_id: str, condition: str, diagnosed_date: str, 
             treatment_status: str) -> str:
        try:
            # Load patient database
            patients_db = load_db(PATIENTS_DB_FILE)
            
            if patient_id not in patients_db:
                return f"❌ Patient not found with ID: {patient_id}"
            
            patient = patients_db[patient_id]
            
            # Initialize chronic conditions if not exists
            if 'chronic_conditions' not in patient:
                patient['chronic_conditions'] = []
            
            # Check if condition already exists
            for existing_condition in patient['chronic_conditions']:
                if isinstance(existing_condition, dict):
                    if existing_condition.get('condition', '').lower() == condition.lower():
                        return f"⚠️ Chronic condition '{condition}' already recorded for this patient."
            
            # Add chronic condition
            condition_entry = {
                "condition": condition,
                "diagnosed_date": diagnosed_date,
                "treatment_status": treatment_status,
                "recorded_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            patient['chronic_conditions'].append(condition_entry)
            patient['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Save database
            patients_db[patient_id] = patient
            save_db(PATIENTS_DB_FILE, patients_db)
            
            return f"""✅ Chronic Condition Added to Medical Record!

👤 Patient: {patient['full_name']} ({patient_id})
🏥 Condition: {condition}
📅 Diagnosed: {diagnosed_date}
📊 Treatment Status: {treatment_status}

📋 Total Chronic Conditions: {len(patient['chronic_conditions'])}
✅ Condition has been added to patient's medical record.
"""
        
        except Exception as e:
            return f"❌ Error adding chronic condition: {str(e)}"
    
    async def _arun(self, patient_id: str, condition: str, diagnosed_date: str, 
                    treatment_status: str) -> str:
        return self._run(patient_id, condition, diagnosed_date, treatment_status)


class CheckDrugInteractionTool(BaseTool):
    """Tool for checking drug interactions."""
    
    name: str = "check_drug_interaction"
    description: str = """Check if new medication interacts with current medications. 
    Provides warnings about potential drug interactions."""
    args_schema: Type[BaseModel] = CheckDrugInteractionInput
    
    def _run(self, current_medications: List[str], new_medication: str) -> str:
        try:
            interactions = []
            
            # Check interactions
            if new_medication in DRUG_INTERACTIONS:
                for med in current_medications:
                    if med in DRUG_INTERACTIONS[new_medication]:
                        interactions.append({
                            "drug1": new_medication,
                            "drug2": med,
                            "severity": "Moderate to Severe"
                        })
            
            # Reverse check
            for med in current_medications:
                if med in DRUG_INTERACTIONS:
                    if new_medication in DRUG_INTERACTIONS[med]:
                        if not any(i['drug2'] == med for i in interactions):
                            interactions.append({
                                "drug1": med,
                                "drug2": new_medication,
                                "severity": "Moderate to Severe"
                            })
            
            if not interactions:
                return f"""✅ No Drug Interactions Detected

💊 New Medication: {new_medication}
📋 Current Medications: {', '.join(current_medications)}

✅ No known interactions found in database.
💡 Always consult with pharmacist or doctor before starting new medication.
"""
            
            result = f"""⚠️ DRUG INTERACTIONS DETECTED!

💊 New Medication: {new_medication}
📋 Current Medications: {', '.join(current_medications)}

{'='*70}
INTERACTIONS FOUND
{'='*70}

"""
            
            for i, interaction in enumerate(interactions, 1):
                result += f"""{i}. {interaction['drug1']} ⚠️ {interaction['drug2']}
   Severity: {interaction['severity']}
   
"""
            
            result += f"""{'='*70}

🚨 RECOMMENDATIONS:
   1. Consult with doctor before proceeding
   2. Consider alternative medications
   3. Monitor for adverse effects
   4. Adjust dosages if necessary

⚠️ This is a simplified check. Always verify with pharmacist!
"""
            
            return result
        
        except Exception as e:
            return f"❌ Error checking drug interactions: {str(e)}"
    
    async def _arun(self, current_medications: List[str], new_medication: str) -> str:
        return self._run(current_medications, new_medication)


class GetTreatmentTimelineTool(BaseTool):
    """Tool for viewing patient treatment timeline."""
    
    name: str = "get_treatment_timeline"
    description: str = """Get chronological timeline of patient's medical treatment. 
    Shows diagnoses, prescriptions, procedures, and visits in order."""
    args_schema: Type[BaseModel] = GetTreatmentTimelineInput
    
    def _run(self, patient_id: str) -> str:
        try:
            # Load databases
            patients_db = load_db(PATIENTS_DB_FILE)
            
            if patient_id not in patients_db:
                return f"❌ Patient not found with ID: {patient_id}"
            
            patient = patients_db[patient_id]
            
            # Load medical records and prescriptions
            medical_records_db = load_db(MEDICAL_RECORDS_DB_FILE)
            prescriptions_db = load_db(PRESCRIPTIONS_DB_FILE)
            
            # Collect timeline events
            timeline = []
            
            # Add registration
            timeline.append({
                "date": patient.get('registration_date', 'Unknown'),
                "type": "Registration",
                "description": f"Patient registered in system"
            })
            
            # Add medical history
            for entry in patient.get('medical_history', []):
                if isinstance(entry, dict):
                    timeline.append({
                        "date": entry.get('diagnosis_date', 'Unknown'),
                        "type": "Diagnosis",
                        "description": f"{entry.get('diagnosis', 'Unknown diagnosis')} by {entry.get('doctor_name', 'Unknown')}"
                    })
            
            # Add chronic conditions
            for condition in patient.get('chronic_conditions', []):
                if isinstance(condition, dict):
                    timeline.append({
                        "date": condition.get('diagnosed_date', 'Unknown'),
                        "type": "Chronic Condition",
                        "description": f"{condition.get('condition', 'Unknown')} - Status: {condition.get('treatment_status', 'Unknown')}"
                    })
            
            # Add medical records
            for record in medical_records_db.values():
                if record.get('patient_id') == patient_id:
                    timeline.append({
                        "date": record.get('visit_date', 'Unknown'),
                        "type": "Medical Visit",
                        "description": f"Visit with {record.get('doctor_name', 'Unknown')} - {record.get('chief_complaint', 'Checkup')}"
                    })
            
            # Add prescriptions
            for rx in prescriptions_db.values():
                if rx.get('patient_id') == patient_id:
                    meds = ', '.join([m.get('name', 'Unknown') for m in rx.get('medications', [])])
                    timeline.append({
                        "date": rx.get('prescription_date', 'Unknown'),
                        "type": "Prescription",
                        "description": f"Prescribed {meds} by {rx.get('doctor_name', 'Unknown')}"
                    })
            
            # Sort timeline by date
            timeline.sort(key=lambda x: x['date'], reverse=True)
            
            result = f"""✅ Treatment Timeline Retrieved

👤 Patient: {patient['full_name']} ({patient_id})
📊 Total Events: {len(timeline)}

{'='*70}
CHRONOLOGICAL TIMELINE (Most Recent First)
{'='*70}

"""
            
            for i, event in enumerate(timeline, 1):
                icon = "🏥" if event['type'] == "Medical Visit" else ("💊" if event['type'] == "Prescription" else ("🩺" if event['type'] == "Diagnosis" else "📋"))
                result += f"""{i}. {icon} {event['type']} - {event['date']}
   {event['description']}

"""
            
            return result
        
        except Exception as e:
            return f"❌ Error retrieving treatment timeline: {str(e)}"
    
    async def _arun(self, patient_id: str) -> str:
        return self._run(patient_id)


# ==================== HELPER FUNCTION ====================

def get_all_medical_records_tools():
    """Get all medical records tools for the agent"""
    return [
        GetMedicalHistoryTool(),
        AddPrescriptionTool(),
        AddAllergyTool(),
        UpdateDiagnosisTool(),
        AddChronicConditionTool(),
        CheckDrugInteractionTool(),
        GetTreatmentTimelineTool()
    ]


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🏥 MEDICAL RECORDS TOOLS - Hospital Management System")
    print("="*70)
    
    print("\n📋 Available Tools:")
    print("  1. get_medical_history - Complete medical history")
    print("  2. add_prescription - Add prescription with drug interaction check")
    print("  3. add_allergy - Record patient allergies")
    print("  4. update_diagnosis - Update diagnoses")
    print("  5. add_chronic_condition - Add chronic conditions")
    print("  6. check_drug_interaction - Check drug interactions")
    print("  7. get_treatment_timeline - Chronological treatment view")
    
    print("\n✅ Features:")
    print("  • Comprehensive medical history tracking")
    print("  • Drug interaction warnings")
    print("  • Allergy checks before prescriptions")
    print("  • Chronic condition monitoring")
    print("  • Treatment timeline visualization")
    
    print("\n" + "="*70)
