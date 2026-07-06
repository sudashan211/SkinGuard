# Health Profile Setup Flow

## Overview
After patient signup, users are now required to complete their health profile before accessing the main dashboard. This ensures we have essential medical information for accurate AI analysis.

## Implementation Details

### 1. New Route
- **Route**: `/setup-profile`
- **Component**: `HealthProfileSetupPage.tsx`
- **Access**: Protected - Patient role only

### 2. Signup Flow Changes
When a patient signs up:
1. Account is created successfully
2. User is logged in automatically
3. **NEW**: User is redirected to `/setup-profile` instead of dashboard
4. User must complete health profile to continue

### 3. Health Profile Form Fields

#### Required Fields
- **Age**: Number between 1-120 years
- **Fitzpatrick Skin Type**: Dropdown with 6 options (I-VI)
  - Type I: Very fair, always burns, never tans
  - Type II: Fair, usually burns, tans minimally
  - Type III: Medium, sometimes burns, tans uniformly
  - Type IV: Olive, rarely burns, tans easily
  - Type V: Brown, very rarely burns, tans very easily
  - Type VI: Dark brown/black, never burns, deeply pigmented

#### Optional Fields
- **Family History**: Textarea for family medical history of skin conditions

### 4. Privacy Disclaimer

A prominent disclaimer box is displayed with:

**Content:**
- Personal health information will be securely stored and encrypted
- Data used for personalized medical analysis and recommendations
- Information only shared with chosen healthcare providers
- Can update or delete information anytime
- HIPAA and GDPR compliance

**Checkbox Requirement:**
- User MUST check the agreement checkbox
- "Create Health Profile" button is disabled until checkbox is checked
- Clear error message if user tries to submit without agreement

### 5. Validation

**Frontend Validation:**
- Age: Must be between 1-120
- Skin Type: Must select one of the 6 Fitzpatrick types
- Disclaimer: Must be checked

**Backend Validation:**
- Age: 1-120 range enforced
- Skin Type: Must be valid Fitzpatrick scale value (I-VI)
- Family History: Optional, no length limit

### 6. User Experience

**Visual Design:**
- Full-screen centered card layout
- Heart icon representing health/care
- Clear section headers and descriptions
- Blue-themed privacy disclaimer box with shield icon
- Disabled state for button when disclaimer not checked
- Loading state during profile creation

**Error Handling:**
- Validation errors shown in red alert box
- Clear error messages for each validation failure
- API errors displayed to user

**Success Flow:**
- Profile created successfully
- User redirected to Patient Dashboard
- Can access all patient features

## API Endpoint

**POST** `/api/patient/profile`

**Request Body:**
```json
{
  "age": 25,
  "skin_type": "III",
  "family_history": "Mother had melanoma"
}
```

**Response:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "age": 25,
  "skin_type": "III",
  "family_history": "Mother had melanoma",
  "created_at": "2026-04-23T10:00:00Z",
  "updated_at": "2026-04-23T10:00:00Z"
}
```

## Files Modified

### Frontend
1. **frontend/src/pages/HealthProfileSetupPage.tsx** (NEW)
   - Complete health profile setup form
   - Privacy disclaimer with checkbox
   - Form validation and submission

2. **frontend/src/utils/constants.ts**
   - Added `HEALTH_PROFILE_SETUP: '/setup-profile'` route

3. **frontend/src/hooks/useAuth.ts**
   - Updated signup success handler
   - Patients now redirect to `/setup-profile` instead of dashboard

4. **frontend/src/App.tsx**
   - Added new protected route for health profile setup
   - Imported HealthProfileSetupPage component

### Backend
No backend changes required - existing `/api/patient/profile` endpoint already supports this flow.

## Future Enhancements

1. **Skip for Existing Profiles**
   - Check if patient already has a profile
   - Redirect to dashboard if profile exists
   - Useful for returning users

2. **Profile Completion Status**
   - Add flag to user profile indicating completion
   - Show banner in dashboard if profile incomplete
   - Allow users to skip and complete later

3. **Additional Fields**
   - Allergies
   - Current medications
   - Previous skin conditions
   - Sun exposure habits

4. **Multi-step Wizard**
   - Break into multiple steps for better UX
   - Progress indicator
   - Save draft functionality

## Testing

### Manual Testing Steps
1. Sign up as a new patient
2. Verify redirect to `/setup-profile`
3. Try submitting without checking disclaimer (should fail)
4. Fill in age, skin type
5. Check disclaimer checkbox
6. Submit form
7. Verify redirect to patient dashboard
8. Check that profile data is saved in database

### Edge Cases
- Invalid age values (0, 121, negative)
- Missing required fields
- Network errors during submission
- User navigates away before completing
- User tries to access dashboard without profile

## Security & Privacy

- All health data encrypted at rest
- HTTPS required for transmission
- User consent explicitly obtained via checkbox
- Clear privacy policy displayed
- User can delete data anytime from profile settings
- HIPAA and GDPR compliant storage

---

**Last Updated**: April 23, 2026
**Feature Status**: ✅ Implemented
