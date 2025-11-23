"""Deploy vLLM models to Modal.com for serverless inference."""

import modal
import os
import logging
from pathlib import Path
from fastapi import HTTPException

log = logging.getLogger(__name__)

# Modal image with vLLM - upgraded to newer version for better compatibility
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "vllm==0.11.2",  # Newer version with better tokenizer support
        "transformers>=4.40.0",
        "torch>=2.1.0",
        "accelerate>=0.25.0",
        "python-multipart",  # Required for FastAPI form data
        "huggingface-hub>=0.20.0",
    )
    .env({"HF_XET_HIGH_PERFORMANCE": "1"})  # Faster model transfers
)

app = modal.App("jailbreak-genome-scanner")

# GPU configuration - use A10G for cost efficiency
GPU_CONFIG = "A10G"  # Can change to "A100" or "H100" if needed

# Global model cache (shared across all functions in same container)
_model_cache = {}
_model_lock = None

def get_model_cache():
    """Get thread-safe model cache."""
    global _model_lock
    if _model_lock is None:
        import threading
        _model_lock = threading.Lock()
    return _model_cache, _model_lock

# Modal Volume for caching model weights (faster startup)
model_volume = modal.Volume.from_name("modal-model-cache", create_if_missing=True)

@app.function(
    image=image,
    gpu=GPU_CONFIG,
    scaledown_window=300,  # Shut down after 5 min idle (saves money!)
    timeout=900,  # Max 15 min per request (model loading can take time)
    volumes={"/root/.cache/huggingface": model_volume},  # Cache model weights
)
@modal.concurrent(max_inputs=1)  # Limit to 1 concurrent request per container (prevents scaling)
@modal.fastapi_endpoint(method="POST")
def serve(request: dict):
    """
    Serve a model via Modal for inference.
    
    Args:
        request: JSON body with 'prompt', 'max_tokens', 'temperature', 'model'
        
    Returns:
        Generated response
    """
    from vllm import LLM, SamplingParams
    
    # Extract parameters from request
    prompt = request.get("prompt", "")
    model = request.get("model", "mistralai/Mistral-7B-Instruct-v0.2")
    max_tokens = request.get("max_tokens", 1000)
    temperature = request.get("temperature", 0.7)
    
    # Initialize LLM (cached across requests using global cache)
    cache, lock = get_model_cache()
    
    with lock:
        if model not in cache:
            try:
                log.info(f"Loading model {model} (first time in this container)")
                cache[model] = LLM(
                    model=model, 
                    tensor_parallel_size=1,
                    trust_remote_code=True,
                    tokenizer_mode="mistral" if "mistral" in model.lower() else "auto"
                )
                log.info(f"Model {model} loaded successfully")
            except Exception as e:
                error_msg = str(e)
                log.error(f"Error loading model {model}: {error_msg}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "Model loading error",
                        "message": f"Failed to load model '{model}': {error_msg}",
                        "suggestion": "Please check the model name and try again, or use a different model."
                    }
                )
        llm = cache[model]
    
    # Generate response
    sampling_params = SamplingParams(
        temperature=temperature,
        max_tokens=max_tokens,
    )
    
    outputs = llm.generate([prompt], sampling_params)
    generated_text = outputs[0].outputs[0].text
    
    return {
        "response": generated_text,
        "model": model,
        "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt
    }


