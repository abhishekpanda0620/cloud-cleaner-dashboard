import asyncio
import logging
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings
from services.budget_service import BudgetService
from models import AsyncSessionLocal
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_budget_alert():
    logger.info("1. Initializing DB Session...")
    async with AsyncSessionLocal() as session:
        bs = BudgetService(session)
        
        # Check initial state
        res = await session.execute(text("SELECT id, amount, current_alert_level, last_alert_sent_at FROM cost_limits ORDER BY id DESC LIMIT 1"))
        row = res.fetchone()
        if row:
            logger.info(f"0. Initial DB State: ID={row[0]}, Level={row[2]}, Last Sent={row[3]}")
        else:
            logger.info("0. Initial DB State: No CostLimit found")

        # Check current state logic
        logger.info("2. Checking and sending alerts...")
        
        # DEBUG: Print budgets
        budgets = await bs.get_budgets()
        logger.info(f"   [DEBUG_SCRIPT] Fetched {len(budgets)} budgets:")
        for b in budgets:
            logger.info(f"     - Name: {b.get('name')}, Type: {b.get('type')}, Status: {b.get('status')}, %: {b.get('percent_used')}")
            
        result = await bs.check_and_send_alerts()
        logger.info(f"   Result: {result}")
        
        if result.get('alerts_sent', 0) > 0:
            logger.info(f"   SUCCESS: {result['alerts_sent']} Alerts Triggered")
        else:
            logger.info("   No alerts sent (no change or no budget exceeded).")

if __name__ == "__main__":
    asyncio.run(debug_budget_alert())
