#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Answer Matching - Find mismatches between questions and answers
Simulates the actual answer extraction and scoring logic
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

class AnswerMatchingTester:
    def __init__(self):
        self.questions: List[Dict[str, Any]] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def load_questions(self):
        """Load all questions"""
        assets_dir = Path('assets/data')
        bank_files = [
            'question_bank.json',
            'question_bank1.json',
            'question_bank2.json',
            'question_bank3.json',
        ]
        
        for bank_file in bank_files:
            file_path = assets_dir / bank_file
            if not file_path.exists():
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.questions.extend(data)
            except Exception as e:
                print(f'Error loading {bank_file}: {e}')
    
    def extract_choice_id(self, unique_value: str, question: Dict[str, Any]) -> str:
        """
        Extract choiceId from unique value format: questionId_choiceId_index
        This simulates the logic in test_screen.dart line 228-237
        """
        if not unique_value or '_' not in unique_value:
            return unique_value
        
        parts = unique_value.split('_')
        if len(parts) < 3:
            return unique_value
        
        # Current logic (WRONG): Get second-to-last element
        # This fails when questionId contains underscores
        current_logic_choice_id = parts[len(parts) - 2]
        
        # CORRECT logic: Find which part matches a choiceId
        choices = question.get('choices', [])
        choice_ids = [c.get('choiceId', '').lower() for c in choices]
        
        # Check if current logic is correct
        if current_logic_choice_id.lower() in choice_ids:
            return current_logic_choice_id
        
        # If current logic fails, find the correct choiceId
        for part in reversed(parts):
            if part.lower() in choice_ids:
                return part
        
        # Fallback: return second-to-last (current behavior)
        return current_logic_choice_id
    
    def is_answer_correct(self, question: Dict[str, Any], user_answer: str) -> bool:
        """
        Simulate ScoringService.isAnswerCorrect() logic
        """
        if not user_answer:
            return False
        
        q_type = question.get('type', '')
        answer = str(question.get('answer', '')).lower().strip()
        user_answer_lower = user_answer.lower().strip()
        choices = question.get('choices', [])
        
        if q_type == 'multiple_choice':
            # For multiple_choice, answer should be choiceId
            return answer == user_answer_lower
        
        elif q_type == 'gap_fill':
            if choices:
                # Check if userAnswer is a choiceId
                user_choice = None
                for c in choices:
                    if c.get('choiceId', '').lower() == user_answer_lower:
                        user_choice = c
                        break
                
                if user_choice:
                    # User selected a choice
                    # Check if answer field is choiceId or text
                    answer_is_choice_id = any(
                        c.get('choiceId', '').lower() == answer
                        for c in choices
                    )
                    
                    if answer_is_choice_id:
                        # Answer is choiceId, compare choiceIds
                        return answer == user_answer_lower
                    else:
                        # Answer is text, get correct choice by isCorrect flag
                        correct_choice = next(
                            (c for c in choices if c.get('isCorrect') is True),
                            None
                        )
                        if correct_choice:
                            # Compare user's choice text with correct choice text
                            return (
                                user_choice.get('text', '').lower().strip() ==
                                correct_choice.get('text', '').lower().strip()
                            )
                        else:
                            # Fallback
                            return answer == user_choice.get('text', '').lower().strip()
                else:
                    # UserAnswer is not a choiceId, treat as text
                    return answer == user_answer_lower
            else:
                # No choices, direct comparison
                return answer == user_answer_lower
        
        else:
            # Default: direct comparison
            return answer == user_answer_lower
    
    def test_answer_extraction(self):
        """Test answer extraction logic"""
        print('=' * 70)
        print('TESTING ANSWER EXTRACTION LOGIC')
        print('=' * 70)
        
        issues = 0
        
        for question in self.questions:
            q_id = question.get('id', 'unknown')
            q_type = question.get('type', '')
            choices = question.get('choices', [])
            
            if not choices or q_type not in ['multiple_choice', 'gap_fill']:
                continue
            
            # Test each choice
            for choice in choices:
                choice_id = choice.get('choiceId', '')
                if not choice_id:
                    continue
                
                # Simulate unique value format: questionId_choiceId_index
                # Example: "q_tenses_001_a_0"
                unique_value = f"{q_id}_{choice_id}_0"
                
                # Extract choiceId using current logic
                extracted = self.extract_choice_id(unique_value, question)
                
                # Check if extraction is correct
                if extracted.lower() != choice_id.lower():
                    self.errors.append(
                        f"{q_id}: Extracted '{extracted}' but should be '{choice_id}' "
                        f"(unique_value: {unique_value})"
                    )
                    issues += 1
        
        print(f'\n📊 Results:')
        print(f'   Questions tested: {len(self.questions)}')
        print(f'   Extraction issues: {issues}')
        
        if issues > 0:
            print(f'\n❌ Found {issues} extraction issues!')
            print('\nFirst 20 issues:')
            for error in self.errors[:20]:
                print(f'  • {error}')
            if len(self.errors) > 20:
                print(f'  ... and {len(self.errors) - 20} more')
        else:
            print(f'\n✅ No extraction issues found!')
        
        return issues == 0
    
    def test_scoring_with_extraction(self):
        """Test scoring after answer extraction"""
        print('\n' + '=' * 70)
        print('TESTING SCORING AFTER EXTRACTION')
        print('=' * 70)
        
        issues = 0
        
        for question in self.questions:
            q_id = question.get('id', 'unknown')
            q_type = question.get('type', '')
            choices = question.get('choices', [])
            correct_answer = question.get('answer', '')
            
            if not choices or q_type not in ['multiple_choice', 'gap_fill']:
                continue
            
            # Find correct choice
            correct_choice = next(
                (c for c in choices if c.get('isCorrect') is True),
                None
            )
            
            if not correct_choice:
                continue
            
            correct_choice_id = correct_choice.get('choiceId', '')
            
            # Simulate user selecting correct answer
            # Create unique value format
            unique_value = f"{q_id}_{correct_choice_id}_0"
            
            # Extract choiceId (simulating test_screen.dart)
            extracted = self.extract_choice_id(unique_value, question)
            
            # Test scoring with extracted answer
            is_correct = self.is_answer_correct(question, extracted)
            
            if not is_correct:
                self.errors.append(
                    f"{q_id}: Correct answer '{correct_choice_id}' extracted as '{extracted}' "
                    f"but marked as incorrect!"
                )
                issues += 1
        
        print(f'\n📊 Results:')
        print(f'   Questions tested: {len(self.questions)}')
        print(f'   Scoring issues: {issues}')
        
        if issues > 0:
            print(f'\n❌ Found {issues} scoring issues!')
            print('\nFirst 20 issues:')
            for error in self.errors[:20]:
                print(f'  • {error}')
            if len(self.errors) > 20:
                print(f'  ... and {len(self.errors) - 20} more')
        else:
            print(f'\n✅ No scoring issues found!')
        
        return issues == 0
    
    def run_all_tests(self):
        """Run all tests"""
        print('🔍 Answer Matching Tester')
        print('=' * 70)
        
        self.load_questions()
        print(f'\nLoaded {len(self.questions)} questions\n')
        
        # Run tests
        test1_passed = self.test_answer_extraction()
        test2_passed = self.test_scoring_with_extraction()
        
        print('\n' + '=' * 70)
        if test1_passed and test2_passed:
            print('✅ ALL TESTS PASSED')
        else:
            print('❌ TESTS FAILED - Issues found')
        print('=' * 70)
        
        return test1_passed and test2_passed

if __name__ == '__main__':
    tester = AnswerMatchingTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)

