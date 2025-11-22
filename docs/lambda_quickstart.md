# Lambda Cloud Quick Start

## Setting Up Your API Key

1. Get your Lambda Cloud API secret from your account dashboard
2. Add it to your `.env` file:

```env
LAMBDA_API_KEY=secret_muele_ce33a3396f9d406583bb611dc3ab0bd9.v5H38gHQqPMfwcPjXaIR6QKer9FglUZg
```

3. Test your connection:

```bash
python examples/test_lambda_connection.py
```

## Using Lambda Cloud in Code

### Basic Usage

```python
from src.integrations.lambda_cloud import LambdaCloudClient

# Initialize client
client = LambdaCloudClient()

# List your instances
instances = await client.list_instances()
print(f"You have {len(instances)} instances")

# Launch an instance
instance_data = await client.launch_instance(
    instance_type="gpu_1x_a10",
    region="us-east-1"
)

instance_id = instance_data["instance_ids"][0]
print(f"Launched instance: {instance_id}")
```

### Using Lambda for Model Evaluation

```python
from src.integrations.lambda_cloud import LambdaModelRunner
from src.defenders.llm_defender import LLMDefender

# Set up Lambda instance for model
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

# Use in arena evaluation
response = await defender.generate_response("Test prompt")
```

## API Authentication

Lambda Cloud uses HTTP Basic Authentication:
- Username: Your API secret (e.g., `secret_xxx.xxx`)
- Password: Empty string

The curl command format:
```bash
curl -u secret_xxx.xxx: https://cloud.lambda.ai/api/v1/instances
```

## Available Instance Types

Common Lambda Cloud instance types:

- `gpu_1x_a10` - 1x NVIDIA A10 (24GB) - $0.50/hr
- `gpu_1x_a100` - 1x NVIDIA A100 (40GB) - $1.10/hr
- `gpu_8x_a100` - 8x NVIDIA A100 - $8.80/hr
- `gpu_1x_h100` - 1x NVIDIA H100 (80GB) - $4.00/hr

## Important Notes

⚠️ **Always terminate instances when done** to avoid charges!

```python
await client.terminate_instance(instance_id)
```

## Testing Connection

Run the test script to verify your API key works:

```bash
python examples/test_lambda_connection.py
```

This will:
1. Check if your API key is configured
2. List your current instances
3. Test API connectivity

