# 🤖 Agentic Hospital Management System - Architecture

## Overview
This document describes how we make the hospital management system **proactive**, **autonomous**, and **human-in-the-loop** enabled.

---

## 🎯 Core Concepts

### 1. **Proactive Agent**
The AI agent actively monitors the system and takes actions **without** being asked.

**Examples:**
- Detects critical lab results → Auto-notifies doctor
- Finds low inventory → Suggests purchase order
- Identifies appointment pattern → Recommends scheduling changes
- Notices missed follow-up → Sends patient reminder

### 2. **Human-in-the-Loop (HITL)**
For important decisions, the agent **asks permission** before acting.

**3-Tier Approval System:**

#### **Tier 1: Auto-Execute** ✅ (No approval needed)
```python
Actions that are safe and routine:
- Send appointment reminders
- Generate daily reports
- Check inventory levels
- Update non-critical records
- Send wellness tips
- Log system events
```

#### **Tier 2: Request Approval** ⚠️ (Quick approval)
```python
Actions requiring admin review:
- Schedule appointments
- Order lab tests
- Dispense medications
- Process refills
- Send bulk emails
- Update patient records
- Generate purchase orders
```

#### **Tier 3: Admin Authorization** 🔴 (Must approve)
```python
Actions requiring explicit authorization:
- Cancel appointments
- Modify prescriptions
- Delete patient records
- Process insurance claims
- Large financial transactions
- Change medication dosages
- Access sensitive records
```

### 3. **Dual UI System**
Two separate interfaces with different access levels.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    HOSPITAL AI AGENT                        │
│                   (LangGraph Workflow)                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐  ┌──────────────┐  ┌──────────────────┐
│   PROACTIVE   │  │    HITL      │  │   NOTIFICATION   │
│   MONITOR     │  │   APPROVAL   │  │     SYSTEM       │
│   (Automated) │  │   (Manual)   │  │   (Multi-Chan)   │
└───────────────┘  └──────────────┘  └──────────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │     FASTAPI BACKEND     │
              │   (REST API + Auth)     │
              └─────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
    ┌──────────────────┐    ┌────────────────────┐
    │  ADMIN DASHBOARD │    │  PATIENT PORTAL    │
    │  (Full Control)  │    │  (Limited Access)  │
    └──────────────────┘    └────────────────────┘
```

---

## 🔄 Proactive Agent Implementation

### **Background Monitoring Tasks**

#### File: `src/proactive_agent.py`

```python
import schedule
import time
from datetime import datetime, timedelta
from tools.lab_management_tool import GetCriticalResultsTool
from tools.appointment_tool import GetAppointmentStatisticsTool
from tools.pharmacy_tool import CheckDrugInventoryTool
from tools.notification_tool import SendNotificationTool

