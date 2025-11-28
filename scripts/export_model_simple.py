#!/usr/bin/env python3
"""
Simplified ONNX export with workaround for Windows path issues
"""

import json
import os
import shutil
from pathlib import Path
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import tempfile

def export_to_onnx_simple():
    """Export model with workaround for Windows path issues"""
    
    print("=" * 60)
    print("Simple ONNX Export (Windows Path Fix)")
    print("=" * 60)
    
    # Use temp directory with short path
    temp_dir = Path(tempfile.gettempdir()) / "grammar_model"
    temp_dir.mkdir(exist_ok=True)
    
    print(f"[INFO] Using temp directory: {temp_dir}")
    
    # Copy model to temp (if needed)
    model_source = Path("models/dialogpt_grammar")
    if not model_source.exists():
        print(f"[ERROR] Model not found at {model_source}")
        return False
    
    # Load model
    print(f"[INFO] Loading model from {model_source}...")
    try:
        model = GPT2LMHeadModel.from_pretrained(str(model_source))
        tokenizer = GPT2Tokenizer.from_pretrained(str(model_source))
        model.eval()
        print("[OK] Model loaded")
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        return False
    
    # Try ONNX export
    try:
        import onnx
        from onnxruntime.quantization import quantize_dynamic, QuantType
        print("[OK] ONNX libraries available")
    except ImportError:
        print("[ERROR] ONNX not installed")
        print("  Try: pip install onnx onnxruntime")
        print("  Or use shorter path workaround")
        return False
    
    # Create dummy input
    dummy_input = "Test input"
    input_ids = tokenizer.encode(dummy_input, return_tensors='pt')
    
    # Export to temp directory first (shorter path)
    onnx_path = temp_dir / "model.onnx"
    print(f"[INFO] Exporting to {onnx_path}...")
    
    try:
        torch.onnx.export(
            model,
            input_ids,
            str(onnx_path),
            input_names=['input_ids'],
            output_names=['logits'],
            dynamic_axes={
                'input_ids': {0: 'batch_size', 1: 'sequence_length'},
                'logits': {0: 'batch_size', 1: 'sequence_length'}
            },
            opset_version=11,
            do_constant_folding=True,
        )
        print(f"[OK] Model exported to {onnx_path}")
    except Exception as e:
        print(f"[ERROR] Export failed: {e}")
        return False
    
    # Quantize
    print("[INFO] Quantizing model...")
    quantized_path = temp_dir / "model_quantized.onnx"
    try:
        quantize_dynamic(
            str(onnx_path),
            str(quantized_path),
            weight_type=QuantType.QUInt8
        )
        print(f"[OK] Quantized model saved")
    except Exception as e:
        print(f"[WARN] Quantization failed: {e}")
        quantized_path = onnx_path
    
    # Copy to final location
    output_dir = Path("assets/models")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    final_path = output_dir / "grammar_explainer.onnx"
    print(f"[INFO] Copying to {final_path}...")
    
    try:
        shutil.copy2(quantized_path, final_path)
        print(f"[OK] Model copied to {final_path}")
        
        # Show size
        size_mb = final_path.stat().st_size / (1024 * 1024)
        print(f"[INFO] Model size: {size_mb:.2f} MB")
    except Exception as e:
        print(f"[ERROR] Failed to copy: {e}")
        return False
    
    # Save tokenizer files
    print("[INFO] Saving tokenizer files...")
    tokenizer.save_vocabulary(str(output_dir))
    
    # Save config
    config = {
        'vocab_size': len(tokenizer),
        'model_max_length': tokenizer.model_max_length,
        'special_tokens': {
            'user_token': '<|user|>',
            'assistant_token': '<|assistant|>',
            'endoftext_token': '<|endoftext|>',
        }
    }
    
    config_path = output_dir / "tokenizer_config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print(f"[OK] Config saved to {config_path}")
    
    # Cleanup temp
    try:
        shutil.rmtree(temp_dir)
        print(f"[OK] Cleaned up temp directory")
    except:
        pass
    
    print("\n" + "=" * 60)
    print("[SUCCESS] ONNX export complete!")
    print("=" * 60)
    print(f"\nModel saved to: {final_path}")
    print(f"Size: {size_mb:.2f} MB")
    print("\nNext steps:")
    print("1. Add model to Flutter assets")
    print("2. Use ONNX runtime in Flutter")
    print("3. Update AIService to use ONNX model")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    export_to_onnx_simple()

