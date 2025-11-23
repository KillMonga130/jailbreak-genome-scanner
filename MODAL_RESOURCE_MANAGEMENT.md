# Modal.com Resource Management

## Current Usage
- **GPUs**: 10/10 (at limit)
- **Containers**: 11/100
- **Billing**: $1.75 / $30 (6% used)

## Understanding Your Resources

### Why So Many GPUs?
Each Modal function with GPU configuration uses 1 GPU when active. If you have:
- Multiple function deployments (serve, chat_completions, completions)
- Multiple app versions
- Functions that haven't scaled down yet

You could easily hit 10 GPUs.

### Container Count
Containers are the actual running instances. Each function call creates a container, and they scale down after the `scaledown_window` (currently 300 seconds = 5 minutes).

## How to Reduce Usage

### 1. Stop Unused Apps
```bash
# List all apps
python -m modal app list

# Stop specific app (if needed)
python -m modal app stop <app-name>
```

### 2. Check Running Functions
```bash
# View Modal dashboard
python -m modal dashboard
```

### 3. Optimize Scaledown Window
The current `scaledown_window=300` means containers stay alive for 5 minutes after the last request. You can reduce this to save money:
- `scaledown_window=60` = 1 minute (saves more money, but slower cold starts)
- `scaledown_window=300` = 5 minutes (current, good balance)

### 4. Use Only What You Need
- If you only need `chat_completions`, you can remove `serve` and `completions` functions
- Each function uses 1 GPU when active

## Current Deployment
Your current deployment has 3 functions:
- `serve` - Uses 1 GPU
- `chat_completions` - Uses 1 GPU  
- `completions` - Uses 1 GPU

If all 3 are active, that's 3 GPUs. If you have multiple app versions or old deployments, that could explain the 10 GPUs.

## Recommendations

1. **Check Modal Dashboard**: `python -m modal dashboard`
   - See which functions are running
   - Stop any you don't need

2. **Remove Unused Functions**: If you only use `chat_completions`, remove the other two from `modal_deploy.py`

3. **Wait for Scale-Down**: Containers automatically scale down after 5 minutes of inactivity

4. **Monitor Usage**: Keep an eye on the billing dashboard

## Cost Optimization
- Current: $1.75 used (6% of $30 free credits)
- You have plenty of credits left
- Each GPU hour costs ~$0.50-1.00 depending on GPU type (A10G is cheaper)

The good news: You're only using 6% of your free credits, so you have plenty of room! 🎉

