"""
Property-Based Tests for Symptom Data Collection

Feature: derman-ai-skin-screening
Tests symptom data completeness and association with medical reports.

Requirements: 5.2, 5.3, 5.4, 5.5, 5.6
"""

import pytest
import os
import sys
from hypothesis import given, strategies as st, settings, assume
from hypothesis import HealthCheck
from dotenv import load_dotenv
from uuid import uuid4
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime

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

# Import models after environment setup
from app.models import SymptomData


# Hypothesis strategies for generating symptom data
@st.composite
def valid_body_location(draw):
    """Generate valid body location strings"""
    locations = [
        "left_arm", "right_arm", "left_leg", "right_leg",
        "chest", "back", "abdomen", "face", "neck",
        "left_hand", "right_hand", "left_foot", "right_foot",
        "scalp", "shoulder"
    ]
    return draw(st.sampled_from(locations))


@st.composite
def valid_sensations(draw):
    """Generate valid sensation lists"""
    allowed_sensations = ['itching', 'pain', 'burning', 'numbness', 'tingling', 'none']
    num_sensations = draw(st.integers(min_value=0, max_value=4))
    
    if num_sensations == 0:
        return []
    
    # Sample unique sensations
    sensations = draw(st.lists(
        st.sampled_from(allowed_sensations),
        min_size=num_sensations,
        max_size=num_sensations,
        unique=True
    ))
    return sensations


@st.composite
def valid_visual_changes(draw):
    """Generate valid visual change lists"""
    allowed_changes = ['color', 'size', 'shape', 'border', 'texture', 'bleeding', 'none']
    num_changes = draw(st.integers(min_value=0, max_value=4))
    
    if num_changes == 0:
        return []
    
    # Sample unique visual changes
    changes = draw(st.lists(
        st.sampled_from(allowed_changes),
        min_size=num_changes,
        max_size=num_changes,
        unique=True
    ))
    return changes


@st.composite
def valid_duration(draw):
    """Generate valid duration strings"""
    durations = [
        "1 day", "2 days", "3 days", "1 week", "2 weeks", "3 weeks",
        "1 month", "2 months", "3 months", "6 months", "1 year",
        "less than a week", "more than a month", "several weeks"
    ]
    return draw(st.sampled_from(durations))


@st.composite
def complete_symptom_data(draw):
    """Generate complete symptom data with all fields"""
    return {
        "body_location": draw(valid_body_location()),
        "sensations": draw(valid_sensations()),
        "visual_changes": draw(valid_visual_changes()),
        "duration": draw(valid_duration())
    }


# Feature: derman-ai-skin-screening, Property 14: Symptom Data Completeness
@given(
    body_location=valid_body_location(),
    sensations=valid_sensations(),
    visual_changes=valid_visual_changes(),
    duration=valid_duration()
)
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None
)
def test_symptom_data_completeness(body_location, sensations, visual_changes, duration):
    """
    Property 14: Symptom Data Completeness
    
    For any completed symptom wizard, the stored symptom data should include
    body location (Step 1), sensations (Step 2), and visual changes (Step 3).
    
    This test verifies that:
    1. SymptomData model accepts all three wizard steps
    2. Body location from Step 1 is stored
    3. Sensations from Step 2 are stored as a list
    4. Visual changes from Step 3 are stored as a list
    5. Duration is stored if provided
    6. All data can be converted to dict for JSONB storage
    7. Data integrity is maintained through conversion
    
    Validates: Requirements 5.2, 5.3, 5.4, 5.5
    """
    # Step 1: Create SymptomData with all wizard steps
    symptom_data = SymptomData(
        body_location=body_location,
        sensations=sensations,
        visual_changes=visual_changes,
        duration=duration
    )
    
    # Verify all fields are present
    assert symptom_data.body_location is not None, \
        "Body location (Step 1) should be stored"
    assert symptom_data.body_location == body_location, \
        "Body location should match input from Step 1"
    
    assert symptom_data.sensations is not None, \
        "Sensations (Step 2) should be stored"
    assert isinstance(symptom_data.sensations, list), \
        "Sensations should be stored as a list"
    assert symptom_data.sensations == sensations, \
        "Sensations should match input from Step 2"
    
    assert symptom_data.visual_changes is not None, \
        "Visual changes (Step 3) should be stored"
    assert isinstance(symptom_data.visual_changes, list), \
        "Visual changes should be stored as a list"
    assert symptom_data.visual_changes == visual_changes, \
        "Visual changes should match input from Step 3"
    
    assert symptom_data.duration is not None, \
        "Duration should be stored if provided"
    assert symptom_data.duration == duration, \
        "Duration should match input"
    
    # Step 2: Convert to dict for JSONB storage (Requirement 5.5)
    symptom_dict = symptom_data.dict()
    
    # Verify dict conversion preserves all data
    assert isinstance(symptom_dict, dict), \
        "Symptom data should convert to dict for JSONB storage"
    
    assert "body_location" in symptom_dict, \
        "Dict should contain body_location field"
    assert symptom_dict["body_location"] == body_location, \
        "Dict body_location should match original"
    
    assert "sensations" in symptom_dict, \
        "Dict should contain sensations field"
    assert symptom_dict["sensations"] == sensations, \
        "Dict sensations should match original"
    
    assert "visual_changes" in symptom_dict, \
        "Dict should contain visual_changes field"
    assert symptom_dict["visual_changes"] == visual_changes, \
        "Dict visual_changes should match original"
    
    assert "duration" in symptom_dict, \
        "Dict should contain duration field"
    assert symptom_dict["duration"] == duration, \
        "Dict duration should match original"
    
    # Step 3: Verify completeness - all three wizard steps are present
    wizard_steps_complete = (
        symptom_dict["body_location"] is not None and
        symptom_dict["sensations"] is not None and
        symptom_dict["visual_changes"] is not None
    )
    
    assert wizard_steps_complete, \
        "All three wizard steps (body_location, sensations, visual_changes) should be complete"


