# Find Doctor Errors Bugfix Design

## Overview

The Find Doctor feature has three critical bugs that prevent users from viewing nearby doctors. The first bug causes a 500 Internal Server Error when the `/api/doctors/nearby` endpoint is called with no doctors in the database, due to attempting to access attributes on None values. The second bug causes Google Maps to fail loading with "InvalidKeyMapError" when the `VITE_GOOGLE_MAPS_API_KEY` environment variable is not configured. The third bug causes 401 Unauthorized errors on protected doctor endpoints because authentication dependencies are missing or incorrectly configured.

The fix strategy involves: (1) adding proper null checks in the nearby doctors endpoint to return empty arrays gracefully, (2) adding API key validation in the DoctorMap component to display user-friendly error messages, and (3) ensuring all protected doctor endpoints use the correct authentication dependencies.

## Glossary

- **Bug_Condition (C)**: The conditions that trigger the three bugs - empty database queries, missing API keys, and missing authentication
- **Property (P)**: The desired behavior - graceful empty responses, user-friendly error messages, and proper authentication enforcement
- **Preservation**: Existing functionality that must remain unchanged - successful doctor queries, working maps with valid keys, and authenticated access
- **get_nearby_doctors**: The endpoint in `backend/app/routers/doctors.py` that returns verified doctors within a radius
- **DoctorMap**: The React component in `frontend/src/components/patient/DoctorMap.tsx` that displays the Google Maps interface
- **get_current_doctor**: Dependency function that validates doctor role authentication
- **get_current_verified_doctor**: Dependency function that validates verified doctor role authentication

## Bug Details

### Fault Condition

The bugs manifest in three distinct scenarios:

**Bug 1 - Nearby Doctors Crash**: When the `/api/doctors/nearby` endpoint is called and no verified doctors exist in the database, the code attempts to access attributes on None values from empty query results, causing a 500 Internal Server Error.

**Bug 2 - Google Maps API Key**: When the DoctorMap component loads and the `VITE_GOOGLE_MAPS_API_KEY` environment variable is not set or is empty, Google Maps fails to load with "InvalidKeyMapError" and displays a generic error message.

**Bug 3 - Authentication Missing**: When users access protected doctor endpoints like `/api/doctors/register` or `/api/doctors/reports/pending` without proper authentication, the system returns 401 Unauthorized errors because the authentication dependencies are not properly enforced.

**Formal Specification:**
```
FUNCTION isBugCondition1(input)
  INPUT: input of type NearbyDoctorsRequest with {lat, lng, radius}
  OUTPUT: boolean
  
  RETURN (verifiedDoctorsQuery.data IS NULL OR verifiedDoctorsQuery.data.length == 0)
         AND codeAttemptsToAccessAttributes(verifiedDoctorsQuery.data)
END FUNCTION

FUNCTION isBugCondition2(input)
  INPUT: input of type ComponentLoad
  OUTPUT: boolean
  
  RETURN (VITE_GOOGLE_MAPS_API_KEY IS NULL OR VITE_GOOGLE_MAPS_API_KEY == '')
         AND googleMapsApiLoader.isInvoked()
END FUNCTION

FUNCTION isBugCondition3(input)
  INPUT: input of type HTTPRequest to protected doctor endpoint
  OUTPUT: boolean
  
  RETURN input.endpoint IN ['/api/doctors/register', '/api/doctors/reports/pending']
         AND (input.authToken IS NULL OR input.authToken IS INVALID)
         AND authenticationDependencyNotEnforced()
END FUNCTION
```

### Examples

**Bug 1 Examples:**
- User opens doctor map in a new deployment with no doctors registered → 500 Internal Server Error
- User searches for doctors in a remote area with no verified doctors → 500 Internal Server Error
- Admin deletes all doctors for testing → subsequent searches crash with 500 error

**Bug 2 Examples:**
- Developer clones repo without setting up `.env` file → "InvalidKeyMapError" displayed
- Production deployment with missing environment variable → Google Maps fails to load
- User sees generic "Error loading Google Maps" without guidance on how to fix it

**Bug 3 Examples:**
- Unauthenticated user tries to access `/api/doctors/register` → 401 Unauthorized
- User with expired token tries to view `/api/doctors/reports/pending` → 401 Unauthorized
- Patient user (non-doctor) tries to access doctor-only endpoints → 401 Unauthorized

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- When verified doctors exist in the database, the `/api/doctors/nearby` endpoint must continue to return the list of doctors with all their details
- When the `VITE_GOOGLE_MAPS_API_KEY` is properly configured, the DoctorMap component must continue to display the Google Maps interface with doctor markers
- When authenticated doctor users access protected endpoints with valid credentials, the system must continue to allow access and return the requested data
- When users interact with doctor markers on the map, the system must continue to display info windows with WhatsApp contact and appointment booking options
- When users request their geolocation and it's available, the system must continue to center the map on the user's location

**Scope:**
All inputs that do NOT involve empty databases, missing API keys, or missing authentication should be completely unaffected by this fix. This includes:
- Successful doctor queries with results
- Map loading with valid API keys
- Authenticated requests with valid tokens
- All other doctor-related functionality (registration, consultation notes, etc.)

