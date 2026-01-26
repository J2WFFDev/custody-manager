# Before and After Examples

## Example 1: Issue #8 (Implementation Issue)

### BEFORE
```markdown
Add Microsoft OAuth login flow to FastAPI backend.
- Use Authlib or python-social-auth
- Store user info after login
- Issue JWT for session management
- Document flow and testing
```

### AFTER
```markdown
Add Microsoft OAuth login flow to FastAPI backend.

### Related User Stories
- **AUTH-003**: As an Armorer, I want to log in with my Google or Microsoft account, so that I can access the system securely without managing passwords.
- **AUTH-004**: As a Coach, I want to log in with my Google or Microsoft account, so that I can access the system securely.
- **AUTH-005**: As a Parent, I want to log in securely with my Google or Microsoft account, so that I can accept custody responsibility.

- Use Authlib or python-social-auth
- Store user info after login
- Issue JWT for session management
- Document flow and testing
```

---

## Example 2: Issue #28 (Multi-Story Issue)

### BEFORE
```markdown
Build custody flow for off-site kit checkout with role and verified adult checks, plus Armorer/Coach approval.
- API endpoint for off-site checkout
- Frontend flow for approval
- Document flow and test cases
```

### AFTER
```markdown
Build custody flow for off-site kit checkout with role and verified adult checks, plus Armorer/Coach approval.

### Related User Stories
- **CUSTODY-002**: As an Armorer, I want to approve off-site checkout requests, so that I maintain control over equipment leaving the facility.
- **CUSTODY-003**: As a Coach, I want to approve off-site checkout requests, so that I can authorize athletes to take equipment to matches.
- **CUSTODY-011**: As a Parent, I want to check out a kit for my child to take off-site, so that they can practice or compete away from the facility.

- API endpoint for off-site checkout
- Frontend flow for approval
- Document flow and test cases
```

---

## Example 3: Issue #4 (Epic with 15 Stories)

### BEFORE
```markdown
Enforce auditable custody event flows and approvals as described in the PRD.

### Scope
- Append-only custody event log
- Role/approval flows for on-prem and off-site custody
- Responsibility attestation
- Reporting of lost/found
- Warnings (soft, non-blocking)

### Acceptance Criteria
- All custody actions logged as events
- Role-based approvals and verification enforced
- Users can check in/out, transfer, report lost/found
- Warnings surfaced but do not block

---
**Sub-epic under project planning.**
```

### AFTER
```markdown
Enforce auditable custody event flows and approvals as described in the PRD.

### Related User Stories
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

### Scope
- Append-only custody event log
- Role/approval flows for on-prem and off-site custody
- Responsibility attestation
- Reporting of lost/found
- Warnings (soft, non-blocking)

### Acceptance Criteria
- All custody actions logged as events
- Role-based approvals and verification enforced
- Users can check in/out, transfer, report lost/found
- Warnings surfaced but do not block

---
**Sub-epic under project planning.**
```

---

## Key Improvements

✅ **Traceability**: Each issue now clearly shows which user stories it implements  
✅ **Context**: Developers can see the user needs behind each technical task  
✅ **Consistency**: All issues follow the same format (matching issue #7)  
✅ **Documentation**: User stories provide the "why" behind the "what"  
✅ **Preserved Content**: All original technical details remain intact  

## Impact

- Better understanding of user needs for each issue
- Easier prioritization based on user value
- Clear connection between requirements (USER_STORIES.md) and implementation (issues)
- Improved team communication about feature purpose
