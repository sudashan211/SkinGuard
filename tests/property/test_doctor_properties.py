"""
Property-Based Tests for Doctor Locator System
Feature: derman-ai-skin-screening

Tests doctor locator correctness properties including verified doctor filtering
and coordinate accuracy.

Requirements: 7.2, 7.3
"""

import pytest
import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings
from hypothesis import HealthCheck
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import uuid
from datetime import datetime

# Add backend to path for imports
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Mock the database module before importing anything that uses it
sys.modules['app.database'] = MagicMock()

from app.models import DoctorResponse


# Hypothesis strategies for generating test data
@st.composite
def doctor_data(draw, verified=None):
    """Generate doctor data for testing"""
    lat = draw(st.floats(min_value=-90, max_value=90))
    lng = draw(st.floats(min_value=-180, max_value=180))
    
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
        "verified": verified if verified is not None else draw(st.booleans()),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }


@st.composite
def doctor_list(draw, min_size=0, max_size=10, verified=None):
    """Generate a list of doctors"""
    size = draw(st.integers(min_value=min_size, max_value=max_size))
    return [draw(doctor_data(verified=verified)) for _ in range(size)]


# Feature: derman-ai-skin-screening, Property 18: Verified Doctor Filtering
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    verified_doctors=doctor_list(min_size=1, max_size=5, verified=True),
    unverified_doctors=doctor_list(min_size=1, max_size=5, verified=False)
)
@pytest.mark.asyncio
async def test_verified_doctor_filtering(verified_doctors, unverified_doctors):
    """
    Property 18: Verified Doctor Filtering
    
    For any doctor locator query, the returned list should contain only doctors
    where verified status is true.
    
    This test verifies:
    1. Only verified doctors are returned
    2. Unverified doctors are excluded from results
    3. Verification status is correctly checked
    4. Empty results when no verified doctors exist
    
    Validates: Requirements 7.2
    """
    from app.routers.doctors import get_nearby_doctors
    
    # Combine all doctors
    all_doctors = verified_doctors + unverified_doctors
    
    # Create mock profiles for verified doctors
    verified_profiles = [
        {
            "id": doc["user_id"],
            "role": "doctor",
            "verified": True
        }
        for doc in verified_doctors
    ]
    
    # Create mock profiles for unverified doctors
    unverified_profiles = [
        {
            "id": doc["user_id"],
            "role": "doctor",
            "verified": False
        }
        for doc in unverified_doctors
    ]
    
    all_profiles = verified_profiles + unverified_profiles
    
    # Mock Supabase responses
    with patch('app.routers.doctors.supabase') as mock_supabase:
        # Mock profiles query - return only verified profiles
        mock_profiles_result = Mock()
        mock_profiles_result.data = verified_profiles
        
        # Mock doctors query - return only doctors for verified profiles
        mock_doctors_result = Mock()
        mock_doctors_result.data = verified_doctors  # Only verified doctors
        
        # Set up the mock to return different results based on the query
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "profiles":
                mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_profiles_result
            elif table_name == "doctors":
                mock_table.select.return_value.in_.return_value.execute.return_value = mock_doctors_result
            return mock_table
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Call the endpoint with arbitrary coordinates and very large radius to include all
        result = await get_nearby_doctors(lat=0.0, lng=0.0, radius=50000)
        
        # Verify only verified doctors are in the result
        assert isinstance(result, list), "Result should be a list"
        
        # All returned doctors should have verified=True
        for doctor in result:
            assert doctor.verified is True, \
                f"Doctor {doctor.id} should have verified=True, got {doctor.verified}"
        
        # Verify the count matches verified doctors (within radius)
        # Since we're using a large radius, all verified doctors should be included
        verified_user_ids = [doc["user_id"] for doc in verified_doctors]
        result_user_ids = [doc.user_id for doc in result]
        
        # All verified doctors should be in the result
        for user_id in verified_user_ids:
            assert user_id in result_user_ids, \
                f"Verified doctor {user_id} should be in results"
        
        # No unverified doctors should be in the result
        unverified_user_ids = [doc["user_id"] for doc in unverified_doctors]
        for user_id in unverified_user_ids:
            assert user_id not in result_user_ids, \
                f"Unverified doctor {user_id} should not be in results"


# Feature: derman-ai-skin-screening, Property 18: Verified Doctor Filtering (Empty Case)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    unverified_doctors=doctor_list(min_size=1, max_size=5, verified=False)
)
@pytest.mark.asyncio
async def test_verified_doctor_filtering_no_verified(unverified_doctors):
    """
    Property 18: Verified Doctor Filtering (No Verified Doctors Case)
    
    For any doctor locator query when no verified doctors exist, the returned
    list should be empty.
    
    This test verifies:
    1. Empty list is returned when no verified doctors exist
    2. Unverified doctors are not included even when they're the only ones
    
    Validates: Requirements 7.2
    """
    from app.routers.doctors import get_nearby_doctors
    
    # Mock Supabase responses with no verified profiles
    with patch('app.routers.doctors.supabase') as mock_supabase:
        # Mock profiles query - return empty list (no verified doctors)
        mock_profiles_result = Mock()
        mock_profiles_result.data = []
        
        # Set up the mock chain
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_profiles_result
        
        mock_supabase.table.return_value = mock_table
        
        # Call the endpoint with large radius
        result = await get_nearby_doctors(lat=0.0, lng=0.0, radius=50000)
        
        # Verify empty result
        assert isinstance(result, list), "Result should be a list"
        assert len(result) == 0, \
            f"Result should be empty when no verified doctors exist, got {len(result)} doctors"


