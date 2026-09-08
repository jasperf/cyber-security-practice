#!/usr/bin/env python3
"""
Simple script to fix answer distribution by only changing checkMCQ calls.
This doesn't swap option texts - it just changes which letter is marked correct.
The revealAnswer text is updated to show the option text of the new correct letter.
"""

import re
import os
from collections import Counter


def get_option_text(html, qid, letter):
    """Get the text of a specific option for a question."""
    # Find the option with this qid and data-val
    pattern = rf'<div class="mcq-opt"[^>]*onclick="selectOpt\(\'{qid}\'[^>]*data-val="{letter}"[^>]*>.*?<div class="opt-indicator"></div><div>([^<]+)</div>'
    match = re.search(pattern, html, re.DOTALL)
    return match.group(1).strip() if match else None


def update_question(html, qid, new_answer):
    """Update a question to have a new correct answer."""
    # Get the text of the new answer option
    opt_text = get_option_text(html, qid, new_answer)
    if not opt_text:
        print(f"  WARNING: Could not get option text for {qid}, {new_answer}")
        return html
    
    # Update checkMCQ call
    check_pattern = rf'(onclick="checkMCQ\(\'{qid}\'\s*,\s*\')([abcd])(\'\s*\)\s*")'
    html = re.sub(check_pattern, rf'\g<1>{new_answer}\g<3>', html)
    
    # Update revealAnswer to show the option text
    # First, find the current revealAnswer
    reveal_pattern = rf"(revealAnswer\('{qid}'\s*,\s*`)([^`]+)(`\))"
    
    def replace_reveal(match):
        # We want to reveal the option text of the new answer
        return f"{match.group(1)}{opt_text}{match.group(3)}"
    
    html = re.sub(reveal_pattern, replace_reveal, html)
    
    return html


def process_file(filepath):
    """Process a file and redistribute answers."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Find all MCQ questions
    mcq_pattern = r"checkMCQ\('([^']+)','([abcd])'\)"
    matches = list(re.finditer(mcq_pattern, html))
    
    if not matches:
        return 0
    
    qids = [m.group(1) for m in matches]
    current_answers = [m.group(2) for m in matches]
    
    print(f"\n{os.path.basename(filepath)}:")
    print(f"  Current: {Counter(current_answers)}")
    
    # Create target distribution
    n = len(qids)
    target_per_letter = n // 4
    remainder = n % 4
    targets = {'a': target_per_letter, 'b': target_per_letter, 'c': target_per_letter, 'd': target_per_letter}
    for i, letter in enumerate(['a', 'b', 'c', 'd']):
        if i < remainder:
            targets[letter] += 1
    
    print(f"  Target: {targets}")
    
    # Count current distribution
    current_counts = Counter(current_answers)
    
    # For each letter that's over target, change excess to under-target letters
    assignments = {}
    
    # First, keep questions that are already at under-target letters
    for qid, current in zip(qids, current_answers):
        if current_counts[current] > targets[current]:
            # This one should potentially change
            assignments[qid] = None  # Mark for potential change
        else:
            # Keep as is
            assignments[qid] = current
    
    # Now assign new answers to questions marked for change
    # Sort by current answer to distribute evenly
    change_candidates = [(qid, current) for qid, current in zip(qids, current_answers) 
                       if assignments[qid] is None]
    
    # Sort to process in order
    change_candidates.sort(key=lambda x: x[1])
    
    # For each under-target letter, assign to questions
    for letter in ['a', 'b', 'c', 'd']:
        needed = targets[letter] - Counter(assignments.values()).get(letter, 0)
        if needed > 0:
            # Assign this letter to 'needed' questions
            for qid, old_letter in change_candidates[:needed]:
                if assignments[qid] is None:
                    assignments[qid] = letter
            change_candidates = change_candidates[needed:]
    
    # Apply assignments
    changes = 0
    for qid, new_answer in assignments.items():
        if new_answer is None:
            continue
        old_answer_idx = current_answers[qids.index(qid)]
        if old_answer_idx != new_answer:
            html = update_question(html, qid, new_answer)
            changes += 1
    
    # Verify
    new_matches = re.findall(mcq_pattern, html)
    new_answers = [m[1] for m in new_matches]
    print(f"  New: {Counter(new_answers)}")
    print(f"  Changes: {changes}")
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return changes


if __name__ == '__main__':
    base = '/Users/jasperfrumau/code/cyber-security-practice'
    files = [
        f'{base}/s1-cryptography/session1-cryptography.html',
        f'{base}/s2-networking/session2-networking.html',
        f'{base}/s3-red-teaming/session3-red-teaming.html',
        f'{base}/s4-forensics/session4-forensics.html',
        f'{base}/s5-misc-ctf/session5-misc-ctf.html',
    ]
    
    print("=" * 60)
    print("Fixing Answer Distribution")
    print("=" * 60)
    
    total_changes = 0
    for f in files:
        total_changes += process_file(f)
    
    print(f"\nTotal changes: {total_changes}")
