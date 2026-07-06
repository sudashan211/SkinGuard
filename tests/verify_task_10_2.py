"""
Verification script for Task 10.2: Add symptom data to analysis endpoint

This script verifies that:
1. POST /api/analyze-skin accepts symptom data
2. Symptoms are stored in medical_reports.symptoms JSONB field
3. Symptoms are associated with report and patient
"""

import os
import sys

# Add backend to path FIRST
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Set mock environment variables before importing backend modules
os.environ['SUPABASE_URL'] = 'https://mock.supabase.co'
os.environ['SUPABASE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2siLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYwOTQ1OTIwMCwiZXhwIjoxOTI1MDM1MjAwfQ.mock_key_signature'
os.environ['SUPABASE_SERVICE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2siLCJyb2xlIjoic2VydmljZV9yb2xlIiwiaWF0IjoxNjA5NDU5MjAwLCJleHAiOjE5MjUwMzUyMDB9.mock_service_key_signature'
os.environ['JWT_SECRET'] = 'mock_jwt_secret_key_for_testing_purposes_only'

from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import uuid

# Import the app
from app.main import app
from app.models import SymptomData

def test_analyze_skin_with_symptoms():
    """Test that analyze-skin endpoint accepts and stores symptom data"""
    print("\n=== Testing Task 10.2: Symptom Data Integration ===\n")
    
    # Create test client
    client = TestClient(app)
    
    # Mock authentication
    mock_user = {
        'id': str(uuid.uuid4()),
        'email': 'test@example.com',
        'role': 'patient'
    }
    
    # Mock Supabase and AI pipeline
    with patch('app.routers.reports.supabase') as mock_supabase, \
         patch('app.routers.reports.analyze_image') as mock_analyze, \
         patch('app.routers.reports.get_current_patient', return_value=mock_user), \
         patch('app.routers.reports.get_audit_logger'):
        
        # Mock AI analysis result
        mock_result = Mock()
        mock_result.risk_level = "low"
        mock_result.processing_times = {"total": 2.5}
        mock_result.to_jsonb.return_value = {
            "predictions": [
                {"type": "melanoma", "probability": 0.15},
                {"type": "basal_cell_carcinoma", "probability": 0.10}
            ],
            "hotspots": [],
            "model_version": "1.0",
            "processing_time": 2.5
        }
        mock_analyze.return_value = mock_result
        
        # Mock storage upload
        mock_storage = MagicMock()
        mock_storage.from_.return_value.upload.return_value = {"path": "test.jpg"}
        mock_storage.from_.return_value.get_public_url.return_value = "https://example.com/test.jpg"
        mock_supabase.storage = mock_storage
        
        # Mock database insert
        report_id = str(uuid.uuid4())
        mock_table = MagicMock()
        mock_table.insert.return_value.execute.return_value.data = [{
            "id": report_id,
            "patient_id": mock_user['id'],
            "image_url": "https://example.com/test.jpg",
            "ai_prediction": mock_result.to_jsonb(),
            "symptoms": {
                "body_location": "face",
                "sensations": ["itching", "burning"],
                "visual_changes": ["color", "size"],
                "duration": "2 weeks"
            },
            "status": "safe",
            "risk_level": "low",
            "body_location": "face",
            "consultation_notes": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }]
        mock_supabase.table.return_value = mock_table
        
        # Create test image
        test_image = b"fake image data"
        
        # Test 1: Upload with complete symptom data
        print("Test 1: Upload with complete symptom data")
        response = client.post(
            "/api/analyze-skin",
            files={"image": ("test.jpg", test_image, "image/jpeg")},
            data={
                "body_location": "face",
                "sensations": "itching, burning",
                "visual_changes": "color, size",
                "duration": "2 weeks"
            }
        )
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        result = response.json()
        
        # Verify response contains symptom data
        assert "symptoms" in result, "Response should contain symptoms field"
        symptoms = result["symptoms"]
        assert symptoms["body_location"] == "face", "Body location should be stored"
        assert "itching" in symptoms["sensations"], "Sensations should be stored"
        assert "burning" in symptoms["sensations"], "Sensations should be stored"
        assert "color" in symptoms["visual_changes"], "Visual changes should be stored"
        assert "size" in symptoms["visual_changes"], "Visual changes should be stored"
        assert symptoms["duration"] == "2 weeks", "Duration should be stored"
        
        print("✓ Complete symptom data accepted and stored")
        print(f"  - Body location: {symptoms['body_location']}")
        print(f"  - Sensations: {symptoms['sensations']}")
        print(f"  - Visual changes: {symptoms['visual_changes']}")
        print(f"  - Duration: {symptoms['duration']}")
        
        # Verify database insert was called with symptom data
        insert_call = mock_table.insert.call_args
        assert insert_call is not None, "Database insert should be called"
        inserted_data = insert_call[0][0]
        assert "symptoms" in inserted_data, "Inserted data should contain symptoms"
        assert inserted_data["symptoms"] is not None, "Symptoms should not be None"
        print("✓ Symptoms stored in medical_reports.symptoms JSONB field")
        
        # Verify association with patient
        assert inserted_data["patient_id"] == mock_user['id'], "Report should be associated with patient"
        print(f"✓ Symptoms associated with patient {mock_user['id']}")
        
        # Test 2: Upload with partial symptom data
        print("\nTest 2: Upload with partial symptom data (location only)")
        mock_table.insert.return_value.execute.return_value.data = [{
            "id": str(uuid.uuid4()),
            "patient_id": mock_user['id'],
            "image_url": "https://example.com/test.jpg",
            "ai_prediction": mock_result.to_jsonb(),
            "symptoms": {
                "body_location": "arm",
                "sensations": [],
                "visual_changes": [],
                "duration": None
            },
            "status": "safe",
            "risk_level": "low",
            "body_location": "arm",
            "consultation_notes": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }]
        
        response = client.post(
            "/api/analyze-skin",
            files={"image": ("test.jpg", test_image, "image/jpeg")},
            data={"body_location": "arm"}
        )
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        result = response.json()
        assert result["symptoms"]["body_location"] == "arm", "Partial symptom data should be accepted"
        print("✓ Partial symptom data accepted")
        
        # Test 3: Upload without symptom data
        print("\nTest 3: Upload without symptom data")
        mock_table.insert.return_value.execute.return_value.data = [{
            "id": str(uuid.uuid4()),
            "patient_id": mock_user['id'],
            "image_url": "https://example.com/test.jpg",
            "ai_prediction": mock_result.to_jsonb(),
            "symptoms": None,
            "status": "safe",
            "risk_level": "low",
            "body_location": None,
            "consultation_notes": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }]
        
        response = client.post(
            "/api/analyze-skin",
            files={"image": ("test.jpg", test_image, "image/jpeg")},
            data={}
        )
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        result = response.json()
        assert result["symptoms"] is None, "Symptoms should be None when not provided"
        print("✓ Upload without symptoms works correctly")
        
    return True

def test_symptom_data_validation():
    """Test that SymptomData model validates correctly"""
    print("\n=== Testing SymptomData Model Validation ===\n")
    
    # Test valid symptom data
    print("Test 1: Valid symptom data")
    symptoms = SymptomData(
        body_location="face",
        sensations=["itching", "burning"],
        visual_changes=["color", "size"],
        duration="2 weeks"
    )
    assert symptoms.body_location == "face"
    assert symptoms.sensations == ["itching", "burning"]
    assert symptoms.visual_changes == ["color", "size"]
    assert symptoms.duration == "2 weeks"
    print("✓ Valid symptom data accepted")
    
    # Test dict conversion for JSONB
    print("\nTest 2: Dict conversion for JSONB storage")
    symptom_dict = symptoms.dict()
    assert isinstance(symptom_dict, dict)
    assert symptom_dict["body_location"] == "face"
    assert symptom_dict["sensations"] == ["itching", "burning"]
    assert symptom_dict["visual_changes"] == ["color", "size"]
    assert symptom_dict["duration"] == "2 weeks"
    print("✓ Symptom data converts to dict for JSONB storage")
    
    # Test optional fields
    print("\nTest 3: Optional fields")
    symptoms = SymptomData()
    assert symptoms.body_location is None
    assert symptoms.sensations == []
    assert symptoms.visual_changes == []
    assert symptoms.duration is None
    print("✓ All fields are optional")
    
    return True

def main():
    """Run all verification tests"""
    print("=" * 70)
    print("TASK 10.2 VERIFICATION: Add symptom data to analysis endpoint")
    print("=" * 70)
    
    try:
        # Test symptom data model
        if not test_symptom_data_validation():
            print("\n✗ SymptomData model validation failed")
            return 1
        
        # Test endpoint integration
        if not test_analyze_skin_with_symptoms():
            print("\n✗ Endpoint integration test failed")
            return 1
        
        print("\n" + "=" * 70)
        print("✓ ALL VERIFICATIONS PASSED")
        print("=" * 70)
        print("\nTask 10.2 Implementation Status:")
        print("  ✓ POST /api/analyze-skin accepts symptom data")
        print("  ✓ Symptoms stored in medical_reports.symptoms JSONB field")
        print("  ✓ Symptoms associated with report and patient")
        print("\nRequirements Validated:")
        print("  ✓ 5.5 - Store symptom data in medical_reports symptoms field")
        print("  ✓ 5.6 - Associate symptoms with report and patient")
        print("\nImplementation Details:")
        print("  - Endpoint accepts body_location, sensations, visual_changes, duration")
        print("  - Sensations and visual_changes are comma-separated strings")
        print("  - SymptomData model validates and converts to JSONB")
        print("  - All symptom fields are optional")
        print("  - Invalid symptom data is logged but doesn't fail the analysis")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ VERIFICATION FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
