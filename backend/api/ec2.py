from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from core.aws_client import get_ec2_client
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/unused")
async def get_unused_instances() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get list of stopped EC2 instances that have been stopped for more than 7 days
    
    Returns:
        Dictionary containing list of unused EC2 instances
    """
    try:
        ec2_client = get_ec2_client()
        
        # Get all stopped instances
        response = ec2_client.describe_instances(
            Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}]
        )
        
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        unused = []
        
        for reservation in response.get('Reservations', []):
            for instance in reservation.get('Instances', []):
                instance_id = instance.get('InstanceId')
                instance_type = instance.get('InstanceType', 'unknown')
                launch_time = instance.get('LaunchTime')
                state_transition_reason = instance.get('StateTransitionReason', '')
                
                # Get instance name from tags
                instance_name = 'N/A'
                for tag in instance.get('Tags', []):
                    if tag.get('Key') == 'Name':
                        instance_name = tag.get('Value', 'N/A')
                        break
                
                # Check if instance was stopped by user
                if 'User initiated' in state_transition_reason:
                    unused.append({
                        "id": instance_id,
                        "name": instance_name,
                        "type": instance_type,
                        "state": "stopped",
                        "launch_time": launch_time.isoformat() if launch_time else None,
                        "state_reason": state_transition_reason
                    })
        
        logger.info(f"Found {len(unused)} unused EC2 instances")
        return {"unused_instances": unused}
        
    except Exception as e:
        logger.error(f"Error fetching unused EC2 instances: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch EC2 instances: {str(e)}"
        )


@router.get("/all")
async def get_all_instances() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get list of all EC2 instances
    
    Returns:
        Dictionary containing list of all EC2 instances
    """
    try:
        ec2_client = get_ec2_client()
        response = ec2_client.describe_instances()
        
        instances = []
        for reservation in response.get('Reservations', []):
            for instance in reservation.get('Instances', []):
                instance_id = instance.get('InstanceId')
                instance_type = instance.get('InstanceType', 'unknown')
                state = instance.get('State', {}).get('Name', 'unknown')
                
                # Get instance name from tags
                instance_name = 'N/A'
                for tag in instance.get('Tags', []):
                    if tag.get('Key') == 'Name':
                        instance_name = tag.get('Value', 'N/A')
                        break
                
                instances.append({
                    "id": instance_id,
                    "name": instance_name,
                    "type": instance_type,
                    "state": state
                })
        
        logger.info(f"Found {len(instances)} total EC2 instances")
        return {"instances": instances}
        
    except Exception as e:
        logger.error(f"Error fetching all EC2 instances: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch EC2 instances: {str(e)}"
        )
