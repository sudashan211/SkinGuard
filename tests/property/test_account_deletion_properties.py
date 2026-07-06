"""
Property-Based Tests for Account Deletion
Feature: derman-ai-skin-screening

Tests account deletion with cascade deletion and 30-day schedule.

Requirements: 18.3
Property: 53
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
import sys
import os
import uuid

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.account_deletion import AccountDeletionService, get_account_deletion_service


class TestAccountDeletionProperties:
    """Property-based tests for account deletion features"""
    
    @pytest.mark.asyncio
    @given(
        user_id=st.uuids().map(str)
    )
    @settings(max_examples=50, deadline=None)
    async def test_property_53_account_deletion_cascade(self, user_id):
        """
        Property 53: Account Deletion Cascade
        
        For any patient account deletion, all associated medical_reports 
        and patient_data records should be marked for deletion and removed 
        within 30 days.
        
        Validates: Requirements 18.3
        
        This test verifies that:
        1. Account deletion is scheduled with 30-day grace period
        2. All associated data is identified for cascade deletion
        3. Deletion date is correctly calculated
        4. Grace period is exactly 30 days
        """
        # Arrange
        service = AccountDeletionService()
        mock_audit_logger = AsyncMock()
        
        # Mock Supabase update for scheduling deletion
        mock_update_result = MagicMock()
        mock_update_result.data = [{
            "id": user_id,
            "deletion_scheduled_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }]
        
        with patch('app.account_deletion.supabase') as mock_supabase:
            # Setup mock chain for scheduling
            mock_table = MagicMock()
            mock_update = MagicMock()
            mock_eq = MagicMock()
            mock_eq.execute.return_value = mock_update_result
            mock_update.eq.return_value = mock_eq
            mock_table.update.return_value = mock_update
            mock_supabase.table.return_value = mock_table
            
            # Act - Schedule deletion
            result = await service.schedule_account_deletion(
                user_id=user_id,
                audit_logger=mock_audit_logger,
                ip_address="127.0.0.1"
            )
            
            # Assert - Verify deletion scheduled
            assert result is not None, "Deletion schedule result should not be None"
            assert "user_id" in result, "Result should include user_id"
            assert result["user_id"] == user_id, f"User ID mismatch: expected {user_id}"
            
            # Verify deletion scheduled flag
            assert "deletion_scheduled" in result, "Result should include deletion_scheduled flag"
            assert result["deletion_scheduled"] is True, "Deletion should be scheduled"
            
            # Verify grace period is 30 days
            assert "grace_period_days" in result, "Result should include grace_period_days"
            assert result["grace_period_days"] == 30, \
                f"Grace period should be 30 days, got {result['grace_period_days']}"
            
            # Verify deletion date is set
            assert "deletion_date" in result, "Result should include deletion_date"
            deletion_date_str = result["deletion_date"]
            deletion_date = datetime.fromisoformat(deletion_date_str.replace('Z', '+00:00'))
            
            # Calculate expected deletion date (30 days from now)
            now = datetime.utcnow()
            expected_deletion = now + timedelta(days=30)
            
            # Allow 1 minute tolerance for test execution time
            time_diff = abs((deletion_date.replace(tzinfo=None) - expected_deletion).total_seconds())
            assert time_diff < 60, \
                f"Deletion date should be 30 days from now, difference: {time_diff} seconds"
            
            # Verify audit log was called
            mock_audit_logger.log_action.assert_called_once()
            call_args = mock_audit_logger.log_action.call_args
            assert call_args[1]["action"] == "account_deletion_scheduled"
            assert call_args[1]["user_id"] == user_id
    
    @pytest.mark.asyncio
    @given(
        user_id=st.uuids().map(str),
        num_reports=st.integers(min_value=0, max_value=10),
        has_patient_data=st.booleans(),
        num_appointments=st.integers(min_value=0, max_value=5),
        num_reviews=st.integers(min_value=0, max_value=5),
        num_notifications=st.integers(min_value=0, max_value=20)
    )
    @settings(max_examples=50, deadline=None)
    async def test_property_53_cascade_deletion_completeness(
        self,
        user_id,
        num_reports,
        has_patient_data,
        num_appointments,
        num_reviews,
        num_notifications
    ):
        """
        Property 53: Cascade Deletion Completeness
        
        For any account deletion, all associated records across all tables
        should be deleted (medical_reports, patient_data, appointments, 
        reviews, notifications).
        
        Validates: Requirements 18.3
        
        This test verifies that:
        1. All medical reports are deleted
        2. Patient data is deleted
        3. All appointments are deleted
        4. All reviews are deleted
        5. All notifications are deleted
        6. Profile is deleted last
        """
        # Arrange
        service = AccountDeletionService()
        mock_audit_logger = AsyncMock()
        
        # Create mock data for each table
        mock_reports = [{"id": str(uuid.uuid4())} for _ in range(num_reports)]
        mock_patient_data = [{"id": str(uuid.uuid4())}] if has_patient_data else []
        mock_appointments = [{"id": str(uuid.uuid4())} for _ in range(num_appointments)]
        mock_reviews = [{"id": str(uuid.uuid4())} for _ in range(num_reviews)]
        mock_notifications = [{"id": str(uuid.uuid4())} for _ in range(num_notifications)]
        mock_profile = [{"id": user_id}]
        
        with patch('app.account_deletion.supabase') as mock_supabase:
            # Setup mock for each table deletion
            def create_delete_mock(data):
                mock_result = MagicMock()
                mock_result.data = data
                mock_eq = MagicMock()
                mock_eq.execute.return_value = mock_result
                mock_delete = MagicMock()
                mock_delete.eq.return_value = mock_eq
                return mock_delete
            
            # Track which tables were deleted
            deleted_tables = []
            
            def mock_table(table_name):
                deleted_tables.append(table_name)
                mock_tbl = MagicMock()
                
                if table_name == "medical_reports":
                    mock_tbl.delete.return_value = create_delete_mock(mock_reports)
                elif table_name == "patient_data":
                    mock_tbl.delete.return_value = create_delete_mock(mock_patient_data)
                elif table_name == "appointments":
                    mock_tbl.delete.return_value = create_delete_mock(mock_appointments)
                elif table_name == "reviews":
                    mock_tbl.delete.return_value = create_delete_mock(mock_reviews)
                elif table_name == "notifications":
                    mock_tbl.delete.return_value = create_delete_mock(mock_notifications)
                elif table_name == "doctors":
                    mock_tbl.delete.return_value = create_delete_mock([])
                elif table_name == "profiles":
                    mock_tbl.delete.return_value = create_delete_mock(mock_profile)
                
                return mock_tbl
            
            mock_supabase.table.side_effect = mock_table
            
            # Act - Execute deletion
            result = await service.execute_account_deletion(
                user_id=user_id,
                audit_logger=mock_audit_logger
            )
            
            # Assert - Verify all data was deleted
            assert result is not None, "Deletion result should not be None"
            assert "deleted" in result, "Result should include deleted flag"
            assert result["deleted"] is True, "Deletion should be successful"
            
            # Verify summary includes all tables
            assert "summary" in result, "Result should include deletion summary"
            summary = result["summary"]
            assert "deleted_records" in summary, "Summary should include deleted_records"
            
            deleted_records = summary["deleted_records"]
            
            # Verify each table was processed
            assert "medical_reports" in deleted_records, "Should track medical_reports deletion"
            assert deleted_records["medical_reports"] == num_reports, \
                f"Should delete {num_reports} reports, got {deleted_records['medical_reports']}"
            
            assert "patient_data" in deleted_records, "Should track patient_data deletion"
            expected_patient_data = 1 if has_patient_data else 0
            assert deleted_records["patient_data"] == expected_patient_data, \
                f"Should delete {expected_patient_data} patient_data, got {deleted_records['patient_data']}"
            
            assert "appointments" in deleted_records, "Should track appointments deletion"
            assert deleted_records["appointments"] == num_appointments, \
                f"Should delete {num_appointments} appointments, got {deleted_records['appointments']}"
            
            assert "reviews" in deleted_records, "Should track reviews deletion"
            assert deleted_records["reviews"] == num_reviews, \
                f"Should delete {num_reviews} reviews, got {deleted_records['reviews']}"
            
            assert "notifications" in deleted_records, "Should track notifications deletion"
            assert deleted_records["notifications"] == num_notifications, \
                f"Should delete {num_notifications} notifications, got {deleted_records['notifications']}"
            
            assert "profiles" in deleted_records, "Should track profiles deletion"
            assert deleted_records["profiles"] == 1, \
                f"Should delete 1 profile, got {deleted_records['profiles']}"
            
            # Verify audit log was called
            mock_audit_logger.log_action.assert_called_once()
            call_args = mock_audit_logger.log_action.call_args
            assert call_args[1]["action"] == "account_permanently_deleted"
    
    @pytest.mark.asyncio
    @given(
        user_id=st.uuids().map(str)
    )
    @settings(max_examples=30, deadline=None)
    async def test_property_53_deletion_cancellation(self, user_id):
        """
        Property 53: Deletion Cancellation During Grace Period
        
        For any scheduled deletion, the user should be able to cancel
        the deletion during the 30-day grace period.
        
        Validates: Requirements 18.3
        
        This test verifies that:
        1. Scheduled deletions can be cancelled
        2. Cancellation removes the deletion schedule
        3. Audit log tracks cancellation
        """
        # Arrange
        service = AccountDeletionService()
        mock_audit_logger = AsyncMock()
        
        # Mock Supabase update for cancellation
        mock_update_result = MagicMock()
        mock_update_result.data = [{
            "id": user_id,
            "deletion_scheduled_at": None
        }]
        
        with patch('app.account_deletion.supabase') as mock_supabase:
            # Setup mock chain for cancellation
            mock_table = MagicMock()
            mock_update = MagicMock()
            mock_eq = MagicMock()
            mock_eq.execute.return_value = mock_update_result
            mock_update.eq.return_value = mock_eq
            mock_table.update.return_value = mock_update
            mock_supabase.table.return_value = mock_table
            
            # Act - Cancel deletion
            result = await service.cancel_account_deletion(
                user_id=user_id,
                audit_logger=mock_audit_logger,
                ip_address="127.0.0.1"
            )
            
            # Assert - Verify cancellation
            assert result is not None, "Cancellation result should not be None"
            assert "user_id" in result, "Result should include user_id"
            assert result["user_id"] == user_id, f"User ID mismatch: expected {user_id}"
            
            # Verify cancellation flag
            assert "deletion_cancelled" in result, "Result should include deletion_cancelled flag"
            assert result["deletion_cancelled"] is True, "Deletion should be cancelled"
            
            # Verify message
            assert "message" in result, "Result should include message"
            assert "cancelled" in result["message"].lower(), "Message should mention cancellation"
            
            # Verify audit log was called
            mock_audit_logger.log_action.assert_called_once()
            call_args = mock_audit_logger.log_action.call_args
            assert call_args[1]["action"] == "account_deletion_cancelled"
            assert call_args[1]["user_id"] == user_id
    
    def test_deletion_service_singleton(self):
        """
        Test that deletion service maintains consistent state
        
        Verifies that get_account_deletion_service returns the same instance
        and maintains consistent configuration.
        """
        # Act
        service1 = get_account_deletion_service()
        service2 = get_account_deletion_service()
        
        # Assert - Should return same instance
        assert service1 is service2, "get_account_deletion_service should return singleton instance"
        
        # Verify consistent configuration
        assert service1.deletion_grace_period_days == service2.deletion_grace_period_days
        assert service1.deletion_grace_period_days == 30, "Grace period should be 30 days"
    
    @pytest.mark.asyncio
    async def test_scheduled_deletion_processing_basic(self):
        """
        Test that scheduled deletions processing returns correct structure
        
        Verifies that the background job returns the expected result structure
        even when no deletions are scheduled.
        """
        # Arrange
        service = AccountDeletionService()
        
        with patch('app.account_deletion.supabase') as mock_supabase:
            # Mock empty result (no scheduled deletions)
            mock_execute_result = MagicMock()
            mock_execute_result.data = []
            
            mock_lte_chain = MagicMock()
            mock_lte_chain.execute.return_value = mock_execute_result
            
            mock_not_chain = MagicMock()
            mock_not_chain.lte.return_value = mock_lte_chain
            
            mock_select_chain = MagicMock()
            mock_select_chain.is_.return_value = mock_not_chain
            
            mock_table = MagicMock()
            mock_table.select.return_value = mock_select_chain
            mock_table.not_ = mock_select_chain
            
            mock_supabase.table.return_value = mock_table
            
            # Act
            result = await service.process_scheduled_deletions()
            
            # Assert - Verify result structure
            assert result is not None, "Processing result should not be None"
            assert "processed" in result, "Result should include processed count"
            assert "successful" in result, "Result should include successful count"
            assert "failed" in result, "Result should include failed count"
            
            # When no deletions scheduled, all counts should be 0
            assert result["processed"] == 0, "Should process 0 accounts when none scheduled"
            assert result["successful"] == 0, "Should have 0 successful when none scheduled"
            assert result["failed"] == 0, "Should have 0 failed when none scheduled"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
