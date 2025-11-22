"""Helper script for Lambda Cloud security group configuration."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.integrations.lambda_cloud import LambdaCloudClient
from src.utils.logger import log


def print_security_group_instructions(instance_id: str, instance_ip: str):
    """Print instructions for configuring Lambda Cloud security group."""
    print("=" * 70)
    print("Lambda Cloud Security Group Configuration Guide")
    print("=" * 70)
    print()
    print(f"Instance ID: {instance_id}")
    print(f"Instance IP: {instance_ip}")
    print(f"Port to open: 8000 (TCP)")
    print()
    print("=" * 70)
    print("HOW TO CONFIGURE SECURITY GROUP")
    print("=" * 70)
    print()
    print("Lambda Cloud uses security groups to control inbound traffic.")
    print("By default, only SSH (port 22) is open.")
    print()
    print("Steps:")
    print()
    print("1. Go to Lambda Cloud Dashboard:")
    print("   https://cloud.lambda.ai/instances")
    print()
    print("2. Find your instance:")
    print(f"   - Look for instance ID: {instance_id}")
    print(f"   - Or IP address: {instance_ip}")
    print()
    print("3. Click on the instance to view details")
    print()
    print("4. Look for 'Security Group' or 'Firewall' settings")
    print("   (Lambda Cloud may use AWS security groups)")
    print()
    print("5. Add inbound rule:")
    print("   - Type: Custom TCP")
    print("   - Port: 8000")
    print("   - Source: Your IP address (recommended)")
    print("     OR: 0.0.0.0/0 (allow from anywhere - for testing only)")
    print("   - Description: vLLM API endpoint")
    print()
    print("6. Save the rule")
    print()
    print("7. Wait 1-2 minutes for changes to propagate")
    print()
    print("=" * 70)
    print("ALTERNATIVE: Use SSH Tunnel (No security group changes needed)")
    print("=" * 70)
    print()
    print("If you can't modify security groups, use SSH tunnel:")
    print()
    print("  python scripts/ssh_tunnel_helper.py --ip {} --key moses.pem".format(instance_ip))
    print()
    print("Then use this endpoint in the dashboard:")
    print("  http://localhost:8000/v1/chat/completions")
    print()
    print("=" * 70)
    print("TESTING CONNECTIVITY")
    print("=" * 70)
    print()
    print("After configuring, test connectivity:")
    print()
    print("  python scripts/check_connectivity.py --instance-id {}".format(instance_id))
    print()
    print("=" * 70)


async def main():
    """Main function."""
    import asyncio
    import json
    
    # Try to get instance from deployments file
    deployments_path = Path("data/lambda_deployments.json")
    instance_id = None
    instance_ip = None
    
    if deployments_path.exists():
        try:
            with open(deployments_path, 'r') as f:
                config = json.load(f)
                deployed = config.get("deployed_models", {})
                if deployed:
                    first_model = list(deployed.keys())[0]
                    model_config = deployed[first_model]
                    instance_id = model_config.get("instance_id")
                    instance_ip = model_config.get("instance_ip")
        except Exception as e:
            log.debug(f"Error loading deployments: {e}")
    
    # If not found, try to get from API
    if not instance_id:
        lambda_client = LambdaCloudClient()
        instances = await lambda_client.list_instances()
        if instances:
            instance_id = instances[0].get("id")
            instance_ip = instances[0].get("ip")
    
    if not instance_id:
        print("[ERROR] No instance found. Please provide instance ID or IP.")
        print("Usage: python scripts/configure_security_group.py")
        sys.exit(1)
    
    # If no IP, get it from API
    if not instance_ip:
        lambda_client = LambdaCloudClient()
        instance = await lambda_client.get_instance_status(instance_id)
        if instance:
            instance_ip = instance.get("ip")
    
    if not instance_ip:
        print(f"[ERROR] Could not get IP for instance {instance_id}")
        sys.exit(1)
    
    # Print instructions
    print_security_group_instructions(instance_id, instance_ip)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

