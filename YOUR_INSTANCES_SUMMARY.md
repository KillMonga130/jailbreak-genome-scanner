# 📊 YOUR INSTANCES - COMPLETE SUMMARY

## ✅ What's Working Right Now

### 1. **H100 (209.20.159.141)** - FOR SCRAPING ONLY
- **Purpose**: Intelligence gathering / scraping jailbreaks from internet
- **Model**: `mistralai/Mistral-7B-Instruct-v0.2`
- **Access**: ✅ Direct API
- **Endpoint**: `http://209.20.159.141:8000/v1/chat/completions`
- **Status**: ✅ Ready

### 2. **Mistral A10 (129.80.191.122)** - MAIN DEFENDER
- **Purpose**: Defender/Attacker for arena evaluations
- **Model**: `mistralai/Mistral-7B-Instruct-v0.2`
- **Access**: ✅ Direct API
- **Endpoint**: `http://129.80.191.122:8000/v1/chat/completions`
- **Status**: ✅ Ready - **USE THIS FOR MAIN EVALUATIONS**

### 3. **Qwen A10 (150.136.220.151)** - ATTACKER/EVALUATOR
- **Purpose**: Attacker or evaluator
- **Model**: Unknown (check via tunnel)
- **Access**: ⚠️ SSH Tunnel Required
- **Tunnel Endpoint**: `http://localhost:8001/v1/chat/completions`
- **Tunnel Status**: ✅ You started it!
- **Check Model**: Run `python check_models_via_tunnel.py` or:
  ```bash
  curl http://localhost:8001/v1/models
  ```

### 4. **A10 Instance #4 (165.1.79.86)**
- **Purpose**: Unknown
- **Model**: Unknown
- **Access**: ⚠️ SSH Tunnel Required
- **Tunnel Endpoint**: `http://localhost:8003/v1/chat/completions`
- **Tunnel Command**: 
  ```powershell
  ssh -i moses.pem -N -L 8003:localhost:8000 ubuntu@165.1.79.86
  ```

---

## 🎯 Recommended Configuration

### For Dashboard Evaluations:

**Defender**:
- Instance: Mistral A10 (129.80.191.122)
- Model: `mistralai/Mistral-7B-Instruct-v0.2`
- Endpoint: `http://129.80.191.122:8000/v1/chat/completions`

**Attacker**:
- Option 1: Same Mistral instance (different role)
- Option 2: Qwen via tunnel (if model is loaded)
  - Endpoint: `http://localhost:8001/v1/chat/completions`

**Intelligence Gathering** (if enabled):
- Instance: H100 (209.20.159.141)
- Endpoint: `http://209.20.159.141:8000/v1/chat/completions`

---

## 🔍 How to Check What's Running

### Check Models on Direct Access Instances:
```bash
# H100
curl http://209.20.159.141:8000/v1/models

# Mistral A10
curl http://129.80.191.122:8000/v1/models
```

### Check Models on Tunneled Instances:
```bash
# Qwen (port 8001)
curl http://localhost:8001/v1/models

# Or use the tool
python check_models_via_tunnel.py
```

### Full Discovery:
```bash
python discover_instances.py
```

---

## 🚀 Quick Start

1. **Verify Qwen model** (since tunnel is running):
   ```bash
   curl http://localhost:8001/v1/models
   ```

2. **Start dashboard**:
   ```bash
   streamlit run dashboard/arena_dashboard.py
   ```

3. **In dashboard**:
   - Select "Lambda Cloud"
   - Choose "Mistral A10" for defender
   - Configure attacker (can use same or Qwen)
   - Start evaluation!

---

## 📝 Port Mapping Reference

| Instance | IP | Direct Port | Tunnel Port | Status |
|----------|-----|-------------|-------------|--------|
| H100 | 209.20.159.141 | 8000 ✅ | N/A | Direct access |
| Mistral | 129.80.191.122 | 8000 ✅ | N/A | Direct access |
| Qwen | 150.136.220.151 | 8000 ❌ | 8001 ✅ | Tunnel active |
| Instance #4 | 165.1.79.86 | 8000 ❌ | 8003 | Tunnel needed |

---

## 🛠️ Troubleshooting

### Qwen tunnel not working?
1. Check if tunnel is running: Look for SSH process
2. Verify vLLM is running on instance:
   ```bash
   ssh -i moses.pem ubuntu@150.136.220.151 'ps aux | grep vllm'
   ```
3. Check vLLM logs:
   ```bash
   ssh -i moses.pem ubuntu@150.136.220.151 'tail -50 /tmp/vllm.log'
   ```

### Can't find model?
- Models might not be loaded yet
- Check via SSH: `ssh -i moses.pem ubuntu@<ip> 'curl http://localhost:8000/v1/models'`
- Or start vLLM if not running

---

## ✅ You're Ready!

**Main setup for evaluations:**
- ✅ Defender: Mistral A10 (129.80.191.122) - Ready!
- ✅ Scraping: H100 (209.20.159.141) - Ready!
- ⚠️ Qwen: Check model via tunnel, then use if needed

**Start the dashboard and begin evaluations!** 🚀

