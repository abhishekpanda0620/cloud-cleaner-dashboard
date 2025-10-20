# Cloud Cleaner Dashboard

A comprehensive AWS resource management dashboard for identifying and tracking unused cloud resources to optimize costs.

## Features

- **EC2 Instance Monitoring**: Track stopped EC2 instances
- **EBS Volume Management**: Identify unattached EBS volumes
- **S3 Bucket Analysis**: Find unused or empty S3 buckets
- **IAM Role Auditing**: Detect unused IAM roles
- **Real-time Dashboard**: Modern React-based frontend with live data
- **RESTful API**: FastAPI backend with comprehensive endpoints

## Architecture

### Backend (FastAPI)

- **Modular Design**: Separate modules for each AWS service
- **Centralized AWS Client**: Single factory pattern for boto3 clients
- **Environment-based Configuration**: Using pydantic-settings
- **Comprehensive Logging**: Structured logging throughout
- **Error Handling**: Proper HTTP exceptions and error responses

### Frontend (Next.js)

- **Server-Side Rendering**: Next.js 14 with App Router
- **TypeScript**: Full type safety
- **Tailwind CSS**: Modern, responsive UI
- **Error Handling**: Loading states and error boundaries

## Project Structure

```
cloud-cleaner-dashboard/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── ec2.py          # EC2 instance endpoints
│   │   ├── ebs.py          # EBS volume endpoints
│   │   ├── s3.py           # S3 bucket endpoints
│   │   ├── iam.py          # IAM role endpoints
│   │   └── notifications.py # Notification endpoints
│   ├── core/
│   │   ├── config.py       # Application configuration
│   │   └── aws_client.py   # AWS client factory
│   ├── main.py             # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables
├── frontend/
│   ├── src/
│   │   └── app/
│   │       ├── dashboard/
│   │       │   └── page.tsx # Dashboard page
│   │       ├── layout.tsx   # Root layout
│   │       └── page.tsx     # Home page
│   ├── package.json
│   └── .env               # Frontend environment variables
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.13+
- Node.js 18+
- AWS Account with appropriate credentials
- AWS CLI configured (optional)
- Docker and Docker Compose (optional, for containerized deployment)

## Deployment Options

You can run this application in two ways:
1. **Local Development** - Run backend and frontend separately
2. **Docker Deployment** - Run both services using Docker Compose

---

## Docker Deployment (Recommended)

### Quick Start with Docker Compose

1. **Clone the repository and navigate to the project directory**

2. **Configure environment variables**:
   
   Create `.env` files in both backend and frontend directories:
   
   **backend/.env**:
   ```env
   AWS_ACCESS_KEY_ID=your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here
   AWS_REGION=ap-south-1
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
   PORT=8084
   HOST=0.0.0.0
   DEBUG=false
   ```
   
   **frontend/.env**:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8084/api
   ```

3. **Build and start all services**:
   ```bash
   docker-compose up -d
   ```

4. **Access the application**:
   - Frontend: [http://localhost:3000/dashboard](http://localhost:3000/dashboard)
   - Backend API: [http://localhost:8084](http://localhost:8084)
   - API Documentation: [http://localhost:8084/docs](http://localhost:8084/docs)

5. **View logs**:
   ```bash
   # All services
   docker-compose logs -f
   
   # Specific service
   docker-compose logs -f backend
   docker-compose logs -f frontend
   ```

6. **Stop services**:
   ```bash
   docker-compose down
   ```

7. **Rebuild after code changes**:
   ```bash
   docker-compose up -d --build
   ```

### Docker Commands Reference

```bash
# Start services in detached mode
docker-compose up -d

# Start services with build
docker-compose up -d --build

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View logs
docker-compose logs -f

# Check service status
docker-compose ps

# Restart a specific service
docker-compose restart backend

# Execute commands in running container
docker-compose exec backend python -c "print('Hello')"
docker-compose exec frontend npm run lint
```

---

## Local Development Setup

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
   Create a `.env` file in the backend directory:

   ```env
   AWS_ACCESS_KEY_ID=your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here
   AWS_REGION=ap-south-1
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
   PORT=8084
   HOST=0.0.0.0
   DEBUG=false
   ```

5. **Run the backend**:

   ```bash
   python main.py
   ```

   Or using uvicorn directly:

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8084 --reload
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

### System Endpoints

- `GET /` - API information
- `GET /health` - Health check

## Configuration

### Backend Configuration (backend/core/config.py)

The application uses pydantic-settings for configuration management:

- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_REGION`: AWS region (default: ap-south-1)
- `SLACK_WEBHOOK_URL`: Slack webhook for notifications (optional)
- `PORT`: Server port (default: 8084)
- `HOST`: Server host (default: 0.0.0.0)
- `APP_NAME`: Application name
- `DEBUG`: Debug mode (default: false)

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
        "iam:GetRole"
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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub.
