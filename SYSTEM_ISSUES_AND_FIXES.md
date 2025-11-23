# 🔧 SYSTEM ISSUES AND FIXES

## DIAGNOSIS SUMMARY

### ✅ What's Working
1. **Lambda API Key**: Configured correctly ✅
2. **Lambda Instances**: 3 instances are active and running ✅
   - H100 (209.20.159.141): Port 8000 accessible ✅
   - Mistral (129.80.191.122): Port 8000 accessible ✅
   - Qwen (150.136.220.151): Port 8000 **BLOCKED** ❌
3. **Backend Dependencies**: All installed ✅
4. **Dashboard**: Exists and has Lambda integration ✅
5. **SSH Key**: Found and accessible ✅

### ❌ Issues Found

#### 1. **Endpoint Configuration Problems**
- **Problem**: `data/lambda_deployments.json` has `localhost` endpoints that won't work unless SSH tunnels are running
- **Impact**: Dashboard tries to use `http://localhost:8000` but tunnels may not be active
- **Fix**: Dashboard should fall back to direct IP endpoints when localhost fails

#### 2. **Qwen Instance Port Blocked**
- **Problem**: Instance `150.136.220.151` has port 8000 blocked by firewall
- **Impact**: Cannot access vLLM API directly
- **Solutions**:
  - Option A: Use SSH tunnel (recommended for testing)
  - Option B: Configure Lambda Cloud security group to allow port 8000

#### 3. **vLLM Status Unknown**
- **Problem**: Not verified if vLLM is actually running on instances
- **Impact**: Endpoints may be configured but vLLM server may not be running
- **Fix**: Need to verify vLLM is running on each instance

---

## 🔧 FIXES

### Fix 1: Update Deployments Config with Direct IP Endpoints

The deployments config should have both localhost (for tunnels) AND direct IP endpoints.

**Current state**:
```json
"api_endpoint": "http://localhost:8000/v1/chat/completions"
```

**Should be**:
```json
"api_endpoint": "http://129.80.191.122:8000/v1/chat/completions",
"api_endpoint_local": "http://localhost:8000/v1/chat/completions"
```

### Fix 2: Dashboard Endpoint Detection

Dashboard should:
1. Try localhost endpoint first (if SSH tunnel is active)
2. Fall back to direct IP endpoint if localhost fails
3. Show clear error if both fail

### Fix 3: Qwen Instance SSH Tunnel

For the Qwen instance (150.136.220.151), set up SSH tunnel:

```powershell
# PowerShell
ssh -i moses.pem -N -L 8001:localhost:8000 ubuntu@150.136.220.151
```

Then use: `http://localhost:8001/v1/chat/completions`

### Fix 4: Verify vLLM is Running

Check each instance:

```bash
# SSH into instance
ssh -i moses.pem ubuntu@<instance_ip>

# Check if vLLM is running
ps aux | grep vllm

# Check health
curl http://localhost:8000/health

# View logs
tail -f /tmp/vllm.log
```

---

## 🚀 QUICK FIX COMMANDS

### 1. Fix Deployments Config
```bash
python -c "
import json
from pathlib import Path

config_path = Path('data/lambda_deployments.json')
with open(config_path, 'r') as f:
    config = json.load(f)

for key, model in config['deployed_models'].items():
    ip = model.get('instance_ip')
    if ip and 'localhost' in model.get('api_endpoint', ''):
        # Keep local endpoint, add direct IP endpoint
        model['api_endpoint'] = f'http://{ip}:8000/v1/chat/completions'
        if 'api_endpoint_local' not in model:
            model['api_endpoint_local'] = model.get('api_endpoint', '').replace(ip, 'localhost')

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)
print('Fixed deployments config')
"
```

### 2. Set Up SSH Tunnel for Qwen
```powershell
# Run in separate terminal
ssh -i moses.pem -N -L 8001:localhost:8000 ubuntu@150.136.220.151
```

### 3. Test All Endpoints
```bash
python test_endpoints.py
```

### 4. Start Dashboard
```bash
streamlit run dashboard/arena_dashboard.py
```

---

## 📋 CHECKLIST

- [ ] Fix deployments.json to have both localhost and direct IP endpoints
- [ ] Set up SSH tunnel for Qwen instance (port 8001)
- [ ] Verify vLLM is running on all instances
- [ ] Test all endpoints work
- [ ] Update dashboard to handle endpoint fallback
- [ ] Test dashboard with all instances

---

## 🎯 EXPECTED RESULT

After fixes:
1. ✅ All instances have working endpoints (direct IP or SSH tunnel)
2. ✅ Dashboard can connect to all instances
3. ✅ vLLM is verified running on all instances
4. ✅ Endpoints fall back gracefully (localhost → direct IP)

---

## 📞 IF STILL NOT WORKING

1. **Check vLLM is running**:
   ```bash
   ssh -i moses.pem ubuntu@<ip> 'ps aux | grep vllm'
   ```

2. **Check port is open**:
   ```bash
   python scripts/check_connectivity.py --ip <ip>
   ```

3. **Check Lambda Cloud security groups**:
   - Go to Lambda Cloud dashboard
   - Find instance security group
   - Add inbound rule: TCP 8000 from 0.0.0.0/0

4. **Check logs**:
   ```bash
   ssh -i moses.pem ubuntu@<ip> 'tail -50 /tmp/vllm.log'
   ```

