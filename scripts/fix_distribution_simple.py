#!/usr/bin/env python3
"""
Simple and reliable script to redistribute MCQ answers.
Changes checkMCQ calls and swaps option texts.
"""

import re
import os
from collections import Counter


def swap_options_and_answer(html, qid, old_letter, new_letter):
    """
    Swap two options in a question and update checkMCQ.
    
    Args:
        html: The full HTML content
        qid: Question ID (e.g., 'q1')
        old_letter: Current correct answer letter
        new_letter: New correct answer letter
    """
    # Extract option text for old_letter and new_letter
    # Match: data-val="X" ... onclick="selectOpt('qid',...)" ... > ... <div class="opt-indicator"></div><div>TEXT</div>
    opt_pattern = rf'data-val="([abcd])"[^>]*onclick="selectOpt\([^)]+{qid}[^)]+\)"[^>]*>.*?<div class="opt-indicator"></div><div>([^<]+)</div>'
    
    all_opts = re.findall(opt_pattern, html)
    
    if not all_opts:
        print(f"  WARNING: Could not find options for {qid}")
        return html
    
    # Find the old and new option texts
    old_text = None
    new_text = None
    
    for letter, text in all_opts:
        if letter == old_letter:
            old_text = text
        elif letter == new_letter:
            new_text = text
    
    if not old_text or not new_text:
        print(f"  WARNING: Could not find both options for {qid} ({old_letter}, {new_letter})")
        return html
    
    # Swap the texts in the HTML
    # Replace old_letter option text with new_text
    # Pattern: data-val="OLD" ... <div class="opt-indicator"></div><div>OLD_TEXT</div>
    old_opt_pattern = rf'(data-val="{old_letter}"[^>]*onclick="selectOpt\([^)]+{qid}[^)]+\)"[^>]*>.*?<div class="opt-indicator"></div><div>)[^<]+(</div>)'
    html = re.sub(old_opt_pattern, rf'\g<1>{new_text}\g<2>', html)
    
    # Replace new_letter option text with old_text
    new_opt_pattern = rf'(data-val="{new_letter}"[^>]*onclick="selectOpt\([^)]+{qid}[^)]+\)"[^>]*>.*?<div class="opt-indicator"></div><div>)[^<]+(</div>)'
    html = re.sub(new_opt_pattern, rf'\g<1>{old_text}\g<2>', html)
    
    # Update checkMCQ call
    check_pattern = rf"(checkMCQ\('{qid}'\s*,\s*'){old_letter}(')"
    html = re.sub(check_pattern, rf'\g<1>{new_letter}\g<2>', html)
    
    return html


def get_assignments_for_session(qids, current_answers):
    """
    Create a balanced assignment of answers.
    Returns dict: {qid: new_answer_letter}
    """
    n = len(qids)
    target = n // 4
    remainder = n % 4
    targets = {'a': target, 'b': target, 'c': target, 'd': target}
    for i, letter in enumerate(['a', 'b', 'c', 'd']):
        if i < remainder:
            targets[letter] += 1
    
    # Current counts
    current_counts = Counter(current_answers)
    
    # Questions to potentially change (those with over-represented answers)
    over_rep = [qid for qid, ans in zip(qids, current_answers) 
                if current_counts[ans] > targets[ans]]
    
    # Questions to keep (those with under-represented answers)
    assignments = {}
    under_counts = {l: targets[l] - current_counts.get(l, 0) for l in ['a', 'b', 'c', 'd']}
    
    # Keep all questions with under-represented answers
    for qid, ans in zip(qids, current_answers):
        if current_counts[ans] <= targets[ans]:
            assignments[qid] = ans
        else:
            assignments[qid] = None  # Mark for change
    
    # Now assign new answers to questions that need to change
    # For each letter that needs more, assign to questions
    import random
    random.seed(42)
    random.shuffle(over_rep)
    
    for letter in ['a', 'b', 'c', 'd']:
        needed = under_counts[letter]
        if needed > 0:
            # Assign 'needed' questions to this letter
            for qid in over_rep[:needed]:
                if assignments[qid] is None:
                    # Find current answer for this qid
                    idx = qids.index(qid)
                    old_letter = current_answers[idx]
                    assignments[qid] = letter
            over_rep = over_rep[needed:]
    
    return assignments


def process_file(filepath):
    """Process a single HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Find all MCQ questions
    mcq_pattern = r"checkMCQ\('([^']+)','([abcd])'\)"
    matches = list(re.finditer(mcq_pattern, html))
    
    if not matches:
        print(f"{os.path.basename(filepath)}: No MCQ found")
        return 0
    
    qids = [m.group(1) for m in matches]
    current_answers = [m.group(2) for m in matches]
    
    print(f"\n{os.path.basename(filepath)}:")
    print(f"  Before: {Counter(current_answers)}")
    
    # Get assignments
    assignments = get_assignments_for_session(qids, current_answers)
    
    # Apply changes
    changes = 0
    for qid, new_answer in assignments.items():
        if new_answer is None:
            continue
        idx = qids.index(qid)
        old_answer = current_answers[idx]
        if old_answer != new_answer:
            html = swap_options_and_answer(html, qid, old_answer, new_answer)
            changes += 1
    
    # Verify
    new_matches = re.findall(mcq_pattern, html)
    new_answers = [m[1] for m in new_matches]
    print(f"  After:  {Counter(new_answers)}")
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
    print("Redistributing MCQ Answers")
    print("=" * 60)
    
    total_changes = 0
    for f in files:
        total_changes += process_file(f)
    
    print(f"\nTotal changes: {total_changes}")
    
    # Final verification
    print("\n" + "=" * 60)
    print("Final Distribution")
    print("=" * 60)
    all_answers = []
    for f in files:
        with open(f, 'r') as fh:
            content = fh.read()
        matches = re.findall(r"checkMCQ\('([^']+)','([abcd])'\)", content)
        answers = [m[1] for m in matches]
        all_answers.extend(answers)
        dist = Counter(answers)
        print(f"{os.path.basename(f)}: {dict(dist)}")
    
    overall = Counter(all_answers)
    print(f"\nOVERALL: {dict(overall)}")
    total = len(all_answers)
    balanced = all(abs(overall.get(l, 0) / total - 0.25) < 0.05 for l in ['a', 'b', 'c', 'd'])
    print(f"Balanced: {'YES' if balanced else 'NO'}")
