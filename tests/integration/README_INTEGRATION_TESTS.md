# Integration Tests - Complete User Journeys

## Overview

This directory contains integration tests for the three main user journeys in the SkinGuard platform:

1. **Patient Journey** - Complete flow from signup to appointment booking
2. **Doctor Journey** - Registration, verification, and patient management
3. **Admin Journey** - Doctor verification and content moderation

## Test Files

### 1. test_patient_journey.py

Tests the complete patient flow:
- **Step 1**: Patient Signup
- **Step 2**: Patient Login
- **Step 3**: Create Patient Health Profile
- **Step 4**: Upload Image for Analysis
- **Step 5**: View AI Results
- **Step 6**: Find Nearby Doctors
- **Step 7**: Book Appointment
- **Step 8**: Verify Appointment in List

**Requirements Validated**: All patient-related requirements (1.1-1.6, 2.1-2.5, 4.1-4.6, 7.1-7.6, 8.1-8.3, 15.1-15.6)

### 2. test_doctor_journey.py

Tests the complete doctor flow:
- **Step 1**: Doctor Registration
- **Step 2**: Verify Unverified Doctor Cannot Access Reports
- **Step 3**: Admin Verification
- **Step 4**: Login as Verified Doctor
- **Step 5**: View Pending Reports
- **Step 6**: Add Consultation Notes
- **Step 7**: Create Appointment
- **Step 8**: Doctor Views Appointments
- **Step 9**: Doctor Updates Appointment Status

**Requirements Validated**: All doctor-related requirements (6.1-6.6, 9.1-9.5, 8.4-8.5)

### 3. test_admin_journey.py

Tests the complete admin flow:
- **Step 1**: Admin Login
- **Step 2**: View Pending Doctor Applications
- **Step 3**: Verify Doctor (Approve)
- **Step 4**: Reject Doctor Application
- **Step 5**: View Flagged Content
- **Step 6**: Review Flagged Content Details
- **Step 7**: Moderate Content
- **Step 8**: Verify Pending List Updated
- **Step 9**: View Platform Analytics
- **Step 10**: Verify Admin Access Control

**Requirements Validated**: All admin-related requirements (10.1-10.5, 6.3-6.4, 3.6)

## Running the Tests

### Prerequisites

1. Ensure the test database is set up (see `tests/SETUP_DATABASE.md`)
2. Environment variables are configured in `tests/.env`
3. Backend server dependencies are installed

### Run All Integration Tests

```bash
cd tests
python -m pytest integration/ -v -s -m integration
```

### Run Specific Journey Test

```bash
# Patient journey
python -m pytest integration/test_patient_journey.py -v -s

# Doctor journey
python -m pytest integration/test_doctor_journey.py -v -s

# Admin journey
python -m pytest integration/test_admin_journey.py -v -s
```

### Run with Coverage

```bash
python -m pytest integration/ -v --cov=app --cov-report=html
```

## Test Structure

Each integration test follows this pattern:

1. **Setup**: Create test data and authentication tokens
2. **Execute**: Run through the complete user journey step-by-step
3. **Assert**: Verify each step produces expected results
4. **Cleanup**: Remove all test data from database

### Cleanup Fixture

All tests use a `cleanup_test_data` fixture that:
- Tracks created user IDs, doctor IDs, report IDs, and appointment IDs
- Automatically cleans up all test data after test completion
- Ensures no test data pollution between test runs

## Key Features

### 1. End-to-End Validation

Tests validate complete workflows across multiple API endpoints and database tables, ensuring:
- Data flows correctly between components
- Foreign key relationships are maintained
- Business logic is enforced across the journey

### 2. Role-Based Access Control

Tests verify that:
- Patients can only access patient endpoints
- Unverified doctors cannot access reports
- Verified doctors can access reports and appointments
- Admins can access all admin endpoints
- Non-admin users are blocked from admin endpoints

### 3. Data Persistence

Tests verify that:
- Profile updates persist to database
- Medical reports are stored correctly
- Consultation notes are saved
- Appointment status changes persist

### 4. Business Logic Validation

Tests verify that:
- Doctors must be verified before accessing reports
- Appointments require verified doctors
- Flagged content appears in admin moderation queue
- Pending doctors appear in admin verification list

## Test Data

### Test Users

Each test creates temporary users with unique UUIDs:
- **Patients**: `patient_<uuid>@test.com`
- **Doctors**: `doctor_<uuid>@test.com`
- **Admins**: Use JWT tokens with admin role

### Test Medical Reports

Mock medical reports include:
- 7 cancer type predictions (as per requirements)
- Hotspot data for lesion localization
- Patient symptoms
- Risk level classification

### Test Appointments

Appointments are created with:
- Future scheduled dates (7 days from now)
- Both in-person and video consultation types
- Initial "pending" status

## Troubleshooting

### TestClient Import Error

If you encounter:
```
TypeError: Client.__init__() got an unexpected keyword argument 'app'
```

This is a known compatibility issue between httpx and starlette versions. Solutions:

1. **Update dependencies**:
   ```bash
   pip install --upgrade httpx starlette fastapi
   ```

2. **Pin compatible versions** in `requirements.txt`:
   ```
   httpx==0.24.1
   starlette==0.27.0
   fastapi==0.100.0
   ```

### Database Connection Issues

If tests fail with database errors:

1. Verify Supabase credentials in `tests/.env`
2. Check database is accessible
3. Ensure tables are created (run migrations)

### Cleanup Issues

If test data is not cleaned up:

1. Manually clean test data:
   ```sql
   DELETE FROM appointments WHERE patient_id LIKE 'patient_%';
   DELETE FROM medical_reports WHERE patient_id LIKE 'patient_%';
   DELETE FROM doctors WHERE user_id LIKE 'doctor_%';
   DELETE FROM profiles WHERE email LIKE '%@test.com';
   ```

2. Check fixture is properly yielding before cleanup

## Integration with CI/CD

These tests are designed to run in CI/CD pipelines:

```yaml
# .github/workflows/integration-tests.yml
name: Integration Tests
on: [push, pull_request]

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install -r tests/requirements.txt
      - name: Run integration tests
        run: |
          cd tests
          python -m pytest integration/ -v -m integration
```

## Success Criteria

Integration tests are considered successful when:

✅ All three journey tests pass  
✅ No test data remains in database after cleanup  
✅ All API endpoints respond with correct status codes  
✅ Data persists correctly across requests  
✅ Role-based access control is enforced  
✅ Business logic rules are validated  

## Next Steps

After integration tests pass:

1. Run E2E tests with Playwright (frontend + backend)
2. Perform load testing with Locust
3. Run security audit with OWASP ZAP
4. Verify performance metrics meet targets

## Related Documentation

- `PHASE_17_TESTING_STRATEGY.md` - Overall testing strategy
- `tests/SETUP_DATABASE.md` - Database setup instructions
- `tests/property/README_*.md` - Property-based test documentation
- `.kiro/specs/derman-ai-skin-screening/requirements.md` - Requirements specification
- `.kiro/specs/derman-ai-skin-screening/design.md` - Design specification

## Task Completion

**Task**: 36.2 Write integration tests  
**Status**: ✅ Complete  
**Files Created**:
- `test_patient_journey.py` - Patient flow integration test
- `test_doctor_journey.py` - Doctor flow integration test
- `test_admin_journey.py` - Admin flow integration test
- `README_INTEGRATION_TESTS.md` - This documentation

**Requirements Validated**: All requirements (complete user journeys)
