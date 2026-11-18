"""
Test Enhanced Google Sheets Monitoring Integration
Comprehensive testing for the staff-agent communication system through Google Sheets.

Tests include:
1. Monitoring tools functionality
2. Billing integration
3. Staff communication workflows
4. Emergency alert processing
5. Real-time bidirectional communication
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.sheets_monitoring_tool import (
    MonitorSheetChangesTool, ReadStaffUpdatesTool, UpdatePatientStatusTool,
    StaffNotificationTool, SheetAnalyticsTool
)
from tools.billing_sheets_tool import (
    CreateBillingRecordTool, ReadBillingInfoTool, UpdatePaymentStatusTool,
    GenerateInvoiceTool, GetBillingSummaryTool
)
from enhanced_workflow import EnhancedHospitalWorkflow

class TestEnhancedIntegration:
    """Test suite for enhanced Google Sheets monitoring integration."""
    
    def __init__(self):
        """Initialize test suite."""
        self.test_results = []
        self.workflow = EnhancedHospitalWorkflow()
        
        # Initialize individual tools for testing
        self.monitor_tool = MonitorSheetChangesTool()
        self.staff_updates_tool = ReadStaffUpdatesTool()
        self.patient_status_tool = UpdatePatientStatusTool()
        self.notification_tool = StaffNotificationTool()
        self.analytics_tool = SheetAnalyticsTool()
        
        # Initialize billing tools
        self.create_billing_tool = CreateBillingRecordTool()
        self.read_billing_tool = ReadBillingInfoTool()
        self.update_payment_tool = UpdatePaymentStatusTool()
        self.generate_invoice_tool = GenerateInvoiceTool()
        self.billing_summary_tool = GetBillingSummaryTool()
    
    def log_test_result(self, test_name: str, success: bool, message: str = "", details: Any = None):
        """Log a test result."""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    async def test_monitor_sheet_changes(self):
        """Test sheet change monitoring functionality."""
        try:
            print("\n📊 Testing Sheet Change Monitoring...")
            
            # Test monitoring different sheet types
            sheet_types = ["patient_status", "doctor_notes", "lab_results", "staff_updates"]
            
            for sheet_type in sheet_types:
                try:
                    result = await self.monitor_tool.arun(
                        sheet_type=sheet_type,
                        check_interval=5
                    )
                    
                    self.log_test_result(
                        f"Monitor {sheet_type} sheet",
                        True,
                        f"Monitoring successful - {result.get('message', 'No changes detected')}"
                    )
                    
                except Exception as e:
                    self.log_test_result(
                        f"Monitor {sheet_type} sheet",
                        False,
                        "Monitoring failed",
                        str(e)
                    )
            
        except Exception as e:
            self.log_test_result(
                "Sheet Change Monitoring",
                False,
                "Test setup failed",
                str(e)
            )
    
    async def test_staff_updates_reading(self):
        """Test reading staff updates from sheets."""
        try:
            print("\n👥 Testing Staff Updates Reading...")
            
            # Test reading updates for different departments
            departments = ["DOCTORS", "NURSES", "PHARMACY", "LAB", "ALL"]
            
            for department in departments:
                try:
                    result = await self.staff_updates_tool.arun(
                        department=department,
                        status_filter="PENDING"
                    )
                    
                    updates_count = len(result.get('updates', []))
                    self.log_test_result(
                        f"Read {department} updates",
                        True,
                        f"Found {updates_count} pending updates"
                    )
                    
                except Exception as e:
                    self.log_test_result(
                        f"Read {department} updates",
                        False,
                        "Reading failed",
                        str(e)
                    )
            
        except Exception as e:
            self.log_test_result(
                "Staff Updates Reading",
                False,
                "Test setup failed",
                str(e)
            )
    
    async def test_patient_status_updates(self):
        """Test updating patient status."""
        try:
            print("\n🏥 Testing Patient Status Updates...")
            
            # Test different types of status updates
            test_updates = [
                {
                    "patient_id": "REG2025001",
                    "status_type": "Vitals",
                    "status_value": "BP: 125/82, HR: 75, Temp: 98.6°F",
                    "updated_by": "Test Nurse"
                },
                {
                    "patient_id": "REG2025002",
                    "status_type": "Medication",
                    "status_value": "Antibiotics administered at 10:00 AM",
                    "updated_by": "Test Pharmacist"
                },
                {
                    "patient_id": "REG2025003",
                    "status_type": "Treatment Plan",
                    "status_value": "Physical therapy scheduled for tomorrow",
                    "updated_by": "Test Doctor"
                }
            ]
            
            for update in test_updates:
                try:
                    result = await self.patient_status_tool.arun(**update)
                    
                    self.log_test_result(
                        f"Update {update['patient_id']} {update['status_type']}",
                        True,
                        f"Status updated successfully"
                    )
                    
                except Exception as e:
                    self.log_test_result(
                        f"Update {update['patient_id']} {update['status_type']}",
                        False,
                        "Update failed",
                        str(e)
                    )
            
        except Exception as e:
            self.log_test_result(
                "Patient Status Updates",
                False,
                "Test setup failed",
                str(e)
            )
    
    async def test_staff_notifications(self):
        """Test staff notification system."""
        try:
            print("\n📢 Testing Staff Notifications...")
            
            # Test different notification types
            test_notifications = [
                {
                    "target_department": "DOCTORS",
                    "priority": "HIGH",
                    "message": "Patient REG2025001 requires immediate attention - elevated BP",
                    "patient_id": "REG2025001"
                },
                {
                    "target_department": "NURSES",
                    "priority": "NORMAL",
                    "message": "Medication administration reminder for patient REG2025002",
                    "patient_id": "REG2025002"
                },
                {
                    "target_department": "PHARMACY",
                    "priority": "NORMAL",
                    "message": "Low stock alert: Paracetamol below minimum threshold",
                    "patient_id": None
                }
            ]
            
            for notification in test_notifications:
                try:
                    result = await self.notification_tool.arun(**notification)
                    
                    self.log_test_result(
                        f"Notify {notification['target_department']} ({notification['priority']})",
                        True,
                        f"Notification sent successfully"
                    )
                    
                except Exception as e:
                    self.log_test_result(
                        f"Notify {notification['target_department']} ({notification['priority']})",
                        False,
                        "Notification failed",
                        str(e)
                    )
            
        except Exception as e:
            self.log_test_result(
                "Staff Notifications",
                False,
                "Test setup failed",
                str(e)
            )
    
    async def test_sheet_analytics(self):
        """Test sheet analytics functionality."""
        try:
            print("\n📈 Testing Sheet Analytics...")
            
            # Test analytics for different sheet types and date ranges
            test_analytics = [
                {"sheet_type": "patient_status", "date_range": "TODAY"},
                {"sheet_type": "doctor_notes", "date_range": "WEEK"},
                {"sheet_type": "lab_results", "date_range": "TODAY"},
                {"sheet_type": "ALL", "date_range": "TODAY"}
            ]
            
            for analytics_test in test_analytics:
                try:
                    result = await self.analytics_tool.arun(**analytics_test)
                    
                    self.log_test_result(
                        f"Analytics {analytics_test['sheet_type']} ({analytics_test['date_range']})",
                        True,
                        f"Analytics generated successfully"
                    )
                    
                except Exception as e:
                    self.log_test_result(
                        f"Analytics {analytics_test['sheet_type']} ({analytics_test['date_range']})",
                        False,
                        "Analytics failed",
                        str(e)
                    )
            
        except Exception as e:
            self.log_test_result(
                "Sheet Analytics",
                False,
                "Test setup failed",
                str(e)
            )
    
    async def test_billing_integration(self):
        """Test billing sheets integration."""
        try:
            print("\n💰 Testing Billing Integration...")
            
            # Test creating billing record
            try:
                billing_result = await self.create_billing_tool.arun(
                    patient_id="REG2025001",
                    service_type="Consultation",
                    amount=1500.00,
                    insurance_coverage=80,
                    notes="General consultation with Dr. Smith"
                )
                
                self.log_test_result(
                    "Create billing record",
                    True,
                    "Billing record created successfully"
                )
                
            except Exception as e:
                self.log_test_result(
                    "Create billing record",
                    False,
                    "Failed to create billing record",
                    str(e)
                )
            
            # Test reading billing info
            try:
                billing_info = await self.read_billing_tool.arun(
                    patient_id="REG2025001"
                )
                
                self.log_test_result(
                    "Read billing info",
                    True,
                    f"Found billing information for patient"
                )
                
            except Exception as e:
                self.log_test_result(
                    "Read billing info",
                    False,
                    "Failed to read billing info",
                    str(e)
                )
            
            # Test payment status update
            try:
                payment_result = await self.update_payment_tool.arun(
                    patient_id="REG2025001",
                    payment_amount=300.00,  # Partial payment
                    payment_method="Card",
                    notes="Partial payment received"
                )
                
                self.log_test_result(
                    "Update payment status",
                    True,
                    "Payment status updated successfully"
                )
                
            except Exception as e:
                self.log_test_result(
                    "Update payment status",
                    False,
                    "Failed to update payment",
                    str(e)
                )
            
            # Test invoice generation
            try:
                invoice_result = await self.generate_invoice_tool.arun(
                    patient_id="REG2025001"
                )
                
                self.log_test_result(
                    "Generate invoice",
                    True,
                    "Invoice generated successfully"
                )
                
            except Exception as e:
                self.log_test_result(
                    "Generate invoice",
                    False,
                    "Failed to generate invoice",
                    str(e)
                )
            
            # Test billing summary
            try:
                summary_result = await self.billing_summary_tool.arun(
                    date_range="TODAY"
                )
                
                self.log_test_result(
                    "Get billing summary",
                    True,
                    "Billing summary generated successfully"
                )
                
            except Exception as e:
                self.log_test_result(
                    "Get billing summary",
                    False,
                    "Failed to get billing summary",
                    str(e)
                )
            
        except Exception as e:
            self.log_test_result(
                "Billing Integration",
                False,
                "Test setup failed",
                str(e)
            )
    
    async def test_workflow_integration(self):
        """Test enhanced workflow integration."""
        try:
            print("\n🔄 Testing Workflow Integration...")
            
            # Test workflow initialization
            try:
                workflow = EnhancedHospitalWorkflow()
                self.log_test_result(
                    "Workflow initialization",
                    True,
                    "Enhanced workflow initialized successfully"
                )
                
            except Exception as e:
                self.log_test_result(
                    "Workflow initialization",
                    False,
                    "Failed to initialize workflow",
                    str(e)
                )
            
            # Test daily report generation
            try:
                daily_report = await workflow.generate_daily_report()
                
                self.log_test_result(
                    "Daily report generation",
                    True,
                    f"Daily report generated for {daily_report.get('date', 'unknown date')}"
                )
                
            except Exception as e:
                self.log_test_result(
                    "Daily report generation",
                    False,
                    "Failed to generate daily report",
                    str(e)
                )
            
        except Exception as e:
            self.log_test_result(
                "Workflow Integration",
                False,
                "Test setup failed",
                str(e)
            )
    
    async def test_bidirectional_communication(self):
        """Test bidirectional communication between staff and AI."""
        try:
            print("\n🔄 Testing Bidirectional Communication...")
            
            # Simulate staff updating sheet -> AI reading and responding
            try:
                # 1. AI sends notification to staff
                await self.notification_tool.arun(
                    target_department="NURSES",
                    priority="NORMAL",
                    message="Please check vitals for patient REG2025001",
                    patient_id="REG2025001"
                )
                
                # 2. AI updates patient status (simulating staff response)
                await self.patient_status_tool.arun(
                    patient_id="REG2025001",
                    status_type="Vitals Check",
                    status_value="Vitals recorded: BP 118/78, HR 72, normal",
                    updated_by="Nurse Response"
                )
                
                # 3. AI reads staff updates to confirm completion
                staff_updates = await self.staff_updates_tool.arun(
                    department="NURSES",
                    status_filter="PENDING"
                )
                
                self.log_test_result(
                    "Bidirectional communication flow",
                    True,
                    "Staff-AI communication cycle completed successfully"
                )
                
            except Exception as e:
                self.log_test_result(
                    "Bidirectional communication flow",
                    False,
                    "Communication flow failed",
                    str(e)
                )
            
        except Exception as e:
            self.log_test_result(
                "Bidirectional Communication",
                False,
                "Test setup failed",
                str(e)
            )
    
    async def run_all_tests(self):
        """Run all integration tests."""
        print("🧪" + "=" * 70)
        print("  ENHANCED GOOGLE SHEETS MONITORING INTEGRATION TESTS")
        print("=" * 70)
        
        # Run all test suites
        await self.test_monitor_sheet_changes()
        await self.test_staff_updates_reading()
        await self.test_patient_status_updates()
        await self.test_staff_notifications()
        await self.test_sheet_analytics()
        await self.test_billing_integration()
        await self.test_workflow_integration()
        await self.test_bidirectional_communication()
        
        # Generate test summary
        self.generate_test_summary()
    
    def generate_test_summary(self):
        """Generate and display test summary."""
        print("\n" + "=" * 70)
        print("  TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("🎉 ALL TESTS PASSED! Enhanced integration is ready for production.")
        elif success_rate >= 80:
            print("⚠️  Most tests passed. Review failed tests before deployment.")
        else:
            print("🚨 Multiple test failures. Integration needs fixes before deployment.")
        
        # Show failed tests details
        if failed_tests > 0:
            print(f"\n❌ Failed Tests Details:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test_name']}: {result['message']}")
                    if result['details']:
                        print(f"     Details: {result['details']}")
        
        # Save detailed results to file
        with open('test_results_enhanced_integration.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: test_results_enhanced_integration.json")
        print("=" * 70)

async def main():
    """Main function to run the enhanced integration tests."""
    try:
        tester = TestEnhancedIntegration()
        await tester.run_all_tests()
        
    except Exception as e:
        print(f"❌ Test runner error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())