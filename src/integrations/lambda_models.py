"""Lambda Cloud model deployment and management for open source models."""

import asyncio
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from src.integrations.lambda_cloud import LambdaCloudClient, LambdaModelRunner
from src.utils.logger import log


class LambdaModelDeployment:
    """Manages deployment of open source models on Lambda Cloud."""
    
    # Common open source models and their requirements
    OPEN_SOURCE_MODELS = {
        "llama-2-7b-chat": {
            "model_name": "meta-llama/Llama-2-7b-chat-hf",
            "instance_type": "gpu_1x_a10",
            "memory_gb": 14,
            "description": "Llama 2 7B Chat - Good for testing and development"
        },
        "llama-2-13b-chat": {
            "model_name": "meta-llama/Llama-2-13b-chat-hf",
            "instance_type": "gpu_1x_a100",
            "memory_gb": 26,
            "description": "Llama 2 13B Chat - Better capabilities"
        },
        "mistral-7b-instruct": {
            "model_name": "mistralai/Mistral-7B-Instruct-v0.2",
            "instance_type": "gpu_1x_a10",
            "memory_gb": 14,
            "description": "Mistral 7B Instruct - High quality responses"
        },
        "phi-2": {
            "model_name": "microsoft/phi-2",
            "instance_type": "gpu_1x_a10",
            "memory_gb": 5,
            "description": "Phi-2 - Small but capable model"
        },
        "falcon-7b-instruct": {
            "model_name": "tiiuae/falcon-7b-instruct",
            "instance_type": "gpu_1x_a10",
            "memory_gb": 14,
            "description": "Falcon 7B Instruct - Good for instruction following"
        },
        "qwen-7b-chat": {
            "model_name": "Qwen/Qwen-7B-Chat",
            "instance_type": "gpu_1x_a10",
            "memory_gb": 14,
            "description": "Qwen 7B Chat - Multilingual support"
        }
    }
    
    def __init__(self, lambda_client: Optional[LambdaCloudClient] = None):
        """
        Initialize model deployment manager.
        
        Args:
            lambda_client: Optional Lambda Cloud client
        """
        self.lambda_client = lambda_client or LambdaCloudClient()
        self.model_runner = LambdaModelRunner(lambda_client=self.lambda_client)
        self.deployed_models: Dict[str, Dict[str, Any]] = {}
        
        log.info("Lambda Model Deployment initialized")
    
    async def deploy_model(
        self,
        model_key: str,
        instance_type: Optional[str] = None,
        region: str = "us-east-1"
    ) -> Optional[str]:
        """
        Deploy an open source model on Lambda Cloud.
        
        Args:
            model_key: Model key (e.g., "llama-2-7b-chat")
            instance_type: Optional instance type override
            region: AWS region
            
        Returns:
            Instance ID if successful
        """
        if model_key not in self.OPEN_SOURCE_MODELS:
            log.error(f"Unknown model key: {model_key}")
            log.info(f"Available models: {list(self.OPEN_SOURCE_MODELS.keys())}")
            return None
        
        model_config = self.OPEN_SOURCE_MODELS[model_key]
        model_name = model_config["model_name"]
        instance_type = instance_type or model_config["instance_type"]
        
        log.info(f"Deploying {model_key} ({model_name}) on {instance_type}...")
        
        # Launch instance
        instance_data = await self.model_runner.setup_model_environment(
            instance_type=instance_type,
            model_name=model_name
        )
        
        if instance_data:
            self.deployed_models[model_key] = {
                "instance_id": instance_data,
                "model_name": model_name,
                "instance_type": instance_type,
                "region": region,
                "status": "deploying"
            }
            log.info(f"✅ Deployed {model_key} on instance {instance_data}")
            return instance_data
        else:
            log.error(f"Failed to deploy {model_key}")
            return None
    
    async def deploy_all_models(
        self,
        instance_types: Optional[Dict[str, str]] = None,
        region: str = "us-east-1"
    ) -> Dict[str, Optional[str]]:
        """
        Deploy all open source models on Lambda Cloud.
        
        Args:
            instance_types: Optional dict of model_key -> instance_type overrides
            region: AWS region
            
        Returns:
            Dict mapping model_key to instance_id
        """
        results = {}
        
        log.info(f"Deploying {len(self.OPEN_SOURCE_MODELS)} open source models...")
        
        for model_key in self.OPEN_SOURCE_MODELS.keys():
            instance_type = instance_types.get(model_key) if instance_types else None
            
            instance_id = await self.deploy_model(
                model_key=model_key,
                instance_type=instance_type,
                region=region
            )
            
            results[model_key] = instance_id
            
            # Small delay between deployments
            await asyncio.sleep(5)
        
        log.info(f"Deployment complete: {sum(1 for v in results.values() if v)}/{len(results)} successful")
        return results
    
    async def list_deployed_models(self) -> List[Dict[str, Any]]:
        """List all deployed models."""
        instances = await self.lambda_client.list_instances()
        
        deployed = []
        for instance in instances:
            if instance.get("status") == "active":
                # Try to match to our model configurations
                instance_id = instance.get("id")
                instance_type = instance.get("instance_type", {}).get("name", "unknown")
                
                # Check if this instance matches any of our models
                for model_key, model_config in self.OPEN_SOURCE_MODELS.items():
                    if instance_type == model_config["instance_type"]:
                        deployed.append({
                            "model_key": model_key,
                            "instance_id": instance_id,
                            "model_name": model_config["model_name"],
                            "instance_type": instance_type,
                            "ip": instance.get("ip"),
                            "status": instance.get("status")
                        })
        
        return deployed
    
    async def get_model_instance(self, model_key: str) -> Optional[str]:
        """
        Get instance ID for a deployed model.
        
        Args:
            model_key: Model key
            
        Returns:
            Instance ID if found
        """
        deployed = await self.list_deployed_models()
        
        for model in deployed:
            if model["model_key"] == model_key:
                return model["instance_id"]
        
        return None
    
    async def cleanup_model(self, model_key: str) -> bool:
        """
        Clean up a deployed model.
        
        Args:
            model_key: Model key
            
        Returns:
            True if successful
        """
        instance_id = await self.get_model_instance(model_key)
        
        if instance_id:
            success = await self.model_runner.cleanup_instance(instance_id)
            if success:
                if model_key in self.deployed_models:
                    del self.deployed_models[model_key]
                log.info(f"✅ Cleaned up {model_key} (instance {instance_id})")
                return True
        
        log.warning(f"Could not find deployed model: {model_key}")
        return False
    
    async def cleanup_all_models(self) -> Dict[str, bool]:
        """Clean up all deployed models."""
        deployed = await self.list_deployed_models()
        
        results = {}
        for model in deployed:
            model_key = model["model_key"]
            results[model_key] = await self.cleanup_model(model_key)
        
        return results
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available open source models."""
        return [
            {
                "key": key,
                "model_name": config["model_name"],
                "instance_type": config["instance_type"],
                "memory_gb": config["memory_gb"],
                "description": config["description"]
            }
            for key, config in self.OPEN_SOURCE_MODELS.items()
        ]
    
    def save_deployment_config(self, file_path: str):
        """Save deployment configuration to file."""
        config = {
            "deployed_models": self.deployed_models,
            "available_models": {
                key: {
                    "model_name": config["model_name"],
                    "instance_type": config["instance_type"],
                    "description": config["description"]
                }
                for key, config in self.OPEN_SOURCE_MODELS.items()
            }
        }
        
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(config, f, indent=2)
        
        log.info(f"Saved deployment config to {file_path}")
    
    @classmethod
    def load_deployment_config(cls, file_path: str) -> Dict[str, Any]:
        """Load deployment configuration from file."""
        path = Path(file_path)
        
        if not path.exists():
            return {}
        
        with open(path, 'r') as f:
            config = json.load(f)
        
        return config

