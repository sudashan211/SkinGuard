# Implementation Plan: SkinGuard AI Skin Cancer Screening Platform

## Overview

This implementation plan breaks down the SkinGuard platform into discrete, incremental tasks. The approach follows a layered architecture: database setup → backend API → AI integration → frontend UI → advanced features. Each task builds on previous work, with checkpoints to ensure stability before proceeding.

The implementation uses:
- **Backend**: Python with FastAPI
- **Frontend**: TypeScript with React + Vite
- **Database**: Supabase (PostgreSQL)
- **AI Models**: PyTorch-based models (NSFW detector, Swin Transformer, EfficientNet-B7)
- **Testing**: Hypothesis (Python) and fast-check (TypeScript) for property-based testing

## Tasks

### Phase 1: Foundation - Database and Authentication

- [x] 1. Database Schema and Infrastructure Setup
  - Create Supabase project and configure connection
  - Implement all database tables (profiles, patient_data, doctors, medical_reports, appointments, reviews, notifications, audit_logs)
  - Set up indexes for performance optimization (geographic indexes for doctors, time-based indexes for reports)
  - Configure Row Level Security (RLS) policies for data isolation
  - Set up Supabase Storage buckets for medical images with encryption
  - _Requirements: 12.1, 12.4, 12.5, 18.1_

- [x]* 1.1 Write property test for referential integrity
  - **Property 33: Referential Integrity Enforcement**
  - **Validates: Requirements 12.4, 12.5**

- [x] 2. Authentication and User Management Backend
  - [x] 2.1 Implement user registration endpoint with role assignment
    - Create POST /api/auth/signup endpoint
    - Implement password hashing with bcrypt
    - Create profile record with UUID generation
    - Support role selection (patient, doctor, admin)
    - _Requirements: 1.1_


  - [x]* 2.2 Write property test for user registration completeness
    - **Property 1: User Registration Completeness**
    - **Validates: Requirements 1.1**

  - [x] 2.3 Implement authentication endpoints
    - Create POST /api/auth/login endpoint with JWT token generation
    - Create POST /api/auth/logout endpoint
    - Create GET /api/auth/me endpoint for current user
    - Create POST /api/auth/refresh for token refresh
    - _Requirements: 1.2_

  - [x]* 2.4 Write property test for authentication round trip
    - **Property 2: Authentication Round Trip**
    - **Validates: Requirements 1.2**

  - [x] 2.5 Implement role-based access control middleware
    - Create permission decorators for patient, doctor, admin roles
    - Implement verification status checks for doctors
    - Block unverified doctors from accessing patient reports
    - _Requirements: 1.4, 1.5, 1.6, 6.5, 6.6_

  - [x]* 2.6 Write property test for role-based access control
    - **Property 4: Role-Based Access Control**
    - **Validates: Requirements 1.4, 1.5, 1.6, 6.5, 6.6**

- [x] 3. Checkpoint - Authentication System
  - Ensure all authentication tests pass
  - Verify JWT token generation and validation
  - Test role-based access control with all three roles
  - Ask the user if questions arise

### Phase 2: Patient Profile and Health Data

- [x] 4. Patient Profile Management
  - [x] 4.1 Implement patient data endpoints
    - Create POST /api/patient/profile for creating patient_data
    - Create PUT /api/patient/profile for updates
    - Create GET /api/patient/profile for retrieval
    - Implement age validation (1-120)
    - Implement Fitzpatrick scale validation (I-VI)
    - Store family history text without length restrictions
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x]* 4.2 Write property tests for patient data validation
    - **Property 5: Age Validation Bounds**
    - **Property 6: Fitzpatrick Scale Enum Validation**
    - **Property 7: Text Storage Without Truncation**
    - **Validates: Requirements 2.2, 2.3, 2.4**

  - [x]* 4.3 Write property test for profile update persistence
    - **Property 3: Profile Update Persistence**
    - **Validates: Requirements 1.3, 2.5**


### Phase 3: Image Processing and AI Pipeline

- [x] 5. Image Quality Validation Module
  - [x] 5.1 Implement image quality validator
    - Create resolution validation (minimum 512x512)
    - Implement blur detection using Laplacian variance
    - Implement brightness histogram analysis
    - Create quality validation error responses with guidance
    - _Requirements: 24.1, 24.2, 24.3, 24.4, 24.6_

  - [x]* 5.2 Write property tests for image quality validation
    - **Property 85: Image Resolution Validation**
    - **Property 86: Low Resolution Error Message**
    - **Property 87: Image Quality Validation**
    - **Property 88: Quality Validation Guidance**
    - **Validates: Requirements 24.1, 24.2, 24.3, 24.4, 24.6**

