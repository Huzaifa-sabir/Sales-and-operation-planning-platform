"""
Email Notification Templates
HTML templates for various notification types
"""
from jinja2 import Template
from datetime import datetime


class NotificationTemplates:
    """Collection of email notification templates"""

    @staticmethod
    def cycle_opened(cycle_name: str, start_date: str, end_date: str, cycle_id: str) -> str:
        """Template for cycle opened notification"""
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #1E40AF; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }
        .content { padding: 30px; background-color: #f9fafb; border: 1px solid #e5e7eb; }
        .footer { padding: 20px; text-align: center; font-size: 12px; color: #6b7280; }
        .button { display: inline-block; padding: 12px 24px; background-color: #10B981; color: white !important; text-decoration: none; border-radius: 5px; margin-top: 20px; }
        .info-box { background-color: #DBEAFE; padding: 15px; border-left: 4px solid #1E40AF; margin: 20px 0; }
        .highlight { color: #1E40AF; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>New S&OP Cycle Opened</h1>
        </div>
        <div class="content">
            <h2>{{ cycle_name }}</h2>
            <p>A new Sales & Operations Planning cycle has been opened and is ready for forecast submissions.</p>

            <div class="info-box">
                <p><strong>Cycle Details:</strong></p>
                <ul>
                    <li><strong>Cycle Name:</strong> {{ cycle_name }}</li>
                    <li><strong>Start Date:</strong> {{ start_date }}</li>
                    <li><strong>End Date:</strong> <span class="highlight">{{ end_date }}</span></li>
                    <li><strong>Status:</strong> OPEN</li>
                </ul>
            </div>

            <p><strong>Action Required:</strong></p>
            <p>Please log in to the S&OP Portal and submit your forecasts before the deadline.</p>

            <a href="http://localhost:3000/cycles/{{ cycle_id }}" class="button">View Cycle Details</a>

            <p style="margin-top: 30px; font-size: 14px; color: #6b7280;">
                This is an automated notification from the S&OP Portal. Please do not reply to this email.
            </p>
        </div>
        <div class="footer">
            <p>&copy; {{ year }} S&OP Portal. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """)

        return template.render(
            cycle_name=cycle_name,
            start_date=start_date,
            end_date=end_date,
            cycle_id=cycle_id,
            year=datetime.now().year
        )

    @staticmethod
    def deadline_reminder(cycle_name: str, end_date: str, days_remaining: int, cycle_id: str, pending_forecasts: int) -> str:
        """Template for deadline reminder notification"""
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #F59E0B; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }
        .content { padding: 30px; background-color: #f9fafb; border: 1px solid #e5e7eb; }
        .footer { padding: 20px; text-align: center; font-size: 12px; color: #6b7280; }
        .button { display: inline-block; padding: 12px 24px; background-color: #EF4444; color: white !important; text-decoration: none; border-radius: 5px; margin-top: 20px; }
        .warning-box { background-color: #FEF3C7; padding: 15px; border-left: 4px solid #F59E0B; margin: 20px 0; }
        .urgent { color: #EF4444; font-weight: bold; font-size: 18px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚠️ Forecast Submission Reminder</h1>
        </div>
        <div class="content">
            <h2>{{ cycle_name }}</h2>
            <p class="urgent">Only {{ days_remaining }} day(s) remaining until deadline!</p>

            <div class="warning-box">
                <p><strong>Deadline Information:</strong></p>
                <ul>
                    <li><strong>Cycle:</strong> {{ cycle_name }}</li>
                    <li><strong>Deadline:</strong> <span style="color: #EF4444; font-weight: bold;">{{ end_date }}</span></li>
                    <li><strong>Days Remaining:</strong> {{ days_remaining }}</li>
                    <li><strong>Pending Forecasts:</strong> {{ pending_forecasts }}</li>
                </ul>
            </div>

            <p><strong>Urgent Action Required:</strong></p>
            <p>You have <strong>{{ pending_forecasts }}</strong> forecast(s) that need to be submitted before the deadline. Please complete your submissions as soon as possible to avoid missing the deadline.</p>

            <a href="http://localhost:3000/forecasts?cycleId={{ cycle_id }}" class="button">Submit Forecasts Now</a>

            <p style="margin-top: 30px; font-size: 14px; color: #6b7280;">
                This is an automated reminder from the S&OP Portal. Please do not reply to this email.
            </p>
        </div>
        <div class="footer">
            <p>&copy; {{ year }} S&OP Portal. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """)

        return template.render(
            cycle_name=cycle_name,
            end_date=end_date,
            days_remaining=days_remaining,
            cycle_id=cycle_id,
            pending_forecasts=pending_forecasts,
            year=datetime.now().year
        )

    @staticmethod
    def submission_received(cycle_name: str, customer_name: str, product_name: str, submitted_by: str, cycle_id: str) -> str:
        """Template for submission received notification"""
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #10B981; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }
        .content { padding: 30px; background-color: #f9fafb; border: 1px solid #e5e7eb; }
        .footer { padding: 20px; text-align: center; font-size: 12px; color: #6b7280; }
        .button { display: inline-block; padding: 12px 24px; background-color: #1E40AF; color: white !important; text-decoration: none; border-radius: 5px; margin-top: 20px; }
        .success-box { background-color: #D1FAE5; padding: 15px; border-left: 4px solid: #10B981; margin: 20px 0; }
        .checkmark { color: #10B981; font-size: 48px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✓ Forecast Submission Received</h1>
        </div>
        <div class="content">
            <div class="checkmark">✓</div>
            <h2 style="text-align: center; color: #10B981;">Submission Successful</h2>

            <div class="success-box">
                <p><strong>Submission Details:</strong></p>
                <ul>
                    <li><strong>Cycle:</strong> {{ cycle_name }}</li>
                    <li><strong>Customer:</strong> {{ customer_name }}</li>
                    <li><strong>Product:</strong> {{ product_name }}</li>
                    <li><strong>Submitted By:</strong> {{ submitted_by }}</li>
                    <li><strong>Submission Time:</strong> {{ submission_time }}</li>
                </ul>
            </div>

            <p>Your forecast has been successfully received and recorded in the system. The forecast is now pending review and approval.</p>

            <p><strong>Next Steps:</strong></p>
            <ul>
                <li>Your forecast will be reviewed by management</li>
                <li>You will receive a notification once it's approved or if changes are requested</li>
                <li>You can view the status of your submission in the portal</li>
            </ul>

            <a href="http://localhost:3000/cycles/{{ cycle_id }}" class="button">View Cycle Details</a>

            <p style="margin-top: 30px; font-size: 14px; color: #6b7280;">
                This is an automated confirmation from the S&OP Portal. Please do not reply to this email.
            </p>
        </div>
        <div class="footer">
            <p>&copy; {{ year }} S&OP Portal. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """)

        return template.render(
            cycle_name=cycle_name,
            customer_name=customer_name,
            product_name=product_name,
            submitted_by=submitted_by,
            submission_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            cycle_id=cycle_id,
            year=datetime.now().year
        )
