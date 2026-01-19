import logging
import boto3
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from core.config import settings
from core.aws_client import get_aws_client_factory
from models.cost_limit import CostLimit
from services.aws.cost_explorer import CostExplorerClient

logger = logging.getLogger(__name__)

class BudgetService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.cost_explorer = CostExplorerClient()

    async def get_budgets(self) -> List[Dict[str, Any]]:
        """
        Get budgets from AWS or fallback to local CostLimit.
        AWS Budgets take precedence if configured.
        """
        aws_budgets = self._get_aws_budgets()
        
        # If AWS budgets exist, return them (Source of Truth)
        if aws_budgets:
            return aws_budgets

        # Fallback to local Native Budget
        return await self._get_native_budget()

    def _get_aws_budgets(self) -> List[Dict[str, Any]]:
        """Fetch budgets directly from AWS Budgets API (Sync Boto3)"""
        try:
            if not settings.aws_account_id:
                return []

            factory = get_aws_client_factory()
            client = factory.get_client('budgets')
            
            response = client.describe_budgets(AccountId=settings.aws_account_id)
            
            budgets = []
            for b in response.get('Budgets', []):
                budget_limit = b.get('BudgetLimit', {})
                current_spend = b.get('CalculatedSpend', {})
                
                limit_amount = float(budget_limit.get('Amount', 0))
                spend_amount = float(current_spend.get('ActualSpend', {}).get('Amount', 0))
                
                percent_used = (spend_amount / limit_amount * 100) if limit_amount > 0 else 0
                
                budgets.append({
                    "name": b.get('BudgetName'),
                    "limit": limit_amount,
                    "unit": budget_limit.get('Unit', 'USD'),
                    "current_spend": spend_amount,
                    "percent_used": percent_used,
                    "status": self._calculate_status(percent_used, 80, 100),
                    "time_period_start": b.get('TimePeriod', {}).get('Start'),
                    "time_period_end": b.get('TimePeriod', {}).get('End'),
                    "type": "AWS"
                })
            return budgets
            
        except Exception as e:
            logger.warning(f"Failed to fetch AWS Budgets: {e}")
            return []

    async def _get_native_budget(self) -> List[Dict[str, Any]]:
        """Fetch local budget and calculate status using CostExplorer"""
        stmt = select(CostLimit).order_by(CostLimit.id.desc()).limit(1)
        result = await self.db.execute(stmt)
        cost_limit = result.scalar_one_or_none()
        
        if not cost_limit:
            return []
            
        try:
            # We need MTD cost. 
            summary = self.cost_explorer.get_cost_summary(days=30)
            current_spend = summary.get('total_cost', 0.0)
            
            percent_used = (current_spend / cost_limit.amount * 100) if cost_limit.amount > 0 else 0
            
            start_of_month = date.today().replace(day=1).isoformat()
            
            return [{
                "name": "Monthly Budget (Native)",
                "limit": cost_limit.amount,
                "unit": cost_limit.currency,
                "current_spend": current_spend,
                "percent_used": percent_used,
                "status": self._calculate_status(percent_used, cost_limit.warning_threshold, cost_limit.alarm_threshold),
                "time_period_start": start_of_month,
                "time_period_end": "N/A",  # Recurring
                "type": "NATIVE"
            }]
            
        except Exception as e:
            logger.error(f"Error calculating native budget: {e}")
            return []

    async def set_limit(self, amount: float) -> CostLimit:
        """Create or update the cost limit"""
        # Delete existing (we only support 1 for now)
        await self.db.execute(delete(CostLimit))
        
        new_limit = CostLimit(amount=amount)
        self.db.add(new_limit)
        await self.db.commit()
        await self.db.refresh(new_limit)
        return new_limit

    def _calculate_status(self, percent: float, warning: float, alarm: float) -> str:
        if percent >= alarm:
            return "ALARM"
        if percent >= warning:
            return "WARNING"
        return "OK"

