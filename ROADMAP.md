# Cloud Cleaner Dashboard - Product Roadmap

This document outlines the planned features and improvements for the Cloud Cleaner Dashboard project. The roadmap is organized by version milestones and priority levels.

## Current Version: 0.5.0 ✅
**Dynamic Service Discovery with Plugin-Based Scanner System**

### Recently Completed (v0.4.0 - v0.4.1)
- ✅ Cost Analysis Dashboard with savings calculator
- ✅ PDF and CSV export functionality
- ✅ Professional UI redesign for Resource Dashboard
- ✅ Enhanced components with gradients and animations
- ✅ Improved visual consistency across all pages

---

## Version 0.5.0 - Dynamic Service Discovery ✅ COMPLETE
**Focus**: Scalable architecture with plugin-based direct API scanning

### ✅ Backend (100% Complete)

#### Database Infrastructure
- ✅ **PostgreSQL 17**: Replaced Redis with proper relational database
- ✅ **SQLAlchemy Async ORM**: Modern async database operations
- ✅ **Alembic Migrations**: Database schema version control
- ✅ **4 Core Tables**: aws_services, resources, cost_history, scan_history

#### AWS Integration (Pivoted Architecture)
- ✅ **Cost Explorer Client**: Automatic service discovery from billing data
- ✅ **Discovery Engine**: Unified workflow for scanning and identifying unused resources
- ✅ **Plugin-Based Scanners**: Direct boto3 API calls (no AWS Config needed)
  - ✅ Scanner Base Class: Abstract interface for all service scanners
  - ✅ Scanner Registry: Dynamic plugin discovery and loading
  - ✅ 4 Specific Scanners: EC2, RDS, S3, Lambda (1,331 lines)
  - ✅ Generic Fallback Scanner: Handles any AWS service automatically
  - ✅ CloudWatch Integration: Metrics-based unused detection
- ✅ **Multi-Cloud Ready**: Architecture supports future Azure/GCP integration

#### Why Plugin-Based Over AWS Config?
- **Zero setup cost**: No AWS Config recorder needed ($2-50/month savings)
- **Instant activation**: Works immediately after IAM role creation
- **Better UX**: No complex AWS Config setup required
- **Extensible**: Easy to add new services via plugins
- **Direct control**: We decide what to scan and when

#### API Development
- ✅ **V2 API Endpoints**: `/api/v2/scan`, `/api/v2/services`, `/api/v2/resources`
- ✅ **Synchronous Scanning**: Reliable scan execution
- ✅ **Backward Compatible**: V1 APIs still functional
- ✅ **RESTful Design**: Proper HTTP methods and status codes
- ✅ **Scheduled Scans**: Updated to use v0.5.0 engine

### ✅ Frontend (100% Complete)

#### Dashboard (Rewritten)
- ✅ **Dynamic Resource Dashboard**: Service-based discovery (no hardcoded types)
- ✅ **Service Cards**: Display discovered services with resource counts
- ✅ **Scan Control**: Manual scan trigger with loading state (30-60s)
- ✅ **Service Drill-down**: Click service to view its resources
- ✅ **Resource Management**: View, filter, and delete resources
- ✅ **Schedule Settings**: Configure automated scans
- ✅ **Loading States**: Proper UI feedback during operations

#### Components (1,783 lines)
- ✅ **API Client**: Type-safe V2 API client (345 lines)
- ✅ **Custom Hooks**: useServices, useScan, useResourcesV2 (367 lines)
- ✅ **ServiceCard**: Service display without cost (92 lines)
- ✅ **ScanControl**: Scan trigger with loading (118 lines)
- ✅ **ServiceGrid**: Responsive grid layout (59 lines)
- ✅ **DynamicResourceTable**: Generic resource table (111 lines)
- ✅ **ServiceResourceView**: Service drill-down (153 lines)
- ✅ **Dashboard**: Complete rewrite (269 lines)

#### Separation of Concerns
- ✅ **`/dashboard`**: Resource discovery and management (v0.5.0)
- ✅ **`/cost-analysis`**: Cost estimation and reporting (unchanged)

### 🎉 Key Achievements

