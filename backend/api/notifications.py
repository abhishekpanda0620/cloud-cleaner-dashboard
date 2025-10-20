from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr
import logging
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from datetime import datetime
from core.config import settings

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


def send_slack_notification(webhook_url: str, message: str, resource_data: Dict[str, Any]) -> bool:
    """
    Send notification to Slack
    
    Args:
        webhook_url: Slack webhook URL
        message: Message to send
        resource_data: Resource data for the message
    
    Returns:
        True if successful, False otherwise
    """
    try:
        payload = {
            "text": message,
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "☁️ Cloud Cleaner Alert"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*EC2 Instances:*\n{resource_data.get('ec2_count', 0)}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*EBS Volumes:*\n{resource_data.get('ebs_count', 0)}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*S3 Buckets:*\n{resource_data.get('s3_count', 0)}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*IAM Users:*\n{resource_data.get('iam_users_count', 0)}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"💰 *Potential Savings:* ${resource_data.get('total_savings', 0):.2f}/month"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info("Slack notification sent successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send Slack notification: {str(e)}")
        return False


def send_email_notification(
    recipients: List[str],
    subject: str,
    resource_data: Dict[str, Any],
    smtp_config: Dict[str, Any]
) -> bool:
    """
    Send notification via email
    
    Args:
        recipients: List of email addresses
        subject: Email subject
        resource_data: Resource data for the message
        smtp_config: SMTP configuration
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create HTML email body
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; }}
                    .header {{ background-color: #1e293b; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f8fafc; }}
                    .resource-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }}
                    .resource-card {{ background-color: white; padding: 15px; border-radius: 8px; border-left: 4px solid #3b82f6; }}
                    .resource-card h3 {{ margin: 0 0 10px 0; color: #1e293b; }}
                    .resource-card .count {{ font-size: 24px; font-weight: bold; color: #3b82f6; }}
                    .savings {{ background-color: #dcfce7; padding: 15px; border-radius: 8px; margin: 20px 0; text-align: center; }}
                    .savings h2 {{ margin: 0; color: #166534; }}
                    .footer {{ text-align: center; padding: 20px; color: #64748b; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>☁️ Cloud Cleaner Report</h1>
                        <p>Unused AWS Resources Alert</p>
                    </div>
                    
                    <div class="content">
                        <p>Hello,</p>
                        <p>Your Cloud Cleaner Dashboard has detected unused AWS resources that could help reduce costs.</p>
                        
                        <div class="resource-grid">
                            <div class="resource-card">
                                <h3>🖥️ EC2 Instances</h3>
                                <div class="count">{resource_data.get('ec2_count', 0)}</div>
                                <p>Stopped instances</p>
                            </div>
                            <div class="resource-card">
                                <h3>💾 EBS Volumes</h3>
                                <div class="count">{resource_data.get('ebs_count', 0)}</div>
                                <p>Unattached volumes</p>
                            </div>
                            <div class="resource-card">
                                <h3>🪣 S3 Buckets</h3>
                                <div class="count">{resource_data.get('s3_count', 0)}</div>
                                <p>Unused buckets</p>
                            </div>
                            <div class="resource-card">
                                <h3>👥 IAM Users</h3>
                                <div class="count">{resource_data.get('iam_users_count', 0)}</div>
                                <p>Inactive users</p>
                            </div>
                        </div>
                        
                        <div class="savings">
                            <h2>💰 Potential Monthly Savings</h2>
                            <h1 style="margin: 10px 0; color: #15803d;">${resource_data.get('total_savings', 0):.2f}</h1>
                        </div>
                        
                        <p>Log in to your Cloud Cleaner Dashboard to review and take action on these resources.</p>
                        <p>Best regards,<br>Cloud Cleaner Team</p>
                    </div>
                    
                    <div class="footer">
                        <p>Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                        <p>This is an automated message. Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_config.get('sender_email', 'noreply@cloudcleaner.local')
        msg['To'] = ', '.join(recipients)
        
        # Attach HTML body
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        with smtplib.SMTP(smtp_config.get('smtp_server'), smtp_config.get('smtp_port', 587)) as server:
            server.starttls()
            server.login(smtp_config.get('smtp_username'), smtp_config.get('smtp_password'))
            server.send_message(msg)
        
        logger.info(f"Email notification sent to {len(recipients)} recipients")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email notification: {str(e)}")
        return False


@router.post("/send-alert")
async def send_alert(alert: ResourceAlert) -> Dict[str, Any]:
    """
    Send resource alert via configured channels (Slack, Email)
    
    Args:
        alert: Resource alert data
    
    Returns:
        Status of notification delivery
    """
    try:
        slack_webhook = settings.slack_webhook_url
        email_recipients_str = settings.notification_email_recipients or ''
        email_recipients = email_recipients_str.split(',') if email_recipients_str else []
        
        logger.info(f"Alert request - Channel: {alert.channel}, Slack configured: {bool(slack_webhook)}, Email configured: {bool(email_recipients_str)}")
        
        results = {
            'slack_sent': False,
            'email_sent': False,
            'message': 'Alert sent'
        }
        
        resource_data = {
            'ec2_count': alert.details.get('ec2_count', 0),
            'ebs_count': alert.details.get('ebs_count', 0),
            's3_count': alert.details.get('s3_count', 0),
            'iam_users_count': alert.details.get('iam_users_count', 0),
            'total_savings': alert.estimated_savings
        }
        
        # Determine which channels to send to
        send_slack = alert.channel is None or alert.channel == 'slack'
        send_email = alert.channel is None or alert.channel == 'email'
        
        # Send Slack notification
        if send_slack and slack_webhook:
            logger.info(f"Sending Slack notification to webhook")
            message = f"🚨 Found {alert.count} unused AWS resources! Potential savings: ${alert.estimated_savings:.2f}/month"
            results['slack_sent'] = send_slack_notification(slack_webhook, message, resource_data)
        elif send_slack and not slack_webhook:
            logger.warning("Slack notification requested but SLACK_WEBHOOK_URL not configured")
        
        # Send Email notification
        if send_email and email_recipients and email_recipients[0]:
            smtp_config = {
                'smtp_server': settings.smtp_server or 'smtp.gmail.com',
                'smtp_port': settings.smtp_port or 587,
                'smtp_username': settings.smtp_username,
                'smtp_password': settings.smtp_password,
                'sender_email': settings.sender_email or 'noreply@cloudcleaner.local'
            }
            
            if smtp_config['smtp_username'] and smtp_config['smtp_password']:
                results['email_sent'] = send_email_notification(
                    [e.strip() for e in email_recipients if e.strip()],
                    f"Cloud Cleaner Alert: {alert.count} Unused Resources Found",
                    resource_data,
                    smtp_config
                )
            else:
                logger.warning("Email notification requested but SMTP credentials not configured")
        elif send_email and not (email_recipients and email_recipients[0]):
            logger.warning("Email notification requested but NOTIFICATION_EMAIL_RECIPIENTS not configured")
        
        # If a specific channel was requested, verify it was sent
        if alert.channel:
            if alert.channel == 'slack' and not results['slack_sent']:
                logger.warning(f"Slack alert requested but failed to send")
                raise HTTPException(
                    status_code=400,
                    detail="Failed to send Slack notification. Please check SLACK_WEBHOOK_URL configuration."
                )
            elif alert.channel == 'email' and not results['email_sent']:
                logger.warning(f"Email alert requested but failed to send")
                raise HTTPException(
                    status_code=400,
                    detail="Failed to send Email notification. Please check SMTP and email recipient configuration."
                )
        
        logger.info(f"Alert sent - Slack: {results['slack_sent']}, Email: {results['email_sent']}")
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending alert: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send alert: {str(e)}"
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
