# 🎛️ Lambda Cloud Management Interface Guide

## Overview

The **Lambda Cloud Management Interface** (`lambda_manager.py`) is a comprehensive, interactive tool for managing your Lambda Cloud instances, models, and connectivity.

## Quick Start

```bash
python lambda_manager.py
```

This launches an interactive menu-driven interface with all management capabilities.

## Features

### 🖥️ Instance Management
- **View All Instances**: Detailed information about all your instances
- **Launch New Instance**: Launch new Lambda Cloud instances
- **Terminate Instance**: Stop instances and charges
- **Check Status**: Monitor instance status in real-time
- **Select Instance**: Choose instance for operations

### 🤖 Model Management
- **List Available Models**: See all available open-source models
- **Install/Setup Model**: Automatically install and configure models
- **Switch Model**: Change model on running instance
- **Check Model Status**: Verify if model is running
- **View Model Logs**: Access vLLM logs

### 🔌 Connectivity Testing
- **Full Connectivity Check**: Test SSH, API ports, and endpoints
- **Test SSH Connection**: Verify SSH access
- **Test API Port**: Check if port 8000 is accessible
- **Test API Endpoint**: Verify API endpoint is working
- **Setup SSH Tunnel**: Instructions for SSH tunneling (if port blocked)

### ⚙️ Setup & Configuration
- **Setup vLLM Environment**: Install vLLM and create virtual environment
- **Configure SSH Key**: Set SSH key path
- **View Setup Instructions**: Manual setup guide

### 🚀 Quick Setup (All-in-One)
- **Complete Setup**: Automatically install model + test connectivity
- **One-Click Setup**: Select model and get everything ready

## Main Menu

```
======================================================================
LAMBDA CLOUD MANAGEMENT INTERFACE
======================================================================

Active Instances: 1
Booting Instances: 0
Total Instances: 1

Current Instances:
  1. [OK] 8d3d9dac2688407aa... - gpu_1x_h100_pcie - 209.20.159.141 - active

----------------------------------------------------------------------
MAIN MENU
----------------------------------------------------------------------
1. Instance Management
   - View instances, launch, terminate, check status
2. Model Management
   - Install models, switch models, check model status
3. Connectivity Testing
   - Test SSH, API ports, endpoints
4. Setup & Configuration
   - Setup vLLM, configure SSH, setup environment
5. View Instance Details
   - Get detailed information about instances
6. Quick Setup (All-in-One)
   - Complete setup: install model + test connectivity
0. Exit

Select option (0-6):
```

## Usage Examples

### Example 1: Complete Setup (Recommended for First Time)

1. **Launch interface**:
   ```bash
   python lambda_manager.py
   ```

2. **Select instance** (if you have one):
   - Option 1 → Option 5 (Select Instance)
   - Choose your instance from the list

3. **Quick Setup**:
   - Option 6 (Quick Setup)
   - Select a model (e.g., `1` for phi-2)
   - Wait 5-10 minutes for setup to complete
   - Get your API endpoint!

### Example 2: Install a Model

1. **Launch interface**:
   ```bash
   python lambda_manager.py
   ```

2. **Select instance**:
   - Option 1 → Option 5 (Select Instance)

3. **Install model**:
   - Option 2 (Model Management)
   - Option 2 (Install/Setup Model)
   - Select model from list
   - Confirm installation
   - Wait for completion

### Example 3: Test Connectivity

1. **Launch interface**:
   ```bash
   python lambda_manager.py
   ```

2. **Select instance**:
   - Option 1 → Option 5 (Select Instance)

3. **Test connectivity**:
   - Option 3 (Connectivity Testing)
   - Option 1 (Full Connectivity Check)
   - View results

### Example 4: Switch Models

1. **Launch interface**:
   ```bash
   python lambda_manager.py
   ```

2. **Select instance** (if not already selected)

3. **Switch model**:
   - Option 2 (Model Management)
   - Option 3 (Switch Model)
   - Select new model
   - Confirm switch

### Example 5: Terminate Instance

1. **Launch interface**:
   ```bash
   python lambda_manager.py
   ```

2. **Terminate instance**:
   - Option 1 (Instance Management)
   - Option 3 (Terminate Instance)
   - Select instance to terminate
   - Confirm termination

## Available Models

| Key | Model Name | Description |
|-----|------------|-------------|
| `phi-2` | microsoft/phi-2 | Phi-2 (2.7B) - Small, fast, recommended for testing |
| `mistral-7b-instruct` | mistralai/Mistral-7B-Instruct-v0.2 | Mistral 7B Instruct - High quality |
| `qwen-7b-chat` | Qwen/Qwen-7B-Chat | Qwen 7B Chat - Multilingual |
| `falcon-7b-instruct` | tiiuae/falcon-7b-instruct | Falcon 7B Instruct - Good for instructions |

