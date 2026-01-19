from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from models import get_db
from services.budget_service import BudgetService

router = APIRouter()

class BudgetConfig(BaseModel):
    amount: float

@router.get("/budgets")
async def get_budgets(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Get budget status.
    Prioritizes AWS Budgets if available, otherwise returns Native "Soft" Budget.
    """
    service = BudgetService(db)
    return await service.get_budgets()

@router.post("/budgets/config")
async def set_budget_config(config: BudgetConfig, db: AsyncSession = Depends(get_db)):
    """
    Set a local "Soft Budget" limit.
    Used when AWS Budgets are not configured.
    """
    service = BudgetService(db)
    limit = await service.set_limit(config.amount)
    return {"message": "Budget limit set", "amount": limit.amount}


