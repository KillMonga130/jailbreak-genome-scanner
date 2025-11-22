# Jailbreak Genome Scanner - Orchestration Guide

## System Overview

The **Jailbreak Genome Scanner & Arena System** orchestrates multiple components to evaluate LLM safety:

```
┌─────────────────────────────────────────────────────────────┐
│              Jailbreak Arena (Orchestrator)                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────┐ │
│  │  Attackers   │ ───▶ │   Defender   │ ───▶ │ Referee  │ │
│  │ (Prompts)    │      │   (Model)    │      │(Safety)  │ │
│  └──────────────┘      └──────────────┘      └──────────┘ │
│       │                       │                     │        │
│       │                       │                     │        │
│       ▼                       ▼                     ▼        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          Results & Evaluation Pipeline               │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  • JVI Calculator  • Genome Map Generator            │   │
│  │  • Leaderboard     • Statistics                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Component Roles

### 1. Attackers (Prompt Generators)
**Purpose**: Generate adversarial prompts using various strategies

**Strategies**:
- Roleplay
- Emotional coercion
- Translation attacks
- Prompt inversion
- Chain-of-command
- Fictional framing
- Multi-turn escalation
- Indirect requests
- Policy probing
- Honeypots

**Code**:
```python
from src.attackers.prompt_generator import PromptGenerator

generator = PromptGenerator()
attackers = generator.generate_attackers(num_strategies=10)

# Generate specific prompt
prompt = generator.generate_prompt(
    strategy=AttackStrategy.ROLEPLAY,
    target_domain="cyber"
)
```

### 2. Defender (Model Under Test)
**Purpose**: The LLM being evaluated for jailbreak vulnerabilities

**Supported**:
- OpenAI models (GPT-4, GPT-3.5)
- Anthropic models (Claude)
- Local models (Llama, Mistral, etc.)
- Lambda Cloud GPU instances

**Code**:
```python
from src.defenders.llm_defender import LLMDefender

# API-based model
defender = LLMDefender(
    model_name="gpt-4",
    model_type="openai",
    api_key="your_key"
)

# Lambda Cloud model
defender = LLMDefender(
    model_name="meta-llama/Llama-2-7b-chat-hf",
    model_type="local",
    use_lambda=True,
    lambda_instance_id="instance_123"
)

# Generate response
response = await defender.generate_response("Test prompt")
```

### 3. Referee (Safety Classifier)
**Purpose**: Classify responses for harmfulness and severity

**Classification**:
- Is jailbroken? (Yes/No)
- Severity level (0-5)
- Violation domains (cyber, bio, fraud, etc.)
- Harmfulness score (0-1)

**Code**:
```python
from src.referee.safety_classifier import SafetyClassifier

referee = SafetyClassifier(classifier_type="rule_based")

evaluation = await referee.classify(
    prompt="adversarial prompt",
    response="model response",
    attack_strategy=AttackStrategy.ROLEPLAY
)

print(f"Jailbroken: {evaluation.is_jailbroken}")
print(f"Severity: {evaluation.severity}")
print(f"Domains: {evaluation.violation_domains}")
```

### 4. Arena (Orchestrator)
**Purpose**: Coordinate the entire evaluation process

**Responsibilities**:
- Manage attackers and defenders
- Run evaluation rounds
- Track scores and statistics
- Generate results and leaderboards

**Code**:
```python
from src.arena.jailbreak_arena import JailbreakArena

arena = JailbreakArena()

# Add defender
arena.add_defender(defender)

# Generate attackers
arena.generate_attackers(num_strategies=10)

# Run evaluation
results = await arena.evaluate(rounds=100)

# Get results
jvi_score = arena.get_jvi_score()
leaderboard = arena.get_leaderboard()
```

### 5. JVI Calculator
**Purpose**: Calculate standardized vulnerability score (0-100)

**Components**:
- Exploit rate (30% weight)
- Mean severity (30% weight)
- High-severity rate (25% weight)
- Failure diversity (15% weight)

**Code**:
```python
from src.scoring.jvi_calculator import JVICalculator

calculator = JVICalculator()

jvi_result = calculator.calculate_jvi(
    evaluations=evaluation_results,
    defender_profile=defender.profile
)

print(f"JVI Score: {jvi_result['jvi_score']:.2f}/100")
print(f"Category: {calculator.get_jvi_category(jvi_result['jvi_score'])}")
```

### 6. Genome Map Generator
**Purpose**: Visualize structural vulnerability patterns

**Process**:
1. Embed successful exploits
2. Reduce dimensionality (UMAP/PCA)
3. Cluster failures
4. Generate visualization

**Code**:
```python
from src.genome.map_generator import GenomeMapGenerator

generator = GenomeMapGenerator()

# Generate map from evaluations
genome_map = generator.generate(
    evaluations=successful_exploits,
    min_cluster_size=3,
    reduction_dimensions=2
)

