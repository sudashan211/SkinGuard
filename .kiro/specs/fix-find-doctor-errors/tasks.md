o# Implementation Plan

- [x] 1. Write bug condition exploration tests
  - **Property 1: Fault Condition** - Empty Database, Missing API Key, and Unauthenticated Access
  - **CRITICAL**: These tests MUST FAIL on unfixed code - failure confirms the bugs exist
  - **DO NOT attempt to fix the tests or the code when they fail**
  - **NOTE**: These tests encode the expected behavior - they will validate the fixes when they pass after implementation
  - **GOAL**: Surface counterexamples that demonstrate the three bugs exist
  - **Scoped PBT Approach**: Scope properties to concrete failing cases for reproducibility
  - Test Bug 1: `/api/doctors/nearby` with empty database crashes with 500 error (from Fault Condition in design)
  - Test Bug 2: DoctorMap with missing `VITE_GOOGLE_MAPS_API_KEY` shows InvalidKeyMapError (from Fault Condition in design)
  - Test Bug 3: Protected endpoints without authentication return 401 errors (from Fault Condition in design)
  - The test assertions should match the Expected Behavior Properties from design (empty array, friendly error, 401 with message)
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests FAIL (this is correct - it proves the bugs exist)
  - Document counterexamples found to understand root causes
  - Mark task complete when tests are written, run, and failures are documented
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2. Write preservation property tests (BEFORE implementing fixes)
  - **Property 2: Preservation** - Successful Queries, Valid API Key, and Authenticated Access
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for non-buggy inputs
  - Observe: `/api/doctors/nearby` with existing doctors returns correct doctor list
  - Observe: DoctorMap with valid `VITE_GOOGLE_MAPS_API_KEY` loads map correctly
  - Observe: Protected endpoints with valid authentication allow access
  - Write property-based tests capturing observed behavior patterns from Preservation Requirements
  - Property-based testing generates many test cases for stronger guarantees
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 3. Fix for Find Doctor errors (empty database crash, missing API key, authentication issues)

  - [x] 3.1 Fix Bug 1: Add null checks in get_nearby_doctors endpoint
    - Add early return for empty profiles: `if not profiles_result.data or len(profiles_result.data) == 0: return []`
    - Add early return for empty doctors: `if not doctors_result.data or len(doctors_result.data) == 0: return []`
    - Verify all attribute accesses on query results are protected by null checks
    - _Bug_Condition: isBugCondition1(input) where verifiedDoctorsQuery.data IS NULL OR length == 0_
    - _Expected_Behavior: Return empty array [] with HTTP 200 status without crashing (Property 1)_
    - _Preservation: Continue to return doctor list when doctors exist (Property 4)_
    - _Requirements: 1.1, 2.1, 3.1_

  - [x] 3.2 Fix Bug 2: Add API key validation in DoctorMap component
    - Add API key validation before rendering map: check if GOOGLE_MAPS_API_KEY is empty or null
    - Display user-friendly error message with specific instructions: "Please set VITE_GOOGLE_MAPS_API_KEY in your .env file"
    - Add early return to prevent useJsApiLoader from being called with empty API key
    - Include guidance on where to obtain a Google Maps API key
    - _Bug_Condition: isBugCondition2(input) where VITE_GOOGLE_MAPS_API_KEY IS NULL OR empty_
    - _Expected_Behavior: Display friendly error message with configuration instructions (Property 2)_
    - _Preservation: Continue to load map correctly when API key is valid (Property 5)_
    - _Requirements: 1.2, 2.2, 3.2, 3.4, 3.5_

  - [x] 3.3 Fix Bug 3: Verify authentication dependencies on protected endpoints
    - Verify `/api/doctors/register` uses `Depends(get_current_doctor)`
    - Verify `/api/doctors/reports/pending` uses `Depends(get_current_verified_doctor)`
    - Ensure dependencies are properly imported and configured
    - Review that dependency functions properly raise 401 errors for missing/invalid tokens
    - _Bug_Condition: isBugCondition3(input) where authToken IS NULL OR INVALID_
    - _Expected_Behavior: Return 401 Unauthorized with clear error message (Property 3)_
    - _Preservation: Continue to allow access with valid authentication (Property 6)_
    - _Requirements: 1.3, 2.3, 3.3_

  - [x] 3.4 Verify bug condition exploration tests now pass
    - **Property 1: Expected Behavior** - Empty Database, Missing API Key, and Unauthenticated Access
    - **IMPORTANT**: Re-run the SAME tests from task 1 - do NOT write new tests
    - The tests from task 1 encode the expected behavior
    - When these tests pass, it confirms the expected behavior is satisfied
    - Run bug condition exploration tests from step 1
    - **EXPECTED OUTCOME**: Tests PASS (confirms bugs are fixed)
    - _Requirements: 2.1, 2.2, 2.3_

  - [x] 3.5 Verify preservation tests still pass
    - **Property 2: Preservation** - Successful Queries, Valid API Key, and Authenticated Access
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run preservation property tests from step 2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all tests still pass after fixes (no regressions)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
