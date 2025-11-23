"""Quick status check - shows what's ready to use."""

import sys
import asyncio
import io
from pathlib import Path

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

async def main():
    print("\n" + "="*60)
    print("LAMBDA INSTANCES - READY TO USE")
    print("="*60 + "\n")
    
    client = LambdaCloudClient()
    instances = await client.list_instances()
    
    active = [i for i in instances if i.get('status') == 'active']
    
    if active:
        print(f"✅ Found {len(active)} active instance(s):\n")
        for i, inst in enumerate(active, 1):
            ip = inst.get('ip', 'N/A')
            instance_type = inst.get('instance_type', {})
            if isinstance(instance_type, dict):
                type_name = instance_type.get('name', 'N/A')
            else:
                type_name = instance_type
            
            endpoint = f"http://{ip}:8000/v1/chat/completions"
            print(f"{i}. {type_name}")
            print(f"   IP: {ip}")
            print(f"   Endpoint: {endpoint}")
            print()
    else:
        print("[WARNING] No active instances found")
    
    print("="*60)
    print("\n🚀 NEXT STEP: Start the dashboard!")
    print("   streamlit run dashboard/arena_dashboard.py")
    print("\n   Or double-click: quick_start.bat\n")

if __name__ == "__main__":
    asyncio.run(main())

