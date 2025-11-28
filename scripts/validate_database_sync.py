#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validate Database Sync
Checks if database questions match JSON files
Note: This requires database access, so it's a template for when you have DB access
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def load_all_questions_from_json() -> Dict[str, Dict[str, Any]]:
    """Load all questions from JSON files, indexed by ID"""
    assets_dir = Path('assets/data')
    bank_files = [
        'question_bank.json',
        'question_bank1.json',
        'question_bank2.json',
        'question_bank3.json',
    ]
    
    questions = {}
    for bank_file in bank_files:
        file_path = assets_dir / bank_file
        if not file_path.exists():
            continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for q in data:
                        q_id = q.get('id')
                        if q_id:
                            q['_source_file'] = bank_file
                            questions[q_id] = q
        except Exception as e:
            print(f'Error loading {bank_file}: {e}')
    
    return questions

def main():
    print('=' * 80)
    print('DATABASE SYNC VALIDATION')
    print('=' * 80)
    print('\nThis script validates that database questions match JSON files.')
    print('Note: Database access requires Flutter/Dart environment.')
    print('\nFor now, this shows all questions from JSON files.\n')
    
    json_questions = load_all_questions_from_json()
    
    print(f'📋 Loaded {len(json_questions)} questions from JSON files\n')
    
    # Show summary by file
    by_file = {}
    for q_id, q in json_questions.items():
        source = q.get('_source_file', 'unknown')
        if source not in by_file:
            by_file[source] = []
        by_file[source].append(q_id)
    
    print('Questions by file:')
    for source, q_ids in sorted(by_file.items()):
        print(f'  {source}: {len(q_ids)} questions')
    
    print('\n✅ To validate database sync:')
    print('   1. Export questions from database (if possible)')
    print('   2. Compare with JSON files')
    print('   3. Fix any mismatches in database')
    print('\n💡 Tip: If database has wrong data, reload from JSON files using:')
    print('   - QuestionBankLoader.loadQuestionsFromAssets()')
    print('   - QuestionLocalDataSource.insertQuestions()')
    
    # Save JSON questions for comparison
    output_file = Path('json_questions_reference.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_questions, f, indent=2, ensure_ascii=False)
    
    print(f'\n✅ JSON questions saved to {output_file} for reference')

if __name__ == '__main__':
    main()

