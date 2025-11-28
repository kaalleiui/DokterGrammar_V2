#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validate and Fix Choice Mismatches
Comprehensive validator that finds and can auto-fix common issues
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

class ChoiceValidator:
    def __init__(self):
        self.issues = []
        self.fixes = []
    
    def validate_gap_fill_choice(self, question: Dict[str, Any], choice: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate that a gap_fill choice is appropriate (word/phrase, not full sentence)"""
        prompt = question.get('prompt', '')
        choice_text = choice.get('text', '').strip()
        
        # Extract sentence with blank
        blank_match = re.search(r"Fill in the blank:\s*['\"](.*?)['\"]", prompt, re.IGNORECASE)
        if not blank_match:
            return True, ""  # Can't validate without blank pattern
        
        sentence_with_blank = blank_match.group(1)
        word_count = len(choice_text.split())
        
        # Rule 1: Choice should not be a full sentence (5+ words)
        if word_count >= 5:
            # Check if it's a complete sentence
            if choice_text[0].isupper() and (choice_text[-1] in '.!?' or word_count >= 6):
                return False, f"Choice has {word_count} words and appears to be a full sentence. Gap fill choices should be single words or short phrases (1-3 words)."
        
        # Rule 2: Choice should not start with article (a, an, the) unless it's a phrase like "a lot"
        if word_count >= 4 and choice_text.lower().startswith(('a ', 'an ', 'the ')):
            # Check if it's a common phrase
            common_phrases = ['a lot', 'a few', 'a little', 'a bit', 'the same', 'the most', 'the least']
            if not any(choice_text.lower().startswith(phrase) for phrase in common_phrases):
                return False, f"Choice starts with article '{choice_text.split()[0]}' and has {word_count} words. This suggests it's a new sentence, not filling the blank."
        
        # Rule 3: Choice should make grammatical sense in the blank context
        # This is harder to validate automatically, but we can check basic patterns
        
        return True, ""
    
    def validate_transformation_choice(self, question: Dict[str, Any], choice: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate that a transformation question choice is a complete sentence"""
        prompt = question.get('prompt', '').lower()
        choice_text = choice.get('text', '').strip()
        
        # Check if it's a transformation question
        is_transformation = any(keyword in prompt for keyword in [
            'change', 'transform', 'convert', 'rewrite', 'rephrase', 'change this', 'change into'
        ])
        
        if not is_transformation:
            return True, ""
        
        words = choice_text.split()
        word_count = len(words)
        
        # Rule: Transformation choices should be complete sentences (typically 4+ words)
        if word_count <= 2:
            # Check if it's just a verb form
            verb_forms = ['is', 'are', 'was', 'were', 'be', 'been', 'being', 'has', 'have', 'had', 
                         'will', 'would', 'can', 'could', 'should', 'must', 'may', 'might']
            if choice_text.lower() in verb_forms or (word_count == 2 and words[0].lower() in verb_forms):
                return False, f"Choice is just a verb form '{choice_text}'. Transformation questions should have complete transformed sentences."
        
        return True, ""
    
    def validate_question(self, question: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate a single question and return list of issues"""
        issues = []
        q_id = question.get('id', 'unknown')
        q_type = question.get('type', '')
        choices = question.get('choices', [])
        
        if not choices:
            return issues
        
        for choice in choices:
            choice_id = choice.get('choiceId', '')
            choice_text = choice.get('text', '').strip()
            
            # Validate based on question type
            if q_type == 'gap_fill':
                is_valid, error_msg = self.validate_gap_fill_choice(question, choice)
                if not is_valid:
                    issues.append({
                        'question_id': q_id,
                        'question_type': q_type,
                        'choice_id': choice_id,
                        'choice_text': choice_text,
                        'prompt': question.get('prompt', ''),
                        'error_type': 'gap_fill_invalid_choice',
                        'error_message': error_msg,
                        'severity': 'high',
                    })
            
            # Validate transformation questions
            is_valid, error_msg = self.validate_transformation_choice(question, choice)
            if not is_valid:
                issues.append({
                    'question_id': q_id,
                    'question_type': q_type,
                    'choice_id': choice_id,
                    'choice_text': choice_text,
                    'prompt': question.get('prompt', ''),
                    'error_type': 'transformation_invalid_choice',
                    'error_message': error_msg,
                    'severity': 'high',
                })
        
        return issues
    
    def scan_all_questions(self, fix_mode: bool = False) -> Dict[str, Any]:
        """Scan all question banks and validate choices"""
        assets_dir = Path('assets/data')
        bank_files = [
            'question_bank.json',
            'question_bank1.json',
            'question_bank2.json',
            'question_bank3.json',
        ]
        
        all_questions = []
        questions_by_file = {}
        
        for bank_file in bank_files:
            file_path = assets_dir / bank_file
            if not file_path.exists():
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        questions_by_file[bank_file] = data
                        for q in data:
                            q['_source_file'] = bank_file
                        all_questions.extend(data)
            except Exception as e:
                print(f'Error loading {bank_file}: {e}')
        
        print('=' * 80)
        print('CHOICE VALIDATION REPORT')
        print('=' * 80)
        print(f'\nTotal questions: {len(all_questions)}\n')
        
        all_issues = []
        issues_by_type = {}
        
        for question in all_questions:
            issues = self.validate_question(question)
            all_issues.extend(issues)
            
            for issue in issues:
                issue_type = issue['error_type']
                if issue_type not in issues_by_type:
                    issues_by_type[issue_type] = []
                issues_by_type[issue_type].append(issue)
        
        # Print results
        if all_issues:
            print(f'🔴 Found {len(all_issues)} issues:\n')
            
            for issue_type, issues in issues_by_type.items():
                print(f'\n{issue_type.replace("_", " ").title()} ({len(issues)} issues):')
                print('-' * 80)
                
                for issue in issues[:20]:  # Show first 20
                    print(f'\n  Question ID: {issue["question_id"]}')
                    print(f'  File: {question.get("_source_file", "unknown")}')
                    print(f'  Choice {issue["choice_id"]}: "{issue["choice_text"][:60]}..."')
                    print(f'  Prompt: {issue["prompt"][:70]}...')
                    print(f'  Error: {issue["error_message"]}')
                
                if len(issues) > 20:
                    print(f'\n  ... and {len(issues) - 20} more issues of this type')
        else:
            print('✅ No issues found! All choices are valid.')
        
        # Save detailed report
        report = {
            'total_questions': len(all_questions),
            'total_issues': len(all_issues),
            'issues_by_type': {k: len(v) for k, v in issues_by_type.items()},
            'all_issues': all_issues,
        }
        
        output_file = Path('choice_validation_report.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f'\n\n✅ Detailed report saved to {output_file}')
        
        return report

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Validate question choices')
    parser.add_argument('--fix', action='store_true', help='Attempt to auto-fix issues (not implemented yet)')
    args = parser.parse_args()
    
    validator = ChoiceValidator()
    report = validator.scan_all_questions(fix_mode=args.fix)
    
    if report['total_issues'] > 0:
        print('\n⚠️  ACTION REQUIRED:')
        print('   Please review the issues in choice_validation_report.json')
        print('   Fix questions where:')
        print('   - Gap fill choices are full sentences (should be 1-3 words)')
        print('   - Transformation choices are just verb forms (should be complete sentences)')
        return 1
    else:
        return 0

if __name__ == '__main__':
    exit(main())

