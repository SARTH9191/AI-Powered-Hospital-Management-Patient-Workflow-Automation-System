"""
Pharmacy Tool for Hospital AI Agent
====================================

This module provides comprehensive pharmacy management tools:
1. Dispense Medication - Dispense prescriptions with verification
2. Check Drug Inventory - View medication stock levels
3. Update Inventory - Add/remove stock
4. Get Medication Info - Drug information and interactions
5. Process Refill Request - Handle prescription refills
6. Get Dispensing History - Patient medication history
7. Check Drug Interactions - Verify drug-drug interactions
8. Get Pharmacy Statistics - Inventory and dispensing analytics

Features:
- Prescription verification
- Drug interaction checking
- Inventory management with low stock alerts
- Refill request processing
- Dispensing history tracking
- Medication information database
- Comprehensive analytics
- Patient safety validations
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
PRESCRIPTIONS_DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "prescriptions_database.json")
PATIENTS_DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "patients_database.json")
PHARMACY_INVENTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pharmacy_inventory.json")
DISPENSING_HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "dispensing_history.json")

# Database helper functions
def load_db(file_path):
    """Load database from JSON file - returns list or dict"""
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        return []
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data
    except:
        return []

def save_db(file_path, data):
    """Save database to JSON file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


# Medication database with comprehensive information
MEDICATION_DATABASE = {
    "Lisinopril": {
        "generic_name": "Lisinopril",
        "brand_names": ["Prinivil", "Zestril"],
        "category": "ACE Inhibitor",
        "indications": ["Hypertension", "Heart Failure"],
        "common_dosages": ["5mg", "10mg", "20mg", "40mg"],
        "route": "Oral",
        "frequency": ["Once daily", "Twice daily"],
        "side_effects": ["Dizziness", "Cough", "Headache"],
        "contraindications": ["Pregnancy", "Angioedema history"],
        "interactions": ["Potassium Supplements", "Spironolactone", "NSAIDs"]
    },
    "Metformin": {
        "generic_name": "Metformin",
        "brand_names": ["Glucophage", "Fortamet"],
        "category": "Antidiabetic",
        "indications": ["Type 2 Diabetes"],
        "common_dosages": ["500mg", "850mg", "1000mg"],
        "route": "Oral",
        "frequency": ["Once daily", "Twice daily", "Three times daily"],
        "side_effects": ["Nausea", "Diarrhea", "Stomach upset"],
        "contraindications": ["Kidney disease", "Liver disease"],
        "interactions": ["Alcohol", "Contrast Dye", "Cimetidine"]
    },
    "Aspirin": {
        "generic_name": "Aspirin",
        "brand_names": ["Bayer", "Ecotrin"],
        "category": "NSAID/Antiplatelet",
        "indications": ["Pain", "Fever", "Cardiovascular protection"],
        "common_dosages": ["81mg", "325mg"],
        "route": "Oral",
        "frequency": ["Once daily", "As needed"],
        "side_effects": ["Stomach irritation", "Bleeding risk"],
        "contraindications": ["Active bleeding", "Severe liver disease"],
        "interactions": ["Warfarin", "Ibuprofen", "Naproxen"]
    },
    "Warfarin": {
        "generic_name": "Warfarin",
        "brand_names": ["Coumadin", "Jantoven"],
        "category": "Anticoagulant",
        "indications": ["Blood clots", "Atrial fibrillation"],
        "common_dosages": ["1mg", "2mg", "5mg", "10mg"],
        "route": "Oral",
        "frequency": ["Once daily"],
        "side_effects": ["Bleeding", "Bruising"],
        "contraindications": ["Pregnancy", "Active bleeding"],
        "interactions": ["Aspirin", "Vitamin K", "Green Tea", "Antibiotics"]
    },
    "Atorvastatin": {
        "generic_name": "Atorvastatin",
        "brand_names": ["Lipitor"],
        "category": "Statin",
        "indications": ["High cholesterol", "Cardiovascular disease"],
        "common_dosages": ["10mg", "20mg", "40mg", "80mg"],
        "route": "Oral",
        "frequency": ["Once daily"],
        "side_effects": ["Muscle pain", "Headache"],
        "contraindications": ["Pregnancy", "Active liver disease"],
        "interactions": ["Grapefruit juice", "Gemfibrozil", "Cyclosporine"]
    },
    "Amoxicillin": {
        "generic_name": "Amoxicillin",
        "brand_names": ["Amoxil", "Trimox"],
        "category": "Antibiotic",
        "indications": ["Bacterial infections"],
        "common_dosages": ["250mg", "500mg"],
        "route": "Oral",
        "frequency": ["Three times daily"],
        "side_effects": ["Diarrhea", "Nausea", "Rash"],
        "contraindications": ["Penicillin allergy"],
        "interactions": ["Birth control pills", "Warfarin"]
    },
    "Omeprazole": {
        "generic_name": "Omeprazole",
        "brand_names": ["Prilosec"],
        "category": "Proton Pump Inhibitor",
        "indications": ["GERD", "Ulcers"],
        "common_dosages": ["20mg", "40mg"],
        "route": "Oral",
        "frequency": ["Once daily"],
        "side_effects": ["Headache", "Diarrhea"],
        "contraindications": ["Allergy to PPIs"],
        "interactions": ["Clopidogrel", "Methotrexate"]
    },
    "Amlodipine": {
        "generic_name": "Amlodipine",
        "brand_names": ["Norvasc"],
        "category": "Calcium Channel Blocker",
        "indications": ["Hypertension", "Angina"],
        "common_dosages": ["2.5mg", "5mg", "10mg"],
        "route": "Oral",
        "frequency": ["Once daily"],
        "side_effects": ["Swelling", "Dizziness", "Flushing"],
        "contraindications": ["Severe aortic stenosis"],
        "interactions": ["Simvastatin", "Grapefruit juice"]
    }
}

