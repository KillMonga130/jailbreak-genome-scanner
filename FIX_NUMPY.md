# Quick Fix: NumPy Compatibility Issue

## Problem
vLLM is failing to start because of NumPy version incompatibility:
- System has NumPy 2.2.6
- TensorFlow (used by vLLM) requires NumPy 1.x

## Quick Fix (Run on Lambda Instance)

SSH into your instance and run:

```bash
pip3 install "numpy<2" --upgrade
```

Then try starting vLLM again:

```bash
python3 -m vllm.entrypoints.openai.api_server \
    --model microsoft/phi-2 \
    --port 8000 \
    --host 0.0.0.0
```

## Automated Fix

Or run the updated setup script from your local machine:

```bash
python scripts/setup_vllm_on_lambda.py --ip 150.136.146.143 --key moses.pem --model microsoft/phi-2
```

This will automatically fix NumPy before installing vLLM.

