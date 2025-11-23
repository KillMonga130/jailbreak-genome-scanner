"""Cost calculator for Modal.com usage."""

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class CostEstimate:
    """Cost estimate for Modal.com usage."""
    total_cost: float
    per_request_cost: float
    compute_time_seconds: float
    gpu_type: str
    num_requests: int
    breakdown: Dict[str, float]


class ModalCostCalculator:
    """Calculate costs for Modal.com inference."""
    
    # GPU costs per second (as of 2024)
    GPU_COSTS = {
        "A10G": 0.0003,  # $0.0003/sec = $1.08/hour
        "A100": 0.0005,  # $0.0005/sec = $1.80/hour
        "H100": 0.001,   # $0.001/sec = $3.60/hour
    }
    
    # Average request times (seconds)
    # Cold start: 60-90s (first request, includes model loading)
    # Warm requests: 2-5s (subsequent requests, model cached)
    COLD_START_TIME = 75.0  # Average cold start time
    WARM_REQUEST_TIME = 3.5  # Average warm request time
    
    @classmethod
    def calculate_cost(
        cls,
        num_requests: int,
        gpu_type: str = "A10G",
        include_cold_start: bool = True,
        avg_tokens_per_request: int = 1000,
    ) -> CostEstimate:
        """
        Calculate estimated Modal.com cost.
        
        Args:
            num_requests: Number of requests
            gpu_type: GPU type (A10G, A100, H100)
            include_cold_start: Whether to include cold start cost
            avg_tokens_per_request: Average tokens per request (for estimation)
            
        Returns:
            CostEstimate object with breakdown
        """
        cost_per_second = cls.GPU_COSTS.get(gpu_type, cls.GPU_COSTS["A10G"])
        
        # Calculate compute time
        if include_cold_start and num_requests > 0:
            # First request: cold start
            compute_time = cls.COLD_START_TIME
            # Remaining requests: warm
            compute_time += (num_requests - 1) * cls.WARM_REQUEST_TIME
        else:
            # All warm requests
            compute_time = num_requests * cls.WARM_REQUEST_TIME
        
        # Calculate costs
        total_cost = compute_time * cost_per_second
        per_request_cost = total_cost / num_requests if num_requests > 0 else 0
        
        # Breakdown
        breakdown = {
            "cold_start": cls.COLD_START_TIME * cost_per_second if include_cold_start and num_requests > 0 else 0,
            "warm_requests": (num_requests - (1 if include_cold_start else 0)) * cls.WARM_REQUEST_TIME * cost_per_second if num_requests > 0 else 0,
            "compute_time_seconds": compute_time,
        }
        
        return CostEstimate(
            total_cost=total_cost,
            per_request_cost=per_request_cost,
            compute_time_seconds=compute_time,
            gpu_type=gpu_type,
            num_requests=num_requests,
            breakdown=breakdown
        )
    
    @classmethod
    def estimate_arena_cost(
        cls,
        num_attackers: int,
        num_rounds: int,
        gpu_type: str = "A10G",
    ) -> CostEstimate:
        """
        Estimate cost for a full arena evaluation.
        
        Args:
            num_attackers: Number of attackers
            num_rounds: Number of rounds
            gpu_type: GPU type
            
        Returns:
            CostEstimate object
        """
        # Each round: each attacker generates a prompt, defender responds
        # Total requests = num_rounds * (num_attackers + 1)
        # +1 because defender responds to each attacker's prompt
        total_requests = num_rounds * (num_attackers + 1)
        
        return cls.calculate_cost(
            num_requests=total_requests,
            gpu_type=gpu_type,
            include_cold_start=True
        )
    
    @classmethod
    def format_cost(cls, cost: float) -> str:
        """Format cost as currency string."""
        if cost < 0.01:
            return f"${cost:.4f}"
        elif cost < 1:
            return f"${cost:.3f}"
        else:
            return f"${cost:.2f}"
    
    @classmethod
    def get_cost_summary(cls, estimate: CostEstimate) -> str:
        """Get human-readable cost summary."""
        return f"""
Cost Estimate:
   Total: {cls.format_cost(estimate.total_cost)}
   Per Request: {cls.format_cost(estimate.per_request_cost)}
   Compute Time: {estimate.compute_time_seconds:.1f}s
   GPU: {estimate.gpu_type}
   
   Breakdown:
   - Cold Start: {cls.format_cost(estimate.breakdown['cold_start'])}
   - Warm Requests: {cls.format_cost(estimate.breakdown['warm_requests'])}
        """.strip()


def calculate_modal_cost(
    num_requests: int,
    gpu_type: str = "A10G",
    include_cold_start: bool = True,
) -> float:
    """
    Quick cost calculation function.
    
    Args:
        num_requests: Number of requests
        gpu_type: GPU type
        include_cold_start: Include cold start
        
    Returns:
        Total cost in USD
    """
    estimate = ModalCostCalculator.calculate_cost(
        num_requests=num_requests,
        gpu_type=gpu_type,
        include_cold_start=include_cold_start
    )
    return estimate.total_cost


if __name__ == "__main__":
    # Example usage
    print("Modal.com Cost Calculator\n")
    
    # Example 1: Single request
    estimate1 = ModalCostCalculator.calculate_cost(1, "A10G")
    print("Single Request:")
    print(ModalCostCalculator.get_cost_summary(estimate1))
    print()
    
    # Example 2: Arena evaluation
    estimate2 = ModalCostCalculator.estimate_arena_cost(
        num_attackers=3,
        num_rounds=10,
        gpu_type="A10G"
    )
    print("Arena Evaluation (3 attackers, 10 rounds):")
    print(ModalCostCalculator.get_cost_summary(estimate2))
    print()
    
    # Example 3: Batch processing (no cold start)
    estimate3 = ModalCostCalculator.calculate_cost(
        num_requests=100,
        gpu_type="A10G",
        include_cold_start=False
    )
    print("100 Warm Requests (model already loaded):")
    print(ModalCostCalculator.get_cost_summary(estimate3))

