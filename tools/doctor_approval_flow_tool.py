"""
Doctor Approval Flow Tool
- Shares the doctor review sheet with identified doctor (by email or specialty)
- Creates an approval request for ordering lab tests
- Returns approval result and recommended action
"""

import os
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain.tools import BaseTool

from tools.google_sheets_tool import ShareSheetTool
from tools.approval_tool import CreateApprovalRequestTool

# Simple speciality -> doctor email mapping (can be extended or loaded from staff directory)
SPECIALTY_EMAIL_MAP = {
    'Cardiologist': os.getenv('CARDIOLOGIST_EMAIL', os.getenv('DOCTOR_EMAIL', 'cardio@cityhospital.com')),
    'Endocrinologist': os.getenv('ENDOCRINOLOGIST_EMAIL', os.getenv('DOCTOR_EMAIL', 'endocrine@cityhospital.com')),
    'Gastroenterologist': os.getenv('GASTROENTEROLOGIST_EMAIL', os.getenv('DOCTOR_EMAIL', 'gastro@cityhospital.com')),
    'General Physician': os.getenv('GENERAL_DOC_EMAIL', os.getenv('DOCTOR_EMAIL', 'doctor@cityhospital.com'))
}


class DoctorApprovalInput(BaseModel):
    spreadsheet_url: str = Field(description="Doctor review sheet URL")
    suggested_tests: List[Dict[str, Any]] = Field(description="List of suggested tests (name, priority, reason)")
    doctor_specialty: Optional[str] = Field(default=None, description="Doctor specialty (e.g., Cardiologist)")
    doctor_email: Optional[str] = Field(default=None, description="Doctor email address (optional)")
    patient_id: Optional[str] = Field(default=None)
    patient_name: Optional[str] = Field(default=None)


class DoctorApprovalFlowTool(BaseTool):
    name: str = "doctor_approval_flow"
    description: str = "Share review sheet with doctor, create approval request for tests, return approval status and next action."
    args_schema: type[BaseModel] = DoctorApprovalInput

    def _extract_spreadsheet_id(self, url: str) -> Optional[str]:
        match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url)
        if match:
            return match.group(1)
        return None

    def _run(self, spreadsheet_url: str, suggested_tests: List[Dict[str, Any]], doctor_specialty: Optional[str] = None, doctor_email: Optional[str] = None, patient_id: Optional[str] = None, patient_name: Optional[str] = None) -> Dict[str, Any]:
        try:
            sheet_id = self._extract_spreadsheet_id(spreadsheet_url)
            if not sheet_id:
                return {'success': False, 'error': 'Invalid spreadsheet URL'}

            # Determine doctor email
            email = doctor_email
            if not email:
                if doctor_specialty and doctor_specialty in SPECIALTY_EMAIL_MAP:
                    email = SPECIALTY_EMAIL_MAP[doctor_specialty]
                else:
                    email = os.getenv('DOCTOR_EMAIL', 'doctor@cityhospital.com')

            # Share the sheet with doctor (writer permissions)
            share_tool = ShareSheetTool()
            try:
                share_res = share_tool._run(spreadsheet_id=sheet_id, email=email, role='writer')
            except Exception as e:
                share_res = f"Error sharing sheet: {str(e)}"

            # Create approval request to order lab tests
            tests_list = [t.get('tests') if isinstance(t.get('tests'), list) else [t.get('tests')] for t in suggested_tests]
            # Flatten tests
            flattened = []
            for item in tests_list:
                if isinstance(item, list):
                    flattened.extend(item)
                else:
                    flattened.append(item)

            # Clean up tests
            cleaned_tests = [str(x).strip() for x in flattened if x]

            approval_tool = CreateApprovalRequestTool()
            details = {
                'patient_id': patient_id,
                'patient_name': patient_name,
                'sheet_url': spreadsheet_url,
                'tests': cleaned_tests,
                'doctor_specialty': doctor_specialty,
                'shared_with': email
            }

            approval_res = approval_tool._run(
                action_type='order_lab_test',
                priority='high',
                requester='AI Agent',
                details=details,
                reason='Doctor review suggested these tests',
                affected_entities=[patient_id] if patient_id else None
            )

            # approval_tool in AUTO_APPROVE_MODE may auto-approve; return the approval details
            approved = False
            approval_id = None
            if approval_res.get('success'):
                approval = approval_res.get('approval') or approval_res.get('approval', None)
                if approval and approval.get('status') in ['approved']:
                    approved = True
                    approval_id = approval.get('approval_id')

            result = {
                'success': True,
                'shared_with': email,
                'share_response': share_res,
                'approved': approved,
                'approval_id': approval_id,
                'tests': cleaned_tests,
                'message': 'Shared with doctor and approval request created.'
            }

            return result

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError('Async not supported')
