"""
AWS Service Discovery Engine.

This module orchestrates the discovery of AWS services and resources
using AWS Config and Cost Explorer, storing results in the database.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from models.service import AWSService
from models.resource import Resource
from models.cost_history import CostHistory
from models.scan_history import ScanHistory
from .config_client import AWSConfigClient
from .cost_explorer import CostExplorerClient
from core.config import settings

logger = logging.getLogger(__name__)


class AWSServiceDiscoveryEngine:
    """
    Main engine for discovering AWS services and resources.
    
    This combines AWS Config (for resources) and Cost Explorer (for costs)
    to provide a complete picture of what's being used and how much it costs.
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """
        Initialize discovery engine.
        
        Args:
            region: AWS region to scan
        """
        self.region = region
        self.config_client = AWSConfigClient(region=region)
        self.cost_client = CostExplorerClient()
    
    async def discover_all(
        self,
        db: AsyncSession,
        lookback_days: int = None
    ) -> Dict[str, Any]:
        """
        Complete discovery workflow:
        1. Find services with costs (Cost Explorer)
        2. Discover resources for each service (AWS Config)
        3. Store everything in database
        
        Args:
            db: Database session
            lookback_days: Days to look back for costs (default from settings)
            
        Returns:
            Summary of discovery results
        """
        lookback_days = lookback_days or settings.discovery_lookback_days
        scan_start = datetime.utcnow()
        
        # Create scan history record
        scan = ScanHistory(
            scan_type='full_discovery',
            status='running',
            started_at=scan_start
        )
        db.add(scan)
        await db.commit()
        
        try:
            # Step 1: Discover services with costs
            logger.info(f"Discovering services with costs (last {lookback_days} days)")
            services_with_costs = self.cost_client.get_services_with_costs(
                days=lookback_days,
                min_cost=settings.min_cost_threshold
            )
            
            # Step 2: Store/update services in database
            services_count = await self._store_services(db, services_with_costs)
            
            # Step 3: Discover resources for each service
            logger.info("Discovering resources from AWS Config")
            resources_count = await self._discover_resources(db)
            
            # Step 4: Calculate unused resources
            unused_count = await self._identify_unused_resources(db)
            
            # Update scan record
            scan_end = datetime.utcnow()
            scan.status = 'success'
            scan.services_found = services_count
            scan.resources_found = resources_count
            scan.unused_resources = unused_count
            scan.completed_at = scan_end
            scan.duration_seconds = int((scan_end - scan_start).total_seconds())
            await db.commit()
            
            logger.info(f"Discovery complete: {services_count} services, {resources_count} resources, {unused_count} unused")
            
            return {
                'success': True,
                'services_found': services_count,
                'resources_found': resources_count,
                'unused_resources': unused_count,
                'duration_seconds': scan.duration_seconds
            }
            
        except Exception as e:
            logger.error(f"Discovery failed: {e}")
            scan.status = 'failed'
            scan.error_message = str(e)
            scan.completed_at = datetime.utcnow()
            await db.commit()
            raise
    
    async def _store_services(
        self,
        db: AsyncSession,
        services_with_costs: List[Dict[str, Any]]
    ) -> int:
        """
        Store or update services in database.
        
        Args:
            db: Database session
            services_with_costs: List of services from Cost Explorer
            
        Returns:
            Number of services stored/updated
        """
        now = datetime.utcnow()
        count = 0
        
        for service_data in services_with_costs:
            service_code = service_data['service_code']
            
            # Check if service exists
            result = await db.execute(
                select(AWSService).where(AWSService.service_code == service_code)
            )
            service = result.scalar_one_or_none()
            
            if service:
                # Update existing service
                service.last_seen = now
                service.is_active = True
                service.total_cost_30d = service_data['cost']
            else:
                # Create new service
                service = AWSService(
                    service_code=service_code,
                    service_name=service_data['service_name'],
                    is_active=True,
                    first_seen=now,
                    last_seen=now,
                    total_cost_30d=service_data['cost'],
                    resource_count=0
                )
                db.add(service)
            
            count += 1
        
        await db.commit()
        logger.info(f"Stored/updated {count} services")
        return count
    
    async def _discover_resources(
        self,
        db: AsyncSession
    ) -> int:
        """
        Discover resources using AWS Config.
        
        Args:
            db: Database session
            
        Returns:
            Number of resources discovered
        """
        now = datetime.utcnow()
        total_resources = 0
        
        # Get all active services from database
        result = await db.execute(
            select(AWSService).where(AWSService.is_active == True)
        )
        services = result.scalars().all()
        
        for service in services:
            try:
                # Map service code to AWS Config resource types
                resource_types = self._get_resource_types_for_service(service.service_code)
                
                service_resources = 0
                for resource_type in resource_types:
                    # Discover resources of this type
                    discovered = self.config_client.list_discovered_resources(
                        resource_type=resource_type,
                        limit=1000
                    )
                    
                    for resource_data in discovered:
                        # Get full configuration
                        config = self.config_client.get_resource_config(
                            resource_type=resource_data['resourceType'],
                            resource_id=resource_data['resourceId']
                        )
                        
                        if not config:
                            continue
                        
                        # Store/update resource
                        await self._store_resource(db, service, config, now)
                        service_resources += 1
                
                # Update service resource count
                service.resource_count = service_resources
                total_resources += service_resources
                
            except Exception as e:
                logger.error(f"Error discovering resources for {service.service_code}: {e}")
                continue
        
        await db.commit()
        logger.info(f"Discovered {total_resources} resources")
        return total_resources
    
    async def _store_resource(
        self,
        db: AsyncSession,
        service: AWSService,
        config: Dict[str, Any],
        timestamp: datetime
    ):
        """
        Store or update a resource in database.
        
        Args:
            db: Database session
            service: Parent service
            config: Resource configuration from AWS Config
            timestamp: Current timestamp
        """
        resource_id = config.get('resourceId')
        resource_type = config.get('resourceType')
        region = config.get('awsRegion', self.region)
        
        # Check if resource exists
        result = await db.execute(
            select(Resource).where(
                Resource.resource_id == resource_id,
                Resource.region == region
            )
        )
        resource = result.scalar_one_or_none()
        
        # Extract resource name from tags or configuration
        resource_name = self._extract_resource_name(config)
        
        if resource:
            # Update existing resource
            resource.last_seen = timestamp
            resource.resource_config = config
        else:
            # Create new resource
            resource = Resource(
                service_id=service.id,
                resource_id=resource_id,
                resource_type=resource_type,
                resource_name=resource_name,
                region=region,
                is_unused=False,  # Will be determined in next step
                resource_config=config,
                first_seen=timestamp,
                last_seen=timestamp
            )
            db.add(resource)
    
    async def _identify_unused_resources(
        self,
        db: AsyncSession
    ) -> int:
        """
        Identify which resources are unused based on their state.
        
        Args:
            db: Database session
            
        Returns:
            Number of unused resources found
        """
        unused_count = 0
        
        # Get all resources
        result = await db.execute(select(Resource))
        resources = result.scalars().all()
        
        for resource in resources:
            is_unused, reason = self._check_if_unused(resource)
            
            if is_unused:
                resource.is_unused = True
                resource.unused_reason = reason
                unused_count += 1
            else:
                resource.is_unused = False
                resource.unused_reason = None
        
        await db.commit()
        logger.info(f"Identified {unused_count} unused resources")
        return unused_count
    
    def _check_if_unused(self, resource: Resource) -> tuple[bool, Optional[str]]:
        """
        Check if a resource is unused based on its configuration.
        
        Args:
            resource: Resource to check
            
        Returns:
            Tuple of (is_unused, reason)
        """
        config = resource.resource_config or {}
        resource_type = resource.resource_type
        
        # EC2 Instances
        if resource_type == 'AWS::EC2::Instance':
            state = config.get('configuration', {}).get('state', {}).get('name')
            if state == 'stopped':
                return True, 'Instance is stopped'
        
        # EBS Volumes
        elif resource_type == 'AWS::EC2::Volume':
            state = config.get('configuration', {}).get('state')
            if state == 'available':
                return True, 'Volume is unattached'
        
        # RDS Instances
        elif resource_type == 'AWS::RDS::DBInstance':
            status = config.get('configuration', {}).get('dBInstanceStatus')
            if status == 'stopped':
                return True, 'Database is stopped'
        
        # Elastic IPs
        elif resource_type == 'AWS::EC2::EIP':
            instance_id = config.get('configuration', {}).get('instanceId')
            if not instance_id:
                return True, 'Elastic IP not attached to instance'
        
        # Load Balancers
        elif resource_type == 'AWS::ElasticLoadBalancingV2::LoadBalancer':
            # Check if has targets
            # This would require additional API calls, so mark as potentially unused
            return False, None
        
        return False, None
    
    def _get_resource_types_for_service(self, service_code: str) -> List[str]:
        """
        Map service code to AWS Config resource types.
        
        Args:
            service_code: AWS service code
            
        Returns:
            List of AWS Config resource types
        """
        mapping = {
            'AmazonEC2': [
                'AWS::EC2::Instance',
                'AWS::EC2::Volume',
                'AWS::EC2::EIP',
                'AWS::EC2::SecurityGroup',
                'AWS::EC2::NetworkInterface'
            ],
            'AmazonS3': ['AWS::S3::Bucket'],
            'AmazonRDS': ['AWS::RDS::DBInstance', 'AWS::RDS::DBCluster'],
            'AWSLambda': ['AWS::Lambda::Function'],
            'AmazonDynamoDB': ['AWS::DynamoDB::Table'],
            'AmazonElastiCache': ['AWS::ElastiCache::CacheCluster'],
            'AWSELB': [
                'AWS::ElasticLoadBalancing::LoadBalancer',
                'AWS::ElasticLoadBalancingV2::LoadBalancer'
            ],
            'AmazonVPC': ['AWS::EC2::VPC', 'AWS::EC2::Subnet'],
            'AmazonCloudFront': ['AWS::CloudFront::Distribution'],
            'AmazonRoute53': ['AWS::Route53::HostedZone'],
            'AmazonECS': ['AWS::ECS::Cluster', 'AWS::ECS::Service'],
            'AmazonEKS': ['AWS::EKS::Cluster'],
        }
        
        return mapping.get(service_code, [])
    
    def _extract_resource_name(self, config: Dict[str, Any]) -> str:
        """
        Extract resource name from configuration.
        
        Args:
            config: Resource configuration from AWS Config
            
        Returns:
            Resource name or 'N/A'
        """
        # Try to get name from tags
        tags = config.get('tags', {})
        if 'Name' in tags:
            return tags['Name']
        
        # Try configuration-specific name fields
        configuration = config.get('configuration', {})
        for name_field in ['name', 'dBInstanceIdentifier', 'functionName', 'tableName']:
            if name_field in configuration:
                return configuration[name_field]
        
        return 'N/A'
    
    async def get_discovery_status(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Get status of last discovery scan.
        
        Args:
            db: Database session
            
        Returns:
            Status information
        """
        # Get most recent scan
        result = await db.execute(
            select(ScanHistory)
            .order_by(ScanHistory.started_at.desc())
            .limit(1)
        )
        last_scan = result.scalar_one_or_none()
        
        if not last_scan:
            return {
                'has_run': False,
                'message': 'No scans have been run yet'
            }
        
        return {
            'has_run': True,
            'last_scan_time': last_scan.started_at.isoformat(),
            'status': last_scan.status,
            'services_found': last_scan.services_found,
            'resources_found': last_scan.resources_found,
            'unused_resources': last_scan.unused_resources,
            'duration_seconds': last_scan.duration_seconds,
            'error_message': last_scan.error_message
        }