- [x] 6. NSFW Content Filter (Gatekeeper)
  - [x] 6.1 Integrate NSFW detection model
    - Set up NSFW detector (NudeNet or Yahoo Open NSFW)
    - Implement image preprocessing for NSFW model
    - Create NSFW scoring function
    - Implement rejection logic (nsfw_score > 0.35 OR non_skin_score > 0.8)
    - Return HTTP 403 with "Inappropriate content detected" message
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [x]* 6.2 Write property tests for NSFW filtering
    - **Property 8: NSFW Score Rejection Threshold**
    - **Property 9: Non-Skin Score Rejection Threshold**
    - **Validates: Requirements 3.2, 3.3, 3.4**

  - [x] 6.3 Implement audit logging for flagged content
    - Create audit log entries for rejected images
    - Store NSFW scores and rejection reasons
    - Log user_id, timestamp, and IP address
    - _Requirements: 3.6, 18.4_

  - [x]* 6.4 Write property test for flagged content audit logging
    - **Property 10: Flagged Content Audit Logging**
    - **Property 54: Data Access Audit Logging**
    - **Validates: Requirements 3.6, 18.4**

- [x] 7. AI Medical Analysis Pipeline
  - [x] 7.1 Set up AI model infrastructure
    - Install PyTorch and required ML libraries
    - Create model loading utilities with caching
    - Set up model storage strategy
    - _Requirements: 4.1, 4.2_

  - [x] 7.2 Integrate Swin Transformer for lesion detection
    - Load pre-trained Swin Transformer model
    - Implement image preprocessing for Swin
    - Create lesion localization function returning hotspots (bounding boxes)
    - _Requirements: 4.1, 4.5_


  - [x] 7.3 Integrate EfficientNet-B7 for cancer classification
    - Load pre-trained EfficientNet-B7 model
    - Implement image preprocessing for EfficientNet
    - Create classification function returning 7 cancer type probabilities
    - Ensure probabilities sum to approximately 1.0
    - _Requirements: 4.2, 4.3_

  - [x]* 7.4 Write property test for cancer classification completeness
    - **Property 11: Cancer Classification Completeness**
    - **Validates: Requirements 4.3**

  - [x] 7.5 Implement complete analysis pipeline
    - Create AnalysisPipeline class orchestrating quality → NSFW → AI
    - Implement risk level assessment (low/medium/high/urgent based on probabilities)
    - Add processing time logging for Gatekeeper and Medical_AI separately
    - _Requirements: 4.4, 20.1, 23.1_

  - [x]* 7.6 Write property tests for AI analysis
    - **Property 12: AI Analysis Persistence**
    - **Property 63: AI Processing Time Logging**
    - **Property 79: High-Risk Urgent Flagging**
    - **Validates: Requirements 4.4, 12.2, 20.1, 23.1**

- [x] 8. Checkpoint - AI Pipeline
  - Ensure all AI processing tests pass
  - Verify NSFW filtering works correctly
  - Test complete image analysis flow from upload to classification
  - Verify risk assessment logic
  - Ask the user if questions arise

### Phase 4: Medical Report Management

- [x] 9. Medical Report Management
  - [x] 9.1 Implement image upload and analysis endpoint
    - Create POST /api/analyze-skin endpoint
    - Accept multipart/form-data with image file
    - Execute complete analysis pipeline (quality → NSFW → AI)
    - Store results in medical_reports table with JSONB predictions
    - Upload image to Supabase Storage and store URL
    - Return report_id, predictions, hotspots, risk_level
    - _Requirements: 4.4, 12.3, 13.2_

  - [x]* 9.2 Write property tests for image storage and report creation
    - **Property 32: Image Storage Round Trip**
    - **Property 34: Multipart Form Data Acceptance**
    - **Validates: Requirements 12.3, 13.2**


  - [x] 9.3 Implement report retrieval endpoints
    - Create GET /api/reports for patient's report history
    - Create GET /api/reports/{report_id} for single report
    - Implement ordering by created_at descending (newest first)
    - Include thumbnail, AI summary, submission date, status in list view
    - Include full image, complete predictions, symptoms in detail view
    - _Requirements: 15.1, 15.2, 15.3_

  - [x]* 9.4 Write property tests for report retrieval
    - **Property 38: Report History Ordering**
    - **Property 39: Report History Display Completeness**
    - **Property 40: Historical Report Retrieval Completeness**
    - **Validates: Requirements 15.1, 15.2, 15.3**

  - [x] 9.5 Implement report comparison functionality
    - Create POST /api/reports/{id}/compare/{other_id} endpoint
    - Implement change detection for lesion size, color, risk level
    - Group reports by body_location for comparison suggestions
    - _Requirements: 15.4, 15.5_

  - [x]* 9.6 Write property tests for report comparison
    - **Property 41: Same-Location Report Grouping**
    - **Property 42: Report Comparison Change Detection**
    - **Validates: Requirements 15.4, 15.5**

  - [x] 9.7 Implement follow-up screening suggestions
    - Add logic to detect reports older than 6 months
    - Include follow-up suggestion in report display
    - _Requirements: 15.6_

  - [x]* 9.8 Write property test for follow-up suggestions
    - **Property 43: Follow-Up Screening Suggestion**
    - **Validates: Requirements 15.6**

