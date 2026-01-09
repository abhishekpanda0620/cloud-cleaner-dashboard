from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime

from . import Base

class SavingsHistory(Base):
    """
    Tracks historical savings from deleted resources.
    Created when a resource is successfully deleted via the dashboard.
    """
    __tablename__ = "savings_history"

    id = Column(Integer, primary_key=True, index=True)
    
    # Resource details
    resource_id = Column(String, index=True)  # AWS Resource ID (e.g., i-12345678)
    resource_name = Column(String)
    resource_type = Column(String)            # e.g., 'AWS::EC2::Instance'
    region = Column(String)
    service_code = Column(String)             # e.g., 'AmazonEC2'
    
    # Cost details
    estimated_monthly_cost = Column(Float)    # The cost that was being incurred
    
    # Timeline
    deleted_at = Column(DateTime, default=datetime.utcnow)
    deletion_date = Column(Date, default=datetime.utcnow().date) # For easier grouping
    
    def __repr__(self):
        return f"<SavingsHistory {self.resource_id} (${self.estimated_monthly_cost}/mo)>"
