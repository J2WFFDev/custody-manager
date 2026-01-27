# Off-Site Checkout Flow Implementation

This document describes the implementation of the off-site checkout flow with multi-role approval for the WilcoSS Custody Manager.

## Overview

The off-site checkout flow allows verified adults (typically parents) to request permission to take equipment kits off-site. These requests require approval from either an Armorer or Coach before the kit is released.

## User Stories Addressed

- **CUSTODY-002**: As an Armorer, I want to approve off-site checkout requests, so that I maintain control over equipment leaving the facility.
- **CUSTODY-003**: As a Coach, I want to approve off-site checkout requests, so that I can authorize athletes to take equipment to matches.
- **CUSTODY-011**: As a Parent, I want to check out a kit for my child to take off-site, so that they can practice or compete away from the facility.
- **AUTH-002**: As an Admin, I want to flag users as "verified adults", so that only approved adults can accept off-site custody.

## Architecture

### Database Schema

#### approval_requests Table
```sql
CREATE TABLE approval_requests (
  id SERIAL PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Kit reference
  kit_id INTEGER NOT NULL REFERENCES kits(id),
  
  -- Requester (e.g., Parent)
  requester_id INTEGER NOT NULL REFERENCES users(id),
  requester_name VARCHAR(200) NOT NULL,
  
  -- Custodian (e.g., athlete/child)
  custodian_id INTEGER REFERENCES users(id),
  custodian_name VARCHAR(200) NOT NULL,
  
  -- Approval status
  status approval_status NOT NULL DEFAULT 'pending',
  
  -- Approver details (Armorer or Coach)
  approver_id INTEGER REFERENCES users(id),
  approver_name VARCHAR(200),
  approver_role VARCHAR(50),
  
  -- Request details
  notes VARCHAR(1000),
  denial_reason VARCHAR(500)
);

CREATE TYPE approval_status AS ENUM ('pending', 'approved', 'denied');
```

### Backend API Endpoints

#### 1. POST /api/v1/custody/offsite-request
**Purpose**: Submit an off-site checkout request

**Authorization**: Requires verified_adult flag

**Request Body**:
```json
{
  "kit_code": "KIT-001",
  "custodian_name": "John Athlete",
  "custodian_id": 123,
  "notes": "Competition at XYZ, weekend practice"
}
```

**Response** (201 Created):
```json
{
  "message": "Off-site checkout request for kit 'Test Kit' submitted successfully. Awaiting approval from Armorer or Coach.",
  "approval_request": {
    "id": 1,
    "kit_id": 1,
    "kit_name": "Test Kit",
    "kit_code": "KIT-001",
    "requester_id": 5,
    "requester_name": "Jane Parent",
    "custodian_name": "John Athlete",
    "status": "pending",
    "notes": "Competition at XYZ, weekend practice",
    "created_at": "2026-01-27T10:30:00Z"
  }
}
```

**Error Responses**:
- 403 Forbidden: User is not a verified adult
- 404 Not Found: Kit code not found
- 400 Bad Request: Kit is not available or already has pending request

#### 2. POST /api/v1/custody/offsite-approve
**Purpose**: Approve or deny an off-site checkout request

**Authorization**: Requires Armorer or Coach role

**Request Body**:
```json
{
  "approval_request_id": 1,
  "approve": true,
  "denial_reason": "Kit needs maintenance" // Required if approve=false
}
```

**Response** (200 OK) - Approval:
```json
{
  "message": "Off-site checkout request approved. Kit 'Test Kit' has been checked out to John Athlete.",
  "approval_request": {
    "id": 1,
    "status": "approved",
    "approver_id": 2,
    "approver_name": "Coach Smith",
    "approver_role": "coach",
    ...
  },
  "custody_event": {
    "id": 10,
    "event_type": "checkout_offsite",
    "location_type": "off_site",
    ...
  }
}
```

**Response** (200 OK) - Denial:
```json
{
  "message": "Off-site checkout request denied. Reason: Kit needs maintenance",
  "approval_request": {
    "id": 1,
    "status": "denied",
    "approver_id": 2,
    "approver_name": "Coach Smith",
    "approver_role": "coach",
    "denial_reason": "Kit needs maintenance",
    ...
  },
  "custody_event": null
}
```

**Error Responses**:
- 403 Forbidden: User is not an Armorer or Coach
- 404 Not Found: Approval request not found
- 400 Bad Request: Request already processed, denial reason missing, or kit no longer available

#### 3. GET /api/v1/custody/pending-approvals
**Purpose**: List all pending off-site checkout requests

