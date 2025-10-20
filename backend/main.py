from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import ec2, ebs, s3, iam, notifications
from core.config import settings
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="API for identifying and managing unused AWS resources",
    version="1.0.0",
    debug=settings.debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ec2.router, prefix="/api/ec2", tags=["EC2"])
app.include_router(ebs.router, prefix="/api/ebs", tags=["EBS"])
app.include_router(s3.router, prefix="/api/s3", tags=["S3"])
app.include_router(iam.router, prefix="/api/iam", tags=["IAM"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])


@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info(f"Starting {settings.app_name}")
    logger.info(f"AWS Region: {settings.aws_region}")
    logger.info(f"Server running on {settings.host}:{settings.port}")
    logger.info(f"Debug mode: {settings.debug}")


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown information"""
    logger.info(f"Shutting down {settings.app_name}")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "ec2": "/api/ec2",
            "ebs": "/api/ebs",
            "s3": "/api/s3",
            "iam": "/api/iam",
            "notifications": "/api/notifications"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "region": settings.aws_region
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )
