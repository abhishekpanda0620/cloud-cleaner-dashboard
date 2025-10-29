from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, DECIMAL, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base

class Resource(Base):
    """Model for AWS resources discovered via AWS Config"""
    __tablename__ = 'resources'
    __table_args__ = (
        UniqueConstraint('resource_id', 'region', name='uq_resource_region'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey('aws_services.id', ondelete='CASCADE'), nullable=False, index=True)
    resource_id = Column(String(255), nullable=False)
    resource_type = Column(String(100), nullable=False)  # AWS::EC2::Instance, etc.
    resource_name = Column(String(255))
    region = Column(String(50), nullable=False, index=True)
    is_unused = Column(Boolean, default=False, index=True)
    unused_reason = Column(String(255))  # Why it's unused (from Config Rule)
    cost_monthly = Column(DECIMAL(10, 2), default=0)
    resource_config = Column(JSONB)  # Full AWS Config data
    first_seen = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    last_seen = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service = relationship("AWSService", back_populates="resources")
    
    def __repr__(self):
        return f"<Resource(id={self.resource_id}, type={self.resource_type}, unused={self.is_unused})>"