"""
Scheduled cleanup tasks
"""
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from ..database import SessionLocal
from ..models.syslog import SyslogMessage
from .settings_service import get_syslog_retention_days, is_syslog_cleanup_enabled, get_syslog_cleanup_hour
import logging

logger = logging.getLogger(__name__)


def cleanup_old_logs():
    """
    Cleanup old syslog messages based on retention settings
    """
    db = SessionLocal()
    try:
        # Check if cleanup is enabled
        if not is_syslog_cleanup_enabled(db):
            logger.info("[CLEANUP] Automatic log cleanup is disabled")
            return

        # Get retention period
        retention_days = get_syslog_retention_days(db)
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        # Delete old logs
        deleted = db.query(SyslogMessage).filter(
            SyslogMessage.timestamp < cutoff_date
        ).delete()

        db.commit()

        if deleted > 0:
            logger.info(f"[CLEANUP] Deleted {deleted} syslog messages older than {retention_days} days")
            print(f"✓ Cleanup: Deleted {deleted} old syslog messages")
        else:
            logger.info(f"[CLEANUP] No logs older than {retention_days} days found")

    except Exception as e:
        logger.error(f"[CLEANUP ERROR] Failed to cleanup logs: {e}")
        db.rollback()
    finally:
        db.close()


def start_cleanup_scheduler():
    """
    Start the background scheduler for automatic cleanup
    """
    scheduler = BackgroundScheduler()

    # Get the configured cleanup hour
    db = SessionLocal()
    try:
        cleanup_hour = get_syslog_cleanup_hour(db)
    finally:
        db.close()

    # Schedule daily cleanup at the configured hour
    scheduler.add_job(
        cleanup_old_logs,
        'cron',
        hour=cleanup_hour,
        minute=0,
        id='syslog_cleanup',
        replace_existing=True
    )

    # Also run cleanup once a day as a backup
    scheduler.add_job(
        cleanup_old_logs,
        'interval',
        days=1,
        id='syslog_cleanup_interval',
        replace_existing=True,
        next_run_time=datetime.now() + timedelta(hours=1)  # First run in 1 hour
    )

    scheduler.start()
    print(f"✓ Cleanup scheduler started (daily at {cleanup_hour}:00)")

    return scheduler
