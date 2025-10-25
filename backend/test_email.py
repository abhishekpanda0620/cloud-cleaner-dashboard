#!/usr/bin/env python3
"""
Test script to verify email configuration and Celery task execution
Usage: python test_email.py
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_config():
    """Test email configuration"""
    print("=== Testing Email Configuration ===\n")
    
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = os.getenv("SMTP_PORT", "587")
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender_email = os.getenv("SENDER_EMAIL")
    recipients = os.getenv("NOTIFICATION_EMAIL_RECIPIENTS", "").split(",")
    
    print(f"SMTP Server: {smtp_server}")
    print(f"SMTP Port: {smtp_port}")
    print(f"SMTP Username: {'✓ Set' if smtp_username else '✗ Not Set'}")
    print(f"SMTP Password: {'✓ Set' if smtp_password else '✗ Not Set'}")
    print(f"Sender Email: {sender_email or 'noreply@cloudcleaner.local'}")
    print(f"Recipients: {recipients if recipients[0] else '✗ Not Set'}")
    
    if not smtp_username or not smtp_password:
        print("\n❌ Email configuration incomplete!")
        print("Please set SMTP_USERNAME and SMTP_PASSWORD in .env file")
        return False
    
    if not recipients[0]:
        print("\n❌ No email recipients configured!")
        print("Please set NOTIFICATION_EMAIL_RECIPIENTS in .env file")
        return False
    
    print("\n✓ Email configuration looks good!")
    return True


def test_celery_connection():
    """Test Celery and Redis connection"""
    print("\n=== Testing Celery Connection ===\n")
    
    try:
        from core.celery_app import celery_app
        
        # Check if Celery can connect to broker
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        
        if stats:
            print(f"✓ Connected to Celery broker")
            print(f"✓ Active workers: {len(stats)}")
            for worker_name in stats.keys():
                print(f"  - {worker_name}")
            return True
        else:
            print("❌ No active Celery workers found!")
            print("\nTo start a worker, run:")
            print("  celery -A core.celery_app worker --loglevel=info")
            return False
            
    except Exception as e:
        print(f"❌ Failed to connect to Celery: {str(e)}")
        print("\nMake sure Redis is running:")
        print("  redis-server")
        return False


def test_send_email():
    """Test sending an actual email via Celery"""
    print("\n=== Testing Email Send via Celery ===\n")
    
    try:
        from core.tasks import send_alert_task
        from core.config import settings
        
        recipients = os.getenv("NOTIFICATION_EMAIL_RECIPIENTS", "").split(",")
        recipients = [r.strip() for r in recipients if r.strip()]
        
        if not recipients:
            print("❌ No recipients configured")
            return False
        
        smtp_config = {
            'smtp_server': os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            'smtp_port': int(os.getenv("SMTP_PORT", "587")),
            'smtp_username': os.getenv("SMTP_USERNAME"),
            'smtp_password': os.getenv("SMTP_PASSWORD"),
            'sender_email': os.getenv("SENDER_EMAIL", "noreply@cloudcleaner.local")
        }
        
        print(f"Queueing test email to: {', '.join(recipients)}")
        
        # Queue the task
        task = send_alert_task.delay(
            channel='email',
            s3_count=5,
            iam_users_count=3,
            slack_webhook=None,
            email_recipients=recipients,
            smtp_config=smtp_config
        )
        
        print(f"✓ Task queued with ID: {task.id}")
        print(f"\nTask status: {task.status}")
        
        # Wait a bit and check status
        import time
        print("\nWaiting for task to complete...")
        for i in range(10):
            time.sleep(1)
            task_status = task.status
            print(f"  [{i+1}/10] Status: {task_status}")
            
            if task_status in ['SUCCESS', 'FAILURE']:
                break
        
        if task.status == 'SUCCESS':
            result = task.result
            print(f"\n✓ Task completed successfully!")
            print(f"  Email sent: {result.get('email_sent', False)}")
            return True
        elif task.status == 'FAILURE':
            print(f"\n❌ Task failed!")
            print(f"  Error: {task.info}")
            return False
        else:
            print(f"\n⚠ Task still pending/running")
            print(f"  Check Celery worker logs for details")
            print(f"  Task ID: {task.id}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Cloud Cleaner - Email & Celery Test\n")
    print("=" * 50)
    
    # Test email config
    email_ok = test_email_config()
    
    # Test Celery connection
    celery_ok = test_celery_connection()
    
    # If both are OK, offer to send test email
    if email_ok and celery_ok:
        print("\n" + "=" * 50)
        response = input("\nDo you want to send a test email? (y/n): ")
        if response.lower() == 'y':
            test_send_email()
    else:
        print("\n" + "=" * 50)
        print("\n❌ Please fix the issues above before testing email send")
        sys.exit(1)