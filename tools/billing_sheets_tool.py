"""
Google Sheets Billing Integration Tools
Integrates with Google Sheets for billing, payment tracking, and invoice management

This tool connects with Google Sheets to:
- Create billing records
- Track payments and costs
- Generate invoices  
- Monitor payment status
- Update financial records

Author: Hospital Management AI System
"""

import os
import json
import pickle
from typing import Optional, Type, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from pydantic import BaseModel, Field
from langchain.tools import BaseTool


# ==================== BILLING SHEET CONFIG ====================

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Environment variables for sheet IDs
BILLING_SHEET_ID = os.getenv('BILLING_SHEET_ID', '1BillingSheetID12345')
INVOICE_SHEET_ID = os.getenv('INVOICE_SHEET_ID', '1InvoiceSheetID12345')
PAYMENT_TRACKING_SHEET_ID = os.getenv('PAYMENT_TRACKING_SHEET_ID', '1PaymentTrackingID12345')


# ==================== INPUT SCHEMAS ====================

class CreateBillingRecordInput(BaseModel):
    """Input schema for creating billing records."""
    patient_id: str = Field(description="Patient's unique ID")
    patient_name: str = Field(description="Patient's full name") 
    patient_email: str = Field(description="Patient's email address")
    service_type: str = Field(description="Type of service (consultation, lab_test, procedure, etc.)")
    service_name: str = Field(description="Name of the service")
    amount: float = Field(description="Service amount in currency")
    insurance_coverage: Optional[float] = Field(default=0.0, description="Insurance coverage percentage (0-100)")
    date: Optional[str] = Field(default=None, description="Service date (YYYY-MM-DD)")

class ReadBillingInfoInput(BaseModel):
    """Input schema for reading billing information."""
    patient_id: str = Field(description="Patient's unique ID")
    include_pending: bool = Field(default=True, description="Include pending payments")
    include_paid: bool = Field(default=True, description="Include completed payments")

class UpdatePaymentStatusInput(BaseModel):
    """Input schema for updating payment status."""
    invoice_id: str = Field(description="Invoice ID to update")
    payment_status: str = Field(description="Payment status (pending, paid, partial, failed)")
    payment_method: Optional[str] = Field(default=None, description="Payment method (cash, card, upi, insurance)")
    payment_amount: Optional[float] = Field(default=None, description="Amount paid")
    payment_date: Optional[str] = Field(default=None, description="Payment date (YYYY-MM-DD)")

class GenerateInvoiceInput(BaseModel):
    """Input schema for generating invoices."""
    patient_id: str = Field(description="Patient's unique ID")
    services: List[Dict[str, Any]] = Field(description="List of services to include in invoice")
    due_date: Optional[str] = Field(default=None, description="Invoice due date (YYYY-MM-DD)")


# ==================== BASE CLASS ====================

class BillingSheetsToolBase(BaseTool):
    """Base class for Google Sheets billing tools."""
    
    # Define service as a class variable to avoid Pydantic field validation
    service: Any = None
    
    def __init__(self):
        super().__init__()
        # Use object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, 'service', self._initialize_sheets_service())
    
    def _initialize_sheets_service(self):
        """Initialize Google Sheets service."""
        try:
            creds = None
            # Use existing sheets_token.pickle file in project root
            token_path = os.path.join(os.path.dirname(__file__), '..', 'sheets_token.pickle')
            credentials_path = os.path.join(os.path.dirname(__file__), '..', 'credentials', 'client_secret.json')
            
            if os.path.exists(token_path):
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next run  
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
            
            service = build('sheets', 'v4', credentials=creds)
            print("✅ Google Sheets service initialized for billing")
            return service
            
        except Exception as e:
            print(f"❌ Error initializing Sheets service: {e}")
            return None
    
    def _get_current_timestamp(self):
        """Get current timestamp in ISO format."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _calculate_final_amount(self, amount: float, insurance_coverage: float) -> float:
        """Calculate final amount after insurance."""
        if insurance_coverage > 0:
            covered_amount = amount * (insurance_coverage / 100)
            return amount - covered_amount
        return amount
    
    def _generate_invoice_id(self, patient_id: str) -> str:
        """Generate unique invoice ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"INV_{patient_id}_{timestamp}"


# ==================== BILLING TOOLS ====================

