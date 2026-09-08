#!/usr/bin/env python3
"""
Apply balanced answer redistribution to all session HTML files.

This script redistributes MCQ correct answers to achieve roughly
equal distribution across A, B, C, D options (target: 25% each).

It works by:
1. Identifying all MCQ questions in each session
2. For questions where the answer needs to change:
   a. Swapping the option texts between the old correct answer and new correct answer
   b. Updating the checkMCQ call to use the new answer letter
   c. Updating selectOpt onclick handlers to maintain consistency

Usage:
    python3 scripts/apply_answer_redistribution.py
"""

import re
import os
from collections import Counter


def get_option_html(html, qid, letter):
    """Extract the full HTML of a specific option for a question."""
    # Find the specific option directly (no need to find the container first)
    # Look for the option with matching qid and letter in its onclick
    opt_pattern = rf'<div class="mcq-opt"[^>]*onclick="selectOpt\(\'{qid}\'[^>]*data-val="{letter}"[^>]*>.*?</div>'
    opt_match = re.search(opt_pattern, html, re.DOTALL)
    
    return opt_match.group(0) if opt_match else None


def extract_option_text(option_html):
    """Extract just the text content from an option HTML."""
    # Find all <div> tags and get the last one (the text content)
    divs = re.findall(r'<div[^>]*>([^<]+)</div>', option_html)
    if divs:
        # The text is in the last div
        return divs[-1].strip()
    return None


def create_option_html(qid, letter, text_content, is_multi=False):
    """Create a new mcq-opt div with the given letter and text."""
    multi_str = 'true' if is_multi else 'false'
    return f'<div class="mcq-opt" data-val="{letter}" onclick="selectOpt(\'{qid}\',this,\'{letter}\',{multi_str})\"><div class=\"opt-indicator\"></div><div>{text_content}</div></div>'


def swap_options_in_html(html, qid, old_letter, new_letter):
    """Swap two options in the HTML by swapping their text content and data-val."""
    # Extract both options
    old_opt = get_option_html(html, qid, old_letter)
    new_opt = get_option_html(html, qid, new_letter)
    
    if not old_opt or not new_opt:
        print(f"  WARNING: Could not find options for {qid} ({old_letter}, {new_letter})")
        return html
    
    # Extract texts
    old_text = extract_option_text(old_opt)
    new_text = extract_option_text(new_opt)
    
    if not old_text or not new_text:
        print(f"  WARNING: Could not extract text from options for {qid}")
        return html
    
    # Create new option HTMLs with swapped content
    old_opt_new = create_option_html(qid, old_letter, new_text)
    new_opt_new = create_option_html(qid, new_letter, old_text)
    
    # Replace in the html
    html = html.replace(old_opt, old_opt_new)
    html = html.replace(new_opt, new_opt_new)
    
    return html


def update_check_mcq(html, qid, new_answer):
    """Update the checkMCQ call to use the new answer."""
    pattern = rf'(onclick="checkMCQ\(\'{qid}\'\s*,\s*\')([abcd])(\'\s*\)\s*")'
    return re.sub(pattern, rf'\g<1>{new_answer}\g<3>', html)


def process_session(filepath, assignments):
    """Process a single session file with given answer assignments."""
    session_name = os.path.basename(filepath).replace('.html', '')
    print(f"\nProcessing {session_name}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Get current distribution
    current_matches = re.findall(r"checkMCQ\('([^']+)','([abcd])'\)", html)
    current_answers = [m[1] for m in current_matches]
    print(f"  Current distribution: {Counter(current_answers)}")
    
    # Apply each assignment
    changes_made = 0
    for qid, new_answer in assignments.items():
        # Find current answer
        current_pattern = rf'checkMCQ\(\'{qid}\'\s*,\s*\'([abcd])\''
        current_match = re.search(current_pattern, html)
        
        if not current_match:
            print(f"  WARNING: Could not find current answer for {qid}")
            continue
        
        old_answer = current_match.group(1)
        
        if old_answer != new_answer:
            # Swap the option texts
            html = swap_options_in_html(html, qid, old_answer, new_answer)
            # Update checkMCQ call
            html = update_check_mcq(html, qid, new_answer)
            changes_made += 1
    
    # Verify new distribution
    new_matches = re.findall(r"checkMCQ\('([^']+)','([abcd])'\)", html)
    new_answers = [m[1] for m in new_matches]
    print(f"  New distribution: {Counter(new_answers)}")
    print(f"  Changes made: {changes_made}")
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)


