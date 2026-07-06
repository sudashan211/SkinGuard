"""
Custom Exception Classes
Provides structured error handling for the SkinGuard API

Requirements: 13.4 - Comprehensive error handling with appropriate HTTP status codes
"""
from fastapi import HTTPException, status
from typing import Optional, Dict, Any


class SkinGuardException(HTTPException):
    """Base exception for SkinGuard application"""
    
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[Any] = None
    ):
        self.error_code = error_code
        super().__init__(
            status_code=status_code,
            detail={
                "code": error_code,
                "message": message,
                "details": details
            }
        )


class ValidationError(SkinGuardException):
    """Raised when input validation fails"""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            message=message,
            details=details
        )


class AuthenticationError(SkinGuardException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR",
            message=message
        )


class AuthorizationError(SkinGuardException):
    """Raised when user lacks permission"""
    
    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR",
            message=message
        )


class ContentViolationError(SkinGuardException):
    """Raised when content violates NSFW policies"""
    
    def __init__(self, message: str = "Inappropriate content detected"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="CONTENT_VIOLATION",
            message=message
        )


class NotFoundError(SkinGuardException):
    """Raised when resource is not found"""
    
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message=f"{resource} not found"
        )


class ConflictError(SkinGuardException):
    """Raised when resource already exists"""
    
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            message=message
        )


class RateLimitError(SkinGuardException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, message: str = "Too many requests. Please try again later."):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            message=message
        )


class ImageQualityError(SkinGuardException):
    """Raised when image quality is insufficient"""
    
    def __init__(self, message: str, guidance: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="IMAGE_QUALITY_ERROR",
            message=message,
            details={"guidance": guidance} if guidance else None
        )


class AIProcessingError(SkinGuardException):
    """Raised when AI processing fails"""
    
    def __init__(self, message: str = "AI processing failed", details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="AI_PROCESSING_ERROR",
            message=message,
            details=details
        )


class DatabaseError(SkinGuardException):
    """Raised when database operation fails"""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            message=message
        )


class ExternalServiceError(SkinGuardException):
    """Raised when external service call fails"""
    
    def __init__(self, service: str, message: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="EXTERNAL_SERVICE_ERROR",
            message=message or f"{service} service is currently unavailable"
        )


class StorageError(SkinGuardException):
    """Raised when file storage operation fails"""
    
    def __init__(self, message: str = "File storage operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="STORAGE_ERROR",
            message=message
        )


# Error response helpers
def error_response(
    code: str,
    message: str,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    details: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Create a standardized error response
    
    Requirements: 13.5 - JSON format for structured data
    """
    from datetime import datetime
    import uuid
    
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": str(uuid.uuid4())
        }
    }


def success_response(
    data: Any,
    message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a standardized success response
    
    Requirements: 13.5 - JSON format for structured data
    """
    from datetime import datetime
    
    response = {
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if message:
        response["message"] = message
    
    return response
