"""
Read Doctor Decisions from Review Sheet Tool
Parses doctor's decisions from Google Sheets:
- Lab tests approval (with modifications)
- Decision type (approve_tests, schedule_appointment, admit_patient, prescription_only)
- Prescription details
- Follow-up instructions
- Safety measures
"""

import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from langchain.tools import BaseTool

from tools.google_sheets_tool import ReadSheetDataTool


class ReadDoctorDecisionInput(BaseModel):
    spreadsheet_url: str = Field(description="Doctor review sheet URL")
    patient_id: Optional[str] = Field(default=None, description="Patient ID")


class ReadDoctorDecisionTool(BaseTool):
    name: str = "read_doctor_decision"
    description: str = "Read doctor's decisions from review sheet: approved tests, decision type, prescriptions, follow-up dates, safety measures"
    args_schema: type[BaseModel] = ReadDoctorDecisionInput

    def _extract_spreadsheet_id(self, url: str) -> Optional[str]:
        match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url)
        if match:
            return match.group(1)
        return None

    def _parse_tests_from_rows(self, rows: List[List[str]], start_row: int, end_row: int) -> List[Dict[str, str]]:
        """Parse lab tests from specific row range"""
        tests = []
        for i in range(start_row, end_row):
            if i < len(rows):
                row = rows[i]
                if len(row) >= 3:
                    # Format: Test Name | Priority | Reason
                    test_name = str(row[0]).strip() if row[0] else ""
                    priority = str(row[1]).strip() if len(row) > 1 and row[1] else ""
                    reason = str(row[2]).strip() if len(row) > 2 and row[2] else ""
                    
                    # Skip if test name starts with number (header row like "1.")
                    if test_name and not test_name.startswith(('1.', '2.', '3.', '4.', '5.', 'Test Name')):
                        # Remove leading numbers like "1. ECG" -> "ECG"
                        test_name = re.sub(r'^\d+\.\s*', '', test_name)
                        if test_name and test_name.lower() not in ['', 'n/a', 'none', '-']:
                            tests.append({
                                'test_name': test_name,
                                'priority': priority or 'Medium',
                                'reason': reason
                            })
        return tests

    def _parse_prescriptions(self, rows: List[List[str]], start_row: int, end_row: int) -> List[Dict[str, str]]:
        """Parse prescriptions from specific row range"""
        prescriptions = []
        for i in range(start_row, end_row):
            if i < len(rows):
                row = rows[i]
                if len(row) >= 2:
                    medication = str(row[0]).strip() if row[0] else ""
                    dosage = str(row[1]).strip() if len(row) > 1 and row[1] else ""
                    
                    # Remove leading numbers
                    medication = re.sub(r'^\d+\.\s*', '', medication)
                    if medication and medication.lower() not in ['', 'n/a', 'none', '-', 'medication/intervention']:
                        prescriptions.append({
                            'medication': medication,
                            'dosage': dosage
                        })
        return prescriptions

    def _detect_decision_type(self, rows: List[List[str]]) -> str:
        """Detect doctor's decision from sheet content"""
        # Search for decision keywords in entire sheet
        sheet_text = ' '.join([' '.join([str(cell).lower() for cell in row]) for row in rows])
        
        # Check for explicit decisions
        if 'admit' in sheet_text or 'admission' in sheet_text or 'hospitalize' in sheet_text:
            return 'admit_patient'
        elif 'operation' in sheet_text or 'surgery' in sheet_text:
            return 'admit_patient'
        elif 'no tests' in sheet_text or 'skip tests' in sheet_text or 'direct appointment' in sheet_text:
            return 'schedule_appointment'
        elif 'prescription only' in sheet_text or 'medication only' in sheet_text:
            return 'prescription_only'
        else:
            return 'approve_tests'  # Default

    def _extract_follow_up_info(self, rows: List[List[str]]) -> Dict[str, Any]:
        """Extract follow-up dates and safety measures from sheet"""
        follow_up_info = {
            'follow_up_date': None,
            'follow_up_weeks': None,
            'safety_measures': []
        }
        
        # Search for follow-up mentions
        for row in rows:
            row_text = ' '.join([str(cell).lower() for cell in row])
            
            # Look for follow-up dates
            if 'follow' in row_text or 'next visit' in row_text:
                # Try to extract number of weeks
                weeks_match = re.search(r'(\d+)\s*(week|wk)', row_text)
                if weeks_match:
                    follow_up_info['follow_up_weeks'] = int(weeks_match.group(1))
                
                # Try to extract specific date
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', row_text)
                if date_match:
                    follow_up_info['follow_up_date'] = date_match.group(1)
            
            # Look for safety measures
            if any(keyword in row_text for keyword in ['precaution', 'safety', 'warning', 'avoid', 'monitor']):
                if len(row) > 1:
                    measure = ' '.join([str(cell) for cell in row if cell])
                    if measure and len(measure) > 10:  # Meaningful content
                        follow_up_info['safety_measures'].append(measure)
        
        return follow_up_info

    def _run(self, spreadsheet_url: str, patient_id: Optional[str] = None) -> Dict[str, Any]:
        try:
            # Extract spreadsheet ID
            sheet_id = self._extract_spreadsheet_id(spreadsheet_url)
            if not sheet_id:
                return {'success': False, 'error': 'Invalid spreadsheet URL'}

            # Read entire sheet data
            read_tool = ReadSheetDataTool()
            sheet_data = read_tool._run(
                spreadsheet_id=sheet_id,
                range_name='A1:E60'  # Read all relevant rows
            )

            if 'Error' in sheet_data or 'No data found' in sheet_data:
                return {'success': False, 'error': 'Could not read sheet data'}

            # Parse sheet data into rows
            lines = sheet_data.strip().split('\n')
            rows = []
            for line in lines:
                # Simple CSV-like parsing (assuming pipe or tab separated)
                if '|' in line:
                    row = [cell.strip() for cell in line.split('|')]
                else:
                    row = [cell.strip() for cell in line.split('\t')]
                rows.append(row)

            # Parse lab tests (rows 27-32 approximately, but search for section)
            approved_tests = []
            test_section_start = None
            for i, row in enumerate(rows):
                row_text = ' '.join([str(cell).lower() for cell in row])
                if 'recommended lab tests' in row_text or 'test name' in row_text:
                    test_section_start = i + 1
                    break
            
            if test_section_start:
                approved_tests = self._parse_tests_from_rows(rows, test_section_start, test_section_start + 10)

            # Parse prescriptions (treatment suggestions section)
            prescriptions = []
            prescription_section_start = None
            for i, row in enumerate(rows):
                row_text = ' '.join([str(cell).lower() for cell in row])
                if 'treatment suggestions' in row_text or 'medication' in row_text:
                    prescription_section_start = i + 1
                    break
            
            if prescription_section_start:
                prescriptions = self._parse_prescriptions(rows, prescription_section_start, prescription_section_start + 5)

            # Detect decision type
            decision_type = self._detect_decision_type(rows)

            # Extract follow-up info
            follow_up_info = self._extract_follow_up_info(rows)

            # Extract doctor's assessment (if available)
            assessment = ""
            assessment_section = None
            for i, row in enumerate(rows):
                row_text = ' '.join([str(cell).lower() for cell in row])
                if "doctor's assessment" in row_text or 'initial assessment' in row_text:
                    assessment_section = i + 1
                    break
            
            if assessment_section and assessment_section < len(rows):
                # Get next few rows as assessment
                assessment_lines = []
                for i in range(assessment_section, min(assessment_section + 5, len(rows))):
                    if rows[i] and len(rows[i]) > 1:
                        assessment_lines.append(' '.join([str(cell) for cell in rows[i] if cell]))
                assessment = ' '.join(assessment_lines)

            result = {
                'success': True,
                'patient_id': patient_id,
                'decision_type': decision_type,
                'approved_tests': approved_tests,
                'prescriptions': prescriptions,
                'follow_up_date': follow_up_info['follow_up_date'],
                'follow_up_weeks': follow_up_info['follow_up_weeks'],
                'safety_measures': follow_up_info['safety_measures'],
                'doctor_assessment': assessment.strip() if assessment else None,
                'tests_count': len(approved_tests),
                'prescriptions_count': len(prescriptions)
            }

            return result

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError('Async not supported')
