# Scheduled Scans Feature

This document describes the scheduled scans feature for the Cloud Cleaner Dashboard, which allows automatic periodic scanning of AWS resources with notifications.

## Overview

The scheduled scans feature enables users to:
- Configure automatic periodic scans of AWS resources
- Choose scan frequency (hourly, daily, weekly, or custom interval)
- Select notification channels (Slack and/or Email)
- View last and next scan times
- Manually trigger scans on demand
- Enable/disable scheduled scans with a toggle

## Architecture

### Backend Components

#### 1. Celery Beat Scheduler
- **Technology**: RedBeat (Redis-backed Celery Beat)
- **Container**: `celery-beat` service in docker-compose.yml
- **Purpose**: Manages scheduled task execution
- **Configuration**: Stores schedules in Redis for dynamic updates

#### 2. Scheduled Scan Task
- **File**: `backend/core/tasks.py`
- **Task Name**: `scheduled_scan_task`
- **Functionality**:
  - Scans all AWS regions for EC2 and EBS resources
  - Fetches global resources (S3, IAM)
  - Sends notifications to configured channels
  - Stores scan timestamp in Redis

#### 3. Schedule API Endpoints
- **File**: `backend/api/schedule.py`
- **Base Path**: `/api/schedule`

**Endpoints:**
- `GET /api/schedule/config` - Get current schedule configuration
- `POST /api/schedule/config` - Update schedule configuration
- `GET /api/schedule/status` - Get last/next scan times
- `POST /api/schedule/enable` - Enable scheduled scans
- `POST /api/schedule/disable` - Disable scheduled scans
- `POST /api/schedule/trigger` - Manually trigger a scan

#### 4. Redis Storage
**Keys used:**
- `schedule:enabled` - Boolean (true/false)
- `schedule:frequency` - String (hourly/daily/weekly/custom)
- `schedule:channels` - Comma-separated list (slack,email)
- `schedule:custom_interval` - Integer (minutes)
- `schedule:last_scan` - ISO timestamp

### Frontend Components

#### 1. ScheduleSettings Component
- **File**: `frontend/src/components/ScheduleSettings.tsx`
- **Location**: Dashboard page, below Alert Panel
- **Features**:
  - Toggle switch for enable/disable
  - Frequency dropdown (Hourly, Daily, Weekly, Custom)
  - Custom interval input (for custom frequency)
  - Notification channel checkboxes (Slack, Email)
  - Last scan and next scan display
  - Save settings button
  - Scan Now button for manual triggers

## Configuration

### Environment Variables

No additional environment variables are required. The feature uses existing notification configuration:
- `SLACK_WEBHOOK_URL` - For Slack notifications
- `NOTIFICATION_EMAIL_RECIPIENTS` - For email notifications
- `SMTP_*` - For email server configuration

### Docker Compose

The `celery-beat` service has been added to `docker-compose.yml`:

```yaml
celery-beat:
  build:
    context: ./backend
    dockerfile: Dockerfile
  container_name: cloud-cleaner-celery-beat
  command: celery -A core.celery_app beat --loglevel=info --scheduler redbeat.RedBeatScheduler
  environment:
    # Same environment variables as backend and celery-worker
  depends_on:
    redis:
      condition: service_healthy
```

### Dependencies

**Backend:**
- `celery-redbeat==2.2.0` - Redis-backed Celery Beat scheduler

**Frontend:**
- `lucide-react==^0.468.0` - Icon library for UI components

## Usage

### 1. Enable Scheduled Scans

1. Navigate to the dashboard
2. Locate the "Schedule Settings" section below the Alert Panel
3. Toggle the switch to enable scheduled scans
4. Select your desired frequency
5. Choose notification channels (Slack and/or Email)
6. Click "Save Settings"

### 2. Configure Scan Frequency

**Available Options:**
- **Hourly**: Scans every hour
- **Daily**: Scans once per day
- **Weekly**: Scans once per week
- **Custom**: Specify interval in minutes (e.g., 30 for every 30 minutes)

### 3. Notification Channels

**Slack:**
- Requires `SLACK_WEBHOOK_URL` to be configured
- Sends formatted messages with resource breakdown by region
- Includes potential savings calculation

**Email:**
- Requires SMTP configuration and `NOTIFICATION_EMAIL_RECIPIENTS`
- Sends HTML-formatted email with detailed resource information
- Includes regional breakdown for EC2 and EBS

