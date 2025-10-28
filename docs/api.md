# API Documentation

This document provides a comprehensive overview of all available API endpoints in the Cloud Cleaner Dashboard.

## Base URL
- **Development**: `http://localhost:8000/api`
- **Production**: Configure via `API_BASE_URL` environment variable

## EC2 Endpoints

### Get Stopped EC2 Instances
```http
GET /api/ec2/unused
```
Returns EC2 instances that are stopped (filtering out user-initiated shutdowns).

**Response:**
```json
{
  "unused_instances": [
    {
      "instance_id": "i-1234567890abcdef0",
      "name": "my-stopped-instance",
      "instance_type": "t2.micro",
      "availability_zone": "ap-south-1a",
      "create_time": "2024-01-15T10:30:00Z",
      "arn": "arn:aws:ec2:ap-south-1:123456789012:instance/i-1234567890abcdef0"
    }
  ]
}
```

### Get All EC2 Instances
```http
GET /api/ec2/all
```
Returns all EC2 instances regardless of state.

## EBS Endpoints

### Get Unattached EBS Volumes
```http
GET /api/ebs/unused
```
Returns EBS volumes with status 'available' (unattached).

**Response:**
```json
{
  "unused_volumes": [
    {
      "volume_id": "vol-1234567890abcdef0",
      "size": 100,
      "volume_type": "gp3",
      "availability_zone": "ap-south-1a",
      "create_time": "2024-01-15T10:30:00Z",
      "encrypted": true,
      "tags": {
        "Environment": "test"
      }
    }
  ]
}
```

### Get All EBS Volumes
```http
GET /api/ebs/all
```
Returns all EBS volumes regardless of attachment status.

## S3 Endpoints

### Get Unused S3 Buckets
```http
GET /api/s3/unused
```
Returns S3 buckets that are unused (empty or unused for 90+ days).

**Response:**
```json
{
  "unused_buckets": [
    {
      "name": "unused-test-bucket",
      "creation_date": "2024-01-15T10:30:00Z",
      "region": "us-east-1",
      "is_empty": true,
      "last_accessed": null
    }
  ]
}
```

### Get All S3 Buckets
```http
GET /api/s3/all
```
Returns all S3 buckets in your account.

## IAM Endpoints

### Get Unused IAM Roles
```http
GET /api/iam/unused
```
Returns IAM roles that haven't been used in 90+ days.

**Response:**
```json
{
  "unused_roles": [
    {
      "name": "unused-role",
      "create_date": "2024-01-15T10:30:00Z",
      "last_used_date": "2024-01-01T10:30:00Z",
      "arn": "arn:aws:iam::123456789012:role/unused-role",
      "description": "Role description"
    }
  ]
}
```

### Get All IAM Roles
```http
GET /api/iam/all
```
Returns all IAM roles with usage details.

### Get Unused IAM Users
```http
GET /api/iam/users/unused
```
Returns IAM users with no recent console or programmatic access.

**Response:**
```json
{
  "unused_users": [
    {
      "name": "unused-user",
      "create_date": "2024-01-15T10:30:00Z",
      "arn": "arn:aws:iam::123456789012:user/unused-user",
      "has_console_access": false,
      "access_keys_count": 0,
      "access_keys": []
    }
  ]
}
```

### Get Unused Access Keys
```http
GET /api/iam/access-keys/unused
```
Returns access keys that haven't been used in 90+ days with security risk assessment.

**Response:**
```json
{
  "unused_keys": [
    {
      "access_key_id": "AKIAIOSFODNN7EXAMPLE",
      "user_name": "test-user",
      "status": "Active",
      "create_date": "2024-01-15T10:30:00Z",
      "last_used_date": null,
      "security_risk": "High"
    }
  ]
}
```

### Get Detailed IAM Role Information
```http
GET /api/iam/roles/{role_name}
```
Returns comprehensive information about a specific IAM role.

**Response:**
```json
{
  "name": "my-role",
  "arn": "arn:aws:iam::123456789012:role/my-role",
  "role_id": "AROABC123DEFG456HIJK",
  "path": "/",
  "create_date": "2024-01-15T10:30:00Z",
  "description": "Role description",
  "max_session_duration": 3600,
  "last_used_date": "2024-01-01T10:30:00Z",
  "last_used_region": "ap-south-1",
  "assume_role_policy": {...},
  "attached_policies": [
    {
      "name": "AmazonS3ReadOnlyAccess",
      "arn": "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
    }
  ],
  "inline_policies": ["my-inline-policy"],
  "tags": {
    "Environment": "production"
  }
}
```

