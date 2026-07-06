# Requirements Document: SkinGuard AI Skin Cancer Screening Platform

## Introduction

SkinGuard is a web-based medical platform that provides AI-powered skin cancer screening combined with a doctor locator system. The platform enables patients to upload skin lesion images for AI analysis, receive probability-based assessments, and connect with verified dermatologists for clinical diagnosis. The system implements multi-layered content filtering to prevent misuse while maintaining medical accuracy through a human-in-the-loop approach.

## Glossary

- **System**: The complete SkinGuard platform including frontend, backend, and database
- **Gatekeeper**: The NSFW content filtering layer that validates images before medical analysis
- **Medical_AI**: The combined Swin Transformer and EfficientNet-B7 models for lesion detection and classification
- **Patient**: A registered user seeking skin cancer screening
- **Doctor**: A verified medical professional providing consultations
- **Admin**: A system administrator managing doctor verification and content moderation
- **Hotspot**: A visual overlay indicating AI-detected lesion locations on uploaded images
- **Fitzpatrick_Scale**: A numerical classification (I-VI) of human skin color types
- **NSFW_Score**: A numerical value (0-1) indicating inappropriate content probability
- **Medical_Report**: A database record containing patient image, AI predictions, and symptoms

## Requirements

### Requirement 1: User Authentication and Profile Management

**User Story:** As a user, I want to register and manage my profile with role-based access, so that I can access features appropriate to my role (patient, doctor, or admin).

#### Acceptance Criteria

1. WHEN a new user registers THEN the System SHALL create a profile record with unique UUID, full name, avatar URL, role assignment, and verification status
2. WHEN a user logs in THEN the System SHALL authenticate credentials using Supabase Auth and establish a session
3. WHEN a user updates their profile THEN the System SHALL persist changes to the profiles table immediately
4. WHEN a user's role is patient THEN the System SHALL grant access to diagnostic dashboard and doctor locator features
5. WHEN a user's role is doctor THEN the System SHALL grant access to patient report review features only after verification status is true
6. WHEN a user's role is admin THEN the System SHALL grant access to doctor verification and content moderation features

### Requirement 2: Patient Health Profile Management

**User Story:** As a patient, I want to maintain my health profile including age, skin type, and family history, so that the AI can provide more accurate risk assessments.

#### Acceptance Criteria

1. WHEN a patient completes onboarding THEN the System SHALL create a patient_data record linked to their profile UUID
2. WHEN a patient enters their age THEN the System SHALL validate it as a positive integer between 1 and 120
3. WHEN a patient selects skin type THEN the System SHALL accept only Fitzpatrick Scale values (I, II, III, IV, V, VI)
4. WHEN a patient enters family history THEN the System SHALL store the text without length restrictions
5. WHEN a patient updates health profile THEN the System SHALL persist changes to patient_data table immediately

### Requirement 3: Content Security and NSFW Filtering

**User Story:** As a system administrator, I want all uploaded images to pass through NSFW filtering before medical analysis, so that the platform prevents misuse and maintains medical integrity.

#### Acceptance Criteria

1. WHEN an image is uploaded THEN the Gatekeeper SHALL analyze it using the NSFW detector before any other processing
2. WHEN the NSFW_Score exceeds 0.35 THEN the Gatekeeper SHALL reject the image and return HTTP 403 error
3. WHEN the Non-Skin score exceeds 0.8 THEN the Gatekeeper SHALL reject the image and return HTTP 403 error
4. WHEN an image is rejected THEN the System SHALL return an error message stating "Inappropriate content detected"
5. WHEN an image passes NSFW filtering THEN the System SHALL proceed to Medical_AI analysis
6. WHEN an image is flagged THEN the System SHALL log the event for admin review

### Requirement 4: AI-Powered Skin Lesion Analysis

**User Story:** As a patient, I want to upload skin lesion images and receive AI-powered analysis with lesion detection and cancer classification, so that I can assess potential risks before consulting a doctor.

#### Acceptance Criteria

