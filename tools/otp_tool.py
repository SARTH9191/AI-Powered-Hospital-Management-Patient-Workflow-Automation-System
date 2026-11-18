"""
Smart OTP Tools - SMS (Twilio) + Email Fallback
Saves Twilio credits by only sending SMS to NEW patients
"""

import os
import random
import string
from typing import Type, Optional, Dict, Any
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from twilio.rest import Client
from dotenv import load_dotenv

# Import database and cache
from database.db_manager import PatientDB, OTPDB
from database.redis_cache import cache
from tools.gmail_tool import SendGmailTool

load_dotenv()

# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class SendOTPInput(BaseModel):
    """Input for SendOTP tool"""
    phone: str = Field(description="Phone number with country code (e.g., +91-9876543210)")
    email: Optional[str] = Field(None, description="Email address for fallback OTP")
    purpose: str = Field(default="registration", description="Purpose: registration, login, payment")


class VerifyOTPInput(BaseModel):
    """Input for VerifyOTP tool"""
    phone: str = Field(description="Phone number used to send OTP")
    otp_code: str = Field(description="6-digit OTP code entered by user")


# ============================================================================
# SEND OTP TOOL (SMART - SMS or Email based on patient status)
# ============================================================================

class SendOTPTool(BaseTool):
    """
    Smart OTP sender that SAVES TWILIO CREDITS!
    
    Logic:
    1. Check if phone exists in database
    2. NEW patient → Send SMS (uses Twilio credit)
    3. EXISTING patient → Send Email (FREE!)
    4. Cache OTP in Redis (5 min expiry, 3 attempts max)
    """
    
    name: str = "send_otp"
    description: str = """Send OTP for verification. 
    Automatically chooses SMS for new patients or Email for existing patients.
    Returns success message with delivery method."""
    args_schema: Type[BaseModel] = SendOTPInput
    
    def _generate_otp(self) -> str:
        """Generate 6-digit OTP code"""
        return ''.join(random.choices(string.digits, k=6))
    
    def _check_existing_otp(self, phone: str) -> Optional[Dict]:
        """Check if valid OTP already exists in Redis"""
        # Check Redis cache first (fast)
        existing = cache.get(f"otp:{phone}")
        if existing and isinstance(existing, dict):
            return existing
        
        # Check PostgreSQL (fallback)
        try:
            otp_db = OTPDB()
            db_otp = otp_db.check_existing_otp(phone)
            if db_otp:
                return {
                    'code': db_otp['otp_code'],
                    'expires_at': db_otp['expires_at'].isoformat(),
                    'attempts': db_otp['attempts']
                }
        except:
            pass
        
        return None
    
    def _is_new_patient(self, phone: str) -> bool:
        """Check if patient already exists in database"""
        
        # TEMPORARY FIX: Force your phone number to be treated as NEW for testing
        if phone == "+91-7447444532" or "7447444532" in phone:
            print("🧪 TESTING MODE: Treating +91-7447444532 as NEW patient for SMS testing")
            return True
            
        try:
            patient_db = PatientDB()
            existing_patient = patient_db.get_patient_by_phone(phone)
            return existing_patient is None  # True if NEW patient
        except:
            return True  # Default to NEW (send SMS to be safe)
    
    def _send_sms_otp(self, phone: str, otp_code: str) -> bool:
        """Send OTP via Twilio SMS (costs money!)"""
        try:
            # Initialize Twilio
            account_sid = os.getenv("TWILIO_ACCOUNT_SID")
            auth_token = os.getenv("TWILIO_AUTH_TOKEN")
            from_number = os.getenv("TWILIO_FROM_NUMBER")
            
            if not all([account_sid, auth_token, from_number]):
                print("⚠️ Twilio credentials not configured")
                return False
            
            client = Client(account_sid, auth_token)
            
            # Send SMS
            message = client.messages.create(
                body=f"Your City Hospital OTP is: {otp_code}\nValid for 5 minutes.\nDo not share this code.",
                from_=from_number,
                to=phone
            )
            
            print(f"✅ SMS sent via Twilio (SID: {message.sid}) - Credit used: ~$0.01")
            return True
            
        except Exception as e:
            print(f"❌ SMS send failed: {e}")
            return False
    
    def _send_email_otp(self, email: str, otp_code: str, phone: str) -> bool:
        """Send OTP via Email (FREE!)"""
        try:
            gmail_tool = SendGmailTool()
            
            email_body = f"""
Dear Patient,

Your verification code for City Hospital is:

**{otp_code}**

This code will expire in 5 minutes.

For security:
• Do not share this code with anyone
• Use it only on our official website/app
• Contact us if you didn't request this

Phone: {phone}

Best regards,
City Hospital Team
"""
            
            result = gmail_tool._run(
                to=email,
                subject="Your City Hospital Verification Code",
                message=email_body
            )
            
            if "sent" in result.lower() and "message id" in result.lower():
                print(f"✅ Email OTP sent to {email} - FREE!")
                return True
            elif "sent successfully" in result.lower():
                print(f"✅ Email OTP sent to {email} - FREE!")
                return True
            else:
                print(f"⚠️ Email send result: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Email send failed: {e}")
            return False
    
    def _run(self, phone: str, email: Optional[str] = None, purpose: str = "registration") -> str:
        """
        Send OTP with smart routing
        
        Returns:
            Success message with delivery method
        """
        
        # Normalize phone number
        phone = phone.strip().replace(" ", "").replace("-", "")
        
        # Fix common phone number formats
        if phone.startswith("91") and len(phone) == 12:
            # Format: 917447444532 → +91-7447444532
            phone = f"+91-{phone[2:]}"
        elif phone.startswith("7447444532"):
            # Format: 7447444532 → +91-7447444532  
            phone = f"+91-{phone}"
        elif not phone.startswith("+"):
            # Assume Indian number if no country code
            if len(phone) == 10 and phone.startswith(("6", "7", "8", "9")):
                phone = f"+91-{phone}"
            else:
                # Default to +91 for other formats
                phone = f"+91-{phone}"
        
        # Ensure proper format: +91-XXXXXXXXXX
        if phone.startswith("+91") and "-" not in phone:
            phone = phone[:3] + "-" + phone[3:]
        
        # Check if valid OTP already exists
        existing_otp = self._check_existing_otp(phone)
        if existing_otp:
            ttl = cache.get_ttl(f"otp:{phone}")
            return f"""⏰ OTP Already Sent!

An OTP was sent to {phone} less than 5 minutes ago.

Please check your messages or wait {ttl} seconds to request a new one.

Attempts remaining: {3 - existing_otp.get('attempts', 0)}"""
        
        # Generate new OTP
        otp_code = self._generate_otp()
        
        # Smart routing: NEW patient → SMS, EXISTING → Email
        is_new = self._is_new_patient(phone)
        
        delivery_method = None
        delivery_status = False
        
        if is_new:
            # NEW PATIENT → Send SMS (costs $0.01)
            print(f"🆕 New patient detected: {phone}")
            print(f"💰 Sending SMS (Twilio credit will be used)")
            delivery_status = self._send_sms_otp(phone, otp_code)
            delivery_method = "SMS"
            
            # If SMS fails and email available, fallback to email
            if not delivery_status and email:
                print(f"📧 SMS failed, falling back to Email...")
                delivery_status = self._send_email_otp(email, otp_code, phone)
                delivery_method = "Email (SMS fallback)"
                
        else:
            # EXISTING PATIENT → Send Email (FREE!)
            print(f"👤 Existing patient detected: {phone}")
            print(f"💚 Sending Email (FREE - saving Twilio credit!)")
            
            if email:
                delivery_status = self._send_email_otp(email, otp_code, phone)
                delivery_method = "Email"
            else:
                # No email available, must use SMS
                print(f"⚠️ No email available, using SMS...")
                delivery_status = self._send_sms_otp(phone, otp_code)
                delivery_method = "SMS"
        
        if not delivery_status:
            return f"❌ Failed to send OTP via {delivery_method}. Please try again."
        
        # Store OTP in Redis (5 min expiry)
        cache.set_otp(phone, otp_code, ttl=300)
        
        # Store in PostgreSQL (backup)
        try:
            otp_db = OTPDB()
            otp_db.create_otp(
                phone=phone,
                otp_code=otp_code,
                otp_type="sms" if "SMS" in delivery_method else "email",
                purpose=purpose,
                email=email
            )
        except Exception as e:
            print(f"Warning: PostgreSQL OTP storage failed: {e}")
        
        # Return success message
        savings_msg = "💰 Credit saved!" if "Email" in delivery_method else "💳 Credit used (~$0.01)"
        
        return f"""✅ OTP Sent Successfully!

📱 Phone: {phone}
📬 Delivery: {delivery_method}
{savings_msg}

🔐 Your 6-digit code has been sent.
⏰ Valid for 5 minutes
🔄 Max 3 verification attempts

Please enter the code to continue."""
    
    async def _arun(self, phone: str, email: Optional[str] = None, purpose: str = "registration") -> str:
        return self._run(phone, email, purpose)


