"""
Email Service for Report Delivery
Sends generated reports via email using SMTP
"""
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formataddr
from jinja2 import Template
from typing import List, Dict, Any
import os
from datetime import datetime


class EmailService:
    """Email service for sending reports"""

    def __init__(self, smtp_host: str, smtp_port: int, smtp_user: str, smtp_password: str,  from_email: str, from_name: str = "S&OP Portal"):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email
        self.from_name = from_name

    async def send_report_email(
        self,
        to_emails: List[str],
        subject: str,
        report_name: str,
        report_type: str,
        file_path: str,
        generated_at: str
    ):
        """Send report via email with attachment"""

        # Create HTML email body
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }
                .container {
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .header {
                    background-color: #1E40AF;
                    color: white;
                    padding: 20px;
                    text-align: center;
                }
                .content {
                    padding: 20px;
                    background-color: #f9fafb;
                }
                .footer {
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #6b7280;
                }
                .button {
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #10B981;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 15px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>S&OP Portal Report</h1>
                </div>
                <div class="content">
                    <h2>{{ report_name }}</h2>
                    <p>Your requested report has been generated and is attached to this email.</p>

                    <p><strong>Report Details:</strong></p>
                    <ul>
                        <li><strong>Report Type:</strong> {{ report_type }}</li>
                        <li><strong>Generated At:</strong> {{ generated_at }}</li>
                        <li><strong>File Name:</strong> {{ file_name }}</li>
                    </ul>

                    <p>The report is attached as {{ file_format }}. You can open it with appropriate software.</p>

                    <p style="margin-top: 20px;">
                        <em>This is an automated email from S&OP Portal. Please do not reply to this email.</em>
                    </p>
                </div>
                <div class="footer">
                    <p>&copy; {{ year }} S&OP Portal. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        template = Template(html_template)

        # Get file name and format
        file_name = os.path.basename(file_path)
        file_format = "Excel (.xlsx)" if file_path.endswith(".xlsx") else "PDF (.pdf)" if file_path.endswith(".pdf") else "Unknown"

        # Render HTML
        html_content = template.render(
            report_name=report_name,
            report_type=report_type,
            generated_at=generated_at,
            file_name=file_name,
            file_format=file_format,
            year=datetime.now().year
        )

        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = formataddr((self.from_name, self.from_email))
        msg['To'] = ', '.join(to_emails)
        msg['Subject'] = subject

        # Add HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        # Attach file
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                file_data = f.read()

            # Determine MIME type
            if file_path.endswith('.xlsx'):
                mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif file_path.endswith('.pdf'):
                mime_type = 'application/pdf'
            else:
                mime_type = 'application/octet-stream'

            attachment = MIMEApplication(file_data, _subtype=mime_type.split('/')[1])
            attachment.add_header('Content-Disposition', 'attachment', filename=file_name)
            msg.attach(attachment)

        # Send email
        await aiosmtplib.send(
            msg,
            hostname=self.smtp_host,
            port=self.smtp_port,
            username=self.smtp_user,
            password=self.smtp_password,
            start_tls=True
        )

    async def send_scheduled_report_notification(
        self,
        to_emails: List[str],
        schedule_name: str,
        next_run: str
    ):
        """Send notification about scheduled report"""

        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }
                .container {
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .header {
                    background-color: #1E40AF;
                    color: white;
                    padding: 20px;
                    text-align: center;
                }
                .content {
                    padding: 20px;
                    background-color: #f9fafb;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Scheduled Report Configured</h1>
                </div>
                <div class="content">
                    <p>Your scheduled report "{{ schedule_name }}" has been successfully configured.</p>
                    <p><strong>Next Execution:</strong> {{ next_run }}</p>
                    <p>You will receive the report via email when it's generated.</p>
                </div>
            </div>
        </body>
        </html>
        """

        template = Template(html_template)
        html_content = template.render(schedule_name=schedule_name, next_run=next_run)

        msg = MIMEMultipart('alternative')
        msg['From'] = formataddr((self.from_name, self.from_email))
        msg['To'] = ', '.join(to_emails)
        msg['Subject'] = f"Scheduled Report Configured: {schedule_name}"

        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        await aiosmtplib.send(
            msg,
            hostname=self.smtp_host,
            port=self.smtp_port,
            username=self.smtp_user,
            password=self.smtp_password,
            start_tls=True
        )


# Factory function to create email service from environment
def create_email_service() -> EmailService:
    """Create email service from environment variables"""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    from_email = os.getenv("FROM_EMAIL", smtp_user)
    from_name = os.getenv("FROM_NAME", "S&OP Portal")

    return EmailService(
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_user=smtp_user,
        smtp_password=smtp_password,
        from_email=from_email,
        from_name=from_name
    )
