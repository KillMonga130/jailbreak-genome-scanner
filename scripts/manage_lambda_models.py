"""Comprehensive Lambda Cloud model management - deploy, switch, and manage multiple open source models."""

import subprocess
import sys
import json
import time
from pathlib import Path
from typing import Dict, Optional, List

# Non-gated open source models that work immediately (no Hugging Face auth needed)
OPEN_SOURCE_MODELS = {
    "phi-2": {
        "model_name": "microsoft/phi-2",
        "description": "Phi-2 - Small, fast, capable (2.7B)",
        "memory_gb": 5,
        "status": "recommended"
    },
    "mistral-7b-instruct": {
        "model_name": "mistralai/Mistral-7B-Instruct-v0.2",
        "description": "Mistral 7B Instruct - High quality responses",
        "memory_gb": 14,
        "status": "recommended"
    },
    "qwen-7b-chat": {
        "model_name": "Qwen/Qwen-7B-Chat",
        "description": "Qwen 7B Chat - Multilingual support",
        "memory_gb": 14,
        "status": "good"
    },
    "falcon-7b-instruct": {
        "model_name": "tiiuae/falcon-7b-instruct",
        "description": "Falcon 7B Instruct - Good for instructions",
        "memory_gb": 14,
        "status": "good"
    },
}


def load_deployments() -> dict:
    """Load deployment configuration."""
    config_path = Path("data/lambda_deployments.json")
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {"deployed_models": {}, "available_models": {}}


def save_deployments(config: dict):
    """Save deployment configuration."""
    config_path = Path("data/lambda_deployments.json")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)


def get_instance_info(ssh_key: str = "moses.pem", instance_ip: str = "150.136.146.143") -> Dict:
    """Get instance information from deployments file."""
    config = load_deployments()
    deployed = config.get("deployed_models", {})
    
    # Find active instance
    for key, model_info in deployed.items():
        if model_info.get("status") == "active" and model_info.get("instance_ip") == instance_ip:
            return {
                "instance_id": model_info.get("instance_id"),
                "instance_ip": instance_ip,
                "current_model": model_info.get("model_name"),
                "api_endpoint": model_info.get("api_endpoint", f"http://{instance_ip}:8000/v1/completions")
            }
    
    # Fallback: use provided IP
    return {
        "instance_id": None,
        "instance_ip": instance_ip,
        "current_model": None,
        "api_endpoint": f"http://{instance_ip}:8000/v1/completions"
    }


def stop_vllm(ssh_key: str, instance_ip: str) -> bool:
    """Stop running vLLM server."""
    print("Stopping existing vLLM server...")
    ssh_key_path = Path(ssh_key)
    
    cmd = ['ssh', '-i', str(ssh_key_path), '-o', 'StrictHostKeyChecking=no',
           f'ubuntu@{instance_ip}', 'pkill', '-f', 'vllm.entrypoints.openai.api_server']
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    time.sleep(2)
    return True


