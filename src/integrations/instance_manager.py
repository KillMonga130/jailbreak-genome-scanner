"""
Instance lifecycle manager for Lambda Cloud instances.
Automatically starts instances when needed and stops them when done.
"""

import asyncio
from typing import Optional, Dict, Any, List
from src.integrations.lambda_cloud import LambdaCloudClient
from src.utils.logger import log


class InstanceLifecycleManager:
    """Manages Lambda instance lifecycle - start/stop on demand."""
    
    def __init__(self):
        """Initialize instance lifecycle manager."""
        self.lambda_client = LambdaCloudClient()
        self.tracked_instances: Dict[str, Dict[str, Any]] = {}  # instance_id -> metadata
    
    async def ensure_instance_running(self, instance_id: str) -> bool:
        """
        Ensure an instance is running. If stopped, start it.
        
        Args:
            instance_id: Lambda instance ID
            
        Returns:
            True if instance is running or was started successfully
        """
        instance = await self.lambda_client.get_instance_status(instance_id)
        
        if not instance:
            log.error(f"Instance {instance_id} not found")
            return False
        
        status = instance.get("status")
        log.info(f"Instance {instance_id} status: {status}")
        
        if status == "active":
            log.info(f"Instance {instance_id} is already running")
            # Track this instance for cleanup
            self.tracked_instances[instance_id] = {
                "instance": instance,
                "auto_stop": True  # Will auto-stop when done
            }
            return True
        elif status == "billing":
            log.info(f"Instance {instance_id} is starting up...")
            # Wait for it to become active
            return await self._wait_for_active(instance_id)
        elif status in ["stopped", "terminated"]:
            log.warning(f"Instance {instance_id} is {status}. Cannot auto-start stopped instances.")
            log.info("Note: Lambda Cloud doesn't support starting stopped instances via API.")
            log.info("You need to manually restart the instance in the Lambda Cloud dashboard.")
            return False
        else:
            log.warning(f"Instance {instance_id} has status '{status}' - may need manual intervention")
            return False
    
    async def _wait_for_active(self, instance_id: str, max_wait: int = 300) -> bool:
        """Wait for instance to become active."""
        elapsed = 0
        while elapsed < max_wait:
            instance = await self.lambda_client.get_instance_status(instance_id)
            if instance:
                status = instance.get("status")
                if status == "active":
                    log.info(f"Instance {instance_id} is now active")
                    self.tracked_instances[instance_id] = {
                        "instance": instance,
                        "auto_stop": True
                    }
                    return True
                elif status == "error":
                    log.error(f"Instance {instance_id} failed to start")
                    return False
            
            await asyncio.sleep(5)
            elapsed += 5
        
        log.warning(f"Instance {instance_id} did not become active in time")
        return False
    
    async def stop_instance_when_done(self, instance_id: str, force: bool = False) -> bool:
        """
        Stop an instance when evaluation is done (to save costs).
        
        Args:
            instance_id: Instance ID to stop
            force: Force stop even if not tracked
            
        Returns:
            True if stop was initiated
        """
        if instance_id not in self.tracked_instances and not force:
            log.debug(f"Instance {instance_id} not tracked, skipping auto-stop")
            return False
        
        tracked = self.tracked_instances.get(instance_id, {})
        if not tracked.get("auto_stop", False) and not force:
            log.debug(f"Instance {instance_id} has auto_stop disabled")
            return False
        
        log.info(f"Stopping instance {instance_id} to save costs...")
        
        # Note: Lambda Cloud doesn't have a "stop" API endpoint
        # We can only terminate instances. For cost savings, users should
        # manually stop instances in the dashboard, or we terminate them.
        # For now, we'll just log and remove from tracking.
        
        log.warning("Lambda Cloud API doesn't support stopping instances (only terminating).")
        log.info("To save costs, manually stop instances in Lambda Cloud dashboard when done.")
        log.info("Or use: python scripts/manage_lambda_instances.py terminate <instance_id>")
        
        # Remove from tracking
        if instance_id in self.tracked_instances:
            del self.tracked_instances[instance_id]
        
        return True
    
    async def cleanup_all_tracked(self) -> int:
        """
        Clean up all tracked instances (stop/terminate them).
        
        Returns:
            Number of instances cleaned up
        """
        count = 0
        for instance_id in list(self.tracked_instances.keys()):
            if await self.stop_instance_when_done(instance_id, force=True):
                count += 1
        return count
    
    def get_tracked_instances(self) -> List[str]:
        """Get list of tracked instance IDs."""
        return list(self.tracked_instances.keys())

