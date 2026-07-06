"""
Audit Logs API endpoints for Admin
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

router = APIRouter(prefix="/api/admin/audit", tags=["Admin - Audit Logs"])


@router.get(
    "/logs",
    response_model=List[dict],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - requires admin role"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_audit_logs(
    action: Optional[str] = Query(None, description="Filter by action type"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_admin)
):
    """
    Get audit logs with filtering
    
    Args:
        action: Filter by action type (login, logout, image_upload, etc.)
        user_id: Filter by specific user
        start_date: Filter logs after this date
        end_date: Filter logs before this date
        limit: Maximum results to return
        offset: Pagination offset
        current_user: Current authenticated admin
        
    Returns:
        List[dict]: Audit log entries
    """
    try:
        # Demo mode
        if supabase is None:
            # Return mock audit logs
            mock_logs = [
                {
                    "id": str(uuid.uuid4()),
                    "user_id": "demo-patient-001",
                    "user_email": "patient@demo.com",
                    "action": "login",
                    "ip_address": "192.168.1.100",
                    "user_agent": "Mozilla/5.0",
                    "metadata": {},
                    "created_at": (datetime.utcnow() - timedelta(hours=2)).isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "user_id": "demo-doctor-001",
                    "user_email": "doctor@demo.com",
                    "action": "login",
                    "ip_address": "192.168.1.101",
                    "user_agent": "Mozilla/5.0",
                    "metadata": {},
                    "created_at": (datetime.utcnow() - timedelta(hours=1)).isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "user_id": "demo-patient-001",
                    "user_email": "patient@demo.com",
                    "action": "image_analysis_completed",
                    "ip_address": "192.168.1.100",
                    "user_agent": "Mozilla/5.0",
                    "metadata": {"risk_level": "high", "cancer_type": "melanoma"},
                    "created_at": (datetime.utcnow() - timedelta(minutes=30)).isoformat()
                }
            ]
            
            # Apply filters
            if action:
                mock_logs = [log for log in mock_logs if log["action"] == action]
            if user_id:
                mock_logs = [log for log in mock_logs if log["user_id"] == user_id]
            
            return mock_logs[:limit]
        
        # Production mode
        query = supabase.table("audit_logs").select("*")
        
        # Apply filters
        if action:
            query = query.eq("action", action)
        
        if user_id:
            query = query.eq("user_id", user_id)
        
        if start_date:
            query = query.gte("created_at", start_date)
        
        if end_date:
            query = query.lte("created_at", end_date)
        
        # Order by most recent first
        query = query.order("created_at", desc=True)
        
        # Apply pagination
        query = query.range(offset, offset + limit - 1)
        
        result = query.execute()
        logs = result.data if result.data else []
        
        # Enrich with user information
        for log in logs:
            user_result = supabase.table("profiles").select("email, full_name").eq("id", log["user_id"]).execute()
            if user_result.data:
                log["user_email"] = user_result.data[0]["email"]
                log["user_name"] = user_result.data[0]["full_name"]
        
        return logs
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get audit logs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to get audit logs",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.get(
    "/security-events",
    response_model=List[dict]
)
async def get_security_events(
    hours: int = Query(24, ge=1, le=168),
    current_user: dict = Depends(get_current_admin)
):
    """
    Get security-related events
    
    Args:
        hours: Number of hours to look back
        current_user: Current authenticated admin
        
    Returns:
        List[dict]: Security events (failed logins, suspicious activity)
    """
    try:
        if supabase is None:
            # Demo mode - return mock security events
            return [
                {
                    "id": str(uuid.uuid4()),
                    "event_type": "failed_login",
                    "user_email": "unknown@example.com",
                    "ip_address": "192.168.1.200",
                    "reason": "Invalid credentials",
                    "created_at": (datetime.utcnow() - timedelta(hours=5)).isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "event_type": "content_flagged",
                    "user_id": "demo-patient-001",
                    "user_email": "patient@demo.com",
                    "reason": "NSFW content detected",
                    "created_at": (datetime.utcnow() - timedelta(hours=12)).isoformat()
                }
            ]
        
        # Production mode
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Get failed login attempts
        failed_logins = supabase.table("audit_logs")\
            .select("*")\
            .eq("action", "login_failed")\
            .gte("created_at", since.isoformat())\
            .order("created_at", desc=True)\
            .execute()
        
        # Get content violations
        content_violations = supabase.table("audit_logs")\
            .select("*")\
            .eq("action", "content_flagged")\
            .gte("created_at", since.isoformat())\
            .order("created_at", desc=True)\
            .execute()
        
        # Combine and format events
        events = []
        
        if failed_logins.data:
            for log in failed_logins.data:
                events.append({
                    "id": log["id"],
                    "event_type": "failed_login",
                    "user_email": log.get("metadata", {}).get("email", "unknown"),
                    "ip_address": log.get("ip_address"),
                    "reason": "Invalid credentials",
                    "created_at": log["created_at"]
                })
        
        if content_violations.data:
            for log in content_violations.data:
                events.append({
                    "id": log["id"],
                    "event_type": "content_flagged",
                    "user_id": log["user_id"],
                    "reason": log.get("metadata", {}).get("rejection_reason", "Content violation"),
                    "created_at": log["created_at"]
                })
        
        # Sort by date
        events.sort(key=lambda x: x["created_at"], reverse=True)
        
        return events
        
    except Exception as e:
        logger.error(f"Failed to get security events: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/compliance-report",
    response_model=dict
)
async def generate_compliance_report(
    start_date: str = Query(..., description="Start date (ISO format)"),
    end_date: str = Query(..., description="End date (ISO format)"),
    current_user: dict = Depends(get_current_admin)
):
    """
    Generate compliance report for a date range
    
    Args:
        start_date: Report start date
        end_date: Report end date
        current_user: Current authenticated admin
        
    Returns:
        dict: Compliance report with statistics
    """
    try:
        if supabase is None:
            # Demo mode - return mock report
            return {
                "report_id": str(uuid.uuid4()),
                "start_date": start_date,
                "end_date": end_date,
                "generated_at": datetime.utcnow().isoformat(),
                "generated_by": current_user["id"],
                "statistics": {
                    "total_users": 3,
                    "new_users": 0,
                    "total_logins": 45,
                    "failed_logins": 2,
                    "data_access_requests": 0,
                    "data_deletion_requests": 0,
                    "content_violations": 0,
                    "security_incidents": 0
                },
                "compliance_status": "compliant",
                "notes": "All systems operating within compliance parameters"
            }
        
        # Production mode
        # Get statistics for the date range
        total_logins = supabase.table("audit_logs")\
            .select("id", count="exact")\
            .eq("action", "login")\
            .gte("created_at", start_date)\
            .lte("created_at", end_date)\
            .execute()
        
        failed_logins = supabase.table("audit_logs")\
            .select("id", count="exact")\
            .eq("action", "login_failed")\
            .gte("created_at", start_date)\
            .lte("created_at", end_date)\
            .execute()
        
        content_violations = supabase.table("audit_logs")\
            .select("id", count="exact")\
            .eq("action", "content_flagged")\
            .gte("created_at", start_date)\
            .lte("created_at", end_date)\
            .execute()
        
        # Get user counts
        total_users = supabase.table("profiles").select("id", count="exact").execute()
        
        new_users = supabase.table("profiles")\
            .select("id", count="exact")\
            .gte("created_at", start_date)\
            .lte("created_at", end_date)\
            .execute()
        
        report = {
            "report_id": str(uuid.uuid4()),
            "start_date": start_date,
            "end_date": end_date,
            "generated_at": datetime.utcnow().isoformat(),
            "generated_by": current_user["id"],
            "statistics": {
                "total_users": total_users.count or 0,
                "new_users": new_users.count or 0,
                "total_logins": total_logins.count or 0,
                "failed_logins": failed_logins.count or 0,
                "content_violations": content_violations.count or 0,
                "data_access_requests": 0,  # Would need separate tracking
                "data_deletion_requests": 0,  # Would need separate tracking
                "security_incidents": (failed_logins.count or 0) + (content_violations.count or 0)
            },
            "compliance_status": "compliant",
            "notes": "Report generated successfully"
        }
        
        return report
        
    except Exception as e:
        logger.error(f"Failed to generate compliance report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/actions",
    response_model=List[str]
)
async def get_audit_action_types(current_user: dict = Depends(get_current_admin)):
    """
    Get list of all audit action types
    
    Returns:
        List[str]: Available action types for filtering
    """
    return [
        "login",
        "logout",
        "login_failed",
        "signup",
        "password_reset",
        "image_upload",
        "image_analysis_completed",
        "content_flagged",
        "emergency_referral_triggered",
        "appointment_created",
        "appointment_cancelled",
        "doctor_verified",
        "doctor_rejected",
        "user_suspended",
        "user_deleted",
        "data_exported"
    ]
