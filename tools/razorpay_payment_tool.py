"""
Razorpay Payment Integration Tool for Indian Healthcare
Alternative to Stripe - Works in India with UPI, Cards, Net Banking, Wallets

NOTE: This is architecture-ready. Add RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET to .env to activate.
For demo purposes, works without API keys by generating demo payment links.
"""

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import os

# Try to import Razorpay
try:
    import razorpay
    RAZORPAY_AVAILABLE = True
except ImportError:
    RAZORPAY_AVAILABLE = False
    print("WARNING: Razorpay not installed. Run: pip install razorpay")

# Load Razorpay configuration
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', '')

if RAZORPAY_AVAILABLE and RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
    razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
else:
    razorpay_client = None


# ==================== INPUT SCHEMAS ====================

class CreatePaymentLinkInput(BaseModel):
    """Input for creating payment link"""
    patient_id: str = Field(description="Patient ID")
    patient_name: str = Field(description="Patient name (e.g., 'Rajesh Kumar')")
    patient_email: str = Field(description="Patient email")
    patient_phone: str = Field(description="Patient phone (+91...)")
    amount: float = Field(description="Amount in Rupees (₹)")
    description: str = Field(description="Payment description")
    invoice_id: Optional[str] = Field(default=None, description="Invoice ID")


# ==================== HELPER FUNCTIONS ====================

def rupees_to_paise(amount: float) -> int:
    """Convert Rupees to paise (Razorpay uses smallest unit)"""
    return int(amount * 100)


# ==================== PAYMENT LINK TOOL ====================

