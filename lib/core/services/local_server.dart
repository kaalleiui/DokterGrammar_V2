import 'dart:isolate';
import 'dart:async';
import '../models/question.dart';
import '../../data/repositories/question_repository.dart';
import 'scoring_service.dart';
import 'adaptive_algorithm.dart';
import 'explanation_service.dart';
import 'rule_engine.dart';

/// On-device server for routing requests
/// This simplifies request/response and concurrency patterns
class LocalServer {
  static LocalServer? _instance;
  Isolate? _isolate;
  SendPort? _sendPort;
  ReceivePort? _receivePort;

  LocalServer._();

  static LocalServer get instance {
    _instance ??= LocalServer._();
    return _instance!;
  }

  /// Initialize the local server (start isolate)
  Future<void> initialize() async {
    if (_isolate != null) return;

    _receivePort = ReceivePort();
    _isolate = await Isolate.spawn(_serverIsolate, _receivePort!.sendPort);
    
    _receivePort!.listen((message) {
      if (message is SendPort) {
        _sendPort = message;
      }
    });

    // Wait for send port
    await Future.delayed(const Duration(milliseconds: 100));
    
    // Initialize rule engine
    await RuleEngine.initialize();
  }

  /// Server isolate entry point
  static void _serverIsolate(SendPort mainSendPort) {
    final receivePort = ReceivePort();
    mainSendPort.send(receivePort.sendPort);

    receivePort.listen((message) async {
      if (message is Map<String, dynamic>) {
        final requestType = message['type'] as String;
        final requestId = message['id'] as String;
        final data = message['data'] as Map<String, dynamic>?;

        dynamic response;

        try {
          switch (requestType) {
            case 'get_questions':
              response = await _handleGetQuestions(data);
              break;
            case 'generate_explanation':
              response = await _handleGenerateExplanation(data);
              break;
            case 'calculate_score':
              response = await _handleCalculateScore(data);
              break;
            case 'get_adaptive_questions':
              response = await _handleGetAdaptiveQuestions(data);
              break;
            default:
              response = {'error': 'Unknown request type'};
          }
        } catch (e) {
          response = {'error': e.toString()};
        }

        mainSendPort.send({
          'id': requestId,
          'response': response,
        });
      }
    });
  }

  /// Send request to server isolate
  Future<dynamic> sendRequest(String type, Map<String, dynamic>? data) async {
    if (_sendPort == null) {
      await initialize();
    }

    final requestId = DateTime.now().millisecondsSinceEpoch.toString();
    final completer = Completer<dynamic>();

    _receivePort!.listen((message) {
      if (message is Map && message['id'] == requestId) {
        completer.complete(message['response']);
      }
    });

    _sendPort!.send({
      'id': requestId,
      'type': type,
      'data': data,
    });

    return completer.future.timeout(
      const Duration(seconds: 30),
      onTimeout: () => {'error': 'Request timeout'},
    );
  }

  /// Handle get questions request
  static Future<Map<String, dynamic>> _handleGetQuestions(Map<String, dynamic>? data) async {
    final questionRepo = QuestionRepository();
    final questionId = data?['question_id'] as String?;
    
    if (questionId != null) {
      final question = await questionRepo.getQuestionById(questionId);
      return {'question': question?.toJson()};
    }
    
    final topicId = data?['topic_id'] as int?;
    final limit = data?['limit'] as int?;
    
    if (topicId != null) {
      final questions = await questionRepo.getQuestionsByTopic(topicId, limit: limit);
      return {'questions': questions.map((q) => q.toJson()).toList()};
    }
    
    return {'error': 'Invalid request parameters'};
  }

  /// Handle generate explanation request
  static Future<Map<String, dynamic>> _handleGenerateExplanation(Map<String, dynamic>? data) async {
    if (data == null) return {'error': 'No data provided'};
    
    final questionJson = data['question'] as Map<String, dynamic>?;
    final userAnswer = data['user_answer'] as String?;
    final isCorrect = data['is_correct'] as bool?;
    
    if (questionJson == null) return {'error': 'Question not provided'};
    
    final question = Question.fromJson(questionJson);
    final explanationService = ExplanationService();
    
    final explanation = await explanationService.generateExplanation(
      question: question,
      userAnswer: userAnswer,
      isCorrect: isCorrect,
    );
    
    return {
      'explanation': explanation,
      'type': 'rule_based', // Will be updated by AIService if AI-generated
    };
  }

  /// Handle calculate score request
  static Future<Map<String, dynamic>> _handleCalculateScore(Map<String, dynamic>? data) async {
    if (data == null) return {'error': 'No data provided'};
    
    final attemptsJson = data['attempts'] as List?;
    if (attemptsJson == null) return {'error': 'Attempts not provided'};
    
    // This is simplified - in real implementation, would convert JSON to TestAttempt objects
    final correctCount = attemptsJson.where((a) => a['is_correct'] == true).length;
    final score = correctCount / attemptsJson.length;
    final level = ScoringService.determineLevel(score);
    
    return {
      'score': score,
      'level': level,
      'correct': correctCount,
      'total': attemptsJson.length,
    };
  }

  /// Handle get adaptive questions request
  static Future<Map<String, dynamic>> _handleGetAdaptiveQuestions(Map<String, dynamic>? data) async {
    if (data == null) return {'error': 'No data provided'};
    
    final userId = data['user_id'] as int?;
    final totalQuestions = data['total_questions'] as int? ?? 20;
    final sessionType = data['session_type'] as String? ?? 'custom';
    final userInterests = (data['user_interests'] as List?)?.cast<String>() ?? [];
    
    if (userId == null) return {'error': 'User ID not provided'};
    
    final adaptiveAlgorithm = AdaptiveAlgorithm();
    List<Question> questions;
    
    if (sessionType == 'custom') {
      questions = await adaptiveAlgorithm.getCustomTestQuestions(
        userId: userId,
        totalQuestions: totalQuestions,
        userInterests: userInterests,
      );
    } else if (sessionType == 'daily') {
      questions = await adaptiveAlgorithm.getDailyTestQuestions(
        userId: userId,
        totalQuestions: totalQuestions,
        userInterests: userInterests,
      );
    } else {
      final questionRepo = QuestionRepository();
      questions = await questionRepo.getQuestionsForPlacement(
        userInterests: userInterests,
        totalQuestions: totalQuestions,
      );
    }
    
    return {
      'questions': questions.map((q) => q.toJson()).toList(),
    };
  }

  /// Shutdown the server
  void shutdown() {
    _isolate?.kill(priority: Isolate.immediate);
    _isolate = null;
    _sendPort = null;
    _receivePort?.close();
    _receivePort = null;
  }
}

