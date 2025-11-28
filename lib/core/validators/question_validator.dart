import '../models/question.dart';

/// Validation issue types
enum ValidationIssueType {
  missingCorrectChoice,
  multipleCorrectChoices,
  answerMismatch,
  gapFillFormatInconsistency,
  missingRequiredField,
  invalidChoiceFormat,
}

/// Validation issue
class ValidationIssue {
  final ValidationIssueType type;
  final String message;
  final bool canAutoFix;

  ValidationIssue({
    required this.type,
    required this.message,
    this.canAutoFix = false,
  });
}

/// Validation result
class ValidationResult {
  final bool isValid;
  final List<ValidationIssue> issues;
  final bool hasErrors;  // true if any issue is critical
  final bool hasWarnings;  // true if any issue is non-critical

  ValidationResult({
    required this.isValid,
    required this.issues,
    this.hasErrors = false,
    this.hasWarnings = false,
  });

  static ValidationResult valid() => ValidationResult(
    isValid: true,
    issues: [],
  );

  static ValidationResult invalid(List<ValidationIssue> issues) {
    final hasErrors = issues.any((i) => 
      i.type == ValidationIssueType.missingCorrectChoice ||
      i.type == ValidationIssueType.multipleCorrectChoices ||
      i.type == ValidationIssueType.answerMismatch ||
      i.type == ValidationIssueType.missingRequiredField
    );
    
    return ValidationResult(
      isValid: false,
      issues: issues,
      hasErrors: hasErrors,
      hasWarnings: !hasErrors,
    );
  }
}

/// Question Validator Service
/// Validates question data integrity and provides auto-fix capabilities
class QuestionValidator {
  /// Validate a question and return validation result
  static ValidationResult validate(Question question) {
    final issues = <ValidationIssue>[];

    // 1. Check required fields
    if (question.id.isEmpty) {
      issues.add(ValidationIssue(
        type: ValidationIssueType.missingRequiredField,
        message: 'Missing question ID',
        canAutoFix: false,
      ));
    }

    if (question.type.isEmpty) {
      issues.add(ValidationIssue(
        type: ValidationIssueType.missingRequiredField,
        message: 'Missing question type',
        canAutoFix: false,
      ));
    }

    if (question.answer.isEmpty) {
      issues.add(ValidationIssue(
        type: ValidationIssueType.missingRequiredField,
        message: 'Missing answer field',
        canAutoFix: false,
      ));
    }

    // 2. Validate choices and answer consistency
    if (question.choices.isNotEmpty) {
      final correctChoices = question.choices.where((c) => c.isCorrect).toList();

      if (correctChoices.isEmpty) {
        // Try to find by matching answer field
        final matchingByAnswer = question.choices.firstWhere(
          (c) => c.choiceId.toLowerCase() == question.answer.toLowerCase(),
          orElse: () => QuestionChoice(choiceId: '', text: ''),
        );

        if (matchingByAnswer.choiceId.isEmpty) {
          issues.add(ValidationIssue(
            type: ValidationIssueType.missingCorrectChoice,
            message: 'No correct choice found and answer field does not match any choiceId',
            canAutoFix: false,
          ));
        } else {
          // Can auto-fix: set isCorrect flag
          issues.add(ValidationIssue(
            type: ValidationIssueType.answerMismatch,
            message: 'Answer field matches choiceId but isCorrect flag not set',
            canAutoFix: true,
          ));
        }
      } else if (correctChoices.length > 1) {
        issues.add(ValidationIssue(
          type: ValidationIssueType.multipleCorrectChoices,
          message: 'Multiple choices have isCorrect: true (${correctChoices.length} found)',
          canAutoFix: true,  // Can fix by keeping first and removing others
        ));
      } else {
        // Exactly one correct choice - validate answer field matches
        final correctChoice = correctChoices.first;
        final answerIsChoiceId = question.choices.any(
          (c) => c.choiceId.toLowerCase() == question.answer.toLowerCase(),
        );

        if (answerIsChoiceId && question.answer.toLowerCase() != correctChoice.choiceId.toLowerCase()) {
          issues.add(ValidationIssue(
            type: ValidationIssueType.answerMismatch,
            message: 'Answer field "${question.answer}" does not match correct choiceId "${correctChoice.choiceId}"',
            canAutoFix: true,  // Can fix by updating answer field
          ));
        } else if (!answerIsChoiceId && question.type == 'gap_fill') {
          // For gap_fill, answer might be text - check if it matches choice text
          final matchingTextChoice = question.choices.firstWhere(
            (c) => c.text.toLowerCase().trim() == question.answer.toLowerCase().trim(),
            orElse: () => QuestionChoice(choiceId: '', text: ''),
          );

          if (matchingTextChoice.choiceId.isEmpty) {
            // Gap fill answer is text but doesn't match any choice - acceptable
            // But we should note this for consistency
            issues.add(ValidationIssue(
              type: ValidationIssueType.gapFillFormatInconsistency,
              message: 'Gap fill answer is text that does not match any choice text',
              canAutoFix: false,
            ));
          }
        } else if (!answerIsChoiceId && question.type != 'gap_fill' && question.type != 'short_answer') {
          issues.add(ValidationIssue(
            type: ValidationIssueType.answerMismatch,
            message: 'Answer field "${question.answer}" does not match any choiceId',
            canAutoFix: false,
          ));
        }
      }

      // 3. Validate gap_fill format consistency
      if (question.type == 'gap_fill') {
        // Gap fill choices should be short (1-3 words), not full sentences
        for (final choice in question.choices) {
          final wordCount = choice.text.trim().split(RegExp(r'\s+')).length;
          if (wordCount > 3) {
            issues.add(ValidationIssue(
              type: ValidationIssueType.invalidChoiceFormat,
              message: 'Gap fill choice "${choice.text}" is too long (${wordCount} words, should be 1-3)',
              canAutoFix: false,
            ));
          }
        }
      }
    }

    if (issues.isEmpty) {
      return ValidationResult.valid();
    }

    return ValidationResult.invalid(issues);
  }

