from celery import shared_task
import logging
import asyncio
import requests
from datetime import datetime
from core.config import settings
from core.cache import get_redis_client
from services.aws.global_scanner import GlobalResourceScanner
from services.notification_service import NotificationService
from services.budget_service import BudgetService
from sqlalchemy.ext.asyncio import AsyncSession
from models import get_db
from models import AsyncSessionLocal
logger = logging.getLogger(__name__)

# Helper to run async code in Celery synchronous workers
def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@shared_task(name='core.tasks.scheduled_scan_task', soft_time_limit=600, time_limit=630)
def scheduled_scan_task():
    """
    Periodic task to scan resources and check budgets.
    Delegates to GlobalResourceScanner and NotificationService.
    """
    logger.info("Starting scheduled scan task")
    
    try:
        # 1. Run Global Scan
        scanner = GlobalResourceScanner(region=settings.aws_region)
        scan_result = run_async(scanner.scan_all_regions())
        
        # 2. Check Budget Limits
        # We need a DB session for budget service
        async def check_budget():
            # Use AsyncSessionLocal directly to control lifecycle within this loop
            async with AsyncSessionLocal() as session:
                try:
                    budget_service = BudgetService(session)
                    return await budget_service.check_and_send_alerts()
                finally:
                    await session.close()
        
        budget_result = run_async(check_budget())
        
        # 3. Handle Notifications
        redis_client = get_redis_client()
        channels_config = redis_client.get('schedule:channels')
        channels = channels_config.decode('utf-8').split(',') if channels_config else []
        
        # Send Alert if resources found
        if scan_result['total_resources'] > 0:
            if 'email' in channels:
                recipients_str = settings.notification_email_recipients
                if recipients_str:
                    recipients = [r.strip() for r in recipients_str.split(',')]
                    NotificationService.send_email_notification(
                        subject=f"Cloud Cleaner Report: {scan_result['total_resources']} Unused Resources",
                        content_data=scan_result['resource_data'],
                        recipients=recipients
                    )
            
            if 'slack' in channels and settings.slack_webhook_url:
                NotificationService.send_slack_notification(
                    webhook_url=settings.slack_webhook_url,
                    message_data=scan_result['resource_data']
                )

        # Update last scan time in Redis for UI
        redis_client.set('schedule:last_scan', datetime.utcnow().isoformat())

        # 4. Handle Budget Alerts (Only if status changed or limit exceeded)
        # Note: BudgetLogic would typically handle the 'status change' check internally 
        # or we check the result here.
        if budget_result and budget_result.get('status') == 'exceeded':
            # Send specific budget alert
            # Re-using notification service for simplicity, or add specific budget method
            pass 
            
        logger.info("Scheduled scan task completed successfully")
        return scan_result

    except Exception as e:
        logger.error(f"Error in scheduled scan task: {str(e)}")
        # Don't re-raise to avoid infinite retries if not configured properly, 
        # just log failure.
        return {'success': False, 'error': str(e)}

@shared_task(name='core.tasks.send_alert_task')
def send_alert_task(alert_type, data):
    """
    Generic alert task.
    """
    if alert_type == 'budget_exceeded':
        # TODO: Implement specific budget alert via NotificationService
        pass
    return True

@shared_task(name='core.tasks.send_budget_alert_task')
def send_budget_alert_task(alert_level, current_spend, limit_amount, currency, slack_webhook, email_recipients, smtp_config=None):
    """
    Task to send budget alerts via Email and/or Slack.
    """
    try:
        logging.info(f"Processing budget alert: {alert_level} - ${current_spend:.2f} / ${limit_amount:.2f}")
        
        # 1. Send Email
        if email_recipients:
            # We use the service's method which internally handles template generation
            NotificationService.send_budget_alert(
                current_cost=float(current_spend),
                limit=float(limit_amount),
                recipients=email_recipients
            )
            
        # 2. Send Slack (if configured)
        if slack_webhook:
            # Simple Slack message
            message = {
                "text": f"🚨 *Budget Alert: {alert_level}*\nCurrent Spend: ${current_spend:.2f}\nLimit: ${limit_amount:.2f} {currency}"
            }
            try:
                requests.post(slack_webhook, json=message, timeout=10)
                logging.info("Sent Slack budget alert")
            except Exception as e:
                logging.error(f"Failed to send Slack alert: {e}")
                
        return True
    except Exception as e:
        logging.error(f"Error in send_budget_alert_task: {e}")
        return False