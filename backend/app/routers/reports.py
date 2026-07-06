"""
Medical Report Management API endpoints
Requirements: 4.4, 12.3, 13.2, 15.1, 15.2, 15.3, 15.4, 15.5, 20.1, 20.2
"""
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form, Request
from typing import Optional, List
from pathlib import Path
from app.models import (
    MedicalReportResponse,
    MedicalReportListResponse,
    ReportComparisonResponse,
    ErrorResponse
)
from app.dependencies import get_current_patient, get_current_user, get_audit_logger, get_client_ip
from app.config import settings
from app.analysis_pipeline import analyze_image, AIProcessingError
from app.image_quality import QualityError
from app.nsfw_filter import ContentViolationError
from app.audit import AuditLogger
from app.emergency_referral import get_emergency_referral_service
from app.metrics import log_ai_metrics
from datetime import datetime
import uuid
import logging

# Conditional imports based on demo mode
if not settings.demo_mode:
    from app.database import supabase
else:
    supabase = None

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Medical Reports"])


@router.post(
    "/analyze-skin",
    response_model=MedicalReportResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Analysis completed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid image or quality issues"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Content violation - inappropriate content detected"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def analyze_skin_image(
    request: Request,
    image: UploadFile = File(..., description="Skin lesion image"),
    body_location: Optional[str] = Form(None, description="Location of lesion on body"),
    sensations: Optional[str] = Form(None, description="Comma-separated sensations (itching, pain, burning, numbness, tingling, none)"),
    visual_changes: Optional[str] = Form(None, description="Comma-separated visual changes (color, size, shape, border, texture, bleeding, none)"),
    duration: Optional[str] = Form(None, description="Duration of symptoms (e.g., '2 weeks', '1 month')"),
    current_user: dict = Depends(get_current_patient),
    audit_logger: AuditLogger = Depends(get_audit_logger)
):
    """
    Upload and analyze skin lesion image with optional symptom data
    Requirements: 4.4, 5.5, 5.6, 12.3, 13.2
    
    Complete analysis pipeline:
    1. Quality validation (resolution, blur, brightness)
    2. NSFW filtering (Gatekeeper)
    3. Lesion detection (Swin Transformer)
    4. Cancer classification (EfficientNet-B7)
    5. Risk assessment
    6. Store results in medical_reports table with symptoms
    7. Upload image to Supabase Storage
    
    Args:
        request: FastAPI request object
        image: Uploaded image file (multipart/form-data)
        body_location: Optional body location (Step 1 of symptom wizard)
        sensations: Optional comma-separated sensations (Step 2 of symptom wizard)
        visual_changes: Optional comma-separated visual changes (Step 3 of symptom wizard)
        duration: Optional symptom duration
        current_user: Current authenticated patient user
        audit_logger: Audit logging service
        
    Returns:
        MedicalReportResponse: Complete analysis results with report ID
        
    Raises:
        HTTPException 400: If image quality is insufficient or symptom data is invalid
        HTTPException 403: If content violation detected
        HTTPException 500: If analysis or storage fails
    """
    request_id = str(uuid.uuid4())
    
    try:
        logger.info(f"Starting image analysis for patient {current_user['id']}, request_id: {request_id}")
        
        # Validate image file
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_FILE_TYPE",
                        "message": "File must be an image (JPEG, PNG, etc.)",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": request_id
                    }
                }
            )
        
        # Read image data
        image_data = await image.read()
        
        if not image_data or len(image_data) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "EMPTY_FILE",
                        "message": "Image file is empty",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": request_id
                    }
                }
            )
        
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(image_data) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "FILE_TOO_LARGE",
                        "message": f"File size exceeds maximum {max_size / (1024*1024):.0f}MB",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": request_id
                    }
                }
            )
        
        # Execute complete analysis pipeline
        logger.info(f"Executing analysis pipeline for request {request_id}")
        analysis_result = await analyze_image(image_data, patient_id=current_user['id'])
        
        # Upload image to storage (or save locally in demo mode)
        if settings.demo_mode:
            # Demo mode - save image locally and create URL
            logger.info(f"DEMO MODE: Saving image locally for request {request_id}")
            import os
            
            # Create uploads directory if it doesn't exist
            uploads_dir = Path("uploads") / current_user['id']
            uploads_dir.mkdir(parents=True, exist_ok=True)
            
            # Save image with unique filename
            image_filename = f"{uuid.uuid4()}.jpg"
            image_path = uploads_dir / image_filename
            
            with open(image_path, "wb") as f:
                f.write(image_data)
            
            # Create URL that points to local file
            image_url = f"/uploads/{current_user['id']}/{image_filename}"
        else:
            # Check if using PostgreSQL (local storage) or Supabase (cloud storage)
            import os
            use_postgres = os.getenv("DATABASE_URL", "").startswith("postgresql://")
            
            if use_postgres:
                # PostgreSQL mode - use local file storage
                logger.info(f"Using local file storage for request {request_id}")
                uploads_dir = Path("uploads") / current_user['id']
                uploads_dir.mkdir(parents=True, exist_ok=True)
                
                # Save image with unique filename
                image_filename = f"{uuid.uuid4()}.jpg"
                image_path = uploads_dir / image_filename
                
                with open(image_path, "wb") as f:
                    f.write(image_data)
                
                # Create URL that points to local file
                image_url = f"/uploads/{current_user['id']}/{image_filename}"
            else:
                # Supabase mode - upload to Supabase Storage
                logger.info(f"Uploading image to Supabase storage for request {request_id}")
                image_filename = f"{current_user['id']}/{uuid.uuid4()}.jpg"
                storage_result = supabase.storage.from_('medical-images').upload(
                    image_filename,
                    image_data,
                    file_options={"content-type": image.content_type}
                )
                
                # Get public URL for the image
                image_url = supabase.storage.from_('medical-images').get_public_url(image_filename)
        
        # Build and validate symptoms data (Requirements: 5.5, 5.6)
        symptoms_data = None
        if body_location or sensations or visual_changes or duration:
            try:
                # Parse comma-separated lists
                sensations_list = [s.strip() for s in sensations.split(',')] if sensations else []
                visual_changes_list = [v.strip() for v in visual_changes.split(',')] if visual_changes else []
                
                # Create and validate SymptomData model
                from app.models import SymptomData
                symptom_model = SymptomData(
                    body_location=body_location,
                    sensations=sensations_list,
                    visual_changes=visual_changes_list,
                    duration=duration
                )
                
                # Convert to dict for JSONB storage
                symptoms_data = symptom_model.dict(exclude_none=False)
                
                logger.info(f"Validated symptom data for request {request_id}: {symptoms_data}")
                
            except ValueError as e:
                # Validation error in symptom data - log warning but continue without symptoms
                # This allows the analysis to proceed even if symptom data is invalid
                logger.warning(f"Invalid symptom data for request {request_id}: {str(e)}")
                symptoms_data = None  # Don't store invalid symptom data
        
        # Determine status based on risk level
        report_status = "urgent" if analysis_result.risk_level == "urgent" else "safe"
        
        # Create medical report record
        report_id = str(uuid.uuid4())
        report_data = {
            "id": report_id,
            "patient_id": current_user['id'],
            "image_url": image_url,
            "ai_prediction": analysis_result.to_jsonb(),
            "symptoms": symptoms_data,
            "status": report_status,
            "risk_level": analysis_result.risk_level,
            "body_location": body_location,
            "consultation_notes": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if settings.demo_mode:
            # Demo mode - store in memory and return mock response
            logger.info(f"DEMO MODE: Storing report in memory for request {request_id}")
            from app import demo_data
            demo_data.create_medical_report(report_data)
            result_data = [report_data]  # Wrap in list to match Supabase response format
        else:
            # Production mode - store in database
            logger.info(f"Storing report to database for request {request_id}")
            result = supabase.table("medical_reports").insert(report_data).execute()
            
            if not result.data or len(result.data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": {
                            "code": "REPORT_CREATION_FAILED",
                            "message": "Failed to create medical report",
                            "timestamp": datetime.utcnow().isoformat(),
                            "request_id": request_id
                        }
                    }
                )
            result_data = result.data
        
        # Log AI processing metrics (Requirements: 20.1)
        await log_ai_metrics(
            report_id=report_id,
            processing_times=analysis_result.processing_times,
            patient_id=current_user['id']
        )
        
        # Log successful analysis
        client_ip = get_client_ip(request)
        await audit_logger.log_action(
            user_id=current_user['id'],
            action="image_analysis_completed",
            resource_type="medical_report",
            resource_id=report_id,
            metadata={
                "risk_level": analysis_result.risk_level,
                "processing_time": analysis_result.processing_times.get("total", 0),
                "status": report_status
            },
            ip_address=client_ip
        )
        
        # Handle urgent cases - notify nearest doctors (Requirements: 23.3)
        if report_status == "urgent":
            logger.info(f"Urgent case detected for report {report_id}, triggering emergency referral")
            
            try:
                # Get patient profile for full name
                patient_profile = supabase.table("profiles").select("full_name").eq("id", current_user['id']).execute()
                patient_name = patient_profile.data[0]["full_name"] if patient_profile.data else "Unknown Patient"
                
                # Get patient location from patient_data if available
                patient_data_result = supabase.table("patient_data").select("*").eq("user_id", current_user['id']).execute()
                patient_lat = None
                patient_lng = None
                # Note: patient_data doesn't have coordinates in current schema
                # In production, you might want to add location fields or use IP geolocation
                
                # Extract top prediction
                top_prediction = None
                if analysis_result.predictions:
                    top_pred = max(analysis_result.predictions, key=lambda p: p.get('probability', 0))
                    top_prediction = {
                        "type": top_pred.get('type', 'Unknown'),
                        "probability": top_pred.get('probability', 0.0)
                    }
                
                # Notify nearest doctors
                emergency_service = get_emergency_referral_service()
                doctors_found, emails_sent = await emergency_service.notify_nearest_doctors(
                    report_id=report_id,
                    patient_id=current_user['id'],
                    patient_name=patient_name,
                    patient_lat=patient_lat,
                    patient_lng=patient_lng,
                    risk_level=analysis_result.risk_level,
                    top_prediction=top_prediction
                )
                
                logger.info(
                    f"Emergency referral completed for report {report_id}: "
                    f"{emails_sent}/{doctors_found} doctors notified"
                )
                
                # Log emergency referral action
                await audit_logger.log_action(
                    user_id=current_user['id'],
                    action="emergency_referral_triggered",
                    resource_type="medical_report",
                    resource_id=report_id,
                    metadata={
                        "doctors_found": doctors_found,
                        "emails_sent": emails_sent,
                        "risk_level": analysis_result.risk_level,
                        "top_prediction": top_prediction
                    },
                    ip_address=client_ip
                )
                
            except Exception as e:
                # Log error but don't fail the request - report was created successfully
                logger.error(
                    f"Error during emergency referral for report {report_id}: {str(e)}",
                    exc_info=True
                )
        
        logger.info(f"Analysis completed successfully for request {request_id}, report_id: {report_id}")
        
        # Return complete report
        return MedicalReportResponse(**result_data[0])
        
    except QualityError as e:
        # Image quality insufficient
        logger.warning(f"Quality validation failed for request {request_id}: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": e.code,
                    "message": e.message,
                    "details": e.details if hasattr(e, 'details') else None,
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": request_id
                }
            }
        )
    except ContentViolationError as e:
        # NSFW content detected - audit log already created by pipeline
        logger.warning(f"Content violation detected for request {request_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": e.code,
                    "message": e.message,
                    "details": e.details,
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": request_id
                }
            }
        )
    except AIProcessingError as e:
        # AI processing failed
        logger.error(f"AI processing failed for request {request_id}: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": e.code,
                    "message": e.message,
                    "details": e.details,
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": request_id
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in image analysis for request {request_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred during image analysis",
                    "details": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": request_id
                }
            }
        )


