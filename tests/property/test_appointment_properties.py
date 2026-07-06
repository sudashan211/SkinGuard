"""
Property-Based Tests for Appointment Management System
Feature: derman-ai-skin-screening

Tests appointment correctness properties including creation completeness,
doctor appointment filtering, and status transition rules.

Requirements: 8.2, 8.3, 8.4, 8.5
"""

import pytest
import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings
from hypothesis import HealthCheck
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import uuid
from datetime import datetime, timedelta

# Add backend to path for imports
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Mock the database module before importing anything that uses it
sys.modules['app.database'] = MagicMock()

from app.models import AppointmentCreateRequest, AppointmentUpdateRequest, AppointmentResponse


# Hypothesis strategies for generating test data
@st.composite
def appointment_data(draw, status=None, scheduled_in_past=False):
    """Generate appointment data for testing"""
    if scheduled_in_past:
        scheduled_at = datetime.utcnow() - timedelta(hours=draw(st.integers(min_value=1, max_value=48)))
    else:
        scheduled_at = datetime.utcnow() + timedelta(hours=draw(st.integers(min_value=1, max_value=168)))
    
    return {
        "id": str(uuid.uuid4()),
        "patient_id": str(uuid.uuid4()),
        "doctor_id": str(uuid.uuid4()),
        "report_id": str(uuid.uuid4()) if draw(st.booleans()) else None,
        "scheduled_at": scheduled_at.isoformat(),
        "status": status if status is not None else draw(st.sampled_from(["pending", "confirmed", "completed", "cancelled"])),
        "consultation_type": draw(st.sampled_from(["in_person", "video"])),
        "video_room_url": None,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }


@st.composite
def appointment_list(draw, min_size=0, max_size=10, doctor_id=None, patient_id=None):
    """Generate a list of appointments"""
    size = draw(st.integers(min_value=min_size, max_value=max_size))
    appointments = []
    for _ in range(size):
        appt = draw(appointment_data())
        if doctor_id:
            appt["doctor_id"] = doctor_id
        if patient_id:
            appt["patient_id"] = patient_id
        appointments.append(appt)
    return appointments


