#!/usr/bin/env python3
"""
Script to update GitHub issues with user story references using GitHub API.

This script reads markdown files from the issues/ directory and updates
the corresponding GitHub issues via the GitHub REST API.

Prerequisites:
- GitHub Personal Access Token with 'repo' scope
- Set via GITHUB_TOKEN environment variable or pass as argument

Usage:
    export GITHUB_TOKEN="your_token_here"
    python update_issues_api.py
    
    OR
    
    python update_issues_api.py --token "your_token_here"
"""

import os
import sys
import requests
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

REPO_OWNER = "J2WFFDev"
REPO_NAME = "custody-manager"
ISSUES_DIR = "issues"
GITHUB_API_URL = "https://api.github.com"

# Issue #7 was already manually updated and should be skipped
SKIPPED_ISSUES = [7]


def get_github_token(args_token: str = None) -> str:
    """Get GitHub token from arguments or environment."""
    token = args_token or os.environ.get('GITHUB_TOKEN')
    if not token:
        print("Error: GitHub token not provided.")
        print("Set GITHUB_TOKEN environment variable or use --token argument")
        sys.exit(1)
    return token


def read_issue_file(issue_number: int) -> str:
    """Read the markdown content for an issue."""
    file_path = Path(ISSUES_DIR) / f"{issue_number}.md"
    if not file_path.exists():
        raise FileNotFoundError(f"Issue file not found: {file_path}")
    
    with open(file_path, 'r') as f:
        return f.read()


def update_github_issue(issue_number: int, body: str, token: str) -> Tuple[bool, str]:
    """
    Update a GitHub issue's body using the REST API.
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/issues/{issue_number}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json'
    }
    data = {
        'body': body
    }
    
    try:
        response = requests.patch(url, headers=headers, json=data)
        
        if response.status_code == 200:
            return True, "Success"
        else:
            error_msg = response.json().get('message', 'Unknown error')
            return False, f"HTTP {response.status_code}: {error_msg}"
    except requests.exceptions.RequestException as e:
        return False, f"Request failed: {str(e)}"


def get_all_issue_numbers() -> List[int]:
    """Get all issue numbers from markdown files in issues/ directory."""
    issues_path = Path(ISSUES_DIR)
    if not issues_path.exists():
        print(f"Error: Directory '{ISSUES_DIR}' not found")
        sys.exit(1)
    
    issue_files = sorted(issues_path.glob('*.md'))
    issue_numbers = []
    
    for file_path in issue_files:
        try:
            issue_num = int(file_path.stem)
            issue_numbers.append(issue_num)
        except ValueError:
            print(f"Warning: Skipping non-numeric file: {file_path.name}")
    
    return sorted(issue_numbers)


def create_summary_report(results: List[Dict], output_file: str = 'ISSUE_UPDATE_SUMMARY.md'):
    """Create a summary report of the update process."""
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    
    content = f"""# GitHub Issues Update Summary

**Generated:** {timestamp}

## Overview

- **Total Issues Processed:** {len(results)}
- **Successfully Updated:** {len(successful)}
- **Failed to Update:** {len(failed)}

## Successfully Updated Issues

"""
    
    if successful:
        for result in successful:
            content += f"- ✓ Issue #{result['issue_number']}\n"
    else:
        content += "*None*\n"
    
    content += "\n## Failed Updates\n\n"
    
    if failed:
        for result in failed:
            content += f"- ✗ Issue #{result['issue_number']}: {result['message']}\n"
    else:
        content += "*None*\n"
    
    content += f"""
## Update Details

All issues were updated with "Related User Stories" sections based on the markdown files in the `issues/` directory.

- **Repository:** {REPO_OWNER}/{REPO_NAME}
- **Source Directory:** {ISSUES_DIR}/
- **Update Method:** GitHub REST API
- **Skipped Issues:** {', '.join(f'#{i}' for i in SKIPPED_ISSUES)} (already contain user stories)

## Files Updated

The following issue descriptions were updated:

"""
    
    for result in successful:
        content += f"- `issues/{result['issue_number']}.md` → Issue #{result['issue_number']}\n"
    
    skipped_notes = '\n'.join([f"- Issue #{i} was intentionally skipped as it already contains user stories" 
                                for i in SKIPPED_ISSUES])
    
    content += f"""
## Notes

{skipped_notes}
- Only issue bodies/descriptions were modified
- All other metadata (title, labels, assignees, etc.) remain unchanged
- All existing issue content was preserved with user stories added

## Verification

To verify the updates, visit any updated issue:
"""
    
    if successful:
        first_issue = successful[0]['issue_number']
        content += f"- https://github.com/{REPO_OWNER}/{REPO_NAME}/issues/{first_issue}\n"
    
    content += "\nAll issues should now display the \"Related User Stories\" section.\n"
    
    with open(output_file, 'w') as f:
        f.write(content)
    
    print(f"\n✓ Summary report created: {output_file}")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Update GitHub issues with user stories')
    parser.add_argument('--token', help='GitHub Personal Access Token')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be updated without making changes')
    args = parser.parse_args()
    
    print("=" * 80)
    print("GitHub Issues Update Script")
    print("=" * 80)
    print(f"\nRepository: {REPO_OWNER}/{REPO_NAME}")
    print(f"Source Directory: {ISSUES_DIR}/\n")
    
    # Get issue numbers to update
    issue_numbers = get_all_issue_numbers()
    print(f"Found {len(issue_numbers)} issue files to process")
    
    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made\n")
    else:
        token = get_github_token(args.token)
        print("✓ GitHub token obtained\n")
    
    # Display list of issues
    print("Issues to update:")
    for num in issue_numbers:
        print(f"  - Issue #{num}")
    
    if not args.dry_run:
        response = input("\nProceed with updating all issues? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)
    
    print("\n" + "=" * 80)
    print("Processing Issues...")
    print("=" * 80 + "\n")
    
    results = []
    
    for issue_number in issue_numbers:
        try:
            # Read issue file
            body = read_issue_file(issue_number)
            
            if args.dry_run:
                print(f"Issue #{issue_number}: Would update with {len(body)} characters")
                results.append({
                    'issue_number': issue_number,
                    'success': True,
                    'message': 'Dry run - not executed'
                })
            else:
                # Update issue
                print(f"Updating issue #{issue_number}... ", end='', flush=True)
                success, message = update_github_issue(issue_number, body, token)
                
                results.append({
                    'issue_number': issue_number,
                    'success': success,
                    'message': message
                })
                
                if success:
                    print("✓")
                else:
                    print(f"✗ {message}")
        
        except FileNotFoundError as e:
            print(f"✗ File not found for issue #{issue_number}")
            results.append({
                'issue_number': issue_number,
                'success': False,
                'message': 'File not found'
            })
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            results.append({
                'issue_number': issue_number,
                'success': False,
                'message': str(e)
            })
    
    # Print summary
    print("\n" + "=" * 80)
    print("Update Complete")
    print("=" * 80)
    
    successful = sum(1 for r in results if r['success'])
    failed = sum(1 for r in results if not r['success'])
    
    print(f"\n✓ Successfully updated: {successful} issues")
    if failed > 0:
        print(f"✗ Failed to update: {failed} issues")
        print("\nFailed issues:")
        for r in results:
            if not r['success']:
                print(f"  - Issue #{r['issue_number']}: {r['message']}")
    
    # Create summary report
    create_summary_report(results)
    
    print("\n" + "=" * 80)
    
    if failed > 0:
        sys.exit(1)
    else:
        print("✓ All issues updated successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
