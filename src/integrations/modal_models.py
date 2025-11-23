"""Available models for Modal.com deployment."""

# Popular vLLM-supported models
AVAILABLE_MODELS = {
    "Mistral 7B Instruct": {
        "model_id": "mistralai/Mistral-7B-Instruct-v0.2",
        "size": "7B",
        "description": "Mistral 7B Instruct - Fast and efficient",
        "recommended_gpu": "A10G"
    },
    "Mistral 7B Instruct (v0.1)": {
        "model_id": "mistralai/Mistral-7B-Instruct-v0.1",
        "size": "7B",
        "description": "Mistral 7B Instruct v0.1",
        "recommended_gpu": "A10G"
    },
    "Qwen 7B Chat": {
        "model_id": "Qwen/Qwen-7B-Chat",
        "size": "7B",
        "description": "Qwen 7B Chat - Good for Chinese and multilingual",
        "recommended_gpu": "A10G"
    },
    "Qwen 14B Chat": {
        "model_id": "Qwen/Qwen-14B-Chat",
        "size": "14B",
        "description": "Qwen 14B Chat - Larger, more capable",
        "recommended_gpu": "A10G"
    },
    "Llama 2 7B Chat": {
        "model_id": "meta-llama/Llama-2-7b-chat-hf",
        "size": "7B",
        "description": "Meta Llama 2 7B Chat",
        "recommended_gpu": "A10G"
    },
    "Llama 2 13B Chat": {
        "model_id": "meta-llama/Llama-2-13b-chat-hf",
        "size": "13B",
        "description": "Meta Llama 2 13B Chat - More capable",
        "recommended_gpu": "A10G"
    },
    "Llama 3 8B Instruct": {
        "model_id": "meta-llama/Llama-3-8B-Instruct",
        "size": "8B",
        "description": "Meta Llama 3 8B Instruct - Latest Llama",
        "recommended_gpu": "A10G"
    },
    "Phi-2": {
        "model_id": "microsoft/phi-2",
        "size": "2.7B",
        "description": "Microsoft Phi-2 - Small but capable",
        "recommended_gpu": "A10G"
    },
    "Mixtral 8x7B Instruct": {
        "model_id": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "size": "47B (8x7B)",
        "description": "Mixtral 8x7B - Mixture of Experts, very capable",
        "recommended_gpu": "A100"
    },
    "CodeLlama 7B Instruct": {
        "model_id": "codellama/CodeLlama-7b-Instruct-hf",
        "size": "7B",
        "description": "CodeLlama 7B - Specialized for code",
        "recommended_gpu": "A10G"
    },
    "Vicuna 7B v1.5": {
        "model_id": "lmsys/vicuna-7b-v1.5",
        "size": "7B",
        "description": "Vicuna 7B v1.5 - Fine-tuned Llama",
        "recommended_gpu": "A10G"
    },
    "Vicuna 13B v1.5": {
        "model_id": "lmsys/vicuna-13b-v1.5",
        "size": "13B",
        "description": "Vicuna 13B v1.5 - Larger fine-tuned Llama",
        "recommended_gpu": "A10G"
    }
}

def get_model_list():
    """Get list of available models for dropdown."""
    return list(AVAILABLE_MODELS.keys())

def get_model_id(model_name: str) -> str:
    """Get model ID from display name."""
    return AVAILABLE_MODELS.get(model_name, {}).get("model_id", model_name)

def get_model_info(model_name: str) -> dict:
    """Get model information."""
    return AVAILABLE_MODELS.get(model_name, {})

