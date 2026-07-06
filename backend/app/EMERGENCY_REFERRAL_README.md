# Emergency Referral System

## Overview

The Emergency Referral System automatically notifies the 3 nearest verified dermatologists when a high-risk skin lesion case is detected (cancer probability > 85%).

**Requirements**: 23.3

## Components

### 1. Email Service (`email_service.py`)

Handles sending email notifications to doctors.

**Features:**
- SMTP-based email sending
- HTML and plain text email templates
- Urgent case notification templates
- Configurable via environment variables

**Configuration:**
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@skinguard.com
FROM_NAME=SkinGuard AI
```

**Usage:**
```python
from app.email_service import get_email_service

email_service = get_email_service()

await email_service.send_urgent_case_notification(
    doctor_email="doctor@example.com",
    doctor_name="Dr. Smith",
    patient_name="John Doe",
    report_id="report-uuid",
    risk_level="urgent",
    top_prediction={"type": "Melanoma", "probability": 0.92},
    report_url="https://skinguard.com/reports/report-uuid"
)
```

### 2. Emergency Referral Service (`emergency_referral.py`)

Finds nearest doctors and coordinates notifications.

**Features:**
- Geographic distance calculation using Haversine formula
- Finds N nearest verified doctors
- Handles cases with no patient location (returns first N doctors)
- Sends email notifications to identified doctors
- Graceful error handling

**Usage:**
```python
from app.emergency_referral import get_emergency_referral_service

service = get_emergency_referral_service()

# Find nearest doctors
nearest_doctors = await service.find_nearest_doctors(
    patient_lat=40.7128,
    patient_lng=-74.0060,
    limit=3
)

# Notify doctors about urgent case
doctors_found, emails_sent = await service.notify_nearest_doctors(
    report_id="report-uuid",
    patient_id="patient-uuid",
    patient_name="John Doe",
    patient_lat=40.7128,
    patient_lng=-74.0060,
    risk_level="urgent",
    top_prediction={"type": "Melanoma", "probability": 0.92}
)
```

### 3. Integration with Report Creation

The emergency referral system is automatically triggered when an urgent report is created.

**Location:** `backend/app/routers/reports.py` - `analyze_skin_image` endpoint

**Flow:**
1. Image is analyzed by AI pipeline
2. Risk level is assessed
3. If risk_level == "urgent", emergency referral is triggered
4. System finds 3 nearest verified doctors
5. Email notifications are sent to each doctor
6. Audit log entry is created

**Code:**
```python
# Handle urgent cases - notify nearest doctors (Requirements: 23.3)
if report_status == "urgent":
    emergency_service = get_emergency_referral_service()
    doctors_found, emails_sent = await emergency_service.notify_nearest_doctors(
        report_id=report_id,
        patient_id=current_user['id'],
        patient_name=patient_name,
        patient_lat=patient_lat,
        patient_lng=patient_lng,
        risk_level=analysis_result.risk_level,
        top_prediction=top_prediction
    )
```

## Email Template

The urgent case notification email includes:

- **Subject:** 🚨 URGENT: High-Risk Skin Lesion Case Requires Review
- **Content:**
  - Doctor's name
  - Patient's name
  - Report ID
  - Risk level
  - AI prediction (cancer type and probability)
  - Date/time
  - Explanation of why doctor received notification
  - Recommended action
  - Link to view full report
  - Medical disclaimer

**Example:**
```
Dear Dr. Smith,

A HIGH-RISK skin lesion case has been detected and requires immediate medical review.

Case Details:
- Patient: John Doe
- Report ID: abc-123-def
- Risk Level: URGENT
- AI Detection: Melanoma (92.0% probability)
- Date: 2024-02-10 15:30 UTC

Why you received this notification:
You are one of the 3 nearest verified dermatologists to this patient's location.
The AI analysis has detected a cancer probability exceeding 85%, triggering our
emergency referral protocol.

Recommended Action:
Please review this case as soon as possible and contact the patient to schedule
an urgent consultation for clinical biopsy and diagnosis.

[View Full Report Button]

Important Disclaimer:
This is an AI-assisted screening result with 94% accuracy. Clinical examination
and biopsy are required for definitive diagnosis.
```

## Distance Calculation

The system uses the Haversine formula to calculate great-circle distances between coordinates:

```python
def calculate_distance(lat1, lng1, lat2, lng2):
    """Calculate distance in kilometers"""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(delta_lng / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c
```

## Error Handling

The system is designed to fail gracefully:

1. **No verified doctors:** Returns empty list, logs warning
2. **Email sending failure:** Continues with remaining doctors, logs error
3. **Database errors:** Catches exceptions, logs error, returns (0, 0)
4. **Missing patient location:** Falls back to returning first N doctors

**Important:** Emergency referral failures do NOT fail the report creation request. The report is created successfully even if notifications fail.

## Testing

### Unit Tests
Location: `tests/unit/test_emergency_referral.py`

Tests:
- Distance calculation accuracy
- Finding nearest doctors with/without location
- Handling no doctors scenario
- Email notification success/failure
- Limit parameter enforcement

### Integration Tests
Location: `tests/integration/test_emergency_referral_integration.py`

Tests:
- Complete urgent report flow
- Graceful handling of no doctors
- Correct distance-based sorting

**Run tests:**
```bash
# Unit tests
python -m pytest tests/unit/test_emergency_referral.py -v

# Integration tests
python -m pytest tests/integration/test_emergency_referral_integration.py -v
```

## Audit Logging

Emergency referrals are logged to the audit_logs table:

```python
await audit_logger.log_action(
    user_id=current_user['id'],
    action="emergency_referral_triggered",
    resource_type="medical_report",
    resource_id=report_id,
    metadata={
        "doctors_found": doctors_found,
        "emails_sent": emails_sent,
        "risk_level": analysis_result.risk_level,
        "top_prediction": top_prediction
    },
    ip_address=client_ip
)
```

## Future Enhancements

1. **SMS Notifications:** Add SMS alerts for urgent cases
2. **Push Notifications:** Mobile app push notifications
3. **Doctor Preferences:** Allow doctors to set notification preferences
4. **Escalation:** Automatic escalation if no doctor responds within X hours
5. **Patient Location:** Add location fields to patient_data for more accurate matching
6. **Specialization Matching:** Prioritize doctors with specific specializations
7. **Load Balancing:** Distribute cases evenly among doctors
8. **Response Tracking:** Track which doctors viewed/responded to notifications

## Production Deployment

### Email Service Setup

For production, use a reliable email service:

**Option 1: Gmail with App Password**
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
```

**Option 2: SendGrid**
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

**Option 3: AWS SES**
```bash
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USERNAME=your-ses-smtp-username
SMTP_PASSWORD=your-ses-smtp-password
```

### Monitoring

Monitor these metrics:
- Emergency referral trigger rate
- Email delivery success rate
- Average notification time
- Doctor response rate
- Failed notification alerts

### Security Considerations

1. **Email Authentication:** Use SPF, DKIM, and DMARC records
2. **Rate Limiting:** Prevent email spam/abuse
3. **PHI Protection:** Ensure emails are HIPAA compliant
4. **Access Control:** Only verified doctors receive notifications
5. **Audit Trail:** All notifications are logged

## Support

For issues or questions:
- Check logs in `backend/logs/`
- Review audit_logs table for notification history
- Verify SMTP configuration
- Test email service with `get_email_service().send_email()`
