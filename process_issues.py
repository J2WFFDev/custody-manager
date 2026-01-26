#!/usr/bin/env python3
"""
Complete working script to generate updated issue markdown files.
This script:
1. Reads USER_STORIES.md
2. Uses embedded GitHub issue data
3. Generates updated markdown files for each issue
4. Creates a summary report
"""

import re
from typing import Dict, List, Optional
from pathlib import Path

# Mapping of issues to user story IDs
ISSUE_MAPPINGS = {
    12: ["DEV-001"], 13: ["DEV-002"], 14: ["DEV-002"], 15: ["DEV-003"], 16: ["DEV-003"],
    8: ["AUTH-003", "AUTH-004", "AUTH-005"], 9: ["AUTH-001", "AUTH-002"],
    10: ["AUTH-006"], 11: ["AUTH-001", "AUTH-002"],
    33: ["QR-001"], 34: ["QR-001"], 35: ["QR-002", "QR-003", "QR-005"],
    26: ["CUSTODY-015"], 27: ["CUSTODY-001", "QR-002"],
    28: ["CUSTODY-002", "CUSTODY-003", "CUSTODY-011"], 29: ["CUSTODY-012"],
    30: ["CUSTODY-005"], 31: ["CUSTODY-007"], 32: ["CUSTODY-008", "CUSTODY-014"],
    22: ["MAINT-001"], 23: ["MAINT-001"], 24: ["MAINT-002"], 25: ["MAINT-003", "MAINT-004"],
    17: ["AUDIT-005", "AUDIT-006"], 18: ["AUDIT-001"], 19: ["AUDIT-002", "AUDIT-006"],
    20: ["AUDIT-004"], 21: ["AUDIT-003"],
    1: ["DEV-001", "DEV-002", "DEV-003", "DEV-004"],
    2: ["AUTH-001", "AUTH-002", "AUTH-003", "AUTH-004", "AUTH-005", "AUTH-006"],
    3: ["QR-001", "QR-002", "QR-003", "QR-004", "QR-005"],
    4: ["CUSTODY-001", "CUSTODY-002", "CUSTODY-003", "CUSTODY-004", "CUSTODY-005",
        "CUSTODY-006", "CUSTODY-007", "CUSTODY-008", "CUSTODY-009", "CUSTODY-010",
        "CUSTODY-011", "CUSTODY-012", "CUSTODY-013", "CUSTODY-014", "CUSTODY-015"],
    5: ["MAINT-001", "MAINT-002", "MAINT-003", "MAINT-004"],
    6: ["AUDIT-001", "AUDIT-002", "AUDIT-003", "AUDIT-004", "AUDIT-005", "AUDIT-006"],
}

# This will be populated with actual GitHub issue data
github_issues = {}


def parse_user_stories(filename: str = 'USER_STORIES.md') -> Dict[str, str]:
    """Parse USER_STORIES.md and extract all user stories."""
    stories = {}
    with open(filename, 'r') as f:
        content = f.read()
    
    pattern = r'- \*\*([A-Z]+-\d+)\*\*:\s*(.+?)(?=\n(?:- \*\*[A-Z]+-\d+\*\*:|$))'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for story_id, story_text in matches:
        stories[story_id] = story_text.strip()
    
    return stories


def generate_user_stories_section(story_ids: List[str], stories_dict: Dict[str, str]) -> str:
    """Generate the 'Related User Stories' section."""
    lines = ["### Related User Stories"]
    for story_id in story_ids:
        if story_id in stories_dict:
            lines.append(f"- **{story_id}**: {stories_dict[story_id]}")
        else:
            lines.append(f"- **{story_id}**: [Story not found]")
    lines.append("")
    return "\n".join(lines)


def update_issue_body(issue_number: int, current_body: str, story_ids: List[str],
                     stories_dict: Dict[str, str]) -> Optional[str]:
    """Add Related User Stories section to issue body."""
    if "### Related User Stories" in current_body:
        return None
    
    stories_section = generate_user_stories_section(story_ids, stories_dict)
    lines = current_body.split('\n')
    
    # Find insertion point: after the opening paragraph(s), before first heading or bullet list
    # Look for the first heading (###) or bullet list (-), that's where we insert before
    insert_index = None
    in_first_para = True
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Skip empty lines at the start
        if i == 0 or (in_first_para and not stripped):
            continue
        
        # Found first heading or bullet list - insert before it
        if stripped.startswith('###') or stripped.startswith('-'):
            insert_index = i
            break
        
        # If we found content, we're past the first para
        if stripped:
            in_first_para = False
    
    # If no heading/bullets found, insert at the end
    if insert_index is None:
        insert_index = len(lines)
    
    # Insert the stories section with proper spacing
    # Ensure there's an empty line before the stories section
    if insert_index > 0 and lines[insert_index - 1].strip():
        updated_lines = lines[:insert_index] + [''] + stories_section.split('\n') + lines[insert_index:]
    else:
        updated_lines = lines[:insert_index] + stories_section.split('\n') + lines[insert_index:]
    
    return '\n'.join(updated_lines)


def process_all_issues(issues_data: Dict[int, Dict]):
    """Process all issues and generate updated markdown files."""
    print("=" * 80)
    print("GitHub Issues User Story Updater")
    print("=" * 80)
    
    stories = parse_user_stories()
    print(f"\n✓ Loaded {len(stories)} user stories from USER_STORIES.md")
    
    issues_dir = Path('issues')
    issues_dir.mkdir(exist_ok=True)
    
    updated = []
    skipped = []
    
    for issue_num in sorted(ISSUE_MAPPINGS.keys()):
        if issue_num not in issues_data:
            print(f"⚠ Issue #{issue_num} not found in data")
            continue
        
        issue = issues_data[issue_num]
        body = issue.get('body', '') or ''
        updated_body = update_issue_body(issue_num, body, ISSUE_MAPPINGS[issue_num], stories)
        
        if updated_body is None:
            skipped.append(issue_num)
            continue
        
        # Save to file
        with open(issues_dir / f'{issue_num}.md', 'w') as f:
            f.write(updated_body)
        
        updated.append(issue_num)
        title = issue.get('title', 'Unknown')[:60]
        print(f"  ✓ Issue #{issue_num}: {title}")
    
    # Generate summary
    print("\n" + "=" * 80)
    print("Summary:")
    print("=" * 80)
    print(f"✓ Generated {len(updated)} updated issue files in issues/ directory")
    if skipped:
        print(f"⚠ Skipped {len(skipped)} issues (already have user stories): {skipped}")
    print("\nGenerated files can be used to update GitHub issues.")
    print("=" * 80)
    
    return updated


# Main execution - to be called with issue data
def main(issues_data):
    """Main entry point."""
    return process_all_issues(issues_data)


if __name__ == "__main__":
    print("This script needs to be called with GitHub issues data.")
    print("Use the wrapper script that fetches issues from GitHub.")
