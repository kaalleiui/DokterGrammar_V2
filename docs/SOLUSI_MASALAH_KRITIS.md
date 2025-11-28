# Solusi Masalah Kritis: Mismatch Pertanyaan dan Opsi Jawaban

**Tanggal**: 2024-11-27  
**Status**: 🔴 KRITIS  
**Masalah**: Pertanyaan dan opsi jawaban tidak sesuai, terjadi berulang meski sudah dimodifikasi 4x

---

## Analisis Masalah

Berdasarkan investigasi codebase, masalah ini kemungkinan disebabkan oleh:

1. **Data Quality Issues**: Meskipun validasi JSON pass, ada kemungkinan data ter-corrupt saat disimpan ke database
2. **Runtime Mismatch**: Pertanyaan dan choices terpisah di database, bisa terjadi mismatch saat query
3. **AI Engine Tidak Berfungsi**: Service AI hanya rule-based fallback, bukan AI sebenarnya
4. **Race Condition**: Saat load questions, choices mungkin belum ter-load dengan benar
5. **Validation Tidak Cukup**: Validasi hanya di JSON level, tidak di database level

---

## 5 Opsi Solusi

### **OPSI 1: Implementasi Validasi & Auto-Fix di Database Layer** ⭐ RECOMMENDED

**Konsep**: Tambahkan validasi dan auto-fix saat insert/load questions dari database

**Keuntungan**:
- Menangkap masalah di level database
- Auto-fix untuk data yang sudah corrupt
- Mencegah masalah baru masuk

**Implementasi**:
```dart
// Di question_local_datasource.dart
Future<void> insertQuestion(Question question) async {
  // 1. Validasi sebelum insert
  final validation = _validateQuestionData(question);
  if (!validation.isValid) {
    // Auto-fix jika mungkin
    question = _autoFixQuestion(question, validation.issues);
  }
  
  // 2. Insert dengan transaction untuk atomicity
  await db.transaction((txn) async {
    // Insert question
    // Insert choices dalam transaction yang sama
    // Insert tags dalam transaction yang sama
  });
  
  // 3. Verifikasi setelah insert
  final verify = await _verifyQuestionIntegrity(question.id);
  if (!verify.isValid) {
    throw Exception('Question integrity check failed: ${verify.message}');
  }
}
```

**File yang perlu diubah**:
- `lib/data/datasources/local/question_local_datasource.dart`
- Tambahkan method `_validateQuestionData()`, `_autoFixQuestion()`, `_verifyQuestionIntegrity()`

**Effort**: Medium (2-3 hari)  
**Risk**: Low  
**Impact**: High - Menyelesaikan masalah di root cause

---

### **OPSI 2: Refactor ke Single Source of Truth dengan Question Builder Pattern**

**Konsep**: Buat QuestionBuilder yang memastikan pertanyaan dan choices selalu konsisten

**Keuntungan**:
- Memastikan data integrity sejak awal
- Mencegah mismatch di level konstruksi
- Lebih mudah di-maintain

**Implementasi**:
```dart
class QuestionBuilder {
  String? _id;
  String? _type;
  String? _prompt;
  String? _answer;
  List<QuestionChoice> _choices = [];
  
  QuestionBuilder withId(String id) {
    _id = id;
    return this;
  }
  
  QuestionBuilder withPrompt(String prompt) {
    _prompt = prompt;
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
  
  QuestionBuilder withAnswer(String answer) {
    _answer = answer;
    // Auto-validate: jika answer adalah choiceId, set isCorrect
    final matchingChoice = _choices.firstWhere(
      (c) => c.choiceId.toLowerCase() == answer.toLowerCase(),
      orElse: () => QuestionChoice(choiceId: '', text: ''),
    );
    
    if (matchingChoice.choiceId.isNotEmpty) {
      // Unset semua isCorrect
      for (var choice in _choices) {
        choice = QuestionChoice(
          choiceId: choice.choiceId,
          text: choice.text,
          isCorrect: false,
        );
      }
      // Set yang benar
      final index = _choices.indexWhere((c) => c.choiceId == matchingChoice.choiceId);
      _choices[index] = QuestionChoice(
        choiceId: matchingChoice.choiceId,
        text: matchingChoice.text,
        isCorrect: true,
      );
    }
    return this;
  }
  
  Question build() {
    // Final validation
    _validate();
    return Question(
      id: _id!,
      type: _type!,
      prompt: _prompt!,
      answer: _answer!,
      choices: _choices,
      // ... other fields
    );
  }
  
  void _validate() {
    // Ensure answer matches a choice with isCorrect=true
    final correctChoices = _choices.where((c) => c.isCorrect).toList();
    if (correctChoices.length != 1) {
      throw Exception('Must have exactly one correct choice');
    }
    if (correctChoices.first.choiceId.toLowerCase() != _answer!.toLowerCase()) {
      throw Exception('Answer must match correct choiceId');
    }
  }
}
```

