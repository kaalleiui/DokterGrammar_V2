// Migration script to add standardized answers to existing questions
// Run with: dart run scripts/migrate_questions_to_standardized.dart

import 'dart:io';
import 'dart:convert';

void main() async {
  print('🔄 Starting question migration to standardized answer format...\n');

  // Find all question bank files
  final questionBankFiles = [
    'assets/data/question_bank1.json',
    'assets/data/question_bank2.json',
    'assets/data/question_bank3.json',
    'assets/data/question_bank.json',
  ];

  int totalQuestions = 0;
  int migratedQuestions = 0;
  int fixedQuestions = 0;
  final errors = <String>[];

  for (final filePath in questionBankFiles) {
    final file = File(filePath);
    if (!await file.exists()) {
      print('⚠️  File not found: $filePath');
      continue;
    }

    print('📄 Processing: $filePath');
    
    try {
      final content = await file.readAsString();
      final List<dynamic> jsonData = json.decode(content);
      
      final migratedData = <Map<String, dynamic>>[];
      
      for (final questionJson in jsonData) {
        totalQuestions++;
        
        try {
          // Check if already has standardizedAnswer
          if (questionJson['standardizedAnswer'] != null) {
            migratedData.add(questionJson as Map<String, dynamic>);
            migratedQuestions++;
            continue;
          }

          // Create standardized answer from legacy format
          final questionType = questionJson['type'] as String? ?? 'multiple_choice';
          final answer = questionJson['answer'] as String? ?? '';
          final choicesJson = questionJson['choices'] as List? ?? [];
          
          // Determine format (default to 'text' if unknown type)
          String format = 'text';
          String? choiceId;
          String? displayText = answer;

          if (questionType == 'multiple_choice') {
            format = 'choiceId';
            choiceId = answer;
            // Find display text from choices
            for (final choiceJson in choicesJson) {
              final choiceIdStr = (choiceJson as Map<String, dynamic>)['choiceId'] as String?;
              if (choiceIdStr != null && choiceIdStr.toLowerCase() == answer.toLowerCase()) {
                displayText = (choiceJson['text'] as String?) ?? answer;
                break;
              }
            }
            displayText ??= answer;
          } else if (questionType == 'gap_fill') {
            // Check if answer is choiceId or text
            bool isChoiceId = false;
            for (final choiceJson in choicesJson) {
              final choiceIdStr = (choiceJson as Map<String, dynamic>)['choiceId'] as String?;
              if (choiceIdStr != null && choiceIdStr.toLowerCase() == answer.toLowerCase()) {
                isChoiceId = true;
                format = 'choiceId';
                choiceId = answer;
                displayText = (choiceJson['text'] as String?) ?? answer;
                break;
              }
            }
            if (!isChoiceId) {
              format = 'text';
              displayText = answer;
            }
          } else if (questionType == 'reorder') {
            format = 'sequence';
            displayText = answer;
          } else {
            // Default to text format
            format = 'text';
            displayText = answer;
          }

          // Add standardized answer
          final migratedQuestion = Map<String, dynamic>.from(questionJson);
          migratedQuestion['standardizedAnswer'] = {
            'format': format,
            'value': answer,
            'choiceId': choiceId,
            'displayText': displayText,
          };

          // Fix answer field if needed (sync with isCorrect)
          if (choicesJson.isNotEmpty) {
            final correctChoices = choicesJson.where((c) {
              final choice = c as Map<String, dynamic>;
              return choice['isCorrect'] == true;
            }).toList();
            if (correctChoices.isNotEmpty) {
              final firstCorrect = correctChoices.first as Map<String, dynamic>;
              final correctChoiceId = firstCorrect['choiceId'] as String?;
              if (correctChoiceId != null && 
                  questionType == 'multiple_choice' && 
                  answer != correctChoiceId) {
                migratedQuestion['answer'] = correctChoiceId;
                fixedQuestions++;
              }
            }
          }

          migratedData.add(migratedQuestion);
          migratedQuestions++;
        } catch (e) {
          errors.add('Error processing question ${questionJson['id']}: $e');
        }
      }

      // Write back to file
      await file.writeAsString(
        const JsonEncoder.withIndent('  ').convert(migratedData),
      );
      
      print('✅ Migrated ${migratedData.length} questions in $filePath');
    } catch (e) {
      errors.add('Error processing file $filePath: $e');
      print('❌ Error: $e');
    }
  }

  print('\n📊 Migration Summary:');
  print('  Total questions: $totalQuestions');
  print('  Migrated: $migratedQuestions');
  print('  Fixed: $fixedQuestions');
  
  if (errors.isNotEmpty) {
    print('\n❌ Errors (${errors.length}):');
    for (final error in errors.take(10)) {
      print('  • $error');
    }
    if (errors.length > 10) {
      print('  ... and ${errors.length - 10} more errors');
    }
  } else {
    print('\n✅ Migration completed successfully!');
  }
}

