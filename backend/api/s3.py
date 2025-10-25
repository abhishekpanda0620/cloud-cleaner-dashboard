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


@router.get("/{bucket_name}")
async def get_bucket_details(bucket_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific S3 bucket
    
    Args:
        bucket_name: The S3 bucket name
        
    Returns:
        Dictionary containing detailed bucket information
    """
    try:
        s3_client = get_s3_client()
        
        # Check if bucket exists
        try:
            s3_client.head_bucket(Bucket=bucket_name)
        except:
            raise HTTPException(status_code=404, detail=f"Bucket {bucket_name} not found")
        
        # Get bucket location
        location_response = s3_client.get_bucket_location(Bucket=bucket_name)
        location = location_response.get('LocationConstraint') or 'us-east-1'
        
        # Get bucket creation date
        buckets_response = s3_client.list_buckets()
        creation_date = None
        for bucket in buckets_response.get('Buckets', []):
            if bucket.get('Name') == bucket_name:
                creation_date = bucket.get('CreationDate')
                break
        
        # Get bucket size and object count
        try:
            objects_response = s3_client.list_objects_v2(Bucket=bucket_name)
            object_count = objects_response.get('KeyCount', 0)
            
            # Calculate total size
            total_size = 0
            if object_count > 0:
                paginator = s3_client.get_paginator('list_objects_v2')
                for page in paginator.paginate(Bucket=bucket_name):
                    for obj in page.get('Contents', []):
                        total_size += obj.get('Size', 0)
        except:
            object_count = 0
            total_size = 0
        
        # Get bucket versioning
        try:
            versioning = s3_client.get_bucket_versioning(Bucket=bucket_name)
            versioning_status = versioning.get('Status', 'Disabled')
        except:
            versioning_status = 'Unknown'
        
        # Get bucket encryption
        try:
            encryption = s3_client.get_bucket_encryption(Bucket=bucket_name)
            encryption_enabled = True
            encryption_type = encryption.get('ServerSideEncryptionConfiguration', {}).get('Rules', [{}])[0].get('ApplyServerSideEncryptionByDefault', {}).get('SSEAlgorithm', 'Unknown')
        except:
            encryption_enabled = False
            encryption_type = 'None'
        
        # Get bucket tags
        try:
            tags_response = s3_client.get_bucket_tagging(Bucket=bucket_name)
            tags = {tag.get('Key'): tag.get('Value') for tag in tags_response.get('TagSet', [])}
        except:
            tags = {}
        
        # Get public access block configuration
        try:
            public_access = s3_client.get_public_access_block(Bucket=bucket_name)
            public_access_config = public_access.get('PublicAccessBlockConfiguration', {})
        except:
            public_access_config = {}
        
        details = {
            "name": bucket_name,
            "location": location,
            "creation_date": creation_date.isoformat() if creation_date else None,
            "object_count": object_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "versioning_status": versioning_status,
            "encryption_enabled": encryption_enabled,
            "encryption_type": encryption_type,
            "tags": tags,
            "public_access_block": public_access_config,
            "is_empty": object_count == 0
        }
        
        logger.info(f"Retrieved details for bucket {bucket_name}")
        return details
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching bucket details for {bucket_name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch bucket details: {str(e)}"
        )


@router.delete("/{bucket_name}")
async def delete_bucket(bucket_name: str, force: bool = False) -> Dict[str, Any]:
    """
    Delete an S3 bucket
    
    Args:
        bucket_name: The S3 bucket name to delete
        force: If True, delete all objects in the bucket before deleting the bucket
        
    Returns:
        Dictionary containing deletion status
    """
    try:
        s3_client = get_s3_client()
        
        # Check if bucket exists
        try:
            s3_client.head_bucket(Bucket=bucket_name)
        except:
            raise HTTPException(status_code=404, detail=f"Bucket {bucket_name} not found")
        
        # Check if bucket is empty
        objects_response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
        is_empty = objects_response.get('KeyCount', 0) == 0
        
        if not is_empty and not force:
            raise HTTPException(
                status_code=400,
                detail=f"Bucket {bucket_name} is not empty. Use force=true to delete all objects and the bucket."
            )
        
        # If force is True and bucket is not empty, delete all objects first
        if force and not is_empty:
            logger.info(f"Force deleting all objects in bucket {bucket_name}")
            
            # Delete all objects
            paginator = s3_client.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=bucket_name):
                objects = page.get('Contents', [])
                if objects:
                    delete_keys = [{'Key': obj['Key']} for obj in objects]
                    s3_client.delete_objects(
                        Bucket=bucket_name,
                        Delete={'Objects': delete_keys}
                    )
            
            # Delete all object versions if versioning is enabled
            try:
                version_paginator = s3_client.get_paginator('list_object_versions')
                for page in version_paginator.paginate(Bucket=bucket_name):
                    versions = page.get('Versions', [])
                    delete_markers = page.get('DeleteMarkers', [])
                    
                    objects_to_delete = []
                    for version in versions:
                        objects_to_delete.append({
                            'Key': version['Key'],
                            'VersionId': version['VersionId']
                        })
                    for marker in delete_markers:
                        objects_to_delete.append({
                            'Key': marker['Key'],
                            'VersionId': marker['VersionId']
                        })
                    
                    if objects_to_delete:
                        s3_client.delete_objects(
                            Bucket=bucket_name,
                            Delete={'Objects': objects_to_delete}
                        )
            except:
                pass
        
        # Delete the bucket
        s3_client.delete_bucket(Bucket=bucket_name)
        
        logger.info(f"Deleted bucket {bucket_name}")
        
        return {
            "success": True,
            "bucket_name": bucket_name,
            "message": f"Bucket {bucket_name} has been deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting bucket {bucket_name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete bucket: {str(e)}"
        )
