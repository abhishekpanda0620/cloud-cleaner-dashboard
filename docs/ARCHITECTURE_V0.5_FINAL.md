# v0.5.0 Architecture: Cost-Driven with Generic Fallback Scanner

## Executive Summary

We build a **hybrid system** that:
1. Uses Cost Explorer to discover services user actually uses
2. Has specific scanners for high-priority services (EC2, RDS, S3, Lambda)
3. Has a **generic fallback scanner** for ANY AWS service automatically
4. Scales infinitely without code changes

This means: **New AWS services are automatically supported the day they appear in Cost Explorer.**

## The Genius: Generic Fallback Scanner

### How It Works

Every AWS service follows standard API patterns:
- `describe_*` or `list_*` operations
- Return resources with metadata
- Support pagination
- Have CloudWatch metrics

**Generic Scanner Logic:**
```
For any service (e.g., DynamoDB):
    1. Get service name from Cost Explorer
    2. Convert to boto3 client (dynamodb)
    3. Find describe/list operations
    4. Call them to get resources
    5. Extract metadata
    6. Check CloudWatch for utilization
    7. Identify unused resources
    8. Store in database
```

### Example: New Service Added

**Scenario: AWS launches new service "Bedrock"**

1. User starts using Bedrock (costs appear in Cost Explorer)
2. Our app detects "AmazonBedrock" in Cost Explorer
3. Generic scanner automatically:
   - Creates boto3 client for bedrock
   - Discovers available list/describe operations
   - Queries resources
   - Stores in database
4. User sees Bedrock service in dashboard
5. **No code changes needed!**

## Architecture Components

### 1. Cost Explorer Integration (Already Built)
- Queries AWS Cost Explorer for services with costs
- Returns list of service codes (e.g., "AmazonEC2", "AmazonBedrock")
- Provides cost breakdown per service

### 2. Scanner Registry
Maps service codes to scanners:
```
Service Code → Scanner
"AmazonEC2" → EC2Scanner (specific)
"AmazonRDS" → RDSScanner (specific)
"AmazonS3" → S3Scanner (specific)
"AmazonLambda" → LambdaScanner (specific)
"AmazonBedrock" → GenericScanner (fallback)
"AmazonDynamoDB" → GenericScanner (fallback)
"AnyNewService" → GenericScanner (fallback)
```

### 3. Specific Scanners (High Priority)
Build optimized scanners for services with most unused resources:

**Phase 1 (v0.5.0):**
- EC2Scanner - Detect unused instances
- RDSScanner - Detect unused databases
- S3Scanner - Detect unused buckets
- LambdaScanner - Detect unused functions

**Why specific scanners?**
- Better unused detection logic (service-specific heuristics)
- Faster scanning (optimized queries)
- More accurate cost estimation
- Better error handling

### 4. Generic Fallback Scanner
Handles ANY AWS service automatically:

**Capabilities:**
- Auto-discover available operations
- Query resources across regions
- Extract metadata
- Check CloudWatch metrics
- Identify unused resources (generic heuristics)
- Handle pagination
- Respect rate limits

**Limitations:**
- Generic unused detection (may not be perfect)
- Slower than specific scanners
- Less detailed analysis

**But:** Better than nothing, and can be improved later with specific scanners

### 5. Discovery Engine (Refactored)
```
Scan Workflow:
    ↓
1. Get services from Cost Explorer
    ↓
2. Load scanner registry
    ↓
3. For each service with cost:
    ├─ Check if specific scanner exists
    ├─ If yes → Use specific scanner
    ├─ If no → Use generic fallback scanner
    ├─ Run scanner
    ├─ Store results
    └─ Update progress
    ↓
4. Aggregate results
    ↓
5. Update database
```

## Implementation Strategy

### Phase 1: Core Infrastructure (1-2 days)
1. Create scanner base class
2. Create scanner registry
3. Build generic fallback scanner
4. Refactor discovery engine

### Phase 2: Specific Scanners (2-3 days)
Build 4 optimized scanners:
1. EC2Scanner
2. RDSScanner
3. S3Scanner
4. LambdaScanner

### Phase 3: Frontend Integration (1-2 days)
1. Update dashboard to show discovered services
2. Display scan progress
3. Show resource details per service

### Phase 4: Testing & Optimization (1-2 days)
1. Test all scanners
2. Performance tuning
3. Error handling

**Total: 5-9 days**

## Generic Scanner Implementation

### Pseudo-Logic

