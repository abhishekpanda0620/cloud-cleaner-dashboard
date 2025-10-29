"""
Scan management API endpoints.

Provides endpoints for triggering and monitoring resource discovery scans.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, List, Optional
from datetime import datetime

from models import get_db
from models.scan_history import ScanHistory
from core.config import settings
from core.tasks import discovery_scan_task
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/scan")
async def trigger_scan(
    region: Optional[str] = None,
    lookback_days: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Trigger a full discovery scan.
    
    This will:
    1. Query Cost Explorer for services with costs
    2. Query AWS Config for resources
    3. Identify unused resources
    4. Store everything in database
    
    Args:
        region: AWS region to scan (default: from settings)
        lookback_days: Days to look back for costs (default: from settings)
        
    Returns:
        Scan initiation confirmation
    """
    try:
        region = region or settings.aws_region
        lookback_days = lookback_days or settings.discovery_lookback_days
        
        # Check if a scan is already running
        result = await db.execute(
            select(ScanHistory)
            .where(ScanHistory.status == 'running')
            .order_by(ScanHistory.started_at.desc())
            .limit(1)
        )
        running_scan = result.scalar_one_or_none()
        
        if running_scan:
            return {
                'success': False,
                'message': 'A scan is already running',
                'scan_id': running_scan.id,
                'started_at': running_scan.started_at.isoformat()
            }
        
        # Create scan record
        scan = ScanHistory(
            scan_type='full_discovery',
            status='running',
            started_at=datetime.utcnow()
        )
        db.add(scan)
        await db.commit()
        await db.refresh(scan)
        
        # Run scan synchronously (simpler, works immediately)
        try:
            from services.aws.discovery import AWSServiceDiscoveryEngine
            engine = AWSServiceDiscoveryEngine()
            result = await engine.discover_all(db, lookback_days=lookback_days)
            logger.info(f"Scan {scan.id} completed: {result}")
        except Exception as e:
            logger.error(f"Scan {scan.id} failed: {e}", exc_info=True)
            scan.status = 'failed'
            scan.error_message = str(e)
            scan.completed_at = datetime.utcnow()
            await db.commit()
            raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")
        
        logger.info(f"Scan {scan.id} completed for region {region}")
        
        return {
            'success': True,
            'message': 'Scan initiated successfully',
            'scan_id': scan.id,
            'region': region,
            'lookback_days': lookback_days
        }
        
    except Exception as e:
        logger.error(f"Error initiating scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/scan/status")
async def get_scan_status(
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Get status of the most recent scan.
    
    Returns:
        Current scan status and statistics
    """
    try:
        from services.aws.discovery import AWSServiceDiscoveryEngine
        engine = AWSServiceDiscoveryEngine()
        status = await engine.get_discovery_status(db)
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting scan status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scan/history")
async def get_scan_history(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Get history of discovery scans.
    
    Args:
        limit: Maximum number of records to return
        
    Returns:
        List of scan history records
    """
    try:
        result = await db.execute(
            select(ScanHistory)
            .order_by(ScanHistory.started_at.desc())
            .limit(limit)
        )
        scans = result.scalars().all()
        
        return {
            'scans': [
                {
                    'id': scan.id,
                    'scan_type': scan.scan_type,
                    'status': scan.status,
                    'services_found': scan.services_found,
                    'resources_found': scan.resources_found,
                    'unused_resources': scan.unused_resources,
                    'duration_seconds': scan.duration_seconds,
                    'started_at': scan.started_at.isoformat(),
                    'completed_at': scan.completed_at.isoformat() if scan.completed_at else None,
                    'error_message': scan.error_message
                }
                for scan in scans
            ],
            'total': len(scans)
        }
        
    except Exception as e:
        logger.error(f"Error getting scan history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scan/{scan_id}")
async def get_scan_details(
    scan_id: int,
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Get details of a specific scan.
    
    Args:
        scan_id: Scan history record ID
        
    Returns:
        Scan details
    """
    try:
        result = await db.execute(
            select(ScanHistory).where(ScanHistory.id == scan_id)
        )
        scan = result.scalar_one_or_none()
        
        if not scan:
            raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found")
        
        return {
            'id': scan.id,
            'scan_type': scan.scan_type,
            'status': scan.status,
            'services_found': scan.services_found,
            'resources_found': scan.resources_found,
            'unused_resources': scan.unused_resources,
            'duration_seconds': scan.duration_seconds,
            'started_at': scan.started_at.isoformat(),
            'completed_at': scan.completed_at.isoformat() if scan.completed_at else None,
            'error_message': scan.error_message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scan details: {e}")
        raise HTTPException(status_code=500, detail=str(e))