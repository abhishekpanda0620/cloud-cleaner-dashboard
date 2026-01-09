from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from models import get_db
from models.savings_history import SavingsHistory
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/savings/summary")
async def get_savings_summary(
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """Get total realized savings summary"""
    try:
        # Total all-time savings (sum of monthly costs of deleted items)
        # Note: This is "Annualized Rate of Savings" technically, 
        # or we can just say "Total Monthly Savings Realized"
        
        result = await db.execute(
            select(func.sum(SavingsHistory.estimated_monthly_cost))
        )
        total_monthly_savings = result.scalar() or 0.0
        
        # Count of deleted resources
        count_result = await db.execute(
            select(func.count(SavingsHistory.id))
        )
        total_items = count_result.scalar() or 0
        
        # Get recent removals (last 30 days)
        last_30_result = await db.execute(
            select(func.sum(SavingsHistory.estimated_monthly_cost))
            .where(SavingsHistory.deleted_at >= datetime.utcnow() - timedelta(days=30))
        )
        last_30_savings = last_30_result.scalar() or 0.0

        return {
            "total_monthly_savings": float(total_monthly_savings),
            "projected_yearly_savings": float(total_monthly_savings * 12),
            "total_items_deleted": total_items,
            "savings_last_30_days": float(last_30_savings)
        }
    except Exception as e:
        logger.error(f"Error getting savings summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/savings/history")
async def get_savings_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
) -> List[Dict]:
    """Get list of recently deleted items and their savings"""
    try:
        result = await db.execute(
            select(SavingsHistory)
            .order_by(SavingsHistory.deleted_at.desc())
            .limit(limit)
        )
        history = result.scalars().all()
        
        return [
            {
                "id": item.id,
                "resource_id": item.resource_id,
                "resource_name": item.resource_name,
                "resource_type": item.resource_type,
                "region": item.region,
                "service_code": item.service_code,
                "estimated_monthly_cost": item.estimated_monthly_cost,
                "deleted_at": item.deleted_at.isoformat()
            }
            for item in history
        ]
    except Exception as e:
        logger.error(f"Error getting savings history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
