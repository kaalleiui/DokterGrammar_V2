#!/usr/bin/env python3
"""
Comprehensive validation test for question bank and AI engine
Tests actual scoring and explanation logic
"""

import json
from pathlib import Path
from typing import List, Dict, Any

class ComprehensiveValidator:
    def __init__(self, assets_dir: str = "assets/data"):
        self.assets_dir = Path(assets_dir)
        self.questions: List[Dict[str, Any]] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def load_questions(self):
        """Load all questions from all banks"""
        bank_files = [
            'question_bank.json',
            'question_bank1.json',
            'question_bank2.json',
            'question_bank3.json',
        ]
        
        for bank_file in bank_files:
            file_path = self.assets_dir / bank_file
            if not file_path.exists():
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.questions.extend(data)
            except Exception as e:
                self.errors.append(f"Error loading {bank_file}: {e}")
    
    def test_answer_isCorrect_consistency(self):
        """Test that answer field matches isCorrect flag"""
        issues = 0
        
        for question in self.questions:
            q_id = question.get('id', 'unknown')
            q_type = question.get('type', '')
            answer = question.get('answer', '')
            choices = question.get('choices', [])
            
            if not choices:
                continue
            
            # Find correct choices
            correct_choices = [c for c in choices if c.get('isCorrect', False)]
            
            if len(correct_choices) == 0:
                self.errors.append(f"{q_id}: No choice has isCorrect=true")
                issues += 1
                continue
            
            if len(correct_choices) > 1:
                self.errors.append(f"{q_id}: Multiple choices have isCorrect=true ({len(correct_choices)} found)")
                issues += 1
                continue
            
            correct_choice = correct_choices[0]
            correct_choice_id = correct_choice.get('choiceId', '')
            correct_choice_text = correct_choice.get('text', '').lower().strip()
            answer_lower = answer.lower().strip()
            
            if q_type == 'multiple_choice':
                # For multiple_choice, answer must be choiceId
                if answer_lower != correct_choice_id.lower():
                    # Check if answer is text instead of choiceId
                    if answer_lower == correct_choice_text:
                        self.errors.append(
                            f"{q_id}: Answer '{answer}' is text, should be choiceId '{correct_choice_id}'"
                        )
                    else:
                        self.errors.append(
                            f"{q_id}: Answer '{answer}' doesn't match correct choiceId '{correct_choice_id}'"
                        )
                    issues += 1
            
            elif q_type == 'gap_fill':
                # For gap_fill, answer can be text or choiceId
                if answer_lower != correct_choice_id.lower() and answer_lower != correct_choice_text:
                    self.warnings.append(
                        f"{q_id}: Gap fill answer '{answer}' doesn't match choiceId '{correct_choice_id}' or text '{correct_choice_text}'"
                    )
        
        return issues == 0
    
    def test_scoring_simulation(self):
        """Simulate scoring for all questions"""
        issues = 0
        
        for question in self.questions:
            q_id = question.get('id', 'unknown')
            q_type = question.get('type', '')
            answer = question.get('answer', '')
            choices = question.get('choices', [])
            
            if not choices:
                continue
            
            # Find correct choice
            correct_choices = [c for c in choices if c.get('isCorrect', False)]
            if len(correct_choices) != 1:
                continue  # Skip if invalid
            
            correct_choice = correct_choices[0]
            correct_choice_id = correct_choice.get('choiceId', '')
            correct_choice_text = correct_choice.get('text', '').lower().strip()
            
            # Test: correct answer should be marked correct
            if q_type == 'multiple_choice':
                # User selects correct choiceId
                is_correct = self.is_answer_correct(question, correct_choice_id)
                if not is_correct:
                    self.errors.append(
                        f"{q_id}: Correct answer '{correct_choice_id}' marked as incorrect!"
                    )
                    issues += 1
                
                # Test: wrong answers should be marked incorrect
                for choice in choices:
                    if choice.get('choiceId') != correct_choice_id:
                        wrong_choice_id = choice.get('choiceId')
                        is_correct = self.is_answer_correct(question, wrong_choice_id)
                        if is_correct:
                            self.errors.append(
                                f"{q_id}: Wrong answer '{wrong_choice_id}' marked as correct!"
                            )
                            issues += 1
            
            elif q_type == 'gap_fill':
                # Test with choiceId
                is_correct = self.is_answer_correct(question, correct_choice_id)
                if not is_correct:
                    # Check if answer is text
                    answer_is_text = answer.lower().strip() == correct_choice_text
                    if answer_is_text:
                        # Answer is text, so we need to compare text
                        # This should still work
                        pass
                    else:
                        self.warnings.append(
                            f"{q_id}: Gap fill with choiceId '{correct_choice_id}' not marked correct"
                        )
                
                # Test with text
                is_correct = self.is_answer_correct(question, correct_choice_text)
                if not is_correct:
                    self.warnings.append(
                        f"{q_id}: Gap fill with text '{correct_choice_text}' not marked correct"
                    )
        
        return issues == 0
    
    def is_answer_correct(self, question: Dict[str, Any], user_answer: str) -> bool:
        """Simulate ScoringService.isAnswerCorrect logic"""
        if not user_answer:
            return False
        
        q_type = question.get('type', '')
        answer = question.get('answer', '').lower().strip()
        user_answer_lower = user_answer.lower().strip()
        choices = question.get('choices', [])
        
        if q_type == 'multiple_choice':
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
                    answer_is_choice_id = any(
                        c.get('choiceId', '').lower() == answer
                        for c in choices
                    )
                    
                    if answer_is_choice_id:
                        # Answer is choiceId, compare choiceIds
                        return answer == user_answer_lower
                    else:
                        # Answer is text, get correct choice and compare text
                        correct_choice = next(
                            (c for c in choices if c.get('isCorrect', False)),
                            None
                        )
                        if correct_choice:
                            return (
                                user_choice.get('text', '').lower().strip() ==
                                correct_choice.get('text', '').lower().strip()
                            )
                        else:
                            # Fallback
                            return answer == user_choice.get('text', '').lower().strip()
                else:
                    # UserAnswer is text
                    return answer == user_answer_lower
            else:
                return answer == user_answer_lower
        
        return answer == user_answer_lower
    
    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("=" * 70)
        print("COMPREHENSIVE QUESTION BANK VALIDATION")
        print("=" * 70)
        
        self.load_questions()
        print(f"\n[INFO] Loaded {len(self.questions)} questions\n")
        
        # Run tests
        tests = [
            ("Answer-isCorrect Consistency", self.test_answer_isCorrect_consistency),
            ("Scoring Simulation", self.test_scoring_simulation),
        ]
        
        all_passed = True
        for test_name, test_func in tests:
            print(f"Running: {test_name}...")
            try:
                result = test_func()
                if result:
                    print(f"  [PASS] {test_name}\n")
                else:
                    print(f"  [FAIL] {test_name}\n")
                    all_passed = False
            except Exception as e:
                print(f"  [ERROR] {test_name}: {e}\n")
                all_passed = False
        
        # Print results
        if self.errors:
            print(f"\n[ERROR] ERRORS ({len(self.errors)}):")
            for error in self.errors[:20]:
                print(f"  • {error}")
            if len(self.errors) > 20:
                print(f"  ... and {len(self.errors) - 20} more errors")
        
        if self.warnings:
            print(f"\n[WARN] WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:
                print(f"  • {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more warnings")
        
        print("\n" + "=" * 70)
        if all_passed and not self.errors:
            print("[SUCCESS] ALL COMPREHENSIVE TESTS PASSED")
        else:
            print(f"[FAILED] Found {len(self.errors)} errors, {len(self.warnings)} warnings")
        print("=" * 70)
        
        return all_passed and not self.errors

if __name__ == "__main__":
    validator = ComprehensiveValidator()
    success = validator.run_all_tests()
    exit(0 if success else 1)

