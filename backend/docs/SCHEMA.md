# Database Schema Documentation

## Overview

The WilcoSS Custody & Equipment Manager uses PostgreSQL as its primary database. The schema is designed to track custody of firearm kits, maintenance events, and approval workflows with complete audit trail capabilities.

## Design Principles

1. **Append-Only Audit Trail**: Custody and maintenance events are never deleted, only appended
2. **Role-Based Access Control**: User roles determine permissions throughout the system
3. **Soft Warnings**: Expected return dates enable non-blocking warnings for overdue items
4. **Denormalized Names**: User and custodian names are stored alongside IDs for historical accuracy
5. **Type Safety**: Enums are used for status fields to ensure data integrity

## Entity Relationship Overview

```
┌─────────────────┐
│     Users       │
│  (AUTH-001/002) │
└────────┬────────┘
         │
         │ owns/manages
         │
    ┌────┴────┬──────────────┬──────────────┐
    │         │              │              │
┌───▼────┐ ┌─▼───────────┐ ┌▼─────────────┐ ┌▼──────────────┐
│  Kits  │ │ Custody     │ │ Maintenance  │ │  Approval     │
│ (QR)   │ │ Events      │ │ Events       │ │  Requests     │
│        │ │ (CUSTODY)   │ │ (MAINT)      │ │ (CUSTODY)     │
└────────┘ └─────────────┘ └──────────────┘ └───────────────┘
```

## Core Tables

### 1. Users Table
**Purpose**: Store authenticated users with OAuth credentials and role assignments

**User Stories**: AUTH-001, AUTH-002, AUTH-003, AUTH-004, AUTH-005, AUTH-006

**Documentation**: [USER_MODEL.md](USER_MODEL.md)

**Key Features**:
- OAuth authentication (Google, Microsoft)
- Role-based access control (Admin, Armorer, Coach, Volunteer, Parent)
- Verified adult flag for off-site custody authorization
- Soft delete with `is_active` flag

**Indexes**:
- Primary: `ix_users_id` (id)
- Unique: `ix_users_email` (email)
- Performance: `ix_users_oauth_id` (oauth_id)

---

### 2. Kits Table
**Purpose**: Track firearm kits and equipment with current status and custody

**User Stories**: QR-001, QR-002, QR-003

**Key Features**:
- Unique QR code identifier (code field)
- Status tracking (available, checked_out, in_maintenance, lost)
- Current custodian tracking
- Serial numbers NOT stored in QR codes (security requirement QR-004)

**Indexes**:
- Primary: `ix_kits_id` (id)
- Unique: `ix_kits_code` (code) - for fast QR lookups

**Schema**:
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | Unique identifier |
| created_at | DateTime(TZ) | Not Null, Default: now() | Creation timestamp |
| updated_at | DateTime(TZ) | Not Null, Default: now() | Last update timestamp |
| code | String(50) | Not Null, Unique, Indexed | QR code identifier |
| name | String(200) | Not Null | Kit display name |
| description | String(500) | Nullable | Kit description |
| status | KitStatus Enum | Not Null, Default: 'available' | Current status |
| current_custodian_id | Integer | Nullable, FK(users.id) | Current custodian user ID |
| current_custodian_name | String(200) | Nullable | Current custodian name |

**Enum: KitStatus**
```python
class KitStatus(str, enum.Enum):
    available = "available"
    checked_out = "checked_out"
    in_maintenance = "in_maintenance"
    lost = "lost"
```

---

### 3. Custody Events Table
**Purpose**: Immutable audit log of all custody changes

**User Stories**: CUSTODY-001 through CUSTODY-015

**Key Features**:
- Append-only (no updates or deletes)
- Tracks check-out, check-in, transfers, lost/found
- Supports both on-premises and off-site custody
- Expected return dates for soft warnings
- Denormalized names for historical accuracy

**Indexes**:
- Primary: `ix_custody_events_id` (id)
- Performance: `ix_custody_events_kit_id` (kit_id) - for kit history queries

**Schema**:
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | Unique identifier |
| created_at | DateTime(TZ) | Not Null, Default: now() | Event timestamp |
| updated_at | DateTime(TZ) | Not Null, Default: now() | Update timestamp |
| event_type | CustodyEventType | Not Null | Type of custody event |
| kit_id | Integer | Not Null, FK(kits.id), Indexed | Kit being transferred |
| initiated_by_id | Integer | Not Null, FK(users.id) | User who initiated action |
| initiated_by_name | String(200) | Not Null | Name of initiator |
| custodian_id | Integer | Nullable, FK(users.id) | User receiving custody |
| custodian_name | String(200) | Not Null | Name of custodian |
| notes | String(1000) | Nullable | Optional notes |
| location_type | String(50) | Not Null, Default: 'on_premises' | Location context |
| expected_return_date | Date | Nullable | For soft warnings |

