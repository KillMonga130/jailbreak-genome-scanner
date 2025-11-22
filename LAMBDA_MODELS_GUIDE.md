# Lambda.ai Model Management Guide

## Quick Start - Deploy and Use Open Source Models

### Available Models (No Authentication Required)

1. **phi-2** - Small, fast, capable (2.7B) - Recommended for testing
2. **mistral-7b-instruct** - High quality responses - Recommended for production
3. **qwen-7b-chat** - Multilingual support
4. **falcon-7b-instruct** - Good for instructions

## Usage

### List Available Models
```bash
python scripts/manage_lambda_models.py list
```

### Switch to a Model
```bash
python scripts/manage_lambda_models.py switch --model phi-2
python scripts/manage_lambda_models.py switch --model mistral-7b-instruct
```

### Check Model Status
```bash
python scripts/manage_lambda_models.py status
```

### Use in Your Application

Once a model is running, use this endpoint:

```
http://150.136.146.143:8000/v1/completions
```

Or with SSH tunnel:
```
http://localhost:8000/v1/completions
```

**Example API Call:**
```python
import httpx

response = httpx.post(
    "http://150.136.146.143:8000/v1/completions",
    json={
        "model": "microsoft/phi-2",
        "prompt": "What is the capital of France?",
        "max_tokens": 50,
        "temperature": 0.7
    },
    timeout=30.0
)

data = response.json()
print(data["choices"][0]["text"])
```

### Dashboard Configuration

1. **Model Name**: Use the full model name (e.g., `microsoft/phi-2`, `mistralai/Mistral-7B-Instruct-v0.2`)
2. **API Endpoint**: `http://150.136.146.143:8000/v1/completions`
3. **Instance ID**: `f401d9d6a1e649b2a74be9a2959a828a`

## Model Switching Workflow

1. **Stop current model** (if running):
   ```bash
   python scripts/manage_lambda_models.py switch --model phi-2
   ```

2. **Start new model**:
   ```bash
   python scripts/manage_lambda_models.py switch --model mistral-7b-instruct
   ```

3. **Wait for model to load** (2-5 minutes depending on model size)

4. **Update your application** with new model name and endpoint

5. **Test connection**:
   ```bash
   python test_vllm_query.py http://150.136.146.143:8000/v1/completions mistralai/Mistral-7B-Instruct-v0.2
   ```

## Multiple Models (Future)

To run multiple models simultaneously:
- Use different ports (8000, 8001, 8002, etc.)
- Configure multiple instances
- Use load balancing

## Troubleshooting

### Model Not Loading
```bash
ssh -i moses.pem ubuntu@150.136.146.143 'tail -50 /tmp/vllm.log'
```

### Check if vLLM is Running
```bash
ssh -i moses.pem ubuntu@150.136.146.143 'pgrep -f vllm'
```

### Restart vLLM
```bash
python scripts/manage_lambda_models.py switch --model phi-2
```

### Check Health
```bash
ssh -i moses.pem ubuntu@150.136.146.143 'curl http://localhost:8000/health'
```

## Integration with Your Application

The system automatically updates `data/lambda_deployments.json` with:
- Current model name
- API endpoint
- Instance status

Your application can read this file to get the current configuration.

