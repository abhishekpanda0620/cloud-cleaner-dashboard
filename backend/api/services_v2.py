"""
Dynamic services API endpoints (v2).

Provides endpoints for discovering and managing AWS services dynamically
based on actual usage from Cost Explorer.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from models import get_db
from models.service import AWSService
from models.resource import Resource
from models.cost_history import CostHistory
from services.aws.cost_explorer import CostExplorerClient
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/services")
async def list_services(
    active_only: bool = True,
    min_cost: float = 0.0,
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    List all discovered AWS services.
    
    Args:
        active_only: Only return active services (default: true)
        min_cost: Minimum cost threshold
        
    Returns:
        List of services with metadata
    """
    try:
        query = select(AWSService)
        
        if active_only:
            query = query.where(AWSService.is_active == True)
        
        if min_cost > 0:
            query = query.where(AWSService.total_cost_30d >= min_cost)
        
        query = query.order_by(AWSService.total_cost_30d.desc())
        
        result = await db.execute(query)
        services = result.scalars().all()
        
        return {
            'services': [
                {
                    'service_code': s.service_code,
                    'service_name': s.service_name,
                    'service_category': s.service_category,
                    'is_active': s.is_active,
                    'resource_count': s.resource_count,
                    'total_cost_30d': float(s.total_cost_30d),
                    'first_seen': s.first_seen.isoformat(),
                    'last_seen': s.last_seen.isoformat()
                }
                for s in services
            ],
            'total_services': len(services),
            'total_cost': sum(float(s.total_cost_30d) for s in services)
        }
        
    except Exception as e:
        logger.error(f"Error listing services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services/{service_code}")
