from celery import Task
from core.celery_app import celery_app
from core.config import settings
from core.aws_client import get_aws_client_factory
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from datetime import datetime, timezone, timedelta
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
            },
            {
                "type": "mrkdwn",
                "text": f"*Access Keys:*\n{resource_data.get('access_keys_count', 0)} ({resource_data.get('high_risk_keys', 0)} :warning: High Risk)"
            }
        ])
        
        payload = {
            "text": message,
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "☁️ Cloud Cleaner 🧹 Alert"
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
                            <div class="resource-card" style="border-left-color: #ef4444;">
                                <h3>🔑 Access Keys</h3>
                                <div class="count">{resource_data.get('access_keys_count', 0)}</div>
                                <p>Unused keys (Global)</p>
                                <div class="regional-breakdown" style="color: #ef4444; font-weight: bold;">
                                    ⚠️ {resource_data.get('high_risk_keys', 0)} High Risk (Active)
                                </div>
                            </div>
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
        
        # Fetch unused access keys (global) - SECURITY CRITICAL
        try:
            factory = get_aws_client_factory()
            iam_client = factory.session.client('iam')
            paginator = iam_client.get_paginator('list_users')
            unused_access_keys = []
            high_risk_keys = 0
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)
            
            for page in paginator.paginate():
                for user in page.get('Users', []):
                    user_name = user.get('UserName')
                    try:
                        access_keys = iam_client.list_access_keys(UserName=user_name)
                        keys = access_keys.get('AccessKeyMetadata', [])
                        
                        for key in keys:
                            key_id = key.get('AccessKeyId')
                            status = key.get('Status')
                            
                            try:
                                key_last_used = iam_client.get_access_key_last_used(AccessKeyId=key_id)
                                last_used_info = key_last_used.get('AccessKeyLastUsed', {})
                                last_used_date = last_used_info.get('LastUsedDate')
                            except:
                                last_used_date = None
                            
                            # Consider key unused if never used or not used in 90+ days
                            is_unused = last_used_date is None or last_used_date < cutoff_date
                            
                            if is_unused:
                                security_risk = "High" if status == "Active" else "Low"
                                unused_access_keys.append({
                                    'key_id': key_id,
                                    'user_name': user_name,
                                    'status': status,
                                    'security_risk': security_risk
                                })
                                if security_risk == "High":
                                    high_risk_keys += 1
                    except Exception as e:
                        logger.warning(f"Could not check access keys for user {user_name}: {str(e)}")
                        continue
            
            access_keys_count = len(unused_access_keys)
            logger.info(f"Found {access_keys_count} unused access keys ({high_risk_keys} high risk)")
        except Exception as e:
            logger.error(f"Error fetching access keys: {str(e)}")
            access_keys_count = 0
            high_risk_keys = 0
            unused_access_keys = []
        
        # Use regional data for EC2 and EBS, use provided data for global resources
        resource_data = {
            'ec2_count': regional_data['ec2_count'],
            'ebs_count': regional_data['ebs_count'],
            'ec2_by_region': regional_data['ec2_by_region'],
            'ebs_by_region': regional_data['ebs_by_region'],
            's3_count': s3_count,
            'iam_users_count': iam_users_count,
            'access_keys_count': access_keys_count,
            'high_risk_keys': high_risk_keys
        }
        
        logger.info(f"Multi-region scan complete: {resource_data['ec2_count']} EC2 across {len(resource_data['ec2_by_region'])} regions, {resource_data['ebs_count']} EBS across {len(resource_data['ebs_by_region'])} regions")
        
        # Determine which channels to send to
        send_slack = channel is None or channel == 'slack'
        send_email = channel is None or channel == 'email'
        
        total_resources = resource_data['ec2_count'] + resource_data['ebs_count'] + resource_data['s3_count'] + resource_data['iam_users_count'] + resource_data['access_keys_count']
        
        # Send Slack notification
        if send_slack and slack_webhook:
            logger.info("Celery task: Sending Slack notification")
            message = f"🚨 Found {total_resources} unused AWS resources across multiple regions!"
            if resource_data.get('high_risk_keys', 0) > 0:
                message += f" ⚠️ {resource_data['high_risk_keys']} HIGH RISK access keys detected!"
            results['slack_sent'] = send_slack_notification(slack_webhook, message, resource_data)
        
        # Send Email notification
        if send_email and email_recipients and smtp_config.get('smtp_username'):
            logger.info("Celery task: Sending Email notification")
            results['email_sent'] = send_email_notification(
                email_recipients,
                f"☁️ Cloud Cleaner 🧹 Alert: {total_resources} Unused Resources Found",
                resource_data,
                smtp_config
            )
        
        logger.info(f"Celery task complete - Slack: {results['slack_sent']}, Email: {results['email_sent']}")
        return results
        
    except Exception as e:
        logger.error(f"Error in Celery task: {str(e)}")
        # Retry the task


