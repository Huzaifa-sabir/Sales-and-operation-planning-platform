"""
Background Task Scheduler
Uses APScheduler to run periodic background jobs
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import os
from typing import Optional

from app.services.settings_service import SettingsService
from app.services.notification_service import NotificationService
from app.services.audit_service import AuditService


class BackgroundScheduler:
    """Manages all background scheduled tasks"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.scheduler = AsyncIOScheduler()
        self.settings_service = SettingsService(db)
        self.notification_service = NotificationService(db)
        self.audit_service = AuditService(db)

    async def send_deadline_reminders(self):
        """
        Send reminders for cycles approaching deadline
        Runs daily at 9 AM
        """
        try:
            # Get reminder days setting
            reminder_days = await self.settings_service.get_setting_value("reminder_days_before_close", 3)

            # Get open cycles
            cycles_collection = self.db.sop_cycles
            forecasts_collection = self.db.forecasts

            # Find cycles that are close to deadline
            target_date = datetime.utcnow() + timedelta(days=reminder_days)

            cycles = await cycles_collection.find({
                "status": "OPEN",
                "endDate": {
                    "$gte": datetime.utcnow(),
                    "$lte": target_date
                }
            }).to_list(100)

            for cycle in cycles:
                cycle_id = str(cycle["_id"])
                cycle_name = cycle.get("cycleName", "Unknown Cycle")
                end_date = cycle.get("endDate").strftime("%Y-%m-%d")
                days_remaining = (cycle.get("endDate") - datetime.utcnow()).days

                # Get users with pending forecasts
                users_collection = self.db.users
                sales_reps = await users_collection.find({"role": "sales_rep", "isActive": True}).to_list(100)

                for user in sales_reps:
                    user_id = str(user["_id"])
                    user_email = user.get("email")

                    # Count pending forecasts for this user
                    pending_count = await forecasts_collection.count_documents({
                        "cycleId": cycle_id,
                        "salesRepId": user_id,
                        "status": "draft"
                    })

                    if pending_count > 0:
                        # Send reminder
                        await self.notification_service.send_deadline_reminder(
                            recipients=[user_email],
                            cycle_name=cycle_name,
                            end_date=end_date,
                            days_remaining=max(days_remaining, 0),
                            cycle_id=cycle_id,
                            pending_forecasts=pending_count
                        )

            print(f"[{datetime.now()}] Sent deadline reminders for {len(cycles)} cycles")

        except Exception as e:
            print(f"[{datetime.now()}] Error sending deadline reminders: {str(e)}")

    async def auto_close_cycles(self):
        """
        Automatically close cycles after deadline
        Runs every hour
        """
        try:
            # Check if auto-close is enabled
            auto_close_enabled = await self.settings_service.get_setting_value("auto_close_cycles", True)

            if not auto_close_enabled:
                return

            cycles_collection = self.db.sop_cycles

            # Find cycles that are past deadline and still open
            result = await cycles_collection.update_many(
                {
                    "status": "OPEN",
                    "endDate": {"$lt": datetime.utcnow()}
                },
                {
                    "$set": {
                        "status": "CLOSED",
                        "updatedAt": datetime.utcnow(),
                        "closedAt": datetime.utcnow(),
                        "autoCloseReason": "Automatically closed after deadline"
                    }
                }
            )

            if result.modified_count > 0:
                print(f"[{datetime.now()}] Auto-closed {result.modified_count} cycle(s)")

                # Log audit event
                await self.audit_service.log(
                    action="CYCLE_CLOSED",
                    entity_type="cycle",
                    severity="INFO",
                    description=f"Auto-closed {result.modified_count} cycle(s) after deadline",
                    metadata={"count": result.modified_count, "auto_closed": True}
                )

        except Exception as e:
            print(f"[{datetime.now()}] Error auto-closing cycles: {str(e)}")

    async def cleanup_old_temp_files(self):
        """
        Delete temporary files older than X days
        Runs daily at 2 AM
        """
        try:
            cleanup_days = await self.settings_service.get_setting_value("cleanup_temp_files_days", 7)
            cutoff_date = datetime.utcnow() - timedelta(days=cleanup_days)

            # Clean up old reports
            reports_collection = self.db.reports
            report_expiry_days = await self.settings_service.get_setting_value("report_expiry_days", 7)
            report_cutoff = datetime.utcnow() - timedelta(days=report_expiry_days)

            old_reports = await reports_collection.find({
                "createdAt": {"$lt": report_cutoff}
            }).to_list(1000)

            deleted_count = 0
            for report in old_reports:
                # Delete physical file
                file_path = report.get("filePath")
                if file_path and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                    except:
                        pass

                # Delete database record
                await reports_collection.delete_one({"_id": report["_id"]})

            if deleted_count > 0:
                print(f"[{datetime.now()}] Cleaned up {deleted_count} old report file(s)")

                # Log audit event
                await self.audit_service.log(
                    action="SYSTEM_BACKUP_CREATED",
                    severity="INFO",
                    description=f"Cleaned up {deleted_count} old report files",
                    metadata={"files_deleted": deleted_count, "cleanup_days": cleanup_days}
                )

        except Exception as e:
            print(f"[{datetime.now()}] Error cleaning up temp files: {str(e)}")

    async def cleanup_old_audit_logs(self):
        """
        Delete audit logs older than 90 days
        Runs weekly on Sunday at 3 AM
        """
        try:
            deleted_count = await self.audit_service.cleanup_old_logs(days=90)

            if deleted_count > 0:
                print(f"[{datetime.now()}] Cleaned up {deleted_count} old audit log(s)")

        except Exception as e:
            print(f"[{datetime.now()}] Error cleaning up audit logs: {str(e)}")

    def start(self):
        """Start the scheduler with all jobs"""
        try:
            # Job 1: Send deadline reminders (daily at 9 AM)
            self.scheduler.add_job(
                self.send_deadline_reminders,
                CronTrigger(hour=9, minute=0),
                id="send_deadline_reminders",
                name="Send Deadline Reminders",
                replace_existing=True
            )

            # Job 2: Auto-close cycles (every hour)
            self.scheduler.add_job(
                self.auto_close_cycles,
                IntervalTrigger(hours=1),
                id="auto_close_cycles",
                name="Auto-close Cycles",
                replace_existing=True
            )

            # Job 3: Cleanup old temp files (daily at 2 AM)
            self.scheduler.add_job(
                self.cleanup_old_temp_files,
                CronTrigger(hour=2, minute=0),
                id="cleanup_temp_files",
                name="Cleanup Temporary Files",
                replace_existing=True
            )

            # Job 4: Cleanup old audit logs (weekly on Sunday at 3 AM)
            self.scheduler.add_job(
                self.cleanup_old_audit_logs,
                CronTrigger(day_of_week='sun', hour=3, minute=0),
                id="cleanup_audit_logs",
                name="Cleanup Old Audit Logs",
                replace_existing=True
            )

            # Start scheduler
            self.scheduler.start()
            print(f"[{datetime.now()}] Background scheduler started with {len(self.scheduler.get_jobs())} jobs")

        except Exception as e:
            print(f"[{datetime.now()}] Error starting scheduler: {str(e)}")

    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print(f"[{datetime.now()}] Background scheduler stopped")