## Hypothesized Root Cause

Based on the bug description and code analysis, the most likely issues are:

1. **Bug 1 - Null Reference Error**: The `get_nearby_doctors` function does not properly handle the case when no verified doctors exist
   - The code queries for verified profiles and doctor records
   - When no results are found, it may attempt to iterate over None or empty results
   - The code does not return early with an empty array when no doctors are found

2. **Bug 2 - Missing API Key Validation**: The DoctorMap component does not validate the API key before attempting to load Google Maps
   - The component uses `import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ''` which defaults to empty string
   - The `useJsApiLoader` hook is called with an empty API key
   - The `loadError` handler displays a generic error message without specific guidance

3. **Bug 3 - Authentication Dependency Issues**: Protected doctor endpoints may not have the correct authentication dependencies
   - The `/api/doctors/register` endpoint uses `get_current_doctor` dependency
   - The `/api/doctors/reports/pending` endpoint uses `get_current_verified_doctor` dependency
   - These dependencies may not be properly configured or may be missing from some endpoints

## Correctness Properties

Property 1: Fault Condition - Empty Database Graceful Handling

_For any_ request to `/api/doctors/nearby` where no verified doctors exist in the database (isBugCondition1 returns true), the fixed endpoint SHALL return an empty array `[]` with HTTP 200 status without crashing or attempting to access attributes on None values.

**Validates: Requirements 2.1**

Property 2: Fault Condition - API Key Validation and User Guidance

_For any_ DoctorMap component load where the `VITE_GOOGLE_MAPS_API_KEY` environment variable is not set or is empty (isBugCondition2 returns true), the fixed component SHALL display a user-friendly error message instructing users to configure the Google Maps API key in their environment variables, instead of showing a generic error.

**Validates: Requirements 2.2**

Property 3: Fault Condition - Authentication Enforcement

_For any_ request to protected doctor endpoints where authentication is missing or invalid (isBugCondition3 returns true), the fixed endpoints SHALL return 401 Unauthorized with a clear error message indicating that authentication is required, ensuring proper security enforcement.

**Validates: Requirements 2.3**

Property 4: Preservation - Successful Doctor Queries

_For any_ request to `/api/doctors/nearby` where verified doctors exist in the database (NOT isBugCondition1), the fixed endpoint SHALL produce exactly the same result as the original endpoint, returning the list of nearby doctors with their complete details (clinic name, location, rating, etc.).

**Validates: Requirements 3.1**

Property 5: Preservation - Map Loading with Valid API Key

_For any_ DoctorMap component load where the `VITE_GOOGLE_MAPS_API_KEY` is properly configured (NOT isBugCondition2), the fixed component SHALL produce exactly the same behavior as the original component, displaying the Google Maps interface with doctor markers and user location.

**Validates: Requirements 3.2, 3.4, 3.5**

Property 6: Preservation - Authenticated Access

_For any_ request to protected doctor endpoints with valid authentication credentials (NOT isBugCondition3), the fixed endpoints SHALL produce exactly the same result as the original endpoints, allowing access and returning the requested data.

**Validates: Requirements 3.3**

## Fix Implementation

### Changes Required

Assuming our root cause analysis is correct:

**File 1**: `backend/app/routers/doctors.py`

**Function**: `get_nearby_doctors`

**Specific Changes**:
1. **Add Early Return for Empty Profiles**: After querying verified profiles, check if the result is empty and return `[]` immediately
   - Add check: `if not profiles_result.data or len(profiles_result.data) == 0: return []`
   - This prevents attempting to access attributes on None values

2. **Add Early Return for Empty Doctors**: After querying doctor records, check if the result is empty and return `[]` immediately
   - Add check: `if not doctors_result.data or len(doctors_result.data) == 0: return []`
   - This ensures graceful handling when no doctors match the verified profiles

3. **Verify Null Safety**: Ensure all attribute accesses on query results are protected by null checks
   - Review all uses of `profiles_result.data` and `doctors_result.data`
   - Ensure no direct attribute access without null checks

**File 2**: `frontend/src/components/patient/DoctorMap.tsx`

**Component**: `DoctorMap`

**Specific Changes**:
1. **Add API Key Validation**: Before rendering the map, check if the API key is configured
   - Add validation: `if (!GOOGLE_MAPS_API_KEY || GOOGLE_MAPS_API_KEY.trim() === '')`
   - Display user-friendly error message with configuration instructions

2. **Improve Error Message**: Update the error display to provide specific guidance
   - Change from generic "Please check your API key configuration"
   - To specific "Please set VITE_GOOGLE_MAPS_API_KEY in your .env file"
   - Include instructions on where to obtain a Google Maps API key

3. **Add Early Return**: Prevent the `useJsApiLoader` hook from being called with an empty API key
   - Return error UI before the hook is invoked
   - This prevents the "InvalidKeyMapError" from occurring

**File 3**: `backend/app/routers/doctors.py`

**Endpoints**: `/api/doctors/register` and `/api/doctors/reports/pending`

