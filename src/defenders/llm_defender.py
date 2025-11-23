"""Model Under Test (Defender) evaluation framework."""

import asyncio
from typing import Optional, Dict, Any, List
from src.models.jailbreak import DefenderProfile
from src.utils.logger import log
from src.config import settings


class LLMDefender:
    """Simplified defender using Modal.com only (with Mock fallback for testing)."""
    
    def __init__(
        self,
        model_name: str,
        model_type: str = "modal",
        api_endpoint: Optional[str] = None,
        mock_mode: bool = False,
        **kwargs
    ):
        """
        Initialize a defender model.
        
        Args:
            model_name: Name of the model (e.g., "microsoft/phi-2", "mistralai/Mistral-7B-Instruct-v0.2")
            model_type: Type of model provider ("modal" or "mock")
            api_endpoint: Modal.com API endpoint URL (auto-detected if not provided)
            mock_mode: If True, use mock defender for testing (overrides model_type)
            **kwargs: Additional model-specific parameters
        """
        self.model_name = model_name
        self.model_type = "mock" if mock_mode else model_type
        self.api_endpoint = api_endpoint or settings.modal_endpoint
        self.kwargs = kwargs
        
        # Initialize defender based on type
        self.defender = None
        if self.model_type == "mock" or mock_mode:
            # Mock defender for testing/demo
            self.defender = None  # Will use _generate_mock directly
            log.info(f"Initialized Mock defender: {model_name}")
        else:
            # Use Modal.com defender
            from src.integrations.modal_client import ModalDefender
            self.defender = ModalDefender(
                app_name="jailbreak-genome-scanner",
                model_name=model_name,
                api_endpoint=self.api_endpoint,
                **kwargs
            )
            log.info(f"Initialized Modal defender: {model_name} (endpoint: {self.api_endpoint})")
        
        # Create defender profile
        self.profile = DefenderProfile(
            id=f"defender_{model_name}_{self.model_type}",
            model_name=model_name,
            model_type=self.model_type,
            model_path=None,
            metadata=kwargs
        )
        
        # Initialize pre-processing filter if enabled
        self.preprocessing_filter = None
        if kwargs.get("enable_defense_filter", False):
            try:
                from src.defense.preprocessing_filter import PreProcessingFilter
                self.preprocessing_filter = PreProcessingFilter(
                    enable_blocking=kwargs.get("defense_filter_blocking", True)
                )
                log.info("Pre-processing defense filter enabled")
            except ImportError:
                log.warning("Defense filter module not available")
        
        # Initialize response guard if enabled
        self.response_guard = None
        if kwargs.get("enable_response_guard", False):
            try:
                from src.defense.response_guard import ResponseGuard
                self.response_guard = ResponseGuard(
                    enable_blocking=kwargs.get("response_guard_blocking", True),
                    strict_mode=kwargs.get("response_guard_strict", False)
                )
                log.info("Response guard enabled")
            except ImportError:
                log.warning("Response guard module not available")
        
        # Initialize adaptive system prompt if enabled
        self.adaptive_system_prompt = None
        if kwargs.get("enable_adaptive_prompt", False):
            try:
                from src.defense.adaptive_system_prompt import AdaptiveSystemPrompt
                self.adaptive_system_prompt = AdaptiveSystemPrompt(
                    base_prompt=kwargs.get("base_system_prompt"),
                    update_frequency_hours=kwargs.get("prompt_update_frequency", 24)
                )
                log.info("Adaptive system prompt enabled")
            except ImportError:
                log.warning("Adaptive system prompt module not available")
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate a response from the defender model.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Model response text
        """
        # Pre-processing filter (if enabled)
        if hasattr(self, 'preprocessing_filter') and self.preprocessing_filter:
            embedding = kwargs.get('embedding')
            attack_strategy = kwargs.get('attack_strategy')
            
            filtered_prompt, should_block, filter_info = self.preprocessing_filter.filter(
                prompt,
                embedding=embedding,
                attack_strategy=attack_strategy
            )
            
            if should_block:
                # Return safe response immediately
                log.info(f"Prompt blocked by pre-processing filter: {filter_info.get('reasons', [])}")
                return (
                    "I cannot assist with this request as it appears to be similar to known security threats. "
                    "If you have a legitimate question, please rephrase it in a way that focuses on "
                    "ethical and responsible use of technology."
                )
            
            # Use filtered prompt (may be modified)
            prompt = filtered_prompt
        
        try:
            # Generate response based on defender type
            if self.model_type == "mock":
                response = await self._generate_mock(prompt, **kwargs)
            elif self.defender:
                # Use Modal defender
                response = await self.defender.generate_response(prompt, **kwargs)
            else:
                raise ValueError(f"Defender not properly initialized for type: {self.model_type}")
            
            # Post-processing: Response Guard (if enabled)
            if hasattr(self, 'response_guard') and self.response_guard:
                attack_strategy = kwargs.get('attack_strategy')
                safe_response, should_block, validation_info = self.response_guard.validate_response(
                    prompt,
                    response,
                    attack_strategy=attack_strategy
                )
                
                if should_block:
                    log.info(f"Response blocked by response guard: {validation_info.get('reasons', [])}")
                    return safe_response
                
                # Use validated response
                response = safe_response
            
            # Check if response is an error (not a real model response)
            if response and response.startswith("Error:"):
                log.error(f"API call failed: {response[:200]}...")
                # Raise exception instead of returning error string
                raise RuntimeError(f"Modal API call failed: {response}")
            
            # Update profile stats only on successful response
            self.profile.total_evaluations += 1
            
            return response
        except Exception as e:
            log.error(f"Error generating response: {e}")
            error_msg = f"Error: {str(e)}"
            # Still increment evaluation count for error tracking
            self.profile.total_evaluations += 1
            return error_msg
    
    async def _generate_mock(self, prompt: str, **kwargs) -> str:
        """Generate mock response for testing."""
        # Simple rule-based mock: detect if prompt looks harmful
        prompt_lower = prompt.lower()
        
        harmful_keywords = [
            "hack", "exploit", "bypass", "ignore", "pretend",
            "dangerous", "harmful", "illegal"
        ]
        
        if any(keyword in prompt_lower for keyword in harmful_keywords):
            # Mock successful jailbreak
            return "I understand you want me to [REDACTED]. Here's how to do it..."
        else:
            # Mock safe response
            return "I can't help with that request. It may be harmful or inappropriate."
    
    def get_profile(self) -> DefenderProfile:
        """Get defender profile."""
        return self.profile
    
    def update_profile(self, **updates) -> None:
        """Update defender profile metrics."""
        for key, value in updates.items():
            if hasattr(self.profile, key):
                setattr(self.profile, key, value)


class DefenderRegistry:
    """Registry for managing multiple defender models."""
    
    def __init__(self):
        """Initialize the registry."""
        self.defenders: Dict[str, LLMDefender] = {}
    
    def register(self, defender: LLMDefender) -> None:
        """Register a defender."""
        self.defenders[defender.profile.id] = defender
        log.info(f"Registered defender: {defender.profile.id}")
    
    def get(self, defender_id: str) -> Optional[LLMDefender]:
        """Get a defender by ID."""
        return self.defenders.get(defender_id)
    
    def list_all(self) -> List[LLMDefender]:
        """List all registered defenders."""
        return list(self.defenders.values())
    
    def get_profiles(self) -> List[DefenderProfile]:
        """Get profiles of all defenders."""
        return [d.profile for d in self.defenders.values()]

