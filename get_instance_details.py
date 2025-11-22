"""Quick script to get Lambda Cloud instance details."""

import asyncio
import os
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load config (which loads from .env)
from src.config import settings
from src.integrations.lambda_cloud import LambdaCloudClient

async def get_instance_details():
    """Get and display instance details."""
    # Check for API key from config (which loads from .env or environment)
    api_key = settings.lambda_api_key or os.getenv("LAMBDA_API_KEY")
    
    if not api_key:
        print("\n" + "=" * 70)
        print("ERROR: Lambda API Key Not Configured")
        print("=" * 70)
        print("\nPlease configure your Lambda Cloud API key:")
        print("\n1. Get API key from: https://cloud.lambda.ai")
        print("2. Create .env file in project root with:")
        print("   LAMBDA_API_KEY=secret_your_id.your_token")
        print("\nOr set environment variable:")
        print("   Windows PowerShell: $env:LAMBDA_API_KEY='your_key'")
        print("   Linux/Mac: export LAMBDA_API_KEY='your_key'")
        print("\nSee LAMBDA_CLOUD_CONFIGURATION.md for details")
        return
    
    client = LambdaCloudClient(api_key=api_key)
    
    print("\n" + "=" * 70)
    print("LAMBDA CLOUD INSTANCES")
    print("=" * 70 + "\n")
    
    instances = await client.list_instances()
    
    if not instances:
        print("No instances found!")
        print("\nPossible reasons:")
        print("  - No instances have been launched yet")
        print("  - API key not configured correctly")
        print("  - All instances were terminated")
        return
    
    for i, instance in enumerate(instances, 1):
        print(f"Instance #{i}")
        print("-" * 70)
        
        # Instance ID
        instance_id = instance.get('id', 'N/A')
        print(f"  Instance ID: {instance_id}")
        
        # IP Address
        ip = instance.get('ip', 'N/A')
        print(f"  IP Address: {ip}")
        
        # Status
        status = instance.get('status', 'N/A')
        if status == "active":
            status_icon = "[OK]"
        elif status == "booting":
            status_icon = "[WAIT]"
        else:
            status_icon = "[!]"
        print(f"  Status: {status_icon} {status}")
        
        # Instance Type
        instance_type = instance.get('instance_type', {})
        if isinstance(instance_type, dict):
            instance_type_name = instance_type.get('name', 'N/A')
        else:
            instance_type_name = instance_type
        print(f"  Instance Type: {instance_type_name}")
        
        # Region
        region = instance.get('region', {})
        if isinstance(region, dict):
            region_name = region.get('name', 'N/A')
        else:
            region_name = region
        print(f"  Region: {region_name}")
        
        # SSH Key
        ssh_keys = instance.get('ssh_key_names', [])
        ssh_key = ssh_keys[0] if ssh_keys else 'N/A'
        print(f"  SSH Key: {ssh_key}")
        
        # Get SSH command
        if ip != 'N/A' and ssh_key != 'N/A':
            ssh_cmd = client.get_ssh_command(instance)
            if ssh_cmd:
                print(f"  SSH Command: {ssh_cmd}")
        
        # API Endpoint (if ready)
        if ip != 'N/A' and status == "active":
            print(f"  API Endpoint: http://{ip}:8000/v1/chat/completions")
        
        print()
    
    print("=" * 70)
    print(f"\nTotal Instances: {len(instances)}")
    
    # Summary
    active = [i for i in instances if i.get('status') == 'active']
    if active:
        print(f"Active Instances: {len(active)}")
        print("\n[OK] Ready to use!")
        print("\nNext steps:")
        print("  1. Set up vLLM on the instance")
        print("  2. Test connectivity: python scripts/check_connectivity.py --ip <IP>")
        print("  3. Use in dashboard or code with the API endpoint")

if __name__ == "__main__":
    asyncio.run(get_instance_details())

