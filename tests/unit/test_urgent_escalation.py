"""
Unit tests for urgent case escalation system
Requirements: 23.6
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch, Mock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

# Mock supabase before importing scheduler
sys.modules['app.database'] = MagicMock()

from app.scheduler import UrgentCaseEscalationService


@pytest.fixture
def escalation_service():
    """Create escalation service instance"""
    return UrgentCaseEscalationService()


@pytest.fixture
def mock_urgent_case():
    """Create a mock urgent case"""
    created_at = datetime.utcnow() - timedelta(hours=25)
    return {
        "id": "report-123",
        "patient_id": "patient-456",
        "status": "urgent",
        "risk_level": "urgent",
        "created_at": created_at.isoformat(),
        "consultation_notes": None,
        "ai_prediction": {
            "predictions": [
                {"type": "Melanoma", "probability": 0.92},
                {"type": "Basal Cell Carcinoma", "probability": 0.05},
                {"type": "Benign", "probability": 0.03}
            ]
        },
        "profiles": {
            "full_name": "John Doe",
            "email": "john.doe@example.com"
        }
    }


@pytest.fixture
def mock_admin_emails():
    """Create mock admin emails"""
    return ["admin1@skinguard.com", "admin2@skinguard.com"]


class TestUrgentCaseEscalation:
    """Test urgent case escalation functionality"""
    
    @pytest.mark.asyncio
    async def test_check_unreviewed_urgent_cases_finds_old_cases(self, escalation_service):
        """Test that check finds urgent cases older than 24 hours"""
        # Mock Supabase response
        mock_case = {
            "id": "report-123",
            "status": "urgent",
            "created_at": (datetime.utcnow() - timedelta(hours=25)).isoformat(),
            "consultation_notes": None
        }
        
        with patch('app.scheduler.supabase') as mock_supabase:
            mock_table = MagicMock()
            mock_supabase.table.return_value = mock_table
            mock_table.select.return_value = mock_table
            mock_table.eq.return_value = mock_table
            mock_table.lt.return_value = mock_table
            mock_table.is_.return_value = mock_table
            mock_table.execute.return_value = MagicMock(data=[mock_case])
            
            cases = await escalation_service.check_unreviewed_urgent_cases()
            
            assert len(cases) == 1
            assert cases[0]["id"] == "report-123"
            assert cases[0]["status"] == "urgent"
    
    @pytest.mark.asyncio
    async def test_check_unreviewed_urgent_cases_ignores_recent_cases(self, escalation_service):
        """Test that check ignores urgent cases less than 24 hours old"""
        with patch('app.scheduler.supabase') as mock_supabase:
            mock_table = MagicMock()
            mock_supabase.table.return_value = mock_table
            mock_table.select.return_value = mock_table
            mock_table.eq.return_value = mock_table
            mock_table.lt.return_value = mock_table
            mock_table.is_.return_value = mock_table
            mock_table.execute.return_value = MagicMock(data=[])
            
            cases = await escalation_service.check_unreviewed_urgent_cases()
            
            assert len(cases) == 0
    
    @pytest.mark.asyncio
    async def test_check_unreviewed_urgent_cases_ignores_reviewed_cases(self, escalation_service):
        """Test that check ignores cases with consultation notes"""
        with patch('app.scheduler.supabase') as mock_supabase:
            mock_table = MagicMock()
            mock_supabase.table.return_value = mock_table
            mock_table.select.return_value = mock_table
            mock_table.eq.return_value = mock_table
            mock_table.lt.return_value = mock_table
            mock_table.is_.return_value = mock_table
            mock_table.execute.return_value = MagicMock(data=[])
            
            cases = await escalation_service.check_unreviewed_urgent_cases()
            
            # Should filter out cases with consultation_notes
            assert len(cases) == 0
    
    @pytest.mark.asyncio
    async def test_get_admin_emails_returns_admin_list(self, escalation_service):
        """Test that get_admin_emails returns list of admin emails"""
        mock_admins = [
            {"email": "admin1@skinguard.com"},
            {"email": "admin2@skinguard.com"}
        ]
        
        with patch('app.scheduler.supabase') as mock_supabase:
            mock_table = MagicMock()
            mock_supabase.table.return_value = mock_table
            mock_table.select.return_value = mock_table
            mock_table.eq.return_value = mock_table
            mock_table.execute.return_value = MagicMock(data=mock_admins)
            
            emails = await escalation_service.get_admin_emails()
            
            assert len(emails) == 2
            assert "admin1@skinguard.com" in emails
            assert "admin2@skinguard.com" in emails
    
    @pytest.mark.asyncio
    async def test_send_admin_escalation_notification_includes_case_details(
        self, escalation_service, mock_urgent_case
    ):
        """Test that admin notification includes all case details"""
        with patch.object(escalation_service.email_service, 'send_email', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True
            
            success = await escalation_service.send_admin_escalation_notification(
                admin_email="admin@skinguard.com",
                case=mock_urgent_case
            )
            
            assert success is True
            assert mock_send.called
            
            # Check email content
            call_args = mock_send.call_args
            assert call_args[1]["to_email"] == "admin@skinguard.com"
            assert "ESCALATION" in call_args[1]["subject"]
            assert "report-123" in call_args[1]["html_body"]
            assert "John Doe" in call_args[1]["html_body"]
            assert "Melanoma" in call_args[1]["html_body"]
            assert "92" in call_args[1]["html_body"]  # 92% probability
    
    @pytest.mark.asyncio
    async def test_send_admin_escalation_notification_calculates_time_elapsed(
        self, escalation_service, mock_urgent_case
    ):
        """Test that notification includes correct time elapsed"""
        with patch.object(escalation_service.email_service, 'send_email', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True
            
            await escalation_service.send_admin_escalation_notification(
                admin_email="admin@skinguard.com",
                case=mock_urgent_case
            )
            
            # Check that time elapsed is mentioned (should be ~25 hours)
            call_args = mock_send.call_args
            html_body = call_args[1]["html_body"]
            
            # Should mention hours elapsed
            assert "hours" in html_body.lower()
            # Should be around 25 hours (created 25 hours ago)
            assert "25" in html_body or "24" in html_body
    
    @pytest.mark.asyncio
    async def test_track_escalation_creates_audit_log(self, escalation_service):
        """Test that escalation tracking creates audit log entry"""
        with patch('app.scheduler.supabase') as mock_supabase:
            mock_table = MagicMock()
            mock_supabase.table.return_value = mock_table
            mock_table.insert.return_value = mock_table
            mock_table.execute.return_value = MagicMock(data=[{"id": "audit-123"}])
            
            success = await escalation_service.track_escalation("report-123")
            
            assert success is True
            assert mock_table.insert.called
            
            # Check audit log entry
            insert_call = mock_table.insert.call_args[0][0]
            assert insert_call["action"] == "urgent_case_escalation"
            assert insert_call["resource_type"] == "medical_report"
            assert insert_call["resource_id"] == "report-123"
    
    @pytest.mark.asyncio
    async def test_has_been_escalated_returns_true_for_escalated_case(self, escalation_service):
        """Test that has_been_escalated returns True for already escalated cases"""
        with patch('app.scheduler.supabase') as mock_supabase:
            mock_table = MagicMock()
            mock_supabase.table.return_value = mock_table
            mock_table.select.return_value = mock_table
            mock_table.eq.return_value = mock_table
            mock_table.execute.return_value = MagicMock(data=[{"id": "audit-123"}])
            
            result = await escalation_service.has_been_escalated("report-123")
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_has_been_escalated_returns_false_for_new_case(self, escalation_service):
        """Test that has_been_escalated returns False for new cases"""
        with patch('app.scheduler.supabase') as mock_supabase:
            mock_table = MagicMock()
            mock_supabase.table.return_value = mock_table
            mock_table.select.return_value = mock_table
            mock_table.eq.return_value = mock_table
            mock_table.execute.return_value = MagicMock(data=[])
            
            result = await escalation_service.has_been_escalated("report-123")
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_process_escalations_sends_notifications_to_all_admins(
        self, escalation_service, mock_urgent_case, mock_admin_emails
    ):
        """Test that process_escalations sends notifications to all admins"""
        with patch('app.scheduler.supabase') as mock_supabase:
            # Mock check_unreviewed_urgent_cases
            mock_table = MagicMock()
            mock_supabase.table.return_value = mock_table
            mock_table.select.return_value = mock_table
            mock_table.eq.return_value = mock_table
            mock_table.lt.return_value = mock_table
            mock_table.is_.return_value = mock_table
            mock_table.insert.return_value = mock_table
            
            # First call: get unreviewed cases
            # Second call: get admin emails
            # Third call: check if escalated
            # Fourth call: track escalation
            mock_table.execute.side_effect = [
                MagicMock(data=[mock_urgent_case]),  # unreviewed cases
                MagicMock(data=[{"email": e} for e in mock_admin_emails]),  # admin emails
                MagicMock(data=[]),  # has_been_escalated check
                MagicMock(data=[{"id": "audit-123"}])  # track escalation
            ]
            
            with patch.object(escalation_service.email_service, 'send_email', new_callable=AsyncMock) as mock_send:
                mock_send.return_value = True
                
                stats = await escalation_service.process_escalations()
                
                assert stats["cases_checked"] == 1
                assert stats["cases_escalated"] == 1
                assert stats["notifications_sent"] == 2  # 2 admins
                assert mock_send.call_count == 2
    
    @pytest.mark.asyncio
    async def test_process_escalations_skips_already_escalated_cases(
        self, escalation_service, mock_urgent_case, mock_admin_emails
    ):
        """Test that process_escalations skips cases that were already escalated"""
        with patch('app.scheduler.supabase') as mock_supabase:
            mock_table = MagicMock()
            mock_supabase.table.return_value = mock_table
            mock_table.select.return_value = mock_table
            mock_table.eq.return_value = mock_table
            mock_table.lt.return_value = mock_table
            mock_table.is_.return_value = mock_table
            
            # First call: get unreviewed cases
            # Second call: get admin emails
            # Third call: check if escalated (returns True - already escalated)
            mock_table.execute.side_effect = [
                MagicMock(data=[mock_urgent_case]),  # unreviewed cases
                MagicMock(data=[{"email": e} for e in mock_admin_emails]),  # admin emails
                MagicMock(data=[{"id": "audit-123"}])  # has_been_escalated returns True
            ]
            
            with patch.object(escalation_service.email_service, 'send_email', new_callable=AsyncMock) as mock_send:
                stats = await escalation_service.process_escalations()
                
                assert stats["cases_checked"] == 1
                assert stats["cases_escalated"] == 0  # Should skip
                assert stats["notifications_sent"] == 0
                assert mock_send.call_count == 0  # No emails sent
    
    @pytest.mark.asyncio
    async def test_process_escalations_handles_no_admins_gracefully(
        self, escalation_service, mock_urgent_case
    ):
        """Test that process_escalations handles missing admins gracefully"""
        with patch('app.scheduler.supabase') as mock_supabase:
            mock_table = MagicMock()
            mock_supabase.table.return_value = mock_table
            mock_table.select.return_value = mock_table
            mock_table.eq.return_value = mock_table
            mock_table.lt.return_value = mock_table
            mock_table.is_.return_value = mock_table
            
            # First call: get unreviewed cases
            # Second call: get admin emails (empty)
            mock_table.execute.side_effect = [
                MagicMock(data=[mock_urgent_case]),  # unreviewed cases
                MagicMock(data=[])  # no admin emails
            ]
            
            stats = await escalation_service.process_escalations()
            
            assert stats["cases_checked"] == 1
            assert stats["cases_escalated"] == 0
            assert stats["notifications_sent"] == 0
    
    @pytest.mark.asyncio
    async def test_process_escalations_handles_no_urgent_cases(self, escalation_service):
        """Test that process_escalations handles no urgent cases gracefully"""
        with patch('app.scheduler.supabase') as mock_supabase:
            mock_table = MagicMock()
            mock_supabase.table.return_value = mock_table
            mock_table.select.return_value = mock_table
            mock_table.eq.return_value = mock_table
            mock_table.lt.return_value = mock_table
            mock_table.is_.return_value = mock_table
            mock_table.execute.return_value = MagicMock(data=[])
            
            stats = await escalation_service.process_escalations()
            
            assert stats["cases_checked"] == 0
            assert stats["cases_escalated"] == 0
            assert stats["notifications_sent"] == 0


class TestEscalationEmailContent:
    """Test escalation email content and formatting"""
    
    @pytest.mark.asyncio
    async def test_email_includes_report_url(self, escalation_service, mock_urgent_case):
        """Test that email includes link to report"""
        with patch.object(escalation_service.email_service, 'send_email', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True
            
            await escalation_service.send_admin_escalation_notification(
                admin_email="admin@skinguard.com",
                case=mock_urgent_case
            )
            
            call_args = mock_send.call_args
            html_body = call_args[1]["html_body"]
            
            assert "https://skinguard.com/admin/reports/report-123" in html_body
    
    @pytest.mark.asyncio
    async def test_email_includes_patient_information(self, escalation_service, mock_urgent_case):
        """Test that email includes patient name and email"""
        with patch.object(escalation_service.email_service, 'send_email', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True
            
            await escalation_service.send_admin_escalation_notification(
                admin_email="admin@skinguard.com",
                case=mock_urgent_case
            )
            
            call_args = mock_send.call_args
            html_body = call_args[1]["html_body"]
            text_body = call_args[1]["text_body"]
            
            assert "John Doe" in html_body
            assert "john.doe@example.com" in html_body
            assert "John Doe" in text_body
            assert "john.doe@example.com" in text_body
    
    @pytest.mark.asyncio
    async def test_email_includes_ai_prediction(self, escalation_service, mock_urgent_case):
        """Test that email includes top AI prediction"""
        with patch.object(escalation_service.email_service, 'send_email', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True
            
            await escalation_service.send_admin_escalation_notification(
                admin_email="admin@skinguard.com",
                case=mock_urgent_case
            )
            
            call_args = mock_send.call_args
            html_body = call_args[1]["html_body"]
            
            assert "Melanoma" in html_body
            assert "92" in html_body  # 92% probability
    
    @pytest.mark.asyncio
    async def test_email_includes_recommended_actions(self, escalation_service, mock_urgent_case):
        """Test that email includes recommended actions for admin"""
        with patch.object(escalation_service.email_service, 'send_email', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True
            
            await escalation_service.send_admin_escalation_notification(
                admin_email="admin@skinguard.com",
                case=mock_urgent_case
            )
            
            call_args = mock_send.call_args
            html_body = call_args[1]["html_body"]
            
            assert "Recommended Actions" in html_body or "recommended action" in html_body.lower()
            assert "contact" in html_body.lower()
            assert "review" in html_body.lower()
