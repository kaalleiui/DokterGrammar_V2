# Flutter ONNX Integration Guide

## For Android Production Deployment

Since localhost server won't work on Android, we need to bundle the model with the app using ONNX.

## Step 1: Export Model to ONNX

### Option A: Use Simple Export Script

```bash
python export_model_simple.py
```

This uses a temp directory to avoid Windows path length issues.

### Option B: Manual Export with Short Path

```bash
# Copy model to shorter path
mkdir C:\m
xcopy models\dialogpt_grammar C:\m\g /E /I

# Export
python export_model_to_onnx.py --model-dir C:\m\g --output-dir C:\m\onnx
```

## Step 2: Add ONNX Model to Flutter

### 2.1 Copy Model Files

Copy these files to `assets/models/`:
- `grammar_explainer.onnx` (or `grammar_explainer_quantized.onnx`)
- `vocab.json`
- `tokenizer_config.json`

### 2.2 Update pubspec.yaml

```yaml
flutter:
  assets:
    - assets/models/grammar_explainer.onnx
    - assets/models/vocab.json
    - assets/models/tokenizer_config.json
```

### 2.3 Add ONNX Runtime Dependency

```yaml
dependencies:
  onnxruntime: ^1.15.0  # Check latest version
  # OR
  # ort_flutter: ^0.1.0  # Alternative package
```

## Step 3: Update AIService.dart

```dart
import 'package:onnxruntime/onnxruntime.dart';
import 'package:flutter/services.dart';
import 'dart:convert';

class AIService {
  static OrtValue? _model;
  static OrtSession? _session;
  static bool _modelLoaded = false;
  
  /// Initialize ONNX model
  static Future<void> initialize() async {
    try {
      // Load model from assets
      final modelBytes = await rootBundle.load('assets/models/grammar_explainer.onnx');
      
      // Create ONNX session
      _session = OrtSession.fromBuffer(modelBytes.buffer.asUint8List());
      _modelLoaded = true;
      
      print('[OK] ONNX model loaded');
    } catch (e) {
      print('[ERROR] Failed to load ONNX model: $e');
      _modelLoaded = false;
    }
  }
  
  /// Generate explanation using ONNX model
  static Future<Map<String, dynamic>> generateExplanation({
    required Question question,
    required String? userAnswer,
    required bool? isCorrect,
    required List<String> userInterests,
    Map<String, dynamic>? context,
  }) async {
    // Try ONNX model first
    if (_modelLoaded && _session != null) {
      try {
        final explanation = await _generateWithONNX(
          question: question,
          userAnswer: userAnswer,
          isCorrect: isCorrect,
        );
        
        if (explanation != null) {
          return {
            'text': explanation,
            'type': 'ai_generated',
            'confidence': 0.85,
            'rule_applied': _getRuleIdFromQuestion(question),
            'example': question.exampleSentence,
            'follow_up_available': false,
            'related_topics': _getRelatedTopics(question),
            'generation_time_ms': 0,
          };
        }
      } catch (e) {
        print('[WARN] ONNX generation failed: $e');
      }
    }
    
    // Fallback to rule-based
    return _generateRuleBasedExplanation(
      question: question,
      userAnswer: userAnswer,
      isCorrect: isCorrect,
    );
  }
  
  /// Generate with ONNX model
  static Future<String?> _generateWithONNX({
    required Question question,
    required String? userAnswer,
    required bool? isCorrect,
  }) async {
    // Format input context
    final context = _formatContext(question, userAnswer, isCorrect);
    final inputText = '<|user|>$context<|assistant|>';
    
    // Tokenize (you'll need to implement tokenization)
    final inputIds = _tokenize(inputText);
    
    // Run inference
    final inputs = {
      'input_ids': OrtValueTensor.createTensorWithDataAsList(
        [inputIds],
        [1, inputIds.length],
        OrtTensorType.ortTensorTypeInt64,
      ),
    };
    
    final outputs = _session!.run(OrtValueTensor.createTensorWithDataAsList(
      inputs,
      [1, inputIds.length],
      OrtTensorType.ortTensorTypeInt64,
    ));
    
    // Decode output
    final outputIds = outputs[0].value as List<List<int>>;
    final explanation = _detokenize(outputIds[0]);
    
    return explanation;
  }
  
  // Tokenization and detokenization methods
  // (You'll need to implement these based on your tokenizer)
  static List<int> _tokenize(String text) {
    // Load vocab.json and implement BPE tokenization
    // This is complex - consider using a simpler approach
    return [];
  }
  
  static String _detokenize(List<int> tokenIds) {
    // Implement detokenization
    return '';
  }
}
```

## Step 4: Alternative - Use Python Script on Device

If ONNX is too complex, consider:

### Option A: Bundle Python with App

Use packages like:
- `python_flutter_bridge`
- `chaquopy` (Android only)

### Option B: Pre-generate Explanations

Generate explanations for all questions during build, store in JSON.

## ⚠️ Complexity Warning

ONNX integration in Flutter is complex because:
1. Tokenization needs to be reimplemented in Dart
2. ONNX runtime setup can be tricky
3. Model format conversion may lose some features

## 🎯 Recommended Approach

**For now (MVP):**
- Keep rule-based system (it works well)
- Use AI server for development/testing
- Plan ONNX integration for future version

**For production:**
- Fix ONNX export
- Integrate ONNX in Flutter
- Or: Pre-generate explanations and bundle JSON

## Quick Alternative: Pre-generate Explanations

Generate all explanations during build, store in JSON:

```python
# generate_all_explanations.py
# Run this during build process
# Generates explanations for all questions
# Saves to assets/data/explanations.json
```

Then Flutter just loads from JSON - no model needed!

---

**Status**: ONNX integration is complex
**Recommendation**: Use rule-based for now, plan ONNX for v2

