# Cloud Cleaner Dashboard - Simplified Architecture (v0.5.0 - REVISED)

## Overview

This revised architecture leverages **AWS Config** and **AWS Cost Explorer** to eliminate the need for service-specific handlers. AWS Config already tracks resource compliance and configuration, so we use its intelligence instead of reimplementing detection logic.

## Why AWS Config?

AWS Config provides:
- ✅ **Automatic resource discovery** across ALL AWS services
- ✅ **Built-in compliance rules** for unused resources
- ✅ **Resource relationships** and dependencies
- ✅ **Configuration history** and change tracking
- ✅ **No service-specific code needed**
- ✅ **Supports 100+ AWS resource types** out of the box

## Simplified Architecture

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
│              Service Discovery Engine (Simplified)               │
│  1. Query AWS Cost Explorer for services with costs             │
│  2. Query AWS Config for all resources                          │
│  3. Apply Config Rules to identify unused resources             │
│  4. Store in PostgreSQL database                                │
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

## Core Components

### 1. AWS Config Integration

**What AWS Config Provides:**

```python
# List all resources across ALL services
config_client.list_discovered_resources(
    resourceType='AWS::AllSupported'
)

# Get resource details
config_client.get_resource_config_history(
    resourceType='AWS::EC2::Instance',
    resourceId='i-1234567890abcdef0'
)

# Query resources with advanced filters
config_client.select_resource_config(
    Expression="""
        SELECT resourceId, resourceType, configuration, tags
        WHERE resourceType = 'AWS::EC2::Instance'
        AND configuration.state.name = 'stopped'
    """
)
```

**Built-in Config Rules for Unused Resources:**
- `ec2-stopped-instance` - Detects stopped EC2 instances
- `ebs-optimized-instance` - Detects unattached EBS volumes
- `s3-bucket-public-read-prohibited` - Detects unused S3 buckets
- `rds-instance-deletion-protection-enabled` - Detects unused RDS
- `lambda-function-public-access-prohibited` - Detects unused Lambda
- And 200+ more managed rules

### 2. Simplified Service Discovery

**No Handlers Needed!**

```python
class ServiceDiscoveryEngine:
    """
    Uses AWS Config + Cost Explorer for complete automation
    """
    
    async def discover_all(self, db: AsyncSession):
        """
        Single method to discover everything
        """
        # Step 1: Get services with costs from Cost Explorer
        services = await self.get_services_from_cost_explorer()
        
        # Step 2: Get all resources from AWS Config
        resources = await self.get_resources_from_config()
        
        # Step 3: Apply Config Rules to identify unused
        unused_resources = await self.identify_unused_resources(resources)
        
        # Step 4: Calculate costs using Pricing API
        await self.calculate_costs(unused_resources)
        
        # Step 5: Store in database
        await self.store_in_database(db, services, unused_resources)
```

### 3. Database Schema (Simplified)

**Same tables, but simpler data flow:**

