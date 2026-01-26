#!/usr/bin/env python3
"""
Preview script to show before/after comparison of issue updates.

This script fetches current issue bodies from GitHub and shows
what will change when the updates are applied.

Usage:
    python3 preview_changes.py [issue_number]
    
    # Preview all issues
    python3 preview_changes.py
    
    # Preview specific issue
    python3 preview_changes.py 8
"""

import sys
import requests
from pathlib import Path
from typing import Optional

REPO_OWNER = "J2WFFDev"
REPO_NAME = "custody-manager"
ISSUES_DIR = "issues"
GITHUB_API_URL = "https://api.github.com"


def get_current_issue_body(issue_number: int) -> Optional[str]:
    """Fetch current issue body from GitHub (no auth required for public repos)."""
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/issues/{issue_number}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('body', '')
        elif response.status_code == 404:
            print(f"Error: Issue #{issue_number} not found")
            return None
        elif response.status_code == 403:
            print(f"Error: Access forbidden (rate limit or permissions)")
            return None
        elif response.status_code == 401:
            print(f"Error: Authentication required")
            return None
        else:
            print(f"Error: HTTP {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching issue #{issue_number}: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error fetching issue #{issue_number}: {str(e)}")
        return None


def get_new_issue_body(issue_number: int) -> Optional[str]:
    """Read new issue body from markdown file."""
    file_path = Path(ISSUES_DIR) / f"{issue_number}.md"
    if not file_path.exists():
        return None
    
    with open(file_path, 'r') as f:
        return f.read()


def show_diff(issue_number: int):
    """Show before/after comparison for an issue."""
    print(f"\n{'=' * 80}")
    print(f"Issue #{issue_number}")
    print('=' * 80)
    
    current = get_current_issue_body(issue_number)
    new = get_new_issue_body(issue_number)
    
    if current is None:
        print("❌ Could not fetch current issue body from GitHub")
        return False
    
    if new is None:
        print("❌ No markdown file found")
        return False
    
    # Check if user stories already exist
    if "### Related User Stories" in current:
        print("⚠️  This issue already has 'Related User Stories' section")
        print("\nCurrent content (first 500 chars):")
        print("-" * 80)
        print(current[:500] + ("..." if len(current) > 500 else ""))
        return False
    
    print("\n📋 CURRENT (GitHub):")
    print("-" * 80)
    print(current[:300] + ("..." if len(current) > 300 else ""))
    
    print("\n\n✨ NEW (Will be updated to):")
    print("-" * 80)
    print(new[:500] + ("..." if len(new) > 500 else ""))
    
    print("\n\n🔍 CHANGES:")
    print("-" * 80)
    
    # Find where user stories section will be inserted
    if "### Related User Stories" in new and "### Related User Stories" not in current:
        print("✓ Will ADD 'Related User Stories' section")
        
        # Extract just the user stories section
        start = new.find("### Related User Stories")
        end = new.find("\n\n", start + 25)
        if end == -1:
            end = new.find("\n-", start + 25)
        if end != -1:
            stories_section = new[start:end].strip()
            print("\n" + stories_section)
    
    print("\n✓ All other content will be preserved")
    
    return True


def main():
    """Main function."""
    if len(sys.argv) > 1:
        # Preview specific issue
        try:
            issue_number = int(sys.argv[1])
            show_diff(issue_number)
        except ValueError:
            print(f"Error: '{sys.argv[1]}' is not a valid issue number")
            sys.exit(1)
    else:
        # Preview all issues
        print("=" * 80)
        print("ISSUE UPDATES PREVIEW")
        print("=" * 80)
        print("\nThis shows what will change when updates are applied.\n")
        
        # Get all issue numbers from files
        issues_path = Path(ISSUES_DIR)
        issue_files = sorted(issues_path.glob('*.md'))
        issue_numbers = []
        
        for file_path in issue_files:
            try:
                issue_num = int(file_path.stem)
                issue_numbers.append(issue_num)
            except ValueError:
                pass
        
        print(f"Found {len(issue_numbers)} issues to preview\n")
        
        # Show first 3 as examples
        print("=" * 80)
        print("SHOWING FIRST 3 ISSUES (use 'python3 preview_changes.py <number>' for specific issue)")
        print("=" * 80)
        
        for issue_num in issue_numbers[:3]:
            show_diff(issue_num)
            print()
        
        if len(issue_numbers) > 3:
            print("\n" + "=" * 80)
            print(f"... and {len(issue_numbers) - 3} more issues ...")
            print("=" * 80)
            print("\nTo preview a specific issue:")
            print("  python3 preview_changes.py 8")
            print("\nTo preview all issues:")
            for num in issue_numbers:
                print(f"  python3 preview_changes.py {num}")


if __name__ == "__main__":
    main()
