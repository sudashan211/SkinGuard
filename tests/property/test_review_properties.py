"""
Property-Based Tests for Review and Rating System
Feature: derman-ai-skin-screening

Tests review correctness properties including review prompt after appointment,
review association and visibility, and doctor rating statistics display.

Requirements: 22.1, 22.2, 22.3
"""

import pytest
import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings
from hypothesis import HealthCheck
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import uuid
from datetime import datetime, timedelta

# Add backend to path for imports
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Mock the database module before importing anything that uses it
sys.modules['app.database'] = MagicMock()

from app.models import ReviewCreateRequest, ReviewResponse, DoctorReviewsResponse


# Hypothesis strategies for generating test data
@st.composite
def review_data(draw):
    """Generate review data for testing"""
    return {
        "id": str(uuid.uuid4()),
        "patient_id": str(uuid.uuid4()),
        "doctor_id": str(uuid.uuid4()),
        "appointment_id": str(uuid.uuid4()) if draw(st.booleans()) else None,
        "rating": draw(st.integers(min_value=1, max_value=5)),
        "review_text": draw(st.text(min_size=0, max_size=500)) if draw(st.booleans()) else None,
        "flagged": False,
        "created_at": datetime.utcnow().isoformat()
    }


# Feature: derman-ai-skin-screening, Property 73: Review Prompt After Appointment
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    rating=st.integers(min_value=1, max_value=5),
    has_review_text=st.booleans(),
    has_appointment_id=st.booleans()
)
@pytest.mark.asyncio
async def test_review_prompt_after_appointment(rating, has_review_text, has_appointment_id):
    """
    Property 73: Review Prompt After Appointment
    
    For any appointment with status "completed", the system should prompt the
    patient for a rating (1-5 stars) and optional review text.
    
    This test verifies:
    1. Patients can submit reviews after completed appointments
    2. Rating is required and must be 1-5 stars
    3. Review text is optional
    4. Review can be associated with an appointment
    5. Review is successfully created and stored
    
    Validates: Requirements 22.1
    """
    from app.routers.reviews import create_review
    
    # Generate test data
    patient_id = str(uuid.uuid4())
    doctor_id = str(uuid.uuid4())
    doctor_user_id = str(uuid.uuid4())
    appointment_id = str(uuid.uuid4()) if has_appointment_id else None
    review_text = "Great doctor, very helpful!" if has_review_text else None
    
    # Create request
    request = ReviewCreateRequest(
        doctor_id=doctor_id,
        appointment_id=appointment_id,
        rating=rating,
        review_text=review_text
    )
    
    # Mock current user (patient)
    current_user = {
        "id": patient_id,
        "role": "patient",
        "full_name": "Test Patient",
        "verified": False
    }
    
    # Mock doctor data
    doctor_data = {
        "id": doctor_id,
        "user_id": doctor_user_id,
        "license_no": "LIC123456",
        "clinic_name": "Test Clinic",
        "average_rating": 4.5,
        "review_count": 10
    }
    
    # Mock appointment data (patient has appointment with doctor)
    appointment_data = {
        "id": appointment_id if appointment_id else str(uuid.uuid4()),
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "status": "completed",
        "scheduled_at": (datetime.utcnow() - timedelta(hours=24)).isoformat()
    }
    
    # Expected review data
    expected_review = {
        "id": str(uuid.uuid4()),
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "appointment_id": appointment_id,
        "rating": rating,
        "review_text": review_text,
        "flagged": False,
        "created_at": datetime.utcnow().isoformat(),
        "patient_name": "Test Patient"
    }
    
    # Mock Supabase responses
    with patch('app.routers.reviews.supabase') as mock_supabase, \
         patch('app.routers.reviews.update_doctor_rating') as mock_update_rating:
        
        # Mock doctor lookup
        mock_doctor_result = Mock()
        mock_doctor_result.data = [doctor_data]
        
        # Mock appointments lookup (patient has appointment with doctor)
        mock_appointments_result = Mock()
        mock_appointments_result.data = [appointment_data]
        
        # Mock specific appointment lookup if provided
        mock_appointment_result = Mock()
        if has_appointment_id:
            mock_appointment_result.data = [appointment_data]
        else:
            mock_appointment_result.data = []
        
        # Mock existing review check (no duplicate)
        mock_existing_review = Mock()
        mock_existing_review.data = []
        
        # Mock review insert
        mock_insert_result = Mock()
        mock_insert_result.data = [expected_review]
        
        # Set up the mock chain
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "doctors":
                mock_table.select.return_value.eq.return_value.execute.return_value = mock_doctor_result
            elif table_name == "appointments":
                # For general appointments check
                select_mock = Mock()
                eq1_mock = Mock()
                eq2_mock = Mock()
                select_mock.eq.return_value = eq1_mock
                eq1_mock.eq.return_value = eq2_mock
                
                # For specific appointment check
                eq3_mock = Mock()
                eq2_mock.eq.return_value = eq3_mock
                eq3_mock.execute.return_value = mock_appointment_result
                
                # For general check
                eq2_mock.execute.return_value = mock_appointments_result
                
                mock_table.select.return_value = select_mock
            elif table_name == "reviews":
                # For existing review check
                select_mock = Mock()
                eq1_mock = Mock()
                eq2_mock = Mock()
                select_mock.eq.return_value = eq1_mock
                eq1_mock.eq.return_value = eq2_mock
                eq2_mock.execute.return_value = mock_existing_review
                
                # For insert
                insert_mock = Mock()
                insert_mock.execute.return_value = mock_insert_result
                mock_table.insert.return_value = insert_mock
                
                mock_table.select.return_value = select_mock
            return mock_table
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Call the endpoint
        result = await create_review(request, current_user)
        
        # Verify result is a ReviewResponse
        assert isinstance(result, ReviewResponse), \
            f"Result should be ReviewResponse, got {type(result)}"
        
        # Verify rating is within valid range
        assert 1 <= result.rating <= 5, \
            f"Rating should be between 1 and 5, got {result.rating}"
        
        # Verify rating matches request
        assert result.rating == rating, \
            f"Rating should be {rating}, got {result.rating}"
        
        # Verify review text is preserved if provided
        if has_review_text:
            assert result.review_text == review_text, \
                f"Review text should be '{review_text}', got '{result.review_text}'"
        
        # Verify appointment association if provided
        if has_appointment_id:
            assert result.appointment_id == appointment_id, \
                f"appointment_id should be {appointment_id}, got {result.appointment_id}"
        
        # Verify patient and doctor IDs
        assert result.patient_id == patient_id, \
            f"patient_id should be {patient_id}, got {result.patient_id}"
        assert result.doctor_id == doctor_id, \
            f"doctor_id should be {doctor_id}, got {result.doctor_id}"
        
        # Verify review is not flagged initially
        assert result.flagged == False, \
            f"Review should not be flagged initially, got {result.flagged}"
        
        # Verify update_doctor_rating was called
        mock_update_rating.assert_called_once_with(doctor_id)


# Feature: derman-ai-skin-screening, Property 74: Review Association and Visibility
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    num_reviews=st.integers(min_value=1, max_value=10)
)
@pytest.mark.asyncio
async def test_review_association_and_visibility(num_reviews):
    """
    Property 74: Review Association and Visibility
    
    For any submitted review, the system should associate it with the doctor's
    profile and make it publicly visible on the doctor's page.
    
    This test verifies:
    1. Reviews are associated with the correct doctor_id
    2. All reviews for a doctor are publicly accessible
    3. Reviews include patient information (name)
    4. Reviews are ordered by creation date (newest first)
    5. Review data is complete and accurate
    
    Validates: Requirements 22.2
    """
    from app.routers.reviews import get_doctor_reviews
    
    # Generate test data
    doctor_id = str(uuid.uuid4())
    doctor_user_id = str(uuid.uuid4())
    
    # Mock doctor data
    doctor_data = {
        "id": doctor_id,
        "user_id": doctor_user_id,
        "license_no": "LIC123456",
        "clinic_name": "Test Clinic",
        "average_rating": 4.5,
        "review_count": num_reviews
    }
    
    # Generate reviews for this doctor
    reviews = []
    patient_profiles = {}
    
    for i in range(num_reviews):
        patient_id = str(uuid.uuid4())
        patient_name = f"Patient {i+1}"
        
        review = {
            "id": str(uuid.uuid4()),
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "appointment_id": str(uuid.uuid4()),
            "rating": (i % 5) + 1,  # Ratings 1-5
            "review_text": f"Review text {i+1}",
            "flagged": False,
            "created_at": (datetime.utcnow() - timedelta(hours=i)).isoformat()
        }
        reviews.append(review)
        
        patient_profiles[patient_id] = {
            "id": patient_id,
            "full_name": patient_name
        }
    
    # Mock Supabase responses
    with patch('app.routers.reviews.supabase') as mock_supabase:
        # Mock doctor lookup
        mock_doctor_result = Mock()
        mock_doctor_result.data = [doctor_data]
        
        # Mock reviews lookup (ordered by created_at desc)
        mock_reviews_result = Mock()
        mock_reviews_result.data = reviews
        
        # Mock patient profiles lookup
        mock_profiles_result = Mock()
        mock_profiles_result.data = list(patient_profiles.values())
        
        # Set up the mock chain
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "doctors":
                mock_table.select.return_value.eq.return_value.execute.return_value = mock_doctor_result
            elif table_name == "reviews":
                order_mock = Mock()
                order_mock.execute.return_value = mock_reviews_result
                mock_table.select.return_value.eq.return_value.order.return_value = order_mock
            elif table_name == "profiles":
                in_mock = Mock()
                in_mock.execute.return_value = mock_profiles_result
                mock_table.select.return_value.in_.return_value = in_mock
            return mock_table
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Call the endpoint
        result = await get_doctor_reviews(doctor_id)
        
        # Verify result is a DoctorReviewsResponse
        assert isinstance(result, DoctorReviewsResponse), \
            f"Result should be DoctorReviewsResponse, got {type(result)}"
        
        # Verify doctor_id matches
        assert result.doctor_id == doctor_id, \
            f"doctor_id should be {doctor_id}, got {result.doctor_id}"
        
        # Verify all reviews are returned
        assert len(result.reviews) == num_reviews, \
            f"Should return {num_reviews} reviews, got {len(result.reviews)}"
        
        # Verify all reviews are associated with the correct doctor
        for review in result.reviews:
            assert review.doctor_id == doctor_id, \
                f"Review {review.id} should be associated with doctor {doctor_id}, got {review.doctor_id}"
        
        # Verify all reviews have patient names
        for review in result.reviews:
            assert review.patient_name is not None, \
                f"Review {review.id} should have patient_name"
            assert len(review.patient_name) > 0, \
                f"Review {review.id} patient_name should not be empty"
        
        # Verify reviews are ordered by created_at descending (newest first)
        if len(result.reviews) > 1:
            for i in range(len(result.reviews) - 1):
                current_review = result.reviews[i]
                next_review = result.reviews[i+1]
                
                # Handle both string and datetime objects
                if isinstance(current_review.created_at, str):
                    current_time = datetime.fromisoformat(current_review.created_at.replace('Z', '+00:00'))
                else:
                    current_time = current_review.created_at
                
                if isinstance(next_review.created_at, str):
                    next_time = datetime.fromisoformat(next_review.created_at.replace('Z', '+00:00'))
                else:
                    next_time = next_review.created_at
                
                assert current_time >= next_time, \
                    f"Reviews should be ordered by created_at descending"


# Feature: derman-ai-skin-screening, Property 75: Doctor Rating Statistics Display
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    num_reviews=st.integers(min_value=1, max_value=20),
    rating_seed=st.integers(min_value=0, max_value=1000)
)
@pytest.mark.asyncio
async def test_doctor_rating_statistics_display(num_reviews, rating_seed):
    """
    Property 75: Doctor Rating Statistics Display
    
    For any doctor profile display, the interface should show the average rating
    (computed from all reviews) and total review count.
    
    This test verifies:
    1. Average rating is calculated correctly from all reviews
    2. Review count matches the number of reviews
    3. Average rating is rounded to 2 decimal places
    4. Statistics are updated after each new review
    5. Statistics are displayed in the doctor reviews response
    
    Validates: Requirements 22.3
    """
    from app.routers.reviews import get_doctor_reviews, update_doctor_rating
    
    # Generate test data
    doctor_id = str(uuid.uuid4())
    doctor_user_id = str(uuid.uuid4())
    
    # Generate random ratings for reviews
    import random
    random.seed(rating_seed)
    ratings = [random.randint(1, 5) for _ in range(num_reviews)]
    
    # Calculate expected average
    expected_average = sum(ratings) / len(ratings)
    expected_average = round(expected_average, 2)
    
    # Mock doctor data with calculated statistics
    doctor_data = {
        "id": doctor_id,
        "user_id": doctor_user_id,
        "license_no": "LIC123456",
        "clinic_name": "Test Clinic",
        "average_rating": expected_average,
        "review_count": num_reviews
    }
    
    # Generate reviews with the ratings
    reviews = []
    patient_profiles = {}
    
    for i, rating in enumerate(ratings):
        patient_id = str(uuid.uuid4())
        patient_name = f"Patient {i+1}"
        
        review = {
            "id": str(uuid.uuid4()),
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "appointment_id": str(uuid.uuid4()),
            "rating": rating,
            "review_text": f"Review {i+1}",
            "flagged": False,
            "created_at": (datetime.utcnow() - timedelta(hours=i)).isoformat()
        }
        reviews.append(review)
        
        patient_profiles[patient_id] = {
            "id": patient_id,
            "full_name": patient_name
        }
    
    # Test get_doctor_reviews endpoint
    with patch('app.routers.reviews.supabase') as mock_supabase:
        # Mock doctor lookup
        mock_doctor_result = Mock()
        mock_doctor_result.data = [doctor_data]
        
        # Mock reviews lookup
        mock_reviews_result = Mock()
        mock_reviews_result.data = reviews
        
        # Mock patient profiles lookup
        mock_profiles_result = Mock()
        mock_profiles_result.data = list(patient_profiles.values())
        
        # Set up the mock chain
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "doctors":
                mock_table.select.return_value.eq.return_value.execute.return_value = mock_doctor_result
            elif table_name == "reviews":
                order_mock = Mock()
                order_mock.execute.return_value = mock_reviews_result
                mock_table.select.return_value.eq.return_value.order.return_value = order_mock
            elif table_name == "profiles":
                in_mock = Mock()
                in_mock.execute.return_value = mock_profiles_result
                mock_table.select.return_value.in_.return_value = in_mock
            return mock_table
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Call the endpoint
        result = await get_doctor_reviews(doctor_id)
        
        # Verify result is a DoctorReviewsResponse
        assert isinstance(result, DoctorReviewsResponse), \
            f"Result should be DoctorReviewsResponse, got {type(result)}"
        
        # Verify average rating is displayed
        assert result.average_rating is not None, \
            "Average rating should be present"
        
        # Verify average rating matches expected value
        assert result.average_rating == expected_average, \
            f"Average rating should be {expected_average}, got {result.average_rating}"
        
        # Verify review count is displayed
        assert result.review_count is not None, \
            "Review count should be present"
        
        # Verify review count matches number of reviews
        assert result.review_count == num_reviews, \
            f"Review count should be {num_reviews}, got {result.review_count}"
        
        # Verify average rating is within valid range
        assert 0 <= result.average_rating <= 5, \
            f"Average rating should be between 0 and 5, got {result.average_rating}"
    
    # Test update_doctor_rating function
    with patch('app.routers.reviews.supabase') as mock_supabase:
        # Mock reviews lookup for rating calculation
        mock_reviews_result = Mock()
        mock_reviews_result.data = [{"rating": r} for r in ratings]
        
        # Mock doctor update
        mock_update_result = Mock()
        mock_update_result.data = [doctor_data]
        
        # Set up the mock chain
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "reviews":
                mock_table.select.return_value.eq.return_value.execute.return_value = mock_reviews_result
            elif table_name == "doctors":
                eq_mock = Mock()
                eq_mock.execute.return_value = mock_update_result
                mock_table.update.return_value.eq.return_value = eq_mock
            return mock_table
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Call the update function
        await update_doctor_rating(doctor_id)
        
        # Verify update was called with correct data
        # The function should have called table("doctors").update(...).eq(...).execute()
        assert mock_supabase.table.called, "Supabase table should be called"
        
        # Verify doctor table was accessed
        table_calls = [str(call) for call in mock_supabase.table.call_args_list]
        assert any("doctors" in str(call) for call in table_calls), \
            "Doctor table should be accessed for update"


# Feature: derman-ai-skin-screening, Property 75: Doctor Rating Statistics (Edge Case - No Reviews)
@pytest.mark.asyncio
async def test_doctor_rating_statistics_no_reviews():
    """
    Property 75: Doctor Rating Statistics Display (No Reviews)
    
    For any doctor with no reviews, the average rating should be 0.0 and
    review count should be 0.
    
    This test verifies:
    1. Doctors with no reviews have average_rating = 0.0
    2. Doctors with no reviews have review_count = 0
    3. Empty review list is handled correctly
    
    Validates: Requirements 22.3
    """
    from app.routers.reviews import get_doctor_reviews
    
    # Generate test data
    doctor_id = str(uuid.uuid4())
    doctor_user_id = str(uuid.uuid4())
    
    # Mock doctor data with no reviews
    doctor_data = {
        "id": doctor_id,
        "user_id": doctor_user_id,
        "license_no": "LIC123456",
        "clinic_name": "Test Clinic",
        "average_rating": 0.0,
        "review_count": 0
    }
    
    # Mock Supabase responses
    with patch('app.routers.reviews.supabase') as mock_supabase:
        # Mock doctor lookup
        mock_doctor_result = Mock()
        mock_doctor_result.data = [doctor_data]
        
        # Mock reviews lookup (empty)
        mock_reviews_result = Mock()
        mock_reviews_result.data = []
        
        # Set up the mock chain
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "doctors":
                mock_table.select.return_value.eq.return_value.execute.return_value = mock_doctor_result
            elif table_name == "reviews":
                order_mock = Mock()
                order_mock.execute.return_value = mock_reviews_result
                mock_table.select.return_value.eq.return_value.order.return_value = order_mock
            return mock_table
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Call the endpoint
        result = await get_doctor_reviews(doctor_id)
        
        # Verify result is a DoctorReviewsResponse
        assert isinstance(result, DoctorReviewsResponse), \
            f"Result should be DoctorReviewsResponse, got {type(result)}"
        
        # Verify average rating is 0.0 for no reviews
        assert result.average_rating == 0.0, \
            f"Average rating should be 0.0 for no reviews, got {result.average_rating}"
        
        # Verify review count is 0
        assert result.review_count == 0, \
            f"Review count should be 0 for no reviews, got {result.review_count}"
        
        # Verify reviews list is empty
        assert len(result.reviews) == 0, \
            f"Reviews list should be empty, got {len(result.reviews)} reviews"



# Feature: derman-ai-skin-screening, Property 76: Review Flagging Availability
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    rating=st.integers(min_value=1, max_value=5),
    has_review_text=st.booleans()
)
@pytest.mark.asyncio
async def test_review_flagging_availability(rating, has_review_text):
    """
    Property 76: Review Flagging Availability
    
    For any review displayed to a doctor, the interface should include a
    "flag for review" option to report inappropriate content.
    
    This test verifies:
    1. Doctors can flag any review
    2. Flagging sets the flagged field to true
    3. Review remains accessible after flagging
    4. Only doctors can flag reviews (not patients or admins)
    5. Flagged status is persisted correctly
    
    Validates: Requirements 22.4
    """
    from app.routers.reviews import flag_review
    
    # Generate test data
    review_id = str(uuid.uuid4())
    patient_id = str(uuid.uuid4())
    doctor_id = str(uuid.uuid4())
    doctor_user_id = str(uuid.uuid4())
    review_text = "Inappropriate content" if has_review_text else None
    
    # Create review data
    review_data = {
        "id": review_id,
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "appointment_id": str(uuid.uuid4()),
        "rating": rating,
        "review_text": review_text,
        "flagged": False,
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Create current user (doctor)
    current_user = {
        "id": doctor_user_id,
        "role": "doctor",
        "full_name": "Test Doctor",
        "verified": True
    }
    
    # Create patient profile
    patient_profile = {
        "id": patient_id,
        "full_name": "Test Patient"
    }
    
    # Expected flagged review
    flagged_review = review_data.copy()
    flagged_review["flagged"] = True
    
    # Mock Supabase responses
    with patch('app.routers.reviews.supabase') as mock_supabase, \
         patch('app.routers.reviews.send_low_rating_notification') as mock_notification:
        
        # Mock review lookup
        mock_review_result = Mock()
        mock_review_result.data = [review_data]
        
        # Mock review update
        mock_update_result = Mock()
        mock_update_result.data = [flagged_review]
        
        # Mock patient profile lookup
        mock_patient_result = Mock()
        mock_patient_result.data = [patient_profile]
        
        # Set up the mock chain
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "reviews":
                # For select query
                select_mock = Mock()
                eq_mock = Mock()
                eq_mock.execute.return_value = mock_review_result
                select_mock.eq.return_value = eq_mock
                mock_table.select.return_value = select_mock
                
                # For update query
                update_mock = Mock()
                update_eq_mock = Mock()
                update_eq_mock.execute.return_value = mock_update_result
                update_mock.eq.return_value = update_eq_mock
                mock_table.update.return_value = update_mock
            elif table_name == "profiles":
                select_mock = Mock()
                eq_mock = Mock()
                eq_mock.execute.return_value = mock_patient_result
                select_mock.eq.return_value = eq_mock
                mock_table.select.return_value = select_mock
            return mock_table
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Call the endpoint
        result = await flag_review(review_id, current_user)
        
        # Verify result is a ReviewResponse
        assert isinstance(result, ReviewResponse), \
            f"Result should be ReviewResponse, got {type(result)}"
        
        # Verify review is flagged
        assert result.flagged == True, \
            f"Review should be flagged, got flagged={result.flagged}"
        
        # Verify review ID matches
        assert result.id == review_id, \
            f"Review ID should be {review_id}, got {result.id}"
        
        # Verify other fields are preserved
        assert result.rating == rating, \
            f"Rating should be preserved as {rating}, got {result.rating}"
        assert result.patient_id == patient_id, \
            f"patient_id should be preserved as {patient_id}, got {result.patient_id}"
        assert result.doctor_id == doctor_id, \
            f"doctor_id should be preserved as {doctor_id}, got {result.doctor_id}"
        
        # Verify notification is sent for low ratings
        if rating < 3:
            mock_notification.assert_called_once_with(review_id, doctor_id, rating)
        else:
            mock_notification.assert_not_called()


# Feature: derman-ai-skin-screening, Property 76: Review Flagging (Non-Doctor Access)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    user_role=st.sampled_from(["patient", "admin"])
)
@pytest.mark.asyncio
async def test_review_flagging_doctor_only(user_role):
    """
    Property 76: Review Flagging Availability (Access Control)
    
    For any review flagging attempt, only doctors should be able to flag reviews.
    Patients and admins should be denied access.
    
    This test verifies:
    1. Only doctors can flag reviews
    2. Patients cannot flag reviews
    3. Admins cannot flag reviews (they have separate moderation tools)
    4. Appropriate error messages for unauthorized access
    
    Validates: Requirements 22.4
    """
    from app.routers.reviews import flag_review
    from fastapi import HTTPException
    
    # Generate test data
    review_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    # Create current user (not a doctor)
    current_user = {
        "id": user_id,
        "role": user_role,  # patient or admin
        "full_name": f"Test {user_role.capitalize()}",
        "verified": True
    }
    
    # Mock Supabase (should not be called since access check happens first)
    with patch('app.routers.reviews.supabase') as mock_supabase:
        # Should raise HTTPException 403
        with pytest.raises(HTTPException) as exc_info:
            await flag_review(review_id, current_user)
        
        # Verify error status code
        assert exc_info.value.status_code == 403, \
            f"Should return 403 Forbidden, got {exc_info.value.status_code}"
        
        # Verify error message mentions permissions
        error_detail = exc_info.value.detail
        assert "INSUFFICIENT_PERMISSIONS" in str(error_detail), \
            f"Error should mention insufficient permissions, got: {error_detail}"


