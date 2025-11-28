#!/usr/bin/env python3
"""
AI-Powered Question Validator
Uses trained DialogGPT model to detect and fix question-answer mismatches
"""

import json
from pathlib import Path
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

class AIQuestionValidator:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.issues = []
        self.fixes = []
        
    def load_model(self):
        """Load trained model"""
        print("[INFO] Loading AI model...")
        model_path = Path("models/dialogpt_grammar")
        if not model_path.exists():
            print("[ERROR] Model not found")
            return False
        
        self.model = GPT2LMHeadModel.from_pretrained(str(model_path))
        self.tokenizer = GPT2Tokenizer.from_pretrained(str(model_path))
        self.model.eval()
        print("[OK] Model loaded")
        return True
    
    def load_questions(self):
        """Load all questions"""
        assets_dir = Path("assets/data")
        bank_files = [
            'question_bank.json',
            'question_bank1.json',
            'question_bank2.json',
            'question_bank3.json',
        ]
        
        all_questions = []
        for bank_file in bank_files:
            file_path = assets_dir / bank_file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            all_questions.extend(data)
                except Exception as e:
                    print(f"[WARN] Error loading {bank_file}: {e}")
        
        return all_questions
    
    def get_correct_choice(self, question):
        """Get the correct choice from question"""
        choices = question.get('choices', [])
        answer = question.get('answer', '').lower()
        
        # Find choice with isCorrect = true
        correct_choices = [c for c in choices if c.get('isCorrect', False)]
        
        if len(correct_choices) == 1:
            return correct_choices[0]
        elif len(correct_choices) > 1:
            # Multiple correct - check which one matches answer field
            for choice in correct_choices:
                if choice.get('choiceId', '').lower() == answer:
                    return choice
            return correct_choices[0]  # Return first if no match
        else:
            # No isCorrect flag - try to find by answer field
            for choice in choices:
                if choice.get('choiceId', '').lower() == answer:
                    return choice
            return None
    
    def validate_question(self, question):
        """Validate a single question using AI"""
        issues = []
        
        question_id = question.get('id', 'unknown')
        question_type = question.get('type', '')
        answer = question.get('answer', '')
        choices = question.get('choices', [])
        prompt = question.get('prompt', '')
        
        # Check 1: Answer field matches isCorrect flag
        correct_choice = self.get_correct_choice(question)
        
        if correct_choice is None:
            issues.append({
                'type': 'no_correct_choice',
                'question_id': question_id,
                'message': 'No correct choice found',
            })
        else:
            correct_choice_id = correct_choice.get('choiceId', '').lower()
            answer_lower = answer.lower()
            
            if correct_choice_id != answer_lower:
                # Mismatch detected - use AI to determine correct answer
                ai_suggestion = self._ai_suggest_correct_answer(
                    question, correct_choice, answer
                )
                
                issues.append({
                    'type': 'answer_mismatch',
                    'question_id': question_id,
                    'current_answer': answer,
                    'correct_choice_id': correct_choice_id,
                    'correct_choice_text': correct_choice.get('text', ''),
                    'ai_suggestion': ai_suggestion,
                    'fix': {
                        'answer': correct_choice_id,
                        'confidence': ai_suggestion.get('confidence', 0.8),
                    }
                })
        
        # Check 2: Gap fill questions - answer should match choice text
        if question_type == 'gap_fill':
            if correct_choice:
                answer_text = correct_choice.get('text', '').lower().strip()
                answer_field = answer.lower().strip()
                
                # If answer field is choiceId, check if it matches
                if answer_field not in [c.get('choiceId', '').lower() for c in choices]:
                    # Answer might be text instead of choiceId
                    if answer_text != answer_field:
                        issues.append({
                            'type': 'gap_fill_mismatch',
                            'question_id': question_id,
                            'current_answer': answer,
                            'expected_text': answer_text,
                            'fix': {
                                'answer': correct_choice.get('choiceId', ''),
                            }
                        })
        
        # Check 3: Multiple correct choices (should only be one)
        correct_count = sum(1 for c in choices if c.get('isCorrect', False))
        if correct_count > 1:
            issues.append({
                'type': 'multiple_correct',
                'question_id': question_id,
                'count': correct_count,
                'fix': {
                    'keep_correct': correct_choice.get('choiceId', '') if correct_choice else None,
                }
            })
        
        # Check 4: No correct choice marked
        if correct_count == 0 and len(choices) > 0:
            issues.append({
                'type': 'no_correct_marked',
                'question_id': question_id,
                'fix': {
                    'mark_correct': correct_choice.get('choiceId', '') if correct_choice else None,
                }
            })
        
        return issues
    
    def _ai_suggest_correct_answer(self, question, correct_choice, current_answer):
        """Use AI to suggest which answer is correct"""
        if self.model is None:
            return {'confidence': 0.5, 'suggestion': 'Use correct_choice_id'}
        
        prompt_text = question.get('prompt', '')
        correct_text = correct_choice.get('text', '')
        current_choice = None
        
        for choice in question.get('choices', []):
            if choice.get('choiceId', '').lower() == current_answer.lower():
                current_choice = choice.get('text', '')
                break
        
        # Create context for AI
        context = f"""
Question: {prompt_text}
Current answer field: {current_answer}
Current answer text: {current_choice or 'N/A'}
Correct choice ID: {correct_choice.get('choiceId', '')}
Correct choice text: {correct_text}
Which one is actually correct based on the grammar rules?
"""
        
        try:
            input_text = f"<|user|>{context}<|assistant|>"
            input_ids = self.tokenizer.encode(input_text, return_tensors='pt')
            
            with torch.no_grad():
                output = self.model.generate(
                    input_ids,
                    max_length=100,
                    num_return_sequences=1,
                    temperature=0.3,  # Lower temperature for more deterministic
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                )
            
            response = self.tokenizer.decode(output[0], skip_special_tokens=False)
            
            if '<|assistant|>' in response:
                suggestion = response.split('<|assistant|>')[1].split('<|endoftext|>')[0].strip()
                
                # Analyze response to determine confidence
                confidence = 0.8
                if 'correct' in suggestion.lower() and correct_choice.get('choiceId', '').lower() in suggestion.lower():
                    confidence = 0.9
                
                return {
                    'confidence': confidence,
                    'suggestion': suggestion,
                    'recommended_answer': correct_choice.get('choiceId', ''),
                }
        except Exception as e:
            print(f"[WARN] AI suggestion failed: {e}")
        
        return {
            'confidence': 0.7,
            'suggestion': f'Use {correct_choice.get("choiceId", "")} based on isCorrect flag',
            'recommended_answer': correct_choice.get('choiceId', ''),
        }
    
    def validate_all(self):
        """Validate all questions"""
        print("\n" + "=" * 60)
        print("AI-Powered Question Validator")
        print("=" * 60)
        
        if not self.load_model():
            return False
        
        questions = self.load_questions()
        print(f"\n[INFO] Validating {len(questions)} questions...")
        
        all_issues = []
        for i, question in enumerate(questions, 1):
            if i % 50 == 0:
                print(f"  Progress: {i}/{len(questions)}")
            
            issues = self.validate_question(question)
            all_issues.extend(issues)
        
        self.issues = all_issues
        return True
    
    def generate_fixes(self):
        """Generate fix suggestions"""
        print("\n" + "=" * 60)
        print("Generating Fixes")
        print("=" * 60)
        
        fixes_by_type = {}
        for issue in self.issues:
            issue_type = issue['type']
            if issue_type not in fixes_by_type:
                fixes_by_type[issue_type] = []
            fixes_by_type[issue_type].append(issue)
        
        # Generate fix file
        fixes = []
        for issue in self.issues:
            if 'fix' in issue:
                fixes.append({
                    'question_id': issue['question_id'],
                    'issue_type': issue['type'],
                    'current': issue.get('current_answer'),
                    'fix': issue['fix'],
                    'confidence': issue.get('ai_suggestion', {}).get('confidence', 0.8),
                })
        
        self.fixes = fixes
        return fixes
    
    def save_report(self):
        """Save validation report"""
        report = {
            'total_issues': len(self.issues),
            'issues_by_type': {},
            'fixes': self.fixes,
        }
        
        for issue in self.issues:
            issue_type = issue['type']
            if issue_type not in report['issues_by_type']:
                report['issues_by_type'][issue_type] = []
            report['issues_by_type'][issue_type].append(issue)
        
        report_path = Path("question_validation_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n[OK] Report saved to {report_path}")
        return report_path
    
    def print_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 60)
        print("Validation Summary")
        print("=" * 60)
        
        if not self.issues:
            print("\n✅ No issues found! All questions are valid.")
            return
        
        print(f"\n🔴 Found {len(self.issues)} issues:")
        
        issues_by_type = {}
        for issue in self.issues:
            issue_type = issue['type']
            issues_by_type[issue_type] = issues_by_type.get(issue_type, 0) + 1
        
        for issue_type, count in sorted(issues_by_type.items()):
            print(f"  {issue_type}: {count}")
        
        print(f"\n💡 Generated {len(self.fixes)} fix suggestions")
        
        # Show sample issues
        print("\n📋 Sample Issues:")
        for issue in self.issues[:5]:
            print(f"\n  Question: {issue['question_id']}")
            print(f"  Type: {issue['type']}")
            if 'current_answer' in issue:
                print(f"  Current: {issue['current_answer']}")
            if 'fix' in issue:
                print(f"  Fix: {issue['fix']}")

def main():
    validator = AIQuestionValidator()
    
    if validator.validate_all():
        validator.generate_fixes()
        validator.save_report()
        validator.print_summary()
        
        print("\n" + "=" * 60)
        print("Next Steps:")
        print("1. Review question_validation_report.json")
        print("2. Apply fixes to question bank files")
        print("3. Re-run validation to verify")
        print("=" * 60)
    else:
        print("\n[ERROR] Validation failed")

if __name__ == "__main__":
    main()

