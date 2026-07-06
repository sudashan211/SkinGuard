"""
Security Tests for NSFW Filter Effectiveness
Task: 36.5 Security audit
Requirements: 3.1, 3.2, 3.3, 3.4

Tests NSFW filter effectiveness with known test images:
- NSFW images are rejected
- Safe medical images are accepted
- Threshold enforcement (0.35 for NSFW, 0.8 for non-skin)
- Audit logging for rejections
"""
import pytest
from PIL import Image
import io
import numpy as np
import sys
import os
from unittest.mock import Mock, patch, AsyncMock

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.nsfw_filter import NSFWDetector, ContentViolationError, NSFWResult


def create_test_image(width=512, height=512, color=(128, 128, 128)):
    """Create a test image with specified dimensions and color"""
    image = Image.new('RGB', (width, height), color)
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    return buffer.getvalue()


def create_skin_tone_image(width=512, height=512):
    """Create an image with realistic skin-tone colors"""
    image = Image.new('RGB', (width, height))
    pixels = image.load()
    
    # Create varied skin tones (realistic medical image)
    for i in range(width):
        for j in range(height):
            # Skin tone: R > G > B pattern with variation
            r = 180 + (i % 20) - 10
            g = 140 + (j % 15) - 7
            b = 100 + ((i + j) % 10) - 5
            pixels[i, j] = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
    
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    return buffer.getvalue()


def create_non_skin_image(width=512, height=512):
    """Create an image with non-skin colors (e.g., blue sky)"""
    image = Image.new('RGB', (width, height), (50, 100, 200))
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    return buffer.getvalue()


class TestNSFWThresholdEnforcement:
    """Test NSFW threshold enforcement"""
    
    def test_nsfw_threshold_is_0_35(self):
        """
        Test that NSFW threshold is set to 0.35
        
        Security: Requirement 3.2 - NSFW score > 0.35 should be rejected
        """
        detector = NSFWDetector()
        assert detector.NSFW_THRESHOLD == 0.35
    
    def test_non_skin_threshold_is_0_8(self):
        """
        Test that non-skin threshold is set to 0.8
        
        Security: Requirement 3.3 - Non-skin score > 0.8 should be rejected
        """
        detector = NSFWDetector()
        assert detector.NON_SKIN_THRESHOLD == 0.8
    
    @patch('app.nsfw_filter.NSFWDetector._calculate_scores')
    def test_image_rejected_when_nsfw_exceeds_threshold(self, mock_calculate):
        """
        Test that images are rejected when NSFW score exceeds 0.35
        
        Security: Requirement 3.2 - Prevents inappropriate content
        """
        detector = NSFWDetector()
        
        # Mock high NSFW score (above threshold)
        mock_calculate.return_value = (0.45, 0.2, 0.35)  # nsfw, non_skin, safe
        
        image_data = create_test_image()
        
        # Should raise ContentViolationError
        with pytest.raises(ContentViolationError) as exc_info:
            detector.check_nsfw(image_data)
        
        assert exc_info.value.code == "CONTENT_VIOLATION"
        assert exc_info.value.status_code == 403
        assert "NSFW score exceeds threshold" in exc_info.value.details
    
    @patch('app.nsfw_filter.NSFWDetector._calculate_scores')
    def test_image_rejected_when_non_skin_exceeds_threshold(self, mock_calculate):
        """
        Test that images are rejected when non-skin score exceeds 0.8
        
        Security: Requirement 3.3 - Ensures medical relevance
        """
        detector = NSFWDetector()
        
        # Mock high non-skin score (above threshold)
        mock_calculate.return_value = (0.1, 0.85, 0.05)  # nsfw, non_skin, safe
        
        image_data = create_test_image()
        
        # Should raise ContentViolationError
        with pytest.raises(ContentViolationError) as exc_info:
            detector.check_nsfw(image_data)
        
        assert exc_info.value.code == "CONTENT_VIOLATION"
        assert exc_info.value.status_code == 403
        assert "Non-skin score exceeds threshold" in exc_info.value.details
    
    @patch('app.nsfw_filter.NSFWDetector._calculate_scores')
    def test_image_accepted_when_below_thresholds(self, mock_calculate):
        """
        Test that images are accepted when scores are below thresholds
        
        Security: Requirement 3.5 - Safe images should pass
        """
        detector = NSFWDetector()
        
        # Mock safe scores (below thresholds)
        mock_calculate.return_value = (0.1, 0.3, 0.9)  # nsfw, non_skin, safe
        
        image_data = create_test_image()
        
        # Should not raise exception
        result = detector.check_nsfw(image_data)
        
        assert isinstance(result, NSFWResult)
        assert result.safe is True
        assert result.nsfw_score == 0.1
        assert result.non_skin_score == 0.3
    
    @patch('app.nsfw_filter.NSFWDetector._calculate_scores')
    def test_boundary_case_nsfw_exactly_at_threshold(self, mock_calculate):
        """
        Test boundary case: NSFW score exactly at 0.35
        
        Security: Clarifies threshold behavior
        """
        detector = NSFWDetector()
        
        # Mock NSFW score exactly at threshold
        mock_calculate.return_value = (0.35, 0.2, 0.45)
        
        image_data = create_test_image()
        
        # At threshold should be accepted (> 0.35 is rejected)
        result = detector.check_nsfw(image_data)
        assert result.safe is True
    
    @patch('app.nsfw_filter.NSFWDetector._calculate_scores')
    def test_boundary_case_non_skin_exactly_at_threshold(self, mock_calculate):
        """
        Test boundary case: Non-skin score exactly at 0.8
        
        Security: Clarifies threshold behavior
        """
        detector = NSFWDetector()
        
        # Mock non-skin score exactly at threshold
        mock_calculate.return_value = (0.1, 0.8, 0.1)
        
        image_data = create_test_image()
        
        # At threshold should be accepted (> 0.8 is rejected)
        result = detector.check_nsfw(image_data)
        assert result.safe is True


