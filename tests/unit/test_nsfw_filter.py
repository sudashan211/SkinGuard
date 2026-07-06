"""
Unit tests for NSFW Content Filter
Requirements: 3.1, 3.2, 3.3, 3.4
"""
import pytest
from PIL import Image
import io
import numpy as np
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.nsfw_filter import NSFWDetector, ContentViolationError, NSFWResult


@pytest.fixture
def nsfw_detector():
    """Create NSFW detector instance"""
    return NSFWDetector()


def create_test_image(width=512, height=512, color=(128, 128, 128)):
    """
    Create a test image with specified dimensions and color
    
    Args:
        width: Image width
        height: Image height
        color: RGB color tuple
        
    Returns:
        bytes: Image data as bytes
    """
    image = Image.new('RGB', (width, height), color)
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    return buffer.getvalue()


def create_skin_tone_image(width=512, height=512):
    """
    Create an image with skin-tone colors
    
    Returns:
        bytes: Image data as bytes
    """
    # Create image with skin tone (R > G > B pattern)
    image = Image.new('RGB', (width, height))
    pixels = image.load()
    
    for i in range(width):
        for j in range(height):
            # Skin tone: R=180, G=140, B=100
            pixels[i, j] = (180, 140, 100)
    
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    return buffer.getvalue()


def create_non_skin_image(width=512, height=512):
    """
    Create an image with non-skin colors (e.g., blue sky)
    
    Returns:
        bytes: Image data as bytes
    """
    # Create blue image (non-skin)
    image = Image.new('RGB', (width, height), (50, 100, 200))
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    return buffer.getvalue()


class TestNSFWDetector:
    """Test suite for NSFW detector"""
    
    def test_detector_initialization(self, nsfw_detector):
        """Test that detector initializes correctly"""
        assert nsfw_detector is not None
        assert nsfw_detector.NSFW_THRESHOLD == 0.35
        assert nsfw_detector.NON_SKIN_THRESHOLD == 0.8
    
    def test_check_nsfw_with_safe_image(self, nsfw_detector):
        """Test NSFW check with a safe skin-tone image"""
        # Create a skin-tone image
        image_data = create_skin_tone_image()
        
        # Should not raise exception
        result = nsfw_detector.check_nsfw(image_data)
        
        assert isinstance(result, NSFWResult)
        assert result.safe is True
        assert 0.0 <= result.nsfw_score <= 1.0
        assert 0.0 <= result.non_skin_score <= 1.0
        assert 0.0 <= result.safe_score <= 1.0
    
    def test_check_nsfw_with_non_skin_image(self, nsfw_detector):
        """Test NSFW check with non-skin image (should have high non_skin_score)"""
        # Create a blue image (non-skin)
        image_data = create_non_skin_image()
        
        # Get scores without validation
        scores = nsfw_detector.get_scores_only(image_data)
        
        # Non-skin score should be relatively high
        assert scores["non_skin_score"] > 0.5
    
    def test_nsfw_threshold_boundary(self, nsfw_detector):
        """Test NSFW threshold boundary"""
        # The threshold is 0.35
        assert nsfw_detector.NSFW_THRESHOLD == 0.35
    
    def test_non_skin_threshold_boundary(self, nsfw_detector):
        """Test non-skin threshold boundary"""
        # The threshold is 0.8
        assert nsfw_detector.NON_SKIN_THRESHOLD == 0.8
    
    def test_get_scores_only(self, nsfw_detector):
        """Test getting scores without validation"""
        image_data = create_test_image()
        
        scores = nsfw_detector.get_scores_only(image_data)
        
        assert "nsfw_score" in scores
        assert "non_skin_score" in scores
        assert "safe_score" in scores
        assert "passes_nsfw_check" in scores
        assert "passes_skin_check" in scores
        
        # All scores should be in valid range
        assert 0.0 <= scores["nsfw_score"] <= 1.0
        assert 0.0 <= scores["non_skin_score"] <= 1.0
        assert 0.0 <= scores["safe_score"] <= 1.0
    
    def test_invalid_image_data(self, nsfw_detector):
        """Test handling of invalid image data"""
        invalid_data = b"not an image"
        
        # Should raise ContentViolationError (fail-safe behavior)
        with pytest.raises(ContentViolationError):
            nsfw_detector.check_nsfw(invalid_data)
    
    def test_empty_image_data(self, nsfw_detector):
        """Test handling of empty image data"""
        empty_data = b""
        
        # Should raise ContentViolationError (fail-safe behavior)
        with pytest.raises(ContentViolationError):
            nsfw_detector.check_nsfw(empty_data)
    
    def test_content_violation_error_attributes(self, nsfw_detector):
        """Test ContentViolationError has correct attributes"""
        try:
            # Force an error with invalid data
            nsfw_detector.check_nsfw(b"invalid")
        except ContentViolationError as e:
            assert e.code == "CONTENT_VIOLATION"
            assert e.status_code == 403
            assert "message" in dir(e)
            assert "nsfw_score" in dir(e)
            assert "non_skin_score" in dir(e)
            assert "details" in dir(e)
    
    def test_preprocess_image(self, nsfw_detector):
        """Test image preprocessing"""
        image_data = create_test_image(width=1024, height=768)
        
        # Load and preprocess
        from PIL import Image
        pil_image = Image.open(io.BytesIO(image_data))
        processed = nsfw_detector._preprocess_image(pil_image)
        
        # Should be resized to 224x224
        assert processed.shape == (224, 224, 3)
        
        # Should be normalized to [0, 1]
        assert processed.min() >= 0.0
        assert processed.max() <= 1.0
    
    def test_calculate_scores_returns_valid_range(self, nsfw_detector):
        """Test that score calculation returns values in valid range"""
        # Create a random image array
        image_array = np.random.rand(224, 224, 3).astype(np.float32)
        
        nsfw_score, non_skin_score, safe_score = nsfw_detector._calculate_scores(image_array)
        
        # All scores should be in [0, 1]
        assert 0.0 <= nsfw_score <= 1.0
        assert 0.0 <= non_skin_score <= 1.0
        assert 0.0 <= safe_score <= 1.0


class TestNSFWResult:
    """Test suite for NSFWResult class"""
    
    def test_nsfw_result_creation(self):
        """Test NSFWResult object creation"""
        result = NSFWResult(
            safe=True,
            nsfw_score=0.1,
            non_skin_score=0.2,
            safe_score=0.9,
            rejection_reason=""
        )
        
        assert result.safe is True
        assert result.nsfw_score == 0.1
        assert result.non_skin_score == 0.2
        assert result.safe_score == 0.9
        assert result.rejection_reason == ""
    
    def test_nsfw_result_with_rejection(self):
        """Test NSFWResult with rejection reason"""
        result = NSFWResult(
            safe=False,
            nsfw_score=0.5,
            non_skin_score=0.3,
            safe_score=0.2,
            rejection_reason="NSFW score exceeds threshold"
        )
        
        assert result.safe is False
        assert result.rejection_reason == "NSFW score exceeds threshold"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
