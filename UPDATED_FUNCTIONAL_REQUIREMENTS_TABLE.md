# Table 4.1 - Functional Requirements of SkinGuard Web Application (Updated)

## Authentication & Account Management

| ID | Use Case | Actor | Functional Requirements |
|----|----------|-------|------------------------|
| UC001 | Patient Login | Patient | This use case enables patients to access the system by authenticating with their email and password. The system validates credentials against the database and creates an authenticated session with JWT token. |
| UC002 | Hospital/Clinic Staff Login | Hospital Staff | This use case enables hospital/clinic staff (doctors/dermatologists) to access the system by authenticating with their credentials. Upon successful login, staff can access the hospital dashboard to review reports and manage appointments. |
| UC003 | Register Patient Account | Patient | This use case allows new users to create a patient account by providing email, password, full name, and role selection. The system validates email uniqueness, encrypts password using bcrypt, and stores user data in the database. |
| UC004 | Forgot Password | Patient/Hospital | If a user forgets their password, this use case enables them to request a password reset link via email. The system generates a secure JWT token, sends it via email, and allows the user to set a new password. |
| UC005 | Logout | Patient/Hospital | This use case allows users to terminate their authenticated session and clear JWT tokens from local storage. |

---

## Patient Health Profile Management

| ID | Use Case | Actor | Functional Requirements |
|----|----------|-------|------------------------|
| UC006 | Create Health Profile | Patient | This use case allows patients to create their initial health profile by providing age (1-120 years), Fitzpatrick skin type (I-VI), and family history of skin conditions. The system validates input and stores data in the patient_data table. |
| UC007 | Update Health Profile | Patient | This use case enables patients to modify their existing health profile information. The system validates changes and updates the patient_data table with new information and timestamp. |
| UC008 | View Health Profile | Patient | This use case allows patients to view their current health profile including age, skin type, family history, and profile creation/update dates. |

---

## Image Upload & AI Analysis

| ID | Use Case | Actor | Functional Requirements |
|----|----------|-------|------------------------|
| UC009 | Upload Skin Lesion Image | Patient | This use case allows patients to upload a photograph of their skin lesion. The system validates file type (JPEG/PNG), file size (max 10MB), and stores the image securely. The upload triggers the AI analysis pipeline automatically. |
| UC010 | Complete Symptom Wizard | Patient | This use case guides patients through a 3-step wizard to record symptoms:<br>• Step 1: Select body location (arm, leg, face, torso, etc.)<br>• Step 2: Select sensations (itching, pain, burning, numbness, tingling, none)<br>• Step 3: Select visual changes (color, size, shape, border, texture, bleeding, none)<br>• Optional: Enter symptom duration<br>The system stores symptom data as JSONB in medical_reports table. |
| UC011 | Validate Image Quality | AI System | This automated use case checks uploaded images for minimum quality standards:<br>• Resolution ≥ 300x300 pixels<br>• Blur score within acceptable range<br>• Brightness within acceptable range<br>If validation fails, the system rejects the image with specific error message. |
| UC012 | Validate Skin Content | AI System | This automated use case verifies that uploaded images contain skin lesions (not posters, text, or other objects). The system:<br>• Calculates skin-like pixel percentage using color analysis<br>• Detects text/graphics patterns using edge detection<br>• Requires ≥25% skin content<br>• Rejects images with text or high-contrast graphics<br>If validation fails, system returns user-friendly error message. |
| UC013 | Detect Lesion Hotspots | AI System | This automated use case identifies and localizes skin lesions within the validated image using Swin Transformer object detection model. The system generates bounding boxes with confidence scores for detected lesions. |
| UC014 | Classify Cancer Type | AI System | This automated use case classifies the detected lesion into one of 7 cancer types using Vision Transformer (ViT) model:<br>1. Melanoma<br>2. Basal Cell Carcinoma<br>3. Actinic Keratoses<br>4. Benign Keratosis-Like Lesions<br>5. Dermatofibroma<br>6. Vascular Lesions<br>7. Melanocytic Nevi<br>The model (Anwarkh1/Skin_Cancer-Image_Classification) provides probability scores for each type with 84% accuracy on HAM10000 dataset. |
| UC015 | Assess Risk Level | AI System | This automated use case categorizes the analysis into risk levels based on cancer probability:<br>• **Low**: <20% malignancy probability (routine monitoring)<br>• **Medium**: 20-50% probability (schedule consultation)<br>• **High**: 50-80% probability (urgent consultation needed)<br>• **Urgent**: >80% probability (immediate medical attention)<br>Risk level determines report priority for hospital staff. |
| UC016 | Generate Medical Report | AI System | This automated use case creates a structured medical report containing:<br>• AI predictions with probabilities for all 7 cancer types<br>• Risk level classification<br>• Lesion hotspot locations<br>• Symptom data from wizard<br>• Image with annotations<br>• Quality metrics<br>• Processing timestamps<br>• Medical disclaimer<br>Report is stored in medical_reports table with unique ID. |
| UC017 | View Analysis Results | Patient | This use case displays the AI analysis results to the patient, including:<br>• Top prediction with confidence percentage<br>• All 7 predictions with probability bars<br>• Risk level with color coding (green/yellow/orange/red)<br>• Disclaimer about AI screening vs clinical diagnosis<br>• Recommendation to consult dermatologist |
| UC018 | View Medical Report History | Patient | This use case allows patients to access all their past skin analysis reports. The system displays reports sorted by date (newest first) with filters for risk level. Patients can view full details or download reports as PDF. |

