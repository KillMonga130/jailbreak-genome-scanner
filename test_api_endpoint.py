"""Test the vLLM API endpoint end-to-end."""

import requests
import json
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def test_api_endpoint(endpoint="http://209.20.159.141:8000/v1/chat/completions"):
    """Test the API endpoint with a simple request."""
    
    print("=" * 70)
    print("TESTING vLLM API ENDPOINT")
    print("=" * 70)
    print(f"\nEndpoint: {endpoint}")
    print()
    
    # Test payload
    payload = {
        "model": "mistralai/Mistral-7B-Instruct-v0.2",
        "messages": [
            {
                "role": "user",
                "content": "Say 'Hello, API is working!' in exactly one sentence."
            }
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    print("Sending test request...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        # Make the request
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            print("[SUCCESS] API Request Successful!")
            print()
            print("Response:")
            print(json.dumps(result, indent=2))
            print()
            
            # Extract the message content
            if "choices" in result and len(result["choices"]) > 0:
                message = result["choices"][0].get("message", {})
                content = message.get("content", "")
                print("=" * 70)
                print("EXTRACTED RESPONSE:")
                print("=" * 70)
                print(content)
                print("=" * 70)
                print()
                print("[SUCCESS] END-TO-END TEST PASSED!")
                print()
                print("Your API endpoint is fully functional and ready to use!")
                return True
            else:
                print("[WARNING] Response doesn't contain expected 'choices' field")
                return False
        else:
            print(f"[ERROR] Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out after 30 seconds")
        print("The server may still be processing or the model is loading.")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check if port 8000 is accessible from your machine")
        print("2. You may need to use SSH tunnel if port is blocked")
        print(f"3. Verify server is running: ssh -i moses.pem ubuntu@209.20.159.141 'curl http://localhost:8000/health'")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    endpoint = sys.argv[1] if len(sys.argv) > 1 else "http://209.20.159.141:8000/v1/chat/completions"
    success = test_api_endpoint(endpoint)
    sys.exit(0 if success else 1)

