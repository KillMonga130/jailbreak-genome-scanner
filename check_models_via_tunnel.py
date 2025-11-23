"""Check models on instances that require SSH tunnels."""

import sys
import asyncio
import httpx
import io
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

async def check_models_via_localhost(endpoint: str, instance_name: str):
    """Check models via localhost endpoint (SSH tunnel)."""
    print(f"\nChecking {instance_name} via SSH tunnel...")
    print(f"Endpoint: {endpoint}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Try /v1/models
            models_url = endpoint.replace("/v1/chat/completions", "/v1/models")
            models_url = models_url.replace("/v1/completions", "/v1/models")
            
            try:
                response = await client.get(models_url, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    if "data" in data:
                        models = [m.get("id", "unknown") for m in data["data"]]
                        print(f"✅ Found {len(models)} model(s):")
                        for model in models:
                            print(f"   - {model}")
                        return models
                    elif isinstance(data, list):
                        models = [m.get("id", "unknown") if isinstance(m, dict) else str(m) for m in data]
                        print(f"✅ Found {len(models)} model(s):")
                        for model in models:
                            print(f"   - {model}")
                        return models
            except httpx.ConnectError:
                print(f"❌ Cannot connect - SSH tunnel may not be running")
                print(f"   Make sure you started the SSH tunnel in another terminal")
                return None
            except Exception as e:
                print(f"⚠️  Error checking models: {e}")
                return None
    except Exception as e:
        print(f"❌ Failed: {e}")
        return None

async def main():
    """Main function."""
    print("="*80)
    print("CHECKING MODELS VIA SSH TUNNELS")
    print("="*80)
    print("\n⚠️  Make sure SSH tunnels are running before checking!")
    print()
    
    # Qwen instance (you started tunnel on port 8001)
    await check_models_via_localhost(
        "http://localhost:8001/v1/chat/completions",
        "Qwen (150.136.220.151) - Port 8001"
    )
    
    # Instance #4 (if you set up tunnel)
    await check_models_via_localhost(
        "http://localhost:8003/v1/chat/completions",
        "Instance #4 (165.1.79.86) - Port 8003"
    )
    
    print("\n" + "="*80)
    print("Done!")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())

