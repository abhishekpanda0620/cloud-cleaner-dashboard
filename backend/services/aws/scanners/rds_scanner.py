"""
RDS Scanner for identifying unused RDS database instances.

This scanner checks for RDS instances that are:
- Stopped for extended periods
- Running but with no database connections
- Running but with low CPU utilization
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from ..scanner_base import ScannerBase

logger = logging.getLogger(__name__)


class RDSScanner(ScannerBase):
    """
    Scanner for Amazon RDS instances.
    
    Identifies unused databases based on:
    - Instance status (stopped, failed)
    - Database connections (0 connections for 7+ days)
    - CPU utilization (< 5% for 7+ days)
    - Read/Write IOPS (< 1 for 7+ days)
    """
    
    @property
    def service_name(self) -> str:
        return "Amazon Relational Database Service"
    
    @property
    def service_code(self) -> str:
        return "AmazonRDS"
    
    @property
    def service_category(self) -> str:
        return "Database"
    
    def scan(self, regions: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Scan for RDS instances across regions.
        
        Args:
            regions: List of regions to scan. If None, scan all regions.
            
        Returns:
            List of RDS instance resources
        """
        if regions is None:
            regions = self.get_supported_regions()
        
        all_instances = []
        
        for region in regions:
            try:
                instances = self._scan_region(region)
                all_instances.extend(instances)
                logger.info(f"Found {len(instances)} RDS instances in {region}")
            except Exception as e:
                logger.error(f"Error scanning RDS in {region}: {e}")
                continue
        
        return all_instances
    
    def _scan_region(self, region: str) -> List[Dict[str, Any]]:
        """
        Scan RDS instances in a specific region.
        
        Args:
            region: AWS region code
            
        Returns:
            List of RDS instance resources
        """
        instances = []
        
        try:
            rds_client = self.session.client('rds', region_name=region)
            
            # Describe all DB instances
            paginator = rds_client.get_paginator('describe_db_instances')
            page_iterator = paginator.paginate()
            
            for page in page_iterator:
                for db_instance in page['DBInstances']:
                    resource = self._process_instance(db_instance, region)
                    instances.append(resource)
        
        except Exception as e:
            logger.error(f"Error describing RDS instances in {region}: {e}")
            raise
        
        return instances
    
    def _process_instance(self, db_instance: Dict[str, Any], region: str) -> Dict[str, Any]:
        """
        Process an RDS instance into standardized resource format.
        
        Args:
            db_instance: RDS instance dict from boto3
            region: AWS region
            
        Returns:
            Standardized resource dict
        """
        db_identifier = db_instance['DBInstanceIdentifier']
        db_instance_class = db_instance['DBInstanceClass']
        status = db_instance['DBInstanceStatus']
        engine = db_instance['Engine']
        engine_version = db_instance.get('EngineVersion', '')
        
        # Extract tags
        tags = {}
        for tag in db_instance.get('TagList', []):
            tags[tag['Key']] = tag['Value']
        
        # Determine if unused
        is_unused = self.identify_unused(db_instance)
        
        # Estimate monthly cost
        monthly_cost = self.estimate_monthly_cost(db_instance_class, db_instance)
        
        return {
            'resource_id': db_identifier,
            'resource_type': 'RDSInstance',
            'region': region,
            'status': 'unused' if is_unused else 'active',
            'estimated_monthly_cost': monthly_cost,
            'resource_config': {
                'db_identifier': db_identifier,
                'db_instance_class': db_instance_class,
                'engine': engine,
                'engine_version': engine_version,
                'status': status,
                'availability_zone': db_instance.get('AvailabilityZone'),
                'multi_az': db_instance.get('MultiAZ', False),
                'storage_type': db_instance.get('StorageType'),
                'allocated_storage': db_instance.get('AllocatedStorage'),
                'endpoint': db_instance.get('Endpoint', {}).get('Address'),
                'port': db_instance.get('Endpoint', {}).get('Port'),
                'vpc_id': db_instance.get('DBSubnetGroup', {}).get('VpcId'),
                'publicly_accessible': db_instance.get('PubliclyAccessible', False),
            },
            'tags': tags,
            'last_seen': datetime.utcnow()
        }
    
    def identify_unused(self, resource: Dict[str, Any]) -> bool:
        """
        Determine if an RDS instance is unused.
        
        An instance is considered unused if:
        1. It's stopped or in failed state
        2. It has no database connections for 7+ days
        3. It has low CPU utilization (< 5%) for 7+ days
        4. It has minimal read/write IOPS for 7+ days
        
        Args:
            resource: RDS instance dict (either from boto3 or standardized format)
            
        Returns:
            True if instance is unused
        """
        # Handle both raw boto3 format and standardized format
        if 'DBInstanceStatus' in resource:
            # Raw boto3 format
            status = resource['DBInstanceStatus']
            db_identifier = resource['DBInstanceIdentifier']
            region = resource.get('AvailabilityZone', 'us-east-1')[:-1]
        else:
            # Standardized format
            status = resource.get('resource_config', {}).get('status', 'unknown')
            db_identifier = resource.get('resource_id')
            region = resource.get('region', 'us-east-1')
        
        # Stopped, failed, or incompatible instances are unused
        if status in ['stopped', 'failed', 'incompatible-parameters', 'incompatible-restore']:
            return True
        
        # For available instances, check CloudWatch metrics
        if status == 'available':
            return self._check_low_utilization(db_identifier, region)
        
        return False
    
    def _check_low_utilization(self, db_identifier: str, region: str) -> bool:
        """
        Check if RDS instance has low utilization based on CloudWatch metrics.
        
        Args:
            db_identifier: RDS instance identifier
            region: AWS region
            
        Returns:
            True if instance has low utilization
        """
        try:
            # Check database connections
            connection_metrics = self.get_cloudwatch_metrics(
                namespace='AWS/RDS',
                metric_name='DatabaseConnections',
                dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_identifier}],
                days=7
            )
            
            if connection_metrics:
                avg_connections = sum(m.get('Average', 0) for m in connection_metrics) / len(connection_metrics)
                if avg_connections < 1.0:  # Less than 1 connection on average
                    logger.debug(f"RDS {db_identifier} has low connections: {avg_connections:.2f}")
                    return True
            
            # Check CPU utilization
            cpu_metrics = self.get_cloudwatch_metrics(
                namespace='AWS/RDS',
                metric_name='CPUUtilization',
                dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_identifier}],
                days=7
            )
            
            if cpu_metrics:
                avg_cpu = sum(m.get('Average', 0) for m in cpu_metrics) / len(cpu_metrics)
                if avg_cpu < 5.0:  # Less than 5% CPU
                    logger.debug(f"RDS {db_identifier} has low CPU: {avg_cpu:.2f}%")
                    return True
            
            # Check read IOPS
            read_iops_metrics = self.get_cloudwatch_metrics(
                namespace='AWS/RDS',
                metric_name='ReadIOPS',
                dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_identifier}],
                days=7
            )
            
            if read_iops_metrics:
                avg_read_iops = sum(m.get('Average', 0) for m in read_iops_metrics) / len(read_iops_metrics)
                if avg_read_iops < 1.0:  # Less than 1 IOPS
                    logger.debug(f"RDS {db_identifier} has low read IOPS: {avg_read_iops:.2f}")
                    return True
        
        except Exception as e:
            logger.warning(f"Could not check utilization for {db_identifier}: {e}")
        
        return False
    
    def estimate_monthly_cost(
        self,
        resource_type: str,
        resource_config: Dict[str, Any]
    ) -> float:
        """
        Estimate monthly cost for an RDS instance.
        
        This is a simplified estimation based on instance class.
        For accurate pricing, integrate with AWS Price List API.
        
        Args:
            resource_type: Instance class (e.g., 'db.t3.micro')
            resource_config: Instance configuration
            
        Returns:
            Estimated monthly cost in USD
        """
        # Simplified pricing (approximate on-demand prices for MySQL/PostgreSQL)
        # In production, use AWS Price List API for accurate pricing
        pricing = {
            # T-series (burstable)
            'db.t2.micro': 0.017,
            'db.t2.small': 0.034,
            'db.t2.medium': 0.068,
            'db.t3.micro': 0.016,
            'db.t3.small': 0.032,
            'db.t3.medium': 0.064,
            'db.t3.large': 0.128,
            
            # M-series (general purpose)
            'db.m5.large': 0.192,
            'db.m5.xlarge': 0.384,
            'db.m5.2xlarge': 0.768,
            'db.m5.4xlarge': 1.536,
            
            # R-series (memory optimized)
            'db.r5.large': 0.24,
            'db.r5.xlarge': 0.48,
            'db.r5.2xlarge': 0.96,
            'db.r5.4xlarge': 1.92,
        }
        
        hourly_rate = pricing.get(resource_type, 0.10)  # Default to $0.10/hour
        
        # Calculate monthly cost (730 hours per month)
        monthly_cost = hourly_rate * 730
        
        # Add storage cost (approximate $0.10 per GB-month)
        allocated_storage = resource_config.get('AllocatedStorage', 0)
        if isinstance(resource_config, dict) and 'allocated_storage' in resource_config:
            allocated_storage = resource_config['allocated_storage']
        
        storage_cost = allocated_storage * 0.10
        
        total_cost = monthly_cost + storage_cost
        
        return round(total_cost, 2)
    
    def validate_permissions(self) -> Dict[str, Any]:
        """
        Validate that required IAM permissions are available.
        
        Returns:
            Dict with validation results
        """
        required_permissions = [
            'rds:DescribeDBInstances',
            'cloudwatch:GetMetricStatistics'
        ]
        
        try:
            # Try to describe DB instances in one region
            rds_client = self.session.client('rds', region_name='us-east-1')
            rds_client.describe_db_instances(MaxRecords=20)
            
            return {
                'has_permissions': True,
                'missing_permissions': [],
                'error': None
            }
        
        except Exception as e:
            error_msg = str(e)
            if 'AccessDenied' in error_msg or 'UnauthorizedOperation' in error_msg:
                return {
                    'has_permissions': False,
                    'missing_permissions': required_permissions,
                    'error': 'Missing RDS describe permissions'
                }
            return {
                'has_permissions': False,
                'missing_permissions': [],
                'error': error_msg
            }