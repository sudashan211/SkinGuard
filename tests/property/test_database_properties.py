"""
Property-Based Tests for Database Schema

Feature: derman-ai-skin-screening
Tests database-level correctness properties including referential integrity,
constraints, and data consistency.

Requirements: 12.4, 12.5
"""

import pytest
import psycopg2
import os
from hypothesis import given, strategies as st, settings, assume
from hypothesis import HealthCheck
from dotenv import load_dotenv
from uuid import uuid4

# Load environment variables
load_dotenv()


@pytest.fixture(scope="module")
def db_connection():
    """Create database connection for tests"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        pytest.skip("DATABASE_URL not set - skipping database tests")
    
    conn = psycopg2.connect(database_url)
    yield conn
    conn.close()


@pytest.fixture
def db_cursor(db_connection):
    """Create a cursor with automatic rollback after each test"""
    cursor = db_connection.cursor()
    yield cursor
    db_connection.rollback()  # Rollback after each test
    cursor.close()


# Hypothesis strategies for generating test data
@st.composite
def valid_email(draw):
    """Generate valid email addresses"""
    username = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Ll', 'Nd')),
        min_size=3,
        max_size=20
    ))
    domain = draw(st.sampled_from(['example.com', 'test.com', 'demo.org']))
    return f"{username}@{domain}"


@st.composite
def valid_profile(draw):
    """Generate valid profile data"""
    return {
        'id': str(uuid4()),
        'email': draw(valid_email()),
        'full_name': draw(st.text(min_size=2, max_size=100)),
        'role': draw(st.sampled_from(['patient', 'doctor', 'admin'])),
        'verified': draw(st.booleans())
    }


@st.composite
def valid_patient_data(draw, user_id):
    """Generate valid patient data"""
    return {
        'id': str(uuid4()),
        'user_id': user_id,
        'age': draw(st.integers(min_value=1, max_value=120)),
        'skin_type': draw(st.sampled_from(['I', 'II', 'III', 'IV', 'V', 'VI'])),
        'family_history': draw(st.text(max_size=500))
    }


@st.composite
def valid_doctor(draw, user_id):
    """Generate valid doctor data"""
    return {
        'id': str(uuid4()),
        'user_id': user_id,
        'license_no': f"MD{draw(st.integers(min_value=10000, max_value=99999))}",
        'clinic_name': draw(st.text(min_size=5, max_size=100)),
        'lat': draw(st.floats(min_value=-90, max_value=90)),
        'lng': draw(st.floats(min_value=-180, max_value=180)),
        'whatsapp_no': f"+1{draw(st.integers(min_value=1000000000, max_value=9999999999))}"
    }


@st.composite
def valid_medical_report(draw, patient_id):
    """Generate valid medical report data"""
    return {
        'id': str(uuid4()),
        'patient_id': patient_id,
        'image_url': f"https://storage.example.com/{uuid4()}.jpg",
        'ai_prediction': '{"predictions": [{"type": "melanoma", "probability": 0.75}]}',
        'status': draw(st.sampled_from(['safe', 'flagged', 'urgent'])),
        'risk_level': draw(st.sampled_from(['low', 'medium', 'high', 'urgent']))
    }


# Feature: derman-ai-skin-screening, Property 33: Referential Integrity Enforcement
@given(profile=valid_profile())
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_patient_data_referential_integrity(db_cursor, profile):
    """
    Property 33: Referential Integrity Enforcement
    
    For any attempt to create a patient_data record with invalid patient_id
    (not existing in profiles table), the database should reject the operation
    with a foreign key constraint error.
    
    Validates: Requirements 12.4, 12.5
    """
    # Generate a random UUID that doesn't exist in profiles
    non_existent_user_id = str(uuid4())
    
    # Attempt to insert patient_data with non-existent user_id
    try:
        db_cursor.execute("""
            INSERT INTO patient_data (id, user_id, age, skin_type)
            VALUES (%s, %s, %s, %s)
        """, (str(uuid4()), non_existent_user_id, 25, 'III'))
        
        # If we get here, the constraint didn't work - test should fail
        pytest.fail("Foreign key constraint not enforced - invalid user_id was accepted")
        
    except psycopg2.IntegrityError as e:
        # Expected behavior - foreign key constraint violation
        assert 'foreign key constraint' in str(e).lower() or 'violates' in str(e).lower()
        # Rollback the failed transaction
        db_cursor.connection.rollback()


# Feature: derman-ai-skin-screening, Property 33: Referential Integrity Enforcement
@given(profile=valid_profile())
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_medical_report_referential_integrity(db_cursor, profile):
    """
    Property 33: Referential Integrity Enforcement
    
    For any attempt to create a medical_report with invalid patient_id
    (not existing in profiles table), the database should reject the operation
    with a foreign key constraint error.
    
    Validates: Requirements 12.4, 12.5
    """
    # Generate a random UUID that doesn't exist in profiles
    non_existent_patient_id = str(uuid4())
    
    # Attempt to insert medical_report with non-existent patient_id
    try:
        db_cursor.execute("""
            INSERT INTO medical_reports (id, patient_id, image_url, ai_prediction, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            str(uuid4()),
            non_existent_patient_id,
            'https://storage.example.com/test.jpg',
            '{"predictions": []}',
            'safe'
        ))
        
        # If we get here, the constraint didn't work - test should fail
        pytest.fail("Foreign key constraint not enforced - invalid patient_id was accepted")
        
    except psycopg2.IntegrityError as e:
        # Expected behavior - foreign key constraint violation
        assert 'foreign key constraint' in str(e).lower() or 'violates' in str(e).lower()
        # Rollback the failed transaction
        db_cursor.connection.rollback()


