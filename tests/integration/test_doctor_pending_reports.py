"""
Integration tests for doctor pending reports endpoint
Task 15.1: Implement doctor report endpoints
Requirements: 9.1, 9.2, 9.3, 23.5
"""
import pytest
import os
import sys
from datetime import datetime
import uuid

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app.database import supabase
from app.auth import create_access_token


class TestDoctorPendingReports:
    """Test suite for GET /api/doctors/reports/pending endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test"""
        self.created_ids = {
            'profiles': [],
            'patient_data': [],
            'doctors': [],
            'medical_reports': []
        }
        yield
        # Cleanup
        self._cleanup()
    
    def _cleanup(self):
        """Clean up test data"""
        try:
            # Delete in reverse order of dependencies
            for report_id in self.created_ids['medical_reports']:
                supabase.table("medical_reports").delete().eq("id", report_id).execute()
            
            for doctor_id in self.created_ids['doctors']:
                supabase.table("doctors").delete().eq("id", doctor_id).execute()
            
            for patient_data_id in self.created_ids['patient_data']:
                supabase.table("patient_data").delete().eq("id", patient_data_id).execute()
            
            for profile_id in self.created_ids['profiles']:
                supabase.table("profiles").delete().eq("id", profile_id).execute()
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    def _create_test_doctor(self, verified=True):
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
        self.created_ids['profiles'].append(doctor_id)
        
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
        self.created_ids['doctors'].append(doctor_record_id)
        
        return result.data[0]
    
    def _create_test_patient(self):
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
        self.created_ids['profiles'].append(patient_id)
        
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
        self.created_ids['patient_data'].append(patient_data_id)
        
        return result.data[0]
    
    def _create_test_report(self, patient_id, status="safe", risk_level="low"):
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
        self.created_ids['medical_reports'].append(report_id)
        
        return result.data[0]
    
    def test_pending_reports_requires_verified_doctor(self):
        """Test that only verified doctors can access pending reports"""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        # Create unverified doctor
        unverified_doctor = self._create_test_doctor(verified=False)
        token = create_access_token({"sub": unverified_doctor["id"]})
        
        # Try to access pending reports
        response = client.get(
            "/api/doctors/reports/pending",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should be forbidden
        assert response.status_code == 403
        assert "verified" in response.json()["detail"].lower()
    
    def test_pending_reports_returns_safe_and_urgent(self):
        """Test that pending reports returns safe and urgent reports"""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        # Create verified doctor
        doctor = self._create_test_doctor(verified=True)
        token = create_access_token({"sub": doctor["id"]})
        
        # Create patient
        patient = self._create_test_patient()
        
        # Create reports with different statuses
        safe_report = self._create_test_report(patient["id"], status="safe", risk_level="low")
        urgent_report = self._create_test_report(patient["id"], status="urgent", risk_level="urgent")
        flagged_report = self._create_test_report(patient["id"], status="flagged", risk_level="medium")
        
        # Get pending reports
        response = client.get(
            "/api/doctors/reports/pending",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        reports = response.json()
        
        # Should include safe and urgent, but not flagged
        report_ids = [r["id"] for r in reports]
        assert safe_report["id"] in report_ids
        assert urgent_report["id"] in report_ids
        assert flagged_report["id"] not in report_ids
    
    def test_pending_reports_includes_patient_data(self):
        """Test that pending reports include patient information"""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        # Create verified doctor
        doctor = self._create_test_doctor(verified=True)
        token = create_access_token({"sub": doctor["id"]})
        
        # Create patient
        patient = self._create_test_patient()
        
        # Create report
        report = self._create_test_report(patient["id"], status="safe", risk_level="low")
        
        # Get pending reports
        response = client.get(
            "/api/doctors/reports/pending",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        reports = response.json()
        
        # Find our report
        our_report = next((r for r in reports if r["id"] == report["id"]), None)
        assert our_report is not None
        
        # Verify patient data is included
        assert our_report["patient_name"] == "Test Patient"
        assert our_report["patient_email"] == patient["email"]
        assert our_report["patient_age"] == 35
        assert our_report["patient_skin_type"] == "III"
        assert our_report["patient_family_history"] == "No family history of skin cancer"
    
    def test_pending_reports_prioritizes_urgent_cases(self):
        """Test that urgent cases appear at the top of the list"""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        # Create verified doctor
        doctor = self._create_test_doctor(verified=True)
        token = create_access_token({"sub": doctor["id"]})
        
        # Create patient
        patient = self._create_test_patient()
        
        # Create reports in specific order: safe, urgent, safe
        safe_report_1 = self._create_test_report(patient["id"], status="safe", risk_level="low")
        urgent_report = self._create_test_report(patient["id"], status="urgent", risk_level="urgent")
        safe_report_2 = self._create_test_report(patient["id"], status="safe", risk_level="medium")
        
        # Get pending reports
        response = client.get(
            "/api/doctors/reports/pending",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        reports = response.json()
        
        # Urgent report should be first
        assert len(reports) >= 3
        assert reports[0]["id"] == urgent_report["id"]
        assert reports[0]["status"] == "urgent"
        
        # Safe reports should come after
        safe_report_ids = [safe_report_1["id"], safe_report_2["id"]]
        for report in reports[1:]:
            if report["id"] in safe_report_ids:
                assert report["status"] == "safe"
    
    def test_pending_reports_status_filter(self):
        """Test filtering by status"""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        # Create verified doctor
        doctor = self._create_test_doctor(verified=True)
        token = create_access_token({"sub": doctor["id"]})
        
        # Create patient
        patient = self._create_test_patient()
        
        # Create reports with different statuses
        safe_report = self._create_test_report(patient["id"], status="safe", risk_level="low")
        urgent_report = self._create_test_report(patient["id"], status="urgent", risk_level="urgent")
        
        # Filter for urgent only
        response = client.get(
            "/api/doctors/reports/pending?status_filter=urgent",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        reports = response.json()
        
        # Should only include urgent reports
        assert all(r["status"] == "urgent" for r in reports)
        assert urgent_report["id"] in [r["id"] for r in reports]
        assert safe_report["id"] not in [r["id"] for r in reports]
        
        # Filter for safe only
        response = client.get(
            "/api/doctors/reports/pending?status_filter=safe",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        reports = response.json()
        
        # Should only include safe reports
        assert all(r["status"] == "safe" for r in reports)
        assert safe_report["id"] in [r["id"] for r in reports]
        assert urgent_report["id"] not in [r["id"] for r in reports]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
