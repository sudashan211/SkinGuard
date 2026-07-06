"""
Content Filter Integration
Combines NSFW detection with audit logging
Requirements: 3.1, 3.2, 3.3, 3.4, 3.6, 18.4
"""
from typing import Optional
from app.nsfw_filter import NSFWDetector, ContentViolationError, NSFWResult
from app.audit import AuditLogger
import logging

logger = logging.getLogger(__name__)


class ContentFilter:
    """
    Content filtering service that combines NSFW detection with audit logging
    
    This is the Gatekeeper that validates all uploaded images before medical analysis.
    """
    
    def __init__(self, nsfw_detector: NSFWDetector, audit_logger: AuditLogger):
        """
        Initialize content filter
        
        Args:
            nsfw_detector: NSFW detection service
            audit_logger: Audit logging service
        """
        self.nsfw_detector = nsfw_detector
        self.audit_logger = audit_logger
    
    async def validate_image(
        self,
        image_data: bytes,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> NSFWResult:
        """
        Validate image for inappropriate content
        
        This is the main gatekeeper function that:
        1. Checks image for NSFW content
        2. Logs violations to audit trail
        3. Raises exception if content violates policy
        
        Args:
            image_data: Raw image bytes
            user_id: User ID (if authenticated)
            ip_address: Client IP address
            
        Returns:
            NSFWResult if image passes validation
            
        Raises:
            ContentViolationError: If image violates content policy
        """
        try:
            # Run NSFW detection
            result = self.nsfw_detector.check_nsfw(image_data)
            
            # Image passed - log successful validation
            logger.info(f"Image passed content validation for user {user_id}")
            
            return result
            
        except ContentViolationError as e:
            # Image failed - log violation to audit trail
            logger.warning(f"Content violation detected for user {user_id}: {e.message}")
            
            await self.audit_logger.log_content_violation(
                user_id=user_id,
                nsfw_score=e.nsfw_score,
                non_skin_score=e.non_skin_score,
                rejection_reason=e.message,
                ip_address=ip_address,
                additional_metadata={
                    "threshold_nsfw": self.nsfw_detector.NSFW_THRESHOLD,
                    "threshold_non_skin": self.nsfw_detector.NON_SKIN_THRESHOLD
                }
            )
            
            # Re-raise the exception to reject the upload
            raise


def create_content_filter(nsfw_detector: NSFWDetector, audit_logger: AuditLogger) -> ContentFilter:
    """
    Factory function to create content filter instance
    
    Args:
        nsfw_detector: NSFW detection service
        audit_logger: Audit logging service
        
    Returns:
        ContentFilter instance
    """
    return ContentFilter(nsfw_detector, audit_logger)