class CreateBillingRecordTool(BillingSheetsToolBase):
    """Creates a new billing record in Google Sheets."""
    
    name: str = "create_billing_record"
    description: str = """Creates a billing record for a patient service in Google Sheets.
    
    Use this tool to:
    - Record new charges for services (consultations, tests, procedures)
    - Track service costs and insurance coverage
    - Create billing entries for future invoice generation
    - Maintain financial records in sheets
    
    Required: patient_id, patient_name, patient_email, service_type, service_name, amount
    Optional: insurance_coverage, date
    """
    args_schema: Type[BaseModel] = CreateBillingRecordInput
    
    def _run(self, patient_id: str, patient_name: str, patient_email: str, 
             service_type: str, service_name: str, amount: float,
             insurance_coverage: float = 0.0, date: str = None) -> str:
        """Execute the billing record creation."""
        
        if not self.service:
            return "❌ Error: Google Sheets service not available"
        
        try:
            # Use current date if not provided
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            
            # Calculate final amount after insurance
            final_amount = self._calculate_final_amount(amount, insurance_coverage)
            
            # Generate billing record ID
            record_id = f"BILL_{patient_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Prepare row data
            row_data = [
                record_id,           # Billing Record ID
                patient_id,          # Patient ID
                patient_name,        # Patient Name
                patient_email,       # Patient Email
                service_type,        # Service Type
                service_name,        # Service Name
                amount,              # Original Amount
                f"{insurance_coverage}%",  # Insurance Coverage
                final_amount,        # Final Amount
                "Pending",           # Payment Status
                date,                # Service Date
                self._get_current_timestamp(),  # Created At
                ""                   # Notes
            ]
            
            # Append to billing sheet
            result = self.service.spreadsheets().values().append(
                spreadsheetId=BILLING_SHEET_ID,
                range='Sheet1!A:M',
                valueInputOption='USER_ENTERED',
                body={'values': [row_data]}
            ).execute()
            
            return f"""✅ Billing Record Created Successfully!

📋 **Record Details:**
   • Record ID: {record_id}
   • Patient: {patient_name} ({patient_id})
   • Service: {service_name} ({service_type})
   • Amount: ₹{amount:.2f}
   • Insurance: {insurance_coverage}% coverage
   • Final Amount: ₹{final_amount:.2f}
   • Status: Pending
   • Date: {date}

💡 **Next Steps:**
   • Generate invoice when ready
   • Update payment status when paid
   • Patient can view charges in their portal
"""
        
        except HttpError as e:
            return f"❌ Error creating billing record: {e}"
        except Exception as e:
            return f"❌ Unexpected error: {e}"