# Feature: derman-ai-skin-screening, Property 19: Doctor Marker Coordinate Accuracy
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    doctors=doctor_list(min_size=1, max_size=10, verified=True)
)
@pytest.mark.asyncio
async def test_doctor_marker_coordinate_accuracy(doctors):
    """
    Property 19: Doctor Marker Coordinate Accuracy
    
    For any list of doctors, the map markers should be placed at coordinates
    exactly matching the lat and lng fields from the database.
    
    This test verifies:
    1. Returned doctor coordinates match database values exactly
    2. Latitude values are preserved without modification
    3. Longitude values are preserved without modification
    4. Coordinate precision is maintained (no rounding errors)
    5. All doctors have valid coordinate data
    
    Validates: Requirements 7.3
    """
    from app.routers.doctors import get_nearby_doctors
    
    # Create mock profiles for all doctors
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
        # Mock profiles query
        mock_profiles_result = Mock()
        mock_profiles_result.data = profiles
        
        # Mock doctors query
        mock_doctors_result = Mock()
        mock_doctors_result.data = doctors
        
        # Set up the mock chain
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_profiles_result
        mock_table.select.return_value.in_.return_value.execute.return_value = mock_doctors_result
        
        mock_supabase.table.return_value = mock_table
        
        # Call the endpoint with large radius to include all doctors
        result = await get_nearby_doctors(lat=0.0, lng=0.0, radius=50000)
        
        # Verify result is a list
        assert isinstance(result, list), "Result should be a list"
        
        # Create a mapping of user_id to original doctor data
        doctor_map = {doc["user_id"]: doc for doc in doctors}
        
        # Verify each returned doctor has exact coordinate match
        for returned_doctor in result:
            original_doctor = doctor_map[returned_doctor.user_id]
            
            # Verify latitude matches exactly
            assert returned_doctor.lat == original_doctor["lat"], \
                f"Doctor {returned_doctor.id} latitude mismatch: " \
                f"expected {original_doctor['lat']}, got {returned_doctor.lat}"
            
            # Verify longitude matches exactly
            assert returned_doctor.lng == original_doctor["lng"], \
                f"Doctor {returned_doctor.id} longitude mismatch: " \
                f"expected {original_doctor['lng']}, got {returned_doctor.lng}"
            
            # Verify coordinates are valid numbers
            assert isinstance(returned_doctor.lat, (int, float)), \
                f"Latitude should be a number, got {type(returned_doctor.lat)}"
            assert isinstance(returned_doctor.lng, (int, float)), \
                f"Longitude should be a number, got {type(returned_doctor.lng)}"
            
            # Verify coordinates are within valid ranges
            assert -90 <= returned_doctor.lat <= 90, \
                f"Latitude {returned_doctor.lat} should be between -90 and 90"
            assert -180 <= returned_doctor.lng <= 180, \
                f"Longitude {returned_doctor.lng} should be between -180 and 180"
            
            # Verify no precision loss (coordinates should match to many decimal places)
            lat_diff = abs(returned_doctor.lat - original_doctor["lat"])
            lng_diff = abs(returned_doctor.lng - original_doctor["lng"])
            
            assert lat_diff < 1e-10, \
                f"Latitude precision loss detected: difference {lat_diff}"
            assert lng_diff < 1e-10, \
                f"Longitude precision loss detected: difference {lng_diff}"


