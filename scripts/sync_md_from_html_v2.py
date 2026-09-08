#!/usr/bin/env python3
"""
Sync markdown files to match option orderings from HTML files.
Simpler version that just extracts text from mcq-opt divs.
"""

import re
import os


def extract_options_from_html_simple(html_file):
    """Extract all question options from an HTML file using simple patterns."""
    with open(html_file, 'r') as f:
        html = f.read()
    
    questions = {}
    
    # Find all mcq-opt divs
    # Pattern: find selectOpt('qX',this,'letter',...
    opt_pattern = r"selectOpt\('([^']+)\',this,'([abcd])'[^>]*>.*?<div class=\"opt-indicator\"></div><div>([^<]+)</div>"
    
    for match in re.finditer(opt_pattern, html):
        qid = match.group(1)
        letter = match.group(2)
        text = match.group(3).strip()
        
        if qid not in questions:
            questions[qid] = {}
        questions[qid][letter] = text
    
    # Sort each question's options by letter
    for qid in questions:
        sorted_opts = [(letter, questions[qid][letter]) for letter in sorted(questions[qid].keys())]
        questions[qid] = sorted_opts
    
    return questions


def extract_questions_from_md_simple(md_file):
    """Extract all question options from a markdown file."""
    with open(md_file, 'r') as f:
        md = f.read()
    
    questions = {}
    
    # Pattern: **Q1** ... - A) ... - B) ... etc.
    q_pattern = r'\*\*Q(\d+)\*\*'
    
    for q_match in re.finditer(q_pattern, md):
        qid = 'q' + q_match.group(1)
        start_pos = q_match.end()
        remaining = md[start_pos:]
        
        # Find options (lines starting with - A), - B), etc.)
        options = []
        opt_pattern = r'- ([ABCD])\)\s*(.+?)(?:\n|$)'
        
        for opt_match in re.finditer(opt_pattern, remaining):
            letter = opt_match.group(1)
            text = opt_match.group(2).strip()
            options.append((letter, text))
            
            if len(options) >= 4:
                break
        
        if options:
            questions[qid] = options
    
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
        
        # Build the expected options block
        expected_opts = []
        for letter, text in html_opts:
            # Use uppercase letter (A, B, C, D)
            expected_opts.append(f"- {letter.upper()}) {text}")
        expected_block = "\n".join(expected_opts)
        
        # Find the question in markdown
        # Pattern: **QN** ... (options follow)
        # We need to find the question and replace its options
        q_pattern = rf'\*\*Q{q_num}\*\*[^\n]*\n((?:[^\n]*\n)*?)(?=\n\*\*Q|\n---|\n##|\n\*\*|\Z)'
        q_match = re.search(q_pattern, md_content, re.DOTALL)
        
        if q_match:
            question_text_and_opts = q_match.group(1)
            
            # Find the options part in this question
            # Options are lines starting with - A), - B), etc.
            opt_match = re.search(r'(\n- [A-D]\) .+?)+', question_text_and_opts, re.DOTALL)
            
            if opt_match:
                current_opts_block = opt_match.group(0).strip()
                
                # Check if different
                if current_opts_block.replace('\n', '') != expected_block.replace('\n', ''):
                    # Replace
                    new_question = question_text_and_opts.replace(current_opts_block, '\n' + expected_block + '\n')
                    md_content = md_content.replace(question_text_and_opts, new_question)
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
