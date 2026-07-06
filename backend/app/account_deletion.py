"""
Account Deletion Service
Requirements: 18.3

Handles account deletion with cascade deletion and 30-day schedule.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.database import supabase
from app.audit import AuditLogger

logger = logging.getLogger(__name__)


class AccountDeletionService:
    """
    Service for managing account deletion
    
    Implements:
    - Cascade deletion of all user data
    - 30-day deletion schedule
    - Audit logging of deletion requests
    """
    
    def __init__(self):
        """Initialize account deletion service"""
        self.deletion_grace_period_days = 30
        logger.info("Account deletion service initialized")
    
    async def schedule_account_deletion(
        self,
        user_id: str,
        audit_logger: Optional[AuditLogger] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Schedule account for deletion
        
        Marks the account for deletion and schedules permanent deletion
        after 30 days. During the grace period, the user can cancel
        the deletion request.
        
        Args:
            user_id: User ID to delete
            audit_logger: Optional audit logger
            ip_address: Optional IP address for audit log
            
        Returns:
            Dict with deletion schedule information
            
        Raises:
            ValueError: If user not found or deletion fails
        """
        try:
            # Calculate deletion date (30 days from now)
            deletion_date = datetime.utcnow() + timedelta(days=self.deletion_grace_period_days)
            
            # Mark account for deletion
            # Add deletion_scheduled_at field to profiles table
            update_result = supabase.table("profiles").update({
                "deletion_scheduled_at": deletion_date.isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
            
            if not update_result.data:
                raise ValueError(f"User {user_id} not found")
            
            # Log deletion request
            if audit_logger:
                await audit_logger.log_action(
                    user_id=user_id,
                    action="account_deletion_scheduled",
                    resource_type="profile",
                    resource_id=user_id,
                    metadata={
                        "deletion_date": deletion_date.isoformat(),
                        "grace_period_days": self.deletion_grace_period_days
                    },
                    ip_address=ip_address
                )
            
            logger.info(f"Account deletion scheduled for user {user_id}, deletion date: {deletion_date}")
            
            return {
                "user_id": user_id,
                "deletion_scheduled": True,
                "deletion_date": deletion_date.isoformat(),
                "grace_period_days": self.deletion_grace_period_days,
                "message": f"Account deletion scheduled for {deletion_date.strftime('%Y-%m-%d')}. "
                          f"You have {self.deletion_grace_period_days} days to cancel this request."
            }
            
        except Exception as e:
            logger.error(f"Error scheduling account deletion for user {user_id}: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to schedule account deletion: {str(e)}")
    
    async def cancel_account_deletion(
        self,
        user_id: str,
        audit_logger: Optional[AuditLogger] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Cancel scheduled account deletion
        
        Cancels a pending account deletion request during the grace period.
        
        Args:
            user_id: User ID
            audit_logger: Optional audit logger
            ip_address: Optional IP address for audit log
            
        Returns:
            Dict with cancellation confirmation
            
        Raises:
            ValueError: If user not found or no deletion scheduled
        """
        try:
            # Remove deletion schedule
            update_result = supabase.table("profiles").update({
                "deletion_scheduled_at": None,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
            
            if not update_result.data:
                raise ValueError(f"User {user_id} not found")
            
            # Log cancellation
            if audit_logger:
                await audit_logger.log_action(
                    user_id=user_id,
                    action="account_deletion_cancelled",
                    resource_type="profile",
                    resource_id=user_id,
                    metadata={},
                    ip_address=ip_address
                )
            
            logger.info(f"Account deletion cancelled for user {user_id}")
            
            return {
                "user_id": user_id,
                "deletion_cancelled": True,
                "message": "Account deletion has been cancelled. Your account will remain active."
            }
            
        except Exception as e:
            logger.error(f"Error cancelling account deletion for user {user_id}: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to cancel account deletion: {str(e)}")
    
    async def execute_account_deletion(
        self,
        user_id: str,
        audit_logger: Optional[AuditLogger] = None
    ) -> Dict[str, Any]:
        """
        Execute permanent account deletion
        
        Permanently deletes the account and all associated data:
        - Medical reports (cascade)
        - Patient data (cascade)
        - Appointments (cascade)
        - Reviews (cascade)
        - Notifications (cascade)
        - Profile record
        
        This should only be called after the grace period has expired.
        
        Args:
            user_id: User ID to delete
            audit_logger: Optional audit logger
            
        Returns:
            Dict with deletion confirmation
            
        Raises:
            ValueError: If deletion fails
        """
        try:
            deletion_summary = {
                "user_id": user_id,
                "deleted_at": datetime.utcnow().isoformat(),
                "deleted_records": {}
            }
            
            # Delete medical reports (images will be deleted separately)
            reports_result = supabase.table("medical_reports").delete().eq("patient_id", user_id).execute()
            deletion_summary["deleted_records"]["medical_reports"] = len(reports_result.data) if reports_result.data else 0
            
            # Delete patient data
            patient_data_result = supabase.table("patient_data").delete().eq("user_id", user_id).execute()
            deletion_summary["deleted_records"]["patient_data"] = len(patient_data_result.data) if patient_data_result.data else 0
            
            # Delete appointments (as patient)
            appointments_result = supabase.table("appointments").delete().eq("patient_id", user_id).execute()
            deletion_summary["deleted_records"]["appointments"] = len(appointments_result.data) if appointments_result.data else 0
            
            # Delete reviews (as patient)
            reviews_result = supabase.table("reviews").delete().eq("patient_id", user_id).execute()
            deletion_summary["deleted_records"]["reviews"] = len(reviews_result.data) if reviews_result.data else 0
            
            # Delete notifications
            notifications_result = supabase.table("notifications").delete().eq("user_id", user_id).execute()
            deletion_summary["deleted_records"]["notifications"] = len(notifications_result.data) if notifications_result.data else 0
            
            # Delete audit logs (optional - you may want to keep these for compliance)
            # audit_logs_result = supabase.table("audit_logs").delete().eq("user_id", user_id).execute()
            # deletion_summary["deleted_records"]["audit_logs"] = len(audit_logs_result.data) if audit_logs_result.data else 0
            
            # Delete doctor record if exists
            doctor_result = supabase.table("doctors").delete().eq("user_id", user_id).execute()
            deletion_summary["deleted_records"]["doctors"] = len(doctor_result.data) if doctor_result.data else 0
            
            # Finally, delete the profile
            profile_result = supabase.table("profiles").delete().eq("id", user_id).execute()
            deletion_summary["deleted_records"]["profiles"] = len(profile_result.data) if profile_result.data else 0
            
            # Log final deletion
            if audit_logger:
                await audit_logger.log_action(
                    user_id=user_id,
                    action="account_permanently_deleted",
                    resource_type="profile",
                    resource_id=user_id,
                    metadata=deletion_summary,
                    ip_address=None
                )
            
            logger.info(f"Account permanently deleted for user {user_id}: {deletion_summary}")
            
            return {
                "user_id": user_id,
                "deleted": True,
                "message": "Account and all associated data have been permanently deleted",
                "summary": deletion_summary
            }
            
        except Exception as e:
            logger.error(f"Error executing account deletion for user {user_id}: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to execute account deletion: {str(e)}")
    
    async def process_scheduled_deletions(self) -> Dict[str, Any]:
        """
        Process all scheduled deletions that have passed the grace period
        
        This should be called by a background job (e.g., daily cron job)
        to process pending deletions.
        
        Returns:
            Dict with processing summary
        """
        try:
            # Find all profiles with deletion_scheduled_at in the past
            current_time = datetime.utcnow().isoformat()
            
            profiles_result = supabase.table("profiles")\
                .select("id, email, deletion_scheduled_at")\
                .not_.is_("deletion_scheduled_at", "null")\
                .lte("deletion_scheduled_at", current_time)\
                .execute()
            
            if not profiles_result.data:
                logger.info("No scheduled deletions to process")
                return {
                    "processed": 0,
                    "successful": 0,
                    "failed": 0,
                    "message": "No scheduled deletions to process"
                }
            
            processed = 0
            successful = 0
            failed = 0
            errors = []
            
            for profile in profiles_result.data:
                processed += 1
                try:
                    await self.execute_account_deletion(profile["id"])
                    successful += 1
                    logger.info(f"Successfully deleted account {profile['id']} ({profile['email']})")
                except Exception as e:
                    failed += 1
                    error_msg = f"Failed to delete account {profile['id']}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg, exc_info=True)
            
            summary = {
                "processed": processed,
                "successful": successful,
                "failed": failed,
                "errors": errors if errors else None,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Scheduled deletion processing complete: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"Error processing scheduled deletions: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to process scheduled deletions: {str(e)}")


# Global service instance
account_deletion_service = AccountDeletionService()


def get_account_deletion_service() -> AccountDeletionService:
    """
    Get the global account deletion service instance
    
    Returns:
        AccountDeletionService instance
    """
    return account_deletion_service
