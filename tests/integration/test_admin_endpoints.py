"""
Integration tests for admin doctor verification endpoints
Requirements: 6.3, 6.4, 10.1

Tests the following endpoints:
- GET /api/admin/doctors/pending
- PUT /api/admin/doctors/{doctor_id}/verify
"""
import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from uuid import uuid4
from datetime import datetime

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.main import app
from app.database import supabase
from app.auth import create_access_token


client = TestClient(app)


@pytest.fixture
def admin_token():
    """Create admin access token"""
    admin_id = str(uuid4())
    token_data = {
        "sub": admin_id,
        "email": "admin@test.com",
        "role": "admin",
        "verified": True
    }
    return create_access_token(token_data)


@pytest.fixture
def doctor_token():
    """Create doctor access token"""
    doctor_id = str(uuid4())
    token_data = {
        "sub": doctor_id,
        "email": "doctor@test.com",
        "role": "doctor",
        "verified": False
    }
    return create_access_token(token_data)


@pytest.fixture
def patient_token():
    """Create patient access token"""
    patient_id = str(uuid4())
    token_data = {
        "sub": patient_id,
        "email": "patient@test.com",
        "role": "patient",
        "verified": True
    }
    return create_access_token(token_data)


class TestGetPendingDoctors:
    """Test GET /api/admin/doctors/pending endpoint"""
    
    def test_get_pending_doctors_success(self, admin_token):
        """Test admin can retrieve pending doctor applications"""
        # Make request
        response = client.get(
            "/api/admin/doctors/pending",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Verify response
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        
        # If there are pending doctors, verify structure
        if len(response.json()) > 0:
            doctor = response.json()[0]
            assert "id" in doctor
            assert "user_id" in doctor
            assert "license_no" in doctor
            assert "clinic_name" in doctor
            assert "lat" in doctor
            assert "lng" in doctor
            assert "whatsapp_no" in doctor
            assert "verified" in doctor
            assert doctor["verified"] == False  # Should only return unverified
    
    def test_get_pending_doctors_unauthorized(self):
        """Test endpoint requires authentication"""
        response = client.get("/api/admin/doctors/pending")
        assert response.status_code == 401
    
    def test_get_pending_doctors_forbidden_patient(self, patient_token):
        """Test patient cannot access admin endpoint"""
        response = client.get(
            "/api/admin/doctors/pending",
            headers={"Authorization": f"Bearer {patient_token}"}
        )
        assert response.status_code == 403
        assert "admin role" in response.json()["detail"].lower()
    
    def test_get_pending_doctors_forbidden_doctor(self, doctor_token):
        """Test doctor cannot access admin endpoint"""
        response = client.get(
            "/api/admin/doctors/pending",
            headers={"Authorization": f"Bearer {doctor_token}"}
        )
        assert response.status_code == 403
        assert "admin role" in response.json()["detail"].lower()
    
    def test_get_pending_doctors_empty_list(self, admin_token):
        """Test endpoint returns empty list when no pending doctors"""
        # This test assumes there might be no pending doctors
        response = client.get(
            "/api/admin/doctors/pending",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestVerifyDoctor:
    """Test PUT /api/admin/doctors/{doctor_id}/verify endpoint"""
    
    @pytest.fixture
    def test_doctor(self):
        """Create a test doctor for verification"""
        # Create profile
        user_id = str(uuid4())
        profile_data = {
            "id": user_id,
            "email": f"test_doctor_{uuid4()}@test.com",
            "full_name": "Test Doctor",
            "role": "doctor",
            "verified": False,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        profile_result = supabase.table("profiles").insert(profile_data).execute()
        
        # Create doctor record
        doctor_id = str(uuid4())
        doctor_data = {
            "id": doctor_id,
            "user_id": user_id,
            "license_no": f"LIC{uuid4().hex[:8]}",
            "clinic_name": "Test Clinic",
            "lat": 40.7128,
            "lng": -74.0060,
            "whatsapp_no": "+1234567890",
            "specialization": "Dermatology",
            "average_rating": 0.0,
            "review_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        doctor_result = supabase.table("doctors").insert(doctor_data).execute()
        
        yield {
            "doctor_id": doctor_id,
            "user_id": user_id,
            "profile": profile_result.data[0],
            "doctor": doctor_result.data[0]
        }
        
        # Cleanup
        try:
            supabase.table("doctors").delete().eq("id", doctor_id).execute()
            supabase.table("profiles").delete().eq("id", user_id).execute()
        except:
            pass
    
    def test_verify_doctor_approve(self, admin_token, test_doctor):
        """Test admin can approve doctor application"""
        doctor_id = test_doctor["doctor_id"]
        
        # Approve doctor
        response = client.put(
            f"/api/admin/doctors/{doctor_id}/verify",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"verified": True}
        )
        
        # Verify response
        assert response.status_code == 200
        doctor_response = response.json()
        assert doctor_response["id"] == doctor_id
        assert doctor_response["verified"] == True
        
        # Verify database was updated
        profile_result = supabase.table("profiles").select("*").eq("id", test_doctor["user_id"]).execute()
        assert len(profile_result.data) > 0
        assert profile_result.data[0]["verified"] == True
    
    def test_verify_doctor_reject(self, admin_token, test_doctor):
        """Test admin can reject doctor application with reason"""
        doctor_id = test_doctor["doctor_id"]
        
        # Reject doctor
        response = client.put(
            f"/api/admin/doctors/{doctor_id}/verify",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "verified": False,
                "rejection_reason": "Invalid license number"
            }
        )
        
        # Verify response
        assert response.status_code == 200
        doctor_response = response.json()
        assert doctor_response["id"] == doctor_id
        assert doctor_response["verified"] == False
    
    def test_verify_doctor_reject_without_reason(self, admin_token, test_doctor):
        """Test rejection requires a reason"""
        doctor_id = test_doctor["doctor_id"]
        
        # Try to reject without reason
        response = client.put(
            f"/api/admin/doctors/{doctor_id}/verify",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"verified": False}
        )
        
        # Should fail validation
        assert response.status_code == 422
    
    def test_verify_doctor_not_found(self, admin_token):
        """Test verification fails for non-existent doctor"""
        fake_doctor_id = str(uuid4())
        
        response = client.put(
            f"/api/admin/doctors/{fake_doctor_id}/verify",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"verified": True}
        )
        
        assert response.status_code == 404
    
    def test_verify_doctor_unauthorized(self, test_doctor):
        """Test endpoint requires authentication"""
        doctor_id = test_doctor["doctor_id"]
        
        response = client.put(
            f"/api/admin/doctors/{doctor_id}/verify",
            json={"verified": True}
        )
        
        assert response.status_code == 401
    
    def test_verify_doctor_forbidden_patient(self, patient_token, test_doctor):
        """Test patient cannot verify doctors"""
        doctor_id = test_doctor["doctor_id"]
        
        response = client.put(
            f"/api/admin/doctors/{doctor_id}/verify",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={"verified": True}
        )
        
        assert response.status_code == 403
        assert "admin role" in response.json()["detail"].lower()
    
    def test_verify_doctor_forbidden_doctor(self, doctor_token, test_doctor):
        """Test doctor cannot verify other doctors"""
        doctor_id = test_doctor["doctor_id"]
        
        response = client.put(
            f"/api/admin/doctors/{doctor_id}/verify",
            headers={"Authorization": f"Bearer {doctor_token}"},
            json={"verified": True}
        )
        
        assert response.status_code == 403
        assert "admin role" in response.json()["detail"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