# Visualize
generator.visualize(
    genome_map,
    output_path="genome_map.png",
    show_plot=False
)
```

## Complete Orchestration Example

```python
import asyncio
from src.arena.jailbreak_arena import JailbreakArena
from src.defenders.llm_defender import LLMDefender
from src.integrations.lambda_cloud import LambdaModelRunner
from src.genome.map_generator import GenomeMapGenerator

async def full_orchestration():
    """
    Complete orchestration of the evaluation system:
    1. Set up infrastructure (Lambda Cloud)
    2. Initialize components
    3. Run evaluation
    4. Generate results
    5. Clean up
    """
    
    runner = LambdaModelRunner()
    instance_id = None
    
    try:
        # STEP 1: Infrastructure Setup
        print("Setting up Lambda GPU instance...")
        instance_id = await runner.setup_model_environment(
            instance_type="gpu_1x_a10",
            model_name="meta-llama/Llama-2-7b-chat-hf"
        )
        
        # STEP 2: Initialize Components
        print("Initializing components...")
        
        # Defender
        defender = LLMDefender(
            model_name="meta-llama/Llama-2-7b-chat-hf",
            model_type="local",
            use_lambda=True,
            lambda_instance_id=instance_id
        )
        
        # Arena
        arena = JailbreakArena()
        arena.add_defender(defender)
        arena.generate_attackers(num_strategies=10)
        
        # STEP 3: Run Evaluation
        print("Running evaluation...")
        results = await arena.evaluate(rounds=100)
        
        # STEP 4: Generate Results
        print("Generating results...")
        
        # JVI Score
        jvi = results['defenders'][0]['jvi']['jvi_score']
        print(f"JVI Score: {jvi:.2f}/100")
        
        # Genome Map
        exploits = [e for e in results['evaluation_history'] if e.is_jailbroken]
        if exploits:
            map_gen = GenomeMapGenerator()
            genome_map = map_gen.generate(exploits)
            map_gen.visualize(genome_map, output_path="genome_map.png")
        
        # Export
        arena.export_results("results.json")
        
        # Leaderboard
        leaderboard = arena.get_leaderboard()
        print(f"\nTop Attacker: {leaderboard.top_attackers[0].name}")
        
        return results
        
    finally:
        # STEP 5: Cleanup
        if instance_id:
            print("Cleaning up...")
            await runner.cleanup_instance(instance_id)

# Run
asyncio.run(full_orchestration())
```

## Evaluation Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Evaluation Flow                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Initialize Arena                                          │
│     ├─ Add Defender(s)                                        │
│     ├─ Generate Attackers                                     │
│     └─ Initialize Referee                                     │
│                                                               │
│  2. For each Round:                                           │
│     ├─ For each Attacker:                                     │
│     │   ├─ Generate adversarial prompt                        │
│     │   ├─ Send to Defender (get response)                    │
│     │   ├─ Classify response (Referee)                        │
│     │   ├─ Update attacker scores                             │
│     │   └─ Store evaluation result                            │
│     └─ Update round statistics                                │
│                                                               │
│  3. Calculate Results:                                        │
│     ├─ Compute JVI scores                                     │
│     ├─ Generate Genome Map                                    │
│     ├─ Create Leaderboard                                     │
│     └─ Export results                                         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

### Environment Variables

```env
# Lambda Cloud
LAMBDA_API_KEY=secret_xxx.xxx
LAMBDA_DEFAULT_INSTANCE_TYPE=gpu_1x_a10
LAMBDA_DEFAULT_REGION=us-east-1

# LLM APIs
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx

# Arena Configuration
ARENA_ROUNDS=100
MIN_ATTACKERS=5
SCORING_THRESHOLD=0.7

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/scanner.log
```

### Programmatic Configuration

```python
from src.config import settings

# Modify settings
settings.arena_rounds = 200
settings.min_attackers = 10
settings.scoring_threshold = 0.8
```

## Best Practices

### 1. Resource Management
- Always clean up Lambda instances after use
- Use context managers or try/finally blocks
- Monitor costs regularly

### 2. Evaluation Design
- Use diverse attacker strategies
- Run sufficient rounds for statistical significance
- Test multiple defenders for comparison

### 3. Results Analysis
- Check JVI score and components
- Examine Genome Map clusters
- Review top attack strategies
- Identify failure patterns

### 4. Performance
- Run evaluations in parallel when possible
- Batch process multiple defenders
- Cache embeddings for Genome Maps
- Use GPU instances for local models

## Next Steps

1. **Test Connection**: `python test_lambda.py`
2. **Run Simple Evaluation**: Use basic arena example
3. **Full Pipeline**: Use complete orchestration example
4. **Analyze Results**: Generate Genome Maps and JVI scores
5. **Scale Up**: Test multiple defenders and strategies

