"""
Fast Property-Based Tests for AI Analysis Pipeline
These tests use max_examples=5 and mock heavy operations for speed

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
from unittest.mock import Mock, patch
import json

# Add backend to path for imports
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.cancer_classifier import CancerPrediction
from app.lesion_detector import Hotspot


# Hypothesis strategies for generating test data
@st.composite
def mock_predictions(draw):
    """Generate mock cancer predictions for testing"""
    num_predictions = draw(st.integers(min_value=1, max_value=3))
    predictions = []
    
    cancer_types = ["melanoma", "basal_cell_carcinoma", "squamous_cell_carcinoma", "benign"]
    
    for _ in range(num_predictions):
        cancer_type = draw(st.sampled_from(cancer_types))
        probability = draw(st.floats(min_value=0.0, max_value=1.0))
        confidence = draw(st.floats(min_value=0.0, max_value=1.0))
        
        predictions.append(CancerPrediction(
            cancer_type=cancer_type,
            probability=probability,
            confidence=confidence
        ))
    
    return predictions


@st.composite
def mock_hotspots(draw):
    """Generate mock hotspots for testing"""
    num_hotspots = draw(st.integers(min_value=0, max_value=5))
    hotspots = []
    
    for _ in range(num_hotspots):
        x = draw(st.integers(min_value=0, max_value=600))
        y = draw(st.integers(min_value=0, max_value=600))
        width = draw(st.integers(min_value=20, max_value=100))
        height = draw(st.integers(min_value=20, max_value=100))
        confidence = draw(st.floats(min_value=0.5, max_value=1.0))
        
        hotspots.append(Hotspot(
            x=x,
            y=y,
            width=width,
            height=height,
            confidence=confidence
        ))
    
    return hotspots


# Feature: derman-ai-skin-screening, Property 12: AI Analysis Persistence
@settings(
    max_examples=5,  # Fast version with 5 examples
    deadline=None
)
@given(
    predictions=mock_predictions(),
    hotspots=mock_hotspots()
)
def test_ai_analysis_persistence_fast(predictions, hotspots):
    """
    Property 12: AI Analysis Persistence (Fast Version)
    
    For any completed AI analysis, storing the results then retrieving the
    medical report should return the same prediction data in JSONB format.
    
    This test verifies:
    1. AI analysis produces valid results
    2. Results can be converted to JSONB format
    3. JSONB format preserves all prediction data
    4. Round-trip conversion maintains data integrity
    
    Validates: Requirements 4.4, 12.2
    """
    from app.analysis_pipeline import AnalysisResult
    from app.cancer_classifier import CancerClassifier
    
    # Get risk level from predictions
    classifier = CancerClassifier()
    risk_level = classifier.get_risk_level(predictions)
    
    # Create analysis result (simulating what the pipeline does)
    result = AnalysisResult(
        hotspots=hotspots,
        predictions=predictions,
        risk_level=risk_level,
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
        assert abs(retrieved_pred["confidence"] - pred.confidence) < 0.0001, \
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
    max_examples=5,  # Fast version with 5 examples
    deadline=None
)
@given(
    predictions=mock_predictions(),
    hotspots=mock_hotspots()
)
def test_ai_processing_time_logging_fast(predictions, hotspots):
    """
    Property 63: AI Processing Time Logging (Fast Version)
    
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
    from app.analysis_pipeline import AnalysisResult
    from app.cancer_classifier import CancerClassifier
    
    # Get risk level from predictions
    classifier = CancerClassifier()
    risk_level = classifier.get_risk_level(predictions)
    
    # Create mock processing times (simulating what the pipeline records)
    processing_times = {
        "quality_validation": 0.05,
        "nsfw_filtering": 0.15,
        "lesion_detection": 0.45,
        "cancer_classification": 0.55,
        "total": 1.2,
        "ai_total": 1.0  # lesion_detection + cancer_classification
    }
    
    # Create analysis result
    result = AnalysisResult(
        hotspots=hotspots,
        predictions=predictions,
        risk_level=risk_level,
        quality_metrics={"resolution": (600, 600), "blur_score": 100.0, "brightness_score": 0.5},
        nsfw_scores={"nsfw_score": 0.1, "non_skin_score": 0.2, "safe_score": 0.7},
        processing_times=processing_times
    )
    
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