```
GenericScanner(service_code):
    client = boto3.client(service_code)
    
    # Discover available operations
    operations = client.meta.service_model.operation_names
    list_ops = [op for op in operations if 'List' in op or 'Describe' in op]
    
    # Query resources
    for operation in list_ops:
        try:
            resources = client.call(operation)
            for resource in resources:
                # Extract metadata
                resource_id = extract_id(resource)
                resource_type = extract_type(resource)
                
                # Check utilization
                metrics = cloudwatch.get_metrics(resource_id)
                is_unused = analyze_metrics(metrics)
                
                # Store in database
                store_resource(resource_id, resource_type, is_unused)
        except Exception as e:
            log_error(e)
            continue
```

### Unused Detection Heuristics

**Generic (applies to all services):**
- No CloudWatch metrics in 7+ days
- No API calls in 7+ days
- Creation date > 90 days ago

**Service-Specific (only in specific scanners):**
- EC2: CPU < 5% for 7 days
- RDS: Connections = 0 for 7 days
- S3: No GET/PUT operations for 30 days
- Lambda: No invocations for 7 days

## Workflow Example

### Scenario 1: Known Service (EC2)
```
Cost Explorer: "AmazonEC2 - $500/month"
    ↓
Registry lookup: "AmazonEC2" → EC2Scanner
    ↓
Run EC2Scanner (optimized)
    ↓
Results: 500 instances, 50 unused
```

### Scenario 2: Unknown Service (Bedrock)
```
Cost Explorer: "AmazonBedrock - $100/month"
    ↓
Registry lookup: "AmazonBedrock" → Not found
    ↓
Use GenericScanner as fallback
    ↓
Results: 20 resources, 5 unused
```

### Scenario 3: New Service Later
```
User starts using DynamoDB
    ↓
Cost Explorer: "AmazonDynamoDB - $50/month"
    ↓
Registry lookup: "AmazonDynamoDB" → Not found
    ↓
Use GenericScanner (works immediately)
    ↓
Results: 10 tables, 3 unused
    ↓
Later: We build DynamoDBScanner for better detection
```

## Database Schema (Unchanged)

The existing PostgreSQL schema remains perfect:
- `aws_services` - Service metadata
- `resources` - Individual resources
- `cost_history` - Daily costs
- `scan_history` - Scan audit trail

## API Endpoints (Unchanged)

The V2 API structure remains the same:
- `POST /api/v2/scan` - Trigger scan
- `GET /api/v2/scan/status` - Get scan progress
- `GET /api/v2/services` - List services (from Cost Explorer)
- `GET /api/v2/resources` - List resources (from scanners)

## Scaling Strategy

### As AWS Adds New Services
1. Service appears in Cost Explorer
2. Generic scanner automatically handles it
3. Works immediately (may not be perfect)
4. We can build specific scanner later for better detection

### Continuous Improvement
- Monitor which services have most unused resources
- Build specific scanners for high-impact services
- Generic scanner always available as fallback

## Error Handling

### Service Not Supported by Boto3
```
Cost Explorer: "AmazonNewService"
Generic Scanner: boto3 doesn't have client
Action: Log and skip, user notified
```

### Service Doesn't Support List/Describe
```
Generic Scanner: No list/describe operations found
Action: Log and skip, user notified
```

### Permission Errors
```
Generic Scanner: Access denied
Action: Log error, user sees "Permission denied for service X"
```

## Security Considerations

### IAM Permissions
Generic scanner needs broad read permissions:
- `*:Describe*`
- `*:List*`
- `cloudwatch:GetMetricStatistics`

Or specific permissions per service:
- `ec2:Describe*`
- `rds:Describe*`
- `s3:List*`
- etc.

### Data Privacy
- No data stored outside user's AWS account
- Results stored in user's PostgreSQL DB
- No telemetry or tracking

## Comparison: Approaches

| Aspect | 100+ Plugins | Cost-Driven | Cost-Driven + Generic |
|--------|-------------|-----------|----------------------|
| Initial effort | Massive | Minimal | Minimal |
| Maintenance | High | Low | Low |
| New services | Manual | Manual | Automatic |
| User value | Overkill | Good | Excellent |
| Scaling | Difficult | Easy | Infinite |
| Time to MVP | Weeks | Days | Days |

## Success Criteria

- [ ] Generic fallback scanner works for any service
- [ ] Cost Explorer integration working
- [ ] Scanner registry dynamically loads scanners
- [ ] 4 specific scanners working (EC2, RDS, S3, Lambda)
- [ ] New services automatically supported
- [ ] Scan completes in <5 minutes for typical account
- [ ] Error handling for unsupported services
- [ ] Frontend shows discovered services
- [ ] Database populated with resources

## Next Steps

1. Approve cost-driven + generic fallback architecture
2. Build generic fallback scanner
3. Build scanner base class and registry
4. Implement 4 specific scanners
5. Integrate with discovery engine
6. Update frontend
7. Test and optimize

---

**Architecture Status**: Final and Optimized  
**Estimated Timeline**: 5-9 days  
**Approach**: Smart, scalable, future-proof, infinite service support