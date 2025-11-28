#!/usr/bin/env python3
"""
AI Explanation Server for Flutter Integration
Provides HTTP API to generate explanations using trained DialogGPT model
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import json
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for Flutter app

# Global model variables
model = None
tokenizer = None
model_loaded = False

def load_model():
    """Load the trained model"""
    global model, tokenizer, model_loaded
    
    if model_loaded:
        return True
    
    try:
        print("[INFO] Loading model...")
        model_path = "models/dialogpt_grammar"
        model = GPT2LMHeadModel.from_pretrained(model_path)
        tokenizer = GPT2Tokenizer.from_pretrained(model_path)
        model.eval()
        model_loaded = True
        print("[OK] Model loaded successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        return False

def format_context(question_data):
    """Format question data into context string"""
    parts = [
        f"Question: {question_data.get('prompt', '')}",
        f"Type: {question_data.get('type', 'multiple_choice')}",
    ]
    
    if question_data.get('grammar_point'):
        parts.append(f"Grammar Point: {question_data['grammar_point']}")
    
    if question_data.get('difficulty'):
        parts.append(f"Difficulty: {question_data['difficulty']}")
    
    parts.append(f"User Answer: {question_data.get('user_answer', '')}")
    parts.append(f"Correct Answer: {question_data.get('correct_answer', '')}")
    parts.append(f"Is Correct: {question_data.get('is_correct', False)}")
    
    return " | ".join(parts)

def generate_explanation(context, max_length=150, temperature=0.7, top_p=0.9):
    """Generate explanation using the model"""
    global model, tokenizer
    
    if not model_loaded:
        return None
    
    try:
        # Format input
        input_text = f"<|user|>{context}<|assistant|>"
        input_ids = tokenizer.encode(input_text, return_tensors='pt')
        
        # Generate
        with torch.no_grad():
            output = model.generate(
                input_ids,
                max_length=max_length,
                num_return_sequences=1,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.encode('<|endoftext|>')[0] if '<|endoftext|>' in tokenizer.get_vocab() else tokenizer.eos_token_id,
            )
        
        # Decode
        generated_text = tokenizer.decode(output[0], skip_special_tokens=False)
        
        # Extract assistant response
        if '<|assistant|>' in generated_text:
            response = generated_text.split('<|assistant|>')[1]
            response = response.split('<|endoftext|>')[0].strip()
        else:
            response = generated_text.strip()
        
        return response
    except Exception as e:
        print(f"[ERROR] Generation failed: {e}")
        return None

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'model_loaded': model_loaded,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/generate', methods=['POST'])
def generate():
    """Generate explanation endpoint"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['prompt', 'user_answer', 'correct_answer', 'is_correct']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}',
                    'success': False
                }), 400
        
        # Format context
        context = format_context(data)
        
        # Generate explanation
        start_time = datetime.now()
        explanation = generate_explanation(
            context,
            max_length=data.get('max_length', 150),
            temperature=data.get('temperature', 0.7),
            top_p=data.get('top_p', 0.9)
        )
        generation_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if explanation is None:
            return jsonify({
                'error': 'Failed to generate explanation',
                'success': False
            }), 500
        
        # Return response matching AIService format
        return jsonify({
            'text': explanation,
            'type': 'ai_generated',
            'confidence': 0.85,  # Can be calculated based on model output
            'rule_applied': data.get('grammar_point'),
            'example': data.get('example_sentence'),
            'follow_up_available': False,
            'related_topics': [data.get('grammar_point')] if data.get('grammar_point') else [],
            'generation_time_ms': int(generation_time),
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint with sample data"""
    test_data = {
        'prompt': "Choose the correct form: 'I _____ to school every day.'",
        'type': 'multiple_choice',
        'grammar_point': 'simple_present',
        'user_answer': 'went',
        'correct_answer': 'go',
        'is_correct': False,
        'difficulty': 1
    }
    
    context = format_context(test_data)
    explanation = generate_explanation(context)
    
    return jsonify({
        'test': True,
        'context': context,
        'explanation': explanation,
        'model_loaded': model_loaded
    })

if __name__ == '__main__':
    # Load model on startup
    if load_model():
        print("\n" + "=" * 60)
        print("AI Explanation Server")
        print("=" * 60)
        print("\n[INFO] Server starting...")
        print("[INFO] Endpoints:")
        print("  GET  /health - Health check")
        print("  POST /generate - Generate explanation")
        print("  GET  /test - Test with sample data")
        print("\n[INFO] Server running on http://localhost:5000")
        print("=" * 60 + "\n")
        
        # Run server
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("[ERROR] Failed to load model. Server cannot start.")

