from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional, Union
from core.aws_client import get_aws_client_factory
from core.cache import cached, invalidate_cache
from core.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/unused")
@cached(ttl_minutes=5, key_prefix="ebs")
async def get_unused_ebs(region: Optional[str] = Query(None)) -> Dict[str, Union[List[Dict[str, Any]], str]]:
    """
    Get list of unattached EBS volumes (potential cleanup candidates)
    
    Args:
        region: AWS region to scan (optional, defaults to configured region)
    
    Returns:
        Dictionary containing list of unused EBS volumes
    """
    try:
        # Use provided region or default from settings
        target_region = region or settings.aws_region
        
        # Get EC2 client for specific region (EBS uses EC2 client)
        factory = get_aws_client_factory()
        ec2_client = factory.session.client('ec2', region_name=target_region)
        
        # Get all volumes
        response = ec2_client.describe_volumes(
            Filters=[{'Name': 'status', 'Values': ['available']}]
        )
        
        unused_volumes = []
        for volume in response.get('Volumes', []):
            volume_id = volume.get('VolumeId')
            size = volume.get('Size', 0)
            volume_type = volume.get('VolumeType', 'unknown')
            create_time = volume.get('CreateTime')
            state = volume.get('State', 'unknown')
            
            # Get volume name from tags
            volume_name = 'N/A'
            for tag in volume.get('Tags', []):
                if tag.get('Key') == 'Name':
                    volume_name = tag.get('Value', 'N/A')
                    break
            
            unused_volumes.append({
                "id": volume_id,
                "name": volume_name,
                "size": size,
                "type": volume_type,
                "state": state,
                "create_time": create_time.isoformat() if create_time else None
            })
        
        logger.info(f"Found {len(unused_volumes)} unused EBS volumes in region {target_region}")
        return {"unused_volumes": unused_volumes, "region": target_region}
        
    except Exception as e:
        logger.error(f"Error fetching unused EBS volumes: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch EBS volumes: {str(e)}"
        )


@router.get("/all")
@cached(ttl_minutes=5, key_prefix="ebs")
async def get_all_volumes(region: Optional[str] = Query(None)) -> Dict[str, Union[List[Dict[str, Any]], str]]:
    """
    Get list of all EBS volumes
    
    Args:
        region: AWS region to scan (optional, defaults to configured region)
    
    Returns:
        Dictionary containing list of all EBS volumes
    """
    try:
        # Use provided region or default from settings
        target_region = region or settings.aws_region
        
        # Get EC2 client for specific region (EBS uses EC2 client)
        factory = get_aws_client_factory()
        ec2_client = factory.session.client('ec2', region_name=target_region)
        response = ec2_client.describe_volumes()
        
        volumes = []
        for volume in response.get('Volumes', []):
            volume_id = volume.get('VolumeId')
            size = volume.get('Size', 0)
            volume_type = volume.get('VolumeType', 'unknown')
            state = volume.get('State', 'unknown')
            
            # Get volume name from tags
            volume_name = 'N/A'
            for tag in volume.get('Tags', []):
                if tag.get('Key') == 'Name':
                    volume_name = tag.get('Value', 'N/A')
                    break
            
            # Check if attached
            attachments = volume.get('Attachments', [])
            attached_to = attachments[0].get('InstanceId') if attachments else None
            
            volumes.append({
                "id": volume_id,
                "name": volume_name,
                "size": size,
                "type": volume_type,
                "state": state,
                "attached_to": attached_to
            })
        
        logger.info(f"Found {len(volumes)} total EBS volumes in region {target_region}")
        return {"volumes": volumes, "region": target_region}
        
    except Exception as e:
        logger.error(f"Error fetching all EBS volumes: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch EBS volumes: {str(e)}"
        )


