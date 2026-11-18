"""
Lab Results Reader Tool - Reads lab results from Google Sheets
Staff fills the sheet, AI reads it!

This tool reads lab results that staff members have entered into
the Lab Results Master Sheet. No database needed - direct from sheets!
"""

import os
from typing import Dict, Any, List, Optional
from langchain.tools import BaseTool
from dotenv import load_dotenv
import pickle
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from datetime import datetime

load_dotenv()

class SheetsReaderBase:
    """Base class for reading from Google Sheets"""
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    def _get_credentials(self):
        """Get Google credentials"""
        creds = None
        token_path = 'credentials/token.pickle'
        
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
            else:
                # If token is completely invalid, need to re-authenticate
                from google_auth_oauthlib.flow import InstalledAppFlow
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials/client_secret.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
        
        return creds
    
    def _get_sheets_service(self):
        """Get Google Sheets service"""
        creds = self._get_credentials()
        return build('sheets', 'v4', credentials=creds)


class ReadLabResultsFromSheetTool(BaseTool, SheetsReaderBase):
    """
    Reads lab results from Google Sheets for a specific patient.
    
    Staff workflow:
    1. Lab technician opens Lab Results Sheet
    2. Finds patient row by Patient ID
    3. Fills in: Test Name, Result, Unit, Normal Range, Status
    4. AI reads this data when patient asks!
    
    This tool:
    - Reads from LAB_RESULTS_SHEET_ID
    - Filters by patient_id
    - Returns all test results with status
    - Includes technician notes
    """
    
    name: str = "read_lab_results_from_sheet"
    description: str = """
    Reads lab test results from Google Sheets for a specific patient.
    Lab technicians fill this sheet with test results.
    
    Use this when:
    - Patient asks: "Are my lab results ready?"
    - Patient asks: "What are my test results?"
    - Patient asks: "Is my CBC report complete?"
    - You need to check lab test status
    
    Input: patient_id (e.g., 'REG2025001')
    Output: List of all lab tests with results, status, and notes
    """
    
    def _run(self, patient_id: str) -> Dict[str, Any]:
        """
        Read lab results for a patient from Google Sheet
        
        Args:
            patient_id: Patient registration ID (e.g., REG2025001)
        
        Returns:
            Dictionary with results list and summary
        """
        try:
            # Get sheet ID from environment
            sheet_id = os.getenv('LAB_RESULTS_SHEET_ID')
            if not sheet_id:
                return {
                    "success": False,
                    "error": "LAB_RESULTS_SHEET_ID not configured",
                    "message": "Please set up the Lab Results Sheet first"
                }
            
            # Get sheets service
            service = self._get_sheets_service()
            
            # Read all data from sheet
            range_name = 'Lab Results!A2:L1000'  # Skip header row
            result = service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            rows = result.get('values', [])
            
            if not rows:
                return {
                    "success": True,
                    "patient_id": patient_id,
                    "results": [],
                    "total_tests": 0,
                    "message": "No lab results found in the sheet"
                }
            
            # Filter rows for this patient
            patient_results = []
            for row in rows:
                # Ensure row has enough columns
                if len(row) < 7:
                    continue
                
                # Check if this row is for our patient
                if row[0] == patient_id:
                    # Parse the row
                    result_data = {
                        "patient_id": row[0],
                        "patient_name": row[1] if len(row) > 1 else "",
                        "test_name": row[2] if len(row) > 2 else "",
                        "result": row[3] if len(row) > 3 else "",
                        "unit": row[4] if len(row) > 4 else "",
                        "normal_range": row[5] if len(row) > 5 else "",
                        "status": row[6] if len(row) > 6 else "Pending",
                        "test_date": row[7] if len(row) > 7 else "",
                        "ordered_date": row[8] if len(row) > 8 else "",
                        "technician": row[9] if len(row) > 9 else "",
                        "notes": row[10] if len(row) > 10 else "",
                        "last_updated": row[11] if len(row) > 11 else ""
                    }
                    patient_results.append(result_data)
            
            if not patient_results:
                return {
                    "success": True,
                    "patient_id": patient_id,
                    "results": [],
                    "total_tests": 0,
                    "message": f"No lab results found for patient {patient_id}"
                }
            
            # Calculate statistics
            completed_tests = [r for r in patient_results if r['status'] == 'Complete']
            pending_tests = [r for r in patient_results if r['status'] == 'Pending']
            review_tests = [r for r in patient_results if r['status'] == 'Review Required']
            
            return {
                "success": True,
                "patient_id": patient_id,
                "patient_name": patient_results[0]['patient_name'],
                "results": patient_results,
                "total_tests": len(patient_results),
                "completed_count": len(completed_tests),
                "pending_count": len(pending_tests),
                "review_count": len(review_tests),
                "completed_tests": completed_tests,
                "pending_tests": pending_tests,
                "review_tests": review_tests,
                "message": f"Found {len(patient_results)} lab test(s) for {patient_id}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "patient_id": patient_id,
                "error": str(e),
                "message": f"Error reading lab results: {str(e)}"
            }
    
    async def _arun(self, patient_id: str) -> Dict[str, Any]:
        """Async version"""
        return self._run(patient_id)


