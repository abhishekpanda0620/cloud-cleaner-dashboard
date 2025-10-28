# Configuration Guide

This guide covers all configuration options for the Cloud Cleaner Dashboard.

## Environment Variables

### Backend Configuration

Create a `.env` file in the `backend/` directory:

```env
# AWS Configuration (Required)
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_REGION=ap-south-1

# Server Configuration
HOST=0.0.0.0
PORT=8084
APP_NAME="Cloud Cleaner Dashboard"
DEBUG=false

# Redis Configuration (Required for scheduled scanning)
REDIS_URL=redis://localhost:6379/0

# Slack Notifications (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Email Notifications (Optional)
NOTIFICATION_EMAIL_RECIPIENTS=admin@company.com,devops@company.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com
```

### Frontend Configuration

Create a `.env.local` file in the `frontend/` directory:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8084/api

# Development
NEXT_PUBLIC_APP_NAME="Cloud Cleaner Dashboard"
NEXT_PUBLIC_DEBUG=true
```

### Docker Configuration

Root `.env` file for docker-compose:

```env
# AWS Configuration
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_REGION=ap-south-1

# Slack Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Email Notifications
NOTIFICATION_EMAIL_RECIPIENTS=admin@company.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com

# Database
POSTGRES_DB=cloudcleaner
POSTGRES_USER=cloudcleaner
POSTGRES_PASSWORD=secure-password

# Redis
REDIS_PASSWORD=redis-password
```

## AWS Configuration

### Required Permissions

Your AWS user/role needs the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeVolumes",
        "s3:ListAllMyBuckets",
        "s3:GetBucketLocation",
        "s3:ListBucket",
        "iam:ListRoles",
        "iam:GetRole",
        "iam:ListUsers",
        "iam:ListAccessKeys",
        "iam:GetAccessKeyLastUsed"
      ],
      "Resource": "*"
    }
  ]
}
```

### Security Best Practices

1. **Use IAM Roles**: Prefer IAM roles over access keys when running on EC2
2. **Principle of Least Privilege**: Grant only required permissions
3. **Regular Rotation**: Rotate access keys regularly
4. **MFA**: Enable Multi-Factor Authentication for AWS console access

### Regional Configuration

The application scans across all enabled regions by default. You can specify a default region:

```env
AWS_REGION=us-east-1
```

## Notification Configuration

### Slack Integration

