# AI Model Integration Guide

## ✅ Model Training Complete!

Your DialogGPT model is trained and ready. Now let's integrate it with your Flutter app.

## Integration Options

### Option 1: Python API Server (Recommended - Easiest)

**Pros:**
- ✅ Works immediately
- ✅ No ONNX conversion needed
- ✅ Easy to test and debug
- ✅ Can update model without rebuilding app

**Cons:**
- ⚠️ Requires Python server running
- ⚠️ Needs network connection (can run locally)

### Option 2: ONNX Export (For Full Offline)

**Pros:**
- ✅ Fully offline
- ✅ No server needed
- ✅ Better performance

**Cons:**
- ⚠️ ONNX installation had Windows path issues
- ⚠️ More complex integration
- ⚠️ Larger app size

## Quick Start: Python API Server

### Step 1: Install Flask

```bash
pip install flask flask-cors
```

### Step 2: Start the Server

```bash
python ai_explanation_server.py
```

You should see:
```
[INFO] Loading model...
[OK] Model loaded successfully
[INFO] Server running on http://localhost:5000
```

### Step 3: Test the Server

Open browser or use curl:
```bash
curl http://localhost:5000/test
```

Or visit: `http://localhost:5000/test`

### Step 4: Update Flutter App

1. **Add HTTP dependency** to `pubspec.yaml`:
```yaml
dependencies:
  http: ^1.1.0
```

2. **Update AIService.dart**:

Replace the `generateExplanation` method in `AIService` with:

```dart
static Future<Map<String, dynamic>> generateExplanation({
  required Question question,
  required String? userAnswer,
  required bool? isCorrect,
  required List<String> userInterests,
  Map<String, dynamic>? context,
}) async {
  // Try AI server first
  try {
    final aiResponse = await AIExplanationService.generateExplanation(
      question: question,
      userAnswer: userAnswer,
      isCorrect: isCorrect,
      userInterests: userInterests,
      context: context,
    );
    
    // If AI server is available and working
    if (aiResponse['type'] == 'ai_generated') {
      return aiResponse;
    }
  } catch (e) {
    // Fallback to rule-based if AI fails
    print('AI server unavailable, using fallback: $e');
  }
  
  // Fallback to rule-based
  return _generateRuleBasedExplanation(
    question: question,
    userAnswer: userAnswer,
    isCorrect: isCorrect,
  );
}
```

3. **Add the AIExplanationService** (copy from `flutter_ai_service_integration.dart`)

### Step 5: Update Server URL

In `flutter_ai_service_integration.dart`, update the server URL:

**For Android Emulator:**
```dart
static const String serverUrl = 'http://10.0.2.2:5000';
```

**For iOS Simulator:**
```dart
static const String serverUrl = 'http://localhost:5000';
```

**For Physical Device:**
```dart
// Use your computer's IP address
static const String serverUrl = 'http://192.168.1.XXX:5000';
```

Find your IP:
- Windows: `ipconfig` (look for IPv4 Address)
- Mac/Linux: `ifconfig` or `ip addr`

## Testing

### Test Server Locally

```bash
# Start server
python ai_explanation_server.py

# In another terminal, test
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Choose the correct form: \"I _____ to school every day.\"",
    "type": "multiple_choice",
    "grammar_point": "simple_present",
    "user_answer": "went",
    "correct_answer": "go",
    "is_correct": false
  }'
```

### Test in Flutter

1. Start the Python server
2. Run your Flutter app
3. Answer a question
4. Check if explanation is AI-generated (should be more natural than templates)

## Production Deployment

### Option A: Keep Server Local (Development)
- Run server on your machine
- Use for testing only

### Option B: Deploy Server (Production)
- Deploy to cloud (Heroku, AWS, etc.)
- Update Flutter app with server URL
- Add authentication if needed

### Option C: Convert to ONNX (Future)
- Fix ONNX installation issues
- Export model to ONNX
- Integrate directly in Flutter app
- Fully offline solution

## Troubleshooting

### Server won't start
- Check if model files exist in `models/dialogpt_grammar/`
- Check Python dependencies: `pip install flask flask-cors transformers torch`

### Flutter can't connect
- Check server is running: `curl http://localhost:5000/health`
- Check firewall settings
- Verify IP address is correct
- For Android emulator, use `10.0.2.2:5000`

### Model not loading
- Verify model files exist
- Check model path in `ai_explanation_server.py`
- Check disk space

### Slow responses
- First request is slower (model loading)
- Subsequent requests should be faster
- Consider caching common explanations

## Next Steps

1. ✅ Start the server: `python ai_explanation_server.py`
2. ✅ Test the server: Visit `http://localhost:5000/test`
3. ✅ Update Flutter app with integration code
4. ✅ Test in Flutter app
5. ⏳ Deploy for production (if needed)

---

**Status**: Ready to integrate
**Server Script**: `ai_explanation_server.py`
**Flutter Integration**: `flutter_ai_service_integration.dart`

