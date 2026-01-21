import logging
import smtplib
import json
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
from core.config import settings

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def get_email_template(title: str, content_data: Dict[str, Any], scan_summary: str) -> str:
        """
        Generates a premium, responsive HTML email template.
        """
        
        # Extract data for cards
        total_resources = content_data.get('total_resources', 0)
        
        # Counts
        s3_count = content_data.get('s3_count', 0)
        iam_count = content_data.get('iam_users_count', 0)
        key_count = content_data.get('access_keys_count', 0)
        high_risk_keys = content_data.get('high_risk_keys', 0)
        
        ec2_count = content_data.get('ec2_count', 0)
        ebs_count = content_data.get('ebs_count', 0)
        rds_count = content_data.get('rds_count', 0) # Assumed based on scanner types
        lambda_count = content_data.get('lambda_count', 0)
        
        # Determine status color based on high risk items
        status_color = "#ef4444" if high_risk_keys > 0 else "#22c55e"
        header_bg = "#0f172a" 
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{ margin: 0; padding: 0; background-color: #f1f5f9; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin-top: 40px; margin-bottom: 40px; }}
                .header {{ background-color: {header_bg}; padding: 32px; text-align: center; }}
                .logo-text {{ color: #ffffff; font-size: 24px; font-weight: 700; letter-spacing: -0.5px; margin: 0; }}
                .hero {{ padding: 40px 32px; text-align: center; border-bottom: 1px solid #e2e8f0; }}
                .hero h1 {{ color: #1e293b; font-size: 28px; margin: 0 0 12px 0; font-weight: 800; }}
                .hero p {{ color: #64748b; font-size: 16px; margin: 0; line-height: 1.5; }}
                .grid {{ padding: 32px; display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
                .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; text-align: left; }}
                .card-label {{ color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; margin-bottom: 8px; }}
                .card-value {{ color: #0f172a; font-size: 24px; font-weight: 700; }}
                .card-sub {{ font-size: 13px; margin-top: 4px; display: flex; align-items: center; gap: 6px; }}
                .footer {{ background-color: #f8fafc; padding: 24px; text-align: center; border-top: 1px solid #e2e8f0; }}
                .footer p {{ color: #94a3b8; font-size: 12px; margin: 0; }}
                
                .resource-row {{ display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #f1f5f9; }}
                .resource-row:last-child {{ border-bottom: none; }}
                .resource-name {{ color: #475569; font-weight: 600; font-size: 14px; }}
                .resource-count {{ color: #0f172a; font-weight: 700; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo-text">☁️ Cloud Cleaner</div>
                </div>
                
                <div class="hero">
                    <h1>Scan Complete</h1>
                    <p>{scan_summary}</p>
                    <a href="{settings.frontend_url}" style="display: inline-block; background-color: #2563eb; color: #ffffff !important; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: 600; font-size: 14px; margin-top: 24px;">View Dashboard</a>
                </div>
                
                <div style="padding: 32px;">
                    <div style="margin-bottom: 24px;">
                        <span style="font-size: 14px; font-weight: 700; color: #334155; text-transform: uppercase; letter-spacing: 1px;">Resource Breakdown</span>
                    </div>
                    
                    <div style="background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; padding: 0 20px;">
                        <!-- Compute -->
                        <div class="resource-row">
                            <span class="resource-name">Compute (EC2)</span>
                            <span class="resource-count">{ec2_count}</span>
                        </div>
                        <!-- Storage -->
                        <div class="resource-row">
                            <span class="resource-name">Storage (EBS)</span>
                            <span class="resource-count">{ebs_count}</span>
                        </div>
                         <!-- S3 -->
                        <div class="resource-row">
                            <span class="resource-name">Storage (S3)</span>
                            <span class="resource-count">{s3_count}</span>
                        </div>
                        <!-- DB -->
                        <div class="resource-row">
                            <span class="resource-name">Database (RDS)</span>
                            <span class="resource-count">{rds_count}</span>
                        </div>
                        <!-- Lambda -->
                        <div class="resource-row">
                            <span class="resource-name">Serverless (Lambda)</span>
                            <span class="resource-count">{lambda_count}</span>
                        </div>
                         <!-- IAM -->
                        <div class="resource-row">
                            <span class="resource-name">Identity (IAM Users/Keys)</span>
                            <span class="resource-count">{iam_count + key_count}</span>
                        </div>
                    </div>

                    <!-- Risk Badge -->
                     <div style="margin-top: 24px; text-align: center;">
                        {
                            f'<span style="display: inline-block; padding: 4px 12px; border-radius: 99px; font-size: 12px; font-weight: 600; background: #fee2e2; color: #ef4444; border: 1px solid #fecaca;">⚠️ {high_risk_keys} High Risk IAM Keys</span>' 
                            if high_risk_keys > 0 
                            else '<span style="display: inline-block; padding: 4px 12px; border-radius: 99px; font-size: 12px; font-weight: 600; background: #dcfce7; color: #166534; border: 1px solid #bbf7d0;">✅ Identity Security: Safe</span>'
                        }
                    </div>
                    
                    <div style="margin-top: 32px; text-align: center; color: #64748b; font-size: 13px; line-height: 1.6;">
                        This report was generated automatically based on your scheduled scan configurations.<br>
                        Cloud Cleaner helps you identify and remove unused AWS resources to reduce costs and security risks.
                    </div>
                </div>

                <div class="footer">
                    <p>&copy; 2026 Cloud Cleaner Dashboard. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    @staticmethod
    def send_email_notification(subject: str, content_data: Dict[str, Any], recipients: List[str]) -> bool:
        """
        Sends an email notification with the premium HTML template.
        """
        if not recipients:
            return False

        smtp_config = {
            'smtp_server': settings.smtp_server,
            'smtp_port': settings.smtp_port,
            'smtp_username': settings.smtp_username,
            'smtp_password': settings.smtp_password,
            'sender_email': settings.sender_email
        }

        # Validate config
        if not all([smtp_config['smtp_server'], smtp_config['smtp_username'], smtp_config['smtp_password']]):
            logger.warning("SMTP configuration incomplete. Skipping email.")
            return False

        try:
            total_waste = content_data.get('total_resources', 0)
            scan_summary = f"Found {total_waste} potential unused resources."
            
            html_email = NotificationService.get_email_template("Scan Report", content_data, scan_summary)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = smtp_config.get('sender_email', 'noreply@cloudcleaner.local')
            msg['To'] = ', '.join(recipients)
            
            # Attach HTML
            msg.attach(MIMEText(html_email, 'html'))
            
            # Send
            with smtplib.SMTP(smtp_config.get('smtp_server'), smtp_config.get('smtp_port', 587)) as server:
                server.starttls()
                server.login(smtp_config.get('smtp_username'), smtp_config.get('smtp_password'))
                server.send_message(msg)
            
            logger.info(f"Email notification sent to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            return False

    @staticmethod
    def send_budget_alert(current_cost: float, limit: float, recipients: List[str]) -> bool:
        """
        Sends a specific budget exceeded alert.
        """
        if not recipients:
            return False

        subject = f"🚨 Budget Alert: ${current_cost:.2f} exceeds limit of ${limit:.2f}"
        
        # Simple HTML for budget alert
        html = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: sans-serif; background: #f1f5f9; padding: 40px;">
            <div style="max-width: 600px; margin: 0 auto; background: #fff; padding: 32px; border-radius: 8px; border-left: 6px solid #ef4444;">
                <h1 style="color: #ef4444; margin-top: 0;">Budget Threshold Exceeded</h1>
                <p style="font-size: 16px; color: #334155;">Your estimated AWS costs have exceeded your configured budget.</p>
                <div style="background: #fee2e2; padding: 24px; border-radius: 6px; margin: 24px 0; text-align: center;">
                    <div style="font-size: 14px; text-transform: uppercase; color: #991b1b; font-weight: bold;">Current Costs</div>
                    <div style="font-size: 36px; font-weight: 800; color: #7f1d1d;">${current_cost:.2f}</div>
                    <div style="font-size: 14px; color: #ef4444; margin-top: 8px;">Limit: ${limit:.2f}</div>
                </div>
                <a href="{settings.frontend_url}" style="display: inline-block; background: #ef4444; color: #fff; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">View Details</a>
            </div>
        </body>
        </html>
        """
        
        return NotificationService.send_email_by_smtp(subject, html, recipients)

    @staticmethod
    def send_email_by_smtp(subject: str, html_content: str, recipients: List[str]) -> bool:
        """Helper to send SMTP email"""
        smtp_config = {
            'smtp_server': settings.smtp_server,
            'smtp_port': settings.smtp_port,
            'smtp_username': settings.smtp_username,
            'smtp_password': settings.smtp_password,
            'sender_email': settings.sender_email
        }
        
        if not all([smtp_config['smtp_server'], smtp_config['smtp_username'], smtp_config['smtp_password']]):
            return False
            
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = smtp_config.get('sender_email', 'noreply@cloudcleaner.local')
            msg['To'] = ', '.join(recipients)
            msg.attach(MIMEText(html_content, 'html'))
            
            with smtplib.SMTP(smtp_config.get('smtp_server'), smtp_config.get('smtp_port', 587)) as server:
                server.starttls()
                server.login(smtp_config.get('smtp_username'), smtp_config.get('smtp_password'))
                server.send_message(msg)
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
