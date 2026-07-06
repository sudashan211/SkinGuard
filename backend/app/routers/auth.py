"""
Authentication API endpoints
Requirements: 1.1, 1.2
"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.models import (
    UserSignupRequest,
    UserLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserProfile,
    UserProfileUpdate,
    ErrorResponse
)
from app.auth import register_user, authenticate_user, refresh_access_token, create_access_token, create_refresh_token
from app.dependencies import get_current_user
from app.config import settings
from datetime import datetime
import uuid


router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input or email already exists"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def signup(request: UserSignupRequest):
    """
    Register a new user with role assignment and auto-login
    Requirements: 1.1
    
    Creates a new user account with:
    - Unique UUID generation
    - Password hashing
    - Profile record creation
    - Role assignment (patient, doctor, admin)
    - Automatic login with JWT tokens
    
    Args:
        request: User signup request with email, password, full_name, and role
        
    Returns:
        dict: Authentication response with tokens and user profile
        
    Raises:
        HTTPException 400: If email already exists or validation fails
        HTTPException 500: If registration fails
    """
    try:
        print(f"[SIGNUP] Received request: email={request.email}, full_name={request.full_name}, role={request.role}")
        
        # Register user and create profile
        profile = register_user(
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            role=request.role
        )
        
        print(f"[SIGNUP] Successfully created profile: {profile.get('id')}")
        
        # Auto-login: Create JWT tokens
        token_data = {
            "sub": profile["id"],
            "email": request.email,
            "role": profile["role"],
            "verified": profile.get("verified", False)
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"sub": profile["id"]})
        
        # Return tokens and user profile for auto-login
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.jwt_access_token_expire_minutes * 60,
            "user": profile
        }
        
    except HTTPException as he:
        print(f"[SIGNUP] HTTPException: {he.status_code} - {he.detail}")
        raise
    except Exception as e:
        print(f"[SIGNUP] Exception: {type(e).__name__} - {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "REGISTRATION_ERROR",
                "message": "Failed to register user",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.post(
    "/login",
    response_model=dict,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def login(request: UserLoginRequest):
    """
    Authenticate user and generate JWT tokens
    Requirements: 1.2
    
    Authenticates user with email and password, then generates:
    - Access token (JWT) for API authentication
    - Refresh token for token renewal
    - User profile information
    
    Args:
        request: User login request with email and password
        
    Returns:
        dict: Authentication response with tokens and user profile
        
    Raises:
        HTTPException 401: If credentials are invalid
        HTTPException 500: If authentication fails
    """
    try:
        # Authenticate and get tokens
        auth_response = authenticate_user(
            email=request.email,
            password=request.password
        )
        
        return auth_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "AUTH_ERROR",
                "message": "Authentication failed",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Successfully logged out"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout current user
    Requirements: 1.2
    
    Logs out the current authenticated user. In a stateless JWT system,
    this is primarily handled client-side by discarding tokens.
    
    Args:
        current_user: Current authenticated user (from token)
        
    Returns:
        dict: Success message
    """
    # In a stateless JWT system, logout is handled client-side
    # The client should discard the tokens
    # For enhanced security, you could implement token blacklisting here
    
    return {
        "message": "Successfully logged out",
        "user_id": current_user["id"]
    }


