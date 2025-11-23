# 🎯 DASHBOARD QUICK GUIDE

## ✅ Dashboard is Running!

Your dashboard is available at:
- **Local**: http://localhost:8501
- **Network**: http://192.168.98.7:8501

---

## ⚠️ About the Warnings

The UMAP warnings are **not errors** - they're just informational:
- UMAP is optional for better visualization
- Code automatically falls back to PCA/t-SNE (works fine)
- Dashboard is fully functional

**To fix warnings (optional):**
```bash
pip install umap-learn
```

But it's not necessary - everything works without it!

---

## 🚀 Using the Dashboard

### Step 1: Configure Defender

1. In sidebar, select **"Lambda Cloud"** as Defender Type
2. Choose an instance from dropdown:
   - **Mistral A10 (129.80.191.122)** - Recommended for main defender
   - **H100** - For scraping/intelligence (if enabled)
   - **Qwen** - Via tunnel on localhost:8001
3. Verify API endpoint is auto-filled
4. Verify model name matches instance

### Step 2: Configure Attackers

- Default attackers are fine to start
- You can customize attack strategies
- Set number of rounds

### Step 3: Start Evaluation

1. Click **"START EVALUATION"**
2. Watch real-time progress
3. See results as they come in

---

## 📊 What You'll See

- **Real-time evaluation progress**
- **Attack success rates**
- **Defender responses**
- **Threat radar visualization**
- **Genome map of vulnerabilities**

---

## 🎯 Recommended Setup

**For Main Evaluations:**
- Defender: Mistral A10 (129.80.191.122)
  - Endpoint: `http://129.80.191.122:8000/v1/chat/completions`
  - Model: `mistralai/Mistral-7B-Instruct-v0.2`

**For Intelligence Gathering:**
- H100 (209.20.159.141) - if enabled in dashboard
  - Endpoint: `http://209.20.159.141:8000/v1/chat/completions`

**For Attacker/Evaluator:**
- Can use same Mistral or Qwen (if tunnel active)

---

## 🆘 Troubleshooting

### "Connection failed" error
- Check if instance is active: `python check_status.py`
- Verify endpoint is correct
- For tunneled instances, make sure SSH tunnel is running

### "Model not found" error
- Check actual model on instance: `python discover_instances.py`
- Update model name in dashboard to match

### Dashboard not loading
- Check terminal for errors
- Make sure port 8501 is not in use
- Try refreshing browser

---

## ✅ You're All Set!

The dashboard is running and ready to use. Just:
1. Configure defender (Mistral A10 recommended)
2. Set up attackers
3. Click "START EVALUATION"
4. Watch the magic happen! 🚀

