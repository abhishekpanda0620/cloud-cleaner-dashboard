# Cloud Cleaner Dashboard - Dynamic Service Discovery Architecture (v0.5.0)

## Overview

This document outlines the architecture for transforming Cloud Cleaner from a hardcoded, resource-centric system to a dynamic, service-discovery system that automatically detects and tracks AWS services actually being used by the user.

## Current Problems

1. **Hardcoded Resource Types**: Only supports EC2, EBS, S3, IAM, IAM Users, Access Keys
2. **Not Scalable**: Adding new services requires code changes in multiple places
3. **Duplicated Logic**: Each resource type has its own API file with similar patterns
4. **No Persistence**: Uses Redis cache only, no historical data
5. **Manual Discovery**: Doesn't automatically detect what services user is using

## Design Principles

1. **Service-Centric, Not Resource-Centric**: Focus on AWS services the user actually uses
2. **Dynamic Discovery**: Automatically detect services from AWS Cost Explorer
3. **Database-Backed**: Use PostgreSQL for persistence and historical tracking
3. **Extensible**: Easy to add new service handlers without core changes
4. **Only Track Active Services**: Ignore services with zero usage/cost

## Architecture Components

### 1. Database Layer (PostgreSQL)

Replace Redis-only caching with PostgreSQL for persistence:

```
┌─────────────────────────────────────────────────────────────┐
│                     PostgreSQL Database                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  aws_services    │  │  resources       │                │
│  ├──────────────────┤  ├──────────────────┤                │
│  │ id (PK)          │  │ id (PK)          │                │
│  │ service_code     │  │ service_id (FK)  │                │
│  │ service_name     │  │ resource_id      │                │
│  │ is_active        │  │ resource_type    │                │
│  │ first_seen       │  │ resource_name    │                │
│  │ last_seen        │  │ region           │                │
│  │ total_cost       │  │ state            │                │
│  │ metadata (JSON)  │  │ metadata (JSON)  │                │
│  └──────────────────┘  │ is_unused        │                │
│                        │ cost_monthly     │                │
│  ┌──────────────────┐  │ first_seen       │                │
│  │  cost_history    │  │ last_seen        │                │
│  ├──────────────────┤  │ created_at       │                │
│  │ id (PK)          │  │ updated_at       │                │
│  │ service_id (FK)  │  └──────────────────┘                │
│  │ date             │                                        │
│  │ cost             │  ┌──────────────────┐                │
│  │ usage_quantity   │  │  scan_history    │                │
│  │ usage_unit       │  ├──────────────────┤                │
│  │ created_at       │  │ id (PK)          │                │
│  └──────────────────┘  │ scan_type        │                │
│                        │ region           │                │
│                        │ services_found   │                │
│                        │ resources_found  │                │
│                        │ duration_seconds │                │
│                        │ status           │                │
│                        │ error_message    │                │
│                        │ started_at       │                │
│                        │ completed_at     │                │
│                        └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

### 2. Service Discovery Engine

Uses AWS Cost Explorer to discover services:

```python
# Pseudo-code for service discovery
class ServiceDiscoveryEngine:
    """
    Discovers AWS services by querying Cost Explorer for actual usage
    """
    
    async def discover_services(self, days: int = 30):
        """
        Query Cost Explorer to find services with actual costs
        Returns: List of service codes that have been used
        """
        # Query Cost Explorer grouped by SERVICE
        # Filter services with cost > 0
        # Return unique service codes
        
    async def get_service_metadata(self, service_code: str):
        """
        Get metadata about a service from AWS
        Returns: Service name, category, pricing info
        """
        
    async def scan_service_resources(self, service_code: str):
        """
        For a discovered service, scan for unused resources
        Uses service-specific handlers
        """
```

### 3. Service Handler Registry

Dynamic handler system for different AWS services:

```python
# Base handler interface
class ServiceHandler(ABC):
    service_code: str  # e.g., "AmazonEC2"
    service_name: str  # e.g., "EC2"
    
    @abstractmethod
    async def scan_unused_resources(self, region: str) -> List[Resource]:
        """Scan for unused resources of this service type"""
        pass
    
    @abstractmethod
    async def get_resource_cost(self, resource: Resource) -> float:
        """Calculate cost for a specific resource"""
        pass
    
    @abstractmethod
    async def delete_resource(self, resource_id: str, region: str) -> bool:
        """Delete a specific resource"""
        pass

# Handler registry
class ServiceHandlerRegistry:
    _handlers: Dict[str, ServiceHandler] = {}
    
    @classmethod
    def register(cls, service_code: str, handler: ServiceHandler):
        """Register a handler for a service"""
        cls._handlers[service_code] = handler
    
    @classmethod
    def get_handler(cls, service_code: str) -> Optional[ServiceHandler]:
        """Get handler for a service"""
        return cls._handlers.get(service_code)
    
    @classmethod
    def get_all_handlers(cls) -> Dict[str, ServiceHandler]:
        """Get all registered handlers"""
        return cls._handlers
