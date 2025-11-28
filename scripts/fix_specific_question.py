#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Specific Question
Tool to fix a specific question by Question ID
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def find_question(question_id: str) -> Optional[Dict[str, Any]]:
    """Find a question by ID in all question banks"""
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
                    for q in data:
                        if q.get('id') == question_id:
                            q['_source_file'] = bank_file
                            return q
        except Exception as e:
            print(f'Error loading {bank_file}: {e}')
    
    return None

def fix_gap_fill_choice(choice_text: str, prompt: str) -> Optional[str]:
    """Try to fix a gap fill choice that's a full sentence"""
    # Extract the sentence with blank
    blank_match = re.search(r"Fill in the blank:\s*['\"](.*?)['\"]", prompt, re.IGNORECASE)
    if not blank_match:
        return None
    
    sentence_with_blank = blank_match.group(1)
    
    # Try to extract relevant word/phrase from the choice
    # This is heuristic - may need manual review
    
    # If choice contains the blank context, try to extract the relevant part
    # For example: "a new city has been built" -> "has been" (if blank is about passive voice)
    
    # Check if it's a passive voice question
    if 'built' in sentence_with_blank.lower() or 'built' in choice_text.lower():
        if 'has been' in choice_text.lower():
            return 'has been'
        elif 'will be' in choice_text.lower():
            return 'will be'
        elif 'is being' in choice_text.lower():
            return 'is being'
        elif 'was' in choice_text.lower() and 'was built' in choice_text.lower():
            return 'was'
        elif 'is' in choice_text.lower():
            return 'is'
    
    # Generic: try to find verb forms
    words = choice_text.split()
    verb_forms = ['is', 'are', 'was', 'were', 'has', 'have', 'had', 'will', 'would', 
                 'can', 'could', 'should', 'must', 'may', 'might', 'be', 'been', 'being']
    
    for word in words:
        if word.lower() in verb_forms:
            return word
    
    # If no fix found, return None (needs manual fix)
    return None

def fix_transformation_choice(choice_text: str, prompt: str) -> Optional[str]:
    """Try to fix a transformation choice that's just a verb form"""
    # This is harder to auto-fix - transformation needs the full sentence
    # Return None to indicate manual fix needed
    return None

def fix_question_choice(question: Dict[str, Any], choice_id: str, new_text: str) -> bool:
    """Fix a specific choice in a question"""
    choices = question.get('choices', [])
    
    for choice in choices:
        if choice.get('choiceId') == choice_id:
            old_text = choice.get('text', '')
            choice['text'] = new_text
            print(f'  ✓ Fixed choice {choice_id}: "{old_text}" -> "{new_text}"')
            return True
    
    print(f'  ✗ Choice {choice_id} not found')
    return False

def save_question(question: Dict[str, Any]) -> bool:
    """Save question back to its source file"""
    source_file = question.get('_source_file')
    if not source_file:
        print('  ✗ No source file found')
        return False
    
    file_path = Path('assets/data') / source_file
    if not file_path.exists():
        print(f'  ✗ Source file not found: {file_path}')
        return False
    
    try:
        # Load all questions
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print(f'  ✗ Invalid file format')
            return False
        
        # Find and update the question
        updated = False
        for i, q in enumerate(data):
            if q.get('id') == question.get('id'):
                # Remove _source_file before saving
                question_copy = question.copy()
                question_copy.pop('_source_file', None)
                data[i] = question_copy
                updated = True
                break
        
        if not updated:
            print(f'  ✗ Question not found in file')
            return False
        
        # Save back
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f'  ✓ Saved to {file_path}')
        return True
        
    except Exception as e:
        print(f'  ✗ Error saving: {e}')
        return False

def main():
    if len(sys.argv) < 2:
        print('Usage: python fix_specific_question.py <question_id> [choice_id] [new_text]')
        print('\nExamples:')
        print('  python fix_specific_question.py q_passive_005')
        print('    - Shows the question and its choices')
        print('  python fix_specific_question.py q_passive_005 a "has been"')
        print('    - Fixes choice a to "has been"')
        return 1
    
    question_id = sys.argv[1]
    
    # Find question
    question = find_question(question_id)
    if not question:
        print(f'❌ Question "{question_id}" not found')
        return 1
    
    print(f'📋 Question: {question_id}')
    print(f'   File: {question.get("_source_file")}')
    print(f'   Type: {question.get("type")}')
    print(f'   Prompt: {question.get("prompt")}')
    print(f'\n   Choices:')
    
    for choice in question.get('choices', []):
        choice_id = choice.get('choiceId', '')
        choice_text = choice.get('text', '')
        is_correct = '✓' if choice.get('isCorrect') else ' '
        word_count = len(choice_text.split())
        print(f'     {is_correct} {choice_id}. "{choice_text}" ({word_count} words)')
    
    # If fixing a choice
    if len(sys.argv) >= 4:
        choice_id = sys.argv[2]
        new_text = sys.argv[3]
        
        print(f'\n🔧 Fixing choice {choice_id} to "{new_text}"...')
        
        if fix_question_choice(question, choice_id, new_text):
            if save_question(question):
                print('\n✅ Question fixed successfully!')
                return 0
            else:
                print('\n❌ Failed to save question')
                return 1
        else:
            print('\n❌ Failed to fix choice')
            return 1
    
    # If just showing, check for potential issues
    print('\n🔍 Analysis:')
    q_type = question.get('type', '')
    prompt = question.get('prompt', '').lower()
    
    issues_found = []
    for choice in question.get('choices', []):
        choice_id = choice.get('choiceId', '')
        choice_text = choice.get('text', '').strip()
        word_count = len(choice_text.split())
        
        if q_type == 'gap_fill':
            if word_count >= 5:
                issues_found.append(f'Choice {choice_id} has {word_count} words (should be 1-3)')
            elif word_count >= 4 and choice_text.lower().startswith(('a ', 'an ', 'the ')):
                issues_found.append(f'Choice {choice_id} starts with article (might be wrong)')
        
        if 'change' in prompt or 'transform' in prompt or 'convert' in prompt:
            if word_count <= 2:
                verb_forms = ['is', 'are', 'was', 'were', 'be', 'been', 'being']
                if choice_text.lower() in verb_forms:
                    issues_found.append(f'Choice {choice_id} is just a verb form (should be full sentence)')
    
    if issues_found:
        print('  ⚠️  Potential issues:')
        for issue in issues_found:
            print(f'     • {issue}')
    else:
        print('  ✅ No obvious issues found')
    
    return 0

if __name__ == '__main__':
    exit(main())

