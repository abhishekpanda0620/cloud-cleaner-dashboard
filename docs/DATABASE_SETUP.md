# Database Setup Guide

## Prerequisites

- PostgreSQL 17 running (via docker-compose)
- Python environment with uv package manager
- All dependencies installed from requirements.txt

## Environment Variables

Make sure these are set in `backend/.env`:

```bash
POSTGRES_PASSWORD=toor
DATABASE_URL=postgresql+asyncpg://postgres:toor@0.0.0.0:5432/cloud_cleaner_db
```

## Database Migration Commands

### 1. Start PostgreSQL

```bash
# From project root
docker-compose up postgres -d

# Verify it's running
docker-compose ps postgres

# Check logs
docker-compose logs postgres
```

### 2. Create Initial Migration

```bash
cd backend

# Generate migration from models
uv run alembic revision --autogenerate -m "Initial schema with AWS services, resources, cost history, and scan history"
```

### 3. Apply Migration

```bash
# Apply all pending migrations
uv run alembic upgrade head
```

### 4. Verify Database

```bash
# Connect to database
docker exec -it cloud-cleaner-postgres psql -U postgres -d cloud_cleaner_db

# List tables
\dt

# Describe a table
\d aws_services

# Exit
\q
```

## Common Migration Commands

### Check Current Migration Status
```bash
uv run alembic current
```

### View Migration History
```bash
uv run alembic history
```

### Downgrade One Version
```bash
uv run alembic downgrade -1
```

### Downgrade to Specific Version
```bash
uv run alembic downgrade <revision_id>
```

### Create Empty Migration
```bash
uv run alembic revision -m "description"
```

### Generate Migration from Model Changes
```bash
uv run alembic revision --autogenerate -m "description of changes"
```

## Database Schema

### Tables Created

1. **aws_services** - Tracks AWS services discovered via Cost Explorer
   - service_code (unique)
   - service_name
   - is_active
   - total_cost_30d
   - resource_count
   - Relationships: resources, cost_history

2. **resources** - Individual AWS resources from AWS Config
   - resource_id + region (unique)
   - resource_type (e.g., AWS::EC2::Instance)
   - is_unused
   - cost_monthly
   - config_data (JSONB)
   - Relationship: service

3. **cost_history** - Daily cost tracking per service
   - service_id + date (unique)
   - cost
   - usage_quantity
   - Relationship: service

4. **scan_history** - Audit trail of discovery scans
   - scan_type
   - services_found
   - resources_found
   - status
   - duration_seconds

## Troubleshooting

### Migration Fails with "relation already exists"

```bash
# Drop all tables and start fresh (CAUTION: deletes all data)
docker exec -it cloud-cleaner-postgres psql -U postgres -d cloud_cleaner_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Re-run migration
uv run alembic upgrade head
```

### Can't Connect to Database

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Verify credentials in .env match docker-compose.yml
```

### Alembic Can't Find Models

```bash
# Make sure you're in the backend directory
cd backend

# Verify models are importable
uv run python -c "from models.service import AWSService; print('Models OK')"
```

## Development Workflow

1. Make changes to models in `backend/models/`
2. Generate migration: `uv run alembic revision --autogenerate -m "description"`
3. Review generated migration in `backend/alembic/versions/`
4. Apply migration: `uv run alembic upgrade head`
5. Test changes
6. Commit migration file to git

## Production Deployment

1. Backup database before migration
2. Run migrations: `uv run alembic upgrade head`
3. Verify application works
4. If issues, rollback: `uv run alembic downgrade -1`

## Notes

- Alembic uses synchronous SQLAlchemy (not asyncpg) for migrations
- The DATABASE_URL is automatically converted from `postgresql+asyncpg://` to `postgresql://` in alembic/env.py
- All models must be imported in alembic/env.py for autogenerate to work
- Migration files are stored in `backend/alembic/versions/`