"""
Unit tests for emergency referral system
Requirements: 23.3

Tests:
- Finding nearest verified doctors
- Distance calculation
- Email notification sending
- Handling edge cases (no doctors, email failures)
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

# Mock supabase before importing emergency_referral
sys.modules['app.database'] = MagicMock()
sys.modules['app.email_service'] = MagicMock()

from app.emergency_referral import EmergencyReferralService, get_emergency_referral_service
import math


class TestEmergencyReferralService:
    """Test suite for EmergencyReferralService"""
    
    def test_calculate_distance_same_location(self):
        """Test distance calculation for same location returns 0"""
        distance = EmergencyReferralService.calculate_distance(
            40.7128, -74.0060,  # New York
            40.7128, -74.0060   # New York
        )
        assert distance == 0.0
    
    def test_calculate_distance_known_locations(self):
        """Test distance calculation between known locations"""
        # Distance between New York and Los Angeles is approximately 3944 km
        distance = EmergencyReferralService.calculate_distance(
            40.7128, -74.0060,  # New York
            34.0522, -118.2437  # Los Angeles
        )
        # Allow 1% tolerance
        assert 3900 < distance < 4000
    
    def test_calculate_distance_symmetry(self):
        """Test that distance calculation is symmetric"""
        dist1 = EmergencyReferralService.calculate_distance(
            40.7128, -74.0060,
            34.0522, -118.2437
        )
        dist2 = EmergencyReferralService.calculate_distance(
            34.0522, -118.2437,
            40.7128, -74.0060
        )
        assert abs(dist1 - dist2) < 0.01  # Should be essentially equal
    
    @pytest.mark.asyncio
    async def test_find_nearest_doctors_no_verified_doctors(self):
        """Test finding nearest doctors when no verified doctors exist"""
        service = EmergencyReferralService()
        
        # Mock supabase to return no verified doctors
        with patch('app.emergency_referral.supabase') as mock_supabase:
            mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
            
            result = await service.find_nearest_doctors(
                patient_lat=40.7128,
                patient_lng=-74.0060,
                limit=3
            )
            
            assert result == []
    
    @pytest.mark.asyncio
    async def test_find_nearest_doctors_with_location(self):
        """Test finding nearest doctors with patient location"""
        service = EmergencyReferralService()
        
        # Mock verified profiles
        mock_profiles = [
            {"id": "doctor1", "full_name": "Dr. Smith", "email": "smith@example.com", "role": "doctor", "verified": True},
            {"id": "doctor2", "full_name": "Dr. Jones", "email": "jones@example.com", "role": "doctor", "verified": True},
            {"id": "doctor3", "full_name": "Dr. Brown", "email": "brown@example.com", "role": "doctor", "verified": True},
        ]
        
        # Mock doctor records with different distances
        mock_doctors = [
            {
                "id": "doc1", "user_id": "doctor1", "clinic_name": "Clinic A",
                "lat": 40.7200, "lng": -74.0100,  # Close to patient
                "whatsapp_no": "+1234567890", "specialization": "Dermatology"
            },
            {
                "id": "doc2", "user_id": "doctor2", "clinic_name": "Clinic B",
                "lat": 40.8000, "lng": -74.1000,  # Medium distance
                "whatsapp_no": "+1234567891", "specialization": "Dermatology"
            },
            {
                "id": "doc3", "user_id": "doctor3", "clinic_name": "Clinic C",
                "lat": 41.0000, "lng": -75.0000,  # Far from patient
                "whatsapp_no": "+1234567892", "specialization": "Dermatology"
            },
        ]
        
        with patch('app.emergency_referral.supabase') as mock_supabase:
            # Mock profiles query
            profiles_mock = MagicMock()
            profiles_mock.data = mock_profiles
            
            # Mock doctors query
            doctors_mock = MagicMock()
            doctors_mock.data = mock_doctors
            
            # Setup mock chain
            mock_table = MagicMock()
            mock_supabase.table.return_value = mock_table
            
            # First call returns profiles, second call returns doctors
            mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = profiles_mock
            mock_table.select.return_value.in_.return_value.execute.return_value = doctors_mock
            
            result = await service.find_nearest_doctors(
                patient_lat=40.7128,
                patient_lng=-74.0060,
                limit=3
            )
            
            # Should return 3 doctors
            assert len(result) == 3
            
            # Should be sorted by distance (nearest first)
            assert result[0]["full_name"] == "Dr. Smith"  # Closest
            assert result[0]["distance_km"] is not None
            assert result[0]["distance_km"] < result[1]["distance_km"]
            assert result[1]["distance_km"] < result[2]["distance_km"]
    
    @pytest.mark.asyncio
    async def test_find_nearest_doctors_without_location(self):
        """Test finding nearest doctors without patient location"""
        service = EmergencyReferralService()
        
        mock_profiles = [
            {"id": "doctor1", "full_name": "Dr. Smith", "email": "smith@example.com", "role": "doctor", "verified": True},
        ]
        
        mock_doctors = [
            {
                "id": "doc1", "user_id": "doctor1", "clinic_name": "Clinic A",
                "lat": 40.7200, "lng": -74.0100,
                "whatsapp_no": "+1234567890", "specialization": "Dermatology"
            },
        ]
        
        with patch('app.emergency_referral.supabase') as mock_supabase:
            profiles_mock = MagicMock()
            profiles_mock.data = mock_profiles
            
            doctors_mock = MagicMock()
            doctors_mock.data = mock_doctors
            
            mock_table = MagicMock()
            mock_supabase.table.return_value = mock_table
            
            mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = profiles_mock
            mock_table.select.return_value.in_.return_value.execute.return_value = doctors_mock
            
            result = await service.find_nearest_doctors(
                patient_lat=None,
                patient_lng=None,
                limit=3
            )
            
            # Should return doctors even without location
            assert len(result) == 1
            assert result[0]["distance_km"] is None  # No distance calculated
    
    @pytest.mark.asyncio
    async def test_find_nearest_doctors_limit(self):
        """Test that limit parameter is respected"""
        service = EmergencyReferralService()
        
        # Create 5 mock doctors
        mock_profiles = [
            {"id": f"doctor{i}", "full_name": f"Dr. Doctor{i}", "email": f"doc{i}@example.com", "role": "doctor", "verified": True}
            for i in range(5)
        ]
        
        mock_doctors = [
            {
                "id": f"doc{i}", "user_id": f"doctor{i}", "clinic_name": f"Clinic {i}",
                "lat": 40.7200 + i * 0.1, "lng": -74.0100,
                "whatsapp_no": f"+123456789{i}", "specialization": "Dermatology"
            }
            for i in range(5)
        ]
        
        with patch('app.emergency_referral.supabase') as mock_supabase:
            profiles_mock = MagicMock()
            profiles_mock.data = mock_profiles
            
            doctors_mock = MagicMock()
            doctors_mock.data = mock_doctors
            
            mock_table = MagicMock()
            mock_supabase.table.return_value = mock_table
            
            mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = profiles_mock
            mock_table.select.return_value.in_.return_value.execute.return_value = doctors_mock
            
            # Request only 3 doctors
            result = await service.find_nearest_doctors(
                patient_lat=40.7128,
                patient_lng=-74.0060,
                limit=3
            )
            
            # Should return exactly 3 doctors
            assert len(result) == 3
    
    @pytest.mark.asyncio
    async def test_notify_nearest_doctors_success(self):
        """Test successful notification of nearest doctors"""
        service = EmergencyReferralService()
        
        # Mock find_nearest_doctors to return 3 doctors
        mock_doctors = [
            {
                "doctor_id": "doc1", "user_id": "doctor1",
                "full_name": "Dr. Smith", "email": "smith@example.com",
                "clinic_name": "Clinic A", "lat": 40.7200, "lng": -74.0100,
                "whatsapp_no": "+1234567890", "specialization": "Dermatology",
                "distance_km": 1.5
            },
            {
                "doctor_id": "doc2", "user_id": "doctor2",
                "full_name": "Dr. Jones", "email": "jones@example.com",
                "clinic_name": "Clinic B", "lat": 40.8000, "lng": -74.1000,
                "whatsapp_no": "+1234567891", "specialization": "Dermatology",
                "distance_km": 10.2
            },
            {
                "doctor_id": "doc3", "user_id": "doctor3",
                "full_name": "Dr. Brown", "email": "brown@example.com",
                "clinic_name": "Clinic C", "lat": 41.0000, "lng": -75.0000,
                "whatsapp_no": "+1234567892", "specialization": "Dermatology",
                "distance_km": 50.8
            },
        ]
        
        # Mock email service
        mock_email_service = AsyncMock()
        mock_email_service.send_urgent_case_notification = AsyncMock(return_value=True)
        service.email_service = mock_email_service
        
        with patch.object(service, 'find_nearest_doctors', return_value=mock_doctors):
            doctors_found, emails_sent = await service.notify_nearest_doctors(
                report_id="report123",
                patient_id="patient123",
                patient_name="John Doe",
                patient_lat=40.7128,
                patient_lng=-74.0060,
                risk_level="urgent",
                top_prediction={"type": "Melanoma", "probability": 0.92}
            )
            
            # Should find 3 doctors and send 3 emails
            assert doctors_found == 3
            assert emails_sent == 3
            
            # Verify email service was called 3 times
            assert mock_email_service.send_urgent_case_notification.call_count == 3
    
    @pytest.mark.asyncio
    async def test_notify_nearest_doctors_no_doctors(self):
        """Test notification when no doctors are available"""
        service = EmergencyReferralService()
        
        with patch.object(service, 'find_nearest_doctors', return_value=[]):
            doctors_found, emails_sent = await service.notify_nearest_doctors(
                report_id="report123",
                patient_id="patient123",
                patient_name="John Doe",
                risk_level="urgent"
            )
            
            # Should find 0 doctors and send 0 emails
            assert doctors_found == 0
            assert emails_sent == 0
    
    @pytest.mark.asyncio
    async def test_notify_nearest_doctors_partial_email_failure(self):
        """Test notification when some emails fail to send"""
        service = EmergencyReferralService()
        
        mock_doctors = [
            {
                "doctor_id": "doc1", "user_id": "doctor1",
                "full_name": "Dr. Smith", "email": "smith@example.com",
                "clinic_name": "Clinic A", "lat": 40.7200, "lng": -74.0100,
                "whatsapp_no": "+1234567890", "specialization": "Dermatology",
                "distance_km": 1.5
            },
            {
                "doctor_id": "doc2", "user_id": "doctor2",
                "full_name": "Dr. Jones", "email": "jones@example.com",
                "clinic_name": "Clinic B", "lat": 40.8000, "lng": -74.1000,
                "whatsapp_no": "+1234567891", "specialization": "Dermatology",
                "distance_km": 10.2
            },
        ]
        
        # Mock email service to fail on second email
        mock_email_service = AsyncMock()
        mock_email_service.send_urgent_case_notification = AsyncMock(side_effect=[True, False])
        service.email_service = mock_email_service
        
        with patch.object(service, 'find_nearest_doctors', return_value=mock_doctors):
            doctors_found, emails_sent = await service.notify_nearest_doctors(
                report_id="report123",
                patient_id="patient123",
                patient_name="John Doe",
                risk_level="urgent"
            )
            
            # Should find 2 doctors but only send 1 email successfully
            assert doctors_found == 2
            assert emails_sent == 1
    
    def test_get_emergency_referral_service_singleton(self):
        """Test that get_emergency_referral_service returns singleton instance"""
        service1 = get_emergency_referral_service()
        service2 = get_emergency_referral_service()
        
        assert service1 is service2  # Should be same instance


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