```sql
-- Services discovered from Cost Explorer
CREATE TABLE aws_services (
    id SERIAL PRIMARY KEY,
    service_code VARCHAR(100) UNIQUE NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    total_cost_30d DECIMAL(10, 2) DEFAULT 0,
    resource_count INTEGER DEFAULT 0,
    first_seen TIMESTAMP NOT NULL,
    last_seen TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resources from AWS Config
CREATE TABLE resources (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES aws_services(id),
    resource_id VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,  -- AWS::EC2::Instance, etc.
    resource_name VARCHAR(255),
    region VARCHAR(50) NOT NULL,
    is_unused BOOLEAN DEFAULT false,
    unused_reason VARCHAR(255),  -- Why it's unused (from Config Rule)
    cost_monthly DECIMAL(10, 2) DEFAULT 0,
    config_data JSONB,  -- Full AWS Config data
    first_seen TIMESTAMP NOT NULL,
    last_seen TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(resource_id, region)
);

-- Cost history (same as before)
CREATE TABLE cost_history (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES aws_services(id),
    date DATE NOT NULL,
    cost DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(service_id, date)
);

-- Scan history (same as before)
CREATE TABLE scan_history (
    id SERIAL PRIMARY KEY,
    scan_type VARCHAR(50) NOT NULL,
    services_found INTEGER DEFAULT 0,
    resources_found INTEGER DEFAULT 0,
    unused_resources INTEGER DEFAULT 0,
    duration_seconds INTEGER,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. AWS Config Rules Mapping

**How we identify "unused" for each service:**

| Service | AWS Config Rule | Unused Criteria |
|---------|----------------|-----------------|
| EC2 | `ec2-stopped-instance` | State = stopped for > 7 days |
| EBS | `ec2-volume-inuse-check` | Status = available (unattached) |
| S3 | Custom query | No objects or no access > 90 days |
| RDS | `rds-instance-deletion-protection-enabled` | Status = stopped |
| Lambda | `lambda-function-public-access-prohibited` | No invocations > 30 days |
| ElastiCache | Custom query | Status = available |
| ELB | `elb-deletion-protection-enabled` | No targets attached |
| NAT Gateway | Custom query | No traffic > 30 days |
| Elastic IP | `eip-attached` | Not attached to instance |
| CloudFront | Custom query | No requests > 90 days |

### 5. Implementation Structure

**Much simpler file structure:**

```
backend/
  ├── models/
  │   ├── __init__.py
  │   ├── service.py
  │   ├── resource.py
  │   ├── cost_history.py
  │   └── scan_history.py
  │
  ├── services/
  │   ├── __init__.py
  │   ├── discovery.py          # Single discovery engine
  │   ├── config_client.py      # AWS Config wrapper
  │   └── cost_explorer.py      # Cost Explorer wrapper
  │
  ├── api/
  │   ├── services.py           # Service endpoints
  │   ├── resources.py          # Resource endpoints
  │   └── scan.py               # Scan endpoints
  │
  └── core/
      ├── config.py
      ├── aws_client.py
      └── database.py
```

**No handlers directory needed!**

## Key Advantages

### 1. Zero Service-Specific Code
- No EC2Handler, EBSHandler, S3Handler, etc.
- AWS Config handles ALL services
- Add new services automatically as AWS adds them

### 2. Leverages AWS Intelligence
- AWS Config Rules are maintained by AWS
- Best practices built-in
- Compliance-ready

### 3. Simpler Maintenance
- One discovery engine instead of multiple handlers
- Fewer files to maintain
- Less code to test

### 4. More Comprehensive
- Supports 100+ AWS resource types immediately
- Includes services we haven't thought of
- Automatic updates as AWS adds services

### 5. Better Accuracy
- AWS Config tracks actual resource state
- Real-time configuration data
- Relationship tracking (e.g., EBS attached to EC2)

## AWS Config Query Examples

### Find All Stopped EC2 Instances
```sql
SELECT 
    resourceId,
    resourceName,
    configuration.state.name,
    configuration.instanceType,
    tags
WHERE 
    resourceType = 'AWS::EC2::Instance'
    AND configuration.state.name = 'stopped'
```

### Find Unattached EBS Volumes
```sql
SELECT 
    resourceId,
    configuration.size,
    configuration.volumeType,
    configuration.state
WHERE 
    resourceType = 'AWS::EC2::Volume'
    AND configuration.state = 'available'
```

### Find Unused RDS Instances
```sql
SELECT 
    resourceId,
    configuration.dBInstanceStatus,
    configuration.dBInstanceClass,
    configuration.engine
WHERE 
    resourceType = 'AWS::RDS::DBInstance'
    AND configuration.dBInstanceStatus = 'stopped'
```

### Find All Resources by Service
```sql
SELECT 
    resourceType,
    COUNT(*) as count
WHERE 
    resourceType LIKE 'AWS::EC2::%'
GROUP BY 
    resourceType