**Authorization**: Requires Armorer or Coach role

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "kit_id": 1,
    "kit_name": "Test Kit",
    "kit_code": "KIT-001",
    "requester_name": "Jane Parent",
    "custodian_name": "John Athlete",
    "status": "pending",
    "notes": "Competition at XYZ",
    "created_at": "2026-01-27T10:30:00Z"
  },
  ...
]
```

**Error Responses**:
- 403 Forbidden: User is not an Armorer or Coach

### Frontend Components

#### 1. OffSiteCheckoutModal
- **Location**: `frontend/src/components/OffSiteCheckoutModal.tsx`
- **Purpose**: Modal for verified adults to submit off-site checkout requests
- **Features**:
  - Kit code input (manual or QR scan)
  - Custodian name input
  - Optional notes field
  - Verified adult requirement notice
  - Error handling and validation

#### 2. ApprovalDashboard
- **Location**: `frontend/src/components/ApprovalDashboard.tsx`
- **Purpose**: Dashboard for Armorers and Coaches to review and approve requests
- **Features**:
  - List of pending approval requests
  - Approve/deny actions
  - Denial reason modal
  - Real-time updates after actions
  - Empty state when no pending requests

#### 3. Approvals Page
- **Location**: `frontend/src/pages/Approvals.tsx`
- **Route**: `/approvals`
- **Purpose**: Main page for approval management

### User Workflow

#### Requesting Off-Site Checkout (Parent)
1. Navigate to Kits page
2. Find available kit
3. Click "Request Off-Site Checkout" button
4. Fill out form:
   - Kit code (pre-filled from button click)
   - Custodian name (e.g., child's name)
   - Optional notes
5. Submit request
6. Receive confirmation that request is pending approval

#### Approving/Denying Requests (Armorer/Coach)
1. Navigate to Approvals page via navigation menu
2. View list of pending requests
3. Review request details:
   - Kit information
   - Requester name
   - Custodian name
   - Request notes
   - Timestamp
4. Choose action:
   - **Approve**: Kit is immediately checked out off-site, custody event created
   - **Deny**: Provide reason, kit remains available

## Security Considerations

### Verified Adult Requirement
- Only users with `verified_adult=true` can submit off-site checkout requests
- This flag is set by Admins through the user management interface
- Prevents unauthorized off-site custody

### Multi-Role Approval
- Both Armorers AND Coaches can approve requests
- Provides flexibility while maintaining control
- Either role is sufficient for approval

### Audit Trail
- All approval requests are permanently recorded
- When approved, creates immutable custody_event with type `checkout_offsite`
- Tracks who requested, who approved, when, and why
- Denial reasons are recorded for accountability

### ⚠️ Important Security Note
The custody endpoints currently use **mock authentication** for development/testing purposes. This MUST be replaced with proper JWT-based authentication (already implemented in `app/api/v1/endpoints/auth.py`) before production deployment. See TODO comments in the code.

## Testing

### Backend Tests
- **Location**: `backend/tests/test_offsite_approval.py`
- **Coverage**: 11 comprehensive tests covering:
  - Successful request by verified parent
  - Rejection of unverified parent
  - Kit not found scenarios
  - Kit availability checks
  - Approval by Armorer
  - Approval by Coach
  - Denial workflow
  - Denial reason requirement
  - Unauthorized user attempts
  - Listing pending approvals
  - Permission checks for listing

**Run tests**:
```bash
cd backend
python -m pytest tests/test_offsite_approval.py -v
```

### Test Results
✅ All 11 tests passing
✅ No security vulnerabilities detected by CodeQL

## Database Migration

**Migration File**: `backend/alembic/versions/004_create_approval_requests.py`

**Apply migration**:
```bash
cd backend
alembic upgrade head
```

**Rollback migration**:
```bash
cd backend
alembic downgrade -1
```

## Future Enhancements

1. **Email Notifications**: Notify approvers when new requests are submitted
2. **SMS Alerts**: Alert parents when their request is approved/denied
3. **Request Expiration**: Auto-deny requests older than X hours
4. **Batch Approval**: Allow approving multiple requests at once
5. **Request History**: Show approved/denied history for users
6. **Analytics Dashboard**: Track approval rates, response times, etc.
7. **QR Code Integration**: Full QR scanner implementation (currently placeholder)
8. **Mobile App**: Native mobile experience for quicker approvals

## Deployment Checklist

Before deploying to production:

- [ ] Replace mock authentication with JWT-based auth
- [ ] Configure email/SMS notification service
- [ ] Set up proper role-based access control middleware
- [ ] Test with production database
- [ ] Verify SSL/TLS configuration
- [ ] Set up monitoring and alerting
- [ ] Document admin procedures for managing verified adults
- [ ] Train staff on approval workflow
- [ ] Create user documentation

## Support

For questions or issues:
- Repository: https://github.com/J2WFFDev/custody-manager
- Issues: https://github.com/J2WFFDev/custody-manager/issues
