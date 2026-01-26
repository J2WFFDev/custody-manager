#!/bin/bash
#
# Script to update all GitHub issues with user story references
# 
# Prerequisites:
# - GitHub CLI (gh) installed and authenticated
# - Run from the repository root directory
#
# Usage:
#   ./update_github_issues.sh
#

set -e

REPO="J2WFFDev/custody-manager"
ISSUES_DIR="issues"

echo "=========================================="
echo "GitHub Issues Update Script"
echo "=========================================="
echo ""
echo "This script will update all GitHub issues with user story references."
echo "Repository: $REPO"
echo "Source directory: $ISSUES_DIR/"
echo ""

# Check if gh is installed and authenticated
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed."
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "Error: Not authenticated with GitHub CLI."
    echo "Please run: gh auth login"
    exit 1
fi

echo "✓ GitHub CLI is installed and authenticated"
echo ""

# Count files to update
file_count=$(ls $ISSUES_DIR/*.md 2>/dev/null | wc -l)
if [ $file_count -eq 0 ]; then
    echo "Error: No markdown files found in $ISSUES_DIR/"
    exit 1
fi

echo "Found $file_count issue files to update"
echo ""
read -p "Do you want to proceed with updating all issues? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Updating issues..."
echo ""

# Track success/failures
success_count=0
fail_count=0
failed_issues=""

# Update each issue
for issue_file in $ISSUES_DIR/*.md; do
    issue_number=$(basename "$issue_file" .md)
    
    echo -n "Updating issue #$issue_number... "
    
    if gh issue edit "$issue_number" --repo "$REPO" --body-file "$issue_file" 2>/dev/null; then
        echo "✓"
        ((success_count++))
    else
        echo "✗ FAILED"
        ((fail_count++))
        failed_issues="$failed_issues $issue_number"
    fi
done

echo ""
echo "=========================================="
echo "Update Complete"
echo "=========================================="
echo "Successfully updated: $success_count issues"
echo "Failed to update: $fail_count issues"

if [ $fail_count -gt 0 ]; then
    echo "Failed issues:$failed_issues"
    exit 1
fi

echo ""
echo "✓ All issues updated successfully!"
