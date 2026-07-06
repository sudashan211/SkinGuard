---
title: Patient Features Completion
status: draft
priority: high
---

# Patient Features Completion - Requirements

## Overview
Implement missing patient-facing features to complete the SkinGuard platform for production readiness.

## Missing Features to Implement

### 1. Health Profile Management
**User Story**: As a patient, I want to set up and manage my health profile so that doctors have relevant medical context.

**Requirements**:
- Create dedicated Health Profile page
- Form fields:
  - Age (number, 1-120)
  - Skin Type (Fitzpatrick scale: I, II, III, IV, V, VI)
  - Family History (text area)
  - Medical conditions (optional)
  - Allergies (optional)
- Save profile to database
- Edit existing profile
- Display profile in patient dashboard

**Acceptance Criteria**:
- [ ] Profile page accessible from patient dashboard
- [ ] Form validates all required fields
- [ ] Data persists to Supabase database
- [ ] Profile displays on patient dashboard
- [ ] Doctors can view patient profile when reviewing reports

### 2. Appointment Booking System
**User Story**: As a patient, I want to book appointments with dermatologists so I can get professional consultation.

**Requirements**:
- Create Appointments page
- Features:
  - View available doctors
  - Select doctor and view their availability
  - Book appointment with date/time selection
  - Add appointment notes/reason
  - View upcoming appointments
  - View past appointments
  - Cancel appointments
  - Reschedule appointments
- Email notifications for:
  - Appointment confirmation
  - Appointment reminders (24 hours before)
  - Appointment cancellation

**Acceptance Criteria**:
- [ ] Appointments page accessible from patient dashboard
- [ ] Can browse and select doctors
- [ ] Can book appointments with available time slots
- [ ] Appointments saved to database
- [ ] Can view upcoming and past appointments
- [ ] Can cancel/reschedule appointments
- [ ] Email notifications sent (if SMTP configured)

### 3. Video Consultation System
**User Story**: As a patient, I want to have video consultations with doctors so I can get remote medical advice.

**Requirements**:
- Integrate video calling solution (WebRTC or third-party like Twilio/Agora)
- Features:
  - Join video call from appointment
  - Screen sharing capability
  - Chat during call
  - Record consultation (with consent)
  - End call functionality
- Security:
  - End-to-end encryption
  - HIPAA compliance considerations
  - Consent recording

**Acceptance Criteria**:
- [ ] Video call button available for scheduled appointments
- [ ] Both patient and doctor can join call
- [ ] Audio and video work properly
- [ ] Chat functionality works
- [ ] Call can be ended by either party
- [ ] Consultation notes saved after call

### 4. Privacy & Security Settings
**User Story**: As a patient, I want to manage my privacy and security settings so I can control my data.

**Requirements**:
- Create Privacy & Security Settings page
- Features:
  - Change password
  - Enable/disable two-factor authentication (2FA)
  - Manage data sharing preferences
  - View encryption status
  - Download personal data (GDPR compliance)
  - Delete account
  - View privacy policy
  - View terms of service
  - Manage notification preferences

**Acceptance Criteria**:
- [ ] Settings page accessible from patient dashboard
- [ ] Can change password with validation
- [ ] Can enable/disable 2FA
- [ ] Can manage data sharing preferences
- [ ] Can download personal data as JSON/PDF
- [ ] Can request account deletion
- [ ] Encryption status displayed
- [ ] Links to privacy policy and terms

## Technical Requirements

### Frontend
- Create new pages:
  - `HealthProfilePage.tsx`
  - `AppointmentsPage.tsx`
  - `VideoConsultationPage.tsx`
  - `PrivacySettingsPage.tsx`
- Add routes to `PatientDashboard.tsx`
- Create components:
  - `HealthProfileForm.tsx`
  - `AppointmentBooking.tsx`
  - `AppointmentList.tsx`
  - `VideoCall.tsx`
  - `SecuritySettings.tsx`
- Add services:
  - `healthProfile.ts`
  - `appointments.ts`
  - `videoCall.ts`
  - `security.ts`

### Backend
- Endpoints already exist for:
  - Patient data (health profile)
  - Appointments
- Need to add:
  - Video call token generation
  - 2FA endpoints
  - Data export endpoint
  - Account deletion endpoint

### Database
- Tables already exist:
  - `patient_data` (for health profile)
  - `appointments`
- May need to add:
  - `video_consultations`
  - `user_preferences`

## Dependencies
- Video calling: Need to choose provider (Twilio, Agora, or WebRTC)
- Email service: SMTP configuration for notifications
- 2FA: Need to integrate library (e.g., speakeasy, pyotp)

## Out of Scope
- Payment integration for appointments
- Insurance verification
- Prescription management
- Lab results integration

## Success Metrics
- Patients can complete health profile (100% of new users)
- Appointment booking success rate > 95%
- Video consultation completion rate > 90%
- Privacy settings usage > 50% of users
