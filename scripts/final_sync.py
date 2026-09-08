#!/usr/bin/env python3
"""
Final script to sync markdown options from HTML files.
Uses a line-by-line approach for reliability.
"""

import re
import os


def get_html_options(html_file):
    """Get options for each question from HTML."""
    with open(html_file, 'r') as f:
        html = f.read()
    
    questions = {}
    
    # Find all mcq-opt entries
    opt_pattern = r"selectOpt\('([^']+)\',this,'([abcd])'[^>]*>.*?<div class=\"opt-indicator\"></div><div>([^<]+)</div>"
    
    for match in re.finditer(opt_pattern, html):
        qid = match.group(1)
        letter = match.group(2)
        text = match.group(3).strip()
        
        if qid not in questions:
            questions[qid] = {}
        questions[qid][letter] = text
    
    # Convert to sorted lists
    result = {}
    for qid in questions:
        opts = [(letter, questions[qid][letter]) for letter in sorted(questions[qid].keys())]
        result[qid] = opts
    
    return result


def get_md_questions(md_file):
    """Get all questions from markdown file."""
    with open(md_file, 'r') as f:
        lines = f.readlines()
    
    questions = {}
    current_qid = None
    current_options = []
    
    for i, line in enumerate(lines):
        # Check for question header
        q_match = re.match(r'\*\*Q(\d+)\*\*', line)
        if q_match:
            # Save previous question
            if current_qid:
                questions[current_qid] = current_options
            
            current_qid = 'q' + q_match.group(1)
            current_options = []
        elif current_qid and line.strip().startswith('- '):
            # Option line
            opt_match = re.match(r'- ([ABCD])\)\s*(.+?)\s*$', line.strip())
            if opt_match:
                letter = opt_match.group(1)
                text = opt_match.group(2).strip()
                current_options.append((letter, text))
        
        # Check if we're at a new section (--- or ##)
        if line.strip().startswith('---') or line.strip().startswith('## '):
            if current_qid:
                questions[current_qid] = current_options
                current_qid = None
    
    # Save last question
    if current_qid:
        questions[current_qid] = current_options
    
    return questions


def update_md_file(md_file, html_file):
    """Update markdown file with options from HTML."""
    html_options = get_html_options(html_file)
    md_questions = get_md_questions(md_file)
    
    with open(md_file, 'r') as f:
        lines = f.readlines()
    
    changes = 0
    current_qid = None
    option_lines_start = None
    
    for i, line in enumerate(lines):
        # Check for question header
        q_match = re.match(r'\*\*Q(\d+)\*\*', line)
        if q_match:
            # Save previous question if needed
            if current_qid and option_lines_start:
                # Check if options need updating
                qid = current_qid
                if qid in html_options and qid in md_questions:
                    html_opts = html_options[qid]
                    md_opts = md_questions[qid]
                    
                    # Check if different
                    if len(html_opts) != len(md_opts) or any(h != m for h, m in zip(html_opts, md_opts)):
                        # Replace option lines
                        new_opt_lines = [f"- {letter.upper()}) {text}\n" for letter, text in html_opts]
                        lines[option_lines_start:i] = new_opt_lines
                        changes += 1
            
            current_qid = 'q' + q_match.group(1)
            option_lines_start = None
        elif current_qid and line.strip().startswith('- '):
            # First option line for this question
            if option_lines_start is None:
                option_lines_start = i
    
    # Handle last question
    if current_qid and option_lines_start:
        qid = current_qid
        if qid in html_options and qid in md_questions:
            html_opts = html_options[qid]
            md_opts = md_questions[qid]
            
            if len(html_opts) != len(md_opts) or any(h != m for h, m in zip(html_opts, md_opts)):
                new_opt_lines = [f"- {letter.upper()}) {text}\n" for letter, text in html_opts]
                lines[option_lines_start:] = new_opt_lines
                changes += 1
    
    if changes > 0:
        with open(md_file, 'w') as f:
            f.writelines(lines)
        print(f"  Updated {changes} questions")
    else:
        print(f"  No changes needed")
    
    return changes


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
            changes = update_md_file(md_file, html_file)
            total_changes += changes
        else:
            print(f"  Files not found")
    
    print(f"\nTotal questions updated: {total_changes}")


if __name__ == '__main__':
    main()
