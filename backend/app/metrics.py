"""
Performance Metrics Collection Service
Requirements: 20.1, 20.2, 20.4

Tracks API response times, AI processing times, and error rates for monitoring.
"""
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from functools import wraps
from app.config import settings

# Conditional imports based on demo mode
if not settings.demo_mode:
    from app.database import supabase
else:
    supabase = None

from app.notification_service import NotificationService

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collects and stores performance metrics for monitoring
    
    Tracks:
    - API response times (Requirement 20.2)
    - AI processing times separately for Gatekeeper and Medical_AI (Requirement 20.1)
    - Error rates (Requirement 20.2)
    - Performance alerts for slow responses >5s (Requirement 20.4)
    """
    
    def __init__(self):
        self.notification_service = NotificationService()
        self.alert_threshold = 5.0  # seconds (Requirement 20.4)
    
    async def log_api_metrics(
        self,
        endpoint: str,
        method: str,
        response_time: float,
        status_code: int,
        user_id: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> None:
        """
        Log API endpoint metrics
        
        Property 64: API Metrics Tracking
        For any API endpoint call, the system should record response time 
        and success/error status in metrics storage.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method (GET, POST, etc.)
            response_time: Response time in seconds
            status_code: HTTP status code
            user_id: Optional user identifier
            error_message: Optional error message if request failed
        
        Requirements: 20.2
        """
        if settings.demo_mode:
            # In demo mode, just log to console
            logger.info(
                f"[DEMO] API metrics: {method} {endpoint} - "
                f"{response_time:.3f}s - {status_code}"
            )
            return
        
        try:
            # Determine if this is an error
            is_error = status_code >= 400
            
            # Create metrics log entry
            metrics_data = {
                "action": "api_request",
                "resource_type": "api_endpoint",
                "resource_id": endpoint,
                "user_id": user_id,
                "metadata": {
                    "endpoint": endpoint,
                    "method": method,
                    "response_time": response_time,
                    "status_code": status_code,
                    "is_error": is_error,
                    "error_message": error_message
                },
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store in audit_logs table
            supabase.table("audit_logs").insert(metrics_data).execute()
            
            # Check for performance degradation (Requirement 20.4)
            if response_time > self.alert_threshold:
                await self._send_performance_alert(
                    endpoint=endpoint,
                    response_time=response_time,
                    method=method
                )
            
            logger.debug(
                f"API metrics logged: {method} {endpoint} - "
                f"{response_time:.3f}s - {status_code}"
            )
            
        except Exception as e:
            logger.error(f"Failed to log API metrics: {str(e)}", exc_info=True)
    
    async def log_ai_processing_metrics(
        self,
        report_id: str,
        gatekeeper_time: float,
        medical_ai_time: float,
        total_time: float,
        patient_id: Optional[str] = None
    ) -> None:
        """
        Log AI processing metrics with separate timing for Gatekeeper and Medical_AI
        
        Property 63: AI Processing Time Logging
        For any AI analysis, the system should log separate processing times 
        for NSFW Gatekeeper and Medical_AI (Swin + EfficientNet) stages.
        
        Args:
            report_id: Medical report identifier
            gatekeeper_time: NSFW filtering time in seconds
            medical_ai_time: Medical AI processing time in seconds
            total_time: Total processing time in seconds
            patient_id: Optional patient identifier
        
        Requirements: 20.1
        """
        try:
            # Create AI processing log entry
            log_data = {
                "action": "ai_processing",
                "resource_type": "medical_report",
                "resource_id": report_id,
                "user_id": patient_id,
                "metadata": {
                    "gatekeeper_time": gatekeeper_time,
                    "medical_ai_time": medical_ai_time,
                    "total_processing_time": total_time,
                    "timestamp": datetime.utcnow().isoformat()
                },
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store in audit_logs table (skip in demo mode)
            if not settings.demo_mode:
                supabase.table("audit_logs").insert(log_data).execute()
            
            logger.info(
                f"AI processing metrics logged for report {report_id}: "
                f"Gatekeeper={gatekeeper_time:.3f}s, Medical_AI={medical_ai_time:.3f}s, "
                f"Total={total_time:.3f}s"
            )
            
        except Exception as e:
            logger.error(f"Failed to log AI processing metrics: {str(e)}", exc_info=True)
    
    async def log_error_metrics(
        self,
        error_type: str,
        error_message: str,
        endpoint: Optional[str] = None,
        user_id: Optional[str] = None,
        stack_trace: Optional[str] = None
    ) -> None:
        """
        Log error metrics for tracking error rates
        
        Args:
            error_type: Type of error (e.g., "ValidationError", "AIProcessingError")
            error_message: Error message
            endpoint: Optional API endpoint where error occurred
            user_id: Optional user identifier
            stack_trace: Optional stack trace
        
        Requirements: 20.2
        """
        try:
            # Create error log entry
            error_data = {
                "action": "error_occurred",
                "resource_type": "error",
                "resource_id": error_type,
                "user_id": user_id,
                "metadata": {
                    "error_type": error_type,
                    "error_message": error_message,
                    "endpoint": endpoint,
                    "stack_trace": stack_trace,
                    "timestamp": datetime.utcnow().isoformat()
                },
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store in audit_logs table
            supabase.table("audit_logs").insert(error_data).execute()
            
            logger.debug(f"Error metrics logged: {error_type} - {error_message}")
            
        except Exception as e:
            logger.error(f"Failed to log error metrics: {str(e)}", exc_info=True)
    
    async def _send_performance_alert(
        self,
        endpoint: str,
        response_time: float,
        method: str
    ) -> None:
        """
        Send performance degradation alert to administrators
        
        Property 66: Performance Degradation Alerting
        For any API response taking longer than 5 seconds, the system should 
        send an alert notification to administrators.
        
        Args:
            endpoint: API endpoint that was slow
            response_time: Response time in seconds
            method: HTTP method
        
        Requirements: 20.4
        """
        try:
            # Get all admin users
            admins_result = supabase.table("profiles")\
                .select("id, email, full_name")\
                .eq("role", "admin")\
                .execute()
            
            if not admins_result.data:
                logger.warning("No admin users found to send performance alert")
                return
            
            # Send notification to each admin
            for admin in admins_result.data:
                notification_data = {
                    "user_id": admin["id"],
                    "type": "performance_alert",
                    "title": "Performance Degradation Detected",
                    "message": (
                        f"Slow response detected: {method} {endpoint} "
                        f"took {response_time:.2f}s (threshold: {self.alert_threshold}s)"
                    ),
                    "metadata": {
                        "endpoint": endpoint,
                        "method": method,
                        "response_time": response_time,
                        "threshold": self.alert_threshold,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    "read": False,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                # Store notification
                supabase.table("notifications").insert(notification_data).execute()
                
                # Send email notification
                await self.notification_service.send_email(
                    to_email=admin["email"],
                    subject="Performance Alert - SkinGuard",
                    body=(
                        f"Hello {admin['full_name']},\n\n"
                        f"A performance degradation has been detected:\n\n"
                        f"Endpoint: {method} {endpoint}\n"
                        f"Response Time: {response_time:.2f} seconds\n"
                        f"Threshold: {self.alert_threshold} seconds\n\n"
                        f"Please investigate the issue.\n\n"
                        f"SkinGuard System"
                    )
                )
            
            logger.info(
                f"Performance alert sent to {len(admins_result.data)} admins: "
                f"{method} {endpoint} - {response_time:.2f}s"
            )
            
        except Exception as e:
            logger.error(f"Failed to send performance alert: {str(e)}", exc_info=True)
    
    async def get_error_rate(self, hours: int = 24) -> Dict[str, Any]:
        """
        Calculate error rate for the specified time period
        
        Args:
            hours: Number of hours to look back
        
        Returns:
            Dict with error rate statistics
        
        Requirements: 20.2
        """
        try:
            from datetime import timedelta
            
            since_time = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
            
            # Get all API requests in time period
            all_requests = supabase.table("audit_logs")\
                .select("metadata")\
                .eq("action", "api_request")\
                .gte("created_at", since_time)\
                .execute()
            
            if not all_requests.data:
                return {
                    "total_requests": 0,
                    "error_count": 0,
                    "error_rate": 0.0,
                    "time_period_hours": hours
                }
            
            total_requests = len(all_requests.data)
            error_count = sum(
                1 for req in all_requests.data
                if req.get("metadata", {}).get("is_error", False)
            )
            
            error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0.0
            
            return {
                "total_requests": total_requests,
                "error_count": error_count,
                "error_rate": round(error_rate, 2),
                "time_period_hours": hours
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate error rate: {str(e)}", exc_info=True)
            return {
                "total_requests": 0,
                "error_count": 0,
                "error_rate": 0.0,
                "time_period_hours": hours,
                "error": str(e)
            }


# Global metrics collector instance
metrics_collector = MetricsCollector()


def track_api_metrics(endpoint_name: Optional[str] = None):
    """
    Decorator to automatically track API endpoint metrics
    
    Usage:
        @track_api_metrics("analyze_skin")
        async def analyze_skin_endpoint(...):
            ...
    
    Args:
        endpoint_name: Optional custom endpoint name
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            error_message = None
            status_code = 200
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error_message = str(e)
                status_code = getattr(e, 'status_code', 500)
                raise
            finally:
                response_time = time.time() - start_time
                
                # Extract endpoint name
                endpoint = endpoint_name or func.__name__
                
                # Log metrics
                try:
                    await metrics_collector.log_api_metrics(
                        endpoint=endpoint,
                        method="POST",  # Default, can be enhanced
                        response_time=response_time,
                        status_code=status_code,
                        error_message=error_message
                    )
                except Exception as log_error:
                    logger.error(f"Failed to log metrics: {str(log_error)}")
        
        return wrapper
    return decorator


async def log_ai_metrics(
    report_id: str,
    processing_times: Dict[str, float],
    patient_id: Optional[str] = None
) -> None:
    """
    Convenience function to log AI processing metrics
    
    Args:
        report_id: Medical report identifier
        processing_times: Dict with timing data
        patient_id: Optional patient identifier
    """
    gatekeeper_time = processing_times.get("nsfw_filtering", 0.0)
    medical_ai_time = (
        processing_times.get("lesion_detection", 0.0) +
        processing_times.get("cancer_classification", 0.0)
    )
    total_time = processing_times.get("total", 0.0)
    
    await metrics_collector.log_ai_processing_metrics(
        report_id=report_id,
        gatekeeper_time=gatekeeper_time,
        medical_ai_time=medical_ai_time,
        total_time=total_time,
        patient_id=patient_id
    )
