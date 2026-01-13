"""
Base class for AWS service scanners.

All service scanners (specific and generic) must inherit from this base class
and implement the required abstract methods.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from core.aws_client import get_aws_client_factory
from .pricing import PricingService

logger = logging.getLogger(__name__)


class ScannerBase(ABC):
    """
    Abstract base class for all AWS service scanners.
    
    Each scanner is responsible for:
    1. Discovering resources for a specific AWS service
    2. Identifying unused/idle resources
    3. Extracting resource metadata and costs
    4. Handling service-specific logic
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """
        Initialize scanner.
        
        Args:
            region: AWS region to scan
        """
        self.region = region
        self.factory = get_aws_client_factory()
        self.session = self.factory.session
        self.pricing_service = PricingService()
        
    @property
    @abstractmethod
    def service_name(self) -> str:
        """
        Human-readable service name.
        
        Example: "Amazon Elastic Compute Cloud"
        """
        pass
    
    @property
    @abstractmethod
    def service_code(self) -> str:
        """
        AWS service code used in Cost Explorer.
        
        Example: "AmazonEC2"
        """
        pass
    
    @property
    @abstractmethod
    def service_category(self) -> str:
        """
        Service category for grouping.
        
        Options: "Compute", "Storage", "Database", "Networking", 
                 "Analytics", "Security", "Management", "Other"
        """
        pass
    
    @abstractmethod
    def scan(self, regions: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Scan for resources in specified regions.
        
        Args:
            regions: List of regions to scan. If None, scan all available regions.
            
        Returns:
            List of resource dictionaries with standardized format:
            {
                'resource_id': str,
                'resource_type': str,
                'region': str,
                'status': 'active' | 'unused' | 'unknown',
                'estimated_monthly_cost': float,
                'resource_config': dict,
                'tags': dict,
                'last_seen': datetime
            }
        """
        pass
    
    @abstractmethod
    def identify_unused(self, resource: Dict[str, Any]) -> bool:
        """
        Determine if a resource is unused/idle.
        
        Args:
            resource: Resource dictionary from scan()
            
        Returns:
            True if resource is unused, False otherwise
        """
        pass
    
    def get_supported_regions(self) -> List[str]:
        """
        Get list of regions where this service is available.
        
        Returns:
            List of region codes
        """
        try:
            ec2_client = self.session.client('ec2', region_name=self.region or 'us-east-1')
            response = ec2_client.describe_regions(AllRegions=False)
            return [region['RegionName'] for region in response['Regions']]
        except Exception as e:
            logger.warning(f"Could not fetch regions: {e}")
            # Fallback to common regions
            return [
                'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
                'eu-west-1', 'eu-central-1', 'ap-southeast-1', 'ap-northeast-1'
            ]
    
    def validate_permissions(self) -> Dict[str, Any]:
        """
        Validate that required IAM permissions are available.
        
        Returns:
            Dict with validation results:
            {
                'has_permissions': bool,
                'missing_permissions': List[str],
                'error': Optional[str]
            }
        """
        # Default implementation - subclasses can override
        return {
            'has_permissions': True,
            'missing_permissions': [],
            'error': None
        }
    
    def get_cloudwatch_metrics(
        self,
        namespace: str,
        metric_name: str,
        dimensions: List[Dict[str, str]],
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get CloudWatch metrics for a resource.
        
        Args:
            namespace: CloudWatch namespace (e.g., 'AWS/EC2')
            metric_name: Metric name (e.g., 'CPUUtilization')
            dimensions: Metric dimensions
            days: Number of days to retrieve
            
        Returns:
            List of metric datapoints
        """
        try:
            cloudwatch = self.session.client('cloudwatch', region_name=self.region)
            
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            response = cloudwatch.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1 hour
                Statistics=['Average', 'Maximum']
            )
            
            return response.get('Datapoints', [])
            
        except Exception as e:
            logger.warning(f"Could not fetch CloudWatch metrics: {e}")
            return []
    
    def estimate_monthly_cost(
        self,
        resource_type: str,
        resource_config: Dict[str, Any]
    ) -> float:
        """
        Estimate monthly cost for a resource.
        
        This is a basic implementation. Subclasses should override
        with service-specific pricing logic.
        
        Args:
            resource_type: Type of resource
            resource_config: Resource configuration
            
        Returns:
            Estimated monthly cost in USD
        """
        # Default: return 0, subclasses should implement actual pricing
        return 0.0
    
    def extract_tags(self, resource: Any) -> Dict[str, str]:
        """
        Extract tags from AWS resource object.
        
        Args:
            resource: AWS resource object
            
        Returns:
            Dict of tag key-value pairs
        """
        tags = {}
        
        # Handle different tag formats
        if hasattr(resource, 'tags') and resource.tags:
            for tag in resource.tags:
                if isinstance(tag, dict):
                    tags[tag.get('Key', '')] = tag.get('Value', '')
        elif isinstance(resource, dict) and 'Tags' in resource:
            for tag in resource['Tags']:
                tags[tag.get('Key', '')] = tag.get('Value', '')
        
        return tags
    
    def get_scanner_info(self) -> Dict[str, Any]:
        """
        Get information about this scanner.
        
        Returns:
            Dict with scanner metadata
        """
        return {
            'service_name': self.service_name,
            'service_code': self.service_code,
            'service_category': self.service_category,
            'scanner_type': self.__class__.__name__,
            'supported_regions': self.get_supported_regions()
        }


class GenericScanner(ScannerBase):
    """
    Generic fallback scanner for services without specific scanners.
    
    This scanner uses boto3's introspection capabilities to automatically
    discover and query resources for any AWS service.
    """
    
    def __init__(self, service_code: str, service_name: str, region: str = 'us-east-1'):
        """
        Initialize generic scanner.
        
        Args:
            service_code: AWS service code (e.g., 'dynamodb')
            service_name: Human-readable service name
            region: AWS region
        """
        super().__init__(region)
        self._service_code = service_code
        self._service_name = service_name
        self._service_category = 'Other'
        
    @property
    def service_name(self) -> str:
        return self._service_name
    
    @property
    def service_code(self) -> str:
        return self._service_code
    
    @property
    def service_category(self) -> str:
        return self._service_category
    
    def scan(self, regions: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Generic scan implementation using boto3 introspection.
        
        This method attempts to discover resources by:
        1. Creating a boto3 client for the service
        2. Finding list/describe operations
        3. Calling them to get resources
        4. Extracting metadata
        """
        resources = []
        
        if regions is None:
            regions = [self.region]
        
        for region in regions:
            try:
                # Convert service code to boto3 service name
                boto3_service = self._map_service_code_to_boto3(self._service_code)
                
                # Create client
                client = self.session.client(boto3_service, region_name=region)
                
                # Find list/describe operations
                operations = self._find_list_operations(client)
                
                # Call each operation and collect resources
                for operation in operations:
                    try:
                        region_resources = self._call_operation(client, operation, region)
                        resources.extend(region_resources)
                    except Exception as e:
                        logger.debug(f"Operation {operation} failed: {e}")
                        continue
                        
            except Exception as e:
                logger.warning(f"Could not scan {self._service_code} in {region}: {e}")
                continue
        
        return resources
    
    def identify_unused(self, resource: Dict[str, Any]) -> bool:
        """
        Generic unused detection using CloudWatch metrics.
        
        This is a basic heuristic - specific scanners should override
        with service-specific logic.
        """
        # Generic heuristic: check if resource has any CloudWatch activity
        try:
            # Try to get generic metrics
            metrics = self.get_cloudwatch_metrics(
                namespace=f'AWS/{self._service_code}',
                metric_name='Requests',  # Generic metric
                dimensions=[],
                days=7
            )
            
            # If no metrics or all zeros, likely unused
            if not metrics:
                return True
            
            avg_value = sum(m.get('Average', 0) for m in metrics) / len(metrics)
            return avg_value < 0.01
            
        except Exception:
            # If we can't determine, mark as unknown (not unused)
            return False
    
    def _map_service_code_to_boto3(self, service_code: str) -> str:
        """
        Map Cost Explorer service code to boto3 service name.
        
        Args:
            service_code: Service code from Cost Explorer
            
        Returns:
            boto3 service name
        """
        # Common mappings
        mapping = {
            'AmazonEC2': 'ec2',
            'AmazonS3': 's3',
            'AmazonRDS': 'rds',
            'AWSLambda': 'lambda',
            'AmazonDynamoDB': 'dynamodb',
            'AmazonElastiCache': 'elasticache',
            'AmazonECS': 'ecs',
            'AmazonEKS': 'eks',
            'AmazonSNS': 'sns',
            'AmazonSQS': 'sqs',
            'AmazonKinesis': 'kinesis',
        }
        
        if service_code in mapping:
            return mapping[service_code]
        
        # Fallback: lowercase and remove 'Amazon'/'AWS' prefix
        service_name = service_code.lower()
        for prefix in ['amazon', 'aws']:
            if service_name.startswith(prefix):
                service_name = service_name[len(prefix):]
        
        return service_name
    
    def _find_list_operations(self, client) -> List[str]:
        """
        Find list/describe operations for a service.
        
        Args:
            client: boto3 client
            
        Returns:
            List of operation names
        """
        operations = []
        
        try:
            # Get all operations from service model
            service_model = client.meta.service_model
            operation_names = service_model.operation_names
            
            # Filter for list/describe operations
            for op in operation_names:
                op_lower = op.lower()
                if any(keyword in op_lower for keyword in ['list', 'describe', 'get']):
                    # Exclude operations that require parameters
                    operation_model = service_model.operation_model(op)
                    required_params = operation_model.input_shape.required_members if operation_model.input_shape else []
                    
                    if not required_params:
                        operations.append(op)
        
        except Exception as e:
            logger.debug(f"Could not introspect service operations: {e}")
        
        return operations
    
    def _call_operation(
        self,
        client,
        operation: str,
        region: str
    ) -> List[Dict[str, Any]]:
        """
        Call a boto3 operation and extract resources.
        
        Args:
            client: boto3 client
            operation: Operation name
            region: AWS region
            
        Returns:
            List of resources
        """
        resources = []
        
        try:
            # Call operation
            response = getattr(client, operation)()
            
            # Extract resources from response
            # Look for common response keys
            for key in response.keys():
                if isinstance(response[key], list) and key not in ['ResponseMetadata']:
                    for item in response[key]:
                        if isinstance(item, dict):
                            resource = {
                                'resource_id': self._extract_resource_id(item),
                                'resource_type': key,
                                'region': region,
                                'status': 'unknown',
                                'estimated_monthly_cost': 0.0,
                                'resource_config': item,
                                'tags': self.extract_tags(item),
                                'last_seen': datetime.utcnow()
                            }
                            resources.append(resource)
        
        except Exception as e:
            logger.debug(f"Operation {operation} failed: {e}")
        
        return resources
    
    def _extract_resource_id(self, resource: Dict[str, Any]) -> str:
        """
        Extract resource ID from resource dict.
        
        Args:
            resource: Resource dictionary
            
        Returns:
            Resource ID string
        """
        # Try common ID field names
        for field in ['Id', 'id', 'ResourceId', 'Arn', 'Name', 'name']:
            if field in resource:
                return str(resource[field])
        
        # Fallback: use first string value
        for value in resource.values():
            if isinstance(value, str):
                return value
        
        return 'unknown'