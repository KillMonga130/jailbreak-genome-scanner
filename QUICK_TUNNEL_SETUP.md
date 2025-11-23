# Quick SSH Tunnel Setup - Manual Instructions

## Your 3 Lambda Instances

1. **Mistral 7B**: `129.80.191.122` → Use port `8000`
2. **Qwen 7B**: `150.136.220.151` → Use port `8001`  
3. **H100**: `209.20.159.141` → Use port `8002`

## Step-by-Step Setup

### Option 1: Using PowerShell (3 separate windows)

Open **3 separate PowerShell windows** and run one command in each:

**Window 1 - Mistral:**
```powershell
ssh -i moses.pem -N -L 8000:localhost:8000 ubuntu@129.80.191.122
```

**Window 2 - Qwen:**
```powershell
ssh -i moses.pem -N -L 8001:localhost:8000 ubuntu@150.136.220.151
```

**Window 3 - H100:**
```powershell
ssh -i moses.pem -N -L 8002:localhost:8000 ubuntu@209.20.159.141
```

**Keep all 3 windows open!** The tunnels must stay running.

### Option 2: Using WSL (if you have it)

Open **3 separate terminals** and run:

```bash
# Terminal 1
ssh -i moses.pem -N -L 8000:localhost:8000 ubuntu@129.80.191.122

# Terminal 2
ssh -i moses.pem -N -L 8001:localhost:8000 ubuntu@150.136.220.151

# Terminal 3
ssh -i moses.pem -N -L 8002:localhost:8000 ubuntu@209.20.159.141
```

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

## Update Dashboard

Once tunnels are active, use these endpoints in your dashboard:

- **Defender**: `http://localhost:8000/v1/chat/completions` (Mistral)
- **Attacker**: `http://localhost:8001/v1/chat/completions` (Qwen)
- **Evaluator**: `http://localhost:8001/v1/chat/completions` (Qwen)

## Troubleshooting

### "Permission denied" or SSH key issues

You may need to specify your SSH key:

```powershell
ssh -i ~/.ssh/moses.pem -N -L 8000:localhost:8000 ubuntu@129.80.191.122
```

Or if your key is in a different location, adjust the path.

### "Connection refused" 

This means:
1. The tunnel is working, but vLLM isn't running on the instance
2. You need to SSH into the instance and start vLLM

### Port already in use

If port 8000 is busy, use different ports:
- Mistral: `8003`
- Qwen: `8004`
- H100: `8005`

Then update the dashboard endpoints accordingly.

## Stop Tunnels

Press `Ctrl+C` in each terminal window to stop the tunnels.