### 4. Manual Scan Trigger

Click the "Scan Now" button to immediately trigger a scan without waiting for the scheduled time.

### 5. Monitor Scan Status

The Schedule Settings panel displays:
- **Last Scan**: Timestamp of the most recent scan
- **Next Scan**: Calculated time for the next scheduled scan
- **Status**: Whether scheduled scans are enabled or disabled

## API Examples

### Get Current Configuration

```bash
curl http://localhost:8084/api/schedule/config
```

Response:
```json
{
  "enabled": true,
  "frequency": "daily",
  "channels": ["slack", "email"],
  "custom_interval": null
}
```

### Update Configuration

```bash
curl -X POST http://localhost:8084/api/schedule/config \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "frequency": "hourly",
    "channels": ["slack"],
    "custom_interval": null
  }'
```

### Get Schedule Status

```bash
curl http://localhost:8084/api/schedule/status
```

Response:
```json
{
  "enabled": true,
  "frequency": "daily",
  "channels": ["slack", "email"],
  "last_scan": "2025-10-26T12:00:00",
  "next_scan": "2025-10-27T12:00:00"
}
```

### Trigger Manual Scan

```bash
curl -X POST http://localhost:8084/api/schedule/trigger
```

Response:
```json
{
  "message": "Scan triggered successfully",
  "task_id": "abc123-def456-ghi789"
}
```

## Deployment

### Starting the Services

```bash
# Build and start all services including celery-beat
docker-compose up -d

# View celery-beat logs
docker-compose logs -f celery-beat

# Restart celery-beat after configuration changes
docker-compose restart celery-beat
```

### Verifying Operation

1. Check celery-beat logs for schedule registration:
```bash
docker-compose logs celery-beat | grep "scheduled-scan"
```

2. Monitor task execution in celery-worker logs:
```bash
docker-compose logs -f celery-worker | grep "scheduled_scan_task"
```

3. Check Redis for schedule data:
```bash
docker-compose exec redis redis-cli
> GET schedule:enabled
> GET schedule:frequency
> GET schedule:last_scan
```

## Troubleshooting

### Schedule Not Running

1. **Check if celery-beat is running:**
```bash
docker-compose ps celery-beat
```

2. **Verify Redis connection:**
```bash
docker-compose logs celery-beat | grep -i redis
```

3. **Check schedule entry in Redis:**
```bash
docker-compose exec redis redis-cli KEYS "redbeat:*"
```

### Notifications Not Sending

1. **Verify notification configuration:**
   - Check `SLACK_WEBHOOK_URL` for Slack
   - Check SMTP settings for Email

2. **Check selected channels in schedule config:**
```bash
curl http://localhost:8084/api/schedule/config
```

3. **Review task logs:**
```bash
docker-compose logs celery-worker | grep "scheduled_scan_task"
```

### Schedule Not Updating

1. **Restart celery-beat after major changes:**
```bash
docker-compose restart celery-beat
```

2. **Clear Redis schedule data if needed:**
```bash
docker-compose exec redis redis-cli DEL "redbeat:scheduled-scan"
```

3. **Re-save configuration from UI**

## Technical Details

### Dynamic Schedule Updates

The feature uses RedBeat, which stores schedules in Redis. This allows:
- Dynamic schedule updates without restarting services
- Persistent schedules across container restarts
- Real-time schedule modifications from the API

### Scan Process

1. **Resource Discovery**: Scans all enabled AWS regions
2. **Data Collection**: Gathers EC2, EBS, S3, and IAM data
3. **Aggregation**: Combines regional and global resource counts
4. **Notification**: Sends to configured channels
5. **Storage**: Updates last scan timestamp in Redis

### Performance Considerations

- Scans run asynchronously in Celery workers
- Regional scans are performed sequentially to avoid rate limits
- Failed region scans don't block the entire process
- Task has 5-minute timeout with retry logic

## Future Enhancements

Potential improvements for future versions:
- Custom notification templates
- Scan result history and trends
- Resource-specific scan schedules
- Webhook support for custom integrations
- Scan result comparison and change detection
- Cost trend analysis over time
- Multi-account support
- Scan filtering by resource type or tags

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review container logs for error messages
3. Verify AWS credentials and permissions
4. Ensure Redis is running and accessible
5. Check notification channel configurations