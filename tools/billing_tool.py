"""
Billing & Insurance Management Tools
Handles invoice generation, insurance claims, payments, and financial reporting
"""

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from datetime import datetime, timedelta
import json
import os
import random

# Database file paths
BILLING_DB_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'billing_database.json')
INSURANCE_DB_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'insurance_database.json')
PAYMENTS_DB_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'payments_database.json')
APPOINTMENTS_DB_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'appointments_database.json')
LAB_TESTS_DB_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'lab_tests_database.json')
PATIENTS_DB_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'patients_database.json')

# Pricing structure
PRICING = {
    'appointments': {
        'General Medicine': 150.00,
        'Cardiology': 250.00,
        'Pediatrics': 180.00,
        'Orthopedics': 220.00,
        'Dermatology': 200.00,
        'Follow-up': 100.00,
        'Emergency': 300.00
    },
    'lab_tests': {
        'Complete Blood Count (CBC)': 45.00,
        'Blood Glucose Fasting': 25.00,
        'Hemoglobin A1C': 55.00,
        'Lipid Profile': 65.00,
        'Liver Function Test': 75.00,
        'Kidney Function Test': 70.00,
        'Thyroid Function Test': 80.00,
        'Urinalysis': 30.00,
        'Urine Culture': 50.00,
        'X-Ray Chest': 120.00,
        'X-Ray': 100.00,
        'CT Scan': 450.00,
        'MRI': 650.00,
        'Ultrasound': 180.00,
        'Biopsy': 300.00,
        'Pap Smear': 75.00
    }
}

# Insurance providers database
INSURANCE_PROVIDERS = {
    'BLUE001': {
        'name': 'Blue Cross Blue Shield',
        'coverage_percentage': 80,
        'copay': 30.00,
        'deductible': 1000.00,
        'max_coverage': 50000.00,
        'network': 'PPO'
    },
    'UNIT002': {
        'name': 'UnitedHealthcare',
        'coverage_percentage': 70,
        'copay': 40.00,
        'deductible': 1500.00,
        'max_coverage': 75000.00,
        'network': 'HMO'
    },
    'AETNA003': {
        'name': 'Aetna',
        'coverage_percentage': 75,
        'copay': 35.00,
        'deductible': 1200.00,
        'max_coverage': 60000.00,
        'network': 'PPO'
    },
    'CIGNA004': {
        'name': 'Cigna',
        'coverage_percentage': 85,
        'copay': 25.00,
        'deductible': 800.00,
        'max_coverage': 100000.00,
        'network': 'EPO'
    },
    'HUMANA005': {
        'name': 'Humana',
        'coverage_percentage': 65,
        'copay': 50.00,
        'deductible': 2000.00,
        'max_coverage': 40000.00,
        'network': 'HMO'
    }
}

def load_db(file_path):
    """Load database from JSON file"""
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Convert dict to list for backward compatibility
            if isinstance(data, dict) and 'data' in data:
                return data['data']
            elif isinstance(data, dict) and len(data) > 0:
                # Check if it's a dict of records with IDs as keys
                first_key = list(data.keys())[0]
                if isinstance(data[first_key], dict):
                    return list(data.values())
            return data if isinstance(data, list) else []
    return []

