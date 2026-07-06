"""
FastAPI dependencies for authentication and authorization
Requirements: 1.2, 1.4, 1.5, 1.6, 6.5, 6.6
"""
from typing import Optional, Literal
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth import get_current_user_from_token
from app.audit import AuditLogger, create_audit_logger
from app.database import get_supabase_client
from app.config import settings


# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Dependency to get current authenticated user
    Requirements: 1.2
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        dict: Current user profile
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    user = get_current_user_from_token(token)
    return user


async def get_current_patient(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Dependency to ensure current user is a patient
    Requirements: 1.4
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        dict: Current patient user
        
    Raises:
        HTTPException: If user is not a patient
    """
    if current_user["role"] != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires patient role"
        )
    return current_user


async def get_current_doctor(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Dependency to ensure current user is a doctor
    Requirements: 1.5, 6.5
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        dict: Current doctor user
        
    Raises:
        HTTPException: If user is not a doctor
    """
    if current_user["role"] != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires doctor role"
        )
    return current_user


async def get_current_verified_doctor(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Dependency to ensure current user is a verified doctor
    Requirements: 1.5, 6.5, 6.6
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        dict: Current verified doctor user
        
    Raises:
        HTTPException: If user is not a verified doctor
    """
    if current_user["role"] != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires doctor role"
        )
    
    if not current_user["verified"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires verified doctor status"
        )
    
    return current_user


async def get_current_admin(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Dependency to ensure current user is an admin
    Requirements: 1.6
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        dict: Current admin user
        
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires admin role"
        )
    return current_user


def require_role(allowed_roles: list[str]):
    """
    Decorator factory to require specific roles
    Requirements: 1.4, 1.5, 1.6
    
    Args:
        allowed_roles: List of allowed roles
        
    Returns:
        Dependency function that checks role
    """
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of these roles: {', '.join(allowed_roles)}"
            )
        return current_user
    
    return role_checker


def require_verified_doctor():
    """
    Decorator to require verified doctor status
    Requirements: 6.5, 6.6
    
    Returns:
        Dependency function that checks verified doctor status
    """
    async def verified_doctor_checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] != "doctor":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This action requires doctor role"
            )
        
        if not current_user["verified"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This action requires verified doctor status. Please wait for admin approval."
            )
        
        return current_user
    
    return verified_doctor_checker


async def get_audit_logger() -> AuditLogger:
    """
    Dependency to get audit logger instance
    Requirements: 3.6, 18.4
    
    Returns:
        AuditLogger instance
    """
    if settings.demo_mode:
        # Demo mode - return a mock audit logger that doesn't require database
        return create_audit_logger(None)
    else:
        supabase = get_supabase_client()
        return create_audit_logger(supabase)


def get_client_ip(request: Request) -> Optional[str]:
    """
    Extract client IP address from request
    
    Args:
        request: FastAPI request object
        
    Returns:
        Client IP address or None
    """
    # Check for forwarded IP (behind proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    # Check for real IP
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to direct client
    if request.client:
        return request.client.host
    
    return None
