#!/usr/bin/env python3
"""Test vLLM API endpoint."""

import requests
import json
import sys

def test_api():
    """Test the vLLM API endpoint."""
    url = "http://localhost:8000/v1/chat/completions"
    
    payload = {
        "model": "microsoft/phi-2",
        "messages": [{"role": "user", "content": "Say hello"}],
        "max_tokens": 10
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(json.dumps(result, indent=2))
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)

