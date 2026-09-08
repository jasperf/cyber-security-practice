#!/usr/bin/env python3
"""
Sync markdown files to match option orderings from HTML files.
This ensures that printable worksheets match the interactive versions.
"""

import re
import os


def extract_options_from_html(html_file):
    """Extract all question options from an HTML file."""
    with open(html_file, 'r') as f:
        html = f.read()
    
    questions = {}
    
    # Find all q-card divs
    qcard_pattern = r'<div class="q-card"[^>]*id="qcard-(q\d+)"[^>]*>'
    
    for q_match in re.finditer(qcard_pattern, html):
        qid = q_match.group(1)
        start_pos = q_match.end()
        
        # Find the mcq-options div for this question
        remaining = html[start_pos:]
        opts_match = re.search(r'<div class="mcq-options"[^>]*id="' + re.escape(qid) + r'-opts"[^>]*>(.*?)</div>', remaining, re.DOTALL)
        
        if opts_match:
            opts_html = opts_match.group(1)
            options = []
            
            # Extract each option
            for opt_match in re.finditer(r'<div class="mcq-opt"[^>]*data-val="([abcd])"[^>]*>.*?<div class="opt-indicator"></div><div>([^<]+)</div>', opts_html):
                letter = opt_match.group(1)
                text = opt_match.group(2).strip()
                options.append((letter, text))
            
            if options:
                # Sort by letter (A, B, C, D)
                options.sort(key=lambda x: x[0])
                questions[qid] = options
    
    return questions


def extract_questions_from_md(md_file):
    """Extract all question options from a markdown file."""
    with open(md_file, 'r') as f:
        md = f.read()
    
    questions = {}
    
    # Pattern: **Q1** (1 mark) ... - A) ... - B) ... etc.
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


def update_md_file(md_file, html_file):
    """Update markdown file to match HTML file options."""
    html_options = extract_options_from_html(html_file)
    md_options = extract_questions_from_md(md_file)
    
    if not html_options:
        print(f"  No options found in {os.path.basename(html_file)}")
        return 0
    
    with open(md_file, 'r') as f:
        md_content = f.read()
    
    changes = 0
    
    # For each question in HTML
    for qid, html_opts in html_options.items():
        if qid not in md_options:
            continue
        
        md_opts = md_options[qid]
        
        # Check if options match
        options_match = True
        for (h_letter, h_text), (m_letter, m_text) in zip(html_opts, md_opts):
            if h_text != m_text:
                options_match = False
                break
        
        if options_match:
            continue
        
        # Options differ - need to update
        # Find the question in markdown
        q_num = qid[1:]
        q_pattern = rf'\*\*Q{q_num}\*\*[^\n]*\n(.*?)(?=\n\*\*Q|\n---|\n##|\Z)'
        q_match = re.search(q_pattern, md_content, re.DOTALL)
        
        if q_match:
            question_block = q_match.group(0)
            
            # Replace the options part
            # Find the options lines
            opt_lines_pattern = r'(- [A-D]\) .+?\n)+'
            opt_match = re.search(opt_lines_pattern, question_block)
            
            if opt_match:
                old_opts_text = opt_match.group(0)
                
                # Build new options text from HTML
                new_opts_lines = []
                for letter, text in html_opts:
                    new_opts_lines.append(f"- {letter}) {text}")
                new_opts_text = "\n".join(new_opts_lines) + "\n"
                
                # Replace
                new_block = question_block.replace(old_opts_text, new_opts_text)
                md_content = md_content.replace(question_block, new_block)
                changes += 1
    
    if changes > 0:
        with open(md_file, 'w') as f:
            f.write(md_content)
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
    print("\nNow regenerate PDFs using convert-to-pdf.sh")


if __name__ == '__main__':
    main()
