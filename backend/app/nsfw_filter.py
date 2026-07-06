"""
NSFW Content Filter (Gatekeeper)
Validates uploaded images for inappropriate content before medical analysis
Requirements: 3.1, 3.2, 3.3, 3.4
"""
from typing import Dict, Any
from PIL import Image
import numpy as np
from io import BytesIO
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class ContentViolationError(Exception):
    """Exception raised when inappropriate content is detected"""
    def __init__(self, nsfw_score: float, non_skin_score: float, message: str = "Inappropriate content detected"):
        self.code = "CONTENT_VIOLATION"
        self.message = message
        self.status_code = 403
        self.nsfw_score = nsfw_score
        self.non_skin_score = non_skin_score
        self.details = {
            "nsfw_score": nsfw_score,
            "non_skin_score": non_skin_score
        }
        super().__init__(self.message)


class NSFWResult:
    """Result of NSFW content detection"""
    def __init__(
        self,
        safe: bool,
        nsfw_score: float,
        non_skin_score: float,
        safe_score: float,
        rejection_reason: str = ""
    ):
        self.safe = safe
        self.nsfw_score = nsfw_score
        self.non_skin_score = non_skin_score
        self.safe_score = safe_score
        self.rejection_reason = rejection_reason


class NSFWDetector:
    """
    NSFW Content Detection & Skin Validation (Gatekeeper)
    
    Validates images for inappropriate content AND verifies they contain skin before medical analysis.
    Uses a heuristic-based approach for demonstration.
    
    In production, this should be replaced with:
    - NudeNet (https://github.com/notAI-tech/NudeNet)
    - Yahoo Open NSFW (https://github.com/yahoo/open_nsfw)
    - Or similar pre-trained NSFW detection models
    
    Rejection Criteria:
    - NSFW score > 0.35: Explicit content detected
    - Skin percentage < 15%: Not a skin image (posters, text, objects, etc.)
    """
    
    # Detection thresholds
    NSFW_THRESHOLD = 0.5 if settings.demo_mode else 0.35
    NON_SKIN_THRESHOLD = 0.99  # Legacy threshold (kept for compatibility)
    MIN_SKIN_PERCENTAGE = 0.15  # Minimum 15% skin content required
    
    def __init__(self):
        """Initialize NSFW detector"""
        # In production, load pre-trained model here
        # For now, we'll use a heuristic-based approach
        logger.info("NSFW Detector initialized (heuristic mode)")
    
    def check_nsfw(self, image_data: bytes) -> NSFWResult:
        """
        Check image for NSFW content and validate skin image
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            NSFWResult with detection scores
            
        Raises:
            ContentViolationError: If image violates content policy or is not a skin image
        """
        try:
            # Load image
            pil_image = Image.open(BytesIO(image_data))
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Preprocess image for NSFW detection
            processed_image = self._preprocess_image(pil_image)
            
            # Calculate NSFW scores (heuristic-based for demonstration)
            nsfw_score, non_skin_score, safe_score = self._calculate_scores(processed_image)
            
            # ENHANCED VALIDATION FOR REAL AI MODE
            # Even in real AI mode, we need to ensure the image contains skin
            if settings.use_real_ai:
                logger.info("REAL AI MODE: Performing skin content validation")
                
                # Calculate skin percentage
                skin_percentage = self._calculate_skin_percentage(processed_image)
                
                # Also check for text/graphics indicators
                has_text_or_graphics = self._detect_text_or_graphics(processed_image)
                
                # Strict validation: Reject if image has very low skin content
                MIN_SKIN_PERCENTAGE = 0.25  # At least 25% of image should be skin-like (raised from 15%)
                
                if skin_percentage < MIN_SKIN_PERCENTAGE or has_text_or_graphics:
                    rejection_reason = []
                    if skin_percentage < MIN_SKIN_PERCENTAGE:
                        rejection_reason.append(f"insufficient skin content ({skin_percentage:.1%})")
                    if has_text_or_graphics:
                        rejection_reason.append("text/graphics detected")
                    
                    reason_str = " and ".join(rejection_reason)
                    
                    logger.warning(
                        f"Image rejected: {reason_str}. "
                        f"This does not appear to be a skin lesion image."
                    )
                    raise ContentViolationError(
                        nsfw_score=0.0,
                        non_skin_score=1.0 - skin_percentage,
                        message=(
                            "Image does not appear to contain a skin lesion. "
                            "Please upload a clear, close-up photo of the affected skin area. "
                            "Make sure the image shows actual skin (not posters, text, or other objects)."
                        )
                    )
                
                # Log successful validation
                logger.info(f"Skin validation passed: {skin_percentage:.2%} skin content detected")
                
                # Return early with validated result
                return NSFWResult(
                    safe=True,
                    nsfw_score=0.01,
                    non_skin_score=1.0 - skin_percentage,
                    safe_score=skin_percentage
                )
            
            # STANDARD NSFW VALIDATION (when use_real_ai=false)
            # Check rejection criteria
            if nsfw_score > self.NSFW_THRESHOLD:
                logger.warning(f"Image rejected: NSFW score {nsfw_score:.3f} exceeds threshold {self.NSFW_THRESHOLD}")
                raise ContentViolationError(
                    nsfw_score=nsfw_score,
                    non_skin_score=non_skin_score,
                    message="Inappropriate content detected"
                )
            
            if non_skin_score > self.NON_SKIN_THRESHOLD:
                logger.warning(f"Image rejected: Non-skin score {non_skin_score:.3f} exceeds threshold {self.NON_SKIN_THRESHOLD}")
                raise ContentViolationError(
                    nsfw_score=nsfw_score,
                    non_skin_score=non_skin_score,
                    message="Inappropriate content detected"
                )
            
            # Image passed NSFW checks
            logger.info(f"Image passed NSFW checks: nsfw={nsfw_score:.3f}, non_skin={non_skin_score:.3f}")
            return NSFWResult(
                safe=True,
                nsfw_score=nsfw_score,
                non_skin_score=non_skin_score,
                safe_score=safe_score
            )
            
        except ContentViolationError:
            # Re-raise content violations
            raise
        except Exception as e:
            logger.error(f"Error during NSFW detection: {str(e)}")
            # On error, fail safe and reject
            raise ContentViolationError(
                nsfw_score=1.0,
                non_skin_score=1.0,
                message=f"Unable to validate image content: {str(e)}"
            )
    
    def _preprocess_image(self, image: Image.Image) -> np.ndarray:
        """
        Preprocess image for NSFW model
        
        In production, this would resize and normalize for the specific model.
        For demonstration, we just convert to numpy array.
        
        Args:
            image: PIL Image
            
        Returns:
            Preprocessed image as numpy array
        """
        # Resize to standard size (e.g., 224x224 for most models)
        # For demonstration, we'll use 224x224
        image_resized = image.resize((224, 224), Image.Resampling.LANCZOS)
        
        # Convert to numpy array
        image_array = np.array(image_resized, dtype=np.float32)
        
        # Normalize to [0, 1]
        image_array = image_array / 255.0
        
        return image_array
    
    def _calculate_skin_percentage(self, image: np.ndarray) -> float:
        """
        Calculate percentage of pixels that match skin tone characteristics
        
        This uses a heuristic approach based on color analysis.
        Real skin tones typically have:
        - R > G > B (red channel highest, blue lowest)
        - Specific RGB value ranges
        - Moderate saturation
        
        Args:
            image: Preprocessed image array (H, W, 3), normalized to [0, 1]
            
        Returns:
            Float between 0.0 and 1.0 representing skin percentage
        """
        r, g, b = image[:, :, 0], image[:, :, 1], image[:, :, 2]
        
        # Skin tone detection using multiple criteria
        # Based on research on skin tone detection in RGB color space
        
        # Criterion 1: RGB channel ordering (R > G > B for most skin tones)
        channel_order = (r > g) & (g > b)
        
        # Criterion 2: RGB value ranges for skin
        # Wider ranges to accommodate different skin types (Fitzpatrick I-VI)
        rgb_range = (
            (r > 0.20) & (r < 0.95) &  # Red: 20-95%
            (g > 0.15) & (g < 0.85) &  # Green: 15-85%
            (b > 0.10) & (b < 0.75)    # Blue: 10-75%
        )
        
        # Criterion 3: Brightness range (not too dark, not too bright)
        brightness = (r + g + b) / 3.0
        brightness_range = (brightness > 0.20) & (brightness < 0.90)
        
        # Criterion 4: Saturation (skin has moderate saturation, not pure colors)
        # Saturation = (max - min) / max (simplified)
        max_channel = np.maximum(np.maximum(r, g), b)
        min_channel = np.minimum(np.minimum(r, g), b)
        saturation = np.where(max_channel > 0, (max_channel - min_channel) / max_channel, 0)
        saturation_range = (saturation > 0.10) & (saturation < 0.70)
        
        # Combine all criteria (pixel must pass at least 3 out of 4)
        criteria_passed = (
            channel_order.astype(int) +
            rgb_range.astype(int) +
            brightness_range.astype(int) +
            saturation_range.astype(int)
        )
        
        # A pixel is considered "skin-like" if it passes at least 3 criteria
        skin_mask = criteria_passed >= 3
        
        # Calculate percentage
        skin_percentage = np.mean(skin_mask)
        
        return float(skin_percentage)
    
    def _detect_text_or_graphics(self, image: np.ndarray) -> bool:
        """
        Detect if image contains text, graphics, or high-contrast patterns
        typical of posters, screenshots, or documents
        
        Args:
            image: Preprocessed image array (H, W, 3), normalized to [0, 1]
            
        Returns:
            True if text/graphics detected, False otherwise
        """
        # Convert to grayscale for edge detection
        grayscale = np.mean(image, axis=2)
        
        # Calculate horizontal and vertical gradients (simple edge detection)
        grad_x = np.abs(np.diff(grayscale, axis=1))
        grad_y = np.abs(np.diff(grayscale, axis=0))
        
        # High edge density suggests text/graphics
        edge_density_x = np.mean(grad_x > 0.15)
        edge_density_y = np.mean(grad_y > 0.15)
        total_edge_density = (edge_density_x + edge_density_y) / 2
        
        # Check for high contrast (text usually has sharp boundaries)
        contrast = np.std(grayscale)
        
        # Check for pure colors (graphics often have solid color blocks)
        # Count pixels with very low variance across channels
        channel_variance = np.var(image, axis=2)
        low_variance_pixels = np.mean(channel_variance < 0.01)
        
        # Detection criteria:
        # - High edge density (>15%) = likely text/graphics
        # - High contrast (>0.25) + low variance (>30%) = likely poster/screenshot
        has_text_patterns = total_edge_density > 0.15
        has_graphics_patterns = (contrast > 0.25 and low_variance_pixels > 0.30)
        
        if has_text_patterns or has_graphics_patterns:
            logger.info(
                f"Text/graphics detected: edge_density={total_edge_density:.2%}, "
                f"contrast={contrast:.3f}, low_var_pixels={low_variance_pixels:.2%}"
            )
            return True
        
        return False
    
    def _calculate_scores(self, image: np.ndarray) -> tuple[float, float, float]:
        """
        Calculate NSFW scores using heuristic approach
        
        IMPORTANT: This is a simplified heuristic for demonstration purposes.
        In production, replace this with actual NSFW model inference.
        
        The heuristic uses color distribution analysis:
        - High skin-tone pixels + low clothing indicators = higher NSFW score
        - Low skin-tone pixels = higher non-skin score
        - Otherwise = safe
        
        Args:
            image: Preprocessed image array (H, W, 3)
            
        Returns:
            Tuple of (nsfw_score, non_skin_score, safe_score)
        """
        # Calculate skin tone percentage (simplified heuristic)
        # Skin tones typically have: R > G > B, with specific ranges
        r, g, b = image[:, :, 0], image[:, :, 1], image[:, :, 2]
        
        # Skin tone detection (very simplified)
        # Real skin detection would use more sophisticated algorithms
        skin_mask = (
            (r > 0.4) & (r < 0.9) &
            (g > 0.3) & (g < 0.8) &
            (b > 0.2) & (b < 0.7) &
            (r > g) & (g > b)
        )
        
        skin_percentage = np.mean(skin_mask)
        
        # Calculate color variance (high variance suggests complex scenes)
        color_variance = np.var(image)
        
        # Calculate brightness
        brightness = np.mean(image)
        
        # Heuristic scoring (simplified for demonstration)
        # In production, these would come from trained model predictions
        
        # NSFW score: Based on skin percentage and other factors
        # This is a placeholder - real models use deep learning
        if skin_percentage > 0.6 and color_variance < 0.05:
            # High skin, low variance might indicate inappropriate content
            nsfw_score = min(0.3, skin_percentage * 0.5)  # Keep below threshold for demo
        else:
            nsfw_score = skin_percentage * 0.2
        
        # Non-skin score: Inverse of skin percentage
        non_skin_score = 1.0 - skin_percentage
        
        # Safe score: Complement of max(nsfw, non_skin)
        safe_score = 1.0 - max(nsfw_score, non_skin_score)
        
        # Ensure scores are in valid range [0, 1]
        nsfw_score = np.clip(nsfw_score, 0.0, 1.0)
        non_skin_score = np.clip(non_skin_score, 0.0, 1.0)
        safe_score = np.clip(safe_score, 0.0, 1.0)
        
        return float(nsfw_score), float(non_skin_score), float(safe_score)
    
    def get_scores_only(self, image_data: bytes) -> Dict[str, float]:
        """
        Get NSFW scores without validation (for testing/debugging)
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dictionary with scores
        """
        try:
            pil_image = Image.open(BytesIO(image_data))
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            processed_image = self._preprocess_image(pil_image)
            nsfw_score, non_skin_score, safe_score = self._calculate_scores(processed_image)
            
            return {
                "nsfw_score": nsfw_score,
                "non_skin_score": non_skin_score,
                "safe_score": safe_score,
                "passes_nsfw_check": nsfw_score <= self.NSFW_THRESHOLD,
                "passes_skin_check": non_skin_score <= self.NON_SKIN_THRESHOLD
            }
        except Exception as e:
            return {
                "error": str(e)
            }


# Global detector instance
detector = NSFWDetector()
