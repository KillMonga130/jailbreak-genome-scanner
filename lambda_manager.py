"""
Interactive Lambda Cloud Management Interface

Comprehensive tool for managing Lambda Cloud instances, models, and connectivity.
"""

import asyncio
import sys
import os
import json
from pathlib import Path
from typing import Optional, Dict, List, Any

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load config
from src.config import settings
from src.integrations.lambda_cloud import LambdaCloudClient
from scripts.check_connectivity import check_instance_connectivity
from scripts.setup_vllm_on_lambda import setup_vllm
from scripts.manage_lambda_models import (
    OPEN_SOURCE_MODELS, 
    switch_model, 
    check_status as check_model_status,
    list_models as list_available_models
)

# Available models for installation
MODELS = {
    "1": {"key": "phi-2", "name": "microsoft/phi-2", "desc": "Phi-2 (2.7B) - Small, fast, recommended for testing"},
    "2": {"key": "mistral-7b-instruct", "name": "mistralai/Mistral-7B-Instruct-v0.2", "desc": "Mistral 7B Instruct - High quality"},
    "3": {"key": "qwen-7b-chat", "name": "Qwen/Qwen-7B-Chat", "desc": "Qwen 7B Chat - Multilingual"},
    "4": {"key": "falcon-7b-instruct", "name": "tiiuae/falcon-7b-instruct", "desc": "Falcon 7B Instruct"},
}


