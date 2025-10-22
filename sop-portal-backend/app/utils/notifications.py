"""
Notification Helper Utilities
Simple logging-based notifications for cycle events
(Full email implementation can be added in Step 10)
"""
import logging
from typing import List, Optional
from datetime import datetime

# Setup logger
logger = logging.getLogger(__name__)


def notify_cycle_opened(cycle_name: str, cycle_id: str, user_emails: Optional[List[str]] = None):
    """
    Send notification when a cycle is opened
    For now, just logs the event. Can be extended to send emails.
    """
    message = f"S&OP Cycle OPENED: '{cycle_name}' (ID: {cycle_id}) at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    logger.info(message)

    # TODO: Implement email sending in Step 10
    # if user_emails:
    #     send_email(
    #         to=user_emails,
    #         subject=f"New S&OP Cycle Opened: {cycle_name}",
    #         body=f"The S&OP cycle '{cycle_name}' is now open for forecast submissions..."
    #     )

    print(f"[NOTIFICATION] {message}")
    if user_emails:
        print(f"[NOTIFICATION] Would notify {len(user_emails)} users: {', '.join(user_emails[:3])}...")


def notify_cycle_closed(cycle_name: str, cycle_id: str, completion_pct: float, admin_emails: Optional[List[str]] = None):
    """
    Send notification when a cycle is closed
    For now, just logs the event. Can be extended to send emails.
    """
    message = f"S&OP Cycle CLOSED: '{cycle_name}' (ID: {cycle_id}) - Completion: {completion_pct}% at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    logger.info(message)

    # TODO: Implement email sending in Step 10
    # if admin_emails:
    #     send_email(
    #         to=admin_emails,
    #         subject=f"S&OP Cycle Closed: {cycle_name}",
    #         body=f"The S&OP cycle '{cycle_name}' has been closed. Final completion: {completion_pct}%..."
    #     )

    print(f"[NOTIFICATION] {message}")
    if admin_emails:
        print(f"[NOTIFICATION] Would notify {len(admin_emails)} admins: {', '.join(admin_emails[:3])}...")


def notify_submission_reminder(cycle_name: str, user_email: str, deadline: datetime):
    """
    Send reminder notification for forecast submission
    For now, just logs the event. Can be extended to send emails.
    """
    message = f"REMINDER: Submit forecast for '{cycle_name}' before {deadline.strftime('%Y-%m-%d')}"
    logger.info(f"{message} - User: {user_email}")

    # TODO: Implement email sending in Step 10
    print(f"[NOTIFICATION] {message} -> {user_email}")
