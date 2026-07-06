"""
Image Quality Validation Module
Validates uploaded images for resolution, blur, and brightness quality
"""
from typing import Tuple, Dict, Any
from PIL import Image
import numpy as np
import cv2
from io import BytesIO
from app.config import settings


class QualityError(Exception):
    """Base exception for image quality validation errors"""
    def __init__(self, reason: str, code: str = "IMAGE_QUALITY_ERROR"):
        self.code = code
        self.message = f"Image quality insufficient: {reason}"
        self.status_code = 400
        self.reason = reason
        super().__init__(self.message)


class QualityResult:
    """Result of image quality validation"""
    def __init__(
        self,
        passed: bool,
        resolution: Tuple[int, int],
        blur_score: float,
        brightness_score: float,
        message: str = "",
        guidance: str = ""
    ):
        self.passed = passed
        self.resolution = resolution
        self.blur_score = blur_score
        self.brightness_score = brightness_score
        self.message = message
        self.guidance = guidance


class ImageQualityValidator:
    """
    Validates image quality for medical analysis
    
    Checks:
    - Resolution: Minimum 512x512 pixels (or 200x200 in demo mode)
    - Blur: Laplacian variance threshold
    - Brightness: Histogram analysis for proper lighting
    """
    
    # Quality thresholds
    MIN_RESOLUTION = 200 if settings.demo_mode else 400  # Lowered to support HAM10000 (600x450)
    BLUR_THRESHOLD = 20.0  # Very lenient for HAM10000 dataset (same as demo mode)
    BRIGHTNESS_MIN = 10 if settings.demo_mode else 30
    BRIGHTNESS_MAX = 245 if settings.demo_mode else 225
    
    def __init__(self):
        pass
    
    def validate_quality(self, image_data: bytes) -> QualityResult:
        """
        Validates image meets minimum quality standards
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            QualityResult with validation details
            
        Raises:
            QualityError: If image fails validation
        """
        # Load image
        try:
            pil_image = Image.open(BytesIO(image_data))
            # Convert to RGB if necessary
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
        except Exception as e:
            raise QualityError(
                reason="Unable to load image file",
                code="INVALID_IMAGE_FORMAT"
            )
        
        # Get resolution
        width, height = pil_image.size
        resolution = (width, height)
        
        # Validate resolution
        if width < self.MIN_RESOLUTION or height < self.MIN_RESOLUTION:
            raise QualityError(
                reason="Image resolution too low for accurate analysis",
                code="LOW_RESOLUTION"
            )
        
        # Convert to numpy array for OpenCV processing
        image_array = np.array(pil_image)
        
        # Convert RGB to BGR for OpenCV
        image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Calculate blur score using Laplacian variance
        blur_score = self._calculate_blur_score(image_bgr)
        
        # Calculate brightness score
        brightness_score = self._calculate_brightness_score(image_bgr)
        
        # Check blur quality
        if blur_score < self.BLUR_THRESHOLD:
            guidance = "Image appears blurry. Please hold camera steady and ensure proper focus."
            return QualityResult(
                passed=False,
                resolution=resolution,
                blur_score=blur_score,
                brightness_score=brightness_score,
                message="Image is too blurry for accurate analysis",
                guidance=guidance
            )
        
        # Check brightness quality
        if brightness_score < self.BRIGHTNESS_MIN:
            guidance = "Image is too dark. Please ensure good lighting conditions."
            return QualityResult(
                passed=False,
                resolution=resolution,
                blur_score=blur_score,
                brightness_score=brightness_score,
                message="Image is too dark for accurate analysis",
                guidance=guidance
            )
        
        if brightness_score > self.BRIGHTNESS_MAX:
            guidance = "Image is too bright. Please avoid direct flash or harsh lighting."
            return QualityResult(
                passed=False,
                resolution=resolution,
                blur_score=blur_score,
                brightness_score=brightness_score,
                message="Image is too bright for accurate analysis",
                guidance=guidance
            )
        
        # All checks passed
        return QualityResult(
            passed=True,
            resolution=resolution,
            blur_score=blur_score,
            brightness_score=brightness_score,
            message="Image quality is acceptable"
        )
    
    def _calculate_blur_score(self, image: np.ndarray) -> float:
        """
        Calculate blur score using Laplacian variance
        
        Higher values indicate sharper images
        Lower values indicate blurrier images
        
        Args:
            image: OpenCV image (BGR format)
            
        Returns:
            Blur score (Laplacian variance)
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate Laplacian
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        
        # Calculate variance of Laplacian
        variance = laplacian.var()
        
        return float(variance)
    
    def _calculate_brightness_score(self, image: np.ndarray) -> float:
        """
        Calculate brightness score using histogram analysis
        
        Returns average brightness value (0-255)
        
        Args:
            image: OpenCV image (BGR format)
            
        Returns:
            Average brightness score
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate mean brightness
        mean_brightness = np.mean(gray)
        
        return float(mean_brightness)
    
    def get_quality_metrics(self, image_data: bytes) -> Dict[str, Any]:
        """
        Get detailed quality metrics without validation
        
        Useful for debugging and analytics
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dictionary with quality metrics
        """
        try:
            pil_image = Image.open(BytesIO(image_data))
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            width, height = pil_image.size
            image_array = np.array(pil_image)
            image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            blur_score = self._calculate_blur_score(image_bgr)
            brightness_score = self._calculate_brightness_score(image_bgr)
            
            return {
                "resolution": {"width": width, "height": height},
                "blur_score": blur_score,
                "brightness_score": brightness_score,
                "meets_resolution": width >= self.MIN_RESOLUTION and height >= self.MIN_RESOLUTION,
                "meets_blur": blur_score >= self.BLUR_THRESHOLD,
                "meets_brightness": self.BRIGHTNESS_MIN <= brightness_score <= self.BRIGHTNESS_MAX
            }
        except Exception as e:
            return {
                "error": str(e)
            }


# Global validator instance
validator = ImageQualityValidator()