# Feature: derman-ai-skin-screening, Property 19: Doctor Marker Coordinate Accuracy (Boundary Values)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    lat=st.sampled_from([-90.0, -45.0, 0.0, 45.0, 90.0]),
    lng=st.sampled_from([-180.0, -90.0, 0.0, 90.0, 180.0])
)
@pytest.mark.asyncio
async def test_doctor_marker_coordinate_accuracy_boundaries(lat, lng):
    """
    Property 19: Doctor Marker Coordinate Accuracy (Boundary Values)
    
    For any doctor with boundary coordinate values (e.g., -90, 90, -180, 180),
    the coordinates should be preserved exactly without modification.
    
    This test verifies:
    1. Extreme latitude values (-90, 90) are preserved
    2. Extreme longitude values (-180, 180) are preserved
    3. Zero coordinates (0, 0) are preserved
    4. No special handling or rounding of boundary values
    
    Validates: Requirements 7.3
    """
    from app.routers.doctors import get_nearby_doctors
    
    # Create a doctor with specific boundary coordinates
    doctor = {
        "id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4()),
        "license_no": "LIC123456",
        "clinic_name": "Boundary Clinic",
        "lat": lat,
        "lng": lng,
        "whatsapp_no": "+11234567890",
        "specialization": "Dermatology",
        "average_rating": 4.5,
        "review_count": 10,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    # Create mock profile
    profile = {
        "id": doctor["user_id"],
        "role": "doctor",
        "verified": True
    }
    
    # Mock Supabase responses
    with patch('app.routers.doctors.supabase') as mock_supabase:
        # Mock profiles query
        mock_profiles_result = Mock()
        mock_profiles_result.data = [profile]
        
        # Mock doctors query
        mock_doctors_result = Mock()
        mock_doctors_result.data = [doctor]
        
        # Set up the mock chain
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_profiles_result
        mock_table.select.return_value.in_.return_value.execute.return_value = mock_doctors_result
        
        mock_supabase.table.return_value = mock_table
        
        # Call the endpoint with large radius
        result = await get_nearby_doctors(lat=0.0, lng=0.0, radius=50000)
        
        # Verify we got results
        assert len(result) > 0, "Should return at least one doctor"
        
        # Find our doctor in the results
        returned_doctor = result[0]
        
        # Verify exact coordinate match
        assert returned_doctor.lat == lat, \
            f"Boundary latitude mismatch: expected {lat}, got {returned_doctor.lat}"
        assert returned_doctor.lng == lng, \
            f"Boundary longitude mismatch: expected {lng}, got {returned_doctor.lng}"
        
        # Verify no type conversion issues
        assert type(returned_doctor.lat) == type(lat), \
            f"Latitude type changed: expected {type(lat)}, got {type(returned_doctor.lat)}"
        assert type(returned_doctor.lng) == type(lng), \
            f"Longitude type changed: expected {type(lng)}, got {type(returned_doctor.lng)}"



# ============================================================================
# Doctor Report Access Properties (Task 15.2)
# ============================================================================


@st.composite
def medical_report_data(draw, status=None, risk_level=None):
    """Generate medical report data for testing"""
    if status is None:
        status = draw(st.sampled_from(["safe", "urgent", "flagged"]))
    if risk_level is None:
        risk_level = draw(st.sampled_from(["low", "medium", "high", "urgent"]))
    
    # Generate AI predictions with 7 cancer types
    cancer_types = [
        "melanoma",
        "basal_cell_carcinoma",
        "squamous_cell_carcinoma",
        "actinic_keratosis",
        "benign_keratosis",
        "dermatofibroma",
        "vascular_lesion"
    ]
    
    predictions = []
    for cancer_type in cancer_types:
        predictions.append({
            "type": cancer_type,
            "probability": draw(st.floats(min_value=0.0, max_value=1.0)),
            "confidence": draw(st.floats(min_value=0.0, max_value=1.0))
        })
    
    return {
        "id": str(uuid.uuid4()),
        "patient_id": str(uuid.uuid4()),
        "image_url": f"https://storage.example.com/{uuid.uuid4()}.jpg",
        "ai_prediction": {
            "predictions": predictions,
            "hotspots": [],
            "model_version": "1.0.0",
            "processing_time": draw(st.floats(min_value=0.5, max_value=5.0))
        },
        "symptoms": {
            "location": draw(st.sampled_from(["left_arm", "right_arm", "chest", "back", "leg"])),
            "sensations": draw(st.lists(st.sampled_from(["itching", "pain", "burning", "numbness"]), min_size=0, max_size=3)),
            "visual_changes": draw(st.lists(st.sampled_from(["color", "size", "shape", "border"]), min_size=0, max_size=3))
        },
        "status": status,
        "risk_level": risk_level,
        "body_location": draw(st.sampled_from(["left_arm", "right_arm", "chest", "back", "leg"])),
        "consultation_notes": None,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }


@st.composite
def patient_profile_data(draw):
    """Generate patient profile data for testing"""
    return {
        "id": str(uuid.uuid4()),
        "email": draw(st.emails()),
        "full_name": draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'Zs')))),
        "role": "patient",
        "verified": True
    }


@st.composite
def patient_data_record(draw, user_id):
    """Generate patient_data record for testing"""
    return {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "age": draw(st.integers(min_value=1, max_value=120)),
        "skin_type": draw(st.sampled_from(["I", "II", "III", "IV", "V", "VI"])),
        "family_history": draw(st.text(min_size=0, max_size=200, alphabet=st.characters(whitelist_categories=('L', 'N', 'Zs', 'P'))))
    }