1. WHEN a safe image is received THEN the Medical_AI SHALL process it through Swin Transformer for lesion localization
2. WHEN lesion localization completes THEN the Medical_AI SHALL process the image through EfficientNet-B7 for cancer classification
3. WHEN classification completes THEN the System SHALL return predictions for all 7 skin cancer classes with probability scores
4. WHEN AI analysis completes THEN the System SHALL store results in medical_reports table with JSONB format
5. WHEN displaying results THEN the System SHALL overlay Hotspot markers on the original image indicating detected lesion locations
6. WHEN displaying predictions THEN the System SHALL include the disclaimer "This is a 94% probability estimate. Please consult verified doctors for clinical biopsy"

### Requirement 5: Symptom Collection and Documentation

**User Story:** As a patient, I want to document symptoms associated with my skin lesion through a structured wizard, so that doctors have comprehensive information for diagnosis.

#### Acceptance Criteria

1. WHEN a patient uploads an image THEN the System SHALL present a 3-step symptom wizard
2. WHEN completing Step 1 THEN the System SHALL capture lesion location on the body
3. WHEN completing Step 2 THEN the System SHALL capture sensation information (itching, pain, burning, numbness)
4. WHEN completing Step 3 THEN the System SHALL capture visual changes (color, size, shape, border irregularity)
5. WHEN the wizard is completed THEN the System SHALL store all symptom data in the medical_reports symptoms field
6. WHEN symptom data is saved THEN the System SHALL associate it with the corresponding image and AI prediction

### Requirement 6: Doctor Registration and Verification

**User Story:** As a doctor, I want to register with my medical license and clinic information, so that I can provide consultations to patients after admin verification.

#### Acceptance Criteria

1. WHEN a doctor registers THEN the System SHALL create a doctors record with license number, clinic name, location coordinates, and WhatsApp number
2. WHEN a doctor submits registration THEN the System SHALL set their verified status to false
3. WHEN an admin reviews a doctor application THEN the System SHALL display license number and clinic information
4. WHEN an admin approves a doctor THEN the System SHALL set verified status to true
5. WHEN a doctor's verified status is false THEN the System SHALL prevent access to patient reports
6. WHEN a doctor's verified status is true THEN the System SHALL grant access to pending patient reports

### Requirement 7: Geographic Doctor Discovery

**User Story:** As a patient, I want to find verified doctors near my location on an interactive map, so that I can easily connect with medical professionals for in-person consultations.

#### Acceptance Criteria

1. WHEN a patient accesses the doctor locator THEN the System SHALL display a Google Maps interface
2. WHEN the map loads THEN the System SHALL query all doctors where verified status is true
3. WHEN displaying doctors THEN the System SHALL place markers at coordinates specified by lat and lng fields
4. WHEN a patient clicks a marker THEN the System SHALL display a card with clinic name, doctor name, and WhatsApp contact
5. WHEN a patient clicks the WhatsApp button THEN the System SHALL generate a URL with format "https://wa.me/{whatsapp_no}?text=I would like to share my Derman Report"
6. WHEN the WhatsApp link is clicked THEN the System SHALL open the WhatsApp application or web interface with pre-filled message

### Requirement 8: Appointment Scheduling

**User Story:** As a patient, I want to schedule appointments with verified doctors, so that I can receive professional medical consultations.

#### Acceptance Criteria

1. WHEN a patient selects a doctor THEN the System SHALL display available appointment slots
2. WHEN a patient confirms an appointment THEN the System SHALL create an appointments record with patient_id, doctor_id, scheduled_at timestamp, and status
3. WHEN an appointment is created THEN the System SHALL set initial status to "pending"
4. WHEN a doctor views appointments THEN the System SHALL display all appointments where doctor_id matches their profile
5. WHEN an appointment time passes THEN the System SHALL allow status updates to "completed" or "cancelled"

### Requirement 9: Medical Report Management

**User Story:** As a doctor, I want to view pending patient reports with high-resolution images and AI predictions, so that I can provide informed medical consultations.

#### Acceptance Criteria

1. WHEN a doctor accesses the reports dashboard THEN the System SHALL display all medical_reports where status is "safe"
2. WHEN displaying a report THEN the System SHALL show the original high-resolution image, AI prediction JSONB data, and patient symptoms
3. WHEN a doctor reviews a report THEN the System SHALL display patient age, skin type, and family history from patient_data
4. WHEN a report contains AI predictions THEN the System SHALL display probability scores for all 7 cancer classes
5. WHEN a doctor completes review THEN the System SHALL allow adding consultation notes to the report

