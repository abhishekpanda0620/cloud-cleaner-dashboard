"""
EC2 Scanner for identifying unused EC2 instances.

This scanner checks for EC2 instances that are:
- Stopped for extended periods
- Running but with low CPU utilization
- Running but with no network activity
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from ..scanner_base import ScannerBase

logger = logging.getLogger(__name__)


class EC2Scanner(ScannerBase):
    """
    Scanner for Amazon EC2 instances.
    
    Identifies unused instances based on:
    - Instance state (stopped, terminated)
    - CPU utilization (< 5% for 7+ days)
    - Network activity (< 1KB for 7+ days)
    """
    
    @property
    def service_name(self) -> str:
        return "Amazon Elastic Compute Cloud"
    
    @property
    def service_code(self) -> str:
        return "AmazonEC2"
    
    @property
    def service_category(self) -> str:
        return "Compute"
    
    def scan(self, regions: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Scan for EC2 instances across regions.
        
        Args:
            regions: List of regions to scan. If None, scan all regions.
            
        Returns:
            List of EC2 instance resources
        """
        if regions is None:
            regions = self.get_supported_regions()
        
        all_instances = []
        
        for region in regions:
            try:
                # Scan Instances
                instances = self._scan_region(region)
                all_instances.extend(instances)
                
                # Scan Volumes (EBS)
                volumes = self._scan_volumes(region)
                all_instances.extend(volumes)
                
                logger.info(f"Found {len(instances)} instances and {len(volumes)} volumes in {region}")
            except Exception as e:
                logger.error(f"Error scanning EC2/EBS in {region}: {e}")
                continue
        
        return all_instances
    
    def _scan_region(self, region: str) -> List[Dict[str, Any]]:
        """
        Scan EC2 instances in a specific region.
        
        Args:
            region: AWS region code
            
        Returns:
            List of instance resources
        """
        instances = []
        
        try:
            ec2_client = self.session.client('ec2', region_name=region)
            
            # Describe all instances
            paginator = ec2_client.get_paginator('describe_instances')
            page_iterator = paginator.paginate()
            
            for page in page_iterator:
                for reservation in page['Reservations']:
                    for instance in reservation['Instances']:
                        resource = self._process_instance(instance, region)
                        instances.append(resource)
        
        except Exception as e:
            logger.error(f"Error describing instances in {region}: {e}")
            raise
        
        return instances

    def _scan_volumes(self, region: str) -> List[Dict[str, Any]]:
        """
        Scan EBS volumes in a specific region.
        """
        volumes = []
        try:
            ec2_client = self.session.client('ec2', region_name=region)
            paginator = ec2_client.get_paginator('describe_volumes')
            for page in paginator.paginate():
                for volume in page['Volumes']:
                    resource = self._process_volume(volume, region)
                    volumes.append(resource)
        except Exception as e:
            logger.error(f"Error describing volumes in {region}: {e}")
        return volumes

    def _process_volume(self, volume: Dict[str, Any], region: str) -> Dict[str, Any]:
        volume_id = volume['VolumeId']
        size = volume['Size']
        state = volume['State']
        volume_type = volume['VolumeType']
        
        # Tags
        tags = {t['Key']: t['Value'] for t in volume.get('Tags', [])}
        
        # Unused logic: 'available' state means not attached
        is_unused = (state == 'available')
        
        # Estimate cost
        # Get price per GB-month from Pricing API
        price_per_gb = self.pricing_service.get_ebs_price(volume_type, region)
        # Fallback if price is 0 (API failure or not found) - usage hardcoded
        if price_per_gb == 0.0:
            price_per_gb = 0.10
            
        monthly_cost = size * price_per_gb
        
        return {
            'resource_id': volume_id,
            'resource_type': 'EBSVolume',
            'resource_name': f"Volume {size}GB ({state})",
            'region': region,
            'status': 'unused' if is_unused else 'active',
            'is_unused': is_unused,
            'unused_reason': 'Volume not attached to any instance' if is_unused else None,
            'estimated_monthly_cost': monthly_cost,
            'resource_config': {
                'volume_id': volume_id,
                'size': size,
                'state': state,
                'volume_type': volume_type,
                'encrypted': volume.get('Encrypted', False),
                'create_time': volume['CreateTime'].isoformat()
            },
            'tags': tags,
            'last_seen': datetime.now()
        }
    
    def _process_instance(self, instance: Dict[str, Any], region: str) -> Dict[str, Any]:
        """
        Process an EC2 instance into standardized resource format.
        
        Args:
            instance: EC2 instance dict from boto3
            region: AWS region
            
        Returns:
            Standardized resource dict
        """
        instance_id = instance['InstanceId']
        instance_type = instance['InstanceType']
        state = instance['State']['Name']
        launch_time = instance.get('LaunchTime')
        
        # Extract tags
        tags = {}
        for tag in instance.get('Tags', []):
            tags[tag['Key']] = tag['Value']
        
        # Determine if unused
        is_unused = self.identify_unused(instance)
        
        # Estimate monthly cost
        monthly_cost = self.estimate_monthly_cost(instance_type, instance)
        
        return {
            'resource_id': instance_id,
            'resource_type': 'EC2Instance',
            'region': region,
            'status': 'unused' if is_unused else 'active',
            'estimated_monthly_cost': monthly_cost,
            'resource_config': {
                'instance_id': instance_id,
                'instance_type': instance_type,
                'state': state,
                'launch_time': launch_time.isoformat() if launch_time else None,
                'availability_zone': instance.get('Placement', {}).get('AvailabilityZone'),
                'vpc_id': instance.get('VpcId'),
                'subnet_id': instance.get('SubnetId'),
                'private_ip': instance.get('PrivateIpAddress'),
                'public_ip': instance.get('PublicIpAddress'),
                'platform': instance.get('Platform', 'Linux'),
            },
            'tags': tags,
            'last_seen': datetime.utcnow()
        }
    
    def identify_unused(self, resource: Dict[str, Any]) -> bool:
        """
        Determine if an EC2 instance is unused.
        
        An instance is considered unused if:
        1. It's stopped or terminated
        2. It's running but has low CPU utilization (< 5%) for 7+ days
        3. It's running but has no network activity for 7+ days
        
        Args:
            resource: Instance dict (either from boto3 or standardized format)
            
        Returns:
            True if instance is unused
        """
        # Handle both raw boto3 format and standardized format
        if 'State' in resource:
            # Raw boto3 format
            state = resource['State']['Name']
            instance_id = resource['InstanceId']
            region = resource.get('Placement', {}).get('AvailabilityZone', 'us-east-1')[:-1]
        else:
            # Standardized format
            state = resource.get('resource_config', {}).get('state', 'unknown')
            instance_id = resource.get('resource_id')
            region = resource.get('region', 'us-east-1')
        
        # Stopped or terminated instances are unused
        if state in ['stopped', 'terminated', 'stopping', 'terminating']:
            return True
        
        # For running instances, check CloudWatch metrics
        if state == 'running':
            return self._check_low_utilization(instance_id, region)
        
        return False
    
    def _check_low_utilization(self, instance_id: str, region: str) -> bool:
        """
        Check if instance has low utilization based on CloudWatch metrics.
        
        Args:
            instance_id: EC2 instance ID
            region: AWS region
            
        Returns:
            True if instance has low utilization
        """
        try:
            # Check CPU utilization
            cpu_metrics = self.get_cloudwatch_metrics(
                namespace='AWS/EC2',
                metric_name='CPUUtilization',
                dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                days=7
            )
            
            if cpu_metrics:
                avg_cpu = sum(m.get('Average', 0) for m in cpu_metrics) / len(cpu_metrics)
                if avg_cpu < 5.0:  # Less than 5% CPU
                    logger.debug(f"Instance {instance_id} has low CPU: {avg_cpu:.2f}%")
                    return True
            
            # Check network activity
            network_in_metrics = self.get_cloudwatch_metrics(
                namespace='AWS/EC2',
                metric_name='NetworkIn',
                dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                days=7
            )
            
            if network_in_metrics:
                avg_network = sum(m.get('Average', 0) for m in network_in_metrics) / len(network_in_metrics)
                if avg_network < 1000:  # Less than 1KB
                    logger.debug(f"Instance {instance_id} has low network: {avg_network:.2f} bytes")
                    return True
        
        except Exception as e:
            logger.warning(f"Could not check utilization for {instance_id}: {e}")
        
        return False
    
    def estimate_monthly_cost(
        self,
        resource_type: str,
        resource_config: Dict[str, Any]
    ) -> float:
        """
        Estimate monthly cost for an EC2 instance.
        
        This is a simplified estimation based on instance type.
        For accurate pricing, integrate with AWS Price List API.
        
        Args:
            resource_type: Instance type (e.g., 't2.micro')
            resource_config: Instance configuration
            
        Returns:
            Estimated monthly cost in USD
        """
        # Simplified pricing (approximate on-demand prices)
        # In production, use AWS Price List API for accurate pricing
        hourly_rate = self.pricing_service.get_ec2_price(resource_type, self.region)
        
        # Fallback to hardcoded if API returns 0.0
        if hourly_rate == 0.0:
            # Simplified pricing (approximate on-demand prices)
            pricing = {
                # T-series (burstable)
                't2.micro': 0.0116,
                't2.small': 0.023,
                't2.medium': 0.0464,
                't2.large': 0.0928,
                't3.micro': 0.0104,
                't3.small': 0.0208,
                't3.medium': 0.0416,
                't3.large': 0.0832,
                
                # M-series (general purpose)
                'm5.large': 0.096,
                'm5.xlarge': 0.192,
                'm5.2xlarge': 0.384,
                'm5.4xlarge': 0.768,
                
                # C-series (compute optimized)
                'c5.large': 0.085,
                'c5.xlarge': 0.17,
                'c5.2xlarge': 0.34,
                
                # R-series (memory optimized)
                'r5.large': 0.126,
                'r5.xlarge': 0.252,
                'r5.2xlarge': 0.504,
                'r5.2xlarge': 0.504,
            }
            hourly_rate = pricing.get(resource_type, 0.05)
        
        # Calculate monthly cost (730 hours per month)
        monthly_cost = hourly_rate * 730
        
        return round(monthly_cost, 2)
    
    def validate_permissions(self) -> Dict[str, Any]:
        """
        Validate that required IAM permissions are available.
        
        Returns:
            Dict with validation results
        """
        required_permissions = [
            'ec2:DescribeInstances',
            'cloudwatch:GetMetricStatistics'
        ]
        
        try:
            # Try to describe instances in one region
            ec2_client = self.session.client('ec2', region_name='us-east-1')
            ec2_client.describe_instances(MaxResults=5)
            
            return {
                'has_permissions': True,
                'missing_permissions': [],
                'error': None
            }
        
        except Exception as e:
            error_msg = str(e)
            if 'UnauthorizedOperation' in error_msg:
                return {
                    'has_permissions': False,
                    'missing_permissions': required_permissions,
                    'error': 'Missing EC2 describe permissions'
                }
            return {
                'has_permissions': False,
                'missing_permissions': [],
                'error': error_msg
            }