class ProactiveAgent:
    """
    Autonomous agent that monitors and takes actions
    """
    
    def __init__(self):
        self.critical_results_tool = GetCriticalResultsTool()
        self.notification_tool = SendNotificationTool()
        self.inventory_tool = CheckDrugInventoryTool()
    
    def monitor_critical_results(self):
        """
        Check for critical lab results every 30 minutes
        AUTO-EXECUTE (Tier 1)
        """
        print("🔍 Checking for critical lab results...")
        
        # Get critical results from last hour
        results = self.critical_results_tool._run(time_range_hours=1)
        
        if results['critical_count'] > 0:
            # Auto-notify doctor (no approval needed)
            for result in results['critical_results']:
                self.notification_tool._run(
                    recipient_type="doctor",
                    priority="urgent",
                    message=f"🚨 CRITICAL: {result['test_name']} for Patient {result['patient_id']}",
                    channel=["email", "sms"]
                )
            print(f"✅ Notified doctors about {results['critical_count']} critical results")
    
    def monitor_inventory(self):
        """
        Check inventory levels daily
        REQUEST APPROVAL (Tier 2)
        """
        print("📦 Checking inventory levels...")
        
        # Get low stock items
        inventory = self.inventory_tool._run(show_low_stock_only=True)
        
        if inventory['low_stock_items']:
            # Create approval request (needs admin approval)
            for item in inventory['low_stock_items']:
                approval_request = {
                    'type': 'purchase_order',
                    'priority': 'medium',
                    'item': item['medication_name'],
                    'current_stock': item['quantity_in_stock'],
                    'suggested_quantity': 500,
                    'estimated_cost': 500 * item['unit_price'],
                    'reason': 'Low stock alert'
                }
                # Send to approval center
                self.create_approval_request(approval_request)
            
            print(f"⚠️ Created {len(inventory['low_stock_items'])} purchase order requests")
    
    def send_appointment_reminders(self):
        """
        Send reminders for tomorrow's appointments
        AUTO-EXECUTE (Tier 1)
        """
        print("📅 Sending appointment reminders...")
        
        # Get tomorrow's appointments
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Auto-send reminders (no approval needed)
        # Logic to send reminders...
        
        print("✅ Appointment reminders sent")
    
    def analyze_patterns(self):
        """
        Analyze patterns and generate insights
        AUTO-EXECUTE (Tier 1)
        """
        print("📊 Analyzing patterns...")
        
        # Example: Detect high no-show rate
        stats = GetAppointmentStatisticsTool()._run(days=30)
        
        if stats['no_show_percentage'] > 15:
            # Auto-generate report and notify admin
            insight = {
                'type': 'high_no_show_rate',
                'percentage': stats['no_show_percentage'],
                'recommendation': 'Consider implementing SMS reminders or deposit policy'
            }
            # Send insight to admin dashboard
            print(f"💡 Insight generated: High no-show rate ({stats['no_show_percentage']}%)")
    
    def start_monitoring(self):
        """
        Start all scheduled tasks
        """
        # Schedule tasks
        schedule.every(30).minutes.do(self.monitor_critical_results)
        schedule.every().day.at("09:00").do(self.send_appointment_reminders)
        schedule.every().day.at("08:00").do(self.monitor_inventory)
        schedule.every().day.at("23:00").do(self.analyze_patterns)
        
        print("🤖 Proactive Agent started - Monitoring in background...")
        
        # Run forever
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

# Start the agent
if __name__ == "__main__":
    agent = ProactiveAgent()
    agent.start_monitoring()
```

---

## 🔐 Human-in-the-Loop (HITL) System

### **Approval Workflow**

#### File: `tools/approval_tool.py`

```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Literal
import json

class CreateApprovalRequestInput(BaseModel):
    action_type: str = Field(description="Type of action: schedule_appointment, dispense_medication, purchase_order, etc.")
    priority: Literal["low", "medium", "high"] = Field(description="Priority level")
    details: dict = Field(description="Details of the action requiring approval")
    requester: str = Field(description="Who/what is requesting approval")
    
class CreateApprovalRequestTool(BaseTool):
    name: str = "create_approval_request"
    description: str = "Create an approval request for human review"
    args_schema: type[BaseModel] = CreateApprovalRequestInput
    
    def _run(self, action_type: str, priority: str, details: dict, requester: str) -> dict:
        """
        Create approval request and add to queue
        """
        approval_request = {
            'id': f"APR{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'action_type': action_type,
            'priority': priority,
            'details': details,
            'requester': requester,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'approved_by': None,
            'approved_at': None
        }
        
        # Save to approval queue
        approvals = load_db('approvals_database.json')
        approvals.append(approval_request)
        save_db('approvals_database.json', approvals)
        
        # Send notification to admin
        notify_admin(f"New approval request: {action_type}")
        
        return {
            'success': True,
            'approval_id': approval_request['id'],
            'message': f"Approval request created. Admin will review shortly."
        }

class ProcessApprovalInput(BaseModel):
    approval_id: str = Field(description="ID of the approval request")
    decision: Literal["approve", "reject", "modify"] = Field(description="Admin decision")
    admin_id: str = Field(description="ID of admin making decision")
    comments: str = Field(description="Optional comments", default="")
    
