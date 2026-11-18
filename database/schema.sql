-- ============================================================================
-- HOSPITAL AI AGENT - PostgreSQL Database Schema
-- ============================================================================
-- Created: 2025-10-21
-- Purpose: Replace JSON files with proper relational database
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- PATIENTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id VARCHAR(20) UNIQUE NOT NULL, -- REG2025XXXXXX format
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    full_name VARCHAR(200),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    date_of_birth DATE NOT NULL,
    age INTEGER,
    gender VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(10),
    
    -- Additional metadata
    drive_folder_id VARCHAR(100),
    drive_folder_url TEXT,
    spreadsheet_id VARCHAR(100),
    photo_url TEXT,
    
    -- Emergency contact
    emergency_contact_name VARCHAR(200),
    emergency_contact_phone VARCHAR(20),
    emergency_contact_relation VARCHAR(50),
    
    -- Registration info
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_visit_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, discharged
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for patients table
CREATE INDEX idx_patient_id ON patients(patient_id);
CREATE INDEX idx_email ON patients(email);
CREATE INDEX idx_phone ON patients(phone);
CREATE INDEX idx_status ON patients(status);

-- ============================================================================
-- WORKFLOW STATES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS workflow_states (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id VARCHAR(20) UNIQUE NOT NULL REFERENCES patients(patient_id) ON DELETE CASCADE,
    
    -- Workflow tracking
    current_stage INTEGER DEFAULT 1,
    stage_name VARCHAR(50),
    stage_data JSONB DEFAULT '{}', -- Store stage-specific data
    conversation_history JSONB DEFAULT '[]', -- Full conversation log
    
    -- State flags
    awaiting_confirmation BOOLEAN DEFAULT FALSE,
    pending_actions JSONB DEFAULT '[]',
    
    -- Metadata
    workflow_started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_interaction_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Session management
    session_id VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for workflow_states table
CREATE INDEX idx_patient_workflow ON workflow_states(patient_id);
CREATE INDEX idx_session ON workflow_states(session_id);
CREATE INDEX idx_active ON workflow_states(is_active);

-- ============================================================================
-- OTP VERIFICATIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS otp_verifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id VARCHAR(20),
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    
    -- OTP details
    otp_code VARCHAR(6) NOT NULL,
    otp_type VARCHAR(10) DEFAULT 'sms', -- sms, email
    purpose VARCHAR(50) DEFAULT 'registration', -- registration, login, payment
    
    -- Verification status
    is_verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP,
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    
    -- Expiry
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for otp_verifications table
CREATE INDEX idx_phone_otp ON otp_verifications(phone);
CREATE INDEX idx_email_otp ON otp_verifications(email);
CREATE INDEX idx_expiry ON otp_verifications(expires_at);

-- ============================================================================
-- MEDICAL RECORDS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS medical_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id VARCHAR(20) REFERENCES patients(patient_id) ON DELETE CASCADE,
    
    -- Medical history
    chief_complaint TEXT,
    past_conditions JSONB DEFAULT '[]',
    allergies JSONB DEFAULT '[]',
    current_medications JSONB DEFAULT '[]',
    family_history JSONB DEFAULT '{}',
    
    -- Risk assessment
    risk_level VARCHAR(20), -- low, medium, high
    risk_analysis TEXT,
    
    -- Timestamps
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for medical_records table
CREATE INDEX idx_patient_medical ON medical_records(patient_id);

-- ============================================================================
-- APPOINTMENTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS appointments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    appointment_id VARCHAR(20) UNIQUE NOT NULL,
    patient_id VARCHAR(20) REFERENCES patients(patient_id) ON DELETE CASCADE,
    
    -- Appointment details
    appointment_type VARCHAR(50), -- consultation, lab, follow-up
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    duration_minutes INTEGER DEFAULT 30,
    
    -- Doctor/Department
    doctor_name VARCHAR(200),
    department VARCHAR(100),
    
    -- Status
    status VARCHAR(20) DEFAULT 'scheduled', -- scheduled, completed, cancelled, no-show
    
    -- Calendar integration
    calendar_event_id VARCHAR(200),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for appointments table
CREATE INDEX idx_patient_appointments ON appointments(patient_id);
CREATE INDEX idx_appointment_date ON appointments(appointment_date);
CREATE INDEX idx_appointment_status ON appointments(status);

-- ============================================================================
-- LAB TESTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS lab_tests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_id VARCHAR(20) UNIQUE NOT NULL,
    patient_id VARCHAR(20) REFERENCES patients(patient_id) ON DELETE CASCADE,
    
    -- Test details
    test_name VARCHAR(200) NOT NULL,
    test_category VARCHAR(100),
    ordered_date DATE DEFAULT CURRENT_DATE,
    sample_collection_date DATE,
    result_date DATE,
    
    -- Results
    result_value VARCHAR(100),
    reference_range VARCHAR(100),
    status VARCHAR(20), -- normal, abnormal, critical
    result_notes TEXT,
    
    -- Metadata
    ordered_by VARCHAR(200),
    approved_by VARCHAR(200),
    lab_technician VARCHAR(200),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for lab_tests table
CREATE INDEX idx_patient_tests ON lab_tests(patient_id);
CREATE INDEX idx_test_status ON lab_tests(status);

-- ============================================================================
-- PAYMENTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    payment_id VARCHAR(20) UNIQUE NOT NULL,
    patient_id VARCHAR(20) REFERENCES patients(patient_id) ON DELETE CASCADE,
    
    -- Payment details
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'INR',
    payment_type VARCHAR(50), -- registration, consultation, lab, admission, discharge
    description TEXT,
    
    -- Payment gateway
    gateway VARCHAR(50), -- razorpay, stripe, cash
    gateway_transaction_id VARCHAR(200),
    payment_link TEXT,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- pending, completed, failed, refunded
    payment_date TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for payments table
CREATE INDEX idx_patient_payments ON payments(patient_id);
CREATE INDEX idx_payment_status ON payments(status);

-- ============================================================================
-- DOCUMENTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id VARCHAR(20) REFERENCES patients(patient_id) ON DELETE CASCADE,
    
    -- Document details
    document_name VARCHAR(255) NOT NULL,
    document_type VARCHAR(50), -- id_proof, medical_report, insurance, prescription
    file_path TEXT,
    drive_file_id VARCHAR(100),
    drive_file_url TEXT,
    
    -- OCR/Extracted data
    extracted_data JSONB,
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by VARCHAR(200),
    verified_at TIMESTAMP,
    
    -- Timestamps
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for documents table
CREATE INDEX idx_patient_documents ON documents(patient_id);
CREATE INDEX idx_document_type ON documents(document_type);

-- ============================================================================
-- NOTIFICATIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id VARCHAR(20) REFERENCES patients(patient_id) ON DELETE CASCADE,
    
    -- Notification details
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50), -- email, sms, whatsapp, push
    
    -- Delivery
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending', -- pending, sent, delivered, failed
    
    -- Metadata
    channel_details JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for notifications table
