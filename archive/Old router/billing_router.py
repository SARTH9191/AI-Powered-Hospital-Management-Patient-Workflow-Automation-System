"""Billing & Insurance Management Router - API Endpoints
==========================================================

This router provides comprehensive billing and insurance management:
- Generate invoices for services rendered
- Verify insurance coverage
- Process insurance claims
- Record payments (cash, card, insurance)
- Get patient balance and payment history
- Generate financial reports and analytics

All endpoints are protected with role-based access control.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import os
from api.auth import get_current_user, require_admin, require_doctor, require_staff

# Import billing and insurance tools
from tools.billing_tool import (
    GenerateInvoiceTool,
    VerifyInsuranceCoverageTool,
    ProcessInsuranceClaimTool,
    RecordPaymentTool,
    GetPatientBalanceTool,
    GenerateFinancialReportTool
)

router = APIRouter()

# Initialize tools
generate_invoice_tool = GenerateInvoiceTool()
verify_insurance_tool = VerifyInsuranceCoverageTool()
process_claim_tool = ProcessInsuranceClaimTool()
record_payment_tool = RecordPaymentTool()
get_balance_tool = GetPatientBalanceTool()
generate_report_tool = GenerateFinancialReportTool()

# =====================================================
# Pydantic Models
# =====================================================

class GenerateInvoiceRequest(BaseModel):
    """Request model for generating invoice"""
    patient_id: str = Field(..., description="Patient ID (e.g., REG2025123456)")
    services: List[Dict[str, Any]] = Field(..., description="List of services with name, quantity, and price")
    doctor_id: Optional[str] = Field(None, description="Doctor ID who provided service")
    notes: Optional[str] = Field(None, description="Additional notes or special instructions")

class VerifyInsuranceRequest(BaseModel):
    """Request model for verifying insurance coverage"""
    patient_id: str = Field(..., description="Patient ID")
    service_codes: List[str] = Field(..., description="List of service/procedure codes to verify")

class ProcessClaimRequest(BaseModel):
    """Request model for processing insurance claim"""
    invoice_id: str = Field(..., description="Invoice ID to process claim for")
    insurance_policy_number: str = Field(..., description="Insurance policy number")
    claim_details: Optional[Dict[str, Any]] = Field(None, description="Additional claim details")

class RecordPaymentRequest(BaseModel):
    """Request model for recording payment"""
    patient_id: str = Field(..., description="Patient ID")
    invoice_id: str = Field(..., description="Invoice ID being paid")
    amount: float = Field(..., description="Payment amount", gt=0)
    payment_method: str = Field(..., description="Payment method: Cash, Credit Card, Debit Card, Insurance, Check")
    transaction_id: Optional[str] = Field(None, description="Transaction/reference ID")
    notes: Optional[str] = Field(None, description="Payment notes")

class APIResponse(BaseModel):
    """Standard API response format"""
    success: bool
    data: Any
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# =====================================================
# Endpoints
# =====================================================

@router.get("/", response_model=APIResponse)
async def billing_info(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get information about the Billing & Insurance API
    
    Returns list of available endpoints and their descriptions.
    """
    return {
        "success": True,
        "data": {
            "endpoints": [
                "GET / - API information",
                "POST /invoice - Generate invoice",
                "GET /invoice/{invoice_id} - Get invoice details",
                "POST /insurance/verify - Verify insurance coverage",
                "POST /insurance/claim - Process insurance claim",
                "POST /payment - Record payment",
                "GET /patient/{patient_id}/balance - Get patient balance",
                "GET /patient/{patient_id}/payments - Get payment history",
                "GET /reports/financial - Generate financial report"
            ],
            "tools_available": 6,
            "description": "Comprehensive billing, insurance, and financial management"
        },
        "message": "Billing & Insurance Management API",
        "timestamp": datetime.now().isoformat()
    }