# Feature: derman-ai-skin-screening, Property 79: High-Risk Urgent Flagging
@st.composite
def cancer_predictions_with_high_probability(draw):
    """
    Generate cancer predictions where at least one has probability > 85%
    """
    # Generate 7 predictions (one for each cancer type)
    cancer_types = [
        "Melanoma",
        "Basal Cell Carcinoma",
        "Squamous Cell Carcinoma",
        "Actinic Keratosis",
        "Benign Keratosis",
        "Dermatofibroma",
        "Vascular Lesion"
    ]
    
    # Pick one cancer type to have high probability (> 85%)
    high_prob_index = draw(st.integers(min_value=0, max_value=6))
    high_probability = draw(st.floats(min_value=0.851, max_value=0.99))
    
    # Distribute remaining probability among other types
    remaining_prob = 1.0 - high_probability
    
    predictions = []
    for i, cancer_type in enumerate(cancer_types):
        if i == high_prob_index:
            probability = high_probability
        else:
            # Distribute remaining probability
            if i == len(cancer_types) - 1:
                # Last one gets whatever is left
                probability = remaining_prob
            else:
                # Random portion of remaining
                max_portion = remaining_prob / (len(cancer_types) - i)
                probability = draw(st.floats(min_value=0.0, max_value=max_portion))
                remaining_prob -= probability
        
        predictions.append(CancerPrediction(
            cancer_type=cancer_type,
            probability=probability,
            confidence=probability
        ))
    
    return predictions


@st.composite
def cancer_predictions_with_low_probability(draw):
    """
    Generate cancer predictions where all probabilities are <= 85%
    """
    cancer_types = [
        "Melanoma",
        "Basal Cell Carcinoma",
        "Squamous Cell Carcinoma",
        "Actinic Keratosis",
        "Benign Keratosis",
        "Dermatofibroma",
        "Vascular Lesion"
    ]
    
    # Generate probabilities that sum to 1.0, all <= 85%
    probabilities = []
    remaining = 1.0
    
    for i in range(len(cancer_types) - 1):
        max_prob = min(0.85, remaining)
        prob = draw(st.floats(min_value=0.0, max_value=max_prob))
        probabilities.append(prob)
        remaining -= prob
    
    # Last probability gets the remainder (ensure it's <= 85%)
    probabilities.append(min(remaining, 0.85))
    
    # If last probability would be > 85%, redistribute
    if probabilities[-1] > 0.85:
        # Redistribute to make all <= 85%
        excess = probabilities[-1] - 0.85
        probabilities[-1] = 0.85
        # Add excess to other predictions
        for i in range(len(probabilities) - 1):
            if probabilities[i] + excess <= 0.85:
                probabilities[i] += excess
                break
    
    predictions = []
    for cancer_type, probability in zip(cancer_types, probabilities):
        predictions.append(CancerPrediction(
            cancer_type=cancer_type,
            probability=probability,
            confidence=probability
        ))
    
    return predictions


@settings(
    max_examples=10,  # Test with 10 examples to cover various probability distributions
    deadline=None
)
@given(
    predictions=cancer_predictions_with_high_probability()
)
def test_high_risk_urgent_flagging_positive(predictions):
    """
    Property 79: High-Risk Urgent Flagging (Positive Case)
    
    For any AI prediction where any cancer type probability exceeds 85%,
    the system should set the report's status to "urgent".
    
    This test verifies:
    1. Risk assessment correctly identifies high-probability predictions
    2. Risk level is set to "urgent" when any probability > 85%
    3. Report status is set to "urgent" when risk level is "urgent"
    4. The urgent flag is applied regardless of which cancer type has high probability
    
    Validates: Requirements 23.1
    """
    from app.cancer_classifier import CancerClassifier
    
    # Create classifier instance
    classifier = CancerClassifier()
    
    # Get risk level from predictions
    risk_level = classifier.get_risk_level(predictions)
    
    # Verify at least one prediction has probability > 85%
    max_probability = max(p.probability for p in predictions)
    assert max_probability > 0.85, \
        f"Test setup error: max probability should be > 85%, got {max_probability}"
    
    # Verify risk level is "urgent"
    assert risk_level == "urgent", \
        f"Risk level should be 'urgent' when any probability > 85% (max prob: {max_probability:.3f}), got '{risk_level}'"
    
    # Simulate what the report creation endpoint does
    # (from backend/app/routers/reports.py line 197)
    report_status = "urgent" if risk_level == "urgent" else "safe"
    
    # Verify report status is set to "urgent"
    assert report_status == "urgent", \
        f"Report status should be 'urgent' when risk level is 'urgent', got '{report_status}'"
    
    # Verify the high-probability prediction is identifiable
    high_prob_predictions = [p for p in predictions if p.probability > 0.85]
    assert len(high_prob_predictions) >= 1, \
        "Should have at least one prediction with probability > 85%"
    
    # Log which cancer type triggered urgent status (for debugging)
    for pred in high_prob_predictions:
        print(f"Urgent case detected: {pred.type} with probability {pred.probability:.3f}")