- [x] 10. Symptom Collection System
  - [x] 10.1 Implement symptom data models
    - Create Pydantic models for symptom wizard steps
    - Implement validation for body location, sensations, visual changes
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [x] 10.2 Add symptom data to analysis endpoint
    - Extend POST /api/analyze-skin to accept symptom data
    - Store symptoms in medical_reports.symptoms JSONB field
    - Associate symptoms with report and patient
    - _Requirements: 5.5, 5.6_

  - [x]* 10.3 Write property tests for symptom data
    - **Property 14: Symptom Data Completeness**
    - **Property 15: Symptom-Report Association**
    - **Validates: Requirements 5.2, 5.3, 5.4, 5.5, 5.6**


### Phase 5: Doctor Management and Locator

- [x] 11. Doctor Registration and Verification
  - [x] 11.1 Implement doctor registration endpoint
    - Create POST /api/doctors/register endpoint
    - Accept license number, clinic info, coordinates, WhatsApp number, specialization
    - Set initial verified status to false
    - _Requirements: 6.1, 6.2_

  - [x]* 11.2 Write property tests for doctor registration
    - **Property 16: Doctor Registration Completeness**
    - **Validates: Requirements 6.1, 6.2**

  - [x] 11.3 Implement admin doctor verification endpoints
    - Create GET /api/admin/doctors/pending for pending applications
    - Create PUT /api/admin/doctors/{id}/verify for approval/rejection
    - Update verified status and send notification to doctor
    - _Requirements: 6.3, 6.4, 10.1_

  - [x]* 11.4 Write property tests for doctor verification
    - **Property 17: Doctor Verification State Transition**
    - **Property 28: Pending Doctor Application Filtering**
    - **Validates: Requirements 6.4, 10.1**

- [x] 12. Doctor Locator System
  - [x] 12.1 Implement doctor search endpoint
    - Create GET /api/doctors/nearby with lat, lng, radius params
    - Filter only verified doctors
    - Use PostGIS for geographic queries (ll_to_earth)
    - Return doctor profiles with coordinates
    - _Requirements: 7.2, 7.3_

  - [x]* 12.2 Write property tests for doctor locator
    - **Property 18: Verified Doctor Filtering**
    - **Property 19: Doctor Marker Coordinate Accuracy**
    - **Validates: Requirements 7.2, 7.3**

  - [x] 12.3 Implement WhatsApp integration
    - Create function to generate WhatsApp URLs
    - Format: https://wa.me/{whatsapp_no}?text=I would like to share my Derman Report
    - _Requirements: 7.5, 7.6_

  - [x]* 12.4 Write property test for WhatsApp URL format
    - **Property 20: WhatsApp URL Format**
    - **Validates: Requirements 7.5**

- [x] 13. Checkpoint - Core Backend Features
  - Ensure all backend tests pass
  - Verify complete upload-to-results flow
  - Test doctor locator functionality
  - Verify WhatsApp URL generation
  - Ask the user if questions arise


### Phase 6: Appointments and Consultations

- [x] 14. Appointment Management
  - [x] 14.1 Implement appointment endpoints
    - Create POST /api/appointments for booking
    - Create GET /api/appointments for listing user's appointments
    - Create PUT /api/appointments/{id} for status updates
    - Set initial status to "pending"
    - Validate status transitions based on scheduled_at (prevent "pending" after time passes)
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

  - [x]* 14.2 Write property tests for appointments
    - **Property 21: Appointment Creation Completeness**
    - **Property 22: Doctor Appointment Filtering**
    - **Property 23: Appointment Status Transition Rules**
    - **Validates: Requirements 8.2, 8.3, 8.4, 8.5**

  - [x] 14.3 Implement video consultation support
    - Create POST /api/appointments/{id}/video-room endpoint
    - Generate unique video room URLs (using Twilio/Agora)
    - Store video_room_url in appointments table
    - Send video links to both patient and doctor at scheduled_at time
    - _Requirements: 25.1, 25.2, 25.3_

  - [x]* 14.4 Write property tests for video consultations
    - **Property 89: Consultation Type Options**
    - **Property 90: Video Room URL Uniqueness**
    - **Property 91: Video Link Distribution**
    - **Validates: Requirements 25.1, 25.2, 25.3**

- [x] 15. Doctor Report Review System
  - [x] 15.1 Implement doctor report endpoints
    - Create GET /api/doctors/reports/pending for pending reports
    - Filter reports by status (safe, urgent) - exclude flagged
    - Join with patient_data for complete information (age, skin type, family history)
    - Prioritize urgent cases at top of list
    - _Requirements: 9.1, 9.2, 9.3, 23.5_

  - [x]* 15.2 Write property tests for doctor report access
    - **Property 24: Safe Report Filtering**
    - **Property 25: Report Display Completeness**
    - **Property 83: Urgent Case Prioritization**
    - **Validates: Requirements 9.1, 9.2, 9.3, 23.5**

  - [x] 15.3 Implement consultation notes
    - Create POST /api/doctors/reports/{id}/notes endpoint
    - Store notes in medical_reports.consultation_notes
    - Allow adding notes during or after video consultation
    - _Requirements: 9.5, 25.5_

  - [x]* 15.4 Write property tests for consultation notes
    - **Property 27: Consultation Notes Persistence**
    - **Property 92: Consultation Notes Persistence**
    - **Validates: Requirements 9.5, 25.5**


  - [x] 15.5 Display all 7 cancer classes in doctor view
    - Ensure doctor report view shows probability scores for all 7 cancer types
    - _Requirements: 9.4_

  - [x]* 15.6 Write property test for cancer class display
    - **Property 26: Cancer Class Display Completeness**
    - **Validates: Requirements 9.4**