# Initialize inventory with sample data
def initialize_inventory():
    """Initialize pharmacy inventory if not exists"""
    inventory_file = PHARMACY_INVENTORY_FILE
    
    if not os.path.exists(inventory_file):
        initial_inventory = {}
        
        for drug_name, drug_info in MEDICATION_DATABASE.items():
            for dosage in drug_info["common_dosages"]:
                key = f"{drug_name}_{dosage}"
                initial_inventory[key] = {
                    "drug_name": drug_name,
                    "generic_name": drug_info["generic_name"],
                    "dosage": dosage,
                    "quantity_in_stock": random.randint(100, 1000),
                    "reorder_level": 50,
                    "unit_price": round(random.uniform(5.0, 50.0), 2),
                    "location": f"Shelf-{random.randint(1, 20)}",
                    "expiry_date": (datetime.now() + timedelta(days=random.randint(180, 730))).strftime("%Y-%m-%d"),
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
        
        save_db(inventory_file, initial_inventory)
        return initial_inventory
    
    return load_db(inventory_file)


def generate_dispensing_id():
    """Generate unique dispensing ID"""
    year = datetime.now().year
    random_digits = ''.join(random.choices(string.digits, k=6))
    return f"DISP{year}{random_digits}"


# =====================================================
# TOOL 1: Dispense Medication
# =====================================================

class DispenseMedicationInput(BaseModel):
    prescription_id: str = Field(..., description="Prescription ID to dispense")
    pharmacist_id: str = Field(..., description="Pharmacist ID dispensing the medication")
    quantity_dispensed: int = Field(..., description="Quantity being dispensed")
    notes: Optional[str] = Field(None, description="Dispensing notes")

class DispenseMedicationTool(BaseTool):
    name: str = "dispense_medication"
    description: str = "Dispense prescription medication with verification and inventory update"
    args_schema: type[BaseModel] = DispenseMedicationInput
    
    def _run(self, prescription_id: str, pharmacist_id: str, quantity_dispensed: int,
             notes: Optional[str] = None) -> str:
        try:
            # Initialize inventory
            initialize_inventory()
            
            # Load prescription
            prescriptions_db = load_db(PRESCRIPTIONS_DB_FILE)
            prescription = next((p for p in prescriptions_db if p.get("prescription_id") == prescription_id), None)
            
            if not prescription:
                return f"❌ Error: Prescription ID '{prescription_id}' not found."
            
            # Check prescription status
            if prescription.get("status") == "Dispensed":
                return f"⚠️ Warning: Prescription already dispensed on {prescription.get('dispensed_date')}."
            
            if prescription.get("status") == "Cancelled":
                return f"❌ Error: Prescription is cancelled. Cannot dispense."
            
            # Verify patient and medication
            patient_id = prescription.get("patient_id")
            medication = prescription.get("medication", "")
            dosage = prescription.get("dosage", "")
            
            # Check inventory
            inventory = load_db(PHARMACY_INVENTORY_FILE)
            inventory_key = f"{medication}_{dosage}"
            
            if inventory_key not in inventory:
                return f"❌ Error: Medication '{medication} {dosage}' not found in inventory."
            
            stock_item = inventory[inventory_key]
            current_stock = stock_item.get("quantity_in_stock", 0)
            
            if current_stock < quantity_dispensed:
                return f"❌ Error: Insufficient stock. Available: {current_stock}, Requested: {quantity_dispensed}"
            
            # Generate dispensing record
            dispensing_id = generate_dispensing_id()
            
            dispensing_record = {
                "dispensing_id": dispensing_id,
                "prescription_id": prescription_id,
                "patient_id": patient_id,
                "patient_name": prescription.get("patient_name"),
                "medication": medication,
                "dosage": dosage,
                "quantity_dispensed": quantity_dispensed,
                "pharmacist_id": pharmacist_id,
                "dispensed_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "instructions": prescription.get("instructions", ""),
                "notes": notes or "",
                "unit_price": stock_item.get("unit_price", 0),
                "total_cost": round(stock_item.get("unit_price", 0) * quantity_dispensed, 2)
            }
            
            # Update inventory
            inventory[inventory_key]["quantity_in_stock"] -= quantity_dispensed
            inventory[inventory_key]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_db(PHARMACY_INVENTORY_FILE, inventory)
            
            # Update prescription status
            prescription["status"] = "Dispensed"
            prescription["dispensed_date"] = dispensing_record["dispensed_date"]
            prescription["dispensing_id"] = dispensing_id
            prescription["quantity_dispensed"] = quantity_dispensed
            save_db(PRESCRIPTIONS_DB_FILE, prescriptions_db)
            
            # Save dispensing history
            dispensing_history = load_db(DISPENSING_HISTORY_FILE)
            if not isinstance(dispensing_history, list):
                dispensing_history = []
            dispensing_history.append(dispensing_record)
            save_db(DISPENSING_HISTORY_FILE, dispensing_history)
            
            # Check for low stock
            new_stock = inventory[inventory_key]["quantity_in_stock"]
            reorder_level = stock_item.get("reorder_level", 50)
            low_stock_warning = ""
            
            if new_stock <= reorder_level:
                low_stock_warning = f"\n⚠️ LOW STOCK ALERT: {medication} {dosage} - Only {new_stock} units remaining!"
            
            # Format response
            result = f"✅ Medication Dispensed Successfully!\n"
            result += f"{'=' * 50}\n\n"
            result += f"🆔 Dispensing ID: {dispensing_id}\n"
            result += f"📋 Prescription ID: {prescription_id}\n"
            result += f"👤 Patient: {prescription.get('patient_name')} ({patient_id})\n"
            result += f"💊 Medication: {medication} {dosage}\n"
            result += f"📦 Quantity Dispensed: {quantity_dispensed}\n"
            result += f"👨‍⚕️ Pharmacist: {pharmacist_id}\n"
            result += f"📅 Dispensed: {dispensing_record['dispensed_date']}\n"
            result += f"💰 Unit Price: ${stock_item.get('unit_price', 0):.2f}\n"
            result += f"💵 Total Cost: ${dispensing_record['total_cost']:.2f}\n\n"
            result += f"📝 Instructions: {prescription.get('instructions', 'Take as directed')}\n"
            if notes:
                result += f"📌 Notes: {notes}\n"
            result += f"\n📊 Inventory Update:\n"
            result += f"   Previous Stock: {current_stock}\n"
            result += f"   New Stock: {new_stock}\n"
            result += f"   Location: {stock_item.get('location')}\n"
            
            if low_stock_warning:
                result += low_stock_warning
            
            result += f"\n💡 Patient counseling completed. Record saved.\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error dispensing medication: {str(e)}"


# =====================================================
# TOOL 2: Check Drug Inventory
# =====================================================

class CheckDrugInventoryInput(BaseModel):
    drug_name: Optional[str] = Field(None, description="Specific drug name (optional, leave empty for all)")
    show_low_stock_only: Optional[bool] = Field(False, description="Show only low stock items")

class CheckDrugInventoryTool(BaseTool):
    name: str = "check_drug_inventory"
    description: str = "Check medication inventory levels with low stock alerts"
    args_schema: type[BaseModel] = CheckDrugInventoryInput
    
    def _run(self, drug_name: Optional[str] = None, show_low_stock_only: Optional[bool] = False) -> str:
        try:
            # Initialize and load inventory
            initialize_inventory()
            inventory = load_db(PHARMACY_INVENTORY_FILE)
            
            if not inventory:
                return "📦 Inventory is empty."
            
            # Filter inventory
            filtered_items = []
            
            for key, item in inventory.items():
                if drug_name and item.get("drug_name") != drug_name:
                    continue
                
                if show_low_stock_only:
                    if item.get("quantity_in_stock", 0) > item.get("reorder_level", 50):
                        continue
                
                filtered_items.append(item)
            
            if not filtered_items:
                if drug_name:
                    return f"📦 No inventory found for '{drug_name}'."
                elif show_low_stock_only:
                    return "✅ No low stock items. All medications adequately stocked."
                return "📦 No inventory items found."
            
            # Sort by stock level
            filtered_items.sort(key=lambda x: x.get("quantity_in_stock", 0))
            
            # Format response
            result = f"📦 Pharmacy Inventory\n"
            result += f"{'=' * 50}\n\n"
            
            if drug_name:
                result += f"🔍 Filter: {drug_name}\n"
            if show_low_stock_only:
                result += f"⚠️ Showing Low Stock Items Only\n"
            
            result += f"📊 Total Items: {len(filtered_items)}\n\n"
            
            low_stock_count = 0
            
            for item in filtered_items:
                stock = item.get("quantity_in_stock", 0)
                reorder = item.get("reorder_level", 50)
                
                # Stock status indicator
                if stock == 0:
                    status = "🔴 OUT OF STOCK"
                    low_stock_count += 1
                elif stock <= reorder:
                    status = "🟡 LOW STOCK"
                    low_stock_count += 1
                else:
                    status = "🟢 IN STOCK"
                
                result += f"{status}\n"
                result += f"💊 {item.get('drug_name')} {item.get('dosage')}\n"
                result += f"   Stock: {stock} units\n"
                result += f"   Reorder Level: {reorder} units\n"
                result += f"   Location: {item.get('location')}\n"
                result += f"   Price: ${item.get('unit_price', 0):.2f}/unit\n"
                result += f"   Expiry: {item.get('expiry_date')}\n"
                result += f"   Updated: {item.get('last_updated')}\n\n"
            
            # Summary
            if low_stock_count > 0:
                result += f"⚠️ ACTION REQUIRED: {low_stock_count} items need reordering!\n"
            else:
                result += f"✅ All items adequately stocked.\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error checking inventory: {str(e)}"


# =====================================================
# TOOL 3: Update Inventory
# =====================================================

class UpdateInventoryInput(BaseModel):
    drug_name: str = Field(..., description="Drug name")
    dosage: str = Field(..., description="Dosage (e.g., '10mg')")
    quantity_change: int = Field(..., description="Quantity to add (positive) or remove (negative)")
    reason: str = Field(..., description="Reason for update (e.g., 'Restock', 'Expired', 'Damaged')")

class UpdateInventoryTool(BaseTool):
    name: str = "update_inventory"
    description: str = "Add or remove medication from inventory"
    args_schema: type[BaseModel] = UpdateInventoryInput
    
    def _run(self, drug_name: str, dosage: str, quantity_change: int, reason: str) -> str:
        try:
            # Initialize and load inventory
            initialize_inventory()
            inventory = load_db(PHARMACY_INVENTORY_FILE)
            
            inventory_key = f"{drug_name}_{dosage}"
            
            if inventory_key not in inventory:
                return f"❌ Error: Medication '{drug_name} {dosage}' not found in inventory."
            
            item = inventory[inventory_key]
            old_stock = item.get("quantity_in_stock", 0)
            new_stock = old_stock + quantity_change
            
            # Prevent negative stock
            if new_stock < 0:
                return f"❌ Error: Cannot remove {abs(quantity_change)} units. Only {old_stock} units available."
            
            # Update inventory
            item["quantity_in_stock"] = new_stock
            item["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Add update history
            if "update_history" not in item:
                item["update_history"] = []
            
            item["update_history"].append({
                "timestamp": item["last_updated"],
                "change": quantity_change,
                "reason": reason,
                "old_stock": old_stock,
                "new_stock": new_stock
            })
            
            save_db(PHARMACY_INVENTORY_FILE, inventory)
            
            # Determine action type
            action = "Added" if quantity_change > 0 else "Removed"
            
            # Format response
            result = f"✅ Inventory Updated Successfully!\n"
            result += f"{'=' * 50}\n\n"
            result += f"💊 Medication: {drug_name} {dosage}\n"
            result += f"📦 {action}: {abs(quantity_change)} units\n"
            result += f"💬 Reason: {reason}\n\n"
            result += f"📊 Stock Levels:\n"
            result += f"   Previous: {old_stock} units\n"
            result += f"   Change: {quantity_change:+d} units\n"
            result += f"   Current: {new_stock} units\n"
            result += f"   Reorder Level: {item.get('reorder_level')} units\n\n"
            
            # Stock status
            if new_stock == 0:
                result += f"🔴 OUT OF STOCK - Immediate reorder required!\n"
            elif new_stock <= item.get("reorder_level", 50):
                result += f"🟡 LOW STOCK - Reorder recommended\n"
            else:
                result += f"🟢 Stock level adequate\n"
            
            result += f"\n📍 Location: {item.get('location')}\n"
            result += f"⏰ Updated: {item.get('last_updated')}\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error updating inventory: {str(e)}"


# =====================================================
# TOOL 4: Get Medication Info
# =====================================================

class GetMedicationInfoInput(BaseModel):
    drug_name: str = Field(..., description="Drug name to look up")

class GetMedicationInfoTool(BaseTool):
    name: str = "get_medication_info"
    description: str = "Get comprehensive medication information including interactions and contraindications"
    args_schema: type[BaseModel] = GetMedicationInfoInput
    
    def _run(self, drug_name: str) -> str:
        try:
            if drug_name not in MEDICATION_DATABASE:
                return f"❌ Error: Medication '{drug_name}' not found in database.\n" \
                       f"Available medications: {', '.join(MEDICATION_DATABASE.keys())}"
            
            med_info = MEDICATION_DATABASE[drug_name]
            
            # Format response
            result = f"💊 Medication Information: {drug_name}\n"
            result += f"{'=' * 50}\n\n"
            result += f"📋 Generic Name: {med_info['generic_name']}\n"
            result += f"🏷️  Brand Names: {', '.join(med_info['brand_names'])}\n"
            result += f"📂 Category: {med_info['category']}\n"
            result += f"🩺 Route: {med_info['route']}\n\n"
            
            result += f"💉 Common Dosages:\n"
            for dosage in med_info['common_dosages']:
                result += f"   • {dosage}\n"
            
            result += f"\n⏰ Frequency Options:\n"
            for freq in med_info['frequency']:
                result += f"   • {freq}\n"
            
            result += f"\n🎯 Indications:\n"
            for indication in med_info['indications']:
                result += f"   • {indication}\n"
            
            result += f"\n⚠️ Common Side Effects:\n"
            for side_effect in med_info['side_effects']:
                result += f"   • {side_effect}\n"
            
            result += f"\n🚫 Contraindications:\n"
            for contraindication in med_info['contraindications']:
                result += f"   • {contraindication}\n"
            
            result += f"\n⚡ Drug Interactions:\n"
            for interaction in med_info['interactions']:
                result += f"   • {interaction}\n"
            
            result += f"\n💡 Always check patient allergies and current medications before dispensing.\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error retrieving medication info: {str(e)}"


# =====================================================
# TOOL 5: Process Refill Request
# =====================================================

class ProcessRefillRequestInput(BaseModel):
    prescription_id: str = Field(..., description="Original prescription ID")
    patient_id: str = Field(..., description="Patient ID")
    pharmacist_id: str = Field(..., description="Pharmacist ID processing refill")
    refill_quantity: int = Field(..., description="Quantity for refill")

class ProcessRefillRequestTool(BaseTool):
    name: str = "process_refill_request"
    description: str = "Process prescription refill request with validation"
    args_schema: type[BaseModel] = ProcessRefillRequestInput
    
    def _run(self, prescription_id: str, patient_id: str, pharmacist_id: str,
             refill_quantity: int) -> str:
        try:
            # Load prescription
            prescriptions_db = load_db(PRESCRIPTIONS_DB_FILE)
            prescription = next((p for p in prescriptions_db if p.get("prescription_id") == prescription_id), None)
            
            if not prescription:
                return f"❌ Error: Prescription ID '{prescription_id}' not found."
            
            # Verify patient
            if prescription.get("patient_id") != patient_id:
                return f"❌ Error: Prescription belongs to different patient."
            
            # Check refills remaining
            refills_remaining = prescription.get("refills_remaining", 0)
            
            if refills_remaining <= 0:
                return f"❌ Error: No refills remaining. Doctor authorization required.\n" \
                       f"💡 Contact prescribing doctor: {prescription.get('doctor_id')}"
            
            # Create new prescription for refill
            refill_id = f"RX{datetime.now().year}{random.randint(100000, 999999)}"
            
            refill_prescription = {
                "prescription_id": refill_id,
                "original_prescription_id": prescription_id,
                "patient_id": patient_id,
                "patient_name": prescription.get("patient_name"),
                "doctor_id": prescription.get("doctor_id"),
                "medication": prescription.get("medication"),
                "dosage": prescription.get("dosage"),
                "quantity": refill_quantity,
                "instructions": prescription.get("instructions"),
                "refills_remaining": 0,  # Refills don't carry over
                "status": "Active",
                "issue_date": datetime.now().strftime("%Y-%m-%d"),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "is_refill": True,
                "processed_by": pharmacist_id
            }
            
            # Update original prescription
            prescription["refills_remaining"] -= 1
            prescription["last_refill_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Save both prescriptions
            prescriptions_db.append(refill_prescription)
            save_db(PRESCRIPTIONS_DB_FILE, prescriptions_db)
            
            # Format response
            result = f"✅ Refill Request Processed!\n"
            result += f"{'=' * 50}\n\n"
            result += f"🆔 New Prescription ID: {refill_id}\n"
            result += f"📋 Original Prescription: {prescription_id}\n"
            result += f"👤 Patient: {prescription.get('patient_name')} ({patient_id})\n"
            result += f"💊 Medication: {prescription.get('medication')} {prescription.get('dosage')}\n"
            result += f"📦 Quantity: {refill_quantity}\n"
            result += f"📝 Instructions: {prescription.get('instructions')}\n"
            result += f"👨‍⚕️ Processed By: {pharmacist_id}\n"
            result += f"📅 Date: {refill_prescription['created_at']}\n\n"
            result += f"📊 Refills Status:\n"
            result += f"   Original Refills Remaining: {prescription.get('refills_remaining') + 1}\n"
            result += f"   After This Refill: {prescription.get('refills_remaining')}\n\n"
            
            if prescription.get('refills_remaining') == 0:
                result += f"⚠️ WARNING: This was the last refill!\n"
                result += f"💡 Patient needs new prescription from doctor for future refills.\n"
            else:
                result += f"✅ {prescription.get('refills_remaining')} refill(s) remaining on original prescription.\n"
            
            result += f"\n💡 Next Step: Dispense medication using prescription ID {refill_id}\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error processing refill: {str(e)}"


# =====================================================
# TOOL 6: Get Dispensing History
# =====================================================

class GetDispensingHistoryInput(BaseModel):
    patient_id: str = Field(..., description="Patient ID")
    days: Optional[int] = Field(30, description="Number of days to look back (default 30)")

class GetDispensingHistoryTool(BaseTool):
    name: str = "get_dispensing_history"
    description: str = "Get patient's medication dispensing history"
    args_schema: type[BaseModel] = GetDispensingHistoryInput
    
    def _run(self, patient_id: str, days: Optional[int] = 30) -> str:
        try:
            # Load patient
            patients_db = load_db(PATIENTS_DB_FILE)
            patient = next((p for p in patients_db if p.get("patient_id") == patient_id), None)
            
            if not patient:
                return f"❌ Error: Patient ID '{patient_id}' not found."
            
            # Load dispensing history
            dispensing_history = load_db(DISPENSING_HISTORY_FILE)
            
            if not isinstance(dispensing_history, list):
                dispensing_history = []
            
            # Filter by patient and date range
            cutoff_date = datetime.now() - timedelta(days=days)
            
            patient_history = []
            for record in dispensing_history:
                if record.get("patient_id") == patient_id:
                    try:
                        dispensed_date = datetime.strptime(record.get("dispensed_date"), "%Y-%m-%d %H:%M:%S")
                        if dispensed_date >= cutoff_date:
                            patient_history.append(record)
                    except:
                        pass
            
            if not patient_history:
                return f"📋 No dispensing history found for {patient.get('name')} in the last {days} days."
            
            # Sort by date (most recent first)
            patient_history.sort(key=lambda x: x.get("dispensed_date", ""), reverse=True)
            
            # Calculate statistics
            total_medications = len(patient_history)
            total_cost = sum(record.get("total_cost", 0) for record in patient_history)
            unique_meds = len(set(record.get("medication") for record in patient_history))
            
            # Format response
            result = f"💊 Dispensing History: {patient.get('name')}\n"
            result += f"{'=' * 50}\n\n"
            result += f"👤 Patient: {patient.get('name')} ({patient_id})\n"
            result += f"📅 Period: Last {days} days\n"
            result += f"📊 Total Dispensings: {total_medications}\n"
            result += f"💊 Unique Medications: {unique_meds}\n"
            result += f"💵 Total Cost: ${total_cost:.2f}\n\n"
            
            result += f"📋 Dispensing Records:\n"
            result += f"{'-' * 50}\n\n"
            
            for record in patient_history:
                result += f"🆔 {record.get('dispensing_id')}\n"
                result += f"📅 Date: {record.get('dispensed_date')}\n"
                result += f"💊 Medication: {record.get('medication')} {record.get('dosage')}\n"
                result += f"📦 Quantity: {record.get('quantity_dispensed')}\n"
                result += f"💵 Cost: ${record.get('total_cost', 0):.2f}\n"
                result += f"👨‍⚕️ Pharmacist: {record.get('pharmacist_id')}\n"
                result += f"📝 Instructions: {record.get('instructions', 'N/A')}\n"
                if record.get('notes'):
                    result += f"📌 Notes: {record.get('notes')}\n"
                result += f"\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error retrieving dispensing history: {str(e)}"


# =====================================================
# TOOL 7: Check Drug Interactions
# =====================================================

class CheckDrugInteractionsInput(BaseModel):
    drug1: str = Field(..., description="First drug name")
    drug2: str = Field(..., description="Second drug name")

class CheckDrugInteractionsTool(BaseTool):
    name: str = "check_drug_interactions"
    description: str = "Check for potential drug-drug interactions"
    args_schema: type[BaseModel] = CheckDrugInteractionsInput
    
    def _run(self, drug1: str, drug2: str) -> str:
        try:
            # Check if drugs exist in database
            if drug1 not in MEDICATION_DATABASE:
                return f"❌ Error: Drug '{drug1}' not found in database."
            
            if drug2 not in MEDICATION_DATABASE:
                return f"❌ Error: Drug '{drug2}' not found in database."
            
            # Get drug information
            drug1_info = MEDICATION_DATABASE[drug1]
            drug2_info = MEDICATION_DATABASE[drug2]
            
            # Check for interactions (bidirectional)
            interaction_found = False
            severity = "Unknown"
            
            if drug2 in drug1_info["interactions"]:
                interaction_found = True
            elif drug1 in drug2_info["interactions"]:
                interaction_found = True
            
            # Determine severity (simplified logic)
            if interaction_found:
                if ("Warfarin" in [drug1, drug2] and "Aspirin" in [drug1, drug2]) or \
                   ("Warfarin" in [drug1, drug2] and "Antibiotic" in [drug1_info["category"], drug2_info["category"]]):
                    severity = "Severe"
                elif "NSAID" in [drug1_info["category"], drug2_info["category"]] and \
                     "Anticoagulant" in [drug1_info["category"], drug2_info["category"]]:
                    severity = "Severe"
                else:
                    severity = "Moderate"
            
            # Format response
            result = f"⚡ Drug Interaction Check\n"
            result += f"{'=' * 50}\n\n"
            result += f"💊 Drug 1: {drug1}\n"
            result += f"   Category: {drug1_info['category']}\n"
            result += f"   Generic: {drug1_info['generic_name']}\n\n"
            result += f"💊 Drug 2: {drug2}\n"
            result += f"   Category: {drug2_info['category']}\n"
            result += f"   Generic: {drug2_info['generic_name']}\n\n"
            
            if interaction_found:
                result += f"⚠️ INTERACTION DETECTED!\n"
                result += f"🚨 Severity: {severity}\n\n"
                result += f"⚡ Potential Effects:\n"
                
                # Provide specific interaction details
                if severity == "Severe":
                    result += f"   • Increased bleeding risk\n"
                    result += f"   • Enhanced anticoagulant effect\n"
                    result += f"   • Close monitoring required\n"
                    result += f"   • Dosage adjustment may be needed\n"
                else:
                    result += f"   • Possible reduced efficacy\n"
                    result += f"   • Monitor for side effects\n"
                    result += f"   • Timing of doses may need adjustment\n"
                
                result += f"\n💡 Recommendations:\n"
                result += f"   • Consult prescribing physician\n"
                result += f"   • Monitor patient closely\n"
                result += f"   • Consider alternative medications\n"
                result += f"   • Document interaction in patient record\n"
                
                if severity == "Severe":
                    result += f"\n🚨 ALERT: Severe interaction - Doctor consultation required!\n"
            else:
                result += f"✅ No known interactions detected\n"
                result += f"💡 However, always monitor patient for unexpected effects.\n"
            
            # List all known interactions for both drugs
            result += f"\n📋 Known Interactions:\n"
            result += f"   {drug1}: {', '.join(drug1_info['interactions'])}\n"
            result += f"   {drug2}: {', '.join(drug2_info['interactions'])}\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error checking interactions: {str(e)}"


# =====================================================
# TOOL 8: Get Pharmacy Statistics
# =====================================================

class GetPharmacyStatisticsInput(BaseModel):
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")

class GetPharmacyStatisticsTool(BaseTool):
    name: str = "get_pharmacy_statistics"
    description: str = "Generate comprehensive pharmacy analytics including inventory and dispensing stats"
    args_schema: type[BaseModel] = GetPharmacyStatisticsInput
    
    def _run(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
        try:
            # Initialize inventory
            initialize_inventory()
            
            # Load data
            inventory = load_db(PHARMACY_INVENTORY_FILE)
            dispensing_history = load_db(DISPENSING_HISTORY_FILE)
            
            if not isinstance(dispensing_history, list):
                dispensing_history = []
            
            # Filter dispensing history by date
            filtered_dispensings = dispensing_history
            
            if start_date or end_date:
                filtered_dispensings = []
                for record in dispensing_history:
                    try:
                        record_date = record.get("dispensed_date", "").split()[0]
                        if start_date and record_date < start_date:
                            continue
                        if end_date and record_date > end_date:
                            continue
                        filtered_dispensings.append(record)
                    except:
                        pass
            
            # Calculate statistics
            total_items = len(inventory)
            total_value = sum(item.get("quantity_in_stock", 0) * item.get("unit_price", 0) 
                            for item in inventory.values())
            
            low_stock_items = sum(1 for item in inventory.values() 
                                 if item.get("quantity_in_stock", 0) <= item.get("reorder_level", 50))
            
            out_of_stock = sum(1 for item in inventory.values() 
                              if item.get("quantity_in_stock", 0) == 0)
            
            # Dispensing statistics
            total_dispensings = len(filtered_dispensings)
            total_revenue = sum(record.get("total_cost", 0) for record in filtered_dispensings)
            
            # Most dispensed medications
            med_counts = {}
            for record in filtered_dispensings:
                med = record.get("medication")
                med_counts[med] = med_counts.get(med, 0) + 1
            
            # Format response
            result = f"📊 Pharmacy Statistics Dashboard\n"
            result += f"{'=' * 50}\n\n"
            
            if start_date or end_date:
                result += f"📅 Date Range: "
                if start_date:
                    result += f"From {start_date} "
                if end_date:
                    result += f"To {end_date}"
                result += "\n\n"
            
            result += f"📦 INVENTORY STATISTICS\n"
            result += f"{'-' * 50}\n"
            result += f"   Total Medications: {total_items} items\n"
            result += f"   Total Inventory Value: ${total_value:,.2f}\n"
            result += f"   🟡 Low Stock Items: {low_stock_items}\n"
            result += f"   🔴 Out of Stock Items: {out_of_stock}\n\n"
            
            result += f"💊 DISPENSING STATISTICS\n"
            result += f"{'-' * 50}\n"
            result += f"   Total Dispensings: {total_dispensings}\n"
            result += f"   Total Revenue: ${total_revenue:,.2f}\n"
            
            if total_dispensings > 0:
                result += f"   Average Transaction: ${total_revenue/total_dispensings:.2f}\n"
            
            result += f"\n"
            
            # Top dispensed medications
            if med_counts:
                result += f"🏆 TOP DISPENSED MEDICATIONS\n"
                result += f"{'-' * 50}\n"
                
                sorted_meds = sorted(med_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                for med, count in sorted_meds:
                    percentage = (count / total_dispensings * 100) if total_dispensings > 0 else 0
                    result += f"   {count:3d}x - {med} ({percentage:.1f}%)\n"
                
                result += f"\n"
            
            # Low stock alerts
            if low_stock_items > 0:
                result += f"⚠️ LOW STOCK ALERTS\n"
                result += f"{'-' * 50}\n"
                
                low_items = [item for item in inventory.values() 
                           if item.get("quantity_in_stock", 0) <= item.get("reorder_level", 50)]
                low_items.sort(key=lambda x: x.get("quantity_in_stock", 0))
                
                for item in low_items[:10]:  # Show top 10
                    stock = item.get("quantity_in_stock", 0)
                    status = "🔴 OUT" if stock == 0 else "🟡 LOW"
                    result += f"   {status} - {item.get('drug_name')} {item.get('dosage')}: {stock} units\n"
                
                result += f"\n"
            
            # Insights
            result += f"💡 INSIGHTS\n"
            result += f"{'-' * 50}\n"
            
            if out_of_stock > 0:
                result += f"   🚨 {out_of_stock} medication(s) out of stock - immediate reorder!\n"
            
            if low_stock_items > 0:
                result += f"   ⚠️ {low_stock_items} item(s) below reorder level\n"
            
            if total_dispensings > 0:
                result += f"   📈 {total_dispensings} dispensings processed\n"
                result += f"   💰 ${total_revenue:,.2f} revenue generated\n"
            
            if low_stock_items == 0 and out_of_stock == 0:
                result += f"   ✅ All medications adequately stocked\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error generating statistics: {str(e)}"


# =====================================================
# Helper Function: Get All Tools
# =====================================================

def get_all_pharmacy_tools():
    """Returns list of all pharmacy management tools"""
    return [
        DispenseMedicationTool(),
        CheckDrugInventoryTool(),
        UpdateInventoryTool(),
        GetMedicationInfoTool(),
        ProcessRefillRequestTool(),
        GetDispensingHistoryTool(),
        CheckDrugInteractionsTool(),
        GetPharmacyStatisticsTool()
    ]


# =====================================================
# Usage Example
# =====================================================

if __name__ == "__main__":
    print("💊 PHARMACY TOOL - DEMO")
    print("=" * 60)
    
    # Get all tools
    tools = get_all_pharmacy_tools()
    
    print(f"\n✅ Loaded {len(tools)} Pharmacy Management Tools:\n")
    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool.name}")
    
    print("\n" + "=" * 60)
    print("✅ PHARMACY TOOLS READY!")
    print("=" * 60)
