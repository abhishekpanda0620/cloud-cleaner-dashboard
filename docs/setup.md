# Setup Guide

This guide covers all setup options for the Cloud Cleaner Dashboard.

## Quick Start with Docker

### Prerequisites

- Docker and Docker Compose installed
- Redis server (required for scheduled scanning and caching)
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
- Redis server running locally
- AWS Account with appropriate credentials

### Install Redis

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

**Verify Redis:**
```bash
redis-cli ping  # Should return: PONG
```

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

5. **Run the backend** (Terminal 1):
   ```bash
   python main.py
   # OR with uvicorn:
   uvicorn main:app --reload --host 0.0.0.0 --port 8084
   ```

6. **Start Celery Worker** (Terminal 2):
   ```bash
   ./start_celery_worker.sh
   # OR manually:
   celery -A core.celery_app worker --loglevel=info
   ```

7. **Start Celery Beat Scheduler** (Terminal 3) - Required for scheduled scans:
   ```bash
   ./start_celery_beat.sh
   # OR manually:
   celery -A core.celery_app beat --loglevel=info --scheduler redbeat.RedBeatScheduler
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

4. **Run the development server** (Terminal 4):
   ```bash
   npm run dev
   ```

5. **Access the application**:
   Open [http://localhost:3000/dashboard](http://localhost:3000/dashboard) in your browser

### Running Summary

You need **4 terminals** running simultaneously:
1. **Terminal 1**: Backend API (`python main.py`)
2. **Terminal 2**: Celery Worker (`./start_celery_worker.sh`)
3. **Terminal 3**: Celery Beat (`./start_celery_beat.sh`)
4. **Terminal 4**: Frontend (`npm run dev`)

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