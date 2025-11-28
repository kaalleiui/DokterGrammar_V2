# DialogGPT Training Proposal for Dokter Grammar AI Engine

## Overview

This proposal outlines a plan to train a DialogGPT-style small model using your question bank to improve the AI explanation engine. The model will learn to generate natural, contextual explanations for grammar questions.

## Current State

- **Current System**: Rule-based template system (works but limited)
- **Question Bank**: ~200+ questions in JSON format with:
  - Prompts, choices, answers
  - Explanation templates
  - Grammar point tags
  - Example sentences
- **AI Service**: Framework exists but uses rule-based fallback

## Proposed Solution

### 1. Model Architecture
- **Base Model**: GPT-2 Small (117M parameters) - similar to DialogGPT
- **Fine-tuning**: Custom fine-tuning on grammar explanation dataset
- **Output Format**: ONNX for Flutter integration
- **Size**: ~45-50MB (suitable for mobile)

### 2. Training Data Generation

From your question bank, we'll create conversation-style training pairs:

**Input Format** (Context + Question):
```
Question: "Choose the correct form: 'I _____ to school every day.'"
User Answer: "went"
Correct Answer: "go"
Grammar Point: "simple_present"
Question Type: "multiple_choice"
```

**Output Format** (Explanation):
```
"Jawaban yang benar adalah 'go'. Pilihan 'went' tidak tepat karena menggunakan simple past tense untuk aksi yang sudah selesai di masa lalu, padahal kalimat ini menunjukkan aksi habitual (setiap hari). Simple present tense digunakan untuk aksi yang terjadi secara rutin. Contoh: I go to school every day."
```

### 3. Training Pipeline

1. **Data Extraction** (`prepare_training_data.py`)
   - Load all question bank JSON files
   - Extract questions, answers, explanations
   - Generate multiple training examples per question:
     - Correct answer scenario
     - Incorrect answer scenarios (for each wrong choice)
     - Varied explanation styles

2. **Data Formatting** (DialogGPT format)
   - Convert to conversation format
   - Add special tokens for context
   - Create train/validation splits

3. **Model Training** (`train_dialogpt_model.py`)
   - Load GPT-2 Small pre-trained model
   - Fine-tune on grammar explanation dataset
   - Use learning rate scheduling
   - Early stopping based on validation loss

4. **Model Export** (`export_model.py`)
   - Convert to ONNX format
   - Optimize for mobile inference
   - Generate vocabulary files

5. **Integration** (Flutter)
   - Update `AIService` to use ONNX model
   - Add fallback to rule-based if model unavailable
   - Implement tokenization and inference

## Benefits

✅ **Natural Explanations**: More varied, contextual explanations
✅ **Better Understanding**: Model learns grammar patterns
✅ **Scalable**: Can improve with more training data
✅ **Offline**: Fully on-device, no API needed
✅ **Maintainable**: Can retrain with updated question bank

## Requirements

### Python Dependencies
- `transformers` (Hugging Face)
- `torch` (PyTorch)
- `onnxruntime` / `onnx`
- `datasets`
- `numpy`
- `json`

### Hardware
- Training: GPU recommended (can use CPU but slower)
- Inference: CPU (mobile-friendly)

### Data
- Question bank JSON files (already have)
- ~200+ questions = ~600-800 training examples (with variations)

## Implementation Steps

1. ✅ Create training data preparation script
2. ✅ Create model training script
3. ✅ Create model export script
4. ✅ Test model inference
5. ⏳ Integrate with Flutter app
6. ⏳ Test end-to-end

## Expected Outcomes

- **Model Size**: ~45-50MB
- **Inference Time**: <500ms per explanation (on mobile)
- **Quality**: Better than templates, more natural language
- **Fallback**: Rule-based system still available

## Next Steps

1. Review and approve this proposal
2. Set up Python environment
3. Run training data preparation
4. Train model (may take 1-2 hours on GPU, 4-6 hours on CPU)
5. Export and test model
6. Integrate with Flutter app

---

**Status**: Ready to implement
**Estimated Time**: 1-2 days for full implementation
**Risk Level**: Low (fallback system exists)