CREATE INDEX idx_patient_notifications ON notifications(patient_id);
CREATE INDEX idx_notification_status ON notifications(status);

-- ============================================================================
-- TRIGGERS FOR AUTO-UPDATE TIMESTAMPS AND COMPUTED FIELDS
-- ============================================================================

-- Update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Update computed fields for patients
CREATE OR REPLACE FUNCTION update_patient_computed_fields()
RETURNS TRIGGER AS $$
BEGIN
    -- Update full_name
    NEW.full_name = NEW.first_name || ' ' || COALESCE(NEW.last_name, '');
    
    -- Update age from date_of_birth
    NEW.age = EXTRACT(YEAR FROM AGE(NEW.date_of_birth));
    
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_patients_computed_fields BEFORE INSERT OR UPDATE ON patients
    FOR EACH ROW EXECUTE FUNCTION update_patient_computed_fields();

CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON patients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflow_states_updated_at BEFORE UPDATE ON workflow_states
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_medical_records_updated_at BEFORE UPDATE ON medical_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_appointments_updated_at BEFORE UPDATE ON appointments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Active patients with their current workflow stage
CREATE OR REPLACE VIEW active_patient_workflows AS
SELECT 
    p.patient_id,
    p.full_name,
    p.email,
    p.phone,
    w.current_stage,
    w.stage_name,
    w.last_interaction_at,
    w.awaiting_confirmation
FROM patients p
LEFT JOIN workflow_states w ON p.patient_id = w.patient_id
WHERE p.status = 'active' AND w.is_active = TRUE;

-- Patient complete profile
CREATE OR REPLACE VIEW patient_profiles AS
SELECT 
    p.*,
    m.chief_complaint,
    m.risk_level,
    w.current_stage,
    w.stage_name,
    COUNT(DISTINCT a.id) as total_appointments,
    COUNT(DISTINCT l.id) as total_lab_tests
FROM patients p
LEFT JOIN medical_records m ON p.patient_id = m.patient_id
LEFT JOIN workflow_states w ON p.patient_id = w.patient_id
LEFT JOIN appointments a ON p.patient_id = a.patient_id
LEFT JOIN lab_tests l ON p.patient_id = l.patient_id
GROUP BY p.id, m.id, w.id;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Composite indexes for common queries
CREATE INDEX idx_patient_status_date ON patients(status, registration_date DESC);
CREATE INDEX idx_workflow_patient_active ON workflow_states(patient_id, is_active);
CREATE INDEX idx_appointments_patient_date ON appointments(patient_id, appointment_date DESC);
CREATE INDEX idx_lab_tests_patient_date ON lab_tests(patient_id, result_date DESC);

-- ============================================================================
-- SAMPLE DATA INSERT (FOR TESTING)
-- ============================================================================

-- This will be populated by the application
-- INSERT INTO patients (patient_id, first_name, email, phone, date_of_birth, gender, address)
-- VALUES ('REG2025000001', 'Test', 'test@example.com', '+91-9999999999', '1990-01-01', 'Male', 'Test Address');