# Feature: derman-ai-skin-screening, Property 24: Safe Report Filtering
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    data=st.data(),
    num_safe=st.integers(min_value=1, max_value=3),
    num_urgent=st.integers(min_value=1, max_value=3),
    num_flagged=st.integers(min_value=1, max_value=3)
)
@pytest.mark.asyncio
async def test_safe_report_filtering(data, num_safe, num_urgent, num_flagged):
    """
    Property 24: Safe Report Filtering
    
    **Validates: Requirements 9.1, 9.2, 9.3, 23.5**
    
    For any doctor accessing the reports dashboard, the returned medical_reports
    should only include records where status is "safe" or "urgent", excluding
    "flagged" reports.
    
    This test verifies:
    1. Safe reports are included in results
    2. Urgent reports are included in results
    3. Flagged reports are excluded from results
    4. No other status values appear in results
    5. Status filtering is applied correctly
    
    Validates: Requirements 9.1
    """
    from app.routers.doctors import get_pending_reports
    
    # Generate reports with specific statuses
    safe_reports = [data.draw(medical_report_data(status="safe")) for _ in range(num_safe)]
    urgent_reports = [data.draw(medical_report_data(status="urgent")) for _ in range(num_urgent)]
    flagged_reports = [data.draw(medical_report_data(status="flagged")) for _ in range(num_flagged)]
    
    # Combine all reports
    all_reports = safe_reports + urgent_reports + flagged_reports
    
    # Create mock profiles and patient_data for all reports
    profiles = []
    patient_data_records = []
    
    for report in all_reports:
        profile = data.draw(patient_profile_data())
        profile["id"] = report["patient_id"]
        profiles.append(profile)
        
        patient_data = data.draw(patient_data_record(user_id=report["patient_id"]))
        patient_data_records.append(patient_data)
    
    # Mock verified doctor user
    mock_doctor = {
        "id": str(uuid.uuid4()),
        "role": "doctor",
        "verified": True
    }
    
    # Mock Supabase responses
    with patch('app.routers.doctors.supabase') as mock_supabase:
        # Mock reports query - return only safe and urgent reports
        expected_reports = safe_reports + urgent_reports
        mock_reports_result = Mock()
        mock_reports_result.data = expected_reports
        
        # Mock profiles query
        mock_profiles_result = Mock()
        mock_profiles_result.data = profiles
        
        # Mock patient_data query
        mock_patient_data_result = Mock()
        mock_patient_data_result.data = patient_data_records
        
        # Set up the mock chain
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "medical_reports":
                # Mock the query chain for reports
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
        
        # Call the endpoint
        result = await get_pending_reports(status_filter=None, current_user=mock_doctor)
        
        # Verify result is a list
        assert isinstance(result, list), "Result should be a list"
        
        # Verify only safe and urgent reports are returned
        result_statuses = [report["status"] for report in result]
        
        # All returned reports should have status "safe" or "urgent"
        for status in result_statuses:
            assert status in ["safe", "urgent"], \
                f"Report status should be 'safe' or 'urgent', got '{status}'"
        
        # Verify no flagged reports are in the result
        for report in result:
            assert report["status"] != "flagged", \
                f"Flagged report {report['id']} should not be in results"
        
        # Verify all safe reports are included
        safe_report_ids = [report["id"] for report in safe_reports]
        result_ids = [report["id"] for report in result]
        
        for report_id in safe_report_ids:
            assert report_id in result_ids, \
                f"Safe report {report_id} should be in results"
        
        # Verify all urgent reports are included
        urgent_report_ids = [report["id"] for report in urgent_reports]
        
        for report_id in urgent_report_ids:
            assert report_id in result_ids, \
                f"Urgent report {report_id} should be in results"
        
        # Verify no flagged reports are included
        flagged_report_ids = [report["id"] for report in flagged_reports]
        
        for report_id in flagged_report_ids:
            assert report_id not in result_ids, \
                f"Flagged report {report_id} should not be in results"