### Delete IAM Role
```http
DELETE /api/iam/roles/{role_name}?force=true
```
Deletes an IAM role. Use `force=true` to detach all policies and remove from instance profiles before deletion.

**Response:**
```json
{
  "success": true,
  "role_name": "my-role",
  "message": "Role my-role has been deleted"
}
```

### Get Detailed IAM User Information
```http
GET /api/iam/users/{user_name}
```
Returns comprehensive information about a specific IAM user.

**Response:**
```json
{
  "name": "test-user",
  "arn": "arn:aws:iam::123456789012:user/test-user",
  "user_id": "AIDACKCEVSQ6C2EXAMPLE",
  "path": "/",
  "create_date": "2024-01-15T10:30:00Z",
  "password_last_used": "2024-01-01T10:30:00Z",
  "has_console_access": true,
  "attached_policies": [...],
  "inline_policies": [...],
  "access_keys": [
    {
      "access_key_id": "AKIAIOSFODNN7EXAMPLE",
      "status": "Active",
      "create_date": "2024-01-15T10:30:00Z"
    }
  ],
  "groups": ["Developers"],
  "tags": {
    "Department": "Engineering"
  }
}
```

### Delete IAM User
```http
DELETE /api/iam/users/{user_name}?force=true
```
Deletes an IAM user. Use `force=true` to remove all user resources before deletion.

**Response:**
```json
{
  "success": true,
  "user_name": "test-user",
  "message": "User test-user has been deleted"
}
```

## Schedule Endpoints

### Get Schedule Configuration
```http
GET /api/schedule/config
```
Returns current schedule configuration.

**Response:**
```json
{
  "enabled": true,
  "frequency": "daily",
  "channels": ["slack", "email"],
  "custom_interval": 60
}
```

### Update Schedule Configuration
```http
POST /api/schedule/config
```
Updates schedule configuration.

**Request Body:**
```json
{
  "enabled": true,
  "frequency": "daily",
  "channels": ["slack"],
  "custom_interval": null
}
```

### Get Schedule Status
```http
GET /api/schedule/status
```
Returns schedule status including last and next scan times.

**Response:**
```json
{
  "enabled": true,
  "frequency": "daily",
  "channels": ["slack"],
  "last_scan": "2024-01-15T10:30:00Z",
  "next_scan": "2024-01-16T10:30:00Z"
}
```

### Enable Scheduled Scanning
```http
POST /api/schedule/enable
```
Enables automated scheduled scanning.

**Response:**
```json
{
  "message": "Scheduled scans enabled successfully",
  "enabled": true
}
```

### Disable Scheduled Scanning
```http
POST /api/schedule/disable
```
Disables automated scheduled scanning.

**Response:**
```json
{
  "message": "Scheduled scans disabled successfully",
  "enabled": false
}
```

### Manually Trigger Scan
```http
POST /api/schedule/trigger
```
Manually triggers a scan immediately.

**Response:**
```json
{
  "message": "Scan triggered successfully",
  "task_id": "abc123-def456-ghi789"
}
```

## Notification Endpoints

### Send Alert
```http
POST /api/notifications/send-alert
```
Send resource summary alerts via configured channels.

**Request Body:**
```json
{
  "channel": "slack", // "slack", "email", or null for both
  "message": "Custom message (optional)"
}
```

**Response:**
```json
{
  "slack_sent": true,
  "email_sent": false,
  "message": "Alerts sent successfully"
}
```

### Get Notification Configuration
```http
GET /api/notifications/config
```
Returns current notification channel configuration.

**Response:**
```json
{
  "slack_configured": true,
  "email_configured": true,
  "slack_webhook_url": "https://hooks.slack.com/...",
  "email_recipients": ["admin@company.com"]
}
```

## System Endpoints

### API Information
```http
GET /
```
Returns API version and basic information.

**Response:**
```json
{
  "name": "Cloud Cleaner Dashboard API",
  "version": "1.0.0",
  "description": "AWS resource monitoring and cleanup tool",
  "docs": "/docs"
}
```

### Health Check
```http
GET /health
```
Returns API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

## Error Responses

All endpoints return standardized error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Resource Not Found
- `500` - Internal Server Error

## Rate Limiting

API endpoints are rate-limited to prevent abuse:
- Standard endpoints: 60 requests per minute
- Delete endpoints: 10 requests per minute
- Scan triggers: 5 requests per minute

## Caching

Several endpoints implement caching to improve performance:
- Resource endpoints: 5-minute cache
- Detail endpoints: 10-minute cache
- Schedule endpoints: 1-minute cache

Cache invalidation occurs automatically when resources are modified.