from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Union
from core.aws_client import get_aws_client_factory
from core.cache import cached, invalidate_cache
from core.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/unused")
@cached(ttl_minutes=5, key_prefix="ec2")
async def get_unused_instances(region: Optional[str] = Query(None)) -> Dict[str, Union[List[Dict[str, Any]], str]]:
    """
    Get list of stopped EC2 instances that have been stopped for more than 7 days
    
    Args:
        region: AWS region to scan (optional, defaults to configured region)
    
    Returns:
        Dictionary containing list of unused EC2 instances
    """
    try:
        # Use provided region or default from settings
        target_region = region or settings.aws_region
        
        # Get EC2 client for specific region
        factory = get_aws_client_factory()
        ec2_client = factory.session.client('ec2', region_name=target_region)
        
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
        
        logger.info(f"Found {len(unused)} unused EC2 instances in region {target_region}")
        return {"unused_instances": unused, "region": target_region}
        
    except Exception as e:
        logger.error(f"Error fetching unused EC2 instances: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch EC2 instances: {str(e)}"
        )


@router.get("/all")
@cached(ttl_minutes=5, key_prefix="ec2")
async def get_all_instances(region: Optional[str] = Query(None)) -> Dict[str, Union[List[Dict[str, Any]], str]]:
    """
    Get list of all EC2 instances
    
    Args:
        region: AWS region to scan (optional, defaults to configured region)
    
    Returns:
        Dictionary containing list of all EC2 instances
    """
    try:
        # Use provided region or default from settings
        target_region = region or settings.aws_region
        
        # Get EC2 client for specific region
        factory = get_aws_client_factory()
        ec2_client = factory.session.client('ec2', region_name=target_region)
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
        
        logger.info(f"Found {len(instances)} total EC2 instances in region {target_region}")
        return {"instances": instances, "region": target_region}
        
    except Exception as e:
        logger.error(f"Error fetching all EC2 instances: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch EC2 instances: {str(e)}"
        )


@router.get("/{instance_id}")
@cached(ttl_minutes=10, key_prefix="ec2")
async def get_instance_details(instance_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific EC2 instance
    
    Args:
        instance_id: The EC2 instance ID
        
    Returns:
        Dictionary containing detailed instance information
    """
    try:
        factory = get_aws_client_factory()
        ec2_client = factory.session.client('ec2', region_name=settings.aws_region)
        
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        
        if not response.get('Reservations'):
            raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")
        
        instance = response['Reservations'][0]['Instances'][0]
        
        # Get instance name from tags
        instance_name = 'N/A'
        tags = {}
        for tag in instance.get('Tags', []):
            tags[tag.get('Key')] = tag.get('Value')
            if tag.get('Key') == 'Name':
                instance_name = tag.get('Value', 'N/A')
        
        # Get security groups
        security_groups = [
            {
                "id": sg.get('GroupId'),
                "name": sg.get('GroupName')
            }
            for sg in instance.get('SecurityGroups', [])
        ]
        
        # Get network interfaces
        network_interfaces = [
            {
                "id": ni.get('NetworkInterfaceId'),
                "private_ip": ni.get('PrivateIpAddress'),
                "public_ip": ni.get('Association', {}).get('PublicIp')
            }
            for ni in instance.get('NetworkInterfaces', [])
        ]
        
        details = {
            "id": instance.get('InstanceId'),
            "name": instance_name,
            "type": instance.get('InstanceType'),
            "state": instance.get('State', {}).get('Name'),
            "launch_time": instance.get('LaunchTime').isoformat() if instance.get('LaunchTime') else None,
            "availability_zone": instance.get('Placement', {}).get('AvailabilityZone'),
            "vpc_id": instance.get('VpcId'),
            "subnet_id": instance.get('SubnetId'),
            "private_ip": instance.get('PrivateIpAddress'),
            "public_ip": instance.get('PublicIpAddress'),
            "key_name": instance.get('KeyName'),
            "platform": instance.get('Platform', 'Linux'),
            "architecture": instance.get('Architecture'),
            "root_device_type": instance.get('RootDeviceType'),
            "state_transition_reason": instance.get('StateTransitionReason'),
            "monitoring": instance.get('Monitoring', {}).get('State'),
            "security_groups": security_groups,
            "network_interfaces": network_interfaces,
            "tags": tags,
            "block_device_mappings": [
                {
                    "device_name": bdm.get('DeviceName'),
                    "volume_id": bdm.get('Ebs', {}).get('VolumeId'),
                    "status": bdm.get('Ebs', {}).get('Status')
                }
                for bdm in instance.get('BlockDeviceMappings', [])
            ]
        }
        
        logger.info(f"Retrieved details for instance {instance_id}")
        return details
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching instance details for {instance_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch instance details: {str(e)}"
        )


@router.delete("/{instance_id}")
async def terminate_instance(instance_id: str) -> Dict[str, Any]:
    """
    Terminate an EC2 instance
    
    Args:
        instance_id: The EC2 instance ID to terminate
        
    Returns:
        Dictionary containing termination status
    """
    try:
        factory = get_aws_client_factory()
        ec2_client = factory.session.client('ec2', region_name=settings.aws_region)
        
        # First verify the instance exists and get its current state
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        
        if not response.get('Reservations'):
            raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")
        
        instance = response['Reservations'][0]['Instances'][0]
        current_state = instance.get('State', {}).get('Name')
        
        # Terminate the instance
        terminate_response = ec2_client.terminate_instances(InstanceIds=[instance_id])
        
        terminated_instance = terminate_response['TerminatingInstances'][0]
        previous_state = terminated_instance['PreviousState']['Name']
        current_state = terminated_instance['CurrentState']['Name']
        
        logger.info(f"Terminated instance {instance_id} (previous state: {previous_state}, current state: {current_state})")
        
        # Invalidate EC2 cache after deletion
        invalidate_cache("ec2")
        
        return {
            "success": True,
            "instance_id": instance_id,
            "previous_state": previous_state,
            "current_state": current_state,
            "message": f"Instance {instance_id} is being terminated"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error terminating instance {instance_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to terminate instance: {str(e)}"
        )
