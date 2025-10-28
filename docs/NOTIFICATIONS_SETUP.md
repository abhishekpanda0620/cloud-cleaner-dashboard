# Cloud Cleaner Dashboard - Notifications Setup Guide

This guide explains how to configure Slack and Email notifications for the Cloud Cleaner Dashboard.

## Overview

The Cloud Cleaner Dashboard supports two notification channels:
- **Slack**: Real-time alerts to your Slack workspace
- **Email**: Detailed HTML email reports

## Slack Notifications Setup

### Step 1: Create a Slack Webhook

1. Go to your Slack workspace
2. Navigate to [Slack Apps](https://api.slack.com/apps)
3. Click "Create New App" → "From scratch"
4. Name your app (e.g., "Cloud Cleaner")
5. Select your workspace
6. Go to "Incoming Webhooks" in the left menu
7. Toggle "Activate Incoming Webhooks" to ON
8. Click "Add New Webhook to Workspace"
9. Select the channel where you want notifications
10. Copy the Webhook URL

### Step 2: Configure Environment Variable

Add the webhook URL to your `.env` file or docker-compose:

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Example Slack Notification

```
☁️ Cloud Cleaner Alert

🚨 Found 15 unused AWS resources! Potential savings: $150.00/month

🖥️ EC2 Instances: 5
💾 EBS Volumes: 3
🪣 S3 Buckets: 4
👥 IAM Users: 3

💰 Potential Savings: $150.00/month

Generated at 2025-10-20 05:45:00 UTC
```

## Email Notifications Setup

### Step 1: Configure SMTP Server

You can use any SMTP server. Here are popular options:

#### Gmail (Recommended for testing)

1. Enable 2-Factor Authentication on your Google Account
2. Generate an [App Password](https://myaccount.google.com/apppasswords)
3. Use these credentials:

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com
```

#### Office 365

```bash
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=your-email@company.com
SMTP_PASSWORD=your-password
SENDER_EMAIL=your-email@company.com
```

#### SendGrid

```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=SG.your-sendgrid-api-key
SENDER_EMAIL=your-email@company.com
```

### Step 2: Configure Recipients

Add email recipients to your `.env` file:

```bash
NOTIFICATION_EMAIL_RECIPIENTS=admin@company.com,devops@company.com,finance@company.com
```

### Step 3: Complete Environment Configuration

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com
NOTIFICATION_EMAIL_RECIPIENTS=recipient1@company.com,recipient2@company.com
```

## Docker Compose Configuration

Update your `docker-compose.yml` or `.env` file with all notification variables:

```yaml
environment:
  # Slack
  - SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
  
  # Email
  - NOTIFICATION_EMAIL_RECIPIENTS=${NOTIFICATION_EMAIL_RECIPIENTS}
  - SMTP_SERVER=${SMTP_SERVER:-smtp.gmail.com}
  - SMTP_PORT=${SMTP_PORT:-587}
  - SMTP_USERNAME=${SMTP_USERNAME}
  - SMTP_PASSWORD=${SMTP_PASSWORD}
  - SENDER_EMAIL=${SENDER_EMAIL}
```

## API Endpoints

### Send Alert

**Endpoint:** `POST /api/notifications/send-alert`

**Request Body:**
```json
{
  "resource_type": "unused_resources",
  "count": 15,
  "estimated_savings": 150.00,
  "details": {
    "ec2_count": 5,
    "ebs_count": 3,
    "s3_count": 4,
    "iam_users_count": 3
  }
}
```

**Response:**
```json
{
  "slack_sent": true,
  "email_sent": true,
  "message": "Alert sent"
}
```

### Get Configuration Status

**Endpoint:** `GET /api/notifications/config`

**Response:**
```json
{
  "slack_configured": true,
  "email_configured": true,
  "email_recipients": ["admin@company.com", "devops@company.com"]
}
```

## Complete .env Example

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=ap-south-1

# Server Configuration
PORT=8084
HOST=0.0.0.0
DEBUG=false

# Slack Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Email Notifications
NOTIFICATION_EMAIL_RECIPIENTS=admin@company.com,devops@company.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com
```

## Testing Notifications

### Test Slack Notification

```bash
curl -X POST http://localhost:8084/api/notifications/send-alert \
  -H "Content-Type: application/json" \
  -d '{
    "resource_type": "unused_resources",
    "count": 10,
    "estimated_savings": 100.00,
    "details": {
      "ec2_count": 3,
      "ebs_count": 2,
      "s3_count": 3,
      "iam_users_count": 2
    }
  }'
```

### Check Configuration

```bash
curl http://localhost:8084/api/notifications/config
```

## Troubleshooting

### Alert Panel Issues

#### Issue: "Failed to send Slack notification. Please check SLACK_WEBHOOK_URL configuration."

**Possible Causes:**

1. **Environment Variable Not Set**
   ```bash
   # Check if variable is set
   docker-compose exec backend env | grep SLACK_WEBHOOK_URL
   ```
   - Solution: Add to `.env` file and restart backend

2. **Backend Not Restarted**
   - Solution: Restart the backend service:
     ```bash
     docker-compose restart backend
     ```

3. **Invalid Webhook URL**
   - Verify format: `https://hooks.slack.com/services/YOUR/WEBHOOK/URL`
   - Solution: Regenerate webhook in Slack workspace settings

4. **Network Connectivity**
   - Solution: Check firewall rules and network connectivity

#### Issue: "Failed to send Email notification. Please check SMTP and email recipient configuration."

**Possible Causes:**

1. **Missing SMTP Credentials**
   ```bash
   # Check SMTP settings
   docker-compose exec backend env | grep SMTP
   docker-compose exec backend env | grep NOTIFICATION_EMAIL
   ```
   - Solution: Configure all SMTP variables in `.env`

2. **Invalid Credentials**
   - For Gmail: Use App Password, not regular password
   - Solution: Regenerate App Password and update `.env`

3. **Missing Email Recipients**
   - Solution: Set `NOTIFICATION_EMAIL_RECIPIENTS` in `.env`

4. **SMTP Port Blocked**
   - Solution: Check firewall allows port 587 (or 465 for SSL)

### Slack Notifications Not Sending

1. Verify webhook URL is correct
2. Check if `SLACK_WEBHOOK_URL` environment variable is set
3. Ensure webhook URL is still valid (regenerate if needed)
4. Check backend logs: `docker-compose logs backend`

### Email Notifications Not Sending

1. Verify SMTP credentials are correct
2. Check if port 587 is accessible (firewall issues)
3. For Gmail: Ensure App Password is used (not regular password)
4. Verify email recipients are valid
5. Check backend logs: `docker-compose logs backend`

### Common Errors

**"Failed to send Slack notification"**
- Invalid webhook URL
- Network connectivity issue
- Slack service temporarily unavailable
- `SLACK_WEBHOOK_URL` environment variable not loaded

**"Failed to send email notification"**
- Invalid SMTP credentials
- SMTP server unreachable
- Invalid email addresses
- SMTP port blocked by firewall
- Missing `NOTIFICATION_EMAIL_RECIPIENTS`

## Debugging Steps

### Step 1: Check Backend Logs

```bash
# View recent logs
docker-compose logs backend | tail -50

# Follow logs in real-time
docker-compose logs -f backend
```

Look for messages like:
- `Alert request - Channel: slack, Slack configured: True`
- `Sending Slack notification to webhook`
- `Slack notification sent successfully`

### Step 2: Verify Environment Variables

```bash
# Check all notification variables
docker-compose exec backend env | grep -E 'SLACK|SMTP|NOTIFICATION|EMAIL'
```

### Step 3: Test Configuration Endpoint

```bash
# Check notification configuration status
curl http://localhost:8084/api/notifications/config
```

Expected response:
```json
{
  "slack_configured": true,
  "email_configured": true,
  "email_recipients": ["admin@company.com"]
}
```

### Step 4: Manual API Test

**Test Slack (with channel parameter):**
```bash
curl -X POST http://localhost:8084/api/notifications/send-alert \
  -H "Content-Type: application/json" \
  -d '{
    "resource_type": "unused_resources",
    "count": 5,
    "estimated_savings": 250.00,
    "channel": "slack",
    "details": {
      "ec2_count": 2,
      "ebs_count": 1,
      "s3_count": 2,
      "iam_users_count": 0,
      "access_keys_count": 0,
      "total_savings": 250.00
    }
  }'
```

**Test Email (with channel parameter):**
```bash
curl -X POST http://localhost:8084/api/notifications/send-alert \
  -H "Content-Type: application/json" \
  -d '{
    "resource_type": "unused_resources",
    "count": 5,
    "estimated_savings": 250.00,
    "channel": "email",
    "details": {
      "ec2_count": 2,
      "ebs_count": 1,
      "s3_count": 2,
      "iam_users_count": 0,
      "access_keys_count": 0,
      "total_savings": 250.00
    }
  }'
```

### Step 5: Restart Backend After Configuration Changes

```bash
# Restart backend to reload environment variables
docker-compose restart backend

# Or rebuild and restart
docker-compose down
docker-compose up -d --build
```

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** for all sensitive data
3. **Use App Passwords** instead of main passwords (Gmail)
4. **Restrict webhook access** in Slack (use specific channels)
5. **Use TLS/SSL** for SMTP connections (port 587)
6. **Rotate credentials** regularly
7. **Monitor notification logs** for suspicious activity

## Automation

To send notifications automatically when resources are detected:

1. Set up a scheduled task (cron job or Lambda)
2. Call the `/api/notifications/send-alert` endpoint
3. Include resource data from the dashboard APIs

Example cron job:

```bash
# Send daily report at 9 AM
0 9 * * * curl -X POST http://localhost:8084/api/notifications/send-alert \
  -H "Content-Type: application/json" \
  -d '{"resource_type":"unused_resources","count":0,"estimated_savings":0,"details":{}}'
```

## Support

For issues or questions:
1. Check the logs: `docker-compose logs backend`
2. Verify environment variables are set correctly
3. Test SMTP/Slack connectivity manually
4. Review this guide for configuration examples

## Additional Notification Options

While the Cloud Cleaner Dashboard currently supports Slack and Email, here are other notification services that can be easily integrated:

### Chat Platforms
- **Microsoft Teams**: Similar to Slack, with webhook support
- **Discord**: Community-friendly notifications with webhooks
- **Telegram**: Bot-based notifications
- **Mattermost**: Self-hosted Slack alternative

### SMS & Phone
- **Twilio**: Send SMS alerts to team members
- **AWS SNS**: Native AWS service for SMS and push notifications
- **Nexmo/Vonage**: Global SMS delivery

### Incident Management
- **PagerDuty**: Alert critical unused resources
- **Opsgenie**: On-call management and escalation
- **Incident.io**: Incident response platform

### Monitoring & Logging
- **Datadog**: Centralized monitoring and alerts
- **New Relic**: Application performance monitoring
- **CloudWatch**: AWS native monitoring
- **Splunk**: Log aggregation and analysis

### Webhooks & Automation
- **Zapier**: Connect to 5000+ apps
- **IFTTT**: If This Then That automation
- **Make (formerly Integromat)**: Advanced automation

### How to Add Custom Notifications

To add a new notification channel to Cloud Cleaner:

1. **Add configuration** to `backend/core/config.py`:
   ```python
   custom_webhook_url: Optional[str] = None
   ```

2. **Create notification function** in `backend/api/notifications.py`:
   ```python
   def send_custom_notification(webhook_url: str, message: str, resource_data: Dict) -> bool:
       try:
           # Your implementation here
           return True
       except Exception as e:
           logger.error(f"Failed to send custom notification: {str(e)}")
           return False
   ```

3. **Update send_alert endpoint** to support the new channel

4. **Update frontend** to add button for new channel

5. **Test thoroughly** before deploying

## References

- [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)
- [SMTP Configuration Guide](https://en.wikipedia.org/wiki/Simple_Mail_Transfer_Protocol)
- [Discord Webhooks](https://discord.com/developers/docs/resources/webhook)
- [Twilio SMS API](https://www.twilio.com/sms)
- [AWS SNS](https://aws.amazon.com/sns/)