class ProcessApprovalTool(BaseTool):
    name: str = "process_approval"
    description: str = "Admin processes an approval request"
    args_schema: type[BaseModel] = ProcessApprovalInput
    
    def _run(self, approval_id: str, decision: str, admin_id: str, comments: str = "") -> dict:
        """
        Process approval decision and execute if approved
        """
        approvals = load_db('approvals_database.json')
        
        # Find approval request
        approval = next((a for a in approvals if a['id'] == approval_id), None)
        
        if not approval:
            return {'success': False, 'message': 'Approval request not found'}
        
        # Update approval status
        approval['status'] = decision
        approval['approved_by'] = admin_id
        approval['approved_at'] = datetime.now().isoformat()
        approval['comments'] = comments
        
        # If approved, execute the action
        if decision == 'approve':
            result = self.execute_approved_action(approval)
            approval['execution_result'] = result
        
        save_db('approvals_database.json', approvals)
        
        return {
            'success': True,
            'message': f"Approval {decision}ed successfully",
            'approval': approval
        }
    
    def execute_approved_action(self, approval: dict) -> dict:
        """
        Execute the approved action
        """
        action_type = approval['action_type']
        details = approval['details']
        
        # Route to appropriate tool
        if action_type == 'purchase_order':
            # Execute purchase order
            return {'status': 'Purchase order created', 'po_id': 'PO123456'}
        
        elif action_type == 'dispense_medication':
            # Execute medication dispensing
            from tools.pharmacy_tool import DispenseMedicationTool
            tool = DispenseMedicationTool()
            return tool._run(**details)
        
        # Add more action types...
        
        return {'status': 'Executed', 'action': action_type}
```

---

## 👥 Dual UI Architecture

### **1. Admin Dashboard** (Full Control)

```javascript
// Admin Dashboard Features

┌────────────────────────────────────────────────────┐
│  ADMIN DASHBOARD - Hospital Management System      │
├────────────────────────────────────────────────────┤
│                                                    │
│  👤 Logged in as: Dr. Admin (Admin Role)          │
│                                                    │
│  ┌──────────────┬──────────────┬──────────────┐  │
│  │  📊 Stats    │  🔔 Alerts   │  ✅ Approvals│  │
│  │  52 Patients │  3 Critical  │  12 Pending  │  │
│  └──────────────┴──────────────┴──────────────┘  │
│                                                    │
│  🔔 APPROVAL CENTER (Human-in-the-Loop)           │
│  ┌──────────────────────────────────────────┐    │
│  │ 🔴 HIGH PRIORITY (3)                     │    │
│  │  • Prescription Modification             │    │
│  │  • Large Purchase Order ($10,000)        │    │
│  │  • Patient Record Deletion Request       │    │
│  │                                          │    │
│  │ 🟡 MEDIUM PRIORITY (7)                   │    │
│  │  • Medication Dispensing (5)             │    │
│  │  • Lab Test Orders (2)                   │    │
│  │                                          │    │
│  │ 🟢 LOW PRIORITY (2)                      │    │
│  │  • Bulk Email Campaign                   │    │
│  │  • Report Generation                     │    │
│  └──────────────────────────────────────────┘    │
│                                                    │
│  MAIN SECTIONS:                                   │
│  • 👥 Patient Management (Full CRUD)              │
│  • 📅 Appointments (Schedule/Cancel/Modify)       │
│  • 🧪 Lab Tests (Order/Results/Reports)           │
│  • 💊 Pharmacy (Dispense/Inventory/Orders)        │
│  • 💰 Billing (Invoices/Insurance/Payments)       │
│  • 📊 Analytics (Performance/Revenue/Stats)       │
│  • ⚙️ Settings (Users/Roles/Permissions)          │
│  • 🤖 AI Agent (Monitor/Configure/Logs)           │
│                                                    │
└────────────────────────────────────────────────────┘

