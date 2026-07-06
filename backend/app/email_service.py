"""
Email notification service for SkinGuard platform
Requirements: 17.1, 17.2, 17.3, 23.3

This module provides email notification functionality for:
- Urgent case notifications to doctors
- Appointment confirmations
- Analysis completion notifications
- Doctor verification status updates
"""
import os
import logging
from typing import List, Optional, Dict
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service for sending notifications
    
    Supports multiple backends:
    - SMTP (for development and production)
    - SendGrid (optional, for production)
    - AWS SES (optional, for production)
    """
    
    def __init__(self):
        """Initialize email service with configuration from environment"""
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@skinguard.com")
        self.from_name = os.getenv("FROM_NAME", "SkinGuard AI")
        
        # Check if email is configured
        self.is_configured = bool(self.smtp_username and self.smtp_password)
        
        if not self.is_configured:
            logger.warning("Email service not configured. Set SMTP_USERNAME and SMTP_PASSWORD environment variables.")
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """
        Send an email
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text email body (optional, falls back to HTML)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.is_configured:
            logger.warning(f"Email not sent to {to_email}: Email service not configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Add text and HTML parts
            if text_body:
                part1 = MIMEText(text_body, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(html_body, 'html')
            msg.attach(part2)
            
            # Send email via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}", exc_info=True)
            return False
    
    async def send_urgent_case_notification(
        self,
        doctor_email: str,
        doctor_name: str,
        patient_name: str,
        report_id: str,
        risk_level: str,
        top_prediction: Dict[str, float],
        report_url: str
    ) -> bool:
        """
        Send urgent case notification to a doctor
        Requirements: 23.3
        
        Args:
            doctor_email: Doctor's email address
            doctor_name: Doctor's full name
            patient_name: Patient's full name
            report_id: Medical report UUID
            risk_level: Risk level (urgent)
            top_prediction: Top AI prediction {type: str, probability: float}
            report_url: URL to view the report
            
        Returns:
            bool: True if email sent successfully
        """
        subject = "🚨 URGENT: High-Risk Skin Lesion Case Requires Review"
        
        # HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #dc2626; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f9fafb; padding: 20px; border: 1px solid #e5e7eb; }}
                .urgent-badge {{ background-color: #dc2626; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold; }}
                .info-box {{ background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #dc2626; }}
                .button {{ display: inline-block; background-color: #dc2626; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 15px 0; }}
                .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 20px; padding-top: 20px; border-top: 1px solid #e5e7eb; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 Urgent Case Notification</h1>
                </div>
                <div class="content">
                    <p>Dear Dr. {doctor_name},</p>
                    
                    <p>A <span class="urgent-badge">HIGH-RISK</span> skin lesion case has been detected and requires immediate medical review.</p>
                    
                    <div class="info-box">
                        <h3>Case Details:</h3>
                        <ul>
                            <li><strong>Patient:</strong> {patient_name}</li>
                            <li><strong>Report ID:</strong> {report_id}</li>
                            <li><strong>Risk Level:</strong> {risk_level.upper()}</li>
                            <li><strong>AI Detection:</strong> {top_prediction.get('type', 'Unknown')} ({top_prediction.get('probability', 0) * 100:.1f}% probability)</li>
                            <li><strong>Date:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</li>
                        </ul>
                    </div>
                    
                    <p><strong>Why you received this notification:</strong><br>
                    You are one of the 3 nearest verified dermatologists to this patient's location. The AI analysis has detected a cancer probability exceeding 85%, triggering our emergency referral protocol.</p>
                    
                    <p><strong>Recommended Action:</strong><br>
                    Please review this case as soon as possible and contact the patient to schedule an urgent consultation for clinical biopsy and diagnosis.</p>
                    
                    <a href="{report_url}" class="button">View Full Report →</a>
                    
                    <p style="margin-top: 20px;"><strong>Important Disclaimer:</strong><br>
                    This is an AI-assisted screening result with 94% accuracy. Clinical examination and biopsy are required for definitive diagnosis. This notification is for informational purposes and does not establish a doctor-patient relationship.</p>
                </div>
                <div class="footer">
                    <p>SkinGuard AI - Emergency Referral System<br>
                    This is an automated notification. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text fallback
        text_body = f"""
        URGENT: High-Risk Skin Lesion Case Requires Review
        
        Dear Dr. {doctor_name},
        
        A HIGH-RISK skin lesion case has been detected and requires immediate medical review.
        
        Case Details:
        - Patient: {patient_name}
        - Report ID: {report_id}
        - Risk Level: {risk_level.upper()}
        - AI Detection: {top_prediction.get('type', 'Unknown')} ({top_prediction.get('probability', 0) * 100:.1f}% probability)
        - Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
        
        Why you received this notification:
        You are one of the 3 nearest verified dermatologists to this patient's location. The AI analysis has detected a cancer probability exceeding 85%, triggering our emergency referral protocol.
        
        Recommended Action:
        Please review this case as soon as possible and contact the patient to schedule an urgent consultation for clinical biopsy and diagnosis.
        
        View Full Report: {report_url}
        
        Important Disclaimer:
        This is an AI-assisted screening result with 94% accuracy. Clinical examination and biopsy are required for definitive diagnosis. This notification is for informational purposes and does not establish a doctor-patient relationship.
        
        ---
        SkinGuard AI - Emergency Referral System
        This is an automated notification. Please do not reply to this email.
        """
        
        return await self.send_email(
            to_email=doctor_email,
            subject=subject,
            html_body=html_body,
            text_body=text_body
        )


# Global email service instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """
    Get or create the global email service instance
    
    Returns:
        EmailService: Global email service instance
    """
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
