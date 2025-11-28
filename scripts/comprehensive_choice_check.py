#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Choice Check
Finds all potential mismatches between question types and their choices
"""

import json
import sys
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def count_words(text: str) -> int:
    """Count words in text"""
    return len(text.strip().split())

def is_likely_sentence(text: str) -> bool:
    """Check if text is likely a complete sentence"""
    text = text.strip()
    if not text:
        return False
    
    word_count = count_words(text)
    
    # Very short = not a sentence
    if word_count <= 2:
        return False
    
    # Starts with capital and ends with period = likely sentence
    if text[0].isupper() and text[-1] in '.!?':
        return True
    
    # Has article at start + verb = likely sentence
    if word_count >= 4:
        words = text.split()
        has_article = words[0].lower() in ['a', 'an', 'the']
        common_verbs = ['is', 'are', 'was', 'were', 'has', 'have', 'had', 'will', 'would']
        has_verb = any(v in text.lower() for v in common_verbs)
        
        if has_article and has_verb:
            return True
    
    return False

def check_question(question: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Check a single question for issues"""
    issues = []
    q_id = question.get('id', 'unknown')
    q_type = question.get('type', '')
    prompt = question.get('prompt', '')
    choices = question.get('choices', [])
    source_file = question.get('_source_file', 'unknown')
    
    if not choices:
        return issues
    
    prompt_lower = prompt.lower()
    
    # Check 1: Gap fill questions
    if q_type == 'gap_fill':
        for choice in choices:
            choice_id = choice.get('choiceId', '')
            choice_text = choice.get('text', '').strip()
            word_count = count_words(choice_text)
            
            # Issue: Choice is a full sentence (5+ words or looks like sentence)
            if word_count >= 5 or (word_count >= 4 and is_likely_sentence(choice_text)):
                issues.append({
                    'question_id': q_id,
                    'source_file': source_file,
                    'question_type': q_type,
                    'prompt': prompt,
                    'choice_id': choice_id,
                    'choice_text': choice_text,
                    'word_count': word_count,
                    'issue_type': 'gap_fill_full_sentence',
                    'severity': 'high',
                    'description': f'Gap fill question has choice with {word_count} words that appears to be a full sentence. Gap fill choices should be 1-3 words/phrases.',
                })
            
            # Issue: Choice starts with article (suggests new sentence)
            if word_count >= 4 and choice_text.lower().startswith(('a ', 'an ', 'the ')):
                common_phrases = ['a lot', 'a few', 'a little', 'a bit', 'the same', 'the most', 'the least']
                if not any(choice_text.lower().startswith(phrase) for phrase in common_phrases):
                    issues.append({
                        'question_id': q_id,
                        'source_file': source_file,
                        'question_type': q_type,
                        'prompt': prompt,
                        'choice_id': choice_id,
                        'choice_text': choice_text,
                        'word_count': word_count,
                        'issue_type': 'gap_fill_starts_with_article',
                        'severity': 'medium',
                        'description': f'Gap fill choice starts with article "{choice_text.split()[0]}" and has {word_count} words. This suggests it might be a new sentence rather than filling the blank.',
                    })
    
    # Check 2: Transformation questions
    is_transformation = any(keyword in prompt_lower for keyword in [
        'change', 'transform', 'convert', 'rewrite', 'rephrase', 'change this', 'change into'
    ])
    
    if is_transformation:
        for choice in choices:
            choice_id = choice.get('choiceId', '')
            choice_text = choice.get('text', '').strip()
            word_count = count_words(choice_text)
            
            # Issue: Choice is just a verb form (1-2 words, common verbs)
            if word_count <= 2:
                verb_forms = ['is', 'are', 'was', 'were', 'be', 'been', 'being', 'has', 'have', 'had',
                             'will', 'would', 'can', 'could', 'should', 'must', 'may', 'might']
                words = choice_text.lower().split()
                if choice_text.lower() in verb_forms or (word_count == 2 and words[0].lower() in verb_forms):
                    issues.append({
                        'question_id': q_id,
                        'source_file': source_file,
                        'question_type': q_type,
                        'prompt': prompt,
                        'choice_id': choice_id,
                        'choice_text': choice_text,
                        'word_count': word_count,
                        'issue_type': 'transformation_verb_form_only',
                        'severity': 'high',
                        'description': f'Transformation question has choice that is just a verb form "{choice_text}". Transformation choices should be complete transformed sentences (4+ words).',
                    })
            
            # Issue: Choice is too short for a transformation (less than 4 words)
            elif word_count < 4:
                issues.append({
                    'question_id': q_id,
                    'source_file': source_file,
                    'question_type': q_type,
                    'prompt': prompt,
                    'choice_id': choice_id,
                    'choice_text': choice_text,
                    'word_count': word_count,
                    'issue_type': 'transformation_too_short',
                    'severity': 'medium',
                    'description': f'Transformation question has choice with only {word_count} words. Transformation choices should typically be complete sentences (4+ words).',
                })
    
    return issues

