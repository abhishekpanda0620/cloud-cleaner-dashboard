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
            factory = get_aws_client_factory()
            
            # Ensure we have Account ID
            if not settings.aws_account_id:
                try:
                    sts = factory.get_client('sts')
                    settings.aws_account_id = sts.get_caller_identity()['Account']
                except Exception as e:
                    logger.warning(f"Could not determine AWS Account ID: {e}")
                    return []

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

    async def check_and_send_alerts(self) -> Dict[str, Any]:
        """
        Check all budgets (Native + AWS) and trigger alerts if thresholds are exceeded.
        """
        from core.tasks import send_budget_alert_task
        from core.cache import get_redis_client
        import json
        
        alerts_sent = 0
        redis_client = get_redis_client()
        
        # 1. Fetch ALL budgets
        all_budgets = await self.get_budgets()
        
        for budget in all_budgets:
            status = budget.get('status', 'OK')
            percent = budget.get('percent_used', 0)
            budget_name = budget.get('name', 'Unknown Budget')
            budget_type = budget.get('type', 'UNKNOWN')
            
            should_alert = False
            alert_level = "OK"
            
            # Key for tracking state: budget:alert:{type}:{name}
            state_key = f"budget:alert:{budget_type}:{budget_name}"
            
            # Get previous state
            if budget_type == 'NATIVE':
                # For Native, we still prefer DB as source of truth for state to persist across restarts better,
                # but we can use the loop here.
                # Re-fetch native limit to write back logic? 
                # To keep it simple: We delegated native logic to DB in previous code.
                # Let's handle Native specifically to update DB.
                stmt = select(CostLimit).order_by(CostLimit.id.desc()).limit(1)
                result = await self.db.execute(stmt)
                cost_limit = result.scalar_one_or_none()
                if not cost_limit: continue
                
                prev_level = cost_limit.current_alert_level
            else:
                # AWS Budget - Use Redis
                cached_state = redis_client.get(state_key)
                prev_level = cached_state.decode('utf-8') if cached_state else "OK"

            # Determine if we should alert
            if status == "ALARM":
                if prev_level != "ALARM":
                    should_alert = True
                    alert_level = "ALARM"
            elif status == "WARNING":
                if prev_level not in ["WARNING", "ALARM"]:
                    should_alert = True
                    alert_level = "WARNING"
            
            if should_alert:
                logger.info(f"Budget Alert Triggered for {budget_name}: {alert_level} ({percent:.1f}%)")
                
                # Prepare notification config
                email_recipients = []
                if settings.notification_email_recipients:
                    email_recipients = [e.strip() for e in settings.notification_email_recipients.split(',')]
                
                smtp_config = {
                    'smtp_server': settings.smtp_server,
                    'smtp_port': settings.smtp_port,
                    'smtp_username': settings.smtp_username,
                    'smtp_password': settings.smtp_password,
                    'sender_email': settings.sender_email
                }
                
                # Trigger background task
                send_budget_alert_task.delay(
                    alert_level=alert_level,
                    current_spend=budget.get('current_spend', 0),
                    limit_amount=budget.get('limit', 0),
                    currency=budget.get('unit', 'USD'),
                    slack_webhook=settings.slack_webhook_url,
                    email_recipients=email_recipients,
                    smtp_config=smtp_config
                )
                
                # Update State
                if budget_type == 'NATIVE' and cost_limit:
                    cost_limit.current_alert_level = alert_level
                    cost_limit.last_alert_sent_at = datetime.utcnow()
                    await self.db.commit()
                else:
                    # Update Redis (Expire after 7 days to re-alert eventually or keep indefinite?)
                    # Let's keep indefinite or long TTL
                    redis_client.set(state_key, alert_level, ex=86400 * 7)
                
                alerts_sent += 1

        return {"status": "checked", "alerts_sent": alerts_sent}

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

