from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, DECIMAL
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base

class AWSService(Base):
    """Model for AWS services discovered via Cost Explorer"""
    __tablename__ = 'aws_services'
    
    id = Column(Integer, primary_key=True, index=True)
    service_code = Column(String(100), unique=True, nullable=False, index=True)
    service_name = Column(String(100), nullable=False)
    service_category = Column(String(50))
    is_active = Column(Boolean, default=True, index=True)
    resource_count = Column(Integer, default=0)
    first_seen = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    last_seen = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    total_cost_30d = Column(DECIMAL(10, 2), default=0)
    metadata = Column(JSONB)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resources = relationship("Resource", back_populates="service", cascade="all, delete-orphan")
    cost_history = relationship("CostHistory", back_populates="service", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AWSService(code={self.service_code}, name={self.service_name})>"