**Enum: CustodyEventType**
```python
class CustodyEventType(str, enum.Enum):
    checkout_onprem = "checkout_onprem"
    checkout_offsite = "checkout_offsite"
    checkin = "checkin"
    transfer = "transfer"
    lost = "lost"
    found = "found"
```

---

### 4. Approval Requests Table
**Purpose**: Track multi-role approval workflow for off-site custody

**User Stories**: CUSTODY-010, CUSTODY-011, CUSTODY-012

**Key Features**:
- Requester submits request (typically Parent)
- Approver reviews and approves/denies (Armorer or Coach)
- Digital responsibility attestation
- Expected return date tracking
- Audit trail with IP address and timestamp

**Indexes**:
- Primary: `ix_approval_requests_id` (id)
- Performance: `ix_approval_requests_kit_id` (kit_id)

**Schema**:
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | Unique identifier |
| created_at | DateTime(TZ) | Not Null, Default: now() | Request creation |
| updated_at | DateTime(TZ) | Not Null, Default: now() | Last update |
| kit_id | Integer | Not Null, FK(kits.id), Indexed | Kit being requested |
| requester_id | Integer | Not Null, FK(users.id) | User requesting custody |
| requester_name | String(200) | Not Null | Requester name |
| custodian_id | Integer | Nullable, FK(users.id) | Actual custodian |
| custodian_name | String(200) | Not Null | Custodian name |
| status | ApprovalStatus | Not Null, Default: 'pending' | Approval status |
| approver_id | Integer | Nullable, FK(users.id) | User who approved/denied |
| approver_name | String(200) | Nullable | Approver name |
| approver_role | String(50) | Nullable | Role of approver |
| notes | String(1000) | Nullable | Request notes |
| denial_reason | String(500) | Nullable | Reason if denied |
| expected_return_date | Date | Nullable | Expected return |
| attestation_text | Text | Nullable | Legal attestation text |
| attestation_signature | String(200) | Nullable | Digital signature |
| attestation_timestamp | DateTime | Nullable | When attested |
| attestation_ip_address | String(45) | Nullable | IP for audit trail |

**Enum: ApprovalStatus**
```python
class ApprovalStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    denied = "denied"
```

---

### 5. Maintenance Events Table
**Purpose**: Track when kits enter and exit maintenance

**User Stories**: MAINT-001, MAINT-002, MAINT-003

**Key Features**:
- Open/close tracking with `is_open` flag
- Track who opened and who closed
- Round count and parts replacement tracking
- Notes for maintenance details

**Indexes**:
- Primary: `ix_maintenance_events_id` (id)
- Performance: `ix_maintenance_events_kit_id` (kit_id)

**Schema**:
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, Auto-increment | Unique identifier |
| created_at | DateTime(TZ) | Not Null, Default: now() | When opened |
| updated_at | DateTime(TZ) | Not Null, Default: now() | When last updated |
| kit_id | Integer | Not Null, FK(kits.id), Indexed | Kit in maintenance |
| opened_by_id | Integer | Not Null, FK(users.id) | User who opened |
| opened_by_name | String(200) | Not Null | Opener name |
| closed_by_id | Integer | Nullable, FK(users.id) | User who closed |
| closed_by_name | String(200) | Nullable | Closer name |
| notes | Text | Nullable | Maintenance notes |
| parts_replaced | Text | Nullable | Parts description |
| round_count | Integer | Nullable | Rounds fired count |
| is_open | Boolean | Not Null, Default: true | Open/closed status |

---

## Migrations

### Migration History

| Revision | File | Description |
|----------|------|-------------|
| 001 | `001_add_user_model.py` | Create users table with OAuth fields |
| 002 | `002_create_kits.py` | Create kits table with QR codes |
| 003 | `003_create_custody_events.py` | Create custody events audit trail |
| 004 | `004_create_approval_requests.py` | Create approval workflow table |
| 005 | `005_add_attestation_fields.py` | Add responsibility attestation |
| 006 | `006_create_maintenance_events.py` | Create maintenance tracking table |
| 007 | `007_convert_user_role_to_enum.py` | Convert role to enum for type safety |
| 008 | `008_add_expected_return_date.py` | Add expected return date fields |

