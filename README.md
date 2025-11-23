# Jailbreak Genome Scanner (JGS) — The Immune System for AI

**Automated Red-Teaming & Radar System for Dual-Use Capabilities**

> **Built for the [Defensive Acceleration Hackathon](https://apartresearch.com/sprints) - Track 2: Cybersecurity & Infrastructure Protection**

## Overview

**Attackers are automating. A manual red team cannot keep up with a 100x acceleration in offensive AI capabilities.**

**JGS is the defensive acceleration answer: an automated, evolving system that maps the 'genome' of biological and cyber threats before they are deployed.**

The **Jailbreak Genome Scanner (JGS)** is an **Active Defense Infrastructure** designed to protect against catastrophic risks in AI systems. Instead of reactive filters that block harmful outputs after deployment, JGS provides **predictive defenses** through automated red-teaming at scale.

### 🏆 Hackathon Submission

This project addresses the **Defensive Acceleration Hackathon** challenge: building defensive systems that protect us from AI-enabled threats. JGS specifically targets **Track 2: Cybersecurity & Infrastructure Protection** by providing an **AI-powered red-teaming tool for critical infrastructure** that uses advanced models to automatically find vulnerabilities before attackers can exploit them.

At the heart of the system is the **Jailbreak Arena** — an automated red-teaming environment where specialized attacker agents (Bio-Radar, Cyber-Sentinel, and social engineering agents) systematically probe models for dual-use capabilities. Every exploit is fingerprinted and mapped to create a **Threat Radar** that identifies vulnerability patterns before attackers can exploit them.

The entire system forms a **pre-deployment risk assessment standard** that allows governments, enterprises, and AI labs to quantify catastrophic risk exposure before models are released.

## The Asymmetry Problem

**Offense is getting cheaper. A biology grad student with an LLM can now design vectors that used to require a state lab.**

Current defenses are **reactive** (filters). We need **predictive defenses**.

### The Critical Gap

- **Manual red teams cannot scale**: A 100x acceleration in offensive AI capabilities requires automated defense
- **Reactive filters fail**: They block outputs after deployment, not before
- **No threat intelligence**: We don't map attack patterns to vaccinate other models
- **Catastrophic risks unmeasured**: Biological and cyber weaponization capabilities go undetected
- **No pre-deployment standard**: Regulators lack quantitative risk assessment tools

**Impact**: AI labs, governments, and enterprises deploy models without understanding their dual-use risk exposure.

## The Solution: Automated Red-Teaming & Threat Radar

### A. Threat Radar System

JGS builds an evolutionary engine that finds threats before attackers do.

By running specialized attacker agents (Bio-Radar, Cyber-Sentinel) at 100x speed, JGS maps the "genome" of biological and cyber threats. The **Threat Radar** visualizes:

- **Pathogen Synthesis Vectors**: Clusters of biological weaponization capabilities
- **Zero-Day Exploit Patterns**: Memory safety vulnerabilities and code exploitation vectors
- **Attack Pattern Fingerprints**: Reusable signatures to vaccinate other models
- **JVI Live Monitor**: Real-time vulnerability tracking as models are patched

### B. The Jailbreak Arena — Automated Red-Teaming

An automated red-teaming environment where:
- **Bio-Radar Agent**: Tests for pathogen synthesis using obfuscated technical jargon
- **Cyber-Sentinel Agent**: Feeds vulnerable C++ code and tests memory safety exploitation
- **Social Agents**: Test emotional manipulation and policy boundary erosion
- **Defender** is the Model Under Test (MUT)
- **Referee** classifies harmfulness and fingerprints attack patterns
- **JVI Live Monitor**: Real-time dashboard showing vulnerability index as patches are applied

This is the dashboard a government regulator would use to decide if a model is safe to deploy.

### C. Pre-Deployment Risk Assessment Pipeline

JGS provides a standardized evaluation workflow:
1. **Auto-Red Teaming**: Run specialized agents at 100x speed
2. **Threat Fingerprinting**: Map exploit patterns to create vaccination signatures
3. **Threat Radar Generation**: Visualize "Pathogen Synthesis Vectors" and "Zero-Day Clusters"
4. **JVI Calculation**: Compute Jailbreak Vulnerability Index (0–100)
5. **Live Monitoring**: Track JVI as model is patched in real-time
6. **Regulatory Dashboard**: Export risk assessment for deployment decisions

## Key Components

### 1. Specialized Attacker Agents
Multi-domain attack generation including:
- **Bio-Radar Agent**: Obfuscated pathogen synthesis prompts using technical jargon
- **Cyber-Sentinel Agent**: C++/Rust vulnerability exploitation (buffer overflows, memory safety)
- **Social Engineering Agents**: Roleplay, emotional coercion, policy probing
- **Translation Attacks**: Cross-language boundary testing
- **Multi-turn Escalation**: Progressive boundary erosion

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

### 4. Threat Radar Engine
Transforms responses into embeddings → reduces dimensionality → clusters failure patterns → generates the **Threat Radar** with specialized visualization for:
- **Pathogen Synthesis Vectors** (bright red clusters)
- **Zero-Day Exploit Patterns** (cyber attack clusters)
- **Attack Pattern Fingerprints** (reusable vaccination signatures)

### 5. JVI — Jailbreak Vulnerability Index
A standardized robustness score (0–100), combining:
- Exploit rate
- Mean severity
- High-severity rate
- Failure-mode diversity (entropy)

### 6. JVI Live Monitor Dashboard
Real-time regulatory dashboard including:
- **JVI Live Score**: Real-time vulnerability index tracking
- **Threat Radar Visualization**: Interactive map showing "Pathogen Synthesis Vectors" and "Zero-Day Clusters"
- **Exploit-rate KPIs**: Per-threat-domain breakdown
- **Attack Pattern Library**: Fingerprinted exploits for model vaccination
- **Patch Tracking**: JVI score changes as model is updated
- **Regulatory Export**: Risk assessment reports for deployment decisions

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
│   ├── attackers/
│   │   ├── bio_agent.py        # Bio-Radar: Specialized pathogen synthesis prompter
│   │   ├── cyber_agent.py      # Cyber-Sentinel: C++/Rust vulnerability exploiter
│   │   └── social_agent.py     # Social engineering agents
│   ├── defenders/
│   │   └── shield_layer.py     # Lightweight filter trained on JGS data
│   ├── referee/                # Safety classifier & harmfulness scoring
│   ├── arena/                  # Automated red-teaming system
│   ├── genome/
│   │   └── threat_radar.py     # Threat Radar (renamed from map_generator)
│   ├── scoring/                # JVI calculation & metrics
│   ├── dashboard/              # JVI Live Monitor & regulatory dashboard
│   └── utils/                  # Utility functions
├── data/                       # Evaluation results & threat fingerprints
├── config/                     # Configuration files
└── tests/                      # Test suite
```

## Quick Start (Hackathon Demo)

### 1. Deploy to Modal.com

```bash
# Install Modal CLI
python -m pip install modal

# Deploy the infrastructure
python -m modal deploy modal_deploy.py
```

This creates three endpoints:
- `chat_completions` - OpenAI-compatible chat API (used by dashboard)
- `serve` - Simple prompt → response
- `completions` - OpenAI-compatible completions

### 2. Configure Environment

Add to your `.env` file:
```env
MODAL_ENDPOINT_CHAT=https://your-username--jailbreak-genome-scanner-chat-completions.modal.run
```

### 3. Launch Dashboard

```bash
streamlit run dashboard/arena_dashboard.py
```

### 4. Run Evaluation

1. Select **Defender Model** (model to test)
2. Select **Attacker Model** (generates attack prompts)
3. Select **Judge Model** (evaluates responses)
4. Configure attack parameters
5. Click **START EVALUATION**

## Installation (Full Setup)

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
# Edit .env with your Modal endpoint
```

## Configuration

### Modal.com Setup (Required)

JGS uses Modal.com for serverless model inference. After deploying, add to your `.env`:

```env
# Modal.com Configuration
MODAL_ENDPOINT_CHAT=https://your-username--jailbreak-genome-scanner-chat-completions.modal.run
MODAL_API_KEY=your_modal_api_key
MODAL_SECRET=your_modal_secret
```

### Optional Configuration

```env
# Vector database (for threat intelligence)
CHROMA_HOST=localhost
CHROMA_PORT=8000

# Arena configuration
ARENA_ROUNDS=100
MIN_ATTACKERS=5
SCORING_THRESHOLD=0.7
```

**Note:** JGS is now 100% Modal.com-based. All models (defender, attacker, judge) run on the same Modal.com infrastructure for cost efficiency.

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

### Multi-Strategy Attack Generation
Generate diverse adversarial prompts using roleplay, emotional coercion, translation attacks, and specialized Bio-Radar and Cyber-Sentinel agents.

### Comprehensive Defender Evaluation
Test any LLM model - open-source, fine-tuned, or enterprise APIs with automated red-teaming at scale.

### Safety Classification
Automated harmfulness scoring with severity levels and domain classification. Enhanced detection for obfuscated biological and cyber threats.

### Structural Vulnerability Mapping
Visualize failure patterns and exploit clusters in the Threat Radar. Highlights Pathogen Synthesis Vectors and Zero-Day Exploit Patterns.

### JVI Scoring
Standardized risk score (0-100) for cross-model comparison. Real-time JVI Live Monitor for regulatory assessment.

### Automated Red-Teaming Arena
Competitive evaluation environment with attacker rankings and live leaderboards. Runs at 100x speed for comprehensive coverage.

### Threat Fingerprinting
Attack pattern identification for model vaccination. Generates reusable signatures from Threat Radar analysis.

### Shield Layer Defense
Lightweight filter trained on JGS threat data. Blocks known attack patterns identified through automated red-teaming.

## Self-Evolving Architecture

JGS is designed to evolve with the AI ecosystem. New attacker strategies, threat domains, and safety classifiers can be plugged in as they emerge, creating a co-evolutionary loop:

**Better attacker models → Better evaluations → Safer defender models → Stronger JVI standards → Better attacker models...**

## Value Proposition: The Standard for Pre-Deployment Risk Assessment

- **For Governments & Regulators**: **JVI Live Monitor** — the dashboard to decide if a model is safe to deploy. Quantitative risk assessment for catastrophic risks (bio, cyber).
- **For AI Labs**: Automated red-teaming at 100x speed. Find vulnerabilities before attackers do. Threat fingerprinting for model vaccination.
- **For Enterprises**: Pre-deployment dual-use risk assessment. Compliance with biosecurity and cybersecurity regulations. Reduced catastrophic risk exposure.
- **For Defense Contractors**: Active defense infrastructure. Automated threat detection for biological and cyber weaponization capabilities.
- **For Red-Teamers**: Scalable adversarial testing. Attack pattern fingerprinting. Systematic coverage of dual-use capabilities.

## Security Considerations

**⚠️ Important:** See [SECURITY_CONSIDERATIONS.md](SECURITY_CONSIDERATIONS.md) for detailed security analysis, limitations, and recommendations.

### Key Points:

- All adversarial content remains in a controlled environment
- Harmful outputs are not exposed to end-users
- Evaluations must not be used for misuse or real-world harm
- Classifier blocks sensitive content from being displayed
- Attacker models are sandboxed
- Storage handles hazardous text securely

### Known Limitations:

- **False Positives/Negatives**: Automated evaluation may miss sophisticated attacks or flag legitimate responses
- **Model Selection Impact**: Evaluation quality depends on attacker and judge model capabilities
- **Coverage Gaps**: Cannot test all possible attack vectors automatically
- **Adversarial Robustness**: Evaluation system itself could be targeted

See the full Security Considerations document for detailed analysis and recommendations.

## Hackathon Submission

### Project Report

See [PROJECT_REPORT.md](PROJECT_REPORT.md) for the complete hackathon submission document including:
- Executive Summary
- AI Safety Relevance
- Def/Acc Relevance
- Execution Quality
- Demonstration Guide

### Key Features for Hackathon

✅ **Automated Red-Teaming**: 100x faster than manual testing  
✅ **Multi-Model Support**: Defender, Attacker, and Judge models on same infrastructure  
✅ **Maximum Difficulty Testing**: Always uses H1-H10 for comprehensive coverage  
✅ **Cost-Efficient**: 60-80% cost reduction via Modal.com serverless architecture  
✅ **Real-Time Dashboard**: Live evaluation monitoring and threat visualization  
✅ **Threat Intelligence**: Integration with pattern database for emerging attacks  

### Alignment with Hackathon Goals

- **Track 2: Cybersecurity & Infrastructure Protection** ✅
- **AI-Powered Red-Teaming Tool** ✅
- **Automated Vulnerability Discovery** ✅
- **Pre-Deployment Risk Assessment** ✅
- **Scalable Defense Infrastructure** ✅

## Documentation

- **[PROJECT_REPORT.md](PROJECT_REPORT.md)** - Complete hackathon submission
- **[SECURITY_CONSIDERATIONS.md](SECURITY_CONSIDERATIONS.md)** - Security analysis and limitations
- **[MODAL_MIGRATION_PLAN.md](MODAL_MIGRATION_PLAN.md)** - Infrastructure details

## License

MIT License - see [LICENSE](LICENSE) for details

## Authors

- Moses (moses130)
- Built for the Defensive Acceleration Hackathon (November 2024)
- Contributors welcome!

## Acknowledgments

Built for evaluating AI safety before deployment. Combines adversarial testing, competitive evaluation, and structural vulnerability analysis to create a comprehensive safety assessment framework.

**Hackathon Sponsors:**
- Halcyon Futures
- Apart Research
- BlueDot Impact
