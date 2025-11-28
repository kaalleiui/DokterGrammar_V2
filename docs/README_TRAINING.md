# DialogGPT Training Guide

This guide explains how to train a DialogGPT-style model for the Dokter Grammar AI engine using your question bank.

## Overview

The training pipeline consists of 3 main steps:
1. **Prepare Training Data** - Convert question bank to conversation format
2. **Train Model** - Fine-tune GPT-2 Small on grammar explanations
3. **Export Model** - Convert to ONNX format for Flutter integration

## Prerequisites

### 1. Install Python Dependencies

```bash
pip install -r requirements_training.txt
```

### 2. Verify Question Bank

Make sure your question bank files are in `assets/data/`:
- `question_bank.json`
- `question_bank1.json`
- `question_bank2.json`
- `question_bank3.json`

## Step 1: Prepare Training Data

This script converts your question bank into training examples:

```bash
python prepare_training_data.py
```

**What it does:**
- Loads all question bank JSON files
- Creates training examples for each question (correct + incorrect scenarios)
- Formats data in DialogGPT conversation style
- Splits into train/validation sets (80/20)
- Saves to `training_data/` directory

**Output:**
- `training_data/train.json` - Training examples
- `training_data/val.json` - Validation examples
- `training_data/stats.json` - Dataset statistics

**Expected output:**
```
[OK] Loaded 200+ questions
[OK] Generated 600-800 training examples
[OK] Split: 480 train, 120 validation
```

## Step 2: Train Model

Train the DialogGPT model on your data:

```bash
python train_dialogpt_model.py
```

**Options:**
```bash
python train_dialogpt_model.py \
    --epochs 3 \
    --batch-size 4 \
    --learning-rate 5e-5 \
    --data-dir training_data \
    --output-dir models/dialogpt_grammar
```

**What it does:**
- Loads GPT-2 Small pre-trained model
- Fine-tunes on your grammar explanation dataset
- Saves checkpoints during training
- Tests generation at the end

**Training time:**
- GPU: ~1-2 hours (3 epochs)
- CPU: ~4-6 hours (3 epochs)

**Output:**
- `models/dialogpt_grammar/` - Trained model files
- Model checkpoints saved during training

## Step 3: Export to ONNX

Export the trained model to ONNX format for Flutter:

```bash
python export_model_to_onnx.py
```

**Options:**
```bash
python export_model_to_onnx.py \
    --model-dir models/dialogpt_grammar \
    --output-dir assets/models \
    --no-quantization  # Skip quantization (larger file)
```

**What it does:**
- Converts PyTorch model to ONNX format
- Quantizes model to reduce size (optional)
- Saves tokenizer configuration
- Creates model info file

**Output:**
- `assets/models/grammar_explainer_quantized.onnx` - ONNX model (~45-50MB)
- `assets/models/vocab.json` - Vocabulary
- `assets/models/tokenizer_config.json` - Tokenizer config
- `assets/models/model_info.json` - Model metadata

## Model Integration with Flutter

After exporting, integrate the model into your Flutter app:

### 1. Copy Model Files

Copy from `assets/models/` to your Flutter `assets/models/` directory.

### 2. Update AIService

The `AIService` in `lib/core/services/ai_service.dart` already has the framework. You'll need to:

1. Add ONNX runtime dependency to `pubspec.yaml`:
```yaml
dependencies:
  onnxruntime: ^1.15.0
```

2. Update `AIService.initialize()` to load ONNX model
3. Update `AIService.generateExplanation()` to use model inference

### 3. Test Inference

Test the model generates explanations correctly before deploying.

## Troubleshooting

### Out of Memory During Training

Reduce batch size:
```bash
python train_dialogpt_model.py --batch-size 2
```

### Model Too Large

Use quantization when exporting:
```bash
python export_model_to_onnx.py  # Quantization enabled by default
```

### Poor Quality Explanations

- Increase training epochs: `--epochs 5`
- Adjust learning rate: `--learning-rate 3e-5`
- Add more training data (more questions)

### ONNX Export Fails

Make sure ONNX is installed:
```bash
pip install onnx onnxruntime
```

## Expected Results

After training, you should have:
- ✅ Model size: ~45-50MB (quantized)
- ✅ Inference time: <500ms per explanation
- ✅ Better explanations than templates
- ✅ Natural, varied language

## Next Steps

1. Review generated explanations
2. Test model in Flutter app
3. Compare with rule-based system
4. Iterate and improve if needed

## Support

If you encounter issues:
1. Check that all dependencies are installed
2. Verify question bank format is correct
3. Ensure sufficient disk space (models can be large)
4. Check GPU availability if using GPU training

---

**Status**: Ready to use
**Last Updated**: 2024-11-27

