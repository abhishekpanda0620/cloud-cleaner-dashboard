from celery import Task
from core.celery_app import celery_app
from core.config import settings
from core.aws_client import get_aws_client_factory
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


def fetch_all_regions_data() -> Dict[str, Any]:
    """
    Fetch EC2 and EBS data from all AWS regions
    
    Returns:
        Dictionary with aggregated resource counts and regional breakdown
    """
    try:
        factory = get_aws_client_factory()
        
        # Get list of all enabled regions
        ec2_client = factory.session.client('ec2', region_name=settings.aws_region)
        regions_response = ec2_client.describe_regions(
            Filters=[{'Name': 'opt-in-status', 'Values': ['opt-in-not-required', 'opted-in']}]
        )
        regions = [region['RegionName'] for region in regions_response['Regions']]
        
        logger.info(f"Scanning {len(regions)} regions for unused resources")
        
        ec2_by_region = {}
        ebs_by_region = {}
        total_ec2 = 0
        total_ebs = 0
        
        # Scan each region
        for region in regions:
            try:
                regional_ec2_client = factory.session.client('ec2', region_name=region)
                
                # Get stopped EC2 instances
                ec2_response = regional_ec2_client.describe_instances(
                    Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}]
                )
                
                ec2_count = 0
                for reservation in ec2_response.get('Reservations', []):
                    for instance in reservation.get('Instances', []):
                        state_transition_reason = instance.get('StateTransitionReason', '')
                        if 'User initiated' in state_transition_reason:
                            ec2_count += 1
                
                if ec2_count > 0:
                    ec2_by_region[region] = ec2_count
                    total_ec2 += ec2_count
                
                # Get unattached EBS volumes
                ebs_response = regional_ec2_client.describe_volumes(
                    Filters=[{'Name': 'status', 'Values': ['available']}]
                )
                
                ebs_count = len(ebs_response.get('Volumes', []))
                if ebs_count > 0:
                    ebs_by_region[region] = ebs_count
                    total_ebs += ebs_count
                
                logger.info(f"Region {region}: {ec2_count} EC2, {ebs_count} EBS")
                
            except Exception as e:
                logger.warning(f"Failed to scan region {region}: {str(e)}")
                continue
        
        return {
            'ec2_count': total_ec2,
            'ebs_count': total_ebs,
            'ec2_by_region': ec2_by_region,
            'ebs_by_region': ebs_by_region
        }
        
    except Exception as e:
        logger.error(f"Error fetching multi-region data: {str(e)}")
        return {
            'ec2_count': 0,
            'ebs_count': 0,
            'ec2_by_region': {},
            'ebs_by_region': {}
        }


