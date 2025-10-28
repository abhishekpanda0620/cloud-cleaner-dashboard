# Scheduled Scanning

The Cloud Cleaner Dashboard supports automated scheduled scanning with Celery Beat for continuous monitoring of your AWS resources across all regions.

## Overview

Scheduled scanning allows you to automatically:
- Scan EC2 instances, EBS volumes, S3 buckets, and IAM resources across all AWS regions
- Send notifications via Slack and Email based on configured channels
- Monitor security risks like unused active access keys
- Track scan history and next scheduled runs

## Prerequisites

- **Redis Server**: Required for task queue and scheduling
- **Celery Worker**: Processes individual scan tasks
- **Celery Beat**: Background scheduler manages periodic scans
- **Configured AWS credentials**: With appropriate permissions

## Setup Instructions

### 1. Ensure Redis is Running

Redis is automatically included in Docker Compose setup:
```bash
docker-compose up -d
```

For local development:
```bash
# Ubuntu/Debian
sudo systemctl start redis

# macOS
brew services start redis

# Verify Redis is working
redis-cli ping  # Should return: PONG
```

### 2. Start Celery Services

In a new terminal (Terminal 2):
```bash
cd backend
./start_celery_worker.sh
```

In another terminal (Terminal 3):
```bash
cd backend
./start_celery_beat.sh
```

### 3. Configure Schedule via API

Use the Schedule Settings component in the dashboard or API endpoints:

```bash
# Enable daily scanning with Slack notifications
curl -X POST http://localhost:8084/api/schedule/config \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "frequency": "daily",
    "channels": ["slack"]
  }'
```

## Configuration Options

### Frequency Options
- **hourly**: Scan every hour
- **daily**: Scan once per day (default)
- **weekly**: Scan once per week
- **custom**: Custom interval in minutes

### Notification Channels
- **slack**: Send alerts to configured Slack webhook
- **email**: Send detailed HTML reports via email

### Example Configurations

#### Daily Slack Reports
```json
{
  "enabled": true,
  "frequency": "daily",
  "channels": ["slack"],
  "custom_interval": null
}
```

#### Weekly Email Summary
```json
{
  "enabled": true,
  "frequency": "weekly",
  "channels": ["email"],
  "custom_interval": null
}
```

#### Hourly Security Monitoring
```json
{
  "enabled": true,
  "frequency": "custom",
  "channels": ["slack", "email"],
  "custom_interval": 60
}
```

## API Endpoints

### Get Current Configuration
```http
GET /api/schedule/config
```

### Update Configuration
```http
POST /api/schedule/config
Content-Type: application/json

{
  "enabled": true,
  "frequency": "daily",
  "channels": ["slack"],
  "custom_interval": null
}
```

### Get Status Information
```http
GET /api/schedule/status
```

### Enable Scanning
```http
POST /api/schedule/enable
```

### Disable Scanning
```http
POST /api/schedule/disable
```

### Manual Trigger
```http
POST /api/schedule/trigger
```

## Scan Behavior

### Multi-Region Scanning
The scheduled scanner automatically:
- Scans all enabled AWS regions for EC2 and EBS resources
- Performs global checks for S3 buckets and IAM resources
- Aggregates results with regional breakdowns

### Security Monitoring
Access keys are categorized by risk:
- **High Risk**: Active unused access keys (potential security threat)
- **Low Risk**: Inactive unused access keys

### Notification Content

#### Slack Message Example
```
🚨 Found 25 unused AWS resources across multiple regions!

EC2 Instances:
• us-east-1: 8
• eu-west-1: 3
• ap-south-1: 2

EBS Volumes:
• us-east-1: 5
• eu-west-1: 2

S3 Buckets: 3
IAM Users: 2
Access Keys: 0 (0 High Risk)
```

#### Email Report
Detailed HTML email with:
- Resource breakdown by type and region
- Security risk assessment
- Estimated cost savings
- Professional formatting with charts and summaries

## Monitoring and Logs

### Check Celery Worker Logs
```bash
docker-compose logs -f celery-worker
```

### Check Celery Beat Logs
```bash
docker-compose logs -f celery-beat
```

### Check Schedule Status
```bash
curl http://localhost:8084/api/schedule/status
```

### View Redis Task Queue
```bash
redis-cli
> KEYS *
> GET redbeat:scheduled-scan
```

## Troubleshooting

### Common Issues

#### Redis Connection Error
**Symptom**: "Connection to Redis failed"
**Solution**: Ensure Redis is running and accessible
```bash
redis-cli ping
```

#### Celery Worker Not Processing Tasks
**Symptom**: Tasks stay in queue but aren't executed
**Solution**: Restart Celery worker with verbose logging
```bash
celery -A core.celery_app worker --loglevel=info
```

#### Schedule Not Triggering
**Symptom**: Scans aren't running automatically
**Solution**: Check Celery Beat is running and RedBeat scheduler is configured
```bash
# Check RedBeat entries
redis-cli KEYS redbeat:*
```

#### AWS API Rate Limiting
**Symptom**: Scan fails with throttling errors
**Solution**: Increase custom interval frequency or implement exponential backoff

### Debug Mode
Enable debug logging:
```bash
export DEBUG=true
celery -A core.celery_app worker --loglevel=debug
```

## Performance Considerations

### Resource Impact
- **Scan Duration**: Typically 2-5 minutes depending on account size
- **API Calls**: Cached to minimize AWS API usage
- **Memory Usage**: Minimal impact with Redis caching
- **Network**: Optimized regional aggregation

### Optimization Tips
- Use region-specific scans for large accounts
- Configure reasonable intervals (not too frequent)
- Monitor AWS API usage in CloudWatch
- Cache frequently accessed resource data

## Security Best Practices

1. **Credential Management**: Use IAM roles instead of access keys when possible
2. **Least Privilege**: Grant minimal required permissions
3. **Network Security**: Use VPC endpoints for AWS API calls
4. **Audit Logging**: Enable CloudTrail for all API actions
5. **Notification Security**: Secure webhook URLs and email configurations

## Integration Examples

### Slack Integration
```bash
# Test Slack notification
curl -X POST http://localhost:8084/api/notifications/send-alert \
  -H "Content-Type: application/json" \
  -d '{"channel": "slack"}'
```

### Email Integration
```bash
# Test email notification
curl -X POST http://localhost:8084/api/notifications/send-alert \
  -H "Content-Type: application/json" \
  -d '{"channel": "email"}'
```

### Custom Webhook Integration
```python
import requests
import json

# Trigger scan from external system
response = requests.post(
    'http://your-dashboard/api/schedule/trigger',
    headers={'Authorization': 'Bearer your-token'},
    json={'source': 'external-system'}
)