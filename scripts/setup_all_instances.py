"""
Setup vLLM on all Lambda Cloud instances.
This script will set up vLLM on all your configured instances.
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded environment variables from {env_path}")
    else:
        print(f"Warning: .env file not found at {env_path}")
except ImportError:
    print("Warning: python-dotenv not installed, environment variables may not load from .env file")
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")

from src.integrations.lambda_cloud import LambdaCloudClient
from src.utils.logger import log

# Your instance configurations
INSTANCE_CONFIGS = [
    {
        "name": "Mistral_7B_Instruct",
        "ip": "129.80.191.122",
        "instance_id": "cd6537df1d7640a995090d45eff85e3e",
        "model": "mistralai/Mistral-7B-Instruct-v0.2",
        "port": 8000,
        "ssh_key": "moses.pem"
    },
    {
        "name": "Qwen_7B_Chat",
        "ip": "150.136.220.151",
        "instance_id": None,  # Will be detected
        "model": "Qwen/Qwen-7B-Chat",
        "port": 8000,
        "ssh_key": "moses.pem"
    },
    {
        "name": "H100_FOR_THE_HACKATHON",
        "ip": "209.20.159.141",
        "instance_id": None,  # Will be detected
        "model": "mistralai/Mistral-7B-Instruct-v0.2",  # Or whatever model you want on H100
        "port": 8000,
        "ssh_key": "moses.pem"
    }
]


async def check_instance_status(ip: str, instance_id: Optional[str] = None) -> Dict[str, Any]:
    """Check if instance is accessible and get status."""
    client = LambdaCloudClient()
    
    # Try to get instance status from Lambda API
    if instance_id:
        instance = await client.get_instance_status(instance_id)
        if instance:
            return {
                "accessible": True,
                "status": instance.get("status", "unknown"),
                "ip": instance.get("ip", ip)
            }
    
    # Fallback: just check if IP is accessible
    return {
        "accessible": True,  # Assume accessible if we have IP
        "status": "unknown",
        "ip": ip
    }


def check_vllm_running(ip: str, ssh_key: str) -> bool:
    """Check if vLLM is already running on the instance."""
    import subprocess
    
    try:
        cmd = [
            "ssh",
            "-i", ssh_key,
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=5",
            f"ubuntu@{ip}",
            "ps aux | grep vllm | grep -v grep || echo 'not_running'"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return "not_running" not in result.stdout
    except Exception as e:
        log.warning(f"Could not check vLLM status on {ip}: {e}")
        return False


def setup_vllm_on_instance(config: Dict[str, Any], force: bool = False) -> bool:
    """Set up vLLM on a single instance."""
    name = config["name"]
    ip = config["ip"]
    model = config["model"]
    ssh_key = config["ssh_key"]
    port = config.get("port", 8000)
    
    print(f"\n{'='*70}")
    print(f"Setting up {name}")
    print(f"{'='*70}")
    print(f"IP: {ip}")
    print(f"Model: {model}")
    print(f"Port: {port}")
    print()
    
    # Check if vLLM is already running
    if not force:
        print("Checking if vLLM is already running...")
        if check_vllm_running(ip, ssh_key):
            print(f"✅ vLLM is already running on {name}")
            print("   Use --force to restart it")
            return True
    
    # Use the existing setup script
    setup_script = project_root / "scripts" / "setup_vllm_on_lambda.py"
    if not setup_script.exists():
        print(f"❌ Setup script not found: {setup_script}")
        return False
    
    import subprocess
    
    cmd = [
        sys.executable,
        str(setup_script),
        "--ip", ip,
        "--key", ssh_key,
        "--model", model
        # Note: setup_vllm_on_lambda.py always uses port 8000, --port not supported
    ]
    
    if force:
        cmd.append("--force")
    
    print(f"Running setup script...")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, check=False)
        if result.returncode == 0:
            print(f"✅ Successfully set up vLLM on {name}")
            return True
        else:
            print(f"❌ Setup failed for {name} (exit code: {result.returncode})")
            return False
    except Exception as e:
        print(f"❌ Error setting up {name}: {e}")
        return False


async def setup_all_instances(force: bool = False, instances: Optional[List[str]] = None):
    """Set up vLLM on all configured instances."""
    print("="*70)
    print("LAMBDA CLOUD INSTANCE SETUP")
    print("="*70)
    print()
    print(f"Found {len(INSTANCE_CONFIGS)} instance configurations")
    print()
    
    # Filter instances if specific ones requested
    configs_to_setup = INSTANCE_CONFIGS
    if instances:
        configs_to_setup = [c for c in INSTANCE_CONFIGS if c["name"] in instances]
        if not configs_to_setup:
            print(f"❌ No matching instances found. Available: {[c['name'] for c in INSTANCE_CONFIGS]}")
            return
    
    results = {}
    
    for config in configs_to_setup:
        name = config["name"]
        print(f"\nProcessing {name}...")
        
        # Check instance status
        try:
            status = await check_instance_status(config["ip"], config.get("instance_id"))
            if status["status"] not in ["active", "unknown"]:
                print(f"⚠️  Instance status: {status['status']}")
                print(f"   Instance may need to be started in Lambda Cloud dashboard")
        except Exception as e:
            print(f"⚠️  Could not check instance status: {e}")
        
        # Set up vLLM
        success = setup_vllm_on_instance(config, force=force)
        results[name] = success
    
    # Summary
    print("\n" + "="*70)
    print("SETUP SUMMARY")
    print("="*70)
    print()
    
    for name, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{name}: {status}")
    
    print()
    successful = sum(1 for s in results.values() if s)
    print(f"Total: {successful}/{len(results)} instances set up successfully")
    
    if successful == len(results):
        print("\n🎉 All instances are ready!")
        print("\nNext steps:")
        print("1. Start SSH tunnels: .\\scripts\\setup_ssh_tunnels.ps1")
        print("2. Test connections: curl http://localhost:8000/v1/models")
        print("3. Run evaluations in the dashboard!")
    else:
        print("\n⚠️  Some instances failed. Check the errors above.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Set up vLLM on all Lambda Cloud instances"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force setup even if vLLM is already running"
    )
    parser.add_argument(
        "--instances",
        nargs="+",
        help="Specific instances to set up (by name). Available: " + ", ".join([c["name"] for c in INSTANCE_CONFIGS])
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all configured instances"
    )
    
    args = parser.parse_args()
    
    if args.list:
        print("Configured instances:")
        for config in INSTANCE_CONFIGS:
            print(f"  - {config['name']}: {config['ip']} ({config['model']})")
        return
    
    asyncio.run(setup_all_instances(force=args.force, instances=args.instances))


if __name__ == "__main__":
    main()

