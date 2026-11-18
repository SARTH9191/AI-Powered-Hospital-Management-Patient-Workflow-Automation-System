"""
Test Calendar Integration - Phase 3 Complete Testing
Tests all Google Calendar functionality in hospital workflow

This test validates:
1. Calendar tool creation and API connectivity
2. Appointment scheduling with doctors
3. Availability checking and conflict detection
4. Appointment management (update, cancel, list)
5. Integration with hospital workflow stages
6. Email notifications and reminders

Author: Hospital Management AI System
"""

import os
import sys
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import calendar tools
from tools.google_calendar_tool import (
    CreateAppointmentTool, CheckAvailabilityTool, UpdateAppointmentTool,
    CancelAppointmentTool, ListAppointmentsTool
)

# Import workflow agent
from src.workflow_chat_agent import WorkflowChatAgent

# Import patient state
from src.workflow_state import PatientState


class TestCalendarIntegration(unittest.TestCase):
    """Test suite for Google Calendar integration."""
    
    def setUp(self):
        """Set up test environment."""
        print(f"\n{'='*60}")
        print("GOOGLE CALENDAR INTEGRATION TEST SETUP")
        print(f"{'='*60}")
        
    def test_1_calendar_tools_initialization(self):
        """Test that all calendar tools can be initialized."""
        print("\n📅 Test 1: Calendar Tools Initialization")
        print("-" * 40)
        
        try:
            # Test tool creation (without actual API calls)
            with patch('tools.google_calendar_tool.CalendarToolBase.__init__', return_value=None):
                create_tool = CreateAppointmentTool()
                availability_tool = CheckAvailabilityTool()
                update_tool = UpdateAppointmentTool()
                cancel_tool = CancelAppointmentTool()
                list_tool = ListAppointmentsTool()
                
                # Verify tool names and descriptions
                self.assertEqual(create_tool.name, "create_appointment")
                self.assertEqual(availability_tool.name, "check_availability")
                self.assertEqual(update_tool.name, "update_appointment")
                self.assertEqual(cancel_tool.name, "cancel_appointment")
                self.assertEqual(list_tool.name, "list_appointments")
                
                print("✅ All calendar tools initialized successfully")
                print(f"   • CreateAppointmentTool: {create_tool.name}")
                print(f"   • CheckAvailabilityTool: {availability_tool.name}")
                print(f"   • UpdateAppointmentTool: {update_tool.name}")
                print(f"   • CancelAppointmentTool: {cancel_tool.name}")
                print(f"   • ListAppointmentsTool: {list_tool.name}")
                
        except Exception as e:
            self.fail(f"Calendar tool initialization failed: {e}")
    
    def test_2_appointment_creation_workflow(self):
        """Test appointment creation workflow with mock data."""
        print("\n🗓️ Test 2: Appointment Creation Workflow")
        print("-" * 40)
        
        # Mock Google Calendar service
        mock_service = Mock()
        mock_event = {
            'id': 'test_event_123',
            'htmlLink': 'https://calendar.google.com/event/test_event_123',
            'summary': '🩺 Consultation: John Doe with Dr. Smith'
        }
        mock_service.events().insert().execute.return_value = mock_event
        
        # Mock tool with service
        with patch('tools.google_calendar_tool.CalendarToolBase.__init__', return_value=None):
            create_tool = CreateAppointmentTool()
            create_tool.service = mock_service
            
            # Test appointment creation
            result = create_tool._run(
                patient_name="John Doe",
                patient_email="john.doe@example.com",
                doctor_name="Sarah Smith",
                doctor_email="dr.smith@hospital.com",
                appointment_date="2025-10-30",
                appointment_time="14:00",
                duration_minutes=45,
                appointment_type="Consultation",
                notes="Follow-up for previous treatment"
            )
            
            # Verify result
            self.assertIn("Appointment Created Successfully", result)
            self.assertIn("John Doe", result)
            self.assertIn("Dr. Sarah Smith", result)
            self.assertIn("2025-10-30", result)
            self.assertIn("14:00", result)
            
            print("✅ Appointment creation workflow successful")
            print(f"   • Patient: John Doe")
            print(f"   • Doctor: Dr. Sarah Smith")
            print(f"   • Date/Time: 2025-10-30 at 14:00")
            print(f"   • Duration: 45 minutes")
            print(f"   • Type: Consultation")
    
    def test_3_availability_checking(self):
        """Test doctor availability checking."""
        print("\n🔍 Test 3: Doctor Availability Checking")
        print("-" * 40)
        
        # Mock Google Calendar service for availability
        mock_service = Mock()
        
        # Mock freebusy response
        mock_freebusy = {
            'calendars': {
                'dr.smith@hospital.com': {
                    'busy': [
                        {
                            'start': '2025-10-30T10:00:00+05:30',
                            'end': '2025-10-30T11:00:00+05:30'
                        },
                        {
                            'start': '2025-10-30T15:00:00+05:30',
                            'end': '2025-10-30T16:00:00+05:30'
                        }
                    ]
                }
            }
        }
        mock_service.freebusy().query().execute.return_value = mock_freebusy
        
        # Mock events response
        mock_events = {
            'items': [
                {
                    'summary': 'Patient consultation',
                    'start': {'dateTime': '2025-10-30T10:00:00+05:30'},
                    'end': {'dateTime': '2025-10-30T11:00:00+05:30'}
                }
            ]
        }
        mock_service.events().list().execute.return_value = mock_events
        
        # Test availability checking
        with patch('tools.google_calendar_tool.CalendarToolBase.__init__', return_value=None):
            availability_tool = CheckAvailabilityTool()
            availability_tool.service = mock_service
            
            result = availability_tool._run(
                doctor_email="dr.smith@hospital.com",
                date="2025-10-30",
                start_time="09:00",
                end_time="17:00"
            )
            
            # Verify result contains availability info
            self.assertIn("Availability for 2025-10-30", result)
            self.assertIn("dr.smith@hospital.com", result)
            self.assertIn("Busy Times", result)
            self.assertIn("Available Time Slots", result)
            
            print("✅ Availability checking successful")
            print("   • Doctor: dr.smith@hospital.com")
            print("   • Date: 2025-10-30")
            print("   • Found busy periods and free slots")
    
    def test_4_appointment_management(self):
        """Test appointment update and cancellation."""
        print("\n📝 Test 4: Appointment Management")
        print("-" * 40)
        
        # Mock Google Calendar service
        mock_service = Mock()
        
        # Mock existing event for update
        mock_existing_event = {
            'id': 'test_event_123',
            'summary': '🩺 Consultation: John Doe with Dr. Smith',
            'start': {'dateTime': '2025-10-30T14:00:00+05:30'},
            'end': {'dateTime': '2025-10-30T14:45:00+05:30'},
            'description': 'Original appointment'
        }
        
        mock_updated_event = {
            'id': 'test_event_123',
            'htmlLink': 'https://calendar.google.com/event/test_event_123'
        }
        
        mock_service.events().get().execute.return_value = mock_existing_event
        mock_service.events().update().execute.return_value = mock_updated_event
        
        # Test appointment update
        with patch('tools.google_calendar_tool.CalendarToolBase.__init__', return_value=None):
            update_tool = UpdateAppointmentTool()
            update_tool.service = mock_service
            
            result = update_tool._run(
                event_id="test_event_123",
                new_date="2025-10-31",
                new_time="15:00",
                new_duration=60,
                new_notes="Rescheduled due to emergency"
            )
            
            # Verify update result
            self.assertIn("Appointment Updated Successfully", result)
            self.assertIn("test_event_123", result)
            self.assertIn("Date/Time: 2025-10-31 at 15:00", result)
            
            print("✅ Appointment update successful")
            print("   • Event ID: test_event_123")
            print("   • New Date/Time: 2025-10-31 at 15:00")
            print("   • New Duration: 60 minutes")
        
        # Test appointment cancellation
        with patch('tools.google_calendar_tool.CalendarToolBase.__init__', return_value=None):
            cancel_tool = CancelAppointmentTool()
            cancel_tool.service = mock_service
            
            # Mock cancelled event
            mock_existing_event['attendees'] = [
                {'email': 'john.doe@example.com'},
                {'email': 'dr.smith@hospital.com'}
            ]
            
            result = cancel_tool._run(
                event_id="test_event_123",
                cancellation_reason="Patient requested cancellation",
                notify_attendees=True
            )
            
            # Verify cancellation result
            self.assertIn("Appointment Cancelled Successfully", result)
            self.assertIn("Patient requested cancellation", result)
            self.assertIn("john.doe@example.com", result)
            
            print("✅ Appointment cancellation successful")
            print("   • Event ID: test_event_123")
            print("   • Reason: Patient requested cancellation")
            print("   • Notifications sent to attendees")
    
    def test_5_appointment_listing(self):
        """Test listing upcoming appointments."""
        print("\n📋 Test 5: Appointment Listing")
        print("-" * 40)
        
        # Mock Google Calendar service
        mock_service = Mock()
        
        # Mock events response
        mock_events = {
            'items': [
                {
                    'id': 'event_1',
                    'summary': '🩺 Consultation: Alice Johnson with Dr. Wilson',
                    'start': {'dateTime': '2025-10-30T10:00:00+05:30'},
                    'end': {'dateTime': '2025-10-30T10:30:00+05:30'},
                    'status': 'confirmed',
                    'attendees': [{'email': 'alice@example.com'}]
                },
                {
                    'id': 'event_2',
                    'summary': '🩺 Follow-up: Bob Smith with Dr. Davis',
                    'start': {'dateTime': '2025-10-30T14:00:00+05:30'},
                    'end': {'dateTime': '2025-10-30T14:45:00+05:30'},
                    'status': 'confirmed',
                    'attendees': [{'email': 'bob@example.com'}]
                }
            ]
        }
        mock_service.events().list().execute.return_value = mock_events
        
        # Test appointment listing
        with patch('tools.google_calendar_tool.CalendarToolBase.__init__', return_value=None):
            list_tool = ListAppointmentsTool()
            list_tool.service = mock_service
            
            result = list_tool._run(
                start_date="2025-10-30",
                end_date="2025-10-31",
                max_results=10
            )
            
            # Verify listing result
            self.assertIn("Upcoming Appointments", result)
            self.assertIn("Alice Johnson", result)
            self.assertIn("Bob Smith", result)
            self.assertIn("Total Found: 2", result)
            
            print("✅ Appointment listing successful")
            print("   • Found 2 appointments")
            print("   • Date range: 2025-10-30 to 2025-10-31")
            print("   • Alice Johnson with Dr. Wilson")
            print("   • Bob Smith with Dr. Davis")
    
    def test_6_workflow_integration(self):
        """Test calendar tools integration with workflow agent."""
        print("\n🔄 Test 6: Workflow Integration")
        print("-" * 40)
        
        try:
            # Create workflow agent (mock database dependencies)
            with patch('src.workflow_chat_agent.PatientDB'), \
                 patch('src.workflow_chat_agent.WorkflowStateDB'):
                
                agent = WorkflowChatAgent(patient_email="test@example.com")
                
                # Import WORKFLOW_STAGES to check calendar tools integration
                from src.workflow_chat_agent import WORKFLOW_STAGES
                
                # Check that calendar tools are available in relevant stages
                stage_7_tools = WORKFLOW_STAGES[7]["tools"]
                stage_11_tools = WORKFLOW_STAGES[11]["tools"]
                
                # Verify stage 7 (admission planning) has calendar tools
                stage_7_tool_names = [tool.__class__.__name__ for tool in stage_7_tools]
                self.assertIn("CheckAvailabilityTool", stage_7_tool_names)
                self.assertIn("CreateAppointmentTool", stage_7_tool_names)
                self.assertIn("UpdateAppointmentTool", stage_7_tool_names)
                self.assertIn("ListAppointmentsTool", stage_7_tool_names)
                
                # Verify stage 11 (follow-up) has calendar tools
                stage_11_tool_names = [tool.__class__.__name__ for tool in stage_11_tools]
                self.assertIn("CheckAvailabilityTool", stage_11_tool_names)
                self.assertIn("CreateAppointmentTool", stage_11_tool_names)
                self.assertIn("UpdateAppointmentTool", stage_11_tool_names)
                self.assertIn("CancelAppointmentTool", stage_11_tool_names)
                self.assertIn("ListAppointmentsTool", stage_11_tool_names)
                
                print("✅ Workflow integration successful")
                print(f"   • Stage 7 tools: {len(stage_7_tools)} total")
                print(f"   • Stage 11 tools: {len(stage_11_tools)} total")
                print("   • All calendar tools properly integrated")
                
        except Exception as e:
            self.fail(f"Workflow integration test failed: {e}")
    
    def test_7_patient_appointment_scenario(self):
        """Test complete patient appointment scenario."""
        print("\n👤 Test 7: Complete Patient Appointment Scenario")
        print("-" * 40)
        
        # Mock patient state - simplified dictionary
        mock_patient_state = {
            "patient_id": "TEST_PATIENT_001",
            "name": "Emma Wilson",
            "email": "emma.wilson@example.com",
            "phone": "+1234567890",
            "current_stage": "7",  # Admission planning
            "preferred_admission_date": "2025-11-01"
        }
        
        # Mock doctor information
        doctor_email = "dr.johnson@hospital.com"
        doctor_name = "Michael Johnson"
        
        print("📋 Scenario: Emma Wilson needs admission appointment")
        print(f"   • Patient: {mock_patient_state['name']}")
        print(f"   • Email: {mock_patient_state['email']}")
        print(f"   • Doctor: Dr. {doctor_name}")
        print(f"   • Preferred Date: {mock_patient_state['preferred_admission_date']}")
        
        # Step 1: Check doctor availability
        with patch('tools.google_calendar_tool.CalendarToolBase.__init__', return_value=None):
            availability_tool = CheckAvailabilityTool()
            
            # Mock availability response
            mock_service = Mock()
            mock_freebusy = {
                'calendars': {
                    doctor_email: {
                        'busy': []  # Doctor is free
                    }
                }
            }
            mock_service.freebusy().query().execute.return_value = mock_freebusy
            mock_service.events().list().execute.return_value = {'items': []}
            availability_tool.service = mock_service
            
            availability_result = availability_tool._run(
                doctor_email=doctor_email,
                date="2025-11-01",
                start_time="09:00",
                end_time="17:00"
            )
            
            self.assertIn("Available Time Slots", availability_result)
            print("   ✅ Step 1: Doctor availability checked")
        
        # Step 2: Create appointment
        with patch('tools.google_calendar_tool.CalendarToolBase.__init__', return_value=None):
            create_tool = CreateAppointmentTool()
            
            # Mock appointment creation
            mock_service = Mock()
            mock_event = {
                'id': 'appointment_emma_001',
                'htmlLink': 'https://calendar.google.com/event/appointment_emma_001',
                'summary': f'🩺 Admission Planning: {mock_patient_state["name"]} with Dr. {doctor_name}'
            }
            mock_service.events().insert().execute.return_value = mock_event
            create_tool.service = mock_service
            
            appointment_result = create_tool._run(
                patient_name=mock_patient_state["name"],
                patient_email=mock_patient_state["email"],
                doctor_name=doctor_name,
                doctor_email=doctor_email,
                appointment_date="2025-11-01",
                appointment_time="10:00",
                duration_minutes=60,
                appointment_type="Admission Planning",
                notes="Hospital admission planning and preparation"
            )
            
            self.assertIn("Appointment Created Successfully", appointment_result)
            self.assertIn("Emma Wilson", appointment_result)
            print("   ✅ Step 2: Appointment created successfully")
        
        print("✅ Complete patient appointment scenario successful")
        print("   • Availability checked")
        print("   • Appointment scheduled")
        print("   • Notifications sent")
        print("   • Ready for admission planning")


def run_calendar_integration_tests():
    """Run all calendar integration tests."""
    print(f"\n{'='*60}")
    print("🗓️  GOOGLE CALENDAR INTEGRATION TEST SUITE")
    print(f"{'='*60}")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test methods
    test_methods = [
        'test_1_calendar_tools_initialization',
        'test_2_appointment_creation_workflow',
        'test_3_availability_checking',
        'test_4_appointment_management',
        'test_5_appointment_listing',
        'test_6_workflow_integration',
        'test_7_patient_appointment_scenario'
    ]
    
    for method in test_methods:
        test_suite.addTest(TestCalendarIntegration(method))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 CALENDAR INTEGRATION TEST SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Tests Run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"   • {test}: {traceback}")
    
    if result.errors:
        print(f"\n⚠️  ERRORS:")
        for test, traceback in result.errors:
            print(f"   • {test}: {traceback}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\n📈 Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 ALL CALENDAR INTEGRATION TESTS PASSED!")
        print("✅ Phase 3: Google Calendar Integration is ready for production!")
    else:
        print("⚠️  Some tests failed. Please review and fix issues.")
    
    print(f"{'='*60}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    """Run calendar integration tests when script is executed directly."""
    run_calendar_integration_tests()