## Workflow

### First-Time Setup

1. **Launch instance** (via Lambda Cloud dashboard or interface)
2. **Launch management interface**: `python lambda_manager.py`
3. **Select instance**: Main Menu → Instance Management → Select Instance
4. **Quick Setup**: Main Menu → Quick Setup (All-in-One)
   - Select model
   - Wait for setup
   - Get API endpoint
5. **Test connectivity**: Main Menu → Connectivity Testing → Full Connectivity Check
6. **Use in your project**: Use the provided API endpoint

### Regular Usage

1. **Launch interface**: `python lambda_manager.py`
2. **Select instance** (if not already selected)
3. **Install/Switch model** as needed
4. **Test connectivity** before using
5. **Use API endpoint** in your project
6. **Terminate instance** when done (to stop charges!)

## Configuration

### SSH Key

Default SSH key is `moses.pem` in project root.

To change SSH key:
1. Main Menu → Setup & Configuration
2. Configure SSH Key
3. Enter new path

### API Key

Lambda API key must be configured in `.env` file:

```env
LAMBDA_API_KEY=secret_your_id.your_token
```

Or set as environment variable:

```bash
# Windows PowerShell
$env:LAMBDA_API_KEY='your_key'

# Linux/Mac
export LAMBDA_API_KEY='your_key'
```

## Troubleshooting

### "No instance selected" Error

**Solution**: Select an instance first:
- Main Menu → Instance Management → Select Instance
- Choose instance from list

### "Instance has no IP address" Error

**Solution**: Wait for instance to finish booting:
- Instance status should be "active" (not "booting")
- Check status: Main Menu → Instance Management → Check Instance Status

### "SSH key not found" Error

**Solution**: Configure SSH key path:
- Main Menu → Setup & Configuration → Configure SSH Key
- Enter correct path to SSH key file

### "Port 8000 blocked" Error

**Solution**: Use SSH tunnel:
- Main Menu → Connectivity Testing → Setup SSH Tunnel
- Follow instructions to create SSH tunnel
- Use `http://localhost:8000/v1/chat/completions` as endpoint

### Model Installation Failed

**Solution**: Check logs:
- Main Menu → Model Management → View Model Logs
- SSH into instance and check: `tail -f /tmp/vllm.log`
- Verify instance has enough GPU memory for the model

## Tips

1. **Always select instance first** before model/connectivity operations
2. **Use Quick Setup** for first-time setup (it does everything automatically)
3. **Test connectivity** before using the endpoint in your project
4. **Terminate instances** when done to avoid charges
5. **Check logs** if something doesn't work
6. **Use SSH tunnel** if port 8000 is blocked

## Keyboard Shortcuts

- **Enter**: Continue/Confirm
- **Ctrl+C**: Exit interface
- **0**: Go back/Cancel

## API Endpoint Format

After setup, your API endpoint will be:

```
http://<instance_ip>:8000/v1/chat/completions
```

Or with SSH tunnel:

```
http://localhost:8000/v1/chat/completions
```

## Using in Your Project

### Dashboard

1. Launch dashboard: `streamlit run dashboard/arena_dashboard.py`
2. Select "Lambda Cloud" as defender type
3. Enter instance ID (from management interface)
4. Enter API endpoint (from management interface)
5. Start evaluation!

### Code

```python
from src.defenders.llm_defender import LLMDefender

defender = LLMDefender(
    model_name="microsoft/phi-2",
    model_type="local",
    use_lambda=True,
    lambda_instance_id="8d3d9dac2688407aa395179c75fb4203",  # From interface
    lambda_api_endpoint="http://209.20.159.141:8000/v1/chat/completions"  # From interface
)
```

## Next Steps

1. ✅ **Launch interface**: `python lambda_manager.py`
2. ✅ **Select your instance**: Instance Management → Select Instance
3. ✅ **Quick Setup**: Main Menu → Quick Setup (All-in-One)
4. ✅ **Get API endpoint**: Save the endpoint for your project
5. ✅ **Test connectivity**: Connectivity Testing → Full Connectivity Check
6. ✅ **Use in dashboard/code**: Use the endpoint you got!

---

## 🎉 You're Ready to Manage Everything!

The management interface makes it easy to:
- ✅ Manage instances
- ✅ Install models
- ✅ Test connectivity
- ✅ Set up everything automatically
- ✅ Monitor status
- ✅ Control costs

**Start using it now**: `python lambda_manager.py`