# ============================================================================
# VERIFY OTP TOOL
# ============================================================================

class VerifyOTPTool(BaseTool):
    """
    Verify OTP code entered by user
    
    Features:
    - Check Redis cache first (fast)
    - Fallback to PostgreSQL
    - Track attempts (max 3)
    - Auto-expire after 5 minutes
    """
    
    name: str = "verify_otp"
    description: str = """Verify OTP code entered by user.
    Returns success/failure with remaining attempts."""
    args_schema: Type[BaseModel] = VerifyOTPInput
    
    def _run(self, phone: str, otp_code: str) -> str:
        """
        Verify OTP code
        
        Returns:
            Success or error message with attempts remaining
        """
        
        # Normalize inputs - use SAME logic as SendOTPTool
        phone = phone.strip().replace(" ", "").replace("-", "")
        
        # Fix common phone number formats
        if phone.startswith("91") and len(phone) == 12:
            # Format: 917447444532 → +91-7447444532
            phone = f"+91-{phone[2:]}"
        elif phone.startswith("7447444532"):
            # Format: 7447444532 → +91-7447444532  
            phone = f"+91-{phone}"
        elif not phone.startswith("+"):
            # Assume Indian number if no country code
            if len(phone) == 10 and phone.startswith(("6", "7", "8", "9")):
                phone = f"+91-{phone}"
            else:
                # Default to +91 for other formats
                phone = f"+91-{phone}"
        
        # Ensure proper format: +91-XXXXXXXXXX
        if phone.startswith("+91") and "-" not in phone:
            phone = phone[:3] + "-" + phone[3:]
        
        otp_code = otp_code.strip()
        
        # Check if OTP exists in cache
        otp_data = cache.get(f"otp:{phone}")
        if not otp_data:
            return f"""❌ No OTP Found

No valid OTP exists for {phone}.

Please request a new OTP first."""
        
        # Verify using Redis (fast)
        is_valid = cache.verify_otp(phone, otp_code)
        
        if is_valid:
            # Mark as verified in PostgreSQL
            try:
                otp_db = OTPDB()
                otp_db.verify_otp(phone, otp_code)
            except:
                pass
            
            return f"""✅ OTP Verified Successfully!

Phone: {phone}
Status: Verified ✓

You can now proceed with registration."""
        
        else:
            # Check remaining attempts
            attempts = cache.get_otp_attempts(phone)
            remaining = 3 - attempts
            
            if remaining <= 0:
                return f"""❌ Verification Failed!

Too many incorrect attempts. OTP has been invalidated.

Please request a new OTP."""
            
            return f"""❌ Invalid OTP Code

The code you entered is incorrect.

Attempts remaining: {remaining}/3

Please check your messages and try again."""
    
    async def _arun(self, phone: str, otp_code: str) -> str:
        return self._run(phone, otp_code)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = ['SendOTPTool', 'VerifyOTPTool']


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("Testing Smart OTP System...")
    print()
    
    # Test 1: Send OTP to new patient
    send_tool = SendOTPTool()
    result = send_tool._run(
        phone="+91-9999999999",
        email="test@example.com",
        purpose="registration"
    )
    print(result)
    print()
    
    # Test 2: Try to send again (should be blocked)
    result = send_tool._run(
        phone="+91-9999999999",
        email="test@example.com"
    )
    print(result)
    print()
    
    # Test 3: Verify OTP
    verify_tool = VerifyOTPTool()
    result = verify_tool._run(
        phone="+91-9999999999",
        otp_code="123456"  # Wrong code
    )
    print(result)