def save_db(file_path, data):
    """Save database to JSON file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def generate_invoice_id():
    """Generate unique invoice ID"""
    return f"INV{datetime.now().strftime('%Y')}{random.randint(100000, 999999)}"

def generate_claim_id():
    """Generate unique insurance claim ID"""
    return f"CLM{datetime.now().strftime('%Y')}{random.randint(100000, 999999)}"

def generate_payment_id():
    """Generate unique payment ID"""
    return f"PAY{datetime.now().strftime('%Y')}{random.randint(100000, 999999)}"

# ==================== TOOL 1: Generate Invoice ====================

class GenerateInvoiceInput(BaseModel):
    patient_id: str = Field(description="Patient registration ID")
    appointment_ids: Optional[List[str]] = Field(default=None, description="List of appointment IDs to include")
    lab_test_ids: Optional[List[str]] = Field(default=None, description="List of lab test IDs to include")
    prescription_ids: Optional[List[str]] = Field(default=None, description="List of prescription IDs to include (pharmacy dispensing)")
    additional_charges: Optional[List[dict]] = Field(default=None, description="Additional charges: [{'description': 'Item', 'amount': 100.00}]")
    notes: Optional[str] = Field(default="", description="Additional notes for the invoice")

class GenerateInvoiceTool(BaseTool):
    name: str = "generate_invoice"
    description: str = """Generate a comprehensive invoice for a patient including appointments, lab tests, 
    and pharmacy charges. Calculates total amount, itemizes all services, and creates billing record."""
    args_schema: type[BaseModel] = GenerateInvoiceInput
    
    def _run(self, patient_id: str, appointment_ids: Optional[List[str]] = None, 
             lab_test_ids: Optional[List[str]] = None, prescription_ids: Optional[List[str]] = None,
             additional_charges: Optional[List[dict]] = None, notes: str = "") -> dict:
        """Generate invoice for patient services"""
        
        try:
            # Load databases
            patients = load_db(PATIENTS_DB_FILE)
            appointments = load_db(APPOINTMENTS_DB_FILE)
            lab_tests = load_db(LAB_TESTS_DB_FILE)
            billings = load_db(BILLING_DB_FILE)
            
            # Find patient
            patient = next((p for p in patients if p.get('patient_id') == patient_id), None)
            if not patient:
                return {'success': False, 'message': f'Patient {patient_id} not found'}
            
            # Initialize invoice
            invoice = {
                'invoice_id': generate_invoice_id(),
                'patient_id': patient_id,
                'patient_name': patient.get('name', 'Unknown'),
                'invoice_date': datetime.now().strftime('%Y-%m-%d'),
                'due_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'items': [],
                'subtotal': 0.0,
                'tax': 0.0,
                'total_amount': 0.0,
                'amount_paid': 0.0,
                'balance_due': 0.0,
                'status': 'Pending',
                'notes': notes,
                'created_at': datetime.now().isoformat()
            }
            
            # Add appointment charges
            if appointment_ids:
                for appt_id in appointment_ids:
                    appt = next((a for a in appointments if a.get('appointment_id') == appt_id), None)
                    if appt:
                        specialty = appt.get('specialty', 'General Medicine')
                        charge = PRICING['appointments'].get(specialty, 150.00)
                        invoice['items'].append({
                            'type': 'Appointment',
                            'description': f"{specialty} - Dr. {appt.get('doctor_name', 'Unknown')}",
                            'date': appt.get('date', ''),
                            'quantity': 1,
                            'unit_price': charge,
                            'amount': charge
                        })
                        invoice['subtotal'] += charge
            
            # Add lab test charges
            if lab_test_ids:
                for test_id in lab_test_ids:
                    test = next((t for t in lab_tests if t.get('test_id') == test_id), None)
                    if test:
                        test_name = test.get('test_name', 'Lab Test')
                        charge = PRICING['lab_tests'].get(test_name, 50.00)
                        invoice['items'].append({
                            'type': 'Lab Test',
                            'description': test_name,
                            'date': test.get('ordered_date', ''),
                            'quantity': 1,
                            'unit_price': charge,
                            'amount': charge
                        })
                        invoice['subtotal'] += charge
            
            # Add pharmacy charges (from dispensing history)
            if prescription_ids:
                for rx_id in prescription_ids:
                    # Load dispensing history to get actual costs
                    try:
                        dispensing_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'dispensing_history.json')
                        if os.path.exists(dispensing_file):
                            with open(dispensing_file, 'r') as f:
                                dispensing_history = json.load(f)
                                dispensing = next((d for d in dispensing_history if d.get('prescription_id') == rx_id), None)
                                if dispensing:
                                    charge = dispensing.get('total_cost', 50.00)
                                    invoice['items'].append({
                                        'type': 'Pharmacy',
                                        'description': f"{dispensing.get('medication_name', 'Medication')} - {dispensing.get('quantity', 0)} units",
                                        'date': dispensing.get('dispensed_date', ''),
                                        'quantity': 1,
                                        'unit_price': charge,
                                        'amount': charge
                                    })
                                    invoice['subtotal'] += charge
                    except:
                        # If dispensing history not found, use placeholder
                        invoice['items'].append({
                            'type': 'Pharmacy',
                            'description': f"Medication (Prescription {rx_id})",
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            'quantity': 1,
                            'unit_price': 50.00,
                            'amount': 50.00
                        })
                        invoice['subtotal'] += 50.00
            
            # Add additional charges
            if additional_charges:
                for charge_item in additional_charges:
                    amount = charge_item.get('amount', 0.0)
                    invoice['items'].append({
                        'type': 'Additional',
                        'description': charge_item.get('description', 'Additional Charge'),
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'quantity': 1,
                        'unit_price': amount,
                        'amount': amount
                    })
                    invoice['subtotal'] += amount
            
            # Calculate tax (8% healthcare services tax)
            invoice['tax'] = round(invoice['subtotal'] * 0.08, 2)
            invoice['total_amount'] = round(invoice['subtotal'] + invoice['tax'], 2)
            invoice['balance_due'] = invoice['total_amount']
            
            # Save invoice
            billings.append(invoice)
            save_db(BILLING_DB_FILE, billings)
            
            # Format output
            output = f"\n{'='*60}\n"
            output += f"💰 INVOICE GENERATED\n"
            output += f"{'='*60}\n\n"
            output += f"📄 Invoice ID: {invoice['invoice_id']}\n"
            output += f"👤 Patient: {invoice['patient_name']} ({patient_id})\n"
            output += f"📅 Invoice Date: {invoice['invoice_date']}\n"
            output += f"📅 Due Date: {invoice['due_date']}\n"
            output += f"\n{'='*60}\n"
            output += f"ITEMIZED CHARGES\n"
            output += f"{'='*60}\n\n"
            
            for item in invoice['items']:
                output += f"• {item['type']}: {item['description']}\n"
                output += f"  Date: {item['date']} | Amount: ${item['amount']:.2f}\n\n"
            
            output += f"{'='*60}\n"
            output += f"Subtotal: ${invoice['subtotal']:.2f}\n"
            output += f"Tax (8%): ${invoice['tax']:.2f}\n"
            output += f"{'='*60}\n"
            output += f"💵 TOTAL AMOUNT: ${invoice['total_amount']:.2f}\n"
            output += f"💰 BALANCE DUE: ${invoice['balance_due']:.2f}\n"
            output += f"{'='*60}\n"
            
            if notes:
                output += f"\n📝 Notes: {notes}\n"
            
            return {
                'success': True,
                'message': output,
                'invoice': invoice
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error generating invoice: {str(e)}'}

# ==================== TOOL 2: Verify Insurance Coverage ====================

class VerifyInsuranceCoverageInput(BaseModel):
    patient_id: str = Field(description="Patient registration ID")
    insurance_provider_id: str = Field(description="Insurance provider ID (e.g., BLUE001)")
    policy_number: str = Field(description="Patient's insurance policy number")
    service_amount: float = Field(description="Total service amount to verify coverage for")

class VerifyInsuranceCoverageTool(BaseTool):
    name: str = "verify_insurance_coverage"
    description: str = """Verify patient's insurance coverage, check policy status, calculate coverage amount, 
    copay, and patient responsibility. Returns detailed breakdown of what insurance covers."""
    args_schema: type[BaseModel] = VerifyInsuranceCoverageInput
    
    def _run(self, patient_id: str, insurance_provider_id: str, policy_number: str, service_amount: float) -> dict:
        """Verify insurance coverage and calculate patient responsibility"""
        
        try:
            # Get insurance provider info
            provider = INSURANCE_PROVIDERS.get(insurance_provider_id)
            if not provider:
                return {'success': False, 'message': f'Insurance provider {insurance_provider_id} not found'}
            
            # Calculate coverage
            coverage_percentage = provider['coverage_percentage']
            copay = provider['copay']
            deductible = provider['deductible']
            
            # For simplicity, assume deductible is already met (in real system, check patient's claim history)
            deductible_remaining = 0.00  # Assume met
            
            # Calculate amounts
            amount_after_copay = service_amount - copay
            insurance_coverage = round(amount_after_copay * (coverage_percentage / 100), 2)
            patient_responsibility = round(service_amount - insurance_coverage, 2)
            
            # Format output
            output = f"\n{'='*60}\n"
            output += f"🏥 INSURANCE COVERAGE VERIFICATION\n"
            output += f"{'='*60}\n\n"
            output += f"📋 Insurance Provider: {provider['name']}\n"
            output += f"🆔 Provider ID: {insurance_provider_id}\n"
            output += f"📄 Policy Number: {policy_number}\n"
            output += f"🌐 Network: {provider['network']}\n"
            output += f"👤 Patient ID: {patient_id}\n"
            output += f"\n{'='*60}\n"
            output += f"COVERAGE BREAKDOWN\n"
            output += f"{'='*60}\n\n"
            output += f"💵 Total Service Amount: ${service_amount:.2f}\n"
            output += f"💳 Copay: ${copay:.2f}\n"
            output += f"📊 Coverage Percentage: {coverage_percentage}%\n"
            output += f"🏦 Deductible: ${deductible:.2f} (Status: Met ✅)\n"
            output += f"\n{'='*60}\n"
            output += f"Amount After Copay: ${amount_after_copay:.2f}\n"
            output += f"✅ Insurance Covers: ${insurance_coverage:.2f}\n"
            output += f"👤 Patient Responsibility: ${patient_responsibility:.2f}\n"
            output += f"{'='*60}\n\n"
            output += f"📝 Coverage Status: ✅ APPROVED\n"
            output += f"🎯 Max Annual Coverage: ${provider['max_coverage']:.2f}\n"
            
            return {
                'success': True,
                'message': output,
                'coverage_details': {
                    'provider_name': provider['name'],
                    'provider_id': insurance_provider_id,
                    'policy_number': policy_number,
                    'service_amount': service_amount,
                    'copay': copay,
                    'coverage_percentage': coverage_percentage,
                    'insurance_coverage': insurance_coverage,
                    'patient_responsibility': patient_responsibility,
                    'deductible': deductible,
                    'deductible_remaining': deductible_remaining,
                    'max_coverage': provider['max_coverage'],
                    'status': 'approved'
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error verifying insurance coverage: {str(e)}'}

# ==================== TOOL 3: Process Insurance Claim ====================

class ProcessInsuranceClaimInput(BaseModel):
    invoice_id: str = Field(description="Invoice ID to process claim for")
    insurance_provider_id: str = Field(description="Insurance provider ID")
    policy_number: str = Field(description="Patient's insurance policy number")
    diagnosis_codes: List[str] = Field(description="ICD-10 diagnosis codes for the claim")
    procedure_codes: List[str] = Field(description="CPT procedure codes for the claim")
    notes: Optional[str] = Field(default="", description="Additional notes for the claim")

class ProcessInsuranceClaimTool(BaseTool):
    name: str = "process_insurance_claim"
    description: str = """Submit an insurance claim for an invoice. Creates claim record, calculates insurance 
    coverage, updates invoice with insurance information, and tracks claim status."""
    args_schema: type[BaseModel] = ProcessInsuranceClaimInput
    
    def _run(self, invoice_id: str, insurance_provider_id: str, policy_number: str, 
             diagnosis_codes: List[str], procedure_codes: List[str], notes: str = "") -> dict:
        """Process insurance claim for an invoice"""
        
        try:
            # Load databases
            billings = load_db(BILLING_DB_FILE)
            claims = load_db(INSURANCE_DB_FILE)
            
            # Find invoice
            invoice = next((b for b in billings if b.get('invoice_id') == invoice_id), None)
            if not invoice:
                return {'success': False, 'message': f'Invoice {invoice_id} not found'}
            
            # Get insurance provider
            provider = INSURANCE_PROVIDERS.get(insurance_provider_id)
            if not provider:
                return {'success': False, 'message': f'Insurance provider {insurance_provider_id} not found'}
            
            # Calculate coverage
            service_amount = invoice['total_amount']
            copay = provider['copay']
            coverage_percentage = provider['coverage_percentage']
            
            amount_after_copay = service_amount - copay
            insurance_coverage = round(amount_after_copay * (coverage_percentage / 100), 2)
            patient_responsibility = round(service_amount - insurance_coverage, 2)
            
            # Create claim record
            claim = {
                'claim_id': generate_claim_id(),
                'invoice_id': invoice_id,
                'patient_id': invoice['patient_id'],
                'patient_name': invoice['patient_name'],
                'insurance_provider_id': insurance_provider_id,
                'insurance_provider_name': provider['name'],
                'policy_number': policy_number,
                'service_amount': service_amount,
                'copay': copay,
                'insurance_coverage': insurance_coverage,
                'patient_responsibility': patient_responsibility,
                'diagnosis_codes': diagnosis_codes,
                'procedure_codes': procedure_codes,
                'claim_date': datetime.now().strftime('%Y-%m-%d'),
                'status': 'Submitted',
                'status_history': [
                    {
                        'status': 'Submitted',
                        'date': datetime.now().isoformat(),
                        'notes': 'Claim submitted to insurance provider'
                    }
                ],
                'notes': notes,
                'created_at': datetime.now().isoformat()
            }
            
            # Update invoice with insurance info
            invoice['insurance_claim_id'] = claim['claim_id']
            invoice['insurance_coverage'] = insurance_coverage
            invoice['balance_due'] = patient_responsibility
            invoice['status'] = 'Insurance Processing'
            
            # Save databases
            claims.append(claim)
            save_db(INSURANCE_DB_FILE, claims)
            save_db(BILLING_DB_FILE, billings)
            
            # Format output
            output = f"\n{'='*60}\n"
            output += f"🏥 INSURANCE CLAIM PROCESSED\n"
            output += f"{'='*60}\n\n"
            output += f"📄 Claim ID: {claim['claim_id']}\n"
            output += f"📄 Invoice ID: {invoice_id}\n"
            output += f"👤 Patient: {invoice['patient_name']} ({invoice['patient_id']})\n"
            output += f"🏥 Insurance: {provider['name']}\n"
            output += f"📋 Policy Number: {policy_number}\n"
            output += f"📅 Claim Date: {claim['claim_date']}\n"
            output += f"\n{'='*60}\n"
            output += f"CLAIM DETAILS\n"
            output += f"{'='*60}\n\n"
            output += f"💵 Service Amount: ${service_amount:.2f}\n"
            output += f"💳 Copay: ${copay:.2f}\n"
            output += f"📊 Coverage: {coverage_percentage}%\n"
            output += f"✅ Insurance Will Pay: ${insurance_coverage:.2f}\n"
            output += f"👤 Patient Responsibility: ${patient_responsibility:.2f}\n"
            output += f"\n📋 Diagnosis Codes: {', '.join(diagnosis_codes)}\n"
            output += f"🔧 Procedure Codes: {', '.join(procedure_codes)}\n"
            output += f"\n{'='*60}\n"
            output += f"📊 Claim Status: {claim['status']}\n"
            output += f"{'='*60}\n\n"
            output += f"✉️ Claim submitted to {provider['name']}\n"
            output += f"⏳ Processing time: 7-14 business days\n"
            
            return {
                'success': True,
                'message': output,
                'claim': claim
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error processing insurance claim: {str(e)}'}

# ==================== TOOL 4: Record Payment ====================

class RecordPaymentInput(BaseModel):
    invoice_id: str = Field(description="Invoice ID to record payment for")
    payment_amount: float = Field(description="Payment amount")
    payment_method: Literal["Cash", "Credit Card", "Debit Card", "Check", "Bank Transfer", "Insurance"] = Field(description="Payment method")
    payment_reference: Optional[str] = Field(default="", description="Payment reference number (check number, transaction ID, etc.)")
    notes: Optional[str] = Field(default="", description="Additional notes")

class RecordPaymentTool(BaseTool):
    name: str = "record_payment"
    description: str = """Record a payment for an invoice. Updates invoice balance, creates payment record, 
    and marks invoice as paid if balance is zero."""
    args_schema: type[BaseModel] = RecordPaymentInput
    
    def _run(self, invoice_id: str, payment_amount: float, payment_method: str, 
             payment_reference: str = "", notes: str = "") -> dict:
        """Record payment for an invoice"""
        
        try:
            # Load databases
            billings = load_db(BILLING_DB_FILE)
            payments = load_db(PAYMENTS_DB_FILE)
            
            # Find invoice
            invoice = next((b for b in billings if b.get('invoice_id') == invoice_id), None)
            if not invoice:
                return {'success': False, 'message': f'Invoice {invoice_id} not found'}
            
            # Validate payment amount
            if payment_amount <= 0:
                return {'success': False, 'message': 'Payment amount must be greater than zero'}
            
            if payment_amount > invoice['balance_due']:
                return {'success': False, 'message': f'Payment amount ${payment_amount:.2f} exceeds balance due ${invoice["balance_due"]:.2f}'}
            
            # Create payment record
            payment = {
                'payment_id': generate_payment_id(),
                'invoice_id': invoice_id,
                'patient_id': invoice['patient_id'],
                'patient_name': invoice['patient_name'],
                'payment_amount': payment_amount,
                'payment_method': payment_method,
                'payment_reference': payment_reference,
                'payment_date': datetime.now().strftime('%Y-%m-%d'),
                'payment_time': datetime.now().strftime('%H:%M:%S'),
                'notes': notes,
                'created_at': datetime.now().isoformat()
            }
            
            # Update invoice
            invoice['amount_paid'] += payment_amount
            invoice['balance_due'] -= payment_amount
            invoice['balance_due'] = round(invoice['balance_due'], 2)
            
            if invoice['balance_due'] == 0:
                invoice['status'] = 'Paid'
                invoice['paid_date'] = datetime.now().strftime('%Y-%m-%d')
            else:
                invoice['status'] = 'Partially Paid'
            
            # Add payment to invoice history
            if 'payments' not in invoice:
                invoice['payments'] = []
            invoice['payments'].append({
                'payment_id': payment['payment_id'],
                'amount': payment_amount,
                'method': payment_method,
                'date': payment['payment_date']
            })
            
            # Save databases
            payments.append(payment)
            save_db(PAYMENTS_DB_FILE, payments)
            save_db(BILLING_DB_FILE, billings)
            
            # Format output
            output = f"\n{'='*60}\n"
            output += f"💰 PAYMENT RECORDED\n"
            output += f"{'='*60}\n\n"
            output += f"🆔 Payment ID: {payment['payment_id']}\n"
            output += f"📄 Invoice ID: {invoice_id}\n"
            output += f"👤 Patient: {invoice['patient_name']} ({invoice['patient_id']})\n"
            output += f"📅 Payment Date: {payment['payment_date']} {payment['payment_time']}\n"
            output += f"\n{'='*60}\n"
            output += f"PAYMENT DETAILS\n"
            output += f"{'='*60}\n\n"
            output += f"💵 Payment Amount: ${payment_amount:.2f}\n"
            output += f"💳 Payment Method: {payment_method}\n"
            
            if payment_reference:
                output += f"📝 Reference: {payment_reference}\n"
            
            output += f"\n{'='*60}\n"
            output += f"INVOICE STATUS\n"
            output += f"{'='*60}\n\n"
            output += f"Total Amount: ${invoice['total_amount']:.2f}\n"
            output += f"Amount Paid: ${invoice['amount_paid']:.2f}\n"
            output += f"Balance Due: ${invoice['balance_due']:.2f}\n"
            output += f"Status: {invoice['status']}\n"
            output += f"{'='*60}\n\n"
            
            if invoice['balance_due'] == 0:
                output += f"✅ Invoice fully paid! Thank you for your payment.\n"
            else:
                output += f"💡 Remaining balance: ${invoice['balance_due']:.2f}\n"
            
            return {
                'success': True,
                'message': output,
                'payment': payment,
                'updated_invoice': {
                    'invoice_id': invoice_id,
                    'total_amount': invoice['total_amount'],
                    'amount_paid': invoice['amount_paid'],
                    'balance_due': invoice['balance_due'],
                    'status': invoice['status']
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error recording payment: {str(e)}'}

# ==================== TOOL 5: Get Patient Balance ====================

class GetPatientBalanceInput(BaseModel):
    patient_id: str = Field(description="Patient registration ID")
    include_paid: bool = Field(default=False, description="Include paid invoices in the report")

class GetPatientBalanceTool(BaseTool):
    name: str = "get_patient_balance"
    description: str = """Get patient's billing balance and payment history. Shows all outstanding invoices, 
    payment history, and total balance due."""
    args_schema: type[BaseModel] = GetPatientBalanceInput
    
    def _run(self, patient_id: str, include_paid: bool = False) -> dict:
        """Get patient's billing balance and history"""
        
        try:
            # Load databases
            billings = load_db(BILLING_DB_FILE)
            payments = load_db(PAYMENTS_DB_FILE)
            patients = load_db(PATIENTS_DB_FILE)
            
            # Find patient
            patient = next((p for p in patients if p.get('patient_id') == patient_id), None)
            if not patient:
                return {'success': False, 'message': f'Patient {patient_id} not found'}
            
            # Get patient's invoices
            patient_invoices = [b for b in billings if b.get('patient_id') == patient_id]
            
            if not include_paid:
                patient_invoices = [b for b in patient_invoices if b.get('balance_due', 0) > 0]
            
            # Get patient's payments
            patient_payments = [p for p in payments if p.get('patient_id') == patient_id]
            
            # Calculate totals
            total_billed = sum(inv.get('total_amount', 0) for inv in patient_invoices)
            total_paid = sum(inv.get('amount_paid', 0) for inv in patient_invoices)
            total_balance = sum(inv.get('balance_due', 0) for inv in patient_invoices)
            
            # Format output
            output = f"\n{'='*60}\n"
            output += f"💰 PATIENT BILLING SUMMARY\n"
            output += f"{'='*60}\n\n"
            output += f"👤 Patient: {patient.get('name', 'Unknown')} ({patient_id})\n"
            output += f"📅 As of: {datetime.now().strftime('%Y-%m-%d')}\n"
            output += f"\n{'='*60}\n"
            output += f"ACCOUNT SUMMARY\n"
            output += f"{'='*60}\n\n"
            output += f"💵 Total Billed: ${total_billed:.2f}\n"
            output += f"✅ Total Paid: ${total_paid:.2f}\n"
            output += f"⚠️ Total Balance Due: ${total_balance:.2f}\n"
            output += f"\n{'='*60}\n"
            output += f"OUTSTANDING INVOICES ({len([b for b in patient_invoices if b.get('balance_due', 0) > 0])})\n"
            output += f"{'='*60}\n\n"
            
            outstanding_invoices = [b for b in patient_invoices if b.get('balance_due', 0) > 0]
            
            if outstanding_invoices:
                for inv in sorted(outstanding_invoices, key=lambda x: x.get('invoice_date', ''), reverse=True):
                    output += f"📄 {inv.get('invoice_id')}\n"
                    output += f"   Date: {inv.get('invoice_date')} | Due: {inv.get('due_date')}\n"
                    output += f"   Total: ${inv.get('total_amount', 0):.2f} | Paid: ${inv.get('amount_paid', 0):.2f} | Balance: ${inv.get('balance_due', 0):.2f}\n"
                    output += f"   Status: {inv.get('status', 'Unknown')}\n\n"
            else:
                output += "✅ No outstanding invoices. Account is current!\n\n"
            
            if include_paid:
                paid_invoices = [b for b in patient_invoices if b.get('balance_due', 0) == 0]
                if paid_invoices:
                    output += f"{'='*60}\n"
                    output += f"PAID INVOICES ({len(paid_invoices)})\n"
                    output += f"{'='*60}\n\n"
                    
                    for inv in sorted(paid_invoices, key=lambda x: x.get('invoice_date', ''), reverse=True)[:5]:
                        output += f"✅ {inv.get('invoice_id')} - ${inv.get('total_amount', 0):.2f} (Paid: {inv.get('paid_date', 'N/A')})\n"
                    
                    output += "\n"
            
            output += f"{'='*60}\n"
            output += f"PAYMENT HISTORY (Last 5)\n"
            output += f"{'='*60}\n\n"
            
            if patient_payments:
                recent_payments = sorted(patient_payments, key=lambda x: x.get('payment_date', ''), reverse=True)[:5]
                for pay in recent_payments:
                    output += f"💳 {pay.get('payment_id')} - ${pay.get('payment_amount', 0):.2f}\n"
                    output += f"   Date: {pay.get('payment_date')} | Method: {pay.get('payment_method')}\n"
                    output += f"   Invoice: {pay.get('invoice_id')}\n\n"
            else:
                output += "No payment history found.\n\n"
            
            output += f"{'='*60}\n"
            
            return {
                'success': True,
                'message': output,
                'summary': {
                    'patient_id': patient_id,
                    'patient_name': patient.get('name', 'Unknown'),
                    'total_billed': total_billed,
                    'total_paid': total_paid,
                    'total_balance': total_balance,
                    'outstanding_count': len(outstanding_invoices),
                    'paid_count': len([b for b in patient_invoices if b.get('balance_due', 0) == 0])
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error retrieving patient balance: {str(e)}'}

# ==================== TOOL 6: Generate Financial Report ====================

class GenerateFinancialReportInput(BaseModel):
    report_type: Literal["daily", "weekly", "monthly", "custom"] = Field(description="Type of financial report")
    start_date: Optional[str] = Field(default=None, description="Start date (YYYY-MM-DD) for custom report")
    end_date: Optional[str] = Field(default=None, description="End date (YYYY-MM-DD) for custom report")
    include_departments: bool = Field(default=True, description="Include department breakdown")

class GenerateFinancialReportTool(BaseTool):
    name: str = "generate_financial_report"
    description: str = """Generate comprehensive financial report showing revenue, payments, outstanding balances, 
    and department-wise breakdown for specified period."""
    args_schema: type[BaseModel] = GenerateFinancialReportInput
    
    def _run(self, report_type: str, start_date: Optional[str] = None, end_date: Optional[str] = None, 
             include_departments: bool = True) -> dict:
        """Generate financial report for specified period"""
        
        try:
            # Determine date range
            today = datetime.now()
            
            if report_type == "daily":
                start_dt = today
                end_dt = today
                period_name = today.strftime('%Y-%m-%d')
            elif report_type == "weekly":
                start_dt = today - timedelta(days=7)
                end_dt = today
                period_name = f"Last 7 Days"
            elif report_type == "monthly":
                start_dt = today.replace(day=1)
                end_dt = today
                period_name = today.strftime('%B %Y')
            else:  # custom
                if not start_date or not end_date:
                    return {'success': False, 'message': 'Start date and end date required for custom report'}
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                period_name = f"{start_date} to {end_date}"
            
            start_str = start_dt.strftime('%Y-%m-%d')
            end_str = end_dt.strftime('%Y-%m-%d')
            
            # Load databases
            billings = load_db(BILLING_DB_FILE)
            payments = load_db(PAYMENTS_DB_FILE)
            
            # Filter by date range
            period_invoices = [
                b for b in billings 
                if start_str <= b.get('invoice_date', '9999-99-99') <= end_str
            ]
            
            period_payments = [
                p for p in payments 
                if start_str <= p.get('payment_date', '9999-99-99') <= end_str
            ]
            
            # Calculate totals
            total_invoiced = sum(inv.get('total_amount', 0) for inv in period_invoices)
            total_payments = sum(pay.get('payment_amount', 0) for pay in period_payments)
            total_outstanding = sum(inv.get('balance_due', 0) for inv in period_invoices)
            
            # Count statistics
            invoice_count = len(period_invoices)
            payment_count = len(period_payments)
            
            # Department breakdown
            dept_revenue = {
                'Appointments': 0.0,
                'Lab Tests': 0.0,
                'Pharmacy': 0.0,
                'Additional': 0.0
            }
            
            if include_departments:
                for inv in period_invoices:
                    for item in inv.get('items', []):
                        item_type = item.get('type', 'Additional')
                        amount = item.get('amount', 0)
                        
                        if item_type == 'Appointment':
                            dept_revenue['Appointments'] += amount
                        elif item_type == 'Lab Test':
                            dept_revenue['Lab Tests'] += amount
                        elif item_type == 'Pharmacy':
                            dept_revenue['Pharmacy'] += amount
                        else:
                            dept_revenue['Additional'] += amount
            
            # Payment method breakdown
            payment_methods = {}
            for pay in period_payments:
                method = pay.get('payment_method', 'Unknown')
                payment_methods[method] = payment_methods.get(method, 0) + pay.get('payment_amount', 0)
            
            # Format output
            output = f"\n{'='*60}\n"
            output += f"📊 FINANCIAL REPORT\n"
            output += f"{'='*60}\n\n"
            output += f"📅 Period: {period_name}\n"
            output += f"📆 Date Range: {start_str} to {end_str}\n"
            output += f"🕒 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            output += f"\n{'='*60}\n"
            output += f"REVENUE SUMMARY\n"
            output += f"{'='*60}\n\n"
            output += f"💰 Total Invoiced: ${total_invoiced:.2f}\n"
            output += f"✅ Total Payments Received: ${total_payments:.2f}\n"
            output += f"⚠️ Total Outstanding: ${total_outstanding:.2f}\n"
            output += f"📄 Invoices Generated: {invoice_count}\n"
            output += f"💳 Payments Processed: {payment_count}\n"
            
            if total_invoiced > 0:
                collection_rate = (total_payments / total_invoiced) * 100
                output += f"📊 Collection Rate: {collection_rate:.1f}%\n"
            
            if include_departments and dept_revenue:
                output += f"\n{'='*60}\n"
                output += f"DEPARTMENT BREAKDOWN\n"
                output += f"{'='*60}\n\n"
                
                for dept, revenue in sorted(dept_revenue.items(), key=lambda x: x[1], reverse=True):
                    if revenue > 0:
                        percentage = (revenue / total_invoiced * 100) if total_invoiced > 0 else 0
                        output += f"• {dept}: ${revenue:.2f} ({percentage:.1f}%)\n"
            
            if payment_methods:
                output += f"\n{'='*60}\n"
                output += f"PAYMENT METHODS\n"
                output += f"{'='*60}\n\n"
                
                for method, amount in sorted(payment_methods.items(), key=lambda x: x[1], reverse=True):
                    percentage = (amount / total_payments * 100) if total_payments > 0 else 0
                    output += f"• {method}: ${amount:.2f} ({percentage:.1f}%)\n"
            
            output += f"\n{'='*60}\n"
            output += f"💡 INSIGHTS\n"
            output += f"{'='*60}\n\n"
            
            if total_invoiced > 0:
                if collection_rate >= 90:
                    output += f"✅ Excellent collection rate ({collection_rate:.1f}%)\n"
                elif collection_rate >= 70:
                    output += f"⚠️ Good collection rate, room for improvement ({collection_rate:.1f}%)\n"
                else:
                    output += f"🔴 Low collection rate, review billing processes ({collection_rate:.1f}%)\n"
            
            if total_outstanding > total_invoiced * 0.3:
                output += f"⚠️ High outstanding balance - consider payment reminders\n"
            
            if invoice_count > 0:
                avg_invoice = total_invoiced / invoice_count
                output += f"📊 Average invoice value: ${avg_invoice:.2f}\n"
            
            output += f"\n{'='*60}\n"
            
            return {
                'success': True,
                'message': output,
                'report': {
                    'period': period_name,
                    'start_date': start_str,
                    'end_date': end_str,
                    'total_invoiced': total_invoiced,
                    'total_payments': total_payments,
                    'total_outstanding': total_outstanding,
                    'invoice_count': invoice_count,
                    'payment_count': payment_count,
                    'collection_rate': (total_payments / total_invoiced * 100) if total_invoiced > 0 else 0,
                    'department_revenue': dept_revenue,
                    'payment_methods': payment_methods
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error generating financial report: {str(e)}'}

# Export all tools
__all__ = [
    'GenerateInvoiceTool',
    'VerifyInsuranceCoverageTool',
    'ProcessInsuranceClaimTool',
    'RecordPaymentTool',
    'GetPatientBalanceTool',
    'GenerateFinancialReportTool'
]
