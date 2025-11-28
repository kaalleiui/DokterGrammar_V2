import '../models/question.dart';
import 'rule_engine.dart';
import 'ai_service.dart';

class ExplanationService {
  /// Generate explanation for a question attempt
  /// Uses AI explanations if available, falls back to rule-based
  Future<String> generateExplanation({
    required Question question,
    required String? userAnswer,
    required bool? isCorrect,
  }) async {
    // Try AI service first
    try {
      final aiResult = await AIService.generateExplanation(
        question: question,
        userAnswer: userAnswer,
        isCorrect: isCorrect,
        userInterests: [], // Can be enhanced later
      );
      
      // Return AI explanation if available
      if (aiResult['type'] == 'ai_generated') {
        return aiResult['text'] as String;
      }
    } catch (e) {
      // Fall through to rule-based if AI fails
    }
    // Fallback to rule-based explanation
    // Try to use template from rule engine first
    final template = RuleEngine.getTemplateForQuestionType(
      question.type,
      topic: _getTopicFromQuestion(question),
      isCorrect: isCorrect ?? false,
    );
    
    if (template != null) {
      return _fillTemplateFromRuleEngine(template, question, userAnswer, isCorrect);
    }

    // If there's a question-specific template, use it
    if (question.explanationTemplate != null && question.explanationTemplate!.isNotEmpty) {
      return _fillTemplate(question.explanationTemplate!, question, userAnswer);
    }

    // Generate based on question type
    switch (question.type) {
      case 'multiple_choice':
        return _generateMultipleChoiceExplanation(question, userAnswer, isCorrect);
      case 'gap_fill':
        return _generateGapFillExplanation(question, userAnswer, isCorrect);
      case 'reorder':
        return _generateReorderExplanation(question, userAnswer, isCorrect);
      case 'short_answer':
        return _generateShortAnswerExplanation(question, userAnswer, isCorrect);
      default:
        return _generateDefaultExplanation(question, userAnswer, isCorrect);
    }
  }

  String? _getTopicFromQuestion(Question question) {
    final topicTag = question.tags.firstWhere(
      (tag) => tag.tagType == 'grammar_point',
      orElse: () => QuestionTag(tagType: '', tagValue: ''),
    );
    return topicTag.tagValue.isNotEmpty ? topicTag.tagValue : null;
  }

  String _fillTemplateFromRuleEngine(
    String template,
    Question question,
    String? userAnswer,
    bool? isCorrect,
  ) {
    String result = template;
    
    final correctChoice = _getCorrectChoice(question);
    
    // Get correct answer text
    String correctAnswerText;
    if (question.choices.isNotEmpty) {
      correctAnswerText = correctChoice?.text ?? question.answer;
    } else {
      correctAnswerText = question.answer;
    }
    
    result = result.replaceAll('{correct_answer}', correctAnswerText);
    result = result.replaceAll('{user_answer}', userAnswer ?? 'Tidak dijawab');
    
    // Get rule explanation
    final grammarPoint = _getTopicFromQuestion(question);
    String ruleExplanation = '';
    if (grammarPoint != null) {
      final rule = RuleEngine.getRuleForGrammarPoint(grammarPoint);
      if (rule != null) {
        ruleExplanation = rule['explanation_template'] as String? ?? '';
      }
    }
    result = result.replaceAll('{rule_explanation}', ruleExplanation);
    result = result.replaceAll('{tense_rule}', ruleExplanation);
    
    if (question.exampleSentence != null) {
      result = result.replaceAll('{example}', question.exampleSentence!);
      result = result.replaceAll('{example_sentence}', question.exampleSentence!);
    }
    
    return result;
  }

  String _fillTemplate(String template, Question question, String? userAnswer) {
    String result = template;
    
    // Replace placeholders
    final correctChoice = _getCorrectChoice(question);
    
    // Get correct answer text
    String correctAnswerText;
    if (question.choices.isNotEmpty) {
      correctAnswerText = correctChoice?.text ?? question.answer;
    } else {
      correctAnswerText = question.answer;
    }
    
    result = result.replaceAll('{correct_answer}', correctAnswerText);
    result = result.replaceAll('{user_answer}', userAnswer ?? 'Tidak dijawab');
    
    if (question.exampleSentence != null) {
      result = result.replaceAll('{example}', question.exampleSentence!);
    }
    
    return result;
  }

