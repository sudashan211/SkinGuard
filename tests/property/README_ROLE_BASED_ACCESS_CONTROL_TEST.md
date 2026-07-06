# Property Test: Role-Based Access Control

## Overview

This document describes the property-based test for **Property 4: Role-Based Access Control**.

**Property Statement:**
> For any user with a specific role, access to endpoints should match their role permissions: patients access diagnostic features, unverified doctors are blocked from reports, verified doctors access reports, and admins access moderation features.

**Validates:** Requirements 1.4, 1.5, 1.6, 6.5, 6.6

## Test Location

- **File:** `tests/property/test_database_properties.py`
- **Function:** `test_role_based_access_control`

## What This Test Does

The test verifies that role-based access control is properly enforced by:

1. **Generating random test data** using Hypothesis:
   - Three unique email addresses (for patient, doctor, admin)
   - Full names (2-100 characters)

2. **Creating three user profiles** with different roles:
   - Patient (role='patient', verified=False)
   - Unverified Doctor (role='doctor', verified=False)
   - Admin (role='admin', verified=True)

3. **Creating JWT tokens** for each user with their role and verification status

4. **Testing patient access control**:
   - ✅ Patient CAN access patient endpoints (`get_current_patient`)
   - ❌ Patient CANNOT access doctor endpoints (`get_current_doctor`)
   - ❌ Patient CANNOT access admin endpoints (`get_current_admin`)

5. **Testing unverified doctor access control**:
   - ✅ Unverified doctor CAN access doctor endpoints (`get_current_doctor`)
   - ❌ Unverified doctor CANNOT access verified doctor endpoints (`get_current_verified_doctor`)
   - ❌ Unverified doctor CANNOT access patient endpoints
   - ❌ Unverified doctor CANNOT access admin endpoints

6. **Testing verified doctor access control**:
   - Update doctor's verified status to True
   - Create new token with verified=True
   - ✅ Verified doctor CAN access verified doctor endpoints (reports)
   - ✅ Verified doctor maintains access to regular doctor endpoints

7. **Testing admin access control**:
   - ✅ Admin CAN access admin endpoints (`get_current_admin`)
   - ❌ Admin CANNOT access patient endpoints
   - ❌ Admin CANNOT access doctor endpoints

## Access Control Matrix

| User Role | Patient Endpoints | Doctor Endpoints | Verified Doctor Endpoints | Admin Endpoints |
|-----------|------------------|------------------|---------------------------|-----------------|
| Patient | ✅ Allowed | ❌ Forbidden (403) | ❌ Forbidden (403) | ❌ Forbidden (403) |
| Unverified Doctor | ❌ Forbidden (403) | ✅ Allowed | ❌ Forbidden (403) | ❌ Forbidden (403) |
| Verified Doctor | ❌ Forbidden (403) | ✅ Allowed | ✅ Allowed | ❌ Forbidden (403) |
| Admin | ❌ Forbidden (403) | ❌ Forbidden (403) | ❌ Forbidden (403) | ✅ Allowed |

## Running the Test

### Prerequisites

1. **Database Setup:**
   - Supabase project created
   - Database migrations applied (see `database/migrations/`)
   - Database accessible

2. **Environment Configuration:**
   Create a `.env` file in the project root:
   ```env
   DATABASE_URL=postgresql://postgres:[password]@db.your-project.supabase.co:5432/postgres
   JWT_SECRET_KEY=your-secret-key-here
   JWT_ALGORITHM=HS256
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

3. **Dependencies Installed:**
   ```bash
   pip install -r tests/requirements.txt
   pip install -r backend/requirements.txt
   ```

### Run the Test

```bash
# Run just this test
python -m pytest tests/property/test_database_properties.py::test_role_based_access_control -v

# Run with more examples (thorough testing)
python -m pytest tests/property/test_database_properties.py::test_role_based_access_control -v --hypothesis-profile=thorough

# Run all authorization property tests
python -m pytest tests/property/ -k "access_control" -v
```

### Expected Output

When the test runs successfully:

```
tests/property/test_database_properties.py::test_role_based_access_control PASSED [100%]

