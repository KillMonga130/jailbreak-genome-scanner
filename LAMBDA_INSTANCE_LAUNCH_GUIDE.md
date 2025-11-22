# 🚀 Lambda Cloud Instance Launch Guide

## Current Configuration

You've selected:
- **Instance Type**: 1x H100 (80 GB PCIe) - $2.49/hr
- **Region**: Utah, USA
- **Base Image**: Lambda Stack 22.04
- **Filesystem**: ⚠️ Need to decide

---

## 📁 Filesystem Selection

### ✅ **Recommendation: "Don't attach a filesystem"**

**Select this option** for most use cases with the Jailbreak Genome Scanner.

### Why Not Attach a Filesystem?

1. **Local Storage is Enough**: The H100 PCIe comes with 1 TB SSD - plenty for models
2. **Models Download Automatically**: vLLM downloads models on-demand from Hugging Face
3. **Cost Management**: Instances are typically short-lived (you terminate after use)
4. **No Data Persistence Needed**: Each evaluation session is independent

### When You WOULD Need a Filesystem

You might attach a filesystem if:
- ✅ You need to persist large datasets across instance restarts
- ✅ You want to share model cache between multiple instances
- ✅ You're storing evaluation results that need to persist
- ✅ You're running long-term deployments (but for cost, you probably won't)

**For now: Select "Don't attach a filesystem"** ⬅️

---

## 🔧 Next Steps After Launch

### Step 1: Instance Will Launch

After clicking "Launch" (or "Confirm"):
- ✅ Instance will be created (~2-5 minutes)
- ✅ You'll get an instance ID
- ✅ You'll get an IP address
- ✅ Instance will be in "active" state when ready

### Step 2: Get Instance Details

Once launched, you can get instance info:

```bash
# List all instances
python -c "from src.integrations.lambda_cloud import LambdaCloudClient; import asyncio; client = LambdaCloudClient(); instances = asyncio.run(client.list_instances()); [print(f\"ID: {i['id']}, IP: {i.get('ip')}, Status: {i.get('status')}\") for i in instances]"
```

Or check Lambda Cloud dashboard for:
- **Instance ID**: (e.g., `instance_abc123`)
- **IP Address**: (e.g., `150.136.146.143`)
- **SSH Command**: (if SSH key is configured)

### Step 3: Set Up SSH Access (If Needed)

If you want direct SSH access:

**Option A: SSH Key Already Added to Lambda**
- Lambda Cloud dashboard → SSH Keys
- Make sure your public key is there
- You'll get SSH command automatically

