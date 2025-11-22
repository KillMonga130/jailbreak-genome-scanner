# 🎯 Jailbreak Arena - Gamified Dashboard

## 🚀 Quick Start

### Option 1: Simple Launcher (Windows)
```bash
start_dashboard.bat
```

### Option 2: Direct Command
```bash
streamlit run dashboard/arena_dashboard.py
```

### Option 3: Python Script
```bash
python run_dashboard.py
```

## 🎮 What You'll See

### Live Battle Experience
1. **🔍 Perplexity Data Gathering** (if enabled)
   - Automatically fetches recent AI jailbreak techniques from the web
   - Shows gathered patterns before battle starts
   - Uses Perplexity AI for real-time intelligence

2. **🛡️ Defender Setup**
   - Choose your model type
   - Configure API keys if needed
   - System initializes defender

3. **⚔️ Live Battle Rounds**
   - Watch each round execute in real-time
   - See attacks succeed or fail instantly
   - Track statistics as they update
   - Progress bar shows battle progress

4. **📊 Real-Time Visualization**
   - **JVI Gauge**: Live vulnerability score (0-100)
   - **Leaderboard**: Top attackers chart updating in real-time
   - **Battle Logs**: Color-coded attack/defense logs
   - **Round Statistics**: Live metrics for each round

5. **🏆 Final Results**
   - Complete statistics
   - Downloadable JSON results
   - Final JVI score
   - Attacker rankings

## 🎯 Features

### ✅ Fully Gamified
- Beautiful gradient UI
- Live battle animations
- Color-coded logs (green=success, red=blocked)
- Real-time progress tracking
- Interactive charts and gauges

### ✅ Perplexity Integration
- **Automatic Data Gathering**: Fetches recent jailbreak patterns
- **Web Intelligence**: Gets latest techniques from the web
- **Pre-Battle Intelligence**: Shows gathered patterns before starting
- **Real-time Analysis**: Uses Perplexity AI for content analysis

### ✅ Live Visualization
- Round-by-round updates
- JVI score gauge (0-100)
- Attacker leaderboard chart
- Battle log with timestamps
- Success/failure indicators

### ✅ Multiple Defender Options
- **Mock (Demo)**: No API keys needed
- **OpenAI**: GPT-4, GPT-3.5, etc.
- **Anthropic**: Claude models
- **Lambda Cloud**: GPU-accelerated models

## 📖 Usage Guide

### Step 1: Configure Defender
1. Open sidebar (⚙️ icon)
2. Select defender type
3. Enter API keys if needed
4. Choose model name

### Step 2: Configure Attackers
1. Set number of attackers (3-10)
2. Set number of rounds (1-50)
3. More rounds = better statistics

### Step 3: Enable Perplexity (Recommended!)
1. Check "Gather Recent Attack Data"
2. Enter your Perplexity API key
3. System will gather recent patterns automatically

### Step 4: Start Battle!
1. Click "🚀 START LIVE BATTLE"
2. Watch Perplexity gather recent data
3. See defender initialize
4. Watch live battle rounds
5. View final results and download

## 🔍 Perplexity Features

When enabled, Perplexity will:
- 🔍 Search the web for recent jailbreak techniques
- 📊 Gather actual examples of attack patterns
- 🎯 Provide real-time intelligence before battle
- 💡 Show discovered patterns in expandable section

**Example Query:**
```
"What are recent AI jailbreak techniques and adversarial prompt 
patterns? Give specific examples with actual prompts."
```

## 📊 Dashboard Sections

### Main Battle Area
- Round-by-round results
- Live statistics
- Progress tracking

### Leaderboard
- Top attackers ranked by points
- Success rate for each attacker
- Interactive bar chart

### Battle Log
- Color-coded attack/defense logs
- Success (green) vs Blocked (red)
- Strategy and severity information
- Prompt previews

### Final Results
- JVI score gauge
- Complete statistics
- Downloadable JSON
- Attacker rankings

## 🎨 Gamification Elements

- **Live Battle Feel**: Real-time updates make it feel like a game
- **Visual Feedback**: Color-coded logs and status indicators
- **Progress Tracking**: Progress bar and round counter
- **Leaderboard**: Competitive rankings
- **Victory Conditions**: Clear success/failure indicators
- **Score System**: Points, JVI scores, success rates

## 💡 Tips

1. **Start with Mock**: Test the interface first
2. **Use Perplexity**: Get latest attack patterns automatically
3. **More Rounds**: Better statistics with more rounds
4. **Watch Logs**: See exactly what's happening
5. **Export Results**: Download for detailed analysis

## 🚨 Troubleshooting

**Dashboard won't start?**
- Make sure Streamlit is installed: `pip install streamlit plotly`
- Check if port 8501 is available

**Perplexity not working?**
- Check your API key
- Make sure you have internet connection
- API might be rate-limited

**Battle not starting?**
- Check defender configuration
- Verify API keys if using real models
- Try Mock mode first

## 🎉 Enjoy the Battle!

Watch AI attackers battle defenders in real-time! The fully gamified interface makes it exciting to see which attacks succeed and which are blocked. Perplexity integration ensures you're testing against the latest attack patterns discovered on the web!

