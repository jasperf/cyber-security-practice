#!/usr/bin/env python3
"""
Sync markdown files to match option orderings from HTML files.
Version 3: More reliable parsing and replacement.
"""

import re
import os


def extract_options_from_html_simple(html_file):
    """Extract all question options from an HTML file."""
    with open(html_file, 'r') as f:
        html = f.read()
    
    questions = {}
    
    # Find all mcq-opt divs
    opt_pattern = r"selectOpt\('([^']+)\',this,'([abcd])'[^>]*>.*?<div class=\"opt-indicator\"></div><div>([^<]+)</div>"
    
    for match in re.finditer(opt_pattern, html):
        qid = match.group(1)
        letter = match.group(2)
        text = match.group(3).strip()
        
        if qid not in questions:
            questions[qid] = {}
        questions[qid][letter] = text
    
    # Sort each question's options by letter and convert to list
    for qid in questions:
        sorted_opts = []
        for letter in sorted(questions[qid].keys()):
            sorted_opts.append((letter, questions[qid][letter]))
        questions[qid] = sorted_opts
    
    return questions


def update_md_file_simple(md_file, html_file):
    """Update markdown file to match HTML file options."""
    html_options = extract_options_from_html_simple(html_file)
    
    if not html_options:
        print(f"  No options found in {os.path.basename(html_file)}")
        return 0
    
    with open(md_file, 'r') as f:
        md_content = f.read()
    
    changes = 0
    
    # For each question in HTML
    for qid, html_opts in html_options.items():
        q_num = qid[1:]  # Remove 'q' prefix
        
        # Build the expected options block with uppercase letters
        expected_opts = []
        for letter, text in html_opts:
            expected_opts.append(f"- {letter.upper()}) {text}")
        expected_block = "\n".join(expected_opts)
        
        # Find the question in markdown
        # Pattern: **QN** (marks) question text (may be multiple lines) then options
        # We need to find the exact question and its current options
        # First find the question header
        q_header_pattern = rf'\*\*Q{q_num}\*\*[^\n]*\n'
        q_header_match = re.search(q_header_pattern, md_content)
        
        if q_header_match:
            start_pos = q_header_match.end()
            remaining = md_content[start_pos:]
            
            # Find the question text (lines until we hit options or next section)
            # Question text ends when we find a line starting with - [A-D]) or a new section
            text_end_match = re.search(r'(\n- [A-D]\))', remaining)
            if text_end_match:
                question_text = remaining[:text_end_match.start()]
                full_question = q_header_match.group(0) + question_text
                start_of_opts = start_pos + text_end_match.start()
                
                # Find all consecutive option lines
                opt_pattern = r'(\n- [A-D]\) .+?)+'
                opt_match = re.search(opt_pattern, remaining[text_end_match.start():])
                
                if opt_match:
                    # Check if options already match
                    current_opts_text = opt_match.group(0)
                    
                    # Compare options (not sorted, in order)
                    current_lines = [line.strip() for line in current_opts_text.strip().split('\n') if line.strip()]
                    expected_lines = [line.strip() for line in expected_block.strip().split('\n') if line.strip()]
                    
                    if current_lines != expected_lines:
                        # Replace the options
                        new_full = full_question + expected_block
                        old_full = full_question + current_opts_text
                        md_content = md_content.replace(old_full, new_full)
                        changes += 1
    
    if changes > 0:
        with open(md_file, 'w') as f:
            f.write(md_content)
        print(f"  Updated {changes} questions")
        return changes
    else:
        print(f"  No changes needed")
        return 0


def main():
    base = '/Users/jasperfrumau/code/cyber-security-practice'
    sessions = [
        ('s1-cryptography', f'{base}/s1-cryptography/session1-cryptography'),
        ('s2-networking', f'{base}/s2-networking/session2-networking'),
        ('s3-red-teaming', f'{base}/s3-red-teaming/session3-red-teaming'),
        ('s4-forensics', f'{base}/s4-forensics/session4-forensics'),
        ('s5-misc-ctf', f'{base}/s5-misc-ctf/session5-misc-ctf'),
    ]
    
    print("=" * 60)
    print("Syncing Markdown Options from HTML Files")
    print("=" * 60)
    
    total_changes = 0
    for name, prefix in sessions:
        md_file = f"{prefix}.md"
        html_file = f"{prefix}.html"
        print(f"\nProcessing {name}...")
        
        if os.path.exists(md_file) and os.path.exists(html_file):
            changes = update_md_file_simple(md_file, html_file)
            total_changes += changes
        else:
            print(f"  Files not found")
    
    print(f"\nTotal questions updated: {total_changes}")
    print("\nNow regenerate PDFs using convert-to-pdf.sh")


if __name__ == '__main__':
    main()