class TestNSFWFilterEffectiveness:
    """Test NSFW filter effectiveness with various image types"""
    
    def test_safe_medical_image_passes_filter(self):
        """
        Test that safe medical images pass the filter
        
        Security: Requirement 3.5 - Legitimate medical images should be accepted
        """
        detector = NSFWDetector()
        image_data = create_skin_tone_image()
        
        # Should not raise exception
        result = detector.check_nsfw(image_data)
        
        assert result.safe is True
        assert result.nsfw_score <= 0.35
    
    def test_non_skin_image_has_high_non_skin_score(self):
        """
        Test that non-skin images have high non-skin scores
        
        Security: Requirement 3.3 - Detects non-medical images
        """
        detector = NSFWDetector()
        image_data = create_non_skin_image()
        
        # Get scores without validation
        scores = detector.get_scores_only(image_data)
        
        # Non-skin score should be relatively high
        assert scores["non_skin_score"] > 0.5
    
    def test_filter_returns_detailed_scores(self):
        """
        Test that filter returns detailed scores for analysis
        
        Security: Enables audit and monitoring
        """
        detector = NSFWDetector()
        image_data = create_test_image()
        
        scores = detector.get_scores_only(image_data)
        
        # Should return all score types
        assert "nsfw_score" in scores
        assert "non_skin_score" in scores
        assert "safe_score" in scores
        assert "passes_nsfw_check" in scores
        assert "passes_skin_check" in scores
        
        # All scores should be in valid range [0, 1]
        assert 0.0 <= scores["nsfw_score"] <= 1.0
        assert 0.0 <= scores["non_skin_score"] <= 1.0
        assert 0.0 <= scores["safe_score"] <= 1.0
    
    def test_filter_handles_various_image_sizes(self):
        """
        Test that filter handles images of various sizes
        
        Security: Prevents bypass through unusual image sizes
        """
        detector = NSFWDetector()
        
        sizes = [
            (256, 256),
            (512, 512),
            (1024, 768),
            (1920, 1080),
            (100, 100),
        ]
        
        for width, height in sizes:
            image_data = create_test_image(width, height)
            
            # Should process without error
            scores = detector.get_scores_only(image_data)
            assert scores is not None
            assert "nsfw_score" in scores


