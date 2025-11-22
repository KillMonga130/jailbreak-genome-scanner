"""Switch the model running on Lambda Cloud instance."""

import subprocess
import sys
import time
import json
from pathlib import Path

def switch_vllm_model(instance_ip="150.136.146.143", ssh_key="moses.pem", new_model="meta-llama/Llama-2-7b-chat-hf"):
    """Switch vLLM to a new model on the Lambda instance."""
    
    ssh_key_path = Path(ssh_key)
    if not ssh_key_path.exists():
        print(f"[ERROR] SSH key not found: {ssh_key}")
        return False
    
    print("=" * 60)
    print("Switching vLLM Model")
    print("=" * 60)
    print(f"Instance: {instance_ip}")
    print(f"New Model: {new_model}")
    print()
    
    # Step 1: Stop existing vLLM
    print("Step 1: Stopping existing vLLM server...")
    stop_cmd = ['ssh', '-i', str(ssh_key_path), '-o', 'StrictHostKeyChecking=no',
                f'ubuntu@{instance_ip}', 'pkill', '-f', 'vllm.entrypoints.openai.api_server']
    
    result = subprocess.run(stop_cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print("[OK] Stopped existing vLLM server")
    else:
        print("[INFO] No running vLLM server found (this is OK)")
    
    print()
    time.sleep(2)  # Wait for process to fully stop
    
    # Step 2: Start vLLM with new model
    print(f"Step 2: Starting vLLM with {new_model}...")
    
    # Start in background using nohup
    start_cmd = ['ssh', '-i', str(ssh_key_path), '-o', 'StrictHostKeyChecking=no',
                 f'ubuntu@{instance_ip}',
                 'bash', '-c',
                 f'source ~/vllm_env/bin/activate && '
                 f'nohup python3 -m vllm.entrypoints.openai.api_server '
                 f'--model {new_model} '
                 f'--port 8000 '
                 f'--host 0.0.0.0 '
                 f'> /tmp/vllm.log 2>&1 &']
    
    result = subprocess.run(start_cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("[OK] Started vLLM server in background")
        print()
        print("Step 3: Waiting for model to load (this may take a few minutes)...")
        print("       You can check progress with:")
        print(f"       ssh -i {ssh_key} ubuntu@{instance_ip} 'tail -f /tmp/vllm.log'")
        print()
        
        # Wait a bit and check if server is responding
        for i in range(30):
            time.sleep(5)
            # Check health endpoint
            check_cmd = ['ssh', '-i', str(ssh_key_path), '-o', 'StrictHostKeyChecking=no',
                        f'ubuntu@{instance_ip}', 'curl', '-s', 'http://localhost:8000/health']
            check_result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=5)
            if check_result.returncode == 0 and check_result.stdout.strip():
                print(f"[OK] vLLM server is responding after ~{i*5} seconds")
                break
            print(f"       Waiting... ({i*5}s)")
        else:
            print("[WARNING] Server may still be loading. Check logs if needed.")
        
        print()
        print("=" * 60)
        print("[SUCCESS] Model switch complete!")
        print("=" * 60)
        print(f"Model: {new_model}")
        print(f"Endpoint: http://{instance_ip}:8000/v1/completions")
        print("(Use http://localhost:8000/v1/completions if using SSH tunnel)")
        return True
    else:
        print(f"[ERROR] Failed to start vLLM server")
        print(f"Error: {result.stderr}")
        return False


if __name__ == "__main__":
    import argparse
    import time
    
    parser = argparse.ArgumentParser(description="Switch vLLM model on Lambda instance")
    parser.add_argument("--ip", default="150.136.146.143", help="Instance IP address")
    parser.add_argument("--key", default="moses.pem", help="SSH key file")
    parser.add_argument("--model", default="meta-llama/Llama-2-7b-chat-hf", help="New model name")
    
    args = parser.parse_args()
    
    success = switch_vllm_model(args.ip, args.key, args.model)
    sys.exit(0 if success else 1)

