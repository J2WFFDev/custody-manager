# User Stories - WilcoSS Custody Manager

This document contains all user stories for the WilcoSS Custody & Equipment Manager application, organized by user role and epic.

## Overview

User stories follow the format:
```
As a [role]
I want to [action]
So that [benefit]
```

---

## Stories by User Role

### Admin

- **AUTH-001**: As an Admin, I want to assign roles to users (Armorer, Coach, Volunteer, Parent), so that access control is properly enforced.
- **AUTH-002**: As an Admin, I want to flag users as "verified adults", so that only approved adults can accept off-site custody.
- **AUDIT-001**: As an Admin, I want to export complete audit logs as CSV/JSON, so that I can respond to incidents or compliance requests.
- **AUDIT-002**: As an Admin, I want to view system-wide custody status, so that I know where all equipment is at any time.
- **AUDIT-003**: As an Admin, I want serial numbers to be encrypted in the database, so that they cannot be compromised in a data breach.
- **AUDIT-004**: As an Admin, I want assurance that no events can be deleted or modified, so that the audit trail is legally defensible.

### Armorer

- **AUTH-003**: As an Armorer, I want to log in with my Google or Microsoft account, so that I can access the system securely without managing passwords.
- **QR-001**: As an Armorer, I want to register new kits and generate QR codes, so that equipment can be tracked from day one.
- **QR-004**: As an Armorer, I want QR codes to not expose serial numbers, so that sensitive information remains secure.
- **CUSTODY-002**: As an Armorer, I want to approve off-site checkout requests, so that I maintain control over equipment leaving the facility.
- **CUSTODY-007**: As an Armorer, I want to report a kit as lost, so that everyone knows it's missing.
- **CUSTODY-008**: As an Armorer, I want to see soft warnings (overdue return, extended custody), so that I can follow up without blocking operations.
- **MAINT-001**: As an Armorer, I want to log maintenance events (open/close, parts replaced, round count), so that I can track equipment condition over time.
- **MAINT-002**: As an Armorer, I want to see soft warnings for overdue maintenance, so that I can schedule servicing before problems occur.
- **AUDIT-005**: As an Armorer, I want to view the complete custody and maintenance history for any kit, so that I can answer "who had this last" instantly.

### Coach

- **AUTH-004**: As a Coach, I want to log in with my Google or Microsoft account, so that I can access the system securely.
- **QR-002**: As a Coach, I want to scan a QR code to check out a kit on-premises, so that athletes can quickly get equipment for practice.
- **QR-003**: As a Coach, I want to scan a QR code to check in a kit, so that returns are fast and properly logged.
- **CUSTODY-001**: As a Coach, I want to check out a kit on-premises to an athlete, so that usage is logged without heavy process.
- **CUSTODY-003**: As a Coach, I want to approve off-site checkout requests, so that I can authorize athletes to take equipment to matches.
- **CUSTODY-004**: As a Coach, I want to check in a kit quickly, so that returns are logged immediately.
- **CUSTODY-005**: As a Coach, I want to transfer custody of a kit to another user, so that handoffs are documented.
- **CUSTODY-006**: As a Coach, I want to see which kits are currently checked out and by whom, so that I can track equipment during practice.
- **MAINT-003**: As a Coach, I want to see if a kit is currently in maintenance, so that I don't try to assign it to an athlete.

### Volunteer

- **CUSTODY-009**: As a Volunteer, I want to help athletes check in/out kits by scanning QR codes, so that I can assist with equipment management under supervision.
- **CUSTODY-010**: As a Volunteer, I want to see kit status (available, checked out, in maintenance), so that I can direct athletes appropriately.

### Parent (Verified Adult)

- **AUTH-005**: As a Parent, I want to log in securely with my Google or Microsoft account, so that I can accept custody responsibility.
- **CUSTODY-011**: As a Parent, I want to check out a kit for my child to take off-site, so that they can practice or compete away from the facility.
- **CUSTODY-012**: As a Parent, I want to acknowledge responsibility via a clear attestation statement, so that I understand my legal obligations.
- **CUSTODY-013**: As a Parent, I want to see what equipment is assigned to my child, so that I can ensure it's returned on time.
- **CUSTODY-014**: As a Parent, I want to receive soft warnings if a return is overdue, so that I can avoid causing issues for the organization.

---

## Stories by Epic

### Epic #1: Initial Project Planning and System Architecture

- **DEV-001**: As a Developer, I want a well-structured React frontend with Vite and TailwindCSS, so that I can build UI quickly and efficiently.
- **DEV-002**: As a Developer, I want a FastAPI backend with PostgreSQL, so that I have a modern, type-safe API foundation.
- **DEV-003**: As a Developer, I want automated deployments via Vercel and Railway, so that code changes go live automatically.
- **DEV-004**: As a Developer, I want clear documentation for local dev setup, so that I (or future contributors) can get started quickly.

### Epic #2: Authentication & Identity Management

