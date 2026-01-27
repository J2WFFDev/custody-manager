# Database Setup Quick Start

## Overview

This guide provides a quick reference for setting up and working with the PostgreSQL database for the WilcoSS Custody Manager.

## Prerequisites

- PostgreSQL 14+ installed and running
- Python 3.11+ with pip
- Database credentials configured in `.env`

## Initial Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Database

Create a `.env` file in the `backend/` directory:

```bash
DATABASE_URL=postgresql://username:password@localhost:5432/custody_manager
JWT_SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
DEBUG=true
```

### 3. Create Database

```bash
# Using psql
psql -U postgres
CREATE DATABASE custody_manager;
\q

# Or using createdb
createdb custody_manager
```

### 4. Run Migrations

```bash
cd backend
alembic upgrade head
```

This will create all tables with the following schema:
- `users` - OAuth authentication and roles
- `kits` - Equipment and firearm kits
- `custody_events` - Immutable audit trail
- `approval_requests` - Off-site custody approvals
- `maintenance_events` - Maintenance tracking

## Database Schema

### Tables Created (in order)

1. **users** (Migration 001)
   - Stores authenticated users with OAuth credentials
   - Fields: id, email, name, oauth_provider, oauth_id, role, verified_adult, is_active

2. **kits** (Migration 002)
   - Tracks equipment with QR codes
   - Fields: id, code, name, description, status, current_custodian_id

3. **custody_events** (Migration 003)
   - Append-only audit log of custody changes
   - Fields: id, event_type, kit_id, initiated_by_id, custodian_id, notes, location_type

4. **approval_requests** (Migration 004)
   - Multi-role approval workflow
   - Fields: id, kit_id, requester_id, custodian_id, status, approver_id

5. **maintenance_events** (Migration 006)
   - Open/close maintenance tracking
   - Fields: id, kit_id, opened_by_id, closed_by_id, notes, parts_replaced, is_open

### Enhancements Applied

- **Migration 005**: Adds responsibility attestation fields
- **Migration 007**: Converts user role to enum type for type safety
- **Migration 008**: Adds expected_return_date for soft warnings
- **Migration 009**: Adds performance indexes

## Common Tasks

### Check Migration Status

```bash
alembic current
```

### View All Migrations

```bash
alembic history --verbose
```

### Rollback Last Migration

```bash
alembic downgrade -1
```

### Reset Database (Development Only)

```bash
# Drop all tables
alembic downgrade base

# Reapply all migrations
alembic upgrade head
```

### Generate New Migration

```bash
# After modifying models
alembic revision --autogenerate -m "description of changes"
```

## Verification

### Check Tables Were Created

```bash
psql custody_manager
\dt
```

Expected output:
```
                 List of relations
 Schema |        Name         | Type  |  Owner
--------+---------------------+-------+----------
 public | alembic_version     | table | username
 public | approval_requests   | table | username
 public | custody_events      | table | username
 public | kits                | table | username
 public | maintenance_events  | table | username
 public | users               | table | username
```

### Check Indexes

```bash
psql custody_manager
\di
```

Should show indexes on:
- Primary keys (all tables)
- users.email, users.oauth_id, users.role
- kits.code
- custody_events.kit_id, custody_events.event_type
- approval_requests.kit_id, approval_requests.status
- maintenance_events.kit_id, maintenance_events.is_open

### Check Enum Types

```bash
psql custody_manager
\dT+
```

Should show:
- `approvalstatus` - pending, approved, denied
- `custodyeventtype` - checkout_onprem, checkout_offsite, checkin, transfer, lost, found
- `kitstatus` - available, checked_out, in_maintenance, lost
- `userrole` - admin, armorer, coach, volunteer, parent

## Documentation

- **[SCHEMA.md](SCHEMA.md)** - Complete database schema documentation
- **[MIGRATIONS.md](MIGRATIONS.md)** - Migration reference and commands
- **[USER_MODEL.md](USER_MODEL.md)** - User model details
- **[OAUTH_SETUP.md](OAUTH_SETUP.md)** - OAuth configuration

## Troubleshooting

### "Target database is not up to date"

```bash
# Check which migrations are pending
alembic history

# Apply pending migrations
alembic upgrade head
```

### "Can't locate revision identified by 'xxx'"

Your migration chain might be broken. Check:
```bash
# List all revisions
alembic history

# Verify migration files exist
ls -la alembic/versions/
```

### "Column already exists" or "Table already exists"

Your database might be out of sync. Options:
1. Drop and recreate database (development only)
2. Manually stamp to current revision
3. Create a migration to add missing items

### Import Errors

Make sure you're in the backend directory and have activated your virtual environment:
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

## Production Deployment

### Pre-Deployment Checklist

- [ ] Backup production database
- [ ] Test migrations on staging environment
- [ ] Review migration SQL with `alembic upgrade --sql head`
- [ ] Plan rollback procedure
- [ ] Schedule maintenance window if needed

### Running Migrations in Production

```bash
# Backup database first!
pg_dump custody_manager > backup_$(date +%Y%m%d_%H%M%S).sql

# Apply migrations
alembic upgrade head

# Verify
alembic current
```

### Rollback Plan

If issues occur:
```bash
# Rollback migrations
alembic downgrade <previous_revision>

# Restore from backup if needed
psql custody_manager < backup_20260127_120000.sql
```

## Performance Monitoring

### Check Table Sizes

```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Check Index Usage

```sql
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;
```

Low scan counts indicate unused indexes.

### Check for Missing Indexes

```sql
SELECT 
    c.conrelid::regclass AS table_name,
    a.attname AS column_name
FROM pg_constraint c
JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey)
WHERE c.contype = 'f'
AND NOT EXISTS (
    SELECT 1 FROM pg_index i
    WHERE i.indrelid = c.conrelid
    AND a.attnum = ANY(i.indkey)
);
```

Should return no rows (all foreign keys should be indexed).

## Next Steps

After database setup:
1. Start the FastAPI server: `uvicorn app.main:app --reload`
2. Access API docs: http://localhost:8000/api/v1/docs
3. Configure OAuth providers (see OAUTH_SETUP.md)
4. Run tests: `pytest`

## Support

For issues or questions:
- Check [SCHEMA.md](SCHEMA.md) for database structure details
- See [MIGRATIONS.md](MIGRATIONS.md) for migration commands
- Review model files in `app/models/` for ORM details
