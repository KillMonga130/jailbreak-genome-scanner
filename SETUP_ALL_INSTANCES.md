# Setup vLLM on All Lambda Instances

## Quick Start

### Option 1: PowerShell Script (Easiest)

```powershell
.\scripts\start_vllm_all.ps1
```

This will set up vLLM on all 3 instances automatically.

### Option 2: Python Script

```bash
python scripts/setup_all_instances.py
```

## Your Instances

The script will set up:

1. **Mistral 7B Instruct**
   - IP: `129.80.191.122`
   - Model: `mistralai/Mistral-7B-Instruct-v0.2`
   - Port: `8000`
   - SSH Tunnel: `localhost:8000`

2. **Qwen 7B Chat**
   - IP: `150.136.220.151`
   - Model: `Qwen/Qwen-7B-Chat`
   - Port: `8000`
   - SSH Tunnel: `localhost:8001`

3. **H100 (FOR THE HACKATHON)**
   - IP: `209.20.159.141`
   - Model: `mistralai/Mistral-7B-Instruct-v0.2`
   - Port: `8000`
   - SSH Tunnel: `localhost:8002`

## Advanced Usage

### Set up specific instances only

```bash
python scripts/setup_all_instances.py --instances Mistral_7B_Instruct Qwen_7B_Chat
```

### Force restart (even if vLLM is running)

```bash
python scripts/setup_all_instances.py --force
```

### List configured instances

```bash
python scripts/setup_all_instances.py --list
```

## What the Script Does

1. ✅ Checks if instances are accessible
2. ✅ Checks if vLLM is already running (skips if running)
3. ✅ Sets up virtual environment on each instance
4. ✅ Installs vLLM if needed
5. ✅ Starts vLLM server on port 8000
6. ✅ Verifies server is running

## After Setup

1. **Start SSH tunnels:**
   ```powershell
   .\scripts\setup_ssh_tunnels.ps1
   ```

2. **Test connections:**
   ```powershell
   curl http://localhost:8000/v1/models  # Mistral
   curl http://localhost:8001/v1/models  # Qwen
   curl http://localhost:8002/v1/models  # H100
   ```

3. **Use in dashboard:**
   - Defender: `http://localhost:8000/v1/chat/completions`
   - Attacker: `http://localhost:8001/v1/chat/completions`
   - Evaluator: `http://localhost:8001/v1/chat/completions`

## Troubleshooting

### "SSH connection failed"
- Check that instances are running in Lambda Cloud dashboard
- Verify SSH key path: `moses.pem`
- Test manually: `ssh -i moses.pem ubuntu@<instance_ip>`

### "vLLM already running"
- Use `--force` to restart: `python scripts/setup_all_instances.py --force`

### "Setup failed"
- Check instance logs: `ssh -i moses.pem ubuntu@<instance_ip> 'tail -f /tmp/vllm.log'`
- Verify instance has enough GPU memory for the model
- Check if port 8000 is already in use

### Instance not accessible
- Start instance in Lambda Cloud dashboard first
- Wait for status to show "active"
- Then run setup script

## Manual Setup (Alternative)

If the script fails, you can set up each instance manually:

```bash
# Mistral
python scripts/setup_vllm_on_lambda.py --ip 129.80.191.122 --key moses.pem --model mistralai/Mistral-7B-Instruct-v0.2

# Qwen
python scripts/setup_vllm_on_lambda.py --ip 150.136.220.151 --key moses.pem --model Qwen/Qwen-7B-Chat

# H100
python scripts/setup_vllm_on_lambda.py --ip 209.20.159.141 --key moses.pem --model mistralai/Mistral-7B-Instruct-v0.2
```

## Notes

- Setup takes 5-10 minutes per instance (depends on model download time)
- vLLM servers run in background (use `screen` or `tmux` on instance)
- Servers auto-restart on instance reboot (if configured)
- Check server status: `ssh -i moses.pem ubuntu@<ip> 'ps aux | grep vllm'`