class LambdaManager:
    """Interactive Lambda Cloud management interface."""
    
    def __init__(self):
        """Initialize the manager."""
        self.client = None
        self.current_instance = None
        self.ssh_key = "moses.pem"  # Default SSH key
        self._init_client()
    
    def _init_client(self):
        """Initialize Lambda Cloud client."""
        api_key = settings.lambda_api_key or os.getenv("LAMBDA_API_KEY")
        if not api_key:
            print("\n[ERROR] Lambda API Key not configured!")
            print("\nPlease set up your API key:")
            print("1. Create .env file in project root")
            print("2. Add: LAMBDA_API_KEY=secret_your_id.your_token")
            print("\nOr set environment variable:")
            print("   Windows: $env:LAMBDA_API_KEY='your_key'")
            print("   Linux/Mac: export LAMBDA_API_KEY='your_key'")
            sys.exit(1)
        
        self.client = LambdaCloudClient(api_key=api_key)
        print("[OK] Lambda Cloud client initialized")
    
    async def get_instances(self) -> List[Dict[str, Any]]:
        """Get all instances."""
        return await self.client.list_instances()
    
    async def show_main_menu(self):
        """Display main menu."""
        while True:
            instances = await self.get_instances()
            active_instances = [i for i in instances if i.get('status') == 'active']
            booting_instances = [i for i in instances if i.get('status') == 'booting']
            
            print("\n" + "=" * 70)
            print("LAMBDA CLOUD MANAGEMENT INTERFACE")
            print("=" * 70)
            print(f"\nActive Instances: {len(active_instances)}")
            print(f"Booting Instances: {len(booting_instances)}")
            print(f"Total Instances: {len(instances)}")
            
            if instances:
                print("\nCurrent Instances:")
                for i, inst in enumerate(instances, 1):
                    status = inst.get('status', 'unknown')
                    ip = inst.get('ip', 'N/A')
                    instance_type = inst.get('instance_type', {})
                    if isinstance(instance_type, dict):
                        type_name = instance_type.get('name', 'N/A')
                    else:
                        type_name = instance_type
                    
                    status_icon = "[OK]" if status == "active" else "[WAIT]" if status == "booting" else "[!]"
                    print(f"  {i}. {status_icon} {inst.get('id', 'N/A')[:20]}... - {type_name} - {ip} - {status}")
            
            print("\n" + "-" * 70)
            print("MAIN MENU")
            print("-" * 70)
            print("1. Instance Management")
            print("   - View instances, launch, terminate, check status")
            print("2. Model Management")
            print("   - Install models, switch models, check model status")
            print("3. Connectivity Testing")
            print("   - Test SSH, API ports, endpoints")
            print("4. Setup & Configuration")
            print("   - Setup vLLM, configure SSH, setup environment")
            print("5. View Instance Details")
            print("   - Get detailed information about instances")
            print("6. Quick Setup (All-in-One)")
            print("   - Complete setup: install model + test connectivity")
            print("0. Exit")
            
            choice = input("\nSelect option (0-6): ").strip()
            
            if choice == "1":
                await self.instance_management_menu()
            elif choice == "2":
                await self.model_management_menu()
            elif choice == "3":
                await self.connectivity_menu()
            elif choice == "4":
                await self.setup_menu()
            elif choice == "5":
                await self.view_instance_details()
            elif choice == "6":
                await self.quick_setup()
            elif choice == "0":
                print("\nExiting...")
                break
            else:
                print("\n[ERROR] Invalid option. Please try again.")
    
    async def instance_management_menu(self):
        """Instance management submenu."""
        while True:
            instances = await self.get_instances()
            
            print("\n" + "=" * 70)
            print("INSTANCE MANAGEMENT")
            print("=" * 70)
            
            if instances:
                print("\nCurrent Instances:")
                for i, inst in enumerate(instances, 1):
                    status = inst.get('status', 'unknown')
                    ip = inst.get('ip', 'N/A')
                    instance_id = inst.get('id', 'N/A')
                    print(f"  {i}. [{status}] {instance_id[:20]}... - {ip}")
            
            print("\n" + "-" * 70)
            print("1. View All Instances (Detailed)")
            print("2. Launch New Instance")
            print("3. Terminate Instance")
            print("4. Check Instance Status")
            print("5. Select Instance for Operations")
            print("0. Back to Main Menu")
            
            choice = input("\nSelect option (0-5): ").strip()
            
            if choice == "1":
                await self.view_all_instances()
            elif choice == "2":
                await self.launch_instance()
            elif choice == "3":
                await self.terminate_instance(instances)
            elif choice == "4":
                await self.check_instance_status(instances)
            elif choice == "5":
                await self.select_instance(instances)
            elif choice == "0":
                break
            else:
                print("\n[ERROR] Invalid option.")
    
    async def view_all_instances(self):
        """View detailed information about all instances."""
        instances = await self.get_instances()
        
        print("\n" + "=" * 70)
        print("ALL INSTANCES (DETAILED)")
        print("=" * 70)
        
        if not instances:
            print("\n[INFO] No instances found.")
            return
        
        for i, inst in enumerate(instances, 1):
            print(f"\nInstance #{i}")
            print("-" * 70)
            print(f"  ID: {inst.get('id', 'N/A')}")
            print(f"  IP: {inst.get('ip', 'N/A')}")
            print(f"  Status: {inst.get('status', 'N/A')}")
            
            instance_type = inst.get('instance_type', {})
            if isinstance(instance_type, dict):
                type_name = instance_type.get('name', 'N/A')
            else:
                type_name = instance_type
            print(f"  Type: {type_name}")
            
            region = inst.get('region', {})
            if isinstance(region, dict):
                region_name = region.get('name', 'N/A')
            else:
                region_name = region
            print(f"  Region: {region_name}")
            
            ssh_keys = inst.get('ssh_key_names', [])
            ssh_key = ssh_keys[0] if ssh_keys else 'N/A'
            print(f"  SSH Key: {ssh_key}")
            
            if inst.get('ip') and inst.get('status') == 'active':
                print(f"  API Endpoint: http://{inst.get('ip')}:8000/v1/chat/completions")
        
        input("\nPress Enter to continue...")
    
    async def launch_instance(self):
        """Launch a new instance."""
        print("\n" + "=" * 70)
        print("LAUNCH NEW INSTANCE")
        print("=" * 70)
        print("\n⚠️  WARNING: This will create charges!")
        print("\nRecommended instance types:")
        print("  1. gpu_1x_a10 - $0.75/hr (Testing)")
        print("  2. gpu_1x_a100 - $1.29/hr (Better quality)")
        print("  3. gpu_1x_h100 - $3.29/hr (Large models)")
        
        confirm = input("\nContinue? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Cancelled.")
            return
        
        instance_type = input("\nInstance type (e.g., gpu_1x_a10): ").strip()
        if not instance_type:
            print("[ERROR] Instance type required")
            return
        
        region = input("Region (default: us-west-3): ").strip() or "us-west-3"
        
        print(f"\nLaunching {instance_type} in {region}...")
        
        try:
            instance_data = await self.client.launch_instance(
                instance_type=instance_type,
                region=region,
                quantity=1
            )
            
            if instance_data and instance_data.get("instance_ids"):
                instance_id = instance_data["instance_ids"][0]
                print(f"\n[OK] Instance launched: {instance_id}")
                print("\nWaiting for instance to be active (this may take 2-5 minutes)...")
                print("You can check status from the main menu.")
            else:
                print("\n[ERROR] Failed to launch instance")
                print(f"Response: {instance_data}")
        except Exception as e:
            print(f"\n[ERROR] Error launching instance: {e}")
        
        input("\nPress Enter to continue...")
    
    async def terminate_instance(self, instances: List[Dict]):
        """Terminate an instance."""
        if not instances:
            print("\n[INFO] No instances to terminate.")
            return
        
        print("\n" + "=" * 70)
        print("TERMINATE INSTANCE")
        print("=" * 70)
        print("\n⚠️  WARNING: This will terminate the instance and stop all charges!")
        print("\nAvailable instances:")
        
        for i, inst in enumerate(instances, 1):
            instance_id = inst.get('id', 'N/A')
            ip = inst.get('ip', 'N/A')
            status = inst.get('status', 'unknown')
            print(f"  {i}. {instance_id[:20]}... - {ip} - [{status}]")
        
        try:
            choice = int(input("\nSelect instance number to terminate (0 to cancel): ").strip())
            if choice == 0:
                return
            if choice < 1 or choice > len(instances):
                print("[ERROR] Invalid selection")
                return
            
            instance = instances[choice - 1]
            instance_id = instance.get('id')
            
            confirm = input(f"\n⚠️  Terminate instance {instance_id[:20]}...? (yes/no): ").strip().lower()
            if confirm != "yes":
                print("Cancelled.")
                return
            
            print(f"\nTerminating {instance_id}...")
            success = await self.client.terminate_instance(instance_id)
            
            if success:
                print("[OK] Instance terminated successfully!")
            else:
                print("[ERROR] Failed to terminate instance")
        except (ValueError, KeyError) as e:
            print(f"[ERROR] Invalid input: {e}")
        
        input("\nPress Enter to continue...")
    
    async def check_instance_status(self, instances: List[Dict]):
        """Check status of specific instance."""
        if not instances:
            print("\n[INFO] No instances found.")
            return
        
        print("\n" + "=" * 70)
        print("CHECK INSTANCE STATUS")
        print("=" * 70)
        
        for i, inst in enumerate(instances, 1):
            instance_id = inst.get('id', 'N/A')
            ip = inst.get('ip', 'N/A')
            status = inst.get('status', 'unknown')
            print(f"  {i}. {instance_id[:20]}... - {ip} - [{status}]")
        
        try:
            choice = int(input("\nSelect instance number (0 to cancel): ").strip())
            if choice == 0:
                return
            if choice < 1 or choice > len(instances):
                print("[ERROR] Invalid selection")
                return
            
            instance = instances[choice - 1]
            
            print(f"\nChecking status...")
            status = await self.client.get_instance_status(instance.get('id'))
            
            if status:
                print("\nInstance Details:")
                print(f"  ID: {status.get('id')}")
                print(f"  Status: {status.get('status')}")
                print(f"  IP: {status.get('ip', 'N/A')}")
                
                instance_type = status.get('instance_type', {})
                if isinstance(instance_type, dict):
                    print(f"  Type: {instance_type.get('name', 'N/A')}")
                else:
                    print(f"  Type: {instance_type}")
            else:
                print("\n[ERROR] Could not get instance status")
        except (ValueError, KeyError) as e:
            print(f"[ERROR] Invalid input: {e}")
        
        input("\nPress Enter to continue...")
    
    async def select_instance(self, instances: List[Dict]):
        """Select instance for operations."""
        if not instances:
            print("\n[INFO] No instances found.")
            return
        
        print("\n" + "=" * 70)
        print("SELECT INSTANCE")
        print("=" * 70)
        
        for i, inst in enumerate(instances, 1):
            instance_id = inst.get('id', 'N/A')
            ip = inst.get('ip', 'N/A')
            status = inst.get('status', 'unknown')
            print(f"  {i}. {instance_id[:20]}... - {ip} - [{status}]")
        
        try:
            choice = int(input("\nSelect instance number (0 to cancel): ").strip())
            if choice == 0:
                return
            if choice < 1 or choice > len(instances):
                print("[ERROR] Invalid selection")
                return
            
            self.current_instance = instances[choice - 1]
            ip = self.current_instance.get('ip')
            instance_id = self.current_instance.get('id')
            
            print(f"\n[OK] Selected instance:")
            print(f"  ID: {instance_id}")
            print(f"  IP: {ip}")
            print(f"  Status: {self.current_instance.get('status')}")
            print("\nThis instance will be used for subsequent operations.")
        except (ValueError, KeyError) as e:
            print(f"[ERROR] Invalid input: {e}")
        
        input("\nPress Enter to continue...")
    
    async def model_management_menu(self):
        """Model management submenu."""
        if not self.current_instance:
            print("\n[WARNING] No instance selected. Please select an instance first.")
            instances = await self.get_instances()
            if instances:
                await self.select_instance(instances)
                if not self.current_instance:
                    return
            else:
                print("\n[ERROR] No instances available.")
                return
        
        ip = self.current_instance.get('ip')
        if not ip:
            print("\n[ERROR] Instance has no IP address. It may still be booting.")
            return
        
        while True:
            print("\n" + "=" * 70)
            print("MODEL MANAGEMENT")
            print("=" * 70)
            print(f"\nCurrent Instance: {self.current_instance.get('id', 'N/A')[:20]}...")
            print(f"IP: {ip}")
            print(f"Status: {self.current_instance.get('status')}")
            
            print("\n" + "-" * 70)
            print("1. List Available Models")
            print("2. Install/Setup Model")
            print("3. Switch Model")
            print("4. Check Model Status")
            print("5. View Model Logs")
            print("0. Back to Main Menu")
            
            choice = input("\nSelect option (0-5): ").strip()
            
            if choice == "1":
                self.list_models()
            elif choice == "2":
                await self.install_model(ip)
            elif choice == "3":
                await self.switch_model_menu(ip)
            elif choice == "4":
                self.check_model_status(self.ssh_key, ip)
            elif choice == "5":
                self.view_model_logs(ip)
            elif choice == "0":
                break
            else:
                print("\n[ERROR] Invalid option.")
    
    def list_models(self):
        """List available models."""
        print("\n" + "=" * 70)
        print("AVAILABLE MODELS")
        print("=" * 70)
        
        for num, model_info in MODELS.items():
            print(f"\n{num}. {model_info['key']}")
            print(f"   Model: {model_info['name']}")
            print(f"   Description: {model_info['desc']}")
        
        input("\nPress Enter to continue...")
    
    async def install_model(self, ip: str):
        """Install/setup a model on the instance."""
        print("\n" + "=" * 70)
        print("INSTALL/SETUP MODEL")
        print("=" * 70)
        
        print("\nAvailable models:")
        for num, model_info in MODELS.items():
            print(f"  {num}. {model_info['key']} - {model_info['desc']}")
        
        choice = input("\nSelect model (0 to cancel): ").strip()
        if choice == "0" or choice not in MODELS:
            print("Cancelled.")
            return
        
        model_info = MODELS[choice]
        model_key = model_info['key']
        model_name = model_info['name']
        
        print(f"\nSelected: {model_key} ({model_name})")
        print("\nThis will:")
        print("  1. Set up vLLM virtual environment (if needed)")
        print("  2. Install vLLM server")
        print("  3. Start API server with the selected model")
        print("  4. Verify the server is running")
        
        confirm = input("\nContinue? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Cancelled.")
            return
        
        print(f"\nSetting up model on {ip}...")
        print("This may take 5-10 minutes (model needs to download)...")
        
        # Use the setup script
        try:
            success = setup_vllm(
                instance_ip=ip,
                ssh_key=self.ssh_key,
                model=model_name,
                use_venv=True
            )
            
            if success:
                print("\n" + "=" * 70)
                print("[SUCCESS] Model setup complete!")
                print("=" * 70)
                print(f"\nAPI Endpoint: http://{ip}:8000/v1/chat/completions")
                print("\nYou can now use this endpoint in your dashboard/application!")
            else:
                print("\n[ERROR] Model setup failed. Check logs for details.")
        except Exception as e:
            print(f"\n[ERROR] Error setting up model: {e}")
            import traceback
            traceback.print_exc()
        
        input("\nPress Enter to continue...")
    
    async def switch_model_menu(self, ip: str):
        """Switch to a different model."""
        print("\n" + "=" * 70)
        print("SWITCH MODEL")
        print("=" * 70)
        
        print("\nAvailable models:")
        for num, model_info in MODELS.items():
            print(f"  {num}. {model_info['key']} - {model_info['desc']}")
        
        choice = input("\nSelect model to switch to (0 to cancel): ").strip()
        if choice == "0" or choice not in MODELS:
            print("Cancelled.")
            return
        
        model_key = MODELS[choice]['key']
        
        print(f"\nSwitching to {model_key}...")
        print("This will stop the current model and start the new one.")
        
        confirm = input("\nContinue? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Cancelled.")
            return
        
        try:
            success = switch_model(model_key, self.ssh_key, ip)
            if success:
                print("\n[SUCCESS] Model switched successfully!")
            else:
                print("\n[ERROR] Model switch failed.")
        except Exception as e:
            print(f"\n[ERROR] Error switching model: {e}")
        
        input("\nPress Enter to continue...")
    
    def view_model_logs(self, ip: str):
        """View model logs."""
        print("\n" + "=" * 70)
        print("VIEW MODEL LOGS")
        print("=" * 70)
        print(f"\nInstance: {ip}")
        print("\nTo view logs, run:")
        print(f"  ssh -i {self.ssh_key} ubuntu@{ip} 'tail -f /tmp/vllm.log'")
        print("\nOr view last 50 lines:")
        print(f"  ssh -i {self.ssh_key} ubuntu@{ip} 'tail -50 /tmp/vllm.log'")
        
        input("\nPress Enter to continue...")
    
    async def connectivity_menu(self):
        """Connectivity testing menu."""
        if not self.current_instance:
            print("\n[WARNING] No instance selected. Please select an instance first.")
            instances = await self.get_instances()
            if instances:
                await self.select_instance(instances)
                if not self.current_instance:
                    return
            else:
                print("\n[ERROR] No instances available.")
                return
        
        ip = self.current_instance.get('ip')
        instance_id = self.current_instance.get('id')
        
        if not ip:
            print("\n[ERROR] Instance has no IP address.")
            return
        
        print("\n" + "=" * 70)
        print("CONNECTIVITY TESTING")
        print("=" * 70)
        print(f"\nInstance: {instance_id[:20]}...")
        print(f"IP: {ip}")
        
        print("\n" + "-" * 70)
        print("1. Full Connectivity Check")
        print("   - SSH, API port, endpoint")
        print("2. Test SSH Connection")
        print("3. Test API Port (8000)")
        print("4. Test API Endpoint")
        print("5. Setup SSH Tunnel (if port blocked)")
        print("0. Back to Main Menu")
        
        choice = input("\nSelect option (0-5): ").strip()
        
        if choice == "1":
            await self.full_connectivity_check(instance_id, ip)
        elif choice == "2":
            self.test_ssh(ip)
        elif choice == "3":
            await self.test_api_port(ip)
        elif choice == "4":
            await self.test_api_endpoint(ip)
        elif choice == "5":
            self.setup_ssh_tunnel(ip)
        elif choice == "0":
            return
        else:
            print("\n[ERROR] Invalid option.")
    
    async def full_connectivity_check(self, instance_id: str, ip: str):
        """Run full connectivity check."""
        print("\n" + "=" * 70)
        print("FULL CONNECTIVITY CHECK")
        print("=" * 70)
        
        print(f"\nTesting connectivity to {ip}...")
        print("This may take a minute...")
        
        success = await check_instance_connectivity(instance_id=instance_id, instance_ip=ip)
        
        if success:
            print("\n[SUCCESS] All connectivity checks passed!")
        else:
            print("\n[WARNING] Some connectivity checks failed.")
            print("See details above.")
        
        input("\nPress Enter to continue...")
    
    def test_ssh(self, ip: str):
        """Test SSH connection."""
        print("\n" + "=" * 70)
        print("TEST SSH CONNECTION")
        print("=" * 70)
        print(f"\nTesting SSH to {ip}...")
        print(f"\nSSH Command:")
        print(f"  ssh -i {self.ssh_key} ubuntu@{ip}")
        print("\nRun the command above manually to test SSH.")
        
        input("\nPress Enter to continue...")
    
    async def test_api_port(self, ip: str):
        """Test API port connectivity."""
        from scripts.ssh_tunnel_helper import check_port_connectivity
        
        print("\n" + "=" * 70)
        print("TEST API PORT (8000)")
        print("=" * 70)
        print(f"\nTesting port 8000 on {ip}...")
        
        accessible = check_port_connectivity(ip, 8000, timeout=5.0)
        
        if accessible:
            print("[OK] Port 8000 is accessible!")
        else:
            print("[ERROR] Port 8000 is NOT accessible")
            print("\nOptions:")
            print("  1. Use SSH tunnel (see option 5)")
            print("  2. Configure security group in Lambda Cloud dashboard")
            print("  3. Check if vLLM is running on the instance")
        
        input("\nPress Enter to continue...")
    
    async def test_api_endpoint(self, ip: str):
        """Test API endpoint."""
        from scripts.ssh_tunnel_helper import test_api_endpoint
        
        print("\n" + "=" * 70)
        print("TEST API ENDPOINT")
        print("=" * 70)
        
        endpoint = f"http://{ip}:8000/v1/chat/completions"
        print(f"\nTesting endpoint: {endpoint}")
        
        success, message = test_api_endpoint(endpoint, timeout=10.0)
        
        if success:
            print(f"[OK] {message}")
        else:
            print(f"[ERROR] {message}")
        
        input("\nPress Enter to continue...")
    
    def setup_ssh_tunnel(self, ip: str):
        """Show SSH tunnel setup instructions."""
        print("\n" + "=" * 70)
        print("SSH TUNNEL SETUP")
        print("=" * 70)
        print(f"\nIf port 8000 is blocked, use SSH tunnel:")
        print(f"\nCommand:")
        print(f"  python scripts/ssh_tunnel_helper.py --ip {ip} --key {self.ssh_key}")
        print(f"\nOr use batch file (Windows):")
        print(f"  scripts\\start_ssh_tunnel.bat")
        print(f"\nThen use endpoint: http://localhost:8000/v1/chat/completions")
        
        input("\nPress Enter to continue...")
    
    async def setup_menu(self):
        """Setup and configuration menu."""
        if not self.current_instance:
            print("\n[WARNING] No instance selected. Please select an instance first.")
            instances = await self.get_instances()
            if instances:
                await self.select_instance(instances)
                if not self.current_instance:
                    return
            else:
                print("\n[ERROR] No instances available.")
                return
        
        ip = self.current_instance.get('ip')
        if not ip:
            print("\n[ERROR] Instance has no IP address.")
            return
        
        print("\n" + "=" * 70)
        print("SETUP & CONFIGURATION")
        print("=" * 70)
        print(f"\nInstance: {self.current_instance.get('id', 'N/A')[:20]}...")
        print(f"IP: {ip}")
        
        print("\n" + "-" * 70)
        print("1. Setup vLLM Environment")
        print("   - Install vLLM, create virtual environment")
        print("2. Configure SSH Key Path")
        print(f"   - Current: {self.ssh_key}")
        print("3. View Setup Instructions")
        print("0. Back to Main Menu")
        
        choice = input("\nSelect option (0-3): ").strip()
        
        if choice == "1":
            await self.setup_vllm_environment(ip)
        elif choice == "2":
            self.configure_ssh_key()
        elif choice == "3":
            self.view_setup_instructions(ip)
        elif choice == "0":
            return
        else:
            print("\n[ERROR] Invalid option.")
    
    async def setup_vllm_environment(self, ip: str):
        """Setup vLLM environment on instance."""
        print("\n" + "=" * 70)
        print("SETUP vLLM ENVIRONMENT")
        print("=" * 70)
        print(f"\nSetting up vLLM on {ip}...")
        print("This will:")
        print("  1. Create virtual environment")
        print("  2. Install vLLM")
        print("  3. Configure environment")
        
        confirm = input("\nContinue? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Cancelled.")
            return
        
        print("\nSetting up environment...")
        print("This may take 5-10 minutes...")
        
        # Use a simple model for initial setup
        success = setup_vllm(ip, self.ssh_key, "microsoft/phi-2", use_venv=True)
        
        if success:
            print("\n[SUCCESS] vLLM environment setup complete!")
        else:
            print("\n[ERROR] Setup failed. Check logs.")
        
        input("\nPress Enter to continue...")
    
    def configure_ssh_key(self):
        """Configure SSH key path."""
        print("\n" + "=" * 70)
        print("CONFIGURE SSH KEY")
        print("=" * 70)
        print(f"\nCurrent SSH key: {self.ssh_key}")
        
        new_key = input("\nEnter new SSH key path (or press Enter to keep current): ").strip()
        
        if new_key:
            key_path = Path(new_key)
            if key_path.exists():
                self.ssh_key = new_key
                print(f"\n[OK] SSH key updated to: {self.ssh_key}")
            else:
                print(f"\n[ERROR] File not found: {new_key}")
        else:
            print("\nSSH key unchanged.")
        
        input("\nPress Enter to continue...")
    
    def view_setup_instructions(self, ip: str):
        """View setup instructions."""
        print("\n" + "=" * 70)
        print("SETUP INSTRUCTIONS")
        print("=" * 70)
        print(f"\nFor instance: {ip}")
        print("\n1. SSH into instance:")
        print(f"   ssh -i {self.ssh_key} ubuntu@{ip}")
        print("\n2. Install vLLM:")
        print("   pip3 install vllm --upgrade")
        print("\n3. Start API server:")
        print("   python3 -m vllm.entrypoints.openai.api_server \\")
        print("       --model microsoft/phi-2 \\")
        print("       --port 8000 \\")
        print("       --host 0.0.0.0")
        print("\n4. API endpoint will be:")
        print(f"   http://{ip}:8000/v1/chat/completions")
        
        input("\nPress Enter to continue...")
    
    async def view_instance_details(self):
        """View detailed instance information."""
        instances = await self.get_instances()
        
        if not instances:
            print("\n[INFO] No instances found.")
            return
        
        print("\n" + "=" * 70)
        print("INSTANCE DETAILS")
        print("=" * 70)
        
        for i, inst in enumerate(instances, 1):
            print(f"\nInstance #{i}")
            print("-" * 70)
            print(f"  ID: {inst.get('id', 'N/A')}")
            print(f"  IP: {inst.get('ip', 'N/A')}")
            print(f"  Status: {inst.get('status', 'N/A')}")
            
            instance_type = inst.get('instance_type', {})
            if isinstance(instance_type, dict):
                print(f"  Type: {instance_type.get('name', 'N/A')}")
            else:
                print(f"  Type: {instance_type}")
            
            region = inst.get('region', {})
            if isinstance(region, dict):
                print(f"  Region: {region.get('name', 'N/A')}")
            else:
                print(f"  Region: {region}")
            
            ssh_keys = inst.get('ssh_key_names', [])
            ssh_key = ssh_keys[0] if ssh_keys else 'N/A'
            print(f"  SSH Key: {ssh_key}")
            
            if inst.get('ip') and inst.get('status') == 'active':
                print(f"  API Endpoint: http://{inst.get('ip')}:8000/v1/chat/completions")
                ssh_cmd = self.client.get_ssh_command(inst)
                if ssh_cmd:
                    print(f"  SSH Command: {ssh_cmd}")
        
        input("\nPress Enter to continue...")
    
    async def quick_setup(self):
        """Complete setup: install model + test connectivity."""
        if not self.current_instance:
            print("\n[WARNING] No instance selected. Please select an instance first.")
            instances = await self.get_instances()
            if instances:
                await self.select_instance(instances)
                if not self.current_instance:
                    return
            else:
                print("\n[ERROR] No instances available.")
                return
        
        ip = self.current_instance.get('ip')
        instance_id = self.current_instance.get('id')
        
        if not ip:
            print("\n[ERROR] Instance has no IP address.")
            return
        
        status = self.current_instance.get('status')
        if status != 'active':
            print(f"\n[ERROR] Instance is not active (status: {status})")
            print("Please wait for instance to be active first.")
            return
        
        print("\n" + "=" * 70)
        print("QUICK SETUP (ALL-IN-ONE)")
        print("=" * 70)
        print(f"\nThis will:")
        print("  1. Select a model to install")
        print("  2. Set up vLLM and install the model")
        print("  3. Test connectivity")
        print("  4. Provide you with the API endpoint")
        
        print("\nAvailable models:")
        for num, model_info in MODELS.items():
            print(f"  {num}. {model_info['key']} - {model_info['desc']}")
        
        choice = input("\nSelect model (0 to cancel): ").strip()
        if choice == "0" or choice not in MODELS:
            print("Cancelled.")
            return
        
        model_info = MODELS[choice]
        model_name = model_info['name']
        
        print(f"\nStarting setup for {model_info['key']}...")
        print("This may take 5-10 minutes...")
        
        # Step 1: Install model
        print("\n[Step 1/3] Installing model...")
        success = setup_vllm(ip, self.ssh_key, model_name, use_venv=True)
        
        if not success:
            print("\n[ERROR] Model installation failed. Stopping.")
            input("\nPress Enter to continue...")
            return
        
        # Step 2: Test connectivity
        print("\n[Step 2/3] Testing connectivity...")
        await asyncio.sleep(5)  # Give server time to start
        
        connectivity_success = await check_instance_connectivity(instance_id=instance_id, instance_ip=ip)
        
        # Step 3: Show results
        print("\n" + "=" * 70)
        print("[Step 3/3] SETUP COMPLETE!")
        print("=" * 70)
        
        endpoint = f"http://{ip}:8000/v1/chat/completions"
        print(f"\nAPI Endpoint: {endpoint}")
        
        if connectivity_success:
            print("\n[OK] Connectivity: All checks passed!")
        else:
            print("\n[WARNING] Connectivity: Some checks failed")
            print("You may need to use SSH tunnel or configure security groups")
        
        print("\nYou can now use this endpoint in:")
        print("  - Dashboard")
        print("  - Code (LLMDefender)")
        print("  - API calls")
        
        input("\nPress Enter to continue...")


async def main():
    """Main entry point."""
    print("\n" + "=" * 70)
    print("LAMBDA CLOUD MANAGEMENT INTERFACE")
    print("=" * 70)
    print("\nInitializing...")
    
    manager = LambdaManager()
    await manager.show_main_menu()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)

