"""
Lab Management Tool for Hospital AI Agent
==========================================

This module provides comprehensive laboratory management tools:
1. Order Lab Test - Order new lab tests with doctor authorization
2. Update Test Status - Track sample collection and processing
3. Add Test Results - Record test results with reference ranges
4. Get Test Results - Retrieve patient test results
5. Generate Lab Report - Create formatted lab reports
6. Get Critical Results - Find abnormal/critical results
7. Track Sample - Track sample collection and processing
8. Get Lab Statistics - Lab performance analytics
9. Schedule Lab Appointment - Schedule sample collection
10. Get Patient Lab History - Complete lab test history

Features:
- Sample tracking with barcodes
- Reference range validation
- Critical result flagging
- Multiple test categories (Blood, Urine, Imaging, Pathology)
- Result interpretation (Normal, Abnormal, Critical)
- Doctor authorization
- Sample status tracking
- Comprehensive analytics
"""

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
import os
import random
import string

# Database file paths
LAB_TESTS_DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "lab_tests_database.json")
PATIENTS_DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "patients_database.json")

# Database helper functions
def load_db(file_path):
    """Load database from JSON file - returns list"""
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        return []
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Convert dict to list if needed
            if isinstance(data, dict):
                return list(data.values())
            return data if isinstance(data, list) else []
    except:
        return []

