# Cloud Cleaner Dashboard

A comprehensive AWS resource management dashboard for identifying and tracking unused cloud resources to optimize costs. Built with Python 3.13, Docker, and modern web technologies.

## ✨ Features

### Resource Monitoring
- **🖥️ EC2 Instance Monitoring**: Track stopped EC2 instances
- **💾 EBS Volume Management**: Identify unattached EBS volumes
- **🪣 S3 Bucket Analysis**: Find unused or empty S3 buckets
- **🔐 IAM Role Auditing**: Detect unused IAM roles
- **👥 IAM User Auditing**: Monitor inactive IAM users
- **🔑 Access Key Monitoring**: Track unused access keys with security risk assessment

### Dashboard & UI
- **Real-time Dashboard**: Modern React-based frontend with live data
- **Modular Components**: Reusable, maintainable component architecture
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Card-based Layout**: Clean, professional UI with better readability
- **In-app Notifications**: Real-time alerts and status updates
- **Alert Panel**: Send resource summaries directly from the dashboard

### Notifications & Alerts
- **🔔 Slack Integration**: Real-time alerts to your Slack workspace
- **📧 Email Notifications**: Detailed HTML reports via email
- **Separate Alert Buttons**: Send to Slack or Email independently
- **Configurable Recipients**: Send to multiple email addresses
- **Rich Formatting**: Professional message formatting with resource breakdown
- **Resource Summary**: View resource counts and estimated savings before sending

### Backend & API
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Error Handling**: Graceful error handling with detailed messages
- **Partial Failures**: Continue loading available data even if some APIs fail
- **Health Checks**: Built-in health monitoring for all services

### DevOps & Deployment
- **Docker Support**: Complete containerization for backend and frontend
- **Docker Compose**: One-command deployment with orchestration
- **Python 3.13**: Latest Python version with performance improvements
- **Security**: Non-root users, health checks, and best practices

## Architecture

### Backend (FastAPI + Python 3.13)

- **Modular Design**: Separate modules for each AWS service
- **Centralized AWS Client**: Single factory pattern for boto3 clients
- **Environment-based Configuration**: Using pydantic-settings
- **Comprehensive Logging**: Structured logging throughout
- **Error Handling**: Proper HTTP exceptions and error responses
- **Notifications**: Slack and Email integration

### Frontend (Next.js 14 + TypeScript)

- **Server-Side Rendering**: Next.js 14 with App Router
- **TypeScript**: Full type safety
- **Tailwind CSS**: Modern, responsive UI
- **Error Handling**: Loading states and error boundaries
- **Modular Components**: Reusable component architecture
- **Real-time Notifications**: Toast-style notification system

## Project Structure

```
cloud-cleaner-dashboard/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── ec2.py              # EC2 instance endpoints
│   │   ├── ebs.py              # EBS volume endpoints
│   │   ├── s3.py               # S3 bucket endpoints
│   │   ├── iam.py              # IAM role & user endpoints
│   │   └── notifications.py     # Slack & Email notifications
│   ├── core/
│   │   ├── config.py           # Application configuration
│   │   └── aws_client.py       # AWS client factory
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile              # Backend container
│   ├── .dockerignore           # Docker build optimization
│   └── .env                    # Environment variables
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx    # Dashboard page
│   │   │   ├── layout.tsx      # Root layout
│   │   │   ├── page.tsx        # Home page
│   │   │   └── globals.css     # Global styles
│   │   ├── components/
│   │   │   ├── StatCard.tsx    # Stats display
│   │   │   ├── LoadingSpinner.tsx
│   │   │   ├── ErrorAlert.tsx
│   │   │   ├── EmptyState.tsx
│   │   │   ├── ResourceTable.tsx
│   │   │   ├── ResourceTab.tsx
│   │   │   ├── AlertPanel.tsx  # Alert sending UI
│   │   │   ├── NotificationSetupGuide.tsx  # Interactive setup guide
│   │   │   └── NotificationCenter.tsx
│   │   └── hooks/
│   │       └── useNotifications.ts
│   ├── package.json
│   ├── Dockerfile              # Frontend container
│   ├── .dockerignore           # Docker build optimization
│   ├── next.config.ts          # Next.js configuration
│   └── .env                    # Environment variables
├── docker-compose.yml          # Service orchestration
├── NOTIFICATIONS_SETUP.md      # Notifications guide
└── README.md
```

## Quick Start with Docker

### Prerequisites

- Docker and Docker Compose installed
- AWS Account with appropriate credentials
- (Optional) Slack workspace for notifications
- (Optional) Email account for notifications

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd cloud-cleaner-dashboard
   ```

2. **Configure environment variables**:
   
   Create `.env` file in the root directory:
   ```env
   # AWS Configuration
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_REGION=ap-south-1
   
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

3. **Start all services**:
   ```bash
   docker-compose up -d
   ```