---

## Hospital Finder & Appointments

| ID | Use Case | Actor | Functional Requirements |
|----|----------|-------|------------------------|
| UC019 | Find Nearby Hospitals | Patient | This use case enables patients to search for dermatology hospitals and clinics near their location. The system:<br>• Uses patient's GPS location or manual address input<br>• Searches via Google Maps Places API within 50km radius<br>• Implements 3-tier search strategy:<br>&nbsp;&nbsp;1. Dermatology specialists (keyword: "dermatology skin")<br>&nbsp;&nbsp;2. Dermatology clinics (keyword: "dermatology skin clinic")<br>&nbsp;&nbsp;3. General hospitals (for emergency cases)<br>• Returns up to 180 results (60 per search tier)<br>• Sorts results: High-rated (≥4.5 stars) first, then by distance |
| UC020 | View Hospital Details | Patient | This use case displays detailed information about a selected hospital including:<br>• Hospital name and address<br>• Google Maps rating and review count<br>• Distance from patient location<br>• Operating hours<br>• Direct link to Google Maps for navigation<br>• "View on Maps" button for directions |
| UC021 | Calculate Distance | Google Maps API | This automated use case calculates the distance between patient location and each hospital using Haversine formula (GPS coordinates). Results are displayed in kilometers. |
| UC022 | Book Appointment | Patient | This use case allows patients to request appointments with hospitals for consultation. The patient:<br>• Selects a medical report to share with hospital<br>• Chooses preferred date and time<br>• Adds optional notes for the hospital<br>The system creates appointment record with status "pending" and sends notification to hospital. Patient identity remains hidden until hospital confirms. |
| UC023 | Manage Patient Appointments | Patient | This use case enables patients to view and manage all their appointments:<br>• View appointment list filtered by status (pending/confirmed/completed/cancelled)<br>• View appointment details (hospital, date, time, status)<br>• Cancel pending or confirmed appointments<br>• View consultation notes (if available) for completed appointments |

---

## Hospital Dashboard - Report Review

| ID | Use Case | Actor | Functional Requirements |
|----|----------|-------|------------------------|
| UC024 | Manage Facility Profile | Hospital Staff | This use case allows hospital/clinic staff to update their facility information:<br>• Hospital/Clinic name<br>• Facility description<br>• Operating hours<br>• Contact information (phone, email, address)<br>• Specialties and services offered<br>The system validates input and updates the doctor_profile table. |
| UC025 | View Pending Reports (Grouped by Patient) | Hospital Staff | This use case displays all medical reports awaiting review, organized by patient:<br>• Reports grouped by patient_id<br>• Each patient section is collapsible<br>• Shows patient count and report count per patient<br>• Displays "HAS URGENT CASES" badge for patients with urgent reports<br>• All sections collapsed by default (click to expand)<br>• **Privacy Protection**: Patient names shown as "Unknown Patient" for reports without confirmed appointments |
| UC026 | View Report Details | Hospital Staff | This use case displays full details of a selected medical report:<br>• Patient name (if appointment confirmed)<br>• Skin lesion image with hotspots<br>• AI predictions with probabilities<br>• Risk level classification<br>• Symptom data (location, sensations, visual changes, duration)<br>• Analysis timestamp<br>• Quality metrics |
| UC027 | Review Urgent Cases | Hospital Staff | This use case filters and displays only high-priority reports:<br>• Shows reports with risk level = "urgent" or "high"<br>• Sorted by risk level (urgent first) then date (newest first)<br>• Enables doctors to prioritize critical cases<br>• Displays total count of urgent cases |

---

## Hospital Dashboard - Appointment Management