### Requirement 10: Admin Moderation and Content Management

**User Story:** As an admin, I want to moderate flagged content and manage doctor verifications, so that I can maintain platform integrity and user safety.

#### Acceptance Criteria

1. WHEN an admin accesses the admin panel THEN the System SHALL display pending doctor applications
2. WHEN an admin views flagged content THEN the System SHALL display all medical_reports where status is "flagged"
3. WHEN an admin reviews a doctor application THEN the System SHALL provide options to approve or reject with verification status update
4. WHEN an admin reviews flagged content THEN the System SHALL display the image, NSFW_Score, and rejection reason
5. WHEN an admin updates content THEN the System SHALL allow adding or editing medical information in the Skin-Wiki section

### Requirement 11: Frontend User Interface Components

**User Story:** As a user, I want an intuitive and responsive interface with smooth animations, so that I can easily navigate the platform and complete tasks efficiently.

#### Acceptance Criteria

1. WHEN a user visits the landing page THEN the System SHALL display a carousel with 3 slides showcasing AI Screening, Find Doctors, and Secure History features
2. WHEN the carousel animates THEN the System SHALL use Framer Motion for smooth transitions
3. WHEN a patient accesses the diagnostic dashboard THEN the System SHALL display a drag-and-drop image upload area
4. WHEN a patient drags an image over the dropzone THEN the System SHALL provide visual feedback indicating drop readiness
5. WHEN displaying AI results THEN the System SHALL render the image with Hotspot overlays using visual markers
6. WHEN the doctor locator loads THEN the System SHALL render Google Maps with interactive markers for all verified doctors

### Requirement 12: Data Persistence and Storage

**User Story:** As a system operator, I want all user data, medical reports, and AI predictions to be securely stored in Supabase PostgreSQL, so that data is reliably persisted and queryable.

#### Acceptance Criteria

1. WHEN any database operation occurs THEN the System SHALL use Supabase PostgreSQL as the data store
2. WHEN storing AI predictions THEN the System SHALL use JSONB format for flexible schema storage
3. WHEN storing images THEN the System SHALL upload to Supabase Storage and store the URL in image_url field
4. WHEN a medical report is created THEN the System SHALL ensure referential integrity between patient_id and profiles table
5. WHEN an appointment is created THEN the System SHALL ensure referential integrity between patient_id, doctor_id, and profiles table

### Requirement 13: API Backend Architecture

**User Story:** As a developer, I want a FastAPI backend that handles image processing, AI inference, and database operations, so that the frontend can communicate with backend services efficiently.

#### Acceptance Criteria

1. WHEN the backend starts THEN the System SHALL expose a FastAPI application with RESTful endpoints
2. WHEN an image upload request is received THEN the System SHALL accept multipart/form-data format
3. WHEN the /api/analyze-skin endpoint is called THEN the System SHALL execute the Gatekeeper, Medical_AI, and database storage in sequence
4. WHEN any API error occurs THEN the System SHALL return appropriate HTTP status codes (403 for content violations, 500 for server errors)
5. WHEN API responses are sent THEN the System SHALL use JSON format for structured data

### Requirement 14: Medical Disclaimer and Legal Compliance

**User Story:** As a platform owner, I want all AI predictions to include clear medical disclaimers, so that users understand the limitations and seek professional medical advice.

#### Acceptance Criteria

1. WHEN AI results are displayed THEN the System SHALL show the disclaimer "This is a 94% probability estimate. Please consult verified doctors for clinical biopsy"
2. WHEN a patient views results THEN the System SHALL prominently display the "Find Doctor" call-to-action button
3. WHEN displaying AI predictions THEN the System SHALL never use language suggesting definitive diagnosis
4. WHEN a patient accesses any medical information THEN the System SHALL include disclaimers about the educational nature of content


### Requirement 15: Report History and Tracking

**User Story:** As a patient, I want to view my complete history of skin screenings with comparison over time, so that I can monitor changes in my skin lesions and track my health journey.

#### Acceptance Criteria

