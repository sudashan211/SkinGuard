"""
Appointment Management API endpoints
Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.models import (
    AppointmentCreateRequest,
    AppointmentUpdateRequest,
    AppointmentResponse,
    ErrorResponse
)
from app.dependencies import get_current_user, get_current_patient
from app.database import supabase
from app.config import settings
import app.demo_data as demo_data
from datetime import datetime
import uuid
import os
import logging

logger = logging.getLogger(__name__)

# Check if using PostgreSQL
USE_POSTGRES = os.getenv("DATABASE_URL", "").startswith("postgresql://")

router = APIRouter(prefix="/api/appointments", tags=["Appointments"])


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Doctor or report not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def create_appointment(
    request: AppointmentCreateRequest,
    current_user: dict = Depends(get_current_patient)
):
    """
    Create a new appointment
    Requirements: 8.1, 8.2, 8.3
    
    Creates a new appointment record with:
    - patient_id: Current authenticated patient
    - doctor_id: Selected doctor UUID
    - scheduled_at: Appointment date/time
    - status: Initial status set to "pending"
    - consultation_type: in_person or video
    
    Args:
        request: Appointment creation request
        current_user: Current authenticated patient
        
    Returns:
        AppointmentResponse: Created appointment with status "pending"
        
    Raises:
        HTTPException 400: If validation fails
        HTTPException 404: If doctor or report not found
        HTTPException 500: If creation fails
    """
    request_id = str(uuid.uuid4())
    
    try:
        if settings.demo_mode:
            # Demo mode: Use in-memory storage
            # Verify doctor exists
            doctor = demo_data.get_doctor_by_user_id(request.doctor_id)
            if not doctor:
                # Try to find doctor by ID in doctors_db
                doctor = demo_data.doctors_db.get(request.doctor_id)
                if not doctor:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={
                            "code": "DOCTOR_NOT_FOUND",
                            "message": "Doctor not found",
                            "timestamp": datetime.utcnow().isoformat(),
                            "request_id": request_id
                        }
                    )
            
            # Verify report if provided
            if request.report_id:
                report = demo_data.get_report_by_id(request.report_id)
                if not report or report.get("patient_id") != current_user["id"]:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={
                            "code": "REPORT_NOT_FOUND",
                            "message": "Medical report not found or does not belong to patient",
                            "timestamp": datetime.utcnow().isoformat(),
                            "request_id": request_id
                        }
                    )
            
            # Create appointment
            appointment_id = str(uuid.uuid4())
            appointment_data = {
                "id": appointment_id,
                "patient_id": current_user["id"],
                "doctor_id": doctor.get("id", request.doctor_id),
                "report_id": request.report_id,
                "scheduled_at": request.scheduled_at.isoformat(),
                "status": "pending",
                "consultation_type": request.consultation_type,
                "video_room_url": None,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            demo_data.appointments_db[appointment_id] = appointment_data
            
            return AppointmentResponse(**appointment_data)
        else:
            # Production mode: Use PostgreSQL or Supabase
            logger.info(f"Creating appointment for patient {current_user['id']} with doctor {request.doctor_id}, request_id: {request_id}")
            
            # Verify doctor exists
            doctor_result = supabase.table("doctors").select("*").eq("id", request.doctor_id).execute()
            
            if not doctor_result.data or len(doctor_result.data) == 0:
                logger.warning(f"Doctor not found: {request.doctor_id}, request_id: {request_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "DOCTOR_NOT_FOUND",
                        "message": "Doctor not found",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": request_id
                    }
                )
            
            doctor = doctor_result.data[0]
            logger.info(f"Doctor found: {doctor.get('id')}, user_id: {doctor.get('user_id')}, request_id: {request_id}")
            
            # Check if doctor is verified
            profile_result = supabase.table("profiles").select("verified").eq("id", doctor["user_id"]).execute()
            
            if not profile_result.data or not profile_result.data[0]["verified"]:
                logger.warning(f"Doctor not verified: {doctor['user_id']}, request_id: {request_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "DOCTOR_NOT_VERIFIED",
                        "message": "Cannot book appointment with unverified doctor",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": request_id
                    }
                )
            
            # Verify report exists and belongs to patient if provided
            if request.report_id:
                report_result = supabase.table("medical_reports").select("*").eq("id", request.report_id).eq("patient_id", current_user["id"]).execute()
                
                if not report_result.data or len(report_result.data) == 0:
                    logger.warning(f"Report not found or doesn't belong to patient: {request.report_id}, request_id: {request_id}")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={
                            "code": "REPORT_NOT_FOUND",
                            "message": "Medical report not found or does not belong to patient",
                            "timestamp": datetime.utcnow().isoformat(),
                            "request_id": request_id
                        }
                    )
            
            # Create appointment record
            appointment_id = str(uuid.uuid4())
            appointment_data = {
                "id": appointment_id,
                "patient_id": current_user["id"],
                "doctor_id": request.doctor_id,
                "report_id": request.report_id,
                "scheduled_at": request.scheduled_at.isoformat() if hasattr(request.scheduled_at, 'isoformat') else str(request.scheduled_at),
                "status": "pending",  # Initial status is always "pending"
                "consultation_type": request.consultation_type,
                "video_room_url": None,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Inserting appointment data: {appointment_data}, request_id: {request_id}")
            
            # Insert into database
            result = supabase.table("appointments").insert(appointment_data).execute()
            
            if not result.data or len(result.data) == 0:
                logger.error(f"Failed to create appointment, no data returned, request_id: {request_id}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "code": "APPOINTMENT_CREATION_FAILED",
                        "message": "Failed to create appointment",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": request_id
                    }
                )
            
            logger.info(f"Appointment created successfully: {appointment_id}, request_id: {request_id}")
            return AppointmentResponse(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating appointment: {str(e)}, request_id: {request_id}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during appointment creation",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id
            }
        )


@router.get(
    "",
    response_model=list[AppointmentResponse],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_appointments(
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's appointments
    Requirements: 8.4
    
    Returns appointments based on user role:
    - Patients: All appointments where patient_id matches their profile
    - Doctors: All appointments where doctor_id matches their doctor record
    - Admins: All appointments (for moderation)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        list[AppointmentResponse]: List of user's appointments
        
    Raises:
        HTTPException 500: If query fails
    """
    try:
        # Demo mode
        if supabase is None:
            from app.demo_data import (
                get_appointments_by_patient_id,
                get_appointments_by_doctor_id,
                get_doctor_by_user_id
            )
            
            if current_user["role"] == "patient":
                appointments = get_appointments_by_patient_id(current_user["id"])
            elif current_user["role"] == "doctor":
                doctor = get_doctor_by_user_id(current_user["id"])
                if not doctor:
                    return []
                appointments = get_appointments_by_doctor_id(doctor["id"])
            elif current_user["role"] == "admin":
                # Admins can see all appointments
                from app.demo_data import appointments_db
                appointments = list(appointments_db.values())
                appointments.sort(key=lambda x: x.get("scheduled_at", ""), reverse=False)
            else:
                return []
            
            return [AppointmentResponse(**appointment) for appointment in appointments]
        
        # Production mode
        if current_user["role"] == "patient":
            # Get patient's appointments with doctor info
            result = supabase.table("appointments")\
                .select("*, doctors(clinic_name, specialization, user_id), medical_reports(risk_level)")\
                .eq("patient_id", current_user["id"])\
                .order("scheduled_at", desc=False)\
                .execute()
        
        elif current_user["role"] == "doctor":
            # Get doctor's appointments with patient info - need to find doctor record first
            doctor_result = supabase.table("doctors").select("id").eq("user_id", current_user["id"]).execute()
            
            if not doctor_result.data or len(doctor_result.data) == 0:
                # Doctor not registered yet, return empty list
                return []
            
            doctor_id = doctor_result.data[0]["id"]
            
            # Fetch appointments with patient details - use simpler syntax
            result = supabase.table("appointments")\
                .select("*")\
                .eq("doctor_id", doctor_id)\
                .order("scheduled_at", desc=False)\
                .execute()
            
            logger.info(f"Fetched {len(result.data) if result.data else 0} appointments for doctor {doctor_id}")
            
            # Manually fetch patient details for each appointment
            if result.data:
                for appointment in result.data:
                    patient_id = appointment.get("patient_id")
                    logger.info(f"Processing appointment {appointment.get('id')}, patient_id: {patient_id}, status: {appointment.get('status')}")
                    
                    if patient_id:
                        # Fetch patient profile
                        patient_result = supabase.table("profiles")\
                            .select("full_name, email")\
                            .eq("id", patient_id)\
                            .execute()
                        
                        if patient_result.data and len(patient_result.data) > 0:
                            patient_data = {
                                "fullName": patient_result.data[0].get("full_name", "Unknown"),
                                "email": patient_result.data[0].get("email", "N/A")
                            }
                            appointment["patient"] = patient_data
                            logger.info(f"Added patient data: {patient_data}")
                        else:
                            logger.warning(f"No patient profile found for patient_id: {patient_id}")
                    
                    # Fetch report details if exists
                    report_id = appointment.get("report_id")
                    if report_id:
                        report_result = supabase.table("medical_reports")\
                            .select("risk_level")\
                            .eq("id", report_id)\
                            .execute()
                        
                        if report_result.data and len(report_result.data) > 0:
                            appointment["report"] = report_result.data[0]
                            logger.info(f"Added report data for report_id: {report_id}")
        
        elif current_user["role"] == "admin":
            # Admins can see all appointments
            result = supabase.table("appointments")\
                .select("*")\
                .order("scheduled_at", desc=False)\
                .execute()
            
            # Manually fetch patient and doctor details for each appointment
            if result.data:
                for appointment in result.data:
                    patient_id = appointment.get("patient_id")
                    if patient_id:
                        patient_result = supabase.table("profiles")\
                            .select("full_name, email")\
                            .eq("id", patient_id)\
                            .execute()
                        
                        if patient_result.data and len(patient_result.data) > 0:
                            appointment["patient"] = {
                                "fullName": patient_result.data[0].get("full_name", "Unknown"),
                                "email": patient_result.data[0].get("email", "N/A")
                            }
                    
                    report_id = appointment.get("report_id")
                    if report_id:
                        report_result = supabase.table("medical_reports")\
                            .select("risk_level")\
                            .eq("id", report_id)\
                            .execute()
                        
                        if report_result.data and len(report_result.data) > 0:
                            appointment["report"] = report_result.data[0]
        
        else:
            return []
        
        if not result.data:
            return []
        
        return [AppointmentResponse(**appointment) for appointment in result.data]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while fetching appointments",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.put(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid status transition"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - not authorized to update this appointment"},
        404: {"model": ErrorResponse, "description": "Appointment not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def update_appointment_status(
    appointment_id: str,
    request: AppointmentUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update appointment status
    Requirements: 8.5
    
    Updates appointment status with validation:
    - Status transitions are validated based on scheduled_at timestamp
    - Only patient or doctor associated with appointment can update
    - Admins can update any appointment
    
    Status transition rules:
    - Before scheduled_at: Can update to any status
    - After scheduled_at: Can only update to "completed" or "cancelled"
    - Cannot transition back to "pending" after scheduled_at has passed
    
    Args:
        appointment_id: Appointment UUID
        request: Status update request
        current_user: Current authenticated user
        
    Returns:
        AppointmentResponse: Updated appointment
        
    Raises:
        HTTPException 400: If status transition is invalid
        HTTPException 403: If user is not authorized to update
        HTTPException 404: If appointment not found
        HTTPException 500: If update fails
    """
    try:
        if settings.demo_mode:
            # Demo mode: Use in-memory storage
            appointment = demo_data.get_appointment_by_id(appointment_id)
            
            if not appointment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "APPOINTMENT_NOT_FOUND",
                        "message": "Appointment not found",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            
            # Check authorization
            is_patient = current_user["role"] == "patient" and appointment["patient_id"] == current_user["id"]
            is_doctor = False
            
            if current_user["role"] == "doctor":
                doctor = demo_data.get_doctor_by_user_id(current_user["id"])
                if doctor:
                    is_doctor = doctor["id"] == appointment["doctor_id"]
            
            is_admin = current_user["role"] == "admin"
            
            if not (is_patient or is_doctor or is_admin):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "code": "FORBIDDEN",
                        "message": "You are not authorized to update this appointment",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            
            # Validate status transition
            scheduled_at = datetime.fromisoformat(appointment["scheduled_at"].replace('Z', '+00:00'))
            now = datetime.utcnow()
            
            if now > scheduled_at:
                if request.status not in ["completed", "cancelled"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "code": "INVALID_STATUS_TRANSITION",
                            "message": f"Cannot update to '{request.status}' after scheduled time has passed. Only 'completed' or 'cancelled' are allowed.",
                            "timestamp": datetime.utcnow().isoformat(),
                            "request_id": str(uuid.uuid4())
                        }
                    )
            
            # Update appointment
            update_data = {"status": request.status}
            updated = demo_data.update_appointment(appointment_id, update_data)
            
            if not updated:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "code": "UPDATE_FAILED",
                        "message": "Failed to update appointment status",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            
            return AppointmentResponse(**updated)
        else:
            # Production mode: Use Supabase
            # Fetch appointment
            result = supabase.table("appointments").select("*").eq("id", appointment_id).execute()
            
            if not result.data or len(result.data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "APPOINTMENT_NOT_FOUND",
                        "message": "Appointment not found",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            
            appointment = result.data[0]
            
            # Check authorization
            is_patient = current_user["role"] == "patient" and appointment["patient_id"] == current_user["id"]
            is_doctor = False
            
            if current_user["role"] == "doctor":
                # Check if current user is the doctor for this appointment
                doctor_result = supabase.table("doctors").select("id").eq("user_id", current_user["id"]).execute()
                if doctor_result.data and len(doctor_result.data) > 0:
                    is_doctor = doctor_result.data[0]["id"] == appointment["doctor_id"]
            
            is_admin = current_user["role"] == "admin"
            
            if not (is_patient or is_doctor or is_admin):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "code": "FORBIDDEN",
                        "message": "You are not authorized to update this appointment",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            
            # Validate status transition based on scheduled_at
            from datetime import timezone
            
            scheduled_at = appointment["scheduled_at"]
            # If it's a string, convert to datetime
            if isinstance(scheduled_at, str):
                scheduled_at = datetime.fromisoformat(scheduled_at.replace('Z', '+00:00'))
            
            # Make both datetimes timezone-aware for comparison
            now = datetime.now(timezone.utc)
            if scheduled_at.tzinfo is None:
                scheduled_at = scheduled_at.replace(tzinfo=timezone.utc)
            
            # If appointment time has passed, only allow "completed" or "cancelled"
            if now > scheduled_at:
                if request.status not in ["completed", "cancelled"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "code": "INVALID_STATUS_TRANSITION",
                            "message": f"Cannot update to '{request.status}' after scheduled time has passed. Only 'completed' or 'cancelled' are allowed.",
                            "timestamp": datetime.utcnow().isoformat(),
                            "request_id": str(uuid.uuid4())
                        }
                    )
            
            # Update appointment
            update_data = {
                "status": request.status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            update_result = supabase.table("appointments").update(update_data).eq("id", appointment_id).execute()
            
            if not update_result.data or len(update_result.data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "code": "UPDATE_FAILED",
                        "message": "Failed to update appointment status",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            
            return AppointmentResponse(**update_result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        request_id = str(uuid.uuid4())
        logger.error(f"Unexpected error updating appointment: {str(e)}, request_id: {request_id}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during appointment update",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id
            }
        )


@router.post(
    "/{appointment_id}/video-room",
    response_model=AppointmentResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid appointment type or status"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - not authorized to access this appointment"},
        404: {"model": ErrorResponse, "description": "Appointment not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def create_video_room(
    appointment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate video room URL for appointment
    Requirements: 25.1, 25.2

    Creates a unique video room URL for video consultations:
    - Only for appointments with consultation_type = "video"
    - Only accessible to patient or doctor associated with appointment
    - Generates unique UUID-based video room URL
    - Stores URL in appointments.video_room_url

    Args:
        appointment_id: Appointment UUID
        current_user: Current authenticated user

    Returns:
        AppointmentResponse: Updated appointment with video_room_url

    Raises:
        HTTPException 400: If appointment is not video type
        HTTPException 403: If user is not authorized
        HTTPException 404: If appointment not found
        HTTPException 500: If update fails
    """
    try:
        # Fetch appointment
        result = supabase.table("appointments").select("*").eq("id", appointment_id).execute()

        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "APPOINTMENT_NOT_FOUND",
                    "message": "Appointment not found",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )

        appointment = result.data[0]

        # Check authorization - only patient or doctor can access
        is_patient = current_user["role"] == "patient" and appointment["patient_id"] == current_user["id"]
        is_doctor = False

        if current_user["role"] == "doctor":
            # Check if current user is the doctor for this appointment
            doctor_result = supabase.table("doctors").select("id").eq("user_id", current_user["id"]).execute()
            if doctor_result.data and len(doctor_result.data) > 0:
                is_doctor = doctor_result.data[0]["id"] == appointment["doctor_id"]

        if not (is_patient or is_doctor):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": "You are not authorized to access this appointment",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )

        # Validate consultation type is video
        if appointment["consultation_type"] != "video":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_CONSULTATION_TYPE",
                    "message": "Video room can only be created for video consultations",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )

        # Generate unique video room URL if not already exists
        if appointment["video_room_url"]:
            # Return existing video room URL
            return AppointmentResponse(**appointment)

        # Generate unique video room URL using UUID
        room_id = str(uuid.uuid4())
        video_room_url = f"https://video.skinguard.app/room/{room_id}"

        # Update appointment with video room URL
        update_data = {
            "video_room_url": video_room_url,
            "updated_at": datetime.utcnow().isoformat()
        }

        update_result = supabase.table("appointments").update(update_data).eq("id", appointment_id).execute()

        if not update_result.data or len(update_result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "UPDATE_FAILED",
                    "message": "Failed to create video room",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )

        return AppointmentResponse(**update_result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during video room creation",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )



@router.post(
    "/{appointment_id}/video-room",
    response_model=AppointmentResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid appointment type or status"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - not authorized to access this appointment"},
        404: {"model": ErrorResponse, "description": "Appointment not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def create_video_room(
    appointment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate video room URL for appointment
    Requirements: 25.1, 25.2
    
    Creates a unique video room URL for video consultations:
    - Only for appointments with consultation_type = "video"
    - Only accessible to patient or doctor associated with appointment
    - Generates unique UUID-based video room URL
    - Stores URL in appointments.video_room_url
    
    Args:
        appointment_id: Appointment UUID
        current_user: Current authenticated user
        
    Returns:
        AppointmentResponse: Updated appointment with video_room_url
        
    Raises:
        HTTPException 400: If appointment is not video type
        HTTPException 403: If user is not authorized
        HTTPException 404: If appointment not found
        HTTPException 500: If update fails
    """
    try:
        # Fetch appointment
        result = supabase.table("appointments").select("*").eq("id", appointment_id).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "APPOINTMENT_NOT_FOUND",
                    "message": "Appointment not found",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        appointment = result.data[0]
        
        # Check authorization - only patient or doctor can access
        is_patient = current_user["role"] == "patient" and appointment["patient_id"] == current_user["id"]
        is_doctor = False
        
        if current_user["role"] == "doctor":
            # Check if current user is the doctor for this appointment
            doctor_result = supabase.table("doctors").select("id").eq("user_id", current_user["id"]).execute()
            if doctor_result.data and len(doctor_result.data) > 0:
                is_doctor = doctor_result.data[0]["id"] == appointment["doctor_id"]
        
        if not (is_patient or is_doctor):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": "You are not authorized to access this appointment",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        # Validate consultation type is video
        if appointment["consultation_type"] != "video":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_CONSULTATION_TYPE",
                    "message": "Video room can only be created for video consultations",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        # Generate unique video room URL if not already exists
        if appointment["video_room_url"]:
            # Return existing video room URL
            return AppointmentResponse(**appointment)
        
        # Generate unique video room URL using UUID
        room_id = str(uuid.uuid4())
        video_room_url = f"https://video.skinguard.app/room/{room_id}"
        
        # Update appointment with video room URL
        update_data = {
            "video_room_url": video_room_url,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        update_result = supabase.table("appointments").update(update_data).eq("id", appointment_id).execute()
        
        if not update_result.data or len(update_result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "UPDATE_FAILED",
                    "message": "Failed to create video room",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        return AppointmentResponse(**update_result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during video room creation",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )
