# Quick SSH Tunnel Setup for Your Lambda Instances

## Your Instances

Based on your Lambda Cloud dashboard:

1. **H100 Instance** (FOR THE HACKATHON)
   - IP: `209.20.159.141`
   - Region: us-west-3

2. **Mistral 7B** (mistralai)
   - IP: `129.80.191.122` ⚠️ **This is the one failing in your logs**
   - Region: us-east-1

3. **Qwen 7B** (qwen)
   - IP: `150.136.220.151`
   - Region: us-east-1

## Quick Setup (PowerShell)

### Option 1: Use the Helper Script

```powershell
# Run this in PowerShell
.\scripts\setup_ssh_tunnels.ps1
```

This will automatically set up tunnels for all instances.

### Option 2: Manual Setup (One Terminal Per Instance)

Open **3 separate PowerShell terminals** and run one command in each:

**Terminal 1 - Mistral (Port 8000):**
```powershell
ssh -N -L 8000:localhost:8000 ubuntu@129.80.191.122
```

**Terminal 2 - Qwen (Port 8001):**
```powershell
ssh -N -L 8001:localhost:8000 ubuntu@150.136.220.151
```

**Terminal 3 - H100 (Port 8002):**
```powershell
ssh -N -L 8002:localhost:8000 ubuntu@209.20.159.141
```

**Keep these terminals open!** The tunnels must stay running.

## Verify Tunnels Are Working

After starting tunnels, test them:

```powershell
# Test Mistral
curl http://localhost:8000/v1/models

# Test Qwen
curl http://localhost:8001/v1/models

# Test H100
curl http://localhost:8002/v1/models
```

If you see JSON responses, the tunnels are working! ✅

## Update Dashboard Configuration

Once tunnels are active, update your dashboard:

### Defender Setup
- **API Endpoint**: `http://localhost:8000/v1/chat/completions` (for Mistral)

### Attacker Setup (if using)
- **API Endpoint**: `http://localhost:8001/v1/chat/completions` (for Qwen)

### Evaluator Setup (if using)
- **API Endpoint**: `http://localhost:8001/v1/chat/completions` (for Qwen)

## Troubleshooting

### "Connection refused" or "All connection attempts failed"

1. **Check if vLLM is running on the instance:**
   ```powershell
   ssh ubuntu@129.80.191.122 "ps aux | grep vllm"
   ```

2. **If vLLM is not running, start it:**
   ```powershell
   ssh ubuntu@129.80.191.122
   # Then on the instance:
   source ~/venv/bin/activate
   python3 -m vllm.entrypoints.openai.api_server --model mistralai/Mistral-7B-Instruct-v0.2 --port 8000 --host 0.0.0.0
   ```

3. **Check if port 8000 is listening:**
   ```powershell
   ssh ubuntu@129.80.191.122 "netstat -tuln | grep 8000"
   ```

### "Port already in use"

If port 8000 is already in use, use a different port:
```powershell
ssh -N -L 8003:localhost:8000 ubuntu@129.80.191.122
```
Then use `http://localhost:8003/v1/chat/completions` in the dashboard.

### Stop All Tunnels

```powershell
.\scripts\stop_ssh_tunnels.ps1
```

Or manually:
```powershell
Get-Process ssh | Where-Object {$_.CommandLine -like "* -L *"} | Stop-Process
```

## Next Steps

1. ✅ Start SSH tunnels (keep terminals open)
2. ✅ Verify tunnels work with curl
3. ✅ Update dashboard API endpoints
4. ✅ Start evaluation!

The evaluation should now connect successfully! 🚀

