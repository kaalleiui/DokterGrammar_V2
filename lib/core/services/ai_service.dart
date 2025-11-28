import 'dart:convert';
import 'package:flutter/services.dart';
import '../models/question.dart';
import 'explanation_service.dart';

/// AI Service for on-device model inference
/// Uses pre-generated AI explanations from JSON file
/// Falls back to rule-based explanations if AI explanations not available
class AIService {
  static bool _modelAvailable = false;
  static Map<String, dynamic>? _modelConfig;
  static Map<String, dynamic>? _aiExplanations;

  /// Initialize AI service (load pre-generated explanations from JSON)
  static Future<void> initialize() async {
    try {
      // Try to load pre-generated AI explanations
      final jsonString = await rootBundle.loadString('assets/data/ai_explanations.json');
      _aiExplanations = json.decode(jsonString) as Map<String, dynamic>;
      _modelAvailable = true;
      _modelConfig = {
        'model_name': 'grammar_explainer_v1',
        'model_type': 'pre_generated_json',
        'fallback_to_template': true,
        'explanations_count': _aiExplanations?.length ?? 0,
      };
      print('[AIService] Loaded ${_aiExplanations?.length ?? 0} AI explanations');
    } catch (e) {
      print('[AIService] Failed to load AI explanations: $e');
      _modelAvailable = false;
      _aiExplanations = null;
      _modelConfig = {'fallback_to_template': true};
    }
  }

  /// Generate explanation using AI model (or fallback to rule-based)
  static Future<Map<String, dynamic>> generateExplanation({
    required Question question,
    required String? userAnswer,
    required bool? isCorrect,
    required List<String> userInterests,
    Map<String, dynamic>? context,
  }) async {
    // Try to get AI-generated explanation first
    if (_modelAvailable && _aiExplanations != null) {
      final aiExplanation = _getAIExplanation(
        question: question,
        userAnswer: userAnswer,
        isCorrect: isCorrect,
      );
      
      if (aiExplanation != null) {
        return {
          'text': aiExplanation,
          'type': 'ai_generated',
          'confidence': 0.9,
          'rule_applied': _getRuleIdFromQuestion(question),
          'example': question.exampleSentence,
          'follow_up_available': false,
          'related_topics': _getRelatedTopics(question),
          'generation_time_ms': 0, // Instant lookup
        };
      }
    }

    // Fallback to rule-based explanation
    return _generateRuleBasedExplanation(
      question: question,
      userAnswer: userAnswer,
      isCorrect: isCorrect,
    );
  }

  /// Get AI-generated explanation from pre-generated JSON
  static String? _getAIExplanation({
    required Question question,
    required String? userAnswer,
    required bool? isCorrect,
  }) {
    if (_aiExplanations == null) {
      return null;
    }

    final questionId = question.id;
    final questionData = _aiExplanations![questionId];

    if (questionData == null || questionData is! Map<String, dynamic>) {
      return null;
    }

    try {
      if (isCorrect == true) {
        // Return explanation for correct answer
        return questionData['correct'] as String?;
      } else {
        // Return explanation for incorrect answer
        final incorrect = questionData['incorrect'];
        if (incorrect != null && incorrect is Map<String, dynamic>) {
          // Try to get explanation for specific wrong answer
          if (userAnswer != null && incorrect.containsKey(userAnswer)) {
            return incorrect[userAnswer] as String?;
          }
          // Fallback to first incorrect explanation if available
          if (incorrect.isNotEmpty) {
            return incorrect.values.first as String?;
          }
        }
      }
    } catch (e) {
      print('[AIService] Error getting AI explanation: $e');
    }

    return null;
  }

  /// Generate rule-based explanation (fallback)
  static Map<String, dynamic> _generateRuleBasedExplanation({
    required Question question,
    required String? userAnswer,
    required bool? isCorrect,
  }) {
    final explanationService = ExplanationService();
    final explanation = explanationService.generateExplanation(
      question: question,
      userAnswer: userAnswer,
      isCorrect: isCorrect,
    );

    return {
      'text': explanation,
      'type': 'rule_based',
      'confidence': 1.0,
      'rule_applied': _getRuleIdFromQuestion(question),
      'example': question.exampleSentence,
      'follow_up_available': false,
      'related_topics': _getRelatedTopics(question),
      'generation_time_ms': 0,
    };
  }

  /// Get rule ID from question tags
  static String? _getRuleIdFromQuestion(Question question) {
    final grammarPointTag = question.tags.firstWhere(
      (tag) => tag.tagType == 'grammar_point',
      orElse: () => QuestionTag(tagType: '', tagValue: ''),
    );
    return grammarPointTag.tagValue.isNotEmpty ? grammarPointTag.tagValue : null;
  }

  /// Get related topics from question tags
  static List<String> _getRelatedTopics(Question question) {
    return question.tags
        .where((tag) => tag.tagType == 'grammar_point' || tag.tagType == 'topic')
        .map((tag) => tag.tagValue)
        .toList();
  }

  /// Check if AI model is available
  static bool get isModelAvailable => _modelAvailable;

  /// Get model configuration
  static Map<String, dynamic>? get modelConfig => _modelConfig;
}

