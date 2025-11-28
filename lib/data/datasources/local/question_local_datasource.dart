import 'package:sqflite/sqflite.dart';
import '../../../core/database/database_helper.dart';
import '../../../core/models/question.dart';
import '../../../core/validators/question_validator.dart';

class QuestionLocalDataSource {
  final DatabaseHelper _dbHelper = DatabaseHelper.instance;

  Future<void> insertQuestion(Question question) async {
    // Validate and auto-fix before insert (Plan 1)
    final validation = QuestionValidator.validate(question);
    Question validatedQuestion = question;
    
    if (!validation.isValid && validation.issues.any((i) => i.canAutoFix)) {
      validatedQuestion = QuestionValidator.autoFix(question, validation.issues);
      // Log auto-fix for monitoring
      if (validation.hasErrors) {
        print('⚠️ Auto-fixed question ${question.id}: ${validation.issues.map((i) => i.message).join('; ')}');
      }
    } else if (validation.hasErrors) {
      // Critical errors that cannot be auto-fixed
      throw Exception('Cannot insert invalid question ${question.id}: ${validation.issues.map((i) => i.message).join('; ')}');
    }
    
    final db = await _dbHelper.database;
    
    // Use transaction for atomicity (Plan 1)
    await db.transaction((txn) async {
      // Insert question
      await txn.insert(
        'questions',
        {
          'id': validatedQuestion.id,
          'type': validatedQuestion.type,
          'difficulty': validatedQuestion.difficulty,
          'topic_id': validatedQuestion.topicId,
          'prompt': validatedQuestion.prompt,
          'answer': validatedQuestion.answer,
          'explanation_template': validatedQuestion.explanationTemplate,
          'example_sentence': validatedQuestion.exampleSentence,
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );

      // Insert choices
      for (final choice in validatedQuestion.choices) {
        await txn.insert(
          'question_choices',
          {
            'question_id': validatedQuestion.id,
            'choice_id': choice.choiceId,
            'text': choice.text,
            'is_correct': choice.isCorrect ? 1 : 0,
          },
          conflictAlgorithm: ConflictAlgorithm.replace,
        );
      }

      // Insert tags
      for (final tag in validatedQuestion.tags) {
        await txn.insert(
          'question_tags',
          {
            'question_id': validatedQuestion.id,
            'tag_type': tag.tagType,
            'tag_value': tag.tagValue,
          },
          conflictAlgorithm: ConflictAlgorithm.ignore,
        );
      }
    });
    
    // Verify integrity after insert (Plan 1)
    final verify = await QuestionValidator.verifyIntegrity(validatedQuestion);
    if (!verify) {
      print('⚠️ Warning: Question ${validatedQuestion.id} integrity check failed after insert');
    }
  }

  Future<void> insertQuestions(List<Question> questions) async {
    final batch = (await _dbHelper.database).batch();
    
    // Validate and auto-fix all questions before batch insert
    final validatedQuestions = <Question>[];
    for (final question in questions) {
      final validation = QuestionValidator.validate(question);
      Question validatedQuestion = question;
      
      if (!validation.isValid && validation.issues.any((i) => i.canAutoFix)) {
        validatedQuestion = QuestionValidator.autoFix(question, validation.issues);
      }
      
      validatedQuestions.add(validatedQuestion);
    }
    
    for (final question in validatedQuestions) {
      batch.insert(
        'questions',
        {
          'id': question.id,
          'type': question.type,
          'difficulty': question.difficulty,
          'topic_id': question.topicId,
          'prompt': question.prompt,
          'answer': question.answer,
          'explanation_template': question.explanationTemplate,
          'example_sentence': question.exampleSentence,
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );

      for (final choice in question.choices) {
        batch.insert(
          'question_choices',
          {
            'question_id': question.id,
            'choice_id': choice.choiceId,
            'text': choice.text,
            'is_correct': choice.isCorrect ? 1 : 0,
          },
          conflictAlgorithm: ConflictAlgorithm.replace,
        );
      }

      for (final tag in question.tags) {
        batch.insert(
          'question_tags',
          {
            'question_id': question.id,
            'tag_type': tag.tagType,
            'tag_value': tag.tagValue,
          },
          conflictAlgorithm: ConflictAlgorithm.ignore,
        );
      }
    }
    
    await batch.commit(noResult: true);
  }

  Future<Question?> getQuestionById(String questionId) async {
    final db = await _dbHelper.database;
    
    final questionMaps = await db.query(
      'questions',
      where: 'id = ?',
      whereArgs: [questionId],
      limit: 1,
    );

    if (questionMaps.isEmpty) return null;

    final questionMap = questionMaps.first;
    
    // Runtime validation on load (Plan 1)
    
    // Get choices
    final choiceMaps = await db.query(
      'question_choices',
      where: 'question_id = ?',
      whereArgs: [questionId],
      orderBy: 'choice_id',
    );
    final choices = choiceMaps.map((map) => QuestionChoice(
      choiceId: map['choice_id'] as String,
      text: map['text'] as String,
      isCorrect: (map['is_correct'] as int) == 1,
    )).toList();

    // Get tags
    final tagMaps = await db.query(
      'question_tags',
      where: 'question_id = ?',
      whereArgs: [questionId],
    );
    final tags = tagMaps.map((map) => QuestionTag(
      tagType: map['tag_type'] as String,
      tagValue: map['tag_value'] as String,
    )).toList();

    Question question = Question(
      id: questionMap['id'] as String,
      type: questionMap['type'] as String,
      difficulty: questionMap['difficulty'] as int,
      topicId: questionMap['topic_id'] as int,
      prompt: questionMap['prompt'] as String,
      answer: questionMap['answer'] as String,
      explanationTemplate: questionMap['explanation_template'] as String?,
      exampleSentence: questionMap['example_sentence'] as String?,
      choices: choices,
      tags: tags,
    );
    
    // Validate and auto-fix on load
    final validation = QuestionValidator.validate(question);
    if (!validation.isValid && validation.issues.any((i) => i.canAutoFix)) {
      question = QuestionValidator.autoFix(question, validation.issues);
      // Update database with fixed version
      await insertQuestion(question);
    }
    
    return question;
  }

  Future<List<Question>> getQuestionsByTopic(int topicId, {int? limit}) async {
    final db = await _dbHelper.database;
    
    final questionMaps = await db.query(
      'questions',
      where: 'topic_id = ?',
      whereArgs: [topicId],
      limit: limit,
    );

    final questions = <Question>[];
    
    for (final questionMap in questionMaps) {
      final questionId = questionMap['id'] as String;
      
      // Get choices
      final choiceMaps = await db.query(
        'question_choices',
        where: 'question_id = ?',
        whereArgs: [questionId],
        orderBy: 'choice_id',
      );
      final choices = choiceMaps.map((map) => QuestionChoice(
        choiceId: map['choice_id'] as String,
        text: map['text'] as String,
        isCorrect: (map['is_correct'] as int) == 1,
      )).toList();

      // Get tags
      final tagMaps = await db.query(
        'question_tags',
        where: 'question_id = ?',
        whereArgs: [questionId],
      );
      final tags = tagMaps.map((map) => QuestionTag(
        tagType: map['tag_type'] as String,
        tagValue: map['tag_value'] as String,
      )).toList();

      Question question = Question(
        id: questionId,
        type: questionMap['type'] as String,
        difficulty: questionMap['difficulty'] as int,
        topicId: questionMap['topic_id'] as int,
        prompt: questionMap['prompt'] as String,
        answer: questionMap['answer'] as String,
        explanationTemplate: questionMap['explanation_template'] as String?,
        exampleSentence: questionMap['example_sentence'] as String?,
        choices: choices,
        tags: tags,
      );
      
      // Validate and auto-fix on load
      final validation = QuestionValidator.validate(question);
      if (!validation.isValid && validation.issues.any((i) => i.canAutoFix)) {
        question = QuestionValidator.autoFix(question, validation.issues);
      }
      
      questions.add(question);
    }

    return questions;
  }

  Future<List<Question>> getQuestionsForPlacement({
    required List<String> userInterests,
    int totalQuestions = 50,
  }) async {
    final db = await _dbHelper.database;
    
    // Get all topics
    final topicMaps = await db.query('topics');
    final topics = topicMaps.map((map) => map['id'] as int).toList();
    
    // Distribute questions across topics
    final questionsPerTopic = (totalQuestions / topics.length).ceil();
    final allQuestions = <Question>[];
    
    for (final topicId in topics) {
      final topicQuestions = await getQuestionsByTopic(topicId, limit: questionsPerTopic);
      
      // Filter by interests if possible, otherwise take any
      final filtered = topicQuestions.where((q) {
        if (userInterests.isEmpty) return true;
        return q.tags.any((tag) => 
          tag.tagType == 'interest' && userInterests.contains(tag.tagValue)
        );
      }).toList();
      
      if (filtered.isNotEmpty) {
        allQuestions.addAll(filtered.take(questionsPerTopic));
      } else {
        allQuestions.addAll(topicQuestions.take(questionsPerTopic));
      }
    }
    
    // Shuffle and limit to totalQuestions
    allQuestions.shuffle();
    return allQuestions.take(totalQuestions).toList();
  }

  Future<int> getQuestionCount() async {
    final db = await _dbHelper.database;
    final result = await db.rawQuery('SELECT COUNT(*) as count FROM questions');
    return Sqflite.firstIntValue(result) ?? 0;
  }
}

