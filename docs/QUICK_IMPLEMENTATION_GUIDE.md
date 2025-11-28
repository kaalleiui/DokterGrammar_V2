# Quick Implementation Guide: Real-Time Validation & Auto-Fix

## Overview
Implementasi Opsi 3: Real-Time Validation & Monitoring System

**Goal**: Detect dan auto-fix mismatch pertanyaan-opsi setiap kali question di-load

---

## Step 1: Buat Question Validator

Buat file baru: `lib/core/validators/question_validator.dart`

```dart
import '../models/question.dart';
import 'package:flutter/foundation.dart';

class ValidationResult {
  final bool isValid;
  final List<String> issues;
  final Question question;

  ValidationResult({
    required this.isValid,
    required this.issues,
    required this.question,
  });
}

class QuestionValidator {
  /// Validate question saat di-load
  static ValidationResult validateOnLoad(Question question) {
    final issues = <String>[];
    
    // Check 1: Multiple choice harus punya choices
    if (question.type == 'multiple_choice' && question.choices.isEmpty) {
      issues.add('Multiple choice question has no choices');
    }
    
    // Check 2: Answer harus match dengan salah satu choiceId
    if (question.choices.isNotEmpty) {
      final answerMatches = question.choices.any(
        (c) => c.choiceId.toLowerCase().trim() == question.answer.toLowerCase().trim(),
      );
      if (!answerMatches) {
        issues.add('Answer "${question.answer}" does not match any choiceId');
      }
    }
    
    // Check 3: Harus ada tepat 1 correct choice
    final correctChoices = question.choices.where((c) => c.isCorrect).toList();
    if (correctChoices.isEmpty) {
      issues.add('No choice marked as correct');
    } else if (correctChoices.length > 1) {
      issues.add('Multiple choices marked as correct (${correctChoices.length})');
    } else {
      // Check 4: Correct choice harus match dengan answer
      final correctChoice = correctChoices.first;
      if (correctChoice.choiceId.toLowerCase().trim() != question.answer.toLowerCase().trim()) {
        issues.add('Answer "${question.answer}" does not match correct choice "${correctChoice.choiceId}"');
      }
    }
    
    return ValidationResult(
      isValid: issues.isEmpty,
      issues: issues,
      question: question,
    );
  }
  
  /// Auto-fix common issues
  static Question? autoFix(Question question, ValidationResult validation) {
    if (validation.isValid) return question;
    
    final issues = validation.issues;
    Question? fixed = question;
    
    // Fix 1: Answer tidak match, tapi ada correct choice
    if (issues.any((i) => i.contains('does not match correct choice'))) {
      final correctChoice = question.choices.firstWhere(
        (c) => c.isCorrect,
        orElse: () => QuestionChoice(choiceId: '', text: ''),
      );
      if (correctChoice.choiceId.isNotEmpty) {
        // Update answer untuk match correct choice
        fixed = Question(
          id: question.id,
          type: question.type,
          difficulty: question.difficulty,
          topicId: question.topicId,
          prompt: question.prompt,
          answer: correctChoice.choiceId, // FIX: Update answer
          explanationTemplate: question.explanationTemplate,
          exampleSentence: question.exampleSentence,
          choices: question.choices,
          tags: question.tags,
        );
        
        if (kDebugMode) {
          debugPrint('✅ Auto-fixed: Updated answer from "${question.answer}" to "${correctChoice.choiceId}"');
        }
      }
    }
    
    // Fix 2: Tidak ada correct choice, tapi answer match dengan choiceId
    if (issues.any((i) => i.contains('No choice marked'))) {
      final matchingChoice = question.choices.firstWhere(
        (c) => c.choiceId.toLowerCase().trim() == question.answer.toLowerCase().trim(),
        orElse: () => QuestionChoice(choiceId: '', text: ''),
      );
      if (matchingChoice.choiceId.isNotEmpty) {
        // Mark matching choice sebagai correct
        final fixedChoices = question.choices.map((c) {
          return QuestionChoice(
            choiceId: c.choiceId,
            text: c.text,
            isCorrect: c.choiceId.toLowerCase().trim() == question.answer.toLowerCase().trim(),
          );
        }).toList();
        
        fixed = Question(
          id: question.id,
          type: question.type,
          difficulty: question.difficulty,
          topicId: question.topicId,
          prompt: question.prompt,
          answer: question.answer,
          explanationTemplate: question.explanationTemplate,
          exampleSentence: question.exampleSentence,
          choices: fixedChoices,
          tags: question.tags,
        );
        
        if (kDebugMode) {
          debugPrint('✅ Auto-fixed: Marked choice "${matchingChoice.choiceId}" as correct');
        }
      }
    }
    
    // Fix 3: Multiple correct choices, pilih yang match dengan answer
    if (issues.any((i) => i.contains('Multiple choices marked'))) {
      final matchingChoice = question.choices.firstWhere(
        (c) => c.choiceId.toLowerCase().trim() == question.answer.toLowerCase().trim(),
        orElse: () => QuestionChoice(choiceId: '', text: ''),
      );
      if (matchingChoice.choiceId.isNotEmpty) {
        // Unset semua isCorrect, set hanya yang match answer
        final fixedChoices = question.choices.map((c) {
          return QuestionChoice(
            choiceId: c.choiceId,
            text: c.text,
            isCorrect: c.choiceId.toLowerCase().trim() == question.answer.toLowerCase().trim(),
          );
        }).toList();
        
        fixed = Question(
          id: question.id,
          type: question.type,
          difficulty: question.difficulty,
          topicId: question.topicId,
          prompt: question.prompt,
          answer: question.answer,
          explanationTemplate: question.explanationTemplate,
          exampleSentence: question.exampleSentence,
          choices: fixedChoices,
          tags: question.tags,
        );
        
        if (kDebugMode) {
          debugPrint('✅ Auto-fixed: Set only choice "${matchingChoice.choiceId}" as correct');
        }
      }
    }
    
    return fixed;
  }
}
```

