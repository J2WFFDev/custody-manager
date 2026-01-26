# GitHub Issues Update - Execution Guide

## Current Status: Ready for Execution

All preparation work has been completed. The issue updates are ready to be applied to GitHub but require proper authentication credentials.

## What's Been Prepared

✅ **34 Markdown Files Ready** - All issue descriptions updated with user stories in `issues/` directory  
✅ **Python API Script** - `update_issues_api.py` tested and validated  
✅ **Shell Script** - `update_github_issues.sh` ready for use  
✅ **GitHub Actions Workflow** - `.github/workflows/update-issues.yml` configured  
✅ **Documentation** - Complete instructions in `UPDATE_INSTRUCTIONS.md`  
✅ **Dry Run Validation** - All 34 issues validated successfully  

## Why Issues Haven't Been Updated Yet

The automation is complete, but **execution requires GitHub authentication** which is not available in the current environment. The scripts are ready to run when proper credentials are provided.

## How to Execute the Updates

### Option 1: Using GitHub CLI (Fastest)

**For repository maintainers with write access:**

```bash
# 1. Authenticate with GitHub
gh auth login

# 2. Run the update script
./update_github_issues.sh

# 3. Confirm when prompted
# Type 'y' to proceed

# 4. Review results
cat ISSUE_UPDATE_SUMMARY.md
```

**Estimated time:** 2-3 minutes for all 34 issues

### Option 2: Using Python Script

**For users who prefer Python or don't have gh CLI:**

```bash
# 1. Install dependencies
pip install requests

# 2. Create GitHub Personal Access Token
# Go to: https://github.com/settings/tokens
# Scope needed: repo

# 3. Set environment variable
export GITHUB_TOKEN="your_token_here"

# 4. Run the script
python3 update_issues_api.py

# 5. Confirm when prompted
# Type 'y' to proceed

# 6. Review results
cat ISSUE_UPDATE_SUMMARY.md
```

**Estimated time:** 2-3 minutes for all 34 issues

### Option 3: Using GitHub Actions

**For maintainers who want to run via GitHub Actions:**

1. Go to the repository's **Actions** tab
2. Select **"Update GitHub Issues with User Stories"** workflow
3. Click **"Run workflow"**
4. Enter **"update"** in the confirmation field
5. Click **"Run workflow"** button
6. Wait for completion (1-2 minutes)
7. Download the **summary artifact**

### Option 4: Manual Updates

**If automated methods are not available:**

For each issue (1-6, 8-35):
1. Open the issue in GitHub web interface
2. Click "Edit" on the description
3. Open `issues/{number}.md` in this repository
4. Copy the entire content
5. Paste into the GitHub issue editor
6. Click "Update comment"

**Estimated time:** 30-45 minutes for all 34 issues

## Pre-Execution Checklist

Before running any update method, ensure:

- [ ] You have write access to the J2WFFDev/custody-manager repository
- [ ] You are on the correct branch containing the markdown files
- [ ] You have reviewed at least one sample markdown file (e.g., `issues/8.md`)
- [ ] You understand that this will modify 34 issue descriptions
- [ ] You have a backup plan (Git history allows reverting changes)

## What Will Happen

When you execute the updates:

1. **Script reads** 34 markdown files from `issues/` directory
2. **For each issue**, the script will:
   - Extract the issue number from filename
   - Read the complete markdown content
   - Call GitHub API to update the issue body
   - Log the result (success/failure)
3. **Summary report** is generated or updated
4. **No other changes** are made (titles, labels, etc. remain unchanged)

## Expected Outcome

After successful execution:

- ✅ All 34 issues will have "Related User Stories" sections
- ✅ Original issue content preserved
- ✅ Issue #7 remains untouched (already has user stories)
- ✅ Summary report shows 34 successful updates
- ✅ You can visit any issue to see the new user stories section

Example: https://github.com/J2WFFDev/custody-manager/issues/8

## Rollback Plan

If you need to revert the changes:

1. **Review Git history** to find the commit before updates
2. **For each issue**, restore the original body from GitHub's edit history
3. **Or** keep a backup of current issue states before running updates

Note: GitHub preserves edit history for issues, so original content is never lost.

## Troubleshooting

### "Not authenticated" error
- Run `gh auth login` (for CLI method)
- Or verify `GITHUB_TOKEN` is set (for Python method)

### "Permission denied" error
- Verify you have write access to the repository
- Check that your token has `repo` scope

### "File not found" error
- Ensure you're in the repository root directory
- Verify `issues/` directory exists with 34 .md files

### Rate limiting
- Wait 1 hour for rate limit to reset
- Authenticated requests have much higher limits

## Security Notes

- ✅ Scripts only modify issue bodies, nothing else
- ✅ No destructive operations performed
- ✅ All changes are logged
- ✅ Tokens should never be committed to repository
- ✅ Use environment variables for credentials

## Next Steps

1. **Choose an execution method** from the options above
2. **Prepare authentication** (token or gh login)
3. **Run the update script**
4. **Verify the results** by checking a few issues
5. **Review the summary report**
6. **Close this task** and mark PR as complete

## Questions or Issues?

If you encounter problems during execution:
- Check `UPDATE_INSTRUCTIONS.md` for detailed guidance
- Review error messages carefully
- Ensure all prerequisites are met
- Try the dry-run mode first: `python3 update_issues_api.py --dry-run`

---

**Prepared by:** GitHub Copilot Agent  
**Date:** 2026-01-26  
**Status:** Ready for Execution  
**Approval Required:** Yes (repository write access)  