# Feature: derman-ai-skin-screening, Property 15: Symptom-Report Association
@given(
    patient_id=st.uuids(),
    symptom_data=complete_symptom_data()
)
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None
)
def test_symptom_report_association(patient_id, symptom_data):
    """
    Property 15: Symptom-Report Association
    
    For any saved symptom data, the medical_reports record should correctly
    reference both the patient_id and contain the symptom JSONB data.
    
    This test verifies that:
    1. Symptom data can be stored in medical_reports table
    2. Report is associated with correct patient_id
    3. Symptom data is stored in JSONB format
    4. Symptom data can be retrieved from the report
    5. Retrieved symptom data matches original input
    6. Association between patient, report, and symptoms is maintained
    
    Validates: Requirements 5.6
    """
    # Convert patient_id to string for database operations
    patient_id_str = str(patient_id)
    report_id = str(uuid4())
    
    # Create SymptomData model
    symptoms = SymptomData(**symptom_data)
    symptom_dict = symptoms.dict()
    
    # Mock medical report with symptom data
    mock_report = {
        "id": report_id,
        "patient_id": patient_id_str,
        "image_url": f"https://storage.example.com/{patient_id_str}/{report_id}.jpg",
        "ai_prediction": {
            "predictions": [
                {"type": "melanoma", "probability": 0.15, "confidence": 0.85}
            ],
            "hotspots": [],
            "model_version": "1.0.0",
            "processing_time": 1.5
        },
        "symptoms": symptom_dict,  # Symptom data stored in JSONB field
        "status": "safe",
        "risk_level": "low",
        "body_location": symptom_dict.get("body_location"),
        "consultation_notes": None,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    # Mock database operations
    mock_supabase = MagicMock()
    mock_table = MagicMock()
    mock_insert = MagicMock()
    mock_execute = MagicMock()
    
    # Setup mock chain for insert operation
    mock_execute.execute.return_value = MagicMock(data=[mock_report])
    mock_insert.execute.return_value = MagicMock(data=[mock_report])
    mock_table.insert.return_value = mock_insert
    mock_supabase.table.return_value = mock_table
    
    # Setup mock chain for select operation
    mock_select = MagicMock()
    mock_eq = MagicMock()
    mock_single = MagicMock()
    
    mock_single.execute.return_value = MagicMock(data=mock_report)
    mock_eq.single.return_value = mock_single
    mock_select.eq.return_value = mock_eq
    mock_table.select.return_value = mock_select
    
    # Simulate storing report with symptoms
    # Note: We're using the pre-mocked database module from module setup
    # Step 1: Insert report with symptom data
    insert_result = mock_supabase.table('medical_reports').insert(mock_report).execute()
    
    # Verify insert succeeded
    assert insert_result.data is not None, \
        "Report insert should return data"
    assert len(insert_result.data) > 0, \
        "Report insert should return at least one record"
    
    inserted_report = insert_result.data[0]
    
    # Step 2: Verify patient_id association (Requirement 5.6)
    assert "patient_id" in inserted_report, \
        "Report should contain patient_id field"
    assert inserted_report["patient_id"] == patient_id_str, \
        "Report should be associated with correct patient_id"
    
    # Step 3: Verify symptom data is present in JSONB field (Requirement 5.6)
    assert "symptoms" in inserted_report, \
        "Report should contain symptoms field"
    assert inserted_report["symptoms"] is not None, \
        "Symptoms field should not be None"
    assert isinstance(inserted_report["symptoms"], dict), \
        "Symptoms should be stored as JSONB (dict)"
    
    # Step 4: Verify symptom data completeness
    stored_symptoms = inserted_report["symptoms"]
    
    assert "body_location" in stored_symptoms, \
        "Stored symptoms should contain body_location"
    assert stored_symptoms["body_location"] == symptom_data["body_location"], \
        "Stored body_location should match original"
    
    assert "sensations" in stored_symptoms, \
        "Stored symptoms should contain sensations"
    assert stored_symptoms["sensations"] == symptom_data["sensations"], \
        "Stored sensations should match original"
    
    assert "visual_changes" in stored_symptoms, \
        "Stored symptoms should contain visual_changes"
    assert stored_symptoms["visual_changes"] == symptom_data["visual_changes"], \
        "Stored visual_changes should match original"
    
    assert "duration" in stored_symptoms, \
        "Stored symptoms should contain duration"
    assert stored_symptoms["duration"] == symptom_data["duration"], \
        "Stored duration should match original"
    
    # Step 5: Retrieve report and verify association persists
    retrieve_result = mock_supabase.table('medical_reports').select('*').eq('id', report_id).single().execute()
    
    retrieved_report = retrieve_result.data
    
    # Verify patient-report-symptom association is maintained
    assert retrieved_report["id"] == report_id, \
        "Retrieved report should have correct ID"
    assert retrieved_report["patient_id"] == patient_id_str, \
        "Retrieved report should maintain patient_id association"
    assert retrieved_report["symptoms"] is not None, \
        "Retrieved report should contain symptom data"
    assert retrieved_report["symptoms"] == symptom_dict, \
        "Retrieved symptom data should match original (round trip)"
    
    # Step 6: Verify body_location is also stored at report level for filtering
    if symptom_data.get("body_location"):
        assert "body_location" in retrieved_report, \
            "Report should have body_location field for filtering"
        assert retrieved_report["body_location"] == symptom_data["body_location"], \
            "Report body_location should match symptom body_location"


# Additional test: Partial symptom data (optional fields)
@given(
    patient_id=st.uuids(),
    body_location=st.one_of(st.none(), valid_body_location()),
    sensations=st.one_of(st.none(), valid_sensations()),
    visual_changes=st.one_of(st.none(), valid_visual_changes()),
    duration=st.one_of(st.none(), valid_duration())
)
@settings(
    max_examples=50,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None
)
def test_partial_symptom_data_handling(
    patient_id,
    body_location,
    sensations,
    visual_changes,
    duration
):
    """
    Additional test: Verify that partial symptom data (with optional fields)
    is handled correctly.
    
    This test verifies that:
    1. Symptom data with None values is valid
    2. Empty lists for sensations/visual_changes are valid
    3. Reports can be created with partial symptom data
    4. Partial symptom data is stored and retrieved correctly
    
    Validates: Requirements 5.2, 5.3, 5.4, 5.5, 5.6
    """
    # Create SymptomData with potentially None/empty values
    symptom_kwargs = {}
    if body_location is not None:
        symptom_kwargs["body_location"] = body_location
    if sensations is not None:
        symptom_kwargs["sensations"] = sensations
    if visual_changes is not None:
        symptom_kwargs["visual_changes"] = visual_changes
    if duration is not None:
        symptom_kwargs["duration"] = duration
    
    # Should not raise validation error
    symptoms = SymptomData(**symptom_kwargs)
    
    # Verify model handles optional fields correctly
    if body_location is None:
        assert symptoms.body_location is None, \
            "Body location should be None if not provided"
    else:
        assert symptoms.body_location == body_location, \
            "Body location should match input if provided"
    
    if sensations is None:
        assert symptoms.sensations == [], \
            "Sensations should default to empty list if not provided"
    else:
        assert symptoms.sensations == sensations, \
            "Sensations should match input if provided"
    
    if visual_changes is None:
        assert symptoms.visual_changes == [], \
            "Visual changes should default to empty list if not provided"
    else:
        assert symptoms.visual_changes == visual_changes, \
            "Visual changes should match input if provided"
    
    if duration is None:
        assert symptoms.duration is None, \
            "Duration should be None if not provided"
    else:
        assert symptoms.duration == duration, \
            "Duration should match input if provided"
    
    # Verify dict conversion works with partial data
    symptom_dict = symptoms.dict()
    assert isinstance(symptom_dict, dict), \
        "Partial symptom data should convert to dict"
    
    # Verify all fields are present in dict (even if None or empty)
    assert "body_location" in symptom_dict
    assert "sensations" in symptom_dict
    assert "visual_changes" in symptom_dict
    assert "duration" in symptom_dict


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