def main():
    assets_dir = Path('assets/data')
    bank_files = [
        'question_bank.json',
        'question_bank1.json',
        'question_bank2.json',
        'question_bank3.json',
    ]
    
    all_questions = []
    for bank_file in bank_files:
        file_path = assets_dir / bank_file
        if not file_path.exists():
            continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for q in data:
                        q['_source_file'] = bank_file
                    all_questions.extend(data)
        except Exception as e:
            print(f'Error loading {bank_file}: {e}')
    
    print('=' * 80)
    print('COMPREHENSIVE CHOICE MISMATCH CHECK')
    print('=' * 80)
    print(f'\nTotal questions: {len(all_questions)}\n')
    
    all_issues = []
    issues_by_type = {}
    issues_by_severity = {'high': [], 'medium': [], 'low': []}
    
    for question in all_questions:
        issues = check_question(question)
        all_issues.extend(issues)
        
        for issue in issues:
            issue_type = issue['issue_type']
            severity = issue['severity']
            
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)
            
            issues_by_severity[severity].append(issue)
    
    # Print results
    if all_issues:
        print(f'🔴 Found {len(all_issues)} potential issues:\n')
        
        # Group by severity
        print(f'  High severity: {len(issues_by_severity["high"])}')
        print(f'  Medium severity: {len(issues_by_severity["medium"])}')
        print(f'  Low severity: {len(issues_by_severity["low"])}\n')
        
        # Show by issue type
        for issue_type, issues in sorted(issues_by_type.items()):
            print(f'\n{issue_type.replace("_", " ").title()} ({len(issues)} issues):')
            print('-' * 80)
            
            for issue in issues[:10]:  # Show first 10
                print(f'\n  Question ID: {issue["question_id"]} ({issue["source_file"]})')
                print(f'  Prompt: {issue["prompt"][:70]}...')
                print(f'  Choice {issue["choice_id"]}: "{issue["choice_text"]}" ({issue["word_count"]} words)')
                print(f'  Issue: {issue["description"]}')
            
            if len(issues) > 10:
                print(f'\n  ... and {len(issues) - 10} more issues of this type')
    else:
        print('✅ No issues found! All choices appear to match their question types correctly.')
    
    # Save detailed report
    report = {
        'total_questions': len(all_questions),
        'total_issues': len(all_issues),
        'issues_by_type': {k: len(v) for k, v in issues_by_type.items()},
        'issues_by_severity': {k: len(v) for k, v in issues_by_severity.items()},
        'all_issues': all_issues,
    }
    
    output_file = Path('comprehensive_choice_report.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f'\n\n✅ Detailed report saved to {output_file}')
    
    if all_issues:
        print('\n⚠️  NEXT STEPS:')
        print('   1. Review the issues in comprehensive_choice_report.json')
        print('   2. For each issue, check if the choice is actually wrong or if it\'s a false positive')
        print('   3. Fix confirmed issues in the appropriate question bank file')
        print('   4. Re-run this script to verify fixes')
        return 1
    else:
        return 0

if __name__ == '__main__':
    exit(main())

