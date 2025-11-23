# 🎯 Modal.com Model Selector Guide

## Available Models

The dashboard now includes a model selector with **12 popular vLLM-supported models**:

### 7B Models (Recommended for A10G)
- **Mistral 7B Instruct** - Fast and efficient (default)
- **Mistral 7B Instruct v0.1** - Previous version
- **Qwen 7B Chat** - Good for Chinese and multilingual
- **Llama 2 7B Chat** - Meta's popular model
- **Llama 3 8B Instruct** - Latest Llama model
- **Vicuna 7B v1.5** - Fine-tuned Llama
- **CodeLlama 7B Instruct** - Specialized for code

### Larger Models
- **Qwen 14B Chat** - More capable (14B)
- **Llama 2 13B Chat** - Larger Llama (13B)
- **Vicuna 13B v1.5** - Larger fine-tuned (13B)
- **Mixtral 8x7B Instruct** - Mixture of Experts (47B total) - **Requires A100**

### Small Models
- **Phi-2** - Microsoft's small but capable model (2.7B)

## How to Use

1. **Select "Modal.com"** as Defender Type
2. **Choose a model** from the dropdown
3. **Model info** will show size and description
4. **Start evaluation** - the selected model will be used!

## Model Switching

✅ **No redeployment needed!** The Modal endpoint accepts a `model` parameter, so you can switch models on the fly.

## GPU Requirements

- **A10G**: All 7B models, Phi-2, Qwen 14B, Llama 2 13B
- **A100**: Mixtral 8x7B (recommended for best performance)

## Current Deployment

Your Modal deployment is configured with:
- **GPU**: A10G
- **Default model**: Mistral 7B Instruct
- **All models** can be used via the `model` parameter

## Adding More Models

To add more models, edit `src/integrations/modal_models.py` and add to `AVAILABLE_MODELS` dictionary.

---

**You're all set! Select any model from the dropdown and start evaluating!** 🚀