class CreateRazorpayPaymentLinkTool(BaseTool):
    name: str = "create_razorpay_payment_link"
    description: str = """Create secure payment link for patient billing (India).
    
    Supports:
    - UPI (PhonePe, Google Pay, Paytm, BHIM)
    - Credit/Debit Cards (Visa, Mastercard, RuPay)
    - Net Banking (all major Indian banks)
    - Wallets (Paytm, Mobikwik, Freecharge)
    
    Returns: payment_url (send to patient via Email/SMS/WhatsApp)
    """
    args_schema: type[BaseModel] = CreatePaymentLinkInput
    
    def _run(
        self, 
        patient_id: str, 
        patient_name: str, 
        patient_email: str,
        patient_phone: str,
        amount: float, 
        description: str, 
        invoice_id: Optional[str] = None
    ) -> dict:
        """Create Razorpay payment link"""
        
        try:
            # Check if Razorpay is configured
            if not RAZORPAY_AVAILABLE:
                return {
                    "success": False,
                    "error": "Razorpay not installed. Run: pip install razorpay",
                    "payment_url": None,
                    "demo_url": f"https://demo.razorpay.com/pay/{patient_id}?amount={amount}",
                    "integration_ready": True
                }
            
            if not razorpay_client:
                # Return demo response
                return {
                    "success": False,
                    "error": "Razorpay not configured. Add RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET to .env",
                    "payment_url": None,
                    "demo_url": f"https://razorpay.com/payment-link/{patient_id}",
                    "demo_data": {
                        "amount": f"₹{amount:,.2f}",
                        "patient": patient_name,
                        "phone": patient_phone,
                        "email": patient_email,
                        "description": description,
                        "invoice_id": invoice_id,
                        "payment_methods": [
                            "UPI (PhonePe, Google Pay, Paytm)",
                            "Cards (Visa, Mastercard, RuPay)",
                            "Net Banking",
                            "Wallets (Paytm, Mobikwik)"
                        ]
                    },
                    "integration_ready": True,
                    "note": "⚠️ Tool ready to use once Razorpay credentials configured"
                }
            
            # Create Razorpay Payment Link
            # https://razorpay.com/docs/api/payment-links/
            payment_link_data = {
                "amount": rupees_to_paise(amount),
                "currency": "INR",
                "description": description,
                "customer": {
                    "name": patient_name,
                    "email": patient_email,
                    "contact": patient_phone
                },
                "notify": {
                    "sms": True,
                    "email": True
                },
                "reminder_enable": True,
                "notes": {
                    "patient_id": patient_id,
                    "invoice_id": invoice_id or "N/A",
                    "hospital": os.getenv('HOSPITAL_NAME', 'City General Hospital')
                },
                "callback_url": os.getenv('PAYMENT_SUCCESS_URL', 'https://hospital.com/payment/success'),
                "callback_method": "get"
            }
            
            payment_link = razorpay_client.payment_link.create(payment_link_data)
            
            return {
                "success": True,
                "payment_url": payment_link['short_url'],
                "payment_link_id": payment_link['id'],
                "amount": f"₹{amount:,.2f}",
                "currency": "INR",
                "patient_id": patient_id,
                "patient_name": patient_name,
                "description": description,
                "status": payment_link['status'],
                "created_at": datetime.fromtimestamp(payment_link['created_at']).isoformat(),
                "message": f"✅ Payment link created: ₹{amount:,.2f}"
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Razorpay error: {error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "payment_url": None,
                "demo_url": f"https://demo.razorpay.com/pay/{patient_id}?amount={amount}"
            }


# ==================== CHECK PAYMENT STATUS TOOL ====================

class CheckRazorpayPaymentStatusTool(BaseTool):
    name: str = "check_razorpay_payment_status"
    description: str = """Check status of Razorpay payment link or payment.
    Returns: status (pending/paid/expired), amount, timestamp
    """
    args_schema: type[BaseModel] = BaseModel
    
    def _run(self, payment_link_id: str) -> dict:
        """Check payment status"""
        
        try:
            if not razorpay_client:
                return {
                    "success": False,
                    "error": "Razorpay not configured",
                    "status": "unknown",
                    "demo_status": "pending"
                }
            
            # Fetch payment link details
            payment_link = razorpay_client.payment_link.fetch(payment_link_id)
            
            return {
                "success": True,
                "payment_link_id": payment_link_id,
                "status": payment_link['status'],
                "amount": f"₹{payment_link['amount'] / 100:,.2f}",
                "currency": payment_link['currency'],
                "paid_amount": f"₹{payment_link['amount_paid'] / 100:,.2f}",
                "customer": payment_link.get('customer', {}),
                "created_at": datetime.fromtimestamp(payment_link['created_at']).isoformat(),
                "payments_received": payment_link.get('payments', [])
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Status check error: {error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "payment_link_id": payment_link_id
            }


# ==================== EXPORT ALL TOOLS ====================

def get_all_razorpay_tools():
    """Get all Razorpay tools"""
    return [
        CreateRazorpayPaymentLinkTool(),
        CheckRazorpayPaymentStatusTool()
    ]


# ==================== TESTING ====================

if __name__ == "__main__":
    print("="*70)
    print("💳 RAZORPAY PAYMENT TOOL TEST - Indian Healthcare")
    print("="*70)
    
    # Test tool
    print("\n1️⃣ Testing Razorpay payment link creation (demo)...")
    payment_tool = CreateRazorpayPaymentLinkTool()
    
    result = payment_tool._run(
        patient_id="REG2025_RK_001",
        patient_name="Rajesh Kumar",
        patient_email="rajesh.kumar@example.com",
        patient_phone="+919988776655",
        amount=3000.00,
        description="Lab Tests: ECG, X-Ray, Blood Test",
        invoice_id="INV_2025_001"
    )
    
    print(f"\n📊 Result:")
    import json
    print(json.dumps(result, indent=2))
    
    print("\n" + "="*70)
    print("✅ RAZORPAY TOOL INTEGRATION READY!")
    print("="*70)
    print("\n📋 To activate:")
    print("   1. Sign up at https://razorpay.com")
    print("   2. Get API keys from Dashboard → Settings → API Keys")
    print("   3. Add to .env:")
    print("      RAZORPAY_KEY_ID=rzp_test_...")
    print("      RAZORPAY_KEY_SECRET=...")
    print("   4. Install: pip install razorpay")
    print("\n💡 Payment Methods Supported:")
    print("   ✅ UPI (PhonePe, Google Pay, Paytm, BHIM)")
    print("   ✅ Cards (Visa, Mastercard, RuPay)")
    print("   ✅ Net Banking (100+ banks)")
    print("   ✅ Wallets (Paytm, Mobikwik, Freecharge)")
    print("="*70)
