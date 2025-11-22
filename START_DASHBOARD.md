# 🎯 Jailbreak Arena Dashboard - Quick Start

## Start the Gamified Dashboard

Run this command to launch the interactive dashboard:

```bash
streamlit run dashboard/arena_dashboard.py
```

Or use the helper script:

```bash
python run_dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

## Features

### 🎮 Gamified Interface
- **Live Battle Visualization**: Watch rounds unfold in real-time
- **JVI Gauge**: Visual gauge showing vulnerability score (0-100)
- **Leaderboard**: Interactive chart showing top attackers
- **Battle Logs**: Real-time log of all attacks and defenses

### 🔍 Perplexity Integration
- **Recent Data Gathering**: Automatically fetches recent jailbreak patterns from the web
- **Attack Pattern Analysis**: Uses Perplexity AI to gather latest techniques
- **Real-time Intelligence**: Shows gathered patterns before battle starts

### ⚔️ Battle Modes

1. **Mock (Demo)**: No API keys needed - perfect for testing
2. **OpenAI**: Use GPT-4 or other OpenAI models
3. **Anthropic**: Use Claude models
4. **Lambda Cloud**: GPU-accelerated local models

### 📊 Live Visualization

- Real-time progress bar
- Round-by-round statistics
- Attack success/failure indicators
- Color-coded battle logs
- Final JVI score gauge

## Configuration

### Step 1: Choose Defender
Select your model type in the sidebar

### Step 2: Configure Attackers
- Number of attackers (3-10)
- Number of rounds (1-50)

### Step 3: Enable Perplexity (Optional)
- Check "Gather Recent Attack Data"
- Enter Perplexity API key
- System will gather recent jailbreak patterns automatically

### Step 4: Start Battle!
Click "🚀 START LIVE BATTLE"

## What You'll See

1. **Loading Phase**: Perplexity gathers recent data (if enabled)
2. **Setup Phase**: Defender initializes
3. **Battle Phase**: Rounds execute with live updates
4. **Results Phase**: Final statistics and visualizations

## Output Files

- Results JSON (downloadable button)
- Battle logs in the interface
- Leaderboard chart
- JVI score visualization

## Tips

- Start with Mock mode to see how it works
- Use Perplexity integration for latest attack patterns
- Increase rounds for better statistics
- Export results for detailed analysis

Enjoy the battle! 🎯

