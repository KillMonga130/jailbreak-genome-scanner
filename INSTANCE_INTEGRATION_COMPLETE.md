# ✅ Lambda Instance Integration Complete

## Instances Ready

### 1. Mistral 7B Instruct
- **Instance ID**: `cd6537df1d7640a995090d45eff85e3e`
- **IP**: `129.80.191.122`
- **Status**: ✅ vLLM Running
- **API Endpoint**: `http://129.80.191.122:8000/v1/chat/completions`
- **SSH Tunnel**: `http://localhost:8000/v1/chat/completions`

### 2. Qwen 7B Chat
- **Instance ID**: `fe9576a10897449a8311eb667866abe8`
- **IP**: `150.136.220.151`
- **Status**: ✅ vLLM Running
- **API Endpoint**: `http://150.136.220.151:8000/v1/chat/completions`
- **SSH Tunnel**: `http://localhost:8001/v1/chat/completions`

---

## Integration Status

### ✅ Completed
- [x] Instances launched with SSH keys
- [x] vLLM installed and running on both
- [x] Deployment config updated
- [x] Dashboard auto-detection implemented
- [x] Instance selector in dashboard
- [x] SSH tunnel helper script

### 🔧 Next Steps

#### Option 1: Use SSH Tunnels (Recommended)
Since port 8000 is blocked by default firewall, use SSH tunnels:

```bash
# Set up tunnels for all instances
python scripts/setup_ssh_tunnels.py
```

This will create:
- Mistral: `http://localhost:8000/v1/chat/completions`
- Qwen: `http://localhost:8001/v1/chat/completions`

#### Option 2: Configure Security Groups
Open port 8000 in Lambda Cloud dashboard for direct access.

---

## Using in Dashboard

1. **Start Dashboard**:
   ```bash
   streamlit run dashboard/arena_dashboard.py
   ```

2. **Select Instance**:
   - Choose "Lambda Cloud" as defender type
   - Select instance from dropdown:
     - "Mistral 7B Instruct (Mistral-7B-Instruct-v0.2)"
     - "Qwen 7B Chat (Qwen-7B-Chat)"

3. **Configure Endpoint**:
   - If using SSH tunnel: Use `http://localhost:8000` or `http://localhost:8001`
   - If port is open: Use `http://<instance_ip>:8000`

4. **Start Evaluation**:
   - Configure attackers
   - Click "START EVALUATION"
   - Both instances are ready to use!

---

## Testing

Test instances:
```bash
python test_lambda_instances.py
```

Check SSH access:
```bash
ssh -i moses.pem ubuntu@129.80.191.122
ssh -i moses.pem ubuntu@150.136.220.151
```

---

## Cost

- **Total**: $1.50/hour ($0.75 per instance)
- **Remember**: Terminate when done!

---

**Both instances are integrated and ready for the hackathon! 🚀**