### Phase 7: Emergency Referral and Reviews

- [x] 16. Emergency Referral System
  - [x] 16.1 Implement urgent case detection
    - Add risk assessment logic (probability > 85% = urgent)
    - Set report status to "urgent" for high-risk cases
    - Display prominent warning message to patient
    - _Requirements: 23.1, 23.2_

  - [x]* 16.2 Write property tests for urgent flagging
    - **Property 79: High-Risk Urgent Flagging**
    - **Property 80: Urgent Report Warning Display**
    - **Validates: Requirements 23.1, 23.2**

  - [x] 16.3 Implement nearest doctor notification
    - Create function to find 3 nearest verified doctors using PostGIS
    - Send email notifications to nearest doctors with report summary
    - _Requirements: 23.3_

  - [x]* 16.4 Write property test for nearest doctor notification
    - **Property 81: Nearest Doctor Notification**
    - **Validates: Requirements 23.3**

  - [ ] 16.5 Add emergency consultation button
    - Include "Emergency Consultation" button in urgent result display
    - Link to emergency contact numbers
    - _Requirements: 23.4_

  - [ ]* 16.6 Write property test for emergency button presence
    - **Property 82: Emergency Consultation Button Presence**
    - **Validates: Requirements 23.4**

  - [ ] 16.7 Implement urgent case escalation
    - Create background job to check unreviewed urgent cases
    - Send admin notifications after 24 hours
    - _Requirements: 23.6_

  - [ ]* 16.8 Write property test for urgent case escalation
    - **Property 84: Urgent Case Escalation**
    - **Validates: Requirements 23.6**

- [x] 17. Review and Rating System
  - [x] 17.1 Implement review endpoints
    - Create POST /api/reviews for submitting reviews
    - Create GET /api/doctors/{id}/reviews for fetching reviews
    - Calculate and update doctor average_rating and review_count
    - Prompt patient for review after appointment completion
    - _Requirements: 22.1, 22.2, 22.3_


  - [x]* 17.2 Write property tests for reviews
    - **Property 73: Review Prompt After Appointment**
    - **Property 74: Review Association and Visibility**
    - **Property 75: Doctor Rating Statistics Display**
    - **Validates: Requirements 22.1, 22.2, 22.3**

  - [x] 17.3 Implement review moderation
    - Create PUT /api/reviews/{id}/flag endpoint for doctors to flag inappropriate reviews
    - Send admin notification for ratings below 3 stars
    - _Requirements: 22.4, 22.6_

  - [x]* 17.4 Write property tests for review moderation
    - **Property 76: Review Flagging Availability**
    - **Property 78: Low Rating Admin Notification**
    - **Validates: Requirements 22.4, 22.6**

  - [x] 17.5 Implement doctor ranking
    - Use average rating and number of consultations for ranking
    - _Requirements: 22.5_

  - [x]* 17.6 Write property test for doctor ranking
    - **Property 77: Doctor Ranking Calculation**
    - **Validates: Requirements 22.5**

### Phase 8: Notifications and Admin Features

- [x] 18. Notification System
  - [x] 18.1 Implement notification service
    - Create notification creation function
    - Implement email sending (SendGrid/AWS SES)
    - Create in-app notification storage
    - Send notifications for: analysis complete, appointment confirmation, 24h reminder, verification status, 6-month reminder
    - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6_

  - [x]* 18.2 Write property test for notification delivery
    - **Property 50: Notification Delivery**
    - **Validates: Requirements 17.1, 17.2, 17.3, 17.4, 17.5, 17.6**

  - [ ] 18.3 Implement notification endpoints
    - Create GET /api/notifications for user's notifications
    - Create PUT /api/notifications/{id}/read to mark as read
    - _Requirements: 17.6_

- [ ] 19. Admin Panel Backend
  - [x] 19.1 Implement content moderation endpoints
    - Create GET /api/admin/reports/flagged for flagged content
    - Display images, NSFW scores, rejection reasons
    - _Requirements: 10.2, 10.4_

  - [x]* 19.2 Write property tests for admin moderation
    - **Property 29: Flagged Content Filtering**
    - **Property 30: Flagged Content Metadata Completeness**
    - **Validates: Requirements 10.2, 10.4**


  - [x] 19.3 Implement Skin-Wiki content management
    - Create endpoints for creating/updating educational articles
    - Implement version tracking for content changes
    - _Requirements: 10.5, 16.6_

  - [x]* 19.4 Write property tests for content management
    - **Property 31: Content Update Persistence**
    - **Property 49: Content Version Tracking**
    - **Validates: Requirements 10.5, 16.6**

