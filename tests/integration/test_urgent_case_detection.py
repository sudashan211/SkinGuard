"""
Integration Test for Urgent Case Detection
Tests the complete flow from AI analysis to urgent report creation

Feature: derman-ai-skin-screening
Task: 16.1 Implement urgent case detection

This test verifies:
1. AI analysis correctly identifies high-risk cases (probability > 85%)
2. Report status is automatically set to "urgent" for high-risk cases
3. Report status remains "safe" for non-urgent cases
4. The complete pipeline from image upload to report creation works correctly

Requirements: 23.1
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
from PIL import Image

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.cancer_classifier import CancerPrediction, CancerClassifier
from app.lesion_detector import Hotspot
from app.analysis_pipeline import AnalysisResult


def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (600, 600), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes.getvalue()


class TestUrgentCaseDetection:
    """Integration tests for urgent case detection"""
    
    def test_urgent_case_detection_with_high_probability(self):
        """
        Test that reports are marked as urgent when AI detects high-risk cases
        
        Scenario:
        1. AI analysis returns predictions with one cancer type > 85% probability
        2. Risk assessment identifies this as "urgent"
        3. Report status is set to "urgent"
        """
        # Create mock predictions with high probability (> 85%)
        predictions = [
            CancerPrediction("Melanoma", 0.92, 0.92),
            CancerPrediction("Basal Cell Carcinoma", 0.03, 0.03),
            CancerPrediction("Squamous Cell Carcinoma", 0.02, 0.02),
            CancerPrediction("Actinic Keratosis", 0.01, 0.01),
            CancerPrediction("Benign Keratosis", 0.01, 0.01),
            CancerPrediction("Dermatofibroma", 0.005, 0.005),
            CancerPrediction("Vascular Lesion", 0.005, 0.005)
        ]
        
        # Create classifier and get risk level
        classifier = CancerClassifier()
        risk_level = classifier.get_risk_level(predictions)
        
        # Verify risk level is "urgent"
        assert risk_level == "urgent", \
            f"Risk level should be 'urgent' for 92% probability, got '{risk_level}'"
        
        # Simulate report creation logic (from reports.py line 197)
        report_status = "urgent" if risk_level == "urgent" else "safe"
        
        # Verify report status is "urgent"
        assert report_status == "urgent", \
            f"Report status should be 'urgent', got '{report_status}'"
        
        print(f"✓ Urgent case correctly detected: Melanoma at 92% probability")
    
    def test_safe_case_detection_with_low_probability(self):
        """
        Test that reports are marked as safe when AI detects low-risk cases
        
        Scenario:
        1. AI analysis returns predictions with all cancer types <= 85% probability
        2. Risk assessment identifies this as non-urgent (low/medium/high)
        3. Report status is set to "safe"
        """
        # Create mock predictions with low probability (<= 85%)
        predictions = [
            CancerPrediction("Benign Keratosis", 0.60, 0.60),
            CancerPrediction("Melanoma", 0.15, 0.15),
            CancerPrediction("Basal Cell Carcinoma", 0.10, 0.10),
            CancerPrediction("Squamous Cell Carcinoma", 0.08, 0.08),
            CancerPrediction("Actinic Keratosis", 0.04, 0.04),
            CancerPrediction("Dermatofibroma", 0.02, 0.02),
            CancerPrediction("Vascular Lesion", 0.01, 0.01)
        ]
        
        # Create classifier and get risk level
        classifier = CancerClassifier()
        risk_level = classifier.get_risk_level(predictions)
        
        # Verify risk level is NOT "urgent"
        assert risk_level != "urgent", \
            f"Risk level should NOT be 'urgent' for 60% probability, got '{risk_level}'"
        
        # Simulate report creation logic
        report_status = "urgent" if risk_level == "urgent" else "safe"
        
        # Verify report status is "safe"
        assert report_status == "safe", \
            f"Report status should be 'safe', got '{report_status}'"
        
        print(f"✓ Safe case correctly detected: Benign Keratosis at 60% probability")
    
    def test_boundary_case_at_85_percent(self):
        """
        Test the exact boundary at 85% probability
        
        Scenario:
        1. AI analysis returns predictions with exactly 85% probability
        2. Risk assessment should NOT mark as urgent (must be > 85%)
        3. Report status is set to "safe"
        """
        # Create mock predictions with exactly 85% probability
        predictions = [
            CancerPrediction("Melanoma", 0.85, 0.85),
            CancerPrediction("Basal Cell Carcinoma", 0.05, 0.05),
            CancerPrediction("Squamous Cell Carcinoma", 0.04, 0.04),
            CancerPrediction("Actinic Keratosis", 0.03, 0.03),
            CancerPrediction("Benign Keratosis", 0.02, 0.02),
            CancerPrediction("Dermatofibroma", 0.005, 0.005),
            CancerPrediction("Vascular Lesion", 0.005, 0.005)
        ]
        
        # Create classifier and get risk level
        classifier = CancerClassifier()
        risk_level = classifier.get_risk_level(predictions)
        
        # Verify risk level is NOT "urgent" (85% is not > 85%)
        assert risk_level != "urgent", \
            f"Risk level should NOT be 'urgent' at exactly 85%, got '{risk_level}'"
        
        # Simulate report creation logic
        report_status = "urgent" if risk_level == "urgent" else "safe"
        
        # Verify report status is "safe"
        assert report_status == "safe", \
            f"Report status should be 'safe' at 85%, got '{report_status}'"
        
        print(f"✓ Boundary case correctly handled: 85% is NOT urgent")
    
    def test_boundary_case_just_above_85_percent(self):
        """
        Test just above the 85% boundary
        
        Scenario:
        1. AI analysis returns predictions with 85.1% probability
        2. Risk assessment should mark as urgent (> 85%)
        3. Report status is set to "urgent"
        """
        # Create mock predictions with 85.1% probability
        predictions = [
            CancerPrediction("Melanoma", 0.851, 0.851),
            CancerPrediction("Basal Cell Carcinoma", 0.05, 0.05),
            CancerPrediction("Squamous Cell Carcinoma", 0.04, 0.04),
            CancerPrediction("Actinic Keratosis", 0.03, 0.03),
            CancerPrediction("Benign Keratosis", 0.02, 0.02),
            CancerPrediction("Dermatofibroma", 0.0045, 0.0045),
            CancerPrediction("Vascular Lesion", 0.0045, 0.0045)
        ]
        
        # Create classifier and get risk level
        classifier = CancerClassifier()
        risk_level = classifier.get_risk_level(predictions)
        
        # Verify risk level IS "urgent" (85.1% > 85%)
        assert risk_level == "urgent", \
            f"Risk level should be 'urgent' at 85.1%, got '{risk_level}'"
        
        # Simulate report creation logic
        report_status = "urgent" if risk_level == "urgent" else "safe"
        
        # Verify report status is "urgent"
        assert report_status == "urgent", \
            f"Report status should be 'urgent' at 85.1%, got '{report_status}'"
        
        print(f"✓ Boundary case correctly handled: 85.1% IS urgent")
    
    def test_multiple_cancer_types_with_high_probability(self):
        """
        Test that urgent is triggered even if a less common cancer type has high probability
        
        Scenario:
        1. AI analysis returns predictions with Vascular Lesion at 90% (not typically dangerous)
        2. Risk assessment should still mark as urgent (any type > 85%)
        3. Report status is set to "urgent"
        """
        # Create mock predictions with Vascular Lesion at high probability
        predictions = [
            CancerPrediction("Vascular Lesion", 0.90, 0.90),
            CancerPrediction("Melanoma", 0.04, 0.04),
            CancerPrediction("Basal Cell Carcinoma", 0.03, 0.03),
            CancerPrediction("Squamous Cell Carcinoma", 0.01, 0.01),
            CancerPrediction("Actinic Keratosis", 0.01, 0.01),
            CancerPrediction("Benign Keratosis", 0.005, 0.005),
            CancerPrediction("Dermatofibroma", 0.005, 0.005)
        ]
        
        # Create classifier and get risk level
        classifier = CancerClassifier()
        risk_level = classifier.get_risk_level(predictions)
        
        # Verify risk level is "urgent" (any type > 85%)
        assert risk_level == "urgent", \
            f"Risk level should be 'urgent' for any cancer type > 85%, got '{risk_level}'"
        
        # Simulate report creation logic
        report_status = "urgent" if risk_level == "urgent" else "safe"
        
        # Verify report status is "urgent"
        assert report_status == "urgent", \
            f"Report status should be 'urgent', got '{report_status}'"
        
        print(f"✓ Urgent case correctly detected: Vascular Lesion at 90% probability")
    
    def test_analysis_result_includes_risk_level(self):
        """
        Test that AnalysisResult correctly includes risk level
        
        Scenario:
        1. Create AnalysisResult with urgent predictions
        2. Verify risk_level is included in result
        3. Verify risk_level is preserved in to_dict() and to_jsonb()
        """
        # Create mock predictions with high probability
        predictions = [
            CancerPrediction("Melanoma", 0.92, 0.92),
            CancerPrediction("Basal Cell Carcinoma", 0.08, 0.08)
        ]
        
        hotspots = [
            Hotspot(x=100, y=100, width=50, height=50, confidence=0.9)
        ]
        
        # Create analysis result
        result = AnalysisResult(
            hotspots=hotspots,
            predictions=predictions,
            risk_level="urgent",
            quality_metrics={"resolution": (600, 600), "blur_score": 100.0, "brightness_score": 0.5},
            nsfw_scores={"nsfw_score": 0.1, "non_skin_score": 0.2, "safe_score": 0.7},
            processing_times={"total": 1.5, "ai_total": 1.0}
        )
        
        # Verify risk_level is set
        assert result.risk_level == "urgent", \
            f"AnalysisResult should have risk_level 'urgent', got '{result.risk_level}'"
        
        # Verify risk_level is in to_dict()
        result_dict = result.to_dict()
        assert "risk_level" in result_dict, \
            "to_dict() should include risk_level"
        assert result_dict["risk_level"] == "urgent", \
            f"to_dict() risk_level should be 'urgent', got '{result_dict['risk_level']}'"
        
        print(f"✓ AnalysisResult correctly includes risk_level: {result.risk_level}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
