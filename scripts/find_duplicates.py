#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Find duplicate question IDs across question bank files
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def find_duplicates():
    """Find all duplicate question IDs"""
    assets_dir = Path('assets/data')
    bank_files = [
        'question_bank.json',
        'question_bank1.json',
        'question_bank2.json',
        'question_bank3.json',
    ]
    
    # Track which files contain which question IDs
    question_locations = defaultdict(list)
    all_questions = {}
    
    for bank_file in bank_files:
        file_path = assets_dir / bank_file
        if not file_path.exists():
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for question in data:
                        q_id = question.get('id')
                        if q_id:
                            question_locations[q_id].append(bank_file)
                            # Store question with file info
                            if q_id not in all_questions:
                                all_questions[q_id] = []
                            all_questions[q_id].append({
                                'file': bank_file,
                                'question': question
                            })
        except Exception as e:
            print(f'Error loading {bank_file}: {e}')
    
    # Find duplicates
    duplicates = {q_id: files for q_id, files in question_locations.items() if len(files) > 1}
    
    print('=' * 70)
    print('DUPLICATE QUESTION ID ANALYSIS')
    print('=' * 70)
    print(f'\nTotal unique question IDs: {len(question_locations)}')
    print(f'Duplicate question IDs: {len(duplicates)}\n')
    
    if duplicates:
        print('Duplicate IDs by file:')
        print('─' * 70)
        
        # Group by file pairs
        file_duplicates = defaultdict(set)
        for q_id, files in duplicates.items():
            for file in files:
                file_duplicates[file].add(q_id)
        
        for bank_file in bank_files:
            if bank_file in file_duplicates:
                print(f'\n{bank_file}: {len(file_duplicates[bank_file])} duplicate IDs')
        
        # Show first 20 duplicates
        print('\n' + '=' * 70)
        print('SAMPLE DUPLICATES (first 20):')
        print('=' * 70)
        for i, (q_id, files) in enumerate(list(duplicates.items())[:20], 1):
            print(f'\n{i}. {q_id} appears in: {", ".join(files)}')
            # Show which version might be different
            questions = all_questions[q_id]
            if len(questions) > 1:
                # Check if they're identical
                first_q = json.dumps(questions[0]['question'], sort_keys=True)
                all_same = all(
                    json.dumps(q['question'], sort_keys=True) == first_q
                    for q in questions[1:]
                )
                if all_same:
                    print(f'   → All versions are identical')
                else:
                    print(f'   → ⚠️  Versions differ!')
                    for q_info in questions:
                        q = q_info['question']
                        prompt = q.get('prompt', '')[:50]
                        answer = q.get('answer', '')
                        print(f'      - {q_info["file"]}: answer="{answer}", prompt="{prompt}..."')
    
    return duplicates, all_questions

if __name__ == '__main__':
    duplicates, all_questions = find_duplicates()
    
    print('\n' + '=' * 70)
    print('RECOMMENDATION:')
    print('=' * 70)
    print('Keep questions from newer files (question_bank3.json, question_bank2.json, etc.)')
    print('Remove duplicates from older files (question_bank.json, question_bank1.json)')
    print('This ensures we keep the most recent versions of questions.')

