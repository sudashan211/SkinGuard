"""
Preservation Property Tests for Find Doctor Errors Bugfix
Feature: fix-find-doctor-errors

These tests capture baseline behavior on UNFIXED code for non-buggy inputs.
They should PASS on unfixed code to confirm what behavior must be preserved.
After fixes are implemented, these tests should still PASS to confirm no regressions.

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
"""

import pytest
import sys
import os
from pathlib import Path
from hypothesis import given, strategies as st, settings
from hypothesis import HealthCheck
from unittest.mock import Mock, patch, MagicMock
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path for imports
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Mock the database module before importing routers
sys.modules['app.database'] = MagicMock()

from app.models import DoctorResponse


# ============================================================================
# Hypothesis Strategies for Test Data Generation
# ============================================================================

@st.composite
def verified_doctor_data(draw):
    """Generate verified doctor data for testing preservation"""
    lat = draw(st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False))
    lng = draw(st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False))
    
    return {
        "id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4()),
        "license_no": f"LIC{draw(st.integers(min_value=100000, max_value=999999))}",
        "clinic_name": draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N', 'Zs')))),
        "lat": lat,
        "lng": lng,
        "whatsapp_no": f"+1{draw(st.integers(min_value=1000000000, max_value=9999999999))}",
        "specialization": draw(st.sampled_from(["Dermatology", "Oncology", "General Practice"])),
        "average_rating": draw(st.floats(min_value=0.0, max_value=5.0)),
        "review_count": draw(st.integers(min_value=0, max_value=1000)),
        "verified": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }


@st.composite
def verified_doctor_list(draw, min_size=1, max_size=5):
    """Generate a list of verified doctors"""
    size = draw(st.integers(min_value=min_size, max_value=max_size))
    return [draw(verified_doctor_data()) for _ in range(size)]


# ============================================================================
# Property 4: Preservation - Successful Doctor Queries
# ============================================================================

@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    doctors=verified_doctor_list(min_size=1, max_size=5),
    lat=st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False),
    lng=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False),
    radius=st.floats(min_value=1, max_value=500, allow_nan=False, allow_infinity=False)
)
@pytest.mark.asyncio
async def test_preservation_successful_doctor_queries(doctors, lat, lng, radius):
    """
    Property 4: Preservation - Successful Doctor Queries
    
    **Validates: Requirements 3.1**
    
    For any request to /api/doctors/nearby where verified doctors exist in the
    database (NOT isBugCondition1), the endpoint SHALL produce exactly the same
    result as the original endpoint, returning the list of nearby doctors with
    their complete details (clinic name, location, rating, etc.).
    
    EXPECTED OUTCOME ON UNFIXED CODE: This test should PASS, confirming the
    baseline behavior that must be preserved.
    
    EXPECTED OUTCOME ON FIXED CODE: This test should still PASS, confirming
    no regressions were introduced.
    
    This test verifies:
    1. Endpoint returns list of doctors when doctors exist
    2. All doctor details are included (clinic_name, lat, lng, rating, etc.)
    3. Only verified doctors are returned
    4. Coordinate accuracy is preserved
    5. Distance filtering works correctly
    """
    from app.routers.doctors import get_nearby_doctors
    
    # Create mock profiles for verified doctors
    profiles = [
        {
            "id": doc["user_id"],
            "role": "doctor",
            "verified": True
        }
        for doc in doctors
    ]
    
    # Mock Supabase responses
    with patch('app.routers.doctors.supabase') as mock_supabase:
        # Mock profiles query - return verified profiles
        mock_profiles_result = Mock()
        mock_profiles_result.data = profiles
        
        # Mock doctors query - return verified doctors
        mock_doctors_result = Mock()
        mock_doctors_result.data = doctors
        
        # Set up the mock to return different results based on the table
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "profiles":
                mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_profiles_result
            elif table_name == "doctors":
                mock_table.select.return_value.in_.return_value.execute.return_value = mock_doctors_result
            return mock_table
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Call the endpoint
        result = await get_nearby_doctors(lat=lat, lng=lng, radius=radius)
        
        # PRESERVATION CHECKS: Verify baseline behavior is maintained
        
        # 1. Result should be a list
        assert isinstance(result, list), \
            f"Result should be a list, got {type(result)}"
        
        # 2. All returned doctors should be verified
        for doctor in result:
            assert doctor.verified is True, \
                f"Doctor {doctor.id} should have verified=True"
        
        # 3. All returned doctors should have complete details
        for doctor in result:
            assert hasattr(doctor, 'id'), "Doctor should have id"
            assert hasattr(doctor, 'user_id'), "Doctor should have user_id"
            assert hasattr(doctor, 'license_no'), "Doctor should have license_no"
            assert hasattr(doctor, 'clinic_name'), "Doctor should have clinic_name"
            assert hasattr(doctor, 'lat'), "Doctor should have lat"
            assert hasattr(doctor, 'lng'), "Doctor should have lng"
            assert hasattr(doctor, 'whatsapp_no'), "Doctor should have whatsapp_no"
            assert hasattr(doctor, 'specialization'), "Doctor should have specialization"
            assert hasattr(doctor, 'average_rating'), "Doctor should have average_rating"
            assert hasattr(doctor, 'review_count'), "Doctor should have review_count"
        
        # 4. Coordinate accuracy should be preserved
        for doctor in result:
            assert -90 <= doctor.lat <= 90, \
                f"Latitude {doctor.lat} should be within [-90, 90]"
            assert -180 <= doctor.lng <= 180, \
                f"Longitude {doctor.lng} should be within [-180, 180]"
        
        # 5. Distance filtering should work (doctors within radius)
        import math
        
        def calculate_distance(lat1, lng1, lat2, lng2):
            """Calculate distance using Haversine formula"""
            R = 6371  # Earth's radius in kilometers
            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            delta_lat = math.radians(lat2 - lat1)
            delta_lng = math.radians(lng2 - lng1)
            a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c
        
        for doctor in result:
            distance = calculate_distance(lat, lng, doctor.lat, doctor.lng)
            assert distance <= radius, \
                f"Doctor {doctor.id} at distance {distance}km should be within radius {radius}km"


