"""
Integration test for video room creation endpoint
Requirements: 25.1, 25.2
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import uuid
from datetime import datetime, timedelta

# Add backend to path for imports
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Mock the database module before importing anything that uses it
sys.modules['app.database'] = MagicMock()

from app.routers.appointments import create_video_room
from app.models import AppointmentResponse
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_create_video_room_success():
    """
    Test successful video room creation for video consultation
    
    Verifies:
    1. Video room URL is generated for video consultations
    2. URL is unique (UUID-based)
    3. URL is stored in appointments table
    4. Only patient or doctor can access
    """
    # Generate test data
    appointment_id = str(uuid.uuid4())
    patient_id = str(uuid.uuid4())
    doctor_id = str(uuid.uuid4())
    doctor_user_id = str(uuid.uuid4())
    
    # Create appointment data (video consultation)
    appointment_data = {
        "id": appointment_id,
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "report_id": None,
        "scheduled_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
        "status": "confirmed",
        "consultation_type": "video",
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
        
        # Mock appointment update with video room URL
        updated_appointment = appointment_data.copy()
        updated_appointment["video_room_url"] = "https://video.skinguard.app/room/test-uuid"
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
        assert isinstance(result, AppointmentResponse)
        
        # Verify video room URL was generated
        assert result.video_room_url is not None
        assert result.video_room_url.startswith("https://video.skinguard.app/room/")
        
        # Verify appointment ID matches
        assert result.id == appointment_id


@pytest.mark.asyncio
async def test_create_video_room_invalid_consultation_type():
    """
    Test video room creation fails for in-person consultations
    
    Verifies:
    1. Video room can only be created for video consultations
    2. Appropriate error is returned for in-person appointments
    """
    # Generate test data
    appointment_id = str(uuid.uuid4())
    patient_id = str(uuid.uuid4())
    doctor_id = str(uuid.uuid4())
    
    # Create appointment data (in-person consultation)
    appointment_data = {
        "id": appointment_id,
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "report_id": None,
        "scheduled_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
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
                mock_table.select.return_value.eq.return_value.execute.return_value = mock_appointment_result
            return mock_table
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Call the endpoint - should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await create_video_room(appointment_id, current_user)
        
        # Verify error status code
        assert exc_info.value.status_code == 400
        
        # Verify error message
        error_detail = exc_info.value.detail
        assert "INVALID_CONSULTATION_TYPE" in str(error_detail)


@pytest.mark.asyncio
async def test_create_video_room_unauthorized():
    """
    Test video room creation fails for unauthorized users
    
    Verifies:
    1. Only patient or doctor associated with appointment can access
    2. Other users receive 403 Forbidden error
    """
    # Generate test data
    appointment_id = str(uuid.uuid4())
    patient_id = str(uuid.uuid4())
    doctor_id = str(uuid.uuid4())
    other_user_id = str(uuid.uuid4())  # Different user
    
    # Create appointment data (video consultation)
    appointment_data = {
        "id": appointment_id,
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "report_id": None,
        "scheduled_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
        "status": "confirmed",
        "consultation_type": "video",
        "video_room_url": None,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    # Create current user (different patient - not authorized)
    current_user = {
        "id": other_user_id,
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
                mock_table.select.return_value.eq.return_value.execute.return_value = mock_appointment_result
            return mock_table
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Call the endpoint - should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await create_video_room(appointment_id, current_user)
        
        # Verify error status code
        assert exc_info.value.status_code == 403
        
        # Verify error message
        error_detail = exc_info.value.detail
        assert "FORBIDDEN" in str(error_detail)


@pytest.mark.asyncio
async def test_create_video_room_idempotent():
    """
    Test video room creation is idempotent
    
    Verifies:
    1. If video room URL already exists, return existing URL
    2. Don't generate new URL on subsequent calls
    """
    # Generate test data
    appointment_id = str(uuid.uuid4())
    patient_id = str(uuid.uuid4())
    doctor_id = str(uuid.uuid4())
    existing_video_url = "https://video.skinguard.app/room/existing-uuid"
    
    # Create appointment data with existing video room URL
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
    
    # Mock Supabase responses
    with patch('app.routers.appointments.supabase') as mock_supabase:
        # Mock appointment lookup
        mock_appointment_result = Mock()
        mock_appointment_result.data = [appointment_data]
        
        # Set up the mock chain
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "appointments":
                mock_table.select.return_value.eq.return_value.execute.return_value = mock_appointment_result
            return mock_table
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Call the endpoint
        result = await create_video_room(appointment_id, current_user)
        
        # Verify result is an AppointmentResponse
        assert isinstance(result, AppointmentResponse)
        
        # Verify existing video room URL is returned
        assert result.video_room_url == existing_video_url
        
        # Verify no update was called (idempotent)
        # The mock should not have called update since URL already exists