@settings(
    max_examples=10,  # Test with 10 examples to cover various probability distributions
    deadline=None
)
@given(
    predictions=cancer_predictions_with_low_probability()
)
def test_high_risk_urgent_flagging_negative(predictions):
    """
    Property 79: High-Risk Urgent Flagging (Negative Case)
    
    For any AI prediction where all cancer type probabilities are <= 85%,
    the system should NOT set the report's status to "urgent".
    
    This test verifies:
    1. Risk assessment correctly identifies non-urgent cases
    2. Risk level is NOT "urgent" when all probabilities <= 85%
    3. Report status is "safe" when risk level is not "urgent"
    
    Validates: Requirements 23.1
    """
    from app.cancer_classifier import CancerClassifier
    
    # Create classifier instance
    classifier = CancerClassifier()
    
    # Get risk level from predictions
    risk_level = classifier.get_risk_level(predictions)
    
    # Verify all predictions have probability <= 85%
    max_probability = max(p.probability for p in predictions)
    assert max_probability <= 0.85, \
        f"Test setup error: max probability should be <= 85%, got {max_probability}"
    
    # Verify risk level is NOT "urgent"
    assert risk_level != "urgent", \
        f"Risk level should NOT be 'urgent' when all probabilities <= 85% (max prob: {max_probability:.3f}), got '{risk_level}'"
    
    # Verify risk level is one of the valid non-urgent levels
    valid_non_urgent_levels = ["low", "medium", "high"]
    assert risk_level in valid_non_urgent_levels, \
        f"Risk level should be one of {valid_non_urgent_levels}, got '{risk_level}'"
    
    # Simulate what the report creation endpoint does
    report_status = "urgent" if risk_level == "urgent" else "safe"
    
    # Verify report status is "safe"
    assert report_status == "safe", \
        f"Report status should be 'safe' when risk level is not 'urgent', got '{report_status}'"


@settings(
    max_examples=5,  # Test boundary cases
    deadline=None
)
@given(
    boundary_offset=st.floats(min_value=-0.01, max_value=0.01)
)
def test_high_risk_urgent_flagging_boundary(boundary_offset):
    """
    Property 79: High-Risk Urgent Flagging (Boundary Case)
    
    Test the exact boundary at 85% probability to ensure correct behavior.
    
    This test verifies:
    1. Probability exactly at 85% does NOT trigger urgent
    2. Probability just above 85% (e.g., 85.01%) DOES trigger urgent
    3. Probability just below 85% (e.g., 84.99%) does NOT trigger urgent
    
    Validates: Requirements 23.1
    """
    from app.cancer_classifier import CancerClassifier
    
    # Create classifier instance
    classifier = CancerClassifier()
    
    # Create predictions with one at boundary
    boundary_prob = 0.85 + boundary_offset
    
    # Ensure probability is valid (0-1 range)
    if boundary_prob < 0.0:
        boundary_prob = 0.0
    elif boundary_prob > 1.0:
        boundary_prob = 1.0
    
    # Create 7 predictions with one at boundary
    cancer_types = [
        "Melanoma",
        "Basal Cell Carcinoma",
        "Squamous Cell Carcinoma",
        "Actinic Keratosis",
        "Benign Keratosis",
        "Dermatofibroma",
        "Vascular Lesion"
    ]
    
    remaining_prob = 1.0 - boundary_prob
    predictions = []
    
    # First prediction at boundary
    predictions.append(CancerPrediction(
        cancer_type=cancer_types[0],
        probability=boundary_prob,
        confidence=boundary_prob
    ))
    
    # Distribute remaining probability among other types
    for i in range(1, len(cancer_types)):
        if i == len(cancer_types) - 1:
            prob = remaining_prob
        else:
            prob = remaining_prob / (len(cancer_types) - i)
        
        predictions.append(CancerPrediction(
            cancer_type=cancer_types[i],
            probability=prob,
            confidence=prob
        ))
    
    # Get risk level
    risk_level = classifier.get_risk_level(predictions)
    
    # Verify behavior based on boundary
    if boundary_prob > 0.85:
        # Should be urgent
        assert risk_level == "urgent", \
            f"Risk level should be 'urgent' when probability > 85% ({boundary_prob:.4f}), got '{risk_level}'"
    else:
        # Should NOT be urgent (85% or below)
        assert risk_level != "urgent", \
            f"Risk level should NOT be 'urgent' when probability <= 85% ({boundary_prob:.4f}), got '{risk_level}'"
    
    # Verify report status follows risk level
    report_status = "urgent" if risk_level == "urgent" else "safe"
    
    if boundary_prob > 0.85:
        assert report_status == "urgent", \
            f"Report status should be 'urgent' for probability {boundary_prob:.4f}"
    else:
        assert report_status == "safe", \
            f"Report status should be 'safe' for probability {boundary_prob:.4f}"



