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
