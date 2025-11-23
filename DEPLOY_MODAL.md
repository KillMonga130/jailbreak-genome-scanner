# 🚀 Deploy to Modal.com - Quick Start

## Step 1: Install Modal SDK

```bash
pip install modal
```

## Step 2: Set Up Credentials (Already Done!)

Your credentials are already in `.env`:
- ✅ MODAL_API_KEY=wk-bLY0HgGSR5CiK1ix4UZ3mT
- ✅ MODAL_SECRET=ws-U7PmwVer3BzRBdPak3nzJV

## Step 3: Deploy Models

```bash
modal deploy modal_deploy.py
```

This will:
- Deploy vLLM models to Modal
- Create serverless endpoints
- Set up GPU instances (A10 by default)

## Step 4: Get Endpoint URLs

After deployment, Modal will show you endpoint URLs like:
```
https://your-username--jailbreak-genome-scanner-chat-completions.modal.run
```

**Copy the endpoint URL!**

## Step 5: Add Endpoint to .env

Add this line to your `.env` file:
```bash
MODAL_ENDPOINT_JAILBREAK_GENOME_SCANNER=https://your-username--jailbreak-genome-scanner-chat-completions.modal.run
```

Or use the chat completions endpoint:
```bash
MODAL_ENDPOINT_CHAT=https://your-username--jailbreak-genome-scanner-chat-completions.modal.run
```

## Step 6: Use in Dashboard!

1. Start dashboard: `streamlit run dashboard/arena_dashboard.py`
2. Select **"Modal.com"** as Defender Type
3. Endpoint should auto-fill from `.env`
4. Click **"START EVALUATION"**!

---

## Cost Savings 💰

**Lambda Cloud:**
- $0.75/hour for A10 (even when idle)
- 24/7 = ~$18/day

**Modal.com:**
- $0.0004/second for A10 (only when running)
- 1 hour/day = ~$1.44/day
- **Save ~92%!**

---

## Available Models

You can deploy any vLLM-supported model by editing `modal_deploy.py`:
- `mistralai/Mistral-7B-Instruct-v0.2` (default)
- `Qwen/Qwen-7B-Chat`
- `meta-llama/Llama-2-7b-chat-hf`
- `microsoft/phi-2`
- And many more!

---

## Troubleshooting

**"Modal endpoint not configured"**
- Make sure you deployed: `modal deploy modal_deploy.py`
- Copy endpoint URL from Modal dashboard
- Add to `.env` file

**"Connection error"**
- Check endpoint URL is correct
- Make sure deployment succeeded
- Check Modal dashboard for status

---

🚀 **You're ready to deploy!**