#### Revolutionary Features
- **Generic Fallback Scanner**: Automatically handles ANY AWS service without code changes
- **Cost-Driven Discovery**: Only scans services user actually uses (with fallback to core services)
- **Zero AWS Config Cost**: Direct boto3 API calls eliminate $2-50/month AWS expense
- **Infinite Scalability**: New AWS services work immediately
- **Database-Backed**: PostgreSQL for persistent storage and historical data

#### Total Code Written
- **4,082 lines** of production code
- **Backend**: 2,299 lines (scanner system, discovery engine, API)
- **Frontend**: 1,783 lines (API client, hooks, components, dashboard)

---

## Version 0.6.0 - Security & Compliance ✅ COMPLETE
**Focus**: Integrated CIS AWS Foundations Benchmark scanning and reporting

### ✅ Backend
- ✅ **Security Module**: `services/aws/security/` with modular scanner architecture
- ✅ **CIS Implementation**: Full CIS AWS Foundations Benchmark v1.4.0 (58 Controls)
- ✅ **Automated Scanners**:
  - ✅ **Identity (IAM)**: Root keys, MFA, Password policy
  - ✅ **Monitoring**: CloudWatch Alarms (CIS 4.1-4.15) covering unauthorized API, root usage, etc.
  - ✅ **Logging**: CloudTrail validation, S3 access logging
  - ✅ **Networking**: Security Groups (SSH/RDP exposures), Default SGs, VPC Flow Logs
- ✅ **Database Seeding**: Automated population of all 58 controls and framework definitions

### ✅ Frontend
- ✅ **Security Dashboard**: `/security` page with modular components
- ✅ **Findings Table**: Sortable/Filterable table for security findings
- ✅ **Filtering**: Severity-based and Status-based filtering
- ✅ **Visuals**: Clean, auditor-friendly UI

---


## Version 0.7.0 - Governance & Lifecycle Automation
**Focus**: Active resource management, compliance policies, and financial governance

### 🎯 High Priority

#### Financial Governance
- **Native Budget Support**: Create "Soft Budgets" within the dashboard (for users without AWS Budget access)
- **Budget Integration**: Seamless UI link between "Budget Alarm" and "Resource Cleanup"
- **Budget Alerts**: In-app notifications when local budget thresholds are breached

#### Resource Governance
- **Tag Compliance**: Visual flags for resources missing required tags (e.g., `Owner`, `Project`)
- **Bulk Tagging**: Select multiple resources -> Apply tags in one click
- **Tag-based Filtering**: Enhanced filtering by AWS tags

#### Lifecycle Automation (TTL)
- **Resource Expiry**: Set `TerminationDate` on resources (Time-To-Live)
- **Scheduled Cleanup**: Background worker to terminate expired resources automatically
- **Expiration Alerts**: Notifications for upcoming resource deletions

---

## Version 0.8.0 - CloudWatch Integration & Monitoring
**Focus**: Deep AWS integration and advanced monitoring

### 🎯 High Priority

#### CloudWatch Metrics Integration
- **Resource Utilization**: Display CPU, memory, and network metrics
- **Custom Metrics**: Define and track custom CloudWatch metrics
- **Metric-based Alerts**: Alert on metric thresholds
- **Historical Metrics**: View metric trends over time
- **Metric-based Recommendations**: Suggest actions based on metrics

#### Advanced Monitoring
- **Real-time Monitoring**: Live resource status updates
- **Health Checks**: Automated resource health verification
- **Performance Insights**: Identify performance bottlenecks
- **Anomaly Detection**: Detect unusual resource behavior
- **Predictive Analytics**: Forecast resource usage trends

### 🔧 Medium Priority

#### AWS Service Expansion
- **RDS Monitoring**: Track unused RDS instances
- **Lambda Functions**: Monitor unused Lambda functions
- **Elastic IPs**: Identify unattached Elastic IPs
- **Load Balancers**: Track unused load balancers
- **NAT Gateways**: Monitor idle NAT gateways

---

## Version 0.9.0 - Multi-Cloud Support
**Focus**: Expand beyond AWS to support multiple cloud providers

### 🎯 High Priority

