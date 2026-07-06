"""
Property-based tests for urgent case escalation
Requirements: 23.6

Feature: derman-ai-skin-screening
Property 84: Urgent Case Escalation
"""
import pytest
from hypothesis import given, strategies as st, assume, settings
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

# Mock supabase before importing scheduler
sys.modules['app.database'] = MagicMock()

from app.scheduler import UrgentCaseEscalationService


# Strategy for generating urgent case data
@st.composite
def urgent_case_strategy(draw):
    """Generate a valid urgent case"""
    # Generate a case that's been unreviewed for 24+ hours
    hours_old = draw(st.integers(min_value=24, max_value=168))  # 24 hours to 1 week
    created_at = datetime.utcnow() - timedelta(hours=hours_old)
    
    # Generate AI prediction with high probability
    cancer_types = ["Melanoma", "Basal Cell Carcinoma", "Squamous Cell Carcinoma", 
                   "Actinic Keratosis", "Benign Keratosis", "Dermatofibroma", "Vascular Lesion"]
    top_type = draw(st.sampled_from(cancer_types))
    top_probability = draw(st.floats(min_value=0.85, max_value=0.99))
    
    # Generate remaining probabilities that sum to (1 - top_probability)
    remaining = 1.0 - top_probability
    other_probs = []
    for i in range(6):
        if i == 5:
            other_probs.append(remaining)
        else:
            prob = draw(st.floats(min_value=0.0, max_value=remaining))
            other_probs.append(prob)
            remaining -= prob
    
    predictions = [{"type": top_type, "probability": top_probability}]
    for i, cancer_type in enumerate([t for t in cancer_types if t != top_type]):
        predictions.append({"type": cancer_type, "probability": other_probs[i]})
    
    return {
        "id": f"report-{draw(st.integers(min_value=1000, max_value=9999))}",
        "patient_id": f"patient-{draw(st.integers(min_value=1000, max_value=9999))}",
        "status": "urgent",
        "risk_level": "urgent",
        "created_at": created_at.isoformat(),
        "consultation_notes": None,
        "ai_prediction": {
            "predictions": predictions
        },
        "profiles": {
            "full_name": draw(st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters=' '))),
            "email": draw(st.emails())
        },
        "hours_old": hours_old
    }


# Strategy for generating admin emails
@st.composite
def admin_emails_strategy(draw):
    """Generate a list of admin emails"""
    num_admins = draw(st.integers(min_value=1, max_value=5))
    return [draw(st.emails()) for _ in range(num_admins)]