**File yang perlu diubah**:
- Buat `lib/core/builders/question_builder.dart`
- Update `Question.fromJson()` untuk menggunakan builder
- Update `question_bank_loader.dart` untuk menggunakan builder

**Effort**: Medium-High (3-4 hari)  
**Risk**: Medium  
**Impact**: High - Structural fix yang permanen

---

### **OPSI 3: Implementasi Real-Time Validation & Monitoring System**

**Konsep**: Tambahkan validation layer yang check setiap kali question di-load, dengan logging dan alert

**Keuntungan**:
- Deteksi masalah real-time
- Logging untuk debugging
- Bisa auto-fix atau skip question yang corrupt

**Implementasi**:
```dart
class QuestionValidator {
  static ValidationResult validateOnLoad(Question question) {
    final issues = <String>[];
    
    // Check 1: Choices exist
    if (question.choices.isEmpty && question.type == 'multiple_choice') {
      issues.add('Multiple choice question has no choices');
    }
    
    // Check 2: Answer matches a choice
    if (question.choices.isNotEmpty) {
      final answerMatches = question.choices.any(
        (c) => c.choiceId.toLowerCase() == question.answer.toLowerCase(),
      );
      if (!answerMatches) {
        issues.add('Answer "${question.answer}" does not match any choiceId');
      }
    }
    
    // Check 3: Exactly one correct choice
    final correctChoices = question.choices.where((c) => c.isCorrect).toList();
    if (correctChoices.length == 0) {
      issues.add('No choice marked as correct');
    } else if (correctChoices.length > 1) {
      issues.add('Multiple choices marked as correct (${correctChoices.length})');
    } else {
      // Check 4: Correct choice matches answer
      if (correctChoices.first.choiceId.toLowerCase() != question.answer.toLowerCase()) {
        issues.add('Answer "${question.answer}" does not match correct choice "${correctChoices.first.choiceId}"');
      }
    }
    
    return ValidationResult(
      isValid: issues.isEmpty,
      issues: issues,
      question: question,
    );
  }
  
  static Question? autoFix(Question question, ValidationResult validation) {
    if (validation.isValid) return question;
    
    // Try to fix common issues
    final issues = validation.issues;
    
    // Fix 1: Answer doesn't match, but there's a correct choice
    if (issues.any((i) => i.contains('does not match'))) {
      final correctChoice = question.choices.firstWhere(
        (c) => c.isCorrect,
        orElse: () => QuestionChoice(choiceId: '', text: ''),
      );
      if (correctChoice.choiceId.isNotEmpty) {
        // Update answer to match correct choice
        return Question(
          id: question.id,
          type: question.type,
          difficulty: question.difficulty,
          topicId: question.topicId,
          prompt: question.prompt,
          answer: correctChoice.choiceId, // FIX
          explanationTemplate: question.explanationTemplate,
          exampleSentence: question.exampleSentence,
          choices: question.choices,
          tags: question.tags,
        );
      }
    }
    
    // Fix 2: No correct choice, but answer matches a choiceId
    if (issues.any((i) => i.contains('No choice marked'))) {
      final matchingChoice = question.choices.firstWhere(
        (c) => c.choiceId.toLowerCase() == question.answer.toLowerCase(),
        orElse: () => QuestionChoice(choiceId: '', text: ''),
      );
      if (matchingChoice.choiceId.isNotEmpty) {
        // Mark matching choice as correct
        final fixedChoices = question.choices.map((c) {
          return QuestionChoice(
            choiceId: c.choiceId,
            text: c.text,
            isCorrect: c.choiceId == matchingChoice.choiceId, // FIX
          );
        }).toList();
        
        return Question(
          id: question.id,
          type: question.type,
          difficulty: question.difficulty,
          topicId: question.topicId,
          prompt: question.prompt,
          answer: question.answer,
          explanationTemplate: question.explanationTemplate,
          exampleSentence: question.exampleSentence,
          choices: fixedChoices,
          tags: question.tags,
        );
      }
    }
    
    // Cannot auto-fix
    return null;
  }
}

// Usage di question_local_datasource.dart
Future<Question?> getQuestionById(String questionId) async {
  final question = await _loadQuestionFromDb(questionId);
  if (question == null) return null;
  
  // Validate
  final validation = QuestionValidator.validateOnLoad(question);
  
  if (!validation.isValid) {
    // Log issue
    if (kDebugMode) {
      debugPrint('⚠️ Question ${question.id} has issues:');
      for (final issue in validation.issues) {
        debugPrint('  - $issue');
      }
    }
    
    // Try auto-fix
    final fixed = QuestionValidator.autoFix(question, validation);
    if (fixed != null) {
      if (kDebugMode) {
        debugPrint('✅ Auto-fixed question ${question.id}');
      }
      // Optionally: Save fixed version back to DB
      return fixed;
    } else {
      // Cannot fix, skip or return null
      if (kDebugMode) {
        debugPrint('❌ Cannot auto-fix question ${question.id}, skipping');
      }
      return null; // atau return question as-is dengan warning
    }
  }
  
  return question;
}
```

