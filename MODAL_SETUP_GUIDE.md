# 🚀 Modal.com Setup Guide

## Why Modal?

✅ **Pay-per-use**: Only pay when functions run (per second)  
✅ **No idle costs**: Containers shut down after 5 min idle  
✅ **Access to models**: Pre-configured model access  
✅ **Serverless**: No instance management needed  
✅ **Auto-scaling**: Handles traffic automatically  

## Setup Steps

### 1. Install Modal SDK

```bash
pip install modal
```

### 2. Set Up Credentials (Already Done!)

Your credentials are already configured:
- API Key: `wk-bLY0HgGSR5CiK1ix4UZ3mT`
- Secret: `ws-U7PmwVer3BzRBdPak3nzJV`

### 3. Deploy Models to Modal

```bash
modal deploy modal_deploy.py
```

This will:
- Deploy vLLM models to Modal
- Create serverless endpoints
- Set up GPU instances (A10 by default)

### 4. Get Endpoint URLs

After deployment, Modal will give you endpoint URLs like:
```
https://your-username--jailbreak-genome-scanner-serve.modal.run
https://your-username--jailbreak-genome-scanner-chat-completions.modal.run
https://your-username--jailbreak-genome-scanner-completions.modal.run
```

### 5. Configure Endpoints

Add to `.env` file:
```bash
MODAL_ENDPOINT_JAILBREAK_GENOME_SCANNER=https://your-username--jailbreak-genome-scanner-serve.modal.run
MODAL_ENDPOINT_CHAT=https://your-username--jailbreak-genome-scanner-chat-completions.modal.run
MODAL_ENDPOINT_COMPLETIONS=https://your-username--jailbreak-genome-scanner-completions.modal.run
```

### 6. Update Dashboard

The dashboard will automatically detect Modal endpoints and use them!

---

## Available Endpoints

After deployment, you'll have:

1. **`/serve`** - Simple prompt → response
2. **`/chat_completions`** - OpenAI-compatible chat format
3. **`/completions`** - OpenAI-compatible completions format

---

## Cost Comparison

### Lambda Cloud
- **Cost**: ~$0.75/hour for A10 (even when idle)
- **24/7 running**: ~$18/day
- **Best for**: Long-running, always-on services

### Modal
- **Cost**: ~$0.0004/second for A10 (only when running)
- **5 min inference**: ~$0.12
- **Idle time**: $0 (containers shut down)
- **Best for**: On-demand, pay-per-use

**Savings**: If you run 1 hour/day of inference:
- Lambda: $18/day (24/7)
- Modal: ~$1.44/day (1 hour)
- **Save ~92%!** 💰

---

## Quick Start

1. **Deploy**:
   ```bash
   modal deploy modal_deploy.py
   ```

2. **Get endpoints** from Modal dashboard

3. **Add to .env**:
   ```bash
   MODAL_ENDPOINT_JAILBREAK_GENOME_SCANNER=<your-endpoint>
   ```

4. **Use in dashboard**: Select "Modal" as defender type!

---

## Models Available

You can deploy any model supported by vLLM:
- `mistralai/Mistral-7B-Instruct-v0.2`
- `Qwen/Qwen-7B-Chat`
- `meta-llama/Llama-2-7b-chat-hf`
- `microsoft/phi-2`
- And many more!

Just change the `model` parameter in `modal_deploy.py`!

---

## Next Steps

1. ✅ Credentials configured
2. ⏭️ Deploy: `modal deploy modal_deploy.py`
3. ⏭️ Get endpoints from Modal dashboard
4. ⏭️ Add endpoints to .env
5. ⏭️ Use in dashboard!

🚀 **You're ready to deploy!**

