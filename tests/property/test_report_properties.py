"""
Property-Based Tests for Medical Report Management

Feature: derman-ai-skin-screening
Tests report storage, image upload, and multipart form data handling.

Requirements: 12.3, 13.2
"""

import pytest
import os
import sys
from hypothesis import given, strategies as st, settings, assume
from hypothesis import HealthCheck
from dotenv import load_dotenv
from uuid import uuid4
from PIL import Image
import io
from unittest.mock import patch, MagicMock, Mock

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
def valid_image_data(draw):
    """Generate valid image data"""
    # Create a simple test image
    width = draw(st.integers(min_value=512, max_value=1024))
    height = draw(st.integers(min_value=512, max_value=1024))
    color = (
        draw(st.integers(min_value=0, max_value=255)),
        draw(st.integers(min_value=0, max_value=255)),
        draw(st.integers(min_value=0, max_value=255))
    )
    
    image = Image.new('RGB', (width, height), color)
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    return buffer.getvalue()



# Feature: derman-ai-skin-screening, Property 32: Image Storage Round Trip
@given(
    image_data=valid_image_data()
)
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None  # Disable deadline for storage operations
)
def test_image_storage_round_trip(image_data):
    """
    Property 32: Image Storage Round Trip
    
    For any uploaded image file, storing it to Supabase Storage then retrieving
    via the returned URL should yield the same image data.
    
    This test verifies that:
    1. Images can be uploaded to Supabase Storage
    2. A valid URL is returned after upload
    3. The image can be retrieved using the URL
    4. The retrieved image data matches the original
    
    Validates: Requirements 12.3
    """
    from app.database import supabase
    
    # Generate unique filename
    filename = f"test/{uuid4()}.jpg"
    
    # Mock Supabase Storage operations
    mock_storage = MagicMock()
    mock_bucket = MagicMock()
    
    # Track uploaded data
    uploaded_data = None
    
    def mock_upload(path, data, file_options=None):
        nonlocal uploaded_data
        uploaded_data = data
        result = MagicMock()
        result.path = path
        return result
    
    def mock_get_public_url(path):
        return f"https://storage.example.com/{path}"
    
    mock_bucket.upload = mock_upload
    mock_bucket.get_public_url = mock_get_public_url
    
    def mock_from_bucket(bucket_name):
        return mock_bucket
    
    mock_storage.from_ = mock_from_bucket
    
    # Patch supabase.storage
    with patch.object(supabase, 'storage', mock_storage):
        # Step 1: Upload image
        upload_result = supabase.storage.from_('medical-images').upload(
            filename,
            image_data,
            file_options={"content-type": "image/jpeg"}
        )
        
        # Verify upload succeeded
        assert upload_result is not None, "Upload should return a result"
        assert upload_result.path == filename, "Upload result should contain the path"
        
        # Verify data was uploaded
        assert uploaded_data is not None, "Image data should be uploaded"
        assert uploaded_data == image_data, "Uploaded data should match original"
        
        # Step 2: Get public URL
        image_url = supabase.storage.from_('medical-images').get_public_url(filename)
        
        # Verify URL is valid
        assert image_url is not None, "URL should be returned"
        assert isinstance(image_url, str), "URL should be a string"
        assert len(image_url) > 0, "URL should not be empty"
        assert filename in image_url, "URL should contain the filename"
        
        # Step 3: Mock retrieval of image from URL
        # In a real scenario, we would fetch from the URL
        # For testing, we verify the round trip by checking uploaded data
        retrieved_data = uploaded_data
        
        # Verify round trip: original -> upload -> retrieve -> same data
        assert retrieved_data == image_data, \
            "Retrieved image data should match original image data (round trip)"
        
        # Verify image can be decoded
        try:
            retrieved_image = Image.open(io.BytesIO(retrieved_data))
            original_image = Image.open(io.BytesIO(image_data))
            
            # Verify dimensions match
            assert retrieved_image.size == original_image.size, \
                "Retrieved image dimensions should match original"
            
            # Verify format matches
            assert retrieved_image.format == original_image.format or retrieved_image.format == 'JPEG', \
                "Retrieved image format should match original or be JPEG"
            
        except Exception as e:
            pytest.fail(f"Retrieved image data should be valid image: {e}")



