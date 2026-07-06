"""
Unit tests for Audit Logging
Requirements: 3.6, 18.4
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, MagicMock
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))
from app.audit import AuditLogger


@pytest.fixture
def mock_supabase():
    """Create mock Supabase client"""
    mock_client = Mock()
    mock_table = Mock()
    mock_client.table.return_value = mock_table
    return mock_client


@pytest.fixture
def audit_logger(mock_supabase):
    """Create AuditLogger instance with mock Supabase"""
    return AuditLogger(mock_supabase)


class TestAuditLogger:
    """Test suite for AuditLogger"""
    
    @pytest.mark.asyncio
    async def test_log_content_violation(self, audit_logger, mock_supabase):
        """Test logging content violation"""
        # Setup mock response
        mock_result = Mock()
        mock_result.data = [{"id": "test-audit-id"}]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_result
        
        # Log content violation
        audit_id = await audit_logger.log_content_violation(
            user_id="user-123",
            nsfw_score=0.45,
            non_skin_score=0.2,
            rejection_reason="NSFW score exceeds threshold",
            ip_address="192.168.1.1"
        )
        
        # Verify audit log was created
        assert audit_id == "test-audit-id"
        
        # Verify Supabase was called correctly
        mock_supabase.table.assert_called_with("audit_logs")
        insert_call = mock_supabase.table.return_value.insert.call_args
        
        # Check the data that was inserted
        inserted_data = insert_call[0][0]
        assert inserted_data["user_id"] == "user-123"
        assert inserted_data["action"] == "content_violation"
        assert inserted_data["resource_type"] == "image_upload"
        assert inserted_data["metadata"]["nsfw_score"] == 0.45
        assert inserted_data["metadata"]["non_skin_score"] == 0.2
        assert inserted_data["metadata"]["rejection_reason"] == "NSFW score exceeds threshold"
        assert inserted_data["ip_address"] == "192.168.1.1"
    
    @pytest.mark.asyncio
    async def test_log_data_access(self, audit_logger, mock_supabase):
        """Test logging data access event"""
        # Setup mock response
        mock_result = Mock()
        mock_result.data = [{"id": "test-audit-id-2"}]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_result
        
        # Log data access
        audit_id = await audit_logger.log_data_access(
            user_id="user-456",
            resource_type="medical_report",
            resource_id="report-789",
            action="read",
            ip_address="192.168.1.2"
        )
        
        # Verify audit log was created
        assert audit_id == "test-audit-id-2"
        
        # Verify correct action was logged
        insert_call = mock_supabase.table.return_value.insert.call_args
        inserted_data = insert_call[0][0]
        assert inserted_data["action"] == "data_access_read"
        assert inserted_data["resource_type"] == "medical_report"
        assert inserted_data["resource_id"] == "report-789"
    
    @pytest.mark.asyncio
    async def test_log_authentication_event(self, audit_logger, mock_supabase):
        """Test logging authentication event"""
        # Setup mock response
        mock_result = Mock()
        mock_result.data = [{"id": "test-audit-id-3"}]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_result
        
        # Log authentication event
        audit_id = await audit_logger.log_authentication_event(
            user_id="user-789",
            event_type="login",
            success=True,
            ip_address="192.168.1.3"
        )
        
        # Verify audit log was created
        assert audit_id == "test-audit-id-3"
        
        # Verify correct action was logged
        insert_call = mock_supabase.table.return_value.insert.call_args
        inserted_data = insert_call[0][0]
        assert inserted_data["action"] == "auth_login"
        assert inserted_data["metadata"]["success"] is True
    
    @pytest.mark.asyncio
    async def test_log_admin_action(self, audit_logger, mock_supabase):
        """Test logging admin action"""
        # Setup mock response
        mock_result = Mock()
        mock_result.data = [{"id": "test-audit-id-4"}]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_result
        
        # Log admin action
        audit_id = await audit_logger.log_admin_action(
            admin_user_id="admin-123",
            action="verify_doctor",
            resource_type="doctor",
            resource_id="doctor-456",
            ip_address="192.168.1.4"
        )
        
        # Verify audit log was created
        assert audit_id == "test-audit-id-4"
        
        # Verify correct action was logged
        insert_call = mock_supabase.table.return_value.insert.call_args
        inserted_data = insert_call[0][0]
        assert inserted_data["action"] == "admin_verify_doctor"
        assert inserted_data["resource_type"] == "doctor"
    
    @pytest.mark.asyncio
    async def test_log_content_violation_with_additional_metadata(self, audit_logger, mock_supabase):
        """Test logging content violation with additional metadata"""
        # Setup mock response
        mock_result = Mock()
        mock_result.data = [{"id": "test-audit-id-5"}]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_result
        
        # Log with additional metadata
        audit_id = await audit_logger.log_content_violation(
            user_id="user-999",
            nsfw_score=0.85,
            non_skin_score=0.15,
            rejection_reason="High NSFW score",
            ip_address="192.168.1.5",
            additional_metadata={
                "image_size": 1024000,
                "image_format": "JPEG"
            }
        )
        
        # Verify metadata was merged
        insert_call = mock_supabase.table.return_value.insert.call_args
        inserted_data = insert_call[0][0]
        assert inserted_data["metadata"]["image_size"] == 1024000
        assert inserted_data["metadata"]["image_format"] == "JPEG"
        assert inserted_data["metadata"]["nsfw_score"] == 0.85
    
    @pytest.mark.asyncio
    async def test_log_content_violation_without_user_id(self, audit_logger, mock_supabase):
        """Test logging content violation for unauthenticated user"""
        # Setup mock response
        mock_result = Mock()
        mock_result.data = [{"id": "test-audit-id-6"}]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_result
        
        # Log without user_id (unauthenticated)
        audit_id = await audit_logger.log_content_violation(
            user_id=None,
            nsfw_score=0.5,
            non_skin_score=0.3,
            rejection_reason="Content violation",
            ip_address="192.168.1.6"
        )
        
        # Verify audit log was created with None user_id
        insert_call = mock_supabase.table.return_value.insert.call_args
        inserted_data = insert_call[0][0]
        assert inserted_data["user_id"] is None
        assert audit_id == "test-audit-id-6"
    
    @pytest.mark.asyncio
    async def test_audit_log_failure_handling(self, audit_logger, mock_supabase):
        """Test that audit log failures don't crash the application"""
        # Setup mock to raise exception
        mock_supabase.table.return_value.insert.side_effect = Exception("Database error")
        
        # Should not raise exception, but return a UUID
        audit_id = await audit_logger.log_content_violation(
            user_id="user-error",
            nsfw_score=0.4,
            non_skin_score=0.2,
            rejection_reason="Test error handling"
        )
        
        # Should return a UUID even on failure
        assert audit_id is not None
        assert len(audit_id) > 0
    
    @pytest.mark.asyncio
    async def test_get_audit_logs(self, audit_logger, mock_supabase):
        """Test retrieving audit logs"""
        # Setup mock response
        mock_result = Mock()
        mock_result.data = [
            {"id": "log-1", "action": "content_violation"},
            {"id": "log-2", "action": "content_violation"}
        ]
        
        # Setup mock query chain
        mock_query = Mock()
        mock_query.eq.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.execute.return_value = mock_result
        
        mock_supabase.table.return_value.select.return_value = mock_query
        
        # Get audit logs
        logs = await audit_logger.get_audit_logs(
            action="content_violation",
            limit=10
        )
        
        # Verify logs were retrieved
        assert len(logs) == 2
        assert logs[0]["id"] == "log-1"
        assert logs[1]["id"] == "log-2"
    
    @pytest.mark.asyncio
    async def test_get_content_violations(self, audit_logger, mock_supabase):
        """Test retrieving content violation logs"""
        # Setup mock response
        mock_result = Mock()
        mock_result.data = [
            {"id": "violation-1", "action": "content_violation"}
        ]
        
        # Setup mock query chain
        mock_query = Mock()
        mock_query.eq.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.execute.return_value = mock_result
        
        mock_supabase.table.return_value.select.return_value = mock_query
        
        # Get content violations
        violations = await audit_logger.get_content_violations(limit=50)
        
        # Verify violations were retrieved
        assert len(violations) == 1
        assert violations[0]["id"] == "violation-1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
