# WhatsApp Integration Documentation

## Overview

The WhatsApp integration feature allows patients to contact doctors directly through WhatsApp with a pre-filled message. This is part of the Doctor Locator System (Task 12).

**Requirements**: 7.5  
**Property**: Property 20 - WhatsApp URL Format

## Implementation

### Location

The WhatsApp URL generation is implemented in the `DoctorResponse` model:

- **File**: `backend/app/models.py`
- **Class**: `DoctorResponse`
- **Method**: `get_whatsapp_url(message: str = "I would like to share my Derman Report") -> str`

### How It Works

1. **Automatic Generation**: When a `DoctorResponse` object is created, the `whatsapp_url` field is automatically populated by calling `get_whatsapp_url()` in the `__init__` method.

2. **URL Format**: The generated URL follows the WhatsApp web/app URL scheme:
   ```
   https://wa.me/{phone_number}?text={url_encoded_message}
   ```

3. **Phone Number Formatting**: The method automatically removes the '+' prefix from phone numbers, as required by the `wa.me` URL format.

4. **Message Encoding**: Messages are properly URL-encoded using `urllib.parse.quote()` to handle spaces and special characters.

### Code Example

```python
from app.models import DoctorResponse

# Create a doctor response
doctor = DoctorResponse(
    id="...",
    user_id="...",
    license_no="LIC123456",
    clinic_name="City Dermatology Clinic",
    lat=40.7128,
    lng=-74.0060,
    whatsapp_no="+12125551234",
    specialization="Dermatology",
    average_rating=4.5,
    review_count=100,
    verified=True,
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow()
)

# WhatsApp URL is automatically available
print(doctor.whatsapp_url)
# Output: https://wa.me/12125551234?text=I%20would%20like%20to%20share%20my%20Derman%20Report

# Generate URL with custom message
custom_url = doctor.get_whatsapp_url(message="Hello, I need a consultation")
print(custom_url)
# Output: https://wa.me/12125551234?text=Hello%2C%20I%20need%20a%20consultation
```

## API Integration

### Doctor Locator Endpoint

The WhatsApp URL is automatically included in the response from the `/api/doctors/nearby` endpoint:

```python
GET /api/doctors/nearby?lat=40.7128&lng=-74.0060&radius=50
```

**Response**:
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "123e4567-e89b-12d3-a456-426614174001",
    "license_no": "LIC123456",
    "clinic_name": "City Dermatology Clinic",
    "lat": 40.7128,
    "lng": -74.0060,
    "whatsapp_no": "+12125551234",
    "whatsapp_url": "https://wa.me/12125551234?text=I%20would%20like%20to%20share%20my%20Derman%20Report",
    "specialization": "Dermatology",
    "average_rating": 4.5,
    "review_count": 100,
    "verified": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

## Frontend Usage

In the frontend, you can use the `whatsapp_url` directly:

```typescript
// React component example
function DoctorCard({ doctor }: { doctor: Doctor }) {
  return (
    <div className="doctor-card">
      <h3>{doctor.clinic_name}</h3>
      <p>Rating: {doctor.average_rating} ⭐</p>
      
      {/* WhatsApp contact button */}
      <a 
        href={doctor.whatsapp_url}
        target="_blank"
        rel="noopener noreferrer"
        className="whatsapp-button"
      >
        <WhatsAppIcon />
        Contact via WhatsApp
      </a>
    </div>
  );
}
```

## Features

### ✅ Automatic URL Generation
- URLs are generated automatically when `DoctorResponse` objects are created
- No manual URL construction needed

### ✅ Phone Number Normalization
- Handles phone numbers with or without '+' prefix
- Automatically removes '+' for `wa.me` format
- Supports international phone numbers

### ✅ Message Encoding
- Properly URL-encodes messages
- Handles spaces, special characters, and punctuation
- Default message: "I would like to share my Derman Report"

### ✅ Custom Messages
- Supports custom messages via `get_whatsapp_url(message=...)`
- Useful for different contexts (urgent consultations, follow-ups, etc.)

## Testing

### Property-Based Tests
Location: `tests/property/test_whatsapp_url_property.py`

Tests verify:
- ✅ URL format correctness (https://wa.me/{number}?text={message})
- ✅ Phone number formatting ('+' prefix removal)
- ✅ Message URL encoding
- ✅ Default message presence
- ✅ Custom message support
- ✅ International phone numbers
- ✅ URL validity and parseability

**Status**: All property tests passing (100 examples per test)

### Unit Tests
Location: `tests/unit/test_whatsapp_url_generation.py`

Tests cover:
- ✅ Basic URL generation
- ✅ Phone numbers with/without '+' prefix
- ✅ Custom messages
- ✅ International numbers (UK, India, Brazil, Japan, South Africa)
- ✅ Special character encoding
- ✅ Default message verification

**Status**: All unit tests passing (6 tests)

## Demo

Run the demo script to see examples:

```bash
python examples/whatsapp_url_demo.py
```

This demonstrates:
- Basic doctor profile with WhatsApp URL
- International doctor example
- Custom message generation
- Phone numbers without '+' prefix

## Requirements Validation

**Requirement 7.5**: ✅ VALIDATED

> WHEN a patient clicks the WhatsApp button THEN the System SHALL generate a URL with format "https://wa.me/{whatsapp_no}?text=I would like to share my Derman Report"

**Property 20**: ✅ VALIDATED

> For any doctor's WhatsApp contact, the generated URL should match the format "https://wa.me/{whatsapp_no}?text=I would like to share my Derman Report" where {whatsapp_no} is the doctor's WhatsApp number.

## Implementation Status

- ✅ Task 12.3: Implement WhatsApp integration - **COMPLETED**
- ✅ Task 12.4: Write property test for WhatsApp URL format - **COMPLETED**
- ✅ Property 20: WhatsApp URL Format - **PASSING**

## Notes

1. **Security**: The implementation uses `urllib.parse.quote()` for proper URL encoding, preventing injection attacks.

2. **Compatibility**: The `wa.me` URL format works on:
   - WhatsApp Web (desktop browsers)
   - WhatsApp mobile app (iOS and Android)
   - Opens WhatsApp automatically if installed

3. **User Experience**: When a patient clicks the WhatsApp URL:
   - WhatsApp opens automatically
   - The doctor's contact is pre-selected
   - The message is pre-filled
   - Patient just needs to press "Send"

4. **Extensibility**: The `get_whatsapp_url()` method can be called with custom messages for different use cases (urgent consultations, follow-ups, appointment confirmations, etc.).
