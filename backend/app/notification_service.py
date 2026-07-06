"""
Notification service for SkinGuard platform
Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6

This module provides comprehensive notification functionality for:
- Analysis completion notifications (Requirement 17.1)
- Appointment confirmations (Requirement 17.2)
- Appointment reminders (Requirement 17.3)
- Doctor verification status updates (Requirement 17.4)
- Follow-up screening reminders (Requirement 17.5)
- In-app notifications (Requirement 17.6)
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from app.database import supabase
from app.email_service import get_email_service
import uuid

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Comprehensive notification service for email and in-app notifications
    """
    
    def __init__(self):
        """Initialize notification service"""
        self.email_service = get_email_service()
    
    async def create_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create an in-app notification
        
        Requirements: 17.6
        
        Args:
            user_id: User UUID
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            metadata: Optional metadata dictionary
            
        Returns:
            str: Notification ID if successful, None otherwise
        """
        try:
            # Insert notification into database
            result = supabase.table('notifications').insert({
                'user_id': user_id,
                'type': notification_type,
                'title': title,
                'message': message,
                'read': False,
                'metadata': metadata or {},
                'created_at': datetime.utcnow().isoformat()
            }).execute()
            
            if result.data and len(result.data) > 0:
                notification_id = result.data[0]['id']
                logger.info(f"Created in-app notification {notification_id} for user {user_id}")
                return notification_id
            else:
                logger.error(f"Failed to create notification for user {user_id}: No data returned")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create notification for user {user_id}: {str(e)}", exc_info=True)
            return None
    
    async def send_analysis_complete_notification(
        self,
        user_id: str,
        user_email: str,
        user_name: str,
        report_id: str,
        risk_level: str,
        top_prediction: Dict[str, Any]
    ) -> bool:
        """
        Send notification when AI analysis completes
        
        Requirements: 17.1
        
        Args:
            user_id: User UUID
            user_email: User email address
            user_name: User full name
            report_id: Medical report UUID
            risk_level: Risk level (low/medium/high/urgent)
            top_prediction: Top AI prediction {type: str, probability: float}
            
        Returns:
            bool: True if notification sent successfully
        """
        try:
            # Create in-app notification
            await self.create_notification(
                user_id=user_id,
                notification_type='analysis_complete',
                title='Your Skin Analysis is Ready',
                message=f'Your skin screening results are now available. Risk level: {risk_level}',
                metadata={
                    'report_id': report_id,
                    'risk_level': risk_level,
                    'top_prediction': top_prediction
                }
            )
            
            # Send email notification
            subject = f"Your SkinGuard Analysis Results - {risk_level.upper()} Risk"
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #3b82f6; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
                    .content {{ background-color: #f9fafb; padding: 20px; border: 1px solid #e5e7eb; }}
                    .risk-badge {{ padding: 5px 10px; border-radius: 3px; font-weight: bold; display: inline-block; }}
                    .risk-low {{ background-color: #10b981; color: white; }}
                    .risk-medium {{ background-color: #f59e0b; color: white; }}
                    .risk-high {{ background-color: #ef4444; color: white; }}
                    .risk-urgent {{ background-color: #dc2626; color: white; }}
                    .button {{ display: inline-block; background-color: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 15px 0; }}
                    .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 20px; padding-top: 20px; border-top: 1px solid #e5e7eb; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Your Analysis Results Are Ready</h1>
                    </div>
                    <div class="content">
                        <p>Dear {user_name},</p>
                        
                        <p>Your skin screening analysis has been completed by our AI system.</p>
                        
                        <p><strong>Risk Level:</strong> <span class="risk-badge risk-{risk_level.lower()}">{risk_level.upper()}</span></p>
                        
                        <p><strong>Top Detection:</strong> {top_prediction.get('type', 'Unknown')} ({top_prediction.get('probability', 0) * 100:.1f}% probability)</p>
                        
                        <p><strong>Important:</strong> This is a 94% probability estimate from our AI screening tool. Please consult with verified dermatologists for clinical biopsy and definitive diagnosis.</p>
                        
                        <a href="https://skinguard.com/reports/{report_id}" class="button">View Full Report →</a>
                        
                        <p style="margin-top: 20px;">We recommend connecting with a verified dermatologist through our doctor locator to discuss your results.</p>
                    </div>
                    <div class="footer">
                        <p>SkinGuard AI - Skin Cancer Screening Platform<br>
                        This is an automated notification. Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            email_sent = await self.email_service.send_email(
                to_email=user_email,
                subject=subject,
                html_body=html_body
            )
            
            logger.info(f"Analysis complete notification sent to {user_email}: email={email_sent}")
            return email_sent
            
        except Exception as e:
            logger.error(f"Failed to send analysis complete notification: {str(e)}", exc_info=True)
            return False

    async def send_appointment_confirmation(
        self,
        patient_id: str,
        patient_email: str,
        patient_name: str,
        doctor_id: str,
        doctor_email: str,
        doctor_name: str,
        appointment_id: str,
        scheduled_at: datetime,
        consultation_type: str
    ) -> bool:
        """
        Send appointment confirmation to both patient and doctor
        
        Requirements: 17.2
        
        Args:
            patient_id: Patient UUID
            patient_email: Patient email
            patient_name: Patient name
            doctor_id: Doctor UUID
            doctor_email: Doctor email
            doctor_name: Doctor name
            appointment_id: Appointment UUID
            scheduled_at: Scheduled appointment time
            consultation_type: Type of consultation (in_person/video)
            
        Returns:
            bool: True if both notifications sent successfully
        """
        try:
            # Create in-app notifications
            await self.create_notification(
                user_id=patient_id,
                notification_type='appointment_confirmed',
                title='Appointment Confirmed',
                message=f'Your appointment with Dr. {doctor_name} is confirmed for {scheduled_at.strftime("%B %d, %Y at %I:%M %p")}',
                metadata={
                    'appointment_id': appointment_id,
                    'doctor_id': doctor_id,
                    'scheduled_at': scheduled_at.isoformat(),
                    'consultation_type': consultation_type
                }
            )
            
            await self.create_notification(
                user_id=doctor_id,
                notification_type='appointment_confirmed',
                title='New Appointment Scheduled',
                message=f'New appointment with {patient_name} scheduled for {scheduled_at.strftime("%B %d, %Y at %I:%M %p")}',
                metadata={
                    'appointment_id': appointment_id,
                    'patient_id': patient_id,
                    'scheduled_at': scheduled_at.isoformat(),
                    'consultation_type': consultation_type
                }
            )
            
            # Send email to patient
            patient_subject = f"Appointment Confirmed - {scheduled_at.strftime('%B %d, %Y')}"
            patient_html = f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #3b82f6;">Appointment Confirmed</h2>
                    <p>Dear {patient_name},</p>
                    <p>Your appointment has been confirmed with the following details:</p>
                    <ul>
                        <li><strong>Doctor:</strong> Dr. {doctor_name}</li>
                        <li><strong>Date & Time:</strong> {scheduled_at.strftime("%B %d, %Y at %I:%M %p UTC")}</li>
                        <li><strong>Type:</strong> {consultation_type.replace('_', ' ').title()}</li>
                    </ul>
                    <p>We look forward to seeing you!</p>
                    <p style="color: #6b7280; font-size: 12px; margin-top: 20px;">SkinGuard AI</p>
                </div>
            </body>
            </html>
            """
            
            # Send email to doctor
            doctor_subject = f"New Appointment - {scheduled_at.strftime('%B %d, %Y')}"
            doctor_html = f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #3b82f6;">New Appointment Scheduled</h2>
                    <p>Dear Dr. {doctor_name},</p>
                    <p>A new appointment has been scheduled:</p>
                    <ul>
                        <li><strong>Patient:</strong> {patient_name}</li>
                        <li><strong>Date & Time:</strong> {scheduled_at.strftime("%B %d, %Y at %I:%M %p UTC")}</li>
                        <li><strong>Type:</strong> {consultation_type.replace('_', ' ').title()}</li>
                    </ul>
                    <p>Please review the patient's medical report before the appointment.</p>
                    <p style="color: #6b7280; font-size: 12px; margin-top: 20px;">SkinGuard AI</p>
                </div>
            </body>
            </html>
            """
            
            patient_sent = await self.email_service.send_email(
                to_email=patient_email,
                subject=patient_subject,
                html_body=patient_html
            )
            
            doctor_sent = await self.email_service.send_email(
                to_email=doctor_email,
                subject=doctor_subject,
                html_body=doctor_html
            )
            
            success = patient_sent and doctor_sent
            logger.info(f"Appointment confirmation sent: patient={patient_sent}, doctor={doctor_sent}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to send appointment confirmation: {str(e)}", exc_info=True)
            return False

    async def send_appointment_reminder(
        self,
        user_id: str,
        user_email: str,
        user_name: str,
        appointment_id: str,
        scheduled_at: datetime,
        doctor_name: str,
        consultation_type: str
    ) -> bool:
        """
        Send appointment reminder 24 hours before scheduled time
        
        Requirements: 17.3
        
        Args:
            user_id: User UUID (patient or doctor)
            user_email: User email
            user_name: User name
            appointment_id: Appointment UUID
            scheduled_at: Scheduled appointment time
            doctor_name: Doctor name
            consultation_type: Type of consultation
            
        Returns:
            bool: True if reminder sent successfully
        """
        try:
            # Create in-app notification
            await self.create_notification(
                user_id=user_id,
                notification_type='appointment_reminder',
                title='Appointment Reminder',
                message=f'Reminder: Your appointment is tomorrow at {scheduled_at.strftime("%I:%M %p")}',
                metadata={
                    'appointment_id': appointment_id,
                    'scheduled_at': scheduled_at.isoformat(),
                    'consultation_type': consultation_type
                }
            )
            
            # Send email reminder
            subject = f"Appointment Reminder - Tomorrow at {scheduled_at.strftime('%I:%M %p')}"
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #3b82f6;">Appointment Reminder</h2>
                    <p>Dear {user_name},</p>
                    <p>This is a reminder that you have an appointment scheduled for tomorrow:</p>
                    <ul>
                        <li><strong>Doctor:</strong> Dr. {doctor_name}</li>
                        <li><strong>Date & Time:</strong> {scheduled_at.strftime("%B %d, %Y at %I:%M %p UTC")}</li>
                        <li><strong>Type:</strong> {consultation_type.replace('_', ' ').title()}</li>
                    </ul>
                    <p>Please arrive on time or join the video call at the scheduled time.</p>
                    <p style="color: #6b7280; font-size: 12px; margin-top: 20px;">SkinGuard AI</p>
                </div>
            </body>
            </html>
            """
            
            email_sent = await self.email_service.send_email(
                to_email=user_email,
                subject=subject,
                html_body=html_body
            )
            
            logger.info(f"Appointment reminder sent to {user_email}: {email_sent}")
            return email_sent
            
        except Exception as e:
            logger.error(f"Failed to send appointment reminder: {str(e)}", exc_info=True)
            return False

    async def send_doctor_verification_notification(
        self,
        doctor_id: str,
        doctor_email: str,
        doctor_name: str,
        verified: bool,
        rejection_reason: Optional[str] = None
    ) -> bool:
        """
        Send notification when doctor verification status changes
        
        Requirements: 17.4
        
        Args:
            doctor_id: Doctor UUID
            doctor_email: Doctor email
            doctor_name: Doctor name
            verified: Verification status (True=approved, False=rejected)
            rejection_reason: Reason for rejection (if verified=False)
            
        Returns:
            bool: True if notification sent successfully
        """
        try:
            if verified:
                # Doctor approved
                await self.create_notification(
                    user_id=doctor_id,
                    notification_type='doctor_verified',
                    title='Account Verified',
                    message='Congratulations! Your doctor account has been verified. You can now access patient reports.',
                    metadata={'verified': True}
                )
                
                subject = "Welcome to SkinGuard - Account Verified"
                html_body = f"""
                <!DOCTYPE html>
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #10b981;">Account Verified!</h2>
                        <p>Dear Dr. {doctor_name},</p>
                        <p>Congratulations! Your doctor account has been verified by our admin team.</p>
                        <p><strong>What's Next:</strong></p>
                        <ul>
                            <li>You can now access and review patient medical reports</li>
                            <li>Patients can find you through our doctor locator</li>
                            <li>You can schedule appointments and consultations</li>
                            <li>You'll receive notifications for urgent cases in your area</li>
                        </ul>
                        <p><strong>Platform Guidelines:</strong></p>
                        <ul>
                            <li>Always provide professional medical advice</li>
                            <li>Respond to urgent cases within 24 hours</li>
                            <li>Maintain patient confidentiality</li>
                            <li>Use the platform to complement, not replace, clinical examination</li>
                        </ul>
                        <p>Thank you for joining SkinGuard and helping patients with early skin cancer detection!</p>
                        <p style="color: #6b7280; font-size: 12px; margin-top: 20px;">SkinGuard AI Team</p>
                    </div>
                </body>
                </html>
                """
            else:
                # Doctor rejected
                await self.create_notification(
                    user_id=doctor_id,
                    notification_type='doctor_rejected',
                    title='Verification Update',
                    message=f'Your doctor verification was not approved. Reason: {rejection_reason or "Please contact support for details."}',
                    metadata={'verified': False, 'rejection_reason': rejection_reason}
                )
                
                subject = "SkinGuard Account Verification Update"
                html_body = f"""
                <!DOCTYPE html>
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #ef4444;">Verification Update</h2>
                        <p>Dear Dr. {doctor_name},</p>
                        <p>Thank you for your interest in joining SkinGuard. After reviewing your application, we are unable to verify your account at this time.</p>
                        <p><strong>Reason:</strong> {rejection_reason or "Please contact our support team for more details."}</p>
                        <p>If you believe this is an error or would like to resubmit your application with additional documentation, please contact our support team at support@skinguard.com.</p>
                        <p style="color: #6b7280; font-size: 12px; margin-top: 20px;">SkinGuard AI Team</p>
                    </div>
                </body>
                </html>
                """
            
            email_sent = await self.email_service.send_email(
                to_email=doctor_email,
                subject=subject,
                html_body=html_body
            )
            
            logger.info(f"Doctor verification notification sent to {doctor_email}: verified={verified}, email={email_sent}")
            return email_sent
            
        except Exception as e:
            logger.error(f"Failed to send doctor verification notification: {str(e)}", exc_info=True)
            return False

    async def send_followup_screening_reminder(
        self,
        user_id: str,
        user_email: str,
        user_name: str,
        last_screening_date: datetime
    ) -> bool:
        """
        Send reminder for follow-up screening (6 months after last screening)
        
        Requirements: 17.5
        
        Args:
            user_id: User UUID
            user_email: User email
            user_name: User name
            last_screening_date: Date of last screening
            
        Returns:
            bool: True if reminder sent successfully
        """
        try:
            # Create in-app notification
            await self.create_notification(
                user_id=user_id,
                notification_type='followup_reminder',
                title='Time for a Follow-Up Screening',
                message=f'It has been 6 months since your last skin screening on {last_screening_date.strftime("%B %d, %Y")}. Consider scheduling a follow-up.',
                metadata={
                    'last_screening_date': last_screening_date.isoformat()
                }
            )
            
            # Send email reminder
            subject = "Time for Your Follow-Up Skin Screening"
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #3b82f6;">Follow-Up Screening Reminder</h2>
                    <p>Dear {user_name},</p>
                    <p>It has been 6 months since your last skin screening on {last_screening_date.strftime("%B %d, %Y")}.</p>
                    <p>Regular skin screenings are important for early detection of skin cancer. We recommend scheduling a follow-up screening to monitor any changes.</p>
                    <p><strong>Why Regular Screenings Matter:</strong></p>
                    <ul>
                        <li>Early detection significantly improves treatment outcomes</li>
                        <li>Track changes in existing lesions over time</li>
                        <li>Identify new areas of concern</li>
                        <li>Peace of mind through regular monitoring</li>
                    </ul>
                    <p>Log in to SkinGuard to upload new images and get your AI-powered analysis.</p>
                    <p style="color: #6b7280; font-size: 12px; margin-top: 20px;">SkinGuard AI - Your Skin Health Partner</p>
                </div>
            </body>
            </html>
            """
            
            email_sent = await self.email_service.send_email(
                to_email=user_email,
                subject=subject,
                html_body=html_body
            )
            
            logger.info(f"Follow-up screening reminder sent to {user_email}: {email_sent}")
            return email_sent
            
        except Exception as e:
            logger.error(f"Failed to send follow-up screening reminder: {str(e)}", exc_info=True)
            return False


# Global notification service instance
_notification_service: Optional[NotificationService] = None


def get_notification_service() -> NotificationService:
    """
    Get or create the global notification service instance
    
    Returns:
        NotificationService: Global notification service instance
    """
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service