@router.get(
    "/me",
    response_model=UserProfile,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "User not found"}
    }
)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user profile
    Requirements: 1.2
    
    Returns the profile information for the currently authenticated user.
    
    Args:
        current_user: Current authenticated user (from token)
        
    Returns:
        UserProfile: Current user's profile information
    """
    return UserProfile(**current_user)


@router.post(
    "/refresh",
    response_model=dict,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid refresh token"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    Requirements: 1.2
    
    Generates a new access token and refresh token using a valid refresh token.
    
    Args:
        request: Refresh token request
        
    Returns:
        dict: New access token and refresh token
        
    Raises:
        HTTPException 401: If refresh token is invalid or expired
        HTTPException 500: If token refresh fails
    """
    try:
        # Refresh tokens
        token_response = refresh_access_token(request.refresh_token)
        
        return token_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "TOKEN_REFRESH_ERROR",
                "message": "Failed to refresh token",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.put(
    "/profile",
    response_model=UserProfile,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def update_profile(
    update_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update current user profile
    Requirements: 1.3, 19.2
    
    Updates the profile information for the currently authenticated user.
    Supports updating:
    - full_name
    - avatar_url
    - language_preference
    
    Args:
        update_data: Profile update data
        current_user: Current authenticated user (from token)
        
    Returns:
        UserProfile: Updated user profile
        
    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 404: If user profile not found
        HTTPException 500: If update fails
    """
    try:
        from app.database import get_supabase_client
        
        supabase = get_supabase_client()
        
        # Build update data
        update_fields = {}
        if update_data.full_name is not None:
            update_fields['full_name'] = update_data.full_name
        if update_data.avatar_url is not None:
            update_fields['avatar_url'] = update_data.avatar_url
        if update_data.language_preference is not None:
            update_fields['language_preference'] = update_data.language_preference
        
        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "NO_UPDATE_DATA",
                    "message": "No valid update fields provided",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        # Add updated_at timestamp
        update_fields['updated_at'] = datetime.utcnow().isoformat()
        
        # Update profile
        response = supabase.table('profiles').update(update_fields).eq('id', current_user['id']).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "USER_NOT_FOUND",
                    "message": "User profile not found",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        return UserProfile(**response.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "PROFILE_UPDATE_ERROR",
                "message": "Failed to update profile",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Password changed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid current password"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def change_password(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Change user password
    
    Args:
        request: Contains current_password and new_password
        current_user: Current authenticated user (from token)
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException 400: If current password is incorrect
        HTTPException 401: If user is not authenticated
        HTTPException 500: If password change fails
    """
    try:
        from app.config import settings
        from app.database import get_supabase_client
        import app.demo_data as demo_data
        
        current_password = request.get("current_password")
        new_password = request.get("new_password")
        
        if not current_password or not new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "MISSING_FIELDS",
                    "message": "Both current_password and new_password are required",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        if settings.DEMO_MODE:
            # Demo mode: Simple password update
            user = demo_data.get_user_by_id(current_user["id"])
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "USER_NOT_FOUND",
                        "message": "User not found",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            
            # Verify current password
            if user.get("password") != current_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "INVALID_PASSWORD",
                        "message": "Current password is incorrect",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            
            # Update password
            user["password"] = new_password
            
            return {"message": "Password changed successfully"}
        else:
            # Production mode: Check if using PostgreSQL or Supabase
            import os
            USE_POSTGRES = os.getenv("DATABASE_URL", "").startswith("postgresql://")
            supabase = get_supabase_client()
            
            if USE_POSTGRES:
                # PostgreSQL mode: Update password_hash in profiles table
                import bcrypt
                
                # Get current password hash from database
                profile_result = supabase.table("profiles").select("password_hash").eq("id", current_user["id"]).execute()
                
                if not profile_result.data:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={
                            "code": "USER_NOT_FOUND",
                            "message": "User not found",
                            "timestamp": datetime.utcnow().isoformat(),
                            "request_id": str(uuid.uuid4())
                        }
                    )
                
                stored_hash = profile_result.data[0].get("password_hash")
                
                # Verify current password
                if not stored_hash or not bcrypt.checkpw(current_password.encode('utf-8'), stored_hash.encode('utf-8')):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "code": "INVALID_PASSWORD",
                            "message": "Current password is incorrect",
                            "timestamp": datetime.utcnow().isoformat(),
                            "request_id": str(uuid.uuid4())
                        }
                    )
                
                # Hash new password
                new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                # Update password hash in database
                supabase.table("profiles").update({"password_hash": new_hash}).eq("id", current_user["id"]).execute()
                
                return {"message": "Password changed successfully"}
            else:
                # Supabase Auth mode
                # Verify current password by attempting to sign in
                try:
                    supabase.auth.sign_in_with_password({
                        "email": current_user["email"],
                        "password": current_password
                    })
                except Exception:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "code": "INVALID_PASSWORD",
                            "message": "Current password is incorrect",
                            "timestamp": datetime.utcnow().isoformat(),
                            "request_id": str(uuid.uuid4())
                        }
                    )
                
                # Update password
                supabase.auth.update_user({"password": new_password})
                
                return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "PASSWORD_CHANGE_ERROR",
                "message": "Failed to change password",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.post(
    "/export-data",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Data export initiated"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def export_data(
    current_user: dict = Depends(get_current_user)
):
    """
    Request data export
    
    Initiates a data export request for the current user.
    In production, this would generate a downloadable file.
    In demo mode, returns a mock response.
    
    Args:
        current_user: Current authenticated user (from token)
        
    Returns:
        dict: Export information
        
    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 500: If export fails
    """
    try:
        from app.config import settings
        
        export_id = str(uuid.uuid4())
        
        if settings.DEMO_MODE:
            # Demo mode: Return mock response
            return {
                "message": "Data export request received. You will receive an email with download link shortly.",
                "export_id": export_id
            }
        else:
            # Production mode: Implement actual data export
            # This would typically:
            # 1. Gather all user data from database
            # 2. Generate a JSON/CSV file
            # 3. Store it temporarily
            # 4. Send email with download link
            return {
                "message": "Data export request received. You will receive an email with download link shortly.",
                "export_id": export_id
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "EXPORT_ERROR",
                "message": "Failed to initiate data export",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.delete(
    "/account",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Account deletion scheduled"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def delete_account(
    current_user: dict = Depends(get_current_user)
):
    """
    Schedule account deletion
    Requirements: 18.3
    
    Schedules the current user's account for permanent deletion after 30 days.
    During the grace period, the user can cancel the deletion request.
    
    All associated data will be deleted:
    - Medical reports
    - Patient data
    - Appointments
    - Reviews
    - Notifications
    
    Args:
        current_user: Current authenticated user (from token)
        
    Returns:
        dict: Deletion schedule information
        
    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 500: If scheduling fails
    """
    try:
        from app.config import settings
        from app.account_deletion import get_account_deletion_service
        from app.dependencies import get_audit_logger
        import app.demo_data as demo_data
        
        if settings.DEMO_MODE:
            # Demo mode: Simple deletion
            deletion_date = datetime.utcnow() + timedelta(days=30)
            return {
                "message": "Account deletion scheduled successfully",
                "deletion_scheduled_at": deletion_date.isoformat()
            }
        else:
            # Production mode: Use account deletion service
            service = get_account_deletion_service()
            audit_logger = get_audit_logger()
            
            result = await service.schedule_account_deletion(
                user_id=current_user["id"],
                audit_logger=audit_logger,
                ip_address=None
            )
            
            return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "DELETION_ERROR",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "DELETION_ERROR",
                "message": "Failed to schedule account deletion",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.post(
    "/account/cancel-deletion",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Account deletion cancelled"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        400: {"model": ErrorResponse, "description": "No deletion scheduled"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def cancel_account_deletion(
    current_user: dict = Depends(get_current_user)
):
    """
    Cancel scheduled account deletion
    Requirements: 18.3
    
    Cancels a pending account deletion request during the 30-day grace period.
    
    Args:
        current_user: Current authenticated user (from token)
        
    Returns:
        dict: Cancellation confirmation
        
    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 400: If no deletion is scheduled
        HTTPException 500: If cancellation fails
    """
    try:
        from app.account_deletion import get_account_deletion_service
        from app.dependencies import get_audit_logger
        
        service = get_account_deletion_service()
        audit_logger = get_audit_logger()
        
        result = await service.cancel_account_deletion(
            user_id=current_user["id"],
            audit_logger=audit_logger,
            ip_address=None
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "CANCELLATION_ERROR",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "CANCELLATION_ERROR",
                "message": "Failed to cancel account deletion",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )
