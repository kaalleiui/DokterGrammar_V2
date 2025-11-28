#!/usr/bin/env python3
"""
Test script for AI Explanation Server
Tests the server endpoints
"""

import requests
import json
import time

SERVER_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("=" * 60)
    print("Testing Health Endpoint")
    print("=" * 60)
    
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Server is healthy")
            print(f"  Model loaded: {data.get('model_loaded', False)}")
            print(f"  Status: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"[ERROR] Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to server. Is it running?")
        print("  Start server with: python ai_explanation_server.py")
        return False
    except Exception as e:
        print(f"[ERROR] Health check failed: {e}")
        return False

def test_generate():
    """Test explanation generation"""
    print("\n" + "=" * 60)
    print("Testing Explanation Generation")
    print("=" * 60)
    
    test_data = {
        'prompt': "Choose the correct form: 'I _____ to school every day.'",
        'type': 'multiple_choice',
        'grammar_point': 'simple_present',
        'user_answer': 'went',
        'correct_answer': 'go',
        'is_correct': False,
        'difficulty': 1
    }
    
    try:
        print(f"\n[INFO] Sending request...")
        print(f"  Question: {test_data['prompt']}")
        print(f"  User Answer: {test_data['user_answer']}")
        print(f"  Correct Answer: {test_data['correct_answer']}")
        
        response = requests.post(
            f"{SERVER_URL}/generate",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"\n[OK] Explanation generated successfully!")
                print(f"  Type: {data.get('type')}")
                print(f"  Confidence: {data.get('confidence')}")
                print(f"  Generation time: {data.get('generation_time_ms')}ms")
                print(f"\n  Explanation:")
                print(f"  {data.get('text')}")
                return True
            else:
                print(f"[ERROR] Generation failed: {data.get('error')}")
                return False
        else:
            print(f"[ERROR] Request failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Generation test failed: {e}")
        return False

def test_sample():
    """Test sample endpoint"""
    print("\n" + "=" * 60)
    print("Testing Sample Endpoint")
    print("=" * 60)
    
    try:
        response = requests.get(f"{SERVER_URL}/test", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Sample test successful")
            print(f"  Model loaded: {data.get('model_loaded', False)}")
            if data.get('explanation'):
                print(f"\n  Generated explanation:")
                print(f"  {data['explanation']}")
            return True
        else:
            print(f"[ERROR] Sample test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Sample test failed: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("AI Explanation Server Test Suite")
    print("=" * 60)
    print("\n[INFO] Make sure the server is running:")
    print("  python ai_explanation_server.py")
    print("\n[INFO] Waiting 3 seconds for server to be ready...")
    time.sleep(3)
    
    all_passed = True
    
    # Run tests
    all_passed &= test_health()
    
    if all_passed:
        all_passed &= test_sample()
        all_passed &= test_generate()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] All tests passed!")
        print("\nServer is ready to use with Flutter app.")
    else:
        print("[FAILED] Some tests failed.")
        print("\nTroubleshooting:")
        print("1. Make sure server is running: python ai_explanation_server.py")
        print("2. Check server is on port 5000")
        print("3. Check model files exist in models/dialogpt_grammar/")
    print("=" * 60)

