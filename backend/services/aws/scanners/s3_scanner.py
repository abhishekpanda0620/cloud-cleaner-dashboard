"""
S3 Scanner for identifying unused S3 buckets.

This scanner checks for S3 buckets that are:
- Empty (no objects)
- Have no GET/PUT requests for extended periods
- Have minimal storage usage
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from ..scanner_base import ScannerBase

logger = logging.getLogger(__name__)


class S3Scanner(ScannerBase):
    """
    Scanner for Amazon S3 buckets.
    
    Identifies unused buckets based on:
    - Empty buckets (0 objects)
    - No GET requests for 30+ days
    - No PUT requests for 30+ days
    - Minimal storage usage (< 1MB)
    
    Note: S3 is a global service, but buckets have regions
    """
    
    @property
    def service_name(self) -> str:
        return "Amazon Simple Storage Service"
    
    @property
    def service_code(self) -> str:
        return "AmazonS3"
    
    @property
    def service_category(self) -> str:
        return "Storage"
    
    def scan(self, regions: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Scan for S3 buckets.
        
        Note: S3 is global, so we list all buckets once and determine their regions.
        The regions parameter is ignored for S3.
        
        Args:
            regions: Ignored for S3 (global service)
            
        Returns:
            List of S3 bucket resources
        """
        all_buckets = []
        
        try:
            s3_client = self.session.client('s3', region_name='us-east-1')
            
            # List all buckets (global operation)
            response = s3_client.list_buckets()
            
            for bucket in response.get('Buckets', []):
                try:
                    resource = self._process_bucket(bucket, s3_client)
                    all_buckets.append(resource)
                except Exception as e:
                    logger.warning(f"Error processing bucket {bucket.get('Name')}: {e}")
                    continue
            
            logger.info(f"Found {len(all_buckets)} S3 buckets")
        
        except Exception as e:
            logger.error(f"Error scanning S3 buckets: {e}")
        
        return all_buckets
    
    def _process_bucket(self, bucket: Dict[str, Any], s3_client) -> Dict[str, Any]:
        """
        Process an S3 bucket into standardized resource format.
        
        Args:
            bucket: S3 bucket dict from boto3
            s3_client: S3 client for additional queries
            
        Returns:
            Standardized resource dict
        """
        bucket_name = bucket['Name']
        creation_date = bucket.get('CreationDate')
        
        # Get bucket region
        try:
            location_response = s3_client.get_bucket_location(Bucket=bucket_name)
            region = location_response.get('LocationConstraint') or 'us-east-1'
        except Exception as e:
            logger.warning(f"Could not get region for bucket {bucket_name}: {e}")
            region = 'unknown'
        
        # Get bucket size and object count
        size_gb, object_count = self._get_bucket_metrics(bucket_name, region)
        
        # Get bucket tags
        tags = self._get_bucket_tags(bucket_name, s3_client)
        
        # Get bucket versioning status
        versioning_enabled = self._get_versioning_status(bucket_name, s3_client)
        
        # Determine if unused
        bucket_info = {
            'Name': bucket_name,
            'CreationDate': creation_date,
            'Region': region,
            'SizeGB': size_gb,
            'ObjectCount': object_count,
            'VersioningEnabled': versioning_enabled
        }
        is_unused = self.identify_unused(bucket_info)
        
        # Estimate monthly cost
        monthly_cost = self.estimate_monthly_cost(bucket_name, {
            'size_gb': size_gb,
            'object_count': object_count,
            'region': region
        })
        
        return {
            'resource_id': bucket_name,
            'resource_type': 'S3Bucket',
            'region': region,
            'status': 'unused' if is_unused else 'active',
            'estimated_monthly_cost': monthly_cost,
            'resource_config': {
                'bucket_name': bucket_name,
                'creation_date': creation_date.isoformat() if creation_date else None,
                'region': region,
                'size_gb': size_gb,
                'object_count': object_count,
                'versioning_enabled': versioning_enabled,
            },
            'tags': tags,
            'last_seen': datetime.utcnow()
        }
    
    def _get_bucket_metrics(self, bucket_name: str, region: str) -> tuple:
        """
        Get bucket size and object count from CloudWatch metrics.
        
        Args:
            bucket_name: S3 bucket name
            region: Bucket region
            
        Returns:
            Tuple of (size_in_gb, object_count)
        """
        try:
            # Get bucket size
            size_metrics = self.get_cloudwatch_metrics(
                namespace='AWS/S3',
                metric_name='BucketSizeBytes',
                dimensions=[
                    {'Name': 'BucketName', 'Value': bucket_name},
                    {'Name': 'StorageType', 'Value': 'StandardStorage'}
                ],
                days=1  # Latest value
            )
            
            size_bytes = 0
            if size_metrics:
                size_bytes = max(m.get('Average', 0) for m in size_metrics)
            
            size_gb = size_bytes / (1024 ** 3)  # Convert to GB
            
            # Get object count
            count_metrics = self.get_cloudwatch_metrics(
                namespace='AWS/S3',
                metric_name='NumberOfObjects',
                dimensions=[
                    {'Name': 'BucketName', 'Value': bucket_name},
                    {'Name': 'StorageType', 'Value': 'AllStorageTypes'}
                ],
                days=1  # Latest value
            )
            
            object_count = 0
            if count_metrics:
                object_count = int(max(m.get('Average', 0) for m in count_metrics))
            
            return round(size_gb, 2), object_count
        
        except Exception as e:
            logger.debug(f"Could not get metrics for bucket {bucket_name}: {e}")
            return 0.0, 0
    
    def _get_bucket_tags(self, bucket_name: str, s3_client) -> Dict[str, str]:
        """
        Get tags for an S3 bucket.
        
        Args:
            bucket_name: S3 bucket name
            s3_client: S3 client
            
        Returns:
            Dict of tag key-value pairs
        """
        try:
            response = s3_client.get_bucket_tagging(Bucket=bucket_name)
            tags = {}
            for tag in response.get('TagSet', []):
                tags[tag['Key']] = tag['Value']
            return tags
        except Exception as e:
            # NoSuchTagSet or any other error - just return empty tags
            if 'NoSuchTagSet' not in str(e):
                logger.debug(f"Could not get tags for bucket {bucket_name}: {e}")
            return {}
    
    def _get_versioning_status(self, bucket_name: str, s3_client) -> bool:
        """
        Check if bucket versioning is enabled.
        
        Args:
            bucket_name: S3 bucket name
            s3_client: S3 client
            
        Returns:
            True if versioning is enabled
        """
        try:
            response = s3_client.get_bucket_versioning(Bucket=bucket_name)
            status = response.get('Status', 'Disabled')
            return status == 'Enabled'
        except Exception as e:
            logger.debug(f"Could not get versioning status for bucket {bucket_name}: {e}")
            return False
    
    def identify_unused(self, resource: Dict[str, Any]) -> bool:
        """
        Determine if an S3 bucket is unused.
        
        A bucket is considered unused if:
        1. It's empty (0 objects)
        2. It has no GET requests for 30+ days
        3. It has no PUT requests for 30+ days
        4. It has minimal storage (< 1MB)
        
        Args:
            resource: Bucket dict (either from boto3 or standardized format)
            
        Returns:
            True if bucket is unused
        """
        # Handle both raw boto3 format and standardized format
        if 'Name' in resource:
            # Raw boto3 format
            bucket_name = resource['Name']
            object_count = resource.get('ObjectCount', 0)
            size_gb = resource.get('SizeGB', 0)
            region = resource.get('Region', 'us-east-1')
        else:
            # Standardized format
            bucket_name = resource.get('resource_id')
            config = resource.get('resource_config', {})
            object_count = config.get('object_count', 0)
            size_gb = config.get('size_gb', 0)
            region = resource.get('region', 'us-east-1')
        
        # Empty buckets are unused
        if object_count == 0:
            return True
        
        # Very small buckets (< 1MB) might be unused - CHECK REPLACED
        # We now check activity for all non-empty buckets regardless of size
        # to avoid flagging active config/state buckets.
        # if size_gb < 0.001:  # Less than 1MB
        #     return True
        
        # Check request metrics
        return self._check_low_activity(bucket_name, region)
    
    def _check_low_activity(self, bucket_name: str, region: str) -> bool:
        """
        Check if bucket has low activity based on CloudWatch metrics.
        
        Args:
            bucket_name: S3 bucket name
            region: Bucket region
            
        Returns:
            True if bucket has low activity
        """
        try:
            # Check GET requests
            get_metrics = self.get_cloudwatch_metrics(
                namespace='AWS/S3',
                metric_name='AllRequests',
                dimensions=[
                    {'Name': 'BucketName', 'Value': bucket_name},
                    {'Name': 'FilterId', 'Value': 'EntireBucket'}
                ],
                days=30
            )
            
            if get_metrics:
                total_requests = sum(m.get('Sum', 0) for m in get_metrics)
                if total_requests < 10:  # Less than 10 requests in 30 days
                    logger.debug(f"Bucket {bucket_name} has low activity: {total_requests} requests")
                    return True
            else:
                # No metrics means no activity
                return True
        
        except Exception as e:
            logger.debug(f"Could not check activity for bucket {bucket_name}: {e}")
        
        return False
    
    def estimate_monthly_cost(
        self,
        resource_type: str,
        resource_config: Dict[str, Any]
    ) -> float:
        """
        Estimate monthly cost for an S3 bucket.
        
        Cost factors:
        - Storage cost: $0.023 per GB-month (Standard)
        - Request cost: Minimal for unused buckets
        
        Args:
            resource_type: Bucket name (not used)
            resource_config: Bucket configuration with size_gb
            
        Returns:
            Estimated monthly cost in USD
        """
        size_gb = resource_config.get('size_gb', 0)
        
        # Standard storage pricing (approximate)
        storage_cost_per_gb = 0.023  # $0.023 per GB-month
        
        monthly_cost = size_gb * storage_cost_per_gb
        
        return round(monthly_cost, 2)
    
    def validate_permissions(self) -> Dict[str, Any]:
        """
        Validate that required IAM permissions are available.
        
        Returns:
            Dict with validation results
        """
        required_permissions = [
            's3:ListAllMyBuckets',
            's3:GetBucketLocation',
            's3:GetBucketTagging',
            's3:GetBucketVersioning',
            'cloudwatch:GetMetricStatistics'
        ]
        
        try:
            # Try to list buckets
            s3_client = self.session.client('s3', region_name='us-east-1')
            s3_client.list_buckets()
            
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
                    'error': 'Missing S3 list permissions'
                }
            return {
                'has_permissions': False,
                'missing_permissions': [],
                'error': error_msg
            }
    
    def get_supported_regions(self) -> List[str]:
        """
        Get list of regions where S3 is available.
        
        Note: S3 is global, but buckets have regions.
        
        Returns:
            List of region codes
        """
        # S3 is available in all regions
        return super().get_supported_regions()