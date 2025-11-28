#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Review Gap Fill and Transformation Questions
Shows all gap_fill and transformation questions for manual review
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def review_questions():
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
    print('GAP FILL AND TRANSFORMATION QUESTIONS REVIEW')
    print('=' * 80)
    
    gap_fill_questions = []
    transformation_questions = []
    
    for question in all_questions:
        q_type = question.get('type', '')
        prompt = question.get('prompt', '').lower()
        
        if q_type == 'gap_fill':
            gap_fill_questions.append(question)
        
        # Check for transformation keywords
        if any(keyword in prompt for keyword in ['change', 'transform', 'convert', 'rewrite', 'rephrase']):
            transformation_questions.append(question)
    
    print(f'\n📝 GAP FILL QUESTIONS ({len(gap_fill_questions)} total)\n')
    print('=' * 80)
    
    for i, question in enumerate(gap_fill_questions, 1):
        print(f'\n{i}. Question ID: {question.get("id")}')
        print(f'   File: {question.get("_source_file")}')
        print(f'   Prompt: {question.get("prompt")}')
        print(f'   Choices:')
        for choice in question.get('choices', []):
            choice_id = choice.get('choiceId', '')
            choice_text = choice.get('text', '')
            is_correct = '✓' if choice.get('isCorrect') else ' '
            word_count = len(choice_text.split())
            print(f'     {is_correct} {choice_id}. "{choice_text}" ({word_count} words)')
        print()
    
    print(f'\n🔄 TRANSFORMATION QUESTIONS ({len(transformation_questions)} total)\n')
    print('=' * 80)
    
    for i, question in enumerate(transformation_questions, 1):
        print(f'\n{i}. Question ID: {question.get("id")}')
        print(f'   File: {question.get("_source_file")}')
        print(f'   Prompt: {question.get("prompt")}')
        print(f'   Choices:')
        for choice in question.get('choices', []):
            choice_id = choice.get('choiceId', '')
            choice_text = choice.get('text', '')
            is_correct = '✓' if choice.get('isCorrect') else ' '
            word_count = len(choice_text.split())
            print(f'     {is_correct} {choice_id}. "{choice_text}" ({word_count} words)')
        print()
    
    # Save to file for easier review
    review_data = {
        'gap_fill_questions': gap_fill_questions,
        'transformation_questions': transformation_questions,
    }
    
    output_file = Path('question_review_report.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(review_data, f, indent=2, ensure_ascii=False)
    
    print(f'\n✅ Review data saved to {output_file}')
    print('\n📋 MANUAL CHECKLIST:')
    print('   For each gap_fill question:')
    print('   □ Choices should be 1-3 words (not full sentences)')
    print('   □ Choices should make sense in the blank context')
    print('   □ No choices starting with articles (a, an, the) unless it\'s a phrase like "a lot"')
    print('\n   For each transformation question:')
    print('   □ Choices should be complete transformed sentences (4+ words)')
    print('   □ No choices that are just verb forms (is, are, was, were, etc.)')
    print('   □ Choices should show the actual transformation requested')

if __name__ == '__main__':
    review_questions()

