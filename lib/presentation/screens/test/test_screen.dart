import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import '../../../core/constants/color_scheme.dart';
import '../../../core/constants/strings.dart';
import '../../../core/constants/app_constants.dart';
import '../../../core/models/question.dart';
import '../../../core/models/test_session.dart';
import '../../../core/models/user_profile.dart';
import '../../../core/services/scoring_service.dart';
import '../../../data/repositories/question_repository.dart';
import '../../../data/repositories/test_repository.dart';
import '../../../data/repositories/user_repository.dart';
import '../../../data/repositories/performance_repository.dart';
import '../../../core/services/adaptive_algorithm.dart';
import '../../../core/services/streak_service.dart';
import '../../../core/services/badge_service.dart';
import '../../../core/services/debug_service.dart';
import '../../../data/datasources/assets/question_bank_loader.dart';
import '../test_results/test_results_screen.dart';
import '../../theme/page_transitions.dart';

class TestScreen extends StatefulWidget {
  final String sessionType;
  final int totalQuestions;

  const TestScreen({
    super.key,
    required this.sessionType,
    required this.totalQuestions,
  });

  @override
  State<TestScreen> createState() => _TestScreenState();
}

class _TestScreenState extends State<TestScreen> {
  List<Question> _questions = [];
  int _currentQuestionIndex = 0;
  String? _selectedAnswer;
  TestSession? _testSession;
  UserProfile? _user;
  bool _isLoading = true;
  final Map<int, String?> _answers = {}; // question index -> answer
  final Map<int, int> _startTimes = {}; // question index -> start time (ms)

  @override
  void initState() {
    super.initState();
    _initializeDebug();
    _initializeTest();
  }

  Future<void> _initializeDebug() async {
    await DebugService.instance.initialize();
  }

