# Running AI Model - Quick Start Guide

**Date**: 2024-11-28

---

## Option 1: Run Python Server (Live Model)

### Step 1: Install Dependencies

```bash
pip install flask flask-cors transformers torch
```

Or use the requirements file:
```bash
pip install -r requirements_training.txt
```

### Step 2: Start the Server

```bash
# Method 1: Direct run
python scripts/ai_explanation_server.py

# Method 2: Using helper script
python scripts/run_ai_server.py
```

### Step 3: Test the Server

Open a new terminal and test:

```bash
# Health check
curl http://localhost:5000/health

# Test endpoint
curl http://localhost:5000/test
```

### Step 4: Use from Flutter

The Flutter app can now call the server using `AIExplanationService` from `flutter_ai_service_integration.dart`.

---

## Option 2: Pre-Generate All Explanations

### Step 1: Run Generation Script

```bash
python scripts/generate_all_explanations.py
```

This will:
- Load the trained model
- Generate explanations for all questions
- Save to `assets/data/ai_explanations.json`

### Step 2: Verify Output

Check that the file was created:
```bash
# Check file exists
ls -lh assets/data/ai_explanations.json

# Check file size (should be a few MB)
```

### Step 3: Use in Flutter

The Flutter app will automatically use the pre-generated explanations from `AIService`.

---

## Troubleshooting

### Server Won't Start

**Error**: `ModuleNotFoundError: No module named 'flask'`
**Solution**: Install Flask
```bash
pip install flask flask-cors
```

**Error**: `Model not found`
**Solution**: Check model exists at `models/dialogpt_grammar/`

**Error**: `Port 5000 already in use`
**Solution**: Change port in `ai_explanation_server.py` or kill process using port 5000

### Generation Script Fails

**Error**: `No questions found`
**Solution**: Check question bank files exist in `assets/data/`

**Error**: `Out of memory`
**Solution**: Process questions in batches or use GPU

---

## Performance Notes

- **Server**: First request takes ~2-3 seconds (model loading), subsequent requests ~500ms
- **Pre-generation**: Takes 10-30 minutes depending on number of questions
- **File size**: ~2-5 MB for 200 questions

---

## Next Steps

After running either option:

1. **Test the Flutter app** - Explanations should now use AI
2. **Compare quality** - AI vs rule-based explanations
3. **Monitor performance** - Check generation times

