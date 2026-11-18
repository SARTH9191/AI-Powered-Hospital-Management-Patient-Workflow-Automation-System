"""
Test Q&A System Enhancement - Doctor Notes Integration

This tests Phase 2 Priority 2: Patients can ask about doctor's notes anytime
during the workflow using natural language questions.

Test scenarios:
1. Patient has doctor notes → AI reads and answers
2. Patient has NO doctor notes → Friendly explanation
3. Various question phrasings → All detected correctly
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.qa_tools import ContextAwareQATool
from database.db_manager import WorkflowStateDB


def print_section(title: str, content: str = ""):
    """Print formatted section"""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    if content:
        print(content)


def test_doctor_notes_questions():
    """Test various doctor-related questions"""
    
    print_section("🧪 Q&A DOCTOR NOTES INTEGRATION TEST")
    print("Testing: Patients can ask about doctor's notes anytime")
    
    # Setup: Use the test patient from Stage 3 test
    test_patient_id = "REG2025STAGE3TEST"
    
    # Test questions
    test_questions = [
        "What did the doctor say?",
        "What's my diagnosis?",
        "What treatment did the doctor recommend?",
        "What medications did the doctor prescribe?",
        "Can you show me my doctor's notes?"
    ]
    
    qa_tool = ContextAwareQATool()
    
    passed_tests = 0
    total_tests = len(test_questions)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'─'*70}")
        print(f"📝 TEST {i}/{total_tests}: \"{question}\"")
        print(f"{'─'*70}")
        
        try:
            # Classify question
            question_type = qa_tool._classify_question(question)
            print(f"✅ Classified as: {question_type}")
            
            if question_type != "doctor_notes":
                print(f"❌ FAILED: Expected 'doctor_notes', got '{question_type}'")
                continue
            
            # Get answer
            answer = qa_tool._run(question=question, patient_id=test_patient_id)
            
            print(f"\n🤖 AI Response:")
            print(f"{answer[:400]}...")  # Show first 400 chars
            
            # Check if answer contains expected elements
            has_doctor_content = any(keyword in answer.lower() for keyword in [
                'doctor', 'diagnosis', 'treatment', 'pending', 'notes', 'consultation'
            ])
            
            if has_doctor_content:
                print(f"\n✅ TEST PASSED: Answer contains doctor-related content")
                passed_tests += 1
            else:
                print(f"\n❌ TEST FAILED: Answer missing doctor-related content")
        
        except Exception as e:
            print(f"\n❌ TEST EXCEPTION: {e}")
    
    return passed_tests, total_tests


def test_no_doctor_notes():
    """Test patient without doctor notes"""
    
    print_section("🧪 TEST: PATIENT WITHOUT DOCTOR NOTES")
    
    # Use a patient ID that doesn't have doctor notes
    test_patient_id = "NONEXISTENT123"
    
    qa_tool = ContextAwareQATool()
    
    try:
        answer = qa_tool._run(
            question="What's my diagnosis?",
            patient_id=test_patient_id
        )
        
        print(f"🤖 AI Response:")
        print(answer)
        
        # Check for friendly "not available" message
        has_friendly_message = any(keyword in answer.lower() for keyword in [
            'not available', 'hasn\'t completed', 'pending', 'continue', 'schedule'
        ])
        
        if has_friendly_message:
            print(f"\n✅ TEST PASSED: Friendly 'not available' message shown")
            return True
        else:
            print(f"\n❌ TEST FAILED: Expected friendly message about unavailable notes")
            return False
    
    except Exception as e:
        print(f"\n❌ TEST EXCEPTION: {e}")
        return False


def test_classification_accuracy():
    """Test that doctor questions are classified correctly"""
    
    print_section("🧪 TEST: QUESTION CLASSIFICATION ACCURACY")
    
    qa_tool = ContextAwareQATool()
    
    test_cases = [
        ("What did the doctor say?", "doctor_notes"),
        ("What's my diagnosis?", "doctor_notes"),
        ("What treatment plan?", "doctor_notes"),
        ("Show me doctor's notes", "doctor_notes"),
        ("What's my email?", "personal_info"),
        ("When is my appointment?", "appointments"),
        ("What are my lab results?", "lab_results"),
        ("What causes diabetes?", "medical_knowledge"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for question, expected_type in test_cases:
        classified_as = qa_tool._classify_question(question)
        
        if classified_as == expected_type:
            print(f"✅ \"{question[:40]}...\" → {classified_as}")
            passed += 1
        else:
            print(f"❌ \"{question[:40]}...\" → Expected: {expected_type}, Got: {classified_as}")
    
    print(f"\n📊 Classification Accuracy: {passed}/{total} ({(passed/total)*100:.1f}%)")
    
    return passed == total


def main():
    """Run all tests"""
    
    print_section("🏥 PHASE 2 - PRIORITY 2 TEST")
    print("Testing: Q&A System Enhancement - Doctor Notes Integration")
    
    all_passed = True
    
    # Test 1: Doctor notes questions
    print_section("TEST SUITE 1: DOCTOR NOTES QUESTIONS")
    passed, total = test_doctor_notes_questions()
    test1_passed = (passed == total)
    all_passed = all_passed and test1_passed
    print(f"\n📊 Result: {passed}/{total} questions answered correctly")
    
    # Test 2: No doctor notes scenario
    print_section("TEST SUITE 2: GRACEFUL HANDLING")
    test2_passed = test_no_doctor_notes()
    all_passed = all_passed and test2_passed
    
    # Test 3: Classification accuracy
    print_section("TEST SUITE 3: CLASSIFICATION")
    test3_passed = test_classification_accuracy()
    all_passed = all_passed and test3_passed
    
    # Summary
    print_section("📊 TEST SUMMARY")
    
    print(f"✅ SUITE 1: Doctor Notes Questions - {'PASSED' if test1_passed else 'FAILED'}")
    print(f"✅ SUITE 2: Graceful Handling - {'PASSED' if test2_passed else 'FAILED'}")
    print(f"✅ SUITE 3: Classification - {'PASSED' if test3_passed else 'FAILED'}")
    
    if all_passed:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"\n✨ Phase 2 - Priority 2 COMPLETE!")
        print(f"\n📋 What this enables:")
        print(f"   1. ✅ Patients can ask 'What did the doctor say?' anytime")
        print(f"   2. ✅ AI reads doctor's notes from Google Doc")
        print(f"   3. ✅ LLM generates patient-friendly explanations")
        print(f"   4. ✅ Graceful handling when notes not available")
        print(f"   5. ✅ Questions classified correctly (8/8 types)")
        print(f"\n🎯 Phase 2 Integration Status:")
        print(f"   ✅ PRIORITY 1: Stage 3 auto-creates doctor notes doc")
        print(f"   ✅ PRIORITY 2: Q&A system reads doctor notes")
        print(f"   ⏳ PRIORITY 3: Stage 6 diagnosis integration (NEXT)")
    else:
        print(f"\n⚠️  Some tests failed. Review errors above.")
    
    print_section("🏁 TEST COMPLETE")


if __name__ == "__main__":
    main()