- **AUTH-001**: As an Admin, I want to assign roles to users (Armorer, Coach, Volunteer, Parent), so that access control is properly enforced.
- **AUTH-002**: As an Admin, I want to flag users as "verified adults", so that only approved adults can accept off-site custody.
- **AUTH-003**: As an Armorer, I want to log in with my Google or Microsoft account, so that I can access the system securely without managing passwords.
- **AUTH-004**: As a Coach, I want to log in with my Google or Microsoft account, so that I can access the system securely.
- **AUTH-005**: As a Parent, I want to log in securely with my Google or Microsoft account, so that I can accept custody responsibility.
- **AUTH-006**: As any User, I want my session to be secure with JWT tokens, so that my account cannot be compromised.

### Epic #3: QR-Based Operations and Kit Management

- **QR-001**: As an Armorer, I want to register new kits and generate QR codes, so that equipment can be tracked from day one.
- **QR-002**: As a Coach, I want to scan a QR code to check out a kit on-premises, so that athletes can quickly get equipment for practice.
- **QR-003**: As a Coach, I want to scan a QR code to check in a kit, so that returns are fast and properly logged.
- **QR-004**: As an Armorer, I want QR codes to not expose serial numbers, so that sensitive information remains secure.
- **QR-005**: As a Coach/Armorer, I want a manual code entry fallback, so that I can still operate if the camera doesn't work.

### Epic #4: Custody Event Management & Flow

- **CUSTODY-001**: As a Coach, I want to check out a kit on-premises to an athlete, so that usage is logged without heavy process.
- **CUSTODY-002**: As an Armorer, I want to approve off-site checkout requests, so that I maintain control over equipment leaving the facility.
- **CUSTODY-003**: As a Coach, I want to approve off-site checkout requests, so that I can authorize athletes to take equipment to matches.
- **CUSTODY-004**: As a Coach, I want to check in a kit quickly, so that returns are logged immediately.
- **CUSTODY-005**: As a Coach, I want to transfer custody of a kit to another user, so that handoffs are documented.
- **CUSTODY-006**: As a Coach, I want to see which kits are currently checked out and by whom, so that I can track equipment during practice.
- **CUSTODY-007**: As an Armorer, I want to report a kit as lost, so that everyone knows it's missing.
- **CUSTODY-008**: As an Armorer, I want to see soft warnings (overdue return, extended custody), so that I can follow up without blocking operations.
- **CUSTODY-009**: As a Volunteer, I want to help athletes check in/out kits by scanning QR codes, so that I can assist with equipment management under supervision.
- **CUSTODY-010**: As a Volunteer, I want to see kit status (available, checked out, in maintenance), so that I can direct athletes appropriately.
- **CUSTODY-011**: As a Parent, I want to check out a kit for my child to take off-site, so that they can practice or compete away from the facility.
- **CUSTODY-012**: As a Parent, I want to acknowledge responsibility via a clear attestation statement, so that I understand my legal obligations.
- **CUSTODY-013**: As a Parent, I want to see what equipment is assigned to my child, so that I can ensure it's returned on time.
- **CUSTODY-014**: As a Parent, I want to receive soft warnings if a return is overdue, so that I can avoid causing issues for the organization.
- **CUSTODY-015**: As an Admin, I want all custody events to be append-only and immutable, so that the audit trail cannot be tampered with.

### Epic #5: Maintenance Tracking & Scheduling

- **MAINT-001**: As an Armorer, I want to log maintenance events (open/close, parts replaced, round count), so that I can track equipment condition over time.
- **MAINT-002**: As an Armorer, I want to see soft warnings for overdue maintenance, so that I can schedule servicing before problems occur.
- **MAINT-003**: As a Coach, I want to see if a kit is currently in maintenance, so that I don't try to assign it to an athlete.
- **MAINT-004**: As an Armorer, I want to view maintenance history for a kit, so that I can make informed servicing decisions.

### Epic #6: Data & Audit Trail Requirements

- **AUDIT-001**: As an Admin, I want to export complete audit logs as CSV/JSON, so that I can respond to incidents or compliance requests.
- **AUDIT-002**: As an Admin, I want to view system-wide custody status, so that I know where all equipment is at any time.
- **AUDIT-003**: As an Admin, I want serial numbers to be encrypted in the database, so that they cannot be compromised in a data breach.
- **AUDIT-004**: As an Admin, I want assurance that no events can be deleted or modified, so that the audit trail is legally defensible.
- **AUDIT-005**: As an Armorer, I want to view the complete custody and maintenance history for any kit, so that I can answer "who had this last" instantly.
- **AUDIT-006**: As any User, I want to see an audit trail in the UI, so that I can verify recent activity.

---

## Acceptance Criteria Guidelines

Each user story should have acceptance criteria defining "done". Examples:

**AUTH-001**: As an Admin, I want to assign roles to users
- Admin can view list of all users
- Admin can select a user and change their role via dropdown
- Role changes are saved and immediately reflected
- Only Admin role can perform this action
- Audit log records role changes

**QR-002**: As a Coach, I want to scan a QR code to check out a kit
- Camera permission requested on first use
- QR scanner component activates camera
- Valid kit QR code triggers checkout flow
- Invalid code shows error message
- Manual entry fallback available
- Checkout completes in < 15 seconds

---

## Story Status Tracking

Stories are implemented via the GitHub issues in this repository. Each issue references the relevant user story ID(s) in its description.