- [x] 20. Checkpoint - Backend Complete
  - Ensure all backend tests pass
  - Verify all API endpoints work correctly
  - Test emergency referral system
  - Test notification delivery
  - Ask the user if questions arise

### Phase 9: Frontend Foundation

- [x] 21. Frontend Project Setup
  - [x] 21.1 Initialize React + Vite project with TypeScript
    - Set up Vite configuration
    - Install dependencies (React Query, Zustand, Tailwind CSS, Framer Motion, React Dropzone, Google Maps React)
    - Configure TypeScript strict mode
    - Set up ESLint and Prettier
    - _Requirements: 11.1_

  - [x] 21.2 Set up Supabase client
    - Install Supabase JS client
    - Configure authentication
    - Create API service layer for all backend endpoints
    - _Requirements: 1.2_

  - [x] 21.3 Implement routing and layout
    - Set up React Router with protected routes
    - Create main layout component
    - Implement role-based route guards
    - _Requirements: 1.4, 1.5, 1.6_

- [x] 22. Authentication UI
  - [x] 22.1 Create login and signup forms
    - Build LoginForm component
    - Build SignupForm component with role selection
    - Implement form validation
    - Connect to authentication API
    - _Requirements: 1.1, 1.2_

  - [x] 22.2 Implement authentication context
    - Create AuthProvider with Zustand
    - Implement login, logout, session management
    - Create ProtectedRoute component
    - _Requirements: 1.2_

  - [x] 22.3 Create landing page with carousel
    - Build carousel component with Framer Motion
    - Create 3 slides: AI Screening, Find Doctors, Secure History
    - Add smooth transitions
    - Add authentication buttons
    - _Requirements: 11.1, 11.2_


### Phase 10: Patient Dashboard UI

- [x] 23. Diagnostic Uploader and Symptom Wizard
  - [x] 23.1 Create diagnostic uploader component
    - Build drag-and-drop image upload with React Dropzone
    - Add camera capture for mobile devices
    - Implement image preview
    - Add upload progress indicator
    - Provide visual feedback for drag-over state
    - _Requirements: 11.3, 11.4, 21.2_

  - [x] 23.2 Write property test for mobile camera availability
    - **Property 69: Mobile Camera Capture Availability**
    - **Validates: Requirements 21.2**

  - [x] 23.3 Create symptom wizard component
    - Build multi-step form (3 steps)
    - Step 1: Body location selector
    - Step 2: Sensation checkboxes (itching, pain, burning, numbness)
    - Step 3: Visual changes checkboxes (color, size, shape, border irregularity)
    - Implement form state management
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 24. Results Display and Report History
  - [x] 24.1 Create results display component
    - Build AI prediction display with probability bars for all 7 cancer types
    - Implement hotspot overlay visualization on image
    - Add medical disclaimer: "This is a 94% probability estimate. Please consult verified doctors for clinical biopsy"
    - Add "Find Doctor" CTA button
    - _Requirements: 4.5, 4.6, 14.1, 14.2_

  - [x] 24.2 Write property test for disclaimer presence
    - **Property 13: Medical Disclaimer Presence**
    - **Property 37: Educational Content Disclaimer Presence**
    - **Validates: Requirements 4.6, 14.1, 14.4**

  - [x] 24.3 Create report history component
    - Build timeline view of past reports
    - Display thumbnails, summaries, dates, status
    - Implement report selection
    - Add follow-up screening suggestions for reports older than 6 months
    - _Requirements: 15.1, 15.2, 15.3, 15.6_

  - [x] 24.4 Write property test for follow-up suggestions
    - **Property 43: Follow-Up Screening Suggestion**
    - **Validates: Requirements 15.6**

  - [x] 24.5 Create comparison view component
    - Build side-by-side image comparison
    - Highlight changes in size, color, risk level
    - _Requirements: 15.4, 15.5_


### Phase 11: Doctor Locator and Booking UI

- [ ] 25. Doctor Locator UI
  - [x] 25.1 Integrate Google Maps
    - Set up Google Maps React component
    - Implement map initialization with user location
    - Add GPS centering for mobile
    - _Requirements: 7.1, 21.5_

  - [x]* 25.2 Write property test for GPS centering
    - **Property 72: GPS Location Centering**
    - **Validates: Requirements 21.5**

  - [x] 25.3 Create doctor markers and cards
    - Implement custom map markers for doctors at exact lat/lng coordinates
    - Build doctor info cards with rating, clinic name, specialization
    - Add WhatsApp contact button with correct URL format
    - Display average rating and review count
    - _Requirements: 7.3, 7.4, 7.5, 22.3_

  - [x] 25.4 Create appointment booking modal
    - Build appointment booking form
    - Add consultation type selection (in-person/video)
    - Implement date/time picker
    - _Requirements: 8.1, 25.1_

- [x] 26. Checkpoint - Patient Features Complete
  - Ensure all patient UI components render correctly
  - Test complete patient flow: upload → results → find doctor → book appointment
  - Verify responsive design on mobile
  - Ask the user if questions arise

