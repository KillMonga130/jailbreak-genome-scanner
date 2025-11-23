"""
Script to manage Lambda Cloud instances - start/stop on demand.
This helps save costs by only running instances when needed.
"""

import asyncio
import sys
from pathlib import Path
from src.integrations.lambda_cloud import LambdaCloudClient
from src.utils.logger import log

async def list_instances():
    """List all Lambda instances."""
    client = LambdaCloudClient()
    instances = await client.list_instances()
    
    if not instances:
        print("No instances found.")
        return
    
    print("\n=== Lambda Cloud Instances ===\n")
    for instance in instances:
        instance_id = instance.get("id", "N/A")
        name = instance.get("name", "Unnamed")
        status = instance.get("status", "unknown")
        instance_type = instance.get("instance_type", {}).get("name", "N/A")
        ip = instance.get("ip", "N/A")
        
        print(f"ID: {instance_id}")
        print(f"Name: {name}")
        print(f"Status: {status}")
        print(f"Type: {instance_type}")
        print(f"IP: {ip}")
        print("-" * 50)

async def check_and_start_instance(instance_id: str):
    """Check instance status and start if stopped."""
    client = LambdaCloudClient()
    instance = await client.get_instance_status(instance_id)
    
    if not instance:
        print(f"Instance {instance_id} not found.")
        return False
    
    status = instance.get("status")
    print(f"Instance {instance_id} status: {status}")
    
    if status == "active":
        print("Instance is already running.")
        return True
    elif status == "billing":
        print("Instance is starting up...")
        return True
    elif status == "uninitialized":
        print("Instance needs to be initialized. Cannot auto-start.")
        return False
    else:
        print(f"Instance status '{status}' - may need manual intervention.")
        return False

async def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/manage_lambda_instances.py list")
        print("  python scripts/manage_lambda_instances.py check <instance_id>")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        await list_instances()
    elif command == "check":
        if len(sys.argv) < 3:
            print("Error: instance_id required")
            return
        instance_id = sys.argv[2]
        await check_and_start_instance(instance_id)
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    asyncio.run(main())

