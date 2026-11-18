"""
Patient Registration Tool for Hospital Management System
Handles new patient registration, ID generation, demographics, and folder creation
"""

import os
import json
import random
import string
from typing import Optional, Type, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from langchain.tools import BaseTool


# ==================== PATIENT DATABASE (In-Memory for now, will connect to DB later) ====================

PATIENTS_DB_FILE = 'data/patients_database.json'


def load_patients_db():
    """Load patients database from JSON file"""
    if not os.path.exists(PATIENTS_DB_FILE):
        os.makedirs(os.path.dirname(PATIENTS_DB_FILE), exist_ok=True)
        return {}
    
    try:
        with open(PATIENTS_DB_FILE, 'r') as f:
            data = json.load(f)
            
            # Handle both list format (from patients_router) and dict format (from registration_tool)
            if isinstance(data, list):
                # Convert list format to dict format
                dict_data = {}
                for patient in data:
                    if isinstance(patient, dict) and 'patient_id' in patient:
                        dict_data[patient['patient_id']] = patient
                return dict_data
            elif isinstance(data, dict):
                return data
            else:
                return {}
    except:
        return {}


def save_patients_db(db):
    """Save patients database to JSON file"""
    os.makedirs(os.path.dirname(PATIENTS_DB_FILE), exist_ok=True)
    
    # Ensure we always save in dictionary format (patient_id as keys)
    if isinstance(db, dict):
        # Already in correct format
        with open(PATIENTS_DB_FILE, 'w') as f:
            json.dump(db, f, indent=2)
    else:
        # Convert list format to dict format before saving
        dict_db = {}
        if isinstance(db, list):
            for patient in db:
                if isinstance(patient, dict) and 'patient_id' in patient:
                    dict_db[patient['patient_id']] = patient
        with open(PATIENTS_DB_FILE, 'w') as f:
            json.dump(dict_db, f, indent=2)


def generate_patient_id():
    """Generate unique patient registration ID"""
    year = datetime.now().year
    random_num = ''.join(random.choices(string.digits, k=6))
    return f"REG{year}{random_num}"


# ==================== INPUT SCHEMAS ====================

class RegisterPatientInput(BaseModel):
    """Input for registering a new patient."""
    first_name: str = Field(description="Patient's first name")
    last_name: str = Field(description="Patient's last name")
    date_of_birth: str = Field(description="Date of birth (YYYY-MM-DD)")
    gender: str = Field(description="Gender: Male, Female, or Other")
    phone: str = Field(description="Contact phone number")
    email: str = Field(description="Contact email address")
    address: str = Field(description="Residential address")
    emergency_contact_name: Optional[str] = Field(default=None, description="Emergency contact person name")
    emergency_contact_phone: Optional[str] = Field(default=None, description="Emergency contact phone")
    blood_group: Optional[str] = Field(default=None, description="Blood group (A+, B+, O+, AB+, etc.)")
    insurance_provider: Optional[str] = Field(default=None, description="Insurance company name")
    insurance_policy_number: Optional[str] = Field(default=None, description="Insurance policy number")


class SearchPatientInput(BaseModel):
    """Input for searching patients."""
    search_query: str = Field(description="Search by name, patient ID, phone, or email")


class GetPatientDetailsInput(BaseModel):
    """Input for getting patient details."""
    patient_id: str = Field(description="Patient registration ID")


class UpdatePatientInput(BaseModel):
    """Input for updating patient information."""
    patient_id: str = Field(description="Patient registration ID")
    field_name: str = Field(description="Field to update: phone, email, address, emergency_contact_name, emergency_contact_phone, insurance_provider, insurance_policy_number")
    new_value: str = Field(description="New value for the field")


class ValidateInsuranceInput(BaseModel):
    """Input for validating insurance."""
    insurance_provider: str = Field(description="Insurance provider name")
    policy_number: str = Field(description="Policy number")
    patient_name: str = Field(description="Patient name for verification")


# ==================== REGISTRATION TOOLS ====================

