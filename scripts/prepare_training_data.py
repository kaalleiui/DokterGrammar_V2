#!/usr/bin/env python3
"""
Prepare training data for DialogGPT-style model from question bank
Converts questions into conversation format for fine-tuning
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
import random

class TrainingDataGenerator:
    def __init__(self, assets_dir: str = "assets/data", output_dir: str = "training_data"):
        self.assets_dir = Path(assets_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.questions: List[Dict] = []
        
    def load_question_banks(self) -> int:
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
                print(f"[WARN] Question bank file not found: {file_path}")
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.questions.extend(data)
                        total_loaded += len(data)
                        print(f"[OK] Loaded {len(data)} questions from {bank_file}")
            except Exception as e:
                print(f"[ERROR] Error loading {bank_file}: {e}")
        
        print(f"[OK] Total loaded: {total_loaded} questions")
        return total_loaded
    
    def get_grammar_point(self, question: Dict) -> str:
        """Extract grammar point from question tags"""
        tags = question.get('tags', [])
        for tag in tags:
            if tag.get('tagType') == 'grammar_point':
                return tag.get('tagValue', 'general')
        return 'general'
    
    def get_tense(self, question: Dict) -> str:
        """Extract tense from question tags"""
        tags = question.get('tags', [])
        for tag in tags:
            if tag.get('tagType') == 'tense':
                return tag.get('tagValue', '')
        return ''
    
    def format_context(self, question: Dict, user_answer: str, is_correct: bool) -> str:
        """Format question context for model input"""
        prompt = question.get('prompt', '')
        question_type = question.get('type', 'multiple_choice')
        grammar_point = self.get_grammar_point(question)
        tense = self.get_tense(question)
        difficulty = question.get('difficulty', 3)
        
        # Get correct answer text
        correct_answer = self.get_correct_answer_text(question)
        
        context_parts = [
            f"Question: {prompt}",
            f"Type: {question_type}",
            f"Grammar Point: {grammar_point}",
        ]
        
        if tense:
            context_parts.append(f"Tense: {tense}")
        
        context_parts.append(f"Difficulty: {difficulty}")
        context_parts.append(f"User Answer: {user_answer}")
        context_parts.append(f"Correct Answer: {correct_answer}")
        context_parts.append(f"Is Correct: {is_correct}")
        
        return " | ".join(context_parts)
    
    def get_correct_answer_text(self, question: Dict) -> str:
        """Get the text of the correct answer"""
        answer = question.get('answer', '')
        choices = question.get('choices', [])
        
        # Try to find correct choice by isCorrect flag
        for choice in choices:
            if choice.get('isCorrect', False):
                return choice.get('text', answer)
        
        # Try to find by answer field matching choiceId
        for choice in choices:
            if choice.get('choiceId', '').lower() == answer.lower():
                return choice.get('text', answer)
        
        # Fallback to answer field
        return answer
    
    def get_user_answer_text(self, question: Dict, user_answer: str) -> str:
        """Get the text of user's answer"""
        choices = question.get('choices', [])
        
        # Try to find by choiceId
        for choice in choices:
            if choice.get('choiceId', '').lower() == user_answer.lower():
                return choice.get('text', user_answer)
        
        # Fallback to user_answer itself
        return user_answer
    
    def generate_explanation(self, question: Dict, user_answer: str, is_correct: bool) -> str:
        """Generate explanation text (using existing template or generating new one)"""
        explanation_template = question.get('explanationTemplate', '')
        example_sentence = question.get('exampleSentence', '')
        correct_answer_text = self.get_correct_answer_text(question)
        user_answer_text = self.get_user_answer_text(question, user_answer)
        grammar_point = self.get_grammar_point(question)
        
        if is_correct:
            # Correct answer explanation
            if example_sentence:
                return f"Jawaban Anda benar! '{correct_answer_text}' adalah pilihan yang tepat. {explanation_template if explanation_template else 'Pilihan ini sesuai dengan aturan grammar yang berlaku.'} Contoh: {example_sentence}"
            else:
                return f"Jawaban Anda benar! '{correct_answer_text}' adalah pilihan yang tepat. {explanation_template if explanation_template else 'Pilihan ini sesuai dengan aturan grammar yang berlaku.'}"
        else:
            # Incorrect answer explanation
            if explanation_template:
                explanation = explanation_template
            else:
                explanation = f"Jawaban yang benar adalah '{correct_answer_text}'. Pilihan '{user_answer_text}' tidak tepat karena tidak sesuai dengan aturan grammar untuk {grammar_point}."
            
            if example_sentence:
                explanation += f" Contoh yang benar: {example_sentence}"
            
            return explanation
    
    def create_training_examples(self, question: Dict) -> List[Dict]:
        """Create multiple training examples from a single question"""
        examples = []
        question_type = question.get('type', 'multiple_choice')
        choices = question.get('choices', [])
        
        # For multiple choice and gap_fill, create examples for each choice
        if question_type in ['multiple_choice', 'gap_fill'] and choices:
            for choice in choices:
                choice_id = choice.get('choiceId', '')
                is_correct = choice.get('isCorrect', False)
                
                context = self.format_context(question, choice_id, is_correct)
                explanation = self.generate_explanation(question, choice_id, is_correct)
                
                examples.append({
                    'context': context,
                    'explanation': explanation,
                    'is_correct': is_correct,
                    'question_id': question.get('id', ''),
                    'question_type': question_type,
                })
        else:
            # For other types, create correct and incorrect examples
            correct_answer = question.get('answer', '')
            
            # Correct answer example
            context = self.format_context(question, correct_answer, True)
            explanation = self.generate_explanation(question, correct_answer, True)
            examples.append({
                'context': context,
                'explanation': explanation,
                'is_correct': True,
                'question_id': question.get('id', ''),
                'question_type': question_type,
            })
            
            # Incorrect answer example (if we can generate one)
            if question_type == 'short_answer':
                # Generate a plausible wrong answer
                wrong_answer = "wrong_answer_example"
                context = self.format_context(question, wrong_answer, False)
                explanation = self.generate_explanation(question, wrong_answer, False)
                examples.append({
                    'context': context,
                    'explanation': explanation,
                    'is_correct': False,
                    'question_id': question.get('id', ''),
                    'question_type': question_type,
                })
        
        return examples
    
    def format_for_dialogpt(self, examples: List[Dict]) -> List[Dict]:
        """Format examples in DialogGPT conversation format"""
        formatted = []
        
        for example in examples:
            # DialogGPT format: User message + Assistant response
            conversation = {
                'user': example['context'],
                'assistant': example['explanation'],
                'metadata': {
                    'question_id': example['question_id'],
                    'question_type': example['question_type'],
                    'is_correct': example['is_correct'],
                }
            }
            formatted.append(conversation)
        
        return formatted
    
    def generate_training_data(self) -> Tuple[List[Dict], List[Dict]]:
        """Generate training and validation datasets"""
        all_examples = []
        
        print("\n[INFO] Generating training examples from questions...")
        for i, question in enumerate(self.questions):
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(self.questions)} questions...")
            
            examples = self.create_training_examples(question)
            all_examples.extend(examples)
        
        print(f"[OK] Generated {len(all_examples)} training examples")
        
        # Format for DialogGPT
        formatted = self.format_for_dialogpt(all_examples)
        
        # Split into train/validation (80/20)
        random.shuffle(formatted)
        split_idx = int(len(formatted) * 0.8)
        train_data = formatted[:split_idx]
        val_data = formatted[split_idx:]
        
        print(f"[OK] Split: {len(train_data)} train, {len(val_data)} validation")
        
        return train_data, val_data
    
    def save_training_data(self, train_data: List[Dict], val_data: List[Dict]):
        """Save training data to JSON files"""
        train_file = self.output_dir / "train.json"
        val_file = self.output_dir / "val.json"
        
        with open(train_file, 'w', encoding='utf-8') as f:
            json.dump(train_data, f, ensure_ascii=False, indent=2)
        print(f"[OK] Saved training data to {train_file}")
        
        with open(val_file, 'w', encoding='utf-8') as f:
            json.dump(val_data, f, ensure_ascii=False, indent=2)
        print(f"[OK] Saved validation data to {val_file}")
        
        # Also save statistics
        stats = {
            'total_questions': len(self.questions),
            'total_examples': len(train_data) + len(val_data),
            'train_examples': len(train_data),
            'val_examples': len(val_data),
            'question_types': {},
            'grammar_points': {},
        }
        
        # Count question types
        for example in train_data + val_data:
            q_type = example['metadata']['question_type']
            stats['question_types'][q_type] = stats['question_types'].get(q_type, 0) + 1
        
        stats_file = self.output_dir / "stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        print(f"[OK] Saved statistics to {stats_file}")
    
    def run(self):
        """Main execution"""
        print("=" * 60)
        print("Training Data Preparation for DialogGPT")
        print("=" * 60)
        
        # Load questions
        total = self.load_question_banks()
        if total == 0:
            print("[ERROR] No questions loaded. Exiting.")
            return False
        
        # Generate training data
        train_data, val_data = self.generate_training_data()
        
        # Save data
        self.save_training_data(train_data, val_data)
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Training data preparation complete!")
        print("=" * 60)
        print(f"\nNext steps:")
        print(f"1. Review training data in: {self.output_dir}")
        print(f"2. Run: python train_dialogpt_model.py")
        print("=" * 60)
        
        return True

if __name__ == "__main__":
    generator = TrainingDataGenerator()
    generator.run()

