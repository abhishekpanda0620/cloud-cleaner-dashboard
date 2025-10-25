from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from core.aws_client import get_ebs_client
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/unused")
async def get_unused_ebs() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get list of unattached EBS volumes (potential cleanup candidates)
    
    Returns:
        Dictionary containing list of unused EBS volumes
    """
    try:
        ec2_client = get_ebs_client()
        
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
        
        logger.info(f"Found {len(unused_volumes)} unused EBS volumes")
        return {"unused_volumes": unused_volumes}
        
    except Exception as e:
        logger.error(f"Error fetching unused EBS volumes: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch EBS volumes: {str(e)}"
        )


@router.get("/all")
async def get_all_volumes() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get list of all EBS volumes
    
    Returns:
        Dictionary containing list of all EBS volumes
    """
    try:
        ec2_client = get_ebs_client()
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
        
        logger.info(f"Found {len(volumes)} total EBS volumes")
        return {"volumes": volumes}
        
    except Exception as e:
        logger.error(f"Error fetching all EBS volumes: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch EBS volumes: {str(e)}"
        )


@router.get("/{volume_id}")
async def get_volume_details(volume_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific EBS volume
    
    Args:
        volume_id: The EBS volume ID
        
    Returns:
        Dictionary containing detailed volume information
    """
    try:
        ec2_client = get_ebs_client()
        
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
        
        logger.info(f"Retrieved details for volume {volume_id}")
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
async def delete_volume(volume_id: str) -> Dict[str, Any]:
    """
    Delete an EBS volume
    
    Args:
        volume_id: The EBS volume ID to delete
        
    Returns:
        Dictionary containing deletion status
    """
    try:
        ec2_client = get_ebs_client()
        
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
        
        logger.info(f"Deleted volume {volume_id}")
        
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
