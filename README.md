# Jailbreak Genome Scanner & Arena System

**A Self-Evolving, Pre-Deployment Safety Evaluation & Competitive Jailbreak Benchmarking Platform**

## Overview

The **Jailbreak Genome Scanner (JGS)** is a next-generation AI safety evaluation system designed to assess the robustness of large language models (LLMs) before deployment. Instead of relying on anecdotal prompt testing or post-deployment guardrails, JGS systematically probes models with a wide variety of adversarial strategies, measures how and why they fail, and visualizes their vulnerability patterns using a **Jailbreak Genome Map**.

At the heart of the system is the **Jailbreak Arena** — a game-inspired benchmarking environment where different attacker agents (either prompt strategies or attacker LLMs) compete to jailbreak a target model (the "Defender"). Every attacker earns points for successful exploits, while the Defender accumulates a quantitative risk score called the **Jailbreak Vulnerability Index (JVI)**.

The entire system forms a structural, repeatable, scalable evaluation framework that allows researchers, developers, enterprises, and regulators to understand jailbreak risks before models are released.

## The Core Problem

Modern LLMs can be jailbroken with surprisingly simple prompts. Today's guardrails and safety mechanisms suffer from critical limitations:

- **Reactive**: They attempt to block harmful outputs after deployment
- **Brittle**: Small paraphrases break them
- **Inconsistent**: Across models and settings
- **Poorly measured**: No standard scoring exists
- **Non-structural**: Tests are isolated cases, not patterns
- **Not designed for attacker diversity**
- **Rarely tested before deployment**

This leaves AI labs, enterprises, and regulators without a reliable way to quantify how jailbreakable a model is — or to understand why it is vulnerable.

## The Solution

### A. Structural Jailbreak Mapping

Instead of isolated prompts, JGS treats jailbreak detection as a pattern-recognition problem.

By generating diverse adversarial prompts, running them against a model, classifying the responses, embedding them, and clustering the results, JGS builds a **Jailbreak Genome Map** — a 2D representation of a model's structural weaknesses.

This visualization highlights:
- Clusters of failure modes
- Recurring exploit strategies
- Safety boundary weaknesses
- Severity distribution
- Cross-domain vulnerability patterns (cyber, bio, fraud, etc.)

### B. The Jailbreak Arena — Game-Based Evaluation

A competitive arena where:
- **Attackers** (strategies or LLMs) try to break the Defender
- **Defender** is the Model Under Test (MUT)
- **Referee** is the safety classifier scoring harmfulness
- **Scoreboard** displays attacker rankings and Defender risk

This mirrors Kaggle's Game Arena but applied to adversarial AI safety.

### C. Pre-Deployment Testing Pipeline

JGS provides a reproducible evaluation workflow:
1. Generate adversarial prompts across many attack families
2. Run them against the MUT (Llama, Mistral, Phi, Falcon, fine-tunes, enterprise models)
3. Classify responses using a harmfulness classifier
4. Embed + cluster failures to create the Genome Map
5. Compute the JVI score (0–100)
6. Visualize insights through a dashboard & Arena leaderboard

## Key Components

### 1. Adversarial Prompt Generator
Multi-strategy attack generation including:
- Roleplay
- Emotional coercion
- Translation-based attacks
- Prompt inversion
- Chain-of-command manipulation
- Fictional framing
- Multi-turn escalation
- Indirect harmful requests
- Policy probing

### 2. Model Under Test (Defender)
Runs evaluation on any LLM:
- Open-source models (Llama, Mistral, Phi, Falcon)
- Fine-tuned models
- Enterprise deployments (APIs, hosted systems)

### 3. Safety Classifier (Referee)
Labels each prompt–response pair with:
- Safe / unsafe
- Severity score (0–5)
- Violation domain (cyber, bio, fraud, violence, etc.)
- Boundary erosion indicators

### 4. Embedding + Clustering Engine
Transforms responses into embeddings → reduces dimensionality → clusters failure patterns → generates the Jailbreak Genome Map.

### 5. JVI — Jailbreak Vulnerability Index
A standardized robustness score (0–100), combining:
- Exploit rate
- Mean severity
- High-severity rate
- Failure-mode diversity (entropy)

### 6. Dashboard UI
Visual components including:
- Headline JVI score
- Exploit-rate KPIs
- Per-attack-family breakdown chart
- Interactive Genome Map
- Failure case explorer (drill-down)
- Attacker leaderboard (Arena mode)

### 7. Jailbreak Arena
A competitive, game-like environment featuring:
- Attacker strategy diversity
- Attacker model competition
- Rounds & scoring
- Evolving attacker pool
- Live leaderboard
- Defender (model) robustness comparison

## Architecture

```
jailbreak-genome-scanner/
├── src/
│   ├── attackers/          # Adversarial prompt generators & attack strategies
│   ├── defenders/          # Model Under Test (MUT) evaluation framework
│   ├── referee/            # Safety classifier & harmfulness scoring
│   ├── arena/              # Competitive evaluation system
│   ├── genome/             # Vulnerability mapping & clustering
│   ├── scoring/            # JVI calculation & metrics
│   ├── dashboard/          # UI components & visualizations
│   ├── agents/             # Emotional/cognitive agent frameworks (Inside Out style)
│   ├── permissions/        # Agent permissions & sandboxing system
│   └── utils/              # Utility functions
├── data/                   # Evaluation results & datasets
├── config/                 # Configuration files
└── tests/                  # Test suite
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/jailbreak-genome-scanner.git
cd jailbreak-genome-scanner
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Configuration

Create a `.env` file with your API credentials:

```env
# LLM APIs for testing
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
COHERE_API_KEY=your_cohere_key

# Local model paths (optional)
HUGGINGFACE_HUB_TOKEN=your_hf_token
LOCAL_MODEL_PATH=/path/to/local/model

# Safety classifier
SAFETY_CLASSIFIER_MODEL=path/to/classifier

# Lambda Cloud (for scraper and models)
LAMBDA_API_KEY=secret_xxx.xxx

# Vector database
CHROMA_HOST=localhost
CHROMA_PORT=8000

# Arena configuration
ARENA_ROUNDS=100
MIN_ATTACKERS=5
SCORING_THRESHOLD=0.7
```

## Usage

### Basic Evaluation

```python
from src.arena.jailbreak_arena import JailbreakArena
from src.defenders.llm_defender import LLMDefender
from src.attackers.prompt_generator import PromptGenerator

# Initialize arena
arena = JailbreakArena()

# Add defender (model to test)
defender = LLMDefender(
    model_name="gpt-4",
    api_key="your_key"
)
arena.add_defender(defender)

# Add attackers
prompt_generator = PromptGenerator()
attackers = prompt_generator.generate_attackers(num_strategies=10)
arena.add_attackers(attackers)

# Run evaluation
results = arena.evaluate(rounds=100)

# Get JVI score
jvi_score = results.get_jvi_score()
print(f"Jailbreak Vulnerability Index: {jvi_score:.2f}")
```

### Generate Genome Map

```python
from src.genome.map_generator import GenomeMapGenerator

# Generate vulnerability map
map_generator = GenomeMapGenerator()
genome_map = map_generator.generate(results)

# Visualize
map_generator.visualize(genome_map, output_path="genome_map.png")
```

### Command Line Interface

```bash
# Run full evaluation
python -m src.cli evaluate --defender gpt-4 --rounds 100

# Generate genome map
python -m src.cli genome --input results.json --output map.png

# Start Arena dashboard
python -m src.cli dashboard --port 8080
```

## Features

### 🎯 Multi-Strategy Attack Generation
Generate diverse adversarial prompts using roleplay, emotional coercion, translation attacks, and more.

### 🛡️ Comprehensive Defender Evaluation
Test any LLM model - open-source, fine-tuned, or enterprise APIs.

### ⚖️ Safety Classification
Automated harmfulness scoring with severity levels and domain classification.

### 🧬 Structural Vulnerability Mapping
Visualize failure patterns and exploit clusters in an interactive Genome Map.

### 📊 JVI Scoring
Standardized risk score (0-100) for cross-model comparison.

### 🏟️ Competitive Arena
Game-like evaluation environment with attacker rankings and live leaderboards.

### 🧠 Emotional/Cognitive Agents
Advanced agent frameworks inspired by Inside Out for testing social dynamics.

### 🔒 Permissions & Sandboxing
Secure agent execution with fine-grained permissions and monitoring.

## Self-Evolving Architecture

JGS is designed to evolve with the AI ecosystem. New attacker strategies, threat domains, and safety classifiers can be plugged in as they emerge, creating a co-evolutionary loop:

**Better attacker models → Better evaluations → Safer defender models → Stronger JVI standards → Better attacker models...**

## Value Proposition

- **For AI Labs**: Pre-deployment stress testing, structural vulnerability mapping, standardized safety scoring
- **For Enterprises**: Vendor LLM evaluation, compliance with AI regulations, reduced legal & security risk
- **For Governments & Regulators**: Model certification, safety thresholds, early-warning indicators
- **For Red-Teamers**: Scalable adversarial testing, automated coverage
- **For Researchers**: Reproducible, benchmarkable evaluation method

## Security Considerations

- All adversarial content remains in a controlled environment
- Harmful outputs are not exposed to end-users
- Evaluations must not be used for misuse or real-world harm
- Classifier blocks sensitive content from being displayed
- Attacker models are sandboxed
- Storage handles hazardous text securely

## License

MIT License - see [LICENSE](LICENSE) for details

## Authors

- Moses (moses130)
- Contributors welcome!

## Acknowledgments

Built for evaluating AI safety before deployment. Combines adversarial testing, competitive evaluation, and structural vulnerability analysis to create a comprehensive safety assessment framework.