---

## Step 2: Update Question Local Datasource

Update file: `lib/data/datasources/local/question_local_datasource.dart`

Tambahkan import di bagian atas:
```dart
import '../../../core/validators/question_validator.dart';
```

Update method `getQuestionById()`:
```dart
Future<Question?> getQuestionById(String questionId) async {
  final db = await _dbHelper.database;
  
  // ... existing code untuk load question dari database ...
  
  // SETELAH load question, tambahkan validasi:
  
  // Validate question
  final validation = QuestionValidator.validateOnLoad(question);
  
  if (!validation.isValid) {
    // Log issues
    if (kDebugMode) {
      debugPrint('⚠️ Question ${question.id} has validation issues:');
      for (final issue in validation.issues) {
        debugPrint('  - $issue');
      }
    }
    
    // Try auto-fix
    final fixed = QuestionValidator.autoFix(question, validation);
    if (fixed != null) {
      if (kDebugMode) {
        debugPrint('✅ Auto-fixed question ${question.id}');
      }
      // Return fixed version
      return fixed;
    } else {
      // Cannot fix, log error
      if (kDebugMode) {
        debugPrint('❌ Cannot auto-fix question ${question.id}, returning as-is with issues');
      }
      // Option: return null untuk skip question yang corrupt
      // return null;
      // Atau: return question as-is (dengan warning)
      return question;
    }
  }
  
  return question;
}
```

Update juga method `getQuestionsByTopic()` dengan validasi yang sama.

---

## Step 3: Update Question Bank Loader

Update file: `lib/data/datasources/assets/question_bank_loader.dart`

Tambahkan import:
```dart
import '../../../core/validators/question_validator.dart';
```

Update method `loadQuestionsFromAssets()`:
```dart
// Di dalam loop setelah load questions dari JSON:
for (final question in questions) {
  // Existing validation
  final validation = _validateQuestion(question);
  
  // TAMBAHKAN: Real-time validation
  final realTimeValidation = QuestionValidator.validateOnLoad(question);
  
  if (!realTimeValidation.isValid) {
    // Try auto-fix
    final fixed = QuestionValidator.autoFix(question, realTimeValidation);
    if (fixed != null) {
      // Use fixed version
      allQuestions.add(fixed);
      if (kDebugMode) {
        debugPrint('✅ Auto-fixed question ${question.id} during load');
      }
    } else {
      // Cannot fix, skip atau add dengan warning
      if (validation.isValid) {
        // Original validation pass, tapi real-time validation fail
        // Add dengan warning
        validationWarnings.add('${question.id}: Real-time validation failed: ${realTimeValidation.issues.join(", ")}');
        allQuestions.add(question);
      } else {
        // Both validations fail, skip
        validationErrors.add('${question.id}: ${validation.message} + Real-time: ${realTimeValidation.issues.join(", ")}');
      }
    }
  } else {
    // Real-time validation pass
    if (validation.isValid) {
      allQuestions.add(question);
    } else {
      // Original validation fail, tapi real-time pass (shouldn't happen)
      validationWarnings.add('${question.id}: ${validation.message}');
      allQuestions.add(question);
    }
  }
}
```