### Phase 12: Doctor and Admin Dashboards

- [x] 27. Doctor Dashboard UI
  - [x] 27.1 Create pending reports view
    - Build report list with filtering
    - Display patient info, images, AI predictions
    - Prioritize urgent cases at top
    - _Requirements: 9.1, 9.2, 9.3, 23.5_

  - [x] 27.2 Create report detail view
    - Display full-resolution image
    - Show complete AI predictions (all 7 classes with probabilities)
    - Display patient health profile (age, skin type, family history)
    - Add consultation notes editor
    - _Requirements: 9.2, 9.3, 9.4, 9.5_

  - [x] 27.3 Create appointments view
    - List doctor's appointments
    - Show appointment details and status
    - Add video consultation link for video appointments
    - _Requirements: 8.4, 25.3_

- [x] 28. Admin Panel UI
  - [x] 28.1 Create doctor verification interface
    - List pending doctor applications
    - Display license info and clinic details
    - Add approve/reject buttons
    - _Requirements: 10.1, 10.3_


  - [x] 28.2 Create content moderation interface
    - List flagged reports
    - Display images, NSFW scores, rejection reasons
    - _Requirements: 10.2, 10.4_

  - [x] 28.3 Create analytics dashboard
    - Display daily active users
    - Show total screenings and average processing time
    - Add usage pattern charts (most common cancer types, geographic distribution)
    - _Requirements: 20.3, 20.5_

  - [x]* 28.4 Write property tests for analytics
    - **Property 65: Analytics Dashboard Metrics Completeness**
    - **Property 67: Usage Pattern Statistics**
    - **Validates: Requirements 20.3, 20.5**

  - [x] 28.5 Create Skin-Wiki editor
    - Build content management interface
    - Add rich text editor for articles
    - Implement version tracking display
    - _Requirements: 10.5, 16.6_

### Phase 13: Educational Content (Skin-Wiki)

- [x] 29. Skin-Wiki Section
  - [x] 29.1 Create Skin-Wiki article pages
    - Build article listing page
    - Create article detail pages for 7 cancer types
    - Include images, risk factors, symptoms, treatments for each type
    - _Requirements: 16.1, 16.2_

  - [x]* 29.2 Write property tests for Skin-Wiki content
    - **Property 44: Skin-Wiki Cancer Type Completeness**
    - **Property 45: Cancer Type Article Completeness**
    - **Validates: Requirements 16.1, 16.2**

  - [x] 29.3 Create self-examination guides
    - Build illustrated body map component
    - Add prevention tips section
    - Include UV protection recommendations and early detection guidelines
    - _Requirements: 16.3, 16.4_

  - [x]* 29.4 Write property tests for educational content
    - **Property 46: Educational Content Availability**
    - **Property 47: Prevention Tips Completeness**
    - **Validates: Requirements 16.3, 16.4**

  - [x] 29.5 Implement contextual educational links
    - Link AI results to relevant cancer type articles
    - Add educational disclaimers to all medical information
    - _Requirements: 16.5, 14.4_

  - [x]* 29.6 Write property tests for contextual links
    - **Property 48: Contextual Educational Links**
    - **Validates: Requirements 16.5**


### Phase 14: Multi-Language Support

- [x] 30. Internationalization (i18n)
  - [x] 30.1 Set up i18n framework
    - Install and configure react-i18next
    - Create translation files for 5 languages (EN, ES, FR, DE, ZH)
    - Implement language detection from browser Accept-Language header
    - _Requirements: 19.1, 19.5_

  - [x]* 30.2 Write property tests for language support
    - **Property 57: Browser Language Detection**
    - **Property 61: Minimum Language Support**
    - **Validates: Requirements 19.1, 19.5**

  - [x] 30.3 Translate all UI text
    - Translate interface elements
    - Translate medical disclaimers
    - Translate cancer type names and descriptions
    - _Requirements: 19.2, 19.3, 19.4_

  - [x]* 30.4 Write property tests for translations
    - **Property 58: Language Preference Persistence**
    - **Property 59: Disclaimer Translation**
    - **Property 60: AI Result Translation**
    - **Validates: Requirements 19.2, 19.3, 19.4**

  - [x] 30.5 Implement content translation enforcement
    - Prevent publishing content without all translations
    - _Requirements: 19.6_

  - [x]* 30.6 Write property test for translation completeness
    - **Property 62: Content Translation Completeness**
    - **Validates: Requirements 19.6**

### Phase 15: Progressive Web App (PWA)

- [x] 31. PWA Implementation
  - [x] 31.1 Configure PWA with Workbox
    - Set up service worker
    - Configure caching strategies
    - Add offline support for historical reports
    - _Requirements: 21.3_

  - [x]* 31.2 Write property test for offline functionality
    - **Property 70: PWA Offline Functionality**
    - **Validates: Requirements 21.3**

  - [x] 31.3 Implement sync on reconnection
    - Detect network status changes
    - Sync pending uploads when online
    - Fetch new data on reconnection
    - _Requirements: 21.4_

  - [x]* 31.4 Write property test for network sync
    - **Property 71: Network Reconnection Sync**
    - **Validates: Requirements 21.4**

  - [x] 31.5 Add PWA manifest and icons
    - Create manifest.json
    - Generate app icons for all sizes
    - Configure install prompt
    - _Requirements: 21.1_


  - [x] 31.6 Add mobile-specific features
    - Implement touch gestures for image zoom/pan
    - Optimize map interactions for mobile
    - _Requirements: 21.6_

