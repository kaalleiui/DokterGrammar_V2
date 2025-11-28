#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master Fix Tool
Comprehensive tool to identify and fix choice mismatches
"""

import json
import sys
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def count_words(text: str) -> int:
    """Count words in text"""
    return len(text.strip().split())

def is_likely_sentence(text: str) -> bool:
    """Check if text is likely a complete sentence"""
    text = text.strip()
    if not text:
        return False
    
    word_count = count_words(text)
    if word_count <= 2:
        return False
    
    if text[0].isupper() and text[-1] in '.!?':
        return True
    
    if word_count >= 4:
        words = text.split()
        has_article = words[0].lower() in ['a', 'an', 'the']
        common_verbs = ['is', 'are', 'was', 'were', 'has', 'have', 'had', 'will', 'would']
        has_verb = any(v in text.lower() for v in common_verbs)
        if has_article and has_verb:
            return True
    
    return False

def analyze_question(question: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze a question and return list of issues with suggested fixes"""
    issues = []
    q_id = question.get('id', 'unknown')
    q_type = question.get('type', '')
    prompt = question.get('prompt', '')
    choices = question.get('choices', [])
    source_file = question.get('_source_file', 'unknown')
    
    if not choices:
        return issues
    
    prompt_lower = prompt.lower()
    
    # Check gap fill questions
    if q_type == 'gap_fill':
        for choice in choices:
            choice_id = choice.get('choiceId', '')
            choice_text = choice.get('text', '').strip()
            word_count = count_words(choice_text)
            
            # Issue: Full sentence in gap fill
            if word_count >= 5 or (word_count >= 4 and is_likely_sentence(choice_text)):
                # Try to suggest a fix
                suggested_fix = suggest_gap_fill_fix(choice_text, prompt)
                
                issues.append({
                    'question_id': q_id,
                    'source_file': source_file,
                    'choice_id': choice_id,
                    'current_text': choice_text,
                    'issue_type': 'gap_fill_full_sentence',
                    'severity': 'high',
                    'word_count': word_count,
                    'suggested_fix': suggested_fix,
                    'can_auto_fix': suggested_fix is not None,
                })
            
            # Issue: Starts with article
            elif word_count >= 4 and choice_text.lower().startswith(('a ', 'an ', 'the ')):
                common_phrases = ['a lot', 'a few', 'a little', 'a bit', 'the same', 'the most', 'the least']
                if not any(choice_text.lower().startswith(phrase) for phrase in common_phrases):
                    suggested_fix = suggest_gap_fill_fix(choice_text, prompt)
                    issues.append({
                        'question_id': q_id,
                        'source_file': source_file,
                        'choice_id': choice_id,
                        'current_text': choice_text,
                        'issue_type': 'gap_fill_starts_with_article',
                        'severity': 'medium',
                        'word_count': word_count,
                        'suggested_fix': suggested_fix,
                        'can_auto_fix': suggested_fix is not None,
                    })
    
    # Check transformation questions
    is_transformation = any(keyword in prompt_lower for keyword in [
        'change', 'transform', 'convert', 'rewrite', 'rephrase', 'change this', 'change into'
    ])
    
    if is_transformation:
        for choice in choices:
            choice_id = choice.get('choiceId', '')
            choice_text = choice.get('text', '').strip()
            word_count = count_words(choice_text)
            
            # Issue: Just verb form
            if word_count <= 2:
                verb_forms = ['is', 'are', 'was', 'were', 'be', 'been', 'being', 'has', 'have', 'had',
                             'will', 'would', 'can', 'could', 'should', 'must', 'may', 'might']
                words = choice_text.lower().split()
                if choice_text.lower() in verb_forms or (word_count == 2 and words[0].lower() in verb_forms):
                    issues.append({
                        'question_id': q_id,
                        'source_file': source_file,
                        'choice_id': choice_id,
                        'current_text': choice_text,
                        'issue_type': 'transformation_verb_form_only',
                        'severity': 'high',
                        'word_count': word_count,
                        'suggested_fix': None,  # Can't auto-fix transformation
                        'can_auto_fix': False,
                    })
    
    return issues

def suggest_gap_fill_fix(choice_text: str, prompt: str) -> Optional[str]:
    """Suggest a fix for gap fill choice"""
    # Extract sentence with blank
    blank_match = re.search(r"Fill in the blank:\s*['\"](.*?)['\"]", prompt, re.IGNORECASE)
    if not blank_match:
        return None
    
    sentence_with_blank = blank_match.group(1).lower()
    choice_lower = choice_text.lower()
    
    # Try to extract relevant word/phrase
    # Check for common patterns
    
    # Passive voice patterns
    if 'built' in sentence_with_blank or 'built' in choice_lower:
        if 'has been' in choice_lower:
            return 'has been'
        elif 'will be' in choice_lower:
            return 'will be'
        elif 'is being' in choice_lower:
            return 'is being'
        elif 'was' in choice_lower and 'was built' in choice_lower:
            return 'was'
        elif 'is' in choice_lower:
            return 'is'
    
    # Verb forms
    verb_forms = ['is', 'are', 'was', 'were', 'has', 'have', 'had', 'will', 'would',
                 'can', 'could', 'should', 'must', 'may', 'might', 'be', 'been', 'being']
    
    words = choice_text.split()
    for word in words:
        if word.lower() in verb_forms:
            return word
    
    # Try to find 2-word phrases
    if len(words) >= 2:
        two_word_phrases = ['will be', 'has been', 'had been', 'is being', 'was being',
                           'can be', 'could be', 'should be', 'must be', 'may be',
                           'will have', 'would have', 'should have', 'could have']
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}"
            if phrase.lower() in two_word_phrases:
                return phrase
    
    return None

