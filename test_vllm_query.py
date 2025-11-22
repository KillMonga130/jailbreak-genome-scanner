"""Test vLLM API query to verify it's working correctly."""

import httpx
import json
import sys

def test_vllm_api(endpoint="http://localhost:8000/v1/completions", model="microsoft/phi-2"):
    """Test vLLM API with a simple query."""
    print("=" * 60)
    print("Testing vLLM API")
    print("=" * 60)
    print(f"Endpoint: {endpoint}")
    print(f"Model: {model}")
    print()
    
    # Test prompt
    prompt = "What is the capital of France?"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    print(f"Sending request...")
    print(f"Prompt: {prompt}")
    print()
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(endpoint, json=payload)
            
            print(f"Status Code: {response.status_code}")
            print()
            
            if response.status_code == 200:
                data = response.json()
                print("[OK] SUCCESS - API responded correctly!")
                print()
                print("Response:")
                print("-" * 60)
                
                if "choices" in data and len(data["choices"]) > 0:
                    choice = data["choices"][0]
                    if "text" in choice:
                        response_text = choice["text"]
                        print(response_text)
                    elif "message" in choice and "content" in choice["message"]:
                        response_text = choice["message"]["content"]
                        print(response_text)
                    else:
                        print(json.dumps(choice, indent=2))
                else:
                    print(json.dumps(data, indent=2))
                
                print("-" * 60)
                print()
                print("Usage:")
                if "usage" in data:
                    usage = data["usage"]
                    print(f"  Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
                    print(f"  Completion tokens: {usage.get('completion_tokens', 'N/A')}")
                    print(f"  Total tokens: {usage.get('total_tokens', 'N/A')}")
                
                return True
            else:
                print(f"[ERROR] Status {response.status_code}")
                print()
                print("Response:")
                print("-" * 60)
                try:
                    error_data = response.json()
                    print(json.dumps(error_data, indent=2))
                except:
                    print(response.text[:500])
                print("-" * 60)
                return False
                
    except httpx.ConnectError as e:
        print(f"[ERROR] CONNECTION ERROR")
        print(f"   Cannot connect to {endpoint}")
        print(f"   Error: {str(e)}")
        print()
        print("Make sure:")
        print("  1. SSH tunnel is running:")
        print("     python scripts/ssh_tunnel_helper.py --ip 150.136.146.143 --key moses.pem")
        print("  2. vLLM is running on the instance")
        return False
    except httpx.TimeoutException:
        print(f"[ERROR] TIMEOUT ERROR")
        print(f"   Request timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"[ERROR]")
        print(f"   {type(e).__name__}: {str(e)}")
        return False


if __name__ == "__main__":
    # Allow command line arguments
    endpoint = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/v1/completions"
    model = sys.argv[2] if len(sys.argv) > 2 else "microsoft/phi-2"
    
    success = test_vllm_api(endpoint, model)
    sys.exit(0 if success else 1)

