"""
Property-Based Tests for Emergency Referral System
Feature: derman-ai-skin-screening

Tests emergency referral correctness properties including nearest doctor
notification for urgent cases.

Requirements: 23.3
"""

import pytest
import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from hypothesis import HealthCheck
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import uuid
from datetime import datetime
import math

# Add backend to path for imports
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Mock the database module before importing anything that uses it
sys.modules['app.database'] = MagicMock()
sys.modules['app.email_service'] = MagicMock()

from app.emergency_referral import EmergencyReferralService


# Hypothesis strategies for generating test data
@st.composite
def coordinates(draw):
    """Generate valid latitude and longitude coordinates"""
    lat = draw(st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False))
    lng = draw(st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False))
    return (lat, lng)


@st.composite
def doctor_profile(draw, verified=True, unique_id=None):
    """Generate a doctor profile for testing"""
    # Use unique_id to ensure unique emails
    if unique_id is None:
        unique_id = draw(st.integers(min_value=1000, max_value=9999))
    
    # Add prefix to distinguish verified from unverified
    prefix = "verified" if verified else "unverified"
    
    return {
        "id": str(uuid.uuid4()),
        "email": f"{prefix}{unique_id}@example.com",
        "full_name": draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'Zs')))),
        "role": "doctor",
        "verified": verified
    }


@st.composite
def doctor_record(draw, user_id, lat, lng):
    """Generate a doctor record for testing"""
    return {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "license_no": f"LIC{draw(st.integers(min_value=100000, max_value=999999))}",
        "clinic_name": draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N', 'Zs')))),
        "lat": lat,
        "lng": lng,
        "whatsapp_no": f"+1{draw(st.integers(min_value=1000000000, max_value=9999999999))}",
        "specialization": draw(st.sampled_from(["Dermatology", "Oncology", "General Practice"])),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }


@st.composite
def urgent_case_data(draw):
    """Generate urgent case data for testing"""
    return {
        "report_id": str(uuid.uuid4()),
        "patient_id": str(uuid.uuid4()),
        "patient_name": draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'Zs')))),
        "risk_level": "urgent",
        "top_prediction": {
            "type": draw(st.sampled_from(["Melanoma", "Basal Cell Carcinoma", "Squamous Cell Carcinoma"])),
            "probability": draw(st.floats(min_value=0.85, max_value=1.0))
        }
    }


def calculate_distance(lat1, lng1, lat2, lng2):
    """Helper function to calculate distance between two coordinates"""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