| ID | Use Case | Actor | Functional Requirements |
|----|----------|-------|------------------------|
| UC028 | View Appointment Requests | Hospital Staff | This use case displays all appointment requests with status breakdown:<br>• Pending appointments (awaiting confirmation)<br>• Confirmed appointments (scheduled consultations)<br>• Completed appointments (past consultations)<br>• Shows patient name (hidden if pending), date, time, report preview<br>• Sorted by date (upcoming first) |
| UC029 | Confirm Appointment | Hospital Staff | This use case allows hospital staff to accept patient appointment requests:<br>• Review appointment details and patient report<br>• Click "Confirm" to accept<br>• System updates appointment status to "confirmed"<br>• **Privacy Unlock**: Patient identity and full medical history now visible<br>• Sends confirmation email to patient via Email System<br>• Enables doctor to view patient health profile |
| UC030 | Reject/Cancel Appointment | Hospital Staff | This use case enables hospital staff to decline or cancel appointments:<br>• Provide optional reason for cancellation<br>• System updates appointment status to "cancelled"<br>• Sends cancellation email to patient via Email System<br>• Patient can request new appointment if needed |
| UC031 | View Patient Health Profile | Hospital Staff | This use case allows doctors to access complete patient medical history (only after appointment confirmation):<br>• Patient demographics (name, age, email)<br>• Fitzpatrick skin type<br>• Family history of skin conditions<br>• All past medical reports (last 10 analyses)<br>• Report details: date, location, risk level, AI predictions<br>• **Privacy Protection**: Only accessible for patients with confirmed appointments |
| UC032 | Mark Appointment Complete | Hospital Staff | This use case allows doctors to mark consultations as completed:<br>• Add optional consultation notes<br>• Update appointment status to "completed"<br>• Notes visible to patient in their appointment history<br>• Report moves from "pending" to "reviewed" status |

---

## External System Integrations

| ID | Use Case | Actor | Functional Requirements |
|----|----------|-------|------------------------|
| UC033 | Search Hospitals via Google Maps | Google Maps API | This automated use case queries Google Maps Places API to find hospitals:<br>• Accepts patient location (latitude, longitude) and radius<br>• Searches for dermatology-related businesses<br>• Returns hospital data: name, address, rating, coordinates, place_id<br>• Supports pagination (up to 60 results per search)<br>• Filters results by rating and distance |
| UC034 | Generate Navigation Link | Google Maps API | This automated use case creates direct navigation links:<br>• Accepts hospital coordinates<br>• Generates deep link URL to Google Maps<br>• Opens in Google Maps app (mobile) or website (desktop)<br>• Provides turn-by-turn directions from patient location |
| UC035 | Send Appointment Confirmation Email | Email System | This automated use case sends email notifications when appointments are confirmed:<br>• Recipient: Patient email address<br>• Subject: "Appointment Confirmed with [Hospital Name]"<br>• Content: Hospital name, date, time, location, preparation instructions<br>• Triggered by hospital staff confirming appointment |
| UC036 | Send Appointment Cancellation Email | Email System | This automated use case sends email notifications when appointments are cancelled:<br>• Recipient: Patient email address<br>• Subject: "Appointment Cancelled - [Hospital Name]"<br>• Content: Cancellation reason (if provided), next steps, rebooking instructions<br>• Triggered by hospital or patient cancelling appointment |
| UC037 | Send Password Reset Email | Email System | This automated use case sends secure password reset links:<br>• Triggered by "Forgot Password" action<br>• Contains time-limited JWT token (valid 1 hour)<br>• Includes reset link to password change form<br>• Verifies email ownership before allowing password reset |

---

## Summary Statistics

### **Total Use Cases**: 37
### **By Actor**:
- **Patient**: 13 use cases
- **Hospital/Clinic Staff**: 9 use cases
- **AI System**: 8 use cases (automated)
- **Google Maps API**: 3 use cases (automated)
- **Email System**: 3 use cases (automated)
- **Shared (Patient & Hospital)**: 1 use case (Login)

### **Key Changes from Old Table**:
1. ❌ **Removed**: Admin role, Query management (no admin panel in current system)
2. ✅ **Added**: 29 new use cases including:
   - Symptom wizard
   - Skin validation (anti-poster/text detection)
   - Hospital finder with Google Maps
   - Complete appointment workflow
   - Privacy protection system
   - Grouped pending reports
   - Patient health profile access
   - Email notifications
   - Risk-based triage
3. 🔄 **Updated**: "Doctor" → "Hospital/Clinic Staff" (facility-based system)
4. 🔄 **Enhanced**: AI analysis now includes 7 cancer types with 84% accuracy

---

## Notes for Documentation:

1. **Privacy-First Design**: Patient identity hidden until appointment confirmed (UC031)
2. **AI Accuracy**: Vision Transformer model achieves 84% accuracy on HAM10000 dataset
3. **Conservative Bias**: System prioritizes sensitivity over specificity (better to over-predict dangerous cases)
4. **Three-Tier Hospital Search**: Ensures both specialists and general hospitals are available
5. **Smart Triage**: AI automatically prioritizes urgent cases for doctor review
6. **HIPAA-Aligned**: Though not certified, system follows privacy best practices
7. **Technology Stack**: React (frontend) + FastAPI (backend) + PostgreSQL (database)