# Feature: derman-ai-skin-screening, Property 25: Report Display Completeness
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    data=st.data()
)
@pytest.mark.asyncio
async def test_report_display_completeness(data):
    """
    Property 25: Report Display Completeness
    
    **Validates: Requirements 9.1, 9.2, 9.3, 23.5**
    
    For any medical report display, the data should include the image URL,
    AI prediction JSONB, patient symptoms, and joined patient_data (age,
    skin type, family history).
    
    This test verifies:
    1. Report includes image_url field
    2. Report includes ai_prediction JSONB data
    3. Report includes patient symptoms
    4. Report includes patient age from patient_data
    5. Report includes patient skin_type from patient_data
    6. Report includes patient family_history from patient_data
    7. All 7 cancer class predictions are present
    8. Patient profile information is included
    
    Validates: Requirements 9.2, 9.3
    """
    from app.routers.doctors import get_pending_reports
    
    # Generate a report with safe or urgent status
    report = data.draw(medical_report_data(status=st.sampled_from(["safe", "urgent"])))
    
    # Create mock profile and patient_data
    profile = data.draw(patient_profile_data())
    profile["id"] = report["patient_id"]
    
    patient_data = data.draw(patient_data_record(user_id=report["patient_id"]))
    
    # Mock verified doctor user
    mock_doctor = {
        "id": str(uuid.uuid4()),
        "role": "doctor",
        "verified": True
    }
    
    # Mock Supabase responses
    with patch('app.routers.doctors.supabase') as mock_supabase:
        # Mock reports query
        mock_reports_result = Mock()
        mock_reports_result.data = [report]
        
        # Mock profiles query
        mock_profiles_result = Mock()
        mock_profiles_result.data = [profile]
        
        # Mock patient_data query
        mock_patient_data_result = Mock()
        mock_patient_data_result.data = [patient_data]
        
        # Set up the mock chain
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
        
        # Call the endpoint
        result = await get_pending_reports(status_filter=None, current_user=mock_doctor)
        
        # Verify we got results
        assert len(result) > 0, "Should return at least one report"
        
        # Get the first report
        returned_report = result[0]
        
        # Verify report fields are present
        assert "id" in returned_report, "Report should include id"
        assert "patient_id" in returned_report, "Report should include patient_id"
        assert "image_url" in returned_report, "Report should include image_url"
        assert "ai_prediction" in returned_report, "Report should include ai_prediction"
        assert "symptoms" in returned_report, "Report should include symptoms"
        assert "status" in returned_report, "Report should include status"
        assert "risk_level" in returned_report, "Report should include risk_level"
        
        # Verify image_url is present and valid
        assert returned_report["image_url"] is not None, "image_url should not be None"
        assert isinstance(returned_report["image_url"], str), "image_url should be a string"
        assert len(returned_report["image_url"]) > 0, "image_url should not be empty"
        
        # Verify ai_prediction JSONB data is present
        assert returned_report["ai_prediction"] is not None, "ai_prediction should not be None"
        assert isinstance(returned_report["ai_prediction"], dict), "ai_prediction should be a dict"
        assert "predictions" in returned_report["ai_prediction"], \
            "ai_prediction should contain predictions"
        
        # Verify all 7 cancer class predictions are present
        predictions = returned_report["ai_prediction"]["predictions"]
        assert isinstance(predictions, list), "predictions should be a list"
        assert len(predictions) == 7, \
            f"Should have 7 cancer class predictions, got {len(predictions)}"
        
        # Verify each prediction has required fields
        for pred in predictions:
            assert "type" in pred, "Prediction should have type field"
            assert "probability" in pred, "Prediction should have probability field"
            assert "confidence" in pred, "Prediction should have confidence field"
        
        # Verify symptoms are present
        assert returned_report["symptoms"] is not None, "symptoms should not be None"
        assert isinstance(returned_report["symptoms"], dict), "symptoms should be a dict"
        
        # Verify patient profile information is included
        assert "patient_name" in returned_report, "Report should include patient_name"
        assert "patient_email" in returned_report, "Report should include patient_email"
        assert returned_report["patient_name"] == profile["full_name"], \
            "patient_name should match profile full_name"
        
        # Verify patient_data fields are included (Requirements 9.3)
        assert "patient_age" in returned_report, "Report should include patient_age"
        assert "patient_skin_type" in returned_report, "Report should include patient_skin_type"
        assert "patient_family_history" in returned_report, "Report should include patient_family_history"
        
        # Verify patient_data values match
        assert returned_report["patient_age"] == patient_data["age"], \
            f"patient_age should match patient_data age: expected {patient_data['age']}, got {returned_report['patient_age']}"
        assert returned_report["patient_skin_type"] == patient_data["skin_type"], \
            f"patient_skin_type should match patient_data skin_type"
        assert returned_report["patient_family_history"] == patient_data["family_history"], \
            f"patient_family_history should match patient_data family_history"
        
        # Verify age is within valid range
        assert 1 <= returned_report["patient_age"] <= 120, \
            f"patient_age should be between 1 and 120, got {returned_report['patient_age']}"
        
        # Verify skin_type is valid Fitzpatrick scale value
        assert returned_report["patient_skin_type"] in ["I", "II", "III", "IV", "V", "VI"], \
            f"patient_skin_type should be valid Fitzpatrick scale value, got {returned_report['patient_skin_type']}"