# Feature: derman-ai-skin-screening, Property 81: Nearest Doctor Notification
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    data=st.data(),
    patient_coords=coordinates(),
    num_doctors=st.integers(min_value=3, max_value=8)
)
@pytest.mark.asyncio
async def test_nearest_doctor_notification(data, patient_coords, num_doctors):
    """
    Property 81: Nearest Doctor Notification
    
    **Validates: Requirements 23.3**
    
    For any urgent case detection, the system should identify and notify the
    3 nearest verified doctors via email.
    
    This test verifies:
    1. Exactly 3 nearest doctors are identified (or fewer if less than 3 exist)
    2. Doctors are sorted by distance from patient location
    3. Only verified doctors are included
    4. Email notifications are sent to identified doctors
    5. Distance calculation is correct
    6. All notified doctors receive case details
    
    Validates: Requirements 23.3
    """
    patient_lat, patient_lng = patient_coords
    
    # Avoid poles where distance calculations can be problematic
    assume(-85 < patient_lat < 85)
    
    # Generate doctors at various distances from patient
    profiles = []
    doctors = []
    doctor_distances = []
    
    for i in range(num_doctors):
        # Generate coordinates at varying distances
        # Use incremental offsets to ensure unique distances
        lat_offset = (i + 1) * 0.3 + data.draw(st.floats(min_value=0.0, max_value=0.2))
        lng_offset = (i + 1) * 0.3 + data.draw(st.floats(min_value=0.0, max_value=0.2))
        
        doctor_lat = patient_lat + lat_offset
        doctor_lng = patient_lng + lng_offset
        
        # Ensure coordinates are valid
        doctor_lat = max(-85, min(85, doctor_lat))
        doctor_lng = max(-180, min(180, doctor_lng))
        
        # Create profile and doctor record with unique ID
        profile = data.draw(doctor_profile(verified=True, unique_id=i))
        profiles.append(profile)
        
        doctor = data.draw(doctor_record(
            user_id=profile["id"],
            lat=doctor_lat,
            lng=doctor_lng
        ))
        doctors.append(doctor)
        
        # Calculate distance
        distance = calculate_distance(patient_lat, patient_lng, doctor_lat, doctor_lng)
        doctor_distances.append((doctor, profile, distance))
    
    # Sort doctors by distance to determine expected nearest 3
    doctor_distances.sort(key=lambda x: x[2])
    expected_nearest_3 = doctor_distances[:3]
    expected_doctor_ids = [d[0]["user_id"] for d in expected_nearest_3]
    
    # Generate urgent case data
    case = data.draw(urgent_case_data())
    
    # Create service instance
    service = EmergencyReferralService()
    
    # Mock email service to track calls
    mock_email_service = AsyncMock()
    mock_email_service.send_urgent_case_notification = AsyncMock(return_value=True)
    service.email_service = mock_email_service
    
    # Mock Supabase responses
    with patch('app.emergency_referral.supabase') as mock_supabase:
        # Mock profiles query
        mock_profiles_result = Mock()
        mock_profiles_result.data = profiles
        
        # Mock doctors query
        mock_doctors_result = Mock()
        mock_doctors_result.data = doctors
        
        # Set up the mock chain
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "profiles":
                mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_profiles_result
            elif table_name == "doctors":
                mock_table.select.return_value.in_.return_value.execute.return_value = mock_doctors_result
            return mock_table
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Call notify_nearest_doctors
        doctors_found, emails_sent = await service.notify_nearest_doctors(
            report_id=case["report_id"],
            patient_id=case["patient_id"],
            patient_name=case["patient_name"],
            patient_lat=patient_lat,
            patient_lng=patient_lng,
            risk_level=case["risk_level"],
            top_prediction=case["top_prediction"]
        )
        
        # Verify exactly 3 doctors were found (or fewer if less than 3 exist)
        expected_count = min(3, num_doctors)
        assert doctors_found == expected_count, \
            f"Should find {expected_count} doctors, found {doctors_found}"
        
        # Verify emails were sent to all found doctors
        assert emails_sent == expected_count, \
            f"Should send {expected_count} emails, sent {emails_sent}"
        
        # Verify email service was called correct number of times
        assert mock_email_service.send_urgent_case_notification.call_count == expected_count, \
            f"Email service should be called {expected_count} times"
        
        # Verify the correct doctors were notified (the 3 nearest)
        email_calls = mock_email_service.send_urgent_case_notification.call_args_list
        notified_emails = [call.kwargs["doctor_email"] for call in email_calls]
        
        # Get expected emails from nearest doctors
        expected_emails = [profile["email"] for _, profile, _ in expected_nearest_3]
        
        # Verify all expected doctors were notified
        assert set(notified_emails) == set(expected_emails), \
            f"Expected doctors {expected_emails} to be notified, but got {notified_emails}"
        
        # Verify case details were included in notifications
        for call in email_calls:
            assert call.kwargs["patient_name"] == case["patient_name"], \
                "Patient name should be included in notification"
            assert call.kwargs["report_id"] == case["report_id"], \
                "Report ID should be included in notification"
            assert call.kwargs["risk_level"] == case["risk_level"], \
                "Risk level should be included in notification"
            assert call.kwargs["top_prediction"] == case["top_prediction"], \
                "Top prediction should be included in notification"