@celery_app.task(bind=True, name="core.tasks.scheduled_scan_task")
def scheduled_scan_task(self: Task) -> Dict[str, Any]:
    """
    Scheduled task to scan all AWS resources and send notifications
    This task is triggered by Celery Beat based on the configured schedule
    
    Returns:
        Dictionary with scan results and notification status
    """
    try:
        logger.info("Starting scheduled scan of all AWS resources...")
        
        # Fetch EC2 and EBS data from all regions
        regional_data = fetch_all_regions_data()
        
        # Fetch S3 buckets (global) - only unused ones
        try:
            factory = get_aws_client_factory()
            s3_client = factory.session.client('s3')
            s3_response = s3_client.list_buckets()
            
            # Filter for unused buckets (same logic as /api/s3/unused)
            unused_s3_count = 0
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)
            
            for bucket in s3_response.get('Buckets', []):
                bucket_name = bucket.get('Name')
                creation_date = bucket.get('CreationDate')
                
                try:
                    # Check if bucket is empty
                    objects = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
                    is_empty = objects.get('KeyCount', 0) == 0
                    
                    # Consider bucket unused if it's old or empty
                    if creation_date < cutoff_date or is_empty:
                        unused_s3_count += 1
                except Exception as e:
                    logger.warning(f"Could not check bucket {bucket_name}: {str(e)}")
                    continue
            
            s3_count = unused_s3_count
            logger.info(f"Found {s3_count} unused S3 buckets")
        except Exception as e:
            logger.error(f"Error fetching S3 data: {str(e)}")
            s3_count = 0
        
        # Fetch IAM users (global)
        try:
            iam_client = factory.session.client('iam')
            iam_response = iam_client.list_users()
            iam_users_count = len(iam_response.get('Users', []))
        except Exception as e:
            logger.error(f"Error fetching IAM data: {str(e)}")
            iam_users_count = 0
        
        # Fetch unused access keys (global) - SECURITY CRITICAL
        try:
            paginator = iam_client.get_paginator('list_users')
            unused_access_keys = []
            high_risk_keys = 0
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)
            
            for page in paginator.paginate():
                for user in page.get('Users', []):
                    user_name = user.get('UserName')
                    try:
                        access_keys = iam_client.list_access_keys(UserName=user_name)
                        keys = access_keys.get('AccessKeyMetadata', [])
                        
                        for key in keys:
                            key_id = key.get('AccessKeyId')
                            status = key.get('Status')
                            
                            try:
                                key_last_used = iam_client.get_access_key_last_used(AccessKeyId=key_id)
                                last_used_info = key_last_used.get('AccessKeyLastUsed', {})
                                last_used_date = last_used_info.get('LastUsedDate')
                            except:
                                last_used_date = None
                            
                            # Consider key unused if never used or not used in 90+ days
                            is_unused = last_used_date is None or last_used_date < cutoff_date
                            
                            if is_unused:
                                security_risk = "High" if status == "Active" else "Low"
                                unused_access_keys.append({
                                    'key_id': key_id,
                                    'user_name': user_name,
                                    'status': status,
                                    'security_risk': security_risk
                                })
                                if security_risk == "High":
                                    high_risk_keys += 1
                    except Exception as e:
                        logger.warning(f"Could not check access keys for user {user_name}: {str(e)}")
                        continue
            
            access_keys_count = len(unused_access_keys)
            logger.info(f"Found {access_keys_count} unused access keys ({high_risk_keys} high risk)")
        except Exception as e:
            logger.error(f"Error fetching access keys: {str(e)}")
            access_keys_count = 0
            high_risk_keys = 0
            unused_access_keys = []
        
        # Prepare resource data
        resource_data = {
            'ec2_count': regional_data['ec2_count'],
            'ebs_count': regional_data['ebs_count'],
            'ec2_by_region': regional_data['ec2_by_region'],
            'ebs_by_region': regional_data['ebs_by_region'],
            's3_count': s3_count,
            'iam_users_count': iam_users_count,
            'access_keys_count': access_keys_count,
            'high_risk_keys': high_risk_keys
        }
        
        total_resources = resource_data['ec2_count'] + resource_data['ebs_count'] + resource_data['s3_count'] + resource_data['iam_users_count'] + resource_data['access_keys_count']
        
        logger.info(f"Scheduled scan complete: {total_resources} total resources found")
        
        # Get schedule settings from Redis
        from core.cache import get_redis_client
        redis_client = get_redis_client()
        
        channels_str = redis_client.get('schedule:channels')
        channels = channels_str.decode('utf-8').split(',') if channels_str else []
        
        results = {
            'scan_timestamp': datetime.now().isoformat(),
            'total_resources': total_resources,
            'resource_data': resource_data,
            'slack_sent': False,
            'email_sent': False
        }
        
        # Send notifications based on configured channels
        if 'slack' in channels and settings.slack_webhook_url:
            logger.info("Sending scheduled Slack notification")
            message = f"🚨 Found {total_resources} unused AWS resources across multiple regions!"
            if resource_data.get('high_risk_keys', 0) > 0:
                message += f" ⚠️ {resource_data['high_risk_keys']} HIGH RISK access keys detected!"
            results['slack_sent'] = send_slack_notification(settings.slack_webhook_url, message, resource_data)
        
        if 'email' in channels and settings.notification_email_recipients and settings.smtp_username:
            logger.info("Sending scheduled Email notification")
            email_recipients = [email.strip() for email in settings.notification_email_recipients.split(',')]
            smtp_config = {
                'smtp_server': settings.smtp_server,
                'smtp_port': settings.smtp_port,
                'smtp_username': settings.smtp_username,
                'smtp_password': settings.smtp_password,
                'sender_email': settings.sender_email
            }
            results['email_sent'] = send_email_notification(
                email_recipients,
                f"Cloud Cleaner Alert: {total_resources} Unused Resources Found",
                resource_data,
                smtp_config
            )
        
        # Store last scan timestamp in Redis
        redis_client.set('schedule:last_scan', datetime.now().isoformat())
        
        logger.info(f"Scheduled scan task complete - Slack: {results['slack_sent']}, Email: {results['email_sent']}")
        return results
        
    except Exception as e:
        logger.error(f"Error in scheduled scan task: {str(e)}")
        raise self.retry(exc=e, countdown=300)  # Retry after 5 minutes