#### Azure Support
- **Azure VM Monitoring**: Track stopped Azure VMs
- **Azure Disk Management**: Identify unattached managed disks
- **Azure Storage**: Monitor unused storage accounts and blobs
- **Azure IAM**: Track unused service principals and managed identities
- **Azure Cost Analysis**: Azure-specific cost calculations
- **Unified Dashboard**: Single dashboard for AWS and Azure resources

#### Google Cloud Platform (GCP) Support
- **GCP Compute Engine**: Monitor stopped GCP instances
- **GCP Persistent Disks**: Track unattached disks
- **GCP Cloud Storage**: Identify unused buckets
- **GCP IAM**: Monitor unused service accounts
- **GCP Cost Analysis**: GCP-specific cost calculations
- **Multi-Cloud View**: Unified view across AWS, Azure, and GCP

#### Cloud Abstraction Layer
- **Unified API**: Common API interface for all cloud providers
- **Provider Plugins**: Pluggable architecture for cloud providers
- **Resource Mapping**: Map equivalent resources across clouds
- **Cross-Cloud Comparison**: Compare costs and resources across providers
- **Provider Selection**: Easy switching between cloud providers in UI

### 🔧 Medium Priority

#### Additional Cloud Providers
- **Oracle Cloud**: Basic support for OCI resources
- **IBM Cloud**: Support for IBM Cloud resources
- **Alibaba Cloud**: Support for Alibaba Cloud resources
- **DigitalOcean**: Support for DigitalOcean droplets and volumes
- **Linode**: Support for Linode instances

#### Multi-Cloud Features
- **Cloud Cost Comparison**: Compare costs across providers
- **Migration Recommendations**: Suggest cost-effective cloud migrations
- **Multi-Cloud Policies**: Define policies across all clouds
- **Unified Tagging**: Consistent tagging across providers
- **Cross-Cloud Reports**: Consolidated reports for all clouds

---

## Version 1.0.0 - Multi-Account & Advanced Notifications
**Focus**: Enterprise features and notification enhancements

### 🎯 High Priority

#### Multi-Account Support
- **AWS Organizations**: Support for AWS Organizations
- **Cross-Account Scanning**: Scan resources across multiple accounts
- **Account Grouping**: Organize accounts by environment/team
- **Consolidated Reporting**: Unified reports across accounts
- **Account-level Permissions**: Role-based access per account

#### Advanced Notifications
- **Custom Templates**: Create custom notification templates
- **Webhook Support**: Send notifications to custom webhooks
- **Microsoft Teams**: Integration with MS Teams
- **PagerDuty**: Integration with PagerDuty
- **Notification Rules**: Define complex notification conditions
- **Notification Throttling**: Prevent notification spam

### 🔧 Medium Priority

#### Security & Compliance
- **Compliance Reports**: Generate compliance reports (SOC2, HIPAA, etc.)
- **Security Scanning**: Identify security risks in resources
- **Access Audit**: Track who accessed/modified resources
- **Encryption Status**: Monitor encryption status of resources
- **Security Recommendations**: Suggest security improvements

---

## Version 1.1.0 - AI/ML Features & Automation
**Focus**: Intelligent automation and predictive capabilities

### 🎯 High Priority

#### AI-Powered Recommendations
- **Smart Cleanup**: AI-suggested resources safe to delete
- **Usage Prediction**: Predict future resource usage
- **Cost Optimization**: AI-driven cost optimization suggestions
- **Anomaly Detection**: ML-based anomaly detection
- **Pattern Recognition**: Identify resource usage patterns

#### Automation Engine
- **Auto-cleanup Rules**: Automatically delete resources based on rules
- **Workflow Automation**: Create custom automation workflows
- **Approval Workflows**: Multi-step approval for deletions
- **Scheduled Actions**: Schedule resource actions
- **Conditional Actions**: Execute actions based on conditions

### 🔧 Medium Priority

#### Integration Ecosystem
- **Terraform Integration**: Import/export Terraform configurations
- **Kubernetes Integration**: Monitor K8s resources
- **CI/CD Integration**: Integrate with Jenkins, GitLab CI, etc.
- **ITSM Integration**: ServiceNow, Jira Service Management
- **API Expansion**: Comprehensive REST API for integrations

