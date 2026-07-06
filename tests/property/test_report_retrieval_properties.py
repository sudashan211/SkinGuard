"""
Property-Based Tests for Report Retrieval
These tests verify correctness properties for medical report history and retrieval

Feature: derman-ai-skin-screening
Tests report retrieval properties including ordering, display completeness,
and historical report retrieval.

Requirements: 15.1, 15.2, 15.3
"""

import pytest
import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings
from hypothesis import HealthCheck
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
import uuid

# Add backend to path for imports
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Mock environment variables before importing app modules
import os
os.environ.setdefault('SUPABASE_URL', 'https://test.supabase.co')
os.environ.setdefault('SUPABASE_KEY', 'test-key')
os.environ.setdefault('SUPABASE_SERVICE_ROLE_KEY', 'test-service-key')
os.environ.setdefault('JWT_SECRET', 'test-secret')

# Mock the supabase client before importing app modules
sys.modules['app.database'] = Mock()
sys.modules['app.database'].supabase = Mock()
sys.modules['app.database'].supabase_anon = Mock()


# Hypothesis strategies for generating test data
@st.composite
def mock_medical_report(draw, patient_id=None):
    """Generate a mock medical report for testing"""
    if patient_id is None:
        patient_id = str(uuid.uuid4())
    
    # Generate timestamps (within last year)
    days_ago = draw(st.integers(min_value=0, max_value=365))
    created_at = datetime.utcnow() - timedelta(days=days_ago)
    
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
    
    predictions = []
    remaining_prob = 1.0
    for i, cancer_type in enumerate(cancer_types):
        if i == len(cancer_types) - 1:
            prob = remaining_prob
        else:
            max_prob = remaining_prob / (len(cancer_types) - i)
            prob = draw(st.floats(min_value=0.0, max_value=max_prob))
            remaining_prob -= prob
        
        predictions.append({
            "type": cancer_type,
            "probability": prob,
            "confidence": prob
        })
    
    # Generate hotspots
    num_hotspots = draw(st.integers(min_value=0, max_value=3))
    hotspots = []
    for _ in range(num_hotspots):
        hotspots.append({
            "x": draw(st.integers(min_value=0, max_value=600)),
            "y": draw(st.integers(min_value=0, max_value=600)),
            "width": draw(st.integers(min_value=20, max_value=100)),
            "height": draw(st.integers(min_value=20, max_value=100)),
            "confidence": draw(st.floats(min_value=0.5, max_value=1.0))
        })
    
    ai_prediction = {
        "predictions": predictions,
        "hotspots": hotspots,
        "model_version": "1.0.0",
        "processing_time": draw(st.floats(min_value=0.5, max_value=5.0))
    }
    
    # Generate symptoms
    body_locations = ["face", "arm", "leg", "back", "chest", "abdomen"]
    sensations = ["itching", "pain", "burning", "numbness"]
    visual_changes = ["color_change", "size_increase", "shape_change", "border_irregularity"]
    
    symptoms = {
        "location": draw(st.sampled_from(body_locations)),
        "sensations": draw(st.lists(st.sampled_from(sensations), min_size=0, max_size=3, unique=True)),
        "visual_changes": draw(st.lists(st.sampled_from(visual_changes), min_size=0, max_size=3, unique=True)),
        "duration": draw(st.sampled_from(["< 1 week", "1-4 weeks", "1-3 months", "> 3 months"]))
    }
    
    # Determine risk level based on max probability
    max_prob = max(p["probability"] for p in predictions)
    if max_prob > 0.85:
        risk_level = "urgent"
        status = "urgent"
    elif max_prob > 0.7:
        risk_level = "high"
        status = "safe"
    elif max_prob > 0.4:
        risk_level = "medium"
        status = "safe"
    else:
        risk_level = "low"
        status = "safe"
    
    report = {
        "id": str(uuid.uuid4()),
        "patient_id": patient_id,
        "image_url": f"https://storage.example.com/images/{uuid.uuid4()}.jpg",
        "ai_prediction": ai_prediction,
        "symptoms": symptoms,
        "status": status,
        "risk_level": risk_level,
        "body_location": symptoms["location"],
        "consultation_notes": None,
        "created_at": created_at.isoformat(),
        "updated_at": created_at.isoformat()
    }
    
    return report


