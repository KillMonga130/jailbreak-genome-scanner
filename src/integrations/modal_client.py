"""Modal.com integration for serverless model inference."""

import os
import httpx
import asyncio
from typing import Optional, Dict, Any, List
from src.utils.logger import log
from src.config import settings


class ModalClient:
    """Client for interacting with Modal.com API."""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """
        Initialize Modal client.
        
        Args:
            api_key: Modal API key (wk-...)
            api_secret: Modal API secret (ws-...)
        """
        self.api_key = api_key or os.getenv("MODAL_API_KEY") or os.getenv("MODAL_KEY")
        self.api_secret = api_secret or os.getenv("MODAL_SECRET")
        self.base_url = "https://api.modal.com"
        
        if not self.api_key or not self.api_secret:
            log.warning("Modal API credentials not configured")
        else:
            # Modal uses HTTP Basic Auth with API key as username and secret as password
            import base64
            auth_string = f"{self.api_key}:{self.api_secret}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            self.headers = {
                "Authorization": f"Basic {auth_b64}",
                "Content-Type": "application/json"
            }
    
    async def list_apps(self) -> List[Dict[str, Any]]:
        """List all Modal apps."""
        if not self.api_key or not self.api_secret:
            log.error("Cannot list apps: Modal credentials not configured")
            return []
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:  # Increased for model loading
                response = await client.get(
                    f"{self.base_url}/v1/apps",
                    auth=(self.api_key, self.api_secret),
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("apps", [])
        except Exception as e:
            log.error(f"Error listing Modal apps: {e}")
            return []
    
    async def get_app_status(self, app_name: str) -> Optional[Dict[str, Any]]:
        """Get status of a Modal app."""
        apps = await self.list_apps()
        for app in apps:
            if app.get("name") == app_name:
                return app
        return None


class ModalModelRunner:
    """Runs models on Modal.com infrastructure."""
    
    def __init__(self, modal_client: Optional[ModalClient] = None):
        """
        Initialize Modal model runner.
        
        Args:
            modal_client: Optional Modal client
        """
        self.modal_client = modal_client or ModalClient()
        self.active_endpoints: Dict[str, str] = {}
    
    async def get_model_endpoint(self, app_name: str, function_name: str = "serve") -> Optional[str]:
        """
        Get the endpoint URL for a Modal app function.
        
        Args:
            app_name: Modal app name
            function_name: Function name (default: "serve")
            
        Returns:
            Endpoint URL or None
        """
        # Modal endpoints follow pattern: https://<username>--<app-name>-<function-name>.modal.run
        # Or: https://<app-name>--<function-name>.modal.run
        # For now, we'll construct from app name
        # In practice, you'd get this from Modal API or deployment
        
        # Try to get from environment or config
        endpoint = os.getenv(f"MODAL_ENDPOINT_{app_name.upper()}")
        if endpoint:
            return endpoint
        
        # Construct default endpoint (user needs to provide actual endpoint)
        # Modal provides this when you deploy
        log.warning(f"Modal endpoint not configured for {app_name}. Set MODAL_ENDPOINT_{app_name.upper()} environment variable.")
        return None
    
    async def generate_response(
        self,
        prompt: str,
        app_name: str,
        function_name: str = "serve",
        model_name: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate response using Modal-hosted model.
        
        Args:
            prompt: Input prompt
            app_name: Modal app name
            function_name: Function name
            model_name: Optional model name (for compatibility)
            **kwargs: Additional generation parameters
            
        Returns:
            Model response
        """
        endpoint = await self.get_model_endpoint(app_name, function_name)
        if not endpoint:
            raise ValueError(f"Modal endpoint not configured for app: {app_name}")
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:  # Increased for model loading
                # Modal functions accept OpenAI-compatible format
                # Try chat/completions format first (preferred)
                payload = {
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": kwargs.get("max_tokens", 1000),
                    "temperature": kwargs.get("temperature", 0.7)
                }
                
                # If endpoint has "chat-completions" in name, use chat format
                # Otherwise try completions format
                if "chat-completions" in endpoint.lower() or "chat_completions" in endpoint.lower():
                    response = await client.post(endpoint, json=payload)
                else:
                    # Try completions format
                    payload = {
                        "prompt": prompt,
                        "max_tokens": kwargs.get("max_tokens", 1000),
                        "temperature": kwargs.get("temperature", 0.7)
                    }
                    response = await client.post(endpoint, json=payload)
                
                # Handle 400 errors (bad request - like tokenizer errors)
                if response.status_code == 400:
                    try:
                        error_data = response.json()
                        if isinstance(error_data, dict):
                            detail = error_data.get("detail", {})
                            if isinstance(detail, dict):
                                error_msg = detail.get("message", "Unknown error")
                                suggestion = detail.get("suggestion", "")
                                raise ValueError(f"{error_msg}. {suggestion}")
                            else:
                                raise ValueError(f"Bad request: {detail}")
                        else:
                            raise ValueError(f"Bad request: {error_data}")
                    except Exception:
                        raise ValueError(f"Bad request: {response.text}")
                
                response.raise_for_status()
                data = response.json()
                
                # Handle error responses in response body
                if isinstance(data, dict) and "error" in data:
                    error_msg = data.get("message", "Unknown error")
                    suggestion = data.get("suggestion", "")
                    raise ValueError(f"{error_msg}. {suggestion}")
                
                # Handle OpenAI-compatible response format
                if isinstance(data, str):
                    return data
                elif isinstance(data, dict):
                    # OpenAI chat completions format
                    if "choices" in data and len(data["choices"]) > 0:
                        choice = data["choices"][0]
                        if "message" in choice:
                            return choice["message"].get("content", "")
                        elif "text" in choice:
                            return choice["text"]
                    # Simple response format
                    elif "response" in data:
                        return data["response"]
                    elif "text" in data:
                        return data["text"]
                    elif "content" in data:
                        return data["content"]
                    else:
                        return str(data)
                else:
                    return str(data)
                    
        except Exception as e:
            log.error(f"Error calling Modal endpoint: {e}")
            raise


class ModalDefender:
    """Defender model running on Modal.com infrastructure."""
    
    def __init__(
        self,
        app_name: str,
        model_name: str,
        function_name: str = "serve",
        modal_runner: Optional[ModalModelRunner] = None,
        api_endpoint: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize Modal-based defender.
        
        Args:
            app_name: Modal app name
            model_name: Model name (for compatibility/logging)
            function_name: Modal function name
            modal_runner: Optional Modal model runner
            api_endpoint: Optional direct API endpoint URL
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries
        """
        self.app_name = app_name
        self.model_name = model_name
        self.function_name = function_name
        self.modal_runner = modal_runner or ModalModelRunner()
        self.api_endpoint = api_endpoint
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        log.info(f"Initialized Modal defender: {app_name}/{function_name} (model: {model_name})")
        if api_endpoint:
            log.info(f"Using API endpoint: {api_endpoint}")
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate response using Modal-hosted model.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Model response
        """
        if self.api_endpoint:
            # Use direct endpoint
            try:
                # Increased timeout to handle model loading (can take 60-90 seconds on first request)
                async with httpx.AsyncClient(timeout=120.0) as client:
                    # Try chat/completions format first (OpenAI-compatible)
                    if "chat-completions" in self.api_endpoint.lower() or "chat_completions" in self.api_endpoint.lower():
                        payload = {
                            "messages": [{"role": "user", "content": prompt}],
                            "model": self.model_name,  # Pass model name to Modal
                            "max_tokens": kwargs.get("max_tokens", 1000),
                            "temperature": kwargs.get("temperature", 0.7)
                        }
                    else:
                        # Try completions format
                        payload = {
                            "prompt": prompt,
                            "model": self.model_name,  # Pass model name to Modal
                            "max_tokens": kwargs.get("max_tokens", 1000),
                            "temperature": kwargs.get("temperature", 0.7)
                        }
                    
                    for attempt in range(self.max_retries):
                        try:
                            log.debug(f"Calling Modal endpoint (attempt {attempt + 1}/{self.max_retries}): {self.api_endpoint}")
                            response = await client.post(self.api_endpoint, json=payload)
                            
                            # Handle 400 errors (bad request - like tokenizer errors)
                            if response.status_code == 400:
                                try:
                                    error_data = response.json()
                                    if isinstance(error_data, dict):
                                        detail = error_data.get("detail", {})
                                        if isinstance(detail, dict):
                                            error_msg = detail.get("message", "Unknown error")
                                            suggestion = detail.get("suggestion", "")
                                            raise ValueError(f"{error_msg}. {suggestion}")
                                        else:
                                            raise ValueError(f"Bad request: {detail}")
                                    else:
                                        raise ValueError(f"Bad request: {error_data}")
                                except Exception as parse_error:
                                    error_text = response.text[:500] if response.text else "No error text"
                                    raise ValueError(f"Bad request (status 400): {error_text}")
                            
                            # Handle 500 errors (server errors)
                            if response.status_code >= 500:
                                error_text = response.text[:500] if response.text else "No error text"
                                log.warning(f"Modal endpoint returned {response.status_code}: {error_text}")
                                if attempt < self.max_retries - 1:
                                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                                    continue
                                raise ValueError(f"Server error (status {response.status_code}): {error_text}")
                            
                            response.raise_for_status()
                            data = response.json()
                            
                            # Handle error responses in response body
                            if isinstance(data, dict) and "error" in data:
                                error_msg = data.get("message", "Unknown error")
                                suggestion = data.get("suggestion", "")
                                raise ValueError(f"{error_msg}. {suggestion}")
                            
                            # Handle OpenAI-compatible response format
                            if isinstance(data, str):
                                return data
                            elif isinstance(data, dict):
                                # OpenAI chat completions format
                                if "choices" in data and len(data["choices"]) > 0:
                                    choice = data["choices"][0]
                                    if "message" in choice:
                                        return choice["message"].get("content", "")
                                    elif "text" in choice:
                                        return choice["text"]
                                # Simple response format
                                return data.get("response") or data.get("text") or data.get("content") or str(data)
                            else:
                                return str(data)
                        except httpx.TimeoutException as e:
                            error_msg = f"Request timeout after {client.timeout.read} seconds"
                            log.warning(f"{error_msg} (attempt {attempt + 1}/{self.max_retries})")
                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(self.retry_delay * (2 ** attempt))
                                continue
                            raise ValueError(error_msg)
                        except httpx.RequestError as e:
                            error_msg = f"Connection error: {str(e) or type(e).__name__}"
                            log.warning(f"{error_msg} (attempt {attempt + 1}/{self.max_retries})")
                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(self.retry_delay * (2 ** attempt))
                                continue
                            raise ValueError(error_msg)
                        except Exception as e:
                            error_msg = str(e) or f"{type(e).__name__}: {repr(e)}"
                            log.warning(f"Request error: {error_msg} (attempt {attempt + 1}/{self.max_retries})")
                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(self.retry_delay * (2 ** attempt))
                                continue
                            raise
            except Exception as e:
                error_msg = str(e) or f"{type(e).__name__}: {repr(e)}"
                log.error(f"Error calling Modal endpoint {self.api_endpoint}: {error_msg}")
                raise ValueError(error_msg) from e
        else:
            # Use Modal runner
            return await self.modal_runner.generate_response(
                prompt, self.app_name, self.function_name, self.model_name, **kwargs
            )

