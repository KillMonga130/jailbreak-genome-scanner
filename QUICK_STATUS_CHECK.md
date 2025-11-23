# Quick Status Check - All Instances

## ✅ Setup Status

### Mistral 7B Instruct
- **IP**: `129.80.191.122`
- **Status**: ✅ vLLM Running
- **SSH Tunnel**: Port 8000
- **Endpoint**: `http://localhost:8000/v1/chat/completions`

### Qwen 7B Chat  
- **IP**: `150.136.220.151`
- **Status**: ✅ vLLM Setup Complete (may still be starting)
- **SSH Tunnel**: Port 8001
- **Endpoint**: `http://localhost:8001/v1/chat/completions`

### H100 (FOR THE HACKATHON)
- **IP**: `209.20.159.141`
- **Status**: ✅ vLLM Running
- **SSH Tunnel**: Port 8002
- **Endpoint**: `http://localhost:8002/v1/chat/completions`

## Next Steps

### 1. Verify vLLM is Running on Qwen

```bash
ssh -i moses.pem ubuntu@150.136.220.151 'tail -f /tmp/vllm.log'
```

Or check if process is running:
```bash
ssh -i moses.pem ubuntu@150.136.220.151 'ps aux | grep vllm'
```

### 2. Start SSH Tunnels

```powershell
.\scripts\setup_ssh_tunnels.ps1
```

Or manually:
```powershell
# Terminal 1 - Mistral
ssh -i moses.pem -N -L 8000:localhost:8000 ubuntu@129.80.191.122

# Terminal 2 - Qwen
ssh -i moses.pem -N -L 8001:localhost:8000 ubuntu@150.136.220.151

# Terminal 3 - H100
ssh -i moses.pem -N -L 8002:localhost:8000 ubuntu@209.20.159.141
```

### 3. Test Connections

```powershell
# Test Mistral
curl http://localhost:8000/v1/models

# Test Qwen
curl http://localhost:8001/v1/models

# Test H100
curl http://localhost:8002/v1/models
```

### 4. Use in Dashboard

Once tunnels are active and vLLM is running:

- **Defender**: `http://localhost:8000/v1/chat/completions` (Mistral)
- **Attacker**: `http://localhost:8001/v1/chat/completions` (Qwen)
- **Evaluator**: `http://localhost:8001/v1/chat/completions` (Qwen)

## Troubleshooting

### Qwen server still starting
If the health check shows "may still be starting", wait 1-2 minutes and check again:
```bash
ssh -i moses.pem ubuntu@150.136.220.151 'curl http://localhost:8000/health'
```

### SSH tunnels not working
- Check if tunnels are running: `Get-Process ssh`
- Restart tunnels if needed
- Verify port isn't blocked: `netstat -an | findstr "8000 8001 8002"`

### Connection errors
- Make sure vLLM is running: Check logs on instance
- Verify SSH tunnels are active
- Test direct connection: `curl http://localhost:8000/v1/models`

## All Set! 🚀

Once all checks pass, you're ready to run evaluations in the dashboard!