def get_assignments():
    """Define target assignments for each session to achieve balanced distribution."""
    
    # S1: 19 questions, current: A:2, B:13, C:3, D:1
    # Target: A:5, B:5, C:5, D:4
    s1 = {
        'q1': 'd',    # was a
        'q4': 'a',    # was b
        'q5': 'd',    # was b
        'q6': 'd',    # was b
        'q7': 'a',    # was b
        'q8': 'c',    # was b
        'q10': 'd',   # was c
        'q12': 'c',   # was b
        'q13': 'd',   # was b
        'q14': 'c',   # was b
        'q15': 'd',   # was b
        'q17': 'd',   # was a
        'q18': 'c',   # was b
        'q19': 'a',   # was b
        'q20': 'c',   # was b
        'q21': 'a',   # was b
    }
    
    # S2: 19 questions, current: A:3, B:10, C:6, D:0
    # Target: A:5, B:5, C:5, D:4
    s2 = {
        'q1': 'a',    # was c
        'q2': 'a',    # was b
        'q3': 'c',    # was b
        'q4': 'd',    # was c
        'q6': 'd',    # was a
        'q8': 'd',    # was b
        'q9': 'c',    # was b
        'q10': 'd',   # was c
        'q11': 'a',   # was c
        'q12': 'c',   # was b
        'q13': 'd',   # was b
        'q15': 'd',   # was c
        'q16': 'c',   # was b
        'q17': 'd',   # was b
        'q18': 'd',   # was b
        'q20': 'c',   # was b
        'q21': 'd',   # was c
    }
    
    # S3: 20 questions, current: A:3, B:17, C:0, D:0
    # Target: A:5, B:5, C:5, D:5
    s3 = {
        'q1': 'a',    # was b
        'q2': 'd',    # was b
        'q3': 'c',    # was b
        'q5': 'c',    # was b
        'q6': 'c',    # was b
        'q7': 'd',    # was b
        'q8': 'd',    # was b
        'q10': 'c',   # was b
        'q11': 'd',   # was b
        'q12': 'd',   # was b
        'q14': 'c',   # was b
        'q15': 'd',   # was b
        'q16': 'a',   # was b
        'q17': 'd',   # was b
        'q18': 'd',   # was b
        'q19': 'd',   # was b
        'q20': 'd',   # was b
    }
    
    # S4: 18 questions, current: A:2, B:13, C:3, D:0
    # Target: A:5, B:5, C:4, D:4
    s4 = {
        'q1': 'a',    # was b
        'q2': 'd',    # was b
        'q3': 'a',    # was b
        'q5': 'd',    # was b
        'q6': 'c',    # was b
        'q7': 'd',    # was c
        'q8': 'd',    # was b
        'q9': 'a',    # was c
        'q10': 'a',   # was c
        'q13': 'a',   # was b
        'q14': 'c',   # was b
        'q15': 'a',   # was b
        'q16': 'd',   # was b
        'q17': 'a',   # was b
        'q18': 'c',   # was b
        'q19': 'd',   # was b
    }
    
    # S5: 19 questions, current: A:1, B:17, C:1, D:0
    # Target: A:5, B:5, C:5, D:4
    s5 = {
        'q1': 'a',    # was b
        'q2': 'd',    # was b
        'q3': 'c',    # was b
        'q4': 'd',    # was b
        'q7': 'a',    # was b
        'q8': 'd',    # was b
        'q9': 'a',    # was c
        'q10': 'a',   # was b
        'q11': 'd',   # was b
        'q12': 'c',   # was b
        'q13': 'a',   # was b
        'q14': 'd',   # was b
        'q15': 'c',   # was b
        'q16': 'd',   # was b
        'q17': 'd',   # was b
        'q18': 'c',   # was b
        'q19': 'a',   # was b
        'q20': 'c',   # was b
    }
    
    return {
        's1-cryptography/session1-cryptography.html': s1,
        's2-networking/session2-networking.html': s2,
        's3-red-teaming/session3-red-teaming.html': s3,
        's4-forensics/session4-forensics.html': s4,
        's5-misc-ctf/session5-misc-ctf.html': s5,
    }


if __name__ == '__main__':
    base_dir = '/Users/jasperfrumau/code/cyber-security-practice'
    
    print("=" * 60)
    print("Applying Answer Redistribution")
    print("=" * 60)
    
    assignments = get_assignments()
    
    for filepath, session_assignments in assignments.items():
        full_path = os.path.join(base_dir, filepath)
        process_session(full_path, session_assignments)
    
    print("\n" + "=" * 60)
    print("Verification")
    print("=" * 60)
    
    # Verify final distribution
    all_answers = []
    for filepath in assignments.keys():
        full_path = os.path.join(base_dir, filepath)
        with open(full_path, 'r') as f:
            content = f.read()
        matches = re.findall(r"checkMCQ\('([^']+)','([abcd])'\)", content)
        answers = [m[1] for m in matches]
        all_answers.extend(answers)
        dist = Counter(answers)
        session_name = os.path.basename(filepath).replace('.html', '')
        print(f"\n{session_name}: {dict(dist)}")
    
    overall = Counter(all_answers)
    print(f"\nOVERALL: {dict(overall)}")
    
    # Check if balanced
    total = len(all_answers)
    balanced = all(abs(overall.get(l, 0) / total - 0.25) < 0.05 for l in ['a', 'b', 'c', 'd'])
    print(f"Balanced: {'YES' if balanced else 'NO'}")
