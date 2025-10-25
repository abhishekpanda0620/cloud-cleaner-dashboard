# Release Notes

### Version 1.0.0 
Initial release with core monitoring and notification features.

**Key Features**:
- ✅ Python 3.13 support
- ✅ Docker & Docker Compose support
- ✅ Modular frontend architecture
- ✅ Slack notifications
- ✅ Email notifications
- ✅ Separate Alert Buttons (Slack & Email)
- ✅ Alert Panel UI component
- ✅ IAM user and access key monitoring
- ✅ Comprehensive error handling
- ✅ Professional UI/UX
- ✅ Complete documentation

## Version 2.0.0 - Major Update (Current)

### 🚀 Major Features

#### Celery Integration for Background Processing
- **Distributed Task Queue**: Implemented Celery with Redis for true background task processing
- **Multi-Region Scanning**: Automatic scanning of all AWS regions for EC2/EBS resources in background
- **Task Persistence**: Redis-backed task result storage with auto-retry (3 attempts, 60s countdown)
- **Worker Management**: Dedicated Celery worker process for task execution

#### Resource Management
- **Delete Operations**: Delete resources directly from dashboard
  - EC2 instances (terminate)
  - EBS volumes (delete)
  - S3 buckets (with force delete option for non-empty buckets)
  - IAM roles (with force delete for roles with policies)
  - IAM users (with force delete for users with access keys)
- **Resource Details**: View comprehensive details for any resource in modal
- **Delete Confirmation**: Safe deletion with confirmation modal and force options

#### Performance & Caching
- **In-Memory Caching**: TTL-based caching for all API responses
- **Cache Invalidation**: Automatic cache clearing on resource deletion
- **Progressive Loading**: Per-resource loading states for better UX
- **Lazy Loading**: Resources load one-by-one for faster initial page load

#### Multi-Region Support
- **Region Selector**: Switch between AWS regions for EC2/EBS resources
- **Regional API Support**: All EC2/EBS endpoints accept `?region=` parameter
- **Multi-Region Notifications**: Email/Slack alerts include regional breakdown

### 🎨 UI/UX Improvements

#### Dashboard Redesign
- **Simplified Layout**: Removed redundant stat cards (counts shown in tabs)
- **Gradient Alert Panel**: Modern card design with integrated send buttons
- **Dynamic Connection Status**: Real-time indicator based on actual API responses
- **Fixed Modal Z-Index**: Proper layering for all modals (z-index: 9999)

#### Component Enhancements
- **ResourceDetailsModal**: Reusable modal for viewing resource details
- **DeleteConfirmationModal**: Reusable modal for safe deletion
- **RegionSelector**: Dropdown component for region selection
- **Progressive Loading**: Individual loading states per resource type

### 📊 Monitoring & Observability

#### Celery Monitoring API
New endpoints at `/api/celery/*`:
- `GET /workers` - View active Celery workers and their stats
- `GET /tasks/active` - Monitor currently running tasks
- `GET /tasks/scheduled` - View scheduled/reserved tasks
- `GET /tasks/{task_id}` - Get status of specific task
- `GET /stats` - Overall Celery statistics
- `POST /tasks/{task_id}/revoke` - Cancel/revoke a task

#### Flower Integration (Optional)
- Web-based monitoring dashboard
- Real-time task tracking
- Worker performance metrics
- Task history and statistics
- Access at `http://localhost:5555` (when running)

### 🔧 Backend Enhancements

#### New API Endpoints

**Delete Endpoints**:
- `DELETE /api/ec2/{instance_id}?region={region}` - Terminate EC2 instance
- `DELETE /api/ebs/{volume_id}?region={region}` - Delete EBS volume
- `DELETE /api/s3/{bucket_name}?force=true` - Delete S3 bucket
- `DELETE /api/iam/roles/{role_name}?force=true` - Delete IAM role
- `DELETE /api/iam/users/{user_name}?force=true` - Delete IAM user

