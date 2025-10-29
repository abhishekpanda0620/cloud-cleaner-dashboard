"""
Dynamic resources API endpoints (v2).

Provides endpoints for managing AWS resources discovered via scanner system.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Dict, List, Optional
from datetime import datetime

from models import get_db
from models.resource import Resource
from models.service import AWSService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/resources/summary")
async def get_resources_summary(
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Get summary statistics for all resources.
    
    Returns:
        Aggregate resource statistics
    """
    try:
        # Total resources
        total_result = await db.execute(
            select(func.count(Resource.id))
        )
        total_resources = total_result.scalar()
        
        # Unused resources
        unused_result = await db.execute(
            select(func.count(Resource.id)).where(Resource.is_unused == True)
        )
        unused_resources = unused_result.scalar()
        
        # Total cost
        cost_result = await db.execute(
            select(func.sum(Resource.cost_monthly))
        )
        total_cost = cost_result.scalar() or 0.0
        
        # Unused cost (potential savings)
        unused_cost_result = await db.execute(
            select(func.sum(Resource.cost_monthly)).where(Resource.is_unused == True)
        )
        unused_cost = unused_cost_result.scalar() or 0.0
        
        # Resources by type
        type_result = await db.execute(
            select(
                Resource.resource_type,
                func.count(Resource.id).label('count'),
                func.sum(Resource.cost_monthly).label('cost')
            )
            .group_by(Resource.resource_type)
            .order_by(func.count(Resource.id).desc())
            .limit(10)
        )
        by_type = type_result.all()
        
        # Resources by region
        region_result = await db.execute(
            select(
                Resource.region,
                func.count(Resource.id).label('count'),
                func.sum(Resource.cost_monthly).label('cost')
            )
            .group_by(Resource.region)
            .order_by(func.count(Resource.id).desc())
        )
        by_region = region_result.all()
        
        return {
            'total_resources': total_resources,
            'unused_resources': unused_resources,
            'unused_percentage': (unused_resources / total_resources * 100) if total_resources > 0 else 0.0,
            'total_cost_monthly': float(total_cost),
            'potential_savings': float(unused_cost),
            'by_type': [
                {
                    'resource_type': rt.resource_type,
                    'count': rt.count,
                    'cost': float(rt.cost) if rt.cost else 0.0
                }
                for rt in by_type
            ],
            'by_region': [
                {
                    'region': rr.region,
                    'count': rr.count,
                    'cost': float(rr.cost) if rr.cost else 0.0
                }
                for rr in by_region
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting resources summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resources")
async def list_resources(
    unused_only: bool = False,
    region: Optional[str] = None,
    resource_type: Optional[str] = None,
    service_code: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    List all discovered resources with filtering.
    
    Args:
        unused_only: Only return unused resources
        region: Filter by AWS region
        resource_type: Filter by resource type (e.g., 'AWS::EC2::Instance')
        service_code: Filter by service code (e.g., 'AmazonEC2')
        limit: Maximum results
        offset: Pagination offset
        
    Returns:
        List of resources with metadata
    """
    try:
        # Build query
        query = select(Resource).join(AWSService)
        
        if unused_only:
            query = query.where(Resource.is_unused == True)
        
        if region:
            query = query.where(Resource.region == region)
        
        if resource_type:
            query = query.where(Resource.resource_type == resource_type)
        
        if service_code:
            query = query.where(AWSService.service_code == service_code)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.order_by(Resource.last_seen.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        resources = result.scalars().all()
        
        # Calculate total cost
        total_cost = sum(float(r.estimated_monthly_cost) if r.estimated_monthly_cost else 0.0 for r in resources)
        
        return {
            'resources': [
                {
                    'id': r.id,
                    'resource_id': r.resource_id,
                    'resource_type': r.resource_type,
                    'resource_name': r.resource_name,
                    'region': r.region,
                    'is_unused': r.is_unused,
                    'unused_reason': r.unused_reason,
                    'estimated_monthly_cost': float(r.estimated_monthly_cost) if r.estimated_monthly_cost else 0.0,
                    'service_code': r.service.service_code if r.service else None,
                    'service_name': r.service.service_name if r.service else None,
                    'first_seen': r.first_seen.isoformat(),
                    'last_seen': r.last_seen.isoformat()
                }
                for r in resources
            ],
            'total': total,
            'total_cost': total_cost,
            'limit': limit,
            'offset': offset,
            'filters': {
                'unused_only': unused_only,
                'region': region,
                'resource_type': resource_type,
                'service_code': service_code
            }
        }
        
    except Exception as e:
        logger.error(f"Error listing resources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resources/{resource_id}")
async def get_resource_details(
    resource_id: int,
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Get detailed information about a specific resource.
    
    Args:
        resource_id: Database resource ID
        
    Returns:
        Resource details including full AWS Config data
    """
    try:
        result = await db.execute(
            select(Resource).where(Resource.id == resource_id)
        )
        resource = result.scalar_one_or_none()
        
        if not resource:
            raise HTTPException(status_code=404, detail=f"Resource {resource_id} not found")
        
        return {
            'id': resource.id,
            'resource_id': resource.resource_id,
            'resource_type': resource.resource_type,
            'resource_name': resource.resource_name,
            'region': resource.region,
            'is_unused': resource.is_unused,
            'unused_reason': resource.unused_reason,
            'estimated_monthly_cost': float(resource.estimated_monthly_cost) if resource.estimated_monthly_cost else 0.0,
            'service': {
                'service_code': resource.service.service_code,
                'service_name': resource.service.service_name
            } if resource.service else None,
            'configuration': resource.resource_config,  # Full AWS Config data
            'first_seen': resource.first_seen.isoformat(),
            'last_seen': resource.last_seen.isoformat(),
            'created_at': resource.created_at.isoformat(),
            'updated_at': resource.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting resource details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/resources/{resource_id}")
async def delete_resource(
    resource_id: int,
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Delete a resource from AWS and database.
    
    This will:
    1. Delete the resource from AWS using appropriate API
    2. Remove it from the database
    
    Args:
        resource_id: Database resource ID
        
    Returns:
        Deletion confirmation
    """
    try:
        # Get resource
        result = await db.execute(
            select(Resource).where(Resource.id == resource_id)
        )
        resource = result.scalar_one_or_none()
        
        if not resource:
            raise HTTPException(status_code=404, detail=f"Resource {resource_id} not found")
        
        # TODO: Implement actual AWS resource deletion based on resource type
        # For now, just remove from database
        # In production, you'd call the appropriate AWS API to delete the resource
        
        resource_type = resource.resource_type
        aws_resource_id = resource.resource_id
        region = resource.region
        
        logger.warning(f"Resource deletion not yet implemented for {resource_type}")
        logger.info(f"Would delete {resource_type} {aws_resource_id} in {region}")
        
        # Remove from database
        await db.delete(resource)
        await db.commit()
        
        return {
            'success': True,
            'message': f'Resource {aws_resource_id} removed from database',
            'resource_id': aws_resource_id,
            'resource_type': resource_type,
            'region': region,
            'note': 'AWS resource deletion not yet implemented - only removed from database'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting resource: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resources/types")
async def list_resource_types(
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Get list of all resource types discovered.
    
    Returns:
        List of unique resource types with counts
    """
    try:
        result = await db.execute(
            select(
                Resource.resource_type,
                func.count(Resource.id).label('count')
            )
            .group_by(Resource.resource_type)
            .order_by(Resource.resource_type)
        )
        types = result.all()
        
        return {
            'resource_types': [
                {
                    'type': t.resource_type,
                    'count': t.count
                }
                for t in types
            ],
            'total_types': len(types)
        }
        
    except Exception as e:
        logger.error(f"Error listing resource types: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resources/regions")
async def list_regions(
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Get list of all regions with resources.
    
    Returns:
        List of regions with resource counts
    """
    try:
        result = await db.execute(
            select(
                Resource.region,
                func.count(Resource.id).label('count')
            )
            .group_by(Resource.region)
            .order_by(func.count(Resource.id).desc())
        )
        regions = result.all()
        
        return {
            'regions': [
                {
                    'region': r.region,
                    'resource_count': r.count
                }
                for r in regions
            ],
            'total_regions': len(regions)
        }
        
    except Exception as e:
        logger.error(f"Error listing regions: {e}")
        raise HTTPException(status_code=500, detail=str(e))