**File yang perlu diubah**:
- Buat `lib/core/validators/question_validator.dart`
- Update `question_local_datasource.dart` untuk validate setiap load
- Update `question_bank_loader.dart` untuk validate saat load dari JSON

**Effort**: Medium (2-3 hari)  
**Risk**: Low  
**Impact**: High - Deteksi dan fix real-time

---

### **OPSI 4: Migrasi ke Embedded Question Format (Single JSON Field)**

**Konsep**: Simpan question + choices sebagai single JSON field di database, bukan terpisah

**Keuntungan**:
- Atomic: question dan choices selalu bersama
- Tidak bisa terjadi mismatch
- Lebih cepat query (single read)

**Implementasi**:
```sql
-- Update schema
ALTER TABLE questions ADD COLUMN question_data TEXT; -- JSON field

-- Migrate existing data
UPDATE questions SET question_data = (
  SELECT json_object(
    'id', q.id,
    'type', q.type,
    'prompt', q.prompt,
    'answer', q.answer,
    'choices', (
      SELECT json_group_array(
        json_object(
          'choiceId', qc.choice_id,
          'text', qc.text,
          'isCorrect', qc.is_correct
        )
      )
      FROM question_choices qc
      WHERE qc.question_id = q.id
    ),
    'tags', (
      SELECT json_group_array(
        json_object(
          'tagType', qt.tag_type,
          'tagValue', qt.tag_value
        )
      )
      FROM question_tags qt
      WHERE qt.question_id = q.id
    )
  )
  FROM questions q
  WHERE q.id = questions.id
);
```

```dart
// Update model untuk load dari JSON
factory Question.fromJsonString(String jsonString) {
  final json = jsonDecode(jsonString);
  return Question.fromJson(json);
}

// Update datasource
Future<Question?> getQuestionById(String questionId) async {
  final db = await _dbHelper.database;
  final result = await db.query(
    'questions',
    columns: ['question_data'],
    where: 'id = ?',
    whereArgs: [questionId],
  );
  
  if (result.isEmpty) return null;
  
  final jsonString = result.first['question_data'] as String;
  return Question.fromJsonString(jsonString);
}
```

**File yang perlu diubah**:
- `lib/core/database/schema.sql` - Add migration
- `lib/core/database/database_helper.dart` - Run migration
- `lib/data/datasources/local/question_local_datasource.dart` - Update queries
- Buat migration script

**Effort**: High (4-5 hari)  
**Risk**: Medium (perlu migration existing data)  
**Impact**: Very High - Structural fix yang permanen, tidak bisa mismatch lagi

---

### **OPSI 5: Implementasi AI-Powered Question Generator & Validator**

