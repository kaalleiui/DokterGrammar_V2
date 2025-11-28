#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Choice Mismatches in Question Bank
Fixes issues where:
1. gap_fill questions have full sentences as choices instead of single words/phrases
2. Sentence transformation questions have incorrect choices
"""

import json
import sys
import re
from pathlib import Path
from typing import List, Dict, Any

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class ChoiceMismatchFixer:
    def __init__(self):
        self.fixes_applied = []
        self.issues_found = []
    
    def is_full_sentence(self, text: str) -> bool:
        """Check if text is a full sentence (has subject and verb, not just a word/phrase)"""
        text = text.strip()
        # If it's very short (1-3 words), it's likely not a full sentence
        words = text.split()
        if len(words) <= 3:
            return False
        
        # Check if it starts with capital and ends with period (likely a sentence)
        if text[0].isupper() and text[-1] in '.!?':
            return True
        
        # Check if it has a verb (basic check - has words that could be verbs)
        # Common verbs in English
        common_verbs = ['is', 'are', 'was', 'were', 'has', 'have', 'had', 'will', 'would', 
                       'can', 'could', 'should', 'must', 'may', 'might', 'do', 'does', 'did',
                       'be', 'been', 'being', 'go', 'went', 'gone', 'make', 'made', 'get', 'got']
        words_lower = [w.lower().rstrip('.,!?') for w in words]
        has_verb = any(v in words_lower for v in common_verbs)
        
        # If it has 4+ words and a verb, it's likely a sentence
        if len(words) >= 4 and has_verb:
            return True
        
        return False
    
    def extract_blank_from_prompt(self, prompt: str) -> str:
        """Extract the sentence with blank from prompt"""
        # Pattern: "Fill in the blank: '...'"
        match = re.search(r"Fill in the blank:\s*['\"](.*?)['\"]", prompt, re.IGNORECASE)
        if match:
            return match.group(1)
        return ""
    
    def should_be_single_word_or_phrase(self, prompt: str, choice_text: str) -> bool:
        """Check if choice should be a single word/phrase based on the prompt"""
        blank_sentence = self.extract_blank_from_prompt(prompt)
        if not blank_sentence:
            return False
        
        # Count blanks in the sentence
        blank_count = blank_sentence.count('_____') + blank_sentence.count('____') + blank_sentence.count('___')
        
        # If there's a blank, the choice should fill just that blank (single word/phrase)
        # If choice is a full sentence, it's wrong
        if blank_count > 0:
            return not self.is_full_sentence(choice_text)
        
        return False
    
    def check_gap_fill_choices(self, question: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check if gap_fill question has inappropriate choices"""
        issues = []
        
        if question.get('type') != 'gap_fill':
            return issues
        
        prompt = question.get('prompt', '')
        choices = question.get('choices', [])
        
        for choice in choices:
            choice_text = choice.get('text', '')
            
            # Check if choice is a full sentence when it should be a word/phrase
            if self.should_be_single_word_or_phrase(prompt, choice_text):
                if self.is_full_sentence(choice_text):
                    issues.append({
                        'type': 'full_sentence_in_gap_fill',
                        'question_id': question.get('id'),
                        'choice_id': choice.get('choiceId'),
                        'choice_text': choice_text,
                        'prompt': prompt,
                    })
        
        return issues
    
    def check_sentence_transformation(self, question: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check if sentence transformation question has incorrect choices"""
        issues = []
        
        prompt = question.get('prompt', '').lower()
        choices = question.get('choices', [])
        
        # Check if it's a transformation question
        is_transformation = any(keyword in prompt for keyword in [
            'change', 'transform', 'convert', 'rewrite', 'rephrase'
        ])
        
        if not is_transformation:
            return issues
        
        # For transformation questions, choices should be transformed sentences
        # Check if choices are just "to be" forms or unrelated sentences
        for choice in choices:
            choice_text = choice.get('text', '')
            
            # If choice is just a verb form (like "is", "are", "was", "were") 
            # and prompt asks for sentence transformation, it's wrong
            if len(choice_text.split()) <= 2 and choice_text.lower() in ['is', 'are', 'was', 'were', 'be', 'been', 'being']:
                issues.append({
                    'type': 'verb_form_in_transformation',
                    'question_id': question.get('id'),
                    'choice_id': choice.get('choiceId'),
                    'choice_text': choice_text,
                    'prompt': question.get('prompt', ''),
                })
        
        return issues
    
    def fix_question(self, question: Dict[str, Any]) -> bool:
        """Fix a question if it has issues"""
        fixed = False
        q_id = question.get('id')
        
        # Check and fix gap_fill issues
        if question.get('type') == 'gap_fill':
            prompt = question.get('prompt', '')
            choices = question.get('choices', [])
            
            for choice in choices:
                choice_text = choice.get('text', '')
                
                # If choice is a full sentence but should be a word/phrase
                if self.should_be_single_word_or_phrase(prompt, choice_text):
                    if self.is_full_sentence(choice_text):
                        # Try to extract the relevant word/phrase from the sentence
                        # This is a heuristic - may need manual review
                        blank_sentence = self.extract_blank_from_prompt(prompt)
                        
                        # For now, mark as needing manual fix
                        self.issues_found.append({
                            'question_id': q_id,
                            'type': 'gap_fill_full_sentence',
                            'prompt': prompt,
                            'choice_id': choice.get('choiceId'),
                            'current_choice': choice_text,
                            'needs_manual_fix': True,
                        })
        
        # Check and fix transformation issues
        prompt_lower = question.get('prompt', '').lower()
        if any(keyword in prompt_lower for keyword in ['change', 'transform', 'convert']):
            choices = question.get('choices', [])
            
            for choice in choices:
                choice_text = choice.get('text', '')
                
                # If choice is just a verb form, mark for manual fix
                if len(choice_text.split()) <= 2 and choice_text.lower() in ['is', 'are', 'was', 'were', 'be', 'been', 'being']:
                    self.issues_found.append({
                        'question_id': q_id,
                        'type': 'transformation_verb_form',
                        'prompt': question.get('prompt', ''),
                        'choice_id': choice.get('choiceId'),
                        'current_choice': choice_text,
                        'needs_manual_fix': True,
                    })
        
        return fixed
    
    def scan_all_questions(self) -> Dict[str, Any]:
        """Scan all question banks for issues"""
        assets_dir = Path('assets/data')
        bank_files = [
            'question_bank.json',
            'question_bank1.json',
            'question_bank2.json',
            'question_bank3.json',
        ]
        
        all_questions = []
        for bank_file in bank_files:
            file_path = assets_dir / bank_file
            if not file_path.exists():
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for q in data:
                            q['_source_file'] = bank_file
                        all_questions.extend(data)
            except Exception as e:
                print(f'Error loading {bank_file}: {e}')
        
        print('=' * 70)
        print('SCANNING FOR CHOICE MISMATCHES')
        print('=' * 70)
        print(f'\nTotal questions: {len(all_questions)}\n')
        
        gap_fill_issues = []
        transformation_issues = []
        
        for question in all_questions:
            # Check gap_fill issues
            gap_issues = self.check_gap_fill_choices(question)
            gap_fill_issues.extend(gap_issues)
            
            # Check transformation issues
            trans_issues = self.check_sentence_transformation(question)
            transformation_issues.extend(trans_issues)
            
            # Try to fix
            self.fix_question(question)
        
        print(f'🔴 Gap Fill Issues (full sentences as choices): {len(gap_fill_issues)}')
        for issue in gap_fill_issues[:10]:
            print(f'  • {issue["question_id"]}: Choice {issue["choice_id"]} = "{issue["choice_text"][:50]}..."')
            print(f'    Prompt: {issue["prompt"][:80]}...')
        
        if len(gap_fill_issues) > 10:
            print(f'  ... and {len(gap_fill_issues) - 10} more')
        
        print(f'\n🔴 Transformation Issues (verb forms instead of sentences): {len(transformation_issues)}')
        for issue in transformation_issues[:10]:
            print(f'  • {issue["question_id"]}: Choice {issue["choice_id"]} = "{issue["choice_text"]}"')
            print(f'    Prompt: {issue["prompt"][:80]}...')
        
        if len(transformation_issues) > 10:
            print(f'  ... and {len(transformation_issues) - 10} more')
        
        print(f'\n📋 Total issues found: {len(gap_fill_issues) + len(transformation_issues)}')
        print(f'📋 Issues needing manual review: {len(self.issues_found)}')
        
        return {
            'gap_fill_issues': gap_fill_issues,
            'transformation_issues': transformation_issues,
            'all_issues': self.issues_found,
        }

def main():
    fixer = ChoiceMismatchFixer()
    results = fixer.scan_all_questions()
    
    # Save issues to file for review
    output_file = Path('choice_mismatch_issues.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f'\n✅ Issues saved to {output_file}')
    print('\nNext steps:')
    print('1. Review the issues in choice_mismatch_issues.json')
    print('2. Manually fix questions with full sentences in gap_fill choices')
    print('3. Manually fix transformation questions with verb forms instead of sentences')

if __name__ == '__main__':
    main()

