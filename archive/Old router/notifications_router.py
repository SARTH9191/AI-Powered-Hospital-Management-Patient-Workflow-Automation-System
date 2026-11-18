"""Notifications Router - Email, SMS, WhatsApp"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from api.auth import get_current_user
from tools.twilio_tool import SendSMSTool, SendWhatsAppTool, GetMessageStatusTool

router = APIRouter()


# ==================== REQUEST MODELS ====================

class SMSRequest(BaseModel):
    """Request model for sending SMS"""
    to: str
    message: str
    from_number: Optional[str] = None


class WhatsAppRequest(BaseModel):
    """Request model for sending WhatsApp"""
    to: str
    message: str
    from_number: Optional[str] = None


class MessageStatusRequest(BaseModel):
    """Request model for checking message status"""
    message_sid: str


# ==================== ENDPOINTS ====================

@router.get("/")
async def notifications_root(current_user: Dict = Depends(get_current_user)):
    """Notifications API overview"""
    return {
        "message": "Notifications API", 
        "features": ["SMS", "WhatsApp", "Email", "Status Tracking"],
        "total_tools": 7
    }


@router.post("/sms/send")
async def send_sms(
    request: SMSRequest, 
    current_user: Dict = Depends(get_current_user)
):
    """
    Send SMS message to patient
    
    **Required:**
    - `to`: Phone number in E.164 format (e.g., +1234567890)
    - `message`: SMS text (max 1600 characters)
    
    **Optional:**
    - `from_number`: Custom sender number (defaults to TWILIO_PHONE_NUMBER)
    
    **Example:**
    ```json
    {
        "to": "+919876543210",
        "message": "Your appointment is confirmed for tomorrow at 10 AM"
    }
    ```
    """
    try:
        sms_tool = SendSMSTool()
        result = sms_tool._run(
            to=request.to,
            message=request.message,
            from_number=request.from_number
        )
        
        if result.get("success"):
            return {
                "success": True,
                "message": "SMS sent successfully",
                "data": result
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to send SMS")
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/whatsapp/send")
async def send_whatsapp(
    request: WhatsAppRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Send WhatsApp message to patient
    
    **Required:**
    - `to`: Phone number in E.164 format (e.g., +1234567890)
    - `message`: WhatsApp text (supports formatting)
    
    **Optional:**
    - `from_number`: Custom sender number (defaults to TWILIO_PHONE_NUMBER)
    
    **Note:** For trial accounts, recipient must join WhatsApp sandbox first
    
    **Example:**
    ```json
    {
        "to": "+919876543210",
        "message": "*Lab Results Ready*\\n\\nYour test results are available.\\nPlease check your email."
    }
    ```
    """
    try:
        whatsapp_tool = SendWhatsAppTool()
        result = whatsapp_tool._run(
            to=request.to,
            message=request.message,
            from_number=request.from_number
        )
        
        if result.get("success"):
            return {
                "success": True,
                "message": "WhatsApp sent successfully",
                "data": result
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to send WhatsApp")
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/message/status")
async def get_message_status(
    request: MessageStatusRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Check delivery status of SMS or WhatsApp message
    
    **Required:**
    - `message_sid`: Twilio message SID (starts with SM or MM)
    
    **Returns:**
    - Status: queued, sent, delivered, failed, undelivered
    - Timestamps, error codes (if any)
    - Pricing information
    
    **Example:**
    ```json
    {
        "message_sid": "SM1234567890abcdef1234567890abcdef"
    }
    ```
    """
    try:
        status_tool = GetMessageStatusTool()
        result = status_tool._run(message_sid=request.message_sid)
        
        if result.get("success"):
            return {
                "success": True,
                "message": "Status retrieved successfully",
                "data": result
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=result.get("error", "Message not found")
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/message/status/{message_sid}")
async def get_message_status_by_path(
    message_sid: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Check delivery status of SMS or WhatsApp message (GET endpoint)
    
    **Usage:** `/api/notifications/message/status/SM1234567890abcdef`
    """
    try:
        status_tool = GetMessageStatusTool()
        result = status_tool._run(message_sid=message_sid)
        
        if result.get("success"):
            return {
                "success": True,
                "message": "Status retrieved successfully",
                "data": result
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=result.get("error", "Message not found")
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