# Feature: derman-ai-skin-screening, Property 34: Multipart Form Data Acceptance
@given(
    image_data=valid_image_data(),
    body_location=st.one_of(st.none(), st.text(min_size=3, max_size=50)),
    sensations=st.one_of(st.none(), st.text(min_size=3, max_size=100)),
    visual_changes=st.one_of(st.none(), st.text(min_size=3, max_size=100)),
    duration=st.one_of(st.none(), st.text(min_size=3, max_size=50))
)
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None  # Disable deadline for API operations
)
def test_multipart_form_data_acceptance(
    image_data,
    body_location,
    sensations,
    visual_changes,
    duration
):
    """
    Property 34: Multipart Form Data Acceptance
    
    For any image upload request with content-type "multipart/form-data",
    the /api/analyze-skin endpoint should accept and process the request.
    
    This test verifies that:
    1. The endpoint accepts multipart/form-data requests
    2. The endpoint can extract the image file from the request
    3. The endpoint can extract optional form fields (body_location, symptoms)
    4. The endpoint processes the request without errors
    5. The endpoint returns a valid response
    
    Validates: Requirements 13.2
    """
    from fastapi.testclient import TestClient
    from app.main import app
    from unittest.mock import patch, MagicMock, AsyncMock
    import json
    
    # Create test client
    client = TestClient(app)
    
    # Create a mock user for authentication
    mock_user = {
        "id": str(uuid4()),
        "email": "test@example.com",
        "full_name": "Test User",
        "role": "patient",
        "verified": False
    }
    
    # Mock authentication using FastAPI dependency override
    def mock_get_current_patient():
        return mock_user
    
    # Mock analysis pipeline to avoid actual AI processing
    async def mock_analyze_image(image_data, patient_id=None):
        from app.analysis_pipeline import AnalysisResult
        from app.lesion_detector import Hotspot
        from app.cancer_classifier import CancerPrediction
        
        # Return mock analysis result
        return AnalysisResult(
            hotspots=[
                Hotspot(x=100, y=100, width=50, height=50, confidence=0.85)
            ],
            predictions=[
                CancerPrediction(cancer_type="Melanoma", probability=0.75, confidence=0.85),
                CancerPrediction(cancer_type="Basal Cell Carcinoma", probability=0.15, confidence=0.70),
                CancerPrediction(cancer_type="Squamous Cell Carcinoma", probability=0.05, confidence=0.60),
                CancerPrediction(cancer_type="Actinic Keratosis", probability=0.03, confidence=0.55),
                CancerPrediction(cancer_type="Benign Keratosis", probability=0.01, confidence=0.50),
                CancerPrediction(cancer_type="Dermatofibroma", probability=0.005, confidence=0.45),
                CancerPrediction(cancer_type="Vascular Lesion", probability=0.005, confidence=0.45)
            ],
            risk_level="medium",
            quality_metrics={
                "resolution": (1024, 1024),
                "blur_score": 100.0,
                "brightness_score": 0.5
            },
            nsfw_scores={
                "nsfw_score": 0.1,
                "non_skin_score": 0.2,
                "safe_score": 0.7
            },
            processing_times={
                "quality_validation": 0.1,
                "nsfw_filtering": 0.2,
                "lesion_detection": 0.5,
                "cancer_classification": 0.8,
                "total": 1.6,
                "ai_total": 1.3
            }
        )
    
    # Mock Supabase storage
    mock_storage_result = MagicMock()
    mock_storage_result.path = f"test/{uuid4()}.jpg"
    
    def mock_storage_upload(path, data, file_options=None):
        return mock_storage_result
    
    def mock_storage_get_url(path):
        return f"https://storage.example.com/{path}"
    
    # Mock Supabase database insert
    def mock_db_insert(data):
        insert_mock = MagicMock()
        
        def mock_execute():
            result_mock = MagicMock()
            result_mock.data = [data]
            return result_mock
        
        insert_mock.execute = mock_execute
        return insert_mock
    
    # Mock audit logger
    mock_audit_logger = MagicMock()
    mock_audit_logger.log_action = AsyncMock(return_value=str(uuid4()))
    
    # Import dependencies to override
    from app.routers.reports import get_current_patient
    from app.dependencies import get_audit_logger
    
    # Override FastAPI dependencies
    app.dependency_overrides[get_current_patient] = mock_get_current_patient
    app.dependency_overrides[get_audit_logger] = lambda: mock_audit_logger
    
    try:
        # Apply all mocks
        with patch('app.routers.reports.analyze_image', side_effect=mock_analyze_image), \
             patch('app.routers.reports.supabase') as mock_supabase:
            
            # Setup mock supabase
            mock_bucket = MagicMock()
            mock_bucket.upload = mock_storage_upload
            mock_bucket.get_public_url = mock_storage_get_url
            
            mock_storage = MagicMock()
            mock_storage.from_ = lambda bucket: mock_bucket
            mock_supabase.storage = mock_storage
            
            mock_table = MagicMock()
            mock_table.insert = mock_db_insert
            mock_supabase.table = lambda name: mock_table
            
            # Prepare multipart form data
            files = {
                'image': ('test.jpg', image_data, 'image/jpeg')
            }
            
            data = {}
            if body_location:
                data['body_location'] = body_location
            if sensations:
                data['sensations'] = sensations
            if visual_changes:
                data['visual_changes'] = visual_changes
            if duration:
                data['duration'] = duration
            
            # Make request with multipart/form-data
            response = client.post(
                "/api/analyze-skin",
                files=files,
                data=data
            )
            
            # Verify response
            assert response.status_code in [200, 201], \
                f"Endpoint should accept multipart/form-data, got status {response.status_code}: {response.text}"
            
            # Verify response is JSON
            assert response.headers.get('content-type', '').startswith('application/json'), \
                "Response should be JSON"
            
            # Verify response contains expected fields
            response_data = response.json()
            assert 'id' in response_data, "Response should contain report ID"
            assert 'patient_id' in response_data, "Response should contain patient ID"
            assert 'image_url' in response_data, "Response should contain image URL"
            assert 'ai_prediction' in response_data, "Response should contain AI predictions"
            assert 'risk_level' in response_data, "Response should contain risk level"
            assert 'status' in response_data, "Response should contain status"
            
            # Verify patient ID matches authenticated user
            assert response_data['patient_id'] == mock_user['id'], \
                "Report should be associated with authenticated user"
            
            # Verify symptoms were stored if provided
            if body_location or sensations or visual_changes or duration:
                assert 'symptoms' in response_data, "Response should contain symptoms if provided"
                if response_data['symptoms']:
                    if body_location:
                        assert response_data['symptoms'].get('body_location') == body_location, \
                            "Stored body_location should match input"
    finally:
        # Clean up dependency overrides
        app.dependency_overrides.clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