**Details Endpoints**:
- `GET /api/ec2/{instance_id}/details?region={region}` - EC2 instance details
- `GET /api/ebs/{volume_id}/details?region={region}` - EBS volume details
- `GET /api/s3/{bucket_name}/details` - S3 bucket details
- `GET /api/iam/roles/{role_name}/details` - IAM role details
- `GET /api/iam/users/{user_name}/details` - IAM user details

**Monitoring Endpoints**:
- `GET /api/regions` - List all available AWS regions
- `GET /api/celery/*` - Celery monitoring endpoints (see above)

#### Core Improvements
- **Centralized AWS Client**: Factory pattern for boto3 client creation
- **Enhanced Error Handling**: Better error messages and partial failure support
- **Cache System**: In-memory cache with TTL and automatic invalidation
- **Background Tasks**: Celery tasks for notifications with multi-region scanning

### 📦 New Dependencies

#### Backend
- `celery==5.4.0` - Distributed task queue
- `redis==5.2.1` - Message broker and result backend
- `flower==2.0.1` - Web-based monitoring (optional)
- `tornado==6.4.2` - Async framework for Flower

#### Infrastructure
- **Redis**: Added to docker-compose.yml (redis:7-alpine)
- **Celery Worker**: Added as separate service in docker-compose.yml

### 🐛 Bug Fixes

1. **Email Notification Issue**: Fixed email showing 0 resources
   - Frontend now passes actual S3 and IAM user counts to backend
   - Backend uses these counts in email notifications

2. **Region Parameter Bug**: Fixed EC2/EBS operations using wrong region
   - Details modal now passes selected region to API
   - Delete operations include region parameter

3. **Modal Z-Index Conflicts**: Fixed overlapping modals
   - Setup guide modal: z-index 9999
   - Other modals: proper layering

4. **Undefined Client Functions**: Fixed EC2/EBS details/delete endpoints
   - Properly initialized regional EC2 clients
   - Fixed method calls on client objects

5. **Response Validation Errors**: Fixed EC2/EBS API response format
   - Corrected response structure for regional resources
   - Fixed data extraction from AWS API responses

### 📚 New Documentation

1. **DEVELOPMENT_SETUP.md**: Complete guide for local development without Docker
   - Redis installation instructions
   - Backend setup with virtual environment
   - Frontend setup
   - Running Celery worker locally
   - Flower monitoring setup
   - Troubleshooting guide

2. **Helper Scripts**:
   - `backend/test_email.py` - Test email configuration and Celery
   - `backend/run_flower.py` - Launch Flower monitoring
   - `backend/start_celery_worker.sh` - Start Celery worker

3. **API Documentation**:
   - Updated with new endpoints
   - Added region parameter documentation
   - Celery monitoring API reference

### ⚠️ Breaking Changes

1. **Notification System**: Now requires Celery worker to be running
   - Emails are processed asynchronously (may take a few seconds)
   - Tasks are queued to Redis and executed by worker

2. **Multi-Region Scanning**: EC2/EBS counts may update after initial load
   - Background task scans all regions
   - Initial dashboard shows selected region only
   - Email/Slack alerts include all regions

3. **Environment Variables**: New required variables for Celery
   - `REDIS_HOST` (default: localhost)
   - `REDIS_PORT` (default: 6379)

### 🔄 Migration Guide from v1.0.0

#### Using Docker Compose (Recommended)
```bash
# Pull latest changes
git pull

# Rebuild containers
docker-compose down
docker-compose up -d --build

# Verify services
docker-compose ps
```

#### Local Development
```bash
# Update backend dependencies
cd backend
pip install -r requirements.txt
# or with uv
uv sync

# Start Redis (in separate terminal)
redis-server

# Start Celery worker (in separate terminal)
./start_celery_worker.sh
# or
uv run python -m celery -A core.celery_app worker --loglevel=info

# Start backend (in separate terminal)
python main.py

# Start frontend (in separate terminal)
cd ../frontend
npm install
npm run dev
```

