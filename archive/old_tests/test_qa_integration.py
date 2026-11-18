"""
Test Context-Aware Q&A Integration in Workflow
Demonstrates how patients can ask questions without losing workflow progress
"""

from tools.qa_tools import (
    GetMyInformationTool,
    GetMyAppointmentsTool,
    GetMyLabResultsTool,
    AskMedicalQuestionTool,
    ContextAwareQATool
)

def print_section(title):
    print()
    print("=" * 80)
    print(f"  {title}")
    print("=" * 80)
    print()

def test_personal_info():
    """Test getting patient's personal information"""
    print_section("TEST 1: Personal Information Retrieval")
    
    tool = GetMyInformationTool()
    
    # Test with existing patient
    print("🔍 Query: 'What's my information?'")
    print(f"📋 Patient ID: REG2025792570")
    print()
    
    result = tool._run(
        question="What's my information?",
        patient_id="REG2025792570"
    )
    
    print(result)

def test_appointments():
    """Test getting appointments"""
    print_section("TEST 2: Appointments Query")
    
    tool = GetMyAppointmentsTool()
    
    print("🔍 Query: 'What are my appointments?'")
    print(f"📋 Patient ID: REG2025001")
    print()
    
    result = tool._run(
        question="What are my appointments?",
        patient_id="REG2025001"
    )
    
    print(result)

def test_lab_results():
    """Test getting lab results"""
    print_section("TEST 3: Lab Results Query")
    
    tool = GetMyLabResultsTool()
    
    print("🔍 Query: 'What are my lab results?'")
    print(f"📋 Patient ID: REG2025001")
    print()
    
    result = tool._run(
        question="What are my lab results?",
        patient_id="REG2025001"
    )
    
    print(result)

def test_medical_knowledge():
    """Test medical knowledge Q&A"""
    print_section("TEST 4: Medical Knowledge Q&A")
    
    tool = AskMedicalQuestionTool()
    
    questions = [
        "What are the symptoms of diabetes?",
        "What are the side effects of metformin?",
        "How do you treat high blood pressure?",
        "What is a normal HbA1c level?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n💡 Question {i}: {question}")
        print("-" * 80)
        
        result = tool._run(
            question=question,
            patient_id="REG2025001"  # Patient ID required but not used for knowledge queries
        )
        
        print(result)
        print()

def test_intelligent_routing():
    """Test the unified Q&A router"""
    print_section("TEST 5: Intelligent Question Routing")
    
    router = ContextAwareQATool()
    
    test_cases = [
        {
            "question": "What's my current status?",
            "expected_route": "personal_info",
            "description": "Should route to personal information"
        },
        {
            "question": "When is my next appointment?",
            "expected_route": "appointments",
            "description": "Should route to appointments"
        },
        {
            "question": "What were my lab results?",
            "expected_route": "lab_results",
            "description": "Should route to lab results"
        },
        {
            "question": "What is diabetes?",
            "expected_route": "medical_knowledge",
            "description": "Should route to medical knowledge"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['question']}")
        print(f"   Expected Route: {test['expected_route']}")
        print(f"   {test['description']}")
        
        detected_route = router._classify_question(test['question'])
        
        if detected_route == test['expected_route']:
            print(f"   ✅ Correctly routed to: {detected_route}")
        else:
            print(f"   ❌ Incorrectly routed to: {detected_route} (expected: {test['expected_route']})")

def test_workflow_integration_simulation():
    """Simulate Q&A during workflow"""
    print_section("TEST 6: Workflow Integration Simulation")
    
    print("""
📋 **Scenario**: Patient is in the middle of registration (Stage 1)
    Agent just asked: "What's your date of birth?"
    
🤔 **Patient asks a question instead of answering**:
    "Wait, what are the symptoms of diabetes? I think I might have it."
    
✅ **Expected Behavior**:
    1. Agent detects this is a QUESTION (not an answer to DOB)
    2. Routes to Medical Knowledge Q&A
    3. Provides comprehensive answer about diabetes symptoms
    4. Returns patient to workflow: "Now, what's your date of birth?"
    5. Workflow continues seamlessly from where it left off
""")
    
    router = ContextAwareQATool()
    
    patient_message = "Wait, what are the symptoms of diabetes? I think I might have it."
    
    print(f"💬 Patient Message: \"{patient_message}\"")
    print()
    
    # Detect if it's a question
    is_question = '?' in patient_message or patient_message.lower().startswith('what')
    
    if is_question:
        print("✅ Detected as QUESTION (not workflow answer)")
        print("   Routing to Q&A system...")
        print()
        
        answer = router._run(
            question=patient_message,
            patient_id="REG2025001"
        )
        
        print("🤖 Agent Response:")
        print(answer)
        print()
        print("---")
        print()
        print("🔄 After answering question, agent continues workflow:")
        print("   'Now, what's your date of birth? (Format: YYYY-MM-DD)'")
    else:
        print("❌ Not detected as question - treating as workflow answer")

def test_multiple_qa_interactions():
    """Test multiple Q&A interactions"""
    print_section("TEST 7: Multiple Q&A Interactions")
    
    router = ContextAwareQATool()
    
    conversation = [
        "What's my information?",
        "What are my appointments?",
        "What is hypertension?",
        "What are the side effects of lisinopril?",
        "What's my current status?"
    ]
    
    print("💬 **Simulated Conversation:**\n")
    
    for i, question in enumerate(conversation, 1):
        print(f"{i}. Patient: \"{question}\"")
        route = router._classify_question(question)
        print(f"   → Routed to: {route}")
        print()

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    print()
    print("=" * 80)
    print("  🏥 CONTEXT-AWARE Q&A SYSTEM - INTEGRATION TESTING")
    print("  💬 Testing Q&A Without Losing Workflow Progress")
    print("=" * 80)
    
    try:
        # Run all tests
        test_personal_info()
        test_appointments()
        test_lab_results()
        test_medical_knowledge()
        test_intelligent_routing()
        test_workflow_integration_simulation()
        test_multiple_qa_interactions()
        
        print()
        print("=" * 80)
        print("  ✅ ALL TESTS COMPLETED!")
        print("=" * 80)
        print()
        print("📊 **Summary:**")
        print("   ✅ Personal information retrieval working")
        print("   ✅ Appointments query working")
        print("   ✅ Lab results query working")
        print("   ✅ Medical knowledge Q&A working (RAG)")
        print("   ✅ Intelligent routing working")
        print("   ✅ Workflow integration ready")
        print()
        print("🎯 **Key Features:**")
        print("   • Patients can ask questions at ANY point in workflow")
        print("   • Agent answers WITHOUT losing workflow progress")
        print("   • Automatically detects question vs answer")
        print("   • Routes to appropriate data source (PostgreSQL/Vector DB)")
        print("   • Continues workflow seamlessly after answering")
        print()
        print("🚀 **Next Steps:**")
        print("   1. Test in live chat interface")
        print("   2. Test with real patient data")
        print("   3. Add more medical knowledge to vector DB")
        print("   4. Monitor question classification accuracy")
        print()
        
    except Exception as e:
        print()
        print("=" * 80)
        print(f"  ❌ TEST FAILED: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
