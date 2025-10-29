"""
Lambda Scanner for identifying unused Lambda functions.

This scanner checks for Lambda functions that are:
- Never invoked
- Have minimal invocations over extended periods
- Have minimal duration/memory usage
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from ..scanner_base import ScannerBase

logger = logging.getLogger(__name__)


class LambdaScanner(ScannerBase):
    """
    Scanner for AWS Lambda functions.
    
    Identifies unused functions based on:
    - No invocations for 7+ days
    - Minimal invocations (< 1 per day)
    - Minimal duration (< 100ms average)
    - Minimal errors (< 1% error rate)
    """
    
    @property
    def service_name(self) -> str:
        return "AWS Lambda"
    
    @property
    def service_code(self) -> str:
        return "AWSLambda"
    
    @property
    def service_category(self) -> str:
        return "Compute"
    
    def scan(self, regions: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Scan for Lambda functions across regions.
        
        Args:
            regions: List of regions to scan. If None, scan all regions.
            
        Returns:
            List of Lambda function resources
        """
        if regions is None:
            regions = self.get_supported_regions()
        
        all_functions = []
        
        for region in regions:
            try:
                functions = self._scan_region(region)
                all_functions.extend(functions)
                logger.info(f"Found {len(functions)} Lambda functions in {region}")
            except Exception as e:
                logger.error(f"Error scanning Lambda in {region}: {e}")
                continue
        
        return all_functions
    
    def _scan_region(self, region: str) -> List[Dict[str, Any]]:
        """
        Scan Lambda functions in a specific region.
        
        Args:
            region: AWS region code
            
        Returns:
            List of Lambda function resources
        """
        functions = []
        
        try:
            lambda_client = self.session.client('lambda', region_name=region)
            
            # List all functions
            paginator = lambda_client.get_paginator('list_functions')
            page_iterator = paginator.paginate()
            
            for page in page_iterator:
                for function in page['Functions']:
                    resource = self._process_function(function, region, lambda_client)
                    functions.append(resource)
        
        except Exception as e:
            logger.error(f"Error describing Lambda functions in {region}: {e}")
            raise
        
        return functions
    
    def _process_function(
        self,
        function: Dict[str, Any],
        region: str,
        lambda_client
    ) -> Dict[str, Any]:
        """
        Process a Lambda function into standardized resource format.
        
        Args:
            function: Lambda function dict from boto3
            region: AWS region
            lambda_client: Lambda client for additional queries
            
        Returns:
            Standardized resource dict
        """
        function_name = function['FunctionName']
        function_arn = function['FunctionArn']
        runtime = function.get('Runtime', 'unknown')
        memory_size = function.get('MemorySize', 128)
        timeout = function.get('Timeout', 3)
        last_modified = function.get('LastModified')
        
        # Extract tags
        tags = function.get('Tags', {})
        
        # Get function metrics
        invocations, errors, duration = self._get_function_metrics(function_name, region)
        
        # Determine if unused
        is_unused = self.identify_unused({
            'FunctionName': function_name,
            'Invocations': invocations,
            'Errors': errors,
            'Duration': duration,
            'LastModified': last_modified
        })
        
        # Estimate monthly cost
        monthly_cost = self.estimate_monthly_cost(memory_size, {
            'memory_size': memory_size,
            'invocations': invocations,
            'duration': duration
        })
        
        return {
            'resource_id': function_arn,
            'resource_type': 'LambdaFunction',
            'region': region,
            'status': 'unused' if is_unused else 'active',
            'estimated_monthly_cost': monthly_cost,
            'resource_config': {
                'function_name': function_name,
                'function_arn': function_arn,
                'runtime': runtime,
                'memory_size': memory_size,
                'timeout': timeout,
                'last_modified': last_modified,
                'handler': function.get('Handler'),
                'code_size': function.get('CodeSize'),
                'invocations_7d': invocations,
                'errors_7d': errors,
                'avg_duration_ms': duration,
            },
            'tags': tags,
            'last_seen': datetime.utcnow()
        }
    
    def _get_function_metrics(
        self,
        function_name: str,
        region: str
    ) -> tuple:
        """
        Get Lambda function metrics from CloudWatch.
        
        Args:
            function_name: Lambda function name
            region: AWS region
            
        Returns:
            Tuple of (invocations, errors, avg_duration_ms)
        """
        try:
            # Get invocations
            invocation_metrics = self.get_cloudwatch_metrics(
                namespace='AWS/Lambda',
                metric_name='Invocations',
                dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
                days=7
            )
            
            invocations = 0
            if invocation_metrics:
                invocations = int(sum(m.get('Sum', 0) for m in invocation_metrics))
            
            # Get errors
            error_metrics = self.get_cloudwatch_metrics(
                namespace='AWS/Lambda',
                metric_name='Errors',
                dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
                days=7
            )
            
            errors = 0
            if error_metrics:
                errors = int(sum(m.get('Sum', 0) for m in error_metrics))
            
            # Get duration
            duration_metrics = self.get_cloudwatch_metrics(
                namespace='AWS/Lambda',
                metric_name='Duration',
                dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
                days=7
            )
            
            duration = 0
            if duration_metrics:
                duration = sum(m.get('Average', 0) for m in duration_metrics) / len(duration_metrics)
            
            return invocations, errors, round(duration, 2)
        
        except Exception as e:
            logger.debug(f"Could not get metrics for function {function_name}: {e}")
            return 0, 0, 0.0
    
    def identify_unused(self, resource: Dict[str, Any]) -> bool:
        """
        Determine if a Lambda function is unused.
        
        A function is considered unused if:
        1. No invocations in 7 days
        2. Less than 1 invocation per day on average
        3. Average duration < 100ms (likely not doing work)
        
        Args:
            resource: Function dict (either from boto3 or standardized format)
            
        Returns:
            True if function is unused
        """
        # Handle both raw boto3 format and standardized format
        if 'FunctionName' in resource:
            # Raw boto3 format
            invocations = resource.get('Invocations', 0)
            duration = resource.get('Duration', 0)
        else:
            # Standardized format
            config = resource.get('resource_config', {})
            invocations = config.get('invocations_7d', 0)
            duration = config.get('avg_duration_ms', 0)
        
        # No invocations in 7 days = unused
        if invocations == 0:
            return True
        
        # Less than 1 invocation per day = likely unused
        if invocations < 7:
            return True
        
        # Very short duration (< 100ms) might indicate unused
        if duration < 100 and invocations < 10:
            return True
        
        return False
    
    def estimate_monthly_cost(
        self,
        resource_type: str,
        resource_config: Dict[str, Any]
    ) -> float:
        """
        Estimate monthly cost for a Lambda function.
        
        Cost factors:
        - Invocations: $0.20 per 1M invocations
        - Duration: $0.0000166667 per GB-second
        
        Args:
            resource_type: Memory size (not used)
            resource_config: Function configuration
            
        Returns:
            Estimated monthly cost in USD
        """
        memory_size = resource_config.get('memory_size', 128)
        invocations = resource_config.get('invocations', 0)
        duration_ms = resource_config.get('duration', 0)
        
        # Extrapolate 7-day metrics to monthly
        monthly_invocations = invocations * (30 / 7)
        
        # Invocation cost: $0.20 per 1M invocations
        invocation_cost = (monthly_invocations / 1_000_000) * 0.20
        
        # Duration cost: $0.0000166667 per GB-second
        # Convert memory from MB to GB
        memory_gb = memory_size / 1024
        # Convert duration from ms to seconds
        duration_seconds = (duration_ms / 1000) * monthly_invocations
        # Calculate cost
        duration_cost = duration_seconds * memory_gb * 0.0000166667
        
        total_cost = invocation_cost + duration_cost
        
        return round(total_cost, 2)
    
    def validate_permissions(self) -> Dict[str, Any]:
        """
        Validate that required IAM permissions are available.
        
        Returns:
            Dict with validation results
        """
        required_permissions = [
            'lambda:ListFunctions',
            'lambda:GetFunction',
            'cloudwatch:GetMetricStatistics'
        ]
        
        try:
            # Try to list functions in one region
            lambda_client = self.session.client('lambda', region_name='us-east-1')
            lambda_client.list_functions(MaxItems=1)
            
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
                    'error': 'Missing Lambda list permissions'
                }
            return {
                'has_permissions': False,
                'missing_permissions': [],
                'error': error_msg
            }