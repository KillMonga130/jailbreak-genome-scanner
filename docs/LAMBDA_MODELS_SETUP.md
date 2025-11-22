# Lambda Cloud Model Deployment Guide

## Overview

This guide explains how to deploy open source models on Lambda Cloud for use in the Jailbreak Arena.

**Note**: Perplexity is not open source, so you'll need to set up your own Perplexity API key separately.

## Available Open Source Models

We support these open source models on Lambda Cloud:

| Model | Instance Type | Memory | Description |
|-------|---------------|--------|-------------|
| **llama-2-7b-chat** | gpu_1x_a10 | 14 GB | Llama 2 7B Chat - Good for testing |
| **llama-2-13b-chat** | gpu_1x_a100 | 26 GB | Llama 2 13B Chat - Better capabilities |
| **mistral-7b-instruct** | gpu_1x_a10 | 14 GB | Mistral 7B Instruct - High quality |
| **phi-2** | gpu_1x_a10 | 5 GB | Phi-2 - Small but capable |
| **falcon-7b-instruct** | gpu_1x_a10 | 14 GB | Falcon 7B Instruct - Good for instructions |
| **qwen-7b-chat** | gpu_1x_a10 | 14 GB | Qwen 7B Chat - Multilingual |

## Quick Start

### 1. List Available Models

```bash
python deploy_models.py list
```

This shows all available models and their requirements.

### 2. Deploy a Model

```bash
python deploy_models.py deploy llama-2-7b-chat
```

This will:
- Launch a Lambda Cloud instance
- Download the model
- Set up the environment
- Return an instance ID

### 3. Use Deployed Model

```python
from src.defenders.llm_defender import LLMDefender

# Use deployed model
defender = LLMDefender(
    model_name="meta-llama/Llama-2-7b-chat-hf",
    model_type="local",
    use_lambda=True,
    lambda_instance_id="your_instance_id"
)

# Use in Arena
arena = JailbreakArena()
arena.add_defender(defender)
results = await arena.evaluate(rounds=10)
```

### 4. List Deployed Models

```bash
python deploy_models.py deployed
```

Shows all currently deployed models with their instance IDs.

### 5. Clean Up Model

```bash
python deploy_models.py cleanup llama-2-7b-chat
```

**Important**: Always clean up instances when done to avoid charges!

## Deployment Commands

### Deploy Single Model

```bash
# Deploy Llama 2 7B
python deploy_models.py deploy llama-2-7b-chat

# Deploy Mistral 7B
python deploy_models.py deploy mistral-7b-instruct

# Deploy Phi-2 (smallest, cheapest)
python deploy_models.py deploy phi-2
```

### Deploy All Models

```bash
python deploy_models.py deploy-all
```

**Warning**: This will deploy all 6 models and incur significant charges (~$3-8/hour total).

### List Deployed Models

```bash
python deploy_models.py deployed
```

### Clean Up

```bash
# Clean up single model
python deploy_models.py cleanup llama-2-7b-chat

# Clean up all models
python deploy_models.py cleanup-all
```

## Using Deployed Models in Code

### In Arena

```python
from src.arena.jailbreak_arena import JailbreakArena
from src.defenders.llm_defender import LLMDefender
from src.integrations.lambda_models import LambdaModelDeployment

# Get instance ID for deployed model
deployment = LambdaModelDeployment()
instance_id = await deployment.get_model_instance("llama-2-7b-chat")

# Create defender
defender = LLMDefender(
    model_name="meta-llama/Llama-2-7b-chat-hf",
    model_type="local",
    use_lambda=True,
    lambda_instance_id=instance_id
)

# Use in Arena
arena = JailbreakArena()
arena.add_defender(defender)
arena.generate_attackers(num_strategies=10)
results = await arena.evaluate(rounds=100)
```

### In Dashboard

1. Select "Lambda Cloud" as defender type
2. Enter model name (e.g., `meta-llama/Llama-2-7b-chat-hf`)
3. Enter instance ID (from `python deploy_models.py deployed`)
4. Start battle

## Cost Management

### Estimated Costs (per hour)

| Model | Instance Type | Cost/Hour |
|-------|---------------|-----------|
| llama-2-7b-chat | gpu_1x_a10 | ~$0.50 |
| mistral-7b-instruct | gpu_1x_a10 | ~$0.50 |
| phi-2 | gpu_1x_a10 | ~$0.50 |
| llama-2-13b-chat | gpu_1x_a100 | ~$1.10 |
| falcon-7b-instruct | gpu_1x_a10 | ~$0.50 |
| qwen-7b-chat | gpu_1x_a10 | ~$0.50 |

### Best Practices

1. **Deploy only what you need**: Don't deploy all models at once
2. **Use smaller models for testing**: Phi-2 or Llama-2-7B are good starting points
3. **Always clean up**: Terminate instances immediately after use
4. **Monitor usage**: Check Lambda Cloud dashboard regularly
5. **Use spot instances**: Lambda Cloud offers spot pricing (lower cost)

## Model Comparison

### For Testing/Development
- **phi-2**: Smallest, cheapest, fast inference
- **llama-2-7b-chat**: Good balance of cost and quality

### For Production
- **mistral-7b-instruct**: High quality responses
- **llama-2-13b-chat**: Better capabilities (higher cost)

### For Multilingual
- **qwen-7b-chat**: Multilingual support

## Troubleshooting

### Model Not Deploying
- Check Lambda Cloud API key
- Verify instance type availability
- Check region availability
- Review Lambda Cloud status

### Instance Not Ready
- Wait 2-5 minutes for instance to become active
- Check instance status: `python deploy_models.py deployed`
- Verify SSH connection works

### Model Loading Errors
- Ensure sufficient GPU memory
- Check model path and permissions
- Verify CUDA/GPU drivers

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

## Next Steps

1. **Deploy a model**: Start with phi-2 or llama-2-7b-chat
2. **Test in Arena**: Run a quick evaluation
3. **Deploy more**: Add models as needed
4. **Clean up**: Always terminate when done

## Perplexity Setup (Separate)

Since Perplexity is not open source, you'll need to:

1. Sign up for Perplexity API at [perplexity.ai](https://www.perplexity.ai)
2. Get your API key from the dashboard
3. Add to `.env`:
   ```env
   PERPLEXITY_API_KEY=your_perplexity_key_here
   ```

The system will automatically use Perplexity for recent data gathering when the key is configured.

