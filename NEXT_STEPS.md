# Important Note: GitHub Issue Updates

## Current Status

✅ **All preparatory work completed**:
- 34 updated issue markdown files generated in `issues/` directory
- Update script created (`update_github_issues.sh`)
- Complete documentation provided

⚠️ **Manual step required**: The actual update of GitHub issues requires authentication that is not available in this automated environment.

## Why Issues Cannot Be Auto-Updated

This automated agent environment has these limitations:
- Cannot update GitHub issue descriptions directly via API
- No GitHub authentication token available for write operations
- GitHub MCP tools available are read-only

This is by design for security reasons - automated agents should not have write access to GitHub issues without explicit user authorization.

## How to Complete the Update

Choose one of these methods to apply the generated updates:

### Method 1: Automated via GitHub CLI (Recommended)

1. Ensure you have GitHub CLI installed: https://cli.github.com/
2. Authenticate if needed: `gh auth login`
3. Run the provided script:
   ```bash
   ./update_github_issues.sh
   ```
4. The script will update all 34 issues automatically

### Method 2: Manual Update via GitHub Web UI

For each issue (#1-6, #8-35):
1. Open the issue on GitHub
2. Click "Edit" on the issue description
3. Open the corresponding file from `issues/` directory
4. Copy the entire content and paste it into the GitHub editor
5. Click "Update comment"

### Method 3: GitHub API with Personal Access Token

Use the GitHub API directly:
```bash
# Set your GitHub token
export GITHUB_TOKEN="your_personal_access_token"

# Update a single issue
issue_num=8
body=$(cat issues/${issue_num}.md | jq -Rs .)
curl -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/J2WFFDev/custody-manager/issues/${issue_num} \
  -d "{\"body\": $body}"
```

### Method 4: GitHub Actions Workflow

Create a GitHub Actions workflow that:
1. Runs on manual trigger
2. Uses `GITHUB_TOKEN` from secrets
3. Updates all issues using the generated markdown files

Example workflow snippet:
```yaml
- name: Update issues
  env:
    GH_TOKEN: ${{ github.token }}
  run: |
    for file in issues/*.md; do
      issue_num=$(basename $file .md)
      gh issue edit $issue_num --body-file $file
    done
```

## What's Been Completed

✅ All 34 issue descriptions generated with user story references
✅ Format verified to match issue #7
✅ All user story IDs validated against USER_STORIES.md
✅ Original content preserved in all issues
✅ Update automation script provided
✅ Comprehensive documentation created

## Next Action Required

**Someone with write access to the repository needs to:**
1. Review the generated files in `issues/` directory
2. Choose an update method from above
3. Apply the updates to all 34 GitHub issues
4. Verify a few issues to confirm successful update

## Files Available for Review

All generated files are in this branch: `copilot/update-github-issues-user-stories`

- `issues/*.md` - 34 updated issue descriptions
- `update_github_issues.sh` - Automation script
- `SUMMARY.md` - Complete summary
- `ISSUE_UPDATE_README.md` - Detailed documentation

---

**Status**: Ready for application (manual step required)
**Next Step**: Apply updates using one of the methods above