```

### 4. Service-Specific Handlers

Each AWS service gets its own handler:

```
backend/
  services/
    __init__.py
    base.py                    # Base ServiceHandler class
    registry.py                # ServiceHandlerRegistry
    ec2_handler.py            # EC2 service handler
    ebs_handler.py            # EBS service handler
    s3_handler.py             # S3 service handler
    rds_handler.py            # RDS service handler (new!)
    lambda_handler.py         # Lambda service handler (new!)
    elasticache_handler.py    # ElastiCache handler (new!)
    # ... more handlers as needed
```

Example handler:

```python
# services/ec2_handler.py
from .base import ServiceHandler
from .registry import ServiceHandlerRegistry

class EC2Handler(ServiceHandler):
    service_code = "AmazonEC2"
    service_name = "EC2"
    
    async def scan_unused_resources(self, region: str):
        # Scan for stopped EC2 instances
        # Return list of Resource objects
        pass
    
    async def get_resource_cost(self, resource):
        # Calculate EC2 instance cost using Pricing API
        pass
    
    async def delete_resource(self, resource_id, region):
        # Terminate EC2 instance
        pass

# Auto-register on import
ServiceHandlerRegistry.register("AmazonEC2", EC2Handler())
```

### 5. New API Structure

Simplified, dynamic API endpoints:

```
GET  /api/services                    # List all discovered services
GET  /api/services/{service_code}     # Get service details
GET  /api/services/{service_code}/resources  # Get resources for service
GET  /api/resources                   # Get all unused resources (all services)
GET  /api/resources/{resource_id}     # Get specific resource details
DELETE /api/resources/{resource_id}   # Delete a resource
POST /api/scan                        # Trigger service discovery scan
GET  /api/scan/history                # Get scan history
```

### 6. Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Request                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Endpoint                            │
│                  /api/services or /api/resources                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Service Discovery Engine                       │
│  1. Query Cost Explorer for services with costs                 │
│  2. Store discovered services in database                       │
│  3. For each service, get appropriate handler                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Service Handler Registry                      │
│  - Lookup handler for service code                              │
│  - Return handler instance                                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Service-Specific Handler                       │
│  - Scan for unused resources using AWS APIs                     │
│  - Calculate costs using Pricing API                            │
│  - Store resources in database                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PostgreSQL Database                         │
│  - Store services, resources, costs                             │
│  - Track historical data                                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Return to Frontend                          │
│  - Dynamic list of services                                     │
│  - Resources grouped by service                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 7. Service Discovery Process

```mermaid
graph TD
    A[Scheduled Scan Trigger] --> B[Query AWS Cost Explorer]
    B --> C{Services with Cost > 0?}
    C -->|Yes| D[For Each Service]
    C -->|No| E[Log: No Active Services]
    
    D --> F{Handler Exists?}
    F -->|Yes| G[Execute Handler.scan_unused_resources]
    F -->|No| H[Log: Handler Not Implemented]
    
    G --> I[Store Resources in DB]
    I --> J[Calculate Costs]
    J --> K[Update Service Metadata]
    K --> L{More Services?}
    L -->|Yes| D
    L -->|No| M[Complete Scan]
    
    H --> L
    E --> M
    M --> N[Update Scan History]
    N --> O[Send Notifications if Needed]