  String _generateMultipleChoiceExplanation(
    Question question,
    String? userAnswer,
    bool? isCorrect,
  ) {
    final correctChoice = _getCorrectChoice(question);
    if (correctChoice == null) {
      return 'Error: Tidak dapat menemukan jawaban yang benar untuk pertanyaan ini.';
    }

    final correctAnswerText = correctChoice.text;

    if (isCorrect == true) {
      return 'Jawaban Anda benar! "$correctAnswerText" adalah pilihan yang tepat. '
          '${question.exampleSentence != null ? "Contoh: ${question.exampleSentence}" : ""}';
    } else {
      final userChoiceText = userAnswer != null
          ? question.choices.firstWhere(
              (c) => c.choiceId == userAnswer,
              orElse: () => QuestionChoice(choiceId: userAnswer, text: userAnswer),
            ).text
          : 'Tidak dijawab';

      return 'Jawaban yang benar adalah "$correctAnswerText". '
          'Pilihan "$userChoiceText" tidak tepat karena ${_getReasonForError(question)}. '
          '${question.exampleSentence != null ? "Contoh yang benar: ${question.exampleSentence}" : ""}';
    }
  }

  String _generateGapFillExplanation(
    Question question,
    String? userAnswer,
    bool? isCorrect,
  ) {
    // Get correct answer text from correct choice or answer field
    String correctAnswerText;
    if (question.choices.isNotEmpty) {
      final correctChoice = _getCorrectChoice(question);
      if (correctChoice != null) {
        correctAnswerText = correctChoice.text;
      } else {
        // Fallback to answer field
        correctAnswerText = question.answer;
      }
    } else {
      correctAnswerText = question.answer;
    }
    
    // Get user answer text (might be choiceId or text)
    String userAnswerText = userAnswer ?? 'tidak dijawab';
    if (userAnswer != null && question.choices.isNotEmpty) {
      final userChoice = question.choices.firstWhere(
        (c) => c.choiceId.toLowerCase() == userAnswer.toLowerCase(),
        orElse: () => QuestionChoice(choiceId: '', text: ''),
      );
      if (userChoice.choiceId.isNotEmpty) {
        userAnswerText = userChoice.text;
      }
    }
    
    if (isCorrect == true) {
      return 'Jawaban Anda benar! "$userAnswerText" adalah bentuk yang tepat untuk konteks ini. '
          '${question.exampleSentence != null ? "Contoh: ${question.exampleSentence}" : ""}';
    } else {
      return 'Jawaban yang benar adalah "$correctAnswerText". '
          'Anda menjawab "$userAnswerText", yang tidak sesuai dengan aturan grammar. '
          '${_getGrammarRule(question)} '
          '${question.exampleSentence != null ? "Contoh: ${question.exampleSentence}" : ""}';
    }
  }

  String _generateReorderExplanation(
    Question question,
    String? userAnswer,
    bool? isCorrect,
  ) {
    if (isCorrect == true) {
      return 'Urutan yang Anda buat benar! Kalimat tersebut sekarang memiliki struktur yang tepat. '
          '${question.exampleSentence != null ? "Contoh: ${question.exampleSentence}" : ""}';
    } else {
      return 'Urutan yang benar adalah: "${question.answer}". '
          'Pastikan kalimat mengikuti struktur yang tepat dengan subjek, predikat, dan objek pada posisi yang benar. '
          '${question.exampleSentence != null ? "Contoh: ${question.exampleSentence}" : ""}';
    }
  }

  String _generateShortAnswerExplanation(
    Question question,
    String? userAnswer,
    bool? isCorrect,
  ) {
    if (isCorrect == true) {
      return 'Jawaban Anda benar! "${userAnswer}" adalah jawaban yang tepat. '
          '${question.exampleSentence != null ? "Contoh: ${question.exampleSentence}" : ""}';
    } else {
      return 'Jawaban yang benar adalah "${question.answer}". '
          'Jawaban Anda "${userAnswer ?? "tidak dijawab"}" tidak sesuai. '
          '${_getGrammarRule(question)} '
          '${question.exampleSentence != null ? "Contoh: ${question.exampleSentence}" : ""}';
    }
  }

  String _generateDefaultExplanation(
    Question question,
    String? userAnswer,
    bool? isCorrect,
  ) {
    if (isCorrect == true) {
      return 'Jawaban Anda benar! '
          '${question.exampleSentence != null ? "Contoh: ${question.exampleSentence}" : ""}';
    } else {
      return 'Jawaban yang benar adalah "${question.answer}". '
          '${_getGrammarRule(question)} '
          '${question.exampleSentence != null ? "Contoh: ${question.exampleSentence}" : ""}';
    }
  }

