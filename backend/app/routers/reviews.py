"""
Review and Rating System API endpoints
Requirements: 22.1, 22.2, 22.3
"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.models import (
    ReviewCreateRequest,
    ReviewResponse,
    DoctorReviewsResponse,
    ErrorResponse
)
from app.dependencies import get_current_patient, get_current_user
from app.database import supabase
from datetime import datetime
import uuid


router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


@router.post(
    "",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input or duplicate review"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - patient must have appointment with doctor"},
        404: {"model": ErrorResponse, "description": "Doctor or appointment not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def create_review(
    request: ReviewCreateRequest,
    current_user: dict = Depends(get_current_patient)
):
    """
    Submit a review for a doctor
    Requirements: 22.1, 22.2, 22.3
    
    Creates a new review record with:
    - doctor_id: Doctor being reviewed
    - appointment_id: Associated appointment (optional but recommended)
    - rating: 1-5 stars
    - review_text: Optional text comment
    
    Validation:
    - Patient must have had an appointment with the doctor
    - No duplicate reviews for the same appointment
    - Rating must be 1-5
    
    After creating review:
    - Calculates new average_rating for doctor
    - Updates doctor's average_rating and review_count fields
    
    Args:
        request: Review creation request
        current_user: Current authenticated patient
        
    Returns:
        ReviewResponse: Created review
        
    Raises:
        HTTPException 400: If validation fails or duplicate review
        HTTPException 403: If patient has no appointment with doctor
        HTTPException 404: If doctor or appointment not found
        HTTPException 500: If creation fails
    """
    try:
        # Step 1: Verify doctor exists
        doctor_result = supabase.table("doctors").select("*").eq("id", request.doctor_id).execute()
        
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
        
        doctor = doctor_result.data[0]
        
        # Step 2: Verify patient has had an appointment with this doctor
        appointments_result = supabase.table("appointments").select("*").eq("patient_id", current_user["id"]).eq("doctor_id", request.doctor_id).execute()
        
        if not appointments_result.data or len(appointments_result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "NO_APPOINTMENT_WITH_DOCTOR",
                    "message": "You must have an appointment with this doctor to leave a review",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        # Step 3: If appointment_id provided, verify it exists and belongs to patient
        if request.appointment_id:
            appointment_result = supabase.table("appointments").select("*").eq("id", request.appointment_id).eq("patient_id", current_user["id"]).eq("doctor_id", request.doctor_id).execute()
            
            if not appointment_result.data or len(appointment_result.data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "APPOINTMENT_NOT_FOUND",
                        "message": "Appointment not found or does not match patient and doctor",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            
            # Step 4: Check for duplicate review for this appointment
            existing_review = supabase.table("reviews").select("*").eq("patient_id", current_user["id"]).eq("appointment_id", request.appointment_id).execute()
            
            if existing_review.data and len(existing_review.data) > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "DUPLICATE_REVIEW",
                        "message": "You have already reviewed this appointment",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
        
        # Step 5: Create review record
        review_data = {
            "id": str(uuid.uuid4()),
            "patient_id": current_user["id"],
            "doctor_id": request.doctor_id,
            "appointment_id": request.appointment_id,
            "rating": request.rating,
            "review_text": request.review_text,
            "flagged": False,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Insert into database
        result = supabase.table("reviews").insert(review_data).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "REVIEW_CREATION_FAILED",
                    "message": "Failed to create review",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        created_review = result.data[0]
        
        # Step 6: Calculate and update doctor's average rating and review count
        await update_doctor_rating(request.doctor_id)
        
        # Step 7: Get patient name for response
        patient_name = current_user.get("full_name", "Anonymous")
        created_review["patient_name"] = patient_name
        
        return ReviewResponse(**created_review)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during review creation",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


@router.get(
    "/doctors/{doctor_id}",
    response_model=DoctorReviewsResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Doctor not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_doctor_reviews(doctor_id: str):
    """
    Get all reviews for a specific doctor
    Requirements: 22.2, 22.3
    
    Returns all reviews for a doctor with:
    - Individual reviews with patient name, rating, comment, date
    - Average rating calculated from all reviews
    - Total review count
    - Reviews ordered by created_at descending (newest first)
    
    Args:
        doctor_id: Doctor UUID
        
    Returns:
        DoctorReviewsResponse: Doctor reviews with statistics
        
    Raises:
        HTTPException 404: If doctor not found
        HTTPException 500: If query fails
    """
    try:
        # Demo mode
        if supabase is None:
            from app.demo_data import get_doctor_by_user_id, get_reviews_by_doctor_id, get_user_by_id
            
            # For demo mode, we need to find the doctor record by doctor_id
            # The doctor_id in demo mode is the doctor record ID, not user_id
            from app.demo_data import doctors_db
            
            # Find doctor by ID
            doctor = None
            for doc in doctors_db.values():
                if doc["id"] == doctor_id:
                    doctor = doc
                    break
            
            if not doctor:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "DOCTOR_NOT_FOUND",
                        "message": "Doctor not found",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(uuid.uuid4())
                    }
                )
            
            # Get reviews for this doctor
            reviews_data = get_reviews_by_doctor_id(doctor_id)
            
            # Build review responses with patient names
            reviews = []
            for review_data in reviews_data:
                patient_user = get_user_by_id(review_data["patient_id"])
                review_data["patient_name"] = patient_user.get("full_name", "Anonymous") if patient_user else "Anonymous"
                reviews.append(ReviewResponse(**review_data))
            
            return DoctorReviewsResponse(
                doctor_id=doctor_id,
                average_rating=float(doctor["average_rating"]),
                review_count=int(doctor["review_count"]),
                reviews=reviews
            )
        
        # Production mode
        # Step 1: Verify doctor exists
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
        
        doctor = doctor_result.data[0]
        
        # Step 2: Get all reviews for this doctor, ordered by created_at descending
        reviews_result = supabase.table("reviews").select("*").eq("doctor_id", doctor_id).order("created_at", desc=True).execute()
        
        reviews = []
        
        if reviews_result.data and len(reviews_result.data) > 0:
            # Step 3: Get patient names for all reviews
            patient_ids = list(set(review["patient_id"] for review in reviews_result.data))
            profiles_result = supabase.table("profiles").select("id, full_name").in_("id", patient_ids).execute()
            
            # Create a map of patient_id to full_name
            patient_names = {profile["id"]: profile["full_name"] for profile in profiles_result.data} if profiles_result.data else {}
            
            # Build review responses with patient names
            for review_data in reviews_result.data:
                review_data["patient_name"] = patient_names.get(review_data["patient_id"], "Anonymous")
                reviews.append(ReviewResponse(**review_data))
        
        # Step 4: Return response with doctor's current rating statistics
        return DoctorReviewsResponse(
            doctor_id=doctor_id,
            average_rating=float(doctor["average_rating"]),
            review_count=int(doctor["review_count"]),
            reviews=reviews
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while fetching reviews",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


async def update_doctor_rating(doctor_id: str):
    """
    Calculate and update doctor's average rating and review count
    Requirements: 22.3
    
    This function:
    1. Fetches all reviews for the doctor
    2. Calculates the average rating
    3. Counts total reviews
    4. Updates the doctor's average_rating and review_count fields
    
    Args:
        doctor_id: Doctor UUID
        
    Raises:
        Exception: If update fails
    """
    try:
        # Step 1: Get all reviews for this doctor
        reviews_result = supabase.table("reviews").select("rating").eq("doctor_id", doctor_id).execute()
        
        if not reviews_result.data or len(reviews_result.data) == 0:
            # No reviews yet, set to 0
            update_data = {
                "average_rating": 0.0,
                "review_count": 0,
                "updated_at": datetime.utcnow().isoformat()
            }
        else:
            # Step 2: Calculate average rating
            ratings = [review["rating"] for review in reviews_result.data]
            average_rating = sum(ratings) / len(ratings)
            review_count = len(ratings)
            
            # Round to 2 decimal places
            average_rating = round(average_rating, 2)
            
            update_data = {
                "average_rating": average_rating,
                "review_count": review_count,
                "updated_at": datetime.utcnow().isoformat()
            }
        
        # Step 3: Update doctor record
        supabase.table("doctors").update(update_data).eq("id", doctor_id).execute()
        
    except Exception as e:
        # Log error but don't fail the review creation
        print(f"Error updating doctor rating: {str(e)}")
        raise



@router.put(
    "/{review_id}/flag",
    response_model=ReviewResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden - only doctors can flag reviews"},
        404: {"model": ErrorResponse, "description": "Review not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def flag_review(
    review_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Flag a review for admin moderation
    Requirements: 22.4, 22.6
    
    Allows doctors to flag inappropriate reviews for admin review.
    When a review is flagged:
    - Sets the flagged field to true
    - If rating is below 3 stars, sends notification to admins
    
    Args:
        review_id: Review UUID to flag
        current_user: Current authenticated user (must be doctor)
        
    Returns:
        ReviewResponse: Updated review with flagged=true
        
    Raises:
        HTTPException 403: If user is not a doctor
        HTTPException 404: If review not found
        HTTPException 500: If flagging fails
    """
    try:
        # Step 1: Verify user is a doctor
        if current_user.get("role") != "doctor":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "INSUFFICIENT_PERMISSIONS",
                    "message": "Only doctors can flag reviews",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        # Step 2: Get the review
        review_result = supabase.table("reviews").select("*").eq("id", review_id).execute()
        
        if not review_result.data or len(review_result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "REVIEW_NOT_FOUND",
                    "message": "Review not found",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        review = review_result.data[0]
        
        # Step 3: Update review to set flagged=true
        update_data = {
            "flagged": True
        }
        
        update_result = supabase.table("reviews").update(update_data).eq("id", review_id).execute()
        
        if not update_result.data or len(update_result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "FLAG_UPDATE_FAILED",
                    "message": "Failed to flag review",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            )
        
        updated_review = update_result.data[0]
        
        # Step 4: If rating is below 3 stars, send admin notification
        if review["rating"] < 3:
            await send_low_rating_notification(review_id, review["doctor_id"], review["rating"])
        
        # Step 5: Get patient name for response
        patient_result = supabase.table("profiles").select("full_name").eq("id", review["patient_id"]).execute()
        patient_name = patient_result.data[0]["full_name"] if patient_result.data else "Anonymous"
        
        updated_review["patient_name"] = patient_name
        
        return ReviewResponse(**updated_review)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while flagging review",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(uuid.uuid4())
            }
        )


