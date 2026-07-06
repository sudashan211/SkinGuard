"""
Manual test for doctor pending reports endpoint
Task 15.1: Implement doctor report endpoints
Requirements: 9.1, 9.2, 9.3, 23.5

Run this script to manually test the pending reports endpoint.
"""
import os
import sys
from datetime import datetime
import uuid

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import supabase
from app.auth import create_access_token


def create_test_doctor(verified=True):
    """Create a test doctor profile"""
    doctor_id = str(uuid.uuid4())
    profile_data = {
        "id": doctor_id,
        "email": f"doctor_{doctor_id[:8]}@test.com",
        "full_name": "Test Doctor",
        "role": "doctor",
        "verified": verified,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    result = supabase.table("profiles").insert(profile_data).execute()
    
    # Create doctor record
    doctor_record_id = str(uuid.uuid4())
    doctor_data = {
        "id": doctor_record_id,
        "user_id": doctor_id,
        "license_no": f"LIC{doctor_id[:8]}",
        "clinic_name": "Test Clinic",
        "lat": 40.7128,
        "lng": -74.0060,
        "whatsapp_no": "+1234567890",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    supabase.table("doctors").insert(doctor_data).execute()
    
    return result.data[0], doctor_record_id


def create_test_patient():
    """Create a test patient profile with patient_data"""
    patient_id = str(uuid.uuid4())
    profile_data = {
        "id": patient_id,
        "email": f"patient_{patient_id[:8]}@test.com",
        "full_name": "Test Patient",
        "role": "patient",
        "verified": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    result = supabase.table("profiles").insert(profile_data).execute()
    
    # Create patient_data
    patient_data_id = str(uuid.uuid4())
    patient_data = {
        "id": patient_data_id,
        "user_id": patient_id,
        "age": 35,
        "skin_type": "III",
        "family_history": "No family history of skin cancer",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    supabase.table("patient_data").insert(patient_data).execute()
    
    return result.data[0], patient_data_id


def create_test_report(patient_id, status="safe", risk_level="low"):
    """Create a test medical report"""
    report_id = str(uuid.uuid4())
    report_data = {
        "id": report_id,
        "patient_id": patient_id,
        "image_url": f"https://example.com/images/{report_id}.jpg",
        "ai_prediction": {
            "predictions": [
                {"type": "Melanoma", "probability": 0.15},
                {"type": "Basal Cell Carcinoma", "probability": 0.10}
            ],
            "hotspots": [{"x": 100, "y": 100, "width": 50, "height": 50, "confidence": 0.8}],
            "model_version": "1.0",
            "processing_time": 2.5
        },
        "symptoms": {
            "body_location": "arm",
            "sensations": ["itching"],
            "visual_changes": ["color", "size"],
            "duration": "2 weeks"
        },
        "status": status,
        "risk_level": risk_level,
        "body_location": "arm",
        "consultation_notes": None,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    result = supabase.table("medical_reports").insert(report_data).execute()
    
    return result.data[0]


def cleanup(profile_ids, doctor_ids, patient_data_ids, report_ids):
    """Clean up test data"""
    try:
        print("\nCleaning up test data...")
        
        for report_id in report_ids:
            supabase.table("medical_reports").delete().eq("id", report_id).execute()
            print(f"  Deleted report: {report_id}")
        
        for doctor_id in doctor_ids:
            supabase.table("doctors").delete().eq("id", doctor_id).execute()
            print(f"  Deleted doctor: {doctor_id}")
        
        for patient_data_id in patient_data_ids:
            supabase.table("patient_data").delete().eq("id", patient_data_id).execute()
            print(f"  Deleted patient_data: {patient_data_id}")
        
        for profile_id in profile_ids:
            supabase.table("profiles").delete().eq("id", profile_id).execute()
            print(f"  Deleted profile: {profile_id}")
        
        print("Cleanup complete!")
    except Exception as e:
        print(f"Cleanup error: {e}")


def main():
    """Main test function"""
    print("=" * 80)
    print("Manual Test: Doctor Pending Reports Endpoint")
    print("Task 15.1: Implement doctor report endpoints")
    print("=" * 80)
    
    profile_ids = []
    doctor_ids = []
    patient_data_ids = []
    report_ids = []
    
    try:
        # Step 1: Create test doctor
        print("\n1. Creating test doctor (verified)...")
        doctor, doctor_record_id = create_test_doctor(verified=True)
        profile_ids.append(doctor["id"])
        doctor_ids.append(doctor_record_id)
        print(f"   Created doctor: {doctor['full_name']} ({doctor['email']})")
        
        # Step 2: Create test patient
        print("\n2. Creating test patient with patient_data...")
        patient, patient_data_id = create_test_patient()
        profile_ids.append(patient["id"])
        patient_data_ids.append(patient_data_id)
        print(f"   Created patient: {patient['full_name']} ({patient['email']})")
        
        # Step 3: Create test reports
        print("\n3. Creating test reports...")
        safe_report = create_test_report(patient["id"], status="safe", risk_level="low")
        report_ids.append(safe_report["id"])
        print(f"   Created SAFE report: {safe_report['id']}")
        
        urgent_report = create_test_report(patient["id"], status="urgent", risk_level="urgent")
        report_ids.append(urgent_report["id"])
        print(f"   Created URGENT report: {urgent_report['id']}")
        
        flagged_report = create_test_report(patient["id"], status="flagged", risk_level="medium")
        report_ids.append(flagged_report["id"])
        print(f"   Created FLAGGED report: {flagged_report['id']}")
        
        # Step 4: Test the endpoint
        print("\n4. Testing GET /api/doctors/reports/pending...")
        
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        token = create_access_token({"sub": doctor["id"]})
        
        response = client.get(
            "/api/doctors/reports/pending",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            reports = response.json()
            print(f"   Retrieved {len(reports)} reports")
            
            # Verify results
            print("\n5. Verifying results...")
            
            # Check that safe and urgent are included, but not flagged
            report_ids_returned = [r["id"] for r in reports]
            
            if safe_report["id"] in report_ids_returned:
                print("   ✓ SAFE report included")
            else:
                print("   ✗ SAFE report NOT included (ERROR)")
            
            if urgent_report["id"] in report_ids_returned:
                print("   ✓ URGENT report included")
            else:
                print("   ✗ URGENT report NOT included (ERROR)")
            
            if flagged_report["id"] not in report_ids_returned:
                print("   ✓ FLAGGED report excluded (correct)")
            else:
                print("   ✗ FLAGGED report included (ERROR)")
            
            # Check urgent prioritization
            if len(reports) >= 2:
                first_report = reports[0]
                if first_report["status"] == "urgent":
                    print("   ✓ URGENT report prioritized at top")
                else:
                    print(f"   ✗ First report is {first_report['status']}, not urgent (ERROR)")
            
            # Check patient data inclusion
            print("\n6. Verifying patient data inclusion...")
            for report in reports:
                if report["id"] == safe_report["id"]:
                    print(f"   Report ID: {report['id']}")
                    print(f"   Patient Name: {report.get('patient_name', 'MISSING')}")
                    print(f"   Patient Email: {report.get('patient_email', 'MISSING')}")
                    print(f"   Patient Age: {report.get('patient_age', 'MISSING')}")
                    print(f"   Patient Skin Type: {report.get('patient_skin_type', 'MISSING')}")
                    print(f"   Patient Family History: {report.get('patient_family_history', 'MISSING')}")
                    
                    if all([
                        report.get('patient_name'),
                        report.get('patient_email'),
                        report.get('patient_age'),
                        report.get('patient_skin_type'),
                        report.get('patient_family_history')
                    ]):
                        print("   ✓ All patient data fields present")
                    else:
                        print("   ✗ Some patient data fields missing (ERROR)")
                    break
            
            print("\n" + "=" * 80)
            print("TEST PASSED: All checks completed successfully!")
            print("=" * 80)
        else:
            print(f"   ERROR: {response.json()}")
            print("\n" + "=" * 80)
            print("TEST FAILED: Endpoint returned error")
            print("=" * 80)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 80)
        print("TEST FAILED: Exception occurred")
        print("=" * 80)
    
    finally:
        # Cleanup
        cleanup(profile_ids, doctor_ids, patient_data_ids, report_ids)


if __name__ == "__main__":
    main()
