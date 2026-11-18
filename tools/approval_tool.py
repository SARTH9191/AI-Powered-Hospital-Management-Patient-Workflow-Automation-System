"""
Human-in-the-Loop (HITL) Approval System Tools
Implements 3-tier approval workflow: Auto-Execute, Request Approval, Admin Authorization
"""

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Any
from datetime import datetime, timedelta
import json
import os

# Database file paths
APPROVALS_DB_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'approvals_database.json')

# ==================== AUTO-APPROVE MODE (FOR PATIENT TESTING) ====================
# Set to True to automatically approve all doctor/staff requests
# This lets you focus on testing the patient workflow end-to-end
AUTO_APPROVE_MODE = True
AUTO_APPROVE_ADMIN = "system_auto_approver"
# ==================================================================================

# 3-Tier Approval Configuration
APPROVAL_TIERS = {
    'tier1_auto_execute': {
        'description': 'Auto-Execute - No approval needed',
        'actions': [
            'send_appointment_reminder',
            'generate_report',
            'check_inventory',
            'log_event',
            'send_wellness_tip',
            'update_non_critical_record',
            'send_notification'
        ],
        'approval_required': False
    },
    'tier2_request_approval': {
        'description': 'Request Approval - Quick review',
        'actions': [
            'schedule_appointment',
            'order_lab_test',
            'dispense_medication',
            'process_refill',
            'send_bulk_email',
            'update_patient_record',
            'generate_purchase_order',
            'process_payment'
        ],
        'approval_required': True,
        'timeout_hours': 24
    },
    'tier3_admin_authorization': {
        'description': 'Admin Authorization - Must approve',
        'actions': [
            'cancel_appointment',
            'modify_prescription',
            'delete_patient_record',
            'process_insurance_claim',
            'large_financial_transaction',
            'change_medication_dosage',
            'access_sensitive_record',
            'bulk_data_export'
        ],
        'approval_required': True,
        'timeout_hours': 72,
        'requires_admin': True
    }
}

def load_db(file_path):
    """Load database from JSON file"""
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    return []

