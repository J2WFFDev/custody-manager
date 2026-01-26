# GitHub Issues Update Summary

## Task Completed

Generated updated descriptions for all 34 GitHub issues (excluding issue #7 which was already updated) to include "Related User Stories" sections.

## What Was Generated

### 1. Issue Markdown Files (`issues/` directory)
- **34 files total** (issues 1-6, 8-35)
- Each file contains the complete updated issue body
- Format matches the template from issue #7
- Each issue now has a "### Related User Stories" section

### 2. Scripts
- **`process_issues.py`** - Core Python module with logic to:
  - Parse USER_STORIES.md
  - Extract user story text by ID
  - Insert Related User Stories section into issue bodies
  - Preserve all existing content

- **`generate_all_issues.py`** - Script that processes all 34 issues and generates the markdown files

- **`update_github_issues.sh`** - Bash script to apply all updates to GitHub using GitHub CLI

- **`github_issues_data.json`** - Cached issue data from GitHub API

### 3. Documentation
- **`ISSUE_UPDATE_README.md`** - Detailed documentation of the update process
- **`THIS FILE`** - Summary and next steps

## Format Example

Each updated issue follows this format (using issue #8 as an example):

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

## Issue Mappings Summary

| Epic | Issue Numbers | User Story Prefix |
|------|--------------|-------------------|
| Epic #1: Project Setup | 12-16 | DEV |
| Epic #2: Authentication | 8-11 | AUTH |
| Epic #3: QR Operations | 33-35 | QR |
| Epic #4: Custody Management | 26-32 | CUSTODY |
| Epic #5: Maintenance | 22-25 | MAINT |
| Epic #6: Audit/Data | 17-21 | AUDIT |
| Epic Issues | 1-6 | All stories from each epic |

## How to Apply Updates to GitHub

### Option 1: Automated Update (Recommended)

Use the provided bash script with GitHub CLI:

```bash
# Ensure GitHub CLI is installed and authenticated
gh auth login

# Run the update script
./update_github_issues.sh
```

The script will:
- Verify GitHub CLI is installed and authenticated
- Ask for confirmation before proceeding
- Update all 34 issues
- Show progress and report success/failures

### Option 2: Manual Update

For each issue:
1. Open the issue on GitHub (e.g., https://github.com/J2WFFDev/custody-manager/issues/8)
2. Click "Edit" on the issue description
3. Open the corresponding file from `issues/` directory (e.g., `issues/8.md`)
4. Copy the entire content
5. Paste into the GitHub issue editor
6. Click "Update comment"

### Option 3: GitHub API

Use the GitHub API directly with authentication. Example using `curl`:

```bash
ISSUE_NUM=8
BODY=$(cat issues/${ISSUE_NUM}.md | jq -Rs .)

curl -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/J2WFFDev/custody-manager/issues/${ISSUE_NUM} \
  -d "{\"body\": $BODY}"
```

## Verification

### Quality Checks Performed
✅ All 34 issue files generated successfully
✅ Format matches template (issue #7)
✅ All user story IDs reference valid stories in USER_STORIES.md
✅ Original issue content preserved (no data loss)
✅ Proper spacing and formatting maintained

### Sample Issues Verified
- Issue #1 (Epic with multi-line paragraph)
- Issue #8 (Standard implementation issue)
- Issue #27 (Issue with multiple story references)
- Issue #33 (QR operations)

## Next Steps

1. **Review** - Spot-check a few generated files to ensure quality
2. **Choose Update Method** - Select automated script, manual, or API approach
3. **Apply Updates** - Update all 34 GitHub issues
4. **Verify** - Check a few updated issues on GitHub to confirm success
5. **Complete** - Mark task as complete

## Files in This Submission

```
.
├── .gitignore                     # Ignore Python cache files
├── ISSUE_UPDATE_README.md         # Detailed documentation
├── SUMMARY.md                     # This file
├── USER_STORIES.md                # Source user stories (unchanged)
├── generate_all_issues.py         # Issue generation script
├── github_issues_data.json        # Cached GitHub issue data
├── process_issues.py              # Core processing logic
├── update_github_issues.sh        # Bash script to apply updates
└── issues/                        # Generated issue markdown files
    ├── 1.md
    ├── 2.md
    ├── 3.md
    ├── 4.md
    ├── 5.md
    ├── 6.md
    ├── 8.md
    ├── 9.md
    ... (total 34 files)
    └── 35.md
```

## Success Criteria Met

✅ All 34 remaining issues have updated descriptions generated
✅ Format matches issue #7
✅ All user story IDs reference existing stories in USER_STORIES.md
✅ Existing issue content is preserved
✅ Scripts provided to apply updates easily
✅ Documentation complete

---

**Status**: Ready for application to GitHub issues
**Generated**: 2026-01-26
**Repository**: J2WFFDev/custody-manager
