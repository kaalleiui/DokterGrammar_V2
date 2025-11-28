#!/usr/bin/env python3
"""
Quick script to run the AI explanation server
Usage: python scripts/run_ai_server.py
"""

import sys
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir.parent))

# Import and run the server
from ai_explanation_server import app, load_model

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("Starting AI Explanation Server")
    print("=" * 60)
    
    # Load model first
    if load_model():
        print("\n[INFO] Server starting on http://localhost:5000")
        print("[INFO] Endpoints:")
        print("  GET  /health - Health check")
        print("  POST /generate - Generate explanation")
        print("  GET  /test - Test with sample data")
        print("\n[INFO] Press Ctrl+C to stop the server")
        print("=" * 60 + "\n")
        
        # Run server
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("\n[ERROR] Failed to load model. Cannot start server.")
        print("[INFO] Make sure the model exists at: models/dialogpt_grammar/")
        sys.exit(1)