### Running Migrations

```bash
# Navigate to backend directory
cd backend

# Check current migration status
alembic current

# View pending migrations
alembic history

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>
```

### Creating New Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description of changes"

# Create empty migration template
alembic revision -m "description of changes"
```

---

## Performance Considerations

### Indexes

All tables have the following indexes:
1. **Primary Key Index**: Automatic on `id` column
2. **Foreign Key Indexes**: On all FK columns referencing users and kits
3. **Business Logic Indexes**: 
   - `users.email` (unique) - OAuth lookup
   - `users.oauth_id` - OAuth provider lookup
   - `kits.code` (unique) - QR code scanning
   - `custody_events.kit_id` - Kit history queries
   - `approval_requests.kit_id` - Pending requests lookup
   - `maintenance_events.kit_id` - Maintenance history queries

### Query Optimization Tips

1. **Kit History**: Index on `custody_events.kit_id` enables fast timeline queries
2. **User Lookup**: Compound index on `oauth_provider` + `oauth_id` would speed up auth
3. **Pending Approvals**: Consider index on `approval_requests.status` for filtering
4. **Open Maintenance**: Index on `maintenance_events.is_open` for active maintenance queries

---

## Data Integrity

### Foreign Key Constraints

All foreign keys use `ON DELETE` default behavior (RESTRICT) to prevent orphaned records:
- `custody_events.kit_id` → `kits.id`
- `custody_events.initiated_by_id` → `users.id`
- `custody_events.custodian_id` → `users.id`
- `approval_requests.kit_id` → `kits.id`
- `approval_requests.requester_id` → `users.id`
- `approval_requests.custodian_id` → `users.id`
- `approval_requests.approver_id` → `users.id`
- `maintenance_events.kit_id` → `kits.id`
- `maintenance_events.opened_by_id` → `users.id`
- `maintenance_events.closed_by_id` → `users.id`

### Enum Types

PostgreSQL ENUM types are used for:
- `UserRole`: admin, armorer, coach, volunteer, parent
- `KitStatus`: available, checked_out, in_maintenance, lost
- `CustodyEventType`: checkout_onprem, checkout_offsite, checkin, transfer, lost, found
- `ApprovalStatus`: pending, approved, denied

---

## Security Considerations

1. **Serial Numbers**: NOT stored in QR codes or exposed via API (QR-004)
2. **Audit Trail**: Custody events are append-only, never deleted
3. **Denormalized Names**: Names stored at event time preserve historical accuracy
4. **Attestation Tracking**: IP addresses and timestamps for legal compliance
5. **Soft Delete**: Users marked inactive rather than deleted
6. **Row-Level Security**: Could be added for multi-tenant scenarios

---

## Backup and Recovery

### Recommended Backup Strategy

1. **Daily Full Backups**: Complete database dump
2. **Point-in-Time Recovery**: Enable WAL archiving
3. **Retention**: Keep 30 days of backups minimum
4. **Test Restores**: Monthly restoration tests

### Critical Tables for Backup Priority

1. `custody_events` - Immutable audit trail (highest priority)
2. `maintenance_events` - Compliance records
3. `users` - Authentication data
4. `approval_requests` - Legal attestations
5. `kits` - Equipment inventory

---

## Future Enhancements

### Potential Schema Additions

1. **Serial Numbers Table**: Encrypted storage separate from QR codes
2. **Audit Log Table**: System-level change tracking
3. **Notifications Table**: Overdue return reminders
4. **Organizations Table**: Multi-organization support
5. **Teams Table**: Group kits by team/program
6. **Attachments Table**: Photos, documents, certificates
7. **Scheduled Maintenance Table**: Preventive maintenance planning

### Performance Improvements

1. **Partitioning**: Partition `custody_events` by year
2. **Materialized Views**: Pre-computed kit status summaries
3. **Full-Text Search**: Enable FTS on notes and descriptions
4. **Compound Indexes**: `(kit_id, created_at)` for timeline queries

---

## Monitoring and Maintenance

### Database Health Checks

```sql
-- Check table sizes
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;

-- Check for missing indexes on foreign keys
SELECT c.conrelid::regclass AS table_name,
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

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-27 | Initial schema documentation with all core tables |

---

## See Also

- [USER_MODEL.md](USER_MODEL.md) - Detailed user model documentation
- [OAUTH_SETUP.md](OAUTH_SETUP.md) - OAuth configuration guide
- [../../ARCHITECTURE.md](../../ARCHITECTURE.md) - Overall system architecture