class RegisterPatientTool(BaseTool):
    """Tool for registering new patients."""
    
    name: str = "register_new_patient"
    description: str = """Register a new patient in the hospital system. 
    Collects demographics, contact info, emergency contacts, and insurance details. 
    Automatically generates unique patient ID and creates patient record."""
    args_schema: Type[BaseModel] = RegisterPatientInput
    
    def _run(self, first_name: str, last_name: str, date_of_birth: str, 
             gender: str, phone: str, email: str, address: str,
             emergency_contact_name: Optional[str] = None,
             emergency_contact_phone: Optional[str] = None,
             blood_group: Optional[str] = None,
             insurance_provider: Optional[str] = None,
             insurance_policy_number: Optional[str] = None) -> str:
        try:
            # Load existing database
            db = load_patients_db()
            
            # Generate unique patient ID
            patient_id = generate_patient_id()
            while patient_id in db:  # Ensure uniqueness
                patient_id = generate_patient_id()
            
            # Calculate age
            try:
                dob = datetime.strptime(date_of_birth, '%Y-%m-%d')
                age = (datetime.now() - dob).days // 365
            except:
                age = None
            
            # Create patient record
            patient_record = {
                'patient_id': patient_id,
                'first_name': first_name,
                'last_name': last_name,
                'full_name': f"{first_name} {last_name}",
                'date_of_birth': date_of_birth,
                'age': age,
                'gender': gender,
                'phone': phone,
                'email': email,
                'address': address,
                'emergency_contact_name': emergency_contact_name,
                'emergency_contact_phone': emergency_contact_phone,
                'blood_group': blood_group,
                'insurance_provider': insurance_provider,
                'insurance_policy_number': insurance_policy_number,
                'registration_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'Active',
                'medical_history': [],
                'appointments': [],
                'lab_tests': [],
                'prescriptions': []
            }
            
            # Save to database
            db[patient_id] = patient_record
            save_patients_db(db)
            
            # Format insurance info
            insurance_info = ""
            if insurance_provider:
                insurance_info = f"""
📋 Insurance Information:
   - Provider: {insurance_provider}
   - Policy Number: {insurance_policy_number or 'N/A'}
"""
            
            # Format emergency contact
            emergency_info = ""
            if emergency_contact_name:
                emergency_info = f"""
🚨 Emergency Contact:
   - Name: {emergency_contact_name}
   - Phone: {emergency_contact_phone or 'N/A'}
"""
            
            return f"""✅ Patient Registered Successfully!

🆔 Patient ID: {patient_id}
👤 Name: {first_name} {last_name}
📅 Date of Birth: {date_of_birth} (Age: {age or 'N/A'})
⚧ Gender: {gender}
🩸 Blood Group: {blood_group or 'Not provided'}

📞 Contact Information:
   - Phone: {phone}
   - Email: {email}
   - Address: {address}
{emergency_info}{insurance_info}
📅 Registration Date: {patient_record['registration_date']}
✅ Status: Active

💡 Patient record created. Use Patient ID '{patient_id}' for all future interactions.

🔜 Next Steps:
   1. Create patient folder in Google Drive
   2. Send welcome email
   3. Schedule initial consultation
"""
        
        except Exception as e:
            return f"❌ Error registering patient: {str(e)}"
    
    async def _arun(self, first_name: str, last_name: str, date_of_birth: str, 
                    gender: str, phone: str, email: str, address: str,
                    emergency_contact_name: Optional[str] = None,
                    emergency_contact_phone: Optional[str] = None,
                    blood_group: Optional[str] = None,
                    insurance_provider: Optional[str] = None,
                    insurance_policy_number: Optional[str] = None) -> str:
        return self._run(first_name, last_name, date_of_birth, gender, phone, 
                        email, address, emergency_contact_name, emergency_contact_phone,
                        blood_group, insurance_provider, insurance_policy_number)


