# 🔧 Fix SSH Tunnel Issue

## Problem
The dashboard is trying to use `http://localhost:8001/v1/chat/completions` (Qwen via SSH tunnel) but it's failing because:
1. SSH tunnel on port 8001 may not be running
2. vLLM may not be running on Qwen instance

## Quick Fix Options

### Option 1: Use Mistral Instead (Easiest)
**Switch to Mistral instance which has direct access:**
- Instance: Mistral A10 (129.80.191.122)
- Endpoint: `http://129.80.191.122:8000/v1/chat/completions`
- ✅ No SSH tunnel needed - works directly!

**In Dashboard:**
1. Select "Lambda Cloud" as Defender Type
2. Choose "Mistral 7B Instruct" instance
3. Use endpoint: `http://129.80.191.122:8000/v1/chat/completions`

### Option 2: Fix Qwen SSH Tunnel
**If you want to use Qwen:**

1. **Check if tunnel is running:**
   ```powershell
   Get-Process ssh | Where-Object {$_.CommandLine -like "*8001*"}
   ```

2. **Restart SSH tunnel:**
   ```powershell
   .\fix_qwen_tunnel.ps1
   ```

3. **Verify vLLM is running on Qwen:**
   ```bash
   ssh -i moses.pem ubuntu@150.136.220.151 'ps aux | grep vllm'
   ```

4. **If vLLM not running, start it:**
   ```bash
   ssh -i moses.pem ubuntu@150.136.220.151
   # Then on the instance:
   source ~/venv/bin/activate  # or wherever vLLM venv is
   python3 -m vllm.entrypoints.openai.api_server \
     --model Qwen/Qwen-7B-Chat \
     --port 8000 \
     --host 0.0.0.0
   ```

## Recommended: Use Mistral
**Mistral instance is ready and working:**
- ✅ Direct access (no tunnel needed)
- ✅ vLLM confirmed running
- ✅ Port 8000 open
- ✅ Same model quality

Just switch to Mistral in the dashboard and you're good to go! 🚀