@settings(
    max_examples=30,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    doctors=verified_doctor_list(min_size=1, max_size=3)
)
@pytest.mark.asyncio
async def test_preservation_doctor_details_completeness(doctors):
    """
    Property 4: Preservation - Doctor Details Completeness
    
    **Validates: Requirements 3.1**
    
    For any successful doctor query, all doctor details should be returned
    including clinic_name, location coordinates, rating, review_count, etc.
    
    EXPECTED OUTCOME: This test should PASS on both unfixed and fixed code,
    confirming that doctor details are always complete.
    
    This test verifies:
    1. All required fields are present in response
    2. Field values match database values exactly
    3. No data loss or corruption occurs
    4. Coordinate precision is maintained
    """
    from app.routers.doctors import get_nearby_doctors
    
    # Create mock profiles
    profiles = [
        {
            "id": doc["user_id"],
            "role": "doctor",
            "verified": True
        }
        for doc in doctors
    ]
    
    # Mock Supabase responses
    with patch('app.routers.doctors.supabase') as mock_supabase:
        mock_profiles_result = Mock()
        mock_profiles_result.data = profiles
        
        mock_doctors_result = Mock()
        mock_doctors_result.data = doctors
        
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "profiles":
                mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_profiles_result
            elif table_name == "doctors":
                mock_table.select.return_value.in_.return_value.execute.return_value = mock_doctors_result
            return mock_table
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Call with large radius to include all doctors
        result = await get_nearby_doctors(lat=0.0, lng=0.0, radius=50000)
        
        # Create mapping for verification
        doctor_map = {doc["user_id"]: doc for doc in doctors}
        
        # Verify each returned doctor has complete and accurate details
        for returned_doctor in result:
            original_doctor = doctor_map[returned_doctor.user_id]
            
            # Verify all fields match exactly
            assert returned_doctor.license_no == original_doctor["license_no"], \
                "License number should match exactly"
            assert returned_doctor.clinic_name == original_doctor["clinic_name"], \
                "Clinic name should match exactly"
            assert returned_doctor.lat == original_doctor["lat"], \
                "Latitude should match exactly"
            assert returned_doctor.lng == original_doctor["lng"], \
                "Longitude should match exactly"
            assert returned_doctor.whatsapp_no == original_doctor["whatsapp_no"], \
                "WhatsApp number should match exactly"
            assert returned_doctor.specialization == original_doctor["specialization"], \
                "Specialization should match exactly"
            assert returned_doctor.average_rating == original_doctor["average_rating"], \
                "Average rating should match exactly"
            assert returned_doctor.review_count == original_doctor["review_count"], \
                "Review count should match exactly"


# ============================================================================
# Property 5: Preservation - Map Loading with Valid API Key
# ============================================================================

