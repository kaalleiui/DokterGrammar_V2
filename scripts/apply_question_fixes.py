#!/usr/bin/env python3
"""
Apply fixes to question bank files based on validation report
"""

import json
from pathlib import Path
from collections import defaultdict

def load_validation_report():
    """Load validation report"""
    report_path = Path("question_validation_report.json")
    if not report_path.exists():
        print("[ERROR] Validation report not found. Run ai_question_validator.py first.")
        return None
    
    with open(report_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_question_banks():
    """Load all question bank files"""
    assets_dir = Path("assets/data")
    bank_files = {
        'question_bank.json': assets_dir / 'question_bank.json',
        'question_bank1.json': assets_dir / 'question_bank1.json',
        'question_bank2.json': assets_dir / 'question_bank2.json',
        'question_bank3.json': assets_dir / 'question_bank3.json',
    }
    
    loaded = {}
    for name, path in bank_files.items():
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        loaded[name] = data
            except Exception as e:
                print(f"[WARN] Error loading {name}: {e}")
    
    return loaded

def find_question_in_banks(question_id, banks):
    """Find which bank file contains the question"""
    for bank_name, questions in banks.items():
        for i, question in enumerate(questions):
            if question.get('id') == question_id:
                return bank_name, i, question
    return None, None, None

def apply_fixes(dry_run=True):
    """Apply fixes to question banks"""
    print("=" * 60)
    print("Applying Question Fixes")
    print("=" * 60)
    
    if dry_run:
        print("\n[INFO] DRY RUN MODE - No files will be modified")
    
    report = load_validation_report()
    if not report:
        return False
    
    fixes = report.get('fixes', [])
    if not fixes:
        print("\n✅ No fixes to apply")
        return True
    
    banks = load_question_banks()
    if not banks:
        print("[ERROR] No question banks loaded")
        return False
    
    applied = 0
    failed = 0
    
    print(f"\n[INFO] Applying {len(fixes)} fixes...")
    
    for fix in fixes:
        question_id = fix['question_id']
        fix_data = fix['fix']
        issue_type = fix['issue_type']
        
        bank_name, index, question = find_question_in_banks(question_id, banks)
        
        if question is None:
            print(f"[WARN] Question {question_id} not found in any bank")
            failed += 1
            continue
        
        # Apply fix
        if issue_type == 'answer_mismatch':
            if 'answer' in fix_data:
                old_answer = question.get('answer', '')
                question['answer'] = fix_data['answer']
                print(f"  [{question_id}] Fixed answer: {old_answer} → {fix_data['answer']}")
                applied += 1
        
        elif issue_type == 'gap_fill_mismatch':
            if 'answer' in fix_data:
                old_answer = question.get('answer', '')
                question['answer'] = fix_data['answer']
                print(f"  [{question_id}] Fixed gap_fill answer: {old_answer} → {fix_data['answer']}")
                applied += 1
        
        elif issue_type == 'no_correct_marked':
            if 'mark_correct' in fix_data and fix_data['mark_correct']:
                choice_id = fix_data['mark_correct']
                for choice in question.get('choices', []):
                    if choice.get('choiceId', '').lower() == choice_id.lower():
                        choice['isCorrect'] = True
                        print(f"  [{question_id}] Marked {choice_id} as correct")
                        applied += 1
                        break
        
        elif issue_type == 'multiple_correct':
            if 'keep_correct' in fix_data and fix_data['keep_correct']:
                keep_id = fix_data['keep_correct'].lower()
                for choice in question.get('choices', []):
                    choice['isCorrect'] = (choice.get('choiceId', '').lower() == keep_id)
                print(f"  [{question_id}] Fixed multiple correct choices")
                applied += 1
    
    # Save fixed banks
    if not dry_run and applied > 0:
        print(f"\n[INFO] Saving fixed question banks...")
        for bank_name, questions in banks.items():
            bank_path = Path("assets/data") / bank_name
            with open(bank_path, 'w', encoding='utf-8') as f:
                json.dump(questions, f, ensure_ascii=False, indent=2)
            print(f"  [OK] Saved {bank_name}")
    
    print("\n" + "=" * 60)
    print(f"Applied: {applied}")
    print(f"Failed: {failed}")
    print("=" * 60)
    
    if dry_run:
        print("\n[INFO] This was a dry run. Use --apply to actually fix files:")
        print("  python apply_question_fixes.py --apply")
    
    return True

if __name__ == "__main__":
    import sys
    dry_run = '--apply' not in sys.argv
    
    if apply_fixes(dry_run=dry_run):
        print("\n✅ Fix application complete!")
    else:
        print("\n❌ Fix application failed!")

