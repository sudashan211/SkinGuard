"""
Doctor Registration and Management API endpoints
Requirements: 6.1, 6.2, 6.3, 6.4, 7.2, 7.3, 7.5, 9.1, 9.2, 9.3, 9.5, 10.1, 23.5, 25.5
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.models import (
    DoctorRegistrationRequest,
    DoctorResponse,
    ErrorResponse,
    ConsultationNotesRequest,
    MedicalReportResponse
)
from app.dependencies import get_current_doctor, get_current_user, get_current_verified_doctor
from app.database import supabase
from datetime import datetime
import uuid


router = APIRouter(prefix="/api/doctors", tags=["Doctors"])


@router.get(
    "/profile",
    response_model=DoctorResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - requires doctor role"},
        404: {"model": ErrorResponse, "description": "Doctor profile not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_doctor_profile(current_user: dict = Depends(get_current_doctor)):
    """
    Get current doctor's profile
    
    Returns the doctor profile for the currently authenticated doctor user.
    
    Args:
        current_user: Current authenticated doctor user
        
    Returns:
        DoctorResponse: Doctor profile with verification status
        
    Raises:
        HTTPException 403: If user is not a doctor
        HTTPException 404: If doctor profile doesn't exist
        HTTPException 500: If retrieval fails
    """
    try:
        # Demo mode
        if supabase is None:
            from app.demo_data import get_doctor_by_user_id
            doctor_data = get_doctor_by_user_id(current_user["id"])
            
            if not doctor_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "DOCTOR_PROFILE_NOT_FOUND",
                        "message": "Doctor profile not found. Please register first.",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            
            doctor_data["verified"] = current_user.get("verified", False)
            return DoctorResponse(**doctor_data)
        
        # Production mode
        result = supabase.table("doctors").select("*").eq("user_id", current_user["id"]).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DOCTOR_PROFILE_NOT_FOUND",
                    "message": "Doctor profile not found. Please register first.",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        doctor_data = result.data[0]
        doctor_data["verified"] = current_user["verified"]
        
        return DoctorResponse(**doctor_data)
        
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
    response_model=DoctorResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - requires doctor role"},
        404: {"model": ErrorResponse, "description": "Doctor profile not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def update_doctor_profile(
    request: dict,
    current_user: dict = Depends(get_current_doctor)
):
    """
    Update doctor profile
    
    Updates the doctor profile with new information. License number cannot be changed.
    
    Args:
        request: Update data (clinic_name, whatsapp_no, specialization, bio, etc.)
        current_user: Current authenticated doctor user
        
    Returns:
        DoctorResponse: Updated doctor profile
        
    Raises:
        HTTPException 403: If user is not a doctor
        HTTPException 404: If doctor profile doesn't exist
        HTTPException 500: If update fails
    """
    try:
        # Build update data (exclude license_no and user_id)
        update_data = {"updated_at": datetime.utcnow().isoformat()}
        
        allowed_fields = [
            "clinic_name", "lat", "lng", "whatsapp_no", "specialization",
            "bio", "education", "certifications", "languages", "clinic_hours"
        ]
        
        for field in allowed_fields:
            if field in request:
                update_data[field] = request[field]
        
        # Demo mode
        if supabase is None:
            from app.demo_data import get_doctor_by_user_id, update_doctor
            
            existing = get_doctor_by_user_id(current_user["id"])
            if not existing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "DOCTOR_PROFILE_NOT_FOUND",
                        "message": "Doctor profile not found",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            
            updated = update_doctor(current_user["id"], update_data)
            updated["verified"] = current_user.get("verified", False)
            return DoctorResponse(**updated)
        
        # Production mode
        existing = supabase.table("doctors").select("*").eq("user_id", current_user["id"]).execute()
        
        if not existing.data or len(existing.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DOCTOR_PROFILE_NOT_FOUND",
                    "message": "Doctor profile not found",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        # Update in database
        result = supabase.table("doctors").update(update_data).eq("user_id", current_user["id"]).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "UPDATE_FAILED",
                    "message": "Failed to update doctor profile",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        doctor_data = result.data[0]
        doctor_data["verified"] = current_user["verified"]
        
        return DoctorResponse(**doctor_data)
        
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
    "/register",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input or doctor already registered"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - requires doctor role"},
        409: {"model": ErrorResponse, "description": "License number already exists"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def register_doctor(
    request: DoctorRegistrationRequest,
    current_user: dict = Depends(get_current_doctor)
):
    """
    Register doctor with license and clinic information
    Requirements: 6.1, 6.2
    
    Creates a new doctors record with:
    - License number (unique)
    - Clinic name and location coordinates
    - WhatsApp contact number
    - Initial verified status set to false (requires admin approval)
    
    Args:
        request: Doctor registration request with license info and clinic details
        current_user: Current authenticated doctor user
        
    Returns:
        DoctorResponse: Created doctor profile with verification status false
        
    Raises:
        HTTPException 400: If validation fails or doctor already registered
        HTTPException 403: If user is not a doctor
        HTTPException 409: If license number already exists
        HTTPException 500: If registration fails
    """
    try:
        # Check if doctor record already exists for this user
        existing_doctor = supabase.table("doctors").select("*").eq("user_id", current_user["id"]).execute()
        
        if existing_doctor.data and len(existing_doctor.data) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "DOCTOR_ALREADY_REGISTERED",
                    "message": "Doctor profile already exists for this user",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        # Check if license number already exists
        existing_license = supabase.table("doctors").select("*").eq("license_no", request.license_no).execute()
        
        if existing_license.data and len(existing_license.data) > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "LICENSE_ALREADY_EXISTS",
                    "message": "A doctor with this license number is already registered",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        # Create doctor record
        doctor_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "license_no": request.license_no,
            "clinic_name": request.clinic_name,
            "lat": float(request.lat),
            "lng": float(request.lng),
            "whatsapp_no": request.whatsapp_no,
            "specialization": request.specialization,
            "average_rating": 0.0,
            "review_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Insert into database
        result = supabase.table("doctors").insert(doctor_data).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "REGISTRATION_FAILED",
                    "message": "Failed to register doctor profile",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        # Add verified status from profiles table
        doctor_response = result.data[0]
        doctor_response["verified"] = current_user["verified"]
        
        return DoctorResponse(**doctor_response)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during doctor registration",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )



@router.get(
    "/nearby",
    response_model=list[DoctorResponse],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid coordinates or radius"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_nearby_doctors(
    lat: float = Query(0, ge=-90, le=90, description="Latitude coordinate (0 for all doctors)"),
    lng: float = Query(0, ge=-180, le=180, description="Longitude coordinate (0 for all doctors)"),
    radius: float = Query(50, ge=1, le=500, description="Search radius in kilometers")
):
    """
    Find verified doctors near a location (or all doctors if lat/lng are 0)
    Requirements: 7.2, 7.3
    
    Returns all verified doctors within the specified radius of the given coordinates.
    If lat=0 and lng=0, returns all verified doctors regardless of location.
    Uses PostGIS for geographic queries to find doctors by distance.
    
    Query parameters:
    - lat: Latitude coordinate (-90 to 90), use 0 to get all doctors
    - lng: Longitude coordinate (-180 to 180), use 0 to get all doctors
    - radius: Search radius in kilometers (default: 50km, max: 500km)
    
    Filtering criteria:
    - verified = true (only verified doctors)
    - within radius distance from coordinates (or all if lat/lng are 0)
    
    Args:
        lat: Latitude coordinate (0 for all doctors)
        lng: Longitude coordinate (0 for all doctors)
        radius: Search radius in kilometers
        
    Returns:
        list[DoctorResponse]: List of verified doctors within radius (or all if lat/lng are 0)
        
    Raises:
        HTTPException 400: If coordinates or radius are invalid
        HTTPException 500: If query fails
    """
    try:
        # Check if supabase client is initialized
        if supabase is None:
            return []
        
        # Step 1: Get all verified doctors
        # First get verified profiles with doctor role
        profiles_result = supabase.table("profiles").select("*").eq("role", "doctor").eq("verified", True).execute()
        
        if not profiles_result.data or len(profiles_result.data) == 0:
            # No verified doctors - return empty list
            return []
        
        verified_user_ids = [profile["id"] for profile in profiles_result.data]
        
        # Step 2: Get doctor records for verified profiles
        # Note: For production, you would use PostGIS earth_distance function
        # For now, we'll get all doctors and filter by simple distance calculation
        doctors_result = supabase.table("doctors").select("*").in_("user_id", verified_user_ids).execute()
        
        if not doctors_result.data or len(doctors_result.data) == 0:
            return []
        
        # Step 3: Filter by distance (or return all if lat=0, lng=0)
        # If lat and lng are both 0, return all verified doctors
        if lat == 0 and lng == 0:
            all_doctors = []
            for doctor_data in doctors_result.data:
                doctor_data["verified"] = True
                all_doctors.append(DoctorResponse(**doctor_data))
            return all_doctors
        
        # Otherwise, filter by distance using Haversine formula
        import math
        
        def calculate_distance(lat1, lng1, lat2, lng2):
            """Calculate distance between two coordinates in kilometers using Haversine formula"""
            R = 6371  # Earth's radius in kilometers
            
            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            delta_lat = math.radians(lat2 - lat1)
            delta_lng = math.radians(lng2 - lng1)
            
            a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            
            return R * c
        
        nearby_doctors = []
        
        for doctor_data in doctors_result.data:
            distance = calculate_distance(lat, lng, float(doctor_data["lat"]), float(doctor_data["lng"]))
            
            if distance <= radius:
                # Add verified status from profiles
                doctor_data["verified"] = True
                nearby_doctors.append(DoctorResponse(**doctor_data))
        
        return nearby_doctors
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while searching for nearby doctors",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.get(
    "/reports/pending",
    response_model=list[dict],
    responses={
        200: {"description": "List of pending reports for doctor review"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - requires verified doctor role"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_pending_reports(
    status_filter: str = Query(None, description="Filter by status: safe, urgent, or all"),
    current_user: dict = Depends(get_current_verified_doctor)
):
    """
    Get pending reports for doctor review from patients with appointments
    Requirements: 9.1, 9.2, 9.3, 23.5

    Returns medical reports from patients who have appointments with this doctor.
    Reports are filtered by status (safe, urgent) and prioritized with urgent cases at the top.

    Filtering criteria:
    - Only reports from patients who have appointments with this doctor
    - status: "safe" or "urgent" (excludes "flagged" reports)
    - Joined with patient_data for complete patient information
    - Ordered by: urgent cases first, then by creation date descending

    Query parameters:
    - status_filter: Optional filter by status ("safe", "urgent", or None for all)

    Args:
        status_filter: Optional status filter
        current_user: Current verified doctor user

    Returns:
        list[dict]: List of pending reports with patient information

    Raises:
        HTTPException 403: If user is not a verified doctor
        HTTPException 500: If query fails
    """
    try:
        # Demo mode
        if supabase is None:
            from app.demo_data import get_reports_by_status, get_user_by_id, get_patient_data_by_user_id
            
            # Validate status filter
            if status_filter and status_filter not in ["safe", "urgent", "all"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "INVALID_STATUS_FILTER",
                        "message": "Status filter must be 'safe', 'urgent', or 'all'",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            
            # Get reports based on filter
            if status_filter == "all" or status_filter is None:
                reports = get_reports_by_status()
            else:
                reports = get_reports_by_status(status_filter)
            
            # Build response with patient information
            pending_reports = []
            for report in reports:
                patient_id = report["patient_id"]
                patient_user = get_user_by_id(patient_id)
                patient_data = get_patient_data_by_user_id(patient_id)
                
                report_with_patient = {
                    **report,
                    # Patient data in nested object format (as expected by frontend)
                    "patient": {
                        "fullName": patient_user.get("full_name", "Unknown Patient") if patient_user else "Unknown Patient",
                        "email": patient_user.get("email") if patient_user else None,
                        "age": patient_data.get("age") if patient_data else None,
                        "fitzpatrick_scale": patient_data.get("skin_type") if patient_data else None,
                        "family_history": patient_data.get("family_history") if patient_data else None
                    }
                }
                pending_reports.append(report_with_patient)
            
            # Sort: urgent first, then by created_at descending
            def sort_key(report):
                priority = 0 if report["status"] == "urgent" else 1
                try:
                    created_at = datetime.fromisoformat(report["created_at"].replace('Z', '+00:00'))
                except:
                    created_at = datetime.min
                return (priority, -created_at.timestamp())
            
            pending_reports.sort(key=sort_key)
            return pending_reports
        
        # Production mode
        # Step 1: Get doctor's ID from user_id
        doctor_result = supabase.table("doctors").select("id").eq("user_id", current_user["id"]).execute()
        
        if not doctor_result.data:
            return []
        
        doctor_id = doctor_result.data[0]["id"]
        
        # Step 2: Get patient IDs who have appointments with this doctor
        appointments_result = supabase.table("appointments").select("patient_id").eq("doctor_id", doctor_id).execute()
        
        if not appointments_result.data:
            # No appointments, no reports to show
            return []
        
        # Get unique patient IDs from appointments
        patient_ids_with_appointments = list(set(apt["patient_id"] for apt in appointments_result.data))
        
        # Step 3: Build query for reports from these patients only
        # Get reports with status "safe" or "urgent" (exclude "flagged")
        query = supabase.table("medical_reports").select("*")

        # Filter by patients who have appointments with this doctor
        query = query.in_("patient_id", patient_ids_with_appointments)

        # Apply status filter if provided
        if status_filter:
            if status_filter not in ["safe", "urgent"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "INVALID_STATUS_FILTER",
                        "message": "Status filter must be 'safe' or 'urgent'",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            query = query.eq("status", status_filter)
        else:
            # Get both safe and urgent reports (exclude flagged)
            query = query.in_("status", ["safe", "urgent"])

        # Execute query
        reports_result = query.execute()

        if not reports_result.data or len(reports_result.data) == 0:
            return []

        # Step 4: Get patient IDs and fetch patient_data
        patient_ids = list(set(report["patient_id"] for report in reports_result.data))

        # Fetch patient profiles
        profiles_result = supabase.table("profiles").select("*").in_("id", patient_ids).execute()
        profiles_map = {profile["id"]: profile for profile in profiles_result.data} if profiles_result.data else {}

        # Fetch patient_data
        patient_data_result = supabase.table("patient_data").select("*").in_("user_id", patient_ids).execute()
        patient_data_map = {pd["user_id"]: pd for pd in patient_data_result.data} if patient_data_result.data else {}

        # Step 3: Join data and build response
        pending_reports = []

        for report in reports_result.data:
            patient_id = report["patient_id"]
            profile = profiles_map.get(patient_id, {})
            patient_data = patient_data_map.get(patient_id, {})

            # Build complete report with patient information
            # Convert datetime objects to ISO strings for JSON serialization
            created_at = report["created_at"]
            updated_at = report["updated_at"]
            if isinstance(created_at, datetime):
                created_at = created_at.isoformat()
            if isinstance(updated_at, datetime):
                updated_at = updated_at.isoformat()
            
            # Transform ai_prediction to match frontend expectations
            # Frontend expects: {predictions: {melanoma: 0.99, ...}, hotspots: [...]}
            # Backend has: {predictions: [{type: 'melanoma', probability: 0.99}, ...], hotspots: [...]}
            ai_prediction = report.get("ai_prediction", {})
            predictions_flat = {}
            hotspots = []
            
            if ai_prediction and isinstance(ai_prediction, dict):
                # Flatten predictions array to object
                predictions_array = ai_prediction.get("predictions", [])
                for pred in predictions_array:
                    if isinstance(pred, dict):
                        pred_type = pred.get("type", "")
                        pred_prob = pred.get("probability", 0)
                        predictions_flat[pred_type] = pred_prob
                
                # Get hotspots
                hotspots = ai_prediction.get("hotspots", [])
            
            report_with_patient = {
                # Report fields
                "id": report["id"],
                "patient_id": report["patient_id"],
                "image_url": report["image_url"],
                "thumbnail_url": report.get("thumbnail_url"),  # Add thumbnail support
                "predictions": predictions_flat,  # Flattened predictions for frontend
                "hotspots": hotspots,
                "ai_prediction": ai_prediction,  # Keep original for reference
                "symptoms": report.get("symptoms"),
                "status": report["status"],
                "risk_level": report["risk_level"],
                "body_location": report.get("body_location"),
                "consultation_notes": report.get("consultation_notes"),
                "created_at": created_at,
                "updated_at": updated_at,

                # Patient data in nested object format (as expected by frontend)
                "patient": {
                    "fullName": profile.get("full_name", "Unknown Patient"),
                    "email": profile.get("email"),
                    "age": patient_data.get("age"),
                    "fitzpatrick_scale": patient_data.get("skin_type"),  # Map skin_type to fitzpatrick_scale
                    "family_history": patient_data.get("family_history")
                }
            }

            pending_reports.append(report_with_patient)

        # Step 4: Sort with urgent cases first, then by creation date descending
        # Priority: urgent status first, then sort by created_at
        def sort_key(report):
            # Urgent reports get priority (0), safe reports get lower priority (1)
            priority = 0 if report["status"] == "urgent" else 1
            # Parse created_at for secondary sort (newer first)
            try:
                created_at_value = report["created_at"]
                # Handle both datetime objects (from PostgreSQL) and strings (from Supabase)
                if isinstance(created_at_value, datetime):
                    created_at = created_at_value
                else:
                    created_at = datetime.fromisoformat(str(created_at_value).replace('Z', '+00:00'))
            except:
                created_at = datetime.min

            # Return tuple: (priority, negative timestamp for descending order)
            return (priority, -created_at.timestamp())

        pending_reports.sort(key=sort_key)

        return pending_reports

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while fetching pending reports",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )



@router.post(
    "/reports/{report_id}/notes",
    response_model=MedicalReportResponse,
    responses={
        200: {"description": "Consultation notes added successfully"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - requires verified doctor role"},
        404: {"model": ErrorResponse, "description": "Report not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def add_consultation_notes(
    report_id: str,
    request: ConsultationNotesRequest,
    current_user: dict = Depends(get_current_verified_doctor)
):
    """
    Add consultation notes to a medical report
    Requirements: 9.5, 25.5
    
    Allows verified doctors to add consultation notes to medical reports.
    Notes are stored in the medical_reports.consultation_notes field.
    
    Only verified doctors can add consultation notes.
    The report must exist and be accessible (status: safe or urgent).
    
    Args:
        report_id: UUID of the medical report
        request: Consultation notes request with notes text
        current_user: Current verified doctor user
        
    Returns:
        MedicalReportResponse: Updated medical report with consultation notes
        
    Raises:
        HTTPException 400: If report_id is invalid UUID
        HTTPException 403: If user is not a verified doctor
        HTTPException 404: If report not found or not accessible
        HTTPException 500: If update fails
    """
    try:
        # Validate report_id is a valid UUID
        try:
            uuid.UUID(report_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_REPORT_ID",
                    "message": "Report ID must be a valid UUID",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        # Demo mode
        if supabase is None:
            from app.demo_data import get_report_by_id, update_report_notes
            
            report = get_report_by_id(report_id)
            if not report:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "REPORT_NOT_FOUND",
                        "message": f"Medical report with ID {report_id} not found",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            
            # Verify report is accessible (not flagged)
            if report["status"] == "flagged":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "code": "REPORT_NOT_ACCESSIBLE",
                        "message": "Cannot add notes to flagged reports",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            
            # Update consultation notes
            updated_report = update_report_notes(report_id, request.notes)
            if not updated_report:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "code": "UPDATE_FAILED",
                        "message": "Failed to update consultation notes",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            
            return MedicalReportResponse(**updated_report)
        
        # Production mode
        # Step 1: Verify report exists and is accessible
        report_result = supabase.table("medical_reports").select("*").eq("id", report_id).execute()
        
        if not report_result.data or len(report_result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "REPORT_NOT_FOUND",
                    "message": f"Medical report with ID {report_id} not found",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        report = report_result.data[0]
        
        # Verify report is accessible (not flagged)
        if report["status"] == "flagged":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "REPORT_NOT_ACCESSIBLE",
                    "message": "Cannot add notes to flagged reports",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        # Step 2: Update consultation notes
        update_data = {
            "consultation_notes": request.notes,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        update_result = supabase.table("medical_reports").update(update_data).eq("id", report_id).execute()
        
        if not update_result.data or len(update_result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "UPDATE_FAILED",
                    "message": "Failed to update consultation notes",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        # Step 3: Return updated report
        updated_report = update_result.data[0]
        
        return MedicalReportResponse(**updated_report)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while adding consultation notes",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )
