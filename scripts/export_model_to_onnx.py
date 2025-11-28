#!/usr/bin/env python3
"""
Export trained DialogGPT model to ONNX format for Flutter integration
"""

import json
import os
from pathlib import Path
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import argparse

try:
    import onnx
    from onnxruntime.quantization import quantize_dynamic, QuantType
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    print("[WARN] ONNX not available. Install: pip install onnx onnxruntime")

class ModelExporter:
    def __init__(self, 
                 model_dir: str = "models/dialogpt_grammar",
                 output_dir: str = "assets/models"):
        self.model_dir = Path(model_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def export_to_onnx(self, use_dynamic_quantization: bool = True):
        """Export PyTorch model to ONNX format"""
        if not ONNX_AVAILABLE:
            print("[ERROR] ONNX not available. Cannot export.")
            return False
        
        print("=" * 60)
        print("Exporting Model to ONNX")
        print("=" * 60)
        
        # Load model and tokenizer
        print(f"[INFO] Loading model from {self.model_dir}")
        model = GPT2LMHeadModel.from_pretrained(str(self.model_dir))
        tokenizer = GPT2Tokenizer.from_pretrained(str(self.model_dir))
        
        model.eval()
        
        # Create dummy input
        dummy_input = "This is a test input for ONNX export"
        input_ids = tokenizer.encode(dummy_input, return_tensors='pt')
        
        # Export to ONNX
        onnx_path = self.output_dir / "grammar_explainer.onnx"
        print(f"[INFO] Exporting to {onnx_path}...")
        
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
            opset_version=11,  # ONNX opset version
            do_constant_folding=True,
        )
        
        print(f"[OK] Model exported to {onnx_path}")
        
        # Quantize model (reduce size)
        if use_dynamic_quantization:
            print("[INFO] Quantizing model...")
            quantized_path = self.output_dir / "grammar_explainer_quantized.onnx"
            quantize_dynamic(
                str(onnx_path),
                str(quantized_path),
                weight_type=QuantType.QUInt8
            )
            print(f"[OK] Quantized model saved to {quantized_path}")
            
            # Show size comparison
            original_size = onnx_path.stat().st_size / (1024 * 1024)
            quantized_size = quantized_path.stat().st_size / (1024 * 1024)
            print(f"\n[INFO] Model sizes:")
            print(f"  Original: {original_size:.2f} MB")
            print(f"  Quantized: {quantized_size:.2f} MB")
            print(f"  Reduction: {(1 - quantized_size/original_size)*100:.1f}%")
        
        # Save tokenizer and config
        self.save_tokenizer_config(tokenizer)
        
        return True
    
    def save_tokenizer_config(self, tokenizer):
        """Save tokenizer configuration for Flutter"""
        # Save vocabulary
        vocab_path = self.output_dir / "vocab.json"
        tokenizer.save_vocabulary(str(self.output_dir))
        print(f"[OK] Vocabulary saved")
        
        # Save tokenizer config
        config = {
            'vocab_size': len(tokenizer),
            'model_max_length': tokenizer.model_max_length,
            'pad_token': tokenizer.pad_token,
            'eos_token': tokenizer.eos_token,
            'bos_token': tokenizer.bos_token,
            'unk_token': tokenizer.unk_token,
            'special_tokens': {
                'user_token': '<|user|>',
                'assistant_token': '<|assistant|>',
                'endoftext_token': '<|endoftext|>',
            }
        }
        
        config_path = self.output_dir / "tokenizer_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        print(f"[OK] Tokenizer config saved to {config_path}")
    
    def create_model_info(self):
        """Create model information file"""
        info = {
            'model_name': 'grammar_explainer_v1',
            'model_type': 'dialogpt_gpt2_small',
            'model_format': 'onnx',
            'model_path': 'assets/models/grammar_explainer_quantized.onnx',
            'vocab_path': 'assets/models/vocab.json',
            'tokenizer_config_path': 'assets/models/tokenizer_config.json',
            'max_tokens': 150,
            'temperature': 0.7,
            'top_p': 0.9,
            'fallback_to_template': True,
            'description': 'DialogGPT-style model fine-tuned on grammar explanation dataset',
            'version': '1.0.0',
        }
        
        info_path = self.output_dir / "model_info.json"
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2)
        print(f"[OK] Model info saved to {info_path}")
    
    def run(self, use_quantization: bool = True):
        """Main execution"""
        success = self.export_to_onnx(use_dynamic_quantization=use_quantization)
        
        if success:
            self.create_model_info()
            
            print("\n" + "=" * 60)
            print("[SUCCESS] Model export complete!")
            print("=" * 60)
            print(f"\nModel files saved to: {self.output_dir}")
            print("\nNext steps:")
            print("1. Copy model files to Flutter assets/models/")
            print("2. Update AIService.dart to use ONNX model")
            print("3. Test inference in Flutter app")
            print("=" * 60)
        else:
            print("\n[ERROR] Model export failed")
        
        return success

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export DialogGPT model to ONNX")
    parser.add_argument("--model-dir", type=str, default="models/dialogpt_grammar", 
                       help="Directory containing trained model")
    parser.add_argument("--output-dir", type=str, default="assets/models",
                       help="Output directory for ONNX model")
    parser.add_argument("--no-quantization", action="store_true",
                       help="Skip model quantization")
    
    args = parser.parse_args()
    
    exporter = ModelExporter(
        model_dir=args.model_dir,
        output_dir=args.output_dir
    )
    exporter.run(use_quantization=not args.no_quantization)

