# Release Notes

## Version 0.4.1 - UI Enhancement & Polish (Current)
**Release Date**: October 29, 2025

### 🎨 Major UI/UX Overhaul

#### Professional Dashboard Redesign
- **Stunning Visual Design**: Complete redesign of Resource Dashboard to match Cost Analysis quality
- **Modern Gradients**: Beautiful gradient backgrounds throughout (blue, indigo, purple, pink, rose)
- **Enhanced Shadows**: Multi-level shadows for depth (shadow-md, shadow-lg, shadow-xl, shadow-2xl)
- **Smooth Animations**: Hover effects, scale transforms, rotations, and fade-in animations
- **Professional Typography**: Bold headings with gradient text effects
- **Consistent Spacing**: Improved padding and margins (space-y-8) for better visual flow

#### Component Enhancements

**AlertPanel Component**:
- Redesigned with stunning purple-to-rose gradient background
- Animated background patterns with blur effects
- Enhanced buttons with gradient overlays and hover animations
- Resource count display badge
- Improved message notifications with icons
- Smooth hover effects with scale and shadow transitions

**ScheduleSettings Component**:
- Complete redesign with decorative gradient backgrounds
- Modern card design with blue-to-indigo gradient accents
- Enhanced toggle switch with gradient colors
- Beautiful status cards with gradient backgrounds and icons
- Improved form inputs with better borders and focus states
- Channel selection cards with hover effects and gradients
- Action buttons with gradient backgrounds and animations

**ResourceTable Component**:
- White card backgrounds with gradient hover effects
- Decorative gradient overlays on hover
- Floating icon badge in top-right corner with rotation animation
- Enhanced action buttons with gradient backgrounds
- Smooth hover animations with scale and shadow effects
- Better spacing and visual hierarchy

**ResourceFilters Component**:
- Modern search input with enhanced focus states
- Gradient backgrounds for active filter states
- Animated filter toggle button with rotation
- Beautiful filter dropdown panel with gradient background
- Enhanced result count badges with gradients
- Smooth animations for all interactions

**ResourceTab Component**:
- Redesigned info notes with gradient backgrounds
- Animated icon badges with hover effects
- Better visual hierarchy with shadows and borders

**Dashboard Page Layout**:
- Improved spacing between sections (space-y-8)
- Added fade-in animations for panels
- Enhanced tab design with gradient backgrounds and active states
- Better border styling (border-2, border-4)
- Improved overall visual flow

### 🎯 Design Features
- **Rounded Corners**: Consistent use of rounded-xl and rounded-2xl
- **Border Styles**: Enhanced borders with gradient effects
- **Icon Animations**: Icons scale and rotate on hover
- **Color Palette**: Professional blue/indigo/purple/pink gradient scheme
- **Accessibility**: Maintained contrast ratios and focus states
- **Responsive**: All enhancements work across all screen sizes

### 📦 Technical Details
- No new dependencies added
- Pure Tailwind CSS enhancements
- Maintained all existing functionality
- Improved performance with CSS transforms
- Better user experience with visual feedback

---

## Version 0.4.0 - Cost Analysis & Reporting
**Release Date**: October 29, 2025

### 🚀 New Features

#### Cost Analysis Dashboard
- **Cost Estimation**: Calculate potential savings for unused resources
- **Cost Breakdown**: Visualize costs by resource type with beautiful gradient cards
- **Resource-specific Costs**: Detailed cost analysis per resource type (EC2, EBS, S3, IAM, etc.)
- **Savings Calculator**: Interactive calculator showing daily, monthly, and yearly savings
- **Professional UI**: Stunning gradient design matching modern SaaS applications
- **Real-time Updates**: Live cost calculations based on current resource data

#### Export & Reporting
- **PDF Reports**: Generate professional PDF reports with cost analysis
- **CSV Export**: Export resource and cost data for external analysis
- **Download Functionality**: One-click download of reports
- **Formatted Reports**: Professional formatting with charts and summaries

### 🎨 UI/UX Enhancements
- **Cost Analysis Page**: New dedicated page at `/cost-analysis`
- **Gradient Design**: Beautiful emerald-to-teal gradient theme
- **StatCard Component**: Reusable card component for displaying metrics
- **Interactive Elements**: Hover effects and smooth transitions throughout
- **Responsive Layout**: Optimized for all screen sizes

### 🔧 Backend Enhancements

#### New API Endpoints
- `GET /api/cost-analysis` - Get comprehensive cost analysis data
- `POST /api/cost-analysis/export/pdf` - Generate and download PDF report
- `GET /api/cost-analysis/export/csv` - Generate and download CSV export