---

## Version 1.2.0 - Performance & Scalability
**Focus**: Enterprise-scale performance and reliability

### 🎯 High Priority

#### Performance Optimization
- ✅ **Database Backend**: PostgreSQL implemented in v0.5.0
- **Caching Layer**: Advanced caching strategies
- **Parallel Processing**: Parallel resource scanning
- **Query Optimization**: Optimize API response times
- **Resource Pagination**: Efficient handling of large datasets

#### Scalability Improvements
- **Horizontal Scaling**: Support for multiple backend instances
- **Load Balancing**: Built-in load balancing support
- **High Availability**: HA configuration options
- **Disaster Recovery**: Backup and recovery mechanisms
- **Performance Monitoring**: Built-in performance metrics

### 🔧 Medium Priority

#### Developer Experience
- **API Documentation**: Interactive API documentation (Swagger/OpenAPI)
- **SDK/Libraries**: Official SDKs for Python, JavaScript, Go
- **Plugin System**: Extensible plugin architecture
- **Custom Integrations**: Framework for custom integrations
- **Developer Portal**: Dedicated developer documentation site

---

## Version 2.0.0 - Production Ready
**Focus**: Production-grade stability and enterprise features

### 🎯 High Priority

#### Enterprise Features
- **SSO/SAML**: Single Sign-On support
- **RBAC**: Role-Based Access Control
- **Audit Logging**: Comprehensive audit trail
- **Data Retention**: Configurable data retention policies
- **SLA Monitoring**: Track and report on SLAs

#### Production Readiness
- **Comprehensive Testing**: 90%+ test coverage
- **Security Hardening**: Security audit and hardening
- **Performance Benchmarks**: Published performance metrics
- **Migration Tools**: Tools for upgrading from previous versions
- **Professional Support**: Dedicated support channels

### 🔧 Medium Priority

#### Documentation & Training
- **Video Tutorials**: Comprehensive video guides
- **Best Practices Guide**: Enterprise deployment best practices
- **Case Studies**: Real-world implementation examples
- **Certification Program**: User certification program
- **Community Forum**: Active community support forum

---

## Future Considerations (Post 1.0.0)

### Potential Features
- **Mobile Apps**: Native iOS and Android applications
- **Desktop App**: Electron-based desktop application
- **Browser Extension**: Chrome/Firefox extension for quick access
- **Voice Integration**: Alexa/Google Assistant integration
- **Blockchain Audit**: Immutable audit trail using blockchain
- **Edge Computing**: Support for AWS Outposts, Azure Stack, and edge locations
- **Quantum-Ready**: Prepare for quantum computing era
- **Hybrid Cloud**: Support for on-premises and hybrid cloud environments
- **Multi-Cloud Kubernetes**: Support for EKS, AKS, GKE clusters
- **Serverless Multi-Cloud**: AWS Lambda, Azure Functions, Google Cloud Functions

### Community Requests
- Features will be added based on community feedback and usage patterns
- Regular community surveys to prioritize features
- Open-source contribution guidelines
- Feature voting system

---

## Contributing to the Roadmap

We welcome community input on our roadmap! Here's how you can contribute:

1. **Feature Requests**: Open an issue with the `feature-request` label
2. **Discussions**: Join discussions in GitHub Discussions
3. **Voting**: Vote on features you'd like to see prioritized
4. **Pull Requests**: Submit PRs for features you'd like to implement

## Roadmap Updates

This roadmap is a living document and will be updated regularly based on:
- User feedback and feature requests
- Market trends and AWS service updates
- Technical feasibility and resource availability
- Community contributions and priorities

**Last Updated**: January 18, 2026
**Next Review**: February 2026

## Related Roadmaps
- [🛡️ Security & Compliance Roadmap](docs/compliance-roadmap.md) - Detailed breakdown of compliance phases.

---

## Priority Definitions

- **🎯 High Priority**: Critical features for the version milestone
- **🔧 Medium Priority**: Important but not blocking features
- **💡 Low Priority**: Nice-to-have features that may be deferred

---

For questions or suggestions about the roadmap, please open an issue or start a discussion on GitHub.