"""Quick script to check vLLM status."""

import subprocess
import sys

def check_vllm_status(instance_ip="150.136.146.143", ssh_key="moses.pem"):
    """Check if vLLM is running and ready."""
    print("Checking vLLM status...")
    print()
    
    # Check if process is running
    cmd = ['ssh', '-i', ssh_key, '-o', 'StrictHostKeyChecking=no',
           f'ubuntu@{instance_ip}', 'pgrep', '-f', 'vllm.entrypoints.openai.api_server']
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
    
    if result.returncode == 0:
        print(f"[OK] vLLM process is running (PID: {result.stdout.strip()})")
    else:
        print("[ERROR] vLLM process not found")
        return False
    
    print()
    
    # Check health endpoint
    cmd = ['ssh', '-i', ssh_key, '-o', 'StrictHostKeyChecking=no',
           f'ubuntu@{instance_ip}', 'curl', '-s', 'http://localhost:8000/health']
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
    
    if result.returncode == 0 and result.stdout.strip():
        print(f"[OK] Health endpoint responding: {result.stdout.strip()}")
    else:
        print("[WARNING] Health endpoint not responding (model may still be loading)")
    
    print()
    
    # Get last few log lines
    cmd = ['ssh', '-i', ssh_key, '-o', 'StrictHostKeyChecking=no',
           f'ubuntu@{instance_ip}', 'tail', '-5', '/tmp/vllm.log']
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
    
    if result.stdout:
        print("Recent log entries:")
        print("-" * 60)
        for line in result.stdout.strip().split('\n')[-5:]:
            # Clean ANSI codes
            clean_line = line.replace('\x1b[1;36m', '').replace('\x1b[0;0m', '')
            if any(x in clean_line for x in ['INFO', 'ERROR', 'WARNING', 'Uvicorn', 'model']):
                print(clean_line)
        print("-" * 60)
    
    return True

if __name__ == "__main__":
    check_vllm_status()

