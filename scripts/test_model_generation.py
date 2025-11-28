#!/usr/bin/env python3
"""
Test the trained DialogGPT model with sample questions
"""

from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

def test_model():
    """Test the trained model with sample questions"""
    
    print("=" * 60)
    print("Testing Trained DialogGPT Model")
    print("=" * 60)
    
    # Load model
    print("\n[INFO] Loading model...")
    model_path = "models/dialogpt_grammar"
    model = GPT2LMHeadModel.from_pretrained(model_path)
    tokenizer = GPT2Tokenizer.from_pretrained(model_path)
    model.eval()
    print("[OK] Model loaded")
    
    # Test cases
    test_cases = [
        {
            "name": "Simple Present - Wrong Answer",
            "context": "Question: Choose the correct form: 'I _____ to school every day.' | Type: multiple_choice | Grammar Point: simple_present | User Answer: went | Correct Answer: go | Is Correct: False"
        },
        {
            "name": "Past Continuous - Correct Answer",
            "context": "Question: Fill in the blank: 'She _____ reading a book when I called.' | Type: gap_fill | Grammar Point: past_continuous | User Answer: was | Correct Answer: was | Is Correct: True"
        },
        {
            "name": "Present Perfect - Wrong Answer",
            "context": "Question: Choose the correct form: 'I _____ here for five years.' | Type: multiple_choice | Grammar Point: present_perfect | User Answer: live | Correct Answer: have lived | Is Correct: False"
        },
    ]
    
    print("\n" + "=" * 60)
    print("Generating Explanations")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[TEST {i}] {test_case['name']}")
        print(f"Context: {test_case['context'][:80]}...")
        
        # Format input
        input_text = f"<|user|>{test_case['context']}<|assistant|>"
        input_ids = tokenizer.encode(input_text, return_tensors='pt')
        
        # Generate
        with torch.no_grad():
            output = model.generate(
                input_ids,
                max_length=200,
                num_return_sequences=1,
                temperature=0.7,
                top_p=0.9,
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
            response = generated_text
        
        print(f"Generated Explanation:")
        print(f"  {response}")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Model testing complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_model()

