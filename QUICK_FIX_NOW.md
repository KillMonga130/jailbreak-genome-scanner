# 🚨 QUICK FIX - Use Mistral Instead of Qwen

## The Problem
- Qwen SSH tunnel on port 8001 isn't working
- Getting connection errors
- `list.remove` bug in retry logic (now fixed)

## ✅ IMMEDIATE SOLUTION: Switch to Mistral

**Mistral instance is ready and working perfectly:**
- ✅ Direct access (no SSH tunnel needed)
- ✅ vLLM confirmed running
- ✅ Port 8000 open
- ✅ Same model: `mistralai/Mistral-7B-Instruct-v0.2`

### In Dashboard:
1. **Refresh the page** (to get the fixes)
2. **Select "Lambda Cloud"** as Defender Type
3. **Choose "Mistral 7B Instruct"** from dropdown
4. **Endpoint should auto-fill**: `http://129.80.191.122:8000/v1/chat/completions`
5. **Click "START EVALUATION"**

That's it! Mistral works directly - no tunnel needed! 🚀

---

## If You Really Want Qwen

1. **Check SSH tunnel:**
   ```powershell
   Get-Process ssh | Where-Object {$_.CommandLine -like "*8001*"}
   ```

2. **Restart tunnel:**
   ```powershell
   .\fix_qwen_tunnel.ps1
   ```

3. **Check vLLM on Qwen:**
   ```bash
   ssh -i moses.pem ubuntu@150.136.220.151 'ps aux | grep vllm'
   ```

4. **If not running, start vLLM:**
   ```bash
   ssh -i moses.pem ubuntu@150.136.220.151
   source ~/venv/bin/activate
   python3 -m vllm.entrypoints.openai.api_server \
     --model Qwen/Qwen-7B-Chat \
     --port 8000 \
     --host 0.0.0.0
   ```

---

## What I Fixed

1. ✅ Fixed `list.remove` bug in retry logic
2. ✅ Better error messages for SSH tunnel issues
3. ✅ Improved connection pool error handling

**Just switch to Mistral and you're good to go!** 🎯

