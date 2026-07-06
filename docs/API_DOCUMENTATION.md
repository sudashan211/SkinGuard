# SkinGuard API Documentation

Version: 1.0.0  
Base URL: `https://api.skinguard.com`  
Environment: Production

## Table of Contents

1. [Authentication](#authentication)
2. [Patient Endpoints](#patient-endpoints)
3. [Doctor Endpoints](#doctor-endpoints)
4. [Admin Endpoints](#admin-endpoints)
5. [Appointment Endpoints](#appointment-endpoints)
6. [Review Endpoints](#review-endpoints)
7. [Notification Endpoints](#notification-endpoints)
8. [Health Check Endpoints](#health-check-endpoints)
9. [Error Codes](#error-codes)
10. [Rate Limiting](#rate-limiting)

## Authentication

All authenticated endpoints require a JWT token in the Authorization header.

### Register

Create a new user account.

**Endpoint:** `POST /api/auth/signup`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "role": "patient"
}
```

**Response:** `201 Created`
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "patient",
    "verified": false,
    "created_at": "2024-01-01T00:00:00Z"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Login

Authenticate and receive access token.

**Endpoint:** `POST /api/auth/login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "patient"
  }
}
```

### Get Current User

Get authenticated user information.

**Endpoint:** `GET /api/auth/me`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "patient",
  "verified": false,
  "avatar_url": "https://...",
  "language_preference": "en"
}
```

### Logout

Invalidate current session.

**Endpoint:** `POST /api/auth/logout`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "message": "Logged out successfully"
}
```

## Patient Endpoints

### Create/Update Patient Profile

Create or update patient health profile.

**Endpoint:** `PUT /api/patient/profile`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "age": 35,
  "skin_type": "III",
  "family_history": "Mother had melanoma at age 60"
}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "age": 35,
  "skin_type": "III",
  "family_history": "Mother had melanoma at age 60",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Analyze Skin Lesion

Upload image for AI analysis.

**Endpoint:** `POST /api/analyze-skin`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body (multipart/form-data):**
- `image`: Image file (JPEG, PNG)
- `symptoms`: JSON string with symptom data

**Symptoms JSON:**
```json
{
  "body_location": "left_arm",
  "sensations": ["itching", "pain"],
  "visual_changes": ["color_change", "size_increase"],
  "duration": "2 weeks"
}
```

**Response:** `200 OK`
```json
{
  "report_id": "uuid",
  "image_url": "https://storage.skinguard.com/...",
  "predictions": [
    {
      "type": "melanoma",
      "probability": 0.15,
      "confidence": 0.92
    },
    {
      "type": "basal_cell_carcinoma",
      "probability": 0.08,
      "confidence": 0.88
    }
  ],
  "hotspots": [
    {
      "x": 120,
      "y": 150,
      "width": 80,
      "height": 80,
      "confidence": 0.95
    }
  ],
  "risk_level": "medium",
  "status": "safe",
  "disclaimer": "This is a 94% probability estimate. Please consult verified doctors for clinical biopsy.",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Error Responses:**

`403 Forbidden` - Inappropriate content detected
```json
{
  "detail": "Inappropriate content detected"
}
```

`400 Bad Request` - Image quality issues
```json
{
  "detail": "Image resolution too low for accurate analysis"
}
```

### Get Report History

Get patient's medical report history.

**Endpoint:** `GET /api/reports`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `limit` (optional): Number of reports to return (default: 20)
- `offset` (optional): Pagination offset (default: 0)

**Response:** `200 OK`
```json
{
  "reports": [
    {
      "id": "uuid",
      "image_url": "https://...",
      "thumbnail_url": "https://...",
      "risk_level": "medium",
      "status": "safe",
      "body_location": "left_arm",
      "created_at": "2024-01-01T00:00:00Z",
      "prediction_summary": {
        "highest_risk": "melanoma",
        "probability": 0.15
      }
    }
  ],
  "total": 5,
  "limit": 20,
  "offset": 0
}
```

### Get Single Report

Get detailed report information.

**Endpoint:** `GET /api/reports/{report_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "patient_id": "uuid",
  "image_url": "https://...",
  "ai_prediction": {
    "predictions": [...],
    "hotspots": [...],
    "model_version": "1.0.0",
    "processing_time": 2500
  },
  "symptoms": {
    "body_location": "left_arm",
    "sensations": ["itching"],
    "visual_changes": ["color_change"]
  },
  "risk_level": "medium",
  "status": "safe",
  "consultation_notes": "Recommend follow-up in 3 months",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Compare Reports

Compare two reports for changes.

**Endpoint:** `POST /api/reports/{report_id}/compare/{other_report_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "report1": {
    "id": "uuid",
    "created_at": "2024-01-01T00:00:00Z",
    "risk_level": "low"
  },
  "report2": {
    "id": "uuid",
    "created_at": "2024-03-01T00:00:00Z",
    "risk_level": "medium"
  },
  "changes": {
    "risk_level_change": "increased",
    "size_change": "increased by 15%",
    "color_change": "darker",
    "recommendations": "Immediate consultation recommended due to changes"
  }
}
```

## Doctor Endpoints

### Register as Doctor

Register doctor profile with license information.

**Endpoint:** `POST /api/doctors/register`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "license_no": "MD123456",
  "clinic_name": "Dermatology Clinic",
  "lat": 40.7128,
  "lng": -74.0060,
  "whatsapp_no": "+1234567890",
  "specialization": "Dermatology"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "license_no": "MD123456",
  "clinic_name": "Dermatology Clinic",
  "verified": false,
  "message": "Registration submitted. Awaiting admin verification."
}
```

### Find Nearby Doctors

Find verified doctors near a location.

**Endpoint:** `GET /api/doctors/nearby`

**Query Parameters:**
- `lat`: Latitude (required)
- `lng`: Longitude (required)
- `radius`: Search radius in km (default: 50)

**Response:** `200 OK`
```json
{
  "doctors": [
    {
      "id": "uuid",
      "name": "Dr. Jane Smith",
      "clinic_name": "Dermatology Clinic",
      "lat": 40.7128,
      "lng": -74.0060,
      "distance_km": 2.5,
      "whatsapp_no": "+1234567890",
      "specialization": "Dermatology",
      "average_rating": 4.8,
      "review_count": 125,
      "verified": true
    }
  ]
}
```

### Get Pending Reports (Doctor)

Get pending patient reports for review.

**Endpoint:** `GET /api/doctors/reports/pending`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status`: Filter by status (safe, urgent) - default: all
- `limit`: Number of reports (default: 20)

**Response:** `200 OK`
```json
{
  "reports": [
    {
      "id": "uuid",
      "patient_id": "uuid",
      "patient_info": {
        "age": 35,
        "skin_type": "III",
        "family_history": "..."
      },
      "image_url": "https://...",
      "ai_prediction": {...},
      "symptoms": {...},
      "risk_level": "urgent",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Add Consultation Notes

Add notes to a patient report.

**Endpoint:** `POST /api/doctors/reports/{report_id}/notes`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "notes": "Examined lesion. Recommend biopsy for definitive diagnosis. Follow-up in 2 weeks."
}
```

**Response:** `200 OK`
```json
{
  "report_id": "uuid",
  "consultation_notes": "Examined lesion. Recommend biopsy...",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## Admin Endpoints

### Get Pending Doctor Verifications

List doctors awaiting verification.

**Endpoint:** `GET /api/admin/doctors/pending`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "doctors": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "name": "Dr. John Doe",
      "email": "doctor@example.com",
      "license_no": "MD123456",
      "clinic_name": "Dermatology Clinic",
      "specialization": "Dermatology",
      "verified": false,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Verify Doctor

Approve or reject doctor application.

**Endpoint:** `PUT /api/admin/doctors/{doctor_id}/verify`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "verified": true,
  "notes": "License verified with state medical board"
}
```

**Response:** `200 OK`
```json
{
  "doctor_id": "uuid",
  "verified": true,
  "message": "Doctor verified successfully"
}
```

### Get Flagged Content

List flagged medical reports.

**Endpoint:** `GET /api/admin/reports/flagged`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "reports": [
    {
      "id": "uuid",
      "patient_id": "uuid",
      "image_url": "https://...",
      "status": "flagged",
      "nsfw_score": 0.45,
      "rejection_reason": "NSFW content detected",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Get Analytics

Get platform usage analytics.

**Endpoint:** `GET /api/admin/analytics`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `start_date`: Start date (ISO 8601)
- `end_date`: End date (ISO 8601)

**Response:** `200 OK`
```json
{
  "daily_active_users": 1250,
  "total_screenings": 5430,
  "average_processing_time_ms": 2500,
  "error_rate": 0.02,
  "cancer_type_distribution": {
    "melanoma": 450,
    "basal_cell_carcinoma": 320,
    "squamous_cell_carcinoma": 180
  },
  "geographic_distribution": {
    "US": 3200,
    "UK": 850,
    "CA": 620
  }
}
```

## Appointment Endpoints

### Create Appointment

Book an appointment with a doctor.

**Endpoint:** `POST /api/appointments`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "doctor_id": "uuid",
  "report_id": "uuid",
  "scheduled_at": "2024-01-15T10:00:00Z",
  "consultation_type": "video"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "patient_id": "uuid",
  "doctor_id": "uuid",
  "scheduled_at": "2024-01-15T10:00:00Z",
  "status": "pending",
  "consultation_type": "video",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Get Appointments

List user's appointments.

**Endpoint:** `GET /api/appointments`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status`: Filter by status (pending, confirmed, completed, cancelled)

**Response:** `200 OK`
```json
{
  "appointments": [
    {
      "id": "uuid",
      "doctor": {
        "name": "Dr. Jane Smith",
        "clinic_name": "Dermatology Clinic"
      },
      "scheduled_at": "2024-01-15T10:00:00Z",
      "status": "confirmed",
      "consultation_type": "video",
      "video_room_url": "https://video.skinguard.com/room/..."
    }
  ]
}
```

### Update Appointment Status

Update appointment status.

**Endpoint:** `PUT /api/appointments/{appointment_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "status": "completed"
}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "status": "completed",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

### Generate Video Room

Generate video consultation room URL.

**Endpoint:** `POST /api/appointments/{appointment_id}/video-room`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "appointment_id": "uuid",
  "video_room_url": "https://video.skinguard.com/room/abc123",
  "expires_at": "2024-01-15T12:00:00Z"
}
```

## Review Endpoints

### Submit Review

Submit a review for a doctor.

**Endpoint:** `POST /api/reviews`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "doctor_id": "uuid",
  "appointment_id": "uuid",
  "rating": 5,
  "review_text": "Excellent consultation. Very thorough and professional."
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "doctor_id": "uuid",
  "rating": 5,
  "review_text": "Excellent consultation...",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Get Doctor Reviews

Get reviews for a doctor.

**Endpoint:** `GET /api/doctors/{doctor_id}/reviews`

**Query Parameters:**
- `limit`: Number of reviews (default: 20)
- `offset`: Pagination offset (default: 0)

**Response:** `200 OK`
```json
{
  "reviews": [
    {
      "id": "uuid",
      "patient_name": "John D.",
      "rating": 5,
      "review_text": "Excellent consultation...",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "average_rating": 4.8,
  "total_reviews": 125
}
```

## Notification Endpoints

### Get Notifications

Get user's notifications.

**Endpoint:** `GET /api/notifications`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `read`: Filter by read status (true/false)
- `limit`: Number of notifications (default: 20)

**Response:** `200 OK`
```json
{
  "notifications": [
    {
      "id": "uuid",
      "type": "analysis_complete",
      "title": "AI Analysis Complete",
      "message": "Your skin analysis results are ready",
      "read": false,
      "metadata": {
        "report_id": "uuid"
      },
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Mark Notification as Read

Mark a notification as read.

**Endpoint:** `PUT /api/notifications/{notification_id}/read`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "read": true
}
```

## Health Check Endpoints

### Overall Health

Check overall system health.

**Endpoint:** `GET /health`

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0"
}
```

### Database Health

Check database connectivity.

**Endpoint:** `GET /health/db`

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "response_time_ms": 15
}
```

### AI Models Health

Check AI models status.

**Endpoint:** `GET /health/ai`

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "models_loaded": true,
  "nsfw_model": "loaded",
  "swin_transformer": "loaded",
  "efficientnet": "loaded"
}
```

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing or invalid token |
| 403 | Forbidden - Insufficient permissions or inappropriate content |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Resource already exists |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

**Error Response Format:**
```json
{
  "detail": "Error message",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Rate Limiting

API requests are rate limited to prevent abuse:

- **Anonymous requests:** 100 requests per hour
- **Authenticated requests:** 1000 requests per hour
- **Image analysis:** 50 requests per hour per user

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1640995200
```

When rate limit is exceeded:
```json
{
  "detail": "Rate limit exceeded. Try again in 3600 seconds.",
  "error_code": "RATE_LIMIT_EXCEEDED"
}
```

## Webhooks

SkinGuard can send webhooks for important events:

### Webhook Events

- `analysis.completed` - AI analysis completed
- `appointment.confirmed` - Appointment confirmed
- `urgent.case.detected` - Urgent case detected
- `doctor.verified` - Doctor verification status changed

### Webhook Payload

```json
{
  "event": "analysis.completed",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "report_id": "uuid",
    "patient_id": "uuid",
    "risk_level": "medium"
  }
}
```

## SDK Examples

### Python

```python
import requests

# Authentication
response = requests.post(
    "https://api.skinguard.com/api/auth/login",
    json={"email": "user@example.com", "password": "password"}
)
token = response.json()["access_token"]

# Upload image for analysis
with open("lesion.jpg", "rb") as f:
    response = requests.post(
        "https://api.skinguard.com/api/analyze-skin",
        headers={"Authorization": f"Bearer {token}"},
        files={"image": f},
        data={"symptoms": '{"body_location": "left_arm"}'}
    )
    
result = response.json()
print(f"Risk Level: {result['risk_level']}")
```

### JavaScript

```javascript
// Authentication
const response = await fetch('https://api.skinguard.com/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password'
  })
});
const { access_token } = await response.json();

// Upload image
const formData = new FormData();
formData.append('image', imageFile);
formData.append('symptoms', JSON.stringify({ body_location: 'left_arm' }));

const result = await fetch('https://api.skinguard.com/api/analyze-skin', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${access_token}` },
  body: formData
});

const data = await result.json();
console.log('Risk Level:', data.risk_level);
```

## Support

For API support:
- Email: api-support@skinguard.com
- Documentation: https://docs.skinguard.com
- Status Page: https://status.skinguard.com