async def get_service_details(
    service_code: str,
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Get detailed information about a specific service.
    
    Args:
        service_code: AWS service code (e.g., 'AmazonEC2')
        
    Returns:
        Service details with resource counts and costs
    """
    try:
        result = await db.execute(
            select(AWSService).where(AWSService.service_code == service_code)
        )
        service = result.scalar_one_or_none()
        
        if not service:
            raise HTTPException(status_code=404, detail=f"Service {service_code} not found")
        
        # Get resource counts by type
        resource_result = await db.execute(
            select(
                Resource.resource_type,
                func.count(Resource.id).label('count'),
                func.sum(Resource.cost_monthly).label('total_cost')
            )
            .where(Resource.service_id == service.id)
            .group_by(Resource.resource_type)
        )
        resource_types = resource_result.all()
        
        # Get unused resource count
        unused_result = await db.execute(
            select(func.count(Resource.id))
            .where(Resource.service_id == service.id, Resource.is_unused == True)
        )
        unused_count = unused_result.scalar()
        
        return {
            'service_code': service.service_code,
            'service_name': service.service_name,
            'service_category': service.service_category,
            'is_active': service.is_active,
            'total_resources': service.resource_count,
            'unused_resources': unused_count,
            'total_cost_30d': float(service.total_cost_30d),
            'first_seen': service.first_seen.isoformat(),
            'last_seen': service.last_seen.isoformat(),
            'resource_types': [
                {
                    'type': rt.resource_type,
                    'count': rt.count,
                    'total_cost': float(rt.total_cost) if rt.total_cost else 0.0
                }
                for rt in resource_types
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services/{service_code}/resources")
async def get_service_resources(
    service_code: str,
    unused_only: bool = False,
    region: Optional[str] = None,
    resource_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Get resources for a specific service.
    
    Args:
        service_code: AWS service code
        unused_only: Only return unused resources
        region: Filter by region
        resource_type: Filter by resource type
        limit: Maximum results
        offset: Pagination offset
        
    Returns:
        List of resources
    """
    try:
        # Get service
        service_result = await db.execute(
            select(AWSService).where(AWSService.service_code == service_code)
        )
        service = service_result.scalar_one_or_none()
        
        if not service:
            raise HTTPException(status_code=404, detail=f"Service {service_code} not found")
        
        # Build query
        query = select(Resource).where(Resource.service_id == service.id)
        
        if unused_only:
            query = query.where(Resource.is_unused == True)
        
        if region:
            query = query.where(Resource.region == region)
        
        if resource_type:
            query = query.where(Resource.resource_type == resource_type)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.order_by(Resource.last_seen.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        resources = result.scalars().all()
        
        return {
            'service_code': service_code,
            'service_name': service.service_name,
            'resources': [
                {
                    'id': r.id,
                    'resource_id': r.resource_id,
                    'resource_type': r.resource_type,
                    'resource_name': r.resource_name,
                    'region': r.region,
                    'is_unused': r.is_unused,
                    'unused_reason': r.unused_reason,
                    'cost_monthly': float(r.cost_monthly) if r.cost_monthly else 0.0,
                    'first_seen': r.first_seen.isoformat(),
                    'last_seen': r.last_seen.isoformat()
                }
                for r in resources
            ],
            'total': total,
            'limit': limit,
            'offset': offset
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service resources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services/{service_code}/costs")
async def get_service_costs(
    service_code: str,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Get cost history for a service.
    
    Args:
        service_code: AWS service code
        days: Number of days of history
        
    Returns:
        Daily cost data
    """
    try:
        # Get service
        service_result = await db.execute(
            select(AWSService).where(AWSService.service_code == service_code)
        )
        service = service_result.scalar_one_or_none()
        
        if not service:
            raise HTTPException(status_code=404, detail=f"Service {service_code} not found")
        
        # Get cost history
        cutoff_date = datetime.now().date() - timedelta(days=days)
        
        result = await db.execute(
            select(CostHistory)
            .where(
                CostHistory.service_id == service.id,
                CostHistory.date >= cutoff_date
            )
            .order_by(CostHistory.date)
        )
        costs = result.scalars().all()
        
        return {
            'service_code': service_code,
            'service_name': service.service_name,
            'period_days': days,
            'daily_costs': [
                {
                    'date': c.date.isoformat(),
                    'cost': float(c.cost),
                    'usage_quantity': float(c.usage_quantity) if c.usage_quantity else None,
                    'usage_unit': c.usage_unit
                }
                for c in costs
            ],
            'total_cost': sum(float(c.cost) for c in costs),
            'average_daily_cost': sum(float(c.cost) for c in costs) / len(costs) if costs else 0.0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service costs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services/summary")
async def get_services_summary(
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Get summary statistics for all services.
    
    Returns:
        Aggregate statistics
    """
    try:
        # Get total services
        services_result = await db.execute(
            select(func.count(AWSService.id)).where(AWSService.is_active == True)
        )
        total_services = services_result.scalar()
        
        # Get total resources
        resources_result = await db.execute(
            select(func.count(Resource.id))
        )
        total_resources = resources_result.scalar()
        
        # Get unused resources
        unused_result = await db.execute(
            select(func.count(Resource.id)).where(Resource.is_unused == True)
        )
        unused_resources = unused_result.scalar()
        
        # Get total cost
        cost_result = await db.execute(
            select(func.sum(AWSService.total_cost_30d)).where(AWSService.is_active == True)
        )
        total_cost = cost_result.scalar() or 0.0
        
        # Get top services by cost
        top_services_result = await db.execute(
            select(AWSService)
            .where(AWSService.is_active == True)
            .order_by(AWSService.total_cost_30d.desc())
            .limit(5)
        )
        top_services = top_services_result.scalars().all()
        
        return {
            'total_services': total_services,
            'total_resources': total_resources,
            'unused_resources': unused_resources,
            'total_cost_30d': float(total_cost),
            'potential_savings': float(total_cost) * 0.3,  # Estimate 30% savings from cleanup
            'top_services': [
                {
                    'service_code': s.service_code,
                    'service_name': s.service_name,
                    'cost': float(s.total_cost_30d),
                    'resource_count': s.resource_count
                }
                for s in top_services
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting services summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))