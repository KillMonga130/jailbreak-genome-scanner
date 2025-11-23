"""Comprehensive instance discovery - finds models, tests ports, shows access methods."""

import sys
import asyncio
import httpx
import io
from pathlib import Path
import json

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load .env
from dotenv import load_dotenv
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)

from src.integrations.lambda_cloud import LambdaCloudClient
from scripts.ssh_tunnel_helper import check_port_connectivity

async def get_models_on_instance(ip: str, endpoint: str):
    """Get list of models running on an instance."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Try /v1/models endpoint
            models_url = endpoint.replace("/v1/chat/completions", "/v1/models")
            models_url = models_url.replace("/v1/completions", "/v1/models")
            
            try:
                response = await client.get(models_url, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    if "data" in data:
                        models = [m.get("id", "unknown") for m in data["data"]]
                        return models
                    elif isinstance(data, list):
                        models = [m.get("id", "unknown") if isinstance(m, dict) else str(m) for m in data]
                        return models
            except:
                pass
            
            # Fallback: Try to infer from health check or test a common model
            # Try common model names
            common_models = [
                "mistralai/Mistral-7B-Instruct-v0.2",
                "Qwen/Qwen-7B-Chat",
                "microsoft/phi-2",
                "meta-llama/Llama-2-7b-chat-hf"
            ]
            
            # Test with a simple prompt to see what works
            for model in common_models:
                try:
                    test_url = endpoint.replace("/chat/completions", "/completions")
                    if "/completions" not in test_url:
                        test_url = endpoint
                    
                    payload = {
                        "model": model,
                        "prompt": "test",
                        "max_tokens": 1
                    }
                    response = await client.post(test_url, json=payload, timeout=3.0)
                    if response.status_code == 200:
                        return [model]  # Found a working model
                except:
                    continue
            
            return None
    except Exception as e:
        return None

async def test_instance_access(ip: str):
    """Test all access methods for an instance."""
    results = {
        "ssh": False,
        "direct_api": False,
        "ssh_tunnel_needed": False,
        "models": []
    }
    
    # Test SSH (port 22)
    results["ssh"] = check_port_connectivity(ip, 22, timeout=3.0)
    
    # Test direct API (port 8000)
    results["direct_api"] = check_port_connectivity(ip, 8000, timeout=3.0)
    
    # If direct API doesn't work, SSH tunnel is needed
    if not results["direct_api"] and results["ssh"]:
        results["ssh_tunnel_needed"] = True
    
    return results

async def discover_all_instances():
    """Discover all instances, their models, and access methods."""
    print("\n" + "="*80)
    print("COMPREHENSIVE INSTANCE DISCOVERY")
    print("="*80 + "\n")
    
    client = LambdaCloudClient()
    instances = await client.list_instances()
    
    active_instances = [i for i in instances if i.get('status') == 'active']
    
    if not active_instances:
        print("[WARNING] No active instances found")
        return
    
    print(f"Found {len(active_instances)} active instance(s)\n")
    
    results = []
    
    for i, inst in enumerate(active_instances, 1):
        instance_id = inst.get('id', 'N/A')
        ip = inst.get('ip', 'N/A')
        instance_type = inst.get('instance_type', {})
        if isinstance(instance_type, dict):
            type_name = instance_type.get('name', 'N/A')
        else:
            type_name = instance_type
        
        print(f"{'='*80}")
        print(f"INSTANCE #{i}: {type_name}")
        print(f"{'='*80}")
        print(f"ID: {instance_id}")
        print(f"IP: {ip}")
        print()
        
        # Test access methods
        print("Testing access methods...")
        access = await test_instance_access(ip)
        
        print(f"  SSH (port 22): {'✅ Accessible' if access['ssh'] else '❌ Not accessible'}")
        print(f"  Direct API (port 8000): {'✅ Accessible' if access['direct_api'] else '❌ Blocked'}")
        
        if access['ssh_tunnel_needed']:
            print(f"  ⚠️  SSH tunnel required for API access")
        
        print()
        
        # Try to get models
        if access['direct_api']:
            endpoint = f"http://{ip}:8000/v1/chat/completions"
            print(f"Discovering models on instance...")
            models = await get_models_on_instance(ip, endpoint)
            
            if models:
                print(f"  ✅ Found {len(models)} model(s):")
                for model in models:
                    print(f"     - {model}")
                access['models'] = models
            else:
                print(f"  ⚠️  Could not detect models (vLLM may not be running)")
                print(f"     Try: ssh -i moses.pem ubuntu@{ip} 'curl http://localhost:8000/v1/models'")
        elif access['ssh_tunnel_needed']:
            print(f"⚠️  Cannot check models - port 8000 blocked")
            print(f"   Set up SSH tunnel first, then check models")
        else:
            print(f"⚠️  Cannot check models - no access method available")
        
        print()
        
        # Show access instructions
        print("ACCESS METHODS:")
        print("-" * 80)
        
        if access['direct_api']:
            endpoint = f"http://{ip}:8000/v1/chat/completions"
            print(f"✅ Direct API Access (Recommended):")
            print(f"   Endpoint: {endpoint}")
            print(f"   Use this in dashboard or code")
        else:
            print(f"❌ Direct API Access: NOT AVAILABLE")
        
        if access['ssh_tunnel_needed']:
            # Determine local port (use 8000, 8001, 8002, etc.)
            port_offset = i - 1
            local_port = 8000 + port_offset
            
            print(f"\n✅ SSH Tunnel Access (Required):")
            print(f"   Command: ssh -i moses.pem -N -L {local_port}:localhost:8000 ubuntu@{ip}")
            print(f"   Endpoint: http://localhost:{local_port}/v1/chat/completions")
            print(f"   Note: Run this in a separate terminal, keep it running")
        
        if access['ssh']:
            print(f"\n✅ SSH Access:")
            print(f"   Command: ssh -i moses.pem ubuntu@{ip}")
            print(f"   Use this to check vLLM status, view logs, etc.")
        
        print()
        
        # Store results
        result = {
            "instance_id": instance_id,
            "ip": ip,
            "type": type_name,
            "access": access,
            "endpoints": {}
        }
        
        if access['direct_api']:
            result["endpoints"]["direct"] = f"http://{ip}:8000/v1/chat/completions"
        
        if access['ssh_tunnel_needed']:
            port_offset = i - 1
            local_port = 8000 + port_offset
            result["endpoints"]["ssh_tunnel"] = f"http://localhost:{local_port}/v1/chat/completions"
            result["endpoints"]["ssh_tunnel_command"] = f"ssh -i moses.pem -N -L {local_port}:localhost:8000 ubuntu@{ip}"
        
        results.append(result)
    
    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print()
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['type']} ({result['ip']})")
        if result['access']['models']:
            print(f"   Models: {', '.join(result['access']['models'])}")
        else:
            print(f"   Models: Unknown")
        
        if result['endpoints'].get('direct'):
            print(f"   ✅ Direct: {result['endpoints']['direct']}")
        elif result['endpoints'].get('ssh_tunnel'):
            print(f"   ⚠️  SSH Tunnel: {result['endpoints']['ssh_tunnel']}")
            print(f"      Command: {result['endpoints']['ssh_tunnel_command']}")
        print()
    
    # Save to file
    output_file = project_root / "data" / "instance_discovery.json"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Results saved to: {output_file}")
    print()
    print("🚀 NEXT STEP: Use these endpoints in your dashboard!")
    print("   streamlit run dashboard/arena_dashboard.py")
    print()

if __name__ == "__main__":
    asyncio.run(discover_all_instances())

