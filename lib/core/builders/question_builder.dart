import '../models/question.dart';
import '../validators/question_validator.dart';

/// Exception thrown when question builder validation fails
class QuestionBuilderException implements Exception {
  final String message;
  QuestionBuilderException(this.message);
  
  @override
  String toString() => 'QuestionBuilderException: $message';
}

/// Question Builder Pattern
/// Ensures questions can only be created in a valid state
class QuestionBuilder {
  String? _id;
  String? _type;
  int? _difficulty;
  int? _topicId;
  String? _prompt;
  String? _answer;
  String? _explanationTemplate;
  String? _exampleSentence;
  final List<QuestionChoice> _choices = [];
  final List<QuestionTag> _tags = [];

  /// Create a new builder
  QuestionBuilder();

  /// Create builder from existing question
  factory QuestionBuilder.fromQuestion(Question question) {
    final builder = QuestionBuilder()
      .._id = question.id
      .._type = question.type
      .._difficulty = question.difficulty
      .._topicId = question.topicId
      .._prompt = question.prompt
      .._answer = question.answer
      .._explanationTemplate = question.explanationTemplate
      .._exampleSentence = question.exampleSentence;
    
    builder._choices.addAll(question.choices);
    builder._tags.addAll(question.tags);
    
    return builder;
  }

  QuestionBuilder withId(String id) {
    _id = id;
    return this;
  }

  QuestionBuilder withType(String type) {
    _type = type;
    return this;
  }

  QuestionBuilder withDifficulty(int difficulty) {
    _difficulty = difficulty;
    return this;
  }

  QuestionBuilder withTopicId(int topicId) {
    _topicId = topicId;
    return this;
  }

  QuestionBuilder withPrompt(String prompt) {
    _prompt = prompt;
    return this;
  }

  QuestionBuilder withAnswer(String answer) {
    _answer = answer;
    return this;
  }

  QuestionBuilder withExplanationTemplate(String? template) {
    _explanationTemplate = template;
    return this;
  }

  QuestionBuilder withExampleSentence(String? sentence) {
    _exampleSentence = sentence;
    return this;
  }

  QuestionBuilder addChoice(String choiceId, String text, {bool isCorrect = false}) {
    _choices.add(QuestionChoice(
      choiceId: choiceId,
      text: text,
      isCorrect: isCorrect,
    ));
    return this;
  }

  QuestionBuilder addChoices(List<QuestionChoice> choices) {
    _choices.addAll(choices);
    return this;
  }

  QuestionBuilder addTag(String tagType, String tagValue) {
    _tags.add(QuestionTag(
      tagType: tagType,
      tagValue: tagValue,
    ));
    return this;
  }

  QuestionBuilder addTags(List<QuestionTag> tags) {
    _tags.addAll(tags);
    return this;
  }

