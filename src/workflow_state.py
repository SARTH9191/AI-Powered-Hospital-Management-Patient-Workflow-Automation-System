"""
Hospital Management Workflow State Definition
Defines the state structure that flows through the LangGraph workflow
"""

from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime


class PatientState(TypedDict):
    """
    State object that flows through the entire hospital workflow.
    This state is passed between all agent nodes and updated at each stage.
    """
    
    # ========== PATIENT INFORMATION ==========
    patient_id: Optional[str]  # Unique patient identifier
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    emergency_contact: Optional[Dict[str, str]]
    is_new_patient: Optional[bool]
    
    # ========== REGISTRATION PHASE ==========
    registration_id: Optional[str]
    registration_date: Optional[str]
    registration_complete: bool
    
    # ========== DOCUMENTS ==========
    documents: List[Dict[str, Any]]  # List of uploaded documents
    documents_complete: bool
    missing_documents: List[str]
    drive_folder_url: Optional[str]
    
    # ========== MEDICAL HISTORY ==========
    medical_history: Optional[Dict[str, Any]]
    past_conditions: List[str]
    allergies: List[str]
    current_medications: List[str]
    has_past_issues: bool
    risk_assessment: Optional[str]
    
    # ========== LAB TESTS ==========
    tests_required: bool
    recommended_tests: List[str]
    lab_preference: Optional[str]  # "internal" or "external"
    lab_appointment: Optional[Dict[str, Any]]
    test_results: Optional[Dict[str, Any]]
    results_normal: bool
    
    # ========== ADMISSION PLANNING ==========
    admission_required: bool
    bed_available: bool
    bed_number: Optional[str]
    room_type: Optional[str]
    assigned_doctor: Optional[str]
    admission_date: Optional[str]
    
    # ========== BILLING ==========
    estimated_cost: float
    has_insurance: bool
    insurance_coverage: Optional[Dict[str, Any]]
    patient_copay: float
    billing_id: Optional[str]
    
    # ========== ADMISSION STATUS ==========
    admission_confirmed: bool
    admission_id: Optional[str]
    checkin_time: Optional[str]
    checkout_time: Optional[str]
    
    # ========== DAILY TRACKING ==========
    daily_charges: List[Dict[str, Any]]
    medicine_from_hospital: bool
    procedures_done: List[Dict[str, Any]]
    total_bill: float
    
    # ========== DISCHARGE ==========
    ready_for_discharge: bool
    discharge_summary: Optional[str]
    discharge_date: Optional[str]
    payment_complete: bool
    payment_plan: Optional[Dict[str, Any]]
    
    # ========== FOLLOW-UP ==========
    followup_scheduled: bool
    followup_date: Optional[str]
    medicine_reminders_set: bool
    feedback_sent: bool
    
    # ========== WORKFLOW CONTROL ==========
    current_stage: str  # Current workflow stage
    next_action: Optional[str]  # Next action to perform
    user_approval_required: bool  # Flag if user approval is needed
    user_approved: bool  # User's approval decision
    continue_command: Optional[bool]  # Flag to continue to next stage (stage gating)
    messages: List[str]  # Communication log
    errors: List[str]  # Error log
    
    # ========== AGENT DECISIONS ==========
    agent_recommendations: List[Dict[str, Any]]  # LLM recommendations at each stage
    
    # ========== METADATA ==========
    workflow_started_at: Optional[str]
    workflow_completed_at: Optional[str]
    last_updated_at: Optional[str]