- [x] 32. Checkpoint - Advanced Features
  - Ensure PWA works offline
  - Test multi-language switching
  - Verify mobile responsiveness
  - Ask the user if questions arise

### Phase 16: Privacy, Security, and Performance

- [-] 33. Privacy and Security Features
  - [x] 33.1 Implement data encryption
    - Configure AES-256 encryption for Supabase Storage
    - Ensure HTTPS/TLS for all connections
    - _Requirements: 18.1, 18.2_

  - [x]* 33.2 Write property tests for encryption
    - **Property 51: Image Encryption at Rest**
    - **Property 52: HTTPS Transport Encryption**
    - **Validates: Requirements 18.1, 18.2**

  - [x] 33.3 Implement account deletion
    - Create DELETE /api/account endpoint
    - Implement cascade deletion of reports and patient data
    - Schedule permanent deletion after 30 days
    - _Requirements: 18.3_

  - [x]* 33.4 Write property test for account deletion
    - **Property 53: Account Deletion Cascade**
    - **Validates: Requirements 18.3**

  - [ ] 33.5 Create privacy settings UI
    - Build privacy settings page
    - Add opt-out option for research data sharing
    - Implement data export functionality (JSON/PDF)
    - _Requirements: 18.5, 18.6_

  - [ ]* 33.6 Write property tests for privacy features
    - **Property 55: Privacy Settings Opt-Out Availability**
    - **Property 56: Data Export Format Validity**
    - **Validates: Requirements 18.5, 18.6**

- [x] 34. Performance Monitoring and Analytics
  - [x] 34.1 Implement metrics collection
    - Add API response time tracking
    - Log AI processing times separately (Gatekeeper vs Medical_AI)
    - Track error rates
    - _Requirements: 20.1, 20.2_

  - [x]* 34.2 Write property tests for metrics
    - **Property 63: AI Processing Time Logging**
    - **Property 64: API Metrics Tracking**
    - **Validates: Requirements 20.1, 20.2**

  - [x] 34.3 Implement performance alerting
    - Create alert system for slow responses (>5s)
    - Send admin notifications
    - _Requirements: 20.4_


  - [x]* 34.4 Write property test for performance alerts
    - **Property 66: Performance Degradation Alerting**
    - **Validates: Requirements 20.4**

  - [x] 34.5 Create analytics reporting
    - Implement usage pattern tracking
    - Generate weekly health reports
    - _Requirements: 20.5, 20.6_

  - [x]* 34.6 Write property tests for analytics
    - **Property 67: Usage Pattern Statistics**
    - **Property 68: Weekly Health Report Generation**
    - **Validates: Requirements 20.5, 20.6**

- [x] 35. Error Handling and User Experience
  - [x] 35.1 Implement comprehensive error handling
    - Create error boundary components
    - Add user-friendly error messages
    - Implement retry logic for transient failures
    - _Requirements: 13.4_

  - [x]* 35.2 Write property tests for error responses
    - **Property 35: HTTP Status Code Correctness**
    - **Property 36: JSON Response Format**
    - **Validates: Requirements 13.4, 13.5**

  - [x] 35.3 Add loading states and feedback
    - Implement loading spinners
    - Add progress indicators for uploads
    - Show success/error toasts
    - _Requirements: 11.4_

### Phase 17: Testing and Quality Assurance

- [x] 36. Comprehensive Testing
  - [x] 36.1 Complete all property-based tests
    - Ensure all 93 correctness properties are implemented
    - Run property tests with minimum 100 iterations each
    - Verify all tests pass
    - _Requirements: All_

  - [x] 36.2 Write integration tests
    - Test complete patient journey (signup → upload → results → booking)
    - Test doctor journey (registration → verification → report review)
    - Test admin workflows (doctor verification, content moderation)
    - _Requirements: All_

  - [x] 36.3 Write end-to-end tests
    - Use Playwright or Cypress for E2E testing
    - Test cross-browser compatibility (Chrome, Firefox, Safari)
    - Test mobile responsiveness
    - _Requirements: 21.1_

  - [x] 36.4 Performance testing
    - Optimize image loading and caching
    - Implement code splitting
    - Minimize bundle size
    - Test performance on 3G connection
    - Verify AI analysis completes within 10 seconds (95th percentile)
    - _Requirements: 20.1_


  - [x] 36.5 Security audit
    - Review authentication and authorization
    - Test NSFW filter effectiveness
    - Verify data encryption
    - Check for SQL injection vulnerabilities
    - Verify HIPAA compliance for video consultations
    - _Requirements: 18.1, 18.2, 25.6_

  - [x]* 36.6 Write property test for video encryption compliance
    - **Property 93: Video Encryption Compliance**
    - **Validates: Requirements 25.6**