**Specific Changes**:
1. **Verify Authentication Dependencies**: Ensure all protected endpoints use the correct authentication dependencies
   - `/api/doctors/register` should use `Depends(get_current_doctor)`
   - `/api/doctors/reports/pending` should use `Depends(get_current_verified_doctor)`
   - Verify these dependencies are properly imported and configured

2. **Review Dependency Functions**: Check that `get_current_doctor` and `get_current_verified_doctor` properly raise 401 errors
   - Ensure they validate JWT tokens correctly
   - Ensure they return proper error responses for missing or invalid tokens

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bugs on unfixed code, then verify the fixes work correctly and preserve existing behavior.

### Exploratory Fault Condition Checking

**Goal**: Surface counterexamples that demonstrate the bugs BEFORE implementing the fix. Confirm or refute the root cause analysis. If we refute, we will need to re-hypothesize.

**Test Plan**: Write tests that simulate the three bug conditions and observe failures on the UNFIXED code to understand the root causes.

**Test Cases**:
1. **Empty Database Test**: Call `/api/doctors/nearby` with valid coordinates when no doctors exist in the database (will fail with 500 error on unfixed code)
2. **Missing API Key Test**: Load DoctorMap component with empty `VITE_GOOGLE_MAPS_API_KEY` (will show InvalidKeyMapError on unfixed code)
3. **Unauthenticated Request Test**: Call `/api/doctors/register` without authentication token (will fail with 401 on unfixed code)
4. **Invalid Token Test**: Call `/api/doctors/reports/pending` with expired or invalid token (will fail with 401 on unfixed code)

**Expected Counterexamples**:
- 500 Internal Server Error when querying nearby doctors with empty database
- "InvalidKeyMapError" displayed when Google Maps API key is missing
- 401 Unauthorized errors when accessing protected endpoints without authentication
- Possible causes: missing null checks, missing API key validation, missing authentication dependencies

### Fix Checking

**Goal**: Verify that for all inputs where the bug conditions hold, the fixed functions produce the expected behavior.

**Pseudocode:**
```
FOR ALL input WHERE isBugCondition1(input) DO
  result := get_nearby_doctors_fixed(input)
  ASSERT result == [] AND statusCode == 200
END FOR

FOR ALL input WHERE isBugCondition2(input) DO
  result := DoctorMap_fixed(input)
  ASSERT result.displaysFriendlyErrorMessage()
  ASSERT result.providesConfigurationInstructions()
END FOR

FOR ALL input WHERE isBugCondition3(input) DO
  result := protectedEndpoint_fixed(input)
  ASSERT statusCode == 401
  ASSERT result.errorMessage.contains("authentication required")
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug conditions do NOT hold, the fixed functions produce the same results as the original functions.

**Pseudocode:**
```
FOR ALL input WHERE NOT isBugCondition1(input) DO
  ASSERT get_nearby_doctors_original(input) = get_nearby_doctors_fixed(input)
END FOR

FOR ALL input WHERE NOT isBugCondition2(input) DO
  ASSERT DoctorMap_original(input) = DoctorMap_fixed(input)
END FOR

FOR ALL input WHERE NOT isBugCondition3(input) DO
  ASSERT protectedEndpoint_original(input) = protectedEndpoint_fixed(input)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain
- It catches edge cases that manual unit tests might miss
- It provides strong guarantees that behavior is unchanged for all non-buggy inputs

**Test Plan**: Observe behavior on UNFIXED code first for successful scenarios, then write property-based tests capturing that behavior.

**Test Cases**:
1. **Successful Doctor Query Preservation**: Observe that querying nearby doctors with existing doctors works correctly on unfixed code, then write test to verify this continues after fix
2. **Map Loading Preservation**: Observe that DoctorMap loads correctly with valid API key on unfixed code, then write test to verify this continues after fix
3. **Authenticated Access Preservation**: Observe that authenticated requests work correctly on unfixed code, then write test to verify this continues after fix
4. **Map Interaction Preservation**: Verify that clicking markers, viewing info windows, and booking appointments continue to work after fix

### Unit Tests

- Test `/api/doctors/nearby` endpoint with empty database returns empty array
- Test `/api/doctors/nearby` endpoint with existing doctors returns correct results
- Test DoctorMap component with missing API key displays error message
- Test DoctorMap component with valid API key loads map correctly
- Test protected endpoints with missing authentication return 401
- Test protected endpoints with valid authentication return correct data
- Test edge cases: invalid coordinates, negative radius, malformed tokens

### Property-Based Tests

- Generate random coordinates and verify `/api/doctors/nearby` never crashes regardless of database state
- Generate random API key configurations and verify DoctorMap always displays appropriate UI (error or map)
- Generate random authentication states and verify protected endpoints always enforce authentication correctly
- Test that all successful scenarios continue to work across many random inputs

### Integration Tests

- Test full user flow: open doctor map → request location → fetch nearby doctors → display on map
- Test doctor registration flow: authenticate → register → verify profile created
- Test consultation flow: authenticate as doctor → view pending reports → add notes
- Test error recovery: start with missing API key → configure key → reload → map loads successfully
