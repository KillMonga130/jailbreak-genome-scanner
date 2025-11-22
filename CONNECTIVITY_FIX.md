# Lambda Cloud API Connectivity Fix Guide

## Problem

Port 8000 on your Lambda instance is blocked by the firewall/security group, causing connection timeouts.

## Quick Fix: SSH Tunnel (Recommended)

The fastest way to get connected without configuring security groups:

### Step 1: Start SSH Tunnel

**Windows:**
```batch
python scripts\ssh_tunnel_helper.py --ip 150.136.146.143 --key moses.pem
```

**Or use the batch file:**
```batch
scripts\start_ssh_tunnel.bat
```

**Linux/Mac:**
```bash
python scripts/ssh_tunnel_helper.py --ip 150.136.146.143 --key moses.pem
```

This will:
- Create an SSH tunnel from `localhost:8000` → `instance:8000`
- Keep running until you press Ctrl+C
- Forward all API requests through the secure tunnel

### Step 2: Update Dashboard Endpoint

In the dashboard, change the API endpoint to:
```
http://localhost:8000/v1/chat/completions
```

### Step 3: Run Evaluation

The dashboard will now connect through the tunnel! Keep the tunnel terminal open while running evaluations.

### Step 4: Stop Tunnel

Press Ctrl+C in the tunnel terminal when done.

## Alternative: Configure Security Group

If you prefer direct access (no tunnel needed):

### Option A: Lambda Cloud Dashboard

1. Go to: https://cloud.lambda.ai/instances
2. Find your instance: `f401d9d6a1e649b2a74be9a2959a828a` or IP `150.136.146.143`
3. Open instance details
4. Find "Security Group" or "Firewall" settings
5. Add inbound rule:
   - **Type:** Custom TCP
   - **Port:** 8000
   - **Source:** Your IP address (or `0.0.0.0/0` for testing)
   - **Description:** vLLM API endpoint
6. Save and wait 1-2 minutes

### Option B: Use Helper Script

```bash
python scripts/configure_security_group.py
```

This will show detailed instructions for your instance.

## Test Connectivity

After setting up (either method), test connectivity:

```bash
python scripts/check_connectivity.py --ip 150.136.146.143
```

Or test with instance ID:
```bash
python scripts/check_connectivity.py --instance-id f401d9d6a1e649b2a74be9a2959a828a
```

## Dashboard Integration

The dashboard now has connectivity testing built-in:

1. **Test API Endpoint** button - Tests if endpoint is accessible
2. **SSH Tunnel Setup** button - Shows instructions for tunnel setup
3. **Auto-detection** - Detects if port is blocked and suggests tunnel

## Troubleshooting

### Tunnel won't start
- Check SSH key path: `moses.pem` must be in project root
- Verify SSH access: `ssh -i moses.pem ubuntu@150.136.146.143`
- Check if port 8000 is already in use locally

### Still can't connect
- Verify vLLM is running: `ssh -i moses.pem ubuntu@150.136.146.143 'curl http://localhost:8000/health'`
- Check logs: `ssh -i moses.pem ubuntu@150.136.146.143 'tail -f /tmp/vllm.log'`
- Restart vLLM if needed: Use `setup_vllm_on_lambda.py` script

### Port already in use
- Change local port: `--local-port 8001`
- Update dashboard endpoint accordingly

## Current Status

- ✅ vLLM is running on instance (confirmed)
- ✅ Port 8000 is listening locally (confirmed)
- ❌ Port 8000 is NOT accessible externally (firewall blocking)
- ✅ SSH port 22 is accessible (can use tunnel)

