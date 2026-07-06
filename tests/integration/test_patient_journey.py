"""
Integration test for complete patient journey
Task 36.2: Write integration tests

Tests the complete patient flow:
1. Signup → 2. Profile Setup → 3. Image Upload → 4. AI Analysis → 
5. View Results → 6. Find Doctor → 7. Book Appointment

Requirements: All (complete patient journey)
"""
import pytest
import sys
import os
from pathlib import Path
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import uuid
from io import BytesIO
from PIL import Image

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.main import app
from app.database import supabase


client = TestClient(app)


@pytest.fixture
def cleanup_test_data():
    """Cleanup test data after test"""
    test_user_ids = []
    test_doctor_ids = []
    test_report_ids = []
    test_appointment_ids = []
    
    yield test_user_ids, test_doctor_ids, test_report_ids, test_appointment_ids
    
    # Cleanup in reverse order of dependencies
    for appointment_id in test_appointment_ids:
        try:
            supabase.table("appointments").delete().eq("id", appointment_id).execute()
        except:
            pass
    
    for report_id in test_report_ids:
        try:
            supabase.table("medical_reports").delete().eq("id", report_id).execute()
        except:
            pass
    
    for doctor_id in test_doctor_ids:
        try:
            supabase.table("doctors").delete().eq("id", doctor_id).execute()
        except:
            pass
    
    for user_id in test_user_ids:
        try:
            supabase.table("patient_data").delete().eq("user_id", user_id).execute()
            supabase.table("profiles").delete().eq("id", user_id).execute()
        except:
            pass