def start_vllm(ssh_key: str, instance_ip: str, model_name: str, wait_for_ready: bool = True) -> bool:
    """Start vLLM server with specified model."""
    print(f"Starting vLLM with model: {model_name}...")
    ssh_key_path = Path(ssh_key)
    
    # Ensure virtual environment exists
    check_venv_cmd = ['ssh', '-i', str(ssh_key_path), '-o', 'StrictHostKeyChecking=no',
                     f'ubuntu@{instance_ip}', 'test', '-d', '~/vllm_env']
    
    result = subprocess.run(check_venv_cmd, capture_output=True)
    if result.returncode != 0:
        print("[WARNING] Virtual environment not found. Setting up...")
        setup_venv(ssh_key, instance_ip)
    
    # Start vLLM
    start_cmd = ['ssh', '-i', str(ssh_key_path), '-o', 'StrictHostKeyChecking=no',
                f'ubuntu@{instance_ip}',
                'bash', '-c',
                f'source ~/vllm_env/bin/activate && '
                f'nohup python3 -m vllm.entrypoints.openai.api_server '
                f'--model {model_name} '
                f'--port 8000 '
                f'--host 0.0.0.0 '
                f'--disable-log-requests '
                f'> /tmp/vllm.log 2>&1 &']
    
    result = subprocess.run(start_cmd, capture_output=True, text=True, timeout=10)
    
    if result.returncode != 0:
        print(f"[ERROR] Failed to start vLLM: {result.stderr}")
        return False
    
    print("[OK] vLLM server started in background")
    
    if wait_for_ready:
        print("Waiting for model to load (this may take 2-5 minutes)...")
        print("Checking every 10 seconds...")
        
        for i in range(60):  # Check for up to 10 minutes
            time.sleep(10)
            
            # Check health endpoint
            health_cmd = ['ssh', '-i', str(ssh_key_path), '-o', 'StrictHostKeyChecking=no',
                         f'ubuntu@{instance_ip}', 'curl', '-s', 'http://localhost:8000/health']
            health_result = subprocess.run(health_cmd, capture_output=True, text=True, timeout=5)
            
            if health_result.returncode == 0 and health_result.stdout.strip():
                print(f"[OK] Model is ready! (took ~{i*10} seconds)")
                
                # Check if model loaded correctly
                check_log_cmd = ['ssh', '-i', str(ssh_key_path), '-o', 'StrictHostKeyChecking=no',
                               f'ubuntu@{instance_ip}', 'grep', '-i', '"Uvicorn running"', '/tmp/vllm.log']
                log_result = subprocess.run(check_log_cmd, capture_output=True, text=True, timeout=5)
                
                if log_result.returncode == 0:
                    return True
            
            # Check for critical errors only (gated repos, auth issues)
            error_cmd = ['ssh', '-i', str(ssh_key_path), '-o', 'StrictHostKeyChecking=no',
                        f'ubuntu@{instance_ip}', 'grep', '-iE', '(gated repo|access.*restricted|401|403|authentication)', '/tmp/vllm.log | tail -5']
            error_result = subprocess.run(error_cmd, shell=True, capture_output=True, text=True, timeout=5)
            
            if error_result.stdout and any(x in error_result.stdout.lower() for x in ['gated', 'restricted', '401', '403', 'authentication']):
                print(f"[ERROR] Model access issue detected. Check logs:")
                print(f"        ssh -i {ssh_key} ubuntu@{instance_ip} 'tail -20 /tmp/vllm.log'")
                print(f"        Error: {error_result.stdout[:200]}")
                return False
            
            if i % 6 == 0:  # Print every minute
                print(f"       Still loading... ({i*10}s)")
        
        print("[WARNING] Model may still be loading. Check logs if needed.")
    
    return True


def setup_venv(ssh_key: str, instance_ip: str) -> bool:
    """Set up vLLM virtual environment on instance."""
    print("Setting up vLLM virtual environment...")
    
    # Upload and run setup script
    script_path = Path(__file__).parent / "setup_vllm_venv.sh"
    if not script_path.exists():
        print("[ERROR] setup_vllm_venv.sh not found")
        return False
    
    ssh_key_path = Path(ssh_key)
    
    # Upload script
    upload_cmd = ['scp', '-i', str(ssh_key_path), '-o', 'StrictHostKeyChecking=no',
                 str(script_path), f'ubuntu@{instance_ip}:/tmp/setup_vllm_venv.sh']
    
    result = subprocess.run(upload_cmd, capture_output=True, timeout=30)
    if result.returncode != 0:
        print(f"[ERROR] Failed to upload setup script: {result.stderr}")
        return False
    
    # Make executable and run
    run_cmd = ['ssh', '-i', str(ssh_key_path), '-o', 'StrictHostKeyChecking=no',
              f'ubuntu@{instance_ip}',
              'bash', '-c', 'chmod +x /tmp/setup_vllm_venv.sh && /tmp/setup_vllm_venv.sh dummy']
    
    result = subprocess.run(run_cmd, capture_output=True, text=True, timeout=600)  # 10 min timeout
    
    if result.returncode != 0:
        print(f"[ERROR] Setup script failed: {result.stderr}")
        return False
    
    print("[OK] Virtual environment setup complete")
    return True