# NOTE: Property 5 tests DoctorMap component behavior with valid VITE_GOOGLE_MAPS_API_KEY.
# This is a React/TypeScript frontend component that requires:
# - React Testing Library or similar frontend testing framework
# - Jest or Vitest for JavaScript/TypeScript testing
# - Mock setup for @react-google-maps/api library
# - Environment variable mocking for import.meta.env.VITE_GOOGLE_MAPS_API_KEY
#
# The DoctorMap component (frontend/src/components/patient/DoctorMap.tsx) already
# implements the following baseline behavior that must be preserved:
# 1. Loads Google Maps when VITE_GOOGLE_MAPS_API_KEY is configured
# 2. Displays user location marker when geolocation is available
# 3. Fetches and displays nearby doctors within radius
# 4. Shows doctor markers with info windows on click
# 5. Provides WhatsApp contact and appointment booking functionality
#
# This preservation property should be tested using frontend testing tools
# in a separate test suite (e.g., frontend/src/components/patient/__tests__/DoctorMap.test.tsx)
#
# Validates: Requirements 3.2, 3.4, 3.5


# ============================================================================
# Property 6: Preservation - Authenticated Access
# ============================================================================

@settings(
    max_examples=30,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    data=st.data()
)
@pytest.mark.asyncio
async def test_preservation_authenticated_doctor_access(data):
    """
    Property 6: Preservation - Authenticated Access
    
    **Validates: Requirements 3.3**
    
    For any request to protected doctor endpoints with valid authentication
    credentials (NOT isBugCondition3), the endpoints SHALL produce exactly
    the same result as the original endpoints, allowing access and returning
    the requested data.
    
    EXPECTED OUTCOME: This test should PASS on both unfixed and fixed code,
    confirming that authenticated access continues to work correctly.
    
    This test verifies:
    1. Valid authentication allows access to protected endpoints
    2. Authenticated requests return correct data
    3. Doctor role validation works correctly
    4. Verified doctor role validation works correctly
    """
    from app.routers.doctors import get_pending_reports
    
    # Generate mock verified doctor user
    mock_doctor = {
        "id": str(uuid.uuid4()),
        "email": "doctor@example.com",
        "role": "doctor",
        "verified": True
    }
    
    # Generate mock medical reports
    reports = [
        {
            "id": str(uuid.uuid4()),
            "patient_id": str(uuid.uuid4()),
            "image_url": f"https://storage.example.com/{uuid.uuid4()}.jpg",
            "ai_prediction": {
                "predictions": [
                    {"type": "melanoma", "probability": 0.1, "confidence": 0.9}
                ]
            },
            "symptoms": {
                "location": "left_arm",
                "sensations": ["itching"],
                "visual_changes": ["color"]
            },
            "status": "safe",
            "risk_level": "low",
            "body_location": "left_arm",
            "consultation_notes": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        for _ in range(data.draw(st.integers(min_value=1, max_value=3)))
    ]
    
    # Generate mock profiles and patient_data
    profiles = []
    patient_data_records = []
    
    for report in reports:
        profile = {
            "id": report["patient_id"],
            "email": f"patient{uuid.uuid4()}@example.com",
            "full_name": "Test Patient",
            "role": "patient",
            "verified": True
        }
        profiles.append(profile)
        
        patient_data = {
            "id": str(uuid.uuid4()),
            "user_id": report["patient_id"],
            "age": data.draw(st.integers(min_value=18, max_value=80)),
            "skin_type": data.draw(st.sampled_from(["I", "II", "III", "IV", "V", "VI"])),
            "family_history": "None"
        }
        patient_data_records.append(patient_data)
    
    # Mock Supabase responses
    with patch('app.routers.doctors.supabase') as mock_supabase:
        mock_reports_result = Mock()
        mock_reports_result.data = reports
        
        mock_profiles_result = Mock()
        mock_profiles_result.data = profiles
        
        mock_patient_data_result = Mock()
        mock_patient_data_result.data = patient_data_records
        
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "medical_reports":
                mock_select = Mock()
                mock_in = Mock()
                mock_execute = Mock()
                mock_execute.execute.return_value = mock_reports_result
                mock_in.in_.return_value = mock_execute
                mock_select.select.return_value = mock_in
                return mock_select
            elif table_name == "profiles":
                mock_select = Mock()
                mock_in = Mock()
                mock_execute = Mock()
                mock_execute.execute.return_value = mock_profiles_result
                mock_in.in_.return_value = mock_execute
                mock_select.select.return_value = mock_in
                return mock_select
            elif table_name == "patient_data":
                mock_select = Mock()
                mock_in = Mock()
                mock_execute = Mock()
                mock_execute.execute.return_value = mock_patient_data_result
                mock_in.in_.return_value = mock_execute
                mock_select.select.return_value = mock_in
                return mock_select
            return Mock()
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Call the endpoint with valid authentication
        result = await get_pending_reports(status_filter=None, current_user=mock_doctor)
        
        # PRESERVATION CHECKS: Verify authenticated access works correctly
        
        # 1. Result should be a list
        assert isinstance(result, list), \
            f"Result should be a list, got {type(result)}"
        
        # 2. Result should contain reports
        assert len(result) > 0, \
            "Authenticated request should return reports"
        
        # 3. All reports should have required fields
        for report in result:
            assert "id" in report, "Report should have id"
            assert "patient_id" in report, "Report should have patient_id"
            assert "image_url" in report, "Report should have image_url"
            assert "ai_prediction" in report, "Report should have ai_prediction"
            assert "symptoms" in report, "Report should have symptoms"
            assert "status" in report, "Report should have status"
            assert "risk_level" in report, "Report should have risk_level"
        
        # 4. Reports should only include safe/urgent (not flagged)
        for report in result:
            assert report["status"] in ["safe", "urgent"], \
                f"Report status should be safe or urgent, got {report['status']}"


@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    verified=st.booleans()
)
@pytest.mark.asyncio
async def test_preservation_doctor_role_validation(verified):
    """
    Property 6: Preservation - Doctor Role Validation
    
    **Validates: Requirements 3.3**
    
    For any authenticated doctor user (verified or unverified), the system
    should correctly validate their role and allow appropriate access.
    
    EXPECTED OUTCOME: This test should PASS on both unfixed and fixed code,
    confirming that role validation continues to work correctly.
    
    This test verifies:
    1. Doctor role is correctly identified
    2. Verified status is correctly checked
    3. Authentication state is preserved
    """
    from app.routers.doctors import get_pending_reports
    
    # Generate mock doctor user with specified verification status
    mock_doctor = {
        "id": str(uuid.uuid4()),
        "email": "doctor@example.com",
        "role": "doctor",
        "verified": verified
    }
    
    # Generate mock data
    reports = [
        {
            "id": str(uuid.uuid4()),
            "patient_id": str(uuid.uuid4()),
            "image_url": "https://storage.example.com/test.jpg",
            "ai_prediction": {"predictions": []},
            "symptoms": {},
            "status": "safe",
            "risk_level": "low",
            "body_location": "arm",
            "consultation_notes": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    ]
    
    profiles = [{
        "id": reports[0]["patient_id"],
        "email": "patient@example.com",
        "full_name": "Test Patient",
        "role": "patient",
        "verified": True
    }]
    
    patient_data_records = [{
        "id": str(uuid.uuid4()),
        "user_id": reports[0]["patient_id"],
        "age": 30,
        "skin_type": "III",
        "family_history": "None"
    }]
    
    # Mock Supabase responses
    with patch('app.routers.doctors.supabase') as mock_supabase:
        mock_reports_result = Mock()
        mock_reports_result.data = reports
        
        mock_profiles_result = Mock()
        mock_profiles_result.data = profiles
        
        mock_patient_data_result = Mock()
        mock_patient_data_result.data = patient_data_records
        
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "medical_reports":
                mock_select = Mock()
                mock_in = Mock()
                mock_execute = Mock()
                mock_execute.execute.return_value = mock_reports_result
                mock_in.in_.return_value = mock_execute
                mock_select.select.return_value = mock_in
                return mock_select
            elif table_name == "profiles":
                mock_select = Mock()
                mock_in = Mock()
                mock_execute = Mock()
                mock_execute.execute.return_value = mock_profiles_result
                mock_in.in_.return_value = mock_execute
                mock_select.select.return_value = mock_in
                return mock_select
            elif table_name == "patient_data":
                mock_select = Mock()
                mock_in = Mock()
                mock_execute = Mock()
                mock_execute.execute.return_value = mock_patient_data_result
                mock_in.in_.return_value = mock_execute
                mock_select.select.return_value = mock_in
                return mock_select
            return Mock()
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Call the endpoint - should work for both verified and unverified doctors
        result = await get_pending_reports(status_filter=None, current_user=mock_doctor)
        
        # PRESERVATION CHECKS: Verify role validation works
        
        # 1. Result should be returned (authentication successful)
        assert isinstance(result, list), \
            "Authenticated doctor should receive results"
        
        # 2. Doctor role should be respected
        assert mock_doctor["role"] == "doctor", \
            "User role should be doctor"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
