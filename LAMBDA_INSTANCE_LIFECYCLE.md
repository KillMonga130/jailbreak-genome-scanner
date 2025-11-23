# Lambda Instance Lifecycle Management

## Cost Optimization: Start/Stop Instances On Demand

Lambda Cloud charges by the hour for running instances. To save costs, you should **stop instances when not in use**.

## Current Setup

Your Lambda API key has been configured in `.env`:
```
LAMBDA_API_KEY=secret_muele_ce33a3396f9d406583bb611dc3ab0bd9.v5H38gHQqPMfwcPjXaIR6QKer9FglUZg
```

## Your Instances

1. **Mistral 7B**: `129.80.191.122` (Instance ID: `cd6537df1d7640a995090d45eff85e3e`)
2. **Qwen 7B**: `150.136.220.151` 
3. **H100**: `209.20.159.141`

## Managing Instances

### Check Instance Status

```bash
python scripts/manage_lambda_instances.py list
```

### Start Instances (Manual)

**Lambda Cloud doesn't support starting stopped instances via API.** You need to:

1. Go to https://cloud.lambda.ai/instances
2. Find your instance
3. Click "Restart" or "Start" button

**Or use the Lambda Cloud dashboard directly.**

### Stop Instances (Manual)

To save costs when not using instances:

1. Go to https://cloud.lambda.ai/instances
2. Find your instance
3. Click "Stop" button

**Important**: Stopped instances don't charge, but you'll need to manually restart them.

### Terminate Instances (Via API)

If you want to completely remove an instance:

```bash
python scripts/manage_lambda_instances.py terminate <instance_id>
```

**Warning**: This permanently deletes the instance and all data on it!

## Best Practices

### 1. Start Before Use
- Start instances 2-3 minutes before running evaluations
- Wait for status to show "active" and vLLM to be running

### 2. Stop After Use
- Stop instances immediately after evaluations complete
- This saves money - instances charge by the hour even when idle

### 3. Use SSH Tunnels
- Keep SSH tunnels running only when instances are active
- Stop tunnels when instances are stopped

### 4. Monitor Costs
- Check Lambda Cloud dashboard regularly
- Set up billing alerts if available

## Dashboard Integration

The dashboard now:
- ✅ Checks instance status before use
- ✅ Warns if instances are stopped
- ✅ Shows cost-saving tips
- ⚠️ **Note**: Auto-start/stop not available via API (Lambda Cloud limitation)

## Workflow

1. **Before Evaluation:**
   - Start instances in Lambda Cloud dashboard
   - Wait for status: "active"
   - Start SSH tunnels: `.\scripts\setup_ssh_tunnels.ps1`
   - Run evaluation

2. **After Evaluation:**
   - Stop SSH tunnels (Ctrl+C in tunnel windows)
   - Stop instances in Lambda Cloud dashboard
   - Save money! 💰

## Cost Savings Example

- **Running 24/7**: ~$720/month per A10 instance
- **Running 8 hours/day**: ~$240/month per A10 instance
- **Running only when needed**: ~$50-100/month per A10 instance

**You can save 80-90% by stopping instances when not in use!**