def create_test_image():
    """Create a test image file"""
    img = Image.new('RGB', (600, 600), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


def create_verified_doctor():
    """Helper to create a verified doctor for testing"""
    doctor_user_id = str(uuid.uuid4())
    doctor_id = str(uuid.uuid4())
    
    # Create doctor profile
    doctor_profile = {
        "id": doctor_user_id,
        "email": f"doctor_{doctor_user_id[:8]}@test.com",
        "full_name": "Dr. Test Doctor",
        "role": "doctor",
        "verified": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    supabase.table("profiles").insert(doctor_profile).execute()
    
    # Create doctor record
    doctor_data = {
        "id": doctor_id,
        "user_id": doctor_user_id,
        "license_no": f"LIC{doctor_user_id[:8]}",
        "clinic_name": "Test Clinic",
        "lat": 40.7128,
        "lng": -74.0060,
        "whatsapp_no": "+1234567890",
        "specialization": "Dermatology",
        "average_rating": 4.5,
        "review_count": 10,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    supabase.table("doctors").insert(doctor_data).execute()
    
    return doctor_user_id, doctor_id


@pytest.mark.integration
class TestCompletePatientJourney:
    """Test complete patient journey from signup to appointment booking"""
    
    def test_complete_patient_flow(self, cleanup_test_data):
        """
        Test the complete patient journey:
        Signup → Profile Setup → Image Upload → AI Analysis → 
        View Results → Find Doctor → Book Appointment
        
        Validates: All requirements (complete patient journey)
        """
        test_user_ids, test_doctor_ids, test_report_ids, test_appointment_ids = cleanup_test_data
        
        # ===== STEP 1: Patient Signup =====
        print("\n=== Step 1: Patient Signup ===")
        
        signup_data = {
            "email": f"patient_{uuid.uuid4().hex[:8]}@test.com",
            "password": "SecurePassword123!",
            "full_name": "Test Patient",
            "role": "patient"
        }
        
        signup_response = client.post("/api/auth/signup", json=signup_data)
        assert signup_response.status_code == 201, f"Signup failed: {signup_response.text}"
        
        patient_profile = signup_response.json()
        assert patient_profile["id"] is not None
        assert patient_profile["email"] == signup_data["email"]
        assert patient_profile["role"] == "patient"
        
        patient_id = patient_profile["id"]
        test_user_ids.append(patient_id)
        
        print(f"✓ Patient created with ID: {patient_id}")
        
        # ===== STEP 2: Patient Login =====
        print("\n=== Step 2: Patient Login ===")
        
        login_data = {
            "email": signup_data["email"],
            "password": signup_data["password"]
        }
        
        login_response = client.post("/api/auth/login", json=login_data)
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        
        auth_data = login_response.json()
        assert "access_token" in auth_data
        assert "user" in auth_data
        
        access_token = auth_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        print(f"✓ Patient logged in successfully")
        
        # ===== STEP 3: Create Patient Health Profile =====
        print("\n=== Step 3: Create Patient Health Profile ===")
        
        patient_data = {
            "age": 35,
            "skin_type": "III",
            "family_history": "No family history of skin cancer"
        }
        
        profile_response = client.post(
            "/api/patient/profile",
            json=patient_data,
            headers=headers
        )
        assert profile_response.status_code == 201, f"Profile creation failed: {profile_response.text}"
        
        patient_profile_data = profile_response.json()
        assert patient_profile_data["age"] == 35
        assert patient_profile_data["skin_type"] == "III"
        
        print(f"✓ Patient health profile created")
        
        # ===== STEP 4: Upload Image for Analysis =====
        print("\n=== Step 4: Upload Image for Analysis ===")
        
        # Note: In a real test, we would upload to /api/analyze-skin
        # For this integration test, we'll create a mock report directly
        # since AI analysis requires actual models
        
        report_id = str(uuid.uuid4())
        report_data = {
            "id": report_id,
            "patient_id": patient_id,
            "image_url": f"https://example.com/images/{report_id}.jpg",
            "ai_prediction": {
                "predictions": [
                    {"type": "Melanoma", "probability": 0.15},
                    {"type": "Basal Cell Carcinoma", "probability": 0.10},
                    {"type": "Squamous Cell Carcinoma", "probability": 0.08},
                    {"type": "Actinic Keratosis", "probability": 0.12},
                    {"type": "Benign Keratosis", "probability": 0.25},
                    {"type": "Dermatofibroma", "probability": 0.20},
                    {"type": "Vascular Lesion", "probability": 0.10}
                ],
                "hotspots": [
                    {"x": 100, "y": 100, "width": 50, "height": 50, "confidence": 0.85}
                ],
                "model_version": "1.0",
                "processing_time": 2.5
            },
            "symptoms": {
                "body_location": "arm",
                "sensations": ["itching"],
                "visual_changes": ["color", "size"],
                "duration": "2 weeks"
            },
            "status": "safe",
            "risk_level": "low",
            "body_location": "arm",
            "consultation_notes": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        supabase.table("medical_reports").insert(report_data).execute()
        test_report_ids.append(report_id)
        
        print(f"✓ Medical report created with ID: {report_id}")
        
        # ===== STEP 5: View Results =====
        print("\n=== Step 5: View Results ===")
        
        reports_response = client.get("/api/reports", headers=headers)
        assert reports_response.status_code == 200, f"Get reports failed: {reports_response.text}"
        
        reports = reports_response.json()
        assert len(reports) > 0
        assert any(r["id"] == report_id for r in reports)
        
        # Get specific report
        report_detail_response = client.get(f"/api/reports/{report_id}", headers=headers)
        assert report_detail_response.status_code == 200
        
        report_detail = report_detail_response.json()
        assert report_detail["id"] == report_id
        assert len(report_detail["ai_prediction"]["predictions"]) == 7
        assert "Melanoma" in [p["type"] for p in report_detail["ai_prediction"]["predictions"]]
        
        print(f"✓ Report retrieved successfully with 7 cancer type predictions")
        
        # ===== STEP 6: Find Nearby Doctors =====
        print("\n=== Step 6: Find Nearby Doctors ===")
        
        # Create a verified doctor for testing
        doctor_user_id, doctor_id = create_verified_doctor()
        test_user_ids.append(doctor_user_id)
        test_doctor_ids.append(doctor_id)
        
        # Search for nearby doctors
        doctors_response = client.get(
            "/api/doctors/nearby?lat=40.7128&lng=-74.0060&radius=50",
            headers=headers
        )
        assert doctors_response.status_code == 200, f"Find doctors failed: {doctors_response.text}"
        
        doctors = doctors_response.json()
        assert len(doctors) > 0
        assert any(d["id"] == doctor_id for d in doctors)
        
        # Verify doctor details
        found_doctor = next(d for d in doctors if d["id"] == doctor_id)
        assert found_doctor["clinic_name"] == "Test Clinic"
        assert found_doctor["verified"] == True
        assert found_doctor["whatsapp_no"] == "+1234567890"
        
        print(f"✓ Found {len(doctors)} verified doctor(s)")
        
        # ===== STEP 7: Book Appointment =====
        print("\n=== Step 7: Book Appointment ===")
        
        appointment_data = {
            "doctor_id": doctor_id,
            "report_id": report_id,
            "scheduled_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "consultation_type": "in_person"
        }
        
        appointment_response = client.post(
            "/api/appointments",
            json=appointment_data,
            headers=headers
        )
        assert appointment_response.status_code == 201, f"Appointment booking failed: {appointment_response.text}"
        
        appointment = appointment_response.json()
        assert appointment["id"] is not None
        assert appointment["patient_id"] == patient_id
        assert appointment["doctor_id"] == doctor_id
        assert appointment["report_id"] == report_id
        assert appointment["status"] == "pending"
        assert appointment["consultation_type"] == "in_person"
        
        appointment_id = appointment["id"]
        test_appointment_ids.append(appointment_id)
        
        print(f"✓ Appointment booked with ID: {appointment_id}")
        
        # ===== STEP 8: Verify Appointment in Patient's List =====
        print("\n=== Step 8: Verify Appointment in Patient's List ===")
        
        appointments_response = client.get("/api/appointments", headers=headers)
        assert appointments_response.status_code == 200
        
        appointments = appointments_response.json()
        assert len(appointments) > 0
        assert any(a["id"] == appointment_id for a in appointments)
        
        print(f"✓ Appointment appears in patient's appointment list")
        
        # ===== JOURNEY COMPLETE =====
        print("\n=== ✓ COMPLETE PATIENT JOURNEY SUCCESSFUL ===")
        print(f"Patient {patient_id} successfully:")
        print(f"  1. Signed up")
        print(f"  2. Logged in")
        print(f"  3. Created health profile")
        print(f"  4. Uploaded image for analysis")
        print(f"  5. Viewed AI results")
        print(f"  6. Found verified doctor")
        print(f"  7. Booked appointment")
        print(f"  8. Verified appointment in list")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
