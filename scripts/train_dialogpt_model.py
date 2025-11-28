#!/usr/bin/env python3
"""
Train DialogGPT-style model for grammar explanations
Fine-tunes GPT-2 Small on grammar explanation dataset
"""

import json
import os
from pathlib import Path
from typing import List, Dict
import torch
from transformers import (
    GPT2LMHeadModel,
    GPT2Tokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
import argparse

class DialogGPTTrainer:
    def __init__(self, 
                 data_dir: str = "training_data",
                 output_dir: str = "models/dialogpt_grammar",
                 model_name: str = "gpt2"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        
    def load_training_data(self) -> tuple:
        """Load training and validation data"""
        train_file = self.data_dir / "train.json"
        val_file = self.data_dir / "val.json"
        
        if not train_file.exists():
            raise FileNotFoundError(f"Training data not found: {train_file}")
        
        with open(train_file, 'r', encoding='utf-8') as f:
            train_data = json.load(f)
        
        val_data = []
        if val_file.exists():
            with open(val_file, 'r', encoding='utf-8') as f:
                val_data = json.load(f)
        
        print(f"[OK] Loaded {len(train_data)} training examples")
        print(f"[OK] Loaded {len(val_data)} validation examples")
        
        return train_data, val_data
    
    def format_conversation(self, example: Dict) -> str:
        """Format conversation for GPT-2 training"""
        # DialogGPT format: <|user|> ... <|assistant|> ...
        user_msg = example['user']
        assistant_msg = example['assistant']
        
        # Use special tokens similar to DialogGPT
        formatted = f"<|user|>{user_msg}<|assistant|>{assistant_msg}<|endoftext|>"
        return formatted
    
    def prepare_dataset(self, data: List[Dict]) -> Dataset:
        """Prepare dataset for training"""
        print("[INFO] Formatting conversations...")
        texts = [self.format_conversation(ex) for ex in data]
        
        print("[INFO] Tokenizing...")
        tokenized = self.tokenizer(
            texts,
            truncation=True,
            max_length=512,  # GPT-2 context window
            padding='max_length',
            return_tensors='pt'
        )
        
        # Create dataset
        dataset = Dataset.from_dict({
            'input_ids': tokenized['input_ids'],
            'attention_mask': tokenized['attention_mask'],
        })
        
        return dataset
    
    def initialize_model(self):
        """Initialize GPT-2 model and tokenizer"""
        print(f"[INFO] Loading model: {self.model_name}")
        
        # Load tokenizer
        self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_name)
        
        # Add special tokens if not present
        special_tokens = {
            'pad_token': '<|pad|>',
            'additional_special_tokens': ['<|user|>', '<|assistant|>', '<|endoftext|>']
        }
        self.tokenizer.add_special_tokens(special_tokens)
        
        # Load model
        self.model = GPT2LMHeadModel.from_pretrained(self.model_name)
        self.model.resize_token_embeddings(len(self.tokenizer))
        
        print(f"[OK] Model initialized with {self.model.num_parameters():,} parameters")
    
    def train(self, 
              train_data: List[Dict],
              val_data: List[Dict],
              epochs: int = 3,
              batch_size: int = 4,
              learning_rate: float = 5e-5,
              use_gpu: bool = True):
        """Train the model"""
        
        # Prepare datasets
        train_dataset = self.prepare_dataset(train_data)
        val_dataset = self.prepare_dataset(val_data) if val_data else None
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False  # GPT-2 is autoregressive, not masked LM
        )
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=str(self.output_dir),
            overwrite_output_dir=True,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            warmup_steps=100,
            logging_steps=50,
            eval_steps=200,
            save_steps=200,  # Must be multiple of eval_steps
            eval_strategy="steps" if val_dataset else "no",
            save_total_limit=3,
            load_best_model_at_end=True if val_dataset else False,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            fp16=use_gpu and torch.cuda.is_available(),
            dataloader_pin_memory=use_gpu and torch.cuda.is_available(),
            report_to="none",  # Disable wandb/tensorboard
        )
        
        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            data_collator=data_collator,
        )
        
        # Train
        print("\n[INFO] Starting training...")
        print(f"  Epochs: {epochs}")
        print(f"  Batch size: {batch_size}")
        print(f"  Learning rate: {learning_rate}")
        print(f"  Device: {'GPU' if use_gpu and torch.cuda.is_available() else 'CPU'}")
        print("=" * 60)
        
        trainer.train()
        
        # Save final model
        print("\n[INFO] Saving model...")
        self.model.save_pretrained(self.output_dir)
        self.tokenizer.save_pretrained(self.output_dir)
        
        print(f"[OK] Model saved to {self.output_dir}")
        
        return trainer
    
    def test_generation(self, context: str, max_length: int = 150):
        """Test model generation"""
        if self.model is None or self.tokenizer is None:
            print("[ERROR] Model not initialized. Load model first.")
            return None
        
        # Format input
        input_text = f"<|user|>{context}<|assistant|>"
        input_ids = self.tokenizer.encode(input_text, return_tensors='pt')
        
        # Generate
        self.model.eval()
        with torch.no_grad():
            output = self.model.generate(
                input_ids,
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.encode('<|endoftext|>')[0],
            )
        
        # Decode
        generated_text = self.tokenizer.decode(output[0], skip_special_tokens=False)
        
        # Extract assistant response
        if '<|assistant|>' in generated_text:
            response = generated_text.split('<|assistant|>')[1]
            response = response.split('<|endoftext|>')[0].strip()
            return response
        
        return generated_text
    
    def run(self, epochs: int = 3, batch_size: int = 4, learning_rate: float = 5e-5):
        """Main execution"""
        print("=" * 60)
        print("DialogGPT Model Training")
        print("=" * 60)
        
        # Initialize model
        self.initialize_model()
        
        # Load data
        train_data, val_data = self.load_training_data()
        
        # Train
        use_gpu = torch.cuda.is_available()
        trainer = self.train(
            train_data,
            val_data,
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            use_gpu=use_gpu
        )
        
        # Test generation
        print("\n[INFO] Testing model generation...")
        test_context = "Question: Choose the correct form: 'I _____ to school every day.' | Type: multiple_choice | Grammar Point: simple_present | User Answer: went | Correct Answer: go | Is Correct: False"
        response = self.test_generation(test_context)
        print(f"\nTest Input: {test_context}")
        print(f"Generated Response: {response}")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Training complete!")
        print("=" * 60)
        print(f"\nNext steps:")
        print(f"1. Review model in: {self.output_dir}")
        print(f"2. Run: python export_model_to_onnx.py")
        print("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train DialogGPT model for grammar explanations")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=4, help="Batch size")
    parser.add_argument("--learning-rate", type=float, default=5e-5, help="Learning rate")
    parser.add_argument("--data-dir", type=str, default="training_data", help="Training data directory")
    parser.add_argument("--output-dir", type=str, default="models/dialogpt_grammar", help="Output directory")
    
    args = parser.parse_args()
    
    trainer = DialogGPTTrainer(
        data_dir=args.data_dir,
        output_dir=args.output_dir
    )
    trainer.run(
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate
    )

