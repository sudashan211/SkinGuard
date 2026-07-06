"""
Property-Based Tests for AI Analysis Pipeline

Feature: derman-ai-skin-screening
Tests AI-related correctness properties including cancer classification,
lesion detection, and analysis pipeline behavior.

Requirements: 4.3, 4.4, 12.2, 20.1
"""

import pytest
import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings
from hypothesis import HealthCheck
from PIL import Image
from io import BytesIO
import numpy as np

# Add backend to path for imports
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.cancer_classifier import CancerClassifier, CancerPrediction
from app.ai_models import ModelConfig


# Hypothesis strategies for generating test data
@st.composite
def valid_image_data(draw, width=600, height=600):
    """
    Generate valid synthetic image data
    
    Creates images with realistic skin tones to pass NSFW filtering
    """
    # Base skin tone (peachy/beige color)
    base_r = draw(st.integers(min_value=180, max_value=220))
    base_g = draw(st.integers(min_value=150, max_value=190))
    base_b = draw(st.integers(min_value=140, max_value=180))
    
    # Create image with base color
    image_array = np.ones((height, width, 3), dtype=np.uint8)
    image_array[:, :, 0] = base_r
    image_array[:, :, 1] = base_g
    image_array[:, :, 2] = base_b
    
    # Add subtle texture
    noise = np.random.randint(-10, 10, (height, width, 3), dtype=np.int16)
    image_array = np.clip(image_array.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    # Optionally add a lesion
    add_lesion = draw(st.booleans())
    if add_lesion:
        center_x = draw(st.integers(min_value=width//4, max_value=3*width//4))
        center_y = draw(st.integers(min_value=height//4, max_value=3*height//4))
        lesion_size = draw(st.integers(min_value=40, max_value=100))
        
        # Create circular lesion
        y, x = np.ogrid[:height, :width]
        mask = (x - center_x)**2 + (y - center_y)**2 <= lesion_size**2
        
        # Darker color for lesion
        lesion_r = draw(st.integers(min_value=80, max_value=140))
        lesion_g = draw(st.integers(min_value=60, max_value=120))
        lesion_b = draw(st.integers(min_value=50, max_value=110))
        
        image_array[mask, 0] = lesion_r
        image_array[mask, 1] = lesion_g
        image_array[mask, 2] = lesion_b
    
    # Convert to PIL Image
    pil_image = Image.fromarray(image_array, mode='RGB')
    
    # Convert to bytes
    buffer = BytesIO()
    pil_image.save(buffer, format='JPEG', quality=95)
    buffer.seek(0)
    
    return buffer.read()


@pytest.fixture(scope="module")
def cancer_classifier():
    """Create cancer classifier instance for tests"""
    return CancerClassifier()


# Feature: derman-ai-skin-screening, Property 11: Cancer Classification Completeness
@settings(
    max_examples=10,  # Reduced for faster testing with large models
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=60000  # 60 second timeout per example (models are slow)
)
@given(image_data=valid_image_data())
def test_cancer_classification_completeness(cancer_classifier, image_data):
    """
    Property 11: Cancer Classification Completeness
    
    For any successful AI classification, the returned predictions should contain
    exactly 7 cancer types, each with a probability score between 0 and 1,
    and all probabilities should sum to approximately 1.0.
    
    Validates: Requirements 4.3
    """
    # Classify the image
    predictions = cancer_classifier.classify_cancer(image_data)
    
    # Check 1: Exactly 7 cancer types
    assert len(predictions) == 7, \
        f"Expected 7 cancer types, got {len(predictions)}"
    
    # Check 2: All predictions are CancerPrediction objects
    assert all(isinstance(p, CancerPrediction) for p in predictions), \
        "All predictions should be CancerPrediction objects"
    
    # Check 3: All cancer types are present
    config = ModelConfig()
    predicted_types = {p.type for p in predictions}
    expected_types = set(config.CANCER_TYPES)
    assert predicted_types == expected_types, \
        f"Missing cancer types: {expected_types - predicted_types}"
    
    # Check 4: All probabilities are in valid range [0, 1]
    for pred in predictions:
        assert 0.0 <= pred.probability <= 1.0, \
            f"Probability {pred.probability} for {pred.type} is out of range [0, 1]"
    
    # Check 5: Probabilities sum to approximately 1.0
    total_prob = sum(p.probability for p in predictions)
    assert 0.99 <= total_prob <= 1.01, \
        f"Probabilities sum to {total_prob:.4f}, expected ~1.0"
    
    # Check 6: Predictions are sorted by probability (highest first)
    probabilities = [p.probability for p in predictions]
    assert probabilities == sorted(probabilities, reverse=True), \
        "Predictions should be sorted by probability (highest first)"
    
    # Check 7: Each prediction has a confidence score
    for pred in predictions:
        assert hasattr(pred, 'confidence'), \
            f"Prediction for {pred.type} missing confidence score"
        assert 0.0 <= pred.confidence <= 1.0, \
            f"Confidence {pred.confidence} for {pred.type} is out of range [0, 1]"


# Additional helper test (not a property test, but useful for validation)
def test_cancer_types_match_config():
    """
    Verify that the cancer classifier uses the correct cancer types
    from ModelConfig
    """
    config = ModelConfig()
    
    # Expected 7 cancer types
    assert len(config.CANCER_TYPES) == 7, \
        f"Expected 7 cancer types in config, got {len(config.CANCER_TYPES)}"
    
    # All types should be non-empty strings
    assert all(isinstance(t, str) and len(t) > 0 for t in config.CANCER_TYPES), \
        "All cancer types should be non-empty strings"
    
    # No duplicates
    assert len(config.CANCER_TYPES) == len(set(config.CANCER_TYPES)), \
        "Cancer types should not contain duplicates"



# Feature: derman-ai-skin-screening, Property 12: AI Analysis Persistence
@settings(
    max_examples=1,  # Minimal for debugging
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None  # No deadline for debugging
)
@given(image_data=valid_image_data())
def test_ai_analysis_persistence(cancer_classifier, image_data):
    """
    Property 12: AI Analysis Persistence
    
    For any completed AI analysis, storing the results then retrieving the
    medical report should return the same prediction data in JSONB format.
    
    This test verifies:
    1. AI analysis produces valid results
    2. Results can be converted to JSONB format
    3. JSONB format preserves all prediction data
    4. Round-trip conversion maintains data integrity
    
    Validates: Requirements 4.4, 12.2
    """
    import json
    from app.analysis_pipeline import AnalysisResult
    from app.lesion_detector import LesionDetector
    
    # Create pipeline components
    lesion_detector = LesionDetector()
    
    # Perform AI analysis
    predictions = cancer_classifier.classify_cancer(image_data)
    hotspots = lesion_detector.detect_lesions(image_data)
    
    # Create analysis result (simulating what the pipeline does)
    result = AnalysisResult(
        hotspots=hotspots,
        predictions=predictions,
        risk_level=cancer_classifier.get_risk_level(predictions),
        quality_metrics={"resolution": (600, 600), "blur_score": 100.0, "brightness_score": 0.5},
        nsfw_scores={"nsfw_score": 0.1, "non_skin_score": 0.2, "safe_score": 0.7},
        processing_times={"total": 1.5, "ai_total": 1.0}
    )
    
    # Convert to JSONB format (what gets stored in database)
    jsonb_data = result.to_jsonb()
    
    # Verify JSONB format is valid JSON
    json_string = json.dumps(jsonb_data)
    assert json_string is not None, "JSONB data should be serializable to JSON"
    
    # Parse back from JSON (simulating database retrieval)
    retrieved_data = json.loads(json_string)
    
    # Verify all required fields are present in JSONB
    assert "predictions" in retrieved_data, "JSONB should contain predictions"
    assert "hotspots" in retrieved_data, "JSONB should contain hotspots"
    assert "model_version" in retrieved_data, "JSONB should contain model_version"
    assert "processing_time" in retrieved_data, "JSONB should contain processing_time"
    
    # Verify predictions data integrity
    assert len(retrieved_data["predictions"]) == len(predictions), \
        "Retrieved predictions count should match original"
    
    for i, pred in enumerate(predictions):
        retrieved_pred = retrieved_data["predictions"][i]
        assert retrieved_pred["type"] == pred.type, \
            f"Prediction type should be preserved (expected {pred.type}, got {retrieved_pred['type']})"
        assert abs(retrieved_pred["probability"] - pred.probability) < 0.0001, \
            f"Prediction probability should be preserved (expected {pred.probability}, got {retrieved_pred['probability']})"
        assert retrieved_pred["confidence"] == pred.confidence, \
            f"Prediction confidence should be preserved"
    
    # Verify hotspots data integrity
    assert len(retrieved_data["hotspots"]) == len(hotspots), \
        "Retrieved hotspots count should match original"
    
    for i, hotspot in enumerate(hotspots):
        retrieved_hotspot = retrieved_data["hotspots"][i]
        assert retrieved_hotspot["x"] == hotspot.x, "Hotspot x coordinate should be preserved"
        assert retrieved_hotspot["y"] == hotspot.y, "Hotspot y coordinate should be preserved"
        assert retrieved_hotspot["width"] == hotspot.width, "Hotspot width should be preserved"
        assert retrieved_hotspot["height"] == hotspot.height, "Hotspot height should be preserved"
        assert abs(retrieved_hotspot["confidence"] - hotspot.confidence) < 0.0001, \
            "Hotspot confidence should be preserved"
    
    # Verify metadata is preserved
    assert retrieved_data["model_version"] == result.model_version, \
        "Model version should be preserved"
    assert retrieved_data["processing_time"] == result.processing_times.get("total", 0.0), \
        "Processing time should be preserved"
    
    # Verify round-trip conversion maintains data integrity
    # Convert back to dict and compare with original
    original_dict = result.to_jsonb()
    assert retrieved_data == original_dict, \
        "Round-trip conversion should maintain exact data integrity"


# Feature: derman-ai-skin-screening, Property 63: AI Processing Time Logging
@settings(
    max_examples=1,  # Minimal for debugging
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None  # No deadline for debugging
)
@given(image_data=valid_image_data())
def test_ai_processing_time_logging(image_data):
    """
    Property 63: AI Processing Time Logging
    
    For any AI analysis, the system should log separate processing times for
    NSFW Gatekeeper and Medical_AI (Swin + EfficientNet) stages.
    
    This test verifies:
    1. Processing times are recorded for each pipeline stage
    2. NSFW filtering time is logged separately
    3. Lesion detection time is logged separately
    4. Cancer classification time is logged separately
    5. Total AI processing time is calculated correctly
    6. All times are positive numbers
    
    Validates: Requirements 20.1
    """
    import asyncio
    from app.analysis_pipeline import AnalysisPipeline
    
    # Create pipeline
    pipeline = AnalysisPipeline()
    
    # Process image through complete pipeline
    result = asyncio.run(pipeline.process_image(image_data, patient_id="test-patient"))
    
    # Verify processing_times dictionary exists
    assert hasattr(result, 'processing_times'), \
        "Analysis result should have processing_times attribute"
    assert isinstance(result.processing_times, dict), \
        "processing_times should be a dictionary"
    
    # Verify all required timing stages are present
    required_stages = [
        "quality_validation",
        "nsfw_filtering",
        "lesion_detection",
        "cancer_classification",
        "total",
        "ai_total"
    ]
    
    for stage in required_stages:
        assert stage in result.processing_times, \
            f"Processing times should include '{stage}' stage"
    
    # Verify NSFW Gatekeeper time is logged separately (Requirement 20.1)
    nsfw_time = result.processing_times["nsfw_filtering"]
    assert isinstance(nsfw_time, (int, float)), \
        "NSFW filtering time should be a number"
    assert nsfw_time >= 0, \
        "NSFW filtering time should be non-negative"
    
    # Verify Medical_AI stages are logged separately (Requirement 20.1)
    lesion_time = result.processing_times["lesion_detection"]
    assert isinstance(lesion_time, (int, float)), \
        "Lesion detection time should be a number"
    assert lesion_time >= 0, \
        "Lesion detection time should be non-negative"
    
    classification_time = result.processing_times["cancer_classification"]
    assert isinstance(classification_time, (int, float)), \
        "Cancer classification time should be a number"
    assert classification_time >= 0, \
        "Cancer classification time should be non-negative"
    
    # Verify quality validation time is logged
    quality_time = result.processing_times["quality_validation"]
    assert isinstance(quality_time, (int, float)), \
        "Quality validation time should be a number"
    assert quality_time >= 0, \
        "Quality validation time should be non-negative"
    
    # Verify total AI processing time is calculated correctly
    ai_total = result.processing_times["ai_total"]
    expected_ai_total = lesion_time + classification_time
    assert abs(ai_total - expected_ai_total) < 0.001, \
        f"AI total time should equal lesion + classification time (expected {expected_ai_total}, got {ai_total})"
    
    # Verify total processing time includes all stages
    total_time = result.processing_times["total"]
    assert isinstance(total_time, (int, float)), \
        "Total processing time should be a number"
    assert total_time >= 0, \
        "Total processing time should be non-negative"
    
    # Total time should be at least the sum of all individual stages
    sum_of_stages = (
        quality_time +
        nsfw_time +
        lesion_time +
        classification_time
    )
    assert total_time >= sum_of_stages - 0.1, \
        f"Total time ({total_time}) should be at least sum of stages ({sum_of_stages})"
    
    # Verify times are reasonable (not zero for actual processing)
    # At least one of the AI stages should have taken some time
    assert lesion_time > 0 or classification_time > 0, \
        "At least one AI processing stage should have non-zero time"
    
    # Verify the result can be converted to dict with timing info
    result_dict = result.to_dict()
    assert "processing_times" in result_dict, \
        "Result dict should include processing_times"
    assert result_dict["processing_times"] == result.processing_times, \
        "Processing times should be preserved in dict conversion"
    
    # Verify JSONB format includes processing time
    jsonb_data = result.to_jsonb()
    assert "processing_time" in jsonb_data, \
        "JSONB format should include processing_time"
    assert jsonb_data["processing_time"] == total_time, \
        "JSONB processing_time should match total time"