def fix_question(question: Dict[str, Any], issue: Dict[str, Any]) -> bool:
    """Fix a specific issue in a question"""
    choice_id = issue['choice_id']
    new_text = issue['suggested_fix']
    
    if not new_text:
        return False
    
    choices = question.get('choices', [])
    for choice in choices:
        if choice.get('choiceId') == choice_id:
            choice['text'] = new_text
            return True
    
    return False

def load_all_questions() -> List[Dict[str, Any]]:
    """Load all questions from JSON files"""
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
    
    return all_questions

def save_question(question: Dict[str, Any]) -> bool:
    """Save question back to file"""
    source_file = question.get('_source_file')
    if not source_file:
        return False
    
    file_path = Path('assets/data') / source_file
    if not file_path.exists():
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            return False
        
        updated = False
        for i, q in enumerate(data):
            if q.get('id') == question.get('id'):
                question_copy = question.copy()
                question_copy.pop('_source_file', None)
                data[i] = question_copy
                updated = True
                break
        
        if not updated:
            return False
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f'Error saving: {e}')
        return False

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Master tool to identify and fix choice mismatches')
    parser.add_argument('--check', action='store_true', help='Only check, don\'t fix')
    parser.add_argument('--fix', action='store_true', help='Auto-fix issues that can be fixed')
    parser.add_argument('--report', type=str, help='Save report to file')
    args = parser.parse_args()
    
    print('=' * 80)
    print('MASTER FIX TOOL - Choice Mismatch Detection & Fix')
    print('=' * 80)
    
    all_questions = load_all_questions()
    print(f'\n📋 Loaded {len(all_questions)} questions\n')
    
    all_issues = []
    questions_by_id = {}
    
    for question in all_questions:
        q_id = question.get('id')
        questions_by_id[q_id] = question
        issues = analyze_question(question)
        all_issues.extend(issues)
    
    if not all_issues:
        print('✅ No issues found! All choices are correct.')
        return 0
    
    print(f'🔴 Found {len(all_issues)} issues:\n')
    
    # Group by type
    issues_by_type = {}
    auto_fixable = []
    manual_fix = []
    
    for issue in all_issues:
        issue_type = issue['issue_type']
        if issue_type not in issues_by_type:
            issues_by_type[issue_type] = []
        issues_by_type[issue_type].append(issue)
        
        if issue.get('can_auto_fix'):
            auto_fixable.append(issue)
        else:
            manual_fix.append(issue)
    
    # Print summary
    print(f'  High severity: {sum(1 for i in all_issues if i["severity"] == "high")}')
    print(f'  Medium severity: {sum(1 for i in all_issues if i["severity"] == "medium")}')
    print(f'  Auto-fixable: {len(auto_fixable)}')
    print(f'  Manual fix required: {len(manual_fix)}\n')
    
    # Show issues
    for issue_type, issues in sorted(issues_by_type.items()):
        print(f'\n{issue_type.replace("_", " ").title()} ({len(issues)} issues):')
        print('-' * 80)
        
        for issue in issues[:10]:
            print(f'\n  Question ID: {issue["question_id"]} ({issue["source_file"]})')
            print(f'  Choice {issue["choice_id"]}: "{issue["current_text"]}" ({issue["word_count"]} words)')
            if issue.get('suggested_fix'):
                print(f'  Suggested fix: "{issue["suggested_fix"]}"')
            else:
                print(f'  ⚠️  Manual fix required')
        
        if len(issues) > 10:
            print(f'\n  ... and {len(issues) - 10} more')
    
    # Auto-fix if requested
    if args.fix and auto_fixable:
        print(f'\n\n🔧 Auto-fixing {len(auto_fixable)} issues...')
        fixed_count = 0
        files_modified = set()
        
        for issue in auto_fixable:
            q_id = issue['question_id']
            question = questions_by_id.get(q_id)
            if not question:
                continue
            
            if fix_question(question, issue):
                if save_question(question):
                    fixed_count += 1
                    files_modified.add(issue['source_file'])
                    print(f'  ✓ Fixed {q_id} choice {issue["choice_id"]}: "{issue["current_text"]}" -> "{issue["suggested_fix"]}"')
        
        print(f'\n✅ Fixed {fixed_count} issues in {len(files_modified)} file(s)')
        print(f'   Files modified: {", ".join(files_modified)}')
    
    # Save report
    if args.report:
        report = {
            'total_questions': len(all_questions),
            'total_issues': len(all_issues),
            'auto_fixable': len(auto_fixable),
            'manual_fix': len(manual_fix),
            'issues_by_type': {k: len(v) for k, v in issues_by_type.items()},
            'all_issues': all_issues,
        }
        
        with open(args.report, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f'\n✅ Report saved to {args.report}')
    
    if manual_fix:
        print(f'\n⚠️  {len(manual_fix)} issues require manual fix')
        print('   Review the issues above and fix them manually')
    
    return 0 if not all_issues else 1

if __name__ == '__main__':
    exit(main())

