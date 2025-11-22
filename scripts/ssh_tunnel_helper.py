"""SSH Tunnel Helper for Lambda Cloud API endpoints."""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path
from typing import Optional


class SSHTunnel:
    """Manages SSH tunnel for Lambda Cloud API endpoint access."""
    
    def __init__(self, instance_ip: str, ssh_key: str, local_port: int = 8000, remote_port: int = 8000):
        """
        Initialize SSH tunnel.
        
        Args:
            instance_ip: Lambda instance IP address
            ssh_key: Path to SSH private key
            local_port: Local port to forward to
            remote_port: Remote port on instance
        """
        self.instance_ip = instance_ip
        self.ssh_key = Path(ssh_key)
        self.local_port = local_port
        self.remote_port = remote_port
        self.process = None
        self.endpoint = f"http://localhost:{local_port}/v1/completions"
        
        if not self.ssh_key.exists():
            raise FileNotFoundError(f"SSH key not found: {ssh_key}")
    
    def start(self) -> bool:
        """
        Start SSH tunnel in background.
        
        Returns:
            True if tunnel started successfully
        """
        if self.is_running():
            print(f"[INFO] SSH tunnel already running on port {self.local_port}")
            return True
        
        ssh_cmd = [
            'ssh',
            '-i', str(self.ssh_key),
            '-N',  # No remote command
            '-L', f'{self.local_port}:localhost:{self.remote_port}',  # Local forwarding
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', 'ExitOnForwardFailure=yes',
            f'ubuntu@{self.instance_ip}'
        ]
        
        try:
            # Start SSH tunnel in background
            if sys.platform == 'win32':
                # Windows: use CREATE_NO_WINDOW flag
                import subprocess as sp
                self.process = sp.Popen(
                    ssh_cmd,
                    stdout=sp.PIPE,
                    stderr=sp.PIPE,
                    creationflags=sp.CREATE_NO_WINDOW
                )
            else:
                # Unix: normal background process
                self.process = subprocess.Popen(
                    ssh_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            # Wait a moment to check if it started successfully
            time.sleep(2)
            
            if self.process.poll() is None:
                print(f"[OK] SSH tunnel started: localhost:{self.local_port} -> {self.instance_ip}:{self.remote_port}")
                print(f"[INFO] Use endpoint: {self.endpoint}")
                return True
            else:
                stdout, stderr = self.process.communicate()
                error_msg = stderr.decode() if stderr else "Unknown error"
                print(f"[ERROR] SSH tunnel failed to start: {error_msg}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Error starting SSH tunnel: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop SSH tunnel."""
        if self.process and self.process.poll() is None:
            try:
                if sys.platform == 'win32':
                    self.process.terminate()
                else:
                    os.kill(self.process.pid, signal.SIGTERM)
                self.process.wait(timeout=5)
                print(f"[OK] SSH tunnel stopped")
                return True
            except Exception as e:
                print(f"[ERROR] Error stopping tunnel: {e}")
                try:
                    self.process.kill()
                except:
                    pass
                return False
        return True
    
    def is_running(self) -> bool:
        """Check if tunnel process is running."""
        if self.process:
            return self.process.poll() is None
        return False
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


def check_port_connectivity(host: str, port: int, timeout: float = 5.0) -> bool:
    """
    Check if a port is accessible.
    
    Args:
        host: Host IP address
        port: Port number
        timeout: Connection timeout in seconds
        
    Returns:
        True if port is accessible
    """
    import socket
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def test_api_endpoint(endpoint: str, timeout: float = 10.0):
    """
    Test if API endpoint is accessible.
    
    Args:
        endpoint: API endpoint URL
        timeout: Request timeout in seconds
        
    Returns:
        Tuple of (success, message)
    """
    try:
        import httpx
        
        # Normalize endpoint
        if not endpoint.startswith('http'):
            endpoint = f"http://{endpoint}"
        
        # Extract host and port from endpoint
        from urllib.parse import urlparse
        parsed = urlparse(endpoint)
        host = parsed.hostname or 'localhost'
        port = parsed.port or 8000
        
        # Check port connectivity first
        print(f"Checking port connectivity: {host}:{port}...")
        if not check_port_connectivity(host, port, timeout=5.0):
            return False, f"Cannot connect to {host}:{port} - port appears to be blocked by firewall"
        
        # Try API request
        print(f"Testing API endpoint: {endpoint}...")
        with httpx.Client(timeout=timeout) as client:
            # First try health check endpoint
            try:
                health_url = endpoint.replace("/v1/chat/completions", "/health").replace("/v1/completions", "/health")
                if "/health" not in health_url and "/v1/" in health_url:
                    base_url = endpoint.split("/v1/")[0]
                    health_url = f"{base_url}/health"
                health_response = client.get(health_url, timeout=5.0)
                if health_response.status_code == 200:
                    return True, "API endpoint is accessible and vLLM server is running"
            except:
                pass  # Health endpoint may not exist, try main endpoint
            
            # Determine endpoint format and try appropriate payload
            use_chat = "/chat/completions" in endpoint.lower()
            
            # Try API request - use completions format per Lambda Cloud docs
            if use_chat:
                payload = {
                    "model": "microsoft/phi-2",
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 10
                }
            else:
                # Use completions format (per Lambda Cloud documentation)
                payload = {
                    "model": "microsoft/phi-2",
                    "prompt": "test",
                    "max_tokens": 10
                }
            
            response = client.post(endpoint, json=payload)
            
            if response.status_code == 200:
                # Check response format
                data = response.json()
                if "choices" in data:
                    return True, "API endpoint is accessible and responding correctly"
                else:
                    return True, f"API endpoint is accessible (unexpected response format: {list(data.keys())[:3]})"
            elif response.status_code in [404, 405]:
                # 404/405 means server responded but endpoint/method not found - connection is working!
                # Try alternative format
                if not use_chat:
                    # Try chat/completions as fallback
                    try:
                        alt_url = endpoint.replace("/v1/completions", "/v1/chat/completions")
                        if alt_url == endpoint:
                            alt_url = f"{endpoint.split('/v1/')[0]}/v1/chat/completions"
                        alt_payload = {
                            "model": "microsoft/phi-2",
                            "messages": [{"role": "user", "content": "test"}],
                            "max_tokens": 10
                        }
                        alt_response = client.post(alt_url, json=alt_payload, timeout=timeout)
                        if alt_response.status_code == 200:
                            return True, f"API endpoint is accessible (using chat/completions format)"
                    except:
                        pass
                
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                error_msg = error_data.get("error", {}).get("message", response.text[:100]) if error_data else response.text[:100]
                return False, f"Method/endpoint not allowed ({response.status_code}): {error_msg}"
            else:
                # Any other response means server is reachable
                return True, f"API endpoint is accessible (status {response.status_code} - server is responding)"
                
    except httpx.ConnectTimeout:
        return False, f"Connection timeout - firewall may be blocking port {port}"
    except httpx.ConnectError as e:
        return False, f"Connection error: {str(e)}"
    except Exception as e:
        return False, f"Error testing endpoint: {str(e)}"


def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="SSH Tunnel Helper for Lambda Cloud")
    parser.add_argument("--ip", required=True, help="Lambda instance IP address")
    parser.add_argument("--key", default="moses.pem", help="SSH key file path")
    parser.add_argument("--local-port", type=int, default=8000, help="Local port (default: 8000)")
    parser.add_argument("--remote-port", type=int, default=8000, help="Remote port (default: 8000)")
    parser.add_argument("--test", action="store_true", help="Test connectivity without starting tunnel")
    parser.add_argument("--endpoint", help="Test specific endpoint URL")
    
    args = parser.parse_args()
    
    if args.test:
        # Test connectivity
        if args.endpoint:
            endpoint = args.endpoint
        else:
            endpoint = f"http://{args.ip}:{args.remote_port}/v1/completions"
        
        print(f"Testing connectivity to {args.ip}:{args.remote_port}...")
        success, message = test_api_endpoint(endpoint)
        
        if success:
            print(f"[OK] {message}")
            sys.exit(0)
        else:
            print(f"[ERROR] {message}")
            print(f"\n[Suggestion] Start SSH tunnel:")
            print(f"  python scripts/ssh_tunnel_helper.py --ip {args.ip} --key {args.key}")
            sys.exit(1)
    else:
        # Start SSH tunnel
        print(f"Starting SSH tunnel for {args.ip}...")
        tunnel = SSHTunnel(
            instance_ip=args.ip,
            ssh_key=args.key,
            local_port=args.local_port,
            remote_port=args.remote_port
        )
        
        if tunnel.start():
            print(f"\n[OK] SSH tunnel is running!")
            print(f"Endpoint: {tunnel.endpoint}")
            print(f"\nPress Ctrl+C to stop the tunnel...")
            
            try:
                # Keep tunnel running
                while True:
                    if not tunnel.is_running():
                        print("[WARNING] Tunnel process stopped unexpectedly")
                        break
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n[INFO] Stopping tunnel...")
                tunnel.stop()
                print("[OK] Tunnel stopped")
        else:
            print("[ERROR] Failed to start SSH tunnel")
            sys.exit(1)


if __name__ == "__main__":
    main()