@st.composite
def mock_report_list(draw, min_size=1, max_size=10):
    """Generate a list of medical reports for the same patient"""
    patient_id = str(uuid.uuid4())
    num_reports = draw(st.integers(min_value=min_size, max_value=max_size))
    
    reports = []
    for _ in range(num_reports):
        report = draw(mock_medical_report(patient_id=patient_id))
        reports.append(report)
    
    return reports, patient_id


# Feature: derman-ai-skin-screening, Property 38: Report History Ordering
@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    reports_data=mock_report_list(min_size=2, max_size=10)
)
def test_report_history_ordering(reports_data):
    """
    Property 38: Report History Ordering
    
    For any patient accessing their dashboard, the returned medical_reports
    should be ordered by created_at timestamp in descending order (newest first).
    
    This test verifies:
    1. Reports are returned in descending order by created_at
    2. Newest reports appear first in the list
    3. Oldest reports appear last in the list
    4. Ordering is consistent across multiple retrievals
    
    Validates: Requirements 15.1
    """
    from app.routers.reports import get_patient_reports
    from app.models import MedicalReportListResponse
    
    reports, patient_id = reports_data
    
    # Mock current user
    current_user = {
        "id": patient_id,
        "role": "patient"
    }
    
    # Mock supabase response
    mock_supabase_result = Mock()
    mock_supabase_result.data = reports
    
    # Create mock supabase client
    with patch('app.routers.reports.supabase') as mock_supabase:
        # Setup mock chain
        mock_table = Mock()
        mock_select = Mock()
        mock_eq = Mock()
        mock_order = Mock()
        
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_eq
        mock_eq.order.return_value = mock_order
        
        # Sort reports by created_at descending (simulating database behavior)
        sorted_reports = sorted(
            reports,
            key=lambda r: datetime.fromisoformat(r['created_at']),
            reverse=True
        )
        mock_order.execute.return_value = Mock(data=sorted_reports)
        
        # Call the endpoint
        import asyncio
        result = asyncio.run(get_patient_reports(current_user=current_user))
        
        # Verify supabase was called with correct ordering
        mock_eq.order.assert_called_once_with("created_at", desc=True)
        
        # Verify result is a list
        assert isinstance(result, list), "Result should be a list"
        assert len(result) == len(reports), f"Should return all {len(reports)} reports"
        
        # Verify ordering: each report should have created_at >= next report
        for i in range(len(result) - 1):
            current_time = result[i].created_at if isinstance(result[i].created_at, datetime) else datetime.fromisoformat(result[i].created_at)
            next_time = result[i + 1].created_at if isinstance(result[i + 1].created_at, datetime) else datetime.fromisoformat(result[i + 1].created_at)
            
            assert current_time >= next_time, \
                f"Reports should be ordered by created_at descending: " \
                f"report[{i}] ({current_time}) should be >= report[{i+1}] ({next_time})"
        
        # Verify newest report is first
        if len(result) > 0:
            newest_in_result = result[0].created_at if isinstance(result[0].created_at, datetime) else datetime.fromisoformat(result[0].created_at)
            newest_in_data = max(datetime.fromisoformat(r['created_at']) for r in reports)
            
            assert newest_in_result == newest_in_data, \
                f"First report should be the newest: expected {newest_in_data}, got {newest_in_result}"
        
        # Verify oldest report is last
        if len(result) > 0:
            oldest_in_result = result[-1].created_at if isinstance(result[-1].created_at, datetime) else datetime.fromisoformat(result[-1].created_at)
            oldest_in_data = min(datetime.fromisoformat(r['created_at']) for r in reports)
            
            assert oldest_in_result == oldest_in_data, \
                f"Last report should be the oldest: expected {oldest_in_data}, got {oldest_in_result}"