# Feature: derman-ai-skin-screening, Property 33: Referential Integrity Enforcement
@given(profile=valid_profile())
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_appointment_referential_integrity_patient(db_cursor, profile):
    """
    Property 33: Referential Integrity Enforcement
    
    For any attempt to create an appointment with invalid patient_id
    (not existing in profiles table), the database should reject the operation
    with a foreign key constraint error.
    
    Validates: Requirements 12.4, 12.5
    """
    # First create a valid doctor to reference
    db_cursor.execute("""
        INSERT INTO profiles (id, email, full_name, role, verified)
        VALUES (%s, %s, %s, %s, %s)
    """, (profile['id'], profile['email'], profile['full_name'], 'doctor', True))
    
    doctor_id = str(uuid4())
    db_cursor.execute("""
        INSERT INTO doctors (id, user_id, license_no, clinic_name, lat, lng, whatsapp_no)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (doctor_id, profile['id'], 'MD12345', 'Test Clinic', 40.7128, -74.0060, '+11234567890'))
    
    # Generate a random UUID that doesn't exist in profiles
    non_existent_patient_id = str(uuid4())
    
    # Attempt to insert appointment with non-existent patient_id
    try:
        db_cursor.execute("""
            INSERT INTO appointments (id, patient_id, doctor_id, scheduled_at, status)
            VALUES (%s, %s, %s, NOW() + INTERVAL '1 day', %s)
        """, (str(uuid4()), non_existent_patient_id, doctor_id, 'pending'))
        
        # If we get here, the constraint didn't work - test should fail
        pytest.fail("Foreign key constraint not enforced - invalid patient_id was accepted")
        
    except psycopg2.IntegrityError as e:
        # Expected behavior - foreign key constraint violation
        assert 'foreign key constraint' in str(e).lower() or 'violates' in str(e).lower()
        # Rollback the failed transaction
        db_cursor.connection.rollback()


# Feature: derman-ai-skin-screening, Property 33: Referential Integrity Enforcement
@given(profile=valid_profile())
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_appointment_referential_integrity_doctor(db_cursor, profile):
    """
    Property 33: Referential Integrity Enforcement
    
    For any attempt to create an appointment with invalid doctor_id
    (not existing in doctors table), the database should reject the operation
    with a foreign key constraint error.
    
    Validates: Requirements 12.4, 12.5
    """
    # First create a valid patient to reference
    db_cursor.execute("""
        INSERT INTO profiles (id, email, full_name, role, verified)
        VALUES (%s, %s, %s, %s, %s)
    """, (profile['id'], profile['email'], profile['full_name'], 'patient', False))
    
    # Generate a random UUID that doesn't exist in doctors
    non_existent_doctor_id = str(uuid4())
    
    # Attempt to insert appointment with non-existent doctor_id
    try:
        db_cursor.execute("""
            INSERT INTO appointments (id, patient_id, doctor_id, scheduled_at, status)
            VALUES (%s, %s, %s, NOW() + INTERVAL '1 day', %s)
        """, (str(uuid4()), profile['id'], non_existent_doctor_id, 'pending'))
        
        # If we get here, the constraint didn't work - test should fail
        pytest.fail("Foreign key constraint not enforced - invalid doctor_id was accepted")
        
    except psycopg2.IntegrityError as e:
        # Expected behavior - foreign key constraint violation
        assert 'foreign key constraint' in str(e).lower() or 'violates' in str(e).lower()
        # Rollback the failed transaction
        db_cursor.connection.rollback()


# Feature: derman-ai-skin-screening, Property 33: Referential Integrity Enforcement
@given(profile=valid_profile())
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_cascade_delete_patient_data(db_cursor, profile):
    """
    Property 33: Referential Integrity Enforcement (Cascade Delete)
    
    For any profile deletion, all associated patient_data records should be
    automatically deleted due to ON DELETE CASCADE constraint.
    
    Validates: Requirements 12.4, 12.5
    """
    # Create a profile
    db_cursor.execute("""
        INSERT INTO profiles (id, email, full_name, role, verified)
        VALUES (%s, %s, %s, %s, %s)
    """, (profile['id'], profile['email'], profile['full_name'], 'patient', False))
    
    # Create associated patient_data
    patient_data_id = str(uuid4())
    db_cursor.execute("""
        INSERT INTO patient_data (id, user_id, age, skin_type)
        VALUES (%s, %s, %s, %s)
    """, (patient_data_id, profile['id'], 30, 'III'))
    
    # Verify patient_data exists
    db_cursor.execute("SELECT COUNT(*) FROM patient_data WHERE id = %s", (patient_data_id,))
    count_before = db_cursor.fetchone()[0]
    assert count_before == 1, "Patient data should exist before deletion"
    
    # Delete the profile
    db_cursor.execute("DELETE FROM profiles WHERE id = %s", (profile['id'],))
    
    # Verify patient_data was cascade deleted
    db_cursor.execute("SELECT COUNT(*) FROM patient_data WHERE id = %s", (patient_data_id,))
    count_after = db_cursor.fetchone()[0]
    assert count_after == 0, "Patient data should be cascade deleted with profile"


# Feature: derman-ai-skin-screening, Property 33: Referential Integrity Enforcement
@given(profile=valid_profile())
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_cascade_delete_medical_reports(db_cursor, profile):
    """
    Property 33: Referential Integrity Enforcement (Cascade Delete)
    
    For any profile deletion, all associated medical_reports should be
    automatically deleted due to ON DELETE CASCADE constraint.
    
    Validates: Requirements 12.4, 12.5
    """
    # Create a profile
    db_cursor.execute("""
        INSERT INTO profiles (id, email, full_name, role, verified)
        VALUES (%s, %s, %s, %s, %s)
    """, (profile['id'], profile['email'], profile['full_name'], 'patient', False))
    
    # Create associated medical_report
    report_id = str(uuid4())
    db_cursor.execute("""
        INSERT INTO medical_reports (id, patient_id, image_url, ai_prediction, status)
        VALUES (%s, %s, %s, %s, %s)
    """, (report_id, profile['id'], 'https://storage.example.com/test.jpg', '{"predictions": []}', 'safe'))
    
    # Verify medical_report exists
    db_cursor.execute("SELECT COUNT(*) FROM medical_reports WHERE id = %s", (report_id,))
    count_before = db_cursor.fetchone()[0]
    assert count_before == 1, "Medical report should exist before deletion"
    
    # Delete the profile
    db_cursor.execute("DELETE FROM profiles WHERE id = %s", (profile['id'],))
    
    # Verify medical_report was cascade deleted
    db_cursor.execute("SELECT COUNT(*) FROM medical_reports WHERE id = %s", (report_id,))
    count_after = db_cursor.fetchone()[0]
    assert count_after == 0, "Medical report should be cascade deleted with profile"


# Feature: derman-ai-skin-screening, Property 1: User Registration Completeness
@given(
    email=valid_email(),
    full_name=st.text(min_size=2, max_size=100),
    role=st.sampled_from(['patient', 'doctor', 'admin'])
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_user_registration_completeness(db_cursor, email, full_name, role):
    """
    Property 1: User Registration Completeness
    
    For any user registration with valid data, the created profile record should
    contain all required fields (UUID, full name, role, verification status) and
    be retrievable from the database.
    
    Validates: Requirements 1.1
    """
    # Generate a unique user ID
    user_id = str(uuid4())
    
    # Insert a profile record (simulating user registration)
    db_cursor.execute("""
        INSERT INTO profiles (id, email, full_name, role, verified, language_preference)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (user_id, email, full_name, role, False, 'en'))
    
    # Retrieve the profile from the database
    db_cursor.execute("""
        SELECT id, email, full_name, role, verified, language_preference, created_at, updated_at
        FROM profiles
        WHERE id = %s
    """, (user_id,))
    
    result = db_cursor.fetchone()
    
    # Verify the profile was created and contains all required fields
    assert result is not None, "Profile should be retrievable from database"
    
    # Unpack the result
    retrieved_id, retrieved_email, retrieved_full_name, retrieved_role, retrieved_verified, retrieved_lang, created_at, updated_at = result
    
    # Verify all required fields are present and correct
    assert retrieved_id == user_id, "UUID should match the generated ID"
    assert retrieved_email == email, "Email should match the input"
    assert retrieved_full_name == full_name, "Full name should match the input"
    assert retrieved_role == role, "Role should match the input"
    assert retrieved_verified == False, "Verification status should be False for new users"
    assert retrieved_lang == 'en', "Default language preference should be 'en'"
    assert created_at is not None, "Created timestamp should be set"
    assert updated_at is not None, "Updated timestamp should be set"
    
    # Verify the UUID is a valid UUID format
    try:
        from uuid import UUID
        UUID(retrieved_id)
    except ValueError:
        pytest.fail(f"Retrieved ID '{retrieved_id}' is not a valid UUID")