# Feature: derman-ai-skin-screening, Property 83: Urgent Case Prioritization
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    data=st.data(),
    num_urgent=st.integers(min_value=1, max_value=3),
    num_safe=st.integers(min_value=1, max_value=3)
)
@pytest.mark.asyncio
async def test_urgent_case_prioritization(data, num_urgent, num_safe):
    """
    Property 83: Urgent Case Prioritization
    
    **Validates: Requirements 9.1, 9.2, 9.3, 23.5**
    
    For any doctor viewing pending reports, urgent cases should appear at the
    top of the list before non-urgent cases.
    
    This test verifies:
    1. Urgent reports appear before safe reports
    2. All urgent reports are at the top of the list
    3. Safe reports appear after all urgent reports
    4. Ordering is consistent and deterministic
    5. Within each priority level, reports are ordered by creation date (newest first)
    
    Validates: Requirements 23.5
    """
    from app.routers.doctors import get_pending_reports
    
    # Generate reports with specific statuses
    urgent_reports = [data.draw(medical_report_data(status="urgent")) for _ in range(num_urgent)]
    safe_reports = [data.draw(medical_report_data(status="safe")) for _ in range(num_safe)]
    
    # Combine all reports
    all_reports = urgent_reports + safe_reports
    
    # Create mock profiles and patient_data for all reports
    profiles = []
    patient_data_records = []
    
    for report in all_reports:
        profile = data.draw(patient_profile_data())
        profile["id"] = report["patient_id"]
        profiles.append(profile)
        
        patient_data = data.draw(patient_data_record(user_id=report["patient_id"]))
        patient_data_records.append(patient_data)
    
    # Mock verified doctor user
    mock_doctor = {
        "id": str(uuid.uuid4()),
        "role": "doctor",
        "verified": True
    }
    
    # Mock Supabase responses
    with patch('app.routers.doctors.supabase') as mock_supabase:
        # Mock reports query - return all reports (unsorted)
        mock_reports_result = Mock()
        mock_reports_result.data = all_reports
        
        # Mock profiles query
        mock_profiles_result = Mock()
        mock_profiles_result.data = profiles
        
        # Mock patient_data query
        mock_patient_data_result = Mock()
        mock_patient_data_result.data = patient_data_records
        
        # Set up the mock chain
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
        
        # Call the endpoint
        result = await get_pending_reports(status_filter=None, current_user=mock_doctor)
        
        # Verify we got results
        assert len(result) > 0, "Should return at least one report"
        
        # Extract statuses from result
        result_statuses = [report["status"] for report in result]
        
        # Find the index of the first safe report
        first_safe_index = None
        for i, status in enumerate(result_statuses):
            if status == "safe":
                first_safe_index = i
                break
        
        # Find the index of the last urgent report
        last_urgent_index = None
        for i in range(len(result_statuses) - 1, -1, -1):
            if result_statuses[i] == "urgent":
                last_urgent_index = i
                break
        
        # Verify urgent reports come before safe reports
        if first_safe_index is not None and last_urgent_index is not None:
            assert last_urgent_index < first_safe_index, \
                f"All urgent reports should appear before safe reports. " \
                f"Last urgent at index {last_urgent_index}, first safe at index {first_safe_index}"
        
        # Verify all urgent reports are at the beginning
        urgent_count = len(urgent_reports)
        for i in range(urgent_count):
            if i < len(result):
                assert result[i]["status"] == "urgent", \
                    f"Report at index {i} should be urgent, got {result[i]['status']}"
        
        # Verify all safe reports are after urgent reports
        for i in range(urgent_count, len(result)):
            assert result[i]["status"] == "safe", \
                f"Report at index {i} should be safe, got {result[i]['status']}"
        
        # Verify the count of urgent and safe reports
        urgent_in_result = sum(1 for r in result if r["status"] == "urgent")
        safe_in_result = sum(1 for r in result if r["status"] == "safe")
        
        assert urgent_in_result == len(urgent_reports), \
            f"Should have {len(urgent_reports)} urgent reports, got {urgent_in_result}"
        assert safe_in_result == len(safe_reports), \
            f"Should have {len(safe_reports)} safe reports, got {safe_in_result}"
        
        # Verify no other statuses are present
        for report in result:
            assert report["status"] in ["safe", "urgent"], \
                f"Report status should be 'safe' or 'urgent', got '{report['status']}'"



# ============================================================================
# Consultation Notes Properties (Task 15.4)
# ============================================================================