# Feature: derman-ai-skin-screening, Property 39: Report History Display Completeness
@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    reports_data=mock_report_list(min_size=1, max_size=5)
)
def test_report_history_display_completeness(reports_data):
    """
    Property 39: Report History Display Completeness
    
    For any report in the history list, the displayed data should include
    thumbnail image, AI prediction summary, submission date, and status.
    
    This test verifies:
    1. Each report includes image_url (thumbnail)
    2. Each report includes top_prediction (AI summary)
    3. Each report includes created_at (submission date)
    4. Each report includes status
    5. Each report includes risk_level
    6. Top prediction contains type and probability
    
    Validates: Requirements 15.2
    """
    from app.routers.reports import get_patient_reports
    from app.models import MedicalReportListResponse
    
    reports, patient_id = reports_data
    
    # Mock current user
    current_user = {
        "id": patient_id,
        "role": "patient"
    }
    
    # Mock supabase response
    with patch('app.routers.reports.supabase') as mock_supabase:
        # Setup mock chain
        mock_table = Mock()
        mock_select = Mock()
        mock_eq = Mock()
        mock_order = Mock()
        
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_eq
        mock_eq.order.return_value = mock_order
        mock_order.execute.return_value = Mock(data=reports)
        
        # Call the endpoint
        import asyncio
        result = asyncio.run(get_patient_reports(current_user=current_user))
        
        # Verify each report has required fields
        assert len(result) > 0, "Should return at least one report"
        
        for i, report_item in enumerate(result):
            # Verify it's the correct type
            assert isinstance(report_item, MedicalReportListResponse), \
                f"Report {i} should be MedicalReportListResponse instance"
            
            # Verify thumbnail image (image_url)
            assert hasattr(report_item, 'image_url'), \
                f"Report {i} should have image_url field"
            assert report_item.image_url is not None, \
                f"Report {i} image_url should not be None"
            assert isinstance(report_item.image_url, str), \
                f"Report {i} image_url should be a string"
            assert len(report_item.image_url) > 0, \
                f"Report {i} image_url should not be empty"
            
            # Verify AI prediction summary (top_prediction)
            assert hasattr(report_item, 'top_prediction'), \
                f"Report {i} should have top_prediction field"
            
            # top_prediction can be None if no predictions, but if present should have type and probability
            if report_item.top_prediction is not None:
                assert isinstance(report_item.top_prediction, dict), \
                    f"Report {i} top_prediction should be a dict"
                assert 'type' in report_item.top_prediction, \
                    f"Report {i} top_prediction should have 'type' field"
                assert 'probability' in report_item.top_prediction, \
                    f"Report {i} top_prediction should have 'probability' field"
                assert isinstance(report_item.top_prediction['type'], str), \
                    f"Report {i} top_prediction type should be a string"
                assert isinstance(report_item.top_prediction['probability'], (int, float)), \
                    f"Report {i} top_prediction probability should be a number"
                assert 0.0 <= report_item.top_prediction['probability'] <= 1.0, \
                    f"Report {i} top_prediction probability should be between 0 and 1"
            
            # Verify submission date (created_at)
            assert hasattr(report_item, 'created_at'), \
                f"Report {i} should have created_at field"
            assert report_item.created_at is not None, \
                f"Report {i} created_at should not be None"
            # created_at should be a datetime object
            assert isinstance(report_item.created_at, datetime), \
                f"Report {i} created_at should be a datetime object"
            
            # Verify status
            assert hasattr(report_item, 'status'), \
                f"Report {i} should have status field"
            assert report_item.status is not None, \
                f"Report {i} status should not be None"
            assert report_item.status in ['safe', 'flagged', 'urgent'], \
                f"Report {i} status should be one of: safe, flagged, urgent, got '{report_item.status}'"
            
            # Verify risk_level
            assert hasattr(report_item, 'risk_level'), \
                f"Report {i} should have risk_level field"
            assert report_item.risk_level is not None, \
                f"Report {i} risk_level should not be None"
            assert report_item.risk_level in ['low', 'medium', 'high', 'urgent'], \
                f"Report {i} risk_level should be one of: low, medium, high, urgent, got '{report_item.risk_level}'"
            
            # Verify body_location (optional but should be present in response)
            assert hasattr(report_item, 'body_location'), \
                f"Report {i} should have body_location field"
            
            # Verify patient_id matches
            assert hasattr(report_item, 'patient_id'), \
                f"Report {i} should have patient_id field"
            assert report_item.patient_id == patient_id, \
                f"Report {i} patient_id should match current user"