  String _getReasonForError(Question question) {
    // Get topic-based reason
    final topicTags = question.tags.where((t) => t.tagType == 'grammar_point').toList();
    if (topicTags.isNotEmpty) {
      final grammarPoint = topicTags.first.tagValue;
      return _getTopicSpecificReason(grammarPoint);
    }
    return 'tidak sesuai dengan aturan grammar yang berlaku';
  }

  String _getTopicSpecificReason(String grammarPoint) {
    switch (grammarPoint) {
      case 'simple_past':
        return 'menggunakan simple past tense untuk aksi yang sudah selesai di masa lalu';
      case 'present_perfect':
        return 'menggunakan present perfect untuk aksi yang dimulai di masa lalu dan masih relevan';
      case 'relative_clause':
        return 'menggunakan relative clause dengan pronoun yang tepat';
      case 'conditional_3':
        return 'menggunakan third conditional (if + past perfect, would have + past participle)';
      case 'passive_voice':
        return 'menggunakan passive voice dengan struktur yang benar';
      default:
        return 'tidak sesuai dengan aturan grammar yang berlaku';
    }
  }

  String _getGrammarRule(Question question) {
    final topicTags = question.tags.where((t) => t.tagType == 'grammar_point').toList();
    if (topicTags.isNotEmpty) {
      final grammarPoint = topicTags.first.tagValue;
      return _getRuleForGrammarPoint(grammarPoint);
    }
    return 'Perhatikan aturan grammar yang berlaku untuk konteks ini.';
  }

  String _getRuleForGrammarPoint(String grammarPoint) {
    switch (grammarPoint) {
      case 'simple_past':
        return 'Simple past tense digunakan untuk aksi yang sudah selesai di masa lalu. Bentuk: subjek + verb2 (past tense).';
      case 'present_perfect':
        return 'Present perfect digunakan untuk aksi yang dimulai di masa lalu dan masih relevan. Bentuk: have/has + past participle.';
      case 'relative_clause':
        return 'Relative clause menggunakan pronoun (who, which, that) yang sesuai dengan antecedent-nya.';
      case 'conditional_3':
        return 'Third conditional untuk situasi hipotetis di masa lalu. Struktur: if + past perfect, would have + past participle.';
      case 'passive_voice':
        return 'Passive voice: be + past participle. Subjek menerima aksi, bukan melakukan aksi.';
      default:
        return 'Perhatikan aturan grammar yang berlaku untuk topik ini.';
    }
  }

  /// Get the correct choice from question, with validation
  /// Returns null if no valid correct choice found
  /// Validates that answer field matches isCorrect flag
  QuestionChoice? _getCorrectChoice(Question question) {
    if (question.choices.isEmpty) {
      return null;
    }

    final correctChoices = question.choices.where((c) => c.isCorrect).toList();

    if (correctChoices.isEmpty) {
      // No correct choice found - this is a data error
      // Try to find by matching answer field as fallback
      final matchingByAnswer = question.choices.firstWhere(
        (c) => c.choiceId.toLowerCase() == question.answer.toLowerCase(),
        orElse: () => QuestionChoice(choiceId: '', text: ''),
      );

      if (matchingByAnswer.choiceId.isNotEmpty) {
        // Found by answer field, but isCorrect flag is missing - data inconsistency
        return matchingByAnswer;
      }

      // Still no match, return null
      return null;
    } else if (correctChoices.length > 1) {
      // Multiple correct choices - data error, but use first one
      // Validate that answer field matches at least one correct choice
      final answerMatches = correctChoices.any(
        (c) => c.choiceId.toLowerCase() == question.answer.toLowerCase(),
      );
      if (!answerMatches) {
        // Answer field doesn't match any correct choice - data inconsistency
        // Still return first correct choice, but this should be fixed in data
      }
      return correctChoices.first;
    } else {
      // Exactly one correct choice - validate answer field matches
      final correctChoice = correctChoices.first;
      final answerMatches = correctChoice.choiceId.toLowerCase() == question.answer.toLowerCase();
      
      if (!answerMatches) {
        // Answer field doesn't match correct choice - data inconsistency
        // For gap_fill questions, answer might be text instead of choiceId
        if (question.type == 'gap_fill') {
          final answerMatchesText = correctChoice.text.toLowerCase().trim() == question.answer.toLowerCase().trim();
          if (answerMatchesText) {
            // Answer is text, which is acceptable for gap_fill
            return correctChoice;
          }
        }
        // For other types, this is an error, but return correct choice anyway
        // The data should be fixed, but we don't want to crash the app
      }
      
      return correctChoice;
    }
  }
}