```

## Cost Calculation

**Still use AWS Pricing API for costs:**

```python
async def calculate_resource_cost(resource_type: str, config_data: dict, region: str):
    """
    Calculate cost based on resource type and configuration
    """
    pricing_client = boto3.client('pricing', region_name='us-east-1')
    
    # Map AWS Config resource type to service code
    service_code = map_resource_type_to_service(resource_type)
    
    # Get pricing based on configuration
    if resource_type == 'AWS::EC2::Instance':
        instance_type = config_data['instanceType']
        return get_ec2_pricing(instance_type, region)
    
    elif resource_type == 'AWS::EC2::Volume':
        size = config_data['size']
        volume_type = config_data['volumeType']
        return get_ebs_pricing(size, volume_type, region)
    
    elif resource_type == 'AWS::RDS::DBInstance':
        instance_class = config_data['dBInstanceClass']
        engine = config_data['engine']
        return get_rds_pricing(instance_class, engine, region)
    
    # ... etc for other types
```

## Required AWS Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "config:DescribeConfigurationRecorders",
        "config:DescribeConfigurationRecorderStatus",
        "config:ListDiscoveredResources",
        "config:GetResourceConfigHistory",
        "config:SelectResourceConfig",
        "config:DescribeComplianceByConfigRule",
        "ce:GetCostAndUsage",
        "ce:GetCostForecast",
        "pricing:GetProducts"
      ],
      "Resource": "*"
    }
  ]
}
```

## Setup Requirements

### 1. Enable AWS Config
```bash
# Enable AWS Config in your account
aws configservice put-configuration-recorder \
    --configuration-recorder name=default,roleARN=arn:aws:iam::ACCOUNT:role/config-role \
    --recording-group allSupported=true,includeGlobalResourceTypes=true

aws configservice start-configuration-recorder --configuration-recorder-name default
```

### 2. Enable Cost Explorer
```bash
# Enable Cost Explorer (via AWS Console or CLI)
# Wait 24 hours for data to populate
```

### 3. Deploy Managed Config Rules (Optional)
```bash
# Deploy AWS managed rules for unused resource detection
aws configservice put-config-rule \
    --config-rule file://config-rules/ec2-stopped-instance.json

aws configservice put-config-rule \
    --config-rule file://config-rules/ebs-volume-unused.json
```

## Migration Benefits

### Before (with handlers)
- ❌ 10+ handler files to maintain
- ❌ Service-specific logic for each AWS service
- ❌ Manual updates when AWS changes APIs
- ❌ Limited to services we implement
- ❌ Complex testing requirements

### After (with AWS Config)
- ✅ Single discovery engine
- ✅ AWS maintains the detection logic
- ✅ Automatic updates from AWS
- ✅ Supports 100+ resource types immediately
- ✅ Simple testing (mock AWS Config responses)

## Implementation Phases

### Phase 1: Database Setup (Week 1)
- Add PostgreSQL to docker-compose
- Create database models
- Setup Alembic migrations

### Phase 2: AWS Config Integration (Week 2)
- Implement AWS Config client wrapper
- Create resource discovery queries
- Test with various resource types

### Phase 3: Cost Explorer Integration (Week 2)
- Implement Cost Explorer client
- Service discovery logic
- Cost history tracking

### Phase 4: API Development (Week 3)
- Create unified API endpoints
- Implement backward compatibility
- Add API documentation

### Phase 5: Frontend Updates (Week 4)
- Update to consume new API
- Dynamic service/resource display
- Testing and refinement

## Cost Considerations

**AWS Config Pricing:**
- Configuration items: $0.003 per item recorded
- Config rule evaluations: $0.001 per evaluation
- Typical cost: $20-50/month for small accounts

**Cost Explorer:**
- Free for AWS customers
- API calls: $0.01 per request (first 100 free)

**Total estimated cost: $25-75/month**

This is offset by the savings from identifying unused resources!

## Conclusion

By leveraging AWS Config instead of custom handlers, we achieve:
- **90% less code** to maintain
- **100+ AWS services** supported immediately
- **AWS-maintained** detection logic
- **Compliance-ready** architecture
- **Future-proof** as AWS adds services

This is a much simpler, more maintainable, and more comprehensive solution than the handler-based approach.