# Feature: derman-ai-skin-screening, Property 40: Historical Report Retrieval Completeness
@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    report_data=mock_medical_report()
)
def test_historical_report_retrieval_completeness(report_data):
    """
    Property 40: Historical Report Retrieval Completeness
    
    For any historical report selection, the retrieved data should include
    the full-resolution image, complete AI predictions, and all symptom data.
    
    This test verifies:
    1. Report includes full-resolution image_url
    2. Report includes complete ai_prediction with all 7 cancer types
    3. Report includes all symptom data (location, sensations, visual_changes)
    4. Report includes all metadata (status, risk_level, timestamps)
    5. AI predictions include hotspots
    6. AI predictions include model version and processing time
    
    Validates: Requirements 15.3
    """
    from app.routers.reports import get_report_by_id
    from app.models import MedicalReportResponse
    
    report_id = report_data['id']
    patient_id = report_data['patient_id']
    
    # Mock current user
    current_user = {
        "id": patient_id,
        "role": "patient"
    }
    
    # Mock supabase response
    with patch('app.routers.reports.supabase') as mock_supabase:
        # Setup mock chain
        mock_table = Mock()
        mock_select = Mock()
        mock_eq = Mock()
        
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_eq
        mock_eq.execute.return_value = Mock(data=[report_data])
        
        # Call the endpoint
        import asyncio
        result = asyncio.run(get_report_by_id(report_id=report_id, current_user=current_user))
        
        # Verify result is correct type
        assert isinstance(result, MedicalReportResponse), \
            "Result should be MedicalReportResponse instance"
        
        # Verify full-resolution image
        assert hasattr(result, 'image_url'), "Report should have image_url field"
        assert result.image_url is not None, "image_url should not be None"
        assert isinstance(result.image_url, str), "image_url should be a string"
        assert len(result.image_url) > 0, "image_url should not be empty"
        assert result.image_url == report_data['image_url'], \
            "image_url should match original report data"
        
        # Verify complete AI predictions
        assert hasattr(result, 'ai_prediction'), "Report should have ai_prediction field"
        assert result.ai_prediction is not None, "ai_prediction should not be None"
        assert isinstance(result.ai_prediction, dict), "ai_prediction should be a dict"
        
        # Verify predictions array
        assert 'predictions' in result.ai_prediction, \
            "ai_prediction should contain 'predictions' field"
        predictions = result.ai_prediction['predictions']
        assert isinstance(predictions, list), "predictions should be a list"
        assert len(predictions) == 7, \
            f"Should have predictions for all 7 cancer types, got {len(predictions)}"
        
        # Verify each prediction has required fields
        for i, pred in enumerate(predictions):
            assert 'type' in pred, f"Prediction {i} should have 'type' field"
            assert 'probability' in pred, f"Prediction {i} should have 'probability' field"
            assert 'confidence' in pred, f"Prediction {i} should have 'confidence' field"
            assert isinstance(pred['type'], str), f"Prediction {i} type should be a string"
            assert isinstance(pred['probability'], (int, float)), \
                f"Prediction {i} probability should be a number"
            assert isinstance(pred['confidence'], (int, float)), \
                f"Prediction {i} confidence should be a number"
            assert 0.0 <= pred['probability'] <= 1.0, \
                f"Prediction {i} probability should be between 0 and 1"
        
        # Verify hotspots
        assert 'hotspots' in result.ai_prediction, \
            "ai_prediction should contain 'hotspots' field"
        hotspots = result.ai_prediction['hotspots']
        assert isinstance(hotspots, list), "hotspots should be a list"
        
        # Verify each hotspot has required fields
        for i, hotspot in enumerate(hotspots):
            assert 'x' in hotspot, f"Hotspot {i} should have 'x' field"
            assert 'y' in hotspot, f"Hotspot {i} should have 'y' field"
            assert 'width' in hotspot, f"Hotspot {i} should have 'width' field"
            assert 'height' in hotspot, f"Hotspot {i} should have 'height' field"
            assert 'confidence' in hotspot, f"Hotspot {i} should have 'confidence' field"
        
        # Verify model metadata
        assert 'model_version' in result.ai_prediction, \
            "ai_prediction should contain 'model_version' field"
        assert 'processing_time' in result.ai_prediction, \
            "ai_prediction should contain 'processing_time' field"
        
        # Verify all symptom data
        assert hasattr(result, 'symptoms'), "Report should have symptoms field"
        if result.symptoms is not None:
            assert isinstance(result.symptoms, dict), "symptoms should be a dict"
            
            # Verify symptom fields
            assert 'location' in result.symptoms, \
                "symptoms should contain 'location' field"
            assert 'sensations' in result.symptoms, \
                "symptoms should contain 'sensations' field"
            assert 'visual_changes' in result.symptoms, \
                "symptoms should contain 'visual_changes' field"
            assert 'duration' in result.symptoms, \
                "symptoms should contain 'duration' field"
            
            # Verify symptom data types
            assert isinstance(result.symptoms['location'], str), \
                "symptom location should be a string"
            assert isinstance(result.symptoms['sensations'], list), \
                "symptom sensations should be a list"
            assert isinstance(result.symptoms['visual_changes'], list), \
                "symptom visual_changes should be a list"
            assert isinstance(result.symptoms['duration'], str), \
                "symptom duration should be a string"
        
        # Verify metadata fields
        assert hasattr(result, 'status'), "Report should have status field"
        assert result.status in ['safe', 'flagged', 'urgent'], \
            f"status should be valid value, got '{result.status}'"
        
        assert hasattr(result, 'risk_level'), "Report should have risk_level field"
        assert result.risk_level in ['low', 'medium', 'high', 'urgent'], \
            f"risk_level should be valid value, got '{result.risk_level}'"
        
        assert hasattr(result, 'body_location'), "Report should have body_location field"
        
        assert hasattr(result, 'created_at'), "Report should have created_at field"
        assert isinstance(result.created_at, datetime), \
            "created_at should be a datetime object"
        
        assert hasattr(result, 'updated_at'), "Report should have updated_at field"
        assert isinstance(result.updated_at, datetime), \
            "updated_at should be a datetime object"
        
        # Verify patient_id matches
        assert hasattr(result, 'patient_id'), "Report should have patient_id field"
        assert result.patient_id == patient_id, \
            "patient_id should match current user"
        
        # Verify report_id matches
        assert hasattr(result, 'id'), "Report should have id field"
        assert result.id == report_id, \
            "Report id should match requested report_id"


