"""
Conversational AI Agent for Hospital Management
This is a TRUE AI agent that decides which tools to call based on conversation

Author: GitHub Copilot
Email: pawarsamarth786@gmail.com (configured for your account)
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# ==================== IMPORT ESSENTIAL TOOLS ====================
# We only import tools the agent NEEDS for conversations

# Patient Management
from tools.patient_registration_tool import (
    RegisterPatientTool,
    SearchPatientTool,
    GetPatientDetailsTool
)

# Appointments
from tools.appointment_tool import (
    CheckDoctorAvailabilityTool,
    ScheduleAppointmentTool,
    GetPatientAppointmentsTool
)

# Lab Management
from tools.lab_management_tool import (
    OrderLabTestTool,
    GetTestResultsTool,
    GetPatientLabHistoryTool
)

# Medical Records
from tools.medical_records_tool import (
    GetMedicalHistoryTool,
    AddPrescriptionTool
)

# Billing
from tools.billing_tool import (
    GenerateInvoiceTool,
    GetPatientBalanceTool,
    VerifyInsuranceCoverageTool
)

# Notifications
from tools.gmail_tool import SendGmailTool
from tools.twilio_tool import SendSMSTool
from src.multi_channel_notification import SendMultiChannelNotificationTool

# Google Workspace
from tools.google_sheets_tool import AddPatientRecordTool, ReadSheetDataTool
from tools.google_calendar_tool import CreateAppointmentTool, CheckAvailabilityTool

# Analytics
from tools.analytics_tool import GetSystemOverviewTool, GetPatientAnalyticsTool

# Approvals (HITL)
from tools.approval_tool import (
    CreateApprovalRequestTool,
    GetPendingApprovalsTool,
    ProcessApprovalTool
)

# ==================== INITIALIZE LLM ====================

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    google_api_key="AIzaSyAtg-gOdmv-0rLan-TYwN2N-J2hph4lQJg",
    temperature=0.3,  # Balanced between creative and consistent
)

# ==================== DEFINE TOOLS ====================

# Create tool instances
tools = [
    # Patient Management (3 tools)
    RegisterPatientTool(),
    SearchPatientTool(),
    GetPatientDetailsTool(),
    
    # Appointments (3 tools)
    CheckDoctorAvailabilityTool(),
    ScheduleAppointmentTool(),
    GetPatientAppointmentsTool(),
    
    # Lab Management (3 tools)
    OrderLabTestTool(),
    GetTestResultsTool(),
    GetPatientLabHistoryTool(),
    
    # Medical Records (2 tools)
    GetMedicalHistoryTool(),
    AddPrescriptionTool(),
    
    # Billing (3 tools)
    GenerateInvoiceTool(),
    GetPatientBalanceTool(),
    VerifyInsuranceCoverageTool(),
    
    # Communication (3 tools)
    SendGmailTool(),
    SendSMSTool(),
    SendMultiChannelNotificationTool(),
    
    # Google Workspace (4 tools)
    AddPatientRecordTool(),
    ReadSheetDataTool(),
    CreateAppointmentTool(),
    CheckAvailabilityTool(),
    
    # Analytics (2 tools)
    GetSystemOverviewTool(),
    GetPatientAnalyticsTool(),
    
    # Approvals (3 tools)
    CreateApprovalRequestTool(),
    GetPendingApprovalsTool(),
    ProcessApprovalTool()
]

print(f"✅ Loaded {len(tools)} tools for conversational agent")

# ==================== AGENT PROMPT ====================

system_prompt = """You are an intelligent AI Hospital Assistant named "MediBot".

You help patients, doctors, and staff with hospital operations through natural conversation.

**Your Capabilities:**
1. 👤 **Patient Registration** - Register new patients, search existing records
2. 📅 **Appointments** - Book, reschedule, check doctor availability
3. 🧪 **Lab Tests** - Order tests, check results, view history
4. 💊 **Medical Records** - View history, add prescriptions
5. 💰 **Billing** - Check balance, verify insurance, generate invoices
6. 📧 **Notifications** - Send emails, SMS, multi-channel alerts
7. 📊 **Analytics** - System overview, patient statistics
8. ✅ **Approvals** - Create approval requests (HITL system)

**How You Work:**
- Always greet users warmly and ask how you can help
- Ask for missing information (name, phone, email, etc.)
- Use tools step-by-step to complete tasks
- Confirm before taking important actions (booking appointments, ordering tests)
- Save data to Google Sheets after registration/updates
- Send confirmation emails/SMS after actions
- Be professional but friendly
- Handle errors gracefully and suggest alternatives

**Important Rules:**
1. **For Patient Registration:**
   - Ask: name, phone, email, date of birth, gender, address
   - After registration → Save to Google Sheets → Send welcome email
   
2. **For Appointments:**
   - Check doctor availability FIRST
   - Confirm with patient before booking
   - After booking → Add to Google Calendar → Send confirmation email
   
3. **For Lab Tests:**
   - If critical tests → Create approval request for doctor
   - Explain why tests are needed
   - After ordering → Send notification to patient
   
4. **For Medical Queries:**
   - Retrieve patient's medical history
   - Provide helpful information
   - Recommend consulting a doctor for serious concerns

**Your Email:** pawarsamarth786@gmail.com (use this for sending emails)

**Tone:** Professional, empathetic, efficient

Available tools: {tool_names}

Today's date: {current_date}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# ==================== CREATE AGENT ====================

agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,  # Show tool calls in console
    handle_parsing_errors=True,
    max_iterations=15,  # Allow multiple tool calls
    return_intermediate_steps=True,  # Return which tools were used
    max_execution_time=60,  # Timeout after 60 seconds
)

# ==================== CHAT FUNCTION ====================

def chat_with_agent(
    user_message: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Main function to interact with the conversational agent
    
    Args:
        user_message: The user's question/request
        chat_history: Previous conversation history
        user_context: User information (user_id, role, patient_id, etc.)
    
    Returns:
        {
            "response": "Agent's response",
            "tools_used": ["Tool1", "Tool2", ...],
            "success": True/False,
            "metadata": {...}
        }
    """
    
    try:
        # Format chat history for LangChain
        formatted_history = []
        if chat_history:
            for msg in chat_history[-10:]:  # Keep last 10 messages
                if msg.get("role") == "user":
                    formatted_history.append(HumanMessage(content=msg["content"]))
                elif msg.get("role") == "assistant":
                    formatted_history.append(AIMessage(content=msg["content"]))
        
        # Add user context to message if available
        enhanced_message = user_message
        if user_context:
            context_info = f"\n\n[Context: User ID={user_context.get('user_id')}, Role={user_context.get('role')}]"
            enhanced_message = user_message + context_info
        
        # Invoke agent
        result = agent_executor.invoke({
            "input": enhanced_message,
            "chat_history": formatted_history,
            "tool_names": ", ".join([tool.name for tool in tools]),
            "current_date": datetime.now().strftime("%Y-%m-%d")
        })
        
        # Extract tools used
        tools_used = []
        if result.get("intermediate_steps"):
            for step in result["intermediate_steps"]:
                action, _ = step
                tools_used.append(action.tool)
        
        return {
            "response": result["output"],
            "tools_used": tools_used,
            "success": True,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "model": "gemini-2.0-flash-exp",
                "tool_count": len(tools_used)
            }
        }
        
    except Exception as e:
        error_msg = f"I apologize, but I encountered an error: {str(e)}\n\nPlease try rephrasing your request or contact support if this persists."
        
        return {
            "response": error_msg,
            "tools_used": [],
            "success": False,
            "error": str(e),
            "metadata": {
                "timestamp": datetime.now().isoformat()
            }
        }

# ==================== HELPER FUNCTIONS ====================

def get_agent_info() -> Dict[str, Any]:
    """Get information about the agent and its capabilities"""
    return {
        "name": "MediBot",
        "version": "1.0.0",
        "model": "gemini-2.0-flash-exp",
        "tools_count": len(tools),
        "tools": [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in tools
        ],
        "capabilities": [
            "Patient Registration",
            "Appointment Booking",
            "Lab Test Management",
            "Medical Records",
            "Billing & Insurance",
            "Notifications",
            "Analytics",
            "Approval Workflows"
        ]
    }

def start_conversation(user_role: str = "patient") -> str:
    """Get initial greeting based on user role"""
    
    greetings = {
        "patient": "👋 Hello! I'm MediBot, your AI Hospital Assistant.\n\nI can help you with:\n• Registering as a patient\n• Booking appointments\n• Checking lab results\n• Viewing medical records\n• Billing inquiries\n\nHow can I assist you today?",
        
        "doctor": "👋 Hello Doctor! I'm MediBot.\n\nI can help you with:\n• Viewing patient records\n• Reviewing pending approvals\n• Checking lab results\n• Managing your schedule\n• Analytics and reports\n\nWhat would you like to do?",
        
        "staff": "👋 Hello! I'm MediBot.\n\nI can assist you with:\n• Patient registration\n• Appointment scheduling\n• Billing management\n• Document uploads\n• System analytics\n\nHow can I help?",
        
        "admin": "👋 Hello Administrator! I'm MediBot.\n\nI can help you with:\n• System overview and analytics\n• User management\n• Approval workflows\n• Financial reports\n• All patient operations\n\nWhat would you like to do?"
    }
    
    return greetings.get(user_role, greetings["patient"])

# ==================== TESTING ====================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 CONVERSATIONAL AI AGENT - INTERACTIVE TEST")
    print("="*60)
    
    print("\n📋 Agent Info:")
    info = get_agent_info()
    print(f"Name: {info['name']}")
    print(f"Model: {info['model']}")
    print(f"Tools Available: {info['tools_count']}")
    
    print("\n" + "-"*60)
    print("💬 CHAT INTERFACE (Type 'exit' to quit)")
    print("-"*60)
    
    # Show initial greeting
    greeting = start_conversation("patient")
    print(f"\n🤖 Agent: {greeting}\n")
    
    # Chat history
    history = []
    
    # Interactive loop
    while True:
        try:
            user_input = input("👤 You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\n🤖 Agent: Thank you for using our Hospital AI Assistant. Take care! 👋\n")
                break
            
            # Get agent response
            print("\n🤖 Thinking...")
            result = chat_with_agent(
                user_message=user_input,
                chat_history=history,
                user_context={"user_id": "TEST_USER", "role": "patient"}
            )
            
            print(f"\n🤖 Agent: {result['response']}")
            
            if result.get('tools_used'):
                print(f"\n📊 Tools Used: {', '.join(result['tools_used'])}")
            
            # Update history
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": result["response"]})
            
            print()  # Blank line for readability
            
        except KeyboardInterrupt:
            print("\n\n🤖 Agent: Goodbye! 👋\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")
            continue
    
    print("="*60)
    print("✅ Chat session ended")
    print("="*60)
