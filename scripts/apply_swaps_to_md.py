#!/usr/bin/env python3
"""
Apply option swaps from HTML to markdown files.

This script parses the git diff to find all option swaps made in the HTML files
and applies the same swaps to the corresponding markdown files.
"""

import re
import subprocess
import os


def get_git_diff():
    """Get the full diff between HEAD~1 and HEAD for all session HTML files."""
    result = subprocess.run(
        ['git', 'diff', 'HEAD~1', '--', 
         's1-cryptography/session1-cryptography.html',
         's2-networking/session2-networking.html',
         's3-red-teaming/session3-red-teaming.html',
         's4-forensics/session4-forensics.html',
         's5-misc-ctf/session5-misc-ctf.html'],
        capture_output=True, text=True, cwd='/Users/jasperfrumau/code/cyber-security-practice'
    )
    return result.stdout


def parse_option_swaps(diff_text):
    """Parse git diff to find all option text swaps."""
    # Pattern: -          <div ...>TEXT</div>\n+          <div ...>DIFFERENT_TEXT</div>
    # We need to find pairs where the same data-val has different text
    
    swaps = {}  # {(session, qid): [(old_letter, old_text, new_text), ...]}
    
    # Split by file
    current_file = None
    for line in diff_text.split('\n'):
        if line.startswith('diff --git'):
            # Extract filename
            match = re.search(r'diff --git a/(s\d-[^/]+/session\d+-[^.]+\.html)', line)
            if match:
                current_file = match.group(1)
                session = current_file.replace('/', '-').replace('.html', '')
        
        if current_file and line.startswith('-') and 'mcq-opt' in line:
            # This is a removed option line
            # Extract: data-val="X" ... >TEXT</div>
            old_match = re.search(r'data-val="([abcd])"[^>]*>(.*?)<div class="opt-indicator"></div><div>([^<]+)</div>', line)
            if old_match:
                old_letter = old_match.group(1)
                old_text = old_match.group(3).strip()
                # Look ahead for the corresponding + line
                # This is tricky with line-by-line parsing
                pass
    
    # Better approach: find all minus and plus blocks for mcq-opt
    # Group diff into hunks
    hunks = diff_text.split('@@')[1:]  # Skip first empty
    
    for hunk in hunks:
        # Each hunk starts with @@ -start,count +start,count @@
        # Then has - and + lines
        lines = hunk.strip().split('\n')
        
        # Skip the @@ line
        if lines and lines[0].startswith('@@'):
            lines = lines[1:]
        
        # Collect removed and added options
        removed = []  # (letter, text)
        added = []    # (letter, text)
        
        for line in lines:
            if line.startswith('-') and not line.startswith('---'):
                # Parse mcq-opt line
                match = re.search(r'data-val="([abcd])"[^>]*onclick="selectOpt\('[^']+','\1'[^>]*>(.*?)</div></div>', line[1:])
                if match:
                    letter = match.group(1)
                    # Extract text from the HTML
                    opt_html = match.group(2)
                    text_match = re.search(r'<div class="opt-indicator"></div><div>([^<]+)</div>', opt_html)
                    if text_match:
                        text = text_match.group(1).strip()
                        removed.append((letter, text))
            
            elif line.startswith('+') and not line.startswith('+++'):
                match = re.search(r'data-val="([abcd])"[^>]*onclick="selectOpt\('[^']+','\1'[^>]*>(.*?)</div></div>', line[1:])
                if match:
                    letter = match.group(1)
                    opt_html = match.group(2)
                    text_match = re.search(r'<div class="opt-indicator"></div><div>([^<]+)</div>', opt_html)
                    if text_match:
                        text = text_match.group(1).strip()
                        added.append((letter, text))
        
        # Match removed and added
        if removed and added:
            # This is a simplified approach - assume same letter means swap
            # Actually, we need to find which letters had their texts swapped
            # If A had text X before and now has text Y, and B had Y before and now has X,
            # then A and B were swapped
            for r_letter, r_text in removed:
                for a_letter, a_text in added:
                    if r_text == a_text and r_letter != a_letter:
                        # This text moved from r_letter to a_letter
                        # Find the question ID
                        qid_match = re.search(r"selectOpt\('([^']+)',", line)
                        if qid_match:
                            qid = qid_match.group(1)
                            # Extract session from current_file
                            session = current_file.split('/')[0] if current_file else 'unknown'
                            # Store the swap
                            if (session, qid) not in swaps:
                                swaps[(session, qid)] = []
                            swaps[(session, qid)].append((r_letter, a_letter, r_text, a_text))
    
    return swaps


def update_markdown_file(md_file, swaps):
    """Update markdown file with the swaps for its session."""
    with open(md_file, 'r') as f:
        content = f.read()
    
    session_md = os.path.basename(md_file).replace('.md', '')
    
    # Find relevant swaps for this session
    relevant_swaps = [
        (qid, old_letter, new_letter)
        for (session, qid), swaps_list in swaps.items()
        if session in md_file
        for old_letter, new_letter, old_text, new_text in swaps_list
    ]
    
    if not relevant_swaps:
        return 0
    
    # For each swap, update the markdown
    changes = 0
    for qid, old_letter, new_letter in relevant_swaps:
        # This is complex - need to find the question and swap the option texts
        pass
    
    return changes


def main():
    print("Parsing git diff for option swaps...")
    diff = get_git_diff()
    
    if not diff:
        print("No diff found (maybe no commits or files not changed)")
        return
    
    swaps = parse_option_swaps(diff)
    print(f"Found {len(swaps)} questions with option changes")
    
    for key, changes in swaps.items():
        print(f"  {key}: {len(changes)} swaps")


if __name__ == '__main__':
    main()