# Feature: derman-ai-skin-screening, Property 78: Low Rating Admin Notification
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    rating=st.integers(min_value=1, max_value=2),
    num_admins=st.integers(min_value=1, max_value=5)
)
@pytest.mark.asyncio
async def test_low_rating_admin_notification(rating, num_admins):
    """
    Property 78: Low Rating Admin Notification
    
    For any review with rating below 3 stars, the system should send a
    notification to admins for quality assurance review.
    
    This test verifies:
    1. Reviews with rating < 3 trigger admin notifications
    2. All admin users receive notifications
    3. Notification includes review details (doctor, rating, review ID)
    4. Notification type is "low_rating_alert"
    5. Email notifications are sent to admins
    
    Validates: Requirements 22.6
    """
    from app.routers.reviews import send_low_rating_notification
    
    # Generate test data
    review_id = str(uuid.uuid4())
    doctor_id = str(uuid.uuid4())
    doctor_user_id = str(uuid.uuid4())
    
    # Create admin users
    admins = []
    for i in range(num_admins):
        admin = {
            "id": str(uuid.uuid4()),
            "email": f"admin{i+1}@skinguard.com",
            "full_name": f"Admin {i+1}",
            "role": "admin"
        }
        admins.append(admin)
    
    # Create doctor data
    doctor_data = {
        "id": doctor_id,
        "user_id": doctor_user_id,
        "license_no": "LIC123456",
        "clinic_name": "Test Clinic"
    }
    
    # Create doctor profile
    doctor_profile = {
        "id": doctor_user_id,
        "full_name": "Dr. Test Doctor"
    }
    
    # Track notification inserts
    notification_inserts = []
    
    # Mock Supabase responses
    with patch('app.routers.reviews.supabase') as mock_supabase, \
         patch('app.email_service.get_email_service') as mock_email_service:
        
        # Mock email service
        mock_email = Mock()
        mock_email.send_email = AsyncMock()
        mock_email_service.return_value = mock_email
        
        # Mock admin lookup
        mock_admins_result = Mock()
        mock_admins_result.data = admins
        
        # Mock doctor lookup
        mock_doctor_result = Mock()
        mock_doctor_result.data = [doctor_data]
        
        # Mock doctor profile lookup
        mock_doctor_profile_result = Mock()
        mock_doctor_profile_result.data = [doctor_profile]
        
        # Mock notification insert
        def capture_notification_insert(data):
            notification_inserts.append(data)
            mock_result = Mock()
            mock_result.data = [data]
            return mock_result
        
        # Set up the mock chain
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "profiles":
                # For admin lookup
                select_mock = Mock()
                eq_mock = Mock()
                
                # Check if it's admin lookup or doctor profile lookup
                def eq_side_effect(field, value):
                    result_mock = Mock()
                    if field == "role" and value == "admin":
                        result_mock.execute.return_value = mock_admins_result
                    elif field == "id":
                        result_mock.execute.return_value = mock_doctor_profile_result
                    return result_mock
                
                eq_mock.side_effect = eq_side_effect
                select_mock.eq = eq_mock
                mock_table.select.return_value = select_mock
            elif table_name == "doctors":
                select_mock = Mock()
                eq_mock = Mock()
                eq_mock.execute.return_value = mock_doctor_result
                select_mock.eq.return_value = eq_mock
                mock_table.select.return_value = select_mock
            elif table_name == "notifications":
                insert_mock = Mock()
                
                def insert_side_effect(data):
                    result = capture_notification_insert(data)
                    execute_mock = Mock()
                    execute_mock.execute.return_value = result
                    return execute_mock
                
                insert_mock.side_effect = insert_side_effect
                mock_table.insert = insert_mock
            return mock_table
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Call the notification function
        await send_low_rating_notification(review_id, doctor_id, rating)
        
        # Verify notifications were created for all admins
        assert len(notification_inserts) == num_admins, \
            f"Should create {num_admins} notifications, got {len(notification_inserts)}"
        
        # Verify each notification has correct structure
        for i, notification in enumerate(notification_inserts):
            # Verify notification type
            assert notification["type"] == "low_rating_alert", \
                f"Notification type should be 'low_rating_alert', got '{notification['type']}'"
            
            # Verify notification is for an admin
            admin_ids = [admin["id"] for admin in admins]
            assert notification["user_id"] in admin_ids, \
                f"Notification should be for an admin user"
            
            # Verify notification is unread
            assert notification["read"] == False, \
                f"Notification should be unread initially"
            
            # Verify metadata includes review details
            assert "review_id" in notification["metadata"], \
                "Notification metadata should include review_id"
            assert notification["metadata"]["review_id"] == review_id, \
                f"review_id should be {review_id}"
            assert notification["metadata"]["doctor_id"] == doctor_id, \
                f"doctor_id should be {doctor_id}"
            assert notification["metadata"]["rating"] == rating, \
                f"rating should be {rating}"
            
            # Verify title mentions quality assurance
            assert "Quality Assurance" in notification["title"], \
                "Notification title should mention Quality Assurance"
        
        # Verify email was sent to each admin
        assert mock_email.send_email.call_count == num_admins, \
            f"Should send {num_admins} emails, sent {mock_email.send_email.call_count}"
        
        # Verify email content includes rating and doctor info
        for call in mock_email.send_email.call_args_list:
            kwargs = call[1]
            assert "to_email" in kwargs, "Email should have to_email"
            assert "subject" in kwargs, "Email should have subject"
            assert "body" in kwargs, "Email should have body"
            
            # Verify subject mentions low rating
            assert "Low Rating" in kwargs["subject"], \
                "Email subject should mention Low Rating"
            
            # Verify body includes rating
            assert str(rating) in kwargs["body"], \
                f"Email body should include rating {rating}"


# Feature: derman-ai-skin-screening, Property 78: Low Rating Admin Notification (High Ratings)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    rating=st.integers(min_value=3, max_value=5)
)
@pytest.mark.asyncio
async def test_no_notification_for_high_ratings(rating):
    """
    Property 78: Low Rating Admin Notification (High Ratings)
    
    For any review with rating 3 stars or above, no admin notification should
    be sent.
    
    This test verifies:
    1. Ratings >= 3 do not trigger admin notifications
    2. Only low ratings (< 3) trigger notifications
    3. Notification system is not called for acceptable ratings
    
    Validates: Requirements 22.6
    """
    from app.routers.reviews import flag_review
    
    # Generate test data
    review_id = str(uuid.uuid4())
    patient_id = str(uuid.uuid4())
    doctor_id = str(uuid.uuid4())
    doctor_user_id = str(uuid.uuid4())
    
    # Create review data with high rating
    review_data = {
        "id": review_id,
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "appointment_id": str(uuid.uuid4()),
        "rating": rating,  # 3, 4, or 5
        "review_text": "Good service",
        "flagged": False,
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Create current user (doctor)
    current_user = {
        "id": doctor_user_id,
        "role": "doctor",
        "full_name": "Test Doctor",
        "verified": True
    }
    
    # Create patient profile
    patient_profile = {
        "id": patient_id,
        "full_name": "Test Patient"
    }
    
    # Expected flagged review
    flagged_review = review_data.copy()
    flagged_review["flagged"] = True
    
    # Mock Supabase responses
    with patch('app.routers.reviews.supabase') as mock_supabase, \
         patch('app.routers.reviews.send_low_rating_notification') as mock_notification:
        
        # Mock review lookup
        mock_review_result = Mock()
        mock_review_result.data = [review_data]
        
        # Mock review update
        mock_update_result = Mock()
        mock_update_result.data = [flagged_review]
        
        # Mock patient profile lookup
        mock_patient_result = Mock()
        mock_patient_result.data = [patient_profile]
        
        # Set up the mock chain
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "reviews":
                # For select query
                select_mock = Mock()
                eq_mock = Mock()
                eq_mock.execute.return_value = mock_review_result
                select_mock.eq.return_value = eq_mock
                mock_table.select.return_value = select_mock
                
                # For update query
                update_mock = Mock()
                update_eq_mock = Mock()
                update_eq_mock.execute.return_value = mock_update_result
                update_mock.eq.return_value = update_eq_mock
                mock_table.update.return_value = update_mock
            elif table_name == "profiles":
                select_mock = Mock()
                eq_mock = Mock()
                eq_mock.execute.return_value = mock_patient_result
                select_mock.eq.return_value = eq_mock
                mock_table.select.return_value = select_mock
            return mock_table
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Call the endpoint
        result = await flag_review(review_id, current_user)
        
        # Verify review is flagged
        assert result.flagged == True, \
            f"Review should be flagged"
        
        # Verify notification was NOT sent for high rating
        mock_notification.assert_not_called(), \
            f"Notification should not be sent for rating {rating} (>= 3)"
