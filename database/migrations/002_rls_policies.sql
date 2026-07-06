-- SkinGuard Row Level Security Policies
-- Migration 002: RLS Policies
-- Requirements: 12.1, 12.4, 12.5

-- ============================================================================
-- ENABLE RLS ON ALL TABLES
-- ============================================================================
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE patient_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE doctors ENABLE ROW LEVEL SECURITY;
ALTER TABLE medical_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- PROFILES TABLE POLICIES
-- ============================================================================

-- Users can view their own profile
CREATE POLICY "Users can view own profile"
    ON profiles FOR SELECT
    USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile"
    ON profiles FOR UPDATE
    USING (auth.uid() = id);

-- Admins can view all profiles
CREATE POLICY "Admins can view all profiles"
    ON profiles FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Admins can update any profile (for verification)
CREATE POLICY "Admins can update profiles"
    ON profiles FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Allow profile creation during signup (handled by Supabase Auth)
CREATE POLICY "Allow profile creation"
    ON profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

-- ============================================================================
-- PATIENT_DATA TABLE POLICIES
-- ============================================================================

-- Patients can view their own data
CREATE POLICY "Patients can view own data"
    ON patient_data FOR SELECT
    USING (auth.uid() = user_id);

-- Patients can insert their own data
CREATE POLICY "Patients can insert own data"
    ON patient_data FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Patients can update their own data
CREATE POLICY "Patients can update own data"
    ON patient_data FOR UPDATE
    USING (auth.uid() = user_id);

-- Doctors can view patient data for their appointments
CREATE POLICY "Doctors can view patient data for appointments"
    ON patient_data FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'doctor' AND verified = TRUE
        )
        AND EXISTS (
            SELECT 1 FROM appointments
            WHERE appointments.patient_id = patient_data.user_id
            AND appointments.doctor_id IN (
                SELECT id FROM doctors WHERE user_id = auth.uid()
            )
        )
    );

-- Admins can view all patient data
CREATE POLICY "Admins can view all patient data"
    ON patient_data FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- ============================================================================
-- DOCTORS TABLE POLICIES
-- ============================================================================

-- Anyone can view verified doctors (for doctor locator)
CREATE POLICY "Anyone can view verified doctors"
    ON doctors FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = doctors.user_id AND profiles.verified = TRUE
        )
    );

-- Doctors can view their own profile
CREATE POLICY "Doctors can view own profile"
    ON doctors FOR SELECT
    USING (auth.uid() = user_id);

-- Doctors can insert their own profile
CREATE POLICY "Doctors can insert own profile"
    ON doctors FOR INSERT
    WITH CHECK (
        auth.uid() = user_id
        AND EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'doctor'
        )
    );

-- Doctors can update their own profile
CREATE POLICY "Doctors can update own profile"
    ON doctors FOR UPDATE
    USING (auth.uid() = user_id);

-- Admins can view all doctors
CREATE POLICY "Admins can view all doctors"
    ON doctors FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Admins can update doctors (for verification)
CREATE POLICY "Admins can update doctors"
    ON doctors FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- ============================================================================
-- MEDICAL_REPORTS TABLE POLICIES
-- ============================================================================

-- Patients can view their own reports
CREATE POLICY "Patients can view own reports"
    ON medical_reports FOR SELECT
    USING (auth.uid() = patient_id);

-- Patients can insert their own reports
CREATE POLICY "Patients can insert own reports"
    ON medical_reports FOR INSERT
    WITH CHECK (auth.uid() = patient_id);

-- Verified doctors can view safe and urgent reports
CREATE POLICY "Verified doctors can view reports"
    ON medical_reports FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'doctor' AND verified = TRUE
        )
        AND status IN ('safe', 'urgent')
    );

-- Verified doctors can update reports (add consultation notes)
CREATE POLICY "Verified doctors can update reports"
    ON medical_reports FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'doctor' AND verified = TRUE
        )
        AND status IN ('safe', 'urgent')
    );

-- Admins can view all reports
CREATE POLICY "Admins can view all reports"
    ON medical_reports FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Admins can update all reports