class SearchPatientTool(BaseTool):
    """Tool for searching patients in the system."""
    
    name: str = "search_patient"
    description: str = """Search for patients by name, patient ID, phone number, or email. 
    Returns list of matching patients with their details."""
    args_schema: Type[BaseModel] = SearchPatientInput
    
    def _run(self, search_query: str) -> str:
        try:
            db = load_patients_db()
            
            if not db:
                return "📭 No patients registered in the system yet."
            
            # Search in database
            search_lower = search_query.lower()
            matches = []
            
            for patient_id, patient in db.items():
                # Check if query matches any field
                if (search_lower in patient_id.lower() or
                    search_lower in patient['full_name'].lower() or
                    search_lower in patient['phone'] or
                    search_lower in patient['email'].lower()):
                    matches.append(patient)
            
            if not matches:
                return f"❌ No patients found matching '{search_query}'"
            
            # Format results
            result = f"✅ Found {len(matches)} patient(s) matching '{search_query}':\n\n"
            
            for i, patient in enumerate(matches, 1):
                result += f"""{'='*70}
Patient {i}:
   🆔 ID: {patient['patient_id']}
   👤 Name: {patient['full_name']}
   📅 DOB: {patient['date_of_birth']} (Age: {patient.get('age', 'N/A')})
   ⚧ Gender: {patient['gender']}
   🩸 Blood Group: {patient.get('blood_group', 'Not provided')}
   📞 Phone: {patient['phone']}
   📧 Email: {patient['email']}
   📅 Registered: {patient['registration_date']}
   ✅ Status: {patient['status']}

"""
            
            result += "="*70 + "\n"
            result += "💡 Use 'get_patient_details' with Patient ID for complete information."
            
            return result
        
        except Exception as e:
            return f"❌ Error searching patients: {str(e)}"
    
    async def _arun(self, search_query: str) -> str:
        return self._run(search_query)


class GetPatientDetailsTool(BaseTool):
    """Tool for getting complete patient details."""
    
    name: str = "get_patient_details"
    description: str = """Get complete patient information by patient ID. 
    Returns demographics, contact info, insurance, medical history, and appointments."""
    args_schema: Type[BaseModel] = GetPatientDetailsInput
    
    def _run(self, patient_id: str) -> str:
        try:
            db = load_patients_db()
            
            if patient_id not in db:
                return f"❌ Patient not found with ID: {patient_id}"
            
            patient = db[patient_id]
            
            # Format complete patient information
            result = f"""✅ Patient Details Retrieved

{"="*70}
PATIENT INFORMATION
{"="*70}

🆔 Patient ID: {patient['patient_id']}
👤 Name: {patient['full_name']}
📅 Date of Birth: {patient['date_of_birth']}
📊 Age: {patient.get('age', 'N/A')} years
⚧ Gender: {patient['gender']}
🩸 Blood Group: {patient.get('blood_group', 'Not provided')}

{"="*70}
CONTACT INFORMATION
{"="*70}

📞 Phone: {patient['phone']}
📧 Email: {patient['email']}
🏠 Address: {patient['address']}

{"="*70}
EMERGENCY CONTACT
{"="*70}

👤 Name: {patient.get('emergency_contact_name', 'Not provided')}
📞 Phone: {patient.get('emergency_contact_phone', 'Not provided')}

{"="*70}
INSURANCE INFORMATION
{"="*70}

🏢 Provider: {patient.get('insurance_provider', 'Not provided')}
🆔 Policy Number: {patient.get('insurance_policy_number', 'Not provided')}

{"="*70}
SYSTEM INFORMATION
{"="*70}

📅 Registration Date: {patient['registration_date']}
✅ Status: {patient['status']}

{"="*70}
MEDICAL HISTORY
{"="*70}

"""
            
            # Add medical history
            if patient.get('medical_history'):
                for i, record in enumerate(patient['medical_history'], 1):
                    result += f"{i}. {record}\n"
            else:
                result += "No medical history recorded yet.\n"
            
            result += f"\n{'='*70}\n"
            result += f"APPOINTMENTS: {len(patient.get('appointments', []))} scheduled\n"
            result += f"LAB TESTS: {len(patient.get('lab_tests', []))} tests\n"
            result += f"PRESCRIPTIONS: {len(patient.get('prescriptions', []))} active\n"
            result += f"{'='*70}\n"
            
            return result
        
        except Exception as e:
            return f"❌ Error retrieving patient details: {str(e)}"
    
    async def _arun(self, patient_id: str) -> str:
        return self._run(patient_id)


