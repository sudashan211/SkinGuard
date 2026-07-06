"""
Background Job Scheduler for SkinGuard Platform
Requirements: 23.6

This module provides background job scheduling for:
- Checking unreviewed urgent cases every hour
- Sending admin escalation notifications after 24 hours
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.database import supabase
from app.email_service import get_email_service

logger = logging.getLogger(__name__)


class UrgentCaseEscalationService:
    """
    Service for checking and escalating unreviewed urgent cases
    Requirements: 23.6
    """
    
    def __init__(self):
        """Initialize escalation service"""
        self.email_service = get_email_service()
        self.escalation_threshold_hours = 24
    
    async def check_unreviewed_urgent_cases(self) -> List[Dict]:
        """
        Check for urgent cases that have been unreviewed for more than 24 hours
        Requirements: 23.6
        
        Returns:
            List[Dict]: List of unreviewed urgent cases requiring escalation
        """
        try:
            # Calculate threshold timestamp (24 hours ago)
            threshold_time = datetime.utcnow() - timedelta(hours=self.escalation_threshold_hours)
            threshold_iso = threshold_time.isoformat()
            
            logger.info(f"Checking for urgent cases unreviewed since {threshold_iso}")
            
            # Query medical_reports for urgent cases
            # Status = 'urgent' AND created_at < threshold AND consultation_notes is NULL
            result = supabase.table("medical_reports")\
                .select("*, profiles!medical_reports_patient_id_fkey(full_name, email)")\
                .eq("status", "urgent")\
                .lt("created_at", threshold_iso)\
                .is_("consultation_notes", "null")\
                .execute()
            
            if not result.data:
                logger.info("No unreviewed urgent cases found requiring escalation")
                return []
            
            unreviewed_cases = result.data
            logger.info(f"Found {len(unreviewed_cases)} unreviewed urgent cases requiring escalation")
            
            return unreviewed_cases
            
        except Exception as e:
            logger.error(f"Error checking unreviewed urgent cases: {str(e)}", exc_info=True)
            return []
    
    async def get_admin_emails(self) -> List[str]:
        """
        Get email addresses of all admin users
        
        Returns:
            List[str]: List of admin email addresses
        """
        try:
            result = supabase.table("profiles")\
                .select("email")\
                .eq("role", "admin")\
                .execute()
            
            if not result.data:
                logger.warning("No admin users found in the system")
                return []
            
            admin_emails = [admin["email"] for admin in result.data]
            logger.info(f"Found {len(admin_emails)} admin users")
            return admin_emails
            
        except Exception as e:
            logger.error(f"Error fetching admin emails: {str(e)}", exc_info=True)
            return []
    
    async def send_admin_escalation_notification(
        self,
        admin_email: str,
        case: Dict
    ) -> bool:
        """
        Send escalation notification to an admin
        Requirements: 23.6
        
        Args:
            admin_email: Admin's email address
            case: Unreviewed urgent case data
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            # Extract case details
            report_id = case.get("id")
            patient_name = case.get("profiles", {}).get("full_name", "Unknown Patient")
            patient_email = case.get("profiles", {}).get("email", "N/A")
            created_at = case.get("created_at")
            risk_level = case.get("risk_level", "urgent")
            
            # Parse created_at to calculate time elapsed
            if isinstance(created_at, str):
                created_datetime = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                created_datetime = created_at
            
            time_elapsed = datetime.utcnow() - created_datetime.replace(tzinfo=None)
            hours_elapsed = int(time_elapsed.total_seconds() / 3600)
            
            # Extract top prediction from ai_prediction
            ai_prediction = case.get("ai_prediction", {})
            predictions = ai_prediction.get("predictions", [])
            top_prediction = {"type": "Unknown", "probability": 0.0}
            
            if predictions:
                # Find prediction with highest probability
                top_pred = max(predictions, key=lambda p: p.get("probability", 0))
                top_prediction = {
                    "type": top_pred.get("type", "Unknown"),
                    "probability": top_pred.get("probability", 0.0)
                }
            
            # Generate report URL
            base_url = "https://skinguard.com"  # TODO: Get from config
            report_url = f"{base_url}/admin/reports/{report_id}"
            
            subject = f"⚠️ ESCALATION: Urgent Case Unreviewed for {hours_elapsed} Hours"
            
            # HTML email body
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #f59e0b; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
                    .content {{ background-color: #f9fafb; padding: 20px; border: 1px solid #e5e7eb; }}
                    .escalation-badge {{ background-color: #f59e0b; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold; }}
                    .info-box {{ background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #f59e0b; }}
                    .warning-box {{ background-color: #fef3c7; padding: 15px; margin: 15px 0; border-left: 4px solid #f59e0b; }}
                    .button {{ display: inline-block; background-color: #f59e0b; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 15px 0; }}
                    .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 20px; padding-top: 20px; border-top: 1px solid #e5e7eb; }}
                    .time-elapsed {{ font-size: 24px; font-weight: bold; color: #f59e0b; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>⚠️ Urgent Case Escalation</h1>
                    </div>
                    <div class="content">
                        <p>Dear Admin,</p>
                        
                        <div class="warning-box">
                            <p><strong>An urgent skin cancer case has remained unreviewed for:</strong></p>
                            <p class="time-elapsed">{hours_elapsed} hours</p>
                            <p>This case requires immediate administrative attention.</p>
                        </div>
                        
                        <div class="info-box">
                            <h3>Case Details:</h3>
                            <ul>
                                <li><strong>Report ID:</strong> {report_id}</li>
                                <li><strong>Patient:</strong> {patient_name}</li>
                                <li><strong>Patient Email:</strong> {patient_email}</li>
                                <li><strong>Risk Level:</strong> <span class="escalation-badge">{risk_level.upper()}</span></li>
                                <li><strong>AI Detection:</strong> {top_prediction['type']} ({top_prediction['probability'] * 100:.1f}% probability)</li>
                                <li><strong>Submitted:</strong> {created_datetime.strftime('%Y-%m-%d %H:%M UTC')}</li>
                                <li><strong>Time Elapsed:</strong> {hours_elapsed} hours</li>
                            </ul>
                        </div>
                        
                        <p><strong>Why this escalation occurred:</strong><br>
                        This urgent case was automatically flagged by our AI system due to high cancer probability (>85%). 
                        Despite notifications sent to the 3 nearest doctors, the case has remained unreviewed for over 24 hours.</p>
                        
                        <p><strong>Recommended Actions:</strong></p>
                        <ul>
                            <li>Review the case immediately in the admin panel</li>
                            <li>Contact the patient directly to ensure they seek medical attention</li>
                            <li>Follow up with the notified doctors to understand why the case wasn't reviewed</li>
                            <li>Consider escalating to emergency services if patient cannot be reached</li>
                        </ul>
                        
                        <a href="{report_url}" class="button">Review Case in Admin Panel →</a>
                        
                        <p style="margin-top: 20px;"><strong>System Information:</strong><br>
                        This is an automated escalation notification triggered by the SkinGuard Emergency Referral System. 
                        The system checks for unreviewed urgent cases every hour.</p>
                    </div>
                    <div class="footer">
                        <p>SkinGuard AI - Urgent Case Escalation System<br>
                        This is an automated notification. Please take immediate action.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text fallback
            text_body = f"""
            ESCALATION: Urgent Case Unreviewed for {hours_elapsed} Hours
            
            Dear Admin,
            
            An urgent skin cancer case has remained unreviewed for {hours_elapsed} hours.
            This case requires immediate administrative attention.
            
            Case Details:
            - Report ID: {report_id}
            - Patient: {patient_name}
            - Patient Email: {patient_email}
            - Risk Level: {risk_level.upper()}
            - AI Detection: {top_prediction['type']} ({top_prediction['probability'] * 100:.1f}% probability)
            - Submitted: {created_datetime.strftime('%Y-%m-%d %H:%M UTC')}
            - Time Elapsed: {hours_elapsed} hours
            
            Why this escalation occurred:
            This urgent case was automatically flagged by our AI system due to high cancer probability (>85%). 
            Despite notifications sent to the 3 nearest doctors, the case has remained unreviewed for over 24 hours.
            
            Recommended Actions:
            - Review the case immediately in the admin panel
            - Contact the patient directly to ensure they seek medical attention
            - Follow up with the notified doctors to understand why the case wasn't reviewed
            - Consider escalating to emergency services if patient cannot be reached
            
            Review Case: {report_url}
            
            System Information:
            This is an automated escalation notification triggered by the SkinGuard Emergency Referral System. 
            The system checks for unreviewed urgent cases every hour.
            
            ---
            SkinGuard AI - Urgent Case Escalation System
            This is an automated notification. Please take immediate action.
            """
            
            return await self.email_service.send_email(
                to_email=admin_email,
                subject=subject,
                html_body=html_body,
                text_body=text_body
            )
            
        except Exception as e:
            logger.error(f"Error sending admin escalation notification: {str(e)}", exc_info=True)
            return False
    
    async def track_escalation(self, report_id: str) -> bool:
        """
        Track that an escalation notification has been sent for a report
        This prevents duplicate notifications
        
        Args:
            report_id: Medical report UUID
            
        Returns:
            bool: True if tracking successful
        """
        try:
            # Create audit log entry for escalation
            audit_entry = {
                "user_id": None,  # System action
                "action": "urgent_case_escalation",
                "resource_type": "medical_report",
                "resource_id": report_id,
                "metadata": {
                    "escalation_timestamp": datetime.utcnow().isoformat(),
                    "reason": "Unreviewed urgent case for 24+ hours"
                },
                "ip_address": None
            }
            
            result = supabase.table("audit_logs").insert(audit_entry).execute()
            
            if result.data:
                logger.info(f"Escalation tracked for report {report_id}")
                return True
            else:
                logger.warning(f"Failed to track escalation for report {report_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error tracking escalation: {str(e)}", exc_info=True)
            return False
    
    async def has_been_escalated(self, report_id: str) -> bool:
        """
        Check if a report has already been escalated
        
        Args:
            report_id: Medical report UUID
            
        Returns:
            bool: True if already escalated
        """
        try:
            result = supabase.table("audit_logs")\
                .select("id")\
                .eq("action", "urgent_case_escalation")\
                .eq("resource_type", "medical_report")\
                .eq("resource_id", report_id)\
                .execute()
            
            return bool(result.data and len(result.data) > 0)
            
        except Exception as e:
            logger.error(f"Error checking escalation status: {str(e)}", exc_info=True)
            return False
    
    async def process_escalations(self) -> Dict[str, int]:
        """
        Main escalation processing function
        Checks for unreviewed urgent cases and sends admin notifications
        Requirements: 23.6
        
        Returns:
            Dict[str, int]: Statistics about escalations processed
        """
        try:
            logger.info("Starting urgent case escalation check...")
            
            # Get unreviewed urgent cases
            unreviewed_cases = await self.check_unreviewed_urgent_cases()
            
            if not unreviewed_cases:
                logger.info("No cases requiring escalation")
                return {
                    "cases_checked": 0,
                    "cases_escalated": 0,
                    "notifications_sent": 0
                }
            
            # Get admin emails
            admin_emails = await self.get_admin_emails()
            
            if not admin_emails:
                logger.error("No admin users found - cannot send escalation notifications")
                return {
                    "cases_checked": len(unreviewed_cases),
                    "cases_escalated": 0,
                    "notifications_sent": 0
                }
            
            # Process each case
            cases_escalated = 0
            notifications_sent = 0
            
            for case in unreviewed_cases:
                report_id = case.get("id")
                
                # Check if already escalated
                if await self.has_been_escalated(report_id):
                    logger.info(f"Report {report_id} already escalated, skipping")
                    continue
                
                # Send notifications to all admins
                case_notifications_sent = 0
                
                for admin_email in admin_emails:
                    success = await self.send_admin_escalation_notification(
                        admin_email=admin_email,
                        case=case
                    )
                    
                    if success:
                        case_notifications_sent += 1
                        notifications_sent += 1
                
                # Track escalation if at least one notification was sent
                if case_notifications_sent > 0:
                    await self.track_escalation(report_id)
                    cases_escalated += 1
                    logger.info(
                        f"Escalated report {report_id}: "
                        f"{case_notifications_sent}/{len(admin_emails)} notifications sent"
                    )
            
            logger.info(
                f"Escalation check completed: {cases_escalated}/{len(unreviewed_cases)} cases escalated, "
                f"{notifications_sent} total notifications sent"
            )
            
            return {
                "cases_checked": len(unreviewed_cases),
                "cases_escalated": cases_escalated,
                "notifications_sent": notifications_sent
            }
            
        except Exception as e:
            logger.error(f"Error in process_escalations: {str(e)}", exc_info=True)
            return {
                "cases_checked": 0,
                "cases_escalated": 0,
                "notifications_sent": 0
            }


# Global scheduler instance
_scheduler: Optional[AsyncIOScheduler] = None
_escalation_service: Optional[UrgentCaseEscalationService] = None


def get_escalation_service() -> UrgentCaseEscalationService:
    """
    Get or create the global escalation service instance
    
    Returns:
        UrgentCaseEscalationService: Global escalation service instance
    """
    global _escalation_service
    if _escalation_service is None:
        _escalation_service = UrgentCaseEscalationService()
    return _escalation_service


async def check_urgent_cases_job():
    """
    Background job to check for unreviewed urgent cases
    Runs every hour
    """
    logger.info("Running scheduled urgent case escalation check")
    escalation_service = get_escalation_service()
    stats = await escalation_service.process_escalations()
    logger.info(f"Escalation check completed: {stats}")


async def process_account_deletions_job():
    """
    Background job to process scheduled account deletions
    Runs daily at 2 AM UTC
    Requirements: 18.3
    """
    logger.info("Running scheduled account deletion processing")
    from app.account_deletion import get_account_deletion_service
    
    deletion_service = get_account_deletion_service()
    stats = await deletion_service.process_scheduled_deletions()
    logger.info(f"Account deletion processing completed: {stats}")


def start_scheduler():
    """
    Start the background job scheduler
    Should be called on application startup
    """
    global _scheduler
    
    if _scheduler is not None:
        logger.warning("Scheduler already running")
        return
    
    logger.info("Starting background job scheduler...")
    
    _scheduler = AsyncIOScheduler()
    
    # Add job to check urgent cases every hour
    _scheduler.add_job(
        check_urgent_cases_job,
        trigger=IntervalTrigger(hours=1),
        id="check_urgent_cases",
        name="Check Unreviewed Urgent Cases",
        replace_existing=True
    )
    
    # Add job to process account deletions daily at 2 AM UTC
    # Requirements: 18.3
    from apscheduler.triggers.cron import CronTrigger
    _scheduler.add_job(
        process_account_deletions_job,
        trigger=CronTrigger(hour=2, minute=0),
        id="process_account_deletions",
        name="Process Scheduled Account Deletions",
        replace_existing=True
    )
    
    _scheduler.start()
    logger.info("Background job scheduler started successfully")


def stop_scheduler():
    """
    Stop the background job scheduler
    Should be called on application shutdown
    """
    global _scheduler
    
    if _scheduler is None:
        logger.warning("Scheduler not running")
        return
    
    logger.info("Stopping background job scheduler...")
    _scheduler.shutdown()
    _scheduler = None
    logger.info("Background job scheduler stopped")
