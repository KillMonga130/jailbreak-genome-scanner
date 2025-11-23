"""Test all configured endpoints to verify they work."""

import sys
import asyncio
import httpx
from pathlib import Path
import json
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.integrations.lambda_cloud import LambdaCloudClient
from src.config import settings
from dotenv import load_dotenv
import os

# Load .env
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)

async def test_endpoint(url: str, name: str):
    """Test an API endpoint."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Try health check first
            health_url = url.replace("/v1/chat/completions", "/health")
            health_url = health_url.replace("/v1/completions", "/health")
            
            try:
                health_response = await client.get(health_url, timeout=5.0)
                if health_response.status_code == 200:
                    print(f"✅ Health check: OK")
                else:
                    print(f"⚠️  Health check: Status {health_response.status_code}")
            except Exception as e:
                print(f"⚠️  Health check: {type(e).__name__}")
            
            # Test API call
            # Try completions format (more compatible)
            completions_url = url.replace("/chat/completions", "/completions")
            if "/completions" not in completions_url:
                completions_url = url
            
            payload = {
                "model": "test",
                "prompt": "Say hello",
                "max_tokens": 5
            }
            
            try:
                response = await client.post(completions_url, json=payload, timeout=10.0)
                
                if response.status_code == 200:
                    data = response.json()
                    if "choices" in data and len(data["choices"]) > 0:
                        print(f"✅ API endpoint: WORKING")
                        print(f"✅ Response format: Valid")
                        return True
                    else:
                        print(f"⚠️  API endpoint: Response format unexpected")
                        print(f"   Response: {str(data)[:200]}")
                        return False
                else:
                    print(f"❌ API endpoint: Status {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                    return False
                    
            except httpx.ConnectError as e:
                print(f"❌ Connection failed: Cannot reach endpoint")
                if "localhost" in url:
                    print(f"   💡 Localhost endpoint - make sure SSH tunnel is running!")
                else:
                    print(f"   💡 Direct IP endpoint - check if port 8000 is open")
                return False
            except httpx.TimeoutException:
                print(f"❌ Request timed out")
                return False
            except Exception as e:
                print(f"❌ Error: {type(e).__name__}: {str(e)[:200]}")
                return False
                
    except Exception as e:
        print(f"❌ Failed to test: {e}")
        return False

async def main():
    """Main function."""
    print("=" * 80)
    print("COMPREHENSIVE ENDPOINT TESTING")
    print("=" * 80)
    print()
    
    # Load deployments config
    deployments_path = project_root / "data" / "lambda_deployments.json"
    endpoints_to_test = []
    
    if deployments_path.exists():
        with open(deployments_path, 'r') as f:
            config = json.load(f)
            deployed = config.get("deployed_models", {})
            
            for model_name, model_info in deployed.items():
                instance_ip = model_info.get("instance_ip")
                direct_endpoint = model_info.get("api_endpoint")
                local_endpoint = model_info.get("api_endpoint_local")
                
                if direct_endpoint and "localhost" not in direct_endpoint:
                    endpoints_to_test.append((direct_endpoint, f"{model_name} (Direct IP)"))
                
                if local_endpoint and "localhost" in local_endpoint:
                    endpoints_to_test.append((local_endpoint, f"{model_name} (SSH Tunnel)"))
    
    # Also get from Lambda API
    try:
        client = LambdaCloudClient()
        instances = await client.list_instances()
        
        for inst in instances:
            ip = inst.get("ip")
            status = inst.get("status")
            instance_type = inst.get("instance_type", {})
            if isinstance(instance_type, dict):
                type_name = instance_type.get("name", "N/A")
            else:
                type_name = instance_type
            
            if status == "active" and ip:
                endpoint = f"http://{ip}:8000/v1/completions"
                # Only add if not already in list
                if not any(e[0] == endpoint for e in endpoints_to_test):
                    endpoints_to_test.append((endpoint, f"{type_name} ({ip})"))
    except Exception as e:
        print(f"⚠️  Could not load instances from API: {e}")
    
    if not endpoints_to_test:
        print("❌ No endpoints found to test")
        print("   Check deployments.json or Lambda instances")
        return
    
    print(f"Found {len(endpoints_to_test)} endpoint(s) to test\n")
    
    results = {}
    for endpoint, name in endpoints_to_test:
        result = await test_endpoint(endpoint, name)
        results[name] = {
            "endpoint": endpoint,
            "working": result
        }
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    working = sum(1 for r in results.values() if r["working"])
    total = len(results)
    
    print(f"\nWorking: {working}/{total}")
    print()
    
    for name, result in results.items():
        status = "✅ WORKING" if result["working"] else "❌ NOT WORKING"
        print(f"{status}: {name}")
        print(f"  Endpoint: {result['endpoint']}")
        if not result["working"]:
            if "localhost" in result["endpoint"]:
                print(f"  💡 Fix: Start SSH tunnel")
            else:
                print(f"  💡 Fix: Check if vLLM is running or port is open")

if __name__ == "__main__":
    asyncio.run(main())

