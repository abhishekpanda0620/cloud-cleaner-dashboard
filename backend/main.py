from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api import ec2, ebs, s3, iam, notifications
from core.config import settings
from core.aws_client import get_aws_client_factory
from core.cache import cached
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


@app.get("/api/regions")
@cached(ttl_minutes=10080, key_prefix="regions")  # 7 days = 10080 minutes
async def get_regions():
    """
    Get AWS regions information from AWS API
    Cached for 7 days as regions rarely change
    """
    try:
        # Get EC2 client to fetch regions
        factory = get_aws_client_factory()
        ec2_client = factory.session.client('ec2', region_name=settings.aws_region)
        
        # Describe all available regions
        response = ec2_client.describe_regions(AllRegions=False)  # Only enabled regions
        
        regions = []
        for region in response.get('Regions', []):
            region_code = region.get('RegionName')
            region_name = region.get('OptInStatus')
            
            # Create a friendly name from the region code
            friendly_name = region_code.replace('-', ' ').title()
            
            regions.append({
                "code": region_code,
                "name": friendly_name,
                "endpoint": region.get('Endpoint', '')
            })
        
        # Sort regions by code for consistency
        regions.sort(key=lambda x: x['code'])
        
        logger.info(f"Retrieved {len(regions)} AWS regions")
        
        return {
            "default_region": settings.aws_region,
            "regions": regions
        }
        
    except Exception as e:
        logger.error(f"Error fetching AWS regions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch AWS regions: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )
