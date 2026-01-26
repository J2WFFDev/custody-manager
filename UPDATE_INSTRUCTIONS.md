# How to Update GitHub Issues with User Stories

This guide explains how to apply the issue updates from PR #36 to all GitHub issues.

## Overview

This repository contains:
- **34 markdown files** in the `issues/` directory with updated issue descriptions
- **Automated scripts** to apply these updates to GitHub
- **Multiple update methods** to choose from based on your preference

## Quick Start

### Method 1: Using the Automated Python Script (Recommended)

**Prerequisites:**
- Python 3.7 or later
- `requests` library (`pip install requests`)
- GitHub Personal Access Token with `repo` scope

**Steps:**

1. **Create a GitHub Personal Access Token:**
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scope: `repo` (Full control of private repositories)
   - Generate and copy the token

2. **Set the token as an environment variable:**
   ```bash
   export GITHUB_TOKEN="your_token_here"
   ```

3. **Run the update script:**
   ```bash
   python3 update_issues_api.py
   ```

4. **Review the generated summary:**
   - Check `ISSUE_UPDATE_SUMMARY.md` for results

**Dry Run Option:**
```bash
python3 update_issues_api.py --dry-run
```

### Method 2: Using the GitHub CLI Script

**Prerequisites:**
- GitHub CLI (`gh`) installed
- Authenticated with `gh auth login`

**Steps:**

1. **Authenticate with GitHub CLI:**
   ```bash
   gh auth login
   ```

2. **Run the shell script:**
   ```bash
   ./update_github_issues.sh
   ```

3. **Confirm when prompted:**
   - The script will show how many issues will be updated
   - Type `y` to proceed

### Method 3: Using GitHub Actions Workflow

**Prerequisites:**
- Write access to the repository
- Ability to trigger workflows

**Steps:**

1. **Go to the Actions tab** in the GitHub repository

2. **Select the "Update GitHub Issues with User Stories" workflow**

3. **Click "Run workflow"**

4. **Enter "update" in the confirmation field** and run

5. **Download the summary artifact** after completion

## What Gets Updated

### Issues Included (34 total):
- Issues #1-6 (Epic issues)
- Issues #8-35 (Implementation tasks)

### Issue #7:
**Skipped** - Already manually updated with user stories

### Content Changes:
- **Updated:** Issue body/description with "Related User Stories" section
- **Preserved:** Title, labels, assignees, milestone, state, and all other metadata
- **Format:** Each issue gets a new section inserted after the opening description

### Example Update:

**Before:**
```markdown
Add Microsoft OAuth login flow to FastAPI backend.

- Use Authlib or python-social-auth
- Store user info after login
- Issue JWT for session management
```

**After:**
```markdown
Add Microsoft OAuth login flow to FastAPI backend.

### Related User Stories
- **AUTH-003**: As an Armorer, I want to log in with my Google or Microsoft account...
- **AUTH-004**: As a Coach, I want to log in with my Google or Microsoft account...
- **AUTH-005**: As a Parent, I want to log in securely with my Google or Microsoft account...

- Use Authlib or python-social-auth
- Store user info after login
- Issue JWT for session management
```

## Files in This Repository

| File | Purpose |
|------|---------|
| `update_issues_api.py` | Python script using GitHub REST API |
| `update_github_issues.sh` | Shell script using GitHub CLI |
| `.github/workflows/update-issues.yml` | GitHub Actions workflow |
| `issues/*.md` | 34 markdown files with updated issue descriptions |
| `ISSUE_UPDATE_SUMMARY.md` | Summary report (generated after running) |
| `ISSUE_UPDATE_README.md` | Documentation about the updates |
| `process_issues.py` | Original processing logic |
| `github_issues_data.json` | Cached GitHub issue data |

## Verification

After running any update method, verify the changes:

1. **Visit a sample issue:**
   - https://github.com/J2WFFDev/custody-manager/issues/8

2. **Check for the "Related User Stories" section:**
   - Should appear after the opening description
   - Should include bullet points with user story IDs and text

3. **Verify metadata unchanged:**
   - Title should be the same
   - Labels should be the same
   - Assignees should be the same

## Troubleshooting

### Authentication Errors

**Problem:** "Error: GitHub token not provided"

**Solution:** 
- Ensure `GITHUB_TOKEN` environment variable is set
- Or use `--token` argument with the Python script

### Permission Errors

**Problem:** "HTTP 403: Forbidden" or "HTTP 401: Unauthorized"

**Solution:**
- Verify your token has `repo` scope
- Ensure you have write access to the repository

### Rate Limiting

**Problem:** "API rate limit exceeded"

**Solution:**
- Wait for the rate limit to reset (usually 1 hour)
- Authenticated requests have higher limits than anonymous

### File Not Found Errors

**Problem:** "Issue file not found: issues/X.md"

**Solution:**
- Ensure you're in the correct branch: `copilot/update-github-issues-user-stories`
- Verify the `issues/` directory exists and contains the markdown files

## Advanced Usage

### Update a Single Issue

Using Python script:
```python
# Edit update_issues_api.py to process only specific issue numbers
# Or use the GitHub CLI directly:
gh issue edit 8 --repo J2WFFDev/custody-manager --body-file issues/8.md
```

### Custom Token Location

```bash
python3 update_issues_api.py --token "$(cat ~/.github_token)"
```

### Integration with CI/CD

The GitHub Actions workflow is configured to:
- Run on manual trigger only (workflow_dispatch)
- Require confirmation input
- Use the repository's `GITHUB_TOKEN` secret
- Generate and upload summary artifact

## Safety Features

All update methods include:
- ✓ Confirmation prompts before making changes
- ✓ Dry-run mode available
- ✓ Detailed logging of each operation
- ✓ Summary report generation
- ✓ Error handling and reporting

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the generated `ISSUE_UPDATE_SUMMARY.md`
3. Verify all prerequisites are met
4. Check the error messages for specific guidance

## Manual Update Option

If automated methods fail, you can manually update each issue:

1. Open the issue in GitHub
2. Click "Edit" on the description
3. Open the corresponding markdown file from `issues/`
4. Copy the entire content
5. Paste into the GitHub issue editor
6. Click "Update comment"

Repeat for all 34 issues.

---

**Last Updated:** 2026-01-26

**Version:** 1.0.0