#### Cost Calculation Engine
- **Resource Pricing**: Accurate pricing for EC2, EBS, S3, and other resources
- **Regional Pricing**: Support for region-specific pricing
- **Savings Estimation**: Calculate potential monthly savings
- **Trend Analysis**: Track cost changes over time

### 📦 New Dependencies

#### Backend
- `reportlab==4.0.7` - PDF generation library
- `matplotlib==3.8.2` - Chart generation for reports

#### Frontend
- Enhanced StatCard component for metrics display
- New Cost Analysis page with professional design

### 📚 Documentation Updates
- Added Cost Analysis feature documentation
- Updated API documentation with new endpoints
- Added export functionality guide

---

## Version 0.3.0 - Scheduled Scans & Advanced Filtering
**Release Date**: October 27, 2025

### 🚀 New Features

#### Scheduled Scans
- **Automated Scanning**: Configure periodic scans of AWS resources
- **Flexible Scheduling**: Choose from hourly, daily, weekly, or custom intervals
- **Multi-Channel Notifications**: Send scan results to Slack and/or Email
- **Manual Triggers**: Scan on-demand with "Scan Now" button
- **Status Monitoring**: View last and next scan times in real-time
- **Celery Beat Integration**: Redis-backed scheduler for persistent schedules
- **Dynamic Updates**: Modify schedules without service restarts

#### Advanced Search & Filtering
- **Resource Filtering**: Filter resources by name, ID, or tags
- **Real-time Search**: Instant search results as you type
- **Filter Persistence**: Maintains filter state across tab switches
- **Clear Filters**: Quick reset to view all resources
- **Type-specific Filters**: Tailored filtering for each resource type

### 🎨 UI/UX Enhancements
- **Schedule Settings Panel**: New component below Alert Panel for schedule configuration
- **Resource Filters Component**: Search bar with filter controls on each resource tab
- **Improved Navigation**: Better visual feedback for active filters
- **Status Indicators**: Clear display of schedule status and scan times

### 🔧 Backend Enhancements

#### New API Endpoints
- `GET /api/schedule/config` - Get current schedule configuration
- `POST /api/schedule/config` - Update schedule configuration
- `GET /api/schedule/status` - Get last/next scan times
- `POST /api/schedule/enable` - Enable scheduled scans
- `POST /api/schedule/disable` - Disable scheduled scans
- `POST /api/schedule/trigger` - Manually trigger a scan

#### New Components
- **ScheduleSettings.tsx**: Schedule configuration UI component
- **ResourceFilters.tsx**: Search and filter UI component
- **useResourceFilters.ts**: Custom hook for filter state management
- **schedule.py**: Schedule API endpoints
- **start_celery_beat.sh**: Celery Beat startup script

### 📦 New Dependencies

#### Backend
- `celery-redbeat==2.2.0` - Redis-backed Celery Beat scheduler

#### Frontend
- `lucide-react==^0.468.0` - Icon library for UI components

#### Infrastructure
- **Celery Beat**: Added to docker-compose.yml for scheduled tasks

### 📚 New Documentation
- **SCHEDULED_SCANS.md**: Complete guide for scheduled scans feature
  - Configuration instructions
  - API examples
  - Troubleshooting guide
  - Deployment instructions

### 🔄 Migration Guide from v0.2.0

#### Using Docker Compose (Recommended)
```bash
# Pull latest changes
git pull

# Rebuild containers
docker-compose down
docker-compose up -d --build

# Verify services (including celery-beat)
docker-compose ps
```

#### Local Development
```bash
# Update backend dependencies
cd backend
pip install -r requirements.txt
# or with uv
uv sync

# Start Celery Beat (in separate terminal)
./start_celery_beat.sh
# or
uv run celery -A core.celery_app beat --loglevel=info --scheduler redbeat.RedBeatScheduler

# Other services remain the same (Redis, Celery worker, backend, frontend)
```

---

## Version 0.2.0 - Major Update
**Release Date**: October 26, 2025

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
#### Dashboard Redesign

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

### 🎯 What's Next (v0.4.0 Planned)

- [ ] Cost analysis dashboard
- [ ] Resource tagging support
- [ ] Bulk delete operations
- [ ] Export reports (PDF/CSV)
- [ ] CloudWatch metrics integration
- [ ] Custom notification templates
- [ ] Webhook support for third-party integrations
- [ ] Scan result history and trends
- [ ] Multi-account support

---

## Version 0.1.0 - Initial Release
**Release Date**: October 25, 2025

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