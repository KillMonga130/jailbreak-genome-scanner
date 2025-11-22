# Quick Start: Connect to Lambda Instance API

## ✅ Status

Your connectivity tools are ready! The SSH tunnel helper is working correctly.

## 🚀 Quick Start: Use SSH Tunnel (Recommended)

### Step 1: Start SSH Tunnel

Open a terminal/command prompt and run:

```bash
python scripts/ssh_tunnel_helper.py --ip 150.136.146.143 --key moses.pem
```

**Keep this terminal open** - the tunnel must stay running!

You should see:
```
[OK] SSH tunnel started: localhost:8000 -> 150.136.146.143:8000
[INFO] Use endpoint: http://localhost:8000/v1/chat/completions
```

### Step 2: Update Dashboard Endpoint

1. Open the dashboard
2. Go to "Defender Setup" section
3. Change API Endpoint to:
   ```
   http://localhost:8000/v1/chat/completions
   ```
4. Click "Test API Endpoint" to verify it works

### Step 3: Start Evaluation

Now you can start evaluations! The dashboard will connect through the tunnel.

### Step 4: Stop Tunnel (When Done)

Press `Ctrl+C` in the tunnel terminal to stop it.

---

## 🔍 Test Connectivity

Before starting the tunnel, check if port 8000 is blocked:

```bash
python scripts/check_connectivity.py --ip 150.136.146.143
```

This will show:
- ✅ SSH port (22) is accessible
- ❌ API port (8000) is blocked (expected)
- **Solution:** Use SSH tunnel

---

## 🔧 Alternative: Configure Security Group

If you prefer direct access (no tunnel needed):

1. Run the helper script:
   ```bash
   python scripts/configure_security_group.py
   ```
2. Follow the instructions to open port 8000 in Lambda Cloud dashboard
3. Wait 1-2 minutes for changes to take effect
4. Update dashboard endpoint to:
   ```
   http://150.136.146.143:8000/v1/chat/completions
   ```

---

## ✅ Verification

The tunnel is working correctly! You can verify by:

1. **Check if tunnel is running:**
   - Look for the tunnel terminal showing "SSH tunnel is running!"
   
2. **Test the endpoint:**
   - In dashboard, click "Test API Endpoint"
   - Should show: ✅ "API endpoint is accessible"

3. **Check connectivity:**
   ```bash
   python scripts/check_connectivity.py --ip 150.136.146.143
   ```
   - Port 8000 will still show as blocked externally (expected)
   - But localhost:8000 will work through the tunnel!

---

## 📝 Important Notes

1. **Keep tunnel running:** The tunnel must stay running while evaluating
2. **Use localhost:** Always use `http://localhost:8000/v1/chat/completions` when tunnel is active
3. **Model name:** Make sure the dashboard uses the correct model name: `microsoft/phi-2`
4. **Multiple terminals:** You can run the dashboard in one terminal and the tunnel in another

---

## 🐛 Troubleshooting

### Tunnel won't start
- Check if SSH key exists: `moses.pem` must be in project root
- Verify SSH access: `ssh -i moses.pem ubuntu@150.136.146.143`
- Check if port 8000 is already in use locally

### Still can't connect
- Make sure tunnel is still running (check terminal)
- Verify endpoint is set to `http://localhost:8000/v1/chat/completions`
- Check if vLLM is running on instance:
  ```bash
  ssh -i moses.pem ubuntu@150.136.146.143 'curl http://localhost:8000/health'
  ```

### Port already in use
- Change local port: `--local-port 8001`
- Update dashboard endpoint accordingly

---

## ✅ You're Ready!

Everything is set up correctly. Just:
1. Keep the SSH tunnel running
2. Use `http://localhost:8000/v1/chat/completions` in the dashboard
3. Start evaluating!