Role-Based Access:
├── 👨‍⚕️ Doctors
│   ├── View/Edit patient medical records
│   ├── Order lab tests
│   ├── Create prescriptions
│   └── View analytics (own patients)
│
├── 👩‍⚕️ Nurses
│   ├── Schedule appointments
│   ├── Update basic patient info
│   ├── View medical records (read-only)
│   └── Enter vital signs
│
├── 💊 Pharmacists
│   ├── Dispense medications
│   ├── Manage inventory
│   ├── Check drug interactions
│   └── Process refills
│
├── 🧪 Lab Technicians
│   ├── Update test status
│   ├── Enter test results
│   ├── Generate lab reports
│   └── Track samples
│
└── 👤 Admins
    ├── Full access to all features
    ├── Process approval requests
    ├── Manage users and roles
    ├── Configure AI agent
    └── View system logs
```

### **2. Patient Portal** (Limited Access)

```javascript
// Patient Portal Features

┌────────────────────────────────────────────────────┐
│  PATIENT PORTAL - My Health Dashboard             │
├────────────────────────────────────────────────────┤
│                                                    │
│  👤 Welcome, John Doe (Patient ID: REG2025001)    │
│                                                    │
│  📅 MY APPOINTMENTS                               │
│  ┌──────────────────────────────────────────┐    │
│  │  Upcoming:                               │    │
│  │  • Oct 20, 2025 - Dr. Johnson (10:00 AM)│    │
│  │    [View Details] [Cancel] [Reschedule]  │    │
│  │                                          │    │
│  │  Past:                                   │    │
│  │  • Sep 15, 2025 - Annual Check-up ✅     │    │
│  │    [View Report]                         │    │
│  └──────────────────────────────────────────┘    │
│                                                    │
│  🧪 LAB RESULTS                                   │
│  ┌──────────────────────────────────────────┐    │
│  │  • Blood Test - Oct 10, 2025            │    │
│  │    Status: ✅ Normal                     │    │
│  │    [View Full Report] [Download PDF]     │    │
│  │                                          │    │
│  │  • Kidney Function - Sep 28, 2025       │    │
│  │    Status: ⚠️ Abnormal (See doctor)      │    │
│  │    [View Details]                        │    │
│  └──────────────────────────────────────────┘    │
│                                                    │
│  💊 MEDICATIONS                                   │
│  ┌──────────────────────────────────────────┐    │
│  │  Active Prescriptions:                   │    │
│  │  • Lisinopril 10mg - Daily               │    │
│  │    Refills: 2 remaining                  │    │
│  │    [Request Refill]                      │    │
│  │                                          │    │
│  │  • Metformin 500mg - Twice daily         │    │
│  │    Refills: 0 remaining                  │    │
│  │    [Contact Doctor]                      │    │
│  └──────────────────────────────────────────┘    │
│                                                    │
│  🤖 AI HEALTH ASSISTANT                           │
│  ┌──────────────────────────────────────────┐    │
│  │  💬 "Ask me anything about your health"  │    │
│  │                                          │    │
│  │  Suggested:                              │    │
│  │  • When is my next appointment?          │    │
│  │  • What are my latest lab results?       │    │
│  │  • How do I request a refill?            │    │
│  └──────────────────────────────────────────┘    │
│                                                    │
│  QUICK ACTIONS:                                   │
│  [📅 Book Appointment] [📄 View Records]          │
│  [💊 Request Refill] [📞 Contact Doctor]          │
│                                                    │
└────────────────────────────────────────────────────┘

Features:
✅ View-only access to medical records
✅ Book/cancel appointments
✅ View lab results (after doctor review)
✅ Request prescription refills
✅ Download reports
✅ Chat with AI assistant (basic queries)
✅ Update personal info (limited)
✅ View billing history
❌ Cannot modify medical records
❌ Cannot access other patients' data
❌ Cannot override doctor decisions
```

---

## 📊 Decision Flow Example

### **Scenario: Low Inventory Detected**

```
1. PROACTIVE AGENT DETECTS:
   📦 Lisinopril 10mg: 45 units (below 50 reorder level)

2. AGENT ANALYSIS:
   📊 Average daily usage: 8 units
   ⏰ Will run out in: 5.6 days
   💡 Recommendation: Order 500 units ($2,500)

3. TIER CHECK:
   ⚠️ Purchase order = Tier 2 (Requires Approval)

4. CREATE APPROVAL REQUEST:
   {
     "type": "purchase_order",
     "priority": "medium",
     "item": "Lisinopril 10mg",
     "current_stock": 45,
     "suggested_quantity": 500,
     "estimated_cost": 2500,
     "reason": "Low stock - will deplete in 5.6 days",
     "auto_analysis": "Critical medication for 12 active patients"
   }

5. NOTIFICATION SENT:
   📧 Email to Admin: "Purchase order approval needed"
   🔔 Dashboard alert: "1 new approval request"

6. ADMIN REVIEWS:
   ✅ Checks budget: OK
   ✅ Verifies usage pattern: Accurate
   ✅ Reviews supplier: Preferred vendor
   
   Decision: APPROVE

7. AGENT EXECUTES:
   ✅ Generate PO: PO2025123456
   ✅ Email supplier: Purchase order sent
   ✅ Update inventory: Expected delivery date set
   ✅ Notify pharmacy: Order placed
   
8. CONFIRMATION:
   📧 Email to Admin: "PO2025123456 created and sent"
   📊 Log event: Purchase order executed
   🔔 Update approval status: Approved & Executed
```

---

## 🎯 Implementation Priorities

### **Phase 2B - Additional Tools** (Current)
1. ✅ Billing & Insurance Tool (6 tools)
2. ✅ Proactive Agent System (Background monitoring)
3. ✅ HITL Approval System (3-tier workflow)
4. ✅ Notification System (Multi-channel)
5. ✅ Analytics & Reporting Dashboard

### **Phase 3 - Backend & UI**
1. FastAPI Backend (REST API)
2. Admin Dashboard (Full features)
3. Patient Portal (Limited access)
4. Authentication & RBAC
5. Real-time updates (WebSocket)

### **Phase 4 - Advanced Features**
1. AI-powered symptom analysis
2. Predictive analytics
3. Mobile app
4. Telemedicine integration
5. HIPAA compliance

---

## 🔒 Security Considerations

### **Authentication & Authorization**
```python
# Role hierarchy
ROLES = {
    'patient': {
        'permissions': ['view_own_records', 'book_appointment', 'request_refill'],
        'cannot': ['edit_records', 'view_others', 'approve_requests']
    },
    'nurse': {
        'permissions': ['view_records', 'schedule_appointments', 'update_vitals'],
        'cannot': ['prescribe', 'dispense', 'approve_major_actions']
    },
    'doctor': {
        'permissions': ['full_medical_access', 'prescribe', 'order_tests'],
        'cannot': ['dispense', 'manage_inventory', 'access_billing']
    },
    'pharmacist': {
        'permissions': ['dispense', 'manage_inventory', 'check_interactions'],
        'cannot': ['prescribe', 'edit_medical_records']
    },
    'admin': {
        'permissions': ['full_access', 'approve_requests', 'manage_users'],
        'cannot': []  # Full access
    }
}
```

### **Audit Trail**
Every action is logged:
- Who performed the action
- What action was performed
- When it was performed
- Why it was performed (approval reference)
- What was changed (before/after)

---

## 📝 Summary

This architecture makes the system:

✅ **Proactive** - Monitors and acts automatically
✅ **Safe** - Human approval for critical actions
✅ **Secure** - Role-based access control
✅ **User-friendly** - Separate interfaces for different users
✅ **Auditable** - Complete action history
✅ **Scalable** - Can add more monitoring tasks
✅ **Intelligent** - AI-driven insights and recommendations

**Next Steps:**
1. Build Billing & Insurance Tool
2. Implement Proactive Agent System
3. Create HITL Approval Workflow
4. Build Notification System
5. Create Analytics Dashboard
6. Then proceed to FastAPI + UI

Ready to start building? 🚀
