from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr
import logging
from core.config import settings
from core.tasks import send_alert_task

logger = logging.getLogger(__name__)
router = APIRouter()


class NotificationConfig(BaseModel):
    """Configuration for notifications"""
    slack_webhook_url: Optional[str] = None
    email_recipients: Optional[List[EmailStr]] = None
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    sender_email: Optional[EmailStr] = None


class ResourceAlert(BaseModel):
    """Resource alert data"""
    resource_type: str
    count: int
    estimated_savings: float
    details: Dict[str, Any]
    channel: Optional[str] = None  # 'slack', 'email', or None for both


@router.post("/send-alert")
async def send_alert(alert: ResourceAlert) -> Dict[str, Any]:
    """
    Send resource alert via configured channels (Slack, Email)
    Uses Celery for true background processing with multi-region scanning
    
    Args:
        alert: Resource alert data
    
    Returns:
        Status indicating task has been queued
    """
    try:
        slack_webhook = settings.slack_webhook_url
        email_recipients_str = settings.notification_email_recipients or ''
        email_recipients = [e.strip() for e in email_recipients_str.split(',') if e.strip()] if email_recipients_str else []
        
        logger.info(f"Alert request - Channel: {alert.channel}, Slack configured: {bool(slack_webhook)}, Email configured: {bool(email_recipients_str)}")
        
        # Validate configuration before queuing
        send_slack = alert.channel is None or alert.channel == 'slack'
        send_email = alert.channel is None or alert.channel == 'email'
        
        if send_slack and not slack_webhook:
            raise HTTPException(
                status_code=400,
                detail="Slack is not configured. Please set SLACK_WEBHOOK_URL in environment variables."
            )
        
        if send_email and not email_recipients:
            raise HTTPException(
                status_code=400,
                detail="Email is not configured. Please set NOTIFICATION_EMAIL_RECIPIENTS in environment variables."
            )
        
        smtp_config = {
            'smtp_server': settings.smtp_server or 'smtp.gmail.com',
            'smtp_port': settings.smtp_port or 587,
            'smtp_username': settings.smtp_username,
            'smtp_password': settings.smtp_password,
            'sender_email': settings.sender_email or 'noreply@cloudcleaner.local'
        }
        
        if send_email and not (smtp_config['smtp_username'] and smtp_config['smtp_password']):
            raise HTTPException(
                status_code=400,
                detail="Email SMTP credentials are not configured. Please set SMTP_USERNAME and SMTP_PASSWORD."
            )
        
        # Queue the Celery task
        task = send_alert_task.delay(
            channel=alert.channel,
            s3_count=alert.details.get('s3_count', 0),
            iam_users_count=alert.details.get('iam_users_count', 0),
            slack_webhook=slack_webhook if send_slack else None,
            email_recipients=email_recipients if send_email else [],
            smtp_config=smtp_config if send_email else {}
        )
        
        logger.info(f"Alert task queued with ID: {task.id}")
        return {
            'task_id': task.id,
            'slack_sent': send_slack and bool(slack_webhook),
            'email_sent': send_email and bool(email_recipients),
            'message': 'Alert is being processed in the background. Scanning all AWS regions for EC2 and EBS resources...'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error queueing alert: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to queue alert: {str(e)}"
        )


@router.get("/config")
async def get_notification_config() -> Dict[str, Any]:
    """
    Get current notification configuration (without sensitive data)
    
    Returns:
        Notification configuration status
    """
    return {
        'slack_configured': bool(settings.slack_webhook_url),
        'email_configured': bool(settings.smtp_username and settings.smtp_password),
        'email_recipients': settings.notification_email_recipients.split(',') if settings.notification_email_recipients else []
    }