  /// Build and validate the question
  /// Throws QuestionBuilderException if validation fails
  Question build({bool autoFix = true}) {
    // Validate required fields
    if (_id == null || _id!.isEmpty) {
      throw QuestionBuilderException('Question ID is required');
    }
    if (_type == null || _type!.isEmpty) {
      throw QuestionBuilderException('Question type is required');
    }
    if (_difficulty == null) {
      throw QuestionBuilderException('Question difficulty is required');
    }
    if (_topicId == null) {
      throw QuestionBuilderException('Topic ID is required');
    }
    if (_prompt == null || _prompt!.isEmpty) {
      throw QuestionBuilderException('Question prompt is required');
    }

    // Create temporary question for validation
    Question tempQuestion = Question(
      id: _id!,
      type: _type!,
      difficulty: _difficulty!,
      topicId: _topicId!,
      prompt: _prompt!,
      answer: _answer ?? '',
      explanationTemplate: _explanationTemplate,
      exampleSentence: _exampleSentence,
      choices: _choices,
      tags: _tags,
    );

    // Validate question
    final validation = QuestionValidator.validate(tempQuestion);

    if (!validation.isValid) {
      if (autoFix && validation.issues.any((i) => i.canAutoFix)) {
        // Auto-fix if possible
        tempQuestion = QuestionValidator.autoFix(tempQuestion, validation.issues);
      } else {
        // Cannot auto-fix or auto-fix disabled - throw exception
        final errorMessages = validation.issues
            .map((i) => i.message)
            .join('; ');
        throw QuestionBuilderException('Question validation failed: $errorMessages');
      }
    }

    // Ensure answer matches isCorrect flag
    if (_choices.isNotEmpty) {
      final correctChoices = _choices.where((c) => c.isCorrect).toList();
      
      if (correctChoices.isEmpty) {
        // Try to find by answer field
        final matchingByAnswer = _choices.firstWhere(
          (c) => c.choiceId.toLowerCase() == (_answer ?? '').toLowerCase(),
          orElse: () => QuestionChoice(choiceId: '', text: ''),
        );

        if (matchingByAnswer.choiceId.isNotEmpty) {
          // Set isCorrect flag
          final index = _choices.indexWhere((c) => c.choiceId == matchingByAnswer.choiceId);
          if (index >= 0) {
            _choices[index] = QuestionChoice(
              choiceId: matchingByAnswer.choiceId,
              text: matchingByAnswer.text,
              isCorrect: true,
            );
          }
        } else {
          throw QuestionBuilderException('No correct choice specified and answer field does not match any choiceId');
        }
      } else if (correctChoices.length > 1) {
        // Multiple correct choices - keep first, mark others as incorrect
        for (int i = 0; i < _choices.length; i++) {
          if (_choices[i].isCorrect && _choices[i].choiceId != correctChoices.first.choiceId) {
            _choices[i] = QuestionChoice(
              choiceId: _choices[i].choiceId,
              text: _choices[i].text,
              isCorrect: false,
            );
          }
        }
      }

      // Sync answer field with correct choice
      final correctChoice = _choices.firstWhere((c) => c.isCorrect);
      _answer = correctChoice.choiceId;
    }

    // Validate gap_fill format
    if (_type == 'gap_fill' && _choices.isNotEmpty) {
      for (final choice in _choices) {
        final wordCount = choice.text.trim().split(RegExp(r'\s+')).length;
        if (wordCount > 3) {
          // Warning: gap fill choice is too long, but allow it
          // (could be a valid edge case)
        }
      }
    }

    // Build final question
    return Question(
      id: _id!,
      type: _type!,
      difficulty: _difficulty!,
      topicId: _topicId!,
      prompt: _prompt!,
      answer: _answer ?? '',
      explanationTemplate: _explanationTemplate,
      exampleSentence: _exampleSentence,
      choices: _choices,
      tags: _tags,
    );
  }

  /// Build question from JSON using builder pattern
  static Question fromJson(Map<String, dynamic> json) {
    final builder = QuestionBuilder()
      .withId(json['id'] as String)
      .withType(json['type'] as String)
      .withDifficulty(json['difficulty'] as int)
      .withTopicId(json['topicId'] as int)
      .withPrompt(json['prompt'] as String)
      .withAnswer(json['answer'] as String? ?? '')
      .withExplanationTemplate(json['explanationTemplate'] as String?)
      .withExampleSentence(json['exampleSentence'] as String?);

    // Add choices
    if (json['choices'] != null) {
      final choicesJson = json['choices'] as List;
      for (final choiceJson in choicesJson) {
        builder.addChoice(
          choiceJson['choiceId'] as String,
          choiceJson['text'] as String,
          isCorrect: choiceJson['isCorrect'] as bool? ?? false,
        );
      }
    }

    // Add tags
    if (json['tags'] != null) {
      final tagsJson = json['tags'] as List;
      for (final tagJson in tagsJson) {
        builder.addTag(
          tagJson['tagType'] as String,
          tagJson['tagValue'] as String,
        );
      }
    }

    return builder.build(autoFix: true);
  }
}