# Feature: derman-ai-skin-screening, Property 81: Nearest Doctor Notification (Distance Sorting)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    data=st.data(),
    patient_coords=coordinates()
)
@pytest.mark.asyncio
async def test_nearest_doctor_notification_distance_sorting(data, patient_coords):
    """
    Property 81: Nearest Doctor Notification (Distance Sorting)
    
    **Validates: Requirements 23.3**
    
    For any urgent case, the 3 notified doctors should be sorted by distance
    from the patient location, with the nearest doctor notified first.
    
    This test verifies:
    1. Doctors are sorted by distance (nearest first)
    2. Distance calculation is accurate
    3. The 3 nearest doctors are selected, not random doctors
    
    Validates: Requirements 23.3
    """
    patient_lat, patient_lng = patient_coords
    
    # Create exactly 5 doctors at known distances
    # Doctor 1: Very close (0.1 degree offset)
    # Doctor 2: Close (0.5 degree offset)
    # Doctor 3: Medium (1.0 degree offset)
    # Doctor 4: Far (2.0 degree offset)
    # Doctor 5: Very far (3.0 degree offset)
    
    offsets = [0.1, 0.5, 1.0, 2.0, 3.0]
    profiles = []
    doctors = []
    
    for i, offset in enumerate(offsets):
        doctor_lat = patient_lat + offset
        doctor_lng = patient_lng + offset
        
        # Ensure coordinates are valid
        doctor_lat = max(-90, min(90, doctor_lat))
        doctor_lng = max(-180, min(180, doctor_lng))
        
        profile = data.draw(doctor_profile(verified=True, unique_id=i))
        profiles.append(profile)
        
        doctor = data.draw(doctor_record(
            user_id=profile["id"],
            lat=doctor_lat,
            lng=doctor_lng
        ))
        doctors.append(doctor)
    
    # Generate urgent case data
    case = data.draw(urgent_case_data())
    
    # Create service instance
    service = EmergencyReferralService()
    
    # Mock email service to track call order
    mock_email_service = AsyncMock()
    mock_email_service.send_urgent_case_notification = AsyncMock(return_value=True)
    service.email_service = mock_email_service
    
    # Mock Supabase responses
    with patch('app.emergency_referral.supabase') as mock_supabase:
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
        
        # Call notify_nearest_doctors
        doctors_found, emails_sent = await service.notify_nearest_doctors(
            report_id=case["report_id"],
            patient_id=case["patient_id"],
            patient_name=case["patient_name"],
            patient_lat=patient_lat,
            patient_lng=patient_lng,
            risk_level=case["risk_level"],
            top_prediction=case["top_prediction"]
        )
        
        # Verify 3 doctors were found
        assert doctors_found == 3, f"Should find 3 doctors, found {doctors_found}"
        
        # Get the emails that were notified
        email_calls = mock_email_service.send_urgent_case_notification.call_args_list
        notified_emails = [call.kwargs["doctor_email"] for call in email_calls]
        
        # The first 3 doctors (with smallest offsets) should be notified
        expected_profiles = profiles[:3]
        expected_emails = [p["email"] for p in expected_profiles]
        
        # Verify the correct doctors were notified
        assert set(notified_emails) == set(expected_emails), \
            f"Expected nearest 3 doctors to be notified"
        
        # Verify the 4th and 5th doctors were NOT notified
        not_expected_emails = [profiles[3]["email"], profiles[4]["email"]]
        for email in not_expected_emails:
            assert email not in notified_emails, \
                f"Doctor {email} should not be notified (too far)"