#### Verify Installation
```bash
# Test email configuration
cd backend
python test_email.py

# Check Celery workers
curl http://localhost:8000/api/celery/workers

# Check Celery stats
curl http://localhost:8000/api/celery/stats
```

### 🎯 What's Next (v2.1.0 Planned)

- [ ] Scheduled scans (cron-based)
- [ ] Cost analysis dashboard
- [ ] Resource tagging support
- [ ] Bulk delete operations
- [ ] Export reports (PDF/CSV)
- [ ] CloudWatch metrics integration
- [ ] Custom notification templates
- [ ] Webhook support for third-party integrations

---

## Version 1.0.0 - Initial Release
**Release Date**: December 15, 2024

### Core Features

#### Resource Monitoring
- **EC2 Instance Monitoring**: Track stopped EC2 instances
- **EBS Volume Management**: Identify unattached EBS volumes
- **S3 Bucket Analysis**: Find unused or empty S3 buckets
- **IAM Role Auditing**: Detect unused IAM roles
- **IAM User Auditing**: Monitor inactive IAM users
- **Access Key Monitoring**: Track unused access keys with security risk assessment

#### Dashboard & UI
- **Real-time Dashboard**: Modern React-based frontend with live data
- **Modular Components**: Reusable, maintainable component architecture
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Card-based Layout**: Clean, professional UI with better readability
- **In-app Notifications**: Real-time alerts and status updates
- **Alert Panel**: Send resource summaries directly from the dashboard

#### Notifications & Alerts
- **Slack Integration**: Real-time alerts to your Slack workspace
- **Email Notifications**: Detailed HTML reports via email
- **Separate Alert Buttons**: Send to Slack or Email independently
- **Configurable Recipients**: Send to multiple email addresses
- **Rich Formatting**: Professional message formatting with resource breakdown
- **Resource Summary**: View resource counts and estimated savings before sending

#### Backend & API
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Error Handling**: Graceful error handling with detailed messages
- **Partial Failures**: Continue loading available data even if some APIs fail
- **Health Checks**: Built-in health monitoring for all services

#### DevOps & Deployment
- **Docker Support**: Complete containerization for backend and frontend
- **Docker Compose**: One-command deployment with orchestration
- **Python 3.13**: Latest Python version with performance improvements
- **Security**: Non-root users, health checks, and best practices

### Technology Stack

#### Backend
- Python 3.13
- FastAPI
- Boto3 (AWS SDK)
- Pydantic Settings
- SMTP (Email)
- Requests (Slack)

#### Frontend
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS

#### Infrastructure
- Docker
- Docker Compose

### Initial API Endpoints

#### EC2
- `GET /api/ec2/unused` - Get stopped EC2 instances
- `GET /api/ec2/all` - Get all EC2 instances

#### EBS
- `GET /api/ebs/unused` - Get unattached EBS volumes
- `GET /api/ebs/all` - Get all EBS volumes

#### S3
- `GET /api/s3/unused` - Get unused S3 buckets
- `GET /api/s3/all` - Get all S3 buckets

#### IAM
- `GET /api/iam/unused` - Get unused IAM roles
- `GET /api/iam/all` - Get all IAM roles
- `GET /api/iam/users/unused` - Get inactive IAM users
- `GET /api/iam/access-keys/unused` - Get unused access keys

#### Notifications
- `POST /api/notifications/send-alert` - Send alert via Slack/Email
- `GET /api/notifications/config` - Get notification configuration

#### System
- `GET /` - API information
- `GET /health` - Health check

### Documentation
- README.md - Complete project documentation
- NOTIFICATIONS_SETUP.md - Detailed notification setup guide
- Docker configuration examples
- Environment variable documentation
- AWS permissions guide

### Known Limitations
- Single region support only (default: ap-south-1)
- Synchronous notification processing
- No resource deletion capability
- No caching mechanism
- No task monitoring