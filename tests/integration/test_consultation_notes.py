"""
Integration tests for consultation notes endpoint
Requirements: 9.5, 25.5
"""
import pytest
import os
import sys
from fastapi.testclient import TestClient
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables from tests/.env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app.main import app
from app.database import supabase


client = TestClient(app)


@pytest.fixture
def cleanup_test_data():
    """Cleanup test data after each test"""
    test_user_ids = []
    test_report_ids = []
    
    yield test_user_ids, test_report_ids
    
    # Cleanup
    for report_id in test_report_ids:
        try:
            supabase.table("medical_reports").delete().eq("id", report_id).execute()
        except:
            pass
    
    for user_id in test_user_ids:
        try:
            supabase.table("doctors").delete().eq("user_id", user_id).execute()
            supabase.table("profiles").delete().eq("id", user_id).execute()
        except:
            pass


def create_test_doctor(verified=True):
    """Helper to create a test doctor user"""
    user_id = str(uuid.uuid4())
    email = f"doctor_{user_id[:8]}@test.com"
    
    # Create profile
    profile_data = {
        "id": user_id,
        "email": email,
        "full_name": "Test Doctor",
        "role": "doctor",
        "verified": verified,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    supabase.table("profiles").insert(profile_data).execute()
    
    # Create doctor record
    doctor_data = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "license_no": f"LIC{user_id[:8]}",
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
    supabase.table("doctors").insert(doctor_data).execute()
    
    return user_id, email


def create_test_patient():
    """Helper to create a test patient user"""
    user_id = str(uuid.uuid4())
    email = f"patient_{user_id[:8]}@test.com"
    
    # Create profile
    profile_data = {
        "id": user_id,
        "email": email,
        "full_name": "Test Patient",
        "role": "patient",
        "verified": False,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    supabase.table("profiles").insert(profile_data).execute()
    
    return user_id


def create_test_report(patient_id, status="safe", risk_level="low"):
    """Helper to create a test medical report"""
    report_id = str(uuid.uuid4())
    
    report_data = {
        "id": report_id,
        "patient_id": patient_id,
        "image_url": "https://example.com/test.jpg",
        "ai_prediction": {
            "predictions": [
                {"type": "melanoma", "probability": 0.1},
                {"type": "basal_cell_carcinoma", "probability": 0.05}
            ],
            "hotspots": [],
            "model_version": "1.0",
            "processing_time": 1.5
        },
        "symptoms": None,
        "status": status,
        "risk_level": risk_level,
        "body_location": "arm",
        "consultation_notes": None,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    result = supabase.table("medical_reports").insert(report_data).execute()
    return report_id


def get_auth_token(user_id: str) -> str:
    """Helper to generate JWT token for testing"""
    from jose import jwt
    from datetime import timedelta
    import os
    
    secret_key = os.getenv("JWT_SECRET_KEY", "test-secret-key-for-development-only")
    
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token


class TestConsultationNotesEndpoint:
    """Test suite for POST /api/doctors/reports/{id}/notes endpoint"""
    
    def test_add_consultation_notes_success(self, cleanup_test_data):
        """Test successfully adding consultation notes to a report"""
        test_user_ids, test_report_ids = cleanup_test_data
        
        # Create verified doctor
        doctor_id, doctor_email = create_test_doctor(verified=True)
        test_user_ids.append(doctor_id)
        
        # Create patient and report
        patient_id = create_test_patient()
        test_user_ids.append(patient_id)
        
        report_id = create_test_report(patient_id, status="safe")
        test_report_ids.append(report_id)
        
        # Get auth token
        token = get_auth_token(doctor_id)
        
        # Add consultation notes
        notes_data = {
            "notes": "Patient shows signs of benign nevus. Recommend monitoring for changes. No immediate treatment required."
        }
        
        response = client.post(
            f"/api/doctors/reports/{report_id}/notes",
            json=notes_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Verify response
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["id"] == report_id
        assert data["consultation_notes"] == notes_data["notes"]
        assert data["patient_id"] == patient_id
        
        # Verify notes were persisted in database
        report_result = supabase.table("medical_reports").select("*").eq("id", report_id).execute()
        assert len(report_result.data) == 1
        assert report_result.data[0]["consultation_notes"] == notes_data["notes"]
    
    
    def test_add_consultation_notes_unverified_doctor(self, cleanup_test_data):
        """Test that unverified doctors cannot add consultation notes"""
        test_user_ids, test_report_ids = cleanup_test_data
        
        # Create unverified doctor
        doctor_id, doctor_email = create_test_doctor(verified=False)
        test_user_ids.append(doctor_id)
        
        # Create patient and report
        patient_id = create_test_patient()
        test_user_ids.append(patient_id)
        
        report_id = create_test_report(patient_id)
        test_report_ids.append(report_id)
        
        # Get auth token
        token = get_auth_token(doctor_id)
        
        # Try to add consultation notes
        notes_data = {
            "notes": "Test notes"
        }
        
        response = client.post(
            f"/api/doctors/reports/{report_id}/notes",
            json=notes_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Verify forbidden response
        assert response.status_code == 403
    
    
    def test_add_consultation_notes_invalid_report_id(self, cleanup_test_data):
        """Test adding notes with invalid report ID"""
        test_user_ids, test_report_ids = cleanup_test_data
        
        # Create verified doctor
        doctor_id, doctor_email = create_test_doctor(verified=True)
        test_user_ids.append(doctor_id)
        
        # Get auth token
        token = get_auth_token(doctor_id)
        
        # Try to add notes with invalid UUID
        notes_data = {
            "notes": "Test notes"
        }
        
        response = client.post(
            f"/api/doctors/reports/invalid-uuid/notes",
            json=notes_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Verify bad request response
        assert response.status_code == 400
        assert "INVALID_REPORT_ID" in response.text
    
    
    def test_add_consultation_notes_report_not_found(self, cleanup_test_data):
        """Test adding notes to non-existent report"""
        test_user_ids, test_report_ids = cleanup_test_data
        
        # Create verified doctor
        doctor_id, doctor_email = create_test_doctor(verified=True)
        test_user_ids.append(doctor_id)
        
        # Get auth token
        token = get_auth_token(doctor_id)
        
        # Try to add notes to non-existent report
        fake_report_id = str(uuid.uuid4())
        notes_data = {
            "notes": "Test notes"
        }
        
        response = client.post(
            f"/api/doctors/reports/{fake_report_id}/notes",
            json=notes_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Verify not found response
        assert response.status_code == 404
        assert "REPORT_NOT_FOUND" in response.text
    
    
    def test_add_consultation_notes_flagged_report(self, cleanup_test_data):
        """Test that notes cannot be added to flagged reports"""
        test_user_ids, test_report_ids = cleanup_test_data
        
        # Create verified doctor
        doctor_id, doctor_email = create_test_doctor(verified=True)
        test_user_ids.append(doctor_id)
        
        # Create patient and flagged report
        patient_id = create_test_patient()
        test_user_ids.append(patient_id)
        
        report_id = create_test_report(patient_id, status="flagged")
        test_report_ids.append(report_id)
        
        # Get auth token
        token = get_auth_token(doctor_id)
        
        # Try to add notes to flagged report
        notes_data = {
            "notes": "Test notes"
        }
        
        response = client.post(
            f"/api/doctors/reports/{report_id}/notes",
            json=notes_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Verify forbidden response
        assert response.status_code == 403
        assert "REPORT_NOT_ACCESSIBLE" in response.text
    
    
    def test_add_consultation_notes_empty_notes(self, cleanup_test_data):
        """Test that empty notes are rejected"""
        test_user_ids, test_report_ids = cleanup_test_data
        
        # Create verified doctor
        doctor_id, doctor_email = create_test_doctor(verified=True)
        test_user_ids.append(doctor_id)
        
        # Create patient and report
        patient_id = create_test_patient()
        test_user_ids.append(patient_id)
        
        report_id = create_test_report(patient_id)
        test_report_ids.append(report_id)
        
        # Get auth token
        token = get_auth_token(doctor_id)
        
        # Try to add empty notes
        notes_data = {
            "notes": "   "  # Just whitespace
        }
        
        response = client.post(
            f"/api/doctors/reports/{report_id}/notes",
            json=notes_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Verify validation error
        assert response.status_code == 422
    
    
    def test_add_consultation_notes_update_existing(self, cleanup_test_data):
        """Test updating existing consultation notes"""
        test_user_ids, test_report_ids = cleanup_test_data
        
        # Create verified doctor
        doctor_id, doctor_email = create_test_doctor(verified=True)
        test_user_ids.append(doctor_id)
        
        # Create patient and report
        patient_id = create_test_patient()
        test_user_ids.append(patient_id)
        
        report_id = create_test_report(patient_id)
        test_report_ids.append(report_id)
        
        # Get auth token
        token = get_auth_token(doctor_id)
        
        # Add initial notes
        initial_notes = {
            "notes": "Initial consultation notes"
        }
        
        response1 = client.post(
            f"/api/doctors/reports/{report_id}/notes",
            json=initial_notes,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response1.status_code == 200
        
        # Update notes
        updated_notes = {
            "notes": "Updated consultation notes with additional findings"
        }
        
        response2 = client.post(
            f"/api/doctors/reports/{report_id}/notes",
            json=updated_notes,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response2.status_code == 200
        
        data = response2.json()
        assert data["consultation_notes"] == updated_notes["notes"]
        
        # Verify updated notes in database
        report_result = supabase.table("medical_reports").select("*").eq("id", report_id).execute()
        assert report_result.data[0]["consultation_notes"] == updated_notes["notes"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
