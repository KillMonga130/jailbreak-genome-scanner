# 🚀 NEXT STEPS - GET STARTED NOW

## Step 1: Verify vLLM is Running with Correct Models

First, let's check what models are actually loaded on your instances:

```bash
# Check H100 instance
ssh -i moses.pem ubuntu@209.20.159.141 'curl http://localhost:8000/v1/models'

# Check Mistral instance  
ssh -i moses.pem ubuntu@129.80.191.122 'curl http://localhost:8000/v1/models'
```

This will show you the actual model names loaded on each instance.

---

## Step 2: Test Endpoints with Real Model Names

Once you know the model names, test the endpoints:

```bash
# Test H100 endpoint (replace MODEL_NAME with actual model from Step 1)
curl -X POST http://209.20.159.141:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "MODEL_NAME",
    "prompt": "Hello, how are you?",
    "max_tokens": 50
  }'
```

---

## Step 3: Start the Dashboard

```bash
streamlit run dashboard/arena_dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

---

## Step 4: Configure Defender in Dashboard

1. **Select "Lambda Cloud"** as Defender Type
2. **Choose an instance** from the dropdown:
   - 🚀 H100 instance (THE BIG ONE!) - Fastest
   - Mistral 7B Instruct - Good quality
3. **Verify API Endpoint** - Should auto-fill with direct IP endpoint
4. **Model Name** - Should auto-fill, but verify it matches what's on the instance

---

## Step 5: Start an Evaluation

1. Configure attackers (default is fine)
2. Set number of rounds
3. Click **"START EVALUATION"**
4. Watch the real-time results!

---

## 🆘 If Something Doesn't Work

### Problem: "Connection failed" or "Cannot reach endpoint"

**Solution**: Check if vLLM is actually running:
```bash
ssh -i moses.pem ubuntu@<instance_ip> 'ps aux | grep vllm'
```

If not running, start it:
```bash
ssh -i moses.pem ubuntu@<instance_ip>
# Then on the instance:
source ~/venv/bin/activate  # or wherever your vLLM venv is
python3 -m vllm.entrypoints.openai.api_server \
  --model <your-model-name> \
  --port 8000 \
  --host 0.0.0.0
```

### Problem: "Model not found" error

**Solution**: The model name in dashboard doesn't match what's on the instance. Check actual model name:
```bash
ssh -i moses.pem ubuntu@<instance_ip> 'curl http://localhost:8000/v1/models'
```

Then update the model name in the dashboard.

### Problem: Qwen instance not working

**Solution**: Port 8000 is blocked. Use SSH tunnel:
```powershell
.\fix_qwen_tunnel.ps1
```

Then use `http://localhost:8001/v1/chat/completions` in dashboard.

---

## ✅ Quick Start (Fastest Path)

**Just want to get started NOW?**

1. Open terminal
2. Run: `streamlit run dashboard/arena_dashboard.py`
3. In browser, select "Lambda Cloud" → Choose H100 instance
4. Click "START EVALUATION"
5. Done! 🎉

The H100 instance is ready to go - it's the fastest and most powerful option.

---

## 📊 What You'll See

- Real-time evaluation progress
- Attack success rates
- Defender responses
- Threat radar visualization
- Genome map of vulnerabilities

**You're all set!** 🚀

