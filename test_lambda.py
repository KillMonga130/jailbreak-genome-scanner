"""Test Lambda Cloud API connection."""

import asyncio
import os
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variable if not set
if not os.getenv("LAMBDA_API_KEY"):
    # You can set it here temporarily for testing
    os.environ["LAMBDA_API_KEY"] = "secret_muele_ce33a3396f9d406583bb611dc3ab0bd9.v5H38gHQqPMfwcPjXaIR6QKer9FglUZg"

from src.integrations.lambda_cloud import LambdaCloudClient
from src.utils.logger import setup_logger

# Setup logger
log = setup_logger()


async def test_lambda_connection():
    """Test Lambda Cloud API connection."""
    print("=" * 60)
    print("Testing Lambda Cloud API Connection")
    print("=" * 60)
    
    # Get API key from environment
    api_key = os.getenv("LAMBDA_API_KEY")
    
    if not api_key:
        print("\n⚠️  LAMBDA_API_KEY not found in environment variables")
        print("Please set it in your .env file or environment:")
        print("LAMBDA_API_KEY=secret_xxx.xxx")
        return False
    
    print(f"\n[OK] API Key found: {api_key[:30]}...")
    
    # Initialize client
    print("\n1. Initializing Lambda Cloud client...")
    client = LambdaCloudClient(api_key=api_key)
    
    if not client.api_key:
        print("   [ERROR] Failed to initialize client (no API key)")
        return False
    
    print("   [OK] Client initialized")
    
    # Test listing instances
    print("\n2. Testing list_instances()...")
    try:
        instances = await client.list_instances()
        
        if instances is not None:
            print(f"   [OK] Successfully retrieved {len(instances)} instances")
            
            if instances:
                print("\n   Active instances:")
                for instance in instances:
                    instance_id = instance.get("id", "unknown")
                    status = instance.get("status", "unknown")
                    instance_type = instance.get("instance_type", {}).get("name", "unknown") if isinstance(instance.get("instance_type"), dict) else "unknown"
                    ip = instance.get("ip", "N/A")
                    
                    print(f"     - ID: {instance_id}")
                    print(f"       Type: {instance_type}")
                    print(f"       Status: {status}")
                    print(f"       IP: {ip}")
                    print()
            else:
                print("   ℹ️  No instances found (this is normal if you haven't launched any)")
                print("   ℹ️  This means your API key is working correctly!")
        else:
            print("   [ERROR] Failed to retrieve instances")
            return False
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test API endpoint connectivity
    print("\n3. Testing API endpoint connectivity...")
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as http_client:
            response = await http_client.get(
                "https://cloud.lambda.ai/api/v1/instances",
                auth=(api_key, "")
            )
            if response.status_code == 200:
                print("   [OK] API endpoint is accessible (200 OK)")
                print(f"   [OK] Response headers: {dict(response.headers)}")
            elif response.status_code == 401:
                print("   [ERROR] Authentication failed (401 Unauthorized)")
                print("   [WARNING] Check your API key")
                return False
            else:
                print(f"   [WARNING] API returned status code: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
    except httpx.ConnectError as e:
        print(f"   [ERROR] Connection error: {e}")
        return False
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("[SUCCESS] All tests passed! Lambda Cloud connection is working.")
    print("=" * 60)
    return True


async def test_instance_operations():
    """Test instance launch/terminate operations (optional - will create charges)."""
    print("\n" + "=" * 60)
    print("Testing Instance Operations (OPTIONAL - will create charges)")
    print("=" * 60)
    
    api_key = os.getenv("LAMBDA_API_KEY")
    if not api_key:
        print("LAMBDA_API_KEY not found")
        return
    
    client = LambdaCloudClient(api_key=api_key)
    
    print("\n⚠️  This will launch an actual Lambda Cloud instance and incur charges.")
    print("   Instance type: gpu_1x_a10")
    print("   Region: us-east-1")
    print("   Estimated cost: ~$0.50/hour")
    
    response = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    if response != "yes":
        print("Skipping instance launch test")
        return
    
    print("\nLaunching instance...")
    try:
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
                
                # Wait a bit
                print("\nWaiting 10 seconds before checking status...")
                await asyncio.sleep(10)
                
                # Check status
                instance = await client.get_instance_status(instance_id)
                if instance:
                    print(f"   Status: {instance.get('status')}")
                    print(f"   IP: {instance.get('ip', 'N/A')}")
            else:
                print("✗ Failed to get instance ID from response")
                print(f"Response: {instance_data}")
        else:
            print("✗ Failed to launch instance")
    except Exception as e:
        print(f"✗ Error launching instance: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main test function."""
    print("\nLambda Cloud Connection Test")
    print("=" * 60)
    
    # Run basic connection test
    success = await test_lambda_connection()
    
    if success:
        print("\n[SUCCESS] Connection test successful!")
        
        # Optionally test instance operations
        test_ops = input("\nDo you want to test instance operations? (yes/no): ").strip().lower()
        if test_ops == "yes":
            await test_instance_operations()
    else:
        print("\n[ERROR] Connection test failed. Please check your API key.")


if __name__ == "__main__":
    asyncio.run(main())