@router.get("/{volume_id}")
@cached(ttl_minutes=10, key_prefix="ebs")
async def get_volume_details(volume_id: str, region: Optional[str] = Query(None)) -> Dict[str, Any]:
    """
    Get detailed information about a specific EBS volume
    
    Args:
        volume_id: The EBS volume ID
        region: AWS region where the volume exists (optional, defaults to configured region)
        
    Returns:
        Dictionary containing detailed volume information
    """
    try:
        # Use provided region or default from settings
        target_region = region or settings.aws_region
        
        factory = get_aws_client_factory()
        ec2_client = factory.session.client('ec2', region_name=target_region)
        
        response = ec2_client.describe_volumes(VolumeIds=[volume_id])
        
        if not response.get('Volumes'):
            raise HTTPException(status_code=404, detail=f"Volume {volume_id} not found")
        
        volume = response['Volumes'][0]
        
        # Get volume name from tags
        volume_name = 'N/A'
        tags = {}
        for tag in volume.get('Tags', []):
            tags[tag.get('Key')] = tag.get('Value')
            if tag.get('Key') == 'Name':
                volume_name = tag.get('Value', 'N/A')
        
        # Get attachment information
        attachments = []
        for attachment in volume.get('Attachments', []):
            attachments.append({
                "instance_id": attachment.get('InstanceId'),
                "device": attachment.get('Device'),
                "state": attachment.get('State'),
                "attach_time": attachment.get('AttachTime').isoformat() if attachment.get('AttachTime') else None,
                "delete_on_termination": attachment.get('DeleteOnTermination')
            })
        
        details = {
            "id": volume.get('VolumeId'),
            "name": volume_name,
            "size": volume.get('Size'),
            "type": volume.get('VolumeType'),
            "state": volume.get('State'),
            "create_time": volume.get('CreateTime').isoformat() if volume.get('CreateTime') else None,
            "availability_zone": volume.get('AvailabilityZone'),
            "snapshot_id": volume.get('SnapshotId'),
            "iops": volume.get('Iops'),
            "throughput": volume.get('Throughput'),
            "encrypted": volume.get('Encrypted'),
            "kms_key_id": volume.get('KmsKeyId'),
            "multi_attach_enabled": volume.get('MultiAttachEnabled'),
            "attachments": attachments,
            "tags": tags
        }
        
        logger.info(f"Retrieved details for volume {volume_id} in region {target_region}")
        return details
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching volume details for {volume_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch volume details: {str(e)}"
        )


@router.delete("/{volume_id}")
async def delete_volume(volume_id: str, region: Optional[str] = Query(None)) -> Dict[str, Any]:
    """
    Delete an EBS volume
    
    Args:
        volume_id: The EBS volume ID to delete
        region: AWS region where the volume exists (optional, defaults to configured region)
        
    Returns:
        Dictionary containing deletion status
    """
    try:
        # Use provided region or default from settings
        target_region = region or settings.aws_region
        
        factory = get_aws_client_factory()
        ec2_client = factory.session.client('ec2', region_name=target_region)
        
        # First verify the volume exists and is available
        response = ec2_client.describe_volumes(VolumeIds=[volume_id])
        
        if not response.get('Volumes'):
            raise HTTPException(status_code=404, detail=f"Volume {volume_id} not found")
        
        volume = response['Volumes'][0]
        state = volume.get('State')
        
        # Check if volume is attached
        if state == 'in-use':
            attachments = volume.get('Attachments', [])
            attached_instances = [att.get('InstanceId') for att in attachments]
            raise HTTPException(
                status_code=400,
                detail=f"Volume {volume_id} is attached to instances: {', '.join(attached_instances)}. Detach before deleting."
            )
        
        # Delete the volume
        ec2_client.delete_volume(VolumeId=volume_id)
        
        logger.info(f"Deleted volume {volume_id} in region {target_region}")
        
        # Invalidate EBS cache after deletion
        invalidate_cache("ebs")
        
        return {
            "success": True,
            "volume_id": volume_id,
            "message": f"Volume {volume_id} has been deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting volume {volume_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete volume: {str(e)}"
        )
