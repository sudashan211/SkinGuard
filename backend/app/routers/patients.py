"""
Patient Profile API endpoints for doctors
"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.dependencies import get_current_user
from app.database import supabase
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/patients", tags=["Patients"])


@router.get("/{patient_id}/profile")
async def get_patient_profile(
    patient_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get patient health profile (for doctors only)
    
    Returns patient's:
    - Basic information (name, email, age, skin type)
    - Family history
    - Recent medical reports
    
    Only accessible by doctors who have a confirmed appointment with the patient
    """
    try:
        # Verify current user is a doctor
        if current_user["role"] != "doctor":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": "Only doctors can access patient profiles",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        # Get doctor's ID
        doctor_result = supabase.table("doctors").select("id").eq("user_id", current_user["id"]).execute()
        
        if not doctor_result.data or len(doctor_result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DOCTOR_NOT_FOUND",
                    "message": "Doctor profile not found",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        doctor_id = doctor_result.data[0]["id"]
        
        # Verify doctor has a confirmed appointment with this patient
        appointment_result = supabase.table("appointments")\
            .select("id, status")\
            .eq("doctor_id", doctor_id)\
            .eq("patient_id", patient_id)\
            .in_("status", ["confirmed", "completed"])\
            .execute()
        
        if not appointment_result.data or len(appointment_result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "NO_APPOINTMENT",
                    "message": "You must have a confirmed appointment with this patient to view their profile",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        # Fetch patient profile
        profile_result = supabase.table("profiles")\
            .select("full_name, email")\
            .eq("id", patient_id)\
            .execute()
        
        if not profile_result.data or len(profile_result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "PATIENT_NOT_FOUND",
                    "message": "Patient not found",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        profile = profile_result.data[0]
        
        # Fetch patient data (age, skin type, family history)
        patient_data_result = supabase.table("patient_data")\
            .select("age, skin_type, family_history")\
            .eq("user_id", patient_id)\
            .execute()
        
        patient_data = patient_data_result.data[0] if patient_data_result.data else {}
        
        # Fetch recent medical reports (last 10)
        reports_result = supabase.table("medical_reports")\
            .select("id, created_at, risk_level, status, body_location, symptoms")\
            .eq("patient_id", patient_id)\
            .order("created_at", desc=True)\
            .limit(10)\
            .execute()
        
        # Combine all data
        patient_profile = {
            "fullName": profile.get("full_name"),
            "email": profile.get("email"),
            "age": patient_data.get("age"),
            "skinType": patient_data.get("skin_type"),
            "familyHistory": patient_data.get("family_history"),
            "reports": reports_result.data if reports_result.data else []
        }
        
        return patient_profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching patient profile: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to fetch patient profile",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )
