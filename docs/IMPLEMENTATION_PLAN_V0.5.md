
# Cloud Cleaner v0.5.0 - Implementation Plan

## Overview

This document provides a step-by-step implementation plan for migrating from the hardcoded resource system to a dynamic service-discovery architecture.

## Prerequisites

- PostgreSQL 15+ (will be added to docker-compose)
- Alembic for database migrations
- AWS Cost Explorer API access (requires AWS Cost Explorer to be enabled)

## Phase 1: Database Setup

### Step 1.1: Update docker-compose.yml

Add PostgreSQL service:

```yaml
services:
  postgres:
    image: postgres:15-alpine
    container_name: cloud-cleaner-postgres
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=cloud_cleaner
      - POSTGRES_USER=cloud_cleaner
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-changeme}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - cloud-cleaner-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U cloud_cleaner"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### Step 1.2: Update requirements.txt

Add database dependencies:

```txt
alembic==1.13.1
asyncpg==0.29.0
```

### Step 1.3: Create Database Models

File: `backend/models/__init__.py`

```python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from core.config import settings

Base = declarative_base()

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db():
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

File: `backend/models/service.py`

```python
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, DECIMAL, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base

class AWSService(Base):
    __tablename__ = 'aws_services'
    
    id = Column(Integer, primary_key=True, index=True)
    service_code = Column(String(100), unique=True, nullable=False, index=True)
    service_name = Column(String(100), nullable=False)
    service_category = Column(String(50))
    is_active = Column(Boolean, default=True, index=True)
    has_handler = Column(Boolean, default=False)
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
```

File: `backend/models/resource.py`

```python
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, DECIMAL, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base

class Resource(Base):
    __tablename__ = 'resources'
    __table_args__ = (
        UniqueConstraint('service_id', 'resource_id', 'region', name='uq_service_resource_region'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey('aws_services.id', ondelete='CASCADE'), nullable=False, index=True)
    resource_id = Column(String(255), nullable=False)
    resource_type = Column(String(100))
    resource_name = Column(String(255))
    region = Column(String(50), nullable=False, index=True)
    state = Column(String(50))
    is_unused = Column(Boolean, default=False, index=True)
    cost_monthly = Column(DECIMAL(10, 2), default=0)
    metadata = Column(JSONB)
    first_seen = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    last_seen = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service = relationship("AWSService", back_populates="resources")
    
    def __repr__(self):
        return f"<Resource(id={self.resource_id}, type={self.resource_type}, unused={self.is_unused})>"
```

File: `backend/models/cost_history.py`

```python
from sqlalchemy import Column, Integer, Date, DECIMAL, String, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base

class CostHistory(Base):
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
```

File: `backend/models/scan_history.py`

```python
from sqlalchemy import Column, Integer, String, TIMESTAMP, Text
from datetime import datetime
from . import Base

class ScanHistory(Base):
    __tablename__ = 'scan_history'
    
    id = Column(Integer, primary_key=True, index=True)
    scan_type = Column(String(50), nullable=False)
    region = Column(String(50))
    services_found = Column(Integer, default=0)
    resources_found = Column(Integer, default=0)
    duration_seconds = Column(Integer)
    status = Column(String(20), nullable=False, index=True)
    error_message = Column(Text)
    started_at = Column(TIMESTAMP, nullable=False, index=True)
    completed_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ScanHistory(type={self.scan_type}, status={self.status}, started={self.started_at})>"
```

### Step 1.4: Setup Alembic

Initialize Alembic:

```bash
cd backend
alembic init alembic
```

Update `alembic/env.py`:

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from core.config import settings
from models import Base
from models.service import AWSService
from models.resource import Resource
from models.cost_history import CostHistory
from models.scan_history import ScanHistory

# this is the Alembic Config object
config = context.config

# Set database URL from settings
config.set_main_option('sqlalchemy.url', settings.database_url.replace('+asyncpg', ''))

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here
target_metadata = Base.metadata

# ... rest of alembic env.py
```

Create initial migration:

```bash
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

## Phase 2: Service Discovery Engine

### Step 2.1: Create Service Discovery Module

File: `backend/services/__init__.py`

```python
from .registry import ServiceHandlerRegistry
from .base import ServiceHandler
from .discovery import ServiceDiscoveryEngine

__all__ = ['ServiceHandlerRegistry', 'ServiceHandler', 'ServiceDiscoveryEngine']
```

File: `backend/services/discovery.py`

```python
import boto3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.service import AWSService
from models.cost_history import CostHistory
from models.scan_history import ScanHistory
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class ServiceDiscoveryEngine:
    """
    Discovers AWS services by querying Cost Explorer for actual usage
    """
    
    def __init__(self):
        self.ce_client = boto3.client('ce', region_name='us-east-1')
    
    async def discover_services(
        self, 
        db: AsyncSession,
        days: int = 30,
        min_cost: float = 0.01
    ) -> List[Dict]:
        """
        Query Cost Explorer to find services with actual costs
        
        Args:
            db: Database session
            days: Number of days to look back
            min_cost: Minimum cost threshold to consider a service active
            
        Returns:
            List of discovered services with metadata
        """
        scan_start = datetime.utcnow()
        scan_record = ScanHistory(
            scan_type='service_discovery',
            status='running',
            started_at=scan_start
        )
        db.add(scan_record)
        await db.commit()
        
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            logger.info(f"Querying Cost Explorer from {start_date} to {end_date}")
            
            # Query Cost Explorer grouped by SERVICE
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                ]
            )
            
            discovered_services = []
            
            for result in response['ResultsByTime']:
                for group in result['Groups']:
                    service_name = group['Keys'][0]
                    cost = float(group['Metrics']['UnblendedCost']['Amount'])
                    
                    # Only track services with meaningful cost
                    if cost >= min_cost:
                        # Map service name to service code
                        service_code = self._map_service_name_to_code(service_name)
                        
                        discovered_services.append({
                            'service_code': service_code,
                            'service_name': service_name,
                            'total_cost': cost,
                            'period_days': days
                        })
            
            # Update database with discovered services
            services_count = await self._update_services_in_db(db, discovered_services)
            
            # Update scan record
            scan_end = datetime.utcnow()
            scan_record.status = 'success'
            scan_record.services_found = services_count
            scan_record.completed_at = scan_end
            scan_record.duration_seconds = int((scan_end - scan_start).total_seconds())
            await db.commit()
            
            logger.info(f"Discovered {services_count} active services")
            return discovered_services
            
        except Exception as e:
            logger.error(f"Error discovering services: {e}")
            scan_record.status = 'failed'
            scan_record.error_message = str(e)
            scan_record.completed_at = datetime.utcnow()
            await db.commit()
            raise
    
    async def _update_services_in_db(
        self, 
        db: AsyncSession, 
        services: List[Dict]
    ) -> int:
        """Update or create services in database"""
        count = 0
        now = datetime.utcnow()
        
        for service_data in services:
            # Check if service exists
            result = await db.execute(
                select(AWSService).where(
                    AWSService.service_code == service_data['service_code']
                )
            )
            service = result.scalar_one_or_none()
            
            if service:
                # Update existing service
                service.last_seen = now
                service.is_active = True
                service.total_cost_30d = service_data['total_cost']
            else:
                # Create new service
                service = AWSService(
                    service_code=service_data['service_code'],
                    service_name=service_data['service_name'],
                    is_active=True,
                    first_seen=now,
                    last_seen=now,
                    total_cost_30d=service_data['total_cost']
                )
                db.add(service)
            
            count += 1
        
        await db.commit()
        return count
    
    def _map_service_name_to_code(self, service_name: str) -> str:
        """Map Cost Explorer service name to AWS service code"""
        # Common mappings
        mapping = {
            'Amazon Elastic Compute Cloud - Compute': 'AmazonEC2',
            'Amazon Simple Storage Service': 'AmazonS3',
            'Amazon Relational Database Service': 'AmazonRDS',
            'AWS Lambda': 'AWSLambda',
            'Amazon ElastiCache': 'AmazonElastiCache',
            'Amazon DynamoDB': 'AmazonDynamoDB',
            'Amazon CloudFront': 'AmazonCloudFront',
            'Amazon Route 53': 'AmazonRoute53',
            'Elastic Load Balancing': 'AWSELB',
            'Amazon Virtual Private Cloud': 'AmazonVPC',
            'AWS Key Management Service': 'awskms',
            'Amazon CloudWatch': 'AmazonCloudWatch',
            'AWS Identity and Access Management': 'AWSIAMIdentityCenter',
        }
        
        return mapping.get(service_name, service_name.replace(' ', ''))
    
    async def get_service_cost_history(
        self,
        db: AsyncSession,
        service_code: str,
        days: int = 30
    ) -> List[Dict]:
        """Get cost history for a specific service"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            # Get service from database
            result = await db.execute(
                select(AWSService).where(AWSService.service_code == service_code)
            )
            service = result.scalar_one_or_none()
            
            if not service:
                return []
            
            # Query Cost Explorer for this specific service
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['UnblendedCost'],
                Filter={
                    'Dimensions': {
                        'Key': 'SERVICE',
                        'Values': [service.service_name]
                    }
                }
            )
            
            cost_data = []
            for result in response['ResultsByTime']:
                date = result['TimePeriod']['Start']
                cost = float(result['Metrics']['UnblendedCost']['Amount'])
                
                cost_data.append({
                    'date': date,
                    'cost': cost
                })
                
                # Store in database
                cost_record = CostHistory(
                    service_id=service.id,
                    date=datetime.strptime(date, '%Y-%m-%d').date(),
                    cost=cost
                )
                db.add(cost_record)
            
            await db.commit()
            return cost_data
            
        except Exception as e:
            logger.error(f"Error fetching cost history for {service_code}: {e}")
            return []
```

## Phase 3: Service Handler System

### Step 3.1: Base Handler Class

File: `backend/services/base.py`

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession

class ServiceHandler(ABC):
    """Base class for AWS service handlers"""
    
    service_code: str  # e.g., "AmazonEC2"
    service_name: str  # e.g., "EC2"
    service_category: str  # e.g., "Compute"
    
    @abstractmethod
    async def scan_unused_resources(
        self, 
        db: AsyncSession,
        region: str
    ) -> List[Dict]:
        """
        Scan for unused resources of this service type
        
        Args:
            db: Database session
            region: AWS region to scan
            
        Returns:
            List of unused resources with metadata
        """
        pass
    
    @abstractmethod
    async def get_resource_cost(
        self, 
        resource: Dict,
        region: str
    ) -> float:
        """
        Calculate monthly cost for a specific resource
        
        Args:
            resource: Resource metadata
            region: AWS region
            
        Returns:
            Estimated monthly cost in USD
        """
        pass
    
    @abstractmethod
    async def delete_resource(
        self, 
        resource_id: str,
        region: str
    ) -> bool:
        """
        Delete a specific resource
        
        Args:
            resource_id: AWS resource ID
            region: AWS region
            
        Returns:
            True if deletion successful
        """
        pass
    
    async def get_resource_details(
        self,
        resource_id: str,
        region: str
    ) -> Optional[Dict]:
        """
        Get detailed information about a resource (optional override)
        
        Args:
            resource_id: AWS resource ID
            region: AWS region
            
        Returns:
            Resource details or None
        """
        return None
```

### Step 3.2: Handler Registry

File: `backend/services/registry.py`

```python
from typing import Dict, Optional, List
from .base import ServiceHandler
import logging

logger = logging.getLogger(__name__)

class ServiceHandlerRegistry:
    """Registry for AWS service handlers"""
    
    _handlers: Dict[str, ServiceHandler] = {}
    
    @classmethod
    def register(cls, handler: ServiceHandler):
        """
        Register a handler for a service
        
        Args:
            handler: ServiceHandler instance
        """
        service_code = handler.service_code
        cls._handlers[service_code] = handler
        logger.info(f"Registered handler for {service_code}")
    
    @classmethod
    def get_handler(cls, service_code: str) -> Optional[ServiceHandler]:
        """
        Get handler for a service
        
        Args:
            service_code: AWS service code
            
        Returns:
            ServiceHandler instance or None
        """
        return cls._handlers.get(service_code)
    
    @classmethod
    def get_all_handlers(cls) -> Dict[str, ServiceHandler]:
        """Get all registered handlers"""
        return cls._handlers.copy()
    
    @classmethod
    def list_supported_services(cls) -> List[str]:
        """Get list of service codes with handlers"""
        return list(cls._handlers.keys())
    
    @classmethod
    def has_handler(cls, service_code: str) -> bool:
        """Check if handler exists for service"""
        return service_code in cls._handlers
```

## Phase 4: Example Handler Implementation

File: `backend/services/ec2_handler.py`

```python
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import boto3
from datetime import datetime, timezone, timedelta
from .base import ServiceHandler
from .registry import ServiceHandlerRegistry
from models.service import AWSService
from models.resource import Resource
from core.aws_client import get_aws_client_factory
import logging

logger = logging.getLogger(__name__)

class EC2Handler(ServiceHandler):
    """Handler for Amazon EC2 service"""
    
    service_code = "AmazonEC2"
    service_name = "EC2"
    service_category = "Compute"
    
    async def scan_unused_resources(
        self, 
        db: AsyncSession,
        region: str
    ) -> List[Dict]:
        """Scan for stopped EC2 instances"""
        try:
            factory = get_aws_client_factory()
            ec2_client = factory.session.client('ec2', region_name=region)
            
            # Get service from database
            result = await db.execute(
                select(AWSService).where(AWSService.service_code == self.service_code)
            )
            service = result.scalar_one_or_none()
            
            if not service:
                logger.warning(f"Service {self.service_code} not found in database")
                return []
            
            # Get stopped instances
            response = ec2_client.describe_instances(
                Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}]
            )
            
            unused_resources = []
            now = datetime.utcnow()
            
            for reservation in response.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    instance_id = instance.get('InstanceId')
                    instance_type = instance.get('InstanceType', 'unknown')
                    state_reason = instance.get('StateTransitionReason', '')
                    
                    # Only consider user-stopped instances
                    if 'User initiated' not in state_reason:
                        continue
                    
                    # Get instance name
                    instance_name = 'N/A'
                    for tag in instance.get('Tags', []):
                        if tag.get('Key') == 'Name':
                            instance_name = tag.get('Value', 'N/A')
                            break
                    
                    # Calculate cost
                    cost = await self.get_resource_cost(
                        {'instance_type': instance_type},
                        region
                    )
                    
                    resource_data = {
                        'resource_id': instance_id,
                        'resource_type': 'instance',
                        'resource_name': instance_name,
                        'instance_type': instance_type,
                        'state': 'stopped',
                        'cost_monthly': cost
                    }
                    
                    # Update or create in database
                    result = await db.execute(
                        select(Resource).where(
                            Resource.service_id == service.id,
                            Resource.resource_id == instance_id,
                            Resource.region == region
                        )
                    )
                    resource = result.scalar_one_or_none()
                    
                    if resource:
                        resource.last_seen = now
                        resource.is_unused = True
                        resource.cost_monthly = cost
                        resource.metadata = resource_data
                    else:
                        resource = Resource(
                            service_id=service.id,
                            resource_id=instance_id,
                            resource_type='instance',
                            resource_name=instance_name,
                            region=region,
                            state='stopped',
                            is_unused=True,
                            cost_monthly=cost,
                            metadata=resource_data,
                            first_seen=now,
                            last_seen=now
                        )
                        db.add(resource)
                    
                    unused_resources.append(resource_data)
            
            await db.commit()
            logger.info(f"Found {len(unused_resources)} unused EC2 instances in {region}")
            return unused_resources
            
        except Exception as e:
            logger.error(f"Error scanning EC2 resources: {e}")
            return []
    
    async def get_resource_cost(self, resource: Dict, region: str) -> float:
        """Calculate EC2 instance cost"""
        # Simplified - use AWS Pricing API in production
        instance_type = resource.get('instance_type', 't2.micro')
        
        # Basic cost estimates (monthly)
        cost_map = {
            't2.micro': 8.50,
            't2.small': 17.00,
            't2.medium': 34.00,
            't3.micro': 7.50,
            't3.small': 15.00,
            't3.medium': 30.00,
        }
        
        return cost_map.get(instance_type, 20.00)
    
    async def delete_resource(self, resource_id: str, region: str) -> bool:
        """Terminate EC2 instance"""
        try:
            factory = get_aws_client_factory()
            ec2_client = factory.session.client('ec2', region_name=region)
            
            ec2_client.terminate_instances(InstanceIds=[resource_id])
            logger.info(f"Terminated EC2 instance {resource_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error terminating instance {resource_id}: {e}")
            return False

# Auto-register handler
ServiceHandlerRegistry.register(EC2Handler())
```

## Phase 5: New API Endpoints

File: `backend/api/services.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict
from models import get_db
from models.service import AWSService
from models.resource import Resource
from services.discovery import ServiceDiscoveryEngine
from services.registry import ServiceHandlerRegistry
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/services")
async def list_services(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """List all discovered AWS services"""
    try:
        query = select(AWSService)
        if active_only:
            query = query.where(AWSService.is_active == True)
        
        result = await db.execute(query.order_by(AWSService.service_name))
        services = result.scalars().all()
        
        return {
            "services": [
                {
                    "service_code": s.service_code,
                    "service_name": s.service_name,
                    "service_category": s.service_category,
                    "is_active": s.is_active,
                    "has_handler": ServiceHandlerRegistry.has_handler(s.service_code),
                    "total_cost_30d": float(s.total_cost_30d),
                    "first_seen": s.first_seen.isoformat(),
                    "last_seen": s.last_seen.isoformat()
                }
                for s in services
            ],
            "total_services": len(services)
        }
    except Exception as e:
        logger.error(f"Error listing services: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/services/{service_code}/resources")
async def get_service_resources(
    service_code: str,
    region: str = None,
    unused_only: bool = True,
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """Get resources for a specific service"""
    try:
        # Get service
        result = await db.execute(
            select(AWSService).where(AWSService.service_code == service_code)
        )
        service = result.scalar_one_or_none()
        
        if not service:
            raise HTTPException(status_code=404, detail=f"Service {service_code} not found")
        
        # Build query
        query = select(Resource).where(Resource.service_id == service.id)
        if unused_only:
            query = query.where(Resource.is_unused == True)
        if region:
            query = query.where(Resource.region == region)
        
        result = await db.execute(query.order_by(Resource.last_seen.desc()))
        resources = result.scalars().all()
        
        return {
            "service_code": service_code,
            "service_name": service.service_name,
            "resources": [
                {
                    "id": r.id,
                    "resource_id": r.resource_id,
                    "resource_type": r.resource_type,
                    "resource_name": r.resource_name,
                    "region": r.region,
                    "state": r.state,
                    "is_unused": r.is_unused,
                    "cost_monthly": float(r.cost_monthly),
                    "metadata": r.metadata,
                    "last_seen": r.last_seen.isoformat()
                }
                for r in resources
            ],
            "total_resources": len(resources)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service resources: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scan")
async def trigger_scan(
    region: str = None,
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """Trigger service discovery and resource scan"""
    try:
        engine = ServiceDiscoveryEngine()
        
        # Discover services
        services = await engine.discover_services(db)
        
        # Scan resources for each service with handler
        total_resources = 0
        for service_data in services:
            service_code = service_data['service_code']
            handler = ServiceHandlerRegistry.get_handler(service_code)
            
            if handler:
                resources = await handler.scan_unused_resources(db, region or 'us-east-1')
                total_resources += len(resources)
        
        return {
            "success": True,
            "services_discovered": len(services),
            "resources_found":