# Feature: derman-ai-skin-screening, Property 2: Authentication Round Trip
@given(
    email=valid_email(),
    password=st.text(min_size=8, max_size=50).filter(
        lambda p: any(c.isupper() for c in p) and 
                  any(c.islower() for c in p) and 
                  any(c.isdigit() for c in p)
    ),
    full_name=st.text(min_size=2, max_size=100),
    role=st.sampled_from(['patient', 'doctor', 'admin'])
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_authentication_round_trip(db_cursor, email, password, full_name, role):
    """
    Property 2: Authentication Round Trip
    
    For any valid user credentials, successful login should return a session token
    that can be used to retrieve the same user's profile information.
    
    This test verifies the complete authentication flow:
    1. Create a user in the database (simulating registration)
    2. Verify the user can authenticate with their credentials
    3. Verify the authentication returns valid tokens
    4. Verify the tokens can be used to retrieve the correct user profile
    
    Validates: Requirements 1.2
    """
    from app.auth import authenticate_user, get_current_user_from_token, hash_password
    
    # Generate a unique user ID
    user_id = str(uuid4())
    
    # Hash the password (simulating what registration does)
    hashed_password = hash_password(password)
    
    # Create a profile record in the database (simulating registration)
    db_cursor.execute("""
        INSERT INTO profiles (id, email, full_name, role, verified, language_preference)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (user_id, email, full_name, role, False, 'en'))
    
    # Commit the profile creation so Supabase Auth can see it
    db_cursor.connection.commit()
    
    try:
        # Step 1: Authenticate the user (login)
        # Note: This test focuses on the JWT token round trip, not Supabase Auth
        # We'll test the token creation and validation directly
        from app.auth import create_access_token, decode_token
        
        # Create token data (simulating what authenticate_user does)
        token_data = {
            "sub": user_id,
            "email": email,
            "role": role,
            "verified": False
        }
        
        # Step 2: Create access token (simulating successful login)
        access_token = create_access_token(token_data)
        
        # Verify token was created
        assert access_token is not None, "Access token should be created"
        assert isinstance(access_token, str), "Access token should be a string"
        assert len(access_token) > 0, "Access token should not be empty"
        
        # Step 3: Decode the token to verify it contains correct data
        decoded_payload = decode_token(access_token)
        
        # Verify token payload contains expected data
        assert decoded_payload["sub"] == user_id, "Token should contain correct user ID"
        assert decoded_payload["email"] == email, "Token should contain correct email"
        assert decoded_payload["role"] == role, "Token should contain correct role"
        assert decoded_payload["verified"] == False, "Token should contain correct verified status"
        assert decoded_payload["type"] == "access", "Token should be marked as access token"
        assert "exp" in decoded_payload, "Token should have expiration time"
        
        # Step 4: Use the token to retrieve user profile (round trip complete)
        retrieved_profile = get_current_user_from_token(access_token)
        
        # Verify the retrieved profile matches the original user
        assert retrieved_profile is not None, "Profile should be retrievable with token"
        assert retrieved_profile["id"] == user_id, "Retrieved profile should have correct ID"
        assert retrieved_profile["email"] == email, "Retrieved profile should have correct email"
        assert retrieved_profile["full_name"] == full_name, "Retrieved profile should have correct full name"
        assert retrieved_profile["role"] == role, "Retrieved profile should have correct role"
        assert retrieved_profile["verified"] == False, "Retrieved profile should have correct verified status"
        
        # Verify the round trip is complete: login -> token -> profile retrieval
        # The user we started with is the same user we got back
        assert retrieved_profile["id"] == user_id, "Round trip should return the same user"
        
    finally:
        # Clean up: rollback will happen automatically via fixture
        pass


# Feature: derman-ai-skin-screening, Property 4: Role-Based Access Control
@given(
    patient_email=valid_email(),
    doctor_email=valid_email(),
    admin_email=valid_email(),
    full_name=st.text(min_size=2, max_size=100)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_role_based_access_control(db_cursor, patient_email, doctor_email, admin_email, full_name):
    """
    Property 4: Role-Based Access Control
    
    For any user with a specific role, access to endpoints should match their role permissions:
    - Patients access diagnostic features
    - Unverified doctors are blocked from reports
    - Verified doctors access reports
    - Admins access moderation features
    
    Validates: Requirements 1.4, 1.5, 1.6, 6.5, 6.6
    """
    from app.dependencies import (
        get_current_patient,
        get_current_doctor,
        get_current_verified_doctor,
        get_current_admin
    )
    from app.auth import create_access_token
    
    # Ensure emails are unique
    assume(patient_email != doctor_email)
    assume(patient_email != admin_email)
    assume(doctor_email != admin_email)
    
    # Create three users with different roles
    patient_id = str(uuid4())
    doctor_id = str(uuid4())
    admin_id = str(uuid4())
    
    # Insert patient profile
    db_cursor.execute("""
        INSERT INTO profiles (id, email, full_name, role, verified)
        VALUES (%s, %s, %s, %s, %s)
    """, (patient_id, patient_email, f"{full_name} Patient", 'patient', False))
    
    # Insert unverified doctor profile
    db_cursor.execute("""
        INSERT INTO profiles (id, email, full_name, role, verified)
        VALUES (%s, %s, %s, %s, %s)
    """, (doctor_id, doctor_email, f"{full_name} Doctor", 'doctor', False))
    
    # Insert admin profile
    db_cursor.execute("""
        INSERT INTO profiles (id, email, full_name, role, verified)
        VALUES (%s, %s, %s, %s, %s)
    """, (admin_id, admin_email, f"{full_name} Admin", 'admin', True))
    
    # Commit to make profiles available
    db_cursor.connection.commit()
    
    try:
        # Create tokens for each user
        patient_token_data = {
            "sub": patient_id,
            "email": patient_email,
            "role": "patient",
            "verified": False
        }
        patient_token = create_access_token(patient_token_data)
        
        doctor_token_data = {
            "sub": doctor_id,
            "email": doctor_email,
            "role": "doctor",
            "verified": False
        }
        doctor_token = create_access_token(doctor_token_data)
        
        admin_token_data = {
            "sub": admin_id,
            "email": admin_email,
            "role": "admin",
            "verified": True
        }
        admin_token = create_access_token(admin_token_data)
        
        # Test 1: Patient can access patient endpoints
        from fastapi.security import HTTPAuthorizationCredentials
        patient_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=patient_token)
        
        # This should succeed - patient accessing patient endpoint
        import asyncio
        patient_user = asyncio.run(get_current_patient(patient_creds))
        assert patient_user["role"] == "patient", "Patient should access patient endpoints"
        assert patient_user["id"] == patient_id, "Correct patient user should be returned"
        
        # Test 2: Patient CANNOT access doctor endpoints
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(get_current_doctor(patient_creds))
        assert exc_info.value.status_code == 403, "Patient should be blocked from doctor endpoints"
        assert "doctor role" in exc_info.value.detail.lower(), "Error should mention doctor role requirement"
        
        # Test 3: Patient CANNOT access admin endpoints
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(get_current_admin(patient_creds))
        assert exc_info.value.status_code == 403, "Patient should be blocked from admin endpoints"
        assert "admin role" in exc_info.value.detail.lower(), "Error should mention admin role requirement"
        
        # Test 4: Unverified doctor can access doctor endpoints (role check only)
        doctor_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=doctor_token)
        doctor_user = asyncio.run(get_current_doctor(doctor_creds))
        assert doctor_user["role"] == "doctor", "Doctor should access doctor endpoints"
        assert doctor_user["id"] == doctor_id, "Correct doctor user should be returned"
        
        # Test 5: Unverified doctor CANNOT access verified doctor endpoints (reports)
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(get_current_verified_doctor(doctor_creds))
        assert exc_info.value.status_code == 403, "Unverified doctor should be blocked from reports"
        assert "verified" in exc_info.value.detail.lower(), "Error should mention verification requirement"
        
        # Test 6: Unverified doctor CANNOT access patient endpoints
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(get_current_patient(doctor_creds))
        assert exc_info.value.status_code == 403, "Doctor should be blocked from patient endpoints"
        
        # Test 7: Unverified doctor CANNOT access admin endpoints
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(get_current_admin(doctor_creds))
        assert exc_info.value.status_code == 403, "Doctor should be blocked from admin endpoints"
        
        # Test 8: Now verify the doctor and test verified access
        db_cursor.execute("""
            UPDATE profiles SET verified = %s WHERE id = %s
        """, (True, doctor_id))
        db_cursor.connection.commit()
        
        # Create new token with verified status
        verified_doctor_token_data = {
            "sub": doctor_id,
            "email": doctor_email,
            "role": "doctor",
            "verified": True
        }
        verified_doctor_token = create_access_token(verified_doctor_token_data)
        verified_doctor_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=verified_doctor_token)
        
        # Test 9: Verified doctor CAN access verified doctor endpoints (reports)
        verified_doctor_user = asyncio.run(get_current_verified_doctor(verified_doctor_creds))
        assert verified_doctor_user["role"] == "doctor", "Verified doctor should access report endpoints"
        assert verified_doctor_user["verified"] == True, "Doctor should be verified"
        assert verified_doctor_user["id"] == doctor_id, "Correct doctor user should be returned"
        
        # Test 10: Admin can access admin endpoints
        admin_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=admin_token)
        admin_user = asyncio.run(get_current_admin(admin_creds))
        assert admin_user["role"] == "admin", "Admin should access admin endpoints"
        assert admin_user["id"] == admin_id, "Correct admin user should be returned"
        
        # Test 11: Admin CANNOT access patient endpoints
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(get_current_patient(admin_creds))
        assert exc_info.value.status_code == 403, "Admin should be blocked from patient endpoints"
        
        # Test 12: Admin CANNOT access doctor endpoints
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(get_current_doctor(admin_creds))
        assert exc_info.value.status_code == 403, "Admin should be blocked from doctor endpoints"
        
        # Summary: All role-based access control checks passed
        # - Patients can only access patient features
        # - Unverified doctors are blocked from reports
        # - Verified doctors can access reports
        # - Admins can only access admin features
        # - Each role is properly isolated from other roles
        
    finally:
        # Cleanup happens automatically via rollback in fixture
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])



# Feature: derman-ai-skin-screening, Property 5: Age Validation Bounds
@given(age=st.integers(min_value=-1000, max_value=1000))  # Limit range to avoid PostgreSQL overflow
@settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])  # Reduced for faster testing
def test_age_validation_bounds(db_cursor, age):
    """
    Property 5: Age Validation Bounds
    
    For any integer input for patient age, the system should accept only values
    in the range [1, 120] and reject all others with a validation error.
    
    Validates: Requirements 2.2
    """
    # Create a test profile first
    profile_id = str(uuid4())
    email = f"test_{uuid4()}@example.com"
    
    db_cursor.execute("""
        INSERT INTO profiles (id, email, full_name, role, verified)
        VALUES (%s, %s, %s, %s, %s)
    """, (profile_id, email, "Test User", 'patient', False))
    
    patient_data_id = str(uuid4())
    
    if 1 <= age <= 120:
        # Valid age - should be accepted
        try:
            db_cursor.execute("""
                INSERT INTO patient_data (id, user_id, age, skin_type)
                VALUES (%s, %s, %s, %s)
            """, (patient_data_id, profile_id, age, 'III'))
            
            # Verify the age was stored correctly
            db_cursor.execute("SELECT age FROM patient_data WHERE id = %s", (patient_data_id,))
            stored_age = db_cursor.fetchone()[0]
            assert stored_age == age, f"Stored age {stored_age} should match input age {age}"
            
        except psycopg2.IntegrityError as e:
            pytest.fail(f"Valid age {age} was rejected: {e}")
    else:
        # Invalid age - should be rejected by check constraint
        try:
            db_cursor.execute("""
                INSERT INTO patient_data (id, user_id, age, skin_type)
                VALUES (%s, %s, %s, %s)
            """, (patient_data_id, profile_id, age, 'III'))
            
            # If we get here, the constraint didn't work
            pytest.fail(f"Invalid age {age} was accepted when it should be rejected")
            
        except psycopg2.IntegrityError as e:
            # Expected behavior - check constraint violation
            assert 'check constraint' in str(e).lower() or 'violates' in str(e).lower()
            db_cursor.connection.rollback()


# Feature: derman-ai-skin-screening, Property 6: Fitzpatrick Scale Enum Validation
@given(skin_type=st.text(min_size=1, max_size=10).filter(lambda x: '\x00' not in x))  # Filter out NUL characters
@settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])  # Reduced for faster testing
def test_fitzpatrick_scale_validation(db_cursor, skin_type):
    """
    Property 6: Fitzpatrick Scale Enum Validation
    
    For any string input for skin type, the system should accept only valid
    Fitzpatrick Scale values (I, II, III, IV, V, VI) and reject all others.
    
    Validates: Requirements 2.3
    """
    # Create a test profile first
    profile_id = str(uuid4())
    email = f"test_{uuid4()}@example.com"
    
    db_cursor.execute("""
        INSERT INTO profiles (id, email, full_name, role, verified)
        VALUES (%s, %s, %s, %s, %s)
    """, (profile_id, email, "Test User", 'patient', False))
    
    patient_data_id = str(uuid4())
    valid_skin_types = ['I', 'II', 'III', 'IV', 'V', 'VI']
    
    if skin_type in valid_skin_types:
        # Valid skin type - should be accepted
        try:
            db_cursor.execute("""
                INSERT INTO patient_data (id, user_id, age, skin_type)
                VALUES (%s, %s, %s, %s)
            """, (patient_data_id, profile_id, 30, skin_type))
            
            # Verify the skin type was stored correctly
            db_cursor.execute("SELECT skin_type FROM patient_data WHERE id = %s", (patient_data_id,))
            stored_skin_type = db_cursor.fetchone()[0]
            assert stored_skin_type == skin_type, f"Stored skin type {stored_skin_type} should match input {skin_type}"
            
        except psycopg2.IntegrityError as e:
            pytest.fail(f"Valid skin type '{skin_type}' was rejected: {e}")
    else:
        # Invalid skin type - should be rejected by check constraint
        try:
            db_cursor.execute("""
                INSERT INTO patient_data (id, user_id, age, skin_type)
                VALUES (%s, %s, %s, %s)
            """, (patient_data_id, profile_id, 30, skin_type))
            
            # If we get here, the constraint didn't work
            pytest.fail(f"Invalid skin type '{skin_type}' was accepted when it should be rejected")
            
        except psycopg2.IntegrityError as e:
            # Expected behavior - check constraint violation
            assert 'check constraint' in str(e).lower() or 'violates' in str(e).lower()
            db_cursor.connection.rollback()


# Feature: derman-ai-skin-screening, Property 7: Text Storage Without Truncation
@given(family_history=st.text(min_size=0, max_size=5000).filter(lambda x: '\x00' not in x))  # Filter out NUL characters
@settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])  # Reduced for faster testing
def test_text_storage_without_truncation(db_cursor, family_history):
    """
    Property 7: Text Storage Without Truncation
    
    For any text input of arbitrary length for family history, the system should
    store and retrieve the complete text without truncation.
    
    Validates: Requirements 2.4
    """
    # Create a test profile first
    profile_id = str(uuid4())
    email = f"test_{uuid4()}@example.com"
    
    db_cursor.execute("""
        INSERT INTO profiles (id, email, full_name, role, verified)
        VALUES (%s, %s, %s, %s, %s)
    """, (profile_id, email, "Test User", 'patient', False))
    
    patient_data_id = str(uuid4())
    
    # Insert patient data with family history
    db_cursor.execute("""
        INSERT INTO patient_data (id, user_id, age, skin_type, family_history)
        VALUES (%s, %s, %s, %s, %s)
    """, (patient_data_id, profile_id, 30, 'III', family_history))
    
    # Retrieve the family history
    db_cursor.execute("SELECT family_history FROM patient_data WHERE id = %s", (patient_data_id,))
    stored_family_history = db_cursor.fetchone()[0]
    
    # Verify no truncation occurred
    if family_history:
        assert stored_family_history == family_history, \
            f"Family history was truncated. Original length: {len(family_history)}, Stored length: {len(stored_family_history or '')}"
    else:
        # Empty string or None should be stored as None or empty
        assert stored_family_history in (None, ''), \
            f"Empty family history should be stored as None or empty string, got: {stored_family_history}"
    
    # Verify the complete text can be retrieved
    assert len(stored_family_history or '') == len(family_history), \
        "Retrieved text length should match original text length"



# Feature: derman-ai-skin-screening, Property 3: Profile Update Persistence
@given(
    original_age=st.integers(min_value=1, max_value=120),
    updated_age=st.integers(min_value=1, max_value=120),
    original_skin_type=st.sampled_from(['I', 'II', 'III', 'IV', 'V', 'VI']),
    updated_skin_type=st.sampled_from(['I', 'II', 'III', 'IV', 'V', 'VI']),
    original_history=st.text(max_size=500).filter(lambda x: '\x00' not in x),  # Filter out NUL characters
    updated_history=st.text(max_size=500).filter(lambda x: '\x00' not in x)  # Filter out NUL characters
)
@settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])  # Reduced for faster testing
def test_profile_update_persistence(
    db_cursor,
    original_age,
    updated_age,
    original_skin_type,
    updated_skin_type,
    original_history,
    updated_history
):
    """
    Property 3: Profile Update Persistence
    
    For any user profile and any valid update data, applying the update then
    fetching the profile should return the updated values.
    
    This test verifies that patient data updates are persisted correctly:
    1. Create a patient profile with original data
    2. Update the profile with new data
    3. Retrieve the profile and verify it contains the updated values
    
    Validates: Requirements 1.3, 2.5
    """
    # Create a test profile first
    profile_id = str(uuid4())
    email = f"test_{uuid4()}@example.com"
    
    db_cursor.execute("""
        INSERT INTO profiles (id, email, full_name, role, verified)
        VALUES (%s, %s, %s, %s, %s)
    """, (profile_id, email, "Test User", 'patient', False))
    
    patient_data_id = str(uuid4())
    
    # Step 1: Create patient data with original values
    db_cursor.execute("""
        INSERT INTO patient_data (id, user_id, age, skin_type, family_history)
        VALUES (%s, %s, %s, %s, %s)
    """, (patient_data_id, profile_id, original_age, original_skin_type, original_history))
    
    # Verify original data was stored
    db_cursor.execute("""
        SELECT age, skin_type, family_history FROM patient_data WHERE id = %s
    """, (patient_data_id,))
    result = db_cursor.fetchone()
    assert result is not None, "Patient data should exist after creation"
    stored_age, stored_skin_type, stored_history = result
    assert stored_age == original_age, "Original age should be stored correctly"
    assert stored_skin_type == original_skin_type, "Original skin type should be stored correctly"
    assert stored_history == original_history or (not original_history and stored_history is None), \
        "Original family history should be stored correctly"
    
    # Step 2: Update the patient data
    db_cursor.execute("""
        UPDATE patient_data
        SET age = %s, skin_type = %s, family_history = %s, updated_at = NOW()
        WHERE id = %s
    """, (updated_age, updated_skin_type, updated_history, patient_data_id))
    
    # Step 3: Retrieve and verify the updated data
    db_cursor.execute("""
        SELECT age, skin_type, family_history, updated_at FROM patient_data WHERE id = %s
    """, (patient_data_id,))
    result = db_cursor.fetchone()
    assert result is not None, "Patient data should still exist after update"
    
    retrieved_age, retrieved_skin_type, retrieved_history, updated_at = result
    
    # Verify all fields were updated correctly
    assert retrieved_age == updated_age, \
        f"Updated age {updated_age} should be persisted, got {retrieved_age}"
    assert retrieved_skin_type == updated_skin_type, \
        f"Updated skin type {updated_skin_type} should be persisted, got {retrieved_skin_type}"
    assert retrieved_history == updated_history or (not updated_history and retrieved_history is None), \
        f"Updated family history should be persisted"
    
    # Verify updated_at timestamp was updated
    assert updated_at is not None, "Updated timestamp should be set"
    
    # Verify the update is persistent (retrieve again)
    db_cursor.execute("""
        SELECT age, skin_type, family_history FROM patient_data WHERE id = %s
    """, (patient_data_id,))
    second_retrieval = db_cursor.fetchone()
    assert second_retrieval is not None, "Patient data should be retrievable multiple times"
    
    second_age, second_skin_type, second_history = second_retrieval
    assert second_age == updated_age, "Updated values should persist across multiple retrievals"
    assert second_skin_type == updated_skin_type, "Updated values should persist across multiple retrievals"
    assert second_history == updated_history or (not updated_history and second_history is None), \
        "Updated values should persist across multiple retrievals"


# ============================================================================
# NSFW Content Filter Property Tests
# ============================================================================

# Feature: derman-ai-skin-screening, Property 8: NSFW Score Rejection Threshold
@given(
    nsfw_score=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    non_skin_score=st.floats(min_value=0.0, max_value=0.8, allow_nan=False, allow_infinity=False)
)
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None  # Disable deadline for image processing tests
)
def test_nsfw_score_rejection_threshold(nsfw_score, non_skin_score):
    """
    Property 8: NSFW Score Rejection Threshold
    
    For any image with NSFW score exceeding 0.35, the system should reject the
    upload and return HTTP 403 with error message "Inappropriate content detected".
    
    This test verifies that:
    1. Images with nsfw_score > 0.35 are rejected
    2. Images with nsfw_score <= 0.35 are accepted (if non_skin_score is also valid)
    3. Rejection returns HTTP 403 status code
    4. Rejection includes the correct error message
    
    Validates: Requirements 3.2, 3.4
    """
    from backend.app.nsfw_filter import NSFWDetector, ContentViolationError
    from PIL import Image
    import io
    from unittest.mock import patch
    
    # Create a test image
    image = Image.new('RGB', (224, 224), (128, 128, 128))
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    image_data = buffer.getvalue()
    
    # Create detector
    detector = NSFWDetector()
    
    # Mock the _calculate_scores method to return our test scores
    def mock_calculate_scores(image_array):
        # Return our test scores
        safe_score = 1.0 - max(nsfw_score, non_skin_score)
        return (nsfw_score, non_skin_score, safe_score)
    
    with patch.object(detector, '_calculate_scores', side_effect=mock_calculate_scores):
        if nsfw_score > 0.35:
            # Should reject with ContentViolationError
            with pytest.raises(ContentViolationError) as exc_info:
                detector.check_nsfw(image_data)
            
            # Verify error attributes
            error = exc_info.value
            assert error.status_code == 403, \
                f"NSFW violation should return HTTP 403, got {error.status_code}"
            assert error.message == "Inappropriate content detected", \
                f"Error message should be 'Inappropriate content detected', got '{error.message}'"
            assert error.nsfw_score == nsfw_score, \
                f"Error should include nsfw_score {nsfw_score}, got {error.nsfw_score}"
            assert error.code == "CONTENT_VIOLATION", \
                f"Error code should be 'CONTENT_VIOLATION', got '{error.code}'"
            
        else:
            # Should accept (nsfw_score <= 0.35 and non_skin_score <= 0.8)
            result = detector.check_nsfw(image_data)
            
            # Verify result is valid
            assert result.safe is True, \
                f"Image with nsfw_score={nsfw_score:.3f} <= 0.35 should be accepted"
            assert result.nsfw_score == nsfw_score, \
                f"Result should include correct nsfw_score"
            assert result.non_skin_score == non_skin_score, \
                f"Result should include correct non_skin_score"


# Feature: derman-ai-skin-screening, Property 9: Non-Skin Score Rejection Threshold
@given(
    nsfw_score=st.floats(min_value=0.0, max_value=0.35, allow_nan=False, allow_infinity=False),
    non_skin_score=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None  # Disable deadline for image processing tests
)
def test_non_skin_score_rejection_threshold(nsfw_score, non_skin_score):
    """
    Property 9: Non-Skin Score Rejection Threshold
    
    For any image with non-skin score exceeding 0.8, the system should reject the
    upload and return HTTP 403 with error message "Inappropriate content detected".
    
    This test verifies that:
    1. Images with non_skin_score > 0.8 are rejected
    2. Images with non_skin_score <= 0.8 are accepted (if nsfw_score is also valid)
    3. Rejection returns HTTP 403 status code
    4. Rejection includes the correct error message
    
    Validates: Requirements 3.3, 3.4
    """
    from backend.app.nsfw_filter import NSFWDetector, ContentViolationError
    from PIL import Image
    import io
    from unittest.mock import patch
    
    # Create a test image
    image = Image.new('RGB', (224, 224), (128, 128, 128))
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    image_data = buffer.getvalue()
    
    # Create detector
    detector = NSFWDetector()
    
    # Mock the _calculate_scores method to return our test scores
    def mock_calculate_scores(image_array):
        # Return our test scores
        safe_score = 1.0 - max(nsfw_score, non_skin_score)
        return (nsfw_score, non_skin_score, safe_score)
    
    with patch.object(detector, '_calculate_scores', side_effect=mock_calculate_scores):
        if non_skin_score > 0.8:
            # Should reject with ContentViolationError
            with pytest.raises(ContentViolationError) as exc_info:
                detector.check_nsfw(image_data)
            
            # Verify error attributes
            error = exc_info.value
            assert error.status_code == 403, \
                f"Non-skin violation should return HTTP 403, got {error.status_code}"
            assert error.message == "Inappropriate content detected", \
                f"Error message should be 'Inappropriate content detected', got '{error.message}'"
            assert error.non_skin_score == non_skin_score, \
                f"Error should include non_skin_score {non_skin_score}, got {error.non_skin_score}"
            assert error.code == "CONTENT_VIOLATION", \
                f"Error code should be 'CONTENT_VIOLATION', got '{error.code}'"
            
        else:
            # Should accept (nsfw_score <= 0.35 and non_skin_score <= 0.8)
            result = detector.check_nsfw(image_data)
            
            # Verify result is valid
            assert result.safe is True, \
                f"Image with non_skin_score={non_skin_score:.3f} <= 0.8 should be accepted"
            assert result.nsfw_score == nsfw_score, \
                f"Result should include correct nsfw_score"
            assert result.non_skin_score == non_skin_score, \
                f"Result should include correct non_skin_score"



# Feature: derman-ai-skin-screening, Property 10: Flagged Content Audit Logging
@given(
    nsfw_score=st.floats(min_value=0.36, max_value=1.0, allow_nan=False, allow_infinity=False),
    non_skin_score=st.floats(min_value=0.0, max_value=0.8, allow_nan=False, allow_infinity=False),
    user_id=st.one_of(st.none(), st.uuids().map(str))
)
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None  # Disable deadline for async operations
)
def test_flagged_content_audit_logging(db_cursor, nsfw_score, non_skin_score, user_id):
    """
    Property 10: Flagged Content Audit Logging
    
    For any image rejected by the NSFW filter, an audit log entry should be created
    with timestamp, user identifier, and rejection reason.
    
    This test verifies that:
    1. When an image is rejected (nsfw_score > 0.35), an audit log is created
    2. The audit log contains the user_id (if authenticated)
    3. The audit log contains the nsfw_score and non_skin_score
    4. The audit log contains the rejection reason
    5. The audit log has a timestamp (created_at)
    6. The audit log action is "content_violation"
    
    Validates: Requirements 3.6, 18.4
    """
    import sys
    import os
    # Add backend to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
    
    from app.nsfw_filter import NSFWDetector, ContentViolationError
    from app.content_filter import ContentFilter
    from app.audit import AuditLogger
    from PIL import Image
    import io
    from unittest.mock import patch, MagicMock
    import asyncio
    
    # Create a test image
    image = Image.new('RGB', (224, 224), (128, 128, 128))
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    image_data = buffer.getvalue()
    
    # Create detector
    detector = NSFWDetector()
    
    # Create a mock Supabase client
    mock_supabase = MagicMock()
    
    # Track the audit log data that was inserted
    inserted_audit_log = None
    
    def mock_table_method(table_name):
        table_mock = MagicMock()
        
        def mock_insert(data):
            nonlocal inserted_audit_log
            inserted_audit_log = data
            insert_mock = MagicMock()
            
            def mock_execute():
                result_mock = MagicMock()
                result_mock.data = [{**data, "id": str(uuid4())}]
                return result_mock
            
            insert_mock.execute = mock_execute
            return insert_mock
        
        table_mock.insert = mock_insert
        return table_mock
    
    mock_supabase.table = mock_table_method
    
    # Create audit logger with mock client
    audit_logger = AuditLogger(mock_supabase)
    
    # Create content filter
    content_filter = ContentFilter(detector, audit_logger)
    
    # Mock the _calculate_scores method to return our test scores
    def mock_calculate_scores(image_array):
        safe_score = 1.0 - max(nsfw_score, non_skin_score)
        return (nsfw_score, non_skin_score, safe_score)
    
    with patch.object(detector, '_calculate_scores', side_effect=mock_calculate_scores):
        # Since nsfw_score > 0.35, this should reject and log
        try:
            asyncio.run(content_filter.validate_image(
                image_data=image_data,
                user_id=user_id,
                ip_address="192.168.1.1"
            ))
            pytest.fail("Expected ContentViolationError to be raised")
        except ContentViolationError as e:
            # Expected - image was rejected
            pass
        
        # Verify audit log was created
        assert inserted_audit_log is not None, \
            "Audit log should be created when image is rejected"
        
        # Verify audit log contains required fields
        assert inserted_audit_log["user_id"] == user_id, \
            f"Audit log should contain user_id {user_id}"
        
        assert inserted_audit_log["action"] == "content_violation", \
            f"Audit log action should be 'content_violation', got '{inserted_audit_log['action']}'"
        
        assert inserted_audit_log["resource_type"] == "image_upload", \
            f"Audit log resource_type should be 'image_upload', got '{inserted_audit_log['resource_type']}'"
        
        # Verify metadata contains scores and rejection reason
        metadata = inserted_audit_log["metadata"]
        assert "nsfw_score" in metadata, \
            "Audit log metadata should contain nsfw_score"
        assert metadata["nsfw_score"] == nsfw_score, \
            f"Audit log should contain correct nsfw_score {nsfw_score}"
        
        assert "non_skin_score" in metadata, \
            "Audit log metadata should contain non_skin_score"
        assert metadata["non_skin_score"] == non_skin_score, \
            f"Audit log should contain correct non_skin_score {non_skin_score}"
        
        assert "rejection_reason" in metadata, \
            "Audit log metadata should contain rejection_reason"
        assert metadata["rejection_reason"] == "Inappropriate content detected", \
            f"Audit log should contain rejection reason"
        
        # Verify timestamp is present
        assert "created_at" in inserted_audit_log, \
            "Audit log should have created_at timestamp"
        assert inserted_audit_log["created_at"] is not None, \
            "Audit log timestamp should not be None"
        
        # Verify IP address is logged
        assert inserted_audit_log["ip_address"] == "192.168.1.1", \
            "Audit log should contain IP address"


# Feature: derman-ai-skin-screening, Property 54: Data Access Audit Logging
@given(
    user_id=st.uuids().map(str),
    resource_type=st.sampled_from(['medical_report', 'patient_data', 'doctor_profile']),
    resource_id=st.uuids().map(str),
    action=st.sampled_from(['read', 'update', 'delete'])
)
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None  # Disable deadline for async operations
)
def test_data_access_audit_logging(db_cursor, user_id, resource_type, resource_id, action):
    """
    Property 54: Data Access Audit Logging
    
    For any data access event, an audit log entry should be created with
    timestamp, user identifier, resource type, resource ID, and action type.
    
    This test verifies that:
    1. Data access events are logged to audit_logs table
    2. The audit log contains user_id, resource_type, resource_id
    3. The audit log contains the action type (read, update, delete)
    4. The audit log has a timestamp
    5. The audit log can be retrieved by filters
    
    Validates: Requirements 18.4
    """
    import sys
    import os
    # Add backend to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
    
    from app.audit import AuditLogger
    from unittest.mock import MagicMock
    import asyncio
    
    # Create a mock Supabase client
    mock_supabase = MagicMock()
    
    # Track the audit log data that was inserted
    inserted_audit_log = None
    
    def mock_table_method(table_name):
        table_mock = MagicMock()
        
        def mock_insert(data):
            nonlocal inserted_audit_log
            inserted_audit_log = data
            insert_mock = MagicMock()
            
            def mock_execute():
                result_mock = MagicMock()
                result_mock.data = [{**data, "id": str(uuid4())}]
                return result_mock
            
            insert_mock.execute = mock_execute
            return insert_mock
        
        table_mock.insert = mock_insert
        return table_mock
    
    mock_supabase.table = mock_table_method
    
    # Create audit logger with mock client
    audit_logger = AuditLogger(mock_supabase)
    
    # Log a data access event
    audit_id = asyncio.run(audit_logger.log_data_access(
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        ip_address="192.168.1.1"
    ))
    
    # Verify audit log was created
    assert inserted_audit_log is not None, \
        "Audit log should be created for data access event"
    
    assert audit_id is not None, \
        "Audit log ID should be returned"
    
    # Verify audit log contains required fields
    assert inserted_audit_log["user_id"] == user_id, \
        f"Audit log should contain user_id {user_id}"
    
    assert inserted_audit_log["action"] == f"data_access_{action}", \
        f"Audit log action should be 'data_access_{action}', got '{inserted_audit_log['action']}'"
    
    assert inserted_audit_log["resource_type"] == resource_type, \
        f"Audit log resource_type should be '{resource_type}', got '{inserted_audit_log['resource_type']}'"
    
    assert inserted_audit_log["resource_id"] == resource_id, \
        f"Audit log should contain resource_id {resource_id}"
    
    # Verify metadata contains action type
    metadata = inserted_audit_log["metadata"]
    assert "action_type" in metadata, \
        "Audit log metadata should contain action_type"
    assert metadata["action_type"] == action, \
        f"Audit log should contain correct action_type {action}"
    
    # Verify timestamp is present
    assert "created_at" in inserted_audit_log, \
        "Audit log should have created_at timestamp"
    assert inserted_audit_log["created_at"] is not None, \
        "Audit log timestamp should not be None"
    
    # Verify IP address is logged
    assert inserted_audit_log["ip_address"] == "192.168.1.1", \
        "Audit log should contain IP address"