@router.post("/invoice", response_model=APIResponse)
async def generate_invoice(
    request: GenerateInvoiceRequest,
    current_user: Dict = Depends(require_staff)
):
    """
    Generate invoice for services rendered
    
    **Access:** Staff, Doctor, Admin
    
    **Parameters:**
    - patient_id: Patient ID
    - services: List of services with name, quantity, price
    - doctor_id: Doctor who provided service (optional)
    - notes: Additional notes (optional)
    
    **Returns:** Generated invoice with invoice ID and total amount
    """
    try:
        result = generate_invoice_tool._run(
            patient_id=request.patient_id,
            services=request.services,
            doctor_id=request.doctor_id,
            notes=request.notes
        )
        
        # Check for errors
        if "❌" in result or "Error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result
            )
        
        return {
            "success": True,
            "data": {"invoice": result},
            "message": "Invoice generated successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate invoice: {str(e)}"
        )


@router.get("/invoice/{invoice_id}", response_model=APIResponse)
async def get_invoice_details(
    invoice_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get details of a specific invoice
    
    **Access:** All authenticated users
    
    **Parameters:**
    - invoice_id: Invoice ID
    
    **Returns:** Complete invoice details with services and amounts
    """
    try:
        # This would typically load invoice from database
        # For now, return a placeholder response
        return {
            "success": True,
            "data": {
                "invoice_id": invoice_id,
                "message": "Invoice details retrieval endpoint - implementation pending"
            },
            "message": "Invoice details retrieved",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get invoice: {str(e)}"
        )


@router.post("/insurance/verify", response_model=APIResponse)
async def verify_insurance_coverage(
    request: VerifyInsuranceRequest,
    current_user: Dict = Depends(require_staff)
):
    """
    Verify insurance coverage for services
    
    **Access:** Staff, Doctor, Admin
    
    **Parameters:**
    - patient_id: Patient ID
    - service_codes: List of service/procedure codes
    
    **Returns:** Coverage details with covered amounts and copays
    """
    try:
        result = verify_insurance_tool._run(
            patient_id=request.patient_id,
            service_codes=request.service_codes
        )
        
        # Check for errors
        if "❌" in result or "Error" in result:
            if "not found" in result or "No insurance" in result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result
            )
        
        return {
            "success": True,
            "data": {"coverage_info": result},
            "message": "Insurance coverage verified successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify insurance coverage: {str(e)}"
        )


@router.post("/insurance/claim", response_model=APIResponse)
async def process_insurance_claim(
    request: ProcessClaimRequest,
    current_user: Dict = Depends(require_staff)
):
    """
    Process insurance claim for invoice
    
    **Access:** Staff, Doctor, Admin
    
    **Parameters:**
    - invoice_id: Invoice ID
    - insurance_policy_number: Insurance policy number
    - claim_details: Additional claim information (optional)
    
    **Returns:** Claim processing result with claim ID and status
    """
    try:
        result = process_claim_tool._run(
            invoice_id=request.invoice_id,
            insurance_policy_number=request.insurance_policy_number,
            claim_details=request.claim_details
        )
        
        # Check for errors
        if "❌" in result or "Error" in result:
            if "not found" in result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result
            )
        
        return {
            "success": True,
            "data": {"claim_info": result},
            "message": "Insurance claim processed successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process insurance claim: {str(e)}"
        )


@router.post("/payment", response_model=APIResponse)
async def record_payment(
    request: RecordPaymentRequest,
    current_user: Dict = Depends(require_staff)
):
    """
    Record payment for invoice
    
    **Access:** Staff, Admin
    
    **Parameters:**
    - patient_id: Patient ID
    - invoice_id: Invoice ID
    - amount: Payment amount
    - payment_method: Cash, Credit Card, Debit Card, Insurance, Check
    - transaction_id: Transaction reference ID (optional)
    - notes: Payment notes (optional)
    
    **Returns:** Payment confirmation with payment ID and receipt
    """
    try:
        result = record_payment_tool._run(
            patient_id=request.patient_id,
            invoice_id=request.invoice_id,
            amount=request.amount,
            payment_method=request.payment_method,
            transaction_id=request.transaction_id,
            notes=request.notes
        )
        
        # Check for errors
        if "❌" in result or "Error" in result:
            if "not found" in result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result
            )
        
        return {
            "success": True,
            "data": {"payment_details": result},
            "message": "Payment recorded successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record payment: {str(e)}"
        )


@router.get("/patient/{patient_id}/balance", response_model=APIResponse)
async def get_patient_balance(
    patient_id: str,
    current_user: Dict = Depends(require_staff)
):
    """
    Get patient's outstanding balance
    
    **Access:** Staff, Doctor, Admin
    
    **Parameters:**
    - patient_id: Patient ID
    
    **Returns:** Outstanding balance with breakdown of unpaid invoices
    """
    try:
        result = get_balance_tool._run(patient_id=patient_id)
        
        # Check for errors
        if "❌" in result or "Error" in result:
            if "not found" in result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result
            )
        
        return {
            "success": True,
            "data": {"balance_info": result},
            "message": "Patient balance retrieved successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get patient balance: {str(e)}"
        )


@router.get("/patient/{patient_id}/payments", response_model=APIResponse)
async def get_patient_payment_history(
    patient_id: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: Dict = Depends(require_staff)
):
    """
    Get patient's payment history
    
    **Access:** Staff, Doctor, Admin
    
    **Parameters:**
    - patient_id: Patient ID
    - start_date: Filter start date (optional)
    - end_date: Filter end date (optional)
    
    **Returns:** Complete payment history with dates, amounts, methods
    """
    try:
        # This would typically query payment records from database
        # For now, return a placeholder response
        return {
            "success": True,
            "data": {
                "patient_id": patient_id,
                "filters": {"start_date": start_date, "end_date": end_date},
                "message": "Payment history retrieval endpoint - implementation pending"
            },
            "message": "Payment history retrieved",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get payment history: {str(e)}"
        )


@router.get("/reports/financial", response_model=APIResponse)
async def generate_financial_report(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    report_type: Optional[str] = Query("summary", description="Report type: summary, detailed, by_doctor"),
    current_user: Dict = Depends(require_admin)
):
    """
    Generate financial report and analytics
    
    **Access:** Admin only
    
    **Parameters:**
    - start_date: Report start date (optional)
    - end_date: Report end date (optional)
    - report_type: summary, detailed, or by_doctor
    
    **Returns:** Comprehensive financial report with:
    - Total revenue
    - Revenue by service type
    - Insurance vs out-of-pocket
    - Outstanding balances
    - Payment method breakdown
    """
    try:
        result = generate_report_tool._run(
            start_date=start_date,
            end_date=end_date,
            report_type=report_type
        )
        
        return {
            "success": True,
            "data": {"financial_report": result},
            "message": "Financial report generated successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate financial report: {str(e)}"
        )


# =====================================================
# NEW ENDPOINT: Get Patient Invoices (for frontend)
# =====================================================

@router.get("/patient/{patient_id}/invoices", response_model=APIResponse)
async def get_patient_invoices(
    patient_id: str,
    status_filter: Optional[str] = Query(None, description="Filter by status: pending, paid, partially_paid, overdue, cancelled"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get all invoices for a patient (returns JSON array for frontend)
    
    **Access:** Patient (own data), Staff, Doctor, Admin
    
    **Parameters:**
    - patient_id: Patient ID
    - status_filter: Optional status filter
    
    **Returns:** JSON array of invoices with calculated totals
    """
    try:
        # Patients can only access their own invoices
        user_role = current_user.get('role')
        user_id = current_user.get('user_id')
        
        if user_role == 'patient' and user_id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Patients can only access their own invoices"
            )
        
        # Read invoices database directly
        db_path = os.path.join('data', 'billing_database.json')
        
        if not os.path.exists(db_path):
            return {
                "success": True,
                "data": {"invoices": [], "total_balance": 0.0},
                "message": "No invoices found",
                "timestamp": datetime.now().isoformat()
            }
        
        with open(db_path, 'r') as f:
            billing_data = json.load(f)
        
        # Get all invoices from the nested structure
        all_invoices = billing_data.get('invoices', [])
        
        # Filter by patient_id
        patient_invoices = [
            invoice for invoice in all_invoices
            if invoice.get('patient_id') == patient_id
        ]
        
        # Apply status filter if provided
        if status_filter:
            patient_invoices = [
                invoice for invoice in patient_invoices
                if invoice.get('status') == status_filter
            ]
        
        # Calculate total outstanding balance
        total_balance = sum(
            invoice.get('balance', 0.0)
            for invoice in patient_invoices
            if invoice.get('status') in ['pending', 'partially_paid', 'overdue']
        )
        
        return {
            "success": True,
            "data": {
                "invoices": patient_invoices,
                "total_balance": total_balance
            },
            "message": f"Found {len(patient_invoices)} invoices",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get patient invoices: {str(e)}"
        )
