#!/usr/bin/env python3
"""
Quick test script to verify training pipeline setup
Tests data loading and basic functionality
"""

import json
from pathlib import Path
from prepare_training_data import TrainingDataGenerator

def test_data_preparation():
    """Test that training data can be prepared"""
    print("=" * 60)
    print("Testing Training Data Preparation")
    print("=" * 60)
    
    generator = TrainingDataGenerator()
    
    # Test loading
    total = generator.load_question_banks()
    if total == 0:
        print("[ERROR] No questions loaded. Check question bank files.")
        return False
    
    print(f"[OK] Loaded {total} questions")
    
    # Test example generation
    if generator.questions:
        test_question = generator.questions[0]
        examples = generator.create_training_examples(test_question)
        print(f"[OK] Generated {len(examples)} examples from test question")
        
        if examples:
            print(f"\n[INFO] Sample training example:")
            print(f"  Context: {examples[0]['context'][:100]}...")
            print(f"  Explanation: {examples[0]['explanation'][:100]}...")
    
    print("\n[SUCCESS] Data preparation test passed!")
    return True

def check_dependencies():
    """Check if required Python packages are available"""
    print("\n" + "=" * 60)
    print("Checking Dependencies")
    print("=" * 60)
    
    required = {
        'torch': 'PyTorch',
        'transformers': 'Transformers (Hugging Face)',
        'datasets': 'Datasets',
        'numpy': 'NumPy',
    }
    
    optional = {
        'onnx': 'ONNX (for export)',
        'onnxruntime': 'ONNX Runtime (for export)',
    }
    
    missing_required = []
    missing_optional = []
    
    for module, name in required.items():
        try:
            __import__(module)
            print(f"[OK] {name} installed")
        except ImportError:
            print(f"[MISSING] {name} not installed")
            missing_required.append(module)
    
    for module, name in optional.items():
        try:
            __import__(module)
            print(f"[OK] {name} installed")
        except ImportError:
            print(f"[OPTIONAL] {name} not installed (needed for export)")
            missing_optional.append(module)
    
    if missing_required:
        print(f"\n[ERROR] Missing required packages: {', '.join(missing_required)}")
        print("Install with: pip install -r requirements_training.txt")
        return False
    
    if missing_optional:
        print(f"\n[WARN] Missing optional packages: {', '.join(missing_optional)}")
        print("Install for ONNX export: pip install onnx onnxruntime")
    
    print("\n[SUCCESS] Dependency check passed!")
    return True

def check_question_banks():
    """Check if question bank files exist"""
    print("\n" + "=" * 60)
    print("Checking Question Bank Files")
    print("=" * 60)
    
    assets_dir = Path("assets/data")
    bank_files = [
        'question_bank.json',
        'question_bank1.json',
        'question_bank2.json',
        'question_bank3.json',
    ]
    
    found = []
    missing = []
    
    for bank_file in bank_files:
        file_path = assets_dir / bank_file
        if file_path.exists():
            # Check if it's valid JSON
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        print(f"[OK] {bank_file} ({len(data)} questions)")
                        found.append(bank_file)
                    else:
                        print(f"[WARN] {bank_file} exists but not a list")
            except Exception as e:
                print(f"[ERROR] {bank_file} exists but invalid: {e}")
        else:
            print(f"[MISSING] {bank_file}")
            missing.append(bank_file)
    
    if not found:
        print("\n[ERROR] No question bank files found!")
        return False
    
    if missing:
        print(f"\n[WARN] Some files missing: {', '.join(missing)}")
        print("This is OK if you only have some files")
    
    print(f"\n[SUCCESS] Found {len(found)} question bank file(s)")
    return True

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Training Pipeline Test Suite")
    print("=" * 60)
    
    all_passed = True
    
    # Run tests
    all_passed &= check_question_banks()
    all_passed &= check_dependencies()
    all_passed &= test_data_preparation()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] All tests passed! Ready to train.")
        print("\nNext steps:")
        print("1. Run: python prepare_training_data.py")
        print("2. Run: python train_dialogpt_model.py")
        print("3. Run: python export_model_to_onnx.py")
    else:
        print("[FAILED] Some tests failed. Please fix issues above.")
    print("=" * 60)

