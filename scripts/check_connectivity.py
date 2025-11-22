"""Check Lambda Cloud instance connectivity and provide diagnostics."""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.ssh_tunnel_helper import check_port_connectivity, test_api_endpoint
from src.integrations.lambda_cloud import LambdaCloudClient
from src.utils.logger import log


async def check_instance_connectivity(instance_id: str = None, instance_ip: str = None, api_endpoint: str = None):
    """Check connectivity to Lambda instance and provide diagnostics."""
    print("=" * 60)
    print("Lambda Cloud Instance Connectivity Diagnostics")
    print("=" * 60)
    print()
    
    # Get instance IP from various sources
    if instance_ip:
        ip = instance_ip
    elif instance_id:
        # Try to get from API
        lambda_client = LambdaCloudClient()
        instance = await lambda_client.get_instance_status(instance_id)
        if instance:
            ip = instance.get("ip")
            status = instance.get("status")
            print(f"Instance ID: {instance_id}")
            print(f"Status: {status}")
        else:
            # Try to load from deployments file
            import json
            deployments_path = Path("data/lambda_deployments.json")
            if deployments_path.exists():
                with open(deployments_path, 'r') as f:
                    config = json.load(f)
                    deployed = config.get("deployed_models", {})
                    for key, value in deployed.items():
                        if value.get("instance_id") == instance_id:
                            ip = value.get("instance_ip")
                            print(f"Instance ID: {instance_id}")
                            print(f"IP Address (from deployments file): {ip}")
                            break
            else:
                print(f"[ERROR] Instance {instance_id} not found and deployments file not available")
                return False
    else:
        # Try to load from deployments file
        import json
        deployments_path = Path("data/lambda_deployments.json")
        if deployments_path.exists():
            with open(deployments_path, 'r') as f:
                config = json.load(f)
                deployed = config.get("deployed_models", {})
                if deployed:
                    first_model = list(deployed.keys())[0]
                    model_config = deployed[first_model]
                    ip = model_config.get("instance_ip")
                    instance_id = model_config.get("instance_id")
                    print(f"Instance ID (from deployments): {instance_id}")
                    print(f"IP Address (from deployments): {ip}")
        else:
            print("[ERROR] No instance ID or IP provided")
            return False
    
    if not ip:
        print("[ERROR] Could not determine instance IP address")
        return False
    
    instance_ip = ip
    print(f"IP Address: {instance_ip}")
    print()
    
    # Check SSH connectivity (port 22)
    print("Step 1: Checking SSH connectivity (port 22)...")
    ssh_accessible = check_port_connectivity(instance_ip, 22, timeout=5.0)
    if ssh_accessible:
        print(f"[OK] SSH port (22) is accessible")
    else:
        print(f"[ERROR] SSH port (22) is not accessible")
        print("         Cannot connect to instance via SSH")
        return False
    
    print()
    
    # Check API port (8000)
    print("Step 2: Checking API port connectivity (port 8000)...")
    api_port = 8000
    port_accessible = check_port_connectivity(instance_ip, api_port, timeout=5.0)
    
    if port_accessible:
        print(f"[OK] Port {api_port} is accessible")
        print()
        
        # Test API endpoint
        endpoint = api_endpoint or f"http://{instance_ip}:{api_port}/v1/chat/completions"
        print(f"Step 3: Testing API endpoint...")
        print(f"        Endpoint: {endpoint}")
        
        success, message = test_api_endpoint(endpoint, timeout=10.0)
        if success:
            print(f"[OK] {message}")
            print()
            print("=" * 60)
            print("[SUCCESS] API endpoint is fully accessible!")
            print("=" * 60)
            return True
        else:
            print(f"[WARNING] {message}")
            print()
            print("Port is open but API may not be responding correctly")
            return False
    else:
        print(f"[ERROR] Port {api_port} is NOT accessible")
        print()
        print("=" * 60)
        print("DIAGNOSIS: Port 8000 is blocked by firewall/security group")
        print("=" * 60)
        print()
        print("Options to fix:")
        print()
        print("Option 1: Use SSH Tunnel (Recommended for testing)")
        print(f"  python scripts/ssh_tunnel_helper.py --ip {instance_ip} --key moses.pem")
        print("  Then use endpoint: http://localhost:8000/v1/chat/completions")
        print()
        print("Option 2: Configure Lambda Cloud Security Group")
        print("  1. Go to Lambda Cloud dashboard")
        print("  2. Find your instance's security group")
        print("  3. Add inbound rule: Allow TCP port 8000 from your IP (or 0.0.0.0/0)")
        print("  4. Wait a few minutes for changes to take effect")
        print()
        print("Option 3: Check if vLLM is running")
        print(f"  ssh -i moses.pem ubuntu@{instance_ip}")
        print("  curl http://localhost:8000/health")
        print("  tail -f /tmp/vllm.log")
        print()
        return False


def main():
    """Main function."""
    import asyncio
    
    parser = argparse.ArgumentParser(description="Check Lambda Cloud instance connectivity")
    parser.add_argument("--instance-id", help="Lambda instance ID")
    parser.add_argument("--ip", help="Instance IP address (alternative to instance-id)")
    parser.add_argument("--endpoint", help="API endpoint to test")
    
    args = parser.parse_args()
    
    instance_id = args.instance_id
    instance_ip = args.ip
    endpoint = args.endpoint
    
    # Run connectivity check (can work with just IP)
    success = asyncio.run(check_instance_connectivity(instance_id=instance_id, instance_ip=instance_ip, api_endpoint=endpoint))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