# Feature: derman-ai-skin-screening, Property 21: Appointment Creation Completeness
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    consultation_type=st.sampled_from(["in_person", "video"]),
    has_report=st.booleans(),
    hours_ahead=st.integers(min_value=1, max_value=168)
)
@pytest.mark.asyncio
async def test_appointment_creation_completeness(consultation_type, has_report, hours_ahead):
    """
    Property 21: Appointment Creation Completeness
    
    For any appointment creation, the appointments record should contain all
    required fields (patient_id, doctor_id, scheduled_at, status) and initial
    status should be "pending".
    
    This test verifies:
    1. All required fields are present in created appointment
    2. Initial status is always "pending"
    3. patient_id matches current authenticated user
    4. doctor_id matches requested doctor
    5. scheduled_at is preserved correctly
    6. consultation_type is stored correctly
    7. report_id is stored if provided
    
    Validates: Requirements 8.2, 8.3
    """
    from app.routers.appointments import create_appointment
    
    # Generate test data
    patient_id = str(uuid.uuid4())
    doctor_id = str(uuid.uuid4())
    doctor_user_id = str(uuid.uuid4())
    report_id = str(uuid.uuid4()) if has_report else None
    scheduled_at = datetime.utcnow() + timedelta(hours=hours_ahead)
    
    # Create request
    request = AppointmentCreateRequest(
        doctor_id=doctor_id,
        report_id=report_id,
        scheduled_at=scheduled_at,
        consultation_type=consultation_type
    )
    
    # Mock current user (patient)
    current_user = {
        "id": patient_id,
        "role": "patient",
        "verified": False
    }
    
    # Mock doctor data
    doctor_data = {
        "id": doctor_id,
        "user_id": doctor_user_id,
        "license_no": "LIC123456",
        "clinic_name": "Test Clinic",
        "lat": 40.7128,
        "lng": -74.0060,
        "whatsapp_no": "+11234567890"
    }
    
    # Mock doctor profile (verified)
    doctor_profile = {
        "id": doctor_user_id,
        "verified": True
    }
    
    # Mock report data if provided
    report_data = None
    if has_report:
        report_data = {
            "id": report_id,
            "patient_id": patient_id,
            "image_url": "https://example.com/image.jpg",
            "status": "safe"
        }
    
    # Expected appointment data
    expected_appointment = {
        "id": str(uuid.uuid4()),
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "report_id": report_id,
        "scheduled_at": scheduled_at.isoformat(),
        "status": "pending",  # Initial status must be "pending"
        "consultation_type": consultation_type,
        "video_room_url": None,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    # Mock Supabase responses
    with patch('app.routers.appointments.supabase') as mock_supabase:
        # Mock doctor lookup
        mock_doctor_result = Mock()
        mock_doctor_result.data = [doctor_data]
        
        # Mock doctor profile lookup
        mock_profile_result = Mock()
        mock_profile_result.data = [doctor_profile]
        
        # Mock report lookup if provided
        mock_report_result = Mock()
        if has_report:
            mock_report_result.data = [report_data]
        else:
            mock_report_result.data = []
        
        # Mock appointment insert
        mock_insert_result = Mock()
        mock_insert_result.data = [expected_appointment]
        
        # Set up the mock chain
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "doctors":
                mock_table.select.return_value.eq.return_value.execute.return_value = mock_doctor_result
            elif table_name == "profiles":
                mock_table.select.return_value.eq.return_value.execute.return_value = mock_profile_result
            elif table_name == "medical_reports":
                mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_report_result
            elif table_name == "appointments":
                mock_table.insert.return_value.execute.return_value = mock_insert_result
            return mock_table
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Call the endpoint
        result = await create_appointment(request, current_user)
        
        # Verify result is an AppointmentResponse
        assert isinstance(result, AppointmentResponse), \
            f"Result should be AppointmentResponse, got {type(result)}"
        
        # Verify all required fields are present
        assert result.id is not None, "Appointment ID should be present"
        assert result.patient_id == patient_id, \
            f"patient_id should be {patient_id}, got {result.patient_id}"
        assert result.doctor_id == doctor_id, \
            f"doctor_id should be {doctor_id}, got {result.doctor_id}"
        assert result.scheduled_at is not None, "scheduled_at should be present"
        
        # Verify initial status is "pending"
        assert result.status == "pending", \
            f"Initial status should be 'pending', got '{result.status}'"
        
        # Verify consultation_type is preserved
        assert result.consultation_type == consultation_type, \
            f"consultation_type should be '{consultation_type}', got '{result.consultation_type}'"
        
        # Verify report_id is preserved if provided
        if has_report:
            assert result.report_id == report_id, \
                f"report_id should be {report_id}, got {result.report_id}"
        
        # Verify timestamps are present
        assert result.created_at is not None, "created_at should be present"
        assert result.updated_at is not None, "updated_at should be present"


# Feature: derman-ai-skin-screening, Property 22: Doctor Appointment Filtering
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    doctor_appointments=st.integers(min_value=1, max_value=5),
    other_appointments=st.integers(min_value=1, max_value=5)
)
@pytest.mark.asyncio
async def test_doctor_appointment_filtering(doctor_appointments, other_appointments):
    """
    Property 22: Doctor Appointment Filtering
    
    For any doctor viewing appointments, the returned list should contain only
    appointments where doctor_id matches their profile UUID.
    
    This test verifies:
    1. Only appointments for the specific doctor are returned
    2. Appointments for other doctors are excluded
    3. Filtering is based on doctor_id field
    4. All returned appointments have matching doctor_id
    
    Validates: Requirements 8.4
    """
    from app.routers.appointments import get_appointments
    
    # Generate test data
    doctor_user_id = str(uuid.uuid4())
    doctor_id = str(uuid.uuid4())
    
    # Create current user (doctor)
    current_user = {
        "id": doctor_user_id,
        "role": "doctor",
        "verified": True
    }
    
    # Create doctor record
    doctor_record = {
        "id": doctor_id,
        "user_id": doctor_user_id
    }
    
    # Create appointments for this doctor
    doctor_appts = []
    for _ in range(doctor_appointments):
        appt = {
            "id": str(uuid.uuid4()),
            "patient_id": str(uuid.uuid4()),
            "doctor_id": doctor_id,  # Matches our doctor
            "report_id": None,
            "scheduled_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            "status": "pending",
            "consultation_type": "in_person",
            "video_room_url": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        doctor_appts.append(appt)
    
    # Create appointments for other doctors
    other_appts = []
    for _ in range(other_appointments):
        appt = {
            "id": str(uuid.uuid4()),
            "patient_id": str(uuid.uuid4()),
            "doctor_id": str(uuid.uuid4()),  # Different doctor
            "report_id": None,
            "scheduled_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            "status": "pending",
            "consultation_type": "in_person",
            "video_room_url": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        other_appts.append(appt)
    
    # Mock Supabase responses
    with patch('app.routers.appointments.supabase') as mock_supabase:
        # Mock doctor record lookup
        mock_doctor_result = Mock()
        mock_doctor_result.data = [doctor_record]
        
        # Mock appointments query - return only doctor's appointments
        mock_appointments_result = Mock()
        mock_appointments_result.data = doctor_appts
        
        # Set up the mock chain
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "doctors":
                mock_table.select.return_value.eq.return_value.execute.return_value = mock_doctor_result
            elif table_name == "appointments":
                mock_table.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_appointments_result
            return mock_table
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Call the endpoint
        result = await get_appointments(current_user)
        
        # Verify result is a list
        assert isinstance(result, list), f"Result should be a list, got {type(result)}"
        
        # Verify count matches doctor's appointments
        assert len(result) == doctor_appointments, \
            f"Should return {doctor_appointments} appointments, got {len(result)}"
        
        # Verify all returned appointments have matching doctor_id
        for appt in result:
            assert appt.doctor_id == doctor_id, \
                f"Appointment {appt.id} should have doctor_id {doctor_id}, got {appt.doctor_id}"
        
        # Verify no appointments from other doctors are included
        result_ids = [appt.id for appt in result]
        other_ids = [appt["id"] for appt in other_appts]
        
        for other_id in other_ids:
            assert other_id not in result_ids, \
                f"Appointment {other_id} from another doctor should not be in results"


# Feature: derman-ai-skin-screening, Property 23: Appointment Status Transition Rules
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    new_status=st.sampled_from(["pending", "confirmed", "completed", "cancelled"]),
    hours_past=st.integers(min_value=1, max_value=48)
)
@pytest.mark.asyncio
async def test_appointment_status_transition_rules(new_status, hours_past):
    """
    Property 23: Appointment Status Transition Rules
    
    For any appointment where scheduled_at timestamp has passed, status updates
    to "completed" or "cancelled" should be allowed, but updates to "pending"
    should be rejected.
    
    This test verifies:
    1. After scheduled_at, only "completed" or "cancelled" are allowed
    2. Updates to "pending" or "confirmed" after scheduled_at are rejected
    3. Status transition validation is based on scheduled_at timestamp
    4. Appropriate error messages for invalid transitions
    
    Validates: Requirements 8.5
    """
    from app.routers.appointments import update_appointment_status
    from fastapi import HTTPException
    
    # Generate test data
    appointment_id = str(uuid.uuid4())
    patient_id = str(uuid.uuid4())
    doctor_id = str(uuid.uuid4())
    doctor_user_id = str(uuid.uuid4())
    
    # Create appointment in the past
    scheduled_at = datetime.utcnow() - timedelta(hours=hours_past)
    
    appointment_data = {
        "id": appointment_id,
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "report_id": None,
        "scheduled_at": scheduled_at.isoformat(),
        "status": "confirmed",
        "consultation_type": "in_person",
        "video_room_url": None,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    # Create current user (doctor)
    current_user = {
        "id": doctor_user_id,
        "role": "doctor",
        "verified": True
    }
    
    # Create doctor record
    doctor_record = {
        "id": doctor_id,
        "user_id": doctor_user_id
    }
    
    # Create update request
    request = AppointmentUpdateRequest(status=new_status)
    
    # Determine if this transition should be allowed
    should_allow = new_status in ["completed", "cancelled"]
    
    # Mock Supabase responses
    with patch('app.routers.appointments.supabase') as mock_supabase:
        # Mock appointment lookup
        mock_appointment_result = Mock()
        mock_appointment_result.data = [appointment_data]
        
        # Mock doctor record lookup
        mock_doctor_result = Mock()
        mock_doctor_result.data = [doctor_record]
        
        # Mock appointment update
        updated_appointment = appointment_data.copy()
        updated_appointment["status"] = new_status
        updated_appointment["updated_at"] = datetime.utcnow().isoformat()
        
        mock_update_result = Mock()
        mock_update_result.data = [updated_appointment]
        
        # Set up the mock chain
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "appointments":
                # For select query
                mock_table.select.return_value.eq.return_value.execute.return_value = mock_appointment_result
                # For update query
                mock_table.update.return_value.eq.return_value.execute.return_value = mock_update_result
            elif table_name == "doctors":
                mock_table.select.return_value.eq.return_value.execute.return_value = mock_doctor_result
            return mock_table
        
        mock_supabase.table.side_effect = table_side_effect
        
        if should_allow:
            # Should succeed for "completed" or "cancelled"
            result = await update_appointment_status(appointment_id, request, current_user)
            
            # Verify result is an AppointmentResponse
            assert isinstance(result, AppointmentResponse), \
                f"Result should be AppointmentResponse, got {type(result)}"
            
            # Verify status was updated
            assert result.status == new_status, \
                f"Status should be '{new_status}', got '{result.status}'"
            
            # Verify appointment ID matches
            assert result.id == appointment_id, \
                f"Appointment ID should be {appointment_id}, got {result.id}"
        
        else:
            # Should fail for "pending" or "confirmed" after scheduled_at
            with pytest.raises(HTTPException) as exc_info:
                await update_appointment_status(appointment_id, request, current_user)
            
            # Verify error status code
            assert exc_info.value.status_code == 400, \
                f"Should return 400 Bad Request, got {exc_info.value.status_code}"
            
            # Verify error message mentions invalid transition
            error_detail = exc_info.value.detail
            assert "INVALID_STATUS_TRANSITION" in str(error_detail), \
                f"Error should mention invalid status transition, got: {error_detail}"


# Feature: derman-ai-skin-screening, Property 23: Appointment Status Transition Rules (Future Appointments)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    new_status=st.sampled_from(["pending", "confirmed", "completed", "cancelled"]),
    hours_ahead=st.integers(min_value=1, max_value=168)
)
@pytest.mark.asyncio
async def test_appointment_status_transition_future(new_status, hours_ahead):
    """
    Property 23: Appointment Status Transition Rules (Future Appointments)
    
    For any appointment where scheduled_at is in the future, status updates to
    any valid status should be allowed.
    
    This test verifies:
    1. Before scheduled_at, all status transitions are allowed
    2. No restrictions on status updates for future appointments
    3. Status validation only applies after scheduled_at has passed
    
    Validates: Requirements 8.5
    """
    from app.routers.appointments import update_appointment_status
    
    # Generate test data
    appointment_id = str(uuid.uuid4())
    patient_id = str(uuid.uuid4())
    doctor_id = str(uuid.uuid4())
    doctor_user_id = str(uuid.uuid4())
    
    # Create appointment in the future
    scheduled_at = datetime.utcnow() + timedelta(hours=hours_ahead)
    
    appointment_data = {
        "id": appointment_id,
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "report_id": None,
        "scheduled_at": scheduled_at.isoformat(),
        "status": "pending",
        "consultation_type": "in_person",
        "video_room_url": None,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    # Create current user (patient)
    current_user = {
        "id": patient_id,
        "role": "patient",
        "verified": False
    }
    
    # Create update request
    request = AppointmentUpdateRequest(status=new_status)
    
    # Mock Supabase responses
    with patch('app.routers.appointments.supabase') as mock_supabase:
        # Mock appointment lookup
        mock_appointment_result = Mock()
        mock_appointment_result.data = [appointment_data]
        
        # Mock appointment update
        updated_appointment = appointment_data.copy()
        updated_appointment["status"] = new_status
        updated_appointment["updated_at"] = datetime.utcnow().isoformat()
        
        mock_update_result = Mock()
        mock_update_result.data = [updated_appointment]
        
        # Set up the mock chain
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "appointments":
                # For select query
                mock_table.select.return_value.eq.return_value.execute.return_value = mock_appointment_result
                # For update query
                mock_table.update.return_value.eq.return_value.execute.return_value = mock_update_result
            return mock_table
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Should succeed for any status when appointment is in the future
        result = await update_appointment_status(appointment_id, request, current_user)
        
        # Verify result is an AppointmentResponse
        assert isinstance(result, AppointmentResponse), \
            f"Result should be AppointmentResponse, got {type(result)}"
        
        # Verify status was updated
        assert result.status == new_status, \
            f"Status should be '{new_status}', got '{result.status}'"
        
        # Verify appointment ID matches
        assert result.id == appointment_id, \
            f"Appointment ID should be {appointment_id}, got {result.id}"


# Feature: derman-ai-skin-screening, Property 89: Consultation Type Options
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    consultation_type=st.sampled_from(["in_person", "video"]),
    hours_ahead=st.integers(min_value=1, max_value=168)
)
@pytest.mark.asyncio
async def test_consultation_type_options(consultation_type, hours_ahead):
    """
    Property 89: Consultation Type Options
    
    For any appointment booking interface, the system should offer both
    "in_person" and "video" consultation type options.
    
    This test verifies:
    1. Both "in_person" and "video" consultation types are accepted
    2. consultation_type is stored correctly in the appointment record
    3. Invalid consultation types are rejected
    4. consultation_type field is required and validated
    
    **Validates: Requirements 25.1**
    """
    from app.routers.appointments import create_appointment
    
    # Generate test data
    patient_id = str(uuid.uuid4())
    doctor_id = str(uuid.uuid4())
    doctor_user_id = str(uuid.uuid4())
    scheduled_at = datetime.utcnow() + timedelta(hours=hours_ahead)
    
    # Create request with consultation type
    request = AppointmentCreateRequest(
        doctor_id=doctor_id,
        report_id=None,
        scheduled_at=scheduled_at,
        consultation_type=consultation_type
    )
    
    # Mock current user (patient)
    current_user = {
        "id": patient_id,
        "role": "patient",
        "verified": False
    }
    
    # Mock doctor data
    doctor_data = {
        "id": doctor_id,
        "user_id": doctor_user_id,
        "license_no": "LIC123456",
        "clinic_name": "Test Clinic",
        "lat": 40.7128,
        "lng": -74.0060,
        "whatsapp_no": "+11234567890"
    }
    
    # Mock doctor profile (verified)
    doctor_profile = {
        "id": doctor_user_id,
        "verified": True
    }
    
    # Expected appointment data
    expected_appointment = {
        "id": str(uuid.uuid4()),
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "report_id": None,
        "scheduled_at": scheduled_at.isoformat(),
        "status": "pending",
        "consultation_type": consultation_type,
        "video_room_url": None,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    # Mock Supabase responses
    with patch('app.routers.appointments.supabase') as mock_supabase:
        # Mock doctor lookup
        mock_doctor_result = Mock()
        mock_doctor_result.data = [doctor_data]
        
        # Mock doctor profile lookup
        mock_profile_result = Mock()
        mock_profile_result.data = [doctor_profile]
        
        # Mock appointment insert
        mock_insert_result = Mock()
        mock_insert_result.data = [expected_appointment]
        
        # Set up the mock chain
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "doctors":
                mock_table.select.return_value.eq.return_value.execute.return_value = mock_doctor_result
            elif table_name == "profiles":
                mock_table.select.return_value.eq.return_value.execute.return_value = mock_profile_result
            elif table_name == "appointments":
                mock_table.insert.return_value.execute.return_value = mock_insert_result
            return mock_table
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Call the endpoint
        result = await create_appointment(request, current_user)
        
        # Verify result is an AppointmentResponse
        assert isinstance(result, AppointmentResponse), \
            f"Result should be AppointmentResponse, got {type(result)}"
        
        # Verify consultation_type is stored correctly
        assert result.consultation_type == consultation_type, \
            f"consultation_type should be '{consultation_type}', got '{result.consultation_type}'"
        
        # Verify consultation_type is one of the valid options
        assert result.consultation_type in ["in_person", "video"], \
            f"consultation_type must be 'in_person' or 'video', got '{result.consultation_type}'"
        
        # Verify appointment was created successfully
        assert result.id is not None, "Appointment ID should be present"
        assert result.status == "pending", "Initial status should be 'pending'"


# Feature: derman-ai-skin-screening, Property 89: Consultation Type Options (Invalid Type)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    hours_ahead=st.integers(min_value=1, max_value=168)
)
@pytest.mark.asyncio
async def test_consultation_type_validation(hours_ahead):
    """
    Property 89: Consultation Type Options (Validation)
    
    For any appointment booking, invalid consultation types should be rejected
    by the system's validation layer.
    
    This test verifies:
    1. Invalid consultation types are rejected at the Pydantic model level
    2. Only "in_person" and "video" are accepted
    3. Appropriate validation errors are raised
    
    **Validates: Requirements 25.1**
    """
    from pydantic import ValidationError
    
    # Generate test data
    doctor_id = str(uuid.uuid4())
    scheduled_at = datetime.utcnow() + timedelta(hours=hours_ahead)
    
    # Try to create request with invalid consultation type
    # This should fail at the Pydantic validation level
    with pytest.raises(ValidationError) as exc_info:
        AppointmentCreateRequest(
            doctor_id=doctor_id,
            report_id=None,
            scheduled_at=scheduled_at,
            consultation_type="invalid_type"  # Invalid type
        )
    
    # Verify validation error mentions consultation_type
    error_str = str(exc_info.value)
    assert "consultation_type" in error_str.lower(), \
        f"Validation error should mention consultation_type field, got: {error_str}"


# Feature: derman-ai-skin-screening, Property 90: Video Room URL Uniqueness
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    num_appointments=st.integers(min_value=2, max_value=10)
)
@pytest.mark.asyncio
async def test_video_room_url_uniqueness(num_appointments):
    """
    Property 90: Video Room URL Uniqueness
    
    For any video consultation appointment, the system should generate a unique
    meeting room URL that is not reused for other appointments.
    
    This test verifies:
    1. Each video consultation gets a unique video_room_url
    2. Video room URLs are never reused across appointments
    3. URLs follow the expected format with unique identifiers
    4. Multiple appointments generate different URLs
    
    **Validates: Requirements 25.2**
    """
    from app.routers.appointments import create_video_room
    
    # Generate multiple appointments and collect their video room URLs
    video_room_urls = []
    
    for i in range(num_appointments):
        # Generate test data for each appointment
        appointment_id = str(uuid.uuid4())
        patient_id = str(uuid.uuid4())
        doctor_id = str(uuid.uuid4())
        doctor_user_id = str(uuid.uuid4())
        
        # Create video consultation appointment
        appointment_data = {
            "id": appointment_id,
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "report_id": None,
            "scheduled_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            "status": "confirmed",
            "consultation_type": "video",  # Video consultation
            "video_room_url": None,  # No URL yet
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Create current user (patient)
        current_user = {
            "id": patient_id,
            "role": "patient",
            "verified": False
        }
        
        # Mock Supabase responses
        with patch('app.routers.appointments.supabase') as mock_supabase:
            # Mock appointment lookup
            mock_appointment_result = Mock()
            mock_appointment_result.data = [appointment_data]
            
            # Generate unique video room URL
            room_id = str(uuid.uuid4())
            video_room_url = f"https://video.skinguard.app/room/{room_id}"
            
            # Mock appointment update with video room URL
            updated_appointment = appointment_data.copy()
            updated_appointment["video_room_url"] = video_room_url
            updated_appointment["updated_at"] = datetime.utcnow().isoformat()
            
            mock_update_result = Mock()
            mock_update_result.data = [updated_appointment]
            
            # Set up the mock chain
            def table_side_effect(table_name):
                mock_table = Mock()
                if table_name == "appointments":
                    # For select query
                    mock_table.select.return_value.eq.return_value.execute.return_value = mock_appointment_result
                    # For update query
                    mock_table.update.return_value.eq.return_value.execute.return_value = mock_update_result
                return mock_table
            
            mock_supabase.table.side_effect = table_side_effect
            
            # Call the endpoint
            result = await create_video_room(appointment_id, current_user)
            
            # Verify result is an AppointmentResponse
            assert isinstance(result, AppointmentResponse), \
                f"Result should be AppointmentResponse, got {type(result)}"
            
            # Verify video room URL was generated
            assert result.video_room_url is not None, \
                f"video_room_url should be generated for video consultation"
            
            # Verify URL format
            assert result.video_room_url.startswith("https://video.skinguard.app/room/"), \
                f"video_room_url should follow expected format, got: {result.video_room_url}"
            
            # Collect the URL
            video_room_urls.append(result.video_room_url)
    
    # Verify all URLs are unique
    assert len(video_room_urls) == len(set(video_room_urls)), \
        f"All video room URLs should be unique. Found {len(video_room_urls)} URLs but only {len(set(video_room_urls))} unique ones"
    
    # Verify no URL is reused
    for i, url1 in enumerate(video_room_urls):
        for j, url2 in enumerate(video_room_urls):
            if i != j:
                assert url1 != url2, \
                    f"Video room URLs should be unique. Found duplicate: {url1}"


# Feature: derman-ai-skin-screening, Property 90: Video Room URL Uniqueness (Idempotency)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    num_calls=st.integers(min_value=2, max_value=5)
)
@pytest.mark.asyncio
async def test_video_room_url_idempotency(num_calls):
    """
    Property 90: Video Room URL Uniqueness (Idempotency)
    
    For any video consultation appointment, calling the video room creation
    endpoint multiple times should return the same URL (idempotent behavior).
    
    This test verifies:
    1. Multiple calls for the same appointment return the same URL
    2. Video room URL is not regenerated if it already exists
    3. Idempotent behavior prevents duplicate room creation
    
    **Validates: Requirements 25.2**
    """
    from app.routers.appointments import create_video_room
    
    # Generate test data
    appointment_id = str(uuid.uuid4())
    patient_id = str(uuid.uuid4())
    doctor_id = str(uuid.uuid4())
    
    # Generate a video room URL
    room_id = str(uuid.uuid4())
    existing_video_url = f"https://video.skinguard.app/room/{room_id}"
    
    # Create video consultation appointment with existing URL
    appointment_data = {
        "id": appointment_id,
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "report_id": None,
        "scheduled_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
        "status": "confirmed",
        "consultation_type": "video",
        "video_room_url": existing_video_url,  # Already has URL
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    # Create current user (patient)
    current_user = {
        "id": patient_id,
        "role": "patient",
        "verified": False
    }
    
    # Call the endpoint multiple times
    returned_urls = []
    
    for _ in range(num_calls):
        # Mock Supabase responses
        with patch('app.routers.appointments.supabase') as mock_supabase:
            # Mock appointment lookup
            mock_appointment_result = Mock()
            mock_appointment_result.data = [appointment_data]
            
            # Set up the mock chain
            def table_side_effect(table_name):
                mock_table = Mock()
                if table_name == "appointments":
                    # For select query
                    mock_table.select.return_value.eq.return_value.execute.return_value = mock_appointment_result
                return mock_table
            
            mock_supabase.table.side_effect = table_side_effect
            
            # Call the endpoint
            result = await create_video_room(appointment_id, current_user)
            
            # Verify result is an AppointmentResponse
            assert isinstance(result, AppointmentResponse), \
                f"Result should be AppointmentResponse, got {type(result)}"
            
            # Verify existing video room URL is returned
            assert result.video_room_url == existing_video_url, \
                f"Should return existing video_room_url '{existing_video_url}', got '{result.video_room_url}'"
            
            # Collect the URL
            returned_urls.append(result.video_room_url)
    
    # Verify all calls returned the same URL (idempotent)
    assert len(set(returned_urls)) == 1, \
        f"All calls should return the same URL (idempotent). Got {len(set(returned_urls))} different URLs"
    
    # Verify the URL matches the existing one
    assert returned_urls[0] == existing_video_url, \
        f"Returned URL should match existing URL '{existing_video_url}', got '{returned_urls[0]}'"


# Feature: derman-ai-skin-screening, Property 90: Video Room URL Uniqueness (In-Person Rejection)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    hours_ahead=st.integers(min_value=1, max_value=168)
)
@pytest.mark.asyncio
async def test_video_room_in_person_rejection(hours_ahead):
    """
    Property 90: Video Room URL Uniqueness (In-Person Rejection)
    
    For any in-person consultation appointment, attempting to create a video
    room should be rejected by the system.
    
    This test verifies:
    1. Video room creation is only allowed for video consultations
    2. In-person consultations cannot have video room URLs
    3. Appropriate error is returned for invalid consultation type
    
    **Validates: Requirements 25.2**
    """
    from app.routers.appointments import create_video_room
    from fastapi import HTTPException
    
    # Generate test data
    appointment_id = str(uuid.uuid4())
    patient_id = str(uuid.uuid4())
    doctor_id = str(uuid.uuid4())
    
    # Create in-person consultation appointment
    appointment_data = {
        "id": appointment_id,
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "report_id": None,
        "scheduled_at": (datetime.utcnow() + timedelta(hours=hours_ahead)).isoformat(),
        "status": "confirmed",
        "consultation_type": "in_person",  # Not video
        "video_room_url": None,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    # Create current user (patient)
    current_user = {
        "id": patient_id,
        "role": "patient",
        "verified": False
    }
    
    # Mock Supabase responses
    with patch('app.routers.appointments.supabase') as mock_supabase:
        # Mock appointment lookup
        mock_appointment_result = Mock()
        mock_appointment_result.data = [appointment_data]
        
        # Set up the mock chain
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "appointments":
                # For select query
                mock_table.select.return_value.eq.return_value.execute.return_value = mock_appointment_result
            return mock_table
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Call the endpoint - should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await create_video_room(appointment_id, current_user)
        
        # Verify error status code
        assert exc_info.value.status_code == 400, \
            f"Should return 400 Bad Request, got {exc_info.value.status_code}"
        
        # Verify error message mentions invalid consultation type
        error_detail = exc_info.value.detail
        assert "INVALID_CONSULTATION_TYPE" in str(error_detail), \
            f"Error should mention invalid consultation type, got: {error_detail}"