async def send_low_rating_notification(review_id: str, doctor_id: str, rating: int):
    """
    Send notification to admins for low-rated reviews
    Requirements: 22.6
    
    When a review with rating below 3 stars is flagged, this function:
    1. Identifies all admin users
    2. Creates notification records for each admin
    3. Sends email notifications to admins
    
    Args:
        review_id: Review UUID
        doctor_id: Doctor UUID who received the low rating
        rating: The rating value (1-2)
        
    Raises:
        Exception: If notification fails (logged but not raised)
    """
    try:
        # Step 1: Get all admin users
        admins_result = supabase.table("profiles").select("id, email, full_name").eq("role", "admin").execute()
        
        if not admins_result.data or len(admins_result.data) == 0:
            print("No admin users found for low rating notification")
            return
        
        # Step 2: Get doctor information
        doctor_result = supabase.table("doctors").select("*").eq("id", doctor_id).execute()
        doctor_name = "Unknown Doctor"
        clinic_name = "Unknown Clinic"
        
        if doctor_result.data and len(doctor_result.data) > 0:
            doctor = doctor_result.data[0]
            # Get doctor's profile for name
            doctor_profile = supabase.table("profiles").select("full_name").eq("id", doctor["user_id"]).execute()
            if doctor_profile.data:
                doctor_name = doctor_profile.data[0]["full_name"]
            clinic_name = doctor.get("clinic_name", "Unknown Clinic")
        
        # Step 3: Create notifications for each admin
        for admin in admins_result.data:
            notification_data = {
                "id": str(uuid.uuid4()),
                "user_id": admin["id"],
                "type": "low_rating_alert",
                "title": "Low Rating Alert - Quality Assurance Review Required",
                "message": f"Doctor {doctor_name} at {clinic_name} received a {rating}-star rating. Review ID: {review_id}",
                "read": False,
                "metadata": {
                    "review_id": review_id,
                    "doctor_id": doctor_id,
                    "rating": rating,
                    "doctor_name": doctor_name,
                    "clinic_name": clinic_name
                },
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Insert notification
            supabase.table("notifications").insert(notification_data).execute()
            
            # Step 4: Send email notification
            try:
                from app.email_service import get_email_service
                email_service = get_email_service()
                
                await email_service.send_email(
                    to_email=admin["email"],
                    subject="Low Rating Alert - Quality Assurance Review Required",
                    body=f"""
                    <html>
                    <body>
                        <h2>Low Rating Alert</h2>
                        <p>A doctor has received a low rating that requires quality assurance review.</p>
                        
                        <h3>Details:</h3>
                        <ul>
                            <li><strong>Doctor:</strong> {doctor_name}</li>
                            <li><strong>Clinic:</strong> {clinic_name}</li>
                            <li><strong>Rating:</strong> {rating} stars</li>
                            <li><strong>Review ID:</strong> {review_id}</li>
                        </ul>
                        
                        <p>Please review this case in the admin panel.</p>
                        
                        <p>Best regards,<br>SkinGuard Platform</p>
                    </body>
                    </html>
                    """
                )
            except Exception as email_error:
                print(f"Failed to send email to admin {admin['email']}: {str(email_error)}")
        
        print(f"Low rating notification sent to {len(admins_result.data)} admins for review {review_id}")
        
    except Exception as e:
        # Log error but don't fail the flagging operation
        print(f"Error sending low rating notification: {str(e)}")