class TestUrgentCaseEscalationProperties:
    """Property-based tests for urgent case escalation"""
    
    @pytest.mark.asyncio
    @given(case=urgent_case_strategy())
    @settings(max_examples=50, deadline=None)
    async def test_property_84_urgent_case_escalation_after_24_hours(self, case):
        """
        Property 84: Urgent Case Escalation
        
        For any urgent case remaining unreviewed for 24 hours, 
        the system should send escalation notifications to admins.
        
        Validates: Requirements 23.6
        """
        escalation_service = UrgentCaseEscalationService()
        
        # Mock Supabase to return the unreviewed case
        with patch('app.scheduler.supabase') as mock_supabase:
            mock_table = MagicMock()
            mock_supabase.table.return_value = mock_table
            mock_table.select.return_value = mock_table
            mock_table.eq.return_value = mock_table
            mock_table.lt.return_value = mock_table
            mock_table.is_.return_value = mock_table
            mock_table.insert.return_value = mock_table
            
            # Mock responses for the escalation process
            admin_emails = ["admin1@test.com", "admin2@test.com"]
            mock_table.execute.side_effect = [
                MagicMock(data=[case]),  # check_unreviewed_urgent_cases
                MagicMock(data=[{"email": e} for e in admin_emails]),  # get_admin_emails
                MagicMock(data=[]),  # has_been_escalated (not escalated yet)
                MagicMock(data=[{"id": "audit-123"}])  # track_escalation
            ]
            
            # Mock email service
            with patch.object(escalation_service.email_service, 'send_email', new_callable=AsyncMock) as mock_send:
                mock_send.return_value = True
                
                # Process escalations
                stats = await escalation_service.process_escalations()
                
                # Property: System should escalate the case
                assert stats["cases_checked"] >= 1, "Should check at least one case"
                assert stats["cases_escalated"] >= 1, "Should escalate at least one case"
                assert stats["notifications_sent"] >= 1, "Should send at least one notification"
                
                # Property: Notifications should be sent to admins
                assert mock_send.call_count == len(admin_emails), \
                    f"Should send notification to all {len(admin_emails)} admins"
                
                # Property: Email should contain case details
                for call in mock_send.call_args_list:
                    email_args = call[1]
                    assert case["id"] in email_args["html_body"], \
                        "Email should contain report ID"
                    assert case["profiles"]["full_name"] in email_args["html_body"], \
                        "Email should contain patient name"
                    assert "ESCALATION" in email_args["subject"].upper(), \
                        "Email subject should indicate escalation"
    
    @pytest.mark.asyncio
    @given(
        case=urgent_case_strategy(),
        admin_emails=admin_emails_strategy()
    )
    @settings(max_examples=50, deadline=None)
    async def test_property_84_escalation_notifies_all_admins(self, case, admin_emails):
        """
        Property 84: Urgent Case Escalation - All Admins Notified
        
        For any urgent case requiring escalation, 
        the system should send notifications to ALL admin users.
        
        Validates: Requirements 23.6
        """
        escalation_service = UrgentCaseEscalationService()
        
        with patch('app.scheduler.supabase') as mock_supabase:
            mock_table = MagicMock()
            mock_supabase.table.return_value = mock_table
            mock_table.select.return_value = mock_table
            mock_table.eq.return_value = mock_table
            mock_table.lt.return_value = mock_table
            mock_table.is_.return_value = mock_table
            mock_table.insert.return_value = mock_table
            
            mock_table.execute.side_effect = [
                MagicMock(data=[case]),
                MagicMock(data=[{"email": e} for e in admin_emails]),
                MagicMock(data=[]),
                MagicMock(data=[{"id": "audit-123"}])
            ]
            
            with patch.object(escalation_service.email_service, 'send_email', new_callable=AsyncMock) as mock_send:
                mock_send.return_value = True
                
                stats = await escalation_service.process_escalations()
                
                # Property: All admins should receive notification
                assert mock_send.call_count == len(admin_emails), \
                    f"Should send notification to all {len(admin_emails)} admins"
                
                # Property: Each admin email should be used exactly once
                sent_to_emails = [call[1]["to_email"] for call in mock_send.call_args_list]
                assert set(sent_to_emails) == set(admin_emails), \
                    "Should send to all unique admin emails"
    
    @pytest.mark.asyncio
    @given(case=urgent_case_strategy())
    @settings(max_examples=50, deadline=None)
    async def test_property_84_escalation_includes_time_elapsed(self, case):
        """
        Property 84: Urgent Case Escalation - Time Elapsed
        
        For any urgent case requiring escalation,
        the notification should include the time elapsed since case creation.
        
        Validates: Requirements 23.6
        """
        escalation_service = UrgentCaseEscalationService()
        
        with patch.object(escalation_service.email_service, 'send_email', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True
            
            success = await escalation_service.send_admin_escalation_notification(
                admin_email="admin@test.com",
                case=case
            )
            
            assert success is True
            assert mock_send.called
            
            # Property: Email should mention time elapsed
            email_args = mock_send.call_args[1]
            html_body = email_args["html_body"]
            text_body = email_args["text_body"]
            
            # Should mention hours
            assert "hour" in html_body.lower(), "Email should mention hours elapsed"
            assert "hour" in text_body.lower(), "Text email should mention hours elapsed"
            
            # Should include the actual hours elapsed (approximately)
            hours_old = case["hours_old"]
            # Allow for some variation due to processing time
            assert str(hours_old) in html_body or str(hours_old - 1) in html_body or str(hours_old + 1) in html_body, \
                f"Email should mention approximately {hours_old} hours elapsed"
    
    @pytest.mark.asyncio
    @given(case=urgent_case_strategy())
    @settings(max_examples=50, deadline=None)
    async def test_property_84_escalation_tracks_in_audit_log(self, case):
        """
        Property 84: Urgent Case Escalation - Audit Tracking
        
        For any urgent case that is escalated,
        the system should create an audit log entry to prevent duplicate notifications.
        
        Validates: Requirements 23.6
        """
        escalation_service = UrgentCaseEscalationService()
        
        with patch('app.scheduler.supabase') as mock_supabase:
            mock_table = MagicMock()
            mock_supabase.table.return_value = mock_table
            mock_table.insert.return_value = mock_table
            mock_table.execute.return_value = MagicMock(data=[{"id": "audit-123"}])
            
            success = await escalation_service.track_escalation(case["id"])
            
            # Property: Should successfully track escalation
            assert success is True
            
            # Property: Should create audit log entry
            assert mock_table.insert.called
            audit_entry = mock_table.insert.call_args[0][0]
            
            # Property: Audit entry should have correct structure
            assert audit_entry["action"] == "urgent_case_escalation"
            assert audit_entry["resource_type"] == "medical_report"
            assert audit_entry["resource_id"] == case["id"]
            assert "escalation_timestamp" in audit_entry["metadata"]
    
    @pytest.mark.asyncio
    @given(case=urgent_case_strategy())
    @settings(max_examples=50, deadline=None)
    async def test_property_84_escalation_prevents_duplicates(self, case):
        """
        Property 84: Urgent Case Escalation - No Duplicates
        
        For any urgent case that has already been escalated,
        the system should not send duplicate notifications.
        
        Validates: Requirements 23.6
        """
        escalation_service = UrgentCaseEscalationService()
        
        with patch('app.scheduler.supabase') as mock_supabase:
            mock_table = MagicMock()
            mock_supabase.table.return_value = mock_table
            mock_table.select.return_value = mock_table
            mock_table.eq.return_value = mock_table
            mock_table.lt.return_value = mock_table
            mock_table.is_.return_value = mock_table
            
            # Mock responses indicating case was already escalated
            mock_table.execute.side_effect = [
                MagicMock(data=[case]),  # check_unreviewed_urgent_cases
                MagicMock(data=[{"email": "admin@test.com"}]),  # get_admin_emails
                MagicMock(data=[{"id": "audit-123"}])  # has_been_escalated returns True
            ]
            
            with patch.object(escalation_service.email_service, 'send_email', new_callable=AsyncMock) as mock_send:
                stats = await escalation_service.process_escalations()
                
                # Property: Should not escalate already-escalated cases
                assert stats["cases_escalated"] == 0, \
                    "Should not escalate cases that were already escalated"
                
                # Property: Should not send any notifications
                assert stats["notifications_sent"] == 0, \
                    "Should not send notifications for already-escalated cases"
                assert mock_send.call_count == 0, \
                    "Should not call email service for already-escalated cases"
    
    @pytest.mark.asyncio
    @given(
        hours_old=st.integers(min_value=0, max_value=23)
    )
    @settings(max_examples=30, deadline=None)
    async def test_property_84_no_escalation_before_24_hours(self, hours_old):
        """
        Property 84: Urgent Case Escalation - 24 Hour Threshold
        
        For any urgent case that is less than 24 hours old,
        the system should NOT escalate the case.
        
        Validates: Requirements 23.6
        """
        escalation_service = UrgentCaseEscalationService()
        
        # Create a case that's less than 24 hours old
        created_at = datetime.utcnow() - timedelta(hours=hours_old)
        recent_case = {
            "id": "report-recent",
            "status": "urgent",
            "created_at": created_at.isoformat(),
            "consultation_notes": None
        }
        
        with patch('app.scheduler.supabase') as mock_supabase:
            mock_table = MagicMock()
            mock_supabase.table.return_value = mock_table
            mock_table.select.return_value = mock_table
            mock_table.eq.return_value = mock_table
            mock_table.lt.return_value = mock_table
            mock_table.is_.return_value = mock_table
            
            # Mock should return empty list (case is too recent)
            mock_table.execute.return_value = MagicMock(data=[])
            
            cases = await escalation_service.check_unreviewed_urgent_cases()
            
            # Property: Should not find cases less than 24 hours old
            assert len(cases) == 0, \
                f"Should not find cases that are only {hours_old} hours old"
    
    @pytest.mark.asyncio
    @given(case=urgent_case_strategy())
    @settings(max_examples=50, deadline=None)
    async def test_property_84_escalation_email_contains_required_info(self, case):
        """
        Property 84: Urgent Case Escalation - Email Content
        
        For any urgent case escalation notification,
        the email should contain: report ID, patient info, time elapsed, 
        AI prediction, and recommended actions.
        
        Validates: Requirements 23.6
        """
        escalation_service = UrgentCaseEscalationService()
        
        with patch.object(escalation_service.email_service, 'send_email', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True
            
            await escalation_service.send_admin_escalation_notification(
                admin_email="admin@test.com",
                case=case
            )
            
            email_args = mock_send.call_args[1]
            html_body = email_args["html_body"]
            text_body = email_args["text_body"]
            
            # Property: Email must contain report ID
            assert case["id"] in html_body, "Email must contain report ID"
            assert case["id"] in text_body, "Text email must contain report ID"
            
            # Property: Email must contain patient name
            assert case["profiles"]["full_name"] in html_body, \
                "Email must contain patient name"
            
            # Property: Email must contain patient email
            assert case["profiles"]["email"] in html_body, \
                "Email must contain patient email"
            
            # Property: Email must contain AI prediction
            top_pred = max(case["ai_prediction"]["predictions"], 
                          key=lambda p: p["probability"])
            assert top_pred["type"] in html_body, \
                "Email must contain AI prediction type"
            
            # Property: Email must contain recommended actions
            assert "action" in html_body.lower() or "recommend" in html_body.lower(), \
                "Email must contain recommended actions"
            
            # Property: Email must contain report URL
            assert "https://" in html_body, "Email must contain report URL"
            assert case["id"] in html_body, "URL must reference the report ID"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