====== 1 passed in X.XXs ======
```

The test will run 100 examples by default (configurable via Hypothesis settings).

## Test Behavior

### Test Isolation

- Each test runs in a **transaction**
- Changes are **automatically rolled back** after each test
- No test data persists in the database
- Tests can run in parallel without conflicts

### Random Data Generation

The test uses Hypothesis to generate random but valid data:

```python
# Example generated data:
patient_email = "patient123@example.com"
doctor_email = "doctor456@test.com"
admin_email = "admin789@demo.org"
full_name = "John Doe"
```

Hypothesis ensures the three emails are unique and will try to find edge cases.

### What Gets Tested

For **100 random examples**, the test verifies:
- Role-based access control is enforced for all roles
- Patients can only access patient features
- Unverified doctors cannot access patient reports
- Verified doctors can access patient reports
- Admins can only access admin features
- HTTP 403 Forbidden is returned for unauthorized access
- Error messages clearly indicate role requirements
- Verification status is properly checked for doctors

## Key Components Tested

### 1. Patient Access Control (`get_current_patient`)
- Allows users with role='patient'
- Blocks users with role='doctor' or role='admin'
- Returns HTTP 403 with appropriate error message

### 2. Doctor Access Control (`get_current_doctor`)
- Allows users with role='doctor' (regardless of verification)
- Blocks users with role='patient' or role='admin'
- Returns HTTP 403 with appropriate error message

### 3. Verified Doctor Access Control (`get_current_verified_doctor`)
- Allows users with role='doctor' AND verified=True
- Blocks users with role='doctor' AND verified=False
- Blocks users with other roles
- Returns HTTP 403 with verification requirement message

### 4. Admin Access Control (`get_current_admin`)
- Allows users with role='admin'
- Blocks users with role='patient' or role='doctor'
- Returns HTTP 403 with appropriate error message

## Security Implications

This test ensures:
- **Role Isolation**: Each role can only access their designated endpoints
- **Verification Enforcement**: Unverified doctors cannot access sensitive patient reports
- **Privilege Escalation Prevention**: Users cannot access higher-privilege endpoints
- **Clear Error Messages**: Users understand why access is denied
- **Token-Based Authorization**: JWT tokens correctly encode and enforce role information

## Troubleshooting

### Test Skipped

```
SKIPPED (DATABASE_URL not set - skipping database tests)
```

**Solution:** Set the `DATABASE_URL` environment variable in a `.env` file.

### Connection Error

```
psycopg2.OperationalError: could not connect to server
```

**Solution:** 
- Verify database is running
- Check DATABASE_URL is correct
- Ensure network access to database

### Import Error

```
ModuleNotFoundError: No module named 'app'
```

**Solution:** 
- Ensure you're running from the project root
- Install backend dependencies: `pip install -r backend/requirements.txt`
- Add backend to Python path: `export PYTHONPATH="${PYTHONPATH}:${PWD}/backend"`

### JWT Configuration Error

```
KeyError: 'JWT_SECRET_KEY'
```

**Solution:** 
- Set JWT_SECRET_KEY in environment variables
- Generate a secure key: `openssl rand -hex 32`
- Add to .env file

### Test Failure

If the test fails, Hypothesis will show the **exact input** that caused the failure:

```
Falsifying example: test_role_based_access_control(
    db_cursor=<cursor>,
    patient_email='patient@example.com',
    doctor_email='doctor@example.com',
    admin_email='admin@example.com',
    full_name='Test User'
)
```

This helps identify the specific case that breaks role-based access control.

## Integration with CI/CD

This test should run in your CI/CD pipeline:

```yaml
# .github/workflows/test.yml
- name: Run role-based access control property tests
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
    JWT_SECRET_KEY: ${{ secrets.JWT_SECRET_KEY }}
  run: |
    pytest tests/property/test_database_properties.py::test_role_based_access_control -v
```

## Related Tests

- **Property 1:** User Registration Completeness
- **Property 2:** Authentication Round Trip
- **Property 3:** Profile Update Persistence (to be implemented)
- **Property 16:** Doctor Registration Completeness (to be implemented)
- **Property 17:** Doctor Verification State Transition (to be implemented)

## Requirements Coverage

This test validates the following requirements:

### Requirement 1.4: Patient Role Access
> WHEN a user's role is patient THEN the System SHALL grant access to diagnostic dashboard and doctor locator features

### Requirement 1.5: Doctor Role Access
> WHEN a user's role is doctor THEN the System SHALL grant access to patient report review features only after verification status is true

### Requirement 1.6: Admin Role Access
> WHEN a user's role is admin THEN the System SHALL grant access to doctor verification and content moderation features

### Requirement 6.5: Unverified Doctor Blocking
> WHEN a doctor's verified status is false THEN the System SHALL prevent access to patient reports

### Requirement 6.6: Verified Doctor Access
> WHEN a doctor's verified status is true THEN the System SHALL grant access to pending patient reports

## Example Test Flow

```python
# 1. Create three users with different roles
patient = create_user(role='patient', verified=False)
doctor = create_user(role='doctor', verified=False)
admin = create_user(role='admin', verified=True)

# 2. Create JWT tokens for each user
patient_token = create_access_token({"sub": patient.id, "role": "patient"})
doctor_token = create_access_token({"sub": doctor.id, "role": "doctor", "verified": False})
admin_token = create_access_token({"sub": admin.id, "role": "admin"})

# 3. Test patient access
get_current_patient(patient_token)  # ✅ Success
get_current_doctor(patient_token)   # ❌ HTTP 403 Forbidden

# 4. Test unverified doctor access
get_current_doctor(doctor_token)           # ✅ Success
get_current_verified_doctor(doctor_token)  # ❌ HTTP 403 Forbidden (not verified)

# 5. Verify doctor and test again
update_verification(doctor.id, verified=True)
verified_doctor_token = create_access_token({"sub": doctor.id, "role": "doctor", "verified": True})
get_current_verified_doctor(verified_doctor_token)  # ✅ Success

# 6. Test admin access
get_current_admin(admin_token)    # ✅ Success
get_current_patient(admin_token)  # ❌ HTTP 403 Forbidden
```

## References

- **Design Document:** `.kiro/specs/derman-ai-skin-screening/design.md` (Property 4)
- **Requirements:** `.kiro/specs/derman-ai-skin-screening/requirements.md` (Requirements 1.4, 1.5, 1.6, 6.5, 6.6)
- **Implementation:** `backend/app/dependencies.py` (role-based access control functions)
- **Authentication:** `backend/app/auth.py` (JWT token creation and validation)
- **Hypothesis Documentation:** https://hypothesis.readthedocs.io/

## Notes

- This test validates **role-based access control at the dependency level**
- It does NOT test the full API endpoint integration (that's an integration test)
- It focuses on **authorization logic and role enforcement**
- The test ensures that any valid user with a specific role can only access endpoints appropriate for that role
- Verification status is properly enforced for doctors accessing patient reports

The test ensures that regardless of what valid user data is provided, the authorization system always:
1. Correctly identifies user roles from JWT tokens
2. Enforces role-based access restrictions
3. Blocks unauthorized access with HTTP 403
4. Provides clear error messages
5. Properly checks verification status for doctors
6. Maintains strict role isolation
