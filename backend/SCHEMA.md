# Database Schema Documentation

## Overview
The WilcoSS Custody Manager uses PostgreSQL with append-only event tables for audit compliance.

## Tables

### Users
Stores user authentication and role information.
- **Primary Key:** id
- **Unique Constraints:** email, (oauth_provider, oauth_id)
- **Roles:** admin, armorer, coach, volunteer, parent

### Kits
Equipment/kit registry with current status and custodian tracking.
- **Primary Key:** id
- **Unique Constraints:** qr_code
- **Statuses:** available, checked_out, in_maintenance, lost

### Custody Events (Append-Only)
Immutable log of all custody transfers and actions.
- **Primary Key:** id
- **Append-Only:** Updates and deletes are blocked via PostgreSQL rules
- **Event Types:** checkout_onprem, checkout_offsite, checkin, transfer, lost, found

### Maintenance Events (Append-Only)
Immutable log of all maintenance activities.
- **Primary Key:** id
- **Append-Only:** Updates and deletes are blocked via PostgreSQL rules
- **Event Types:** open, close

## Relationships
- Users → Kits (current_custodian_id)
- Kits → Custody Events (kit_id)
- Kits → Maintenance Events (kit_id)
- Users → Custody Events (from_user_id, to_user_id, approved_by_user_id)
- Users → Maintenance Events (performed_by_user_id)

## Indexes
All foreign keys are indexed for query performance.
Event tables have indexes on created_at (DESC) for timeline queries.

## Security
- Serial numbers are encrypted using field-level encryption
- Append-only tables prevent tampering with audit trail
- No soft deletes - all events are permanent