#### 1. Create Slack App
1. Go to [Slack API](https://api.slack.com/apps)
2. Click "Create New App"
3. Choose "From scratch"
4. Give your app a name and select workspace

#### 2. Configure Incoming Webhooks
1. Go to "Incoming Webhooks" in app settings
2. Turn on "Activate Incoming Webhooks"
3. Click "Add New Webhook to Workspace"
4. Select channel and authorize

#### 3. Set Environment Variable


#### 4. Test Configuration
```bash
curl -X POST http://localhost:8084/api/notifications/send-alert \
  -H "Content-Type: application/json" \
  -d '{"channel": "slack"}'
```

### Email Configuration

#### Gmail Setup
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com
```

**Important**: Use App Passwords, not your regular Gmail password.

#### Office 365 Setup
```env
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=your-email@company.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@company.com
```

#### SendGrid Setup
```env
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SENDER_EMAIL=noreply@yourdomain.com
```

### Email Recipients

Configure multiple recipients:

```env
NOTIFICATION_EMAIL_RECIPIENTS=admin@company.com,devops@company.com,security@company.com
```

## Redis Configuration

### Local Redis Setup

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Docker:**
```bash
docker run -d -p 6379:6379 redis:alpine
```

### Redis Security

For production, secure your Redis instance:

```env
# Require authentication
REDIS_PASSWORD=your-secure-password

# Bind to localhost only
REDIS_BIND=127.0.0.1

# Use SSL/TLS
REDIS_SSL=true
```

### Redis Persistence

Configure Redis for data persistence:

```conf
# redis.conf
save 900 1
save 300 10
save 60 10000

appendonly yes
appendfsync everysec
```

## Database Configuration

### PostgreSQL (Optional)

If using PostgreSQL for enhanced storage:

```env
# PostgreSQL Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/cloudcleaner
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cloudcleaner
DB_USER=cloudcleaner
DB_PASSWORD=secure-password
```

### SQLite (Default)

Default configuration uses SQLite for simplicity:

```env
# SQLite Configuration
DATABASE_URL=sqlite:///./cloudcleaner.db
```

## Caching Configuration

### Cache Settings

Configure cache behavior:

```env
# Cache TTL (Time To Live) in minutes
CACHE_TTL_EC2=5
CACHE_TTL_EBS=5
CACHE_TTL_S3=5
CACHE_TTL_IAM=5
CACHE_TTL_DETAILS=10

# Redis Cache Configuration
REDIS_CACHE_DB=0
REDIS_CACHE_PREFIX=cloudcleaner:
```

### Cache Invalidation

Cache is automatically invalidated when:
- Resources are deleted
- Scheduled scans complete
- Manual refresh is triggered

## Logging Configuration

### Log Levels

Set appropriate log levels:

```env
# Backend Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json  # json, text

# Frontend Logging
NEXT_PUBLIC_LOG_LEVEL=info
```

### Log Destinations

Configure log output:

```env
# File Logging
LOG_FILE=/var/log/cloudcleaner/app.log
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=5

# External Logging (optional)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

## Security Configuration

### CORS Settings

Configure CORS for your domain:

```env
# Allowed origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# CORS methods
CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS

# CORS headers
CORS_HEADERS=*
```

### Rate Limiting

Configure API rate limiting:

```env
# Rate limit per minute
RATE_LIMIT_PER_MINUTE=60

# Rate limit for delete operations
RATE_LIMIT_DELETE_PER_MINUTE=10

# Rate limit for scan triggers
RATE_LIMIT_SCAN_PER_MINUTE=5
```

### Authentication (Future Enhancement)

```env
# JWT Configuration (if implementing auth)
JWT_SECRET_KEY=your-super-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# OAuth Configuration (if implementing OAuth)
OAUTH_CLIENT_ID=your-oauth-client-id
OAUTH_CLIENT_SECRET=your-oauth-client-secret
OAUTH_REDIRECT_URI=https://yourdomain.com/auth/callback
```

## Monitoring Configuration

### Health Checks

Enable comprehensive health checks:

```env
# Health check endpoints
HEALTH_CHECK_DB=true
HEALTH_CHECK_REDIS=true
HEALTH_CHECK_AWS=true

# Custom health check script
HEALTH_CHECK_SCRIPT=/opt/cloudcleaner/healthcheck.sh
```

### Metrics Collection

```env
# Prometheus metrics
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090

# Custom metrics
METRICS_ENABLED=true
METRICS_ENDPOINT=/metrics
```

## Production Configuration

### Performance Tuning

```env
# Worker processes
WORKER_PROCESSES=4
WORKER_THREADS=2

# Connection pooling
DB_POOL_SIZE=20
DB_POOL_MAX_OVERFLOW=30

# Memory limits
MAX_MEMORY_USAGE=2GB
```

### Security Hardening

```env
# Security headers
SECURITY_HEADERS_ENABLED=true

# HTTPS enforcement
FORCE_HTTPS=true

# Secure cookies
SECURE_COOKIES=true
```

### Backup Configuration

```env
# Database backup
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *  # Daily at 2 AM
BACKUP_RETENTION_DAYS=30

# Log rotation
LOG_ROTATION_ENABLED=true
LOG_COMPRESSION=true
```

## Environment-Specific Configuration

### Development

```env
DEBUG=true
LOG_LEVEL=DEBUG
HOT_RELOAD=true
```

### Staging

```env
DEBUG=false
LOG_LEVEL=INFO
HEALTH_CHECKS_ENABLED=true
```

### Production

```env
DEBUG=false
LOG_LEVEL=WARNING
SECURE_MODE=true
BACKUP_ENABLED=true
MONITORING_ENABLED=true
```

## Configuration Validation

### Environment Validation Script

Create a validation script:

```bash
#!/bin/bash
# scripts/validate-config.sh

echo "Validating configuration..."

# Check required variables
required_vars=("AWS_ACCESS_KEY_ID" "AWS_SECRET_ACCESS_KEY" "AWS_REGION")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var is required"
        exit 1
    fi
done

# Test AWS connectivity
aws sts get-caller-identity > /dev/null
if [ $? -ne 0 ]; then
    echo "Error: AWS credentials are invalid"
    exit 1
fi

# Test Redis connection
redis-cli ping > /dev/null
if [ $? -ne 0 ]; then
    echo "Warning: Redis is not accessible"
fi

echo "Configuration validation completed successfully!"
```

Run validation:
```bash
./scripts/validate-config.sh