class UpdatePatientInfoTool(BaseTool):
    """Tool for updating patient information."""
    
    name: str = "update_patient_info"
    description: str = """Update patient information fields like phone, email, address, 
    emergency contacts, or insurance details. Cannot update name, DOB, or gender."""
    args_schema: Type[BaseModel] = UpdatePatientInput
    
    def _run(self, patient_id: str, field_name: str, new_value: str) -> str:
        try:
            db = load_patients_db()
            
            if patient_id not in db:
                return f"❌ Patient not found with ID: {patient_id}"
            
            # List of updatable fields
            updatable_fields = [
                'phone', 'email', 'address', 
                'emergency_contact_name', 'emergency_contact_phone',
                'insurance_provider', 'insurance_policy_number'
            ]
            
            if field_name not in updatable_fields:
                return f"""❌ Cannot update field '{field_name}'.

Updatable fields:
  • phone
  • email
  • address
  • emergency_contact_name
  • emergency_contact_phone
  • insurance_provider
  • insurance_policy_number

Note: Name, DOB, and Gender cannot be changed after registration.
"""
            
            # Get old value
            old_value = db[patient_id].get(field_name, 'Not set')
            
            # Update field
            db[patient_id][field_name] = new_value
            db[patient_id]['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Save database
            save_patients_db(db)
            
            return f"""✅ Patient Information Updated Successfully!

👤 Patient: {db[patient_id]['full_name']} ({patient_id})
📝 Field Updated: {field_name}
❌ Old Value: {old_value}
✅ New Value: {new_value}
📅 Updated: {db[patient_id]['last_updated']}

💡 Patient record has been updated in the system.
"""
        
        except Exception as e:
            return f"❌ Error updating patient info: {str(e)}"
    
    async def _arun(self, patient_id: str, field_name: str, new_value: str) -> str:
        return self._run(patient_id, field_name, new_value)


class ValidateInsuranceTool(BaseTool):
    """Tool for validating insurance information."""
    
    name: str = "validate_insurance"
    description: str = """Validate patient's insurance coverage. 
    Checks if insurance provider and policy number are valid (simulated validation)."""
    args_schema: Type[BaseModel] = ValidateInsuranceInput
    
    def _run(self, insurance_provider: str, policy_number: str, patient_name: str) -> str:
        try:
            # Simulated insurance validation
            # In production, this would connect to insurance provider API
            
            # List of known insurance providers (simulated)
            known_providers = [
                'Blue Cross Blue Shield', 'Aetna', 'Cigna', 'UnitedHealthcare',
                'Humana', 'Kaiser Permanente', 'Medicare', 'Medicaid',
                'Star Health', 'ICICI Lombard', 'HDFC ERGO', 'Max Bupa'
            ]
            
            # Check if provider is known
            provider_valid = any(provider.lower() in insurance_provider.lower() 
                               for provider in known_providers)
            
            # Validate policy number format (basic check)
            policy_valid = len(policy_number) >= 6 and any(c.isdigit() for c in policy_number)
            
            if provider_valid and policy_valid:
                # Simulated coverage details
                coverage_details = {
                    'consultation': '₹500 copay',
                    'lab_tests': '80% covered',
                    'procedures': '70% covered after deductible',
                    'medications': '₹200 copay per prescription',
                    'hospitalization': '90% covered',
                    'emergency': '100% covered'
                }
                
                result = f"""✅ Insurance Validation Successful!

{"="*70}
INSURANCE DETAILS
{"="*70}

👤 Patient Name: {patient_name}
🏢 Insurance Provider: {insurance_provider}
🆔 Policy Number: {policy_number}
✅ Status: ACTIVE & VALID

{"="*70}
COVERAGE DETAILS
{"="*70}

"""
                for service, coverage in coverage_details.items():
                    result += f"  • {service.replace('_', ' ').title()}: {coverage}\n"
                
                result += f"""
{"="*70}

💡 Note: This is a simulated validation. 
   In production, this connects to real insurance provider APIs.

✅ Patient can proceed with treatment.
   Insurance will cover eligible expenses as per policy terms.
"""
                return result
            
            else:
                issues = []
                if not provider_valid:
                    issues.append("Insurance provider not recognized")
                if not policy_valid:
                    issues.append("Invalid policy number format")
                
                return f"""❌ Insurance Validation Failed

🏢 Provider: {insurance_provider}
🆔 Policy Number: {policy_number}
👤 Patient: {patient_name}

Issues Found:
{chr(10).join(f"  ❌ {issue}" for issue in issues)}

💡 Please verify:
   1. Insurance provider name is correct
   2. Policy number is valid and active
   3. Patient name matches policy holder

Contact insurance provider for verification.
"""
        
        except Exception as e:
            return f"❌ Error validating insurance: {str(e)}"
    
    async def _arun(self, insurance_provider: str, policy_number: str, patient_name: str) -> str:
        return self._run(insurance_provider, policy_number, patient_name)


class ListAllPatientsInput(BaseModel):
    """Input for ListAllPatientsTool - no parameters needed"""
    pass


class ListAllPatientsTool(BaseTool):
    """Tool for listing all registered patients."""
    
    name: str = "list_all_patients"
    description: str = """List all registered patients in the system. 
    Shows patient ID, name, contact info, and registration date. 
    No parameters needed - just call this tool to get the full patient list."""
    args_schema: Type[BaseModel] = ListAllPatientsInput
    
    def _run(self) -> str:
        try:
            db = load_patients_db()
            
            if not db:
                return "📭 No patients registered in the system yet."
            
            result = f"""✅ Total Patients Registered: {len(db)}

{"="*70}
PATIENT LIST
{"="*70}

"""
            
            for i, (patient_id, patient) in enumerate(db.items(), 1):
                result += f"""{i}. {patient['full_name']}
   🆔 ID: {patient_id}
   📞 Phone: {patient['phone']}
   📧 Email: {patient['email']}
   📅 Registered: {patient['registration_date']}
   ✅ Status: {patient['status']}

"""
            
            result += "="*70 + "\n"
            result += "💡 Use 'get_patient_details' with Patient ID for complete information."
            
            return result
        
        except Exception as e:
            return f"❌ Error listing patients: {str(e)}"
    
    async def _arun(self) -> str:
        return self._run()


# ==================== HELPER FUNCTION ====================

def get_all_patient_registration_tools():
    """Get all patient registration tools for the agent"""
    return [
        RegisterPatientTool(),
        SearchPatientTool(),
        GetPatientDetailsTool(),
        UpdatePatientInfoTool(),
        ValidateInsuranceTool(),
        ListAllPatientsTool()
    ]


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🏥 PATIENT REGISTRATION TOOLS - Hospital Management")
    print("="*70)
    
    # Example 1: Register a new patient
    print("\n1️⃣ Registering New Patient...")
    tool1 = RegisterPatientTool()
    result1 = tool1._run(
        first_name="Samarth",
        last_name="Pawar",
        date_of_birth="2000-05-15",
        gender="Male",
        phone="+91-9876543210",
        email="samarth.pawar243@vit.edu",
        address="VIT Campus, Vellore, Tamil Nadu",
        emergency_contact_name="Parent Name",
        emergency_contact_phone="+91-9876543211",
        blood_group="O+",
        insurance_provider="Star Health",
        insurance_policy_number="SH2025001234"
    )
    print(result1)
    
    # Example 2: List all patients
    print("\n2️⃣ Listing All Patients...")
    tool2 = ListAllPatientsTool()
    result2 = tool2._run()
    print(result2)
    
    print("\n" + "="*70)
    print("✅ Patient Registration Tools Test Complete!")
    print("="*70)