**Option B: Add SSH Key Now**
1. Generate key (if you don't have one):
   ```bash
   ssh-keygen -t rsa -b 4096 -f ~/.ssh/lambda_key
   ```

2. Copy public key:
   ```bash
   cat ~/.ssh/lambda_key.pub
   ```

3. Add to Lambda Cloud:
   - Go to Lambda Cloud dashboard → SSH Keys
   - Click "Add SSH Key"
   - Paste your public key

**Option C: Use API Endpoint (No SSH Needed)**
- You can use the instance without SSH if you set up the API server via Lambda Cloud's interface
- Or use our automated setup scripts (see below)

### Step 4: Set Up vLLM (Inference Server)

You need to install and run vLLM on the instance. Choose one method:

#### **Method 1: Automated Setup (Easiest)** ⭐

```bash
# Replace with your instance IP and SSH key
python scripts/setup_vllm_on_lambda.py \
    --ip YOUR_INSTANCE_IP \
    --key ~/.ssh/lambda_key \
    --model microsoft/phi-2
```

This will:
- ✅ Install vLLM on the instance
- ✅ Start the API server automatically
- ✅ Verify it's running

#### **Method 2: Manual SSH Setup**

1. **SSH into instance**:
   ```bash
   ssh -i ~/.ssh/lambda_key ubuntu@YOUR_INSTANCE_IP
   ```

2. **Install vLLM**:
   ```bash
   pip3 install vllm --upgrade
   ```

3. **Start API Server**:
   ```bash
   # Run in background (keeps running after SSH disconnect)
   nohup python3 -m vllm.entrypoints.openai.api_server \
       --model microsoft/phi-2 \
       --port 8000 \
       --host 0.0.0.0 \
       > /tmp/vllm.log 2>&1 &
   ```

4. **Verify it's running**:
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"ok"} or similar
   ```

5. **Check logs** (if needed):
   ```bash
   tail -f /tmp/vllm.log
   ```

#### **Method 3: Use Our Setup Script**

If you have SSH access:

1. **Copy setup script to instance**:
   ```bash
   scp -i ~/.ssh/lambda_key \
       scripts/setup_lambda_instance.sh \
       ubuntu@YOUR_INSTANCE_IP:~/
   ```

2. **SSH into instance**:
   ```bash
   ssh -i ~/.ssh/lambda_key ubuntu@YOUR_INSTANCE_IP
   ```

3. **Run setup script**:
   ```bash
   chmod +x setup_lambda_instance.sh
   ./setup_lambda_instance.sh
   ```

4. **Start vLLM**:
   ```bash
   source ~/venv/bin/activate
   python3 -m vllm.entrypoints.openai.api_server \
       --model microsoft/phi-2 \
       --port 8000 \
       --host 0.0.0.0
   ```

### Step 5: Get API Endpoint

Once vLLM is running, your API endpoint will be:

```
http://YOUR_INSTANCE_IP:8000/v1/chat/completions
```

Or for completions format:
```
http://YOUR_INSTANCE_IP:8000/v1/completions
```

**Example**:
```
http://150.136.146.143:8000/v1/chat/completions
```

### Step 6: Test Connection

Test if the API is accessible:

```bash
# Test connectivity
python scripts/check_connectivity.py --ip YOUR_INSTANCE_IP

# Or test with instance ID
python scripts/check_connectivity.py --instance-id YOUR_INSTANCE_ID
```

**Expected Output**:
```
[OK] SSH port (22) is accessible
[OK] Port 8000 is accessible
[OK] API endpoint is fully accessible!
```

**If port 8000 is blocked** (firewall/security group):
- Use SSH tunnel (see `CONNECTIVITY_FIX.md`)
- Or configure security group in Lambda Cloud dashboard

---

## 🎯 Using the Instance in Your Project

### Option 1: Use in Dashboard

1. **Launch dashboard**:
   ```bash
   streamlit run dashboard/arena_dashboard.py
   ```

2. **Configure defender**:
   - Select "Lambda Cloud" as defender type
   - Enter model name: `microsoft/phi-2` (or your chosen model)
   - Enter instance ID: `YOUR_INSTANCE_ID`
   - Enter API endpoint: `http://YOUR_INSTANCE_IP:8000/v1/chat/completions`

3. **Start evaluation**!

### Option 2: Use in Code

```python
import asyncio
from src.arena.jailbreak_arena import JailbreakArena
from src.defenders.llm_defender import LLMDefender

async def evaluate():
    # Create defender with Lambda instance
    defender = LLMDefender(
        model_name="microsoft/phi-2",
        model_type="local",
        use_lambda=True,
        lambda_instance_id="YOUR_INSTANCE_ID",
        lambda_api_endpoint="http://YOUR_INSTANCE_IP:8000/v1/chat/completions"
    )
    
    # Use in Arena
    arena = JailbreakArena()
    arena.add_defender(defender)
    arena.generate_attackers(num_strategies=10)
    
    # Run evaluation
    results = await arena.evaluate(rounds=50)
    
    # Get JVI score
    jvi = results['defenders'][0]['jvi']['jvi_score']
    print(f"JVI Score: {jvi:.2f}/100")

asyncio.run(evaluate())
```

---

## 🛑 Important: Always Clean Up!

**⚠️ CRITICAL: Always terminate instances when done to avoid charges!**

### Terminate via Dashboard

1. Go to Lambda Cloud dashboard
2. Find your instance
3. Click "Terminate" or "Stop"
4. Confirm termination

