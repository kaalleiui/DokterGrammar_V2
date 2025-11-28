#!/usr/bin/env python3
"""
Pre-generate all explanations for all questions
This creates a JSON file that can be bundled with the Flutter app
No server or model needed at runtime!
"""

import json
from pathlib import Path
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

def load_questions():
    """Load all questions from question bank"""
    assets_dir = Path("assets/data")
    bank_files = [
        'question_bank.json',
        'question_bank1.json',
        'question_bank2.json',
        'question_bank3.json',
    ]
    
    all_questions = []
    for bank_file in bank_files:
        file_path = assets_dir / bank_file
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_questions.extend(data)
            except Exception as e:
                print(f"[WARN] Error loading {bank_file}: {e}")
    
    return all_questions

def get_correct_answer_text(question):
    """Get correct answer text"""
    answer = question.get('answer', '')
    choices = question.get('choices', [])
    
    for choice in choices:
        if choice.get('isCorrect', False):
            return choice.get('text', answer)
    
    for choice in choices:
        if choice.get('choiceId', '').lower() == answer.lower():
            return choice.get('text', answer)
    
    return answer

def format_context(question, user_answer, is_correct):
    """Format context for model"""
    prompt = question.get('prompt', '')
    question_type = question.get('type', 'multiple_choice')
    grammar_point = None
    
    for tag in question.get('tags', []):
        if tag.get('tagType') == 'grammar_point':
            grammar_point = tag.get('tagValue')
            break
    
    correct_answer = get_correct_answer_text(question)
    
    parts = [
        f"Question: {prompt}",
        f"Type: {question_type}",
    ]
    
    if grammar_point:
        parts.append(f"Grammar Point: {grammar_point}")
    
    parts.append(f"User Answer: {user_answer}")
    parts.append(f"Correct Answer: {correct_answer}")
    parts.append(f"Is Correct: {is_correct}")
    
    return " | ".join(parts)

def generate_explanation(model, tokenizer, context):
    """Generate explanation using model"""
    input_text = f"<|user|>{context}<|assistant|>"
    input_ids = tokenizer.encode(input_text, return_tensors='pt')
    
    with torch.no_grad():
        output = model.generate(
            input_ids,
            max_length=150,
            num_return_sequences=1,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.encode('<|endoftext|>')[0] if '<|endoftext|>' in tokenizer.get_vocab() else tokenizer.eos_token_id,
        )
    
    generated_text = tokenizer.decode(output[0], skip_special_tokens=False)
    
    if '<|assistant|>' in generated_text:
        response = generated_text.split('<|assistant|>')[1]
        response = response.split('<|endoftext|>')[0].strip()
        return response
    
    return generated_text.strip()

def main():
    print("=" * 60)
    print("Pre-generating All Explanations")
    print("=" * 60)
    
    # Load model
    print("\n[INFO] Loading model...")
    model_path = Path("models/dialogpt_grammar")
    if not model_path.exists():
        print(f"[ERROR] Model not found at {model_path}")
        return
    
    model = GPT2LMHeadModel.from_pretrained(str(model_path))
    tokenizer = GPT2Tokenizer.from_pretrained(str(model_path))
    model.eval()
    print("[OK] Model loaded")
    
    # Load questions
    print("\n[INFO] Loading questions...")
    questions = load_questions()
    print(f"[OK] Loaded {len(questions)} questions")
    
    # Generate explanations
    print("\n[INFO] Generating explanations...")
    explanations = {}
    
    for i, question in enumerate(questions, 1):
        question_id = question.get('id', f'q_{i}')
        
        if (i) % 20 == 0:
            print(f"  Progress: {i}/{len(questions)}")
        
        # Generate for correct answer
        correct_answer = get_correct_answer_text(question)
        context_correct = format_context(question, correct_answer, True)
        explanation_correct = generate_explanation(model, tokenizer, context_correct)
        
        # Generate for each wrong answer (if multiple choice)
        explanations_for_question = {
            'correct': explanation_correct,
            'incorrect': {}
        }
        
        if question.get('type') in ['multiple_choice', 'gap_fill']:
            choices = question.get('choices', [])
            for choice in choices:
                choice_id = choice.get('choiceId', '')
                if not choice.get('isCorrect', False):
                    context_wrong = format_context(question, choice_id, False)
                    explanation_wrong = generate_explanation(model, tokenizer, context_wrong)
                    explanations_for_question['incorrect'][choice_id] = explanation_wrong
        
        explanations[question_id] = explanations_for_question
    
    # Save to JSON
    output_path = Path("assets/data/ai_explanations.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(explanations, f, ensure_ascii=False, indent=2)
    
    print(f"\n[OK] Saved {len(explanations)} question explanations to {output_path}")
    
    # Calculate size
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"[INFO] File size: {size_mb:.2f} MB")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Pre-generation complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Add ai_explanations.json to Flutter assets")
    print("2. Update AIService to load from JSON")
    print("3. No model or server needed at runtime!")
    print("=" * 60)

if __name__ == "__main__":
    main()