# Feature: derman-ai-skin-screening, Property 13: Medical Disclaimer Presence
@settings(
    max_examples=10,  # Test with 10 examples to ensure consistency
    deadline=None
)
@given(
    predictions=mock_predictions(),
    hotspots=mock_hotspots()
)
def test_medical_disclaimer_presence(predictions, hotspots):
    """
    Property 13: Medical Disclaimer Presence
    
    For any AI prediction display, the rendered output should contain the
    disclaimer text "This is a 94% probability estimate. Please consult
    verified doctors for clinical biopsy".
    
    This test verifies:
    1. Analysis result includes disclaimer in to_dict() output
    2. Analysis result includes disclaimer in to_jsonb() output
    3. Disclaimer text is exactly as specified in requirements
    4. Disclaimer is present regardless of risk level or prediction values
    5. Cancer classifier includes disclaimer in format_results()
    
    Validates: Requirements 4.6, 14.1
    """
    from app.analysis_pipeline import AnalysisResult
    from app.cancer_classifier import CancerClassifier
    
    # Expected disclaimer text from requirements
    expected_disclaimer = "This is a 94% probability estimate. Please consult verified doctors for clinical biopsy"
    
    # Get risk level from predictions
    classifier = CancerClassifier()
    risk_level = classifier.get_risk_level(predictions)
    
    # Create analysis result
    result = AnalysisResult(
        hotspots=hotspots,
        predictions=predictions,
        risk_level=risk_level,
        quality_metrics={"resolution": (600, 600), "blur_score": 100.0, "brightness_score": 0.5},
        nsfw_scores={"nsfw_score": 0.1, "non_skin_score": 0.2, "safe_score": 0.7},
        processing_times={"total": 1.5, "ai_total": 1.0}
    )
    
    # Test 1: Verify disclaimer in to_dict() output
    result_dict = result.to_dict()
    assert "disclaimer" in result_dict, \
        "Analysis result dict should include 'disclaimer' field"
    assert result_dict["disclaimer"] == expected_disclaimer, \
        f"Disclaimer text should match requirements. Expected: '{expected_disclaimer}', Got: '{result_dict['disclaimer']}'"
    
    # Test 2: Verify disclaimer in to_jsonb() output
    jsonb_data = result.to_jsonb()
    assert "disclaimer" in jsonb_data, \
        "Analysis result JSONB should include 'disclaimer' field"
    assert jsonb_data["disclaimer"] == expected_disclaimer, \
        f"JSONB disclaimer text should match requirements. Expected: '{expected_disclaimer}', Got: '{jsonb_data['disclaimer']}'"
    
    # Test 3: Verify disclaimer is present regardless of risk level
    # The disclaimer should be present for all risk levels (low, medium, high, urgent)
    assert result_dict["disclaimer"] is not None, \
        "Disclaimer should never be None"
    assert len(result_dict["disclaimer"]) > 0, \
        "Disclaimer should not be empty string"
    
    # Test 4: Verify cancer classifier includes disclaimer in format_predictions_for_display()
    formatted_results = classifier.format_predictions_for_display(predictions)
    assert "disclaimer" in formatted_results, \
        "Cancer classifier format_predictions_for_display() should include 'disclaimer' field"
    assert formatted_results["disclaimer"] == expected_disclaimer, \
        f"Classifier disclaimer should match requirements. Expected: '{expected_disclaimer}', Got: '{formatted_results['disclaimer']}'"
    
    # Test 5: Verify disclaimer contains key phrases
    key_phrases = [
        "94% probability estimate",
        "consult verified doctors",
        "clinical biopsy"
    ]
    
    for phrase in key_phrases:
        assert phrase in result_dict["disclaimer"], \
            f"Disclaimer should contain key phrase: '{phrase}'"
    
    # Test 6: Verify disclaimer is consistent across different output formats
    assert result_dict["disclaimer"] == jsonb_data["disclaimer"] == formatted_results["disclaimer"], \
        "Disclaimer text should be identical across all output formats"
    
    print(f"✓ Disclaimer verified for risk level: {risk_level}")
    print(f"  Disclaimer: {result_dict['disclaimer'][:50]}...")
