#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remove duplicate questions from question bank files
Keeps questions from newer files, removes duplicates from older files
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def remove_duplicates():
    """Remove duplicate questions, keeping versions from newer files"""
    assets_dir = Path('assets/data')
    
    # Load files in order (newest to oldest)
    bank_files = [
        'question_bank3.json',
        'question_bank2.json',
        'question_bank1.json',
        'question_bank.json',
    ]
    
    # Track seen question IDs (keep first occurrence = newest file)
    seen_ids = set()
    all_unique_questions = []
    removed_count = defaultdict(int)
    
    print('=' * 70)
    print('REMOVING DUPLICATE QUESTIONS')
    print('=' * 70)
    print('\nProcessing files (newest to oldest)...\n')
    
    # First pass: collect all unique questions from newest files
    for bank_file in bank_files:
        file_path = assets_dir / bank_file
        if not file_path.exists():
            print(f'⚠️  {bank_file}: File not found, skipping')
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    print(f'⚠️  {bank_file}: Invalid format, skipping')
                    continue
            
            unique_in_file = []
            duplicates_in_file = 0
            
            for question in data:
                q_id = question.get('id')
                if not q_id:
                    # Keep questions without ID (shouldn't happen, but be safe)
                    unique_in_file.append(question)
                    continue
                
                if q_id in seen_ids:
                    # This is a duplicate, skip it
                    duplicates_in_file += 1
                    removed_count[bank_file] += 1
                else:
                    # First time seeing this ID, keep it
                    seen_ids.add(q_id)
                    unique_in_file.append(question)
            
            all_unique_questions.extend(unique_in_file)
            
            print(f'✅ {bank_file}:')
            print(f'   - Total questions: {len(data)}')
            print(f'   - Unique questions: {len(unique_in_file)}')
            print(f'   - Duplicates removed: {duplicates_in_file}')
            
        except Exception as e:
            print(f'❌ Error processing {bank_file}: {e}')
            continue
    
    print(f'\n📊 SUMMARY:')
    print(f'   - Total unique questions: {len(all_unique_questions)}')
    print(f'   - Total duplicates removed: {sum(removed_count.values())}')
    
    # Now update each file to only contain its unique questions
    print('\n' + '=' * 70)
    print('UPDATING FILES (removing duplicates)')
    print('=' * 70)
    
    # Reset seen_ids for file-by-file processing
    seen_ids = set()
    
    for bank_file in bank_files:
        file_path = assets_dir / bank_file
        if not file_path.exists():
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    continue
            
            # Keep only questions not seen in newer files
            unique_questions = []
            for question in data:
                q_id = question.get('id')
                if not q_id:
                    # Keep questions without ID
                    unique_questions.append(question)
                elif q_id not in seen_ids:
                    # First time seeing this ID, keep it
                    seen_ids.add(q_id)
                    unique_questions.append(question)
                # else: skip duplicate
            
            # Write back only unique questions
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(unique_questions, f, indent=2, ensure_ascii=False)
            
            removed = len(data) - len(unique_questions)
            print(f'✅ {bank_file}: {len(unique_questions)} questions kept, {removed} duplicates removed')
            
        except Exception as e:
            print(f'❌ Error updating {bank_file}: {e}')
            continue
    
    print('\n' + '=' * 70)
    print('✅ DUPLICATE REMOVAL COMPLETE')
    print('=' * 70)
    print('\nNext step: Run validation to verify all questions are still valid')

if __name__ == '__main__':
    # Ask for confirmation
    print('⚠️  WARNING: This will modify question bank files!')
    print('   Duplicate questions will be removed from older files.')
    print('   Questions from newer files will be kept.\n')
    
    response = input('Continue? (yes/no): ').strip().lower()
    if response in ['yes', 'y']:
        remove_duplicates()
    else:
        print('Cancelled.')

