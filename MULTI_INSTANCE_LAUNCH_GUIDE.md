# 🚀 Multi-Instance Launch Guide

Launch multiple Lambda Cloud instances with different models for parallel evaluation.

## Quick Start

### Launch Multiple Models

```bash
# Launch 3 models in parallel
python scripts/launch_multiple_instances.py launch --models phi-2 mistral-7b-instruct qwen-7b-chat --parallel

# Launch sequentially (safer, slower)
python scripts/launch_multiple_instances.py launch --models phi-2 mistral-7b-instruct
```

### List Launched Instances

```bash
python scripts/launch_multiple_instances.py list
```

### Terminate Instances

```bash
# Terminate a specific instance
python scripts/launch_multiple_instances.py terminate --instance-id <instance_id>

# Terminate all instances (requires confirmation)
python scripts/launch_multiple_instances.py terminate-all --confirm
```

---

## Available Models

| Model Key | Description | Instance Type | Cost/Hour |
|-----------|-------------|---------------|-----------|
| `phi-2` | Phi-2 - Small, fast, capable (2.7B) | gpu_1x_a10 | $0.75 |
| `mistral-7b-instruct` | Mistral 7B Instruct - High quality | gpu_1x_a10 | $0.75 |
| `qwen-7b-chat` | Qwen 7B Chat - Multilingual | gpu_1x_a10 | $0.75 |
| `falcon-7b-instruct` | Falcon 7B Instruct | gpu_1x_a10 | $0.75 |
| `llama-2-7b-chat` | Llama 2 7B Chat | gpu_1x_a10 | $0.75 |
| `llama-2-13b-chat` | Llama 2 13B Chat | gpu_1x_a100 | $1.29 |

---

## Complete Workflow

### Step 1: Launch Instances

```bash
python scripts/launch_multiple_instances.py launch \
    --models phi-2 mistral-7b-instruct qwen-7b-chat \
    --parallel \
    --region us-east-1
```

**Output:**
```
🚀 Launching 3 instances...
✅ Instance launched: instance_abc123
✅ Instance ready! IP: 150.136.146.143
📝 Deployment info saved
   Model: microsoft/phi-2
   Instance ID: instance_abc123
   IP: 150.136.146.143
   API Endpoint: http://150.136.146.143:8000/v1/chat/completions
   ⚠️  Remember to set up vLLM: python scripts/setup_vllm_on_lambda.py --ip 150.136.146.143 --key moses.pem --model microsoft/phi-2
```

### Step 2: Set Up vLLM on Each Instance

For each launched instance, set up vLLM:

```bash
# Instance 1: phi-2
python scripts/setup_vllm_on_lambda.py --ip 150.136.146.143 --key moses.pem --model microsoft/phi-2

# Instance 2: mistral-7b-instruct
python scripts/setup_vllm_on_lambda.py --ip 150.136.146.144 --key moses.pem --model mistralai/Mistral-7B-Instruct-v0.2

# Instance 3: qwen-7b-chat
python scripts/setup_vllm_on_lambda.py --ip 150.136.146.145 --key moses.pem --model Qwen/Qwen-7B-Chat
```

### Step 3: Use in Dashboard

The dashboard will automatically detect launched instances from `data/lambda_deployments.json`.

Or manually configure:

```python
# Defender 1: phi-2
defender1 = LLMDefender(
    model_name="microsoft/phi-2",
    model_type="local",
    use_lambda=True,
    lambda_instance_id="instance_abc123",
    lambda_api_endpoint="http://150.136.146.143:8000/v1/chat/completions"
)

# Defender 2: mistral-7b-instruct
defender2 = LLMDefender(
    model_name="mistralai/Mistral-7B-Instruct-v0.2",
    model_type="local",
    use_lambda=True,
    lambda_instance_id="instance_def456",
    lambda_api_endpoint="http://150.136.146.144:8000/v1/chat/completions"
)
```

### Step 4: Check Status

```bash
python scripts/launch_multiple_instances.py list
```

