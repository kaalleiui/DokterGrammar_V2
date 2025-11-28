#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Question Bank Review Helper Script
Helps identify potential issues in questions for manual review

Usage: python review_questions.py
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Any

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class QuestionReviewer:
    def __init__(self):
        self.questions: List[Dict[str, Any]] = []
        self.issues: List[str] = []
        self.stats = {
            'by_type': defaultdict(int),
            'by_topic': defaultdict(int),
            'by_difficulty': defaultdict(int),
            'with_explanation': 0,
            'with_example': 0,
            'with_tags': 0,
        }
    
    def load_questions(self):
        """Load all questions from all banks"""
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
    
    def analyze_questions(self):
        """Analyze questions for potential issues"""
        print('=' * 70)
        print('QUESTION BANK ANALYSIS')
        print('=' * 70)
        print(f'\nTotal Questions: {len(self.questions)}\n')
        
        # Basic statistics
        for question in self.questions:
            q_type = question.get('type', 'unknown')
            topic_id = question.get('topicId', 0)
            difficulty = question.get('difficulty', 0)
            
            self.stats['by_type'][q_type] += 1
            self.stats['by_topic'][topic_id] += 1
            self.stats['by_difficulty'][difficulty] += 1
            
            if question.get('explanationTemplate'):
                self.stats['with_explanation'] += 1
            
            if question.get('exampleSentence'):
                self.stats['with_example'] += 1
            
            if question.get('tags'):
                self.stats['with_tags'] += 1
        
        # Print statistics
        print('📊 STATISTICS:')
        print('─' * 70)
        print('\nBy Type:')
        for q_type, count in sorted(self.stats['by_type'].items()):
            print(f'  {q_type}: {count}')
        
        print('\nBy Difficulty:')
        for diff, count in sorted(self.stats['by_difficulty'].items()):
            print(f'  Difficulty {diff}: {count}')
        
        print('\nBy Topic ID:')
        for topic_id, count in sorted(self.stats['by_topic'].items()):
            print(f'  Topic {topic_id}: {count}')
        
        print(f'\nQuestions with explanation: {self.stats["with_explanation"]}/{len(self.questions)}')
        print(f'Questions with example: {self.stats["with_example"]}/{len(self.questions)}')
        print(f'Questions with tags: {self.stats["with_tags"]}/{len(self.questions)}')
    
    def check_potential_issues(self):
        """Check for potential issues that need manual review"""
        print('\n' + '=' * 70)
        print('POTENTIAL ISSUES FOR MANUAL REVIEW')
        print('=' * 70)
        
        issues_found = {
            'short_prompts': [],
            'long_prompts': [],
            'missing_explanations': [],
            'missing_examples': [],
            'no_tags': [],
            'very_short_explanations': [],
            'very_long_explanations': [],
            'difficulty_0_or_6': [],
            'duplicate_ids': [],
        }
        
        seen_ids = {}
        
        for i, question in enumerate(self.questions):
            q_id = question.get('id', f'unknown_{i}')
            prompt = question.get('prompt', '')
            explanation = question.get('explanationTemplate', '')
            example = question.get('exampleSentence', '')
            tags = question.get('tags', [])
            difficulty = question.get('difficulty', 0)
            
            # Check for duplicate IDs
            if q_id in seen_ids:
                issues_found['duplicate_ids'].append(f'{q_id} (found in multiple files)')
            seen_ids[q_id] = True
            
            # Check prompt length
            if len(prompt) < 20:
                issues_found['short_prompts'].append(f'{q_id}: "{prompt[:50]}..."')
            elif len(prompt) > 200:
                issues_found['long_prompts'].append(f'{q_id}: {len(prompt)} chars')
            
            # Check for missing explanations
            if not explanation or len(explanation.strip()) < 10:
                issues_found['missing_explanations'].append(q_id)
            
            # Check explanation length
            if explanation:
                if len(explanation.strip()) < 20:
                    issues_found['very_short_explanations'].append(f'{q_id}: {len(explanation)} chars')
                elif len(explanation.strip()) > 300:
                    issues_found['very_long_explanations'].append(f'{q_id}: {len(explanation)} chars')
            
            # Check for missing examples
            if not example or len(example.strip()) < 5:
                issues_found['missing_examples'].append(q_id)
            
            # Check for missing tags
            if not tags or len(tags) == 0:
                issues_found['no_tags'].append(q_id)
            
            # Check difficulty range
            if difficulty == 0 or difficulty > 5:
                issues_found['difficulty_0_or_6'].append(f'{q_id}: difficulty={difficulty}')
        
        # Print issues
        total_issues = 0
        for issue_type, items in issues_found.items():
            if items:
                total_issues += len(items)
                print(f'\n⚠️  {issue_type.replace("_", " ").title()} ({len(items)}):')
                for item in items[:10]:  # Show first 10
                    print(f'  • {item}')
                if len(items) > 10:
                    print(f'  ... and {len(items) - 10} more')
        
        if total_issues == 0:
            print('\n✅ No obvious issues found!')
        else:
            print(f'\n📋 Total potential issues: {total_issues}')
            print('   (These need manual review - not all are necessarily problems)')
    
    def sample_questions_by_topic(self, samples_per_topic=2):
        """Sample questions from each topic for review"""
        print('\n' + '=' * 70)
        print(f'SAMPLE QUESTIONS FOR MANUAL REVIEW ({samples_per_topic} per topic)')
        print('=' * 70)
        
        questions_by_topic = defaultdict(list)
        for question in self.questions:
            topic_id = question.get('topicId', 0)
            questions_by_topic[topic_id].append(question)
        
        topic_names = {
            1: 'Tenses',
            2: 'Modals & Auxiliaries',
            3: 'Conditionals',
            4: 'Complex Sentences',
            5: 'Sentence Combining',
            6: 'Articles & Determiners',
            7: 'Subject-Verb Agreement',
            8: 'Passive Voice',
            9: 'Reported Speech',
            10: 'Prepositions',
            11: 'Adjective Clauses',
            12: 'Pronouns & Reference',
        }
        
        for topic_id in sorted(questions_by_topic.keys()):
            topic_questions = questions_by_topic[topic_id]
            topic_name = topic_names.get(topic_id, f'Topic {topic_id}')
            
            print(f'\n📚 {topic_name} (Topic {topic_id}) - {len(topic_questions)} questions')
            print('─' * 70)
            
            # Sample questions
            sample_size = min(samples_per_topic, len(topic_questions))
            samples = topic_questions[:sample_size]  # Take first N
            
            for i, q in enumerate(samples, 1):
                print(f'\n  Sample {i}:')
                print(f'    ID: {q.get("id", "unknown")}')
                print(f'    Type: {q.get("type", "unknown")}')
                print(f'    Difficulty: {q.get("difficulty", 0)}')
                print(f'    Prompt: {q.get("prompt", "")[:80]}...')
                print(f'    Answer: {q.get("answer", "")}')
                has_explanation = '✅' if q.get('explanationTemplate') else '❌'
                has_example = '✅' if q.get('exampleSentence') else '❌'
                has_tags = '✅' if q.get('tags') else '❌'
                print(f'    Explanation: {has_explanation} | Example: {has_example} | Tags: {has_tags}')
    
    def generate_review_report(self):
        """Generate a comprehensive review report"""
        self.load_questions()
        self.analyze_questions()
        self.check_potential_issues()
        self.sample_questions_by_topic(samples_per_topic=2)
        
        print('\n' + '=' * 70)
        print('REVIEW COMPLETE')
        print('=' * 70)
        print('\nNext steps:')
        print('1. Review the potential issues listed above')
        print('2. Check sample questions for each topic')
        print('3. Manually review questions flagged as problematic')
        print('4. Fix any issues found')

def main():
    reviewer = QuestionReviewer()
    reviewer.generate_review_report()

if __name__ == '__main__':
    main()

