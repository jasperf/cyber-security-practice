#!/usr/bin/env python3
"""
Sync markdown files to match the option orderings from HTML files.
After redistributing answers, the HTML files have swapped option texts,
but the markdown files still have the original order. This script updates
the markdown files to match.
"""

import re
import os
from collections import defaultdict


def extract_html_options(html_file):
    """Extract question options from HTML file."""
    with open(html_file, 'r') as f:
        html = f.read()
    
    # Find all questions with their options
    questions = {}
    
    # Pattern to find question text and options
    # First find all mcq-options divs
    q_pattern = r'<div class="q-card"[^>]*id="qcard-(q\d+)"[^>]*>.*?(<div class="q-body">.*?<div class="mcq-options"[^>]*id="\1-opts"[^>]*>.*?</div>.*?</div>)'
    
    for q_match in re.finditer(r'<div class="q-card"[^>]*id="qcard-(q\d+)"[^>]*>', html):
        qid = q_match.group(1)
        
        # Find the options for this question
        start = q_match.end()
        remaining = html[start:]
        
        # Find the mcq-options div
        opts_match = re.search(r'<div class="mcq-options"[^>]*id="' + re.escape(qid) + r'-opts"[^>]*>(.*?)</div>', remaining, re.DOTALL)
        
        if opts_match:
            opts_html = opts_match.group(1)
            
            # Extract each option text with its letter
            options = {}
            for opt_match in re.finditer(r'data-val="([abcd])"[^>]*onclick="selectOpt\(\'' + re.escape(qid) + r'\'[^>]*>(.*?)</div></div>', opts_html, re.DOTALL):
                letter = opt_match.group(1)
                # Extract text - it's in the last <div> before </div></div>
                opt_text_html = opt_match.group(2)
                text_divs = re.findall(r'<div[^>]*>([^<]+)</div>', opt_text_html)
                if text_divs:
                    text = text_divs[-1].strip()
                else:
                    text = opt_text_html.strip()
                options[letter] = text
            
            if options:
                # Sort by letter to get the order
                sorted_options = [(letter, options[letter]) for letter in sorted(options.keys())]
                questions[qid] = sorted_options
    
    return questions


def extract_md_options(md_file):
    """Extract question options from markdown file."""
    with open(md_file, 'r') as f:
        md = f.read()
    
    questions = {}
    
    # Pattern: **Q1** (1 mark) ... - A) ... - B) ... etc.
    q_pattern = r'\*\*Q(\d+)\*\*'
    
    for q_match in re.finditer(q_pattern, md):
        qid = 'q' + q_match.group(1)
        
        # Find the next lines until the next **Q or ---
        start = q_match.end()
        remaining = md[start:]
        
        # Find options (lines starting with - A), - B), etc.)
        options = []
        opt_pattern = r'- ([ABCD])\)\s*(.+?)(?:\n|$)'
        
        for opt_match in re.finditer(opt_pattern, remaining):
            letter = opt_match.group(1)
            text = opt_match.group(2).strip()
            options.append((letter, text))
            
            # Check if we've reached all 4 options or the next question
            if len(options) >= 4:
                break
        
        if options:
            questions[qid] = options
    
    return questions


def update_md_file(md_file, html_file):
    """Update markdown file options to match HTML file."""
    html_options = extract_html_options(html_file)
    md_options = extract_md_options(md_file)
    
    if not html_options or not md_options:
        print(f"  No options found for {os.path.basename(md_file)}")
        return False
    
    with open(md_file, 'r') as f:
        md_content = f.read()
    
    changes_made = 0
    
    # For each question, check if options differ
    for qid in set(html_options.keys()) & set(md_options.keys()):
        html_opts = {letter: text for letter, text in html_options[qid]}
        md_opts = {letter: text for letter, text in md_options[qid]}
        
        # Check if any option texts differ
        if html_opts != md_opts:
            # Need to update the markdown options to match HTML
            # Find the question in markdown
            q_pattern = rf'\*\*Q{qid[1:]}\*\*[^\n]*\n(.*?)(?=\n\*\*Q|\n---|\n##|\Z)'
            q_match = re.search(q_pattern, md_content, re.DOTALL)
            
            if q_match:
                question_block = q_match.group(0)
                # Replace the options part
                # Find the options lines
                opt_lines_pattern = r'(- [A-D]\) .+?\n)+'
                opt_match = re.search(opt_lines_pattern, question_block)
                
                if opt_match:
                    old_opts_text = opt_match.group(0)
                    
                    # Build new options text
                    new_opts_lines = []
                    for letter, text in html_options[qid]:
                        new_opts_lines.append(f"- {letter}) {text}")
                    new_opts_text = "\n".join(new_opts_lines) + "\n"
                    
                    # Replace
                    new_block = question_block.replace(old_opts_text, new_opts_text)
                    md_content = md_content.replace(question_block, new_block)
                    changes_made += 1
    
    if changes_made > 0:
        with open(md_file, 'w') as f:
            f.write(md_content)
        print(f"  Updated {changes_made} questions")
    else:
        print(f"  No changes needed")
    
    return changes_made > 0


def main():
    base = '/Users/jasperfrumau/code/cyber-security-practice'
    sessions = [
        ('s1', f'{base}/s1-cryptography/session1-cryptography'),
        ('s2', f'{base}/s2-networking/session2-networking'),
        ('s3', f'{base}/s3-red-teaming/session3-red-teaming'),
        ('s4', f'{base}/s4-forensics/session4-forensics'),
        ('s5', f'{base}/s5-misc-ctf/session5-misc-ctf'),
    ]
    
    print("=" * 60)
    print("Syncing Markdown Options with HTML")
    print("=" * 60)
    
    total_changes = 0
    for name, prefix in sessions:
        md_file = f"{prefix}.md"
        html_file = f"{prefix}.html"
        print(f"\nProcessing {name}...")
        
        if update_md_file(md_file, html_file):
            total_changes += 1
    
    print(f"\nTotal files updated: {total_changes}")
    print("\nNow regenerate PDFs to reflect the updated markdown files.")


if __name__ == '__main__':
    main()
