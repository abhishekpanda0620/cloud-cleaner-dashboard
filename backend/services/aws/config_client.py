"""
AWS Config Client wrapper for resource discovery.

This module provides a high-level interface to AWS Config service
for discovering and querying AWS resources across all services.
"""

import boto3
from typing import List, Dict, Optional, Any
from botocore.exceptions import ClientError
from core.aws_client import get_aws_client_factory
import logging

logger = logging.getLogger(__name__)


class AWSConfigClient:
    """
    Wrapper for AWS Config service to discover resources dynamically.
    
    AWS Config tracks configuration and changes for AWS resources,
    making it perfect for discovering what resources exist without
    needing service-specific code.
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """
        Initialize AWS Config client.
        
        Args:
            region: AWS region (Config is region-specific)
        """
        self.region = region
        factory = get_aws_client_factory()
        self.client = factory.session.client('config', region_name=region)
        
    def list_discovered_resources(
        self,
        resource_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List all discovered resources, optionally filtered by type.
        
        Args:
            resource_type: AWS resource type (e.g., 'AWS::EC2::Instance')
                          If None, returns all resource types
            limit: Maximum number of resources to return
            
        Returns:
            List of resource identifiers with basic info
            
        Example:
            >>> client = AWSConfigClient()
            >>> resources = client.list_discovered_resources('AWS::EC2::Instance')
            >>> print(resources[0])
            {
                'resourceType': 'AWS::EC2::Instance',
                'resourceId': 'i-1234567890abcdef0',
                'resourceName': 'my-instance'
            }
        """
        try:
            params = {
                'limit': limit,
                'includeDeletedResources': False
            }
            
            if resource_type:
                params['resourceType'] = resource_type
            
            resources = []
            paginator = self.client.get_paginator('list_discovered_resources')
            
            for page in paginator.paginate(**params):
                resources.extend(page.get('resourceIdentifiers', []))
                
                if len(resources) >= limit:
                    break
            
            logger.info(f"Discovered {len(resources)} resources of type {resource_type or 'all'}")
            return resources[:limit]
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchConfigurationRecorderException':
                logger.warning(f"AWS Config not enabled in region {self.region}")
                return []
            logger.error(f"Error listing resources: {e}")
            raise
    
    def get_resource_config(
        self,
        resource_type: str,
        resource_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed configuration for a specific resource.
        
        Args:
            resource_type: AWS resource type (e.g., 'AWS::EC2::Instance')
            resource_id: Resource identifier (e.g., 'i-1234567890abcdef0')
            
        Returns:
            Resource configuration dict or None if not found
            
        Example:
            >>> config = client.get_resource_config('AWS::EC2::Instance', 'i-123')
            >>> print(config['configuration']['state']['name'])
            'stopped'
        """
        try:
            response = self.client.get_resource_config_history(
                resourceType=resource_type,
                resourceId=resource_id,
                limit=1,
                laterTime=None,
                earlierTime=None
            )
            
            items = response.get('configurationItems', [])
            if items:
                return items[0]
            
            return None
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotDiscoveredException':
                logger.warning(f"Resource not found: {resource_type}/{resource_id}")
                return None
            logger.error(f"Error getting resource config: {e}")
            raise
    
    def select_resources(
        self,
        query: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query resources using SQL-like syntax.
        
        This is the most powerful method - allows complex queries
        across all resources using SQL-like WHERE clauses.
        
        Args:
            query: SQL-like query string
            limit: Maximum results to return
            
        Returns:
            List of matching resources with their configurations
            
        Example:
            >>> # Find all stopped EC2 instances
            >>> query = '''
            ...     SELECT resourceId, configuration.state.name, configuration.instanceType
            ...     WHERE resourceType = 'AWS::EC2::Instance'
            ...     AND configuration.state.name = 'stopped'
            ... '''
            >>> results = client.select_resources(query)
        """
        try:
            results = []
            paginator = self.client.get_paginator('select_resource_config')
            
            for page in paginator.paginate(Expression=query, Limit=limit):
                results.extend(page.get('Results', []))
                
                if len(results) >= limit:
                    break
            
            # Parse JSON strings in results
            import json
            parsed_results = []
            for result in results[:limit]:
                try:
                    parsed_results.append(json.loads(result))
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse result: {result}")
                    continue
            
            logger.info(f"Query returned {len(parsed_results)} results")
            return parsed_results
            
        except ClientError as e:
            logger.error(f"Error executing query: {e}")
            raise
    
    def get_all_resource_types(self) -> List[str]:
        """
        Get list of all resource types discovered by AWS Config.
        
        Returns:
            List of resource type strings (e.g., ['AWS::EC2::Instance', ...])
        """
        try:
            # Query to get distinct resource types
            query = "SELECT DISTINCT resourceType"
            results = self.select_resources(query, limit=1000)
            
            resource_types = [r.get('resourceType') for r in results if 'resourceType' in r]
            logger.info(f"Found {len(resource_types)} resource types")
            return sorted(set(resource_types))
            
        except Exception as e:
            logger.error(f"Error getting resource types: {e}")
            return []
    
    def find_unused_ec2_instances(self) -> List[Dict[str, Any]]:
        """
        Find stopped EC2 instances (likely unused).
        
        Returns:
            List of stopped EC2 instances with details
        """
        query = """
            SELECT 
                resourceId,
                resourceName,
                configuration.instanceType,
                configuration.state.name,
                configuration.launchTime,
                tags
            WHERE 
                resourceType = 'AWS::EC2::Instance'
                AND configuration.state.name = 'stopped'
        """
        return self.select_resources(query)
    
    def find_unattached_ebs_volumes(self) -> List[Dict[str, Any]]:
        """
        Find unattached EBS volumes (likely unused).
        
        Returns:
            List of available (unattached) EBS volumes
        """
        query = """
            SELECT 
                resourceId,
                configuration.size,
                configuration.volumeType,
                configuration.state,
                configuration.createTime,
                tags
            WHERE 
                resourceType = 'AWS::EC2::Volume'
                AND configuration.state = 'available'
        """
        return self.select_resources(query)
    
    def find_unused_rds_instances(self) -> List[Dict[str, Any]]:
        """
        Find stopped RDS instances (likely unused).
        
        Returns:
            List of stopped RDS instances
        """
        query = """
            SELECT 
                resourceId,
                configuration.dBInstanceClass,
                configuration.engine,
                configuration.dBInstanceStatus,
                tags
            WHERE 
                resourceType = 'AWS::RDS::DBInstance'
                AND configuration.dBInstanceStatus = 'stopped'
        """
        return self.select_resources(query)
    
    def find_unused_elastic_ips(self) -> List[Dict[str, Any]]:
        """
        Find unattached Elastic IPs (costing money but not used).
        
        Returns:
            List of unattached Elastic IPs
        """
        query = """
            SELECT 
                resourceId,
                configuration.publicIp,
                configuration.allocationId,
                tags
            WHERE 
                resourceType = 'AWS::EC2::EIP'
                AND configuration.instanceId IS NULL
        """
        return self.select_resources(query)
    
    def get_resource_count_by_type(self) -> Dict[str, int]:
        """
        Get count of resources grouped by type.
        
        Returns:
            Dict mapping resource type to count
        """
        try:
            query = "SELECT resourceType, COUNT(*) as count GROUP BY resourceType"
            results = self.select_resources(query, limit=1000)
            
            counts = {}
            for result in results:
                resource_type = result.get('resourceType')
                count = result.get('count', 0)
                if resource_type:
                    counts[resource_type] = count
            
            return counts
            
        except Exception as e:
            logger.error(f"Error getting resource counts: {e}")
            return {}