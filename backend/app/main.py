"""
SkinGuard FastAPI Application
Main application entry point
Requirements: 20.2, 20.4, 13.4
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.routers import auth, patient, reports, doctors, admin, appointments, reviews, notifications, skin_wiki, user_management, system_health, audit_logs, patients
from app.scheduler import start_scheduler, stop_scheduler
from app.metrics import metrics_collector
from app.exceptions import SkinGuardException, error_response
from datetime import datetime
from pathlib import Path
import uuid
import logging
import time

logger = logging.getLogger(__name__)


# Create FastAPI application
app = FastAPI(
    title="SkinGuard API",
    description="AI-Powered Skin Cancer Screening Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)


# Application lifecycle events
@app.on_event("startup")
async def startup_event():
    """
    Application startup event
    Start background job scheduler for urgent case escalation
    Verify encryption configuration
    """
    logger.info("Application starting up...")
    
    # Verify encryption configuration (Requirements: 18.1, 18.2)
    try:
        from app.encryption import verify_encryption_enabled
        verify_encryption_enabled()
        logger.info("Encryption verification passed - all connections secure")
    except Exception as e:
        logger.error(f"Encryption verification failed: {str(e)}", exc_info=True)
        logger.warning("Application starting with encryption warnings")
    
    try:
        start_scheduler()
        logger.info("Background scheduler started successfully")
    except Exception as e:
        logger.error(f"Failed to start background scheduler: {str(e)}", exc_info=True)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event
    Stop background job scheduler
    """
    logger.info("Application shutting down...")
    try:
        stop_scheduler()
        logger.info("Background scheduler stopped successfully")
    except Exception as e:
        logger.error(f"Error stopping background scheduler: {str(e)}", exc_info=True)


# Configure CORS
# Log CORS origins for debugging
logger.info(f"Configuring CORS with origins: {settings.cors_origins}")
# Temporarily use wildcard for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporary wildcard for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount uploads directory for local file storage
# Used in demo mode or when using PostgreSQL (not Supabase storage)
import os
use_local_storage = settings.demo_mode or os.getenv("DATABASE_URL", "").startswith("postgresql://")
if use_local_storage:
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
    logger.info("Mounted /uploads directory for local file serving")


# Metrics collection middleware (Requirements: 20.2, 20.4)
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """
    Middleware to track API metrics for all requests
    
    Property 64: API Metrics Tracking
    For any API endpoint call, the system should record response time 
    and success/error status in metrics storage.
    
    Requirements: 20.2, 20.4
    """
    start_time = time.time()
    response = None
    error_message = None
    status_code = 200
    
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception as e:
        error_message = str(e)
        status_code = 500
        raise
    finally:
        # Calculate response time
        response_time = time.time() - start_time
        
        # Extract user_id from request state if available
        user_id = getattr(request.state, "user_id", None)
        
        # Log metrics asynchronously (don't block response)
        try:
            await metrics_collector.log_api_metrics(
                endpoint=str(request.url.path),
                method=request.method,
                response_time=response_time,
                status_code=status_code,
                user_id=user_id,
                error_message=error_message
            )
        except Exception as log_error:
            # Don't fail the request if metrics logging fails
            logger.error(f"Failed to log metrics: {str(log_error)}")


# Include routers
app.include_router(auth.router)
app.include_router(patient.router)
app.include_router(reports.router)
app.include_router(doctors.router)
app.include_router(admin.router)
app.include_router(appointments.router)
app.include_router(patients.router)
app.include_router(reviews.router)
app.include_router(notifications.router)
app.include_router(skin_wiki.router)
app.include_router(user_management.router)
app.include_router(system_health.router)
app.include_router(audit_logs.router)


# Global exception handlers

@app.exception_handler(SkinGuardException)
async def skinguard_exception_handler(request: Request, exc: SkinGuardException):
    """
    Handle custom SkinGuard exceptions
    
    Requirements: 13.4 - Appropriate HTTP status codes for errors
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            code=exc.error_code,
            message=exc.detail.get("message", "An error occurred"),
            status_code=exc.status_code,
            details=exc.detail.get("details")
        )
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors
    
    Requirements: 13.4 - Appropriate HTTP status codes (400 for validation errors)
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
                "details": [
                    {
                        "loc": list(error.get("loc", [])),
                        "msg": str(error.get("msg", "")),
                        "type": str(error.get("type", ""))
                    }
                    for error in exc.errors()
                ],
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected errors
    
    Requirements: 13.4 - Appropriate HTTP status codes (500 for server errors)
    """
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=str(exc) if settings.api_reload else None  # Only show details in dev
        )
    )


# Health check endpoint
@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


# Encryption status endpoint (Requirements: 18.1, 18.2)
@app.get("/api/encryption-status", tags=["Health"])
async def encryption_status():
    """
    Get encryption status
    
    Returns information about data encryption at rest and in transit.
    Requirements: 18.1, 18.2
    """
    from app.encryption import get_encryption_service
    
    service = get_encryption_service()
    status = service.get_encryption_status()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        **status
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "SkinGuard API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


# Debug endpoint to check CORS configuration
@app.get("/api/debug/cors", tags=["Debug"])
async def debug_cors():
    """Debug endpoint to check CORS configuration"""
    return {
        "cors_origins": settings.cors_origins,
        "cors_origins_str": settings.cors_origins_str,
        "message": "Current CORS configuration"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