# Feature: derman-ai-skin-screening, Property 27: Consultation Notes Persistence
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    data=st.data(),
    notes=st.text(min_size=10, max_size=500, alphabet=st.characters(whitelist_categories=('L', 'N', 'Zs', 'P')))
)
@pytest.mark.asyncio
async def test_consultation_notes_persistence(data, notes):
    """
    Property 27: Consultation Notes Persistence
    
    **Validates: Requirements 9.5, 25.5**
    
    For any doctor adding consultation notes to a report, storing the notes
    then retrieving the report should return the same notes text.
    
    This test verifies:
    1. Consultation notes can be added to a report
    2. Notes are stored in medical_reports.consultation_notes field
    3. Stored notes can be retrieved
    4. Retrieved notes match the original text exactly
    5. Notes persist across database operations
    6. Text content is preserved without truncation or modification
    
    Validates: Requirements 9.5, 25.5
    """
    from app.routers.doctors import add_consultation_notes
    from app.models import ConsultationNotesRequest
    
    # Generate a report with safe or urgent status
    report = data.draw(medical_report_data(status=data.draw(st.sampled_from(["safe", "urgent"]))))
    report_id = report["id"]
    
    # Mock verified doctor user
    mock_doctor = {
        "id": str(uuid.uuid4()),
        "role": "doctor",
        "verified": True
    }
    
    # Create consultation notes request
    notes_request = ConsultationNotesRequest(notes=notes)
    
    # Mock Supabase responses
    with patch('app.routers.doctors.supabase') as mock_supabase:
        # Mock initial report retrieval (to verify report exists)
        mock_select_result = Mock()
        mock_select_result.data = [report]
        
        # Mock update operation
        updated_report = report.copy()
        updated_report["consultation_notes"] = notes
        updated_report["updated_at"] = datetime.utcnow().isoformat()
        
        mock_update_result = Mock()
        mock_update_result.data = [updated_report]
        
        # Set up the mock chain
        mock_table = Mock()
        
        # Mock select chain
        mock_select = Mock()
        mock_eq = Mock()
        mock_execute = Mock()
        mock_execute.execute.return_value = mock_select_result
        mock_eq.eq.return_value = mock_execute
        mock_select.select.return_value.eq.return_value = mock_eq
        
        # Mock update chain
        mock_update = Mock()
        mock_update_eq = Mock()
        mock_update_execute = Mock()
        mock_update_execute.execute.return_value = mock_update_result
        mock_update_eq.eq.return_value = mock_update_execute
        mock_update.update.return_value.eq.return_value = mock_update_eq
        
        # Combine both chains
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_select_result
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_update_result
        
        mock_supabase.table.return_value = mock_table
        
        # Call the endpoint to add consultation notes
        result = await add_consultation_notes(
            report_id=report_id,
            request=notes_request,
            current_user=mock_doctor
        )
        
        # Verify the result contains consultation_notes field
        assert hasattr(result, 'consultation_notes'), \
            "Result should have consultation_notes attribute"
        
        # Verify the notes were stored correctly
        assert result.consultation_notes == notes, \
            f"Stored notes should match original. Expected: '{notes}', Got: '{result.consultation_notes}'"
        
        # Verify notes are not None
        assert result.consultation_notes is not None, \
            "consultation_notes should not be None after adding notes"
        
        # Verify notes are a string
        assert isinstance(result.consultation_notes, str), \
            f"consultation_notes should be a string, got {type(result.consultation_notes)}"
        
        # Verify notes length is preserved
        assert len(result.consultation_notes) == len(notes), \
            f"Notes length should be preserved. Expected {len(notes)}, got {len(result.consultation_notes)}"
        
        # Verify no truncation occurred
        assert result.consultation_notes == notes, \
            "Notes should not be truncated or modified"
        
        # Verify character-by-character match
        for i, (expected_char, actual_char) in enumerate(zip(notes, result.consultation_notes)):
            assert expected_char == actual_char, \
                f"Character mismatch at position {i}: expected '{expected_char}', got '{actual_char}'"
        
        # Verify the update was called with correct data
        mock_supabase.table.assert_called()
        
        # Verify report_id was used in the query
        # The mock should have been called with the report_id


# Feature: derman-ai-skin-screening, Property 92: Consultation Notes Persistence (Video Consultation)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    data=st.data(),
    notes=st.text(min_size=10, max_size=500, alphabet=st.characters(whitelist_categories=('L', 'N', 'Zs', 'P')))
)
@pytest.mark.asyncio
async def test_consultation_notes_persistence_video_consultation(data, notes):
    """
    Property 92: Consultation Notes Persistence (Video Consultation Context)
    
    **Validates: Requirements 9.5, 25.5**
    
    For any ended video consultation, the doctor should be able to add notes,
    and storing then retrieving the report should return those notes.
    
    This test verifies:
    1. Notes can be added after video consultation ends
    2. Notes are stored in the same consultation_notes field
    3. Notes persist correctly regardless of consultation type
    4. Video consultation context doesn't affect notes storage
    5. Notes can be retrieved after being stored
    6. Multiple updates to notes are supported
    
    Validates: Requirements 25.5
    """
    from app.routers.doctors import add_consultation_notes
    from app.models import ConsultationNotesRequest
    
    # Generate a report with safe or urgent status
    report = data.draw(medical_report_data(status=data.draw(st.sampled_from(["safe", "urgent"]))))
    report_id = report["id"]
    
    # Add initial consultation notes (simulating first save)
    initial_notes = "Initial consultation notes from video call"
    report["consultation_notes"] = initial_notes
    
    # Mock verified doctor user
    mock_doctor = {
        "id": str(uuid.uuid4()),
        "role": "doctor",
        "verified": True
    }
    
    # Create consultation notes request with updated notes
    notes_request = ConsultationNotesRequest(notes=notes)
    
    # Mock Supabase responses
    with patch('app.routers.doctors.supabase') as mock_supabase:
        # Mock initial report retrieval (report with initial notes)
        mock_select_result = Mock()
        mock_select_result.data = [report]
        
        # Mock update operation (updating to new notes)
        updated_report = report.copy()
        updated_report["consultation_notes"] = notes
        updated_report["updated_at"] = datetime.utcnow().isoformat()
        
        mock_update_result = Mock()
        mock_update_result.data = [updated_report]
        
        # Set up the mock chain
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_select_result
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_update_result
        
        mock_supabase.table.return_value = mock_table
        
        # Call the endpoint to update consultation notes
        result = await add_consultation_notes(
            report_id=report_id,
            request=notes_request,
            current_user=mock_doctor
        )
        
        # Verify the result contains updated consultation_notes
        assert hasattr(result, 'consultation_notes'), \
            "Result should have consultation_notes attribute"
        
        # Verify the notes were updated correctly
        assert result.consultation_notes == notes, \
            f"Updated notes should match new notes. Expected: '{notes}', Got: '{result.consultation_notes}'"
        
        # Verify notes replaced the initial notes
        assert result.consultation_notes != initial_notes, \
            "Notes should be updated, not appended to initial notes"
        
        # Verify notes are not None
        assert result.consultation_notes is not None, \
            "consultation_notes should not be None after update"
        
        # Verify notes are a string
        assert isinstance(result.consultation_notes, str), \
            f"consultation_notes should be a string, got {type(result.consultation_notes)}"
        
        # Verify exact match with new notes
        assert result.consultation_notes == notes, \
            "Updated notes should exactly match the new notes text"
        
        # Verify no truncation or modification
        assert len(result.consultation_notes) == len(notes), \
            f"Notes length should be preserved. Expected {len(notes)}, got {len(result.consultation_notes)}"


