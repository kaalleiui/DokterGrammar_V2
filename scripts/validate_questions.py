#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Question validation script (Python version)
Validates question bank integrity and reports all issues
Matches the logic from scripts/validate_questions.dart

Usage: python validate_questions.py
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

class QuestionValidator:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.total_questions = 0
        self.valid_questions = 0
        self.invalid_questions = 0
    
    def validate_question_bank(self, file_path: Path):
        print(f'\n📋 Validating: {file_path}')
        print('─' * 60)
        
        if not file_path.exists():
            self.errors.append(f'File not found: {file_path}')
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            if not isinstance(json_data, list):
                self.errors.append(f'Invalid format: expected list, got {type(json_data).__name__}')
                return
            
            for i, question_json in enumerate(json_data):
                self.total_questions += 1
                self.validate_question(question_json, i + 1)
        except json.JSONDecodeError as e:
            self.errors.append(f'Error reading {file_path}: JSON decode error: {e}')
        except Exception as e:
            self.errors.append(f'Error reading {file_path}: {e}')
    
    def validate_question(self, question: Dict[str, Any], index: int):
        question_id = question.get('id', 'unknown')
        is_valid = True
        
        # Check required fields
        if 'id' not in question or not question['id']:
            self.errors.append(f'Question #{index}: Missing required field "id"')
            is_valid = False
        
        if 'type' not in question or not question['type']:
            self.errors.append(f'Question #{index} ({question_id}): Missing required field "type"')
            is_valid = False
        
        if 'answer' not in question or question['answer'] is None:
            self.errors.append(f'Question #{index} ({question_id}): Missing required field "answer"')
            is_valid = False
        
        question_type = question.get('type', '')
        if 'choices' not in question and question_type != 'short_answer':
            self.errors.append(f'Question #{index} ({question_id}): Missing required field "choices"')
            is_valid = False
        
        # Validate answer matches isCorrect flag
        if 'choices' in question and question['choices'] and 'answer' in question and question['answer'] is not None:
            choices = question['choices']
            answer = str(question['answer'])
            
            # Find choices with isCorrect: true
            correct_choices = [c for c in choices if c.get('isCorrect') is True]
            
            # Find choice with matching choiceId
            matching_choice = None
            for c in choices:
                if c.get('choiceId') == answer:
                    matching_choice = c
                    break
            
            if len(correct_choices) == 0:
                self.errors.append(
                    f'Question #{index} ({question_id}): No choice has isCorrect: true'
                )
                is_valid = False
            elif len(correct_choices) > 1:
                self.errors.append(
                    f'Question #{index} ({question_id}): Multiple choices have isCorrect: true ({len(correct_choices)} found)'
                )
                is_valid = False
            else:
                # Check if answer field matches the correct choice
                correct_choice = correct_choices[0]
                correct_choice_id = str(correct_choice.get('choiceId', ''))
                
                if question_type == 'gap_fill':
                    # For gap_fill, answer might be text or choiceId
                    correct_choice_text = str(correct_choice.get('text', '')).strip()
                    if answer != correct_choice_id and answer != correct_choice_text:
                        self.warnings.append(
                            f'Question #{index} ({question_id}): Gap fill answer "{answer}" doesn\'t match correct choiceId "{correct_choice_id}" or text "{correct_choice_text}"'
                        )
                else:
                    # For other types, answer should match choiceId
                    if answer != correct_choice_id:
                        self.errors.append(
                            f'Question #{index} ({question_id}): Answer field "{answer}" doesn\'t match correct choiceId "{correct_choice_id}"'
                        )
                        is_valid = False
                
                # Check if matching choice exists
                if matching_choice is None and question_type != 'gap_fill':
                    self.warnings.append(
                        f'Question #{index} ({question_id}): Answer "{answer}" doesn\'t match any choiceId'
                    )
        
        # Validate explanation template
        if 'explanationTemplate' in question and question['explanationTemplate']:
            template = str(question['explanationTemplate']).strip()
            if not template:
                self.warnings.append(f'Question #{index} ({question_id}): Empty explanation template')
        
        # Validate example sentence
        if 'exampleSentence' in question and question['exampleSentence']:
            example = str(question['exampleSentence']).strip()
            if not example:
                self.warnings.append(f'Question #{index} ({question_id}): Empty example sentence')
        
        if is_valid:
            self.valid_questions += 1
        else:
            self.invalid_questions += 1
    
    def print_report(self):
        print('\n' + '=' * 60)
        print('📊 VALIDATION REPORT')
        print('=' * 60)
        print(f'Total Questions: {self.total_questions}')
        print(f'✅ Valid Questions: {self.valid_questions}')
        print(f'❌ Invalid Questions: {self.invalid_questions}')
        print(f'⚠️  Warnings: {len(self.warnings)}')
        print(f'🔴 Errors: {len(self.errors)}')
        print('=' * 60)
        
        if self.warnings:
            print(f'\n⚠️  WARNINGS ({len(self.warnings)}):')
            print('─' * 60)
            for warning in self.warnings[:50]:  # Show first 50
                print(f'  • {warning}')
            if len(self.warnings) > 50:
                print(f'  ... and {len(self.warnings) - 50} more warnings')
        
        if self.errors:
            print(f'\n🔴 ERRORS ({len(self.errors)}):')
            print('─' * 60)
            for error in self.errors:
                print(f'  • {error}')
        
        if not self.errors and not self.warnings:
            print('\n✅ All questions are valid!')
        elif not self.errors:
            print('\n✅ No critical errors found, but please review warnings.')
        else:
            print('\n❌ CRITICAL ERRORS FOUND - Please fix before presentation!')

def main():
    print('🔍 Question Bank Validator')
    print('=' * 60)
    
    validator = QuestionValidator()
    
    # Validate all question bank files
    assets_dir = Path('assets/data')
    question_banks = [
        assets_dir / 'question_bank.json',
        assets_dir / 'question_bank1.json',
        assets_dir / 'question_bank2.json',
        assets_dir / 'question_bank3.json',
    ]
    
    for bank in question_banks:
        validator.validate_question_bank(bank)
    
    # Print final report
    validator.print_report()
    
    # Exit with error code if critical errors found
    exit(1 if validator.errors else 0)

if __name__ == '__main__':
    main()