1. WHEN a patient accesses their dashboard THEN the System SHALL display all previous medical_reports ordered by creation date descending
2. WHEN displaying report history THEN the System SHALL show thumbnail images, AI prediction summaries, submission dates, and status for each report
3. WHEN a patient selects a historical report THEN the System SHALL display the full report with original image, AI predictions, and symptoms
4. WHEN a patient has multiple reports of the same body location THEN the System SHALL offer a side-by-side comparison view
5. WHEN comparing reports THEN the System SHALL highlight changes in lesion size, color, or AI risk assessment
6. WHEN a report is older than 6 months THEN the System SHALL suggest a follow-up screening

### Requirement 16: Educational Content and Skin Health Resources

**User Story:** As a user, I want access to educational content about skin cancer types, prevention, and self-examination techniques, so that I can make informed decisions about my skin health.

#### Acceptance Criteria

1. WHEN a user accesses the Skin-Wiki section THEN the System SHALL display articles about the 7 skin cancer types with images and descriptions
2. WHEN displaying cancer type information THEN the System SHALL include risk factors, symptoms, and treatment options
3. WHEN a user views educational content THEN the System SHALL provide self-examination guides with illustrated body maps
4. WHEN displaying prevention tips THEN the System SHALL include UV protection recommendations and early detection guidelines
5. WHEN a patient receives AI results THEN the System SHALL link to relevant educational articles based on the detected cancer type
6. WHEN educational content is updated by admins THEN the System SHALL timestamp changes and maintain version history

### Requirement 17: Notification System

**User Story:** As a user, I want to receive notifications about appointment confirmations, report results, and important updates, so that I stay informed about my health status and platform activities.

#### Acceptance Criteria

1. WHEN a patient's AI analysis completes THEN the System SHALL send an email notification with result summary
2. WHEN a doctor confirms an appointment THEN the System SHALL send notifications to both patient and doctor with appointment details
3. WHEN an appointment is scheduled within 24 hours THEN the System SHALL send a reminder notification
4. WHEN a doctor's verification status changes to true THEN the System SHALL send a welcome email with platform guidelines
5. WHEN a patient has not uploaded a screening in 6 months THEN the System SHALL send a reminder notification
6. WHEN critical system updates occur THEN the System SHALL display in-app notifications to all affected users

### Requirement 18: Privacy and Data Security

**User Story:** As a user, I want my medical data to be encrypted and securely stored with clear privacy controls, so that my sensitive health information remains confidential.

#### Acceptance Criteria

1. WHEN storing medical images THEN the System SHALL encrypt files at rest using AES-256 encryption
2. WHEN transmitting data between client and server THEN the System SHALL use HTTPS/TLS encryption
3. WHEN a patient deletes their account THEN the System SHALL permanently remove all associated medical_reports and patient_data within 30 days
4. WHEN a user accesses their data THEN the System SHALL log the access event with timestamp and user identifier
5. WHEN a patient views privacy settings THEN the System SHALL allow opting out of data sharing for research purposes
6. WHEN exporting patient data THEN the System SHALL provide data in machine-readable format (JSON/PDF) for portability

### Requirement 19: Multi-Language Support

**User Story:** As a user, I want to use SkinGuard in my preferred language, so that I can understand medical information and navigate the platform effectively.

#### Acceptance Criteria

1. WHEN a user first visits the platform THEN the System SHALL detect browser language and set interface language accordingly
2. WHEN a user changes language preference THEN the System SHALL persist the selection and apply it to all interface elements
3. WHEN displaying medical disclaimers THEN the System SHALL show translations in the user's selected language
4. WHEN AI results are displayed THEN the System SHALL translate cancer type names and descriptions to the selected language
5. THE System SHALL support at minimum English, Spanish, French, German, and Mandarin Chinese
6. WHEN educational content is added THEN the System SHALL require translations for all supported languages before publication

### Requirement 20: Performance Monitoring and Analytics

**User Story:** As a system administrator, I want to monitor platform performance and usage analytics, so that I can identify issues, optimize resources, and understand user behavior.

#### Acceptance Criteria

1. WHEN AI analysis is performed THEN the System SHALL log processing time for Gatekeeper and Medical_AI separately
2. WHEN API endpoints are called THEN the System SHALL track response times and error rates
3. WHEN the admin accesses analytics dashboard THEN the System SHALL display daily active users, total screenings, and average processing time
4. WHEN system performance degrades THEN the System SHALL send alerts to administrators when response times exceed 5 seconds
5. WHEN analyzing usage patterns THEN the System SHALL track most common cancer types detected and geographic distribution of users
6. WHEN generating reports THEN the System SHALL provide weekly summaries of platform health metrics

