#!/bin/bash
# Script to set up vLLM on Lambda Cloud instance

INSTANCE_IP="${1:-150.136.146.143}"
SSH_KEY="${2:-moses.pem}"
MODEL="${3:-microsoft/phi-2}"

echo "Setting up vLLM on Lambda instance $INSTANCE_IP"
echo "Model: $MODEL"
echo ""

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo "Error: SSH key not found: $SSH_KEY"
    exit 1
fi

echo "Step 1: Installing vLLM on instance..."
ssh -i "$SSH_KEY" ubuntu@"$INSTANCE_IP" << 'ENDSSH'
    # Update package list
    sudo apt-get update
    
    # Install Python dependencies
    pip3 install vllm --upgrade
    
    # Check if vLLM is installed
    python3 -c "import vllm; print('vLLM version:', vllm.__version__)"
ENDSSH

echo ""
echo "Step 2: Starting vLLM API server..."
echo "Note: This will run in the background. Use 'screen' or 'tmux' to keep it running."
echo ""

ssh -i "$SSH_KEY" ubuntu@"$INSTANCE_IP" << ENDSSH
    # Kill any existing vLLM processes
    pkill -f "vllm.entrypoints.openai.api_server" || true
    
    # Start vLLM in background with nohup
    nohup python3 -m vllm.entrypoints.openai.api_server \\
        --model $MODEL \\
        --port 8000 \\
        --host 0.0.0.0 \\
        > /tmp/vllm.log 2>&1 &
    
    echo "vLLM server starting..."
    sleep 5
    
    # Check if server is running
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ vLLM server is running!"
    else
        echo "⚠️  Server may still be starting. Check logs: tail -f /tmp/vllm.log"
    fi
ENDSSH

echo ""
echo "✅ Setup complete!"
echo "API endpoint: http://$INSTANCE_IP:8000/v1/chat/completions"
echo ""
echo "To check server status:"
echo "  ssh -i $SSH_KEY ubuntu@$INSTANCE_IP 'curl http://localhost:8000/health'"
echo ""
echo "To view logs:"
echo "  ssh -i $SSH_KEY ubuntu@$INSTANCE_IP 'tail -f /tmp/vllm.log'"

