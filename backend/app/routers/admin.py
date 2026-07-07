"""
Admin Management API endpoints
Requirements: 6.3, 6.4, 10.1, 10.2, 10.3, 10.4, 10.5, 20.3, 20.5
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models import (
    DoctorResponse,
    DoctorVerificationRequest,
    FlaggedReportResponse,
    ErrorResponse
)
from app.dependencies import get_current_admin
from app.database import supabase
from app.analytics import AnalyticsService
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get(
    "/doctors/pending",
    response_model=list[DoctorResponse],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - requires admin role"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_pending_doctors(current_user: dict = Depends(get_current_admin)):
    """
    Get pending doctor applications for verification
    Requirements: 6.3, 10.1
    
    Returns all doctor applications where verified status is false.
    Admins use this endpoint to review and approve/reject doctor registrations.
    
    Filtering criteria:
    - role = 'doctor'
    - verified = false
    
    Args:
        current_user: Current authenticated admin user
        
    Returns:
        list[DoctorResponse]: List of pending doctor applications
        
    Raises:
        HTTPException 403: If user is not an admin
        HTTPException 500: If retrieval fails
    """
    try:
        # Demo mode
        if supabase is None:
            # In demo mode, all doctors are verified, so return empty list
            return []
        
        # Production mode
        # Step 1: Get all profiles where role = 'doctor' and verified = false
        profiles_result = supabase.table("profiles").select("*").eq("role", "doctor").eq("verified", False).execute()
        
        if not profiles_result.data or len(profiles_result.data) == 0:
            # No pending doctors - return empty list
            return []
        
        # Step 2: Get doctor records for these profiles
        pending_doctors = []
        
        for profile in profiles_result.data:
            # Get doctor record for this profile
            doctor_result = supabase.table("doctors").select("*").eq("user_id", profile["id"]).execute()
            
            if doctor_result.data and len(doctor_result.data) > 0:
                doctor_data = doctor_result.data[0]
                # Add verified status from profile
                doctor_data["verified"] = profile["verified"]
                pending_doctors.append(DoctorResponse(**doctor_data))
        
        return pending_doctors
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while retrieving pending doctors",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.put(
    "/doctors/{doctor_id}/verify",
    response_model=DoctorResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - requires admin role"},
        404: {"model": ErrorResponse, "description": "Doctor not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def verify_doctor(
    doctor_id: str,
    request: DoctorVerificationRequest,
    current_user: dict = Depends(get_current_admin)
):
    """
    Approve or reject doctor application
    Requirements: 6.3, 6.4, 10.1
    
    Updates the verified status in the profiles table for the doctor.
    - verified = true: Approve the doctor (grants access to patient reports)
    - verified = false: Reject the doctor (with rejection reason)
    
    Args:
        doctor_id: UUID of the doctor record
        request: Verification request with verified status and optional rejection reason
        current_user: Current authenticated admin user
        
    Returns:
        DoctorResponse: Updated doctor profile with new verification status
        
    Raises:
        HTTPException 400: If validation fails
        HTTPException 403: If user is not an admin
        HTTPException 404: If doctor not found
        HTTPException 500: If update fails
    """
    try:
        # Step 1: Get the doctor record
        doctor_result = supabase.table("doctors").select("*").eq("id", doctor_id).execute()
        
        if not doctor_result.data or len(doctor_result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DOCTOR_NOT_FOUND",
                    "message": "Doctor not found",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        doctor_data = doctor_result.data[0]
        user_id = doctor_data["user_id"]
        
        # Step 2: Update verified status in profiles table
        update_data = {
            "verified": request.verified,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        profile_result = supabase.table("profiles").update(update_data).eq("id", user_id).execute()
        
        if not profile_result.data or len(profile_result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "UPDATE_FAILED",
                    "message": "Failed to update doctor verification status",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        # Step 3: If rejected, log the rejection reason (could be stored in notifications or audit logs)
        if not request.verified and request.rejection_reason:
            # Create a notification for the doctor about rejection
            notification_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "type": "doctor_verification_rejected",
                "title": "Doctor Application Rejected",
                "message": f"Your doctor application has been rejected. Reason: {request.rejection_reason}",
                "read": False,
                "metadata": {
                    "rejection_reason": request.rejection_reason,
                    "rejected_by": current_user["id"],
                    "rejected_at": datetime.utcnow().isoformat()
                },
                "created_at": datetime.utcnow().isoformat()
            }
            
            supabase.table("notifications").insert(notification_data).execute()
        
        # Step 4: If approved, send welcome notification
        if request.verified:
            notification_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "type": "doctor_verification_approved",
                "title": "Doctor Application Approved",
                "message": "Congratulations! Your doctor application has been approved. You can now access patient reports.",
                "read": False,
                "metadata": {
                    "approved_by": current_user["id"],
                    "approved_at": datetime.utcnow().isoformat()
                },
                "created_at": datetime.utcnow().isoformat()
            }
            
            supabase.table("notifications").insert(notification_data).execute()
        
        # Step 5: Return updated doctor profile
        doctor_data["verified"] = request.verified
        doctor_data["updated_at"] = datetime.utcnow().isoformat()
        
        return DoctorResponse(**doctor_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during doctor verification",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )



@router.get(
    "/reports/flagged",
    response_model=List[FlaggedReportResponse],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - requires admin role"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_flagged_reports(current_user: dict = Depends(get_current_admin)):
    """
    Get all flagged medical reports for content moderation
    Requirements: 10.2, 10.4
    
    Returns all medical reports where status is "flagged", along with:
    - Image URL
    - NSFW scores from audit logs
    - Rejection reasons
    - Patient information
    
    Admins use this endpoint to review content that was rejected by the NSFW filter.
    
    Args:
        current_user: Current authenticated admin user
        
    Returns:
        List[FlaggedReportResponse]: List of flagged reports with metadata
        
    Raises:
        HTTPException 403: If user is not an admin
        HTTPException 500: If retrieval fails
    """
    try:
        # Demo mode
        if supabase is None:
            # In demo mode, no reports are flagged, return empty list
            return []
        
        # Production mode
        # Step 1: Get all flagged medical reports
        reports_result = supabase.table("medical_reports")\
            .select("*")\
            .eq("status", "flagged")\
            .order("created_at", desc=True)\
            .execute()
        
        if not reports_result.data or len(reports_result.data) == 0:
            # No flagged reports - return empty list
            return []
        
        flagged_reports = []
        
        for report in reports_result.data:
            # Step 2: Get patient information
            patient_result = supabase.table("profiles")\
                .select("id, email, full_name")\
                .eq("id", report["patient_id"])\
                .execute()
            
            patient_info = patient_result.data[0] if patient_result.data else {}
            
            # Step 3: Get audit log for this report to find NSFW scores and rejection reason
            # Look for audit logs related to this patient around the report creation time
            audit_result = supabase.table("audit_logs")\
                .select("*")\
                .eq("user_id", report["patient_id"])\
                .eq("action", "content_flagged")\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
            
            nsfw_score = None
            non_skin_score = None
            rejection_reason = "Content flagged by NSFW filter"
            
            if audit_result.data and len(audit_result.data) > 0:
                audit_log = audit_result.data[0]
                metadata = audit_log.get("metadata", {})
                nsfw_score = metadata.get("nsfw_score")
                non_skin_score = metadata.get("non_skin_score")
                rejection_reason = metadata.get("rejection_reason", rejection_reason)
            
            # Step 4: Build response
            flagged_report = FlaggedReportResponse(
                id=report["id"],
                patient_id=report["patient_id"],
                patient_email=patient_info.get("email"),
                patient_name=patient_info.get("full_name"),
                image_url=report["image_url"],
                nsfw_score=nsfw_score,
                non_skin_score=non_skin_score,
                rejection_reason=rejection_reason,
                created_at=report["created_at"],
                status=report["status"]
            )
            
            flagged_reports.append(flagged_report)
        
        logger.info(f"Retrieved {len(flagged_reports)} flagged reports for admin review")
        return flagged_reports
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve flagged reports: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while retrieving flagged reports",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )



# ============================================================================
# Skin-Wiki Content Management
# ============================================================================

@router.get(
    "/wiki/articles",
    response_model=List[dict],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - requires admin role"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_all_wiki_articles(current_user: dict = Depends(get_current_admin)):
    """
    Get all Skin-Wiki articles
    Requirements: 10.5, 16.6
    
    Returns all wiki articles for admin management.
    
    Args:
        current_user: Current authenticated admin user
        
    Returns:
        List[dict]: List of all wiki articles
        
    Raises:
        HTTPException 403: If user is not an admin
        HTTPException 500: If retrieval fails
    """
    try:
        # Demo mode
        if supabase is None:
            # Return empty list in demo mode
            return []
        
        # Production mode
        result = supabase.table("skin_wiki_articles")\
            .select("*")\
            .order("created_at", desc=True)\
            .execute()
        
        articles = result.data if result.data else []
        logger.info(f"Retrieved {len(articles)} wiki articles for admin {current_user['id']}")
        
        return articles
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve wiki articles: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while retrieving wiki articles",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.post(
    "/skin-wiki/articles",
    response_model=dict,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - requires admin role"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def create_skin_wiki_article(
    article_data: dict,
    current_user: dict = Depends(get_current_admin)
):
    """
    Create a new Skin-Wiki educational article
    Requirements: 10.5, 16.6
    
    Creates a new article with version tracking.
    
    Args:
        article_data: Article content including title, content, cancer_type, etc.
        current_user: Current authenticated admin user
        
    Returns:
        dict: Created article with version information
        
    Raises:
        HTTPException 403: If user is not an admin
        HTTPException 500: If creation fails
    """
    try:
        # Add metadata
        article_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        article = {
            "id": article_id,
            **article_data,
            "version": 1,
            "created_by": current_user["id"],
            "updated_by": current_user["id"],
            "created_at": now,
            "updated_at": now
        }
        
        # Store in database (using a skin_wiki_articles table)
        result = supabase.table("skin_wiki_articles").insert(article).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "ARTICLE_CREATE_ERROR",
                    "message": "Failed to create article",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        created_article = result.data[0]
        logger.info(f"Created Skin-Wiki article {article_id} by admin {current_user['id']}")
        
        return created_article
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create Skin-Wiki article: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while creating article",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.put(
    "/skin-wiki/articles/{article_id}",
    response_model=dict,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - requires admin role"},
        404: {"model": ErrorResponse, "description": "Article not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def update_skin_wiki_article(
    article_id: str,
    article_data: dict,
    current_user: dict = Depends(get_current_admin)
):
    """
    Update an existing Skin-Wiki article with version tracking
    Requirements: 10.5, 16.6
    
    Updates article content and increments version number.
    Maintains version history for tracking changes.
    
    Args:
        article_id: Article UUID
        article_data: Updated article content
        current_user: Current authenticated admin user
        
    Returns:
        dict: Updated article with new version information
        
    Raises:
        HTTPException 403: If user is not an admin
        HTTPException 404: If article not found
        HTTPException 500: If update fails
    """
    try:
        # Get current article
        current_result = supabase.table("skin_wiki_articles")\
            .select("*")\
            .eq("id", article_id)\
            .execute()
        
        if not current_result.data or len(current_result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "ARTICLE_NOT_FOUND",
                    "message": "Article not found",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        current_article = current_result.data[0]
        current_version = current_article.get("version", 1)
        
        # Create version history entry
        version_history = {
            "id": str(uuid.uuid4()),
            "article_id": article_id,
            "version": current_version,
            "content": current_article,
            "updated_by": current_article.get("updated_by"),
            "updated_at": current_article.get("updated_at"),
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Store version history
        supabase.table("skin_wiki_versions").insert(version_history).execute()
        
        # Update article with new content and incremented version
        now = datetime.utcnow().isoformat()
        update_data = {
            **article_data,
            "version": current_version + 1,
            "updated_by": current_user["id"],
            "updated_at": now
        }
        
        result = supabase.table("skin_wiki_articles")\
            .update(update_data)\
            .eq("id", article_id)\
            .execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "ARTICLE_UPDATE_ERROR",
                    "message": "Failed to update article",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        updated_article = result.data[0]
        logger.info(f"Updated Skin-Wiki article {article_id} to version {current_version + 1} by admin {current_user['id']}")
        
        return updated_article
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update Skin-Wiki article: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while updating article",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.get(
    "/skin-wiki/articles/{article_id}/versions",
    response_model=List[dict],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - requires admin role"},
        404: {"model": ErrorResponse, "description": "Article not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_article_version_history(
    article_id: str,
    current_user: dict = Depends(get_current_admin)
):
    """
    Get version history for a Skin-Wiki article
    Requirements: 16.6
    
    Returns all previous versions of an article for tracking changes.
    
    Args:
        article_id: Article UUID
        current_user: Current authenticated admin user
        
    Returns:
        List[dict]: List of article versions ordered by version number descending
        
    Raises:
        HTTPException 403: If user is not an admin
        HTTPException 404: If article not found
        HTTPException 500: If retrieval fails
    """
    try:
        # Verify article exists
        article_result = supabase.table("skin_wiki_articles")\
            .select("id")\
            .eq("id", article_id)\
            .execute()
        
        if not article_result.data or len(article_result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "ARTICLE_NOT_FOUND",
                    "message": "Article not found",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        # Get version history
        versions_result = supabase.table("skin_wiki_versions")\
            .select("*")\
            .eq("article_id", article_id)\
            .order("version", desc=True)\
            .execute()
        
        versions = versions_result.data if versions_result.data else []
        
        logger.info(f"Retrieved {len(versions)} versions for article {article_id}")
        return versions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve article versions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while retrieving article versions",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )



# ============================================================================
# Analytics Dashboard
# ============================================================================

@router.get(
    "/analytics",
    response_model=dict,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - requires admin role"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_analytics_dashboard(current_user: dict = Depends(get_current_admin)):
    """
    Get analytics dashboard metrics
    Requirements: 20.3, 20.5
    
    Property 65: Analytics Dashboard Metrics Completeness
    For any admin accessing the analytics dashboard, the displayed data should 
    include daily active users, total screenings performed, and average processing time.
    
    Property 67: Usage Pattern Statistics
    For any usage analysis query, the system should provide statistics on 
    most common cancer types detected and geographic distribution of users.
    
    Args:
        current_user: Current authenticated admin user
        
    Returns:
        dict: Analytics data including:
            - daily_active_users: Number of unique users active in last 24 hours
            - total_screenings: Total number of medical reports
            - average_processing_time: Average AI processing time in seconds
            - most_common_cancer_types: List of cancer types with counts
            - geographic_distribution: List of locations with user counts
        
    Raises:
        HTTPException 403: If user is not an admin
        HTTPException 500: If retrieval fails
    """
    try:
        analytics_service = AnalyticsService()
        
        # Get dashboard metrics (Property 65)
        dashboard_metrics = await analytics_service.get_dashboard_metrics()
        
        # Get usage pattern statistics (Property 67)
        usage_statistics = await analytics_service.get_usage_pattern_statistics()
        
        # Combine all analytics data
        analytics_data = {
            **dashboard_metrics,
            **usage_statistics
        }
        
        logger.info(f"Admin {current_user['id']} accessed analytics dashboard")
        return analytics_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve analytics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while retrieving analytics",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.get(
    "/analytics/debug",
    response_model=dict,
    responses={
        200: {"description": "Debug analytics data with raw database info"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - requires admin role"},
    }
)
async def get_analytics_debug(current_user: dict = Depends(get_current_admin)):
    """
    Debug endpoint to see raw analytics data and database state
    Shows actual report timestamps to help troubleshoot why daily active users might be 0
    
    Args:
        current_user: Current authenticated admin user
        
    Returns:
        dict: Debug data including:
            - current_time_utc: Current server time
            - cutoff_time_24h_ago: 24-hour cutoff timestamp
            - total_reports_all_time: Total number of reports
            - total_reports_last_24h: Reports created in last 24 hours
            - unique_patients_last_24h: Count of unique patients
            - most_recent_reports: List of most recent reports with timestamps
    """
    try:
        yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
        
        # Get all medical reports with timestamps
        all_reports = supabase.table("medical_reports")\
            .select("id, patient_id, created_at")\
            .order("created_at", desc=True)\
            .limit(100)\
            .execute()
        
        # Get recent reports (last 24 hours)
        recent_reports = supabase.table("medical_reports")\
            .select("id, patient_id, created_at")\
            .gte("created_at", yesterday)\
            .execute()
        
        # Count unique patients in last 24 hours
        unique_recent_patients = []
        if recent_reports.data:
            unique_recent_patients = list(set(r["patient_id"] for r in recent_reports.data))
        
        debug_data = {
            "current_time_utc": datetime.utcnow().isoformat(),
            "cutoff_time_24h_ago": yesterday,
            "total_reports_all_time": len(all_reports.data) if all_reports.data else 0,
            "total_reports_last_24h": len(recent_reports.data) if recent_reports.data else 0,
            "unique_patients_last_24h": len(unique_recent_patients),
            "unique_patient_ids": unique_recent_patients,
            "most_recent_reports": all_reports.data[:10] if all_reports.data else [],
            "recent_24h_reports": recent_reports.data if recent_reports.data else [],
        }
        
        logger.info(f"Admin {current_user['id']} accessed analytics debug endpoint")
        return debug_data
        
    except Exception as e:
        logger.error(f"Error in analytics debug: {str(e)}", exc_info=True)
        return {
            "error": str(e),
            "message": "Failed to fetch debug data",
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get(
    "/metrics/error-rate",
    response_model=dict,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - requires admin role"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_error_rate(
    hours: int = 24,
    current_user: dict = Depends(get_current_admin)
):
    """
    Get error rate statistics
    Requirements: 20.2
    
    Property 64: API Metrics Tracking
    For any API endpoint call, the system should record response time 
    and success/error status in metrics storage.
    
    Args:
        hours: Number of hours to look back (default: 24)
        current_user: Current authenticated admin user
        
    Returns:
        dict: Error rate statistics including:
            - total_requests: Total number of API requests
            - error_count: Number of failed requests
            - error_rate: Percentage of failed requests
            - time_period_hours: Time period analyzed
        
    Raises:
        HTTPException 403: If user is not an admin
        HTTPException 500: If retrieval fails
    """
    try:
        from app.metrics import metrics_collector
        
        # Get error rate statistics
        error_stats = await metrics_collector.get_error_rate(hours=hours)
        
        logger.info(
            f"Admin {current_user['id']} accessed error rate statistics: "
            f"{error_stats['error_rate']}% over {hours} hours"
        )
        
        return error_stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve error rate: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while retrieving error rate",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.get(
    "/reports/weekly-health",
    response_model=dict,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - requires admin role"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_weekly_health_report(current_user: dict = Depends(get_current_admin)):
    """
    Get weekly platform health report
    Requirements: 20.6
    
    Property 68: Weekly Health Report Generation
    For any week, the system should generate a summary report containing 
    platform health metrics (uptime, error rates, user activity).
    
    Args:
        current_user: Current authenticated admin user
        
    Returns:
        dict: Weekly health report including:
            - week_start: Start date of the week
            - week_end: End date of the week
            - total_users: Total number of users
            - active_users: Number of active users this week
            - total_screenings: Total screenings performed this week
            - error_rate: Error rate percentage for the week
            - average_response_time: Average API response time
            - top_cancer_types: Most detected cancer types this week
            - system_uptime: Estimated system uptime percentage
        
    Raises:
        HTTPException 403: If user is not an admin
        HTTPException 500: If retrieval fails
    """
    try:
        analytics_service = AnalyticsService()
        
        # Generate weekly health report
        health_report = await analytics_service.generate_weekly_health_report()
        
        logger.info(f"Admin {current_user['id']} accessed weekly health report")
        return health_report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate weekly health report: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while generating weekly health report",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )
