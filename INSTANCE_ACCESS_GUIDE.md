# 🎯 INSTANCE ACCESS GUIDE

## Current Status (From Discovery)

### ✅ Instances with Direct API Access

#### 1. H100 (209.20.159.141) - **FOR SCRAPING ONLY**
- **Model**: `mistralai/Mistral-7B-Instruct-v0.2`
- **Direct Endpoint**: `http://209.20.159.141:8000/v1/chat/completions`
- **Status**: ✅ Ready for scraping/intelligence gathering
- **Note**: You mentioned this is just for scraping, not for main defender

#### 2. Mistral A10 (129.80.191.122)
- **Model**: `mistralai/Mistral-7B-Instruct-v0.2`
- **Direct Endpoint**: `http://129.80.191.122:8000/v1/chat/completions`
- **Status**: ✅ Ready to use as defender/attacker
- **Access**: Direct IP - no tunnel needed

---

### ⚠️ Instances Requiring SSH Tunnels

#### 3. Qwen A10 (150.136.220.151)
- **Model**: Unknown (check via tunnel)
- **SSH Tunnel Endpoint**: `http://localhost:8001/v1/chat/completions`
- **Status**: ⚠️ Port 8000 blocked - SSH tunnel required
- **Tunnel Command**: 
  ```powershell
  ssh -i moses.pem -N -L 8001:localhost:8000 ubuntu@150.136.220.151
  ```
- **You already started this!** ✅

#### 4. A10 Instance #4 (165.1.79.86)
- **Model**: Unknown (check via tunnel)
- **SSH Tunnel Endpoint**: `http://localhost:8003/v1/chat/completions`
- **Status**: ⚠️ Port 8000 blocked - SSH tunnel required
- **Tunnel Command**:
  ```powershell
  ssh -i moses.pem -N -L 8003:localhost:8000 ubuntu@165.1.79.86
  ```

---

## 🔍 How to Check Models on Tunneled Instances

Since you've started the Qwen tunnel on port 8001, check what model is running:

```bash
python check_models_via_tunnel.py
```

Or manually:
```bash
curl http://localhost:8001/v1/models
```

---

## 📋 Quick Reference

### For Main Defender/Attacker (Arena Evaluations)
- **Recommended**: Mistral A10 (129.80.191.122)
  - Endpoint: `http://129.80.191.122:8000/v1/chat/completions`
  - Model: `mistralai/Mistral-7B-Instruct-v0.2`
  - ✅ Direct access - no tunnel needed

### For Scraping/Intelligence Gathering
- **H100** (209.20.159.141)
  - Endpoint: `http://209.20.159.141:8000/v1/chat/completions`
  - Model: `mistralai/Mistral-7B-Instruct-v0.2`
  - ✅ Direct access

### For Qwen (if you need it)
- **Qwen A10** (150.136.220.151)
  - Endpoint: `http://localhost:8001/v1/chat/completions` (via tunnel)
  - ⚠️ Requires SSH tunnel (you already started it!)
  - Check model: `python check_models_via_tunnel.py`

---

## 🚀 Dashboard Configuration

### Recommended Setup:

1. **Defender**: Mistral A10 (129.80.191.122)
   - Model: `mistralai/Mistral-7B-Instruct-v0.2`
   - Endpoint: `http://129.80.191.122:8000/v1/chat/completions`

2. **Intelligence Gathering** (if enabled):
   - H100 (209.20.159.141)
   - Endpoint: `http://209.20.159.141:8000/v1/chat/completions`

3. **Attacker/Evaluator**: Can use same Mistral or Qwen (if tunnel is active)

---

## 🛠️ Tools Available

- `python discover_instances.py` - Full discovery of all instances
- `python check_status.py` - Quick status check
- `python check_models_via_tunnel.py` - Check models on tunneled instances
- `fix_qwen_tunnel.ps1` - Start Qwen SSH tunnel
- `test_all_endpoints.py` - Test all endpoints

---

## ✅ Next Steps

1. **Check Qwen model** (since tunnel is running):
   ```bash
   python check_models_via_tunnel.py
   ```

2. **Start dashboard**:
   ```bash
   streamlit run dashboard/arena_dashboard.py
   ```

3. **Configure in dashboard**:
   - Defender: Mistral A10 (129.80.191.122)
   - Intelligence: H100 (209.20.159.141) - if using scraping
   - Attacker: Your choice

4. **Start evaluation!** 🚀