**Output:**
```
📋 LAUNCHED INSTANCES
======================================================================

✅ phi-2
   Model: microsoft/phi-2
   Instance ID: instance_abc123
   IP: 150.136.146.143
   Status: ACTIVE
   Cost: $0.75/hour
   Launched: 2024-11-23T10:30:00
   API: http://150.136.146.143:8000/v1/chat/completions

✅ mistral-7b-instruct
   Model: mistralai/Mistral-7B-Instruct-v0.2
   Instance ID: instance_def456
   IP: 150.136.146.144
   Status: ACTIVE
   Cost: $0.75/hour
   Launched: 2024-11-23T10:31:00
   API: http://150.136.146.144:8000/v1/chat/completions

Total active instances: 2
Total cost per hour: $1.50

⚠️  Remember to terminate instances when done!
```

### Step 5: Terminate When Done

```bash
# Terminate all instances
python scripts/launch_multiple_instances.py terminate-all --confirm
```

---

## Cost Management

### Example Costs

**Launching 3 models (all on gpu_1x_a10):**
- Total cost: **$2.25/hour**
- Per day (24h): **$54.00**
- Per week: **$378.00**

**Launching 5 models:**
- Total cost: **$3.75/hour** (if all on A10)
- Per day: **$90.00**

### Cost Saving Tips

1. **Terminate immediately after use**
   ```bash
   python scripts/launch_multiple_instances.py terminate-all --confirm
   ```

2. **Use smallest instances for testing**
   - Start with `gpu_1x_a10` ($0.75/hr)
   - Only upgrade when needed

3. **Launch only what you need**
   - Don't launch all models at once
   - Launch 2-3 models for parallel evaluation

4. **Monitor usage**
   ```bash
   python scripts/launch_multiple_instances.py list
   ```

---

## Parallel vs Sequential Launch

### Parallel Launch (Faster)
```bash
python scripts/launch_multiple_instances.py launch --models phi-2 mistral-7b-instruct --parallel
```
- ✅ Faster (all instances launch simultaneously)
- ⚠️ More API calls at once
- ⚠️ May hit rate limits if launching many

### Sequential Launch (Safer)
```bash
python scripts/launch_multiple_instances.py launch --models phi-2 mistral-7b-instruct
```
- ✅ Safer (one at a time)
- ✅ Better for many instances
- ⚠️ Slower (5-10 min per instance)

---

## Troubleshooting

### Problem: Instance launch failed

**Solution:**
- Check Lambda Cloud dashboard for availability
- Try different region: `--region us-west-1`
- Check API key in `.env` file

### Problem: Instance not ready after launch

**Solution:**
- Instances take 2-5 minutes to boot
- Check status: `python scripts/launch_multiple_instances.py list`
- Verify in Lambda Cloud dashboard

### Problem: vLLM setup fails

**Solution:**
- Wait for instance to be fully active
- Check SSH key: `moses.pem` exists
- Verify IP address is correct
- Check instance logs via SSH

### Problem: High costs

**Solution:**
- Always terminate when done
- Use `terminate-all` to clean up
- Monitor with `list` command
- Set up billing alerts in Lambda Cloud

---

## Advanced Usage

### Launch with Custom Instance Types

Edit `scripts/launch_multiple_instances.py` to change instance types:

```python
AVAILABLE_MODELS = {
    "phi-2": {
        "model_name": "microsoft/phi-2",
        "instance_type": "gpu_1x_a100",  # Changed from gpu_1x_a10
        ...
    }
}
```

### Launch in Different Regions

```bash
python scripts/launch_multiple_instances.py launch \
    --models phi-2 mistral-7b-instruct \
    --region us-west-1
```

### Check Specific Instance

```bash
# List all instances
python scripts/launch_multiple_instances.py list

# Find your instance ID, then check in Lambda Cloud dashboard
```

---

## Integration with Dashboard

The dashboard automatically loads launched instances from `data/lambda_deployments.json`.

1. Launch instances: `python scripts/launch_multiple_instances.py launch --models phi-2 mistral-7b-instruct`
2. Set up vLLM on each instance
3. Open dashboard: `streamlit run dashboard/arena_dashboard.py`
4. Instances appear in "Lambda Instance ID" dropdown

---

## Next Steps

1. ✅ Launch instances: `python scripts/launch_multiple_instances.py launch --models phi-2 mistral-7b-instruct`
2. ✅ Set up vLLM: `python scripts/setup_vllm_on_lambda.py --ip <ip> --key moses.pem --model <model>`
3. ✅ Use in dashboard or code
4. ✅ Terminate when done: `python scripts/launch_multiple_instances.py terminate-all --confirm`

---

**Ready to launch! 🚀**