class ReadBillingInfoTool(BillingSheetsToolBase):
    """Reads billing information for a patient from Google Sheets."""
    
    name: str = "read_billing_info"
    description: str = """Reads all billing information for a patient from Google Sheets.
    
    Use this tool to:
    - Get patient's outstanding charges
    - View payment history
    - Check insurance coverage details
    - Display billing summary to patient
    
    Required: patient_id
    Optional: include_pending, include_paid
    """
    args_schema: Type[BaseModel] = ReadBillingInfoInput
    
    def _run(self, patient_id: str, include_pending: bool = True, include_paid: bool = True) -> str:
        """Execute the billing information retrieval."""
        
        if not self.service:
            return "❌ Error: Google Sheets service not available"
        
        try:
            # Read all billing data
            result = self.service.spreadsheets().values().get(
                spreadsheetId=BILLING_SHEET_ID,
                range='Sheet1!A:M'
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return f"📋 No billing records found for patient {patient_id}"
            
            # Filter records for this patient
            patient_records = []
            total_pending = 0.0
            total_paid = 0.0
            
            headers = values[0] if values else []
            
            for row in values[1:]:  # Skip header
                if len(row) > 1 and row[1] == patient_id:  # Patient ID column
                    status = row[9] if len(row) > 9 else "Unknown"  # Payment Status column
                    
                    if status.lower() == "pending" and include_pending:
                        patient_records.append(row)
                        total_pending += float(row[8]) if len(row) > 8 and row[8] else 0.0
                    elif status.lower() in ["paid", "completed"] and include_paid:
                        patient_records.append(row)
                        total_paid += float(row[8]) if len(row) > 8 and row[8] else 0.0
                    elif status.lower() not in ["pending", "paid", "completed"]:
                        patient_records.append(row)
            
            if not patient_records:
                return f"📋 No billing records found for patient {patient_id}"
            
            # Format response
            response = f"""💰 **Billing Information for Patient {patient_id}**\n\n"""
            
            # Summary
            response += f"""📊 **Summary:**
   • Pending Amount: ₹{total_pending:.2f}
   • Paid Amount: ₹{total_paid:.2f}
   • Total Records: {len(patient_records)}

📋 **Detailed Records:**\n"""
            
            for record in patient_records:
                if len(record) >= 10:
                    service_name = record[5] if len(record) > 5 else "Unknown"
                    amount = record[8] if len(record) > 8 else "0.00"
                    status = record[9] if len(record) > 9 else "Unknown"
                    date = record[10] if len(record) > 10 else "Unknown"
                    
                    status_emoji = "💰" if status.lower() == "paid" else "⏳" if status.lower() == "pending" else "❓"
                    
                    response += f"""
   {status_emoji} **{service_name}**
      • Amount: ₹{amount}
      • Status: {status}
      • Date: {date}"""
            
            return response
        
        except HttpError as e:
            return f"❌ Error reading billing info: {e}"
        except Exception as e:
            return f"❌ Unexpected error: {e}"


class UpdatePaymentStatusTool(BillingSheetsToolBase):
    """Updates payment status for a billing record in Google Sheets."""
    
    name: str = "update_payment_status"
    description: str = """Updates the payment status of a billing record in Google Sheets.
    
    Use this tool to:
    - Mark invoices as paid/pending/failed
    - Record payment method and amount
    - Update payment dates
    - Track payment history
    
    Required: invoice_id, payment_status
    Optional: payment_method, payment_amount, payment_date
    """
    args_schema: Type[BaseModel] = UpdatePaymentStatusInput
    
    def _run(self, invoice_id: str, payment_status: str, 
             payment_method: str = None, payment_amount: float = None, 
             payment_date: str = None) -> str:
        """Execute the payment status update."""
        
        if not self.service:
            return "❌ Error: Google Sheets service not available"
        
        try:
            # Use current date if not provided
            if not payment_date and payment_status.lower() == "paid":
                payment_date = datetime.now().strftime("%Y-%m-%d")
            
            # Read current data to find the record
            result = self.service.spreadsheets().values().get(
                spreadsheetId=BILLING_SHEET_ID,
                range='Sheet1!A:M'
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return f"❌ No billing records found"
            
            # Find the record to update
            row_index = None
            for i, row in enumerate(values):
                if len(row) > 0 and row[0] == invoice_id:  # Record ID column
                    row_index = i + 1  # +1 because sheets are 1-indexed
                    break
            
            if row_index is None:
                return f"❌ Invoice {invoice_id} not found"
            
            # Update payment status
            updates = []
            
            # Payment Status (column J)
            updates.append({
                'range': f'Sheet1!J{row_index}',
                'values': [[payment_status]]
            })
            
            # Payment Method (add new column if needed)
            if payment_method:
                updates.append({
                    'range': f'Sheet1!N{row_index}',
                    'values': [[payment_method]]
                })
            
            # Payment Amount (add new column if needed)
            if payment_amount:
                updates.append({
                    'range': f'Sheet1!O{row_index}',
                    'values': [[payment_amount]]
                })
            
            # Payment Date (add new column if needed)
            if payment_date:
                updates.append({
                    'range': f'Sheet1!P{row_index}',
                    'values': [[payment_date]]
                })
            
            # Batch update
            batch_body = {
                'valueInputOption': 'USER_ENTERED',
                'data': updates
            }
            
            result = self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=BILLING_SHEET_ID,
                body=batch_body
            ).execute()
            
            return f"""✅ Payment Status Updated Successfully!

💳 **Update Details:**
   • Invoice ID: {invoice_id}
   • Status: {payment_status}
   • Method: {payment_method or 'Not specified'}
   • Amount: ₹{payment_amount or 'Not specified'}
   • Date: {payment_date or 'Not specified'}

📊 **Record Updated:** Row {row_index} in billing sheet
"""
        
        except HttpError as e:
            return f"❌ Error updating payment status: {e}"
        except Exception as e:
            return f"❌ Unexpected error: {e}"


class GenerateInvoiceTool(BillingSheetsToolBase):
    """Generates an invoice from billing records in Google Sheets."""
    
    name: str = "generate_invoice"
    description: str = """Generates a comprehensive invoice for a patient from their billing records.
    
    Use this tool to:
    - Create invoices from pending charges
    - Combine multiple services into one invoice
    - Set payment due dates
    - Generate invoice for patient billing
    
    Required: patient_id, services
    Optional: due_date
    """
    args_schema: Type[BaseModel] = GenerateInvoiceInput
    
    def _run(self, patient_id: str, services: List[Dict[str, Any]], due_date: str = None) -> str:
        """Execute the invoice generation."""
        
        if not self.service:
            return "❌ Error: Google Sheets service not available"
        
        try:
            # Generate invoice ID
            invoice_id = self._generate_invoice_id(patient_id)
            
            # Use 30 days from now as default due date
            if not due_date:
                due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            
            # Calculate total
            total_amount = 0.0
            total_insurance = 0.0
            final_total = 0.0
            
            invoice_lines = []
            
            for service in services:
                amount = float(service.get('amount', 0))
                insurance = float(service.get('insurance_coverage', 0))
                final_amt = self._calculate_final_amount(amount, insurance)
                
                total_amount += amount
                total_insurance += (amount * insurance / 100) if insurance > 0 else 0
                final_total += final_amt
                
                invoice_lines.append([
                    service.get('service_name', 'Unknown Service'),
                    service.get('service_type', 'General'),
                    amount,
                    f"{insurance}%",
                    final_amt
                ])
            
            # Create invoice record
            invoice_data = [
                invoice_id,                    # Invoice ID
                patient_id,                    # Patient ID
                datetime.now().strftime("%Y-%m-%d"),  # Invoice Date
                due_date,                      # Due Date
                total_amount,                  # Subtotal
                total_insurance,               # Insurance Discount
                final_total,                   # Final Total
                "Generated",                   # Status
                json.dumps(invoice_lines),     # Line Items (JSON)
                self._get_current_timestamp()  # Created At
            ]
            
            # Add to invoice sheet
            result = self.service.spreadsheets().values().append(
                spreadsheetId=INVOICE_SHEET_ID,
                range='Sheet1!A:J',
                valueInputOption='USER_ENTERED',
                body={'values': [invoice_data]}
            ).execute()
            
            # Format invoice for display
            invoice_display = f"""🧾 **INVOICE GENERATED**

📋 **Invoice Details:**
   • Invoice ID: {invoice_id}
   • Patient ID: {patient_id}
   • Invoice Date: {datetime.now().strftime("%Y-%m-%d")}
   • Due Date: {due_date}

💰 **Charges:**"""
            
            for line in invoice_lines:
                invoice_display += f"""
   • {line[0]} ({line[1]}): ₹{line[2]:.2f}
     Insurance Coverage: {line[3]} = ₹{line[2] - line[4]:.2f}
     You Pay: ₹{line[4]:.2f}"""
            
            invoice_display += f"""

📊 **Summary:**
   • Subtotal: ₹{total_amount:.2f}
   • Insurance Discount: -₹{total_insurance:.2f}
   • **Final Amount Due: ₹{final_total:.2f}**

💳 **Payment Instructions:**
   • Pay by: {due_date}
   • Contact billing for payment options
   • Keep this invoice for your records
"""
            
            return invoice_display
        
        except HttpError as e:
            return f"❌ Error generating invoice: {e}"
        except Exception as e:
            return f"❌ Unexpected error: {e}"


class GetBillingSummaryTool(BillingSheetsToolBase):
    """Gets a comprehensive billing summary for analytics."""
    
    name: str = "get_billing_summary"
    description: str = """Gets comprehensive billing analytics and summary from Google Sheets.
    
    Use this tool to:
    - Get hospital revenue analytics
    - View payment trends
    - Monitor outstanding amounts
    - Generate financial reports
    
    No required parameters - returns overall billing summary
    """
    
    def _run(self) -> str:
        """Execute the billing summary retrieval."""
        
        if not self.service:
            return "❌ Error: Google Sheets service not available"
        
        try:
            # Read all billing data
            result = self.service.spreadsheets().values().get(
                spreadsheetId=BILLING_SHEET_ID,
                range='Sheet1!A:M'
            ).execute()
            
            values = result.get('values', [])
            if len(values) <= 1:  # Only header or empty
                return "📊 No billing data available"
            
            # Calculate statistics
            total_revenue = 0.0
            total_pending = 0.0
            total_paid = 0.0
            service_stats = {}
            patient_count = set()
            
            for row in values[1:]:  # Skip header
                if len(row) >= 10:
                    patient_id = row[1]
                    service_type = row[4]
                    amount = float(row[8]) if row[8] else 0.0
                    status = row[9].lower() if row[9] else "unknown"
                    
                    patient_count.add(patient_id)
                    total_revenue += amount
                    
                    if status == "pending":
                        total_pending += amount
                    elif status in ["paid", "completed"]:
                        total_paid += amount
                    
                    # Service statistics
                    if service_type not in service_stats:
                        service_stats[service_type] = {"count": 0, "revenue": 0.0}
                    service_stats[service_type]["count"] += 1
                    service_stats[service_type]["revenue"] += amount
            
            # Format summary
            summary = f"""📊 **BILLING ANALYTICS SUMMARY**

💰 **Financial Overview:**
   • Total Revenue: ₹{total_revenue:.2f}
   • Amount Paid: ₹{total_paid:.2f}
   • Pending Payments: ₹{total_pending:.2f}
   • Collection Rate: {(total_paid/total_revenue*100) if total_revenue > 0 else 0:.1f}%

👥 **Patient Statistics:**
   • Total Patients: {len(patient_count)}
   • Total Records: {len(values)-1}
   • Avg Revenue/Patient: ₹{total_revenue/len(patient_count) if patient_count else 0:.2f}

🏥 **Service Breakdown:**"""
            
            for service, stats in sorted(service_stats.items(), key=lambda x: x[1]["revenue"], reverse=True):
                summary += f"""
   • {service}: {stats['count']} services, ₹{stats['revenue']:.2f} revenue"""
            
            return summary
        
        except HttpError as e:
            return f"❌ Error getting billing summary: {e}"
        except Exception as e:
            return f"❌ Unexpected error: {e}"