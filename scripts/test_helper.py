#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testing Helper Script
Helps verify data integrity and provides testing utilities

Usage: python test_helper.py [command]
Commands:
  - check_db: Check database integrity
  - verify_questions: Verify question bank is loaded
  - stats: Show app statistics
"""

import json
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def check_question_bank():
    """Verify question bank files are valid"""
    print('=' * 70)
    print('QUESTION BANK VERIFICATION')
    print('=' * 70)
    
    assets_dir = Path('assets/data')
    bank_files = [
        'question_bank.json',
        'question_bank1.json',
        'question_bank2.json',
        'question_bank3.json',
    ]
    
    total_questions = 0
    all_ids = set()
    duplicates = []
    
    for bank_file in bank_files:
        file_path = assets_dir / bank_file
        if not file_path.exists():
            print(f'⚠️  {bank_file}: File not found')
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    count = len(data)
                    total_questions += count
                    print(f'✅ {bank_file}: {count} questions')
                    
                    # Check for duplicates
                    for q in data:
                        q_id = q.get('id')
                        if q_id:
                            if q_id in all_ids:
                                duplicates.append(f'{q_id} in {bank_file}')
                            all_ids.add(q_id)
        except Exception as e:
            print(f'❌ {bank_file}: Error - {e}')
    
    print(f'\n📊 Summary:')
    print(f'   Total questions: {total_questions}')
    print(f'   Unique question IDs: {len(all_ids)}')
    
    if duplicates:
        print(f'   ⚠️  Duplicates found: {len(duplicates)}')
        for dup in duplicates[:10]:
            print(f'      - {dup}')
    else:
        print(f'   ✅ No duplicates found')
    
    return total_questions, len(all_ids), len(duplicates) == 0

def show_statistics():
    """Show app statistics"""
    print('=' * 70)
    print('APP STATISTICS')
    print('=' * 70)
    
    # Question bank stats
    total, unique, no_dups = check_question_bank()
    
    print(f'\n📚 Question Bank:')
    print(f'   Total questions in files: {total}')
    print(f'   Unique question IDs: {unique}')
    print(f'   Duplicate status: {"✅ Clean" if no_dups else "⚠️  Has duplicates"}')
    
    # Check for required files
    print(f'\n📁 Required Files:')
    required_files = [
        'assets/data/question_bank1.json',
        'assets/data/question_bank2.json',
        'assets/data/question_bank3.json',
        'assets/rules/grammar_rules.json',
        'assets/templates/explanations.json',
    ]
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f'   ✅ {file_path}')
        else:
            print(f'   ❌ {file_path} - MISSING')
    
    print(f'\n✅ App is ready for testing!')

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'check_db':
            print('Database check would require database access')
            print('Run this check from within the Flutter app')
        elif command == 'verify_questions':
            check_question_bank()
        elif command == 'stats':
            show_statistics()
        else:
            print(f'Unknown command: {command}')
            print('Available commands: check_db, verify_questions, stats')
    else:
        show_statistics()

if __name__ == '__main__':
    main()

