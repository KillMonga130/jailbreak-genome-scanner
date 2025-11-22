"""Test Lambda Cloud API connection."""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.integrations.lambda_cloud import LambdaCloudClient
from src.utils.logger import log


async def test_lambda_connection():
    """Test Lambda Cloud API connection."""
    print("=" * 60)
    print("Testing Lambda Cloud API Connection")
    print("=" * 60)
    
    # Get API key from environment or use provided one
    api_key = os.getenv("LAMBDA_API_KEY")
    
    if not api_key:
        print("\n⚠️  LAMBDA_API_KEY not found in environment variables")
        print("Please set it in your .env file:")
        print("LAMBDA_API_KEY=secret_xxx.xxx")
        return
    
    print(f"\n✓ API Key found: {api_key[:20]}...")
    
    # Initialize client
    print("\nInitializing Lambda Cloud client...")
    client = LambdaCloudClient(api_key=api_key)
    
    # Test listing instances
    print("\n1. Testing list_instances()...")
    instances = await client.list_instances()
    
    if instances is not None:
        print(f"   ✓ Successfully retrieved {len(instances)} instances")
        
        if instances:
            print("\n   Active instances:")
            for instance in instances:
                instance_id = instance.get("id", "unknown")
                status = instance.get("status", "unknown")
                instance_type = instance.get("instance_type", {}).get("name", "unknown")
                ip = instance.get("ip", "N/A")
                
                print(f"     - ID: {instance_id}")
                print(f"       Type: {instance_type}")
                print(f"       Status: {status}")
                print(f"       IP: {ip}")
                print()
        else:
            print("   ℹ️  No instances found (this is normal if you haven't launched any)")
    else:
        print("   ✗ Failed to retrieve instances")
    
    # Test getting instance types (if available)
    print("\n2. Testing API endpoint connectivity...")
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as http_client:
            # Test the instances endpoint
            response = await http_client.get(
                "https://cloud.lambda.ai/api/v1/instances",
                auth=(api_key, "")
            )
            if response.status_code == 200:
                print("   ✓ API endpoint is accessible")
            else:
                print(f"   ⚠️  API returned status code: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error connecting to API: {e}")
    
    print("\n" + "=" * 60)
    print("Connection test complete!")
    print("=" * 60)


async def test_launch_instance():
    """Test launching a Lambda Cloud instance (optional - will create charges)."""
    print("\n" + "=" * 60)
    print("Testing Instance Launch (OPTIONAL - will create charges)")
    print("=" * 60)
    
    api_key = os.getenv("LAMBDA_API_KEY")
    if not api_key:
        print("LAMBDA_API_KEY not found")
        return
    
    client = LambdaCloudClient(api_key=api_key)
    
    print("\n⚠️  This will launch an actual Lambda Cloud instance and incur charges.")
    print("   Instance type: gpu_1x_a10")
    print("   Region: us-east-1")
    
    response = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    if response != "yes":
        print("Skipping instance launch test")
        return
    
    print("\nLaunching instance...")
    instance_data = await client.launch_instance(
        instance_type="gpu_1x_a10",
        region="us-east-1",
        quantity=1
    )
    
    if instance_data:
        instance_ids = instance_data.get("instance_ids", [])
        if instance_ids:
            instance_id = instance_ids[0]
            print(f"✓ Instance launched: {instance_id}")
            print("\n⚠️  Remember to terminate this instance when done!")
            print(f"   Use: await client.terminate_instance('{instance_id}')")
        else:
            print("✗ Failed to get instance ID from response")
    else:
        print("✗ Failed to launch instance")


if __name__ == "__main__":
    print("\nLambda Cloud Connection Test")
    print("=" * 60)
    
    # Run basic connection test
    asyncio.run(test_lambda_connection())
    
    # Optionally test instance launch (commented out by default to avoid charges)
    # asyncio.run(test_launch_instance())

