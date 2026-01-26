# GitHub Issues User Story Update

This directory contains scripts and generated files for updating all GitHub issues with user story references.

## What Was Done

Generated updated markdown files for 34 GitHub issues (excluding issue #7 which was already updated as a template). Each issue now includes a "Related User Stories" section that references the relevant user stories from `USER_STORIES.md`.

## Generated Files

### Issues Directory (`issues/`)
Contains 34 markdown files (1.md through 35.md, excluding 7.md) with the updated issue descriptions. Each file contains:
1. Original issue description
2. **NEW**: Related User Stories section
3. Original remaining content (bullets, acceptance criteria, etc.)

### Scripts

1. **`process_issues.py`** - Core logic for parsing user stories and updating issue bodies
2. **`generate_all_issues.py`** - Main script that processes all issues
3. **`github_issues_data.json`** - Cached GitHub issue data

## Issue to User Story Mappings

### Epic #1: Project Setup (Issues 12-16)
- Issue #12: DEV-001
- Issue #13: DEV-002
- Issue #14: DEV-002
- Issue #15: DEV-003
- Issue #16: DEV-003

### Epic #2: Authentication (Issues 8-11)
- Issue #8: AUTH-003, AUTH-004, AUTH-005
- Issue #9: AUTH-001, AUTH-002
- Issue #10: AUTH-006
- Issue #11: AUTH-001, AUTH-002

### Epic #3: QR Operations (Issues 33-35)
- Issue #33: QR-001
- Issue #34: QR-001
- Issue #35: QR-002, QR-003, QR-005

### Epic #4: Custody Management (Issues 26-32)
- Issue #26: CUSTODY-015
- Issue #27: CUSTODY-001, QR-002
- Issue #28: CUSTODY-002, CUSTODY-003, CUSTODY-011
- Issue #29: CUSTODY-012
- Issue #30: CUSTODY-005
- Issue #31: CUSTODY-007
- Issue #32: CUSTODY-008, CUSTODY-014

### Epic #5: Maintenance (Issues 22-25)
- Issue #22: MAINT-001
- Issue #23: MAINT-001
- Issue #24: MAINT-002
- Issue #25: MAINT-003, MAINT-004

### Epic #6: Audit/Data (Issues 17-21)
- Issue #17: AUDIT-005, AUDIT-006
- Issue #18: AUDIT-001
- Issue #19: AUDIT-002, AUDIT-006
- Issue #20: AUDIT-004
- Issue #21: AUDIT-003

### Epic Issues (Issues 1-6)
- Issue #1: All DEV stories (DEV-001 through DEV-004)
- Issue #2: All AUTH stories (AUTH-001 through AUTH-006)
- Issue #3: All QR stories (QR-001 through QR-005)
- Issue #4: All CUSTODY stories (CUSTODY-001 through CUSTODY-015)
- Issue #5: All MAINT stories (MAINT-001 through MAINT-004)
- Issue #6: All AUDIT stories (AUDIT-001 through AUDIT-006)

## How to Apply These Updates

### Option 1: Manual Update (Recommended for verification)
1. Open each GitHub issue in the web browser
2. Click "Edit" on the issue description
3. Copy the content from the corresponding `.md` file in the `issues/` directory
4. Paste into the GitHub issue editor
5. Save the issue

### Option 2: Using GitHub CLI (Requires authentication)
```bash
# Update a single issue
gh issue edit <issue_number> --repo J2WFFDev/custody-manager --body-file issues/<issue_number>.md

# Or use a script to update all issues
for i in issues/*.md; do
  num=$(basename $i .md)
  echo "Updating issue #$num..."
  gh issue edit $num --repo J2WFFDev/custody-manager --body-file issues/$num.md
done
```

### Option 3: Using GitHub API
Use the GitHub REST API with proper authentication to update each issue programmatically.

## Verification

All generated files follow the same format as issue #7 (the template):
1. Opening description paragraph
2. Empty line
3. ### Related User Stories section with bullet points
4. Empty line  
5. Remaining original content

## Files Generated

Total: 34 issue markdown files
- issues/1.md through issues/6.md (Epic issues)
- issues/8.md through issues/35.md (Implementation issues)
- Issue #7 was not regenerated as it already contains user stories

## Next Steps

1. Review a sample of the generated files to ensure quality
2. Choose an update method (manual, CLI, or API)
3. Apply updates to GitHub issues
4. Verify updates were successful
5. Close this task
