#!/bin/bash
# Set up vLLM in a virtual environment to avoid system package conflicts

set -e

MODEL="${1:-microsoft/phi-2}"
VENV_DIR="$HOME/vllm_env"
VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

echo "Setting up vLLM in virtual environment..."
echo "Model: $MODEL"
echo

# Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Upgrade pip first
echo "Upgrading pip..."
"$VENV_PIP" install --upgrade pip setuptools wheel

# Install NumPy <2 first
echo "Installing pinned NumPy <2.0..."
"$VENV_PIP" install "numpy<2.0"

# Install vLLM (may try to upgrade NumPy)
echo "Installing vLLM..."
"$VENV_PIP" install vllm --no-cache-dir

# Force reinstall NumPy <2 to ensure it stays pinned
echo "Reinstalling NumPy <2.0 to prevent upgrade..."
"$VENV_PIP" install --force-reinstall --no-deps "numpy<2.0"

# Verify NumPy version
echo "Verifying NumPy version..."
NUMPY_VERSION=$("$VENV_PYTHON" -c "import numpy; print(numpy.__version__)" 2>/dev/null || echo "not installed")
echo "NumPy version: $NUMPY_VERSION"

if [[ "$NUMPY_VERSION" == 2.* ]] || [[ "$NUMPY_VERSION" == "not installed" ]] || [[ -z "$NUMPY_VERSION" ]]; then
    echo "ERROR: NumPy verification failed or is 2.x"
    echo "Attempting to fix..."
    "$VENV_PIP" install --force-reinstall --no-deps "numpy<2.0"
    # Check again
    FINAL_CHECK=$("$VENV_PYTHON" -c "import numpy; print(numpy.__version__)" 2>/dev/null || echo "failed")
    if [[ "$FINAL_CHECK" == 2.* ]] || [[ "$FINAL_CHECK" == "failed" ]]; then
        echo "ERROR: Could not fix NumPy version. Manual intervention required."
        exit 1
    fi
    echo "NumPy successfully fixed to: $FINAL_CHECK"
fi

# Final verification
FINAL_NUMPY=$("$VENV_PYTHON" -c "import numpy; print(numpy.__version__)" 2>/dev/null)
if [[ -n "$FINAL_NUMPY" && "$FINAL_NUMPY" != 2.* ]]; then
    echo "Final NumPy version confirmed: $FINAL_NUMPY"
else
    echo "ERROR: Final NumPy verification failed"
    exit 1
fi

# Start vLLM server using venv Python
echo "Starting vLLM server..."
pkill -f "vllm.entrypoints.openai.api_server" || true
sleep 2

# Check if model requires trust_remote_code (Qwen, some others)
TRUST_REMOTE_CODE=""
if [[ "$MODEL" == *"Qwen"* ]] || [[ "$MODEL" == *"qwen"* ]]; then
    echo "Detected Qwen model - adding --trust-remote-code flag"
    TRUST_REMOTE_CODE="--trust-remote-code"
fi

nohup "$VENV_PYTHON" -m vllm.entrypoints.openai.api_server \
    --model "$MODEL" \
    --port 8000 \
    --host 0.0.0.0 \
    $TRUST_REMOTE_CODE \
    > /tmp/vllm.log 2>&1 &

echo "vLLM server started in background"
echo "Check logs: tail -f /tmp/vllm.log"
echo "Check status: curl http://localhost:8000/health"

