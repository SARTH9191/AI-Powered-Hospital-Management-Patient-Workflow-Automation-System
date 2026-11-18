"""
Medical Data Handler - Handles medical history data processing and serialization
Prevents data type issues and ensures proper JSON serialization
"""

import json
from typing import Dict, List, Any, Union
from datetime import datetime

class MedicalDataHandler:
    """Handle medical data processing, parsing, and serialization"""
    
    def __init__(self):
        self.data = {}
    
    def process_medical_conditions(self, conditions_text: str) -> Dict[str, Any]:
        """Process medical conditions and return structured data"""
        try:
            # Ensure all values are strings for JSON serialization
            processed_data = {
                "raw_input": str(conditions_text),
                "conditions_list": [],
                "professional_summary": "",
                "severity_assessment": "",
                "follow_up_needed": False,
                "processed_at": datetime.now().isoformat()
            }
            
            # Basic parsing logic (can be enhanced with LLM)
            if conditions_text.lower() in ['none', 'no', 'nothing']:
                processed_data["professional_summary"] = "No significant past medical history reported"
                processed_data["conditions_list"] = []
            else:
                # Split and clean conditions
                conditions = [cond.strip() for cond in conditions_text.replace(',', ';').split(';') if cond.strip()]
                processed_data["conditions_list"] = conditions
                processed_data["professional_summary"] = f"Patient reports: {', '.join(conditions)}"
                processed_data["follow_up_needed"] = len(conditions) > 0
            
            return processed_data
            
        except Exception as e:
            return {
                "raw_input": str(conditions_text),
                "conditions_list": [],
                "professional_summary": "Error processing medical conditions",
                "error": str(e),
                "processed_at": datetime.now().isoformat()
            }
    
    def process_allergies(self, allergies_text: str) -> Dict[str, Any]:
        """Process allergies and return structured data"""
        try:
            processed_data = {
                "raw_input": str(allergies_text),
                "allergies_list": [],
                "professional_summary": "",
                "severity_flags": [],
                "safety_alerts": [],
                "processed_at": datetime.now().isoformat()
            }
            
            if allergies_text.lower() in ['none', 'no', 'nothing']:
                processed_data["professional_summary"] = "No known drug allergies (NKDA) reported"
                processed_data["allergies_list"] = []
            else:
                # Split and process allergies
                allergies = [allergy.strip() for allergy in allergies_text.replace(',', ';').split(';') if allergy.strip()]
                processed_data["allergies_list"] = allergies
                processed_data["professional_summary"] = f"Known allergies: {', '.join(allergies)}"
                
                # Generate safety alerts for common drug allergies
                for allergy in allergies:
                    if 'penicillin' in allergy.lower():
                        processed_data["safety_alerts"].append("⚠️ PENICILLIN ALLERGY: Avoid all beta-lactam antibiotics")
                        processed_data["severity_flags"].append("High")
            
            return processed_data
            
        except Exception as e:
            return {
                "raw_input": str(allergies_text),
                "allergies_list": [],
                "professional_summary": "Error processing allergies",
                "error": str(e),
                "processed_at": datetime.now().isoformat()
            }
    
    def process_medications(self, medications_text: str) -> Dict[str, Any]:
        """Process current medications and return structured data"""
        try:
            processed_data = {
                "raw_input": str(medications_text),
                "medications_list": [],
                "professional_summary": "",
                "interaction_warnings": [],
                "compliance_notes": [],
                "processed_at": datetime.now().isoformat()
            }
            
            if medications_text.lower() in ['none', 'no', 'nothing']:
                processed_data["professional_summary"] = "Patient reports no current medications"
                processed_data["medications_list"] = []
            else:
                # Split and process medications
                medications = [med.strip() for med in medications_text.replace(',', ';').split(';') if med.strip()]
                processed_data["medications_list"] = medications
                processed_data["professional_summary"] = f"Current medications: {', '.join(medications)}"
            
            return processed_data
            
        except Exception as e:
            return {
                "raw_input": str(medications_text),
                "medications_list": [],
                "professional_summary": "Error processing medications",
                "error": str(e),
                "processed_at": datetime.now().isoformat()
            }
    
    def process_chief_complaint(self, complaint_text: str) -> Dict[str, Any]:
        """Process chief complaint and return structured data"""
        try:
            processed_data = {
                "raw_input": str(complaint_text),
                "primary_symptoms": [],
                "duration": "",
                "severity": "",
                "professional_summary": "",
                "urgency_level": "routine",
                "processed_at": datetime.now().isoformat()
            }
            
            # Basic symptom extraction
            complaint_lower = complaint_text.lower()
            
            # Check for urgent symptoms
            urgent_keywords = ['chest pain', 'shortness of breath', 'difficulty breathing', 'severe pain']
            if any(keyword in complaint_lower for keyword in urgent_keywords):
                processed_data["urgency_level"] = "urgent"
            
            processed_data["professional_summary"] = f"Chief complaint: {complaint_text}"
            processed_data["primary_symptoms"] = [complaint_text]  # Simplified for now
            
            return processed_data
            
        except Exception as e:
            return {
                "raw_input": str(complaint_text),
                "professional_summary": "Error processing chief complaint",
                "error": str(e),
                "processed_at": datetime.now().isoformat()
            }
    
    def ensure_string_serialization(self, data: Any) -> Any:
        """Ensure all data can be JSON serialized as strings"""
        if isinstance(data, dict):
            return {key: self.ensure_string_serialization(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [str(item) for item in data]  # Convert all list items to strings
        elif data is None:
            return ""
        else:
            return str(data)
    
    def safe_join(self, items: List[Any], separator: str = "\n") -> str:
        """Safely join items, converting all to strings first"""
        try:
            # Convert all items to strings
            string_items = [str(item) for item in items if item is not None]
            return separator.join(string_items)
        except Exception as e:
            return f"Error joining items: {str(e)}"
    
    def validate_medical_data(self, stage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean medical data for serialization"""
        try:
            cleaned_data = {}
            
            for key, value in stage_data.items():
                if isinstance(value, dict):
                    # Ensure nested dictionaries are clean
                    cleaned_data[key] = self.ensure_string_serialization(value)
                elif isinstance(value, list):
                    # Convert lists to strings
                    cleaned_data[key] = [str(item) for item in value]
                else:
                    cleaned_data[key] = str(value) if value is not None else ""
            
            return cleaned_data
            
        except Exception as e:
            print(f"Error validating medical data: {e}")
            return stage_data

# Utility functions for use in workflow
def safe_medical_join(items: List[Any], separator: str = "\n") -> str:
    """Utility function for safe joining in workflow"""
    handler = MedicalDataHandler()
    return handler.safe_join(items, separator)

def process_medical_input(input_type: str, text: str) -> Dict[str, Any]:
    """Process medical input based on type"""
    handler = MedicalDataHandler()
    
    if input_type == "conditions":
        return handler.process_medical_conditions(text)
    elif input_type == "allergies":
        return handler.process_allergies(text)
    elif input_type == "medications":
        return handler.process_medications(text)
    elif input_type == "chief_complaint":
        return handler.process_chief_complaint(text)
    else:
        return {"error": f"Unknown input type: {input_type}"}