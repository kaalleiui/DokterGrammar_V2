import 'standardized_answer.dart';
import '../builders/question_builder.dart';

class Question {
  final String id;
  final String type; // 'multiple_choice', 'gap_fill', etc.
  final int difficulty; // 1-5
  final int topicId;
  final String prompt;
  final String answer; // JSON string for complex answers (deprecated, use standardizedAnswer)
  final String? explanationTemplate;
  final String? exampleSentence;
  final List<QuestionChoice> choices;
  final List<QuestionTag> tags;
  final StandardizedAnswer? standardizedAnswer; // NEW: Single source of truth for answers

  Question({
    required this.id,
    required this.type,
    required this.difficulty,
    required this.topicId,
    required this.prompt,
    required this.answer,
    this.explanationTemplate,
    this.exampleSentence,
    required this.choices,
    required this.tags,
    this.standardizedAnswer,
  });

  /// Get standardized answer (creates if not exists)
  StandardizedAnswer getStandardizedAnswer() {
    if (standardizedAnswer != null) {
      return standardizedAnswer!;
    }
    // Create from legacy format
    return StandardizedAnswer.fromLegacy(
      questionType: type,
      answer: answer,
      choices: choices,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'type': type,
    'difficulty': difficulty,
    'topicId': topicId,
    'prompt': prompt,
    'answer': answer,
    'explanationTemplate': explanationTemplate,
    'exampleSentence': exampleSentence,
    'choices': choices.map((c) => c.toJson()).toList(),
    'tags': tags.map((t) => t.toJson()).toList(),
    if (standardizedAnswer != null) 'standardizedAnswer': standardizedAnswer!.toJson(),
  };

  /// Create from JSON using builder pattern (recommended)
  factory Question.fromJson(Map<String, dynamic> json) {
    // Use builder for validation and auto-fix
    try {
      return QuestionBuilder.fromJson(json);
    } catch (e) {
      // Fallback to old method if builder fails (backward compatibility)
      return Question(
        id: json['id'],
        type: json['type'],
        difficulty: json['difficulty'],
        topicId: json['topicId'],
        prompt: json['prompt'],
        answer: json['answer'],
        explanationTemplate: json['explanationTemplate'],
        exampleSentence: json['exampleSentence'],
        choices: (json['choices'] as List?)
            ?.map((c) => QuestionChoice.fromJson(c))
            .toList() ?? [],
        tags: (json['tags'] as List?)
            ?.map((t) => QuestionTag.fromJson(t))
            .toList() ?? [],
        standardizedAnswer: json['standardizedAnswer'] != null
            ? StandardizedAnswer.fromJson(json['standardizedAnswer'])
            : null,
      );
    }
  }

  /// Create immutable copy with modifications
  Question copyWith({
    String? id,
    String? type,
    int? difficulty,
    int? topicId,
    String? prompt,
    String? answer,
    String? explanationTemplate,
    String? exampleSentence,
    List<QuestionChoice>? choices,
    List<QuestionTag>? tags,
    StandardizedAnswer? standardizedAnswer,
  }) {
    return Question(
      id: id ?? this.id,
      type: type ?? this.type,
      difficulty: difficulty ?? this.difficulty,
      topicId: topicId ?? this.topicId,
      prompt: prompt ?? this.prompt,
      answer: answer ?? this.answer,
      explanationTemplate: explanationTemplate ?? this.explanationTemplate,
      exampleSentence: exampleSentence ?? this.exampleSentence,
      choices: choices ?? this.choices,
      tags: tags ?? this.tags,
      standardizedAnswer: standardizedAnswer ?? this.standardizedAnswer,
    );
  }
}

class QuestionChoice {
  final String choiceId; // 'a', 'b', 'c', 'd'
  final String text;
  final bool isCorrect;

  QuestionChoice({
    required this.choiceId,
    required this.text,
    this.isCorrect = false,
  });

  Map<String, dynamic> toJson() => {
    'choiceId': choiceId,
    'text': text,
    'isCorrect': isCorrect,
  };

  factory QuestionChoice.fromJson(Map<String, dynamic> json) => QuestionChoice(
    choiceId: json['choiceId'],
    text: json['text'],
    isCorrect: json['isCorrect'] ?? false,
  );
}

class QuestionTag {
  final String tagType; // 'interest', 'tense', 'grammar_point'
  final String tagValue; // 'anime', 'past', 'conditional_3'

  QuestionTag({
    required this.tagType,
    required this.tagValue,
  });

  Map<String, dynamic> toJson() => {
    'tagType': tagType,
    'tagValue': tagValue,
  };

  factory QuestionTag.fromJson(Map<String, dynamic> json) => QuestionTag(
    tagType: json['tagType'],
    tagValue: json['tagValue'],
  );
}