  /// Auto-fix a question based on validation issues
  static Question autoFix(Question question, List<ValidationIssue> issues) {
    Question fixedQuestion = question;
    final fixedChoices = List<QuestionChoice>.from(question.choices);

    for (final issue in issues) {
      if (!issue.canAutoFix) continue;

      switch (issue.type) {
        case ValidationIssueType.answerMismatch:
          // Fix: Update answer field to match isCorrect flag
          final correctChoice = fixedChoices.firstWhere(
            (c) => c.isCorrect,
            orElse: () => QuestionChoice(choiceId: '', text: ''),
          );

          if (correctChoice.choiceId.isNotEmpty) {
            fixedQuestion = Question(
              id: fixedQuestion.id,
              type: fixedQuestion.type,
              difficulty: fixedQuestion.difficulty,
              topicId: fixedQuestion.topicId,
              prompt: fixedQuestion.prompt,
              answer: correctChoice.choiceId,  // Fix answer field
              explanationTemplate: fixedQuestion.explanationTemplate,
              exampleSentence: fixedQuestion.exampleSentence,
              choices: fixedChoices,
              tags: fixedQuestion.tags,
            );
          } else {
            // Try to set isCorrect flag based on answer field
            final matchingChoice = fixedChoices.firstWhere(
              (c) => c.choiceId.toLowerCase() == fixedQuestion.answer.toLowerCase(),
              orElse: () => QuestionChoice(choiceId: '', text: ''),
            );

            if (matchingChoice.choiceId.isNotEmpty) {
              // Update the choice to be correct
              final index = fixedChoices.indexWhere(
                (c) => c.choiceId == matchingChoice.choiceId,
              );
              if (index >= 0) {
                fixedChoices[index] = QuestionChoice(
                  choiceId: matchingChoice.choiceId,
                  text: matchingChoice.text,
                  isCorrect: true,
                );
              }
            }
          }
          break;

        case ValidationIssueType.multipleCorrectChoices:
          // Fix: Keep first correct choice, mark others as incorrect
          final correctChoices = fixedChoices.where((c) => c.isCorrect).toList();
          if (correctChoices.length > 1) {
            // Keep first, mark others as incorrect
            for (int i = 0; i < fixedChoices.length; i++) {
              if (fixedChoices[i].isCorrect && fixedChoices[i].choiceId != correctChoices.first.choiceId) {
                fixedChoices[i] = QuestionChoice(
                  choiceId: fixedChoices[i].choiceId,
                  text: fixedChoices[i].text,
                  isCorrect: false,
                );
              }
            }
            // Update answer field to match
            fixedQuestion = Question(
              id: fixedQuestion.id,
              type: fixedQuestion.type,
              difficulty: fixedQuestion.difficulty,
              topicId: fixedQuestion.topicId,
              prompt: fixedQuestion.prompt,
              answer: correctChoices.first.choiceId,
              explanationTemplate: fixedQuestion.explanationTemplate,
              exampleSentence: fixedQuestion.exampleSentence,
              choices: fixedChoices,
              tags: fixedQuestion.tags,
            );
          }
          break;

        default:
          // Other issues cannot be auto-fixed
          break;
      }
    }

    return fixedQuestion;
  }

  /// Verify question integrity after database operations
  static Future<bool> verifyIntegrity(Question question) async {
    final validation = validate(question);
    return validation.isValid;
  }
}