CREATE POLICY "Admins can update all reports"
    ON medical_reports FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- ============================================================================
-- APPOINTMENTS TABLE POLICIES
-- ============================================================================

-- Patients can view their own appointments
CREATE POLICY "Patients can view own appointments"
    ON appointments FOR SELECT
    USING (auth.uid() = patient_id);

-- Patients can create appointments
CREATE POLICY "Patients can create appointments"
    ON appointments FOR INSERT
    WITH CHECK (auth.uid() = patient_id);

-- Patients can update their own appointments
CREATE POLICY "Patients can update own appointments"
    ON appointments FOR UPDATE
    USING (auth.uid() = patient_id);

-- Doctors can view their appointments
CREATE POLICY "Doctors can view their appointments"
    ON appointments FOR SELECT
    USING (
        doctor_id IN (
            SELECT id FROM doctors WHERE user_id = auth.uid()
        )
    );

-- Doctors can update their appointments (confirm, complete)
CREATE POLICY "Doctors can update their appointments"
    ON appointments FOR UPDATE
    USING (
        doctor_id IN (
            SELECT id FROM doctors WHERE user_id = auth.uid()
        )
    );

-- Admins can view all appointments
CREATE POLICY "Admins can view all appointments"
    ON appointments FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- ============================================================================
-- REVIEWS TABLE POLICIES
-- ============================================================================

-- Anyone can view reviews (public)
CREATE POLICY "Anyone can view reviews"
    ON reviews FOR SELECT
    USING (TRUE);

-- Patients can insert reviews for their appointments
CREATE POLICY "Patients can insert reviews"
    ON reviews FOR INSERT
    WITH CHECK (
        auth.uid() = patient_id
        AND EXISTS (
            SELECT 1 FROM appointments
            WHERE appointments.id = reviews.appointment_id
            AND appointments.patient_id = auth.uid()
            AND appointments.status = 'completed'
        )
    );

-- Patients can update their own reviews
CREATE POLICY "Patients can update own reviews"
    ON reviews FOR UPDATE
    USING (auth.uid() = patient_id);

-- Doctors can flag reviews
CREATE POLICY "Doctors can flag reviews"
    ON reviews FOR UPDATE
    USING (
        doctor_id IN (
            SELECT id FROM doctors WHERE user_id = auth.uid()
        )
    );

-- Admins can update all reviews
CREATE POLICY "Admins can update all reviews"
    ON reviews FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- ============================================================================
-- NOTIFICATIONS TABLE POLICIES
-- ============================================================================

-- Users can view their own notifications
CREATE POLICY "Users can view own notifications"
    ON notifications FOR SELECT
    USING (auth.uid() = user_id);

-- Users can update their own notifications (mark as read)
CREATE POLICY "Users can update own notifications"
    ON notifications FOR UPDATE
    USING (auth.uid() = user_id);

-- System can insert notifications (via service role)
CREATE POLICY "System can insert notifications"
    ON notifications FOR INSERT
    WITH CHECK (TRUE);

-- Admins can view all notifications
CREATE POLICY "Admins can view all notifications"
    ON notifications FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- ============================================================================
-- AUDIT_LOGS TABLE POLICIES
-- ============================================================================

-- System can insert audit logs (via service role)
CREATE POLICY "System can insert audit logs"
    ON audit_logs FOR INSERT
    WITH CHECK (TRUE);

-- Users can view their own audit logs
CREATE POLICY "Users can view own audit logs"
    ON audit_logs FOR SELECT
    USING (auth.uid() = user_id);

-- Admins can view all audit logs
CREATE POLICY "Admins can view all audit logs"
    ON audit_logs FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- ============================================================================
-- HELPER FUNCTIONS FOR RLS
-- ============================================================================

-- Function to check if user is admin
CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM profiles
        WHERE id = auth.uid() AND role = 'admin'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user is verified doctor
CREATE OR REPLACE FUNCTION is_verified_doctor()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM profiles
        WHERE id = auth.uid() AND role = 'doctor' AND verified = TRUE
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user is patient
CREATE OR REPLACE FUNCTION is_patient()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM profiles
        WHERE id = auth.uid() AND role = 'patient'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
