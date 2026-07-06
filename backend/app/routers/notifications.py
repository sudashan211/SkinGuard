"""
Notification endpoints
Requirements: 17.6
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models import NotificationResponse, NotificationListResponse, MarkNotificationReadRequest, ErrorResponse
from app.dependencies import get_current_user
from app.database import supabase
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"]
)


@router.get(
    "",
    response_model=NotificationListResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_user_notifications(
    current_user: dict = Depends(get_current_user)
):
    """
    Get all notifications for the current user
    
    Requirements: 17.6
    
    Returns:
        NotificationListResponse: List of notifications with unread count
    """
    try:
        user_id = current_user['id']
        
        # Fetch all notifications for user, ordered by created_at descending
        result = supabase.table('notifications')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .execute()
        
        notifications = result.data if result.data else []
        
        # Count unread notifications
        unread_count = sum(1 for n in notifications if not n.get('read', False))
        
        logger.info(f"Retrieved {len(notifications)} notifications for user {user_id} ({unread_count} unread)")
        
        return NotificationListResponse(
            notifications=[NotificationResponse(**n) for n in notifications],
            unread_count=unread_count
        )
        
    except Exception as e:
        logger.error(f"Failed to fetch notifications: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "NOTIFICATION_FETCH_ERROR",
                    "message": "Failed to fetch notifications",
                    "details": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )


@router.put(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Notification not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def mark_notification_read(
    notification_id: str,
    request: MarkNotificationReadRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark a notification as read or unread
    
    Requirements: 17.6
    
    Args:
        notification_id: Notification UUID
        request: Mark read request with read status
        
    Returns:
        NotificationResponse: Updated notification
    """
    try:
        user_id = current_user['id']
        
        # Verify notification belongs to current user
        check_result = supabase.table('notifications')\
            .select('*')\
            .eq('id', notification_id)\
            .eq('user_id', user_id)\
            .execute()
        
        if not check_result.data or len(check_result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOTIFICATION_NOT_FOUND",
                        "message": "Notification not found or does not belong to current user",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
            )
        
        # Update notification read status
        update_result = supabase.table('notifications')\
            .update({
                'read': request.read,
                'updated_at': datetime.utcnow().isoformat()
            })\
            .eq('id', notification_id)\
            .execute()
        
        if not update_result.data or len(update_result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "NOTIFICATION_UPDATE_ERROR",
                        "message": "Failed to update notification",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
            )
        
        updated_notification = update_result.data[0]
        logger.info(f"Notification {notification_id} marked as {'read' if request.read else 'unread'} by user {user_id}")
        
        return NotificationResponse(**updated_notification)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update notification: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "NOTIFICATION_UPDATE_ERROR",
                    "message": "Failed to update notification",
                    "details": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
