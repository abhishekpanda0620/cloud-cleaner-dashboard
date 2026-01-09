from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any
import boto3
from datetime import datetime

from core.config import settings
from core.aws_client import get_aws_client_factory

router = APIRouter()

@router.get("/budgets")
async def get_budgets() -> List[Dict[str, Any]]:
    """
    Get AWS Budgets status.
    Note: Requires 'budgets:ViewBudget' permission.
    First 2 budgets are free in AWS.
    """
    try:
        if not settings.aws_account_id:
            return []

        factory = get_aws_client_factory()
        client = factory.get_client('budgets')
        
        response = client.describe_budgets(
            AccountId=settings.aws_account_id
        )
        
        budgets = []
        for b in response.get('Budgets', []):
            budget_limit = b.get('BudgetLimit', {})
            current_spend = b.get('CalculatedSpend', {})
            
            limit_amount = float(budget_limit.get('Amount', 0))
            spend_amount = float(current_spend.get('ActualSpend', {}).get('Amount', 0))
            
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Budget: {b.get('BudgetName')} - Limit: {limit_amount}, Spend: {spend_amount}")
            
            percent_used = 0
            if limit_amount > 0:
                percent_used = (spend_amount / limit_amount) * 100
            
            budgets.append({
                "name": b.get('BudgetName'),
                "limit": limit_amount,
                "unit": budget_limit.get('Unit', 'USD'),
                "current_spend": spend_amount,
                "percent_used": percent_used,
                "status": "ALARM" if percent_used >= 100 else "WARNING" if percent_used >= 80 else "OK",
                "time_period_start": b.get('TimePeriod', {}).get('Start'),
                "time_period_end": b.get('TimePeriod', {}).get('End')
            })
            
        return budgets
        
    except Exception as e:
        # If no budgets permission or error, return empty list rather than 500
        # to avoid breaking the dashboard
        print(f"Error fetching budgets: {e}")
        return []