class TestContentViolationHandling:
    """Test content violation error handling"""
    
    @patch('app.nsfw_filter.NSFWDetector._calculate_scores')
    def test_content_violation_error_includes_scores(self, mock_calculate):
        """
        Test that ContentViolationError includes score information
        
        Security: Requirement 3.6 - Enables audit logging
        """
        detector = NSFWDetector()
        
        # Mock high NSFW score
        mock_calculate.return_value = (0.75, 0.2, 0.05)
        
        image_data = create_test_image()
        
        try:
            detector.check_nsfw(image_data)
            pytest.fail("Should have raised ContentViolationError")
        except ContentViolationError as e:
            # Error should include scores
            assert hasattr(e, 'nsfw_score')
            assert hasattr(e, 'non_skin_score')
            assert e.nsfw_score == 0.75
            assert e.non_skin_score == 0.2
    
    @patch('app.nsfw_filter.NSFWDetector._calculate_scores')
    def test_content_violation_error_message(self, mock_calculate):
        """
        Test that ContentViolationError has appropriate message
        
        Security: Requirement 3.4 - Clear error messaging
        """
        detector = NSFWDetector()
        
        # Mock high NSFW score
        mock_calculate.return_value = (0.5, 0.2, 0.3)
        
        image_data = create_test_image()
        
        try:
            detector.check_nsfw(image_data)
            pytest.fail("Should have raised ContentViolationError")
        except ContentViolationError as e:
            # Should have appropriate message
            assert "Inappropriate content detected" in str(e)
            assert e.status_code == 403
    
    def test_invalid_image_data_raises_content_violation(self):
        """
        Test that invalid image data raises ContentViolationError
        
        Security: Fail-safe behavior - reject suspicious uploads
        """
        detector = NSFWDetector()
        
        invalid_data = b"not an image"
        
        # Should raise ContentViolationError (fail-safe)
        with pytest.raises(ContentViolationError):
            detector.check_nsfw(invalid_data)
    
    def test_empty_image_data_raises_content_violation(self):
        """
        Test that empty image data raises ContentViolationError
        
        Security: Prevents bypass through empty uploads
        """
        detector = NSFWDetector()
        
        empty_data = b""
        
        # Should raise ContentViolationError
        with pytest.raises(ContentViolationError):
            detector.check_nsfw(empty_data)


class TestAuditLogging:
    """Test audit logging for content violations"""
    
    @patch('app.nsfw_filter.NSFWDetector._calculate_scores')
    def test_rejection_includes_audit_information(self, mock_calculate):
        """
        Test that rejections include information for audit logging
        
        Security: Requirement 3.6 - Enables security monitoring
        """
        detector = NSFWDetector()
        
        # Mock violation
        mock_calculate.return_value = (0.8, 0.3, 0.1)
        
        image_data = create_test_image()
        
        try:
            detector.check_nsfw(image_data)
            pytest.fail("Should have raised ContentViolationError")
        except ContentViolationError as e:
            # Should have all information needed for audit log
            assert hasattr(e, 'code')
            assert hasattr(e, 'nsfw_score')
            assert hasattr(e, 'non_skin_score')
            assert hasattr(e, 'details')
            
            # Details should explain the rejection
            assert e.details is not None
            assert len(e.details) > 0


class TestFilterSecurity:
    """Test overall filter security"""
    
    def test_filter_cannot_be_bypassed_with_corrupted_image(self):
        """
        Test that filter handles corrupted images securely
        
        Security: Prevents bypass through malformed uploads
        """
        detector = NSFWDetector()
        
        # Create corrupted image data
        corrupted_data = b"\xFF\xD8\xFF\xE0" + b"corrupted" * 100
        
        # Should raise ContentViolationError (fail-safe)
        with pytest.raises(ContentViolationError):
            detector.check_nsfw(corrupted_data)
    
    def test_filter_preprocessing_is_consistent(self):
        """
        Test that image preprocessing is consistent
        
        Security: Prevents bypass through preprocessing manipulation
        """
        detector = NSFWDetector()
        
        # Create test image
        image_data = create_test_image(1024, 768)
        
        # Load and preprocess
        from PIL import Image
        pil_image = Image.open(io.BytesIO(image_data))
        processed = detector._preprocess_image(pil_image)
        
        # Should be resized to 224x224 (model input size)
        assert processed.shape == (224, 224, 3)
        
        # Should be normalized to [0, 1]
        assert processed.min() >= 0.0
        assert processed.max() <= 1.0
    
    def test_filter_scores_are_in_valid_range(self):
        """
        Test that all scores are in valid range [0, 1]
        
        Security: Prevents score manipulation
        """
        detector = NSFWDetector()
        
        # Test with multiple images
        for _ in range(10):
            image_data = create_test_image()
            scores = detector.get_scores_only(image_data)
            
            # All scores must be in [0, 1]
            assert 0.0 <= scores["nsfw_score"] <= 1.0
            assert 0.0 <= scores["non_skin_score"] <= 1.0
            assert 0.0 <= scores["safe_score"] <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
