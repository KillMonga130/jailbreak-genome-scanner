# 🚀 Lambda Deployment System - Ready to Deploy!

## Quick Start

### 1. Set Lambda API Key

Add to your `.env` file:
```env
LAMBDA_API_KEY=secret_xxx.xxx
```

Get your API key from: https://lambdalabs.com/cloud

### 2. Deploy a Model

**Interactive Setup (Recommended):**
```bash
python setup_lambda_models.py
```

**Or deploy specific model:**
```bash
# Deploy smallest model (phi-2) - recommended for testing
python deploy_models.py deploy phi-2

# Or deploy llama-2-7b-chat
python deploy_models.py deploy llama-2-7b-chat
```

### 3. List Deployed Models

```bash
python deploy_models.py deployed
```

This shows all deployed models with their instance IDs.

### 4. Use in Arena

```python
from src.defenders.llm_defender import LLMDefender

# Get instance ID from: python deploy_models.py deployed
defender = LLMDefender(
    model_name="meta-llama/Llama-2-7b-chat-hf",
    model_type="local",
    use_lambda=True,
    lambda_instance_id="instance_123",
    lambda_api_endpoint="http://<ip>:8000/v1/chat/completions"  # If using vLLM
)
```

### 5. Use in Dashboard

1. Run: `streamlit run dashboard/arena_dashboard.py`
2. Select "Lambda Cloud" as defender type
3. Enter model name
4. Enter instance ID (from `deploy_models.py deployed`)
5. Optionally enter API endpoint
6. Enable "Gather Recent Attack Data" (uses Lambda scraper)
7. Click "START EVALUATION"

### 6. Clean Up When Done

```bash
# Clean up specific model
python deploy_models.py cleanup phi-2

# Clean up all models
python deploy_models.py cleanup-all
```

**Always clean up to avoid charges!**

## Available Models

| Model Key | Model Name | Instance | Cost/Hour | Recommended For |
|-----------|------------|----------|-----------|-----------------|
| **phi-2** | microsoft/phi-2 | gpu_1x_a10 | ~$0.50 | ⭐ Testing |
| **llama-2-7b-chat** | meta-llama/Llama-2-7b-chat-hf | gpu_1x_a10 | ~$0.50 | Development |
| **mistral-7b-instruct** | mistralai/Mistral-7B-Instruct-v0.2 | gpu_1x_a10 | ~$0.50 | High Quality |
| **falcon-7b-instruct** | tiiuae/falcon-7b-instruct | gpu_1x_a10 | ~$0.50 | Instructions |
| **qwen-7b-chat** | Qwen/Qwen-7B-Chat | gpu_1x_a10 | ~$0.50 | Multilingual |
| **llama-2-13b-chat** | meta-llama/Llama-2-13b-chat-hf | gpu_1x_a100 | ~$1.10 | Better Quality |

## Lambda Scraper (Recent Data Gathering)

The system includes a **free Lambda-based scraper** for gathering recent jailbreak events:

- **No API costs**: Free alternative to Perplexity
- **Automatic**: Works in dashboard when enabled
- **Periodic**: Run `python scripts/run_periodic_scraper.py` for background updates
- **Lambda Integration**: Can use deployed instances for enhanced scraping

See `docs/LAMBDA_SCRAPER_GUIDE.md` for details.

## API Endpoint Setup (Optional)

For best performance, set up vLLM on your Lambda instance:

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

## Cost Management

- **Start with phi-2**: Smallest, cheapest model
- **Deploy only what you need**: Don't deploy all models at once
- **Always clean up**: Terminate instances immediately after use
- **Monitor usage**: Check Lambda Cloud dashboard regularly

## Status

✅ **Deployment system**: Complete and ready
✅ **6 models configured**: Ready to deploy
✅ **Integration**: Arena and dashboard ready
✅ **Documentation**: Complete
✅ **Scripts**: Working
✅ **Lambda scraper**: Integrated and ready

## Next Steps

1. Set `LAMBDA_API_KEY` in `.env`
2. Run `python setup_lambda_models.py`
3. Deploy a model (start with phi-2)
4. Use in Arena or Dashboard
5. Clean up when done!

Everything is ready to deploy! 🎉