def save_db(file_path, data):
    """Save database to JSON file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


# Lab test categories and reference ranges
LAB_TEST_CATEGORIES = {
    "Blood": [
        "Complete Blood Count (CBC)",
        "Blood Glucose",
        "Hemoglobin A1C",
        "Lipid Profile",
        "Liver Function Test",
        "Kidney Function Test",
        "Thyroid Function Test",
        "Electrolytes Panel",
        "Blood Culture",
        "Coagulation Panel"
    ],
    "Urine": [
        "Urinalysis",
        "Urine Culture",
        "24-Hour Urine Protein",
        "Urine Pregnancy Test",
        "Drug Screening"
    ],
    "Imaging": [
        "X-Ray",
        "CT Scan",
        "MRI",
        "Ultrasound",
        "Mammogram",
        "Bone Density Scan"
    ],
    "Pathology": [
        "Biopsy",
        "Pap Smear",
        "Tissue Analysis",
        "Cytology"
    ]
}

# Reference ranges for common tests
REFERENCE_RANGES = {
    "Complete Blood Count (CBC)": {
        "WBC": {"min": 4.5, "max": 11.0, "unit": "10^9/L"},
        "RBC": {"min": 4.5, "max": 5.9, "unit": "10^12/L"},
        "Hemoglobin": {"min": 13.5, "max": 17.5, "unit": "g/dL"},
        "Platelets": {"min": 150, "max": 400, "unit": "10^9/L"}
    },
    "Blood Glucose": {
        "Fasting": {"min": 70, "max": 100, "unit": "mg/dL"},
        "Random": {"min": 70, "max": 140, "unit": "mg/dL"}
    },
    "Hemoglobin A1C": {
        "A1C": {"min": 4.0, "max": 5.6, "unit": "%"}
    },
    "Lipid Profile": {
        "Total Cholesterol": {"min": 125, "max": 200, "unit": "mg/dL"},
        "LDL": {"min": 0, "max": 100, "unit": "mg/dL"},
        "HDL": {"min": 40, "max": 60, "unit": "mg/dL"},
        "Triglycerides": {"min": 0, "max": 150, "unit": "mg/dL"}
    },
    "Liver Function Test": {
        "ALT": {"min": 7, "max": 56, "unit": "U/L"},
        "AST": {"min": 10, "max": 40, "unit": "U/L"},
        "Bilirubin": {"min": 0.1, "max": 1.2, "unit": "mg/dL"}
    },
    "Kidney Function Test": {
        "Creatinine": {"min": 0.7, "max": 1.3, "unit": "mg/dL"},
        "BUN": {"min": 7, "max": 20, "unit": "mg/dL"},
        "eGFR": {"min": 60, "max": 120, "unit": "mL/min"}
    }
}

SAMPLE_STATUS = ["Ordered", "Sample Collected", "In Transit", "Received at Lab", "Processing", "Completed", "Reported"]
RESULT_INTERPRETATION = ["Normal", "Abnormal", "Critical", "Pending"]


def generate_lab_test_id():
    """Generate unique lab test ID in format LAB{YEAR}{6-digit-random}"""
    year = datetime.now().year
    random_digits = ''.join(random.choices(string.digits, k=6))
    return f"LAB{year}{random_digits}"


def generate_sample_id():
    """Generate unique sample barcode"""
    year = datetime.now().year
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"SMPL{year}{random_chars}"


def interpret_result(test_name, parameter, value):
    """Interpret test result based on reference ranges"""
    if test_name not in REFERENCE_RANGES:
        return "Pending"
    
    if parameter not in REFERENCE_RANGES[test_name]:
        return "Pending"
    
    ref_range = REFERENCE_RANGES[test_name][parameter]
    
    try:
        value_float = float(value)
        min_val = ref_range.get("min", 0)
        max_val = ref_range.get("max", float('inf'))
        
        if value_float < min_val * 0.5 or value_float > max_val * 2:
            return "Critical"
        elif value_float < min_val or value_float > max_val:
            return "Abnormal"
        else:
            return "Normal"
    except:
        return "Pending"


# =====================================================
# TOOL 1: Order Lab Test
# =====================================================

class OrderLabTestInput(BaseModel):
    patient_id: str = Field(..., description="Patient ID")
    test_name: str = Field(..., description="Name of lab test (e.g., 'Complete Blood Count (CBC)')")
    test_category: str = Field(..., description="Category: Blood, Urine, Imaging, or Pathology")
    ordered_by: str = Field(..., description="Doctor ID who ordered the test")
    priority: str = Field(..., description="Priority: Routine, Urgent, or STAT")
    clinical_notes: Optional[str] = Field(None, description="Clinical indication or notes")

class OrderLabTestTool(BaseTool):
    name: str = "order_lab_test"
    description: str = "Order a new laboratory test with doctor authorization"
    args_schema: type[BaseModel] = OrderLabTestInput
    
    def _run(self, patient_id: str, test_name: str, test_category: str,
             ordered_by: str, priority: str, clinical_notes: Optional[str] = None) -> str:
        try:
            # Validate patient
            patients_db = load_db(PATIENTS_DB_FILE)
            patient = next((p for p in patients_db if p.get("patient_id") == patient_id), None)
            if not patient:
                return f"❌ Error: Patient ID '{patient_id}' not found."
            
            # Validate test category
            if test_category not in LAB_TEST_CATEGORIES:
                return f"❌ Error: Invalid category. Choose from: {', '.join(LAB_TEST_CATEGORIES.keys())}"
            
            # Validate test name
            if test_name not in LAB_TEST_CATEGORIES[test_category]:
                return f"❌ Error: Test '{test_name}' not found in {test_category} category.\n" \
                       f"Available tests: {', '.join(LAB_TEST_CATEGORIES[test_category])}"
            
            # Validate priority
            if priority not in ["Routine", "Urgent", "STAT"]:
                return "❌ Error: Priority must be 'Routine', 'Urgent', or 'STAT'."
            
            # Generate IDs
            test_id = generate_lab_test_id()
            sample_id = generate_sample_id()
            
            # Calculate expected completion time
            completion_hours = {"Routine": 24, "Urgent": 4, "STAT": 1}
            expected_completion = datetime.now() + timedelta(hours=completion_hours[priority])
            
            # Create lab test record
            lab_test = {
                "test_id": test_id,
                "sample_id": sample_id,
                "patient_id": patient_id,
                "patient_name": patient.get("name"),
                "test_name": test_name,
                "test_category": test_category,
                "ordered_by": ordered_by,
                "priority": priority,
                "clinical_notes": clinical_notes or "",
                "sample_status": "Ordered",
                "result_status": "Pending",
                "results": {},
                "interpretation": "Pending",
                "ordered_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "expected_completion": expected_completion.strftime("%Y-%m-%d %H:%M:%S"),
                "completed_date": None,
                "reported_date": None,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Save to database
            lab_tests_db = load_db(LAB_TESTS_DB_FILE)
            lab_tests_db.append(lab_test)
            save_db(LAB_TESTS_DB_FILE, lab_tests_db)
            
            # Format response
            result = f"✅ Lab Test Ordered Successfully!\n"
            result += f"{'=' * 50}\n\n"
            result += f"🆔 Test ID: {test_id}\n"
            result += f"🔬 Sample ID: {sample_id}\n"
            result += f"👤 Patient: {patient.get('name')} ({patient_id})\n"
            result += f"🧪 Test Name: {test_name}\n"
            result += f"📂 Category: {test_category}\n"
            result += f"👨‍⚕️ Ordered By: {ordered_by}\n"
            result += f"⚡ Priority: {priority}\n"
            result += f"📅 Ordered: {lab_test['ordered_date']}\n"
            result += f"⏰ Expected Completion: {lab_test['expected_completion']}\n"
            if clinical_notes:
                result += f"📝 Clinical Notes: {clinical_notes}\n"
            result += f"\n📊 Status: {lab_test['sample_status']}\n"
            result += f"💡 Next Step: Sample collection scheduled\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error ordering lab test: {str(e)}"


# =====================================================
# TOOL 2: Update Test Status
# =====================================================

class UpdateTestStatusInput(BaseModel):
    test_id: str = Field(..., description="Lab test ID")
    new_status: str = Field(..., description="Status: Ordered, Sample Collected, In Transit, Received at Lab, Processing, Completed, Reported")
    notes: Optional[str] = Field(None, description="Status update notes")

class UpdateTestStatusTool(BaseTool):
    name: str = "update_test_status"
    description: str = "Update the status of a lab test sample"
    args_schema: type[BaseModel] = UpdateTestStatusInput
    
    def _run(self, test_id: str, new_status: str, notes: Optional[str] = None) -> str:
        try:
            # Validate status
            if new_status not in SAMPLE_STATUS:
                return f"❌ Error: Invalid status. Choose from: {', '.join(SAMPLE_STATUS)}"
            
            # Load lab tests
            lab_tests_db = load_db(LAB_TESTS_DB_FILE)
            test = next((t for t in lab_tests_db if t.get("test_id") == test_id), None)
            
            if not test:
                return f"❌ Error: Test ID '{test_id}' not found."
            
            # Store old status
            old_status = test.get("sample_status")
            
            # Update status
            test["sample_status"] = new_status
            test["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if notes:
                if "status_history" not in test:
                    test["status_history"] = []
                test["status_history"].append({
                    "timestamp": test["updated_at"],
                    "status": new_status,
                    "notes": notes
                })
            
            # If completed, update completion date
            if new_status == "Completed":
                test["completed_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # If reported, update reported date
            if new_status == "Reported":
                test["reported_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                test["result_status"] = "Reported"
            
            save_db(LAB_TESTS_DB_FILE, lab_tests_db)
            
            # Format response
            result = f"✅ Test Status Updated Successfully!\n"
            result += f"{'=' * 50}\n\n"
            result += f"🆔 Test ID: {test_id}\n"
            result += f"🔬 Sample ID: {test.get('sample_id')}\n"
            result += f"🧪 Test: {test.get('test_name')}\n"
            result += f"👤 Patient: {test.get('patient_name')}\n\n"
            result += f"📊 Status Update:\n"
            result += f"   Old: {old_status}\n"
            result += f"   New: {new_status}\n"
            if notes:
                result += f"   Notes: {notes}\n"
            result += f"\n⏰ Updated: {test['updated_at']}\n"
            
            if new_status == "Sample Collected":
                result += f"\n💡 Next: Transport sample to lab\n"
            elif new_status == "Received at Lab":
                result += f"\n💡 Next: Begin processing\n"
            elif new_status == "Processing":
                result += f"\n💡 Next: Add test results\n"
            elif new_status == "Completed":
                result += f"\n💡 Next: Report results to doctor\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error updating status: {str(e)}"


# =====================================================
# TOOL 3: Add Test Results
# =====================================================

class AddTestResultsInput(BaseModel):
    test_id: str = Field(..., description="Lab test ID")
    results: Dict[str, Any] = Field(..., description="Dictionary of test parameters and values")
    lab_technician: str = Field(..., description="Lab technician who performed the test")
    comments: Optional[str] = Field(None, description="Lab technician comments")

class AddTestResultsTool(BaseTool):
    name: str = "add_test_results"
    description: str = "Add test results with automatic interpretation based on reference ranges"
    args_schema: type[BaseModel] = AddTestResultsInput
    
    def _run(self, test_id: str, results: Dict[str, Any], lab_technician: str,
             comments: Optional[str] = None) -> str:
        try:
            # Load lab tests
            lab_tests_db = load_db(LAB_TESTS_DB_FILE)
            test = next((t for t in lab_tests_db if t.get("test_id") == test_id), None)
            
            if not test:
                return f"❌ Error: Test ID '{test_id}' not found."
            
            # Check if sample is processed
            if test.get("sample_status") not in ["Processing", "Completed"]:
                return f"❌ Error: Sample must be in 'Processing' or 'Completed' status. Current: {test.get('sample_status')}"
            
            # Interpret results
            test_name = test.get("test_name")
            interpretations = {}
            critical_flags = []
            abnormal_flags = []
            
            for parameter, value in results.items():
                interp = interpret_result(test_name, parameter, value)
                interpretations[parameter] = interp
                
                if interp == "Critical":
                    critical_flags.append(parameter)
                elif interp == "Abnormal":
                    abnormal_flags.append(parameter)
            
            # Determine overall interpretation
            if critical_flags:
                overall_interpretation = "Critical"
            elif abnormal_flags:
                overall_interpretation = "Abnormal"
            else:
                overall_interpretation = "Normal"
            
            # Update test record
            test["results"] = results
            test["result_interpretations"] = interpretations
            test["interpretation"] = overall_interpretation
            test["result_status"] = "Completed"
            test["sample_status"] = "Completed"
            test["lab_technician"] = lab_technician
            test["lab_comments"] = comments or ""
            test["completed_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            test["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            save_db(LAB_TESTS_DB_FILE, lab_tests_db)
            
            # Format response
            result = f"✅ Test Results Added Successfully!\n"
            result += f"{'=' * 50}\n\n"
            result += f"🆔 Test ID: {test_id}\n"
            result += f"🔬 Sample ID: {test.get('sample_id')}\n"
            result += f"🧪 Test: {test_name}\n"
            result += f"👤 Patient: {test.get('patient_name')} ({test.get('patient_id')})\n"
            result += f"👨‍🔬 Lab Technician: {lab_technician}\n\n"
            
            result += f"📊 Test Results:\n"
            for parameter, value in results.items():
                interp = interpretations.get(parameter, "Pending")
                
                # Add emoji based on interpretation
                emoji = {"Normal": "✅", "Abnormal": "⚠️", "Critical": "🚨", "Pending": "⏳"}
                result += f"   {emoji.get(interp, '📊')} {parameter}: {value}"
                
                # Add reference range if available
                if test_name in REFERENCE_RANGES and parameter in REFERENCE_RANGES[test_name]:
                    ref = REFERENCE_RANGES[test_name][parameter]
                    result += f" (Ref: {ref['min']}-{ref['max']} {ref['unit']})"
                
                result += f" - {interp}\n"
            
            result += f"\n🏁 Overall Interpretation: {overall_interpretation}\n"
            
            if comments:
                result += f"💬 Lab Comments: {comments}\n"
            
            if critical_flags:
                result += f"\n🚨 CRITICAL RESULTS DETECTED!\n"
                result += f"   Parameters: {', '.join(critical_flags)}\n"
                result += f"   ⚡ Immediate doctor notification required!\n"
            elif abnormal_flags:
                result += f"\n⚠️ Abnormal results: {', '.join(abnormal_flags)}\n"
                result += f"   💡 Doctor review recommended\n"
            
            result += f"\n⏰ Completed: {test['completed_date']}\n"
            result += f"💡 Next: Generate lab report and notify doctor\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error adding test results: {str(e)}"


# =====================================================
# TOOL 4: Get Test Results
# =====================================================

class GetTestResultsInput(BaseModel):
    test_id: str = Field(..., description="Lab test ID")

class GetTestResultsTool(BaseTool):
    name: str = "get_test_results"
    description: str = "Retrieve complete test results with interpretation"
    args_schema: type[BaseModel] = GetTestResultsInput
    
    def _run(self, test_id: str) -> str:
        try:
            lab_tests_db = load_db(LAB_TESTS_DB_FILE)
            test = next((t for t in lab_tests_db if t.get("test_id") == test_id), None)
            
            if not test:
                return f"❌ Error: Test ID '{test_id}' not found."
            
            # Format response
            result = f"🔬 Lab Test Results\n"
            result += f"{'=' * 50}\n\n"
            result += f"🆔 Test ID: {test_id}\n"
            result += f"🔬 Sample ID: {test.get('sample_id')}\n"
            result += f"👤 Patient: {test.get('patient_name')} ({test.get('patient_id')})\n"
            result += f"🧪 Test Name: {test.get('test_name')}\n"
            result += f"📂 Category: {test.get('test_category')}\n"
            result += f"👨‍⚕️ Ordered By: {test.get('ordered_by')}\n"
            result += f"⚡ Priority: {test.get('priority')}\n\n"
            
            result += f"📅 Timeline:\n"
            result += f"   Ordered: {test.get('ordered_date')}\n"
            if test.get('completed_date'):
                result += f"   Completed: {test.get('completed_date')}\n"
            if test.get('reported_date'):
                result += f"   Reported: {test.get('reported_date')}\n"
            
            result += f"\n📊 Status:\n"
            result += f"   Sample: {test.get('sample_status')}\n"
            result += f"   Results: {test.get('result_status')}\n"
            
            if test.get('clinical_notes'):
                result += f"\n📝 Clinical Notes: {test.get('clinical_notes')}\n"
            
            # Show results if available
            if test.get('results'):
                result += f"\n🧪 Test Results:\n"
                interpretations = test.get('result_interpretations', {})
                
                for parameter, value in test.get('results').items():
                    interp = interpretations.get(parameter, "Pending")
                    emoji = {"Normal": "✅", "Abnormal": "⚠️", "Critical": "🚨", "Pending": "⏳"}
                    result += f"   {emoji.get(interp, '📊')} {parameter}: {value}"
                    
                    # Add reference range
                    test_name = test.get('test_name')
                    if test_name in REFERENCE_RANGES and parameter in REFERENCE_RANGES[test_name]:
                        ref = REFERENCE_RANGES[test_name][parameter]
                        result += f" (Ref: {ref['min']}-{ref['max']} {ref['unit']})"
                    
                    result += f" - {interp}\n"
                
                result += f"\n🏁 Overall: {test.get('interpretation')}\n"
                
                if test.get('lab_technician'):
                    result += f"👨‍🔬 Lab Technician: {test.get('lab_technician')}\n"
                
                if test.get('lab_comments'):
                    result += f"💬 Lab Comments: {test.get('lab_comments')}\n"
            else:
                result += f"\n⏳ Results: Pending\n"
                result += f"⏰ Expected: {test.get('expected_completion')}\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error retrieving test results: {str(e)}"


# =====================================================
# TOOL 5: Generate Lab Report
# =====================================================

class GenerateLabReportInput(BaseModel):
    test_id: str = Field(..., description="Lab test ID")

class GenerateLabReportTool(BaseTool):
    name: str = "generate_lab_report"
    description: str = "Generate a formatted lab report for completed tests"
    args_schema: type[BaseModel] = GenerateLabReportInput
    
    def _run(self, test_id: str) -> str:
        try:
            lab_tests_db = load_db(LAB_TESTS_DB_FILE)
            test = next((t for t in lab_tests_db if t.get("test_id") == test_id), None)
            
            if not test:
                return f"❌ Error: Test ID '{test_id}' not found."
            
            if not test.get('results'):
                return f"❌ Error: Test results not available yet. Status: {test.get('sample_status')}"
            
            # Update reported status
            test["sample_status"] = "Reported"
            test["result_status"] = "Reported"
            test["reported_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            test["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_db(LAB_TESTS_DB_FILE, lab_tests_db)
            
            # Generate formatted report
            report = f"\n{'=' * 60}\n"
            report += f"             LABORATORY TEST REPORT\n"
            report += f"{'=' * 60}\n\n"
            
            report += f"PATIENT INFORMATION:\n"
            report += f"  Name: {test.get('patient_name')}\n"
            report += f"  ID: {test.get('patient_id')}\n\n"
            
            report += f"TEST INFORMATION:\n"
            report += f"  Test ID: {test_id}\n"
            report += f"  Sample ID: {test.get('sample_id')}\n"
            report += f"  Test Name: {test.get('test_name')}\n"
            report += f"  Category: {test.get('test_category')}\n"
            report += f"  Priority: {test.get('priority')}\n\n"
            
            report += f"CLINICAL INFORMATION:\n"
            report += f"  Ordered By: Dr. {test.get('ordered_by')}\n"
            report += f"  Clinical Notes: {test.get('clinical_notes') or 'None'}\n\n"
            
            report += f"TIMELINE:\n"
            report += f"  Ordered: {test.get('ordered_date')}\n"
            report += f"  Completed: {test.get('completed_date')}\n"
            report += f"  Reported: {test.get('reported_date')}\n\n"
            
            report += f"{'-' * 60}\n"
            report += f"TEST RESULTS:\n"
            report += f"{'-' * 60}\n\n"
            
            test_name = test.get('test_name')
            interpretations = test.get('result_interpretations', {})
            
            report += f"{'Parameter':<25} {'Value':<15} {'Reference Range':<20} {'Status'}\n"
            report += f"{'-' * 60}\n"
            
            for parameter, value in test.get('results').items():
                interp = interpretations.get(parameter, "Pending")
                
                # Get reference range
                ref_str = ""
                if test_name in REFERENCE_RANGES and parameter in REFERENCE_RANGES[test_name]:
                    ref = REFERENCE_RANGES[test_name][parameter]
                    ref_str = f"{ref['min']}-{ref['max']} {ref['unit']}"
                
                report += f"{parameter:<25} {str(value):<15} {ref_str:<20} {interp}\n"
            
            report += f"\n{'-' * 60}\n"
            report += f"INTERPRETATION: {test.get('interpretation')}\n"
            report += f"{'-' * 60}\n\n"
            
            if test.get('lab_comments'):
                report += f"LAB COMMENTS:\n{test.get('lab_comments')}\n\n"
            
            report += f"Lab Technician: {test.get('lab_technician', 'N/A')}\n"
            report += f"Report Date: {test.get('reported_date')}\n\n"
            
            if test.get('interpretation') == "Critical":
                report += f"{'*' * 60}\n"
                report += f"⚠️  CRITICAL RESULTS - IMMEDIATE ATTENTION REQUIRED  ⚠️\n"
                report += f"{'*' * 60}\n\n"
            
            report += f"{'=' * 60}\n"
            report += f"        End of Report\n"
            report += f"{'=' * 60}\n"
            
            result = f"✅ Lab Report Generated Successfully!\n\n"
            result += report
            result += f"\n💡 Report can be sent via email using Gmail tool\n"
            result += f"📧 Doctor notification recommended for {test.get('interpretation')} results\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error generating report: {str(e)}"


# =====================================================
# TOOL 6: Get Critical Results
# =====================================================

class GetCriticalResultsInput(BaseModel):
    time_range_hours: Optional[int] = Field(24, description="Time range in hours (default 24)")

class GetCriticalResultsTool(BaseTool):
    name: str = "get_critical_results"
    description: str = "Find all critical and abnormal test results requiring immediate attention"
    args_schema: type[BaseModel] = GetCriticalResultsInput
    
    def _run(self, time_range_hours: Optional[int] = 24) -> str:
        try:
            lab_tests_db = load_db(LAB_TESTS_DB_FILE)
            
            # Filter tests with results in time range
            cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
            
            critical_tests = []
            abnormal_tests = []
            
            for test in lab_tests_db:
                if test.get('completed_date'):
                    completed = datetime.strptime(test.get('completed_date'), "%Y-%m-%d %H:%M:%S")
                    
                    if completed >= cutoff_time:
                        if test.get('interpretation') == "Critical":
                            critical_tests.append(test)
                        elif test.get('interpretation') == "Abnormal":
                            abnormal_tests.append(test)
            
            # Format response
            result = f"🚨 Critical & Abnormal Lab Results\n"
            result += f"{'=' * 50}\n\n"
            result += f"⏰ Time Range: Last {time_range_hours} hours\n"
            result += f"📊 Critical: {len(critical_tests)}\n"
            result += f"⚠️ Abnormal: {len(abnormal_tests)}\n\n"
            
            if critical_tests:
                result += f"🚨 CRITICAL RESULTS (Immediate Action Required):\n"
                result += f"{'-' * 50}\n"
                
                for test in critical_tests:
                    result += f"\n🆔 Test ID: {test.get('test_id')}\n"
                    result += f"👤 Patient: {test.get('patient_name')} ({test.get('patient_id')})\n"
                    result += f"🧪 Test: {test.get('test_name')}\n"
                    result += f"⏰ Completed: {test.get('completed_date')}\n"
                    result += f"👨‍⚕️ Ordered By: {test.get('ordered_by')}\n"
                    
                    # Show critical parameters
                    if test.get('result_interpretations'):
                        critical_params = [p for p, i in test.get('result_interpretations').items() if i == "Critical"]
                        if critical_params:
                            result += f"🚨 Critical Parameters: {', '.join(critical_params)}\n"
                    
                    result += f"{'─' * 50}\n"
            
            if abnormal_tests:
                result += f"\n⚠️ ABNORMAL RESULTS (Review Recommended):\n"
                result += f"{'-' * 50}\n"
                
                for test in abnormal_tests:
                    result += f"\n🆔 Test ID: {test.get('test_id')}\n"
                    result += f"👤 Patient: {test.get('patient_name')}\n"
                    result += f"🧪 Test: {test.get('test_name')}\n"
                    result += f"⏰ Completed: {test.get('completed_date')}\n"
                    result += f"{'─' * 50}\n"
            
            if not critical_tests and not abnormal_tests:
                result += f"✅ No critical or abnormal results in the last {time_range_hours} hours.\n"
            
            result += f"\n💡 Use 'send_critical_result_notification' to alert doctors\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error retrieving critical results: {str(e)}"


# =====================================================
# TOOL 7: Track Sample
# =====================================================

class TrackSampleInput(BaseModel):
    sample_id: str = Field(..., description="Sample barcode ID")

class TrackSampleTool(BaseTool):
    name: str = "track_sample"
    description: str = "Track the location and status of a sample"
    args_schema: type[BaseModel] = TrackSampleInput
    
    def _run(self, sample_id: str) -> str:
        try:
            lab_tests_db = load_db(LAB_TESTS_DB_FILE)
            test = next((t for t in lab_tests_db if t.get("sample_id") == sample_id), None)
            
            if not test:
                return f"❌ Error: Sample ID '{sample_id}' not found."
            
            # Format response with tracking timeline
            result = f"📦 Sample Tracking\n"
            result += f"{'=' * 50}\n\n"
            result += f"🔬 Sample ID: {sample_id}\n"
            result += f"🆔 Test ID: {test.get('test_id')}\n"
            result += f"👤 Patient: {test.get('patient_name')}\n"
            result += f"🧪 Test: {test.get('test_name')}\n"
            result += f"⚡ Priority: {test.get('priority')}\n\n"
            
            result += f"📊 Current Status: {test.get('sample_status')}\n"
            result += f"⏰ Last Updated: {test.get('updated_at')}\n\n"
            
            # Show status timeline
            result += f"📍 Tracking Timeline:\n"
            result += f"{'-' * 50}\n"
            
            status_timeline = [
                ("Ordered", test.get('ordered_date')),
                ("Sample Collected", None),
                ("In Transit", None),
                ("Received at Lab", None),
                ("Processing", None),
                ("Completed", test.get('completed_date')),
                ("Reported", test.get('reported_date'))
            ]
            
            current_status = test.get('sample_status')
            current_reached = False
            
            for status, timestamp in status_timeline:
                if status == current_status:
                    current_reached = True
                    result += f"➤ ✅ {status}"
                    if timestamp:
                        result += f" - {timestamp}"
                    result += " (CURRENT)\n"
                elif not current_reached and SAMPLE_STATUS.index(status) < SAMPLE_STATUS.index(current_status):
                    result += f"  ✅ {status}"
                    if timestamp:
                        result += f" - {timestamp}"
                    result += "\n"
                else:
                    result += f"  ⏳ {status} - Pending\n"
            
            # Show status history if available
            if test.get('status_history'):
                result += f"\n📝 Status History:\n"
                for entry in test.get('status_history'):
                    result += f"  • {entry['timestamp']} - {entry['status']}\n"
                    if entry.get('notes'):
                        result += f"    Notes: {entry['notes']}\n"
            
            # Show expected completion
            if test.get('expected_completion') and current_status not in ["Completed", "Reported"]:
                result += f"\n⏰ Expected Completion: {test.get('expected_completion')}\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error tracking sample: {str(e)}"


# =====================================================
# TOOL 8: Get Lab Statistics
# =====================================================

class GetLabStatisticsInput(BaseModel):
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")

class GetLabStatisticsTool(BaseTool):
    name: str = "get_lab_statistics"
    description: str = "Generate comprehensive lab performance analytics"
    args_schema: type[BaseModel] = GetLabStatisticsInput
    
    def _run(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
        try:
            lab_tests_db = load_db(LAB_TESTS_DB_FILE)
            
            if not lab_tests_db:
                return "📊 No lab tests in database."
            
            # Filter by date range
            filtered_tests = lab_tests_db
            
            if start_date:
                filtered_tests = [t for t in filtered_tests 
                                 if t.get('ordered_date', '').split()[0] >= start_date]
            
            if end_date:
                filtered_tests = [t for t in filtered_tests 
                                 if t.get('ordered_date', '').split()[0] <= end_date]
            
            total = len(filtered_tests)
            
            # Calculate statistics
            category_counts = {}
            status_counts = {}
            priority_counts = {}
            interpretation_counts = {}
            
            for test in filtered_tests:
                # Category
                cat = test.get('test_category', 'Unknown')
                category_counts[cat] = category_counts.get(cat, 0) + 1
                
                # Status
                status = test.get('sample_status', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
                
                # Priority
                priority = test.get('priority', 'Unknown')
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
                
                # Interpretation
                interp = test.get('interpretation', 'Pending')
                interpretation_counts[interp] = interpretation_counts.get(interp, 0) + 1
            
            # Calculate turnaround times
            completed_tests = [t for t in filtered_tests if t.get('completed_date')]
            turnaround_times = []
            
            for test in completed_tests:
                try:
                    ordered = datetime.strptime(test.get('ordered_date'), "%Y-%m-%d %H:%M:%S")
                    completed = datetime.strptime(test.get('completed_date'), "%Y-%m-%d %H:%M:%S")
                    turnaround_hours = (completed - ordered).total_seconds() / 3600
                    turnaround_times.append(turnaround_hours)
                except:
                    pass
            
            # Format response
            result = f"📊 Lab Statistics Dashboard\n"
            result += f"{'=' * 50}\n\n"
            
            if start_date or end_date:
                result += f"📅 Date Range: "
                if start_date:
                    result += f"From {start_date} "
                if end_date:
                    result += f"To {end_date}"
                result += "\n\n"
            
            result += f"📈 Total Tests: {total}\n"
            result += f"✅ Completed: {len(completed_tests)}\n"
            result += f"⏳ Pending: {total - len(completed_tests)}\n\n"
            
            # By Category
            result += f"📂 By Category:\n"
            for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total * 100) if total > 0 else 0
                result += f"   {cat}: {count} ({percentage:.1f}%)\n"
            
            # By Status
            result += f"\n📊 By Status:\n"
            for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total * 100) if total > 0 else 0
                result += f"   {status}: {count} ({percentage:.1f}%)\n"
            
            # By Priority
            result += f"\n⚡ By Priority:\n"
            for priority, count in sorted(priority_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total * 100) if total > 0 else 0
                result += f"   {priority}: {count} ({percentage:.1f}%)\n"
            
            # By Interpretation
            result += f"\n🏁 By Result Interpretation:\n"
            for interp, count in sorted(interpretation_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total * 100) if total > 0 else 0
                emoji = {"Normal": "✅", "Abnormal": "⚠️", "Critical": "🚨", "Pending": "⏳"}
                result += f"   {emoji.get(interp, '📊')} {interp}: {count} ({percentage:.1f}%)\n"
            
            # Turnaround Time
            if turnaround_times:
                avg_turnaround = sum(turnaround_times) / len(turnaround_times)
                result += f"\n⏱️  Average Turnaround Time: {avg_turnaround:.1f} hours\n"
                result += f"   Fastest: {min(turnaround_times):.1f} hours\n"
                result += f"   Slowest: {max(turnaround_times):.1f} hours\n"
            
            # Insights
            result += f"\n💡 Insights:\n"
            
            if category_counts:
                most_common_category = max(category_counts.items(), key=lambda x: x[1])
                result += f"   • Most common test category: {most_common_category[0]} ({most_common_category[1]} tests)\n"
            
            critical_count = interpretation_counts.get("Critical", 0)
            abnormal_count = interpretation_counts.get("Abnormal", 0)
            if critical_count > 0:
                result += f"   • 🚨 {critical_count} critical results requiring immediate attention\n"
            if abnormal_count > 0:
                result += f"   • ⚠️ {abnormal_count} abnormal results requiring review\n"
            
            pending_completion = status_counts.get("Processing", 0) + status_counts.get("Received at Lab", 0)
            if pending_completion > 0:
                result += f"   • ⏳ {pending_completion} tests currently in progress\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error generating statistics: {str(e)}"


# =====================================================
# TOOL 9: Schedule Lab Appointment
# =====================================================

class ScheduleLabAppointmentInput(BaseModel):
    patient_id: str = Field(..., description="Patient ID")
    test_id: str = Field(..., description="Lab test ID")
    appointment_date: str = Field(..., description="Appointment date (YYYY-MM-DD)")
    appointment_time: str = Field(..., description="Appointment time (HH:MM)")
    location: str = Field(..., description="Collection location (e.g., 'Lab Room 1', 'Patient Home')")

class ScheduleLabAppointmentTool(BaseTool):
    name: str = "schedule_lab_appointment"
    description: str = "Schedule sample collection appointment for lab test"
    args_schema: type[BaseModel] = ScheduleLabAppointmentInput
    
    def _run(self, patient_id: str, test_id: str, appointment_date: str,
             appointment_time: str, location: str) -> str:
        try:
            # Validate test
            lab_tests_db = load_db(LAB_TESTS_DB_FILE)
            test = next((t for t in lab_tests_db if t.get("test_id") == test_id), None)
            
            if not test:
                return f"❌ Error: Test ID '{test_id}' not found."
            
            if test.get('patient_id') != patient_id:
                return f"❌ Error: Test belongs to different patient."
            
            # Validate date and time
            try:
                appt_datetime = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M")
                if appt_datetime < datetime.now():
                    return "❌ Error: Cannot schedule appointment in the past."
            except ValueError:
                return "❌ Error: Invalid date/time format."
            
            # Update test with appointment info
            test['collection_appointment'] = {
                'date': appointment_date,
                'time': appointment_time,
                'location': location,
                'scheduled_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            test['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            save_db(LAB_TESTS_DB_FILE, lab_tests_db)
            
            # Format response
            result = f"✅ Lab Appointment Scheduled!\n"
            result += f"{'=' * 50}\n\n"
            result += f"🆔 Test ID: {test_id}\n"
            result += f"🔬 Sample ID: {test.get('sample_id')}\n"
            result += f"👤 Patient: {test.get('patient_name')} ({patient_id})\n"
            result += f"🧪 Test: {test.get('test_name')}\n"
            result += f"⚡ Priority: {test.get('priority')}\n\n"
            result += f"📅 Appointment Details:\n"
            result += f"   Date: {appointment_date}\n"
            result += f"   Time: {appointment_time}\n"
            result += f"   Location: {location}\n\n"
            result += f"💡 Next Steps:\n"
            result += f"   1. Send appointment confirmation email to patient\n"
            result += f"   2. Prepare sample collection materials\n"
            result += f"   3. Update status to 'Sample Collected' after collection\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error scheduling appointment: {str(e)}"


# =====================================================
# TOOL 10: Get Patient Lab History
# =====================================================

class GetPatientLabHistoryInput(BaseModel):
    patient_id: str = Field(..., description="Patient ID")
    test_category: Optional[str] = Field(None, description="Filter by category (optional)")

class GetPatientLabHistoryTool(BaseTool):
    name: str = "get_patient_lab_history"
    description: str = "Get complete lab test history for a patient"
    args_schema: type[BaseModel] = GetPatientLabHistoryInput
    
    def _run(self, patient_id: str, test_category: Optional[str] = None) -> str:
        try:
            # Validate patient
            patients_db = load_db(PATIENTS_DB_FILE)
            patient = next((p for p in patients_db if p.get("patient_id") == patient_id), None)
            if not patient:
                return f"❌ Error: Patient ID '{patient_id}' not found."
            
            # Load lab tests
            lab_tests_db = load_db(LAB_TESTS_DB_FILE)
            patient_tests = [t for t in lab_tests_db if t.get('patient_id') == patient_id]
            
            if test_category:
                patient_tests = [t for t in patient_tests if t.get('test_category') == test_category]
            
            if not patient_tests:
                msg = f"📋 No lab tests found for {patient.get('name')}"
                if test_category:
                    msg += f" in category '{test_category}'"
                return msg + "."
            
            # Sort by date
            patient_tests.sort(key=lambda x: x.get('ordered_date', ''), reverse=True)
            
            # Format response
            result = f"🔬 Lab Test History for {patient.get('name')}\n"
            result += f"{'=' * 50}\n\n"
            result += f"👤 Patient: {patient.get('name')} ({patient_id})\n"
            if test_category:
                result += f"🔍 Filter: {test_category}\n"
            result += f"📊 Total Tests: {len(patient_tests)}\n\n"
            
            # Group by category
            category_groups = {}
            for test in patient_tests:
                cat = test.get('test_category', 'Unknown')
                if cat not in category_groups:
                    category_groups[cat] = []
                category_groups[cat].append(test)
            
            for category, tests in category_groups.items():
                result += f"📂 {category} ({len(tests)} tests):\n"
                result += f"{'-' * 50}\n"
                
                for test in tests:
                    status_emoji = {
                        "Normal": "✅",
                        "Abnormal": "⚠️",
                        "Critical": "🚨",
                        "Pending": "⏳"
                    }
                    
                    interp = test.get('interpretation', 'Pending')
                    emoji = status_emoji.get(interp, '📊')
                    
                    result += f"\n{emoji} {test.get('test_name')}\n"
                    result += f"   🆔 Test ID: {test.get('test_id')}\n"
                    result += f"   📅 Ordered: {test.get('ordered_date')}\n"
                    result += f"   📊 Status: {test.get('sample_status')}\n"
                    result += f"   🏁 Result: {interp}\n"
                    
                    if test.get('completed_date'):
                        result += f"   ✅ Completed: {test.get('completed_date')}\n"
                    
                    if test.get('priority') in ["Urgent", "STAT"]:
                        result += f"   ⚡ Priority: {test.get('priority')}\n"
                
                result += "\n"
            
            # Summary statistics
            completed = len([t for t in patient_tests if t.get('completed_date')])
            critical = len([t for t in patient_tests if t.get('interpretation') == 'Critical'])
            abnormal = len([t for t in patient_tests if t.get('interpretation') == 'Abnormal'])
            
            result += f"📈 Summary:\n"
            result += f"   Completed: {completed}/{len(patient_tests)}\n"
            if critical > 0:
                result += f"   🚨 Critical Results: {critical}\n"
            if abnormal > 0:
                result += f"   ⚠️ Abnormal Results: {abnormal}\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error retrieving lab history: {str(e)}"


# =====================================================
# Helper Function: Get All Tools
# =====================================================

def get_all_lab_tools():
    """Returns list of all lab management tools"""
    return [
        OrderLabTestTool(),
        UpdateTestStatusTool(),
        AddTestResultsTool(),
        GetTestResultsTool(),
        GenerateLabReportTool(),
        GetCriticalResultsTool(),
        TrackSampleTool(),
        GetLabStatisticsTool(),
        ScheduleLabAppointmentTool(),
        GetPatientLabHistoryTool()
    ]


# =====================================================
# Usage Example
# =====================================================

if __name__ == "__main__":
    print("🔬 LAB MANAGEMENT TOOL - DEMO")
    print("=" * 60)
    
    # Get all tools
    tools = get_all_lab_tools()
    
    print(f"\n✅ Loaded {len(tools)} Lab Management Tools:\n")
    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool.name}")
    
    print("\n" + "=" * 60)
    print("✅ LAB MANAGEMENT TOOLS READY!")
    print("=" * 60)
