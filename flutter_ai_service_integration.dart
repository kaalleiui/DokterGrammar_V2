// Flutter Integration for AI Explanation Server
// Add this to your AIService.dart or create a new service

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:dokter_grammar2/core/models/question.dart';

class AIExplanationService {
  // Server URL - change to your server IP/URL
  static const String serverUrl = 'http://localhost:5000';
  static const String generateEndpoint = '$serverUrl/generate';
  static const String healthEndpoint = '$serverUrl/health';
  
  static bool _serverAvailable = false;
  
  /// Check if AI server is available
  static Future<bool> checkServerHealth() async {
    try {
      final response = await http.get(
        Uri.parse(healthEndpoint),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 5));
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _serverAvailable = data['model_loaded'] == true;
        return _serverAvailable;
      }
      return false;
    } catch (e) {
      _serverAvailable = false;
      return false;
    }
  }
  
  /// Generate explanation using AI server
  static Future<Map<String, dynamic>> generateExplanation({
    required Question question,
    required String? userAnswer,
    required bool? isCorrect,
    required List<String> userInterests,
    Map<String, dynamic>? context,
  }) async {
    // Check server availability
    if (!_serverAvailable) {
      final isAvailable = await checkServerHealth();
      if (!isAvailable) {
        // Fallback to rule-based
        return _generateFallback(question, userAnswer, isCorrect);
      }
    }
    
    try {
      // Get grammar point from question tags
      final grammarPoint = question.tags
          .firstWhere(
            (tag) => tag.tagType == 'grammar_point',
            orElse: () => QuestionTag(tagType: '', tagValue: ''),
          )
          .tagValue;
      
      // Get correct answer text
      final correctAnswerText = _getCorrectAnswerText(question);
      
      // Prepare request data
      final requestData = {
        'prompt': question.prompt,
        'type': question.type,
        'grammar_point': grammarPoint.isNotEmpty ? grammarPoint : null,
        'user_answer': userAnswer ?? '',
        'correct_answer': correctAnswerText,
        'is_correct': isCorrect ?? false,
        'difficulty': question.difficulty,
        'example_sentence': question.exampleSentence,
        'max_length': 150,
        'temperature': 0.7,
        'top_p': 0.9,
      };
      
      // Call AI server
      final response = await http.post(
        Uri.parse(generateEndpoint),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(requestData),
      ).timeout(const Duration(seconds: 10));
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['success'] == true) {
          return {
            'text': data['text'],
            'type': data['type'] ?? 'ai_generated',
            'confidence': data['confidence'] ?? 0.85,
            'rule_applied': data['rule_applied'],
            'example': data['example'],
            'follow_up_available': data['follow_up_available'] ?? false,
            'related_topics': data['related_topics'] ?? [],
            'generation_time_ms': data['generation_time_ms'] ?? 0,
          };
        }
      }
      
      // If AI fails, fallback to rule-based
      return _generateFallback(question, userAnswer, isCorrect);
    } catch (e) {
      // On error, fallback to rule-based
      return _generateFallback(question, userAnswer, isCorrect);
    }
  }
  
  /// Get correct answer text from question
  static String _getCorrectAnswerText(Question question) {
    final answer = question.answer;
    final choices = question.choices;
    
    // Try to find correct choice
    for (final choice in choices) {
      if (choice.isCorrect) {
        return choice.text;
      }
    }
    
    // Try to find by answer field
    for (final choice in choices) {
      if (choice.choiceId.toLowerCase() == answer.toLowerCase()) {
        return choice.text;
      }
    }
    
    // Fallback to answer field
    return answer;
  }
  
  /// Fallback to rule-based explanation
  static Map<String, dynamic> _generateFallback(
    Question question,
    String? userAnswer,
    bool? isCorrect,
  ) {
    // Import and use your existing ExplanationService
    // This is a placeholder - replace with actual fallback
    return {
      'text': 'Using rule-based explanation (AI server unavailable)',
      'type': 'rule_based',
      'confidence': 1.0,
      'rule_applied': null,
      'example': question.exampleSentence,
      'follow_up_available': false,
      'related_topics': [],
      'generation_time_ms': 0,
    };
  }
}

