#!/usr/bin/env python3
"""
Test script for Dokter Grammar AI Engine Workflow
Tests question loading, choice assignment, and scoring logic
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any

class Question:
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id')
        self.type = data.get('type')
        self.difficulty = data.get('difficulty')
        self.topic_id = data.get('topicId')  # JSON uses camelCase
        self.prompt = data.get('prompt')
        self.answer = data.get('answer')
        self.choices = data.get('choices', [])
        self.tags = data.get('tags', [])
    
    @property
    def topicId(self):
        """Alias for topic_id to match JSON field name"""
        return self.topic_id
    
    def __repr__(self):
        return f"Question(id={self.id}, type={self.type}, answer={self.answer})"

class QuestionBankTester:
    def __init__(self, assets_dir: str = "assets/data"):
        self.assets_dir = Path(assets_dir)
        self.questions: List[Question] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def load_question_banks(self) -> bool:
        """Load all question bank JSON files"""
        bank_files = [
            'question_bank.json',
            'question_bank1.json',
            'question_bank2.json',
            'question_bank3.json',
        ]
        
        total_loaded = 0
        for bank_file in bank_files:
            file_path = self.assets_dir / bank_file
            if not file_path.exists():
                self.warnings.append(f"Question bank file not found: {file_path}")
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            question = Question(item)
                            self.questions.append(question)
                            total_loaded += 1
                    else:
                        self.errors.append(f"Invalid format in {bank_file}: expected list")
            except json.JSONDecodeError as e:
                self.errors.append(f"JSON decode error in {bank_file}: {e}")
            except Exception as e:
                self.errors.append(f"Error loading {bank_file}: {e}")
        
        print(f"[OK] Loaded {total_loaded} questions from {len(bank_files)} bank files")
        return len(self.questions) > 0
    
    def test_question_structure(self) -> bool:
        """Test that all questions have required fields"""
        all_valid = True
        
        for question in self.questions:
            # Check required fields
            if not question.id:
                self.errors.append(f"Question missing required field: id")
                all_valid = False
            if not question.type:
                self.errors.append(f"Question {question.id} missing required field: type")
                all_valid = False
            if question.difficulty is None:
                self.errors.append(f"Question {question.id} missing required field: difficulty")
                all_valid = False
            if question.topic_id is None:
                self.errors.append(f"Question {question.id} missing required field: topicId")
                all_valid = False
            if not question.prompt:
                self.errors.append(f"Question {question.id} missing required field: prompt")
                all_valid = False
            if not question.answer:
                self.errors.append(f"Question {question.id} missing required field: answer")
                all_valid = False
        
        return all_valid
    
    def test_choices_assignment(self) -> bool:
        """Test that choices are correctly assigned to questions"""
        all_valid = True
        
        for question in self.questions:
            # Check if question has choices
            if not question.choices:
                if question.type in ['multiple_choice', 'gap_fill']:
                    self.warnings.append(f"Question {question.id} ({question.type}) has no choices")
                continue
            
            # Check for duplicate choiceIds
            choice_ids = [c.get('choiceId') for c in question.choices]
            duplicates = [cid for cid in choice_ids if choice_ids.count(cid) > 1]
            if duplicates:
                self.errors.append(f"Question {question.id} has duplicate choiceIds: {duplicates}")
                all_valid = False
            
            # Check if answer matches a choiceId (for multiple_choice) or choice text (for gap_fill)
            if question.type == 'multiple_choice':
                choice_ids = [c.get('choiceId') for c in question.choices]
                if question.answer not in choice_ids:
                    # Check if answer might be text instead of choiceId (data inconsistency)
                    choice_texts = {c.get('text', '').lower().strip(): c.get('choiceId') for c in question.choices}
                    if question.answer.lower().strip() in choice_texts:
                        # Answer is text, but should be choiceId - data inconsistency
                        expected_choice_id = choice_texts[question.answer.lower().strip()]
                        self.warnings.append(
                            f"Question {question.id}: answer '{question.answer}' is text, "
                            f"should be choiceId '{expected_choice_id}'"
                        )
                    else:
                        self.errors.append(
                            f"Question {question.id}: answer '{question.answer}' not in choices {choice_ids}"
                        )
                        all_valid = False
            elif question.type == 'gap_fill':
                # For gap_fill, answer can be text or choiceId
                choice_ids = [c.get('choiceId') for c in question.choices]
                choice_texts = [c.get('text', '').lower().strip() for c in question.choices]
                answer_lower = question.answer.lower().strip()
                
                if answer_lower not in choice_ids and answer_lower not in choice_texts:
                    # Answer not found in either choiceIds or texts
                    self.warnings.append(
                        f"Question {question.id}: answer '{question.answer}' not found in choices"
                    )
            
            # Check if isCorrect flags are consistent
            # For multiple_choice: answer should be a choiceId that has isCorrect=True
            # For gap_fill: answer should match text of a choice that has isCorrect=True
            correct_choices = [c for c in question.choices if c.get('isCorrect', False)]
            
            if question.type == 'multiple_choice':
                # For multiple choice, answer should be a choiceId
                correct_choice_ids = [c.get('choiceId') for c in correct_choices]
                if question.answer not in correct_choice_ids:
                    # This is a data inconsistency warning
                    self.warnings.append(
                        f"Question {question.id}: answer '{question.answer}' doesn't match "
                        f"any isCorrect=True choice {correct_choice_ids}"
                    )
            elif question.type == 'gap_fill':
                # For gap_fill, answer should match text of correct choice
                correct_choice_texts = [c.get('text', '').lower().strip() for c in correct_choices]
                if question.answer.lower().strip() not in correct_choice_texts:
                    # This is a data inconsistency warning
                    self.warnings.append(
                        f"Question {question.id}: answer '{question.answer}' doesn't match "
                        f"text of any isCorrect=True choice"
                    )
        
        return all_valid
    
    def test_answer_extraction_simulation(self) -> bool:
        """Simulate the choiceId extraction logic from test_screen.dart"""
        all_valid = True
        
        for question in self.questions:
            if not question.choices:
                continue
            
            for idx, choice in enumerate(question.choices):
                choice_id = choice.get('choiceId')
                
                # Simulate the unique value format: questionId_choiceId_index
                unique_value = f"{question.id}_{choice_id}_{idx}"
                
                # Test OLD extraction (buggy) - This is expected to fail, just for documentation
                parts_old = unique_value.split('_')
                if len(parts_old) >= 3:
                    extracted_old = '_'.join(parts_old[1:-1])  # Buggy method
                    if extracted_old != choice_id:
                        # This is expected - OLD method was buggy, just log as info
                        pass  # Don't count as error, this is expected behavior
                
                # Test NEW extraction (fixed)
                parts_new = unique_value.split('_')
                if len(parts_new) >= 2:
                    extracted_new = parts_new[-2]  # Fixed method
                    if extracted_new != choice_id:
                        self.errors.append(
                            f"Question {question.id}: NEW extraction failed! "
                            f"Expected '{choice_id}', got '{extracted_new}' from '{unique_value}'"
                        )
                        all_valid = False
        
        return all_valid
    
    def test_scoring_simulation(self) -> bool:
        """Simulate scoring logic to verify it works correctly"""
        all_valid = True
        
        for question in self.questions:
            if not question.choices:
                continue
            
            # Test correct answer
            correct_answer = question.answer
            is_correct = self.is_answer_correct(question, correct_answer)
            if not is_correct:
                self.errors.append(
                    f"Question {question.id}: Correct answer '{correct_answer}' marked as incorrect!"
                )
                all_valid = False
            
            # Test incorrect answers
            for choice in question.choices:
                choice_id = choice.get('choiceId')
                if choice_id != correct_answer:
                    is_correct = self.is_answer_correct(question, choice_id)
                    if is_correct:
                        self.errors.append(
                            f"Question {question.id}: Incorrect answer '{choice_id}' marked as correct!"
                        )
                        all_valid = False
        
        return all_valid
    
    @staticmethod
    def is_answer_correct(question: Question, user_answer: str) -> bool:
        """Simulate ScoringService.isAnswerCorrect() logic"""
        if not user_answer:
            return False
        
        if question.type == 'multiple_choice':
            return question.answer.lower() == user_answer.lower()
        elif question.type in ['gap_fill', 'short_answer']:
            return question.answer.lower().strip() == user_answer.lower().strip()
        else:
            return question.answer.lower() == user_answer.lower()
    
    def test_question_distribution(self):
        """Test question distribution across topics"""
        topic_counts = {}
        for question in self.questions:
            topic_id = question.topic_id
            topic_counts[topic_id] = topic_counts.get(topic_id, 0) + 1
        
        print("\n[STATS] Question Distribution by Topic:")
        for topic_id in sorted(topic_counts.keys()):
            count = topic_counts[topic_id]
            print(f"  Topic {topic_id}: {count} questions")
        
        total = sum(topic_counts.values())
        print(f"\n  Total: {total} questions")
    
    def run_all_tests(self):
        """Run all tests and print results"""
        print("=" * 60)
        print("Dokter Grammar AI Engine Test Suite")
        print("=" * 60)
        
        # Load questions
        if not self.load_question_banks():
            print("[ERROR] Failed to load question banks")
            return False
        
        print(f"\n[INFO] Testing {len(self.questions)} questions...\n")
        
        # Run tests
        tests = [
            ("Question Structure", self.test_question_structure),
            ("Choices Assignment", self.test_choices_assignment),
            ("Answer Extraction Simulation", self.test_answer_extraction_simulation),
            ("Scoring Simulation", self.test_scoring_simulation),
        ]
        
        all_passed = True
        for test_name, test_func in tests:
            print(f"Running: {test_name}...")
            try:
                result = test_func()
                if result:
                    print(f"  [PASS] {test_name}: PASSED\n")
                else:
                    print(f"  [FAIL] {test_name}: FAILED\n")
                    all_passed = False
            except Exception as e:
                print(f"  [ERROR] {test_name}: ERROR - {e}\n")
                all_passed = False
        
        # Print distribution
        self.test_question_distribution()
        
        # Print errors and warnings
        if self.errors:
            print(f"\n[ERROR] ERRORS ({len(self.errors)}):")
            for error in self.errors[:20]:  # Show first 20 errors
                print(f"  - {error}")
            if len(self.errors) > 20:
                print(f"  ... and {len(self.errors) - 20} more errors")
        
        if self.warnings:
            print(f"\n[WARN] WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # Show first 10 warnings
                print(f"  - {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more warnings")
        
        # Summary
        print("\n" + "=" * 60)
        if all_passed and not self.errors:
            print("[SUCCESS] ALL TESTS PASSED")
        else:
            print(f"[FAILED] TESTS FAILED: {len(self.errors)} errors, {len(self.warnings)} warnings")
        print("=" * 60)
        
        return all_passed and not self.errors

if __name__ == "__main__":
    tester = QuestionBankTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)

