from sqlalchemy import Column, Integer, String, TIMESTAMP, Text
from datetime import datetime
from . import Base

class ScanHistory(Base):
    """Model for tracking scan execution history"""
    __tablename__ = 'scan_history'
    
    id = Column(Integer, primary_key=True, index=True)
    scan_type = Column(String(50), nullable=False)  # 'service_discovery', 'resource_scan', etc.
    services_found = Column(Integer, default=0)
    resources_found = Column(Integer, default=0)
    unused_resources = Column(Integer, default=0)
    duration_seconds = Column(Integer)
    status = Column(String(20), nullable=False, index=True)  # 'success', 'failed', 'partial'
    error_message = Column(Text)
    started_at = Column(TIMESTAMP, nullable=False, index=True)
    completed_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ScanHistory(type={self.scan_type}, status={self.status}, started={self.started_at})>"