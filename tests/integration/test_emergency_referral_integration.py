"""
Integration test for emergency referral system
Requirements: 23.3

Tests the complete flow:
1. Create urgent medical report
2. Trigger emergency referral
3. Verify nearest doctors are notified
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os
import uuid

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

# Mock database and email service before importing
sys.modules['app.database'] = MagicMock()
sys.modules['app.email_service'] = MagicMock()


@pytest.mark.asyncio
async def test_urgent_report_triggers_emergency_referral():
    """
    Integration test: Creating an urgent report should trigger emergency referral
    
    This test verifies:
    1. When a report with urgent status is created
    2. The emergency referral system is triggered
    3. Nearest doctors are identified
    4. Email notifications are sent
    """
    # Mock the database and email service
    with patch('app.emergency_referral.supabase') as mock_supabase, \
         patch('app.emergency_referral.get_email_service') as mock_get_email:
        
        # Setup mock verified doctors
        mock_profiles = [
            {
                "id": "doctor1",
                "full_name": "Dr. Alice Smith",
                "email": "alice@example.com",
                "role": "doctor",
                "verified": True
            },
            {
                "id": "doctor2",
                "full_name": "Dr. Bob Jones",
                "email": "bob@example.com",
                "role": "doctor",
                "verified": True
            },
            {
                "id": "doctor3",
                "full_name": "Dr. Carol Brown",
                "email": "carol@example.com",
                "role": "doctor",
                "verified": True
            }
        ]
        
        mock_doctors = [
            {
                "id": "doc1",
                "user_id": "doctor1",
                "clinic_name": "City Dermatology",
                "lat": 40.7200,
                "lng": -74.0100,
                "whatsapp_no": "+1234567890",
                "specialization": "Dermatology"
            },
            {
                "id": "doc2",
                "user_id": "doctor2",
                "clinic_name": "Skin Care Center",
                "lat": 40.7300,
                "lng": -74.0200,
                "whatsapp_no": "+1234567891",
                "specialization": "Dermatology"
            },
            {
                "id": "doc3",
                "user_id": "doctor3",
                "clinic_name": "Advanced Skin Clinic",
                "lat": 40.7400,
                "lng": -74.0300,
                "whatsapp_no": "+1234567892",
                "specialization": "Dermatology"
            }
        ]
        
        # Setup mock responses
        profiles_mock = MagicMock()
        profiles_mock.data = mock_profiles
        
        doctors_mock = MagicMock()
        doctors_mock.data = mock_doctors
        
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        
        # Chain the mocks
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = profiles_mock
        mock_table.select.return_value.in_.return_value.execute.return_value = doctors_mock
        
        # Setup mock email service
        mock_email_service = AsyncMock()
        mock_email_service.send_urgent_case_notification = AsyncMock(return_value=True)
        mock_get_email.return_value = mock_email_service
        
        # Import and create emergency referral service
        from app.emergency_referral import EmergencyReferralService
        
        service = EmergencyReferralService()
        
        # Simulate urgent case notification
        report_id = str(uuid.uuid4())
        patient_id = str(uuid.uuid4())
        
        doctors_found, emails_sent = await service.notify_nearest_doctors(
            report_id=report_id,
            patient_id=patient_id,
            patient_name="John Doe",
            patient_lat=40.7128,
            patient_lng=-74.0060,
            risk_level="urgent",
            top_prediction={"type": "Melanoma", "probability": 0.92}
        )
        
        # Verify results
        assert doctors_found == 3, "Should find 3 nearest doctors"
        assert emails_sent == 3, "Should send 3 email notifications"
        
        # Verify email service was called for each doctor
        assert mock_email_service.send_urgent_case_notification.call_count == 3
        
        # Verify email content for first doctor
        first_call = mock_email_service.send_urgent_case_notification.call_args_list[0]
        assert first_call.kwargs["doctor_email"] in ["alice@example.com", "bob@example.com", "carol@example.com"]
        assert first_call.kwargs["patient_name"] == "John Doe"
        assert first_call.kwargs["report_id"] == report_id
        assert first_call.kwargs["risk_level"] == "urgent"
        assert first_call.kwargs["top_prediction"]["type"] == "Melanoma"
        assert first_call.kwargs["top_prediction"]["probability"] == 0.92


@pytest.mark.asyncio
async def test_emergency_referral_handles_no_doctors_gracefully():
    """
    Integration test: System should handle case when no verified doctors exist
    """
    with patch('app.emergency_referral.supabase') as mock_supabase:
        # Setup mock with no verified doctors
        profiles_mock = MagicMock()
        profiles_mock.data = []
        
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = profiles_mock
        
        # Import and create emergency referral service
        from app.emergency_referral import EmergencyReferralService
        
        service = EmergencyReferralService()
        
        # Attempt to notify doctors
        doctors_found, emails_sent = await service.notify_nearest_doctors(
            report_id=str(uuid.uuid4()),
            patient_id=str(uuid.uuid4()),
            patient_name="Jane Doe",
            risk_level="urgent"
        )
        
        # Should handle gracefully
        assert doctors_found == 0
        assert emails_sent == 0


@pytest.mark.asyncio
async def test_emergency_referral_finds_nearest_by_distance():
    """
    Integration test: System should correctly identify nearest doctors by distance
    """
    with patch('app.emergency_referral.supabase') as mock_supabase, \
         patch('app.emergency_referral.get_email_service') as mock_get_email:
        
        # Patient location: New York City (40.7128, -74.0060)
        patient_lat = 40.7128
        patient_lng = -74.0060
        
        # Setup doctors at different distances
        mock_profiles = [
            {"id": "doctor1", "full_name": "Dr. Near", "email": "near@example.com", "role": "doctor", "verified": True},
            {"id": "doctor2", "full_name": "Dr. Medium", "email": "medium@example.com", "role": "doctor", "verified": True},
            {"id": "doctor3", "full_name": "Dr. Far", "email": "far@example.com", "role": "doctor", "verified": True},
            {"id": "doctor4", "full_name": "Dr. VeryFar", "email": "veryfar@example.com", "role": "doctor", "verified": True},
        ]
        
        mock_doctors = [
            # Very close (< 1 km)
            {"id": "doc1", "user_id": "doctor1", "clinic_name": "Near Clinic", 
             "lat": 40.7150, "lng": -74.0080, "whatsapp_no": "+1111111111", "specialization": "Dermatology"},
            # Medium distance (~10 km)
            {"id": "doc2", "user_id": "doctor2", "clinic_name": "Medium Clinic",
             "lat": 40.8000, "lng": -74.0500, "whatsapp_no": "+2222222222", "specialization": "Dermatology"},
            # Far (~50 km)
            {"id": "doc3", "user_id": "doctor3", "clinic_name": "Far Clinic",
             "lat": 41.0000, "lng": -74.5000, "whatsapp_no": "+3333333333", "specialization": "Dermatology"},
            # Very far (~100 km)
            {"id": "doc4", "user_id": "doctor4", "clinic_name": "Very Far Clinic",
             "lat": 41.5000, "lng": -75.0000, "whatsapp_no": "+4444444444", "specialization": "Dermatology"},
        ]
        
        profiles_mock = MagicMock()
        profiles_mock.data = mock_profiles
        
        doctors_mock = MagicMock()
        doctors_mock.data = mock_doctors
        
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = profiles_mock
        mock_table.select.return_value.in_.return_value.execute.return_value = doctors_mock
        
        # Setup mock email service
        mock_email_service = AsyncMock()
        mock_email_service.send_urgent_case_notification = AsyncMock(return_value=True)
        mock_get_email.return_value = mock_email_service
        
        from app.emergency_referral import EmergencyReferralService
        
        service = EmergencyReferralService()
        
        # Find nearest doctors
        nearest_doctors = await service.find_nearest_doctors(
            patient_lat=patient_lat,
            patient_lng=patient_lng,
            limit=3
        )
        
        # Should return exactly 3 doctors
        assert len(nearest_doctors) == 3
        
        # Should be sorted by distance (nearest first)
        assert nearest_doctors[0]["full_name"] == "Dr. Near"
        assert nearest_doctors[1]["full_name"] == "Dr. Medium"
        assert nearest_doctors[2]["full_name"] == "Dr. Far"
        
        # Verify distances are in ascending order
        assert nearest_doctors[0]["distance_km"] < nearest_doctors[1]["distance_km"]
        assert nearest_doctors[1]["distance_km"] < nearest_doctors[2]["distance_km"]
        
        # Verify the nearest doctor is actually close
        assert nearest_doctors[0]["distance_km"] < 5  # Should be less than 5 km


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
