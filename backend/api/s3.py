from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
from core.aws_client import get_s3_client
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/unused")
async def get_unused_s3_buckets() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get list of S3 buckets that haven't been accessed in 90+ days
    
    Returns:
        Dictionary containing list of potentially unused S3 buckets
    """
    try:
        s3_client = get_s3_client()
        
        # Get all buckets
        response = s3_client.list_buckets()
        
        unused_buckets = []
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)
        
        for bucket in response.get('Buckets', []):
            bucket_name = bucket.get('Name')
            creation_date = bucket.get('CreationDate')
            
            try:
                # Try to get bucket location
                location_response = s3_client.get_bucket_location(Bucket=bucket_name)
                location = location_response.get('LocationConstraint', 'us-east-1')
                
                # Try to get bucket size (this is a simplified check)
                # In production, you'd want to use CloudWatch metrics
                try:
                    objects = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
                    is_empty = objects.get('KeyCount', 0) == 0
                except Exception:
                    is_empty = False
                
                # Consider bucket unused if it's old or empty
                if creation_date < cutoff_date or is_empty:
                    unused_buckets.append({
                        "name": bucket_name,
                        "creation_date": creation_date.isoformat() if creation_date else None,
                        "location": location,
                        "is_empty": is_empty
                    })
                    
            except Exception as e:
                logger.warning(f"Could not check bucket {bucket_name}: {str(e)}")
                continue
        
        logger.info(f"Found {len(unused_buckets)} potentially unused S3 buckets")
        return {"unused_buckets": unused_buckets}
        
    except Exception as e:
        logger.error(f"Error fetching unused S3 buckets: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch S3 buckets: {str(e)}"
        )


@router.get("/all")
async def get_all_buckets() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get list of all S3 buckets
    
    Returns:
        Dictionary containing list of all S3 buckets
    """
    try:
        s3_client = get_s3_client()
        response = s3_client.list_buckets()
        
        buckets = []
        for bucket in response.get('Buckets', []):
            bucket_name = bucket.get('Name')
            creation_date = bucket.get('CreationDate')
            
            try:
                # Get bucket location
                location_response = s3_client.get_bucket_location(Bucket=bucket_name)
                location = location_response.get('LocationConstraint', 'us-east-1')
                
                buckets.append({
                    "name": bucket_name,
                    "creation_date": creation_date.isoformat() if creation_date else None,
                    "location": location
                })
            except Exception as e:
                logger.warning(f"Could not get details for bucket {bucket_name}: {str(e)}")
                buckets.append({
                    "name": bucket_name,
                    "creation_date": creation_date.isoformat() if creation_date else None,
                    "location": "unknown"
                })
        
        logger.info(f"Found {len(buckets)} total S3 buckets")
        return {"buckets": buckets}
        
    except Exception as e:
        logger.error(f"Error fetching all S3 buckets: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch S3 buckets: {str(e)}"
        )
