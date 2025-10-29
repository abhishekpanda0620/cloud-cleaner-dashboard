"""
AWS Cost Explorer Client wrapper for cost tracking and analysis.

This module provides a high-level interface to AWS Cost Explorer
for discovering services with actual costs and tracking cost history.
"""

import boto3
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta, date
from botocore.exceptions import ClientError
from core.aws_client import get_aws_client_factory
import logging

logger = logging.getLogger(__name__)


class CostExplorerClient:
    """
    Wrapper for AWS Cost Explorer service.
    
    Cost Explorer provides actual cost data from AWS billing,
    which we use to discover which services are actually being used.
    """
    
    def __init__(self):
        """
        Initialize Cost Explorer client.
        
        Note: Cost Explorer is a global service (us-east-1 only)
        """
        factory = get_aws_client_factory()
        self.client = factory.session.client('ce', region_name='us-east-1')
    
    def get_services_with_costs(
        self,
        days: int = 30,
        min_cost: float = 0.01
    ) -> List[Dict[str, Any]]:
        """
        Get list of AWS services that have incurred costs.
        
        This is the key method for service discovery - it tells us
        which services the user is actually using based on billing data.
        
        Args:
            days: Number of days to look back
            min_cost: Minimum cost threshold (ignore services below this)
            
        Returns:
            List of services with cost information
            
        Example:
            >>> client = CostExplorerClient()
            >>> services = client.get_services_with_costs(days=30)
            >>> for service in services:
            ...     print(f"{service['service_name']}: ${service['cost']:.2f}")
            Amazon EC2: $123.45
            Amazon S3: $45.67
        """
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                ]
            )
            
            services = []
            for result in response['ResultsByTime']:
                for group in result['Groups']:
                    service_name = group['Keys'][0]
                    cost = float(group['Metrics']['UnblendedCost']['Amount'])
                    
                    # Only include services with meaningful cost
                    if cost >= min_cost:
                        services.append({
                            'service_name': service_name,
                            'service_code': self._map_service_name_to_code(service_name),
                            'cost': cost,
                            'period_days': days
                        })
            
            # Sort by cost descending
            services.sort(key=lambda x: x['cost'], reverse=True)
            
            logger.info(f"Found {len(services)} services with costs >= ${min_cost}")
            return services
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'AccessDeniedException':
                logger.error("Cost Explorer access denied. Enable Cost Explorer in AWS Console.")
                return []
            logger.error(f"Error fetching cost data: {e}")
            raise
    
    def get_daily_costs(
        self,
        service_name: Optional[str] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get daily cost breakdown, optionally for a specific service.
        
        Args:
            service_name: AWS service name (e.g., 'Amazon EC2')
                         If None, returns total costs across all services
            days: Number of days to retrieve
            
        Returns:
            List of daily cost records
            
        Example:
            >>> costs = client.get_daily_costs('Amazon EC2', days=7)
            >>> for day in costs:
            ...     print(f"{day['date']}: ${day['cost']:.2f}")
        """
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            params = {
                'TimePeriod': {
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                'Granularity': 'DAILY',
                'Metrics': ['UnblendedCost']
            }
            
            # Add service filter if specified
            if service_name:
                params['Filter'] = {
                    'Dimensions': {
                        'Key': 'SERVICE',
                        'Values': [service_name]
                    }
                }
            
            response = self.client.get_cost_and_usage(**params)
            
            daily_costs = []
            for result in response['ResultsByTime']:
                cost_date = result['TimePeriod']['Start']
                cost = float(result['Total']['UnblendedCost']['Amount'])
                
                daily_costs.append({
                    'date': cost_date,
                    'cost': cost,
                    'service': service_name or 'All Services'
                })
            
            return daily_costs
            
        except ClientError as e:
            logger.error(f"Error fetching daily costs: {e}")
            raise
    
    def get_cost_forecast(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get cost forecast for upcoming period.
        
        Args:
            days: Number of days to forecast
            
        Returns:
            Forecast data with predicted costs
        """
        try:
            start_date = date.today()
            end_date = start_date + timedelta(days=days)
            
            response = self.client.get_cost_forecast(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Metric='UNBLENDED_COST',
                Granularity='MONTHLY'
            )
            
            forecast_cost = float(response['Total']['Amount'])
            
            return {
                'forecast_cost': forecast_cost,
                'period_days': days,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
            
        except ClientError as e:
            logger.error(f"Error fetching cost forecast: {e}")
            raise
    
    def get_cost_by_region(
        self,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get costs grouped by AWS region.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of regions with their costs
        """
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'REGION'}
                ]
            )
            
            regions = []
            for result in response['ResultsByTime']:
                for group in result['Groups']:
                    region = group['Keys'][0]
                    cost = float(group['Metrics']['UnblendedCost']['Amount'])
                    
                    if cost > 0:
                        regions.append({
                            'region': region,
                            'cost': cost
                        })
            
            # Sort by cost descending
            regions.sort(key=lambda x: x['cost'], reverse=True)
            return regions
            
        except ClientError as e:
            logger.error(f"Error fetching regional costs: {e}")
            raise
    
    def _map_service_name_to_code(self, service_name: str) -> str:
        """
        Map Cost Explorer service name to AWS service code.
        
        Cost Explorer uses display names like "Amazon Elastic Compute Cloud - Compute"
        but we need service codes like "AmazonEC2" for consistency.
        
        Args:
            service_name: Service name from Cost Explorer
            
        Returns:
            Service code string
        """
        # Common mappings
        mapping = {
            'Amazon Elastic Compute Cloud - Compute': 'AmazonEC2',
            'Amazon Simple Storage Service': 'AmazonS3',
            'Amazon Relational Database Service': 'AmazonRDS',
            'AWS Lambda': 'AWSLambda',
            'Amazon ElastiCache': 'AmazonElastiCache',
            'Amazon DynamoDB': 'AmazonDynamoDB',
            'Amazon CloudFront': 'AmazonCloudFront',
            'Amazon Route 53': 'AmazonRoute53',
            'Elastic Load Balancing': 'AWSELB',
            'Amazon Virtual Private Cloud': 'AmazonVPC',
            'AWS Key Management Service': 'awskms',
            'Amazon CloudWatch': 'AmazonCloudWatch',
            'AWS Identity and Access Management': 'AWSIAMIdentityCenter',
            'Amazon Elastic Container Service': 'AmazonECS',
            'Amazon Elastic Kubernetes Service': 'AmazonEKS',
            'Amazon Simple Notification Service': 'AmazonSNS',
            'Amazon Simple Queue Service': 'AmazonSQS',
            'AWS Step Functions': 'AWSStepFunctions',
            'Amazon API Gateway': 'AmazonAPIGateway',
            'AWS Secrets Manager': 'AWSSecretsManager',
            'Amazon Kinesis': 'AmazonKinesis',
            'Amazon Redshift': 'AmazonRedshift',
            'Amazon Elasticsearch Service': 'AmazonES',
            'AWS Glue': 'AWSGlue',
            'Amazon Athena': 'AmazonAthena',
            'AWS Data Transfer': 'AWSDataTransfer',
            'AWS Config': 'AWSConfig',
            'AWS CloudTrail': 'AWSCloudTrail',
            'Amazon GuardDuty': 'AmazonGuardDuty',
            'AWS WAF': 'AWSWAF',
            'AWS Shield': 'AWSShield',
        }
        
        # Try exact match first
        if service_name in mapping:
            return mapping[service_name]
        
        # Fallback: remove spaces and special characters
        service_code = service_name.replace(' ', '').replace('-', '')
        
        # Remove common prefixes
        for prefix in ['Amazon', 'AWS', 'Elastic']:
            if service_code.startswith(prefix):
                service_code = service_code[len(prefix):]
                break
        
        return service_code or service_name
    
    def get_cost_summary(self, days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive cost summary.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with total cost, service breakdown, and trends
        """
        try:
            services = self.get_services_with_costs(days=days, min_cost=0.01)
            daily_costs = self.get_daily_costs(days=days)
            
            total_cost = sum(s['cost'] for s in services)
            
            # Calculate trend (compare first half vs second half)
            mid_point = len(daily_costs) // 2
            first_half_avg = sum(d['cost'] for d in daily_costs[:mid_point]) / mid_point if mid_point > 0 else 0
            second_half_avg = sum(d['cost'] for d in daily_costs[mid_point:]) / (len(daily_costs) - mid_point) if mid_point > 0 else 0
            
            trend = 'increasing' if second_half_avg > first_half_avg else 'decreasing'
            trend_percent = ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg > 0 else 0
            
            return {
                'total_cost': total_cost,
                'period_days': days,
                'service_count': len(services),
                'top_services': services[:5],  # Top 5 by cost
                'daily_average': total_cost / days,
                'trend': trend,
                'trend_percent': trend_percent,
                'daily_costs': daily_costs
            }
            
        except Exception as e:
            logger.error(f"Error generating cost summary: {e}")
            raise