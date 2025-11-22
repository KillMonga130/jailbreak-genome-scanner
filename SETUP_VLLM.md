# Setting Up vLLM on Lambda Instance

## Quick Setup

Your Lambda instance is running but **vLLM is not set up yet**. That's why all attacks are being blocked - the model isn't actually responding.

## Option 1: Automated Setup (Recommended)

```bash
python scripts/setup_vllm_on_lambda.py --ip 150.136.146.143 --key moses.pem --model microsoft/phi-2
```

This will:
1. Install vLLM on the instance
2. Start the API server
3. Verify it's running

## Option 2: Manual Setup

### Step 1: SSH into Instance

```bash
ssh -i moses.pem ubuntu@150.136.146.143
```

### Step 2: Install vLLM

```bash
pip3 install vllm --upgrade
```

### Step 3: Start API Server

```bash
# Run in background (recommended)
nohup python3 -m vllm.entrypoints.openai.api_server \
    --model microsoft/phi-2 \
    --port 8000 \
    --host 0.0.0.0 \
    > /tmp/vllm.log 2>&1 &
```

### Step 4: Verify It's Running

```bash
# Check if server is responding
curl http://localhost:8000/health

# Or check logs
tail -f /tmp/vllm.log
```

## Step 5: Update Dashboard

Once vLLM is running, use this endpoint in the dashboard:

```
http://150.136.146.143:8000/v1/chat/completions
```

The dashboard should auto-fill this, but you can also enter it manually.

## Troubleshooting

### Server won't start
- Check GPU memory: `nvidia-smi`
- Check if port 8000 is in use: `netstat -tuln | grep 8000`
- Check logs: `tail -f /tmp/vllm.log`

### Connection refused
- Make sure `--host 0.0.0.0` is used (not `localhost`)
- Check Lambda security groups allow port 8000
- Verify instance is running: Check Lambda Cloud dashboard

### Model loading errors
- Check if model name is correct: `microsoft/phi-2`
- Verify GPU has enough memory
- Try a smaller model if needed

## Keep Server Running

To keep vLLM running after SSH disconnect, use `screen` or `tmux`:

```bash
# Using screen
screen -S vllm
python3 -m vllm.entrypoints.openai.api_server --model microsoft/phi-2 --port 8000 --host 0.0.0.0
# Press Ctrl+A then D to detach

# Reattach later
screen -r vllm
```

## Current Status

- ✅ Instance: Active (150.136.146.143)
- ❌ vLLM: Not running
- ⚠️ Endpoint: Needs to be set up

After setting up vLLM, the dashboard will work properly and you'll see real model responses!

