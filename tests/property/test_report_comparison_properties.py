"""
Property-Based Tests for Report Comparison

Feature: derman-ai-skin-screening
Tests report grouping by location and comparison change detection.

Requirements: 15.4, 15.5
"""

import pytest
import os
import sys
from hypothesis import given, strategies as st, settings, assume
from hypothesis import HealthCheck
from dotenv import load_dotenv
from uuid import uuid4
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, Mock
import json

# Add backend to path FIRST
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

# Set mock environment variables before importing backend modules
os.environ['SUPABASE_URL'] = 'https://mock.supabase.co'
os.environ['SUPABASE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2siLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYwOTQ1OTIwMCwiZXhwIjoxOTI1MDM1MjAwfQ.mock_key_signature'
os.environ['SUPABASE_SERVICE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2siLCJyb2xlIjoic2VydmljZV9yb2xlIiwiaWF0IjoxNjA5NDU5MjAwLCJleHAiOjE5MjUwMzUyMDB9.mock_service_key_signature'
os.environ['JWT_SECRET'] = 'mock_jwt_secret_key_for_testing_purposes_only'

# Load environment variables
load_dotenv()

# Create mock Supabase client BEFORE importing app modules
mock_supabase_client = MagicMock()
mock_supabase_anon_client = MagicMock()

# Mock the database module before it's imported
mock_database_module = MagicMock()
mock_database_module.supabase = mock_supabase_client
mock_database_module.supabase_anon = mock_supabase_anon_client
mock_database_module.get_supabase_client = MagicMock(return_value=mock_supabase_client)
mock_database_module.get_supabase_anon_client = MagicMock(return_value=mock_supabase_anon_client)

# Inject the mock into sys.modules
sys.modules['app.database'] = mock_database_module


@st.composite
def body_location_strategy(draw):
    """Generate valid body locations"""
    return draw(st.sampled_from([
        "left_arm", "right_arm", "left_leg", "right_leg",
        "chest", "back", "face", "neck", "abdomen", "hand", "foot"
    ]))


@st.composite
def medical_report_with_location(draw, patient_id=None, body_location=None):
    """Generate valid medical report data with specific body location"""
    if patient_id is None:
        patient_id = str(uuid4())
    
    if body_location is None:
        body_location = draw(body_location_strategy())
    
    report_id = str(uuid4())
    
    # Generate AI predictions
    cancer_types = [
        "Melanoma",
        "Basal Cell Carcinoma",
        "Squamous Cell Carcinoma",
        "Actinic Keratosis",
        "Benign Keratosis",
        "Dermatofibroma",
        "Vascular Lesion"
    ]
    
    # Generate probabilities that sum to ~1.0
    probabilities = [draw(st.floats(min_value=0.0, max_value=1.0)) for _ in cancer_types]
    total = sum(probabilities)
    if total > 0:
        probabilities = [p / total for p in probabilities]
    else:
        probabilities = [1.0 / len(cancer_types)] * len(cancer_types)
    
    predictions = [
        {
            "type": cancer_type,
            "probability": prob,
            "confidence": draw(st.floats(min_value=0.5, max_value=1.0))
        }
        for cancer_type, prob in zip(cancer_types, probabilities)
    ]
    
    # Sort by probability descending
    predictions.sort(key=lambda x: x['probability'], reverse=True)
    
    # Generate hotspots
    num_hotspots = draw(st.integers(min_value=1, max_value=5))
    hotspots = [
        {
            "x": draw(st.integers(min_value=0, max_value=1000)),
            "y": draw(st.integers(min_value=0, max_value=1000)),
            "width": draw(st.integers(min_value=10, max_value=200)),
            "height": draw(st.integers(min_value=10, max_value=200)),
            "confidence": draw(st.floats(min_value=0.5, max_value=1.0))
        }
        for _ in range(num_hotspots)
    ]
    
    ai_prediction = {
        "predictions": predictions,
        "hotspots": hotspots,
        "model_version": "1.0.0",
        "processing_time": draw(st.floats(min_value=0.5, max_value=5.0))
    }
    
    risk_level = draw(st.sampled_from(["low", "medium", "high", "urgent"]))
    status = "urgent" if risk_level == "urgent" else draw(st.sampled_from(["safe", "flagged"]))
    
    return {
        "id": report_id,
        "patient_id": patient_id,
        "image_url": f"https://storage.example.com/{patient_id}/{report_id}.jpg",
        "ai_prediction": ai_prediction,
        "symptoms": None,
        "status": status,
        "risk_level": risk_level,
        "body_location": body_location,
        "consultation_notes": draw(st.one_of(st.none(), st.text(min_size=10, max_size=200))),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }


# Feature: derman-ai-skin-screening, Property 41: Same-Location Report Grouping
@given(
    body_location=body_location_strategy(),
    num_same_location=st.integers(min_value=2, max_value=5),
    num_different_location=st.integers(min_value=1, max_value=3),
    data=st.data()
)
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None
)
def test_same_location_report_grouping(body_location, num_same_location, num_different_location, data):
    """
    Property 41: Same-Location Report Grouping
    
    For any patient with multiple reports, reports sharing the same body_location
    value should be grouped together and offer comparison functionality.
    
    This test verifies that:
    1. Reports with the same body_location can be compared
    2. The comparison endpoint accepts reports from the same location
    3. The response indicates same_body_location is True
    4. Reports from different locations can still be compared but with a warning
    
    Validates: Requirements 15.4
    """
    from fastapi.testclient import TestClient
    from app.main import app
    
    # Create test client
    client = TestClient(app)
    
    # Create a mock patient
    patient_id = str(uuid4())
    mock_user = {
        "id": patient_id,
        "email": "test@example.com",
        "full_name": "Test User",
        "role": "patient",
        "verified": False
    }
    
    # Generate reports with same location
    same_location_reports = []
    for i in range(num_same_location):
        report = data.draw(medical_report_with_location(
            patient_id=patient_id,
            body_location=body_location
        ))
        # Add time offset to make them distinct
        timestamp = datetime.utcnow() - timedelta(days=i)
        report['created_at'] = timestamp.isoformat()
        report['updated_at'] = timestamp.isoformat()
        same_location_reports.append(report)
    
    # Generate reports with different locations
    different_locations = ["chest", "back", "face", "neck"]
    different_location_reports = []
    for i in range(num_different_location):
        other_location = different_locations[i % len(different_locations)]
        if other_location == body_location:
            other_location = "abdomen"  # Ensure it's different
        
        report = data.draw(medical_report_with_location(
            patient_id=patient_id,
            body_location=other_location
        ))
        timestamp = datetime.utcnow() - timedelta(days=num_same_location + i)
        report['created_at'] = timestamp.isoformat()
        report['updated_at'] = timestamp.isoformat()
        different_location_reports.append(report)
    
    all_reports = same_location_reports + different_location_reports
    
    # Mock authentication
    def mock_get_current_patient():
        return mock_user
    
    # Mock database query
    def mock_table_select(table_name):
        mock_query = MagicMock()
        
        def mock_select(fields):
            return mock_query
        
        def mock_eq(field, value):
            # Find the report by ID
            matching_reports = [r for r in all_reports if r['id'] == value]
            result_mock = MagicMock()
            result_mock.data = matching_reports
            
            def mock_execute():
                return result_mock
            
            mock_query.execute = mock_execute
            return mock_query
        
        mock_query.select = mock_select
        mock_query.eq = mock_eq
        
        return mock_query
    
    # Import dependencies to override
    from app.routers.reports import get_current_patient
    
    # Override FastAPI dependencies
    app.dependency_overrides[get_current_patient] = mock_get_current_patient
    
    try:
        # Test 1: Compare two reports from the same location
        if len(same_location_reports) >= 2:
            report1 = same_location_reports[0]
            report2 = same_location_reports[1]
            
            with patch('app.routers.reports.supabase') as mock_supabase:
                mock_supabase.table = mock_table_select
                
                # Make comparison request
                response = client.post(f"/api/reports/{report1['id']}/compare/{report2['id']}")
                
                # Verify response
                assert response.status_code == 200, \
                    f"Should return 200 OK for same-location comparison, got {response.status_code}: {response.text}"
                
                response_data = response.json()
                
                # Verify comparison structure
                assert 'report1' in response_data, "Response should contain report1"
                assert 'report2' in response_data, "Response should contain report2"
                assert 'changes' in response_data, "Response should contain changes"
                
                # Verify same_body_location flag
                changes = response_data['changes']
                assert 'same_body_location' in changes, \
                    "Changes should indicate if reports are from same body location"
                
                assert changes['same_body_location'] is True, \
                    f"Reports from same location ({body_location}) should have same_body_location=True"
                
                # Verify both reports have the same body_location
                assert response_data['report1']['body_location'] == body_location, \
                    "Report1 should have the expected body location"
                assert response_data['report2']['body_location'] == body_location, \
                    "Report2 should have the expected body location"
                assert response_data['report1']['body_location'] == response_data['report2']['body_location'], \
                    "Both reports should have the same body location"
        
        # Test 2: Compare reports from different locations (should still work but with warning)
        if len(same_location_reports) >= 1 and len(different_location_reports) >= 1:
            report1 = same_location_reports[0]
            report2 = different_location_reports[0]
            
            with patch('app.routers.reports.supabase') as mock_supabase:
                mock_supabase.table = mock_table_select
                
                # Make comparison request
                response = client.post(f"/api/reports/{report1['id']}/compare/{report2['id']}")
                
                # Verify response (should succeed but indicate different locations)
                assert response.status_code == 200, \
                    f"Should return 200 OK even for different-location comparison, got {response.status_code}: {response.text}"
                
                response_data = response.json()
                
                # Verify same_body_location flag is False
                changes = response_data['changes']
                assert 'same_body_location' in changes, \
                    "Changes should indicate if reports are from same body location"
                
                assert changes['same_body_location'] is False, \
                    "Reports from different locations should have same_body_location=False"
                
                # Verify reports have different body_locations
                assert response_data['report1']['body_location'] != response_data['report2']['body_location'], \
                    "Reports should have different body locations"
    
    finally:
        # Clean up dependency overrides
        app.dependency_overrides.clear()


# Feature: derman-ai-skin-screening, Property 42: Report Comparison Change Detection
@given(
    patient_id=st.just(str(uuid4())),
    body_location=body_location_strategy(),
    days_between=st.integers(min_value=1, max_value=180),
    data=st.data()
)
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None
)
def test_report_comparison_change_detection(patient_id, body_location, days_between, data):
    """
    Property 42: Report Comparison Change Detection
    
    For any two reports being compared, the system should compute and highlight
    differences in lesion size, color descriptors, and AI risk_level.
    
    This test verifies that:
    1. Comparison detects risk_level changes
    2. Comparison detects lesion size changes (from hotspots)
    3. Comparison detects top prediction changes
    4. Comparison calculates time between reports
    5. All change fields include 'from', 'to', and 'changed' indicators
    
    Validates: Requirements 15.5
    """
    from fastapi.testclient import TestClient
    from app.main import app
    
    # Create test client
    client = TestClient(app)
    
    # Create a mock patient
    mock_user = {
        "id": patient_id,
        "email": "test@example.com",
        "full_name": "Test User",
        "role": "patient",
        "verified": False
    }
    
    # Generate two reports with intentional differences
    base_time = datetime.utcnow()
    
    # Report 1 (older)
    report1 = data.draw(medical_report_with_location(
        patient_id=patient_id,
        body_location=body_location
    ))
    report1['created_at'] = (base_time - timedelta(days=days_between)).isoformat()
    report1['updated_at'] = report1['created_at']
    
    # Report 2 (newer) - intentionally different
    report2 = data.draw(medical_report_with_location(
        patient_id=patient_id,
        body_location=body_location
    ))
    report2['created_at'] = base_time.isoformat()
    report2['updated_at'] = report2['created_at']
    
    # Ensure reports have different risk levels for testing
    risk_levels = ["low", "medium", "high", "urgent"]
    report1['risk_level'] = risk_levels[0]
    report2['risk_level'] = risk_levels[-1]  # Different from report1
    
    # Mock authentication
    def mock_get_current_patient():
        return mock_user
    
    # Mock database query
    def mock_table_select(table_name):
        mock_query = MagicMock()
        
        def mock_select(fields):
            return mock_query
        
        def mock_eq(field, value):
            # Find the report by ID
            if value == report1['id']:
                matching_reports = [report1]
            elif value == report2['id']:
                matching_reports = [report2]
            else:
                matching_reports = []
            
            result_mock = MagicMock()
            result_mock.data = matching_reports
            
            def mock_execute():
                return result_mock
            
            mock_query.execute = mock_execute
            return mock_query
        
        mock_query.select = mock_select
        mock_query.eq = mock_eq
        
        return mock_query
    
    # Import dependencies to override
    from app.routers.reports import get_current_patient
    
    # Override FastAPI dependencies
    app.dependency_overrides[get_current_patient] = mock_get_current_patient
    
    try:
        with patch('app.routers.reports.supabase') as mock_supabase:
            mock_supabase.table = mock_table_select
            
            # Make comparison request
            response = client.post(f"/api/reports/{report1['id']}/compare/{report2['id']}")
            
            # Verify response
            assert response.status_code == 200, \
                f"Should return 200 OK, got {response.status_code}: {response.text}"
            
            response_data = response.json()
            
            # Verify comparison structure
            assert 'changes' in response_data, "Response should contain changes"
            changes = response_data['changes']
            
            # Test 1: Risk level change detection
            assert 'risk_level_change' in changes, \
                "Changes should include risk_level_change"
            
            risk_change = changes['risk_level_change']
            assert 'from' in risk_change, "risk_level_change should have 'from' field"
            assert 'to' in risk_change, "risk_level_change should have 'to' field"
            assert 'changed' in risk_change, "risk_level_change should have 'changed' field"
            
            assert risk_change['from'] == report1['risk_level'], \
                f"risk_level_change 'from' should match report1 risk_level"
            assert risk_change['to'] == report2['risk_level'], \
                f"risk_level_change 'to' should match report2 risk_level"
            
            # Verify 'changed' flag is correct
            expected_changed = (report1['risk_level'] != report2['risk_level'])
            assert risk_change['changed'] == expected_changed, \
                f"risk_level_change 'changed' should be {expected_changed}"
            
            # Test 2: Time between reports
            assert 'time_between_reports' in changes, \
                "Changes should include time_between_reports"
            
            if changes['time_between_reports']:
                # Verify it's a string with days
                assert isinstance(changes['time_between_reports'], str), \
                    "time_between_reports should be a string"
                assert 'days' in changes['time_between_reports'].lower(), \
                    "time_between_reports should mention 'days'"
            
            # Test 3: Lesion changes (hotspot comparison)
            if 'lesion_changes' in changes and changes['lesion_changes']:
                lesion_changes = changes['lesion_changes']
                
                # Verify count change structure
                if 'count_change' in lesion_changes:
                    count_change = lesion_changes['count_change']
                    assert 'from' in count_change, "count_change should have 'from' field"
                    assert 'to' in count_change, "count_change should have 'to' field"
                    assert 'changed' in count_change, "count_change should have 'changed' field"
                    
                    # Verify counts match hotspot counts
                    hotspots1 = report1['ai_prediction']['hotspots']
                    hotspots2 = report2['ai_prediction']['hotspots']
                    assert count_change['from'] == len(hotspots1), \
                        "count_change 'from' should match report1 hotspot count"
                    assert count_change['to'] == len(hotspots2), \
                        "count_change 'to' should match report2 hotspot count"
                
                # Verify average size change structure
                if 'average_size_change' in lesion_changes:
                    size_change = lesion_changes['average_size_change']
                    assert 'from' in size_change, "average_size_change should have 'from' field"
                    assert 'to' in size_change, "average_size_change should have 'to' field"
                    assert 'changed' in size_change, "average_size_change should have 'changed' field"
                    
                    # Verify sizes are numeric
                    assert isinstance(size_change['from'], (int, float)), \
                        "average_size_change 'from' should be numeric"
                    assert isinstance(size_change['to'], (int, float)), \
                        "average_size_change 'to' should be numeric"
            
            # Test 4: Prediction changes
            if 'prediction_changes' in changes and changes['prediction_changes']:
                pred_changes = changes['prediction_changes']
                
                if 'top_prediction_change' in pred_changes:
                    top_change = pred_changes['top_prediction_change']
                    assert 'from' in top_change, "top_prediction_change should have 'from' field"
                    assert 'to' in top_change, "top_prediction_change should have 'to' field"
                    assert 'changed' in top_change, "top_prediction_change should have 'changed' field"
                    
                    # Verify 'from' and 'to' have type and probability
                    assert 'type' in top_change['from'], \
                        "top_prediction_change 'from' should have cancer type"
                    assert 'probability' in top_change['from'], \
                        "top_prediction_change 'from' should have probability"
                    
                    assert 'type' in top_change['to'], \
                        "top_prediction_change 'to' should have cancer type"
                    assert 'probability' in top_change['to'], \
                        "top_prediction_change 'to' should have probability"
                    
                    # Verify probabilities are valid
                    assert 0 <= top_change['from']['probability'] <= 1, \
                        "Probability should be between 0 and 1"
                    assert 0 <= top_change['to']['probability'] <= 1, \
                        "Probability should be between 0 and 1"
                    
                    # Verify 'changed' flag matches actual change
                    expected_changed = (top_change['from']['type'] != top_change['to']['type'])
                    assert top_change['changed'] == expected_changed, \
                        f"top_prediction_change 'changed' should be {expected_changed}"
            
            # Test 5: Verify both reports are included in response
            assert 'report1' in response_data, "Response should include report1"
            assert 'report2' in response_data, "Response should include report2"
            
            assert response_data['report1']['id'] == report1['id'], \
                "report1 ID should match"
            assert response_data['report2']['id'] == report2['id'], \
                "report2 ID should match"
    
    finally:
        # Clean up dependency overrides
        app.dependency_overrides.clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
