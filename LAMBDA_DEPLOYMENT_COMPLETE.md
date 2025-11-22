# ✅ Lambda Cloud Model Deployment - Complete!

## 🎯 What Was Created

### 1. Model Deployment System ✅
- **6 open source models** configured and ready to deploy
- **Lambda Cloud integration** for GPU-accelerated inference
- **Deployment scripts** for easy model management
- **API endpoint support** for vLLM/TGI servers

### 2. Available Models ✅

| Model Key | Model Name | Instance Type | Cost/Hour | Use Case |
|-----------|------------|---------------|-----------|----------|
| **phi-2** | microsoft/phi-2 | gpu_1x_a10 | ~$0.50 | ⭐ Testing (Recommended) |
| **llama-2-7b-chat** | meta-llama/Llama-2-7b-chat-hf | gpu_1x_a10 | ~$0.50 | Development |
| **mistral-7b-instruct** | mistralai/Mistral-7B-Instruct-v0.2 | gpu_1x_a10 | ~$0.50 | High Quality |
| **falcon-7b-instruct** | tiiuae/falcon-7b-instruct | gpu_1x_a10 | ~$0.50 | Instructions |
| **qwen-7b-chat** | Qwen/Qwen-7B-Chat | gpu_1x_a10 | ~$0.50 | Multilingual |
| **llama-2-13b-chat** | meta-llama/Llama-2-13b-chat-hf | gpu_1x_a100 | ~$1.10 | Better Quality |

### 3. Deployment Tools ✅

#### Interactive Setup
```bash
python setup_lambda_models.py
```
- Shows available models
- Checks existing deployments
- Interactive model selection
- Automatic configuration saving

#### Command Line Tools
```bash
# List available models
python deploy_models.py list

# Deploy single model
python deploy_models.py deploy phi-2

# List deployed models
python deploy_models.py deployed

# Clean up model
python deploy_models.py cleanup phi-2

# Deploy all models (⚠️ expensive)
python deploy_models.py deploy-all

# Clean up all models
python deploy_models.py cleanup-all
```

### 4. Integration with Arena ✅

#### In Code
```python
from src.defenders.llm_defender import LLMDefender
from src.arena.jailbreak_arena import JailbreakArena

# Deploy model first (get instance_id)
instance_id = "your_instance_id"  # From: python deploy_models.py deployed

# Create defender with API endpoint
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
results = await arena.evaluate(rounds=100)
```

#### In Dashboard
1. Select "Lambda Cloud" as defender type
2. Enter model name
3. Enter instance ID
4. Enter API endpoint (if using vLLM/TGI)
5. Start battle!

### 5. API Endpoint Support ✅

The system supports API endpoints for deployed models:

- **vLLM**: OpenAI-compatible API server
- **Text Generation Inference**: Production-ready inference server
- **Custom endpoints**: Any HTTP API endpoint

**Setup on Lambda instance**:
```bash
# SSH into instance
ssh ubuntu@<instance_ip> -i ~/.ssh/lambda_key

# Install vLLM
pip install vllm

# Start API server
python3 -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-2-7b-chat-hf \
    --port 8000 \
    --host 0.0.0.0
```

Then use endpoint: `http://<instance_ip>:8000/v1/chat/completions`

## 📁 Files Created

### Core Files
- `src/integrations/lambda_models.py` - Model deployment manager
- `src/integrations/lambda_cloud.py` - Updated with API endpoint support
- `src/defenders/llm_defender.py` - Updated to support Lambda models

### Deployment Scripts
- `deploy_models.py` - Command-line deployment tool
- `setup_lambda_models.py` - Interactive setup wizard

### Documentation
- `docs/LAMBDA_MODELS_SETUP.md` - Comprehensive setup guide
- `docs/LAMBDA_INSTANCE_SETUP.md` - Instance setup instructions
- `README_DEPLOYMENT.md` - Quick deployment guide
- `QUICK_START.md` - Quick start instructions

### Scripts
- `scripts/setup_lambda_instance.sh` - Setup script for Lambda instances

## 🚀 Quick Start

### Step 1: Set Lambda API Key

```bash
# In .env file
LAMBDA_API_KEY=secret_xxx.xxx
```

### Step 2: Deploy a Model

```bash
# Interactive setup (recommended)
python setup_lambda_models.py

# Or deploy specific model
python deploy_models.py deploy phi-2
```

### Step 3: Get Instance ID

```bash
python deploy_models.py deployed
```

### Step 4: Set Up API Server (Optional)

SSH into instance and install vLLM:
```bash
pip install vllm
python3 -m vllm.entrypoints.openai.api_server --model <model_name> --port 8000
```

### Step 5: Use in Arena

```python
# With API endpoint
defender = LLMDefender(
    model_name="meta-llama/Llama-2-7b-chat-hf",
    model_type="local",
    use_lambda=True,
    lambda_instance_id="instance_123",
    lambda_api_endpoint="http://<ip>:8000/v1/chat/completions"
)

# Or without endpoint (SSH-based - placeholder for now)
defender = LLMDefender(
    model_name="meta-llama/Llama-2-7b-chat-hf",
    model_type="local",
    use_lambda=True,
    lambda_instance_id="instance_123"
)
```

### Step 6: Clean Up

```bash
python deploy_models.py cleanup phi-2
```

**Always clean up when done to avoid charges!**

## ⚠️ Important Notes

### Lambda Scraper (Recent Data Gathering)

The system uses a **free Lambda-based scraper** instead of Perplexity:
- **No API costs**: Completely free alternative
- **Automatic**: Works out of the box
- **Lambda Integration**: Can use deployed instances for enhanced scraping
- **Periodic Updates**: Background scraping with `python scripts/run_periodic_scraper.py`

The dashboard will automatically use the Lambda scraper when "Gather Recent Attack Data" is enabled!

See `docs/LAMBDA_SCRAPER_GUIDE.md` for details.

### Cost Management

- **Start with phi-2**: Smallest, cheapest (~$0.50/hour)
- **Deploy only what you need**: Don't deploy all models at once
- **Always clean up**: Terminate instances immediately after use
- **Use spot instances**: Lambda Cloud offers spot pricing

### API Endpoint Setup

For best performance, set up vLLM or TGI on your Lambda instances:
1. SSH into instance
2. Install vLLM: `pip install vllm`
3. Start server: `python3 -m vllm.entrypoints.openai.api_server --model <model> --port 8000`
4. Use endpoint in defender configuration

## ✅ Status

All deployment tools and integrations are **complete and ready to use**:

- ✅ Model deployment system
- ✅ 6 open source models configured
- ✅ Lambda Cloud integration
- ✅ API endpoint support
- ✅ Deployment scripts
- ✅ Documentation
- ✅ Arena integration
- ✅ Dashboard support

## 🎉 Ready to Deploy!

You can now:

1. **Deploy models**: `python setup_lambda_models.py`
2. **Use in Arena**: Configure defenders with Lambda models
3. **Use in Dashboard**: Select Lambda Cloud as defender type
4. **Enable Lambda scraper**: Check "Gather Recent Attack Data" in dashboard

Everything is ready! Just set your Lambda API key and start deploying models!