class CheckLabResultStatusTool(BaseTool, SheetsReaderBase):
    """
    Quick check if lab results are ready for a patient.
    Returns simple yes/no with counts.
    """
    
    name: str = "check_lab_result_status"
    description: str = """
    Quickly check if lab results are ready for a patient.
    Returns simple status without full details.
    
    Use this when:
    - Patient asks: "Are my results ready?"
    - You need quick status check
    - Before reading full results
    
    Input: patient_id
    Output: Status summary (ready/pending counts)
    """
    
    def _run(self, patient_id: str) -> Dict[str, Any]:
        """Quick status check"""
        try:
            # Use the main tool to get data
            reader = ReadLabResultsFromSheetTool()
            full_results = reader._run(patient_id)
            
            if not full_results['success']:
                return full_results
            
            total = full_results.get('total_tests', 0)
            completed = full_results.get('completed_count', 0)
            pending = full_results.get('pending_count', 0)
            
            if total == 0:
                status = "no_tests"
                message = "No lab tests found"
            elif completed == total:
                status = "all_ready"
                message = f"All {completed} test(s) are ready!"
            elif completed > 0:
                status = "partially_ready"
                message = f"{completed} of {total} test(s) ready, {pending} still pending"
            else:
                status = "pending"
                message = f"All {total} test(s) are still pending"
            
            return {
                "success": True,
                "patient_id": patient_id,
                "status": status,
                "total_tests": total,
                "completed_tests": completed,
                "pending_tests": pending,
                "message": message,
                "all_ready": (completed == total and total > 0)
            }
            
        except Exception as e:
            return {
                "success": False,
                "patient_id": patient_id,
                "error": str(e),
                "message": f"Error checking status: {str(e)}"
            }
    
    async def _arun(self, patient_id: str) -> Dict[str, Any]:
        """Async version"""
        return self._run(patient_id)


class GetLatestLabResultTool(BaseTool, SheetsReaderBase):
    """
    Get the most recent lab result for a patient.
    Useful for quick updates.
    """
    
    name: str = "get_latest_lab_result"
    description: str = """
    Get the most recently updated lab result for a patient.
    
    Use this when:
    - Patient asks: "What's my latest result?"
    - You need just the most recent update
    - Quick status check
    
    Input: patient_id
    Output: Most recent test result
    """
    
    def _run(self, patient_id: str) -> Dict[str, Any]:
        """Get latest result"""
        try:
            # Use the main tool
            reader = ReadLabResultsFromSheetTool()
            full_results = reader._run(patient_id)
            
            if not full_results['success'] or not full_results.get('results'):
                return {
                    "success": False,
                    "patient_id": patient_id,
                    "message": "No lab results found"
                }
            
            # Get the most recently updated result
            results = full_results['results']
            # Sort by last_updated (if available) or test_date
            sorted_results = sorted(
                results,
                key=lambda x: x.get('last_updated') or x.get('test_date') or '',
                reverse=True
            )
            
            latest = sorted_results[0]
            
            return {
                "success": True,
                "patient_id": patient_id,
                "latest_result": latest,
                "total_results": len(results),
                "message": f"Latest result: {latest['test_name']}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "patient_id": patient_id,
                "error": str(e)
            }
    
    async def _arun(self, patient_id: str) -> Dict[str, Any]:
        """Async version"""
        return self._run(patient_id)


# Export tools
__all__ = [
    'ReadLabResultsFromSheetTool',
    'CheckLabResultStatusTool',
    'GetLatestLabResultTool'
]
