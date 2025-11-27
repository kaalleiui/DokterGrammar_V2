#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Real Answer Extraction - Test with actual question IDs from the database
"""

import json
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def test_extraction_with_real_ids():
    """Test extraction with real question IDs that contain underscores"""
    
    # Load a sample question
    assets_dir = Path('assets/data')
    file_path = assets_dir / 'question_bank1.json'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    print('=' * 70)
    print('TESTING EXTRACTION WITH REAL QUESTION IDs')
    print('=' * 70)
    
    issues = []
    
    for question in questions[:10]:  # Test first 10
        q_id = question.get('id', '')
        choices = question.get('choices', [])
        
        if not choices:
            continue
        
        print(f'\nQuestion: {q_id}')
        print(f'  Question ID parts: {q_id.split("_")}')
        
        for choice in choices:
            choice_id = choice.get('choiceId', '')
            if not choice_id:
                continue
            
            # Simulate the unique value format used in test_screen.dart
            # Format: questionId_choiceId_index
            unique_value = f"{q_id}_{choice_id}_0"
            print(f'  Choice ID: {choice_id}')
            print(f'  Unique value: {unique_value}')
            
            # Current extraction logic (from test_screen.dart line 235)
            parts = unique_value.split('_')
            if len(parts) >= 2:
                extracted = parts[len(parts) - 2]  # Second-to-last element
                print(f'  Extracted (current logic): {extracted}')
                
                if extracted.lower() != choice_id.lower():
                    issues.append({
                        'question': q_id,
                        'choice_id': choice_id,
                        'extracted': extracted,
                        'unique_value': unique_value,
                        'parts': parts
                    })
                    print(f'  ❌ MISMATCH! Expected: {choice_id}, Got: {extracted}')
                else:
                    print(f'  ✅ Match!')
    
    print('\n' + '=' * 70)
    if issues:
        print(f'❌ Found {len(issues)} extraction mismatches!')
        print('\nIssues:')
        for issue in issues:
            print(f"  • {issue['question']}: Expected '{issue['choice_id']}', got '{issue['extracted']}'")
            print(f"    Unique value: {issue['unique_value']}")
            print(f"    Parts: {issue['parts']}")
    else:
        print('✅ No extraction mismatches found in sample!')
    print('=' * 70)

if __name__ == '__main__':
    test_extraction_with_real_ids()