**Konsep**: Ganti rule-based AI dengan real AI (LLM API atau on-device model) untuk generate dan validate questions

**Keuntungan**:
- AI bisa detect semantic mismatch (bukan hanya syntax)
- Bisa generate questions yang lebih baik
- Bisa auto-fix dengan understanding context

**Implementasi**:
```dart
class AIPoweredQuestionService {
  // Option A: Use OpenAI/Anthropic API
  static Future<Question> generateQuestion({
    required String topic,
    required int difficulty,
    required String grammarPoint,
  }) async {
    final prompt = '''
Generate a grammar question for:
- Topic: $topic
- Grammar Point: $grammarPoint
- Difficulty: $difficulty

Requirements:
1. Create a clear, unambiguous question
2. Provide exactly 4 choices (a, b, c, d)
3. Only one choice should be correct
4. Wrong choices should be plausible but clearly wrong
5. Return as JSON with structure matching Question model
''';
    
    final response = await _callAIAPI(prompt);
    final questionJson = jsonDecode(response);
    
    // Validate dengan AI
    final validation = await _validateWithAI(questionJson);
    if (!validation.isValid) {
      // Ask AI to fix
      return await _fixWithAI(questionJson, validation.issues);
    }
    
    return Question.fromJson(questionJson);
  }
  
  // Option B: Use on-device model (TensorFlow Lite, ONNX)
  static Future<Question> validateAndFixQuestion(Question question) async {
    // Use ML model to check:
    // 1. Does prompt match choices semantically?
    // 2. Is correct answer actually correct?
    // 3. Are wrong answers plausibly wrong?
    
    final validation = await _onDeviceModel.validate(question);
    if (!validation.isValid) {
      return await _onDeviceModel.fix(question, validation);
    }
    return question;
  }
}
```

**File yang perlu diubah**:
- `lib/core/services/ai_service.dart` - Implementasi real AI
- Buat `lib/core/services/ai_question_validator.dart`
- Update `pubspec.yaml` untuk AI dependencies (http untuk API, atau tflite untuk on-device)

**Effort**: Very High (5-7 hari)  
**Risk**: High (perlu API key, atau model training)  
**Impact**: Very High - Solusi jangka panjang dengan AI yang benar-benar AI

---

## Rekomendasi Implementasi

### **Fase 1 (Immediate - 1-2 hari)**: Opsi 3
Implementasi real-time validation untuk detect dan auto-fix masalah yang ada sekarang.

### **Fase 2 (Short-term - 3-4 hari)**: Opsi 1
Tambahkan validasi di database layer untuk prevent masalah baru.

### **Fase 3 (Long-term - 1-2 minggu)**: Opsi 4 atau Opsi 2
Refactor ke embedded format atau builder pattern untuk structural fix permanen.

### **Fase 4 (Future)**: Opsi 5
Jika budget dan waktu memungkinkan, implementasi real AI.

---

## Quick Win: Hybrid Approach

**Kombinasi Opsi 1 + Opsi 3**:
1. Tambahkan validation di `question_local_datasource.dart` (Opsi 1)
2. Tambahkan real-time validator yang auto-fix (Opsi 3)
3. Log semua issues untuk monitoring
4. Buat dashboard untuk track question quality

**Effort**: 3-4 hari  
**Impact**: High  
**Risk**: Low

---

## Testing Strategy

Setelah implementasi, test dengan:

1. **Load Test**: Load semua 208 questions, check berapa yang fail validation
2. **Auto-Fix Test**: Check apakah auto-fix benar-benar fix masalah
3. **Integration Test**: Test full flow dari JSON → DB → UI
4. **Regression Test**: Pastikan tidak break existing functionality

---

## Monitoring & Metrics

Track metrics berikut:
- **Question Validation Failure Rate**: Berapa % questions yang fail validation
- **Auto-Fix Success Rate**: Berapa % yang berhasil di-fix otomatis
- **Mismatch Detection Rate**: Berapa banyak mismatch terdeteksi per hari
- **User-Reported Issues**: Track user complaints tentang wrong answers

---

**Status**: 📋 READY FOR IMPLEMENTATION  
**Next Step**: Pilih opsi yang sesuai dengan timeline dan resources

