# 🚀 Model Deployment Guide - Lambda Cloud

## Overview

This guide explains how to deploy open source models on Lambda Cloud for use in the Jailbreak Arena.

**Note**: Perplexity is not open source, so you'll set up your own Perplexity API key separately (already noted).

## Quick Start

### 1. Interactive Setup (Easiest)

```bash
python setup_lambda_models.py
```

This will:
- Show available models
- Check existing deployments
- Help you deploy models interactively
- Save configuration automatically

### 2. Deploy Specific Model

```bash
python deploy_models.py deploy phi-2
```

**Recommended for testing**: Start with `phi-2` (smallest, cheapest)

### 3. List Deployed Models

```bash
python deploy_models.py deployed
```

This shows all deployed models with their instance IDs.

## Available Models

| Model Key | Model Name | Instance Type | Cost/Hour | Use Case |
|-----------|------------|---------------|-----------|----------|
| **phi-2** | microsoft/phi-2 | gpu_1x_a10 | ~$0.50 | Testing |
| **llama-2-7b-chat** | meta-llama/Llama-2-7b-chat-hf | gpu_1x_a10 | ~$0.50 | Development |
| **mistral-7b-instruct** | mistralai/Mistral-7B-Instruct-v0.2 | gpu_1x_a10 | ~$0.50 | High Quality |
| **falcon-7b-instruct** | tiiuae/falcon-7b-instruct | gpu_1x_a10 | ~$0.50 | Instructions |
| **qwen-7b-chat** | Qwen/Qwen-7B-Chat | gpu_1x_a10 | ~$0.50 | Multilingual |
| **llama-2-13b-chat** | meta-llama/Llama-2-13b-chat-hf | gpu_1x_a100 | ~$1.10 | Better Quality |

## Deployment Commands

### Deploy Models

```bash
# Deploy single model
python deploy_models.py deploy llama-2-7b-chat

# Deploy all models (⚠️ expensive - ~$3-8/hour)
python deploy_models.py deploy-all

# List available models
python deploy_models.py list
```

### Manage Deployments

```bash
# List deployed models
python deploy_models.py deployed

# Clean up single model
python deploy_models.py cleanup llama-2-7b-chat

# Clean up all models
python deploy_models.py cleanup-all
```

## Using Deployed Models

### Option 1: In Code (with API endpoint)

After deploying and setting up an API server on the instance:

```python
from src.defenders.llm_defender import LLMDefender
from src.arena.jailbreak_arena import JailbreakArena

# Get instance ID from deployment
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

### Option 2: In Dashboard

1. Launch dashboard: `streamlit run dashboard/arena_dashboard.py`
2. Select "Lambda Cloud" as defender type
3. Enter model name: `meta-llama/Llama-2-7b-chat-hf`
4. Enter instance ID: (from `python deploy_models.py deployed`)
5. Enter API endpoint: `http://<instance_ip>:8000/v1/chat/completions` (if using vLLM)
6. Start battle!

### Option 3: Without API Endpoint (SSH-based)

If you prefer SSH-based inference (needs implementation):

```python
defender = LLMDefender(
    model_name="meta-llama/Llama-2-7b-chat-hf",
    model_type="local",
    use_lambda=True,
    lambda_instance_id=instance_id
    # No API endpoint - will use SSH (placeholder for now)
)
```

## Setting Up API Server on Lambda Instance

After deploying a model, you need to set up an inference server:

### Step 1: SSH into Instance

```bash
# Get SSH command
python -c "from src.integrations.lambda_cloud import LambdaCloudClient; import asyncio; client = LambdaCloudClient(); instances = asyncio.run(client.list_instances()); print(client.get_ssh_command(instances[0]) if instances else 'No instances')"
```

### Step 2: Install vLLM (Recommended)

```bash
# On the Lambda instance
pip install vllm
python3 -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-2-7b-chat-hf \
    --port 8000 \
    --host 0.0.0.0
```

### Step 3: Use API Endpoint

The API will be available at: `http://<instance_ip>:8000/v1/chat/completions`

Use this endpoint in your defender configuration.

## Configuration File

Deployment configuration is saved to `data/lambda_deployments.json`:

```json
{
  "deployed_models": {
    "llama-2-7b-chat": {
      "instance_id": "instance_123",
      "model_name": "meta-llama/Llama-2-7b-chat-hf",
      "instance_type": "gpu_1x_a10",
      "status": "active"
    }
  }
}
```

## Cost Management

### Recommended Approach

1. **Start with phi-2**: Smallest, cheapest model (~$0.50/hour)
2. **Deploy only what you need**: Don't deploy all models at once
3. **Always clean up**: Terminate instances immediately after use
4. **Use spot instances**: Lambda Cloud offers spot pricing (lower cost)

### Estimated Costs

- **Single model (A10)**: ~$0.50/hour = ~$12/day if running 24/7
- **Single model (A100)**: ~$1.10/hour = ~$26/day if running 24/7
- **All 6 models (A10)**: ~$3.00/hour = ~$72/day if running 24/7

**Important**: Always clean up instances when done!

## Troubleshooting

### Deployment Fails
- Check Lambda API key in `.env`
- Verify instance type availability
- Check region availability

### Instance Not Ready
- Wait 2-5 minutes after launch
- Check status: `python deploy_models.py deployed`

### API Endpoint Not Working
- Verify vLLM/TGI is running on instance
- Check firewall rules (port 8000)
- Verify instance IP is correct

## Perplexity Note

Since Perplexity is not open source:

1. Sign up at [perplexity.ai](https://www.perplexity.ai)
2. Get your API key
3. Add to `.env`:
   ```env
   PERPLEXITY_API_KEY=your_key_here
   ```

The dashboard will automatically use Perplexity for recent data gathering!

## Next Steps

1. ✅ **Deploy model**: `python setup_lambda_models.py`
2. ✅ **Set up API server**: SSH into instance and install vLLM
3. ✅ **Configure endpoint**: Add API endpoint to defender
4. ✅ **Test in Arena**: Run evaluation
5. ✅ **Clean up**: Always terminate instances when done

## Complete Example

```bash
# 1. Deploy model
python deploy_models.py deploy phi-2

# 2. Get instance ID
python deploy_models.py deployed

# 3. SSH into instance (manually)
ssh ubuntu@<instance_ip> -i ~/.ssh/lambda_key

# 4. On instance, install and run vLLM
pip install vllm
python3 -m vllm.entrypoints.openai.api_server \
    --model microsoft/phi-2 \
    --port 8000 \
    --host 0.0.0.0

# 5. Use in code
python -c "
from src.defenders.llm_defender import LLMDefender
from src.arena.jailbreak_arena import JailbreakArena
import asyncio

async def test():
    defender = LLMDefender(
        model_name='microsoft/phi-2',
        model_type='local',
        use_lambda=True,
        lambda_instance_id='YOUR_INSTANCE_ID',
        lambda_api_endpoint='http://INSTANCE_IP:8000/v1/chat/completions'
    )
    arena = JailbreakArena()
    arena.add_defender(defender)
    results = await arena.evaluate(rounds=10)
    print(f'JVI Score: {results[\"defenders\"][0][\"jvi\"][\"jvi_score\"]:.2f}')

asyncio.run(test())
"

# 6. Clean up when done
python deploy_models.py cleanup phi-2
```

