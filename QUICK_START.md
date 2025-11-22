# 🚀 Quick Start Guide - Jailbreak Arena

## Deploy Models on Lambda Cloud

### 1. Interactive Setup (Recommended)

```bash
python setup_lambda_models.py
```

This will:
- Show available models
- Check existing deployments
- Help you deploy models interactively
- Save configuration automatically

### 2. Deploy Single Model

```bash
python deploy_models.py deploy llama-2-7b-chat
```

Or deploy the smallest model (phi-2):

```bash
python deploy_models.py deploy phi-2
```

### 3. List Deployed Models

```bash
python deploy_models.py deployed
```

This shows all deployed models with their instance IDs.

### 4. Use in Arena

```python
from src.arena.jailbreak_arena import JailbreakArena
from src.defenders.llm_defender import LLMDefender

# Get instance ID from deployment
instance_id = "your_instance_id_here"  # From deploy_models.py deployed

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

## Lambda Scraper (Recent Data Gathering)

The system uses a free Lambda-based scraper instead of Perplexity:

1. **Automatic**: Works out of the box - no API keys needed
2. **Optional Enhancement**: Use a deployed Lambda instance for more powerful scraping
3. **Periodic Updates**: Run `python scripts/run_periodic_scraper.py` for background scraping

The dashboard will automatically use the Lambda scraper when "Gather Recent Attack Data" is enabled!

## Run Gamified Dashboard

```bash
streamlit run dashboard/arena_dashboard.py
```

Then:
1. Select "Lambda Cloud" defender
2. Enter model name
3. Enter instance ID (from `deploy_models.py deployed`)
4. Enable "Gather Recent Attack Data" (uses Lambda scraper)
5. Optionally provide Lambda instance ID for enhanced scraping
6. Click "START EVALUATION"

## Next Steps

1. ✅ Deploy models: `python setup_lambda_models.py`
2. ✅ Launch dashboard: `streamlit run dashboard/arena_dashboard.py`
3. ✅ Enable Lambda scraper: Check "Gather Recent Attack Data" in dashboard
4. ✅ Start evaluating: Watch the battle unfold!

## Optional: Periodic Scraping

Run periodic scraper for background updates:

```bash
# Run once
python scripts/run_periodic_scraper.py --once

# Run periodically (every 6 hours)
python scripts/run_periodic_scraper.py --interval-hours 6

# Use Lambda instance for enhanced scraping
python scripts/run_periodic_scraper.py --instance-id instance_123
```