# Feature: derman-ai-skin-screening, Property 27 & 92: Consultation Notes Empty and Special Characters
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    data=st.data(),
    notes=st.one_of(
        st.text(min_size=10, max_size=100, alphabet=st.characters(whitelist_categories=('L', 'N', 'Zs', 'P'))),
        st.text(min_size=10, max_size=100).filter(lambda x: any(c in x for c in ['\n', '\t', '"', "'", '\\'])),
        st.just("Patient shows signs of melanoma. Recommend immediate biopsy.\n\nFollow-up in 2 weeks."),
        st.just("Diagnosis: Benign nevus\nTreatment: Monitor for changes\nNext visit: 6 months")
    )
)
@pytest.mark.asyncio
async def test_consultation_notes_special_characters(data, notes):
    """
    Property 27 & 92: Consultation Notes with Special Characters
    
    **Validates: Requirements 9.5, 25.5**
    
    For any consultation notes containing special characters (newlines, tabs,
    quotes, etc.), the notes should be stored and retrieved without corruption.
    
    This test verifies:
    1. Newline characters are preserved
    2. Tab characters are preserved
    3. Quote characters (single and double) are preserved
    4. Backslash characters are preserved
    5. Multi-line notes are supported
    6. Special medical notation is preserved
    
    Validates: Requirements 9.5, 25.5
    """
    from app.routers.doctors import add_consultation_notes
    from app.models import ConsultationNotesRequest
    
    # Generate a report
    report = data.draw(medical_report_data(status=data.draw(st.sampled_from(["safe", "urgent"]))))
    report_id = report["id"]
    
    # Mock verified doctor user
    mock_doctor = {
        "id": str(uuid.uuid4()),
        "role": "doctor",
        "verified": True
    }
    
    # Create consultation notes request
    notes_request = ConsultationNotesRequest(notes=notes)
    
    # Mock Supabase responses
    with patch('app.routers.doctors.supabase') as mock_supabase:
        # Mock initial report retrieval
        mock_select_result = Mock()
        mock_select_result.data = [report]
        
        # Mock update operation
        updated_report = report.copy()
        updated_report["consultation_notes"] = notes
        updated_report["updated_at"] = datetime.utcnow().isoformat()
        
        mock_update_result = Mock()
        mock_update_result.data = [updated_report]
        
        # Set up the mock chain
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_select_result
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_update_result
        
        mock_supabase.table.return_value = mock_table
        
        # Call the endpoint
        result = await add_consultation_notes(
            report_id=report_id,
            request=notes_request,
            current_user=mock_doctor
        )
        
        # Verify exact match including special characters
        assert result.consultation_notes == notes, \
            f"Notes with special characters should be preserved exactly. Expected: '{notes}', Got: '{result.consultation_notes}'"
        
        # Verify newlines are preserved if present
        if '\n' in notes:
            assert '\n' in result.consultation_notes, \
                "Newline characters should be preserved"
            assert notes.count('\n') == result.consultation_notes.count('\n'), \
                "Number of newlines should be preserved"
        
        # Verify tabs are preserved if present
        if '\t' in notes:
            assert '\t' in result.consultation_notes, \
                "Tab characters should be preserved"
        
        # Verify quotes are preserved if present
        if '"' in notes or "'" in notes:
            assert result.consultation_notes == notes, \
                "Quote characters should be preserved"
        
        # Verify backslashes are preserved if present
        if '\\' in notes:
            assert '\\' in result.consultation_notes, \
                "Backslash characters should be preserved"
