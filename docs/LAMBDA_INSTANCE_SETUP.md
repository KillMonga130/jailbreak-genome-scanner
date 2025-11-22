# Lambda Cloud Instance Setup Guide

## After Deploying a Model

Once you've deployed a model using `deploy_models.py`, you need to set up the instance for inference.

### Step 1: SSH into Instance

```bash
# Get SSH command
python -c "from src.integrations.lambda_cloud import LambdaCloudClient; import asyncio; client = LambdaCloudClient(); instances = asyncio.run(client.list_instances()); print(client.get_ssh_command(instances[0]))"
```

Or manually:
```bash
ssh ubuntu@<instance_ip> -i ~/.ssh/lambda_key
```

### Step 2: Run Setup Script

Copy the setup script to the instance:

```bash
# From your local machine
scp -i ~/.ssh/lambda_key scripts/setup_lambda_instance.sh ubuntu@<instance_ip>:~/
```

Then on the instance:

```bash
chmod +x setup_lambda_instance.sh
./setup_lambda_instance.sh
```

### Step 3: Start Inference Server

On the Lambda instance, start vLLM:

```bash
source ~/venv/bin/activate
python3 -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-2-7b-chat-hf \
    --port 8000 \
    --host 0.0.0.0
```

Or use Text Generation Inference:

```bash
text-generation-launcher \
    --model-id meta-llama/Llama-2-7b-chat-hf \
    --port 8000 \
    --hostname 0.0.0.0
```

### Step 4: Get API Endpoint

The API will be available at:
```
http://<instance_ip>:8000
```

Use this endpoint in your defender:

```python
defender = LLMDefender(
    model_name="meta-llama/Llama-2-7b-chat-hf",
    model_type="local",
    use_lambda=True,
    lambda_instance_id="instance_123",
    lambda_api_endpoint="http://<instance_ip>:8000/v1/completions"  # or /v1/chat/completions
)
```

## Quick Setup (Automated)

We're working on automating this process. For now, use the manual steps above.

## Recommended Setup

### Option 1: vLLM (Recommended)
- Fast inference
- OpenAI-compatible API
- Easy to use

```bash
pip install vllm
python3 -m vllm.entrypoints.openai.api_server --model <model_name> --port 8000
```

### Option 2: Text Generation Inference
- Production-ready
- Features like flash attention
- Docker support

```bash
pip install text-generation
text-generation-launcher --model-id <model_name> --port 8000
```

## Next Steps

1. Deploy model: `python deploy_models.py deploy llama-2-7b-chat`
2. SSH into instance
3. Run setup script
4. Start inference server
5. Use in Arena with API endpoint