---

## Step 4: Test Implementation

Buat test script: `test_validation_fix.py`

```python
#!/usr/bin/env python3
"""Test validation and auto-fix"""

import json
from pathlib import Path

def test_validation():
    """Test semua questions dengan validation logic"""
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
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                all_questions.extend(data)
    
    print(f'Testing {len(all_questions)} questions...\n')
    
    issues_found = 0
    auto_fixable = 0
    
    for question in all_questions:
        q_id = question.get('id', 'unknown')
        answer = question.get('answer', '').lower().strip()
        choices = question.get('choices', [])
        
        if not choices:
            continue
        
        # Check 1: Answer matches choiceId
        choice_ids = [c.get('choiceId', '').lower().strip() for c in choices]
        if answer not in choice_ids:
            issues_found += 1
            print(f'❌ {q_id}: Answer "{answer}" not in choices')
            # Check if can auto-fix
            correct_choices = [c for c in choices if c.get('isCorrect')]
            if correct_choices:
                correct_id = correct_choices[0].get('choiceId', '').lower().strip()
                print(f'   → Can auto-fix: Update answer to "{correct_id}"')
                auto_fixable += 1
            print()
        
        # Check 2: Exactly one correct choice
        correct_choices = [c for c in choices if c.get('isCorrect')]
        if len(correct_choices) == 0:
            issues_found += 1
            print(f'❌ {q_id}: No correct choice')
            # Check if can auto-fix
            if answer in choice_ids:
                print(f'   → Can auto-fix: Mark "{answer}" as correct')
                auto_fixable += 1
            print()
        elif len(correct_choices) > 1:
            issues_found += 1
            print(f'❌ {q_id}: Multiple correct choices ({len(correct_choices)})')
            # Check if can auto-fix
            if answer in choice_ids:
                print(f'   → Can auto-fix: Set only "{answer}" as correct')
                auto_fixable += 1
            print()
        else:
            # Check 3: Correct choice matches answer
            correct_id = correct_choices[0].get('choiceId', '').lower().strip()
            if correct_id != answer:
                issues_found += 1
                print(f'❌ {q_id}: Answer "{answer}" != correct choice "{correct_id}"')
                print(f'   → Can auto-fix: Update answer to "{correct_id}"')
                auto_fixable += 1
                print()
    
    print('=' * 70)
    print(f'Total issues found: {issues_found}')
    print(f'Auto-fixable: {auto_fixable}')
    print(f'Cannot fix: {issues_found - auto_fixable}')
    print('=' * 70)

if __name__ == '__main__':
    test_validation()
```

Run test:
```bash
python test_validation_fix.py
```

---

## Step 5: Monitoring & Logging

Tambahkan logging untuk track issues:

```dart
class QuestionValidationLogger {
  static final List<ValidationLog> _logs = [];
  
  static void log(Question question, ValidationResult validation, {Question? fixed}) {
    _logs.add(ValidationLog(
      questionId: question.id,
      timestamp: DateTime.now(),
      issues: validation.issues,
      wasFixed: fixed != null,
    ));
    
    // Optionally: Save to database or file
  }
  
  static Map<String, dynamic> getStats() {
    final total = _logs.length;
    final fixed = _logs.where((l) => l.wasFixed).length;
    final unfixable = total - fixed;
    
    return {
      'total_validations': total,
      'issues_found': total,
      'auto_fixed': fixed,
      'unfixable': unfixable,
      'fix_rate': total > 0 ? (fixed / total) : 0.0,
    };
  }
}

class ValidationLog {
  final String questionId;
  final DateTime timestamp;
  final List<String> issues;
  final bool wasFixed;
  
  ValidationLog({
    required this.questionId,
    required this.timestamp,
    required this.issues,
    required this.wasFixed,
  });
}
```

---

## Testing Checklist

- [ ] Validator detect semua jenis mismatch
- [ ] Auto-fix benar-benar fix masalah
- [ ] Tidak break existing functionality
- [ ] Logging bekerja dengan baik
- [ ] Test dengan semua 208 questions
- [ ] Test di production environment

---

## Expected Results

Setelah implementasi:
- ✅ Semua questions di-validate saat load
- ✅ Issues terdeteksi dan di-log
- ✅ Auto-fixable issues langsung di-fix
- ✅ User tidak melihat mismatch lagi
- ✅ Monitoring data tersedia untuk tracking

---

**Status**: ✅ READY TO IMPLEMENT  
**Estimated Time**: 2-3 hari  
**Priority**: 🔴 CRITICAL

