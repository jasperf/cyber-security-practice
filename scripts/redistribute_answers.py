#!/usr/bin/env python3
"""
Script to redistribute MCQ answers across A, B, C, D evenly.

This script analyzes all session HTML files and reports the current
distribution of correct answers for multiple choice questions.

It can also be extended to automatically redistribute answers to achieve
roughly equal distribution (25% per option).

Usage:
    python3 scripts/redistribute_answers.py           # Analyze current distribution
    python3 scripts/redistribute_answers.py --fix    # Apply balanced distribution
"""

import re
import sys
from collections import Counter


def analyze_distribution():
    """Analyze and print current answer distribution for all sessions."""
    sessions = [
        's1-cryptography/session1-cryptography.html',
        's2-networking/session2-networking.html',
        's3-red-teaming/session3-red-teaming.html',
        's4-forensics/session4-forensics.html',
        's5-misc-ctf/session5-misc-ctf.html',
    ]
    
    print("=" * 60)
    print("MCQ Answer Distribution Analysis")
    print("=" * 60)
    
    all_answers = []
    
    for session in sessions:
        filepath = f'/Users/jasperfrumau/code/cyber-security-practice/{session}'
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"WARNING: {filepath} not found")
            continue
        
        # Find all MCQ answers
        mcq_pattern = r"checkMCQ\('([^']+)','([abcd])'\)"
        matches = re.findall(mcq_pattern, content)
        
        if not matches:
            print(f"{session}: No MCQ questions found")
            continue
        
        answers = [m[1] for m in matches]
        all_answers.extend(answers)
        dist = Counter(answers)
        
        print(f"\n{session}:")
        print(f"  Total MCQ questions: {len(answers)}")
        print(f"  A: {dist.get('a', 0)} ({dist.get('a', 0)/len(answers)*100:.1f}%)")
        print(f"  B: {dist.get('b', 0)} ({dist.get('b', 0)/len(answers)*100:.1f}%)")
        print(f"  C: {dist.get('c', 0)} ({dist.get('c', 0)/len(answers)*100:.1f}%)")
        print(f"  D: {dist.get('d', 0)} ({dist.get('d', 0)/len(answers)*100:.1f}%)")
    
    # Overall statistics
    print("\n" + "=" * 60)
    print("OVERALL")
    print("=" * 60)
    if all_answers:
        overall_dist = Counter(all_answers)
        total = len(all_answers)
        print(f"Total MCQ questions: {total}")
        print(f"A: {overall_dist.get('a', 0)} ({overall_dist.get('a', 0)/total*100:.1f}%)")
        print(f"B: {overall_dist.get('b', 0)} ({overall_dist.get('b', 0)/total*100:.1f}%)")
        print(f"C: {overall_dist.get('c', 0)} ({overall_dist.get('c', 0)/total*100:.1f}%)")
        print(f"D: {overall_dist.get('d', 0)} ({overall_dist.get('d', 0)/total*100:.1f}%)")
        
        # Check if distribution is balanced (within 10% of 25%)
        balanced = all(
            abs(overall_dist.get(letter, 0) / total - 0.25) < 0.10
            for letter in ['a', 'b', 'c', 'd']
        )
        print(f"\nBalanced distribution: {'YES' if balanced else 'NO'}")
        if not balanced:
            print("  -> Consider redistributing answers for better randomness")


if __name__ == '__main__':
    analyze_distribution()