# Feature: derman-ai-skin-screening, Property 43: Follow-Up Screening Suggestion
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    months_old=st.integers(min_value=0, max_value=24)
)
def test_followup_screening_suggestion(months_old):
    """
    Property 43: Follow-Up Screening Suggestion
    
    For any report where created_at timestamp is more than 6 months in the past,
    the display should include a follow-up screening suggestion.
    
    This test verifies:
    1. Reports older than 6 months have needs_followup flag set to True
    2. Reports 6 months or newer have needs_followup flag set to False
    3. The follow-up suggestion is based on the created_at timestamp
    4. The calculation correctly handles the 6-month threshold
    
    Validates: Requirements 15.6
    """
    from app.routers.reports import get_patient_reports
    from app.models import MedicalReportListResponse
    
    # Create a patient ID
    patient_id = str(uuid.uuid4())
    
    # Mock current user
    current_user = {
        "id": patient_id,
        "role": "patient"
    }
    
    # Calculate the report date based on months_old
    report_date = datetime.utcnow() - timedelta(days=months_old * 30)
    
    # Create a mock report with the calculated date
    report_data = {
        "id": str(uuid.uuid4()),
        "patient_id": patient_id,
        "image_url": f"https://storage.example.com/images/{uuid.uuid4()}.jpg",
        "ai_prediction": {
            "predictions": [
                {
                    "type": "Melanoma",
                    "probability": 0.45,
                    "confidence": 0.45
                },
                {
                    "type": "Basal Cell Carcinoma",
                    "probability": 0.30,
                    "confidence": 0.30
                },
                {
                    "type": "Benign Keratosis",
                    "probability": 0.25,
                    "confidence": 0.25
                }
            ],
            "hotspots": [],
            "model_version": "1.0.0",
            "processing_time": 2.5
        },
        "symptoms": None,
        "status": "safe",
        "risk_level": "medium",
        "body_location": "arm",
        "consultation_notes": None,
        "created_at": report_date.isoformat(),
        "updated_at": report_date.isoformat()
    }
    
    # Mock supabase response
    with patch('app.routers.reports.supabase') as mock_supabase:
        # Setup mock chain
        mock_table = Mock()
        mock_select = Mock()
        mock_eq = Mock()
        mock_order = Mock()
        
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_eq
        mock_eq.order.return_value = mock_order
        mock_order.execute.return_value = Mock(data=[report_data])
        
        # Call the endpoint
        import asyncio
        result = asyncio.run(get_patient_reports(current_user=current_user))
        
        # Verify we got a result
        assert len(result) == 1, "Should return one report"
        report = result[0]
        
        # Calculate if report should need follow-up (older than 6 months = 180 days)
        days_old = (datetime.utcnow() - report_date).days
        should_need_followup = days_old > 180
        
        # Verify the report has the needs_followup field
        assert hasattr(report, 'needs_followup'), \
            "Report should have needs_followup field for follow-up suggestion"
        
        # Verify the needs_followup flag matches expectation
        if should_need_followup:
            assert report.needs_followup is True, \
                f"Report created {days_old} days ago (> 180 days) should have needs_followup=True"
        else:
            assert report.needs_followup is False, \
                f"Report created {days_old} days ago (<= 180 days) should have needs_followup=False"
        
        # Verify the created_at timestamp is preserved
        assert report.created_at is not None, "Report should have created_at timestamp"
        
        # Additional verification: test the boundary condition explicitly
        if months_old == 6:
            # At exactly 6 months (180 days), should not need follow-up yet
            # Only reports OLDER than 6 months need follow-up
            days_at_6_months = (datetime.utcnow() - report_date).days
            if days_at_6_months <= 180:
                assert report.needs_followup is False, \
                    "Report at exactly 6 months should not need follow-up yet"
        
        if months_old > 6:
            # Reports older than 6 months should definitely need follow-up
            assert report.needs_followup is True, \
                f"Report {months_old} months old should need follow-up"
        
        if months_old < 6:
            # Reports younger than 6 months should not need follow-up
            assert report.needs_followup is False, \
                f"Report {months_old} months old should not need follow-up"