### Terminate via Code

```python
import asyncio
from src.integrations.lambda_cloud import LambdaCloudClient

async def cleanup():
    client = LambdaCloudClient()
    await client.terminate_instance("YOUR_INSTANCE_ID")
    print("Instance terminated!")

asyncio.run(cleanup())
```

### Terminate via Script

```bash
# If you deployed via our scripts
python deploy_models.py cleanup MODEL_NAME

# Or use API directly
python -c "from src.integrations.lambda_cloud import LambdaCloudClient; import asyncio; client = LambdaCloudClient(); asyncio.run(client.terminate_instance('YOUR_INSTANCE_ID'))"
```

---

## 💰 Cost Reminder

**Your H100 PCIe Instance**: $2.49/hour

- 1 hour = $2.49
- 24 hours = $59.76
- 1 week = $418.32

**💡 Tip**: Always terminate when done! Use try/finally blocks in code:

```python
try:
    # ... use instance ...
finally:
    await client.terminate_instance(instance_id)  # Always runs
```

---

## 📋 Complete Checklist

- [ ] ✅ Selected instance type: 1x H100 (80 GB PCIe)
- [ ] ✅ Selected region: Utah, USA
- [ ] ✅ Selected base image: Lambda Stack 22.04
- [ ] ✅ Selected filesystem: **"Don't attach a filesystem"**
- [ ] ✅ Clicked "Launch" / "Confirm"
- [ ] ⏳ Waiting for instance to be active (~2-5 min)
- [ ] ✅ Got instance ID and IP address
- [ ] ✅ Set up SSH access (if needed)
- [ ] ✅ Installed vLLM on instance
- [ ] ✅ Started vLLM API server
- [ ] ✅ Tested API endpoint connectivity
- [ ] ✅ Configured in dashboard/code
- [ ] ✅ Started evaluation!
- [ ] ⚠️ **Terminated instance when done** (IMPORTANT!)

---

## 🔍 Troubleshooting

### Instance Won't Launch

- Check Lambda Cloud dashboard for error messages
- Verify instance type availability in Utah region
- Try a different region if needed

### Can't SSH into Instance

- Verify SSH key is added to Lambda Cloud
- Check SSH key permissions: `chmod 600 ~/.ssh/lambda_key`
- Verify instance is "active" status

### Port 8000 Blocked

- Use SSH tunnel (see `CONNECTIVITY_FIX.md`)
- Or configure security group in Lambda Cloud dashboard:
  - Allow inbound TCP port 8000 from your IP (or 0.0.0.0/0 for testing)

### vLLM Won't Start

- Check GPU memory: `nvidia-smi` (on instance)
- Verify model name is correct
- Check logs: `tail -f /tmp/vllm.log`
- Try smaller model if GPU memory issue

### API Not Responding

- Verify vLLM is running: `curl http://localhost:8000/health` (on instance)
- Check if `--host 0.0.0.0` is used (not `localhost`)
- Verify firewall/security group allows port 8000

---

## 🎉 Summary

**Right Now:**
1. ✅ Select **"Don't attach a filesystem"**
2. ✅ Click **"Launch"** / **"Confirm"**
3. ⏳ Wait for instance to be active

**After Launch:**
1. ✅ Get instance ID and IP
2. ✅ Set up vLLM (automated or manual)
3. ✅ Get API endpoint URL
4. ✅ Test connectivity
5. ✅ Use in your project
6. ⚠️ **Always terminate when done!**

---

## 📚 Additional Resources

- **Lambda Cloud Docs**: https://docs.lambda.ai
- **vLLM Docs**: https://docs.vllm.ai
- **Project Setup**: See `LAMBDA_CLOUD_CONFIGURATION.md`
- **Connectivity Issues**: See `CONNECTIVITY_FIX.md`
- **Instance Setup**: See `docs/LAMBDA_INSTANCE_SETUP.md`

---

**You're ready to launch! Select "Don't attach a filesystem" and click Launch! 🚀**

