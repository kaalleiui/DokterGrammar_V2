#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Find Choice Mismatches - Comprehensive Check
Finds all questions where choices don't match the question type/format
"""

import json
import sys
import re
from pathlib import Path
from typing import List, Dict, Any

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def analyze_question(question: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze a single question for mismatches"""
    issues = []
    q_id = question.get('id', 'unknown')
    q_type = question.get('type', '')
    prompt = question.get('prompt', '')
    choices = question.get('choices', [])
    
    if not choices:
        return issues
    
    # Check 1: Gap fill questions should have word/phrase choices, not full sentences
    if q_type == 'gap_fill':
        # Extract the sentence with blank
        blank_match = re.search(r"Fill in the blank:\s*['\"](.*?)['\"]", prompt, re.IGNORECASE)
        if blank_match:
            sentence_with_blank = blank_match.group(1)
            
            for choice in choices:
                choice_text = choice.get('text', '').strip()
                choice_id = choice.get('choiceId', '')
                
                # Count words in choice
                word_count = len(choice_text.split())
                
                # If choice has 5+ words, it's likely a full sentence (should be just a word/phrase)
                if word_count >= 5:
                    # Check if it looks like a complete sentence
                    if choice_text[0].isupper() and (choice_text[-1] in '.!?' or word_count >= 6):
                        issues.append({
                            'type': 'gap_fill_full_sentence',
                            'question_id': q_id,
                            'choice_id': choice_id,
                            'choice_text': choice_text,
                            'prompt': prompt,
                            'word_count': word_count,
                            'issue': f'Gap fill choice has {word_count} words - likely a full sentence instead of a word/phrase'
                        })
                
                # Check if choice is a complete sentence that doesn't match the blank context
                # For example, if prompt is "The city _____ built next year" 
                # and choice is "a new city has been built" - this is wrong
                if word_count >= 4:
                    # Check if choice contains subject + verb that could form a sentence
                    has_article = any(choice_text.lower().startswith(art) for art in ['a ', 'an ', 'the '])
                    has_verb = any(v in choice_text.lower() for v in [' is ', ' are ', ' was ', ' were ', ' has ', ' have ', ' had '])
                    
                    if has_article and has_verb:
                        issues.append({
                            'type': 'gap_fill_complete_sentence',
                            'question_id': q_id,
                            'choice_id': choice_id,
                            'choice_text': choice_text,
                            'prompt': prompt,
                            'issue': 'Choice appears to be a complete sentence with article + verb, not a word/phrase for the blank'
                        })
    
    # Check 2: Transformation questions should have transformed sentences, not just verb forms
    prompt_lower = prompt.lower()
    is_transformation = any(keyword in prompt_lower for keyword in [
        'change', 'transform', 'convert', 'rewrite', 'rephrase', 'change this', 'change into'
    ])
    
    if is_transformation:
        for choice in choices:
            choice_text = choice.get('text', '').strip()
            choice_id = choice.get('choiceId', '')
            
            # If choice is just 1-2 words and they're verb forms, it's wrong
            words = choice_text.split()
            if len(words) <= 2:
                # Check if it's just a verb form
                verb_forms = ['is', 'are', 'was', 'were', 'be', 'been', 'being', 'has', 'have', 'had', 
                             'will', 'would', 'can', 'could', 'should', 'must', 'may', 'might']
                if choice_text.lower() in verb_forms or (len(words) == 2 and words[0].lower() in verb_forms):
                    issues.append({
                        'type': 'transformation_verb_form_only',
                        'question_id': q_id,
                        'choice_id': choice_id,
                        'choice_text': choice_text,
                        'prompt': prompt,
                        'issue': 'Transformation question has choice that is just a verb form, not a complete transformed sentence'
                    })
    
    # Check 3: Check if choices semantically don't match the prompt
    # For gap_fill: choices should be able to fill the blank grammatically
    if q_type == 'gap_fill':
        blank_match = re.search(r"Fill in the blank:\s*['\"](.*?)['\"]", prompt, re.IGNORECASE)
        if blank_match:
            sentence_with_blank = blank_match.group(1)
            blank_pos = sentence_with_blank.find('_____')
            if blank_pos == -1:
                blank_pos = sentence_with_blank.find('____')
            if blank_pos == -1:
                blank_pos = sentence_with_blank.find('___')
            
            if blank_pos >= 0:
                # Get context before and after blank
                before_blank = sentence_with_blank[:blank_pos].strip().lower()
                after_blank = sentence_with_blank[blank_pos:].replace('_____', '').replace('____', '').replace('___', '').strip().lower()
                
                for choice in choices:
                    choice_text = choice.get('text', '').strip()
                    choice_id = choice.get('choiceId', '')
                    
                    # If choice is a full sentence, check if it makes sense in context
                    if len(choice_text.split()) >= 4:
                        # Check if choice starts with article (a, an, the) - suggests it's a new sentence, not filling blank
                        if choice_text.lower().startswith(('a ', 'an ', 'the ')):
                            # This is likely wrong - should be a word/phrase, not a new sentence
                            issues.append({
                                'type': 'gap_fill_new_sentence',
                                'question_id': q_id,
                                'choice_id': choice_id,
                                'choice_text': choice_text,
                                'prompt': prompt,
                                'before_blank': before_blank,
                                'after_blank': after_blank,
                                'issue': f'Choice starts with article, suggesting it\'s a new sentence rather than filling the blank. Context: "...{before_blank[-20:]}_____{after_blank[:20]}..."'
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
    print('COMPREHENSIVE CHOICE MISMATCH DETECTION')
    print('=' * 80)
    print(f'\nTotal questions: {len(all_questions)}\n')
    
    all_issues = []
    issues_by_type = {}
    
    for question in all_questions:
        issues = analyze_question(question)
        all_issues.extend(issues)
        
        for issue in issues:
            issue_type = issue['type']
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)
    
    # Print results
    print(f'🔴 Total issues found: {len(all_issues)}\n')
    
    for issue_type, issues in issues_by_type.items():
        print(f'\n{issue_type.replace("_", " ").title()} ({len(issues)} issues):')
        print('-' * 80)
        
        for issue in issues[:15]:  # Show first 15
            print(f'\n  Question ID: {issue["question_id"]}')
            print(f'  Choice {issue["choice_id"]}: "{issue["choice_text"][:60]}..."')
            print(f'  Prompt: {issue["prompt"][:70]}...')
            print(f'  Issue: {issue["issue"]}')
            if 'word_count' in issue:
                print(f'  Word count: {issue["word_count"]}')
        
        if len(issues) > 15:
            print(f'\n  ... and {len(issues) - 15} more issues of this type')
    
    # Save to file
    output_file = Path('choice_mismatch_report.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_issues': len(all_issues),
            'issues_by_type': {k: len(v) for k, v in issues_by_type.items()},
            'all_issues': all_issues,
        }, f, indent=2, ensure_ascii=False)
    
    print(f'\n\n✅ Full report saved to {output_file}')
    
    if all_issues:
        print('\n⚠️  ACTION REQUIRED:')
        print('   Please review and fix the issues found above.')
        print('   For gap_fill questions: Choices should be single words/phrases, not full sentences.')
        print('   For transformation questions: Choices should be complete transformed sentences, not just verb forms.')
    else:
        print('\n✅ No issues found!')

if __name__ == '__main__':
    main()

