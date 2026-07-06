"""
System Health Monitoring API endpoints for Admin
"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.models import ErrorResponse
from app.dependencies import get_current_admin
from app.database import supabase
from datetime import datetime, timedelta
import uuid
import logging
import psutil
import time

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/system", tags=["Admin - System Health"])

# Track server start time
SERVER_START_TIME = time.time()


@router.get(
    "/health",
    response_model=dict,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - requires admin role"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_system_health(current_user: dict = Depends(get_current_admin)):
    """
    Get real-time system health metrics
    
    Returns:
        dict: System health information including CPU, memory, disk usage
    """
    try:
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Calculate uptime
        uptime_seconds = time.time() - SERVER_START_TIME
        uptime_hours = uptime_seconds / 3600
        uptime_days = uptime_hours / 24
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": {
                "seconds": int(uptime_seconds),
                "hours": round(uptime_hours, 2),
                "days": round(uptime_days, 2),
                "started_at": datetime.fromtimestamp(SERVER_START_TIME).isoformat()
            },
            "cpu": {
                "usage_percent": cpu_percent,
                "count": psutil.cpu_count(),
                "status": "healthy" if cpu_percent < 80 else "warning" if cpu_percent < 95 else "critical"
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "usage_percent": memory.percent,
                "status": "healthy" if memory.percent < 80 else "warning" if memory.percent < 95 else "critical"
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "usage_percent": disk.percent,
                "status": "healthy" if disk.percent < 80 else "warning" if disk.percent < 95 else "critical"
            }
        }
        
        # Determine overall status
        statuses = [
            health_data["cpu"]["status"],
            health_data["memory"]["status"],
            health_data["disk"]["status"]
        ]
        
        if "critical" in statuses:
            health_data["status"] = "critical"
        elif "warning" in statuses:
            health_data["status"] = "warning"
        else:
            health_data["status"] = "healthy"
        
        return health_data
        
    except Exception as e:
        logger.error(f"Failed to get system health: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to get system health",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.get(
    "/services",
    response_model=dict
)
async def get_service_status(current_user: dict = Depends(get_current_admin)):
    """
    Get status of all platform services
    
    Returns:
        dict: Status of database, AI models, email service, etc.
    """
    try:
        services = {
            "timestamp": datetime.utcnow().isoformat(),
            "services": []
        }
        
        # Check database
        db_status = "healthy"
        db_message = "Connected"
        try:
            if supabase is not None:
                # Try a simple query
                supabase.table("profiles").select("id").limit(1).execute()
            else:
                db_message = "Demo mode (in-memory)"
        except Exception as e:
            db_status = "unhealthy"
            db_message = f"Connection failed: {str(e)}"
        
        services["services"].append({
            "name": "Database",
            "status": db_status,
            "message": db_message,
            "checked_at": datetime.utcnow().isoformat()
        })
        
        # Check AI models
        ai_status = "healthy"
        ai_message = "Models loaded"
        try:
            from app.cancer_classifier import classifier
            if classifier is None:
                ai_status = "warning"
                ai_message = "Classifier not initialized"
            else:
                ai_message = "Cancer classifier ready"
        except Exception as e:
            ai_status = "warning"
            ai_message = f"Model check skipped: {str(e)[:100]}"
        
        services["services"].append({
            "name": "AI Models",
            "status": ai_status,
            "message": ai_message,
            "checked_at": datetime.utcnow().isoformat()
        })
        
        # Check email service
        email_status = "healthy"
        email_message = "Service available"
        try:
            from app.email_service import get_email_service
            email_service = get_email_service()
            if email_service is None:
                email_status = "warning"
                email_message = "Email service not configured"
        except Exception as e:
            email_status = "unhealthy"
            email_message = f"Service unavailable: {str(e)}"
        
        services["services"].append({
            "name": "Email Service",
            "status": email_status,
            "message": email_message,
            "checked_at": datetime.utcnow().isoformat()
        })
        
        # Overall status
        statuses = [s["status"] for s in services["services"]]
        if "unhealthy" in statuses:
            services["overall_status"] = "unhealthy"
        elif "warning" in statuses:
            services["overall_status"] = "warning"
        else:
            services["overall_status"] = "healthy"
        
        return services
        
    except Exception as e:
        logger.error(f"Failed to get service status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/metrics/performance",
    response_model=dict
)
async def get_performance_metrics(
    hours: int = 24,
    current_user: dict = Depends(get_current_admin)
):
    """
    Get performance metrics over time
    
    Args:
        hours: Number of hours to look back
        current_user: Current authenticated admin
        
    Returns:
        dict: Performance metrics including response times, error rates
    """
    try:
        if supabase is None:
            # Demo mode - return mock data
            return {
                "time_period_hours": hours,
                "average_response_time_ms": 245,
                "p95_response_time_ms": 580,
                "p99_response_time_ms": 1200,
                "total_requests": 15420,
                "successful_requests": 15180,
                "failed_requests": 240,
                "error_rate_percent": 1.56,
                "requests_per_minute": 10.7
            }
        
        # Production mode - get from metrics
        from app.metrics import metrics_collector
        
        metrics = await metrics_collector.get_performance_metrics(hours=hours)
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/alerts",
    response_model=list
)
async def get_system_alerts(current_user: dict = Depends(get_current_admin)):
    """
    Get active system alerts
    
    Returns:
        list: Active alerts and warnings
    """
    try:
        alerts = []
        
        # Check system health
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # CPU alerts
        if cpu_percent > 95:
            alerts.append({
                "id": str(uuid.uuid4()),
                "severity": "critical",
                "type": "cpu",
                "message": f"CPU usage critical: {cpu_percent}%",
                "value": cpu_percent,
                "threshold": 95,
                "created_at": datetime.utcnow().isoformat()
            })
        elif cpu_percent > 80:
            alerts.append({
                "id": str(uuid.uuid4()),
                "severity": "warning",
                "type": "cpu",
                "message": f"CPU usage high: {cpu_percent}%",
                "value": cpu_percent,
                "threshold": 80,
                "created_at": datetime.utcnow().isoformat()
            })
        
        # Memory alerts
        if memory.percent > 95:
            alerts.append({
                "id": str(uuid.uuid4()),
                "severity": "critical",
                "type": "memory",
                "message": f"Memory usage critical: {memory.percent}%",
                "value": memory.percent,
                "threshold": 95,
                "created_at": datetime.utcnow().isoformat()
            })
        elif memory.percent > 80:
            alerts.append({
                "id": str(uuid.uuid4()),
                "severity": "warning",
                "type": "memory",
                "message": f"Memory usage high: {memory.percent}%",
                "value": memory.percent,
                "threshold": 80,
                "created_at": datetime.utcnow().isoformat()
            })
        
        # Disk alerts
        if disk.percent > 95:
            alerts.append({
                "id": str(uuid.uuid4()),
                "severity": "critical",
                "type": "disk",
                "message": f"Disk usage critical: {disk.percent}%",
                "value": disk.percent,
                "threshold": 95,
                "created_at": datetime.utcnow().isoformat()
            })
        elif disk.percent > 80:
            alerts.append({
                "id": str(uuid.uuid4()),
                "severity": "warning",
                "type": "disk",
                "message": f"Disk usage high: {disk.percent}%",
                "value": disk.percent,
                "threshold": 80,
                "created_at": datetime.utcnow().isoformat()
            })
        
        return alerts
        
    except Exception as e:
        logger.error(f"Failed to get system alerts: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
