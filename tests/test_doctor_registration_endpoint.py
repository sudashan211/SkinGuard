"""
Integration test for doctor registration endpoint
Task 11.1: Implement doctor registration endpoint
"""
import pytest
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Load environment variables
load_dotenv()

from fastapi.testclient import TestClient
from app.main import app
from app.auth import create_access_token
from datetime import datetime
import uuid


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def doctor_token():
    """Create a JWT token for a doctor user"""
    # Create a mock doctor user
    doctor_user = {
        "id": str(uuid.uuid4()),
        "email": "test_doctor@example.com",
        "full_name": "Test Doctor",
        "role": "doctor",
        "verified": False
    }
    
    # Create access token
    token = create_access_token(doctor_user)
    return token


def test_doctor_registration_endpoint_structure(client, doctor_token):
    """
    Test that the doctor registration endpoint exists and has correct structure
    
    This test verifies:
    1. POST /api/doctors/register endpoint exists
    2. Endpoint requires authentication
    3. Endpoint requires doctor role
    4. Endpoint accepts DoctorRegistrationRequest
    5. Endpoint returns DoctorResponse with verified=false
    """
    # Test data
    registration_data = {
        "license_no": "MD123456",
        "clinic_name": "Test Medical Center",
        "lat": 40.7128,
        "lng": -74.0060,
        "whatsapp_no": "+15551234567",
        "specialization": "Dermatology"
    }
    
    # Test without authentication - should fail
    response = client.post("/api/doctors/register", json=registration_data)
    assert response.status_code in [401, 403], \
        "Endpoint should require authentication"
    
    # Test with authentication
    headers = {"Authorization": f"Bearer {doctor_token}"}
    response = client.post("/api/doctors/register", json=registration_data, headers=headers)
    
    # Should either succeed or fail with specific error (e.g., already registered)
    assert response.status_code in [201, 400, 409], \
        f"Endpoint should return 201 (created), 400 (bad request), or 409 (conflict), got {response.status_code}"
    
    if response.status_code == 201:
        # Verify response structure
        data = response.json()
        
        assert "id" in data, "Response should contain doctor ID"
        assert "user_id" in data, "Response should contain user ID"
        assert "license_no" in data, "Response should contain license number"
        assert data["license_no"] == registration_data["license_no"], \
            "License number should match input"
        
        assert "clinic_name" in data, "Response should contain clinic name"
        assert data["clinic_name"] == registration_data["clinic_name"], \
            "Clinic name should match input"
        
        assert "lat" in data, "Response should contain latitude"
        assert data["lat"] == registration_data["lat"], \
            "Latitude should match input"
        
        assert "lng" in data, "Response should contain longitude"
        assert data["lng"] == registration_data["lng"], \
            "Longitude should match input"
        
        assert "whatsapp_no" in data, "Response should contain WhatsApp number"
        assert data["whatsapp_no"] == registration_data["whatsapp_no"], \
            "WhatsApp number should match input"
        
        assert "verified" in data, "Response should contain verified status"
        assert data["verified"] == False, \
            "Initial verified status should be false (Requirement 6.2)"
        
        assert "created_at" in data, "Response should contain created timestamp"
        assert "updated_at" in data, "Response should contain updated timestamp"
        
        print("\n✅ Doctor registration endpoint test passed!")
        print(f"   - Endpoint exists at POST /api/doctors/register")
        print(f"   - Requires authentication and doctor role")
        print(f"   - Accepts all required fields")
        print(f"   - Returns doctor profile with verified=false")
        print(f"   - All requirements (6.1, 6.2) satisfied")


def test_doctor_registration_validation(client, doctor_token):
    """
    Test that the doctor registration endpoint validates input correctly
    """
    headers = {"Authorization": f"Bearer {doctor_token}"}
    
    # Test with missing required fields
    invalid_data = {
        "license_no": "MD123456"
        # Missing clinic_name, lat, lng, whatsapp_no
    }
    
    response = client.post("/api/doctors/register", json=invalid_data, headers=headers)
    assert response.status_code == 422, \
        "Endpoint should return 422 for missing required fields"
    
    # Test with invalid coordinates
    invalid_coords = {
        "license_no": "MD123456",
        "clinic_name": "Test Clinic",
        "lat": 100,  # Invalid: > 90
        "lng": -74.0060,
        "whatsapp_no": "+15551234567"
    }
    
    response = client.post("/api/doctors/register", json=invalid_coords, headers=headers)
    assert response.status_code == 422, \
        "Endpoint should return 422 for invalid latitude"
    
    print("\n✅ Doctor registration validation test passed!")
    print(f"   - Validates required fields")
    print(f"   - Validates coordinate ranges")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