@app.function(
    image=image,
    gpu=GPU_CONFIG,
    scaledown_window=300,
    timeout=900,  # Max 15 min per request (model loading can take time)
    volumes={"/root/.cache/huggingface": model_volume},  # Cache model weights
)
@modal.concurrent(max_inputs=1)  # Limit to 1 concurrent request per container
@modal.fastapi_endpoint(method="POST")
def chat_completions(request: dict):
    """
    OpenAI-compatible chat completions endpoint.
    
    Args:
        request: JSON body with 'messages', 'model', 'max_tokens', 'temperature'
        
    Returns:
        OpenAI-compatible response
    """
    from vllm import LLM, SamplingParams
    
    # Extract parameters from request
    messages = request.get("messages", [])
    model = request.get("model", "mistralai/Mistral-7B-Instruct-v0.2")
    max_tokens = request.get("max_tokens", 1000)
    temperature = request.get("temperature", 0.7)
    
    # Initialize LLM (cached across requests using global cache)
    cache, lock = get_model_cache()
    
    with lock:
        if model not in cache:
            try:
                log.info(f"Loading model {model} (first time in this container)")
                cache[model] = LLM(
                    model=model, 
                    tensor_parallel_size=1,
                    trust_remote_code=True,
                    tokenizer_mode="mistral" if "mistral" in model.lower() else "auto"
                )
                log.info(f"Model {model} loaded successfully")
            except Exception as e:
                error_msg = str(e)
                log.error(f"Error loading model {model}: {error_msg}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "Model loading error",
                        "message": f"Failed to load model '{model}': {error_msg}",
                        "suggestion": "Please check the model name and try again, or use a different model."
                    }
                )
        llm = cache[model]
    
    # Use vLLM's built-in chat template if available, otherwise convert manually
    try:
        from transformers import AutoTokenizer
        # Get tokenizer from cache or load it
        tokenizer_key = f"{model}_tokenizer"
        if tokenizer_key not in cache:
            cache[tokenizer_key] = AutoTokenizer.from_pretrained(model, trust_remote_code=True)
        tokenizer = cache[tokenizer_key]
        
        # Use tokenizer's chat template if available
        prompt = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    except Exception:
        # Fallback to manual conversion
        prompt = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt += f"System: {content}\n\n"
            elif role == "user":
                prompt += f"User: {content}\n\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n\n"
    
    # Generate
    sampling_params = SamplingParams(
        temperature=temperature,
        max_tokens=max_tokens,
    )
    
    outputs = llm.generate([prompt], sampling_params)
    generated_text = outputs[0].outputs[0].text
    
    # Return OpenAI-compatible format
    return {
        "id": "modal-response",
        "object": "chat.completion",
        "created": int(__import__("time").time()),
        "model": model,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": generated_text
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": len(prompt.split()),
            "completion_tokens": len(generated_text.split()),
            "total_tokens": len(prompt.split()) + len(generated_text.split())
        }
    }


@app.function(
    image=image,
    gpu=GPU_CONFIG,
    scaledown_window=300,
    timeout=900,  # Max 15 min per request (model loading can take time)
    volumes={"/root/.cache/huggingface": model_volume},  # Cache model weights
)
@modal.concurrent(max_inputs=1)  # Limit to 1 concurrent request per container
@modal.fastapi_endpoint(method="POST")
def completions(request: dict):
    """
    OpenAI-compatible completions endpoint.
    
    Args:
        request: JSON body with 'prompt', 'model', 'max_tokens', 'temperature'
        
    Returns:
        OpenAI-compatible response
    """
    from vllm import LLM, SamplingParams
    
    # Extract parameters from request
    prompt = request.get("prompt", "")
    model = request.get("model", "mistralai/Mistral-7B-Instruct-v0.2")
    max_tokens = request.get("max_tokens", 1000)
    temperature = request.get("temperature", 0.7)
    
    # Initialize LLM (cached across requests using global cache)
    cache, lock = get_model_cache()
    
    with lock:
        if model not in cache:
            try:
                log.info(f"Loading model {model} (first time in this container)")
                cache[model] = LLM(
                    model=model, 
                    tensor_parallel_size=1,
                    trust_remote_code=True,
                    tokenizer_mode="mistral" if "mistral" in model.lower() else "auto"
                )
                log.info(f"Model {model} loaded successfully")
            except Exception as e:
                error_msg = str(e)
                log.error(f"Error loading model {model}: {error_msg}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "Model loading error",
                        "message": f"Failed to load model '{model}': {error_msg}",
                        "suggestion": "Please check the model name and try again, or use a different model."
                    }
                )
        llm = cache[model]
    
    # Generate
    sampling_params = SamplingParams(
        temperature=temperature,
        max_tokens=max_tokens,
    )
    
    outputs = llm.generate([prompt], sampling_params)
    generated_text = outputs[0].outputs[0].text
    
    # Return OpenAI-compatible format
    return {
        "id": "modal-response",
        "object": "text_completion",
        "created": int(__import__("time").time()),
        "model": model,
        "choices": [{
            "index": 0,
            "text": generated_text,
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": len(prompt.split()),
            "completion_tokens": len(generated_text.split()),
            "total_tokens": len(prompt.split()) + len(generated_text.split())
        }
    }


if __name__ == "__main__":
    # Deploy to Modal
    app.deploy("jailbreak-genome-scanner")

