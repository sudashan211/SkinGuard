"""
Pydantic models for request/response validation
"""
from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
import uuid


# ============================================================================
# Authentication Models
# ============================================================================

class UserSignupRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=100)
    role: Literal['patient', 'doctor', 'admin'] = 'patient'
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str


# ============================================================================
# User Profile Models
# ============================================================================

class UserProfile(BaseModel):
    """User profile information"""
    id: str
    email: str
    full_name: str
    avatar_url: Optional[str] = None
    role: Literal['patient', 'doctor', 'admin']
    verified: bool = False
    language_preference: str = 'en'
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """User profile update request"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = None
    language_preference: Optional[str] = None


# ============================================================================
# Response Models
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: dict = Field(..., description="Error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "code": "AUTH_ERROR",
                    "message": "Invalid credentials",
                    "details": None,
                    "timestamp": "2024-02-10T12:00:00Z",
                    "request_id": "req_123456"
                }
            }
        }


class SuccessResponse(BaseModel):
    """Standard success response"""
    message: str
    data: Optional[dict] = None


# ============================================================================
# Patient Data Models
# ============================================================================

class PatientDataCreate(BaseModel):
    """Patient data creation request"""
    age: int = Field(..., ge=1, le=120, description="Patient age (1-120)")
    skin_type: Literal['I', 'II', 'III', 'IV', 'V', 'VI'] = Field(..., description="Fitzpatrick skin type scale")
    family_history: Optional[str] = Field(None, description="Family history of skin conditions")
    
    @validator('age')
    def validate_age_range(cls, v):
        """Validate age is within acceptable range"""
        if v < 1 or v > 120:
            raise ValueError('Age must be between 1 and 120')
        return v
    
    @validator('skin_type')
    def validate_skin_type(cls, v):
        """Validate Fitzpatrick scale value"""
        valid_types = ['I', 'II', 'III', 'IV', 'V', 'VI']
        if v not in valid_types:
            raise ValueError(f'Skin type must be one of: {", ".join(valid_types)}')
        return v


class PatientDataUpdate(BaseModel):
    """Patient data update request"""
    age: Optional[int] = Field(None, ge=1, le=120, description="Patient age (1-120)")
    skin_type: Optional[Literal['I', 'II', 'III', 'IV', 'V', 'VI']] = Field(None, description="Fitzpatrick skin type scale")
    family_history: Optional[str] = Field(None, description="Family history of skin conditions")
    
    @validator('age')
    def validate_age_range(cls, v):
        """Validate age is within acceptable range"""
        if v is not None and (v < 1 or v > 120):
            raise ValueError('Age must be between 1 and 120')
        return v
    
    @validator('skin_type')
    def validate_skin_type(cls, v):
        """Validate Fitzpatrick scale value"""
        if v is not None:
            valid_types = ['I', 'II', 'III', 'IV', 'V', 'VI']
            if v not in valid_types:
                raise ValueError(f'Skin type must be one of: {", ".join(valid_types)}')
        return v


class PatientDataResponse(BaseModel):
    """Patient data response"""
    id: str
    user_id: str
    age: int
    skin_type: Literal['I', 'II', 'III', 'IV', 'V', 'VI']
    family_history: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Medical Report Models
# ============================================================================

# Symptom Wizard Step Models (Requirements: 5.1, 5.2, 5.3, 5.4)

class BodyLocation(BaseModel):
    """Step 1: Body location of lesion"""
    location: str = Field(..., description="Location of lesion on body (e.g., 'left_arm', 'face', 'back')")
    
    @validator('location')
    def validate_location(cls, v):
        """Validate body location is not empty"""
        if not v or not v.strip():
            raise ValueError('Body location cannot be empty')
        return v.strip()


class SensationData(BaseModel):
    """Step 2: Sensation information"""
    sensations: list[str] = Field(default_factory=list, description="List of sensations")
    
    @validator('sensations')
    def validate_sensations(cls, v):
        """Validate sensations are from allowed list"""
        allowed_sensations = ['itching', 'pain', 'burning', 'numbness', 'tingling', 'none']
        if v:
            for sensation in v:
                if sensation.lower() not in allowed_sensations:
                    raise ValueError(f'Invalid sensation: {sensation}. Must be one of: {", ".join(allowed_sensations)}')
        return [s.lower() for s in v]


class VisualChangeData(BaseModel):
    """Step 3: Visual changes information"""
    visual_changes: list[str] = Field(default_factory=list, description="List of visual changes")
    
    @validator('visual_changes')
    def validate_visual_changes(cls, v):
        """Validate visual changes are from allowed list"""
        allowed_changes = ['color', 'size', 'shape', 'border', 'texture', 'bleeding', 'none']
        if v:
            for change in v:
                if change.lower() not in allowed_changes:
                    raise ValueError(f'Invalid visual change: {change}. Must be one of: {", ".join(allowed_changes)}')
        return [c.lower() for c in v]


class SymptomData(BaseModel):
    """Complete symptom data from wizard (Requirements: 5.2, 5.3, 5.4, 5.5)"""
    body_location: Optional[str] = Field(None, description="Location of lesion on body")
    sensations: Optional[list[str]] = Field(default_factory=list, description="Sensations (itching, pain, burning, numbness)")
    visual_changes: Optional[list[str]] = Field(default_factory=list, description="Visual changes (color, size, shape, border)")
    duration: Optional[str] = Field(None, description="Duration of symptoms")
    
    @validator('body_location')
    def validate_body_location(cls, v):
        """Validate body location if provided"""
        if v is not None and not v.strip():
            raise ValueError('Body location cannot be empty string')
        return v.strip() if v else None
    
    @validator('sensations')
    def validate_sensations(cls, v):
        """Validate sensations are from allowed list"""
        allowed_sensations = ['itching', 'pain', 'burning', 'numbness', 'tingling', 'none']
        if v:
            for sensation in v:
                if sensation.lower() not in allowed_sensations:
                    raise ValueError(f'Invalid sensation: {sensation}. Must be one of: {", ".join(allowed_sensations)}')
            return [s.lower() for s in v]
        return v
    
    @validator('visual_changes')
    def validate_visual_changes(cls, v):
        """Validate visual changes are from allowed list"""
        allowed_changes = ['color', 'size', 'shape', 'border', 'texture', 'bleeding', 'none']
        if v:
            for change in v:
                if change.lower() not in allowed_changes:
                    raise ValueError(f'Invalid visual change: {change}. Must be one of: {", ".join(allowed_changes)}')
            return [c.lower() for c in v]
        return v
    
    @validator('duration')
    def validate_duration(cls, v):
        """Validate duration format if provided"""
        if v is not None and not v.strip():
            raise ValueError('Duration cannot be empty string')
        return v.strip() if v else None


class AnalyzeImageRequest(BaseModel):
    """Request for image analysis (form data)"""
    body_location: Optional[str] = None
    sensations: Optional[str] = None  # Comma-separated list
    visual_changes: Optional[str] = None  # Comma-separated list
    duration: Optional[str] = None


class MedicalReportResponse(BaseModel):
    """Medical report response"""
    id: str
    patient_id: str
    image_url: str
    ai_prediction: dict
    symptoms: Optional[dict] = None
    status: Literal['safe', 'flagged', 'urgent']
    risk_level: Literal['low', 'medium', 'high', 'urgent']
    body_location: Optional[str] = None
    consultation_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MedicalReportListResponse(BaseModel):
    """Medical report list item response"""
    id: str
    patient_id: str
    image_url: str
    risk_level: Literal['low', 'medium', 'high', 'urgent']
    status: Literal['safe', 'flagged', 'urgent']
    body_location: Optional[str] = None
    created_at: datetime
    
    # Summary fields
    top_prediction: Optional[dict] = None  # {type: str, probability: float}
    needs_followup: bool = False  # True if report is older than 6 months
    
    class Config:
        from_attributes = True


class ReportComparisonResponse(BaseModel):
    """Report comparison response"""
    report1: MedicalReportResponse
    report2: MedicalReportResponse
    changes: dict = Field(..., description="Detected changes between reports")
    
    class Config:
        from_attributes = True


# ============================================================================
# Doctor Models
# ============================================================================

class DoctorRegistrationRequest(BaseModel):
    """Doctor registration request"""
    license_no: str = Field(..., min_length=1, max_length=100, description="Medical license number")
    clinic_name: str = Field(..., min_length=1, max_length=200, description="Clinic or hospital name")
    lat: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    lng: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    whatsapp_no: str = Field(..., min_length=1, max_length=20, description="WhatsApp contact number")
    specialization: Optional[str] = Field(None, max_length=100, description="Medical specialization")
    
    @validator('license_no')
    def validate_license_no(cls, v):
        """Validate license number is not empty"""
        if not v or not v.strip():
            raise ValueError('License number cannot be empty')
        return v.strip()
    
    @validator('clinic_name')
    def validate_clinic_name(cls, v):
        """Validate clinic name is not empty"""
        if not v or not v.strip():
            raise ValueError('Clinic name cannot be empty')
        return v.strip()
    
    @validator('whatsapp_no')
    def validate_whatsapp_no(cls, v):
        """Validate WhatsApp number format"""
        if not v or not v.strip():
            raise ValueError('WhatsApp number cannot be empty')
        # Remove common formatting characters
        cleaned = v.strip().replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        if not cleaned.isdigit():
            raise ValueError('WhatsApp number must contain only digits (and optional +, -, spaces, parentheses)')
        if len(cleaned) < 7 or len(cleaned) > 15:
            raise ValueError('WhatsApp number must be between 7 and 15 digits')
        return v.strip()
    
    @validator('lat')
    def validate_latitude(cls, v):
        """Validate latitude range"""
        if v < -90 or v > 90:
            raise ValueError('Latitude must be between -90 and 90')
        return v
    
    @validator('lng')
    def validate_longitude(cls, v):
        """Validate longitude range"""
        if v < -180 or v > 180:
            raise ValueError('Longitude must be between -180 and 180')
        return v


class DoctorResponse(BaseModel):
    """Doctor profile response"""
    id: str
    user_id: str
    license_no: str
    clinic_name: str
    lat: float
    lng: float
    whatsapp_no: Optional[str] = None  # Made optional for auto-created profiles
    specialization: Optional[str] = None
    bio: Optional[str] = None
    education: Optional[str] = None
    certifications: Optional[str] = None
    languages: Optional[str] = None
    clinic_hours: Optional[str] = None
    average_rating: float = 0.0
    review_count: int = 0
    verified: bool = False  # From profiles table
    created_at: datetime
    updated_at: datetime
    whatsapp_url: Optional[str] = None  # Computed field for WhatsApp contact URL
    
    class Config:
        from_attributes = True
    
    def __init__(self, **data):
        """Initialize and compute WhatsApp URL"""
        super().__init__(**data)
        # Compute WhatsApp URL if not provided
        if self.whatsapp_url is None and self.whatsapp_no:
            self.whatsapp_url = self.get_whatsapp_url()
    
    def get_whatsapp_url(self, message: str = "I would like to share my Derman Report") -> str:
        """
        Generate WhatsApp contact URL with pre-filled message
        
        Requirements: 7.5
        
        Returns:
            str: WhatsApp URL in format https://wa.me/{whatsapp_no}?text={message}
        """
        from urllib.parse import quote
        
        # Remove '+' prefix if present
        clean_number = self.whatsapp_no.lstrip('+')
        
        # URL encode the message
        encoded_message = quote(message)
        
        # Construct WhatsApp URL
        return f"https://wa.me/{clean_number}?text={encoded_message}"


class DoctorVerificationRequest(BaseModel):
    """Admin doctor verification request"""
    verified: bool = Field(..., description="Verification status (true to approve, false to reject)")
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection (if verified=false)")
    
    @validator('rejection_reason')
    def validate_rejection_reason(cls, v, values):
        """Require rejection reason if not verified"""
        if 'verified' in values and not values['verified'] and not v:
            raise ValueError('Rejection reason is required when rejecting a doctor application')
        return v


# ============================================================================
# Appointment Models
# ============================================================================

class AppointmentCreateRequest(BaseModel):
    """Appointment creation request"""
    doctor_id: str = Field(..., description="Doctor UUID")
    report_id: Optional[str] = Field(None, description="Associated medical report UUID")
    scheduled_at: datetime = Field(..., description="Scheduled appointment time")
    consultation_type: Literal['in_person', 'video'] = Field('in_person', description="Type of consultation")
    
    @validator('doctor_id')
    def validate_doctor_id(cls, v):
        """Validate doctor_id is a valid UUID"""
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError('doctor_id must be a valid UUID')
        return v
    
    @validator('report_id')
    def validate_report_id(cls, v):
        """Validate report_id is a valid UUID if provided"""
        if v is not None:
            try:
                uuid.UUID(v)
            except ValueError:
                raise ValueError('report_id must be a valid UUID')
        return v
    
    @validator('scheduled_at')
    def validate_scheduled_at(cls, v):
        """Validate scheduled_at is in the future"""
        from datetime import timezone
        # Make both datetimes timezone-aware for comparison
        now = datetime.now(timezone.utc)
        scheduled = v if v.tzinfo else v.replace(tzinfo=timezone.utc)
        
        if scheduled <= now:
            raise ValueError('scheduled_at must be in the future')
        return v


class AppointmentUpdateRequest(BaseModel):
    """Appointment status update request"""
    status: Literal['pending', 'confirmed', 'completed', 'cancelled'] = Field(..., description="Appointment status")
    
    @validator('status')
    def validate_status(cls, v):
        """Validate status is one of allowed values"""
        allowed_statuses = ['pending', 'confirmed', 'completed', 'cancelled']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v


class AppointmentResponse(BaseModel):
    """Appointment response"""
    id: str
    patient_id: str = Field(..., alias='patientId')
    doctor_id: str = Field(..., alias='doctorId')
    report_id: Optional[str] = Field(None, alias='reportId')
    scheduled_at: datetime = Field(..., alias='scheduledAt')
    status: Literal['pending', 'confirmed', 'completed', 'cancelled']
    consultation_type: Literal['in_person', 'video'] = Field(..., alias='consultationType')
    video_room_url: Optional[str] = Field(None, alias='videoRoomUrl')
    created_at: datetime = Field(..., alias='createdAt')
    updated_at: datetime = Field(..., alias='updatedAt')
    patient: Optional[dict] = None  # Patient details (fullName, email)
    report: Optional[dict] = None   # Report details (risk_level)
    
    class Config:
        from_attributes = True
        populate_by_name = True
        by_alias = True


# ============================================================================
# Consultation Notes Models
# ============================================================================

class ConsultationNotesRequest(BaseModel):
    """Request to add consultation notes to a medical report"""
    notes: str = Field(..., min_length=1, max_length=10000, description="Consultation notes from doctor")
    
    @validator('notes')
    def validate_notes(cls, v):
        """Validate notes are not empty or just whitespace"""
        if not v or not v.strip():
            raise ValueError('Consultation notes cannot be empty or just whitespace')
        return v.strip()


# ============================================================================
# Review and Rating Models
# ============================================================================

class ReviewCreateRequest(BaseModel):
    """Request to create a review for a doctor"""
    doctor_id: str = Field(..., description="Doctor UUID")
    appointment_id: Optional[str] = Field(None, description="Associated appointment UUID")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    review_text: Optional[str] = Field(None, max_length=2000, description="Optional review text")
    
    @validator('doctor_id')
    def validate_doctor_id(cls, v):
        """Validate doctor_id is a valid UUID"""
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError('doctor_id must be a valid UUID')
        return v
    
    @validator('appointment_id')
    def validate_appointment_id(cls, v):
        """Validate appointment_id is a valid UUID if provided"""
        if v is not None:
            try:
                uuid.UUID(v)
            except ValueError:
                raise ValueError('appointment_id must be a valid UUID')
        return v
    
    @validator('rating')
    def validate_rating(cls, v):
        """Validate rating is between 1 and 5"""
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v
    
    @validator('review_text')
    def validate_review_text(cls, v):
        """Validate review text if provided"""
        if v is not None and v.strip() == '':
            raise ValueError('Review text cannot be empty or just whitespace')
        return v.strip() if v else None


class ReviewResponse(BaseModel):
    """Review response"""
    id: str
    patient_id: str
    doctor_id: str
    appointment_id: Optional[str] = None
    rating: int
    review_text: Optional[str] = None
    flagged: bool = False
    created_at: datetime
    
    # Additional fields for display
    patient_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class DoctorReviewsResponse(BaseModel):
    """Doctor reviews with statistics"""
    doctor_id: str
    average_rating: float
    review_count: int
    reviews: list[ReviewResponse]
    
    class Config:
        from_attributes = True



# ============================================================================
# Notification Models
# ============================================================================

class NotificationResponse(BaseModel):
    """Notification response"""
    id: str
    user_id: str
    type: str
    title: str
    message: str
    read: bool
    metadata: Optional[dict] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """List of notifications"""
    notifications: list[NotificationResponse]
    unread_count: int
    
    class Config:
        from_attributes = True


class MarkNotificationReadRequest(BaseModel):
    """Request to mark notification as read"""
    read: bool = True



# ============================================================================
# Admin Models
# ============================================================================

class FlaggedReportResponse(BaseModel):
    """Flagged medical report for admin moderation"""
    id: str
    patient_id: str
    patient_email: Optional[str] = None
    patient_name: Optional[str] = None
    image_url: str
    nsfw_score: Optional[float] = None
    non_skin_score: Optional[float] = None
    rejection_reason: str
    created_at: datetime
    status: str
    
    class Config:
        from_attributes = True
