"""
Patient Profile Management API endpoints
Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
"""
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Request
from app.models import (
    PatientDataCreate,
    PatientDataUpdate,
    PatientDataResponse,
    ErrorResponse
)
from app.dependencies import get_current_patient, get_audit_logger, get_client_ip
from app.database import supabase
from app.nsfw_filter import detector as nsfw_detector, ContentViolationError
from app.content_filter import create_content_filter
from app.audit import AuditLogger
from datetime import datetime
import uuid


router = APIRouter(prefix="/api/patient", tags=["Patient"])


@router.post(
    "/profile",
    response_model=PatientDataResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input or patient data already exists"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - requires patient role"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def create_patient_profile(
    request: PatientDataCreate,
    current_user: dict = Depends(get_current_patient)
):
    """
    Create patient health profile
    Requirements: 2.1, 2.2, 2.3, 2.4
    
    Creates a new patient_data record with:
    - Age validation (1-120)
    - Fitzpatrick scale validation (I-VI)
    - Family history storage without truncation
    - Link to user profile
    
    Args:
        request: Patient data creation request
        current_user: Current authenticated patient user
        
    Returns:
        PatientDataResponse: Created patient data profile
        
    Raises:
        HTTPException 400: If validation fails or patient data already exists
        HTTPException 403: If user is not a patient
        HTTPException 500: If creation fails
    """
    try:
        from app.config import settings
        import app.demo_data as demo_data
        
        if settings.demo_mode:
            # Demo mode: Use in-memory storage
            existing = demo_data.get_patient_data_by_user_id(current_user["id"])
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "PATIENT_DATA_EXISTS",
                        "message": "Patient data already exists for this user. Use PUT to update.",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            
            # Create patient data
            patient_data = demo_data.create_patient_data({
                "user_id": current_user["id"],
                "age": request.age,
                "skin_type": request.skin_type,
                "family_history": request.family_history or ""
            })
            
            return PatientDataResponse(**patient_data)
        else:
            # Production mode: Use Supabase
            # Check if patient data already exists for this user
            existing = supabase.table("patient_data").select("*").eq("user_id", current_user["id"]).execute()
            
            if existing.data and len(existing.data) > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "PATIENT_DATA_EXISTS",
                        "message": "Patient data already exists for this user. Use PUT to update.",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            
            # Create patient data record
            patient_data = {
                "id": str(uuid.uuid4()),
                "user_id": current_user["id"],
                "age": request.age,
                "skin_type": request.skin_type,
                "family_history": request.family_history,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Insert into database
            result = supabase.table("patient_data").insert(patient_data).execute()
            
            if not result.data or len(result.data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "code": "CREATION_FAILED",
                        "message": "Failed to create patient data",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            
            return PatientDataResponse(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.put(
    "/profile",
    response_model=PatientDataResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - requires patient role"},
        404: {"model": ErrorResponse, "description": "Patient data not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def update_patient_profile(
    request: PatientDataUpdate,
    current_user: dict = Depends(get_current_patient)
):
    """
    Update patient health profile
    Requirements: 2.2, 2.3, 2.4, 2.5
    
    Updates existing patient_data record with:
    - Age validation (1-120)
    - Fitzpatrick scale validation (I-VI)
    - Family history storage without truncation
    - Immediate persistence to database
    
    Args:
        request: Patient data update request
        current_user: Current authenticated patient user
        
    Returns:
        PatientDataResponse: Updated patient data profile
        
    Raises:
        HTTPException 400: If validation fails
        HTTPException 403: If user is not a patient
        HTTPException 404: If patient data doesn't exist
        HTTPException 500: If update fails
    """
    try:
        from app.config import settings
        import app.demo_data as demo_data
        
        if settings.demo_mode:
            # Demo mode: Use in-memory storage
            existing = demo_data.get_patient_data_by_user_id(current_user["id"])
            
            if not existing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "PATIENT_DATA_NOT_FOUND",
                        "message": "Patient data not found. Use POST to create.",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            
            # Build update data
            update_data = {}
            if request.age is not None:
                update_data["age"] = request.age
            if request.skin_type is not None:
                update_data["skin_type"] = request.skin_type
            if request.family_history is not None:
                update_data["family_history"] = request.family_history
            
            # Update in demo storage
            updated = demo_data.update_patient_data(current_user["id"], update_data)
            
            if not updated:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "code": "UPDATE_FAILED",
                        "message": "Failed to update patient data",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            
            return PatientDataResponse(**updated)
        else:
            # Production mode: Use Supabase
            # Check if patient data exists
            existing = supabase.table("patient_data").select("*").eq("user_id", current_user["id"]).execute()
            
            if not existing.data or len(existing.data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "PATIENT_DATA_NOT_FOUND",
                        "message": "Patient data not found. Use POST to create.",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            
            # Build update data (only include fields that were provided)
            update_data = {"updated_at": datetime.utcnow().isoformat()}
            
            if request.age is not None:
                update_data["age"] = request.age
            if request.skin_type is not None:
                update_data["skin_type"] = request.skin_type
            if request.family_history is not None:
                update_data["family_history"] = request.family_history
            
            # Update in database
            result = supabase.table("patient_data").update(update_data).eq("user_id", current_user["id"]).execute()
            
            if not result.data or len(result.data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "code": "UPDATE_FAILED",
                        "message": "Failed to update patient data",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            
            return PatientDataResponse(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.get(
    "/profile",
    response_model=PatientDataResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - requires patient role"},
        404: {"model": ErrorResponse, "description": "Patient data not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_patient_profile(current_user: dict = Depends(get_current_patient)):
    """
    Get patient health profile
    Requirements: 2.1, 2.5
    
    Retrieves the patient_data record for the current user.
    
    Args:
        current_user: Current authenticated patient user
        
    Returns:
        PatientDataResponse: Patient data profile
        
    Raises:
        HTTPException 403: If user is not a patient
        HTTPException 404: If patient data doesn't exist
        HTTPException 500: If retrieval fails
    """
    try:
        from app.config import settings
        import app.demo_data as demo_data
        
        if settings.demo_mode:
            # Demo mode: Use in-memory storage
            patient_data = demo_data.get_patient_data_by_user_id(current_user["id"])
            
            if not patient_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "PATIENT_DATA_NOT_FOUND",
                        "message": "Patient data not found. Please create your profile first.",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            
            return PatientDataResponse(**patient_data)
        else:
            # Production mode: Use Supabase
            # Retrieve patient data
            result = supabase.table("patient_data").select("*").eq("user_id", current_user["id"]).execute()
            
            if not result.data or len(result.data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "PATIENT_DATA_NOT_FOUND",
                        "message": "Patient data not found. Please create your profile first.",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            
            return PatientDataResponse(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )



@router.post(
    "/validate-image",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Image passed content validation"},
        400: {"model": ErrorResponse, "description": "Invalid image file"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Content violation - inappropriate content detected"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def validate_image_content(
    request: Request,
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_patient),
    audit_logger: AuditLogger = Depends(get_audit_logger)
):
    """
    Validate image for NSFW content (Gatekeeper)
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.6
    
    This endpoint demonstrates the NSFW content filter functionality.
    It validates uploaded images for inappropriate content before allowing
    them to proceed to medical analysis.
    
    Rejection criteria:
    - NSFW score > 0.35: Explicit content detected
    - Non-skin score > 0.8: Non-medical image
    
    All rejections are logged to the audit trail.
    
    Args:
        request: FastAPI request object (for IP extraction)
        image: Uploaded image file
        current_user: Current authenticated patient user
        audit_logger: Audit logging service
        
    Returns:
        dict: Validation result with scores
        
    Raises:
        HTTPException 400: If image file is invalid
        HTTPException 403: If content violation detected
        HTTPException 500: If validation fails
    """
    try:
        # Read image data
        image_data = await image.read()
        
        if not image_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_IMAGE",
                        "message": "Image file is empty or invalid",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                }
            )
        
        # Get client IP
        client_ip = get_client_ip(request)
        
        # Create content filter
        content_filter = create_content_filter(nsfw_detector, audit_logger)
        
        # Validate image through content filter (includes audit logging)
        result = await content_filter.validate_image(
            image_data=image_data,
            user_id=current_user["id"],
            ip_address=client_ip
        )
        
        # Image passed validation
        return {
            "message": "Image passed content validation",
            "validation": {
                "safe": result.safe,
                "nsfw_score": result.nsfw_score,
                "non_skin_score": result.non_skin_score,
                "safe_score": result.safe_score
            },
            "thresholds": {
                "nsfw_threshold": nsfw_detector.NSFW_THRESHOLD,
                "non_skin_threshold": nsfw_detector.NON_SKIN_THRESHOLD
            },
            "next_steps": "Image is ready for quality validation and medical analysis"
        }
        
    except ContentViolationError as e:
        # Content violation - audit log already created by content_filter
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": e.code,
                    "message": e.message,
                    "details": e.details,
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred during content validation",
                    "details": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            }
        )
