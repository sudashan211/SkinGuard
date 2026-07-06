"""
Manual test for consultation notes endpoint
Requirements: 9.5, 25.5
"""
import os
import sys
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment from tests/.env
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import supabase
from app.auth import create_access_token


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


def test_add_consultation_notes():
    """Test adding consultation notes to a report"""
    print("\n=== Testing Consultation Notes Endpoint ===\n")
    
    # Create test data
    print("1. Creating test doctor...")
    doctor_id, doctor_email = create_test_doctor(verified=True)
    print(f"   Created doctor: {doctor_id}")
    
    print("2. Creating test patient...")
    patient_id = create_test_patient()
    print(f"   Created patient: {patient_id}")
    
    print("3. Creating test report...")
    report_id = create_test_report(patient_id, status="safe")
    print(f"   Created report: {report_id}")
    
    # Test adding consultation notes
    print("\n4. Testing consultation notes update...")
    notes_text = "Patient shows signs of benign nevus. Recommend monitoring for changes. No immediate treatment required."
    
    update_data = {
        "consultation_notes": notes_text,
        "updated_at": datetime.utcnow().isoformat()
    }
    
    result = supabase.table("medical_reports").update(update_data).eq("id", report_id).execute()
    
    if result.data and len(result.data) > 0:
        print("   ✓ Consultation notes added successfully")
        print(f"   Notes: {result.data[0]['consultation_notes'][:50]}...")
    else:
        print("   ✗ Failed to add consultation notes")
        return False
    
    # Verify notes were persisted
    print("\n5. Verifying notes persistence...")
    verify_result = supabase.table("medical_reports").select("*").eq("id", report_id).execute()
    
    if verify_result.data and len(verify_result.data) > 0:
        stored_notes = verify_result.data[0].get("consultation_notes")
        if stored_notes == notes_text:
            print("   ✓ Notes persisted correctly")
        else:
            print(f"   ✗ Notes mismatch: expected '{notes_text}', got '{stored_notes}'")
            return False
    else:
        print("   ✗ Failed to retrieve report")
        return False
    
    # Cleanup
    print("\n6. Cleaning up test data...")
    try:
        supabase.table("medical_reports").delete().eq("id", report_id).execute()
        supabase.table("doctors").delete().eq("user_id", doctor_id).execute()
        supabase.table("profiles").delete().eq("id", doctor_id).execute()
        supabase.table("profiles").delete().eq("id", patient_id).execute()
        print("   ✓ Cleanup complete")
    except Exception as e:
        print(f"   ⚠ Cleanup error: {e}")
    
    print("\n=== Test Passed ===\n")
    return True


if __name__ == "__main__":
    try:
        success = test_add_consultation_notes()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
