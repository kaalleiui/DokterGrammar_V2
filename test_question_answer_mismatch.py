#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Question-Answer Mismatch
Checks if questions and their choices/answers are correctly matched
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def test_question_answer_mismatches():
    """Test for mismatches between questions and answers"""
    
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
                    all_questions.extend(data)
        except Exception as e:
            print(f'Error loading {bank_file}: {e}')
    
    print('=' * 70)
    print('QUESTION-ANSWER MISMATCH DETECTION')
    print('=' * 70)
    print(f'\nTotal questions: {len(all_questions)}\n')
    
    issues = {
        'answer_not_in_choices': [],
        'multiple_correct_choices': [],
        'no_correct_choice': [],
        'answer_mismatch': [],
        'gap_fill_text_mismatch': [],
    }
    
    for question in all_questions:
        q_id = question.get('id', 'unknown')
        q_type = question.get('type', '')
        answer = question.get('answer', '')
        choices = question.get('choices', [])
        
        if not choices:
            continue
        
        # Check 1: Answer should be in choices (for multiple_choice and gap_fill with choices)
        if q_type in ['multiple_choice', 'gap_fill']:
            choice_ids = [c.get('choiceId', '').lower() for c in choices]
            choice_texts = [c.get('text', '').lower().strip() for c in choices]
            answer_lower = answer.lower().strip()
            
            # Check if answer matches a choiceId
            answer_in_choice_ids = answer_lower in choice_ids
            # Check if answer matches a choice text
            answer_in_choice_texts = answer_lower in choice_texts
            
            if not answer_in_choice_ids and not answer_in_choice_texts:
                issues['answer_not_in_choices'].append({
                    'id': q_id,
                    'type': q_type,
                    'answer': answer,
                    'choice_ids': choice_ids,
                    'choice_texts': choice_texts[:3],  # First 3
                })
        
        # Check 2: Only one choice should have isCorrect: true
        correct_choices = [c for c in choices if c.get('isCorrect') is True]
        if len(correct_choices) == 0:
            issues['no_correct_choice'].append({
                'id': q_id,
                'type': q_type,
            })
        elif len(correct_choices) > 1:
            issues['multiple_correct_choices'].append({
                'id': q_id,
                'type': q_type,
                'count': len(correct_choices),
            })
        else:
            # Check 3: Answer should match the correct choice
            correct_choice = correct_choices[0]
            correct_choice_id = correct_choice.get('choiceId', '').lower()
            correct_choice_text = correct_choice.get('text', '').lower().strip()
            answer_lower = answer.lower().strip()
            
            if q_type == 'multiple_choice':
                # For multiple_choice, answer should be choiceId
                if answer_lower != correct_choice_id:
                    issues['answer_mismatch'].append({
                        'id': q_id,
                        'type': q_type,
                        'answer': answer,
                        'correct_choice_id': correct_choice_id,
                        'correct_choice_text': correct_choice_text,
                    })
            elif q_type == 'gap_fill':
                # For gap_fill, answer can be choiceId or text
                if answer_lower != correct_choice_id and answer_lower != correct_choice_text:
                    issues['gap_fill_text_mismatch'].append({
                        'id': q_id,
                        'type': q_type,
                        'answer': answer,
                        'correct_choice_id': correct_choice_id,
                        'correct_choice_text': correct_choice_text,
                    })
    
    # Print results
    total_issues = sum(len(v) for v in issues.values())
    
    if total_issues == 0:
        print('✅ No mismatches found!')
    else:
        print(f'❌ Found {total_issues} issues:\n')
        
        if issues['answer_not_in_choices']:
            print(f'🔴 Answer not in choices ({len(issues["answer_not_in_choices"])}):')
            for issue in issues['answer_not_in_choices'][:10]:
                print(f'  • {issue["id"]}: Answer "{issue["answer"]}" not found in choices')
                print(f'    Choice IDs: {issue["choice_ids"]}')
            if len(issues['answer_not_in_choices']) > 10:
                print(f'  ... and {len(issues["answer_not_in_choices"]) - 10} more')
            print()
        
        if issues['no_correct_choice']:
            print(f'🔴 No correct choice ({len(issues["no_correct_choice"])}):')
            for issue in issues['no_correct_choice'][:10]:
                print(f'  • {issue["id"]}: No choice has isCorrect=true')
            if len(issues['no_correct_choice']) > 10:
                print(f'  ... and {len(issues["no_correct_choice"]) - 10} more')
            print()
        
        if issues['multiple_correct_choices']:
            print(f'🔴 Multiple correct choices ({len(issues["multiple_correct_choices"])}):')
            for issue in issues['multiple_correct_choices'][:10]:
                print(f'  • {issue["id"]}: {issue["count"]} choices have isCorrect=true')
            if len(issues['multiple_correct_choices']) > 10:
                print(f'  ... and {len(issues["multiple_correct_choices"]) - 10} more')
            print()
        
        if issues['answer_mismatch']:
            print(f'🔴 Answer mismatch ({len(issues["answer_mismatch"])}):')
            for issue in issues['answer_mismatch'][:10]:
                print(f'  • {issue["id"]}: Answer "{issue["answer"]}" != correct choiceId "{issue["correct_choice_id"]}"')
            if len(issues['answer_mismatch']) > 10:
                print(f'  ... and {len(issues["answer_mismatch"]) - 10} more')
            print()
        
        if issues['gap_fill_text_mismatch']:
            print(f'⚠️  Gap fill text mismatch ({len(issues["gap_fill_text_mismatch"])}):')
            for issue in issues['gap_fill_text_mismatch'][:10]:
                print(f'  • {issue["id"]}: Answer "{issue["answer"]}" != choiceId "{issue["correct_choice_id"]}" or text "{issue["correct_choice_text"]}"')
            if len(issues['gap_fill_text_mismatch']) > 10:
                print(f'  ... and {len(issues["gap_fill_text_mismatch"]) - 10} more')
            print()
    
    print('=' * 70)
    return total_issues == 0

if __name__ == '__main__':
    success = test_question_answer_mismatches()
    exit(0 if success else 1)