def send_slack_notification(webhook_url: str, message: str, resource_data: Dict[str, Any]) -> bool:
    """Send notification to Slack"""
    try:
        # Build regional breakdown for EC2 and EBS
        regional_fields = []
        
        # Add EC2 regional breakdown
        ec2_by_region = resource_data.get('ec2_by_region', {})
        if ec2_by_region:
            ec2_text = "*EC2 Instances:*\n"
            for region, count in ec2_by_region.items():
                ec2_text += f"• {region}: {count}\n"
            ec2_text += f"*Total: {resource_data.get('ec2_count', 0)}*"
            regional_fields.append({"type": "mrkdwn", "text": ec2_text})
        else:
            regional_fields.append({
                "type": "mrkdwn",
                "text": f"*EC2 Instances:*\n{resource_data.get('ec2_count', 0)}"
            })
        
        # Add EBS regional breakdown
        ebs_by_region = resource_data.get('ebs_by_region', {})
        if ebs_by_region:
            ebs_text = "*EBS Volumes:*\n"
            for region, count in ebs_by_region.items():
                ebs_text += f"• {region}: {count}\n"
            ebs_text += f"*Total: {resource_data.get('ebs_count', 0)}*"
            regional_fields.append({"type": "mrkdwn", "text": ebs_text})
        else:
            regional_fields.append({
                "type": "mrkdwn",
                "text": f"*EBS Volumes:*\n{resource_data.get('ebs_count', 0)}"
            })
        
        # Add global resources
        regional_fields.extend([
            {
                "type": "mrkdwn",
                "text": f"*S3 Buckets:*\n{resource_data.get('s3_count', 0)}"
            },
            {
                "type": "mrkdwn",
                "text": f"*IAM Users:*\n{resource_data.get('iam_users_count', 0)}"
            }
        ])
        
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
                    "fields": regional_fields
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
    """Send notification via email"""
    try:
        # Build regional breakdown HTML for EC2 and EBS
        ec2_regional_html = ""
        ec2_by_region = resource_data.get('ec2_by_region', {})
        if ec2_by_region:
            ec2_regional_html = "<ul style='margin: 5px 0; padding-left: 20px;'>"
            for region, count in ec2_by_region.items():
                ec2_regional_html += f"<li>{region}: {count}</li>"
            ec2_regional_html += "</ul>"
        
        ebs_regional_html = ""
        ebs_by_region = resource_data.get('ebs_by_region', {})
        if ebs_by_region:
            ebs_regional_html = "<ul style='margin: 5px 0; padding-left: 20px;'>"
            for region, count in ebs_by_region.items():
                ebs_regional_html += f"<li>{region}: {count}</li>"
            ebs_regional_html += "</ul>"
        
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
                    .resource-card .regional-breakdown {{ font-size: 12px; color: #64748b; margin-top: 8px; }}
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
                        <p>Your Cloud Cleaner Dashboard has detected unused AWS resources across multiple regions that could help reduce costs.</p>
                        
                        <div class="resource-grid">
                            <div class="resource-card">
                                <h3>🖥️ EC2 Instances</h3>
                                <div class="count">{resource_data.get('ec2_count', 0)}</div>
                                <p>Stopped instances</p>
                                {f'<div class="regional-breakdown"><strong>By Region:</strong>{ec2_regional_html}</div>' if ec2_regional_html else ''}
                            </div>
                            <div class="resource-card">
                                <h3>💾 EBS Volumes</h3>
                                <div class="count">{resource_data.get('ebs_count', 0)}</div>
                                <p>Unattached volumes</p>
                                {f'<div class="regional-breakdown"><strong>By Region:</strong>{ebs_regional_html}</div>' if ebs_regional_html else ''}
                            </div>
                            <div class="resource-card">
                                <h3>🪣 S3 Buckets</h3>
                                <div class="count">{resource_data.get('s3_count', 0)}</div>
                                <p>Unused buckets (Global)</p>
                            </div>
                            <div class="resource-card">
                                <h3>👥 IAM Users</h3>
                                <div class="count">{resource_data.get('iam_users_count', 0)}</div>
                                <p>Inactive users (Global)</p>
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


@celery_app.task(bind=True, name="send_alert_task", max_retries=3)
def send_alert_task(
    self: Task,
    channel: Optional[str],
    s3_count: int,
    iam_users_count: int,
    slack_webhook: Optional[str],
    email_recipients: List[str],
    smtp_config: Dict[str, Any]
) -> Dict[str, bool]:
    """
    Celery task to send alerts via Slack/Email
    
    Args:
        self: Celery task instance
        channel: 'slack', 'email', or None for both
        s3_count: Number of unused S3 buckets
        iam_users_count: Number of unused IAM users
        slack_webhook: Slack webhook URL
        email_recipients: List of email recipients
        smtp_config: SMTP configuration
        
    Returns:
        Dictionary with send status
    """
    results = {
        'slack_sent': False,
        'email_sent': False
    }
    
    try:
        # Fetch EC2 and EBS data from all regions
        logger.info("Celery task: Fetching EC2 and EBS data from all regions...")
        regional_data = fetch_all_regions_data()
        
        # Use regional data for EC2 and EBS, use provided data for global resources
        resource_data = {
            'ec2_count': regional_data['ec2_count'],
            'ebs_count': regional_data['ebs_count'],
            'ec2_by_region': regional_data['ec2_by_region'],
            'ebs_by_region': regional_data['ebs_by_region'],
            's3_count': s3_count,
            'iam_users_count': iam_users_count,
            'total_savings': (regional_data['ec2_count'] * 50) + (regional_data['ebs_count'] * 10) + (s3_count * 5)
        }
        
        logger.info(f"Multi-region scan complete: {resource_data['ec2_count']} EC2 across {len(resource_data['ec2_by_region'])} regions, {resource_data['ebs_count']} EBS across {len(resource_data['ebs_by_region'])} regions")
        
        # Determine which channels to send to
        send_slack = channel is None or channel == 'slack'
        send_email = channel is None or channel == 'email'
        
        total_resources = resource_data['ec2_count'] + resource_data['ebs_count'] + resource_data['s3_count'] + resource_data['iam_users_count']
        
        # Send Slack notification
        if send_slack and slack_webhook:
            logger.info("Celery task: Sending Slack notification")
            message = f"🚨 Found {total_resources} unused AWS resources across multiple regions! Potential savings: ${resource_data['total_savings']:.2f}/month"
            results['slack_sent'] = send_slack_notification(slack_webhook, message, resource_data)
        
        # Send Email notification
        if send_email and email_recipients and smtp_config.get('smtp_username'):
            logger.info("Celery task: Sending Email notification")
            results['email_sent'] = send_email_notification(
                email_recipients,
                f"Cloud Cleaner Alert: {total_resources} Unused Resources Found",
                resource_data,
                smtp_config
            )
        
        logger.info(f"Celery task complete - Slack: {results['slack_sent']}, Email: {results['email_sent']}")
        return results
        
    except Exception as e:
        logger.error(f"Error in Celery task: {str(e)}")
        # Retry the task
        raise self.retry(exc=e, countdown=60)  # Retry after 60 seconds