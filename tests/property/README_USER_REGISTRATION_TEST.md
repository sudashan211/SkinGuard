# Property Test: User Registration Completeness

## Overview

This document describes the property-based test for **Property 1: User Registration Completeness**.

**Property Statement:**
> For any user registration with valid data, the created profile record should contain all required fields (UUID, full name, role, verification status) and be retrievable from the database.

**Validates:** Requirements 1.1

## Test Location

- **File:** `tests/property/test_database_properties.py`
- **Function:** `test_user_registration_completeness`

## What This Test Does

The test verifies that user registration creates complete and valid profile records by:

1. **Generating random test data** using Hypothesis:
   - Valid email addresses (e.g., `user123@example.com`)
   - Full names (2-100 characters)
   - Roles (patient, doctor, or admin)

2. **Creating a profile record** in the database with:
   - A unique UUID
   - The generated email, full name, and role
   - Default values (verified=False, language_preference='en')

3. **Retrieving the profile** from the database

4. **Verifying completeness** by checking:
   - ✅ UUID is present and valid
   - ✅ Email matches input
   - ✅ Full name matches input
   - ✅ Role matches input
   - ✅ Verification status is False (new users)
   - ✅ Language preference is 'en' (default)
   - ✅ Created timestamp is set
   - ✅ Updated timestamp is set

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
   ```

3. **Dependencies Installed:**
   ```bash
   pip install -r tests/requirements.txt
   ```

### Run the Test

```bash
# Run just this test
python -m pytest tests/property/test_database_properties.py::test_user_registration_completeness -v

# Run with more examples (thorough testing)
python -m pytest tests/property/test_database_properties.py::test_user_registration_completeness -v --hypothesis-profile=thorough

# Run all property tests
python -m pytest tests/property/ -v
```

### Expected Output

When the test runs successfully:

```
tests/property/test_database_properties.py::test_user_registration_completeness PASSED [100%]

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
email = "abc123@example.com"
full_name = "John Doe"
role = "patient"
```

Hypothesis will try to find edge cases and unusual inputs that might break the system.

### What Gets Tested

For **100 random examples**, the test verifies:
- Profile creation succeeds
- All required fields are populated
- Data integrity is maintained
- UUID format is valid
- Default values are correctly set

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

### Foreign Key Constraint Error

```
psycopg2.IntegrityError: foreign key constraint
```

**Solution:** Ensure database migrations are applied (see `database/migrations/`).

### Test Failure

If the test fails, Hypothesis will show the **exact input** that caused the failure:

```
Falsifying example: test_user_registration_completeness(
    db_cursor=<cursor>,
    email='test@example.com',
    full_name='Test User',
    role='patient'
)
```

This helps identify the specific case that breaks the property.

## Integration with CI/CD

This test should run in your CI/CD pipeline:

```yaml
# .github/workflows/test.yml
- name: Run property tests
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
  run: |
    pytest tests/property/test_database_properties.py::test_user_registration_completeness -v
```

## Related Tests

- **Property 33:** Referential Integrity Enforcement
- **Property 2:** Authentication Round Trip (to be implemented)
- **Property 3:** Profile Update Persistence (to be implemented)

## References

- **Design Document:** `.kiro/specs/derman-ai-skin-screening/design.md`
- **Requirements:** `.kiro/specs/derman-ai-skin-screening/requirements.md` (Requirement 1.1)
- **Implementation:** `backend/app/auth.py` (`register_user` function)
- **Hypothesis Documentation:** https://hypothesis.readthedocs.io/

## Notes

- This test validates the **database layer** of user registration
- It does NOT test the API endpoint (that would be an integration test)
- It does NOT test password hashing (that's tested separately)
- It focuses on **data completeness and integrity**

The test ensures that regardless of what valid data is provided, the registration process always creates a complete and valid profile record.