  Future<void> _initializeTest() async {
    try {
      // Get current user
      final userRepo = UserRepository();
      final user = await userRepo.getCurrentUser();
      if (user == null) {
        if (!mounted) return;
        Navigator.of(context).pop();
        return;
      }
      setState(() => _user = user);

      // Load questions using adaptive algorithm
      final adaptiveAlgorithm = AdaptiveAlgorithm();
      List<Question> questions;
      
      // Validate user ID before proceeding
      if (user.id == null) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Error: User ID tidak valid'),
            backgroundColor: AppColors.error,
          ),
        );
        Navigator.of(context).pop();
        return;
      }

      if (widget.sessionType == AppConstants.sessionTypePlacement) {
        final questionRepo = QuestionRepository();
        questions = await questionRepo.getQuestionsForPlacement(
          userInterests: user.interests,
          totalQuestions: widget.totalQuestions,
        );
      } else if (widget.sessionType == AppConstants.sessionTypeCustom) {
        questions = await adaptiveAlgorithm.getCustomTestQuestions(
          userId: user.id!,
          totalQuestions: widget.totalQuestions,
          userInterests: user.interests,
        );
      } else if (widget.sessionType == AppConstants.sessionTypeDaily) {
        questions = await adaptiveAlgorithm.getDailyTestQuestions(
          userId: user.id!,
          totalQuestions: widget.totalQuestions,
          userInterests: user.interests,
        );
      } else {
        // Reassessment
        questions = await adaptiveAlgorithm.getReassessmentQuestions(
          userId: user.id!,
          isTargeted: false,
          totalQuestions: widget.totalQuestions,
          userInterests: user.interests,
        );
      }

      // If no questions in DB, use sample questions
      if (questions.isEmpty) {
        final questionRepo = QuestionRepository();
        questions = await QuestionBankLoader.loadQuestionsFromAssets();
        if (questions.isNotEmpty) {
          await questionRepo.insertQuestions(questions);
          // Retry getting questions after inserting
          if (widget.sessionType == AppConstants.sessionTypePlacement) {
            questions = await questionRepo.getQuestionsForPlacement(
              userInterests: user.interests,
              totalQuestions: widget.totalQuestions,
            );
          } else if (widget.sessionType == AppConstants.sessionTypeCustom) {
            questions = await adaptiveAlgorithm.getCustomTestQuestions(
              userId: user.id!,
              totalQuestions: widget.totalQuestions,
              userInterests: user.interests,
            );
          } else if (widget.sessionType == AppConstants.sessionTypeDaily) {
            questions = await adaptiveAlgorithm.getDailyTestQuestions(
              userId: user.id!,
              totalQuestions: widget.totalQuestions,
              userInterests: user.interests,
            );
          }
        }
      }

      if (questions.isEmpty) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('No questions available')),
        );
        Navigator.of(context).pop();
        return;
      }

      setState(() => _questions = questions);

      // Create test session
      final testRepo = TestRepository();
      final session = TestSession(
        userId: user.id!,
        sessionType: widget.sessionType,
        totalQuestions: questions.length,
        startedAt: DateTime.now(),
      );
      final sessionId = await testRepo.createTestSession(session);
      
      // Validate session ID was created successfully
      if (sessionId <= 0) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Error: Gagal membuat test session. Silakan coba lagi.'),
            backgroundColor: AppColors.error,
          ),
        );
        Navigator.of(context).pop();
        return;
      }
      
      setState(() => _testSession = session.copyWith(id: sessionId));

      // Debug callback: Test start
      DebugService.instance.onTestStart(
        sessionType: widget.sessionType,
        totalQuestions: questions.length,
        user: user,
        metadata: {
          'sessionId': sessionId,
          'questionSource': questions.isEmpty ? 'fallback' : 'database',
        },
      );

      // Debug callback: Question load
      DebugService.instance.onQuestionLoad(
        questions: questions,
        source: questions.isEmpty ? 'fallback' : 'database',
        metadata: {
          'sessionType': widget.sessionType,
          'userId': user.id,
        },
      );

      // Record start time for first question
      _startTimes[_currentQuestionIndex] = DateTime.now().millisecondsSinceEpoch;

      // Debug callback: First question display
      if (questions.isNotEmpty) {
        DebugService.instance.onQuestionDisplay(
          question: questions[_currentQuestionIndex],
          questionIndex: _currentQuestionIndex,
          totalQuestions: questions.length,
        );
      }

      setState(() => _isLoading = false);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error loading test: $e')),
      );
      Navigator.of(context).pop();
    }
  }

  void _saveAnswer() {
    if (_selectedAnswer == null || _testSession == null) return;

    final question = _questions[_currentQuestionIndex];
    // Extract original choiceId from unique value if format is questionId_choiceId_index
    // Otherwise use _selectedAnswer as-is (for backward compatibility)
    String answerToSave = _selectedAnswer!;
    
    // Improved extraction: Find the choiceId by matching against actual choices
    // This is more robust than splitting by underscores
    if (_selectedAnswer!.contains('_') && question.choices.isNotEmpty) {
      // Try to find which part of the unique value matches a choiceId
      final parts = _selectedAnswer!.split('_');
      final choiceIds = question.choices.map((c) => c.choiceId.toLowerCase()).toList();
      
      // Look for a part that matches a choiceId (check from end to start)
      bool found = false;
      for (int i = parts.length - 1; i >= 0; i--) {
        if (choiceIds.contains(parts[i].toLowerCase())) {
          answerToSave = parts[i];
          found = true;
          break;
        }
      }
      
      // Fallback to old logic if no match found
      if (!found && parts.length >= 2) {
        answerToSave = parts[parts.length - 2];
      }
    }
    
    final isCorrect = ScoringService.isAnswerCorrect(question, answerToSave);
    
    // Debug: Log answer extraction for troubleshooting
    if (kDebugMode) {
      debugPrint('🔍 Answer Extraction Debug:');
      debugPrint('  Question ID: ${question.id}');
      debugPrint('  Selected Answer (unique): $_selectedAnswer');
      debugPrint('  Extracted Answer: $answerToSave');
      debugPrint('  Question Answer Field: ${question.answer}');
      debugPrint('  Is Correct: $isCorrect');
      debugPrint('  Question Type: ${question.type}');
    }
    
    // Calculate time spent
    final startTime = _startTimes[_currentQuestionIndex] ?? DateTime.now().millisecondsSinceEpoch;
    final timeSpent = (DateTime.now().millisecondsSinceEpoch - startTime) ~/ 1000;

    // Debug callback: Answer submit
    DebugService.instance.onAnswerSubmit(
      question: question,
      answer: answerToSave,
      isCorrect: isCorrect,
      timeSpentSeconds: timeSpent,
      questionIndex: _currentQuestionIndex,
    );

    // Save answer (store original choiceId, not unique value)
    _answers[_currentQuestionIndex] = answerToSave;

    // Create or update attempt
    _saveAttempt(question, answerToSave, isCorrect, timeSpent);
  }

  Future<void> _saveAttempt(Question question, String answer, bool isCorrect, int timeSpent) async {
    if (_testSession?.id == null) return;

    final testRepo = TestRepository();
    final attempt = TestAttempt(
      sessionId: _testSession!.id!,
      questionId: question.id,
      userAnswer: answer,
      isCorrect: isCorrect,
      timeSpentSeconds: timeSpent,
      answeredAt: DateTime.now(),
    );

    // Check if attempt already exists
    final existingAttempts = _testSession!.attempts.where(
      (a) => a.questionId == question.id,
    ).toList();

    if (existingAttempts.isNotEmpty) {
      final existing = existingAttempts.first;
      if (existing.id != null) {
        final updatedAttempt = TestAttempt(
          id: existing.id,
          sessionId: attempt.sessionId,
          questionId: attempt.questionId,
          userAnswer: attempt.userAnswer,
          isCorrect: attempt.isCorrect,
          timeSpentSeconds: attempt.timeSpentSeconds,
          hintUsed: attempt.hintUsed,
          answeredAt: attempt.answeredAt,
        );
        await testRepo.updateTestAttempt(updatedAttempt);
      }
    } else {
      final attemptId = await testRepo.createTestAttempt(attempt);
      setState(() {
        final updatedAttempt = TestAttempt(
          id: attemptId,
          sessionId: attempt.sessionId,
          questionId: attempt.questionId,
          userAnswer: attempt.userAnswer,
          isCorrect: attempt.isCorrect,
          timeSpentSeconds: attempt.timeSpentSeconds,
          hintUsed: attempt.hintUsed,
          answeredAt: attempt.answeredAt,
        );
        _testSession = _testSession!.copyWith(
          attempts: [..._testSession!.attempts, updatedAttempt],
        );
      });
    }
  }

  void _nextQuestion() {
    if (_currentQuestionIndex < _questions.length - 1) {
      _saveAnswer();
      final oldIndex = _currentQuestionIndex;
      setState(() {
        _currentQuestionIndex++;
        // Restore answer: convert stored choiceId back to unique value format
        final savedAnswer = _answers[_currentQuestionIndex];
        if (savedAnswer != null) {
          final question = _questions[_currentQuestionIndex];
          // Find the choice with matching choiceId and get its index
          final choiceIndex = question.choices.indexWhere((c) => c.choiceId == savedAnswer);
          if (choiceIndex >= 0) {
            _selectedAnswer = '${question.id}_${savedAnswer}_$choiceIndex';
          } else {
            _selectedAnswer = null;
          }
        } else {
          _selectedAnswer = null;
        }
        _startTimes[_currentQuestionIndex] = DateTime.now().millisecondsSinceEpoch;
      });
      
      // Debug callback: Question change
      DebugService.instance.onQuestionChange(
        fromIndex: oldIndex,
        toIndex: _currentQuestionIndex,
        totalQuestions: _questions.length,
      );
      
      // Debug callback: Question display
      DebugService.instance.onQuestionDisplay(
        question: _questions[_currentQuestionIndex],
        questionIndex: _currentQuestionIndex,
        totalQuestions: _questions.length,
      );
    } else {
      _completeTest();
    }
  }

  void _previousQuestion() {
    if (_currentQuestionIndex > 0) {
      _saveAnswer();
      final oldIndex = _currentQuestionIndex;
      setState(() {
        _currentQuestionIndex--;
        // Restore answer: convert stored choiceId back to unique value format
        final savedAnswer = _answers[_currentQuestionIndex];
        if (savedAnswer != null) {
          final question = _questions[_currentQuestionIndex];
          // Find the choice with matching choiceId and get its index
          final choiceIndex = question.choices.indexWhere((c) => c.choiceId == savedAnswer);
          if (choiceIndex >= 0) {
            _selectedAnswer = '${question.id}_${savedAnswer}_$choiceIndex';
          } else {
            _selectedAnswer = null;
          }
        } else {
          _selectedAnswer = null;
        }
      });
      
      // Debug callback: Question change
      DebugService.instance.onQuestionChange(
        fromIndex: oldIndex,
        toIndex: _currentQuestionIndex,
        totalQuestions: _questions.length,
      );
    }
  }

  Future<void> _completeTest() async {
    if (_testSession == null) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Error: Test session tidak ditemukan'),
          backgroundColor: AppColors.error,
        ),
      );
      Navigator.of(context).pop();
      return;
    }

    if (_questions.isEmpty) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Error: Tidak ada pertanyaan yang tersedia'),
          backgroundColor: AppColors.error,
        ),
      );
      Navigator.of(context).pop();
      return;
    }

    try {
      _saveAnswer();

      // Reload session from database to ensure we have all attempts
      final testRepo = TestRepository();
      final reloadedSession = await testRepo.getTestSessionById(_testSession!.id!);
      
      if (reloadedSession == null) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Error: Tidak dapat memuat data test. Silakan coba lagi.'),
            backgroundColor: AppColors.error,
          ),
        );
        Navigator.of(context).pop();
        return;
      }

      // Use reloaded session with all attempts
      _testSession = reloadedSession;

      // Calculate final score using reloaded attempts
      final score = ScoringService.calculateScore(_testSession!.attempts);
      final level = ScoringService.determineLevel(score);
      
      // Debug callback: Score calculate
      final attemptsData = _testSession!.attempts.map((a) => {
        'questionId': a.questionId,
        'isCorrect': a.isCorrect,
        'timeSpent': a.timeSpentSeconds,
      }).toList();
      DebugService.instance.onScoreCalculate(
        attempts: attemptsData,
        score: score,
      );
      
      final duration = DateTime.now().difference(_testSession!.startedAt).inSeconds;

      // Update session
      final updatedSession = _testSession!.copyWith(
        completedQuestions: _questions.length,
        score: score,
        levelAfter: level,
        completedAt: DateTime.now(),
        durationSeconds: duration,
      );

      await testRepo.updateTestSession(updatedSession);

      // Validate session ID before proceeding
      if (updatedSession.id == null) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Error: Session ID tidak valid. Silakan coba lagi.'),
            backgroundColor: AppColors.error,
          ),
        );
        Navigator.of(context).pop();
        return;
      }

      // Update user level if this is placement test
      if (widget.sessionType == AppConstants.sessionTypePlacement && _user != null) {
        if (_user!.id == null) {
          if (!mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Error: User ID tidak valid'),
              backgroundColor: AppColors.error,
            ),
          );
          Navigator.of(context).pop();
          return;
        }

        try {
          final oldLevel = _user!.currentLevel;
          final userRepo = UserRepository();
          await userRepo.updateUser(_user!.copyWith(
            currentLevel: level,
            overallScore: score,
          ));
          
          // Debug callback: Level update
          DebugService.instance.onLevelUpdate(
            oldLevel: oldLevel,
            newLevel: level,
            score: score,
          );
        } catch (e) {
          // Log error but continue - user level update is not critical
          debugPrint('Error updating user level: $e');
        }
      }

      // Update topic performance for all attempts
      if (_user != null && _user!.id != null) {
        try {
          final performanceRepo = PerformanceRepository();
          for (final attempt in updatedSession.attempts) {
            // Find question safely - handle empty questions array
            Question? question;
            try {
              question = _questions.firstWhere(
                (q) => q.id == attempt.questionId,
              );
            } catch (e) {
              // Question not found, skip this attempt
              debugPrint('Question not found for attempt: ${attempt.questionId}');
              continue;
            }
            
            await performanceRepo.recordAttempt(
              userId: _user!.id!,
              topicId: question.topicId,
              isCorrect: attempt.isCorrect == true,
              timeSpentSeconds: attempt.timeSpentSeconds ?? 0,
            );
            
            // Get updated performance for debug
            final performance = await performanceRepo.getTopicPerformance(_user!.id!, question.topicId);
            if (performance != null) {
              // Debug callback: Performance update
              DebugService.instance.onPerformanceUpdate(
                topicId: question.topicId,
                attempts: performance.attempts,
                correct: performance.correct,
                masteryPercentage: performance.masteryPercentage,
              );
            }
          }

          // Update streak
          try {
            final streakService = StreakService();
            await streakService.updateStreak(_user!.id!);
          } catch (e) {
            debugPrint('Error updating streak: $e');
          }

          // Check for new badges
          try {
            final badgeService = BadgeService();
            final newBadges = await badgeService.checkAndAwardBadges(_user!.id!);
            
            if (newBadges.isNotEmpty && mounted) {
              // Show badge notification
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('🏆 Badge baru: ${badgeService.getBadgeDisplayName(newBadges.first)}'),
                  duration: const Duration(seconds: 3),
                  backgroundColor: AppColors.success,
                ),
              );
            }
          } catch (e) {
            debugPrint('Error checking badges: $e');
          }
        } catch (e) {
          // Log error but continue - performance updates are not critical for navigation
          debugPrint('Error updating performance: $e');
        }
      }

      // Debug callback: Test complete
      final correctCount = updatedSession.attempts.where((a) => a.isCorrect == true).length;
      DebugService.instance.onTestComplete(
        session: updatedSession,
        score: score,
        level: level,
        totalQuestions: _questions.length,
        correctAnswers: correctCount,
      );

      // Save debug logs to file
      try {
        await DebugService.instance.saveLogsToFile();
      } catch (e) {
        debugPrint('Error saving debug logs: $e');
      }

      // Navigate to results screen - session ID is validated above
      if (!mounted) return;
      AppNavigator.pushReplacementFadeSlide(
        context,
        TestResultsScreen(sessionId: updatedSession.id!),
      );
    } catch (e) {
      // Handle any unexpected errors
      debugPrint('Error completing test: $e');
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error menyelesaikan test: $e'),
          backgroundColor: AppColors.error,
          duration: const Duration(seconds: 5),
          action: SnackBarAction(
            label: 'Tutup',
            textColor: Colors.white,
            onPressed: () {
              Navigator.of(context).pop();
            },
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        body: Container(
          decoration: const BoxDecoration(
            color: AppColors.background,
          ),
          child: const Center(
            child: CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
            ),
          ),
        ),
      );
    }

    if (_questions.isEmpty) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Error'),
          backgroundColor: AppColors.cardBackground,
        ),
        body: Container(
          decoration: const BoxDecoration(
            color: AppColors.background,
          ),
          child: const Center(
            child: Text(
              'No questions available',
              style: TextStyle(color: AppColors.textPrimary),
            ),
          ),
        ),
      );
    }

    final question = _questions[_currentQuestionIndex];
    final progress = (_currentQuestionIndex + 1) / _questions.length;
    final hasChoices = question.choices.isNotEmpty;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          '${AppStrings.questionProgress} ${_currentQuestionIndex + 1} / ${_questions.length}',
          style: const TextStyle(
            color: AppColors.textPrimary,
            fontWeight: FontWeight.w600,
          ),
        ),
        centerTitle: true,
        backgroundColor: AppColors.cardBackground,
        elevation: 0,
      ),
      body: Container(
        decoration: const BoxDecoration(
          color: AppColors.background,
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Progress Bar
                TweenAnimationBuilder<double>(
                  tween: Tween(begin: 0.0, end: progress),
                  duration: const Duration(milliseconds: 300),
                  curve: Curves.easeOut,
                  builder: (context, value, child) {
                    return LinearProgressIndicator(
                      value: value,
                      backgroundColor: AppColors.primary.withOpacity(0.2),
                      valueColor: const AlwaysStoppedAnimation<Color>(AppColors.primary),
                      minHeight: 8,
                      borderRadius: BorderRadius.circular(4),
                    );
                  },
                ),
                const SizedBox(height: 24),
                
                // Question Card
                Expanded(
                  child: AnimatedSwitcher(
                    duration: const Duration(milliseconds: 300),
                    transitionBuilder: (child, animation) {
                      return FadeTransition(
                        opacity: animation,
                        child: SlideTransition(
                          position: Tween<Offset>(
                            begin: const Offset(0.1, 0),
                            end: Offset.zero,
                          ).animate(CurvedAnimation(
                            parent: animation,
                            curve: Curves.easeOut,
                          )),
                          child: child,
                        ),
                      );
                    },
                    child: Container(
                      key: ValueKey(question.id),
                      decoration: BoxDecoration(
                        color: AppColors.cardBackground,
                        borderRadius: BorderRadius.circular(AppColors.radius),
                        boxShadow: AppColors.cardShadow,
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(24.0),
                        child: SingleChildScrollView(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                question.prompt,
                                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                  color: AppColors.textPrimary,
                                  fontWeight: FontWeight.w600,
                                  height: 1.4,
                                ),
                              ),
                              const SizedBox(height: 24),
                              
                              // Choices - Show for any question type that has choices
                              // Filter duplicates: only show first occurrence of each choiceId
                              if (hasChoices) ...[
                                ...question.choices.asMap().entries.where((entry) {
                                  final index = entry.key;
                                  final choice = entry.value;
                                  // Only include first occurrence of each choiceId
                                  final firstIndex = question.choices.indexWhere((c) => c.choiceId == choice.choiceId);
                                  return firstIndex == index;
                                }).map((entry) {
                                  final index = entry.key;
                                  final choice = entry.value;
                                  // Use unique value combining question.id, choiceId, and index
                                  // This ensures uniqueness even if choiceId is duplicated
                                  final uniqueValue = '${question.id}_${choice.choiceId}_$index';
                                  return Padding(
                                    key: ValueKey(uniqueValue),
                                    padding: const EdgeInsets.only(bottom: 12),
                                    child: AnimatedContainer(
                                      duration: const Duration(milliseconds: 200),
                                      curve: Curves.easeOut,
                                      child: RadioListTile<String>(
                                        title: Text(
                                          choice.text,
                                          style: const TextStyle(
                                            color: AppColors.textPrimary,
                                            fontSize: 16,
                                            fontWeight: FontWeight.w500,
                                          ),
                                        ),
                                        // Use unique value instead of just choiceId to prevent multiple selections
                                        value: uniqueValue,
                                        groupValue: _selectedAnswer,
                                        activeColor: AppColors.textPrimary,
                                        selectedTileColor: AppColors.primary.withOpacity(0.1),
                                        onChanged: (value) {
                                          if (value == null) return;
                                          
                                          setState(() {
                                            _selectedAnswer = value;
                                          });
                                          
                                          // Extract original choiceId from unique value
                                          // Improved: Match against actual choices for robustness
                                          String originalChoiceId = choice.choiceId;
                                          if (value.contains('_') && question.choices.isNotEmpty) {
                                            final parts = value.split('_');
                                            final choiceIds = question.choices.map((c) => c.choiceId.toLowerCase()).toList();
                                            
                                            // Look for a part that matches a choiceId
                                            for (int i = parts.length - 1; i >= 0; i--) {
                                              if (choiceIds.contains(parts[i].toLowerCase())) {
                                                originalChoiceId = parts[i];
                                                break;
                                              }
                                            }
                                            
                                            // Fallback to old logic
                                            if (originalChoiceId == choice.choiceId && parts.length >= 2) {
                                              originalChoiceId = parts[parts.length - 2];
                                            }
                                          }
                                          
                                          // Debug callback: Answer select
                                          DebugService.instance.onAnswerSelect(
                                            question: question,
                                            selectedAnswer: originalChoiceId,
                                            questionIndex: _currentQuestionIndex,
                                          );
                                        },
                                        shape: RoundedRectangleBorder(
                                          borderRadius: BorderRadius.circular(12),
                                        ),
                                        contentPadding: const EdgeInsets.symmetric(
                                          horizontal: 16,
                                          vertical: 8,
                                        ),
                                      ),
                                    ),
                                  );
                                })
                              ]
                              else
                                Padding(
                                  padding: const EdgeInsets.symmetric(vertical: 16),
                                  child: Text(
                                    'No options available for this question type: ${question.type}',
                                    style: const TextStyle(
                                      color: AppColors.textSecondary,
                                      fontStyle: FontStyle.italic,
                                    ),
                                  ),
                                ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
                
                const SizedBox(height: 16),
                
                // Navigation Buttons
                Row(
                  children: [
                    if (_currentQuestionIndex > 0)
                      Expanded(
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          child: OutlinedButton(
                            onPressed: _previousQuestion,
                            style: OutlinedButton.styleFrom(
                              foregroundColor: AppColors.textPrimary,
                              side: const BorderSide(color: AppColors.textPrimary, width: 2),
                              padding: const EdgeInsets.symmetric(vertical: 16),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                            child: const Text(
                              AppStrings.previousQuestion,
                              style: TextStyle(
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ),
                      ),
                    if (_currentQuestionIndex > 0) const SizedBox(width: 12),
                    Expanded(
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 200),
                        child: ElevatedButton(
                          onPressed: hasChoices 
                              ? (_selectedAnswer != null ? _nextQuestion : null)
                              : _nextQuestion, // Allow proceeding even without answer for non-choice questions
                          style: ElevatedButton.styleFrom(
                            backgroundColor: _selectedAnswer != null || !hasChoices
                                ? AppColors.primary
                                : AppColors.primary.withOpacity(0.5),
                            foregroundColor: _selectedAnswer != null || !hasChoices
                                ? Colors.white
                                : AppColors.textSecondary,
                            elevation: _selectedAnswer != null || !hasChoices ? 2 : 0,
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                          child: Text(
                            _currentQuestionIndex < _questions.length - 1
                                ? AppStrings.nextQuestion
                                : AppStrings.finishTest,
                            style: const TextStyle(
                              fontWeight: FontWeight.w600,
                              fontSize: 16,
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
