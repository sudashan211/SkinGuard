# Manual Test: Video Room Creation

## Task 14.3: Implement video consultation support

### Test Scenario 1: Create Video Room for Video Consultation

**Setup:**
1. Create a patient account
2. Create a verified doctor account
3. Create a video consultation appointment

**Test Steps:**
```bash
# 1. Create appointment (video consultation)
POST /api/appointments
{
  "doctor_id": "doctor-uuid",
  "scheduled_at": "2024-12-20T10:00:00Z",
  "consultation_type": "video"
}

# Expected Response: 201 Created
{
  "id": "appointment-uuid",
  "patient_id": "patient-uuid",
  "doctor_id": "doctor-uuid",
  "scheduled_at": "2024-12-20T10:00:00Z",
  "status": "pending",
  "consultation_type": "video",
  "video_room_url": null,
  ...
}

# 2. Generate video room URL
POST /api/appointments/{appointment-uuid}/video-room

# Expected Response: 200 OK
{
  "id": "appointment-uuid",
  "patient_id": "patient-uuid",
  "doctor_id": "doctor-uuid",
  "scheduled_at": "2024-12-20T10:00:00Z",
  "status": "pending",
  "consultation_type": "video",
  "video_room_url": "https://video.skinguard.app/room/{unique-uuid}",
  ...
}
```

**Verification:**
- ✅ Video room URL is generated
- ✅ URL contains unique UUID
- ✅ URL is stored in database
- ✅ URL format: `https://video.skinguard.app/room/{uuid}`

---

### Test Scenario 2: Video Room for In-Person Consultation (Should Fail)

**Test Steps:**
```bash
# 1. Create appointment (in-person consultation)
POST /api/appointments
{
  "doctor_id": "doctor-uuid",
  "scheduled_at": "2024-12-20T10:00:00Z",
  "consultation_type": "in_person"
}

# 2. Try to generate video room URL
POST /api/appointments/{appointment-uuid}/video-room

# Expected Response: 400 Bad Request
{
  "code": "INVALID_CONSULTATION_TYPE",
  "message": "Video room can only be created for video consultations",
  ...
}
```

**Verification:**
- ✅ Returns 400 error
- ✅ Error message indicates invalid consultation type

---

### Test Scenario 3: Unauthorized Access (Should Fail)

**Test Steps:**
```bash
# 1. Create appointment as Patient A
POST /api/appointments
{
  "doctor_id": "doctor-uuid",
  "scheduled_at": "2024-12-20T10:00:00Z",
  "consultation_type": "video"
}

# 2. Try to access video room as Patient B (different user)
POST /api/appointments/{appointment-uuid}/video-room
Authorization: Bearer {patient-b-token}

# Expected Response: 403 Forbidden
{
  "code": "FORBIDDEN",
  "message": "You are not authorized to access this appointment",
  ...
}
```

**Verification:**
- ✅ Returns 403 error
- ✅ Only patient or doctor associated with appointment can access

---

### Test Scenario 4: Idempotent Video Room Creation

**Test Steps:**
```bash
# 1. Create video room (first time)
POST /api/appointments/{appointment-uuid}/video-room

# Response:
{
  "video_room_url": "https://video.skinguard.app/room/abc-123-def",
  ...
}

# 2. Create video room again (second time)
POST /api/appointments/{appointment-uuid}/video-room

# Response (same URL):
{
  "video_room_url": "https://video.skinguard.app/room/abc-123-def",
  ...
}
```

**Verification:**
- ✅ Same URL is returned on subsequent calls
- ✅ No new URL is generated
- ✅ Idempotent behavior

---

### Test Scenario 5: Doctor Access to Video Room

**Test Steps:**
```bash
# 1. Create appointment as patient
POST /api/appointments
{
  "doctor_id": "doctor-uuid",
  "scheduled_at": "2024-12-20T10:00:00Z",
  "consultation_type": "video"
}

# 2. Doctor generates video room URL
POST /api/appointments/{appointment-uuid}/video-room
Authorization: Bearer {doctor-token}

# Expected Response: 200 OK
{
  "video_room_url": "https://video.skinguard.app/room/{unique-uuid}",
  ...
}
```

**Verification:**
- ✅ Doctor can generate video room URL
- ✅ Both patient and doctor have access

---

## Implementation Summary

### Endpoint Details
- **URL**: `POST /api/appointments/{appointment_id}/video-room`
- **Authentication**: Required (patient or doctor)
- **Authorization**: Only patient or doctor associated with appointment

### Request
- No request body required
- Appointment ID in URL path

### Response
- Returns `AppointmentResponse` with `video_room_url` populated
- Status: 200 OK on success

### Error Responses
- 400: Invalid consultation type (not video)
- 401: Unauthorized (no valid token)
- 403: Forbidden (not associated with appointment)
- 404: Appointment not found
- 500: Internal server error

### Video Room URL Format
```
https://video.skinguard.app/room/{unique-uuid}
```

### Database Changes
- Uses existing `video_room_url` column in `appointments` table
- Column is nullable (NULL until video room is created)

### Security Features
1. Only patient or doctor can access
2. Validates consultation type is "video"
3. Generates unique UUID for each room
4. Idempotent (returns existing URL if already created)

### Requirements Validated
- ✅ Requirement 25.1: Video consultation option available
- ✅ Requirement 25.2: Unique meeting room URL generated
