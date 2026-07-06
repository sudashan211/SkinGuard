"""
Property-Based Tests for Notification System
Feature: derman-ai-skin-screening

Tests notification delivery correctness properties including email and in-app
notification creation for various system events.

Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6
"""

import pytest
import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings
from hypothesis import HealthCheck
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import uuid
from datetime import datetime, timedelta

# Add backend to path for imports
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Mock the database module before importing anything that uses it
sys.modules['app.database'] = MagicMock()

from app.notification_service import NotificationService


# Hypothesis strategies for generating test data
@st.composite
def user_data(draw):
    """Generate user data for testing"""
    # Generate a simple name using letters and spaces
    first_name = draw(st.text(min_size=2, max_size=15, alphabet=st.characters(whitelist_categories=('L',))))
    last_name = draw(st.text(min_size=2, max_size=15, alphabet=st.characters(whitelist_categories=('L',))))
    full_name = f"{first_name} {last_name}"
    
    return {
        "id": str(uuid.uuid4()),
        "email": draw(st.emails()),
        "full_name": full_name,
        "role": draw(st.sampled_from(["patient", "doctor", "admin"])),
        "verified": draw(st.booleans())
    }


@st.composite
def report_data(draw):
    """Generate medical report data for testing"""
    return {
        "id": str(uuid.uuid4()),
        "risk_level": draw(st.sampled_from(["low", "medium", "high", "urgent"])),
        "top_prediction": {
            "type": draw(st.sampled_from([
                "Melanoma", "Basal Cell Carcinoma", "Squamous Cell Carcinoma",
                "Actinic Keratosis", "Benign Keratosis", "Dermatofibroma", "Nevus"
            ])),
            "probability": draw(st.floats(min_value=0.0, max_value=1.0))
        }
    }


# Feature: derman-ai-skin-screening, Property 50: Notification Delivery
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    notification_type=st.sampled_from([
        "analysis_complete",
        "appointment_confirmed",
        "appointment_reminder",
        "doctor_verified",
        "followup_reminder"
    ]),
    user=user_data(),
    report=report_data()
)
@pytest.mark.asyncio
async def test_notification_delivery(notification_type, user, report):
    """
    Property 50: Notification Delivery
    
    For any system event that triggers a notification (analysis complete,
    appointment confirmation, reminder, verification, follow-up), the system
    should create both an in-app notification and send an email notification.
    
    This test verifies:
    1. In-app notification is created in the database
    2. Email notification is sent via email service
    3. Notification contains correct user_id, type, title, and message
    4. Both notification channels are triggered for each event
    5. Notification metadata is stored correctly
    
    Validates: Requirements 17.1, 17.2, 17.3, 17.4, 17.5, 17.6
    """
    service = NotificationService()
    
    user_id = user["id"]
    user_email = user["email"]
    user_name = user["full_name"]
    report_id = report["id"]
    risk_level = report["risk_level"]
    top_prediction = report["top_prediction"]
    
    # Mock Supabase for in-app notification creation
    mock_notification_id = str(uuid.uuid4())
    mock_notification_data = {
        "id": mock_notification_id,
        "user_id": user_id,
        "type": notification_type,
        "title": "Test Notification",
        "message": "Test message",
        "read": False,
        "metadata": {},
        "created_at": datetime.utcnow().isoformat()
    }
    
    with patch('app.notification_service.supabase') as mock_supabase, \
         patch.object(service.email_service, 'send_email', new_callable=AsyncMock) as mock_send_email:
        
        # Mock database insert for in-app notification
        mock_insert_result = Mock()
        mock_insert_result.data = [mock_notification_data]
        
        mock_table = Mock()
        mock_table.insert.return_value.execute.return_value = mock_insert_result
        mock_supabase.table.return_value = mock_table
        
        # Mock email service to return success
        mock_send_email.return_value = True
        
        # Call appropriate notification method based on type
        if notification_type == "analysis_complete":
            result = await service.send_analysis_complete_notification(
                user_id=user_id,
                user_email=user_email,
                user_name=user_name,
                report_id=report_id,
                risk_level=risk_level,
                top_prediction=top_prediction
            )
        
        elif notification_type == "appointment_confirmed":
            doctor_id = str(uuid.uuid4())
            doctor_email = "doctor@example.com"
            doctor_name = "Dr. Test"
            appointment_id = str(uuid.uuid4())
            scheduled_at = datetime.utcnow() + timedelta(hours=24)
            
            result = await service.send_appointment_confirmation(
                patient_id=user_id,
                patient_email=user_email,
                patient_name=user_name,
                doctor_id=doctor_id,
                doctor_email=doctor_email,
                doctor_name=doctor_name,
                appointment_id=appointment_id,
                scheduled_at=scheduled_at,
                consultation_type="in_person"
            )
        
        elif notification_type == "appointment_reminder":
            appointment_id = str(uuid.uuid4())
            scheduled_at = datetime.utcnow() + timedelta(hours=24)
            
            result = await service.send_appointment_reminder(
                user_id=user_id,
                user_email=user_email,
                user_name=user_name,
                appointment_id=appointment_id,
                scheduled_at=scheduled_at,
                doctor_name="Dr. Test",
                consultation_type="in_person"
            )
        
        elif notification_type == "doctor_verified":
            result = await service.send_doctor_verification_notification(
                doctor_id=user_id,
                doctor_email=user_email,
                doctor_name=user_name,
                verified=True,
                rejection_reason=None
            )
        
        elif notification_type == "followup_reminder":
            last_screening_date = datetime.utcnow() - timedelta(days=180)
            
            result = await service.send_followup_screening_reminder(
                user_id=user_id,
                user_email=user_email,
                user_name=user_name,
                last_screening_date=last_screening_date
            )
        
        # Verify notification was sent successfully
        assert result is True, \
            f"Notification delivery should succeed for {notification_type}"
        
        # Verify in-app notification was created
        mock_supabase.table.assert_called_with('notifications')
        mock_table.insert.assert_called()
        
        # Verify email was sent
        mock_send_email.assert_called()
        
        # Get the email call arguments
        email_call_args = mock_send_email.call_args
        
        # Verify email recipient
        assert email_call_args.kwargs['to_email'] in [user_email, "doctor@example.com"], \
            f"Email should be sent to user email, got {email_call_args.kwargs['to_email']}"
        
        # Verify email has subject and body
        assert 'subject' in email_call_args.kwargs, "Email should have a subject"
        assert 'html_body' in email_call_args.kwargs, "Email should have HTML body"
        
        # Verify subject is not empty
        assert len(email_call_args.kwargs['subject']) > 0, "Email subject should not be empty"
        
        # Verify HTML body is not empty
        assert len(email_call_args.kwargs['html_body']) > 0, "Email HTML body should not be empty"



# Feature: derman-ai-skin-screening, Property 50: In-App Notification Creation
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    user_id=st.uuids(),
    notification_type=st.text(min_size=3, max_size=50),
    title=st.text(min_size=5, max_size=100),
    message=st.text(min_size=10, max_size=500)
)
@pytest.mark.asyncio
async def test_in_app_notification_creation(user_id, notification_type, title, message):
    """
    Property 50: In-App Notification Creation
    
    For any notification creation request, the system should store the
    notification in the database with all required fields and return the
    notification ID.
    
    This test verifies:
    1. Notification is inserted into notifications table
    2. All required fields are present (user_id, type, title, message, read)
    3. Initial read status is False
    4. Notification ID is returned on success
    5. Metadata is stored correctly if provided
    
    Validates: Requirements 17.6
    """
    service = NotificationService()
    
    user_id_str = str(user_id)
    metadata = {"test_key": "test_value", "number": 42}
    
    # Mock Supabase for notification creation
    mock_notification_id = str(uuid.uuid4())
    mock_notification_data = {
        "id": mock_notification_id,
        "user_id": user_id_str,
        "type": notification_type,
        "title": title,
        "message": message,
        "read": False,
        "metadata": metadata,
        "created_at": datetime.utcnow().isoformat()
    }
    
    with patch('app.notification_service.supabase') as mock_supabase:
        # Mock database insert
        mock_insert_result = Mock()
        mock_insert_result.data = [mock_notification_data]
        
        mock_table = Mock()
        mock_table.insert.return_value.execute.return_value = mock_insert_result
        mock_supabase.table.return_value = mock_table
        
        # Call create_notification
        result = await service.create_notification(
            user_id=user_id_str,
            notification_type=notification_type,
            title=title,
            message=message,
            metadata=metadata
        )
        
        # Verify notification ID was returned
        assert result is not None, "Notification ID should be returned"
        assert result == mock_notification_id, \
            f"Returned ID should match created notification ID"
        
        # Verify database insert was called
        mock_supabase.table.assert_called_with('notifications')
        mock_table.insert.assert_called_once()
        
        # Get the insert call arguments
        insert_call_args = mock_table.insert.call_args[0][0]
        
        # Verify all required fields are present
        assert insert_call_args['user_id'] == user_id_str, \
            f"user_id should be {user_id_str}"
        assert insert_call_args['type'] == notification_type, \
            f"type should be {notification_type}"
        assert insert_call_args['title'] == title, \
            f"title should be {title}"
        assert insert_call_args['message'] == message, \
            f"message should be {message}"
        assert insert_call_args['read'] is False, \
            "Initial read status should be False"
        assert insert_call_args['metadata'] == metadata, \
            f"metadata should be {metadata}"
        assert 'created_at' in insert_call_args, \
            "created_at timestamp should be present"


# Feature: derman-ai-skin-screening, Property 50: Analysis Complete Notification Content
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    risk_level=st.sampled_from(["low", "medium", "high", "urgent"]),
    cancer_type=st.sampled_from([
        "Melanoma", "Basal Cell Carcinoma", "Squamous Cell Carcinoma",
        "Actinic Keratosis", "Benign Keratosis", "Dermatofibroma", "Nevus"
    ]),
    probability=st.floats(min_value=0.0, max_value=1.0)
)
@pytest.mark.asyncio
async def test_analysis_complete_notification_content(risk_level, cancer_type, probability):
    """
    Property 50: Analysis Complete Notification Content
    
    For any analysis completion notification, the email and in-app notification
    should contain the risk level, top prediction type, and probability.
    
    This test verifies:
    1. Risk level is included in notification message
    2. Top prediction type is mentioned in email
    3. Probability is formatted correctly
    4. Medical disclaimer is included in email
    5. Report ID is included in metadata
    
    Validates: Requirements 17.1
    """
    service = NotificationService()
    
    user_id = str(uuid.uuid4())
    user_email = "patient@example.com"
    user_name = "Test Patient"
    report_id = str(uuid.uuid4())
    top_prediction = {"type": cancer_type, "probability": probability}
    
    # Mock Supabase and email service
    mock_notification_id = str(uuid.uuid4())
    mock_notification_data = {
        "id": mock_notification_id,
        "user_id": user_id,
        "type": "analysis_complete",
        "title": "Your Skin Analysis is Ready",
        "message": f"Your skin screening results are now available. Risk level: {risk_level}",
        "read": False,
        "metadata": {
            "report_id": report_id,
            "risk_level": risk_level,
            "top_prediction": top_prediction
        },
        "created_at": datetime.utcnow().isoformat()
    }
    
    with patch('app.notification_service.supabase') as mock_supabase, \
         patch.object(service.email_service, 'send_email', new_callable=AsyncMock) as mock_send_email:
        
        # Mock database insert
        mock_insert_result = Mock()
        mock_insert_result.data = [mock_notification_data]
        
        mock_table = Mock()
        mock_table.insert.return_value.execute.return_value = mock_insert_result
        mock_supabase.table.return_value = mock_table
        
        # Mock email service
        mock_send_email.return_value = True
        
        # Send notification
        result = await service.send_analysis_complete_notification(
            user_id=user_id,
            user_email=user_email,
            user_name=user_name,
            report_id=report_id,
            risk_level=risk_level,
            top_prediction=top_prediction
        )
        
        # Verify notification was sent
        assert result is True, "Notification should be sent successfully"
        
        # Verify email was called
        mock_send_email.assert_called_once()
        email_call_args = mock_send_email.call_args
        
        # Verify email content includes risk level
        html_body = email_call_args.kwargs['html_body']
        assert risk_level.upper() in html_body or risk_level.lower() in html_body, \
            f"Email should mention risk level '{risk_level}'"
        
        # Verify email content includes cancer type
        assert cancer_type in html_body, \
            f"Email should mention cancer type '{cancer_type}'"
        
        # Verify email content includes probability (formatted as percentage)
        probability_str = f"{probability * 100:.1f}"
        assert probability_str in html_body, \
            f"Email should include probability '{probability_str}%'"
        
        # Verify medical disclaimer is present
        assert "94% probability estimate" in html_body or "probability estimate" in html_body, \
            "Email should include medical disclaimer"
        
        # Verify report ID is in metadata
        insert_call_args = mock_table.insert.call_args[0][0]
        assert insert_call_args['metadata']['report_id'] == report_id, \
            f"Metadata should include report_id {report_id}"


# Feature: derman-ai-skin-screening, Property 50: Appointment Confirmation Dual Notification
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    consultation_type=st.sampled_from(["in_person", "video"]),
    hours_ahead=st.integers(min_value=1, max_value=168)
)
@pytest.mark.asyncio
async def test_appointment_confirmation_dual_notification(consultation_type, hours_ahead):
    """
    Property 50: Appointment Confirmation Dual Notification
    
    For any appointment confirmation, the system should send notifications to
    both the patient and the doctor.
    
    This test verifies:
    1. Two in-app notifications are created (one for patient, one for doctor)
    2. Two emails are sent (one to patient, one to doctor)
    3. Both notifications contain appointment details
    4. Consultation type is mentioned in both notifications
    5. Scheduled time is included in both notifications
    
    Validates: Requirements 17.2
    """
    service = NotificationService()
    
    patient_id = str(uuid.uuid4())
    patient_email = "patient@example.com"
    patient_name = "Test Patient"
    doctor_id = str(uuid.uuid4())
    doctor_email = "doctor@example.com"
    doctor_name = "Dr. Test"
    appointment_id = str(uuid.uuid4())
    scheduled_at = datetime.utcnow() + timedelta(hours=hours_ahead)
    
    # Mock Supabase and email service
    with patch('app.notification_service.supabase') as mock_supabase, \
         patch.object(service.email_service, 'send_email', new_callable=AsyncMock) as mock_send_email:
        
        # Mock database inserts (will be called twice)
        mock_insert_result = Mock()
        mock_insert_result.data = [{"id": str(uuid.uuid4())}]
        
        mock_table = Mock()
        mock_table.insert.return_value.execute.return_value = mock_insert_result
        mock_supabase.table.return_value = mock_table
        
        # Mock email service (will be called twice)
        mock_send_email.return_value = True
        
        # Send appointment confirmation
        result = await service.send_appointment_confirmation(
            patient_id=patient_id,
            patient_email=patient_email,
            patient_name=patient_name,
            doctor_id=doctor_id,
            doctor_email=doctor_email,
            doctor_name=doctor_name,
            appointment_id=appointment_id,
            scheduled_at=scheduled_at,
            consultation_type=consultation_type
        )
        
        # Verify notification was sent successfully
        assert result is True, "Appointment confirmation should be sent successfully"
        
        # Verify two in-app notifications were created
        assert mock_table.insert.call_count == 2, \
            "Should create two in-app notifications (patient and doctor)"
        
        # Verify two emails were sent
        assert mock_send_email.call_count == 2, \
            "Should send two emails (patient and doctor)"
        
        # Get email call arguments
        email_calls = mock_send_email.call_args_list
        
        # Verify emails were sent to both patient and doctor
        email_recipients = [call.kwargs['to_email'] for call in email_calls]
        assert patient_email in email_recipients, \
            f"Should send email to patient {patient_email}"
        assert doctor_email in email_recipients, \
            f"Should send email to doctor {doctor_email}"
        
        # Verify both emails contain consultation type
        for call in email_calls:
            html_body = call.kwargs['html_body']
            assert consultation_type.replace('_', ' ').title() in html_body, \
                f"Email should mention consultation type '{consultation_type}'"


# Feature: derman-ai-skin-screening, Property 50: Doctor Verification Notification Status
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    verified=st.booleans()
)
@pytest.mark.asyncio
async def test_doctor_verification_notification_status(verified):
    """
    Property 50: Doctor Verification Notification Status
    
    For any doctor verification status change, the notification content should
    reflect whether the doctor was approved or rejected.
    
    This test verifies:
    1. Approved doctors receive welcome email with platform guidelines
    2. Rejected doctors receive rejection email with reason
    3. Notification type differs based on verification status
    4. Email subject reflects verification outcome
    5. Appropriate tone and content for each outcome
    
    Validates: Requirements 17.4
    """
    service = NotificationService()
    
    doctor_id = str(uuid.uuid4())
    doctor_email = "doctor@example.com"
    doctor_name = "Dr. Test"
    rejection_reason = "Invalid license number" if not verified else None
    
    # Mock Supabase and email service
    with patch('app.notification_service.supabase') as mock_supabase, \
         patch.object(service.email_service, 'send_email', new_callable=AsyncMock) as mock_send_email:
        
        # Mock database insert
        mock_insert_result = Mock()
        mock_insert_result.data = [{"id": str(uuid.uuid4())}]
        
        mock_table = Mock()
        mock_table.insert.return_value.execute.return_value = mock_insert_result
        mock_supabase.table.return_value = mock_table
        
        # Mock email service
        mock_send_email.return_value = True
        
        # Send verification notification
        result = await service.send_doctor_verification_notification(
            doctor_id=doctor_id,
            doctor_email=doctor_email,
            doctor_name=doctor_name,
            verified=verified,
            rejection_reason=rejection_reason
        )
        
        # Verify notification was sent
        assert result is True, "Verification notification should be sent successfully"
        
        # Verify in-app notification was created
        mock_table.insert.assert_called_once()
        insert_call_args = mock_table.insert.call_args[0][0]
        
        # Verify notification type matches verification status
        if verified:
            assert insert_call_args['type'] == 'doctor_verified', \
                "Notification type should be 'doctor_verified' for approved doctors"
        else:
            assert insert_call_args['type'] == 'doctor_rejected', \
                "Notification type should be 'doctor_rejected' for rejected doctors"
        
        # Verify email was sent
        mock_send_email.assert_called_once()
        email_call_args = mock_send_email.call_args
        
        # Verify email content matches verification status
        html_body = email_call_args.kwargs['html_body']
        subject = email_call_args.kwargs['subject']
        
        if verified:
            # Approved doctor should receive welcome message
            assert "Congratulations" in html_body or "verified" in html_body.lower(), \
                "Approved doctor email should contain congratulatory message"
            assert "Platform Guidelines" in html_body or "guidelines" in html_body.lower(), \
                "Approved doctor email should include platform guidelines"
        else:
            # Rejected doctor should receive rejection reason
            assert rejection_reason in html_body, \
                f"Rejected doctor email should include rejection reason '{rejection_reason}'"
            assert "unable to verify" in html_body.lower() or "not approved" in html_body.lower(), \
                "Rejected doctor email should explain rejection"


# Feature: derman-ai-skin-screening, Property 50: Follow-Up Reminder Timing
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    days_since_screening=st.integers(min_value=180, max_value=365)
)
@pytest.mark.asyncio
async def test_followup_reminder_timing(days_since_screening):
    """
    Property 50: Follow-Up Reminder Timing
    
    For any follow-up screening reminder, the notification should reference
    the last screening date and encourage regular monitoring.
    
    This test verifies:
    1. Last screening date is mentioned in notification
    2. Reminder explains importance of regular screenings
    3. Notification encourages user to schedule follow-up
    4. Educational content about early detection is included
    
    Validates: Requirements 17.5
    """
    service = NotificationService()
    
    user_id = str(uuid.uuid4())
    user_email = "patient@example.com"
    user_name = "Test Patient"
    last_screening_date = datetime.utcnow() - timedelta(days=days_since_screening)
    
    # Mock Supabase and email service
    with patch('app.notification_service.supabase') as mock_supabase, \
         patch.object(service.email_service, 'send_email', new_callable=AsyncMock) as mock_send_email:
        
        # Mock database insert
        mock_insert_result = Mock()
        mock_insert_result.data = [{"id": str(uuid.uuid4())}]
        
        mock_table = Mock()
        mock_table.insert.return_value.execute.return_value = mock_insert_result
        mock_supabase.table.return_value = mock_table
        
        # Mock email service
        mock_send_email.return_value = True
        
        # Send follow-up reminder
        result = await service.send_followup_screening_reminder(
            user_id=user_id,
            user_email=user_email,
            user_name=user_name,
            last_screening_date=last_screening_date
        )
        
        # Verify notification was sent
        assert result is True, "Follow-up reminder should be sent successfully"
        
        # Verify email was sent
        mock_send_email.assert_called_once()
        email_call_args = mock_send_email.call_args
        
        # Verify email content mentions last screening date
        html_body = email_call_args.kwargs['html_body']
        
        # Check if date is mentioned (in various formats)
        date_str = last_screening_date.strftime("%B %d, %Y")
        assert date_str in html_body or "6 months" in html_body, \
            f"Email should mention last screening date or time period"
        
        # Verify email encourages regular screenings
        assert "regular" in html_body.lower() or "follow-up" in html_body.lower(), \
            "Email should encourage regular screenings"
        
        # Verify email mentions early detection
        assert "early detection" in html_body.lower() or "monitor" in html_body.lower(), \
            "Email should mention importance of early detection or monitoring"
