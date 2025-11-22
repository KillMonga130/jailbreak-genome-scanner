# Lambda Cloud Setup Guide

This guide explains how to use Lambda Cloud infrastructure for GPU-accelerated model evaluation in the Jailbreak Genome Scanner & Arena System.

## Overview

Lambda Cloud provides on-demand GPU instances that can be used to:
- Run local LLM models for evaluation
- Accelerate inference for large models
- Scale evaluations across multiple GPUs
- Reduce API costs by running models locally

## Prerequisites

1. **Lambda Cloud Account**: Sign up at [lambdalabs.com](https://lambdalabs.com)
2. **API Key**: Get your API key from the Lambda Cloud dashboard
3. **SSH Key**: Set up SSH keys for instance access (optional, for direct SSH)

## Configuration

Add your Lambda Cloud credentials to `.env`:

```env
# Lambda Cloud Configuration
LAMBDA_API_KEY=your_lambda_api_key_here
LAMBDA_DEFAULT_INSTANCE_TYPE=gpu_1x_a10
LAMBDA_DEFAULT_REGION=us-east-1
```

## Available Instance Types

Common Lambda Cloud instance types:

- `gpu_1x_a10` - 1x NVIDIA A10 (24GB) - Good for smaller models
- `gpu_1x_a100` - 1x NVIDIA A100 (40GB) - For medium models
- `gpu_8x_a100` - 8x NVIDIA A100 - For large-scale evaluation
- `gpu_1x_h100` - 1x NVIDIA H100 (80GB) - For very large models

## Usage

### Basic Usage

```python
from src.integrations.lambda_cloud import LambdaModelRunner
from src.defenders.llm_defender import LLMDefender

# Set up Lambda instance
runner = LambdaModelRunner()
instance_id = await runner.setup_model_environment(
    instance_type="gpu_1x_a10",
    model_name="meta-llama/Llama-2-7b-chat-hf"
)

# Create defender using Lambda
defender = LLMDefender(
    model_name="meta-llama/Llama-2-7b-chat-hf",
    model_type="local",
    use_lambda=True,
    lambda_instance_id=instance_id
)

# Use defender in evaluation
response = await defender.generate_response("Test prompt")
```

### With Arena

```python
from src.arena.jailbreak_arena import JailbreakArena
from src.defenders.llm_defender import LLMDefender

arena = JailbreakArena()

# Add Lambda-powered defender
defender = LLMDefender(
    model_name="meta-llama/Llama-2-7b-chat-hf",
    model_type="local",
    use_lambda=True,
    lambda_instance_id=instance_id
)

arena.add_defender(defender)

# Run evaluation
results = await arena.evaluate(rounds=100)
```

## Instance Management

### List Instances

```python
from src.integrations.lambda_cloud import LambdaCloudClient

client = LambdaCloudClient()
instances = await client.list_instances()
for instance in instances:
    print(f"Instance {instance['id']}: {instance['status']}")
```

### Launch Instance

```python
instance_data = await client.launch_instance(
    instance_type="gpu_1x_a10",
    region="us-east-1",
    quantity=1
)
instance_id = instance_data["instance_ids"][0]
```

### Terminate Instance

```python
success = await client.terminate_instance(instance_id)
```

## Cost Optimization

1. **Use Spot Instances**: Lambda Cloud offers spot pricing for lower costs
2. **Auto-terminate**: Always clean up instances after evaluation
3. **Batch Evaluations**: Run multiple evaluations on the same instance
4. **Right-sizing**: Choose instance type based on model size

## Best Practices

1. **Always Clean Up**: Terminate instances when done to avoid charges
2. **Monitor Usage**: Check Lambda Cloud dashboard for usage and costs
3. **SSH Access**: Use SSH for debugging and manual model setup
4. **Model Caching**: Cache models on instances to avoid re-downloading

## Troubleshooting

### Instance Not Starting
- Check API key is valid
- Verify instance type availability in region
- Check Lambda Cloud status page

### SSH Connection Issues
- Ensure SSH key is configured in Lambda Cloud dashboard
- Check instance IP and firewall settings
- Verify instance is in "active" status

### Model Loading Errors
- Ensure sufficient GPU memory for model
- Check model path and permissions
- Verify CUDA/GPU drivers on instance

## Example: Full Evaluation Pipeline

```python
import asyncio
from src.integrations.lambda_cloud import LambdaModelRunner
from src.arena.jailbreak_arena import JailbreakArena
from src.defenders.llm_defender import LLMDefender

async def run_lambda_evaluation():
    # Set up Lambda
    runner = LambdaModelRunner()
    instance_id = await runner.setup_model_environment(
        instance_type="gpu_1x_a10",
        model_name="meta-llama/Llama-2-7b-chat-hf"
    )
    
    try:
        # Create defender
        defender = LLMDefender(
            model_name="meta-llama/Llama-2-7b-chat-hf",
            model_type="local",
            use_lambda=True,
            lambda_instance_id=instance_id
        )
        
        # Run evaluation
        arena = JailbreakArena()
        arena.add_defender(defender)
        results = await arena.evaluate(rounds=100)
        
        # Get JVI score
        jvi = results.get_jvi_score()
        print(f"JVI Score: {jvi}")
        
    finally:
        # Always clean up
        await runner.cleanup_instance(instance_id)

# Run
asyncio.run(run_lambda_evaluation())
```

## Additional Resources

- [Lambda Cloud Documentation](https://docs.lambdalabs.com)
- [Lambda Cloud API Reference](https://docs.lambdalabs.com/cloud-api)
- [Lambda Cloud Pricing](https://lambdalabs.com/pricing)

