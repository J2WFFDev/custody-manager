#!/usr/bin/env python3
"""
Final working script to generate all updated issue markdown files.
Reads from github_issues_data.json and generates updated files in issues/ directory.
"""

import json
from pathlib import Path
from process_issues import main as process_issues

def main():
    """Load issue data and process all issues."""
    # Load issues from JSON file
    with open('github_issues_data.json', 'r') as f:
        issues_list = json.load(f)
    
    # Convert to dict by issue number
    issues_dict = {issue['number']: issue for issue in issues_list}
    
    # Process all issues
    updated = process_issues(issues_dict)
    
    print(f"\n✓ Successfully generated {len(updated)} issue files!")
    print(f"\nFiles are in the issues/ directory and ready to be used")
    print(f"to update GitHub issues (manually or via API).")

if __name__ == "__main__":
    main()
