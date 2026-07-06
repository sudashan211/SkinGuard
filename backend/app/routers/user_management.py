"""
User Management API endpoints for Admin
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from app.models import ErrorResponse
from app.dependencies import get_current_admin
from app.database import supabase
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/users", tags=["Admin - User Management"])


@router.get(
    "",
    response_model=List[dict],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - requires admin role"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def search_users(
    search: Optional[str] = Query(None, description="Search by name or email"),
    role: Optional[str] = Query(None, description="Filter by role: patient, doctor, admin"),
    user_status: Optional[str] = Query(None, description="Filter by status: active, suspended, banned"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_admin)
):
    """
    Search and filter users
    
    Args:
        search: Search term for name or email
        role: Filter by user role
        status: Filter by account status
        limit: Maximum results to return
        offset: Pagination offset
        current_user: Current authenticated admin
        
    Returns:
        List[dict]: List of users with profile information
    """
    try:
        # Demo mode
        if supabase is None:
            from app.demo_data import users_db, doctors_db, patient_data_db
            
            users = list(users_db.values())
            
            # Apply filters
            if role:
                users = [u for u in users if u.get("role") == role]
            
            if search:
                search_lower = search.lower()
                users = [u for u in users if 
                        search_lower in u.get("full_name", "").lower() or 
                        search_lower in u.get("email", "").lower()]
            
            # Add status (demo users are always active)
            for user in users:
                user["status"] = "active"
                user["last_login"] = datetime.utcnow().isoformat()
            
            return users[:limit]
        
        # Production mode
        query = supabase.table("profiles").select("*")
        
        # Apply filters
        if role:
            query = query.eq("role", role)
        
        if search:
            # Search in name or email
            query = query.or_(f"full_name.ilike.%{search}%,email.ilike.%{search}%")
        
        # Apply pagination
        query = query.range(offset, offset + limit - 1)
        
        result = query.execute()
        users = result.data if result.data else []
        
        # Add additional info (last login, status)
        for user in users:
            user["status"] = user.get("status", "active")
            # Get last login from audit logs
            login_result = supabase.table("audit_logs")\
                .select("created_at")\
                .eq("user_id", user["id"])\
                .eq("action", "login")\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
            
            if login_result.data:
                user["last_login"] = login_result.data[0]["created_at"]
            else:
                user["last_login"] = None
        
        return users
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to search users: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to search users",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.get(
    "/{user_id}",
    response_model=dict,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - requires admin role"},
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_user_details(
    user_id: str,
    current_user: dict = Depends(get_current_admin)
):
    """
    Get detailed user information
    
    Args:
        user_id: User UUID
        current_user: Current authenticated admin
        
    Returns:
        dict: Complete user profile with activity history
    """
    try:
        # Demo mode
        if supabase is None:
            from app.demo_data import get_user_by_id, get_doctor_by_user_id, get_patient_data_by_user_id
            
            user = get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"code": "USER_NOT_FOUND", "message": "User not found"}
                )
            
            # Add role-specific data
            if user["role"] == "doctor":
                user["doctor_profile"] = get_doctor_by_user_id(user_id)
            elif user["role"] == "patient":
                user["patient_data"] = get_patient_data_by_user_id(user_id)
            
            user["status"] = "active"
            user["last_login"] = datetime.utcnow().isoformat()
            user["total_screenings"] = 2 if user["role"] == "patient" else 0
            user["total_appointments"] = 2
            
            return user
        
        # Production mode
        user_result = supabase.table("profiles").select("*").eq("id", user_id).execute()
        
        if not user_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "USER_NOT_FOUND", "message": "User not found"}
            )
        
        user = user_result.data[0]
        
        # Get role-specific data
        if user["role"] == "doctor":
            doctor_result = supabase.table("doctors").select("*").eq("user_id", user_id).execute()
            user["doctor_profile"] = doctor_result.data[0] if doctor_result.data else None
        elif user["role"] == "patient":
            patient_result = supabase.table("patient_data").select("*").eq("user_id", user_id).execute()
            user["patient_data"] = patient_result.data[0] if patient_result.data else None
        
        # Get activity stats
        screenings_result = supabase.table("medical_reports").select("id", count="exact").eq("patient_id", user_id).execute()
        user["total_screenings"] = screenings_result.count if screenings_result.count else 0
        
        appointments_result = supabase.table("appointments").select("id", count="exact").or_(f"patient_id.eq.{user_id},doctor_id.eq.{user_id}").execute()
        user["total_appointments"] = appointments_result.count if appointments_result.count else 0
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user details: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to get user details",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.put(
    "/{user_id}/suspend",
    response_model=dict,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - requires admin role"},
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def suspend_user(
    user_id: str,
    reason: str = Query(..., description="Reason for suspension"),
    current_user: dict = Depends(get_current_admin)
):
    """
    Suspend a user account
    
    Args:
        user_id: User UUID
        reason: Reason for suspension
        current_user: Current authenticated admin
        
    Returns:
        dict: Updated user profile
    """
    try:
        # Demo mode
        if supabase is None:
            return {"message": "User suspended (demo mode)", "user_id": user_id}
        
        # Production mode
        update_data = {
            "status": "suspended",
            "suspended_at": datetime.utcnow().isoformat(),
            "suspended_by": current_user["id"],
            "suspension_reason": reason,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("profiles").update(update_data).eq("id", user_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "USER_NOT_FOUND", "message": "User not found"}
            )
        
        # Create notification
        notification_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "type": "account_suspended",
            "title": "Account Suspended",
            "message": f"Your account has been suspended. Reason: {reason}",
            "read": False,
            "created_at": datetime.utcnow().isoformat()
        }
        supabase.table("notifications").insert(notification_data).execute()
        
        logger.info(f"Admin {current_user['id']} suspended user {user_id}")
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to suspend user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to suspend user",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.put(
    "/{user_id}/unsuspend",
    response_model=dict
)
async def unsuspend_user(
    user_id: str,
    current_user: dict = Depends(get_current_admin)
):
    """Unsuspend a user account"""
    try:
        if supabase is None:
            return {"message": "User unsuspended (demo mode)", "user_id": user_id}
        
        update_data = {
            "status": "active",
            "suspended_at": None,
            "suspended_by": None,
            "suspension_reason": None,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("profiles").update(update_data).eq("id", user_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        return result.data[0]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{user_id}",
    response_model=dict
)
async def delete_user_account(
    user_id: str,
    current_user: dict = Depends(get_current_admin)
):
    """
    Permanently delete user account (GDPR compliance)
    
    Args:
        user_id: User UUID
        current_user: Current authenticated admin
        
    Returns:
        dict: Deletion confirmation
    """
    try:
        if supabase is None:
            return {"message": "User deleted (demo mode)", "user_id": user_id}
        
        # Use account deletion service
        from app.account_deletion import get_account_deletion_service
        from app.dependencies import get_audit_logger
        
        service = get_account_deletion_service()
        audit_logger = get_audit_logger()
        
        result = await service.delete_user_data(
            user_id=user_id,
            audit_logger=audit_logger,
            admin_id=current_user["id"]
        )
        
        logger.info(f"Admin {current_user['id']} deleted user {user_id}")
        return {"message": "User account deleted successfully", "user_id": user_id}
        
    except Exception as e:
        logger.error(f"Failed to delete user: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{user_id}/export",
    response_model=dict
)
async def export_user_data(
    user_id: str,
    current_user: dict = Depends(get_current_admin)
):
    """
    Export all user data (GDPR compliance)
    
    Args:
        user_id: User UUID
        current_user: Current authenticated admin
        
    Returns:
        dict: Complete user data export
    """
    try:
        if supabase is None:
            from app.demo_data import get_user_by_id
            user = get_user_by_id(user_id)
            return {"user_data": user, "export_date": datetime.utcnow().isoformat()}
        
        # Get all user data
        user_result = supabase.table("profiles").select("*").eq("id", user_id).execute()
        
        if not user_result.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        export_data = {
            "profile": user_result.data[0],
            "export_date": datetime.utcnow().isoformat(),
            "exported_by": current_user["id"]
        }
        
        # Get role-specific data
        user = user_result.data[0]
        
        if user["role"] == "patient":
            # Get patient data
            patient_result = supabase.table("patient_data").select("*").eq("user_id", user_id).execute()
            export_data["patient_data"] = patient_result.data[0] if patient_result.data else None
            
            # Get medical reports
            reports_result = supabase.table("medical_reports").select("*").eq("patient_id", user_id).execute()
            export_data["medical_reports"] = reports_result.data if reports_result.data else []
            
            # Get appointments
            appointments_result = supabase.table("appointments").select("*").eq("patient_id", user_id).execute()
            export_data["appointments"] = appointments_result.data if appointments_result.data else []
        
        elif user["role"] == "doctor":
            # Get doctor profile
            doctor_result = supabase.table("doctors").select("*").eq("user_id", user_id).execute()
            export_data["doctor_profile"] = doctor_result.data[0] if doctor_result.data else None
            
            # Get reviews
            if doctor_result.data:
                reviews_result = supabase.table("reviews").select("*").eq("doctor_id", doctor_result.data[0]["id"]).execute()
                export_data["reviews"] = reviews_result.data if reviews_result.data else []
        
        logger.info(f"Admin {current_user['id']} exported data for user {user_id}")
        return export_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export user data: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