def save_db(file_path, data):
    """Save database to JSON file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def generate_approval_id():
    """Generate unique approval request ID"""
    import random
    return f"APR{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100, 999)}"

def determine_tier(action_type: str) -> str:
    """Determine approval tier for an action"""
    for tier, config in APPROVAL_TIERS.items():
        if action_type in config['actions']:
            return tier
    return 'tier2_request_approval'  # Default to tier 2

# ==================== TOOL 1: Create Approval Request ====================

class CreateApprovalRequestInput(BaseModel):
    action_type: str = Field(description="Type of action requiring approval (e.g., 'schedule_appointment', 'dispense_medication')")
    priority: Literal["low", "medium", "high", "critical"] = Field(description="Priority level")
    requester: str = Field(description="Who/what is requesting approval (e.g., 'Proactive Agent', 'Dr. Smith', 'System')")
    details: dict = Field(description="Detailed information about the action")
    reason: str = Field(description="Why this action is needed")
    estimated_cost: Optional[float] = Field(default=None, description="Estimated cost if financial transaction")
    affected_entities: Optional[List[str]] = Field(default=None, description="Affected patients/users (e.g., ['REG2025001'])")

class CreateApprovalRequestTool(BaseTool):
    name: str = "create_approval_request"
    description: str = """Create an approval request for human review. Automatically determines approval tier 
    based on action type. Tier 1 actions auto-execute, Tier 2 requires approval, Tier 3 requires admin authorization."""
    args_schema: type[BaseModel] = CreateApprovalRequestInput
    
    def _run(self, action_type: str, priority: str, requester: str, details: dict, 
             reason: str, estimated_cost: Optional[float] = None, 
             affected_entities: Optional[List[str]] = None) -> dict:
        """Create approval request"""
        
        try:
            # Determine approval tier
            tier = determine_tier(action_type)
            tier_config = APPROVAL_TIERS[tier]
            
            # Check if approval is required
            if not tier_config['approval_required']:
                # Tier 1: Auto-execute
                return {
                    'success': True,
                    'tier': tier,
                    'approval_required': False,
                    'message': f'✅ Action "{action_type}" is auto-approved (Tier 1). No approval needed.',
                    'action': 'auto_execute'
                }
            
            # ==================== AUTO-APPROVE MODE ====================
            # If AUTO_APPROVE_MODE is enabled, instantly approve without human intervention
            if AUTO_APPROVE_MODE:
                approval_id = generate_approval_id()
                instant_approval = {
                    'approval_id': approval_id,
                    'action_type': action_type,
                    'tier': tier,
                    'priority': priority,
                    'requester': requester,
                    'details': details,
                    'reason': reason,
                    'estimated_cost': estimated_cost,
                    'affected_entities': affected_entities or [],
                    'status': 'approved',
                    'requires_admin': tier_config.get('requires_admin', False),
                    'created_at': datetime.now().isoformat(),
                    'timeout_at': (datetime.now() + timedelta(hours=999)).isoformat(),
                    'approved_by': AUTO_APPROVE_ADMIN,
                    'approved_at': datetime.now().isoformat(),
                    'rejection_reason': None,
                    'execution_status': 'approved',
                    'execution_result': 'Auto-approved for patient testing',
                    'status_history': [
                        {
                            'status': 'pending',
                            'timestamp': datetime.now().isoformat(),
                            'note': 'Approval request created'
                        },
                        {
                            'status': 'approved',
                            'timestamp': datetime.now().isoformat(),
                            'admin': AUTO_APPROVE_ADMIN,
                            'note': 'AUTO-APPROVED: Patient workflow testing mode'
                        }
                    ]
                }
                
                # Save to database for audit trail
                approvals = load_db(APPROVALS_DB_FILE)
                approvals.append(instant_approval)
                save_db(APPROVALS_DB_FILE, approvals)
                
                return {
                    'success': True,
                    'tier': tier,
                    'approval_required': False,
                    'message': f'✅ AUTO-APPROVED: {action_type} (Patient testing mode)',
                    'action': 'auto_approved',
                    'approval': instant_approval
                }
            # =========================================================
            
            # Load approvals database
            approvals = load_db(APPROVALS_DB_FILE)
            
            # Calculate timeout
            timeout_hours = tier_config.get('timeout_hours', 24)
            timeout_date = (datetime.now() + timedelta(hours=timeout_hours)).isoformat()
            
            # Create approval request
            approval_request = {
                'approval_id': generate_approval_id(),
                'action_type': action_type,
                'tier': tier,
                'priority': priority,
                'requester': requester,
                'details': details,
                'reason': reason,
                'estimated_cost': estimated_cost,
                'affected_entities': affected_entities or [],
                'status': 'pending',
                'requires_admin': tier_config.get('requires_admin', False),
                'created_at': datetime.now().isoformat(),
                'timeout_at': timeout_date,
                'approved_by': None,
                'approved_at': None,
                'rejection_reason': None,
                'execution_status': None,
                'execution_result': None,
                'status_history': [
                    {
                        'status': 'pending',
                        'timestamp': datetime.now().isoformat(),
                        'note': 'Approval request created'
                    }
                ]
            }
            
            # Save approval request
            approvals.append(approval_request)
            save_db(APPROVALS_DB_FILE, approvals)
            
            # Send notification to admin (integrate with notification system)
            try:
                from tools.notification_tool import SendNotificationTool
                notif_tool = SendNotificationTool()
                # In real system, send to actual admin
                # notif_tool._run(recipient_id='ADMIN001', ...)
            except:
                pass  # Notification optional
            
            # Format output
            priority_emoji = {
                'low': '🔵',
                'medium': '🟡',
                'high': '🟠',
                'critical': '🔴'
            }
            
            tier_emoji = {
                'tier1_auto_execute': '✅',
                'tier2_request_approval': '⚠️',
                'tier3_admin_authorization': '🔴'
            }
            
            output = f"\n{'='*60}\n"
            output += f"⚠️ APPROVAL REQUEST CREATED\n"
            output += f"{'='*60}\n\n"
            output += f"🆔 Approval ID: {approval_request['approval_id']}\n"
            output += f"{tier_emoji.get(tier, '⚪')} Tier: {tier.replace('_', ' ').title()}\n"
            output += f"📋 Action: {action_type}\n"
            output += f"{priority_emoji.get(priority, '⚪')} Priority: {priority.upper()}\n"
            output += f"👤 Requester: {requester}\n"
            output += f"📅 Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            output += f"⏰ Timeout: {timeout_hours} hours\n"
            
            if tier_config.get('requires_admin'):
                output += f"🔐 Requires: Admin Authorization\n"
            
            output += f"\n{'='*60}\n"
            output += f"REQUEST DETAILS\n"
            output += f"{'='*60}\n\n"
            output += f"Reason: {reason}\n\n"
            
            if estimated_cost:
                output += f"💰 Estimated Cost: ${estimated_cost:.2f}\n"
            
            if affected_entities:
                output += f"👥 Affected: {', '.join(affected_entities)}\n"
            
            output += f"\nDetails:\n"
            for key, value in details.items():
                output += f"  • {key}: {value}\n"
            
            output += f"\n{'='*60}\n"
            output += f"📊 Status: PENDING APPROVAL\n"
            output += f"{'='*60}\n\n"
            output += f"✉️ Admin notification sent\n"
            output += f"⏳ Awaiting approval decision...\n"
            
            return {
                'success': True,
                'tier': tier,
                'approval_required': True,
                'message': output,
                'approval': approval_request
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error creating approval request: {str(e)}'}

# ==================== TOOL 2: Process Approval ====================

class ProcessApprovalInput(BaseModel):
    approval_id: str = Field(description="ID of the approval request to process")
    decision: Literal["approve", "reject", "modify"] = Field(description="Admin decision")
    admin_id: str = Field(description="ID of admin making the decision")
    comments: Optional[str] = Field(default="", description="Optional comments or rejection reason")
    modifications: Optional[dict] = Field(default=None, description="Modifications to the request (if decision is 'modify')")

class ProcessApprovalTool(BaseTool):
    name: str = "process_approval"
    description: str = """Admin processes an approval request. Can approve, reject, or modify the request. 
    If approved, the action will be queued for execution. Includes audit trail."""
    args_schema: type[BaseModel] = ProcessApprovalInput
    
    def _run(self, approval_id: str, decision: str, admin_id: str, 
             comments: str = "", modifications: Optional[dict] = None) -> dict:
        """Process approval decision"""
        
        try:
            # Load approvals
            approvals = load_db(APPROVALS_DB_FILE)
            
            # Find approval request
            approval = next((a for a in approvals if a.get('approval_id') == approval_id), None)
            if not approval:
                return {'success': False, 'message': f'Approval request {approval_id} not found'}
            
            # Check if already processed
            if approval['status'] != 'pending':
                return {
                    'success': False,
                    'message': f'Approval request already {approval["status"]}'
                }
            
            # Check if timed out
            timeout_dt = datetime.fromisoformat(approval['timeout_at'])
            if datetime.now() > timeout_dt:
                approval['status'] = 'timeout'
                approval['status_history'].append({
                    'status': 'timeout',
                    'timestamp': datetime.now().isoformat(),
                    'note': 'Request timed out'
                })
                save_db(APPROVALS_DB_FILE, approvals)
                return {
                    'success': False,
                    'message': f'Approval request has timed out'
                }
            
            # Process decision
            if decision == 'approve':
                approval['status'] = 'approved'
                approval['approved_by'] = admin_id
                approval['approved_at'] = datetime.now().isoformat()
                approval['execution_status'] = 'queued'
                
                approval['status_history'].append({
                    'status': 'approved',
                    'timestamp': datetime.now().isoformat(),
                    'admin': admin_id,
                    'note': comments or 'Approved'
                })
                
                status_msg = "✅ APPROVED - Queued for execution"
                
            elif decision == 'reject':
                approval['status'] = 'rejected'
                approval['approved_by'] = admin_id
                approval['approved_at'] = datetime.now().isoformat()
                approval['rejection_reason'] = comments or 'No reason provided'
                
                approval['status_history'].append({
                    'status': 'rejected',
                    'timestamp': datetime.now().isoformat(),
                    'admin': admin_id,
                    'note': comments or 'Rejected'
                })
                
                status_msg = "❌ REJECTED"
                
            elif decision == 'modify':
                approval['status'] = 'modified'
                approval['approved_by'] = admin_id
                approval['approved_at'] = datetime.now().isoformat()
                
                if modifications:
                    approval['details'].update(modifications)
                    approval['modified_details'] = modifications
                
                approval['status_history'].append({
                    'status': 'modified',
                    'timestamp': datetime.now().isoformat(),
                    'admin': admin_id,
                    'note': comments or 'Modified and approved',
                    'modifications': modifications
                })
                
                # After modification, mark as approved for execution
                approval['status'] = 'approved'
                approval['execution_status'] = 'queued'
                
                status_msg = "✏️ MODIFIED & APPROVED - Queued for execution"
            
            # Save updates
            save_db(APPROVALS_DB_FILE, approvals)
            
            # Format output
            output = f"\n{'='*60}\n"
            output += f"✅ APPROVAL PROCESSED\n"
            output += f"{'='*60}\n\n"
            output += f"🆔 Approval ID: {approval_id}\n"
            output += f"📋 Action: {approval['action_type']}\n"
            output += f"👤 Admin: {admin_id}\n"
            output += f"🗳️ Decision: {decision.upper()}\n"
            output += f"📅 Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            output += f"\n{'='*60}\n"
            output += f"STATUS: {status_msg}\n"
            output += f"{'='*60}\n\n"
            
            if comments:
                output += f"💬 Comments: {comments}\n\n"
            
            if modifications:
                output += f"✏️ Modifications:\n"
                for key, value in modifications.items():
                    output += f"  • {key}: {value}\n"
                output += "\n"
            
            if decision == 'approve' or (decision == 'modify' and approval['status'] == 'approved'):
                output += f"⏳ Action queued for execution\n"
                output += f"📊 Execution status: {approval['execution_status']}\n"
            
            output += f"\n{'='*60}\n"
            output += f"AUDIT TRAIL ({len(approval['status_history'])} entries)\n"
            output += f"{'='*60}\n\n"
            
            for entry in approval['status_history']:
                output += f"• {entry['timestamp'][:19]} - {entry['status'].upper()}\n"
                if 'note' in entry:
                    output += f"  {entry['note']}\n"
            
            output += f"\n{'='*60}\n"
            
            return {
                'success': True,
                'message': output,
                'approval': approval,
                'decision': decision
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error processing approval: {str(e)}'}

# ==================== TOOL 3: Get Pending Approvals ====================

class GetPendingApprovalsInput(BaseModel):
    filter_priority: Optional[Literal["low", "medium", "high", "critical"]] = Field(default=None, description="Filter by priority")
    filter_tier: Optional[Literal["tier2_request_approval", "tier3_admin_authorization"]] = Field(default=None, description="Filter by tier")
    filter_action_type: Optional[str] = Field(default=None, description="Filter by action type")
    include_expired: bool = Field(default=False, description="Include expired/timed out requests")
    sort_by: Literal["priority", "created_date", "timeout_date"] = Field(default="priority", description="Sort order")

class GetPendingApprovalsTool(BaseTool):
    name: str = "get_pending_approvals"
    description: str = """Get list of pending approval requests. Can filter by priority, tier, action type. 
    Shows all requests awaiting admin decision. Used in admin dashboard approval center."""
    args_schema: type[BaseModel] = GetPendingApprovalsInput
    
    def _run(self, filter_priority: Optional[str] = None, filter_tier: Optional[str] = None,
             filter_action_type: Optional[str] = None, include_expired: bool = False,
             sort_by: str = "priority") -> dict:
        """Get pending approval requests"""
        
        try:
            # Load approvals
            approvals = load_db(APPROVALS_DB_FILE)
            
            if not approvals:
                return {
                    'success': True,
                    'message': '✅ No pending approvals. All clear!',
                    'pending': []
                }
            
            # Filter pending
            pending = [a for a in approvals if a.get('status') == 'pending']
            
            # Check for expired
            now = datetime.now()
            for approval in pending:
                timeout_dt = datetime.fromisoformat(approval['timeout_at'])
                if now > timeout_dt:
                    approval['is_expired'] = True
                else:
                    approval['is_expired'] = False
            
            # Filter expired
            if not include_expired:
                pending = [a for a in pending if not a.get('is_expired', False)]
            
            # Apply filters
            if filter_priority:
                pending = [a for a in pending if a.get('priority') == filter_priority]
            
            if filter_tier:
                pending = [a for a in pending if a.get('tier') == filter_tier]
            
            if filter_action_type:
                pending = [a for a in pending if a.get('action_type') == filter_action_type]
            
            # Sort
            priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            
            if sort_by == 'priority':
                pending.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 3))
            elif sort_by == 'created_date':
                pending.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            elif sort_by == 'timeout_date':
                pending.sort(key=lambda x: x.get('timeout_at', ''))
            
            # Calculate statistics
            total_pending = len(pending)
            by_priority = {}
            by_tier = {}
            by_action = {}
            
            for approval in pending:
                # Priority
                prio = approval.get('priority', 'unknown')
                by_priority[prio] = by_priority.get(prio, 0) + 1
                
                # Tier
                tier = approval.get('tier', 'unknown')
                by_tier[tier] = by_tier.get(tier, 0) + 1
                
                # Action type
                action = approval.get('action_type', 'unknown')
                by_action[action] = by_action.get(action, 0) + 1
            
            # Format output
            priority_emoji = {
                'low': '🔵',
                'medium': '🟡',
                'high': '🟠',
                'critical': '🔴'
            }
            
            tier_emoji = {
                'tier2_request_approval': '⚠️',
                'tier3_admin_authorization': '🔴'
            }
            
            output = f"\n{'='*60}\n"
            output += f"📋 PENDING APPROVALS\n"
            output += f"{'='*60}\n\n"
            output += f"📊 Total Pending: {total_pending}\n"
            
            if filter_priority:
                output += f"🔍 Filtered by Priority: {filter_priority}\n"
            if filter_tier:
                output += f"🔍 Filtered by Tier: {filter_tier}\n"
            if filter_action_type:
                output += f"🔍 Filtered by Action: {filter_action_type}\n"
            
            output += f"📅 As of: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            output += f"\n{'='*60}\n"
            output += f"STATISTICS\n"
            output += f"{'='*60}\n\n"
            
            output += "By Priority:\n"
            for prio in ['critical', 'high', 'medium', 'low']:
                if prio in by_priority:
                    count = by_priority[prio]
                    output += f"  {priority_emoji.get(prio, '⚪')} {prio.upper()}: {count}\n"
            
            output += "\nBy Tier:\n"
            for tier, count in by_tier.items():
                tier_name = tier.replace('_', ' ').title()
                output += f"  {tier_emoji.get(tier, '⚪')} {tier_name}: {count}\n"
            
            output += f"\n{'='*60}\n"
            output += f"PENDING REQUESTS (Showing {min(10, total_pending)})\n"
            output += f"{'='*60}\n\n"
            
            for approval in pending[:10]:
                prio = approval.get('priority', 'medium')
                tier = approval.get('tier', 'unknown')
                
                output += f"{priority_emoji.get(prio, '⚪')} {approval.get('approval_id')}\n"
                output += f"   Action: {approval.get('action_type')}\n"
                output += f"   Requester: {approval.get('requester')}\n"
                output += f"   Priority: {prio.upper()} | Tier: {tier_emoji.get(tier, '⚪')} {tier.replace('_', ' ').title()}\n"
                output += f"   Created: {approval.get('created_at', 'N/A')[:19]}\n"
                output += f"   Timeout: {approval.get('timeout_at', 'N/A')[:19]}\n"
                
                if approval.get('is_expired'):
                    output += f"   ⚠️ STATUS: EXPIRED\n"
                
                if approval.get('estimated_cost'):
                    output += f"   💰 Cost: ${approval['estimated_cost']:.2f}\n"
                
                output += f"   Reason: {approval.get('reason', 'N/A')[:60]}...\n\n"
            
            if total_pending > 10:
                output += f"... and {total_pending - 10} more pending approvals\n\n"
            
            output += f"{'='*60}\n"
            output += f"💡 Use 'process_approval' tool to approve/reject requests\n"
            output += f"{'='*60}\n"
            
            return {
                'success': True,
                'message': output,
                'statistics': {
                    'total_pending': total_pending,
                    'by_priority': by_priority,
                    'by_tier': by_tier,
                    'by_action': by_action
                },
                'pending': pending
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error retrieving pending approvals: {str(e)}'}

# ==================== TOOL 4: Get Approval History ====================

class GetApprovalHistoryInput(BaseModel):
    days: int = Field(default=30, description="Number of days to look back")
    filter_status: Optional[Literal["approved", "rejected", "timeout", "executed", "failed"]] = Field(default=None, description="Filter by status")
    filter_admin: Optional[str] = Field(default=None, description="Filter by admin who processed")
    limit: int = Field(default=50, description="Maximum number of records to return")

class GetApprovalHistoryTool(BaseTool):
    name: str = "get_approval_history"
    description: str = """Get approval history with audit trail. Shows all processed approval requests 
    including approved, rejected, and executed actions. Useful for compliance and auditing."""
    args_schema: type[BaseModel] = GetApprovalHistoryInput
    
    def _run(self, days: int = 30, filter_status: Optional[str] = None, 
             filter_admin: Optional[str] = None, limit: int = 50) -> dict:
        """Get approval history"""
        
        try:
            # Load approvals
            approvals = load_db(APPROVALS_DB_FILE)
            
            if not approvals:
                return {
                    'success': True,
                    'message': 'No approval history found.',
                    'history': []
                }
            
            # Calculate date cutoff
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Filter by date
            history = [a for a in approvals if a.get('created_at', '9999') >= cutoff_date]
            
            # Exclude pending
            history = [a for a in history if a.get('status') != 'pending']
            
            # Apply filters
            if filter_status:
                history = [a for a in history if a.get('status') == filter_status]
            
            if filter_admin:
                history = [a for a in history if a.get('approved_by') == filter_admin]
            
            # Sort by date (most recent first)
            history.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            # Limit results
            history = history[:limit]
            
            # Calculate statistics
            total_count = len(history)
            by_status = {}
            by_action = {}
            by_admin = {}
            
            for approval in history:
                # Status
                status = approval.get('status', 'unknown')
                by_status[status] = by_status.get(status, 0) + 1
                
                # Action type
                action = approval.get('action_type', 'unknown')
                by_action[action] = by_action.get(action, 0) + 1
                
                # Admin
                admin = approval.get('approved_by', 'unknown')
                if admin and admin != 'unknown':
                    by_admin[admin] = by_admin.get(admin, 0) + 1
            
            # Format output
            status_emoji = {
                'approved': '✅',
                'rejected': '❌',
                'timeout': '⏰',
                'executed': '✔️',
                'failed': '🔴',
                'modified': '✏️'
            }
            
            output = f"\n{'='*60}\n"
            output += f"📜 APPROVAL HISTORY\n"
            output += f"{'='*60}\n\n"
            output += f"📅 Period: Last {days} days\n"
            output += f"📊 Total Records: {total_count}\n"
            
            if filter_status:
                output += f"🔍 Filtered by Status: {filter_status}\n"
            if filter_admin:
                output += f"🔍 Filtered by Admin: {filter_admin}\n"
            
            output += f"\n{'='*60}\n"
            output += f"STATISTICS\n"
            output += f"{'='*60}\n\n"
            
            output += "By Status:\n"
            for status, count in sorted(by_status.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_count * 100) if total_count > 0 else 0
                output += f"  {status_emoji.get(status, '⚪')} {status.upper()}: {count} ({percentage:.1f}%)\n"
            
            if by_admin:
                output += "\nBy Admin:\n"
                for admin, count in sorted(by_admin.items(), key=lambda x: x[1], reverse=True)[:5]:
                    output += f"  • {admin}: {count}\n"
            
            output += f"\n{'='*60}\n"
            output += f"RECENT HISTORY (Showing {min(10, total_count)})\n"
            output += f"{'='*60}\n\n"
            
            for approval in history[:10]:
                status = approval.get('status', 'unknown')
                
                output += f"{status_emoji.get(status, '⚪')} {approval.get('approval_id')}\n"
                output += f"   Action: {approval.get('action_type')}\n"
                output += f"   Status: {status.upper()}\n"
                output += f"   Requester: {approval.get('requester')}\n"
                
                if approval.get('approved_by'):
                    output += f"   Processed By: {approval.get('approved_by')}\n"
                    output += f"   Processed: {approval.get('approved_at', 'N/A')[:19]}\n"
                
                if approval.get('execution_status'):
                    output += f"   Execution: {approval.get('execution_status')}\n"
                
                output += f"   Created: {approval.get('created_at', 'N/A')[:19]}\n\n"
            
            if total_count > 10:
                output += f"... and {total_count - 10} more records\n\n"
            
            output += f"{'='*60}\n"
            
            # Calculate approval rate
            if total_count > 0:
                approved_count = by_status.get('approved', 0)
                approval_rate = (approved_count / total_count * 100)
                output += f"📊 Approval Rate: {approval_rate:.1f}%\n"
                output += f"{'='*60}\n"
            
            return {
                'success': True,
                'message': output,
                'statistics': {
                    'total_count': total_count,
                    'by_status': by_status,
                    'by_action': by_action,
                    'by_admin': by_admin
                },
                'history': history
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error retrieving approval history: {str(e)}'}

# ==================== TOOL 5: Execute Approved Action ====================

class ExecuteApprovedActionInput(BaseModel):
    approval_id: str = Field(description="ID of the approved request to execute")
    executor_id: str = Field(description="ID of the system/user executing the action")

class ExecuteApprovedActionTool(BaseTool):
    name: str = "execute_approved_action"
    description: str = """Execute an approved action. Only works on approved requests. Updates execution status 
    and records result. This is called by the system after admin approves a request."""
    args_schema: type[BaseModel] = ExecuteApprovedActionInput
    
    def _run(self, approval_id: str, executor_id: str) -> dict:
        """Execute approved action"""
        
        try:
            # Load approvals
            approvals = load_db(APPROVALS_DB_FILE)
            
            # Find approval
            approval = next((a for a in approvals if a.get('approval_id') == approval_id), None)
            if not approval:
                return {'success': False, 'message': f'Approval {approval_id} not found'}
            
            # Check status
            if approval['status'] != 'approved':
                return {
                    'success': False,
                    'message': f'Cannot execute: Approval status is {approval["status"]}'
                }
            
            if approval.get('execution_status') == 'executed':
                return {
                    'success': False,
                    'message': 'Action already executed'
                }
            
            # Update execution status
            approval['execution_status'] = 'executing'
            approval['executed_by'] = executor_id
            approval['executed_at'] = datetime.now().isoformat()
            
            # Simulate execution (in real system, call the actual tool)
            action_type = approval['action_type']
            details = approval['details']
            
            execution_result = {
                'status': 'success',
                'message': f'Successfully executed {action_type}',
                'executed_at': datetime.now().isoformat(),
                'details': details
            }
            
            # In real system, route to actual tool execution:
            # if action_type == 'schedule_appointment':
            #     from tools.appointment_tool import ScheduleAppointmentTool
            #     tool = ScheduleAppointmentTool()
            #     execution_result = tool._run(**details)
            
            approval['execution_status'] = 'executed'
            approval['execution_result'] = execution_result
            
            approval['status_history'].append({
                'status': 'executed',
                'timestamp': datetime.now().isoformat(),
                'executor': executor_id,
                'note': 'Action executed successfully'
            })
            
            # Save updates
            save_db(APPROVALS_DB_FILE, approvals)
            
            # Format output
            output = f"\n{'='*60}\n"
            output += f"✅ ACTION EXECUTED\n"
            output += f"{'='*60}\n\n"
            output += f"🆔 Approval ID: {approval_id}\n"
            output += f"📋 Action: {action_type}\n"
            output += f"👤 Executor: {executor_id}\n"
            output += f"📅 Executed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            output += f"\n{'='*60}\n"
            output += f"EXECUTION RESULT\n"
            output += f"{'='*60}\n\n"
            output += f"Status: {execution_result['status'].upper()}\n"
            output += f"Message: {execution_result['message']}\n"
            output += f"\n{'='*60}\n"
            
            return {
                'success': True,
                'message': output,
                'approval': approval,
                'execution_result': execution_result
            }
            
        except Exception as e:
            # Mark execution as failed
            try:
                approval['execution_status'] = 'failed'
                approval['execution_error'] = str(e)
                approval['status_history'].append({
                    'status': 'failed',
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                })
                save_db(APPROVALS_DB_FILE, approvals)
            except:
                pass
            
            return {'success': False, 'message': f'Error executing action: {str(e)}'}

# Export all tools
__all__ = [
    'CreateApprovalRequestTool',
    'ProcessApprovalTool',
    'GetPendingApprovalsTool',
    'GetApprovalHistoryTool',
    'ExecuteApprovedActionTool'
]
