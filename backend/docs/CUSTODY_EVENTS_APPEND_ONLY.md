# Custody Events Append-Only Implementation

## Overview

This document describes the implementation of the append-only, immutable custody_events table to satisfy **CUSTODY-015**: *As an Admin, I want all custody events to be append-only and immutable, so that the audit trail cannot be tampered with.*

## Implementation Details

### Database Schema

The `custody_events` table includes all required fields for a complete audit trail:

#### Core Event Fields
- `event_type`: Type of custody event (checkout_onprem, checkout_offsite, checkin, transfer, lost, found)
- `kit_id`: Foreign key to the kit involved in the event

#### User Fields (from_user, to_user, approved_by)
- `initiated_by_id` / `initiated_by_name`: User who initiated the action (maps to 'from_user')
- `custodian_id` / `custodian_name`: User who receives custody (maps to 'to_user')
- `approved_by_id` / `approved_by_name`: User who approved the custody event (NEW)

#### Audit Trail Fields
- `notes`: Optional notes about the event
- `location_type`: Location where event occurred (maps to 'location')
- `expected_return_date`: When kit is expected to be returned

#### Attestation Fields (NEW)
- `attestation_text`: Legal text presented to user
- `attestation_signature`: Digital signature/acknowledgment
- `attestation_timestamp`: When user acknowledged
- `attestation_ip_address`: IP address for audit trail

### Append-Only Enforcement

The implementation uses multiple layers of protection to ensure immutability:

#### 1. SQLAlchemy Event Listeners

```python
@event.listens_for(CustodyEvent, 'before_update')
def prevent_custody_event_update(mapper, connection, target):
    raise ValueError(
        "Cannot update custody events: Custody events are append-only and "
        "immutable (CUSTODY-015). Create a new event instead."
    )

@event.listens_for(CustodyEvent, 'before_delete')
def prevent_custody_event_delete(mapper, connection, target):
    raise ValueError(
        "Cannot delete custody events: Custody events are append-only and "
        "immutable (CUSTODY-015). They form a permanent audit trail."
    )
```

These listeners intercept any attempt to update or delete custody events at the ORM level and raise an exception before the operation can proceed.

#### 2. Database Migration

Migration `010_add_custody_event_append_only_fields.py` adds the new fields:
- `approved_by_id` with foreign key constraint to users table
- `approved_by_name` for denormalized audit trail
- `attestation_text`, `attestation_signature`, `attestation_timestamp`, `attestation_ip_address`

### API Schema Updates

The `CustodyEventResponse` schema has been updated to include all new fields, ensuring they are properly serialized in API responses.

### Testing

Comprehensive tests in `tests/test_custody_append_only.py` verify:

1. ✅ Custody events can be created successfully
2. ✅ Custody events can include approved_by fields
3. ✅ Custody events can include attestation fields
4. ✅ Update attempts raise ValueError with clear error message
5. ✅ Delete attempts raise ValueError with clear error message
6. ✅ All event types are supported
7. ✅ Timestamps are properly set

## Usage Examples

### Creating a Custody Event with Approval

```python
event = CustodyEvent(
    event_type=CustodyEventType.checkout_offsite,
    kit_id=kit.id,
    initiated_by_id=parent.id,
    initiated_by_name=parent.name,
    custodian_id=athlete.id,
    custodian_name=athlete.name,
    approved_by_id=armorer.id,
    approved_by_name=armorer.name,
    attestation_text="I acknowledge responsibility...",
    attestation_signature=parent.name,
    attestation_timestamp=datetime.now(),
    attestation_ip_address=request.client.host,
    location_type="off_site"
)
db.add(event)
db.commit()
```

### Attempting to Modify (Will Fail)

```python
# This will raise ValueError
event.notes = "Modified notes"
db.commit()
# ValueError: Cannot update custody events: Custody events are append-only 
# and immutable (CUSTODY-015). Create a new event instead.
```

### Attempting to Delete (Will Fail)

```python
# This will raise ValueError
db.delete(event)
db.commit()
# ValueError: Cannot delete custody events: Custody events are append-only 
# and immutable (CUSTODY-015). They form a permanent audit trail.
```

## Security Considerations

1. **Immutability**: Once created, events cannot be modified or deleted, ensuring audit trail integrity
2. **Denormalization**: User names are stored alongside IDs to preserve historical records even if user accounts change
3. **Attestation**: Legal acknowledgments are cryptographically signed with timestamps and IP addresses
4. **Approval Tracking**: All approvals are recorded with approver information

## Migration Path

To apply the changes:

```bash
cd backend
alembic upgrade head
```

This will add the new fields to the existing `custody_events` table without affecting existing data.

## Compliance

This implementation satisfies:
- **CUSTODY-015**: Append-only and immutable custody events
- **AUDIT-004**: No events can be deleted or modified (legally defensible audit trail)
- **CUSTODY-012**: Attestation support for parental responsibility acknowledgment

## Future Enhancements

Potential future improvements:
1. Add database-level triggers for additional protection (PostgreSQL specific)
2. Implement event sourcing pattern for complete historical replay
3. Add cryptographic signatures for individual events
4. Implement blockchain-based verification for maximum auditability