```

## Database Schema Details

### Table: aws_services

Tracks AWS services discovered via Cost Explorer:

```sql
CREATE TABLE aws_services (
    id SERIAL PRIMARY KEY,
    service_code VARCHAR(100) UNIQUE NOT NULL,  -- e.g., 'AmazonEC2'
    service_name VARCHAR(100) NOT NULL,          -- e.g., 'EC2'
    service_category VARCHAR(50),                -- e.g., 'Compute'
    is_active BOOLEAN DEFAULT true,
    has_handler BOOLEAN DEFAULT false,           -- Whether we have a handler
    first_seen TIMESTAMP NOT NULL,
    last_seen TIMESTAMP NOT NULL,
    total_cost_30d DECIMAL(10, 2) DEFAULT 0,    -- Total cost last 30 days
    metadata JSONB,                              -- Additional service info
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_services_active ON aws_services(is_active);
CREATE INDEX idx_services_code ON aws_services(service_code);
```

### Table: resources

Tracks individual resources across all services:

```sql
CREATE TABLE resources (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES aws_services(id) ON DELETE CASCADE,
    resource_id VARCHAR(255) NOT NULL,           -- AWS resource ID
    resource_type VARCHAR(100),                  -- e.g., 'instance', 'volume'
    resource_name VARCHAR(255),
    region VARCHAR(50) NOT NULL,
    state VARCHAR(50),                           -- e.g., 'stopped', 'available'
    is_unused BOOLEAN DEFAULT false,
    cost_monthly DECIMAL(10, 2) DEFAULT 0,
    metadata JSONB,                              -- Resource-specific data
    first_seen TIMESTAMP NOT NULL,
    last_seen TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(service_id, resource_id, region)
);

CREATE INDEX idx_resources_service ON resources(service_id);
CREATE INDEX idx_resources_unused ON resources(is_unused);
CREATE INDEX idx_resources_region ON resources(region);
CREATE INDEX idx_resources_composite ON resources(service_id, is_unused, region);
```

### Table: cost_history

Tracks daily costs per service:

```sql
CREATE TABLE cost_history (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES aws_services(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    cost DECIMAL(10, 2) NOT NULL,
    usage_quantity DECIMAL(15, 4),
    usage_unit VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(service_id, date)
);

CREATE INDEX idx_cost_history_service_date ON cost_history(service_id, date);
```

### Table: scan_history

Tracks scan execution history:

```sql
CREATE TABLE scan_history (
    id SERIAL PRIMARY KEY,
    scan_type VARCHAR(50) NOT NULL,              -- 'full', 'service', 'region'
    region VARCHAR(50),
    services_found INTEGER DEFAULT 0,
    resources_found INTEGER DEFAULT 0,
    duration_seconds INTEGER,
    status VARCHAR(20) NOT NULL,                 -- 'success', 'failed', 'partial'
    error_message TEXT,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_scan_history_status ON scan_history(status);
CREATE INDEX idx_scan_history_started ON scan_history(started_at);
```

## Implementation Plan

### Phase 1: Database Setup (v0.5.0-alpha)
- [ ] Add PostgreSQL to docker-compose.yml
- [ ] Create SQLAlchemy models
- [ ] Create database migrations (Alembic)
- [ ] Update config for database connection

### Phase 2: Service Discovery (v0.5.0-beta)
- [ ] Implement ServiceDiscoveryEngine
- [ ] Integrate AWS Cost Explorer API
- [ ] Create service metadata extraction
- [ ] Add scheduled discovery scans

### Phase 3: Handler System (v0.5.0-rc1)
- [ ] Create base ServiceHandler class
- [ ] Implement ServiceHandlerRegistry
- [ ] Migrate existing handlers (EC2, EBS, S3, IAM)
- [ ] Add new handlers (RDS, Lambda, ElastiCache)

### Phase 4: API Refactoring (v0.5.0-rc2)
- [ ] Create new dynamic API endpoints
- [ ] Deprecate old hardcoded endpoints
- [ ] Add backward compatibility layer
- [ ] Update API documentation

### Phase 5: Frontend Updates (v0.5.0)
- [ ] Update to consume dynamic service list
- [ ] Remove hardcoded resource tabs
- [ ] Add service discovery UI
- [ ] Update cost analysis for dynamic services

## Benefits

1. **Automatic Service Detection**: No manual configuration needed
2. **Scalable**: Easy to add new service handlers
3. **Historical Tracking**: Database stores all historical data
4. **Cost Accurate**: Uses actual AWS Cost Explorer data
5. **Extensible**: Plugin-like architecture for handlers
6. **Only Active Services**: Focuses on services user actually uses
7. **Better Performance**: Database queries vs repeated AWS API calls

## Migration Strategy

### Backward Compatibility

During migration, support both old and new APIs:

```python
# Old endpoint (deprecated but functional)
@router.get("/ec2/unused")
async def get_unused_ec2_old():
    # Redirect to new dynamic endpoint
    return await get_resources_by_service("AmazonEC2")

# New endpoint
@router.get("/services/{service_code}/resources")
async def get_resources_by_service(service_code: str):
    # New dynamic implementation
    pass
```

### Data Migration

1. Run initial service discovery scan
2. Migrate existing cached data to database
3. Verify data integrity
4. Switch to new endpoints
5. Remove old code after grace period

## Configuration

Add to [`backend/core/config.py`](backend/core/config.py:1):

```python
class Settings(BaseSettings):
    # ... existing settings ...
    
    # Database Configuration
    database_url: str = "postgresql://user:pass@postgres:5432/cloud_cleaner"
    
    # Service Discovery Configuration
    discovery_scan_interval_hours: int = 6
    discovery_lookback_days: int = 30
    min_cost_threshold: float = 0.01  # Ignore services < $0.01
    
    # Handler Configuration
    enable_auto_handler_discovery: bool = True
    supported_regions: List[str] = ["us-east-1", "ap-south-1"]
```

## Testing Strategy

1. **Unit Tests**: Test each handler independently
2. **Integration Tests**: Test service discovery with mocked AWS
3. **Database Tests**: Test all CRUD operations
4. **Performance Tests**: Ensure scans complete within time limits
5. **Migration Tests**: Verify data migration accuracy

## Future Enhancements (Post v0.5.0)

1. **Multi-Account Support**: Scan across multiple AWS accounts
2. **Custom Handlers**: Allow users to add custom service handlers
3. **ML-Based Predictions**: Predict which resources will become unused
4. **Cost Forecasting**: Predict future costs based on trends
5. **Automated Cleanup**: Auto-delete resources based on rules
6. **Service Recommendations**: Suggest alternative services for cost savings

## Conclusion

This architecture transforms Cloud Cleaner from a hardcoded system to a dynamic, scalable platform that automatically discovers and tracks AWS services based on actual usage. The database-backed approach provides persistence, historical tracking, and better performance, while the handler registry makes it easy to add support for new AWS services without core changes.