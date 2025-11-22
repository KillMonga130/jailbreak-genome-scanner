#!/bin/bash
# Setup script to run on Lambda Cloud instance after SSH connection
# This sets up the model inference server (vLLM or Text Generation Inference)

set -e

echo "Setting up Lambda Cloud instance for model inference..."

# Update system
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv git

# Create virtual environment
python3 -m venv ~/venv
source ~/venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install transformers accelerate bitsandbytes

# Install vLLM for fast inference (recommended)
pip install vllm

# Or install Text Generation Inference (alternative)
# pip install text-generation

echo "Setup complete!"
echo ""
echo "To run inference server:"
echo "  source ~/venv/bin/activate"
echo "  python3 -m vllm.entrypoints.openai.api_server --model meta-llama/Llama-2-7b-chat-hf --port 8000"
echo ""
echo "Or use Text Generation Inference:"
echo "  text-generation-launcher --model-id meta-llama/Llama-2-7b-chat-hf --port 8000"

