from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime
from models import Base

class CostLimit(Base):
    """
    Model for storing user-defined budget/cost limits.
    This acts as a "Secondary" or "Soft" budget system when AWS Budgets
    are not configured.
    """
    __tablename__ = "cost_limits"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)  # The monthly limit in base currency
    warning_threshold = Column(Float, default=80.0)  # Percentage for warning (e.g., 80%)
    alarm_threshold = Column(Float, default=100.0)   # Percentage for alarm (e.g., 100%)
    currency = Column(String, default="USD")
    
    # Alert State Tracking
    last_alert_sent_at = Column(DateTime, nullable=True)
    current_alert_level = Column(String, default="OK")  # OK, WARNING, ALARM
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "warning_threshold": self.warning_threshold,
            "alarm_threshold": self.alarm_threshold,
            "currency": self.currency,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
