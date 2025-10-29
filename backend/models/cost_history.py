from sqlalchemy import Column, Integer, Date, DECIMAL, String, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base

class CostHistory(Base):
    """Model for tracking daily costs per service"""
    __tablename__ = 'cost_history'
    __table_args__ = (
        UniqueConstraint('service_id', 'date', name='uq_service_date'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey('aws_services.id', ondelete='CASCADE'), nullable=False)
    date = Column(Date, nullable=False, index=True)
    cost = Column(DECIMAL(10, 2), nullable=False)
    usage_quantity = Column(DECIMAL(15, 4))
    usage_unit = Column(String(50))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    service = relationship("AWSService", back_populates="cost_history")
    
    def __repr__(self):
        return f"<CostHistory(service_id={self.service_id}, date={self.date}, cost={self.cost})>"