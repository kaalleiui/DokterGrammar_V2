import '../constants/app_constants.dart';
import '../models/test_session.dart';
import '../models/question.dart';
import '../models/standardized_answer.dart';

class ScoringService {
  /// Calculate overall score from test attempts
  static double calculateScore(List<TestAttempt> attempts) {
    if (attempts.isEmpty) return 0.0;
    
    final correctCount = attempts.where((a) => a.isCorrect == true).length;
    return correctCount / attempts.length;
  }

  /// Determine level from score
  static String determineLevel(double score) {
    if (score <= AppConstants.beginnerMax) {
      return AppConstants.levels[0]; // beginner
    } else if (score <= AppConstants.elementaryMax) {
      return AppConstants.levels[1]; // elementary
    } else if (score <= AppConstants.intermediateMax) {
      return AppConstants.levels[2]; // intermediate
    } else if (score <= AppConstants.upperIntermediateMax) {
      return AppConstants.levels[3]; // upper_intermediate
    } else {
      return AppConstants.levels[4]; // advanced
    }
  }

  /// Check if answer is correct
  /// Uses standardized answer format when available (Plan 2), falls back to legacy logic
  static bool isAnswerCorrect(Question question, String? userAnswer) {
    if (userAnswer == null || userAnswer.isEmpty) return false;
    
    // Use standardized answer if available (Plan 2)
    try {
      final standardizedAnswer = question.getStandardizedAnswer();
      
      // Check if user answer is a choiceId
      if (question.choices.isNotEmpty) {
        final userChoice = question.choices.firstWhere(
          (c) => c.choiceId.toLowerCase() == userAnswer.toLowerCase(),
          orElse: () => QuestionChoice(choiceId: '', text: ''),
        );
        
        if (userChoice.choiceId.isNotEmpty) {
          // User selected a choice - check by choiceId or text
          if (standardizedAnswer.format == AnswerFormat.choiceId) {
            return standardizedAnswer.matches(userAnswer);
          } else {
            // Answer is text format, compare by text
            return standardizedAnswer.matchesByText(userChoice.text);
          }
        }
      }
      
      // Direct comparison
      return standardizedAnswer.matches(userAnswer);
    } catch (e) {
      // Fallback to legacy logic if standardized answer fails
      return _legacyAnswerCheck(question, userAnswer);
    }
  }

  /// Legacy answer checking logic (fallback)
  static bool _legacyAnswerCheck(Question question, String userAnswer) {
    switch (question.type) {
      case 'multiple_choice':
        return question.answer.toLowerCase().trim() == userAnswer.toLowerCase().trim();
        
      case 'gap_fill':
        if (question.choices.isNotEmpty) {
          final userChoice = question.choices.firstWhere(
            (c) => c.choiceId.toLowerCase() == userAnswer.toLowerCase(),
            orElse: () => QuestionChoice(choiceId: '', text: ''),
          );
          
          if (userChoice.choiceId.isNotEmpty) {
            final correctChoice = question.choices.firstWhere(
              (c) => c.isCorrect,
              orElse: () => QuestionChoice(choiceId: '', text: ''),
            );
            
            if (correctChoice.choiceId.isNotEmpty) {
              return userChoice.text.toLowerCase().trim() == correctChoice.text.toLowerCase().trim();
            }
            return question.answer.toLowerCase().trim() == userChoice.text.toLowerCase().trim();
          }
        }
        return question.answer.toLowerCase().trim() == userAnswer.toLowerCase().trim();
        
      case 'short_answer':
      case 'reorder':
      default:
        return question.answer.toLowerCase().trim() == userAnswer.toLowerCase().trim();
    }
  }

  /// Calculate topic performance breakdown
  static Map<int, Map<String, dynamic>> calculateTopicBreakdown(
    List<TestAttempt> attempts,
    Map<String, Question> questionMap,
  ) {
    final topicStats = <int, Map<String, dynamic>>{};
    
    for (final attempt in attempts) {
      final question = questionMap[attempt.questionId];
      if (question == null) continue;
      
      final topicId = question.topicId;
      if (!topicStats.containsKey(topicId)) {
        topicStats[topicId] = {
          'attempts': 0,
          'correct': 0,
          'total': 0,
        };
      }
      
      final stats = topicStats[topicId]!;
      stats['attempts'] = (stats['attempts'] as int) + 1;
      stats['total'] = (stats['total'] as int) + 1;
      
      if (attempt.isCorrect == true) {
        stats['correct'] = (stats['correct'] as int) + 1;
      }
    }
    
    // Calculate percentages
    for (final topicId in topicStats.keys) {
      final stats = topicStats[topicId]!;
      final attempts = stats['attempts'] as int;
      final correct = stats['correct'] as int;
      stats['percentage'] = attempts > 0 ? (correct / attempts) : 0.0;
    }
    
    return topicStats;
  }
}