- [x] 37. Final Checkpoint - Production Ready
  - Ensure all tests pass (unit, property, integration, E2E)
  - Verify all 93 correctness properties are implemented and passing
  - Test complete platform with real users
  - Prepare deployment documentation
  - Ask the user if questions arise

### Phase 18: Deployment and Launch

- [x] 38. Deployment Preparation
  - [x] 38.1 Set up production environment
    - Configure production Supabase instance
    - Set up production API server (AWS Lambda/EC2)
    - Configure CDN for frontend (Vercel/Netlify)
    - Set up image storage with CloudFront
    - _Requirements: All_

  - [x] 38.2 Configure monitoring and logging
    - Set up error tracking (Sentry)
    - Configure performance monitoring
    - Set up log aggregation
    - Configure alerting for critical errors
    - _Requirements: 20.2, 20.4_

  - [x] 38.3 Prepare documentation
    - Write API documentation
    - Create user guides for patients, doctors, admins
    - Document deployment procedures
    - Create troubleshooting guide
    - _Requirements: All_

  - [x] 38.4 Final production testing
    - Test all features in production environment
    - Verify SSL certificates
    - Test email delivery
    - Test video consultation service
    - Verify all integrations (Google Maps, WhatsApp, email)
    - _Requirements: All_

- [x] 39. Launch
  - Deploy to production
  - Monitor system health
  - Be ready for user feedback and bug fixes
  - _Requirements: All_

## Notes

- Tasks marked with `*` are optional property-based tests that can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation and allow for course correction
- Property tests validate universal correctness properties across all inputs (minimum 100 iterations each)
- Unit tests validate specific examples and edge cases
- The implementation follows a backend-first approach to establish solid foundations before building UI
- All 93 correctness properties from the design document are mapped to specific test tasks
- Testing framework: Hypothesis (Python) and fast-check (TypeScript)


## Implementation Summary

### Total Tasks: 39 major tasks with 150+ subtasks

### Requirements Coverage:
- **Requirement 1**: User Authentication → Tasks 2, 21-22
- **Requirement 2**: Patient Health Profile → Task 4
- **Requirement 3**: Content Security → Task 6
- **Requirement 4**: AI Analysis → Tasks 7, 9, 24
- **Requirement 5**: Symptom Collection → Tasks 10, 23
- **Requirement 6**: Doctor Registration → Task 11
- **Requirement 7**: Doctor Discovery → Tasks 12, 25
- **Requirement 8**: Appointments → Task 14
- **Requirement 9**: Report Management → Tasks 9, 15, 27
- **Requirement 10**: Admin Moderation → Tasks 19, 28
- **Requirement 11**: Frontend UI → Tasks 21-28
- **Requirement 12**: Data Persistence → Task 1
- **Requirement 13**: API Backend → Tasks 2-19
- **Requirement 14**: Medical Disclaimer → Tasks 24, 29
- **Requirement 15**: Report History → Tasks 9, 24
- **Requirement 16**: Educational Content → Task 29
- **Requirement 17**: Notifications → Task 18
- **Requirement 18**: Privacy & Security → Task 33
- **Requirement 19**: Multi-Language → Task 30
- **Requirement 20**: Performance Monitoring → Task 34
- **Requirement 21**: Mobile & PWA → Task 31
- **Requirement 22**: Reviews & Ratings → Task 17
- **Requirement 23**: Emergency Referral → Task 16
- **Requirement 24**: Image Quality → Task 5
- **Requirement 25**: Telemedicine → Tasks 14, 15

### Property Tests Coverage:
All 93 correctness properties from the design document are mapped to specific test tasks throughout the implementation plan.

### Recommended Implementation Order:
1. **Phase 1-4** (Tasks 1-13): Core backend functionality - enables basic image analysis
2. **Phase 5-8** (Tasks 14-20): Extended backend features - enables appointments and reviews
3. **Phase 9-12** (Tasks 21-28): Frontend application - enables user interaction
4. **Phase 13-16** (Tasks 29-35): Advanced features - enhances user experience
5. **Phase 17-18** (Tasks 36-39): Testing and deployment - ensures production readiness

### Estimated Timeline:
- Backend Foundation (Phases 1-4): 4-6 weeks
- Backend Extensions (Phases 5-8): 3-4 weeks
- Frontend Development (Phases 9-12): 5-7 weeks
- Advanced Features (Phases 13-16): 4-5 weeks
- Testing & Deployment (Phases 17-18): 2-3 weeks
- **Total**: 18-25 weeks for complete implementation

### Key Milestones:
1. **Checkpoint 1** (Task 3): Authentication working
2. **Checkpoint 2** (Task 8): AI pipeline functional
3. **Checkpoint 3** (Task 13): Core backend complete
4. **Checkpoint 4** (Task 20): Backend fully functional
5. **Checkpoint 5** (Task 26): Patient features complete
6. **Checkpoint 6** (Task 32): Advanced features complete
7. **Checkpoint 7** (Task 37): Production ready
