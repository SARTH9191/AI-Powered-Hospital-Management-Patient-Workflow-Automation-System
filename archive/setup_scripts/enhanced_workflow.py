"""
Hospital Workflow with Enhanced Google Sheets Monitoring Integration
Integrates the newly created monitoring tools into the existing workflow system.

This module provides:
1. Real-time staff communication through Google Sheets
2. Bidirectional updates between AI agent and hospital staff
3. Automated monitoring and notifications
4. Integration with existing workflow stages
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Import existing workflow tools
from tools.registration_tool import RegistrationTool
from tools.appointment_tool import AppointmentTool
from tools.billing_sheets_tool import (
    CreateBillingRecordTool, ReadBillingInfoTool, UpdatePaymentStatusTool,
    GenerateInvoiceTool, GetBillingSummaryTool
)
from tools.sheets_monitoring_tool import (
    MonitorSheetChangesTool, ReadStaffUpdatesTool, UpdatePatientStatusTool,
    StaffNotificationTool, SheetAnalyticsTool
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedHospitalWorkflow:
    """Enhanced hospital workflow with Google Sheets monitoring integration."""
    
    def __init__(self):
        """Initialize the enhanced workflow with all tools."""
        self.monitoring_active = False
        self.monitoring_interval = 30  # seconds
        
        # Initialize existing tools
        self.registration_tool = RegistrationTool()
        self.appointment_tool = AppointmentTool()
        
        # Initialize billing tools
        self.create_billing_tool = CreateBillingRecordTool()
        self.read_billing_tool = ReadBillingInfoTool()
        self.update_payment_tool = UpdatePaymentStatusTool()
        self.generate_invoice_tool = GenerateInvoiceTool()
        self.billing_summary_tool = GetBillingSummaryTool()
        
        # Initialize monitoring tools
        self.monitor_changes_tool = MonitorSheetChangesTool()
        self.read_staff_updates_tool = ReadStaffUpdatesTool()
        self.update_patient_status_tool = UpdatePatientStatusTool()
        self.staff_notification_tool = StaffNotificationTool()
        self.sheet_analytics_tool = SheetAnalyticsTool()
        
        logger.info("Enhanced Hospital Workflow initialized with all tools")
    
    async def start_monitoring(self):
        """Start the monitoring system for real-time staff communication."""
        logger.info("Starting Google Sheets monitoring system...")
        self.monitoring_active = True
        
        # Start monitoring tasks
        monitoring_tasks = [
            asyncio.create_task(self.monitor_patient_status()),
            asyncio.create_task(self.monitor_doctor_notes()),
            asyncio.create_task(self.monitor_lab_results()),
            asyncio.create_task(self.monitor_staff_updates()),
            asyncio.create_task(self.monitor_emergency_alerts()),
            asyncio.create_task(self.monitor_pharmacy_inventory())
        ]
        
        logger.info(f"Started {len(monitoring_tasks)} monitoring tasks")
        await asyncio.gather(*monitoring_tasks)
    
    async def stop_monitoring(self):
        """Stop the monitoring system."""
        logger.info("Stopping Google Sheets monitoring system...")
        self.monitoring_active = False
    
    async def monitor_patient_status(self):
        """Monitor patient status sheet for updates from staff."""
        while self.monitoring_active:
            try:
                # Monitor for changes in patient status sheet
                changes = await self.monitor_changes_tool.arun(
                    sheet_type="patient_status",
                    check_interval=self.monitoring_interval
                )
                
                if changes and changes.get('has_changes'):
                    logger.info("Patient status updates detected")
                    await self.process_patient_status_changes(changes)
                
            except Exception as e:
                logger.error(f"Error monitoring patient status: {e}")
            
            await asyncio.sleep(self.monitoring_interval)
    
    async def monitor_doctor_notes(self):
        """Monitor doctor notes sheet for new notes and updates."""
        while self.monitoring_active:
            try:
                changes = await self.monitor_changes_tool.arun(
                    sheet_type="doctor_notes",
                    check_interval=self.monitoring_interval
                )
                
                if changes and changes.get('has_changes'):
                    logger.info("Doctor notes updates detected")
                    await self.process_doctor_notes_changes(changes)
                
            except Exception as e:
                logger.error(f"Error monitoring doctor notes: {e}")
            
            await asyncio.sleep(self.monitoring_interval)
    
    async def monitor_lab_results(self):
        """Monitor lab results sheet for new results."""
        while self.monitoring_active:
            try:
                changes = await self.monitor_changes_tool.arun(
                    sheet_type="lab_results",
                    check_interval=self.monitoring_interval
                )
                
                if changes and changes.get('has_changes'):
                    logger.info("Lab results updates detected")
                    await self.process_lab_results_changes(changes)
                
            except Exception as e:
                logger.error(f"Error monitoring lab results: {e}")
            
            await asyncio.sleep(self.monitoring_interval)
    
    async def monitor_staff_updates(self):
        """Monitor staff updates sheet for communications."""
        while self.monitoring_active:
            try:
                staff_updates = await self.read_staff_updates_tool.arun(
                    department="ALL",
                    status_filter="PENDING"
                )
                
                if staff_updates and staff_updates.get('updates'):
                    logger.info(f"Found {len(staff_updates['updates'])} pending staff updates")
                    await self.process_staff_updates(staff_updates['updates'])
                
            except Exception as e:
                logger.error(f"Error monitoring staff updates: {e}")
            
            await asyncio.sleep(self.monitoring_interval)
    
    async def monitor_emergency_alerts(self):
        """Monitor emergency alerts sheet for urgent situations."""
        while self.monitoring_active:
            try:
                changes = await self.monitor_changes_tool.arun(
                    sheet_type="emergency_alerts",
                    check_interval=self.monitoring_interval
                )
                
                if changes and changes.get('has_changes'):
                    logger.warning("Emergency alerts detected - processing immediately")
                    await self.process_emergency_alerts(changes)
                
            except Exception as e:
                logger.error(f"Error monitoring emergency alerts: {e}")
            
            await asyncio.sleep(10)  # Check emergencies more frequently
    
    async def monitor_pharmacy_inventory(self):
        """Monitor pharmacy inventory sheet for stock levels."""
        while self.monitoring_active:
            try:
                changes = await self.monitor_changes_tool.arun(
                    sheet_type="pharmacy_inventory",
                    check_interval=self.monitoring_interval
                )
                
                if changes and changes.get('has_changes'):
                    logger.info("Pharmacy inventory updates detected")
                    await self.process_pharmacy_updates(changes)
                
            except Exception as e:
                logger.error(f"Error monitoring pharmacy inventory: {e}")
            
            await asyncio.sleep(self.monitoring_interval)
    
    async def process_patient_status_changes(self, changes: Dict[str, Any]):
        """Process patient status changes and take appropriate actions."""
        try:
            for change in changes.get('changes', []):
                patient_id = change.get('patient_id')
                status_type = change.get('status_type')
                status_value = change.get('status_value')
                
                logger.info(f"Processing status update for {patient_id}: {status_type} = {status_value}")
                
                # Update patient status in database and notify relevant staff
                await self.update_patient_status_tool.arun(
                    patient_id=patient_id,
                    status_type=status_type,
                    status_value=status_value,
                    updated_by="Staff Update"
                )
                
                # If vitals are concerning, notify doctors
                if self.is_concerning_vital(status_type, status_value):
                    await self.staff_notification_tool.arun(
                        target_department="DOCTORS",
                        priority="HIGH",
                        message=f"Patient {patient_id} has concerning {status_type}: {status_value}",
                        patient_id=patient_id
                    )
                
        except Exception as e:
            logger.error(f"Error processing patient status changes: {e}")
    
    async def process_doctor_notes_changes(self, changes: Dict[str, Any]):
        """Process doctor notes and update treatment plans."""
        try:
            for change in changes.get('changes', []):
                patient_id = change.get('patient_id')
                doctor_name = change.get('doctor_name')
                notes = change.get('notes')
                diagnosis = change.get('diagnosis')
                treatment_plan = change.get('treatment_plan')
                priority = change.get('priority', 'Normal')
                
                logger.info(f"Processing doctor notes for {patient_id} by {doctor_name}")
                
                # If high priority, notify nursing staff immediately
                if priority.upper() == 'HIGH':
                    await self.staff_notification_tool.arun(
                        target_department="NURSES",
                        priority="HIGH",
                        message=f"High priority notes from {doctor_name} for patient {patient_id}: {notes}",
                        patient_id=patient_id
                    )
                
                # Update treatment plan if specified
                if treatment_plan:
                    await self.update_patient_status_tool.arun(
                        patient_id=patient_id,
                        status_type="Treatment Plan",
                        status_value=treatment_plan,
                        updated_by=doctor_name
                    )
                
        except Exception as e:
            logger.error(f"Error processing doctor notes changes: {e}")
    
    async def process_lab_results_changes(self, changes: Dict[str, Any]):
        """Process new lab results and notify relevant staff."""
        try:
            for change in changes.get('changes', []):
                patient_id = change.get('patient_id')
                test_name = change.get('test_name')
                result = change.get('result')
                status = change.get('status')
                
                logger.info(f"Processing lab result for {patient_id}: {test_name} = {result} ({status})")
                
                # If abnormal results, notify doctors
                if status.upper() in ['HIGH', 'LOW', 'CRITICAL', 'ABNORMAL']:
                    await self.staff_notification_tool.arun(
                        target_department="DOCTORS",
                        priority="HIGH" if status.upper() == 'CRITICAL' else "NORMAL",
                        message=f"Lab result for {patient_id}: {test_name} is {status} ({result})",
                        patient_id=patient_id
                    )
                
                # Update patient status with lab results
                await self.update_patient_status_tool.arun(
                    patient_id=patient_id,
                    status_type=f"Lab: {test_name}",
                    status_value=f"{result} ({status})",
                    updated_by="Lab System"
                )
                
        except Exception as e:
            logger.error(f"Error processing lab results changes: {e}")
    
    async def process_staff_updates(self, updates: List[Dict[str, Any]]):
        """Process pending staff update requests."""
        try:
            for update in updates:
                notification_id = update.get('notification_id')
                priority = update.get('priority')
                department = update.get('target_department')
                patient_id = update.get('patient_id')
                message = update.get('message')
                staff_response = update.get('staff_response', '').strip()
                
                # If staff has responded, process the response
                if staff_response:
                    logger.info(f"Processing staff response for {notification_id}: {staff_response}")
                    
                    # Update patient status based on staff response
                    if patient_id and patient_id != 'GENERAL':
                        await self.update_patient_status_tool.arun(
                            patient_id=patient_id,
                            status_type="Staff Response",
                            status_value=staff_response,
                            updated_by=f"{department} Staff"
                        )
                    
                    # Mark the notification as resolved
                    # (This would typically update the staff updates sheet)
                    logger.info(f"Notification {notification_id} resolved by {department}")
                
        except Exception as e:
            logger.error(f"Error processing staff updates: {e}")
    
    async def process_emergency_alerts(self, changes: Dict[str, Any]):
        """Process emergency alerts with high priority."""
        try:
            for change in changes.get('changes', []):
                alert_type = change.get('alert_type')
                department = change.get('department')
                patient_id = change.get('patient_id')
                alert_message = change.get('alert_message')
                status = change.get('status')
                
                logger.warning(f"EMERGENCY ALERT: {alert_type} in {department} - {alert_message}")
                
                if status != 'RESOLVED':
                    # Notify all relevant departments for emergencies
                    await self.staff_notification_tool.arun(
                        target_department="ALL",
                        priority="URGENT",
                        message=f"🚨 EMERGENCY: {alert_type} in {department} - {alert_message}",
                        patient_id=patient_id if patient_id != 'GENERAL' else None
                    )
                    
                    # Update patient status if patient-specific
                    if patient_id and patient_id != 'GENERAL':
                        await self.update_patient_status_tool.arun(
                            patient_id=patient_id,
                            status_type="Emergency Alert",
                            status_value=f"{alert_type}: {alert_message}",
                            updated_by="Emergency System"
                        )
                
        except Exception as e:
            logger.error(f"Error processing emergency alerts: {e}")
    
    async def process_pharmacy_updates(self, changes: Dict[str, Any]):
        """Process pharmacy inventory updates."""
        try:
            for change in changes.get('changes', []):
                medicine_name = change.get('medicine_name')
                current_stock = change.get('current_stock')
                minimum_required = change.get('minimum_required')
                status = change.get('status')
                
                logger.info(f"Pharmacy update: {medicine_name} - {current_stock} units ({status})")
                
                # If low stock, notify relevant departments
                if status.upper() in ['LOW STOCK', 'OUT OF STOCK']:
                    await self.staff_notification_tool.arun(
                        target_department="DOCTORS",
                        priority="NORMAL",
                        message=f"Pharmacy Alert: {medicine_name} is {status} ({current_stock} units remaining)",
                        patient_id=None
                    )
                
        except Exception as e:
            logger.error(f"Error processing pharmacy updates: {e}")
    
    def is_concerning_vital(self, status_type: str, status_value: str) -> bool:
        """Check if vital signs are concerning and require immediate attention."""
        try:
            if "BP" in status_type.upper() or "BLOOD PRESSURE" in status_type.upper():
                # Extract systolic/diastolic if in format "120/80"
                if "/" in status_value:
                    systolic = int(status_value.split("/")[0].strip())
                    diastolic = int(status_value.split("/")[1].split(",")[0].strip())
                    if systolic > 140 or systolic < 90 or diastolic > 90 or diastolic < 60:
                        return True
            
            if "HR" in status_type.upper() or "HEART RATE" in status_type.upper():
                # Extract heart rate number
                hr_value = ''.join(filter(str.isdigit, status_value))
                if hr_value:
                    hr = int(hr_value)
                    if hr > 100 or hr < 60:
                        return True
            
            if "TEMP" in status_type.upper() or "FEVER" in status_value.upper():
                return True
                
        except Exception as e:
            logger.error(f"Error checking vital concerns: {e}")
        
        return False
    
    async def generate_daily_report(self) -> Dict[str, Any]:
        """Generate daily analytics report using sheet analytics."""
        try:
            logger.info("Generating daily hospital report...")
            
            analytics = await self.sheet_analytics_tool.arun(
                sheet_type="ALL",
                date_range="TODAY"
            )
            
            report = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "patient_updates": analytics.get('patient_status_updates', 0),
                "doctor_notes": analytics.get('doctor_notes_count', 0),
                "lab_results": analytics.get('lab_results_count', 0),
                "staff_communications": analytics.get('staff_updates_count', 0),
                "emergency_alerts": analytics.get('emergency_alerts_count', 0),
                "pharmacy_updates": analytics.get('pharmacy_updates_count', 0),
                "summary": "Daily hospital operations summary",
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Daily report generated: {report}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating daily report: {e}")
            return {"error": str(e)}

# Integration with existing workflow
async def run_enhanced_workflow():
    """Run the enhanced hospital workflow with monitoring."""
    workflow = EnhancedHospitalWorkflow()
    
    try:
        logger.info("🏥 Starting Enhanced Hospital Workflow with Google Sheets Integration")
        
        # Start monitoring system
        await workflow.start_monitoring()
        
    except KeyboardInterrupt:
        logger.info("Workflow interrupted by user")
    except Exception as e:
        logger.error(f"Workflow error: {e}")
    finally:
        await workflow.stop_monitoring()
        logger.info("Enhanced Hospital Workflow stopped")