def switch_model(model_key: str, ssh_key: str = "moses.pem", instance_ip: str = "150.136.146.143") -> bool:
    """Switch to a different model."""
    if model_key not in OPEN_SOURCE_MODELS:
        print(f"[ERROR] Model '{model_key}' not found in available models")
        print("\nAvailable models:")
        for key, info in OPEN_SOURCE_MODELS.items():
            print(f"  - {key}: {info['description']}")
        return False
    
    model_info = OPEN_SOURCE_MODELS[model_key]
    model_name = model_info["model_name"]
    
    print("=" * 70)
    print("LAMBDA CLOUD MODEL SWITCH")
    print("=" * 70)
    print(f"Instance: {instance_ip}")
    print(f"Switching to: {model_name}")
    print(f"Description: {model_info['description']}")
    print()
    
    # Stop existing server
    stop_vllm(ssh_key, instance_ip)
    
    # Start new model
    success = start_vllm(ssh_key, instance_ip, model_name, wait_for_ready=True)
    
    if success:
        # Update deployment config
        instance_info = get_instance_info(ssh_key, instance_ip)
        config = load_deployments()
        
        if "deployed_models" not in config:
            config["deployed_models"] = {}
        
        config["deployed_models"][model_key] = {
            "instance_id": instance_info.get("instance_id"),
            "model_name": model_name,
            "instance_type": "gpu_1x_a10",
            "status": "active",
            "instance_ip": instance_ip,
            "api_endpoint": f"http://{instance_ip}:8000/v1/completions"
        }
        
        save_deployments(config)
        
        print()
        print("=" * 70)
        print("[SUCCESS] Model switch complete!")
        print("=" * 70)
        print(f"Model: {model_name}")
        print(f"Endpoint: http://{instance_ip}:8000/v1/completions")
        print(f"        (or http://localhost:8000/v1/completions with SSH tunnel)")
        print()
        print("Use this in your dashboard/application!")
        return True
    else:
        print("[ERROR] Model switch failed. Check logs for details.")
        return False


def list_models():
    """List available models."""
    print("=" * 70)
    print("AVAILABLE OPEN SOURCE MODELS (No Authentication Required)")
    print("=" * 70)
    print()
    
    for key, info in OPEN_SOURCE_MODELS.items():
        status_icon = "[RECOMMENDED]" if info.get("status") == "recommended" else "           "
        print(f"{status_icon} {key:25s} - {info['description']}")
        print(f"   Model: {info['model_name']}")
        print(f"   Memory: ~{info['memory_gb']} GB")
        print()


def check_status(ssh_key: str = "moses.pem", instance_ip: str = "150.136.146.143"):
    """Check current model status."""
    print("=" * 70)
    print("MODEL STATUS CHECK")
    print("=" * 70)
    print(f"Instance: {instance_ip}")
    print()
    
    # Check if process is running
    ssh_key_path = Path(ssh_key)
    cmd = ['ssh', '-i', str(ssh_key_path), '-o', 'StrictHostKeyChecking=no',
           f'ubuntu@{instance_ip}', 'pgrep', '-f', 'vllm.entrypoints.openai.api_server']
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
    
    if result.returncode == 0:
        print(f"[OK] vLLM is running (PID: {result.stdout.strip()})")
    else:
        print("[ERROR] vLLM is NOT running")
        return
    
    # Check health
    health_cmd = ['ssh', '-i', str(ssh_key_path), '-o', 'StrictHostKeyChecking=no',
                 f'ubuntu@{instance_ip}', 'curl', '-s', 'http://localhost:8000/health']
    health_result = subprocess.run(health_cmd, capture_output=True, text=True, timeout=5)
    
    if health_result.returncode == 0:
        print(f"[OK] Health endpoint: {health_result.stdout.strip()}")
    else:
        print("[WARNING] Health endpoint not responding")
    
    # Get current model from deployments
    config = load_deployments()
    deployed = config.get("deployed_models", {})
    
    for key, info in deployed.items():
        if info.get("instance_ip") == instance_ip and info.get("status") == "active":
            print()
            print(f"Configured Model: {info.get('model_name')}")
            print(f"API Endpoint: {info.get('api_endpoint')}")
            break


def main():
    """Main CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage Lambda Cloud models")
    parser.add_argument("action", choices=["list", "switch", "status"],
                       help="Action to perform")
    parser.add_argument("--model", help="Model key (for switch action)")
    parser.add_argument("--ip", default="150.136.146.143", help="Instance IP")
    parser.add_argument("--key", default="moses.pem", help="SSH key file")
    
    args = parser.parse_args()
    
    if args.action == "list":
        list_models()
    elif args.action == "switch":
        if not args.model:
            print("[ERROR] --model required for switch action")
            print("\nAvailable models:")
            for key in OPEN_SOURCE_MODELS.keys():
                print(f"  - {key}")
            sys.exit(1)
        success = switch_model(args.model, args.key, args.ip)
        sys.exit(0 if success else 1)
    elif args.action == "status":
        check_status(args.key, args.ip)


if __name__ == "__main__":
    main()

