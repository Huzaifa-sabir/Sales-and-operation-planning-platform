"""
Notification Service
Sends email notifications for various events
"""
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
import os

from app.utils.email_service import EmailService, create_email_service
from app.utils.notification_templates import NotificationTemplates
from app.services.settings_service import SettingsService


class NotificationService:
    """Service for sending notifications"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.settings_service = SettingsService(db)
        self.email_service: Optional[EmailService] = None

    async def _get_email_service(self) -> EmailService:
        """Get or create email service with current settings"""
        # Get email settings
        smtp_host = await self.settings_service.get_setting_value("smtp_host", "smtp.gmail.com")
        smtp_port = await self.settings_service.get_setting_value("smtp_port", 587)
        smtp_user = os.getenv("SMTP_USER", "")
        smtp_password = os.getenv("SMTP_PASSWORD", "")
        from_email = await self.settings_service.get_setting_value("from_email", "noreply@sopportal.com")
        from_name = await self.settings_service.get_setting_value("from_name", "S&OP Portal")

        return EmailService(
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_user=smtp_user,
            smtp_password=smtp_password,
            from_email=from_email,
            from_name=from_name
        )

    async def _is_notifications_enabled(self) -> bool:
        """Check if email notifications are enabled"""
        return await self.settings_service.get_setting_value("notification_email_enabled", True)

    async def send_cycle_opened_notification(
        self,
        recipients: List[str],
        cycle_name: str,
        start_date: str,
        end_date: str,
        cycle_id: str
    ):
        """Send notification when a new cycle is opened"""
        if not await self._is_notifications_enabled():
            return

        email_service = await self._get_email_service()

        html_content = NotificationTemplates.cycle_opened(
            cycle_name=cycle_name,
            start_date=start_date,
            end_date=end_date,
            cycle_id=cycle_id
        )

        # Create plain text message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"New S&OP Cycle Opened: {cycle_name}"
        msg['From'] = email_service.from_email
        msg['To'] = ', '.join(recipients)

        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        try:
            await email_service.send_report_email(
                to_emails=recipients,
                subject=f"New S&OP Cycle Opened: {cycle_name}",
                report_name=cycle_name,
                report_type="Cycle Notification",
                file_path="",  # No attachment
                generated_at=start_date
            )
        except Exception as e:
            print(f"Failed to send cycle opened notification: {str(e)}")

    async def send_deadline_reminder(
        self,
        recipients: List[str],
        cycle_name: str,
        end_date: str,
        days_remaining: int,
        cycle_id: str,
        pending_forecasts: int = 0
    ):
        """Send deadline reminder notification"""
        if not await self._is_notifications_enabled():
            return

        email_service = await self._get_email_service()

        html_content = NotificationTemplates.deadline_reminder(
            cycle_name=cycle_name,
            end_date=end_date,
            days_remaining=days_remaining,
            cycle_id=cycle_id,
            pending_forecasts=pending_forecasts
        )

        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"⚠️ Reminder: {cycle_name} deadline in {days_remaining} day(s)"
        msg['From'] = email_service.from_email
        msg['To'] = ', '.join(recipients)

        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        try:
            import aiosmtplib
            await aiosmtplib.send(
                msg,
                hostname=email_service.smtp_host,
                port=email_service.smtp_port,
                username=email_service.smtp_user,
                password=email_service.smtp_password,
                start_tls=True
            )
        except Exception as e:
            print(f"Failed to send deadline reminder: {str(e)}")

    async def send_submission_received_notification(
        self,
        recipients: List[str],
        cycle_name: str,
        customer_name: str,
        product_name: str,
        submitted_by: str,
        cycle_id: str
    ):
        """Send notification when forecast is submitted"""
        if not await self._is_notifications_enabled():
            return

        email_service = await self._get_email_service()

        html_content = NotificationTemplates.submission_received(
            cycle_name=cycle_name,
            customer_name=customer_name,
            product_name=product_name,
            submitted_by=submitted_by,
            cycle_id=cycle_id
        )

        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Forecast Submission Received: {customer_name} - {product_name}"
        msg['From'] = email_service.from_email
        msg['To'] = ', '.join(recipients)

        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        try:
            import aiosmtplib
            await aiosmtplib.send(
                msg,
                hostname=email_service.smtp_host,
                port=email_service.smtp_port,
                username=email_service.smtp_user,
                password=email_service.smtp_password,
                start_tls=True
            )
        except Exception as e:
            print(f"Failed to send submission notification: {str(e)}")
