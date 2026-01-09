"""
AWS Service Discovery Engine (v0.5.0).

This module orchestrates the discovery of AWS services and resources
using Cost Explorer (for service discovery) and Scanner plugins (for resource discovery).

Architecture:
1. Cost Explorer identifies services user actually uses
2. Scanner Registry loads appropriate scanner for each service
3. Scanners discover resources using direct boto3 API calls
4. Results are stored in PostgreSQL database
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
from .cost_explorer import CostExplorerClient
from .scanner_registry import get_scanner_registry
from core.config import settings

logger = logging.getLogger(__name__)


class AWSServiceDiscoveryEngine:
    """
    Main engine for discovering AWS services and resources.
    
    This combines Cost Explorer (for service discovery) and Scanner plugins
    (for resource discovery) to provide a complete picture of what's being used
    and how much it costs.
    
    Workflow:
    1. Cost Explorer identifies services with costs
    2. Scanner Registry loads appropriate scanner for each service
    3. Each scanner discovers resources for that service
    4. Results are stored in database
    5. Unused resources are identified
    """
    
    def __init__(self):
        """Initialize discovery engine."""
        self.cost_client = CostExplorerClient()
        self.scanner_registry = get_scanner_registry()
        self.scanner_registry.load_scanners()
    
    async def discover_all(
        self,
        db: AsyncSession,
        lookback_days: int = None
    ) -> Dict[str, Any]:
        """
        Complete discovery workflow:
        1. Find services with costs (Cost Explorer)
        2. Load appropriate scanner for each service
        3. Discover resources using scanners
        4. Store everything in database
        
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
            
            # Ensure core services are always included
            core_services = [
                {'service_code': 'AmazonS3', 'service_name': 'Amazon Simple Storage Service', 'cost': 0.0, 'period_days': lookback_days},
                {'service_code': 'AmazonEC2', 'service_name': 'Amazon Elastic Compute Cloud', 'cost': 0.0, 'period_days': lookback_days},
                {'service_code': 'AmazonRDS', 'service_name': 'Amazon Relational Database Service', 'cost': 0.0, 'period_days': lookback_days},
                {'service_code': 'AWSLambda', 'service_name': 'AWS Lambda', 'cost': 0.0, 'period_days': lookback_days},
            ]

            # Merge core services with discovered services (prefer discovered data)
            service_map = {s['service_code']: s for s in core_services}
            
            # Update/Overwrite with Cost Explorer data if available
            if services_with_costs:
                for s in services_with_costs:
                    service_map[s['service_code']] = s
            
            services_with_costs = list(service_map.values())
            logger.info(f"Proceeding with {len(services_with_costs)} services (including core services)")
            
            # Step 2: Store/update services in database
            services_count = await self._store_services(db, services_with_costs)
            
            # Update scan record with found services immediately
            scan.services_found = services_count
            await db.commit()
            
            # Step 3: Discover resources for each service using scanners
            logger.info(f"Discovering resources for {services_count} services using scanners")
            resources_count = await self._discover_resources_with_scanners(db, services_with_costs)
            
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
            
            logger.info(
                f"Discovery complete: {services_count} services, "
                f"{resources_count} resources, {unused_count} unused "
                f"({scan.duration_seconds}s)"
            )
            
            return {
                'success': True,
                'services_found': services_count,
                'resources_found': resources_count,
                'unused_resources': unused_count,
                'duration_seconds': scan.duration_seconds
            }
            
        except Exception as e:
            logger.error(f"Discovery failed: {e}", exc_info=True)
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
        Store or update services in database using Upsert.
        
        Args:
            db: Database session
            services_with_costs: List of services from Cost Explorer
            
        Returns:
            Number of services stored/updated
        """
        from sqlalchemy.dialects.postgresql import insert
        
        now = datetime.utcnow()
        count = 0
        
        for service_data in services_with_costs:
            service_code = service_data['service_code']
            service_name = service_data['service_name']
            cost = service_data['cost']
            
            # Prepare upsert statement
            stmt = insert(AWSService).values(
                service_code=service_code,
                service_name=service_name,
                is_active=True,
                first_seen=now,
                last_seen=now,
                total_cost_30d=cost,
                resource_count=0
            )
            
            # On conflict, update existing fields
            stmt = stmt.on_conflict_do_update(
                index_elements=['service_code'],
                set_=dict(
                    last_seen=now,
                    is_active=True,
                    total_cost_30d=cost,
                    # Don't overwrite first_seen or resource_count immediately
                )
            )
            
            await db.execute(stmt)
            count += 1
        
        await db.commit()
        logger.info(f"Stored/updated {count} services")
        return count
    
    async def _discover_resources_with_scanners(
        self,
        db: AsyncSession,
        services_with_costs: List[Dict[str, Any]]
    ) -> int:
        """
        Discover resources using scanner plugins.
        
        For each service with costs:
        1. Get appropriate scanner from registry
        2. Run scanner to discover resources
        3. Store resources in database
        
        Args:
            db: Database session
            services_with_costs: List of services from Cost Explorer
            
        Returns:
            Number of resources discovered
        """
        now = datetime.utcnow()
        total_resources = 0
        
        for service_data in services_with_costs:
            service_code = service_data['service_code']
            service_name = service_data['service_name']
            
            try:
                # Get service from database
                result = await db.execute(
                    select(AWSService).where(AWSService.service_code == service_code)
                )
                service = result.scalar_one_or_none()
                
                if not service:
                    logger.warning(f"Service {service_code} not found in database")
                    continue
                
                # Get scanner for this service
                scanner = self.scanner_registry.get_scanner(
                    service_code=service_code,
                    service_name=service_name
                )
                
                logger.info(f"Scanning {service_code} using {scanner.__class__.__name__}")
                
                # Run scanner
                discovered_resources = scanner.scan()
                
                # Store resources and collect IDs
                service_resources = 0
                discovered_ids = []
                for resource_data in discovered_resources:
                    await self._store_resource(db, service, resource_data, now)
                    service_resources += 1
                    if 'resource_id' in resource_data:
                        discovered_ids.append(resource_data['resource_id'])
                
                # Cleanup stale resources (not seen in this scan)
                # Instead of relying on timestamp (which might not be flushed to DB yet),
                # explicitly exclude the IDs we just found.
                from sqlalchemy import delete
                
                if discovered_ids:
                    delete_stmt = delete(Resource).where(
                        Resource.service_id == service.id,
                        Resource.resource_id.notin_(discovered_ids)
                    )
                else:
                    # If nothing found, delete all resources for this service
                    delete_stmt = delete(Resource).where(
                        Resource.service_id == service.id
                    )
                
                result = await db.execute(delete_stmt)
                deleted_count = result.rowcount
                
                if deleted_count > 0:
                    logger.info(f"Removed {deleted_count} stale resources for {service_code}")

                # Update service resource count
                service.resource_count = service_resources
                total_resources += service_resources
                
                logger.info(f"Discovered {service_resources} resources for {service_code}")
                
            except Exception as e:
                logger.error(f"Error discovering resources for {service_code}: {e}", exc_info=True)
                continue
        
        await db.commit()
        logger.info(f"Discovered {total_resources} total resources")
        return total_resources
    
    async def _store_resource(
        self,
        db: AsyncSession,
        service: AWSService,
        resource_data: Dict[str, Any],
        timestamp: datetime
    ):
        """
        Store or update a resource in database.
        
        Args:
            db: Database session
            service: Parent service
            resource_data: Resource data from scanner (standardized format)
            timestamp: Current timestamp
        """
        resource_id = resource_data.get('resource_id')
        resource_type = resource_data.get('resource_type')
        region = resource_data.get('region', 'us-east-1')
        status = resource_data.get('status', 'unknown')
        estimated_cost = resource_data.get('estimated_monthly_cost', 0.0)
        resource_config = resource_data.get('resource_config', {})
        tags = resource_data.get('tags', {})
        
        # Check if resource exists
        result = await db.execute(
            select(Resource).where(
                Resource.resource_id == resource_id,
                Resource.region == region
            )
        )
        resource = result.scalar_one_or_none()
        
        # Extract resource name from tags or config
        resource_name = tags.get('Name') or resource_config.get('name') or resource_id
        
        if resource:
            # Update existing resource
            resource.last_seen = timestamp
            resource.resource_config = resource_config
            resource.cost_monthly = estimated_cost
        else:
            # Create new resource
            resource = Resource(
                service_id=service.id,
                resource_id=resource_id,
                resource_type=resource_type,
                resource_name=resource_name,
                region=region,
                is_unused=status == 'unused',
                cost_monthly=estimated_cost,
                resource_config=resource_config,
                first_seen=timestamp,
                last_seen=timestamp
            )
            db.add(resource)
    
    async def _identify_unused_resources(
        self,
        db: AsyncSession
    ) -> int:
        """
        Identify which resources are unused.
        
        Note: Scanners already identify unused resources during scanning.
        This method counts them and updates the database.
        
        Args:
            db: Database session
            
        Returns:
            Number of unused resources found
        """
        # Get all unused resources
        result = await db.execute(
            select(Resource).where(Resource.is_unused == True)
        )
        unused_resources = result.scalars().all()
        
        unused_count = len(unused_resources)
        logger.info(f"Identified {unused_count} unused resources")
        
        return unused_count
    
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
    
    def get_scanner_info(self) -> Dict[str, Any]:
        """
        Get information about available scanners.
        
        Returns:
            Dict with scanner information
        """
        return {
            'total_scanners': self.scanner_registry.get_scanner_count(),
            'specific_scanners': self.scanner_registry.list_scanners(),
            'generic_fallback': 'Enabled - new services automatically supported'
        }