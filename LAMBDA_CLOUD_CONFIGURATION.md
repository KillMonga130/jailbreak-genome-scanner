# 🚀 Lambda Cloud Configuration Guide

Complete step-by-step guide for configuring Lambda Cloud with the Jailbreak Genome Scanner.

## 📋 Quick Overview

**What you need:**
1. Lambda Cloud API Key (from Lambda Cloud dashboard)
2. `.env` file with your API key
3. SSH key (optional, for direct instance access)
4. Test the connection

---

## 🔑 Step 1: Get Your Lambda Cloud API Key

### 1.1 Sign Up / Log In
1. Go to [https://cloud.lambda.ai](https://cloud.lambda.ai)
2. Sign up or log in to your account

### 1.2 Get API Key
1. Go to **Settings** or **API Keys** section
2. Click **"Generate API Key"** or copy existing key
3. The key format is: `secret_<id>.<token>`
   - Example: `secret_abc123.xyz789token`

### 1.3 Save Your API Key Securely
⚠️ **Important**: Store this key securely - you'll need it for configuration!

---

## ⚙️ Step 2: Configure Environment Variables

### 2.1 Create `.env` File

Create a `.env` file in the project root directory:

```bash
# If file doesn't exist, create it
touch .env  # Linux/Mac
# or in PowerShell: New-Item .env
```

### 2.2 Add Lambda Cloud Configuration

Open `.env` file and add:

```env
# ============================================
# LAMBDA CLOUD CONFIGURATION
# ============================================

# Required: Your Lambda Cloud API Key
# Format: secret_<id>.<token>
LAMBDA_API_KEY=your_lambda_api_key_here

# Optional: Default instance type (if not specified in code)
# Recommended for testing: gpu_1x_a10
LAMBDA_DEFAULT_INSTANCE_TYPE=gpu_1x_a10

# Optional: Default region (if not specified in code)
# Recommended: us-east-1
LAMBDA_DEFAULT_REGION=us-east-1

# ============================================
# OPTIONAL: Other API Keys (if needed)
# ============================================

# OpenAI (optional, for using GPT models)
# OPENAI_API_KEY=sk-xxx

# Anthropic (optional, for using Claude models)
# ANTHROPIC_API_KEY=sk-ant-xxx

# Perplexity (optional, for recent data gathering)
# PERPLEXITY_API_KEY=pplx-xxx
```

### 2.3 Replace `your_lambda_api_key_here`

Replace `your_lambda_api_key_here` with your actual API key from Step 1.

**Example:**
```env
LAMBDA_API_KEY=secret_abc123def456.v5H38gHQqPMfwcPjXaIR6QKer9FglUZg
```

---

## 🎯 Step 3: Choose Your Instance Type

### Recommended Instance Types by Use Case

#### ✅ **For Testing / Development** (Recommended to Start)

| Instance Type | GPU | Memory | Cost/Hour | Command/Config |
|--------------|-----|--------|-----------|----------------|
| **`gpu_1x_a10`** ⭐ | 1x A10 | 24GB | **$0.75/hr** | Best for testing |
| `gpu_1x_a100` | 1x A100 | 40GB | $1.29/hr | Better quality |

**Use case**: Small models (<7B parameters)
- phi-2 (2.7B)
- Llama-2-7b-chat
- Mistral-7B-Instruct

**Configuration:**
```env
LAMBDA_DEFAULT_INSTANCE_TYPE=gpu_1x_a10
```

#### 🚀 **For Production / Better Quality**

| Instance Type | GPU | Memory | Cost/Hour | Best For |
|--------------|-----|--------|-----------|----------|
| `gpu_1x_h100` | 1x H100 | 80GB | **$3.29/hr** | Large models (13B+) |
| `gpu_1x_a100` | 1x A100 | 40GB | $1.29/hr | Medium models (7-13B) |

**Use case**: Larger models (13B+ parameters)
- Llama-2-13b-chat
- Mistral-Medium
- Other 13B+ models

#### 💪 **For Large-Scale Evaluation**

| Instance Type | GPUs | Memory | Cost/Hour | Use When |
|--------------|------|--------|-----------|----------|
| `gpu_8x_a100` | 8x A100 | 320GB | $10.32/hr | Multiple models parallel |
| `gpu_2x_h100` | 2x H100 | 160GB | $6.38/hr | Very large models |

**Use case**: Running multiple evaluations simultaneously or very large models.

### 📊 All Available Instance Types (From Your List)

| Instance Type | GPUs | Memory | vCPUs | RAM | SSD | Cost/Hour |
|--------------|------|--------|-------|-----|-----|-----------|
| **`gpu_1x_a10`** ⭐ | 1x A10 | 24GB | 30 | 200GB | 1.4TB | **$0.75/hr** |
| `gpu_1x_a100` | 1x A100 | 40GB | 30 | 200GB | 0.5TB | $1.29/hr |
| `gpu_8x_a100` | 8x A100 | 320GB | 124 | 1800GB | 6TB | $10.32/hr |
| `gpu_1x_h100` | 1x H100 | 80GB PCIe | 26 | 200GB | 1TB | $2.49/hr |
| `gpu_1x_h100` | 1x H100 | 80GB SXM5 | 26 | 225GB | 2.8TB | $3.29/hr |
| `gpu_2x_h100` | 2x H100 | 160GB SXM5 | 52 | 450GB | 5.5TB | $6.38/hr |
| `gpu_4x_h100` | 4x H100 | 320GB SXM5 | 104 | 900GB | 11TB | $12.36/hr |
| `gpu_8x_h100` | 8x H100 | 640GB SXM5 | 208 | 1800GB | 22TB | $23.92/hr |
| `gpu_8x_b200` | 8x B200 | 180GB SXM6 | 208 | 2900GB | 22TB | $39.92/hr |
| `gpu_1x_gh200` | 1x GH200 | 96GB | 64 | 432GB | 4TB | $1.49/hr |

### 💡 **Recommendation for Starting**

**Start with**: `gpu_1x_a10` ($0.75/hr)
- Cheapest option
- Good for testing
- Supports models up to 7B parameters
- Perfect for learning the system

**When to upgrade**:
- Need faster inference → `gpu_1x_a100`
- Running 13B+ models → `gpu_1x_h100`
- Need parallel evaluation → `gpu_8x_a100`

---

## 🧪 Step 4: Test Your Configuration

### 4.1 Test Lambda Cloud Connection

Run the test script:

```bash
python test_lambda.py
```

**Expected Output (Success):**
```
[OK] API Key found
[OK] Client initialized
[OK] Successfully retrieved X instances
[OK] API endpoint is accessible (200 OK)
[SUCCESS] All tests passed!
```

**If you get an error:**
- ❌ `401 Unauthorized` → Check your API key in `.env`
- ❌ `API key not configured` → Make sure `.env` file exists and has `LAMBDA_API_KEY`
- ❌ `Connection timeout` → Check your internet connection

### 4.2 Test with Python (Optional)

```python
import asyncio
from src.integrations.lambda_cloud import LambdaCloudClient

async def test():
    client = LambdaCloudClient()
    instances = await client.list_instances()
    print(f"Found {len(instances)} instances")
    print("✅ Connection successful!")

asyncio.run(test())
```

---

## 📝 Step 5: Complete Configuration Example

### Complete `.env` File Template

Copy this entire template and fill in your values:

```env
# ============================================
# LAMBDA CLOUD CONFIGURATION (REQUIRED)
# ============================================

# Your Lambda Cloud API Key (get from https://cloud.lambda.ai)
# Format: secret_<id>.<token>
LAMBDA_API_KEY=secret_your_id_here.your_token_here

# Default instance type for deployments
# Recommended: gpu_1x_a10 for testing ($0.75/hr)
# Options: gpu_1x_a10, gpu_1x_a100, gpu_1x_h100, etc.
LAMBDA_DEFAULT_INSTANCE_TYPE=gpu_1x_a10

# Default region for instance launches
# Recommended: us-east-1
LAMBDA_DEFAULT_REGION=us-east-1

# ============================================
# OPTIONAL: LLM API KEYS
# ============================================

# OpenAI API Key (optional - for GPT models)
# OPENAI_API_KEY=sk-your-openai-key-here

# Anthropic API Key (optional - for Claude models)
# ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Perplexity API Key (optional - for recent data gathering)
# PERPLEXITY_API_KEY=pplx-your-perplexity-key-here

# ============================================
# OPTIONAL: ARENA CONFIGURATION
# ============================================

# Number of rounds per evaluation
# ARENA_ROUNDS=100

# Minimum number of attackers
# MIN_ATTACKERS=5

# Scoring threshold for exploits
# SCORING_THRESHOLD=0.7

# ============================================
# OPTIONAL: LOGGING
# ============================================

# Log level: DEBUG, INFO, WARNING, ERROR
# LOG_LEVEL=INFO

# Log file path
# LOG_FILE=logs/scanner.log
```

---

## 🚀 Step 6: Quick Start - Deploy Your First Model

### 6.1 Interactive Setup (Easiest)

```bash
python setup_lambda_models.py
```

This will:
- ✅ Check your configuration
- ✅ Show available models
- ✅ Guide you through deployment
- ✅ Save deployment info automatically

### 6.2 Deploy Specific Model

```bash
# Deploy smallest/cheapest model for testing
python deploy_models.py deploy phi-2

# Or deploy Llama-2-7b-chat
python deploy_models.py deploy llama-2-7b-chat
```

### 6.3 Check Deployed Models

```bash
python deploy_models.py deployed
```

This shows all your deployed models with instance IDs.

---

## 🔐 Step 7: SSH Key Setup (Optional)

### If you want direct SSH access to instances:

1. **Generate SSH Key** (if you don't have one):
   ```bash
   ssh-keygen -t rsa -b 4096 -f ~/.ssh/lambda_key
   ```

2. **Add Public Key to Lambda Cloud**:
   - Go to Lambda Cloud dashboard
   - Navigate to **SSH Keys** section
   - Click **"Add SSH Key"**
   - Paste your public key (`~/.ssh/lambda_key.pub`)

3. **Use in Project**:
   - Place private key (`lambda_key`) in project root
   - Or update SSH path in code if needed

**Note**: SSH keys are optional. The system can work without them if you're using API endpoints.

---

## ✅ Configuration Checklist

Before you start using Lambda Cloud:

- [ ] ✅ Signed up for Lambda Cloud account
- [ ] ✅ Got API key from Lambda Cloud dashboard
- [ ] ✅ Created `.env` file in project root
- [ ] ✅ Added `LAMBDA_API_KEY` to `.env` file
- [ ] ✅ Set `LAMBDA_DEFAULT_INSTANCE_TYPE` (recommended: `gpu_1x_a10`)
- [ ] ✅ Set `LAMBDA_DEFAULT_REGION` (recommended: `us-east-1`)
- [ ] ✅ Tested connection with `python test_lambda.py`
- [ ] ✅ (Optional) Added SSH key to Lambda Cloud
- [ ] ✅ Ready to deploy models!

---

## 🎯 Usage Examples

### Example 1: Basic Instance Management

```python
import asyncio
from src.integrations.lambda_cloud import LambdaCloudClient

async def manage_instances():
    client = LambdaCloudClient()
    
    # List all instances
    instances = await client.list_instances()
    print(f"Active instances: {len(instances)}")
    
    # Launch a new instance
    instance_data = await client.launch_instance(
        instance_type="gpu_1x_a10",  # Cheapest option
        region="us-east-1",
        quantity=1
    )
    
    instance_id = instance_data["instance_ids"][0]
    print(f"Launched: {instance_id}")
    
    # Get instance status
    instance = await client.get_instance_status(instance_id)
    print(f"IP: {instance.get('ip')}, Status: {instance.get('status')}")
    
    # IMPORTANT: Always terminate when done!
    await client.terminate_instance(instance_id)
    print("Terminated")

asyncio.run(manage_instances())
```

### Example 2: Use Lambda Model in Arena

```python
import asyncio
from src.arena.jailbreak_arena import JailbreakArena
from src.defenders.llm_defender import LLMDefender

async def evaluate_with_lambda():
    # Get instance ID from deployment
    # Run: python deploy_models.py deployed
    instance_id = "your_instance_id_here"
    
    # Create defender with Lambda instance
    defender = LLMDefender(
        model_name="meta-llama/Llama-2-7b-chat-hf",
        model_type="local",
        use_lambda=True,
        lambda_instance_id=instance_id,
        lambda_api_endpoint="http://<instance_ip>:8000/v1/chat/completions"  # If using vLLM
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

asyncio.run(evaluate_with_lambda())
```

---

## 💰 Cost Management

### Instance Costs (Per Hour)

| Instance Type | Cost/Hour | Cost/Day (24h) | Cost/Month (720h) |
|--------------|-----------|----------------|-------------------|
| `gpu_1x_a10` ⭐ | $0.75 | $18.00 | $540.00 |
| `gpu_1x_a100` | $1.29 | $30.96 | $928.80 |
| `gpu_1x_h100` | $3.29 | $78.96 | $2,368.80 |
| `gpu_8x_a100` | $10.32 | $247.68 | $7,430.40 |

### 💡 Cost Saving Tips

1. **Always Terminate Instances**:
   ```python
   try:
       # ... use instance ...
   finally:
       await client.terminate_instance(instance_id)  # IMPORTANT!
   ```

2. **Use Smallest Instance for Testing**:
   - Start with `gpu_1x_a10` ($0.75/hr)
   - Only upgrade when needed

3. **Batch Evaluations**:
   - Run multiple evaluations on same instance
   - Don't launch new instance for each evaluation

4. **Monitor Usage**:
   ```bash
   python deploy_models.py deployed  # Check active instances
   ```

5. **Set Up Alerts**:
   - Check Lambda Cloud dashboard regularly
   - Set billing alerts if available

---

## 🔧 Troubleshooting

### Problem: `401 Unauthorized`

**Solution:**
- Check API key is correct in `.env`
- Make sure key format is: `secret_<id>.<token>`
- Verify no extra spaces in `.env` file

### Problem: `API key not configured`

**Solution:**
- Make sure `.env` file exists in project root
- Check file has `LAMBDA_API_KEY=` line
- Restart terminal/IDE after creating `.env`

### Problem: `Instance launch failed`

**Solution:**
- Check instance type availability: `python deploy_models.py list`
- Try different region
- Check Lambda Cloud status page

### Problem: `Connection timeout`

**Solution:**
- Check internet connection
- Verify Lambda Cloud API is accessible: `curl https://cloud.lambda.ai/api/v1/instances`
- Check firewall settings

### Problem: Port 8000 blocked

**Solution:**
- Use SSH tunnel (see `CONNECTIVITY_FIX.md`)
- Or configure security group in Lambda Cloud dashboard

---

## 📚 Next Steps

After configuration is complete:

1. ✅ **Test Connection**: `python test_lambda.py`
2. ✅ **Deploy Model**: `python setup_lambda_models.py`
3. ✅ **List Deployments**: `python deploy_models.py deployed`
4. ✅ **Launch Dashboard**: `streamlit run dashboard/arena_dashboard.py`
5. ✅ **Start Evaluating**: Use Lambda models in Arena!

---

## 📖 Additional Resources

- **Lambda Cloud Docs**: https://docs.lambda.ai
- **API Reference**: https://docs.lambda.ai/api-reference
- **Dashboard**: https://cloud.lambda.ai
- **Project Documentation**: See `README.md` and `docs/` folder

---

## ✅ Summary

**Minimum Required Configuration:**

```env
LAMBDA_API_KEY=secret_your_id.your_token
LAMBDA_DEFAULT_INSTANCE_TYPE=gpu_1x_a10
LAMBDA_DEFAULT_REGION=us-east-1
```

**Quick Start Commands:**

```bash
# 1. Test configuration
python test_lambda.py

# 2. Deploy a model
python setup_lambda_models.py

# 3. Check deployments
python deploy_models.py deployed

# 4. Launch dashboard
streamlit run dashboard/arena_dashboard.py
```

**You're ready to go! 🚀**

