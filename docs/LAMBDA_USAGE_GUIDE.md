# Lambda Cloud Integration - Complete Usage Guide

## ✅ Connection Status

**Test Results:**
- ✅ API connection successful
- ✅ Authentication working
- ✅ Endpoint accessible (200 OK)
- ✅ No active instances found (normal if you haven't launched any)

## Setup

### 1. Configure API Key

Add your Lambda Cloud API secret to `.env`:

```env
LAMBDA_API_KEY=secret_muele_ce33a3396f9d406583bb611dc3ab0bd9.v5H38gHQqPMfwcPjXaIR6QKer9FglUZg
```

Or set as environment variable:

```bash
# Windows PowerShell
$env:LAMBDA_API_KEY="secret_muele_ce33a3396f9d406583bb611dc3ab0bd9.v5H38gHQqPMfwcPjXaIR6QKer9FglUZg"

# Linux/Mac
export LAMBDA_API_KEY="secret_muele_ce33a3396f9d406583bb611dc3ab0bd9.v5H38gHQqPMfwcPjXaIR6QKer9FglUZg"
```

### 2. Test Connection

```bash
python test_lambda.py
```

Expected output:
```
[OK] API Key found
[OK] Client initialized
[OK] Successfully retrieved 0 instances
[OK] API endpoint is accessible (200 OK)
[SUCCESS] All tests passed!
```

## Usage Patterns

### Pattern 1: Basic Instance Management

```python
import asyncio
from src.integrations.lambda_cloud import LambdaCloudClient

async def manage_instances():
    # Initialize client
    client = LambdaCloudClient()
    
    # List existing instances
    instances = await client.list_instances()
    print(f"Active instances: {len(instances)}")
    
    # Launch a new instance
    instance_data = await client.launch_instance(
        instance_type="gpu_1x_a10",
        region="us-east-1",
        quantity=1
    )
    
    instance_id = instance_data["instance_ids"][0]
    print(f"Launched instance: {instance_id}")
    
    # Check instance status
    instance = await client.get_instance_status(instance_id)
    print(f"Status: {instance['status']}, IP: {instance.get('ip', 'N/A')}")
    
    # Terminate when done (IMPORTANT!)
    await client.terminate_instance(instance_id)
    print(f"Terminated instance: {instance_id}")

# Run
asyncio.run(manage_instances())
```

### Pattern 2: Using Lambda for Model Evaluation (Defender)

```python
import asyncio
from src.integrations.lambda_cloud import LambdaModelRunner
from src.defenders.llm_defender import LLMDefender
from src.arena.jailbreak_arena import JailbreakArena

async def evaluate_with_lambda():
    # Step 1: Set up Lambda instance for model
    runner = LambdaModelRunner()
    
    print("Setting up Lambda instance...")
    instance_id = await runner.setup_model_environment(
        instance_type="gpu_1x_a10",
        model_name="meta-llama/Llama-2-7b-chat-hf"
    )
    
    if not instance_id:
        print("Failed to set up Lambda instance")
        return
    
    try:
        # Step 2: Create defender using Lambda
        defender = LLMDefender(
            model_name="meta-llama/Llama-2-7b-chat-hf",
            model_type="local",
            use_lambda=True,
            lambda_instance_id=instance_id
        )
        
        # Step 3: Use in Arena evaluation
        arena = JailbreakArena()
        arena.add_defender(defender)
        
        # Generate attackers
        arena.generate_attackers(num_strategies=5)
        
        # Run evaluation
        print("Running evaluation...")
        results = await arena.evaluate(rounds=10)
        
        # Get JVI score
        jvi = results.get('defenders')[0]['jvi']['jvi_score']
        print(f"JVI Score: {jvi:.2f}")
        
        # Export results
        arena.export_results("results.json")
        
    finally:
        # Step 4: Always clean up
        print("Cleaning up Lambda instance...")
        await runner.cleanup_instance(instance_id)

# Run
asyncio.run(evaluate_with_lambda())
```

### Pattern 3: Full Evaluation Pipeline with Lambda

```python
import asyncio
from src.integrations.lambda_cloud import LambdaModelRunner
from src.defenders.llm_defender import LLMDefender
from src.arena.jailbreak_arena import JailbreakArena
from src.genome.map_generator import GenomeMapGenerator

async def full_evaluation_pipeline():
    """
    Complete evaluation pipeline:
    1. Set up Lambda GPU instance
    2. Load model on Lambda
    3. Run Arena evaluation
    4. Generate Genome Map
    5. Calculate JVI scores
    6. Clean up
    """
    
    # Initialize Lambda runner
    runner = LambdaModelRunner()
    
    try:
        # 1. Launch Lambda instance
        print("=" * 60)
        print("STEP 1: Launching Lambda GPU instance")
        print("=" * 60)
        
        instance_id = await runner.setup_model_environment(
            instance_type="gpu_1x_a10",  # 1x NVIDIA A10 (24GB)
            model_name="meta-llama/Llama-2-7b-chat-hf"
        )
        
        if not instance_id:
            print("Failed to launch Lambda instance")
            return
        
        print(f"✓ Lambda instance ready: {instance_id}")
        
        # 2. Create defender
        print("\n" + "=" * 60)
        print("STEP 2: Creating defender model")
        print("=" * 60)
        
        defender = LLMDefender(
            model_name="meta-llama/Llama-2-7b-chat-hf",
            model_type="local",
            use_lambda=True,
            lambda_instance_id=instance_id
        )
        
        print(f"✓ Defender created: {defender.profile.model_name}")
        
        # 3. Set up Arena
        print("\n" + "=" * 60)
        print("STEP 3: Setting up Jailbreak Arena")
        print("=" * 60)
        
        arena = JailbreakArena()
        arena.add_defender(defender)
        
        # Generate diverse attackers
        arena.generate_attackers(
            num_strategies=10,
            strategies=[
                "roleplay",
                "emotional_coercion",
                "translation_attack",
                "prompt_inversion",
                "chain_of_command",
                "fictional_framing",
                "multi_turn_escalation",
                "indirect_request",
                "policy_probing",
                "honeypot"
            ]
        )
        
        print(f"✓ Arena ready: {len(arena.attackers)} attackers, 1 defender")
        
        # 4. Run evaluation
        print("\n" + "=" * 60)
        print("STEP 4: Running evaluation (100 rounds)")
        print("=" * 60)
        
        results = await arena.evaluate(rounds=100)
        
        print(f"✓ Evaluation complete:")
        print(f"  - Total evaluations: {results['statistics']['total_evaluations']}")
        print(f"  - Successful exploits: {results['statistics']['total_exploits']}")
        print(f"  - Exploit rate: {results['statistics']['exploit_rate']:.2%}")
        
        # 5. Calculate JVI
        print("\n" + "=" * 60)
        print("STEP 5: Calculating JVI scores")
        print("=" * 60)
        
        defender_result = results['defenders'][0]
        jvi = defender_result['jvi']['jvi_score']
        
        print(f"✓ Jailbreak Vulnerability Index (JVI): {jvi:.2f}/100")
        print(f"  - Exploit rate: {defender_result['jvi']['exploit_rate']:.2%}")
        print(f"  - Mean severity: {defender_result['jvi']['mean_severity']:.2f}/5")
        print(f"  - High-severity rate: {defender_result['jvi']['high_severity_rate']:.2%}")
        print(f"  - Failure diversity: {defender_result['jvi']['failure_diversity']:.3f}")
        
        # 6. Generate Genome Map
        print("\n" + "=" * 60)
        print("STEP 6: Generating Genome Map")
        print("=" * 60)
        
        successful_exploits = [
            e for e in results['evaluation_history'] if e.is_jailbroken
        ]
        
        if successful_exploits:
            map_generator = GenomeMapGenerator()
            genome_map = map_generator.generate(successful_exploits)
            
            print(f"✓ Genome Map generated: {len(genome_map)} failure clusters")
            
            # Visualize
            map_generator.visualize(
                genome_map,
                output_path="genome_map.png",
                show_plot=False
            )
            print("✓ Genome Map saved to genome_map.png")
        else:
            print("⚠️  No successful exploits found - cannot generate Genome Map")
        
        # 7. Export results
        print("\n" + "=" * 60)
        print("STEP 7: Exporting results")
        print("=" * 60)
        
        arena.export_results("evaluation_results.json")
        print("✓ Results exported to evaluation_results.json")
        
        # 8. Display leaderboard
        print("\n" + "=" * 60)
        print("STEP 8: Attacker Leaderboard")
        print("=" * 60)
        
        leaderboard = arena.get_leaderboard()
        print(f"\nTop 5 Attackers:")
        for i, attacker in enumerate(leaderboard.top_attackers[:5], 1):
            print(f"  {i}. {attacker.name} - {attacker.total_points:.2f} points "
                  f"(Success rate: {attacker.success_rate:.2%})")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Full evaluation pipeline complete!")
        print("=" * 60)
        
    finally:
        # 9. Clean up Lambda instance
        print("\n" + "=" * 60)
        print("STEP 9: Cleaning up Lambda instance")
        print("=" * 60)
        
        if instance_id:
            await runner.cleanup_instance(instance_id)
            print(f"✓ Lambda instance terminated: {instance_id}")
            print("✓ Charges stopped")

# Run full pipeline
if __name__ == "__main__":
    asyncio.run(full_evaluation_pipeline())
```

## Cost Management

### Instance Types and Pricing

| Instance Type | GPU | Memory | Price/Hour | Use Case |
|--------------|-----|--------|------------|----------|
| `gpu_1x_a10` | 1x A10 | 24GB | ~$0.50 | Small models (<7B params) |
| `gpu_1x_a100` | 1x A100 | 40GB | ~$1.10 | Medium models (7-13B params) |
| `gpu_8x_a100` | 8x A100 | 320GB | ~$8.80 | Large models (13B+ params) |
| `gpu_1x_h100` | 1x H100 | 80GB | ~$4.00 | Very large models |

### Best Practices

1. **Always Clean Up**: Terminate instances immediately after use
   ```python
   try:
       # ... use instance ...
   finally:
       await runner.cleanup_instance(instance_id)
   ```

2. **Monitor Usage**: Check Lambda Cloud dashboard regularly
   ```python
   instances = await client.list_instances()
   for instance in instances:
       print(f"Instance {instance['id']}: {instance['status']} - Cost: ~${hourly_rate}")
   ```

3. **Use Spot Instances**: Lambda Cloud offers spot pricing (lower cost)
4. **Batch Evaluations**: Run multiple evaluations on same instance to amortize costs

## Troubleshooting

### Common Issues

**Issue**: `401 Unauthorized`
- **Solution**: Check API key is correct in `.env` file
- **Test**: Run `python test_lambda.py`

**Issue**: `No instances found`
- **Solution**: This is normal if you haven't launched any instances
- **Action**: Launch an instance first

**Issue**: `Instance launch failed`
- **Solution**: Check instance type availability in region
- **Action**: Try different region or instance type

**Issue**: `Connection timeout`
- **Solution**: Check network connectivity to `cloud.lambda.ai`
- **Test**: `curl https://cloud.lambda.ai/api/v1/instances -u your_secret:`

## API Reference

### LambdaCloudClient

```python
client = LambdaCloudClient(api_key="your_secret")

# List instances
instances = await client.list_instances()

# Launch instance
instance_data = await client.launch_instance(
    instance_type="gpu_1x_a10",
    region="us-east-1",
    quantity=1
)

# Get instance status
instance = await client.get_instance_status(instance_id)

# Terminate instance
await client.terminate_instance(instance_id)

# Get SSH command
ssh_cmd = client.get_ssh_command(instance)
```

### LambdaModelRunner

```python
runner = LambdaModelRunner()

# Set up environment
instance_id = await runner.setup_model_environment(
    instance_type="gpu_1x_a10",
    model_name="meta-llama/Llama-2-7b-chat-hf"
)

# Clean up
await runner.cleanup_instance(instance_id)
```

## Next Steps

1. ✅ **Test Connection**: Run `python test_lambda.py`
2. ✅ **Launch Instance**: Use `Pattern 1` above
3. ✅ **Run Evaluation**: Use `Pattern 2` or `Pattern 3`
4. ✅ **Generate Results**: Export results and Genome Maps
5. ✅ **Clean Up**: Always terminate instances when done

## Support

- **Lambda Cloud Docs**: https://docs.lambda.ai
- **API Reference**: https://docs.lambda.ai/api-reference
- **Status Page**: Check Lambda Cloud status for outages

