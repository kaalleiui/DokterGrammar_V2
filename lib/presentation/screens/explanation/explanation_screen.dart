import 'package:flutter/material.dart';
import '../../../core/constants/color_scheme.dart';
import '../../../core/models/question.dart';
import '../../../core/services/explanation_service.dart';
import '../../../data/repositories/question_repository.dart';
import '../../widgets/common/modern_header.dart';

class ExplanationScreen extends StatefulWidget {
  final int attemptId;
  final String questionId;
  final String? userAnswer;
  final bool? isCorrect;

  const ExplanationScreen({
    super.key,
    required this.attemptId,
    required this.questionId,
    this.userAnswer,
    this.isCorrect,
  });

  @override
  State<ExplanationScreen> createState() => _ExplanationScreenState();
}

class _ExplanationScreenState extends State<ExplanationScreen> {
  Question? _question;
  bool _isLoading = true;
  String? _explanationText;
  final ExplanationService _explanationService = ExplanationService();

  @override
  void initState() {
    super.initState();
    _loadQuestion();
  }

  Future<void> _loadQuestion() async {
    try {
      final questionRepo = QuestionRepository();
      final question = await questionRepo.getQuestionById(widget.questionId);
      
      if (question != null) {
        final explanation = await _explanationService.generateExplanation(
          question: question,
          userAnswer: widget.userAnswer,
          isCorrect: widget.isCorrect,
        );
        
        setState(() {
          _question = question;
          _explanationText = explanation;
          _isLoading = false;
        });
      } else {
        setState(() => _isLoading = false);
      }
    } catch (e) {
      setState(() => _isLoading = false);
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
            child: CircularProgressIndicator(),
          ),
        ),
      );
    }

    if (_question == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Error')),
        body: const Center(child: Text('Question not found')),
      );
    }

    final question = _question!;
    final correctChoice = question.choices.firstWhere(
      (c) => c.isCorrect,
      orElse: () => question.choices.first,
    );

    return Scaffold(
      backgroundColor: AppColors.backgroundLight,
      body: SafeArea(
        child: Column(
          children: [
            // Modern Header
            ModernHeader(
              title: 'Pembahasan',
              showTitle: true,
              leading: IconButton(
                icon: const Icon(Icons.arrow_back_rounded, color: AppColors.textPrimary),
                onPressed: () => Navigator.of(context).pop(),
              ),
            ),
            
            // Content Area
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Question Card
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: AppColors.cardBackground,
                        borderRadius: BorderRadius.circular(AppColors.radius),
                        boxShadow: AppColors.cardShadow,
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            question.prompt,
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.w600,
                              color: AppColors.textPrimary,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                    
                    // Answer Status
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: AppColors.cardBackground,
                        borderRadius: BorderRadius.circular(AppColors.radius),
                        boxShadow: AppColors.cardShadow,
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(
                                widget.isCorrect == true 
                                    ? Icons.check_circle_rounded
                                    : Icons.cancel_rounded,
                                color: widget.isCorrect == true 
                                    ? AppColors.success
                                    : AppColors.error,
                                size: 28,
                              ),
                              const SizedBox(width: 12),
                              Text(
                                widget.isCorrect == true 
                                    ? 'Jawaban Benar'
                                    : 'Jawaban Salah',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                  color: widget.isCorrect == true 
                                      ? AppColors.success
                                      : AppColors.error,
                                ),
                              ),
                            ],
                          ),
                          if (widget.userAnswer != null) ...[
                            const SizedBox(height: 12),
                            Text(
                              'Jawaban Anda: ${_getAnswerText(question, widget.userAnswer!)}',
                              style: const TextStyle(
                                fontSize: 15,
                                color: AppColors.textPrimary,
                              ),
                            ),
                          ],
                          const SizedBox(height: 8),
                          Text(
                            'Jawaban Benar: ${correctChoice.text}',
                            style: const TextStyle(
                              fontSize: 15,
                              fontWeight: FontWeight.bold,
                              color: AppColors.textPrimary,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                    
                    // Explanation Card
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: AppColors.cardBackground,
                        borderRadius: BorderRadius.circular(AppColors.radius),
                        boxShadow: AppColors.cardShadow,
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Penjelasan',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: AppColors.textPrimary,
                            ),
                          ),
                          const SizedBox(height: 12),
                          Text(
                            _explanationText ?? 'Penjelasan tidak tersedia.',
                            style: const TextStyle(
                              fontSize: 15,
                              color: AppColors.textPrimary,
                              height: 1.5,
                            ),
                          ),
                          if (question.exampleSentence != null) ...[
                            const SizedBox(height: 16),
                            Container(
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: AppColors.lemonMedium.withOpacity(0.3),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Text(
                                    'Contoh:',
                                    style: TextStyle(
                                      fontSize: 14,
                                      fontWeight: FontWeight.bold,
                                      color: AppColors.textPrimary,
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    question.exampleSentence!,
                                    style: const TextStyle(
                                      fontSize: 15,
                                      color: AppColors.textPrimary,
                                      fontStyle: FontStyle.italic,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                    const SizedBox(height: 20),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _getAnswerText(Question question, String answerId) {
    try {
      final choice = question.choices.firstWhere(
        (c) => c.choiceId == answerId,
      );
      return choice.text;
    } catch (e) {
      return answerId;
    }
  }
}