4. **Access the application**:
   - Frontend: [http://localhost:3000/dashboard](http://localhost:3000/dashboard)
   - Backend API: [http://localhost:8084](http://localhost:8084)
   - API Documentation: [http://localhost:8084/docs](http://localhost:8084/docs)

### Docker Commands

```bash
# Start services
docker-compose up -d

# Start with rebuild
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart specific service
docker-compose restart backend
```

## Local Development Setup

### Prerequisites

- Python 3.13+
- Node.js 24+
- AWS Account with appropriate credentials

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file in the backend directory with your AWS credentials and optional notification settings.

5. **Run the backend**:
   ```bash
   python main.py
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment variables**:
   Create a `.env` file in the frontend directory:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8084/api
   ```

4. **Run the development server**:
   ```bash
   npm run dev
   ```

5. **Access the application**:
   Open [http://localhost:3000/dashboard](http://localhost:3000/dashboard) in your browser

## API Endpoints

### EC2 Endpoints
- `GET /api/ec2/unused` - Get stopped EC2 instances
- `GET /api/ec2/all` - Get all EC2 instances

### EBS Endpoints
- `GET /api/ebs/unused` - Get unattached EBS volumes
- `GET /api/ebs/all` - Get all EBS volumes

### S3 Endpoints
- `GET /api/s3/unused` - Get unused S3 buckets
- `GET /api/s3/all` - Get all S3 buckets

### IAM Endpoints
- `GET /api/iam/unused` - Get unused IAM roles
- `GET /api/iam/all` - Get all IAM roles
- `GET /api/iam/users/unused` - Get inactive IAM users
- `GET /api/iam/access-keys/unused` - Get unused access keys

### Notifications Endpoints
- `POST /api/notifications/send-alert` - Send alert via Slack/Email
- `GET /api/notifications/config` - Get notification configuration

### System Endpoints
- `GET /` - API information
- `GET /health` - Health check

## Using the Alert Panel

The Alert Panel on the dashboard allows you to send resource summaries directly to your configured notification channels:

### Features
- **Resource Summary**: View counts of all unused resources (EC2, EBS, S3, IAM Users, Access Keys)
- **Estimated Savings**: See potential monthly savings before sending
- **Separate Buttons**: Send to Slack or Email independently
- **Status Messages**: Get immediate feedback on success or errors
- **Smart Disabling**: Buttons are disabled when no resources to report or while sending
- **Interactive Setup Guide**: User-friendly modal with step-by-step instructions

### How to Use

1. **Navigate to Dashboard**: Go to [http://localhost:3000/dashboard](http://localhost:3000/dashboard)
2. **Scroll to Alert Panel**: Find the "Send Alert" section below the Savings Card
3. **Review Resource Summary**: Check the resource counts and estimated savings
4. **Send Alert**:
   - Click **"💬 Send to Slack"** to send to your Slack workspace
   - Click **"📧 Send to Email"** to send to configured email recipients
   - Or send to both channels independently

### Setup Guide

The Alert Panel includes an interactive setup guide to help you configure notifications:

1. **Click "📖 Setup Guide"** button in the Alert Panel info box
2. **Choose your notification type**:
   - **Slack Setup**: Step-by-step guide to create a Slack webhook
   - **Email Setup**: Instructions for Gmail, Office 365, SendGrid, and other SMTP servers
3. **Follow the numbered steps** with direct links to required services
4. **Copy configuration** code snippets directly from the guide
5. **Restart backend** to apply changes

### Configuration Requirements

Before using the Alert Panel, ensure you have configured:

**For Slack Alerts**:
- Set `SLACK_WEBHOOK_URL` environment variable
- Use the interactive setup guide for step-by-step instructions

**For Email Alerts**:
- Set `NOTIFICATION_EMAIL_RECIPIENTS` environment variable
- Configure SMTP settings (`SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`)
- Use the interactive setup guide for your email provider

## Configuration

### Backend Configuration (backend/core/config.py)

The application uses pydantic-settings for configuration management:

- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_REGION`: AWS region (default: ap-south-1)
- `PORT`: Server port (default: 8084)
- `HOST`: Server host (default: 0.0.0.0)
- `APP_NAME`: Application name
- `DEBUG`: Debug mode (default: false)

### Notifications Configuration

See [NOTIFICATIONS_SETUP.md](NOTIFICATIONS_SETUP.md) for detailed setup instructions for:
- Slack webhook integration
- Email notifications (Gmail, Office 365, SendGrid, etc.)
- SMTP configuration
- Testing and troubleshooting

### Frontend Configuration

- `NEXT_PUBLIC_API_URL`: Backend API URL

## AWS Permissions

The application requires the following AWS permissions:

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

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Backend linting
cd backend
flake8 .
black .

# Frontend linting
cd frontend
npm run lint
```

## Production Deployment

### Backend

1. Set `DEBUG=false` in environment variables
2. Use a production WSGI server (gunicorn recommended)
3. Configure proper CORS origins
4. Set up SSL/TLS certificates
5. Use environment-specific AWS credentials
6. Configure notification credentials securely

### Frontend

1. Build the production bundle:
   ```bash
   npm run build
   ```
2. Start the production server:
   ```bash
   npm start
   ```

## Security Considerations

- Never commit `.env` files to version control
- Use IAM roles instead of access keys when possible
- Implement proper authentication and authorization
- Restrict CORS origins in production
- Use AWS Secrets Manager for sensitive credentials
- Enable CloudTrail for audit logging
- Use strong SMTP passwords or app-specific passwords
- Rotate Slack webhook URLs periodically
- Restrict email recipient lists to authorized users

## Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'pydantic_settings'`
- **Solution**: Install pydantic-settings: `pip install pydantic-settings`

**Issue**: AWS credentials not found
- **Solution**: Ensure `.env` file is properly configured or AWS CLI is configured

**Issue**: Port already in use
- **Solution**: Change the PORT in `.env` or kill the process using the port

### Frontend Issues

**Issue**: API connection refused
- **Solution**: Ensure backend is running and `NEXT_PUBLIC_API_URL` is correct

**Issue**: CORS errors
- **Solution**: Check CORS configuration in backend `main.py`

### Notification Issues

See [NOTIFICATIONS_SETUP.md](NOTIFICATIONS_SETUP.md) for detailed troubleshooting guide.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
1. Review [NOTIFICATIONS_SETUP.md](NOTIFICATIONS_SETUP.md) for notification issues
2. Check backend logs: `docker-compose logs backend`
3. Check frontend logs: `docker-compose logs frontend`
4. Open an issue on GitHub

## Changelog

**See [RELEASES.md](RELEASES.md) for detailed release notes.**