### Requirement 21: Mobile Responsiveness and Progressive Web App

**User Story:** As a mobile user, I want to access SkinGuard on my smartphone with a native-like experience, so that I can conveniently upload photos and check results on the go.

#### Acceptance Criteria

1. WHEN a user accesses SkinGuard on a mobile device THEN the System SHALL display a responsive layout optimized for screen size
2. WHEN a mobile user uploads an image THEN the System SHALL allow direct camera capture in addition to file selection
3. WHEN installed as a PWA THEN the System SHALL function offline for viewing historical reports
4. WHEN network connectivity is restored THEN the System SHALL sync pending uploads and fetch new data
5. WHEN a mobile user interacts with the map THEN the System SHALL use device GPS to center on user location
6. WHEN displaying images on mobile THEN the System SHALL use touch gestures for zoom and pan functionality

### Requirement 22: Doctor Rating and Review System

**User Story:** As a patient, I want to rate and review doctors after consultations, so that I can help other patients make informed decisions and provide feedback to medical professionals.

#### Acceptance Criteria

1. WHEN a patient completes an appointment THEN the System SHALL prompt for a rating (1-5 stars) and optional written review
2. WHEN a patient submits a review THEN the System SHALL associate it with the doctor's profile and display it publicly
3. WHEN displaying doctor profiles THEN the System SHALL show average rating and total number of reviews
4. WHEN a review contains inappropriate content THEN the System SHALL allow doctors to flag it for admin review
5. WHEN calculating doctor rankings THEN the System SHALL use average rating and number of consultations as factors
6. WHEN a doctor receives a rating below 3 stars THEN the System SHALL notify the admin for quality assurance review

### Requirement 23: Emergency Referral System

**User Story:** As a patient, I want to be immediately alerted if AI detects high-risk lesions, so that I can seek urgent medical attention when necessary.

#### Acceptance Criteria

1. WHEN AI prediction shows any cancer type with probability exceeding 85% THEN the System SHALL flag the report as "urgent"
2. WHEN a report is flagged as urgent THEN the System SHALL display a prominent warning message to the patient
3. WHEN an urgent case is detected THEN the System SHALL automatically notify the 3 nearest verified doctors via email
4. WHEN displaying urgent results THEN the System SHALL provide a direct "Emergency Consultation" button linking to emergency contact numbers
5. WHEN a doctor views urgent cases THEN the System SHALL prioritize them at the top of the pending reports list
6. WHEN an urgent case remains unreviewed for 24 hours THEN the System SHALL send escalation notifications to admins

### Requirement 24: Image Quality Validation

**User Story:** As a system operator, I want to ensure uploaded images meet minimum quality standards, so that AI analysis can provide accurate results.

#### Acceptance Criteria

1. WHEN an image is uploaded THEN the System SHALL validate minimum resolution of 512x512 pixels
2. WHEN an image is too small THEN the System SHALL reject it with message "Image resolution too low for accurate analysis"
3. WHEN an image is blurry THEN the System SHALL calculate blur score and warn if below quality threshold
4. WHEN an image has poor lighting THEN the System SHALL analyze brightness histogram and suggest retaking with better lighting
5. WHEN an image passes quality checks THEN the System SHALL proceed to NSFW filtering
6. WHEN an image fails quality validation THEN the System SHALL provide specific guidance on how to capture a better image

### Requirement 25: Telemedicine Integration

**User Story:** As a patient, I want to conduct video consultations with doctors directly through the platform, so that I can receive medical advice without traveling to a clinic.

#### Acceptance Criteria

1. WHEN a patient books an appointment THEN the System SHALL offer options for in-person or video consultation
2. WHEN a video consultation is scheduled THEN the System SHALL generate a unique meeting room URL
3. WHEN the appointment time arrives THEN the System SHALL send meeting links to both patient and doctor
4. WHEN a video call is active THEN the System SHALL allow screen sharing for reviewing medical reports together
5. WHEN a consultation ends THEN the System SHALL allow the doctor to add consultation notes directly to the medical report
6. WHEN video consultations are conducted THEN the System SHALL ensure HIPAA-compliant video encryption
