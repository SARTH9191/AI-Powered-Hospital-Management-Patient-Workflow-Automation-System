"""
Simple Test - Force Stage 3 Document Creation
This manually triggers document creation for testing
"""

import sys
import codecs
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from tools.unified_workflow_doc_tool import create_workflow_doc
from src.workflow_chat_agent import WorkflowChatAgent


def main():
    print("="*80)
    print("  FORCE DOCUMENT CREATION TEST")
    print("="*80)
    print()
    
    # Get patient info
    test_email = "iamsamarth786@gmail.com"
    agent = WorkflowChatAgent(patient_email=test_email)
    
    print(f"Patient ID: {agent.patient_id}")
    print(f"Patient Email: {test_email}")
    print()
    
    # Check if document already exists
    existing_doc = agent.state.get('workflow_doc_id')
    if existing_doc:
        print(f"✅ Document already exists: {agent.state.get('workflow_doc_url')}")
        print(f"   Doc ID: {existing_doc}")
        return True
    
    # Get medical history data
    stage_data = agent.state.get('stage_data', {}).get('medical_history', {})
    registration_data = agent.state.get('stage_data', {}).get('registration', {})
    
    if not stage_data or not stage_data.get('chief_complaint'):
        print("❌ No medical history found. Please run Stage 3 first.")
        return False
    
    print("Found medical history data:")
    print(f"  • Chief Complaint: {stage_data.get('chief_complaint', 'Not set')}")
    print(f"  • Past Conditions: {stage_data.get('past_conditions', {}).get('professional_summary', 'None')}")
    print(f"  • Allergies: {stage_data.get('allergies', {}).get('professional_summary', 'None')}")
    print()
    
    # Prepare data for document
    patient_name = registration_data.get('full_name', agent.state.get('full_name', 'Unknown Patient'))
    
    medical_history_text = f"""
PATIENT INFORMATION:
• Name: {patient_name}
• Email: {test_email}
• Patient ID: {agent.patient_id}

PRESENTING COMPLAINT:
{stage_data.get('chief_complaint', 'Not specified')}

PAST MEDICAL HISTORY:
{stage_data.get('past_conditions', {}).get('professional_summary', 'None reported')}

ALLERGIES:
{stage_data.get('allergies', {}).get('professional_summary', 'None reported')}

CURRENT MEDICATIONS:
{stage_data.get('current_medications', {}).get('professional_summary', 'None reported')}
"""
    
    ai_analysis_text = """
CLINICAL ASSESSMENT:
Based on the patient's medical history and presenting complaint, a comprehensive evaluation is recommended.

Risk Factors:
• Cardiovascular risk factors present
• Metabolic concerns identified

RECOMMENDED DIAGNOSTIC TESTS:
1. Complete Blood Count (CBC)
2. Basic Metabolic Panel
3. Lipid Profile
4. ECG (Electrocardiogram)
5. HbA1c (Diabetes monitoring)

NEXT STEPS:
1. Doctor will review this assessment
2. Doctor will approve/modify the recommended tests
3. Approved tests will be scheduled
4. Results will be analyzed and shared
"""
    
    recommended_tests = [
        "Complete Blood Count (CBC)",
        "Basic Metabolic Panel",
        "Lipid Profile",
        "ECG (Electrocardiogram)",
        "HbA1c"
    ]
    
    print("Creating unified workflow document...")
    print()
    
    doc_result = create_workflow_doc(
        patient_id=agent.patient_id,
        patient_name=patient_name,
        patient_email=test_email,
        medical_history=medical_history_text,
        ai_analysis=ai_analysis_text,
        recommended_tests=recommended_tests
    )
    
    if doc_result.get('success'):
        # Save to agent state
        agent.state['workflow_doc_id'] = doc_result['doc_id']
        agent.state['workflow_doc_url'] = doc_result['doc_url']
        agent._save_state()
        
        print("✅ SUCCESS!")
        print()
        print(f"📄 Document ID: {doc_result['doc_id']}")
        print(f"📄 Document URL: {doc_result['doc_url']}")
        print(f"✅ Shared with: {doc_result['shared_with']}")
        print()
        print("="*80)
        print("  NEXT STEPS")
        print("="*80)
        print()
        print(f"1. Open: {doc_result['doc_url']}")
        print("2. Go to Section 3: DOCTOR'S DECISION")
        print("3. Update with:")
        print("   Doctor's Decision: APPROVE")
        print("   Approved Tests: Complete Blood Count (CBC), Lipid Profile, ECG")
        print("   Doctor's Assessment: Proceed with comprehensive testing")
        print("   Updated by: Dr. [Your Name]")
        print()
        print("4. Then test with: python test_fresh_unified_workflow.py")
        print()
        
        return True
    else:
        print(f"❌ Failed: {doc_result.get('error', 'Unknown error')}")
        return False


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
