"""
Integration test for complete doctor journey
Task 36.2: Write integration tests

Tests the complete doctor flow:
1. Registration → 2. Admin Verification → 3. Login → 4. View Pending Reports → 
5. Add Consultation Notes → 6. Manage Appointments

Requirements: All (complete doctor journey)
"""
import pytest
import sys
import os
from pathlib import Path
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import uuid

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.main import app
from app.database import supabase
from app.auth import create_access_token


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


def create_test_patient_with_report():
    """Helper to create a test patient with a medical report"""
    patient_id = str(uuid.uuid4())
    
    # Create patient profile
    patient_profile = {
        "id": patient_id,
        "email": f"patient_{patient_id[:8]}@test.com",
        "full_name": "Test Patient",
        "role": "patient",
        "verified": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    supabase.table("profiles").insert(patient_profile).execute()
    
    # Create patient data
    patient_data = {
        "id": str(uuid.uuid4()),
        "user_id": patient_id,
        "age": 35,
        "skin_type": "III",
        "family_history": "No family history",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    supabase.table("patient_data").insert(patient_data).execute()
    
    # Create medical report
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
            "hotspots": [{"x": 100, "y": 100, "width": 50, "height": 50, "confidence": 0.85}],
            "model_version": "1.0",
            "processing_time": 2.5
        },
        "symptoms": {
            "body_location": "arm",
            "sensations": ["itching"],
            "visual_changes": ["color", "size"]
        },
        "status": "safe",
        "risk_level": "low",
        "body_location": "arm",
        "consultation_notes": None,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    supabase.table("medical_reports").insert(report_data).execute()
    
    return patient_id, report_id


@pytest.mark.integration
class TestCompleteDoctorJourney:
    """Test complete doctor journey from registration to managing appointments"""
    
    def test_complete_doctor_flow(self, cleanup_test_data):
        """
        Test the complete doctor journey:
        Registration → Admin Verification → Login → View Pending Reports → 
        Add Consultation Notes → Manage Appointments
        
        Validates: All requirements (complete doctor journey)
        """
        test_user_ids, test_doctor_ids, test_report_ids, test_appointment_ids = cleanup_test_data
        
        # ===== STEP 1: Doctor Registration =====
        print("\n=== Step 1: Doctor Registration ===")
        
        doctor_email = f"doctor_{uuid.uuid4().hex[:8]}@test.com"
        signup_data = {
            "email": doctor_email,
            "password": "SecurePassword123!",
            "full_name": "Dr. Test Doctor",
            "role": "doctor"
        }
        
        signup_response = client.post("/api/auth/signup", json=signup_data)
        assert signup_response.status_code == 201, f"Signup failed: {signup_response.text}"
        
        doctor_profile = signup_response.json()
        assert doctor_profile["role"] == "doctor"
        assert doctor_profile["verified"] == False  # Initially unverified
        
        doctor_user_id = doctor_profile["id"]
        test_user_ids.append(doctor_user_id)
        
        print(f"✓ Doctor profile created with ID: {doctor_user_id}")
        
        # Register doctor details
        doctor_id = str(uuid.uuid4())
        doctor_data = {
            "id": doctor_id,
            "user_id": doctor_user_id,
            "license_no": f"LIC{uuid.uuid4().hex[:8]}",
            "clinic_name": "Test Medical Clinic",
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
        test_doctor_ids.append(doctor_id)
        
        print(f"✓ Doctor details registered with license: {doctor_data['license_no']}")
        
        # ===== STEP 2: Verify Doctor Cannot Access Reports (Unverified) =====
        print("\n=== Step 2: Verify Unverified Doctor Cannot Access Reports ===")
        
        # Login as unverified doctor
        login_response = client.post("/api/auth/login", json={
            "email": doctor_email,
            "password": signup_data["password"]
        })
        assert login_response.status_code == 200
        
        unverified_token = login_response.json()["access_token"]
        unverified_headers = {"Authorization": f"Bearer {unverified_token}"}
        
        # Try to access pending reports
        reports_response = client.get(
            "/api/doctors/reports/pending",
            headers=unverified_headers
        )
        assert reports_response.status_code == 403, "Unverified doctor should not access reports"
        assert "verified" in reports_response.json()["detail"].lower()
        
        print(f"✓ Unverified doctor correctly blocked from accessing reports")
        
        # ===== STEP 3: Admin Verification =====
        print("\n=== Step 3: Admin Verification ===")
        
        # Create admin token
        admin_id = str(uuid.uuid4())
        admin_token = create_access_token({
            "sub": admin_id,
            "email": "admin@test.com",
            "role": "admin",
            "verified": True
        })
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get pending doctors
        pending_response = client.get(
            "/api/admin/doctors/pending",
            headers=admin_headers
        )
        assert pending_response.status_code == 200
        
        pending_doctors = pending_response.json()
        assert any(d["id"] == doctor_id for d in pending_doctors)
        
        print(f"✓ Doctor appears in pending verification list")
        
        # Approve doctor
        verify_response = client.put(
            f"/api/admin/doctors/{doctor_id}/verify",
            json={"verified": True},
            headers=admin_headers
        )
        assert verify_response.status_code == 200
        
        verified_doctor = verify_response.json()
        assert verified_doctor["verified"] == True
        
        print(f"✓ Doctor verified by admin")
        
        # ===== STEP 4: Login as Verified Doctor =====
        print("\n=== Step 4: Login as Verified Doctor ===")
        
        # Login again to get updated token
        login_response = client.post("/api/auth/login", json={
            "email": doctor_email,
            "password": signup_data["password"]
        })
        assert login_response.status_code == 200
        
        auth_data = login_response.json()
        assert auth_data["user"]["verified"] == True
        
        doctor_token = auth_data["access_token"]
        doctor_headers = {"Authorization": f"Bearer {doctor_token}"}
        
        print(f"✓ Verified doctor logged in successfully")
        
        # ===== STEP 5: View Pending Reports =====
        print("\n=== Step 5: View Pending Reports ===")
        
        # Create a test patient with report
        patient_id, report_id = create_test_patient_with_report()
        test_user_ids.append(patient_id)
        test_report_ids.append(report_id)
        
        # Get pending reports
        reports_response = client.get(
            "/api/doctors/reports/pending",
            headers=doctor_headers
        )
        assert reports_response.status_code == 200, f"Get reports failed: {reports_response.text}"
        
        reports = reports_response.json()
        assert len(reports) > 0
        assert any(r["id"] == report_id for r in reports)
        
        # Verify report includes patient data
        found_report = next(r for r in reports if r["id"] == report_id)
        assert found_report["patient_name"] == "Test Patient"
        assert found_report["patient_age"] == 35
        assert found_report["patient_skin_type"] == "III"
        assert len(found_report["ai_prediction"]["predictions"]) == 7
        
        print(f"✓ Doctor can view {len(reports)} pending report(s) with patient data")
        
        # ===== STEP 6: Add Consultation Notes =====
        print("\n=== Step 6: Add Consultation Notes ===")
        
        consultation_notes = {
            "notes": "Patient presents with benign-appearing nevus on left arm. "
                    "Lesion shows regular borders and uniform coloration. "
                    "Recommend monitoring for any changes. No immediate treatment required. "
                    "Follow-up in 6 months if any changes occur."
        }
        
        notes_response = client.post(
            f"/api/doctors/reports/{report_id}/notes",
            json=consultation_notes,
            headers=doctor_headers
        )
        assert notes_response.status_code == 200, f"Add notes failed: {notes_response.text}"
        
        updated_report = notes_response.json()
        assert updated_report["consultation_notes"] == consultation_notes["notes"]
        
        print(f"✓ Consultation notes added successfully")
        
        # Verify notes persistence
        verify_response = client.get(
            "/api/doctors/reports/pending",
            headers=doctor_headers
        )
        assert verify_response.status_code == 200
        
        reports = verify_response.json()
        found_report = next(r for r in reports if r["id"] == report_id)
        assert found_report["consultation_notes"] == consultation_notes["notes"]
        
        print(f"✓ Consultation notes persisted in database")
        
        # ===== STEP 7: Create Appointment =====
        print("\n=== Step 7: Create Appointment ===")
        
        # Create appointment (as patient)
        patient_token = create_access_token({
            "sub": patient_id,
            "email": f"patient_{patient_id[:8]}@test.com",
            "role": "patient",
            "verified": True
        })
        patient_headers = {"Authorization": f"Bearer {patient_token}"}
        
        appointment_data = {
            "doctor_id": doctor_id,
            "report_id": report_id,
            "scheduled_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "consultation_type": "video"
        }
        
        appointment_response = client.post(
            "/api/appointments",
            json=appointment_data,
            headers=patient_headers
        )
        assert appointment_response.status_code == 201
        
        appointment = appointment_response.json()
        appointment_id = appointment["id"]
        test_appointment_ids.append(appointment_id)
        
        print(f"✓ Appointment created with ID: {appointment_id}")
        
        # ===== STEP 8: Doctor Views Appointments =====
        print("\n=== Step 8: Doctor Views Appointments ===")
        
        appointments_response = client.get(
            "/api/appointments",
            headers=doctor_headers
        )
        assert appointments_response.status_code == 200
        
        appointments = appointments_response.json()
        assert len(appointments) > 0
        assert any(a["id"] == appointment_id for a in appointments)
        
        found_appointment = next(a for a in appointments if a["id"] == appointment_id)
        assert found_appointment["doctor_id"] == doctor_id
        assert found_appointment["patient_id"] == patient_id
        assert found_appointment["status"] == "pending"
        
        print(f"✓ Doctor can view {len(appointments)} appointment(s)")
        
        # ===== STEP 9: Doctor Updates Appointment Status =====
        print("\n=== Step 9: Doctor Updates Appointment Status ===")
        
        update_response = client.put(
            f"/api/appointments/{appointment_id}",
            json={"status": "confirmed"},
            headers=doctor_headers
        )
        assert update_response.status_code == 200
        
        updated_appointment = update_response.json()
        assert updated_appointment["status"] == "confirmed"
        
        print(f"✓ Appointment status updated to 'confirmed'")
        
        # ===== JOURNEY COMPLETE =====
        print("\n=== ✓ COMPLETE DOCTOR JOURNEY SUCCESSFUL ===")
        print(f"Doctor {doctor_user_id} successfully:")
        print(f"  1. Registered with license")
        print(f"  2. Was blocked from reports (unverified)")
        print(f"  3. Got verified by admin")
        print(f"  4. Logged in as verified doctor")
        print(f"  5. Viewed pending patient reports")
        print(f"  6. Added consultation notes")
        print(f"  7. Viewed appointments")
        print(f"  8. Updated appointment status")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
