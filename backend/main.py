from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from api import ec2, ebs, s3, iam, notifications, celery_monitor, schedule, cost_analysis, rightsizing, savings, budgets

# ... (skip to near end)


from api import admin
from api import scan, services_v2, resources_v2
from core.config import settings
from core.aws_client import get_aws_client_factory
from core.cache import cached
from contextlib import asynccontextmanager
from models import AsyncSessionLocal, init_db
from sqlalchemy import text
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the application"""
    # Startup
    logger.info(f"Starting {settings.app_name}")
    logger.info(f"AWS Region: {settings.aws_region}")
    logger.info(f"Server running on {settings.host}:{settings.port}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Initialize database tables
    await init_db()

    # 1. Reset any stuck "running" scans to "failed"
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(
                text("UPDATE scan_history SET status = 'failed', error_message = 'System restart detected', completed_at = NOW() WHERE status = 'running'")
            )
            await db.commit()
            logger.info("Cleared stale scan records")
    except Exception as e:
        logger.error(f"Error clearing stale scans: {e}")

    # 2. Check AWS credentials (Synchronous)
    try:
        factory = get_aws_client_factory()
        sts = factory.get_client('sts')
        identity = sts.get_caller_identity()
        logger.info(f"AWS Credentials verified. Account: {identity['Account']}")
        settings.aws_account_id = identity['Account']
    except Exception as e:
        logger.error(f"AWS Credential Error: {e}")
        logger.warning("Application will start but scanning may fail")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="API for identifying and managing unused AWS resources",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers

# V2 API - Dynamic service discovery (new)
app.include_router(scan.router, prefix="/api/v2", tags=["V2 - Scan Management"])
app.include_router(services_v2.router, prefix="/api/v2", tags=["V2 - Services"])
app.include_router(resources_v2.router, prefix="/api/v2", tags=["V2 - Resources"])

# V1 API - Legacy endpoints (deprecated but functional)
app.include_router(ec2.router, prefix="/api/ec2", tags=["V1 - EC2 (Legacy)"])
app.include_router(ebs.router, prefix="/api/ebs", tags=["V1 - EBS (Legacy)"])
app.include_router(s3.router, prefix="/api/s3", tags=["V1 - S3 (Legacy)"])
app.include_router(iam.router, prefix="/api/iam", tags=["V1 - IAM (Legacy)"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(celery_monitor.router, prefix="/api/celery", tags=["Celery Monitoring"])
app.include_router(schedule.router, prefix="/api/schedule", tags=["Schedule"])
app.include_router(cost_analysis.router, prefix="/api", tags=["Cost Analysis"])
app.include_router(rightsizing.router, prefix="/api", tags=["Right-Sizing"])
app.include_router(savings.router, prefix="/api", tags=["Savings"])
app.include_router(budgets.router, prefix="/api", tags=["Budgets"])
from api import admin
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
from api import security
app.include_router(security.router, prefix="/api", tags=["Security - CIS Benchmark"])


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.app_name,
        "version": "2.0.0",
        "status": "running",
        "api_versions": {
            "v2": {
                "description": "Dynamic service discovery with plugin-based scanning",
                "endpoints": {
                    "scan": "/api/v2/scan",
                    "services": "/api/v2/services",
                    "resources": "/api/v2/resources"
                }
            },
            "v1": {
                "description": "Legacy hardcoded endpoints (deprecated)",
                "endpoints": {
                    "ec2": "/api/ec2",
                    "ebs": "/api/ebs",
                    "s3": "/api/s3",
                    "iam": "/api/iam",
                    "notifications": "/api/notifications",
                    "celery": "/api/celery",
                    "schedule": "/api/schedule",
                    "cost_analysis": "/api/cost-analysis"
                }
            }
        },
        "documentation": "/docs"
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