@router.get(
    "/reports",
    response_model=List[MedicalReportListResponse],
    responses={
        200: {"description": "List of patient's medical reports"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - requires patient role"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_patient_reports(
    current_user: dict = Depends(get_current_patient)
):
    """
    Get patient's report history
    Requirements: 15.1, 15.2
    
    Returns all medical reports for the current patient, ordered by
    creation date descending (newest first).
    
    Args:
        current_user: Current authenticated patient user
        
    Returns:
        List[MedicalReportListResponse]: List of medical reports with summaries
        
    Raises:
        HTTPException 403: If user is not a patient
        HTTPException 500: If retrieval fails
    """
    request_id = str(uuid.uuid4())
    
    try:
        logger.info(f"Fetching reports for patient {current_user['id']}, request_id: {request_id}")
        
        # Fetch reports based on mode
        if settings.demo_mode:
            # Demo mode - get from in-memory storage
            from app.demo_data import get_reports_by_patient
            report_data = get_reports_by_patient(current_user['id'])
        else:
            # Production mode - get from database
            result = supabase.table("medical_reports")\
                .select("*")\
                .eq("patient_id", current_user['id'])\
                .order("created_at", desc=True)\
                .execute()
            report_data = result.data if result.data else []
        
        if not report_data:
            return []
        
        # Build response with summaries
        reports = []
        current_time = datetime.utcnow()
        
        for report in report_data:
            # Extract top prediction from ai_prediction
            top_prediction = None
            if report.get('ai_prediction') and report['ai_prediction'].get('predictions'):
                predictions = report['ai_prediction']['predictions']
                if predictions:
                    # Find prediction with highest probability
                    top = max(predictions, key=lambda p: p.get('probability', 0))
                    top_prediction = {
                        "type": top.get('type', 'Unknown'),
                        "probability": top.get('probability', 0.0)
                    }
            
            # Calculate if follow-up is needed (report older than 6 months = 180 days)
            # Requirement 15.6: Reports older than 6 months should suggest follow-up
            needs_followup = False
            try:
                created_at = datetime.fromisoformat(report['created_at'].replace('Z', '+00:00'))
                days_old = (current_time - created_at).days
                needs_followup = days_old > 180  # More than 6 months (180 days)
            except Exception as e:
                logger.warning(f"Error calculating follow-up status for report {report['id']}: {str(e)}")
                needs_followup = False
            
            report_item = {
                "id": report['id'],
                "patient_id": report['patient_id'],
                "image_url": report['image_url'],
                "risk_level": report['risk_level'],
                "status": report['status'],
                "body_location": report.get('body_location'),
                "created_at": report['created_at'],
                "top_prediction": top_prediction,
                "needs_followup": needs_followup
            }
            reports.append(MedicalReportListResponse(**report_item))
        
        logger.info(f"Retrieved {len(reports)} reports for patient {current_user['id']}")
        return reports
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching reports for request {request_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred while fetching reports",
                    "details": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": request_id
                }
            }
        )


@router.get(
    "/reports/{report_id}",
    response_model=MedicalReportResponse,
    responses={
        200: {"description": "Medical report details"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - not your report"},
        404: {"model": ErrorResponse, "description": "Report not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_report_by_id(
    report_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get single medical report by ID
    Requirements: 15.3
    
    Returns complete report details including full-resolution image,
    AI predictions, and symptoms.
    Accessible by patients (their own reports) and doctors (any report).
    
    Args:
        report_id: Report UUID
        current_user: Current authenticated user (patient or doctor)
        
    Returns:
        MedicalReportResponse: Complete medical report
        
    Raises:
        HTTPException 403: If patient tries to access another patient's report
        HTTPException 404: If report not found
        HTTPException 500: If retrieval fails
    """
    request_id = str(uuid.uuid4())
    
    try:
        logger.info(f"Fetching report {report_id} for patient {current_user['id']}, request_id: {request_id}")
        
        # Fetch report based on mode
        if settings.demo_mode:
            # Demo mode - get from in-memory storage
            from app.demo_data import get_report_by_id as get_demo_report
            report = get_demo_report(report_id)
            if not report:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": {
                            "code": "REPORT_NOT_FOUND",
                            "message": "Medical report not found",
                            "timestamp": datetime.utcnow().isoformat(),
                            "request_id": request_id
                        }
                    }
                )
        else:
            # Production mode - get from database
            result = supabase.table("medical_reports")\
                .select("*")\
                .eq("id", report_id)\
                .execute()
            
            if not result.data or len(result.data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": {
                            "code": "REPORT_NOT_FOUND",
                            "message": "Medical report not found",
                            "timestamp": datetime.utcnow().isoformat(),
                            "request_id": request_id
                        }
                    }
                )
            
            report = result.data[0]
        
        # Authorization check:
        # - Patients can only view their own reports
        # - Doctors can view any report
        # - Admins can view any report
        if current_user['role'] == 'patient' and report['patient_id'] != current_user['id']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You do not have permission to access this report",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": request_id
                    }
                }
            )
        
        logger.info(f"Retrieved report {report_id} successfully")
        return MedicalReportResponse(**report)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching report {report_id} for request {request_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred while fetching report",
                    "details": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": request_id
                }
            }
        )


@router.post(
    "/reports/{report_id}/compare/{other_report_id}",
    response_model=ReportComparisonResponse,
    responses={
        200: {"description": "Report comparison results"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - not your reports"},
        404: {"model": ErrorResponse, "description": "One or both reports not found"},
        400: {"model": ErrorResponse, "description": "Reports are not from same body location"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def compare_reports(
    report_id: str,
    other_report_id: str,
    current_user: dict = Depends(get_current_patient)
):
    """
    Compare two medical reports
    Requirements: 15.4, 15.5
    
    Compares two reports and detects changes in:
    - Lesion size (from hotspots)
    - Risk level
    - Top predicted cancer type
    
    Reports should be from the same body location for meaningful comparison.
    
    Args:
        report_id: First report UUID
        other_report_id: Second report UUID
        current_user: Current authenticated patient user
        
    Returns:
        ReportComparisonResponse: Comparison results with detected changes
        
    Raises:
        HTTPException 400: If reports are not from same body location
        HTTPException 403: If reports don't belong to current user
        HTTPException 404: If one or both reports not found
        HTTPException 500: If comparison fails
    """
    request_id = str(uuid.uuid4())
    
    try:
        logger.info(f"Comparing reports {report_id} and {other_report_id} for patient {current_user['id']}, request_id: {request_id}")
        
        # Fetch both reports based on mode
        if settings.demo_mode:
            # Demo mode - get from in-memory storage
            from app.demo_data import get_report_by_id as get_demo_report
            report1 = get_demo_report(report_id)
            report2 = get_demo_report(other_report_id)
        else:
            # Production mode - get from database
            result1 = supabase.table("medical_reports").select("*").eq("id", report_id).execute()
            result2 = supabase.table("medical_reports").select("*").eq("id", other_report_id).execute()
            
            if not result1.data or len(result1.data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": {
                            "code": "REPORT_NOT_FOUND",
                            "message": f"Report {report_id} not found",
                            "timestamp": datetime.utcnow().isoformat(),
                            "request_id": request_id
                        }
                    }
                )
            
            if not result2.data or len(result2.data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": {
                            "code": "REPORT_NOT_FOUND",
                            "message": f"Report {other_report_id} not found",
                            "timestamp": datetime.utcnow().isoformat(),
                            "request_id": request_id
                        }
                    }
                )
            
            report1 = result1.data[0]
            report2 = result2.data[0]
        
        # Check if reports exist (for demo mode)
        if not report1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "REPORT_NOT_FOUND",
                        "message": f"Report {report_id} not found",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": request_id
                    }
                }
            )
        
        if not report2:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "REPORT_NOT_FOUND",
                        "message": f"Report {other_report_id} not found",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": request_id
                    }
                }
            )
        
        # Verify ownership
        if report1['patient_id'] != current_user['id'] or report2['patient_id'] != current_user['id']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You do not have permission to access these reports",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": request_id
                    }
                }
            )
        
        # Check if same body location (optional warning, not blocking)
        location_match = report1.get('body_location') == report2.get('body_location')
        
        # Detect changes
        changes = {
            "same_body_location": location_match,
            "risk_level_change": {
                "from": report1['risk_level'],
                "to": report2['risk_level'],
                "changed": report1['risk_level'] != report2['risk_level']
            },
            "time_between_reports": None,
            "time_difference_days": 0,
            "lesion_changes": [],
            "prediction_changes": []
        }
        
        # Calculate time between reports
        try:
            date1 = datetime.fromisoformat(report1['created_at'].replace('Z', '+00:00'))
            date2 = datetime.fromisoformat(report2['created_at'].replace('Z', '+00:00'))
            time_diff = abs((date2 - date1).days)
            changes["time_between_reports"] = f"{time_diff} days"
            changes["time_difference_days"] = time_diff
        except:
            pass
        
        # Compare hotspots (lesion size)
        if report1.get('ai_prediction', {}).get('hotspots') and report2.get('ai_prediction', {}).get('hotspots'):
            hotspots1 = report1['ai_prediction']['hotspots']
            hotspots2 = report2['ai_prediction']['hotspots']
            
            # Simple comparison: count and average size
            avg_size1 = sum(h.get('width', 0) * h.get('height', 0) for h in hotspots1) / len(hotspots1) if hotspots1 else 0
            avg_size2 = sum(h.get('width', 0) * h.get('height', 0) for h in hotspots2) / len(hotspots2) if hotspots2 else 0
            
            changes["lesion_changes"] = {
                "count_change": {
                    "from": len(hotspots1),
                    "to": len(hotspots2),
                    "changed": len(hotspots1) != len(hotspots2)
                },
                "average_size_change": {
                    "from": round(avg_size1, 2),
                    "to": round(avg_size2, 2),
                    "changed": abs(avg_size1 - avg_size2) > 0.01
                }
            }
        
        # Compare predictions
        if report1.get('ai_prediction', {}).get('predictions') and report2.get('ai_prediction', {}).get('predictions'):
            preds1 = report1['ai_prediction']['predictions']
            preds2 = report2['ai_prediction']['predictions']
            
            # Find top predictions
            top1 = max(preds1, key=lambda p: p.get('probability', 0)) if preds1 else None
            top2 = max(preds2, key=lambda p: p.get('probability', 0)) if preds2 else None
            
            if top1 and top2:
                changes["prediction_changes"] = {
                    "top_prediction_change": {
                        "from": {
                            "type": top1.get('type', 'Unknown'),
                            "probability": top1.get('probability', 0.0)
                        },
                        "to": {
                            "type": top2.get('type', 'Unknown'),
                            "probability": top2.get('probability', 0.0)
                        },
                        "changed": top1.get('type') != top2.get('type')
                    }
                }
        
        logger.info(f"Comparison completed for reports {report_id} and {other_report_id}")
        
        return ReportComparisonResponse(
            report1=MedicalReportResponse(**report1),
            report2=MedicalReportResponse(**report2),
            changes=changes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing reports for request {request_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred while comparing reports",
                    "details": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": request_id
                }
            }
        )
