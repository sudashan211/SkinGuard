# Property Test: Authentication Round Trip

## Overview

This document describes the property-based test for **Property 2: Authentication Round Trip**.

**Property Statement:**
> For any valid user credentials, successful login should return a session token that can be used to retrieve the same user's profile information.

**Validates:** Requirements 1.2

## Test Location

- **File:** `tests/property/test_database_properties.py`
- **Function:** `test_authentication_round_trip`

## What This Test Does

The test verifies the complete authentication round trip by:

1. **Generating random test data** using Hypothesis:
   - Valid email addresses (e.g., `user123@example.com`)
   - Strong passwords (8-50 characters with uppercase, lowercase, and digits)
   - Full names (2-100 characters)
   - Roles (patient, doctor, or admin)

2. **Creating a user profile** in the database:
   - Generate a unique UUID
   - Hash the password using bcrypt
   - Insert profile record with all required fields

3. **Simulating authentication flow**:
   - Create JWT token data with user information
   - Generate access token using JWT encoding
   - Verify token contains correct payload

4. **Completing the round trip**:
   - Decode the access token
   - Use token to retrieve user profile from database
   - Verify retrieved profile matches original user

5. **Verifying completeness** by checking:
   - ✅ Access token is created and non-empty
   - ✅ Token payload contains user ID, email, role, verified status
   - ✅ Token is marked as "access" type
   - ✅ Token has expiration time
   - ✅ Retrieved profile matches original user data
   - ✅ Round trip returns the same user (ID, email, name, role)

## Authentication Flow Tested

```
User Registration → Token Creation → Token Validation → Profile Retrieval
     (Step 1)           (Step 2)         (Step 3)          (Step 4)
```

This ensures that:
- Users can authenticate with valid credentials
- JWT tokens are properly created and encoded
- Tokens contain all necessary user information
- Tokens can be decoded and validated
- User profiles can be retrieved using tokens
- The entire authentication cycle is consistent

## Running the Test

### Prerequisites

1. **Database Setup:**
   - Supabase project created
   - Database migrations applied (see `database/migrations/`)
   - Database accessible

2. **Environment Configuration:**
   Create a `.env` file in the project root or `database/` directory:
   ```env
   DATABASE_URL=postgresql://postgres:[password]@db.your-project.supabase.co:5432/postgres
   ```

3. **Dependencies Installed:**
   ```bash
   pip install -r tests/requirements.txt
   pip install -r backend/requirements.txt
   ```

### Run the Test

```bash
# Run just this test
python -m pytest tests/property/test_database_properties.py::test_authentication_round_trip -v

# Run with more examples (thorough testing)
python -m pytest tests/property/test_database_properties.py::test_authentication_round_trip -v --hypothesis-profile=thorough

# Run all authentication property tests
python -m pytest tests/property/ -k "auth" -v
```

### Expected Output

When the test runs successfully:

```
tests/property/test_database_properties.py::test_authentication_round_trip PASSED [100%]

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
password = "SecurePass123"  # Must have uppercase, lowercase, and digits
full_name = "John Doe"
role = "patient"
```

Hypothesis will try to find edge cases and unusual inputs that might break the authentication system.

### What Gets Tested

For **100 random examples**, the test verifies:
- Token creation succeeds for any valid user
- Token payload contains all required fields
- Token can be decoded successfully
- Profile retrieval works with any valid token
- Round trip maintains data consistency
- User identity is preserved throughout the flow

## Key Components Tested

### 1. Token Creation (`create_access_token`)
- Generates JWT tokens with user data
- Sets expiration time
- Marks token type as "access"
- Uses configured secret key and algorithm

### 2. Token Decoding (`decode_token`)
- Validates JWT signature
- Checks expiration time
- Extracts payload data
- Handles invalid/expired tokens

### 3. Profile Retrieval (`get_current_user_from_token`)
- Validates token type
- Extracts user ID from token
- Queries database for user profile
- Returns complete profile data

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

### Token Validation Error

```
HTTPException: Invalid or expired token
```

**Solution:** 
- Check JWT_SECRET_KEY is set in environment
- Verify JWT_ALGORITHM matches configuration
- Ensure system clock is synchronized

### Test Failure

If the test fails, Hypothesis will show the **exact input** that caused the failure:

```
Falsifying example: test_authentication_round_trip(
    db_cursor=<cursor>,
    email='test@example.com',
    password='SecurePass123',
    full_name='Test User',
    role='patient'
)
```

This helps identify the specific case that breaks the authentication round trip.

## Integration with CI/CD

This test should run in your CI/CD pipeline:

```yaml
# .github/workflows/test.yml
- name: Run authentication property tests
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
    JWT_SECRET_KEY: ${{ secrets.JWT_SECRET_KEY }}
  run: |
    pytest tests/property/test_database_properties.py::test_authentication_round_trip -v
```

## Related Tests

- **Property 1:** User Registration Completeness
- **Property 3:** Profile Update Persistence (to be implemented)
- **Property 4:** Role-Based Access Control (to be implemented)

## Security Considerations

This test verifies:
- **Token Security**: JWT tokens are properly signed and validated
- **Data Integrity**: User data is preserved throughout authentication
- **Access Control**: Tokens contain role and verification status
- **Expiration**: Tokens have expiration times set

The test does NOT verify:
- Password strength requirements (tested separately)
- Brute force protection (rate limiting)
- Token blacklisting (logout functionality)
- Multi-factor authentication

## References

- **Design Document:** `.kiro/specs/derman-ai-skin-screening/design.md` (Property 2)
- **Requirements:** `.kiro/specs/derman-ai-skin-screening/requirements.md` (Requirement 1.2)
- **Implementation:** `backend/app/auth.py` (authentication functions)
- **API Endpoints:** `backend/app/routers/auth.py` (login, refresh endpoints)
- **Hypothesis Documentation:** https://hypothesis.readthedocs.io/

## Notes

- This test validates the **JWT token round trip** for authentication
- It does NOT test the full Supabase Auth integration (that's an integration test)
- It focuses on **token creation, validation, and profile retrieval**
- The test ensures that any valid user can authenticate and retrieve their profile
- Password hashing is tested but not the full Supabase Auth flow

The test ensures that regardless of what valid user data is provided, the authentication system always:
1. Creates valid JWT tokens
2. Encodes correct user information
3. Allows token-based profile retrieval
4. Maintains data consistency throughout the round trip

## Example Test Flow

```python
# 1. Create user in database
user_id = "550e8400-e29b-41d4-a716-446655440000"
email = "patient@example.com"
role = "patient"

# 2. Create JWT token
token_data = {"sub": user_id, "email": email, "role": role}
access_token = create_access_token(token_data)
# Result: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 3. Decode token
decoded = decode_token(access_token)
# Result: {"sub": user_id, "email": email, "role": role, "exp": ..., "type": "access"}

# 4. Retrieve profile using token
profile = get_current_user_from_token(access_token)
# Result: {"id": user_id, "email": email, "role": role, ...}

# 5. Verify round trip
assert profile["id"] == user_id  # ✅ Same user returned
```

This demonstrates the complete authentication round trip working correctly.
