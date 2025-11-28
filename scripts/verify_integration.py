#!/usr/bin/env python3
"""
Comprehensive Integration Verification
Checks all components are connected and working properly
"""

import json
from pathlib import Path
from collections import defaultdict

def check_ai_explanations_file():
    """Check AI explanations file exists and is valid"""
    print("=" * 60)
    print("1. Checking AI Explanations File")
    print("=" * 60)
    
    file_path = Path("assets/data/ai_explanations.json")
    if not file_path.exists():
        print("❌ File not found: assets/data/ai_explanations.json")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, dict):
            print("❌ Invalid format: Expected dict")
            return False
        
        size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"✅ File exists: {file_path}")
        print(f"✅ Size: {size_mb:.2f} MB")
        print(f"✅ Questions with explanations: {len(data)}")
        
        # Check structure
        sample_key = list(data.keys())[0] if data else None
        if sample_key:
            sample = data[sample_key]
            if 'correct' in sample and 'incorrect' in sample:
                print("✅ Structure valid: Has 'correct' and 'incorrect' keys")
            else:
                print("⚠️  Structure warning: Missing expected keys")
        
        return True
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return False

def check_question_banks():
    """Check question bank files are valid and fixed"""
    print("\n" + "=" * 60)
    print("2. Checking Question Bank Files")
    print("=" * 60)
    
    assets_dir = Path("assets/data")
    bank_files = [
        'question_bank.json',
        'question_bank1.json',
        'question_bank2.json',
        'question_bank3.json',
    ]
    
    all_questions = []
    question_ids = set()
    
    for bank_file in bank_files:
        file_path = assets_dir / bank_file
        if not file_path.exists():
            print(f"⚠️  File not found: {bank_file}")
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_questions.extend(data)
                    for q in data:
                        q_id = q.get('id')
                        if q_id:
                            if q_id in question_ids:
                                print(f"⚠️  Duplicate question ID: {q_id}")
                            question_ids.add(q_id)
                    print(f"✅ {bank_file}: {len(data)} questions")
        except Exception as e:
            print(f"❌ Error loading {bank_file}: {e}")
            return False
    
    print(f"✅ Total questions: {len(all_questions)}")
    print(f"✅ Unique question IDs: {len(question_ids)}")
    
    # Check for mismatches
    mismatches = 0
    for question in all_questions:
        answer = question.get('answer', '').lower()
        choices = question.get('choices', [])
        correct_choices = [c for c in choices if c.get('isCorrect', False)]
        
        if correct_choices:
            correct_id = correct_choices[0].get('choiceId', '').lower()
            if answer != correct_id:
                mismatches += 1
    
    if mismatches == 0:
        print("✅ No answer mismatches found")
    else:
        print(f"⚠️  Found {mismatches} potential mismatches")
    
    return True, question_ids

def check_explanation_coverage(question_ids):
    """Check if all questions have AI explanations"""
    print("\n" + "=" * 60)
    print("3. Checking Explanation Coverage")
    print("=" * 60)
    
    file_path = Path("assets/data/ai_explanations.json")
    if not file_path.exists():
        print("❌ AI explanations file not found")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        explanations = json.load(f)
    
    explanation_ids = set(explanations.keys())
    
    missing = question_ids - explanation_ids
    extra = explanation_ids - question_ids
    
    print(f"✅ Questions in banks: {len(question_ids)}")
    print(f"✅ Explanations available: {len(explanation_ids)}")
    
    if missing:
        print(f"⚠️  Missing explanations: {len(missing)}")
        for q_id in list(missing)[:5]:
            print(f"    - {q_id}")
        if len(missing) > 5:
            print(f"    ... and {len(missing) - 5} more")
    else:
        print("✅ All questions have explanations")
    
    if extra:
        print(f"⚠️  Extra explanations (not in banks): {len(extra)}")
        for q_id in list(extra)[:5]:
            print(f"    - {q_id}")
    
    coverage = (len(explanation_ids & question_ids) / len(question_ids) * 100) if question_ids else 0
    print(f"✅ Coverage: {coverage:.1f}%")
    
    return len(missing) == 0

def check_aiservice_code():
    """Check AIService code is correct"""
    print("\n" + "=" * 60)
    print("4. Checking AIService Code")
    print("=" * 60)
    
    file_path = Path("lib/core/services/ai_service.dart")
    if not file_path.exists():
        print("❌ AIService file not found")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('rootBundle.loadString', 'Loads JSON from assets'),
        ('assets/data/ai_explanations.json', 'Correct file path'),
        ('_getAIExplanation', 'Has lookup method'),
        ('_generateRuleBasedExplanation', 'Has fallback method'),
        ('isCorrect == true', 'Handles correct answers'),
        ('incorrect.containsKey', 'Handles incorrect answers'),
    ]
    
    all_pass = True
    for check, desc in checks:
        if check in content:
            print(f"✅ {desc}")
        else:
            print(f"❌ Missing: {desc}")
            all_pass = False
    
    return all_pass

def check_pubspec_assets():
    """Check pubspec.yaml includes assets"""
    print("\n" + "=" * 60)
    print("5. Checking pubspec.yaml Assets")
    print("=" * 60)
    
    file_path = Path("pubspec.yaml")
    if not file_path.exists():
        print("❌ pubspec.yaml not found")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'assets/data/' in content:
        print("✅ assets/data/ included in assets")
    else:
        print("❌ assets/data/ NOT included in assets")
        return False
    
    return True

def check_explanation_structure():
    """Check explanation structure matches AIService expectations"""
    print("\n" + "=" * 60)
    print("6. Checking Explanation Structure")
    print("=" * 60)
    
    file_path = Path("assets/data/ai_explanations.json")
    with open(file_path, 'r', encoding='utf-8') as f:
        explanations = json.load(f)
    
    issues = []
    for q_id, data in list(explanations.items())[:10]:  # Check first 10
        if not isinstance(data, dict):
            issues.append(f"{q_id}: Not a dict")
            continue
        
        if 'correct' not in data:
            issues.append(f"{q_id}: Missing 'correct' key")
        
        if 'incorrect' not in data:
            issues.append(f"{q_id}: Missing 'incorrect' key")
        elif not isinstance(data['incorrect'], dict):
            issues.append(f"{q_id}: 'incorrect' should be dict")
    
    if issues:
        print(f"⚠️  Found {len(issues)} structure issues:")
        for issue in issues[:5]:
            print(f"    - {issue}")
    else:
        print("✅ Structure is correct")
    
    return len(issues) == 0

def main():
    print("\n" + "=" * 60)
    print("COMPREHENSIVE INTEGRATION VERIFICATION")
    print("=" * 60)
    
    results = {}
    
    # Run all checks
    results['ai_file'] = check_ai_explanations_file()
    results['question_banks'], question_ids = check_question_banks()
    results['coverage'] = check_explanation_coverage(question_ids)
    results['aiservice'] = check_aiservice_code()
    results['pubspec'] = check_pubspec_assets()
    results['structure'] = check_explanation_structure()
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    all_pass = all(results.values())
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check}")
    
    print("\n" + "=" * 60)
    if all_pass:
        print("✅ ALL CHECKS PASSED - Integration is ready!")
    else:
        print("⚠️  SOME CHECKS FAILED - Review issues above")
    print("=" * 60)
    
    return all_pass

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

