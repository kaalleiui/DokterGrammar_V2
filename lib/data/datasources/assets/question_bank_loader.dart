import 'dart:convert';
import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart';
import '../../../core/models/question.dart';
import '../../../core/builders/question_builder.dart';
import '../../../core/validators/question_validator.dart';

class QuestionBankLoader {
  static Future<List<Question>> loadQuestionsFromAssets() async {
    final List<Question> allQuestions = [];
    final List<String> validationErrors = [];
    final List<String> validationWarnings = [];
    int autoFixedCount = 0;
    
    // Load from multiple question bank files
    final List<String> bankFiles = [
      'assets/data/question_bank1.json',
      'assets/data/question_bank2.json',
      'assets/data/question_bank3.json',
      // Keep old file for backward compatibility
      'assets/data/question_bank.json',
    ];
    
    for (final filePath in bankFiles) {
      try {
        final String jsonString = await rootBundle.loadString(filePath);
        final List<dynamic> jsonData = json.decode(jsonString);
        // Use builder pattern for validation and auto-fix (Plan 5)
        final questions = <Question>[];
        
        for (final json in jsonData) {
          try {
            // Use builder which validates and auto-fixes
            final question = QuestionBuilder.fromJson(json);
            questions.add(question);
          } catch (e) {
            // Builder failed, try fallback
            try {
              final question = Question.fromJson(json);
              // Validate manually
              final validation = QuestionValidator.validate(question);
              if (validation.isValid) {
                questions.add(question);
              } else if (validation.issues.any((i) => i.canAutoFix)) {
                final fixed = QuestionValidator.autoFix(question, validation.issues);
                questions.add(fixed);
                autoFixedCount++;
                validationWarnings.add('${question.id}: Auto-fixed - ${validation.issues.map((i) => i.message).join('; ')}');
              } else {
                validationErrors.add('${question.id}: ${validation.issues.map((i) => i.message).join('; ')}');
              }
            } catch (e2) {
              validationErrors.add('Failed to parse question: $e2');
            }
          }
        }
        
        allQuestions.addAll(questions);
      } catch (e) {
        // File doesn't exist or can't be loaded, skip it
        if (kDebugMode) {
          debugPrint('Warning: Could not load $filePath: $e');
        }
        continue;
      }
    }
    
    // Log validation results
    if (kDebugMode) {
      if (autoFixedCount > 0) {
        debugPrint('🔧 Auto-fixed $autoFixedCount questions during load');
      }
      if (validationErrors.isNotEmpty) {
        debugPrint('❌ Question validation errors (${validationErrors.length}):');
        for (final error in validationErrors.take(10)) {
          debugPrint('  • $error');
        }
        if (validationErrors.length > 10) {
          debugPrint('  ... and ${validationErrors.length - 10} more errors');
        }
      }
      if (validationWarnings.isNotEmpty) {
        debugPrint('⚠️  Question validation warnings (${validationWarnings.length}):');
        for (final warning in validationWarnings.take(10)) {
          debugPrint('  • $warning');
        }
        if (validationWarnings.length > 10) {
          debugPrint('  ... and ${validationWarnings.length - 10} more warnings');
        }
      }
      if (validationErrors.isEmpty && validationWarnings.isEmpty && autoFixedCount == 0) {
        debugPrint('✅ All questions passed validation');
      }
    }
    
    // If no questions loaded, return sample questions
    if (allQuestions.isEmpty) {
      return _getSampleQuestions();
    }
    
    return allQuestions;
  }

  // Old validation method removed - now using QuestionValidator

  static List<Question> _getSampleQuestions() {
    // Return sample questions for testing
    return [
      Question(
        id: 'q_sample_1',
        type: 'multiple_choice',
        difficulty: 2,
        topicId: 1, // tenses
        prompt: 'Choose the correct form: "I _____ to the store yesterday."',
        answer: 'b',
        explanationTemplate: 'Use simple past tense for completed actions in the past.',
        exampleSentence: 'I went to the store yesterday.',
        choices: [
          QuestionChoice(choiceId: 'a', text: 'go', isCorrect: false),
          QuestionChoice(choiceId: 'b', text: 'went', isCorrect: true),
          QuestionChoice(choiceId: 'c', text: 'going', isCorrect: false),
          QuestionChoice(choiceId: 'd', text: 'gone', isCorrect: false),
        ],
        tags: [
          QuestionTag(tagType: 'tense', tagValue: 'past'),
          QuestionTag(tagType: 'grammar_point', tagValue: 'simple_past'),
        ],
      ),
      Question(
        id: 'q_sample_2',
        type: 'multiple_choice',
        difficulty: 3,
        topicId: 4, // complex_sentences
        prompt: 'Choose the best sentence combination: "The book was interesting. I read it last week."',
        answer: 'b',
        explanationTemplate: 'Use a relative clause to combine the sentences.',
        exampleSentence: 'The book that I read last week was interesting.',
        choices: [
          QuestionChoice(choiceId: 'a', text: 'The book was interesting, I read it last week.', isCorrect: false),
          QuestionChoice(choiceId: 'b', text: 'The book that I read last week was interesting.', isCorrect: true),
          QuestionChoice(choiceId: 'c', text: 'The book was interesting that I read last week.', isCorrect: false),
          QuestionChoice(choiceId: 'd', text: 'The book interesting I read last week.', isCorrect: false),
        ],
        tags: [
          QuestionTag(tagType: 'grammar_point', tagValue: 'relative_clause'),
        ],
      ),
    ];
  }
}