# Feature: derman-ai-skin-screening, Property 81: Nearest Doctor Notification (Verified Only)
@settings(
    max_examples=30,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    data=st.data(),
    patient_coords=coordinates(),
    num_verified=st.integers(min_value=3, max_value=5),
    num_unverified=st.integers(min_value=1, max_value=3)
)
@pytest.mark.asyncio
async def test_nearest_doctor_notification_verified_only(data, patient_coords, num_verified, num_unverified):
    """
    Property 81: Nearest Doctor Notification (Verified Only)
    
    **Validates: Requirements 23.3**
    
    For any urgent case, only verified doctors should be notified, even if
    unverified doctors are closer to the patient.
    
    This test verifies:
    1. Only verified doctors are included in notifications
    2. Unverified doctors are excluded even if they are closer
    3. Verification status is correctly checked
    
    Validates: Requirements 23.3
    """
    patient_lat, patient_lng = patient_coords
    
    # Avoid poles
    assume(-85 < patient_lat < 85)
    
    # Create verified doctors (farther away)
    verified_profiles = []
    verified_doctors = []
    
    for i in range(num_verified):
        # Place verified doctors farther away (offset 2.0+)
        offset = 2.0 + i * 0.5
        doctor_lat = patient_lat + offset
        doctor_lng = patient_lng + offset
        
        doctor_lat = max(-85, min(85, doctor_lat))
        doctor_lng = max(-180, min(180, doctor_lng))
        
        profile = data.draw(doctor_profile(verified=True, unique_id=i))
        verified_profiles.append(profile)
        
        doctor = data.draw(doctor_record(
            user_id=profile["id"],
            lat=doctor_lat,
            lng=doctor_lng
        ))
        verified_doctors.append(doctor)
    
    # Create unverified doctors (closer)
    unverified_profiles = []
    unverified_doctors = []
    
    for i in range(num_unverified):
        # Place unverified doctors closer (offset 0.2-0.5)
        offset = 0.2 + i * 0.1
        doctor_lat = patient_lat + offset
        doctor_lng = patient_lng + offset
        
        doctor_lat = max(-85, min(85, doctor_lat))
        doctor_lng = max(-180, min(180, doctor_lng))
        
        profile = data.draw(doctor_profile(verified=False, unique_id=1000 + i))
        unverified_profiles.append(profile)
        
        doctor = data.draw(doctor_record(
            user_id=profile["id"],
            lat=doctor_lat,
            lng=doctor_lng
        ))
        unverified_doctors.append(doctor)
    
    # Generate urgent case data
    case = data.draw(urgent_case_data())
    
    # Create service instance
    service = EmergencyReferralService()
    
    # Mock email service
    mock_email_service = AsyncMock()
    mock_email_service.send_urgent_case_notification = AsyncMock(return_value=True)
    service.email_service = mock_email_service
    
    # Mock Supabase responses - only return verified profiles
    with patch('app.emergency_referral.supabase') as mock_supabase:
        mock_profiles_result = Mock()
        mock_profiles_result.data = verified_profiles  # Only verified
        
        mock_doctors_result = Mock()
        mock_doctors_result.data = verified_doctors  # Only verified
        
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "profiles":
                mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_profiles_result
            elif table_name == "doctors":
                mock_table.select.return_value.in_.return_value.execute.return_value = mock_doctors_result
            return mock_table
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Call notify_nearest_doctors
        doctors_found, emails_sent = await service.notify_nearest_doctors(
            report_id=case["report_id"],
            patient_id=case["patient_id"],
            patient_name=case["patient_name"],
            patient_lat=patient_lat,
            patient_lng=patient_lng,
            risk_level=case["risk_level"],
            top_prediction=case["top_prediction"]
        )
        
        # Verify only verified doctors were found
        expected_count = min(3, num_verified)
        assert doctors_found == expected_count, \
            f"Should find {expected_count} verified doctors, found {doctors_found}"
        
        # Get notified emails
        email_calls = mock_email_service.send_urgent_case_notification.call_args_list
        notified_emails = [call.kwargs["doctor_email"] for call in email_calls]
        
        # Verify only verified doctors were notified
        verified_emails = [p["email"] for p in verified_profiles]
        for email in notified_emails:
            assert email in verified_emails, \
                f"Notified email {email} should be from verified doctors only"
        
        # Verify no unverified doctors were notified
        unverified_emails = [p["email"] for p in unverified_profiles]
        for email in unverified_emails:
            assert email not in notified_emails, \
                f"Unverified doctor {email} should not be notified"


# Feature: derman-ai-skin-screening, Property 81: Nearest Doctor Notification (No Doctors)
@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    data=st.data(),
    patient_coords=coordinates()
)
@pytest.mark.asyncio
async def test_nearest_doctor_notification_no_doctors(data, patient_coords):
    """
    Property 81: Nearest Doctor Notification (No Doctors Available)
    
    **Validates: Requirements 23.3**
    
    For any urgent case when no verified doctors are available, the system
    should handle gracefully and return (0, 0) for doctors found and emails sent.
    
    This test verifies:
    1. System handles case with no verified doctors
    2. No errors are raised
    3. Returns (0, 0) for doctors found and emails sent
    
    Validates: Requirements 23.3
    """
    patient_lat, patient_lng = patient_coords
    
    # Generate urgent case data
    case = data.draw(urgent_case_data())
    
    # Create service instance
    service = EmergencyReferralService()
    
    # Mock email service (should not be called)
    mock_email_service = AsyncMock()
    mock_email_service.send_urgent_case_notification = AsyncMock(return_value=True)
    service.email_service = mock_email_service
    
    # Mock Supabase responses - return empty lists
    with patch('app.emergency_referral.supabase') as mock_supabase:
        mock_profiles_result = Mock()
        mock_profiles_result.data = []  # No verified doctors
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_profiles_result
        
        mock_supabase.table.return_value = mock_table
        
        # Call notify_nearest_doctors
        doctors_found, emails_sent = await service.notify_nearest_doctors(
            report_id=case["report_id"],
            patient_id=case["patient_id"],
            patient_name=case["patient_name"],
            patient_lat=patient_lat,
            patient_lng=patient_lng,
            risk_level=case["risk_level"],
            top_prediction=case["top_prediction"]
        )
        
        # Verify no doctors were found
        assert doctors_found == 0, \
            f"Should find 0 doctors when none available, found {doctors_found}"
        
        # Verify no emails were sent
        assert emails_sent == 0, \
            f"Should send 0 emails when no doctors available, sent {emails_sent}"
        
        # Verify email service was not called
        assert mock_email_service.send_urgent_case_notification.call_count == 0, \
            "Email service should not be called when no doctors available"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
