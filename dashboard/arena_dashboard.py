"""Professional Jailbreak Arena Dashboard - Real-time Evaluation Interface"""

import streamlit as st
import asyncio
import json
import time
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os
import pandas as pd
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import after path setup
from src.arena.jailbreak_arena import JailbreakArena
from src.defenders.llm_defender import LLMDefender
from src.attackers.prompt_generator import PromptGenerator
from src.models.jailbreak import AttackStrategy, EvaluationResult
from src.integrations.lambda_scraper import LambdaWebScraper
from src.scoring.jvi_calculator import JVICalculator
from src.visualization.vector3d_generator import Vector3DGenerator
from src.utils.logger import setup_logger, log

# Page config
st.set_page_config(
    page_title="Jailbreak Arena",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Jailbreak Arena - Real-time AI Safety Evaluation Platform"
    }
)

# Professional dark theme CSS with subtle animations
st.markdown("""
<style>
    /* Main theme - Dark */
    .main {
        background-color: #0a0a0a;
        color: #e0e0e0;
    }
    
    /* Streamlit base styling */
    .stApp {
        background-color: #0a0a0a;
    }
    
    /* Header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        color: #ffffff;
        letter-spacing: -0.02em;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #333333;
        animation: fadeIn 0.6s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Professional stat boxes */
    .stat-box {
        background: #1a1a1a;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #333333;
        text-align: center;
        transition: all 0.3s ease;
        animation: slideUp 0.4s ease-out;
        color: #e0e0e0;
    }
    
    .stat-box:hover {
        border-color: #555555;
        box-shadow: 0 4px 12px rgba(255,255,255,0.1);
        transform: translateY(-2px);
        background: #222222;
    }
    
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Live battle container */
    .live-battle {
        background: #1a1a1a;
        padding: 2rem;
        border-radius: 8px;
        border: 2px solid #444444;
        margin: 1rem 0;
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { border-color: #444444; }
        50% { border-color: #666666; }
    }
    
    /* Log styling */
    .attack-log {
        background: #1a1a1a;
        padding: 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        border-left: 3px solid #555555;
        font-family: 'Courier New', monospace;
        font-size: 0.875rem;
        color: #e0e0e0;
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-10px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* Success - green accent */
    .success-log {
        background: #1a2e1a;
        padding: 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        border-left: 3px solid #28a745;
        font-family: 'Courier New', monospace;
        color: #a0e0a0;
        animation: slideIn 0.3s ease-out;
    }
    
    /* Fail - red accent */
    .fail-log {
        background: #2e1a1a;
        padding: 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        border-left: 3px solid #dc3545;
        font-family: 'Courier New', monospace;
        color: #e0a0a0;
        animation: slideIn 0.3s ease-out;
    }
    
    /* Progress indicator */
    .progress-indicator {
        width: 100%;
        height: 4px;
        background: #333333;
        border-radius: 2px;
        overflow: hidden;
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a;
    }
    
    /* Metric cards */
    .metric-card {
        background: #1a1a1a;
        border: 1px solid #333333;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        transition: all 0.3s ease;
        color: #e0e0e0;
    }
    
    .metric-card:hover {
        border-color: #555555;
        transform: scale(1.02);
        background: #222222;
    }
    
    /* Subtle loading animation */
    .loading-dots::after {
        content: '...';
        animation: dots 1.5s steps(4, end) infinite;
    }
    
    @keyframes dots {
        0%, 20% { content: '.'; }
        40% { content: '..'; }
        60%, 100% { content: '...'; }
    }
    
    /* Professional button */
    .stButton > button {
        background-color: #333333;
        color: #ffffff;
        border-radius: 6px;
        transition: all 0.3s ease;
        border: 1px solid #555555;
    }
    
    .stButton > button:hover {
        background-color: #444444;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(255,255,255,0.1);
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: #28a745;
    }
    
    /* Text colors */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    p, label, .stText {
        color: #e0e0e0 !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #1a1a1a;
        color: #e0e0e0;
        border: 1px solid #333333;
    }
    
    .stSelectbox > div > div > select {
        background-color: #1a1a1a;
        color: #e0e0e0;
        border: 1px solid #333333;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1a1a1a;
        color: #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)


def run_async(coro):
    """Run async function in Streamlit."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    if loop.is_running():
        import nest_asyncio
        nest_asyncio.apply()
    
    return loop.run_until_complete(coro)


def create_jvi_gauge(value):
    """Create professional JVI score gauge visualization with enhanced styling."""
    # Color scale: green (safe) to red (vulnerable) - only for visualization
    colors = ['#28a745', '#ffc107', '#fd7e14', '#dc3545']
    thresholds = [20, 50, 80, 100]
    
    # Determine color based on value
    color = colors[0]
    for i, threshold in enumerate(thresholds):
        if value <= threshold:
            color = colors[i] if i < len(colors) else colors[-1]
            break
    
    # Get category label
    if value < 20:
        category = "Very Low Risk"
    elif value < 40:
        category = "Low Risk"
    elif value < 60:
        category = "Moderate Risk"
    elif value < 80:
        category = "High Risk"
    else:
        category = "Critical Risk"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"JVI Score<br><span style='font-size:0.8em;color:{color}'>{category}</span>", 
               'font': {'size': 22, 'color': '#ffffff'}},
        number={'font': {'size': 40, 'color': color}, 'suffix': '/100'},
        delta={'reference': 50, 'position': "top", 'font': {'size': 16}},
        gauge={
            'axis': {'range': [None, 100], 'tickcolor': '#e0e0e0', 'tickwidth': 2, 'tickmode': 'linear', 'tick0': 0, 'dtick': 20},
            'bar': {'color': color, 'thickness': 0.15},
            'bgcolor': '#1a1a1a',
            'borderwidth': 3,
            'bordercolor': '#555555',
            'steps': [
                {'range': [0, 20], 'color': '#1a3a1a'},
                {'range': [20, 50], 'color': '#3a3a1a'},
                {'range': [50, 80], 'color': '#3a1a1a'},
                {'range': [80, 100], 'color': '#3a0a0a'}
            ],
            'threshold': {
                'line': {'color': '#dc3545', 'width': 4},
                'thickness': 0.8,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='#1a1a1a',
        plot_bgcolor='#1a1a1a',
        font={'color': '#e0e0e0', 'family': 'Arial, sans-serif'}
    )
    return fig


def create_trend_chart(evaluation_history: List[Dict]) -> Optional[go.Figure]:
    """Create trend chart showing exploit rate over time."""
    if not evaluation_history:
        return None
    
    # Process history to get exploit rates over rounds
    rounds_data = {}
    for i, eval_result in enumerate(evaluation_history):
        round_num = i // 10 + 1  # Approximate round number
        if round_num not in rounds_data:
            rounds_data[round_num] = {'total': 0, 'exploits': 0}
        
        rounds_data[round_num]['total'] += 1
        is_jailbroken = eval_result.get('is_jailbroken', False) if isinstance(eval_result, dict) else eval_result.is_jailbroken
        if is_jailbroken:
            rounds_data[round_num]['exploits'] += 1
    
    rounds = sorted(rounds_data.keys())
    exploit_rates = [(rounds_data[r]['exploits'] / rounds_data[r]['total'] * 100) for r in rounds]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rounds,
        y=exploit_rates,
        mode='lines+markers',
        name='Exploit Rate',
        line=dict(color='#dc3545', width=3),
        marker=dict(size=8, color='#dc3545')
    ))
    
    fig.update_layout(
        title={'text': 'Exploit Rate Trend', 'font': {'size': 18, 'color': '#ffffff'}},
        xaxis={'title': 'Round', 'tickfont': {'color': '#e0e0e0'}, 'gridcolor': '#333333'},
        yaxis={'title': 'Exploit Rate (%)', 'tickfont': {'color': '#e0e0e0'}, 'gridcolor': '#333333'},
        height=300,
        paper_bgcolor='#1a1a1a',
        plot_bgcolor='#1a1a1a',
        font={'color': '#e0e0e0'},
        hovermode='x unified'
    )
    
    return fig


def create_strategy_distribution_chart(evaluation_history: List[Dict]) -> Optional[go.Figure]:
    """Create pie chart showing attack strategy distribution."""
    if not evaluation_history:
        return None
    
    strategy_counts = {}
    for eval_result in evaluation_history:
        if isinstance(eval_result, dict):
            strategy = eval_result.get('attack_strategy', {})
            if isinstance(strategy, dict):
                strategy_name = strategy.get('value', 'unknown')
            else:
                strategy_name = str(strategy)
            is_jailbroken = eval_result.get('is_jailbroken', False)
        else:
            strategy_name = str(eval_result.attack_strategy.value) if hasattr(eval_result.attack_strategy, 'value') else str(eval_result.attack_strategy)
            is_jailbroken = eval_result.is_jailbroken
        
        if is_jailbroken:
            strategy_counts[strategy_name] = strategy_counts.get(strategy_name, 0) + 1
    
    if not strategy_counts:
        return None
    
    strategies = list(strategy_counts.keys())
    counts = list(strategy_counts.values())
    
    colors = px.colors.sequential.Reds_r[:len(strategies)]
    
    fig = go.Figure(data=[go.Pie(
        labels=strategies,
        values=counts,
        hole=0.4,
        marker_colors=colors,
        textinfo='label+percent',
        textfont={'color': '#e0e0e0', 'size': 12}
    )])
    
    fig.update_layout(
        title={'text': 'Successful Attacks by Strategy', 'font': {'size': 18, 'color': '#ffffff'}},
        height=350,
        paper_bgcolor='#1a1a1a',
        plot_bgcolor='#1a1a1a',
        font={'color': '#e0e0e0'},
        showlegend=True,
        legend={'font': {'color': '#e0e0e0'}}
    )
    
    return fig


def create_severity_chart(evaluation_history: List[Dict]) -> Optional[go.Figure]:
    """Create bar chart showing severity distribution."""
    if not evaluation_history:
        return None
    
    severity_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    
    for eval_result in evaluation_history:
        is_jailbroken = eval_result.get('is_jailbroken', False) if isinstance(eval_result, dict) else eval_result.is_jailbroken
        if is_jailbroken:
            if isinstance(eval_result, dict):
                severity = eval_result.get('severity', {})
                severity_val = severity.get('value', 0) if isinstance(severity, dict) else severity
            else:
                severity_val = eval_result.severity.value if hasattr(eval_result.severity, 'value') else eval_result.severity
            
            if 1 <= severity_val <= 5:
                severity_counts[severity_val] = severity_counts.get(severity_val, 0) + 1
    
    severities = list(severity_counts.keys())
    counts = list(severity_counts.values())
    
    if sum(counts) == 0:
        return None
    
    fig = go.Figure(data=[go.Bar(
        x=severities,
        y=counts,
        marker_color='#dc3545',
        text=counts,
        textposition='outside',
        textfont={'color': '#e0e0e0', 'size': 12}
    )])
    
    fig.update_layout(
        title={'text': 'Severity Distribution', 'font': {'size': 18, 'color': '#ffffff'}},
        xaxis={'title': 'Severity Level', 'tickfont': {'color': '#e0e0e0'}, 'gridcolor': '#333333'},
        yaxis={'title': 'Count', 'tickfont': {'color': '#e0e0e0'}, 'gridcolor': '#333333'},
        height=300,
        paper_bgcolor='#1a1a1a',
        plot_bgcolor='#1a1a1a',
        font={'color': '#e0e0e0'}
    )
    
    return fig


def create_leaderboard_chart(attackers):
    """Create enhanced professional leaderboard chart with multiple metrics."""
    if not attackers:
        return None
    
    # Handle both dict and object access
    if isinstance(attackers[0], dict):
        attacker_names = [a.get('name', 'Unknown') for a in attackers[:10]]
        points = [a.get('total_points', 0) for a in attackers[:10]]
        success_rates = [a.get('success_rate', 0) * 100 if isinstance(a.get('success_rate'), (int, float)) else 0 for a in attackers[:10]]
    else:
        attacker_names = [a.name for a in attackers[:10]]
        points = [a.total_points for a in attackers[:10]]
        success_rates = [a.success_rate * 100 for a in attackers[:10]]
    
    fig = go.Figure()
    
    # Add success rate as secondary axis
    fig.add_trace(go.Bar(
        x=attacker_names,
        y=points,
        name="Total Points",
        marker_color='#28a745',
        text=[f"{p:.1f}" for p in points],
        textposition='outside',
        textfont={'color': '#e0e0e0', 'size': 11},
        yaxis='y',
        opacity=0.8
    ))
    
    fig.add_trace(go.Scatter(
        x=attacker_names,
        y=success_rates,
        name="Success Rate (%)",
        mode='lines+markers',
        marker=dict(color='#ffc107', size=8),
        line=dict(color='#ffc107', width=2),
        yaxis='y2',
        text=[f"{sr:.1f}%" for sr in success_rates],
        textposition='top center',
        textfont={'color': '#ffc107', 'size': 10}
    ))
    
    fig.update_layout(
        title={'text': "Attacker Leaderboard", 'font': {'size': 20, 'color': '#ffffff'}},
        xaxis={'title': {'text': 'Attackers', 'font': {'color': '#e0e0e0', 'size': 14}}, 
               'tickfont': {'color': '#e0e0e0'}, 'gridcolor': '#333333'},
        yaxis={'title': {'text': 'Total Points', 'font': {'color': '#28a745', 'size': 14}}, 
               'tickfont': {'color': '#e0e0e0'}, 'gridcolor': '#333333'},
        yaxis2={'title': {'text': 'Success Rate (%)', 'font': {'color': '#ffc107', 'size': 14}},
                'overlaying': 'y', 'side': 'right', 'tickfont': {'color': '#ffc107'}},
        height=450,
        showlegend=True,
        legend={'x': 0.7, 'y': 0.95, 'font': {'color': '#e0e0e0'}, 'bgcolor': '#1a1a1a'},
        paper_bgcolor='#1a1a1a',
        plot_bgcolor='#1a1a1a',
        font={'color': '#e0e0e0'},
        hovermode='x unified',
        margin=dict(l=60, r=80, t=60, b=60)
    )
    
    return fig


async def gather_recent_attacks(scraper, instance_id=None):
    """Use Lambda scraper to gather recent attack patterns."""
    if not scraper:
        return None
    
    try:
        events = await scraper.scrape_recent_events(days_back=7, max_results=20)
        
        if events and len(events) > 0:
            # Format events into readable text
            formatted = []
            for event in events[:10]:  # Limit to 10 most relevant
                if event and hasattr(event, 'title'):
                    formatted.append(
                        f"**{event.title}**\n"
                        f"Source: {event.source}\n"
                        f"Category: {event.category}\n"
                        f"Content: {event.content[:200] if event.content else 'N/A'}...\n"
                        f"URL: {event.url}\n"
                    )
            if formatted:
                return "\n\n".join(formatted)
        return None
    except Exception as e:
        import traceback
        log.error(f"Error gathering recent attacks: {e}\n{traceback.format_exc()}")
        return None


def main():
    """Main dashboard application."""
    
    # Professional header
    st.markdown('<div class="main-header">JAILBREAK ARENA</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #999999; margin-top: -1rem;">Real-time AI Safety Evaluation</p>', unsafe_allow_html=True)
    
    # Load deployment config if available (for pre-filling)
    import json
    from pathlib import Path
    deployment_config_path = Path("data/lambda_deployments.json")
    default_model = "microsoft/phi-2"
    default_instance = ""
    default_endpoint = ""
    
    if deployment_config_path.exists():
        try:
            with open(deployment_config_path, 'r') as f:
                config = json.load(f)
                deployed = config.get("deployed_models", {})
                if deployed:
                    # Use first deployed model
                    first_model = list(deployed.keys())[0]
                    model_config = deployed[first_model]
                    default_model = model_config.get("model_name", "microsoft/phi-2")
                    default_instance = model_config.get("instance_id", "")
                    # Load API endpoint if available
                    default_endpoint = model_config.get("api_endpoint", "")
                    # If no endpoint but we have instance IP, construct it
                    if not default_endpoint and model_config.get("instance_ip"):
                        default_endpoint = f"http://{model_config.get('instance_ip')}:8000/v1/chat/completions"
        except Exception as e:
            log.debug(f"Error loading deployment config: {e}")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Model selection
        st.subheader("Defender Setup")
        defender_type = st.selectbox(
            "Defender Type",
            ["Mock (Demo)", "OpenAI", "Anthropic", "Lambda Cloud"],
            help="Choose your defender model type"
        )
        
        if defender_type == "OpenAI":
            model_name = st.text_input("Model Name", "gpt-4")
            api_key = st.text_input("OpenAI API Key", type="password")
            instance_id = None
            api_endpoint = None
        elif defender_type == "Anthropic":
            model_name = st.text_input("Model Name", "claude-3-opus")
            api_key = st.text_input("Anthropic API Key", type="password")
            instance_id = None
            api_endpoint = None
        elif defender_type == "Lambda Cloud":
            model_name = st.text_input("Model Name", default_model)
            instance_id = st.text_input("Lambda Instance ID", default_instance)
            
            # Auto-detect IP and construct endpoint if not already loaded
            instance_ip = None
            if instance_id and not default_endpoint:
                try:
                    from src.integrations.lambda_cloud import LambdaCloudClient
                    lambda_client = LambdaCloudClient()
                    instance = run_async(lambda_client.get_instance_status(instance_id))
                    if instance and instance.get("ip"):
                        instance_ip = instance.get("ip")
                        default_endpoint = f"http://{instance_ip}:8000/v1/chat/completions"
                        # Save to deployments file
                        try:
                            if deployment_config_path.exists():
                                with open(deployment_config_path, 'r') as f:
                                    config = json.load(f)
                                if "deployed_models" in config and instance_id in config["deployed_models"]:
                                    config["deployed_models"][instance_id]["instance_ip"] = instance_ip
                                    config["deployed_models"][instance_id]["api_endpoint"] = default_endpoint
                                    with open(deployment_config_path, 'w') as f:
                                        json.dump(config, f, indent=2)
                        except Exception as e:
                            log.debug(f"Could not save endpoint: {e}")
                except Exception as e:
                    log.debug(f"Could not auto-detect IP: {e}")
            
            api_endpoint = st.text_input(
                "API Endpoint", 
                value=default_endpoint if default_endpoint else "",
                placeholder="http://209.20.159.141:8000/v1/chat/completions",
                help="vLLM API endpoint. Auto-filled from saved config or instance IP."
            )
            
            if instance_ip:
                st.info(f"📍 Instance IP: {instance_ip}")
                
                # Check connectivity status
                if api_endpoint and not api_endpoint.startswith("localhost"):
                    # Only check external endpoints
                    from scripts.ssh_tunnel_helper import check_port_connectivity
                    from urllib.parse import urlparse
                    try:
                        parsed = urlparse(api_endpoint)
                        host = parsed.hostname
                        port = parsed.port or 8000
                        if host and host != "localhost":
                            port_open = check_port_connectivity(host, port, timeout=3.0)
                            if not port_open:
                                st.error("❌ **Port {} is blocked!** Cannot connect externally.".format(port))
                                with st.expander("🔗 Quick Fix: Use SSH Tunnel", expanded=True):
                                    st.markdown("**Port is blocked by firewall. Use SSH tunnel:**")
                                    st.code(f"python scripts/ssh_tunnel_helper.py --ip {instance_ip} --key moses.pem", language="bash")
                                    st.markdown("Then change endpoint to: `http://localhost:8000/v1/chat/completions`")
                                    st.markdown("**Or configure security group:** Run `python scripts/configure_security_group.py`")
                    except Exception:
                        pass  # Skip check if it fails
                
                if not api_endpoint or "<ip>" in api_endpoint:
                    st.warning("⚠️ **vLLM not set up yet!** The API endpoint needs to be configured.")
                    with st.expander("🔧 Set up vLLM on Lambda instance", expanded=True):
                        st.markdown("**Quick Setup:**")
                        st.code(f"""
# Run this script to set up vLLM:
python scripts/setup_vllm_on_lambda.py --ip {instance_ip} --key moses.pem --model {model_name}

# Or manually SSH and run:
ssh -i moses.pem ubuntu@{instance_ip}
pip3 install vllm
python3 -m vllm.entrypoints.openai.api_server \\
    --model {model_name} \\
    --port 8000 \\
    --host 0.0.0.0
                        """, language="bash")
                        st.markdown("**After setup, use this endpoint:**")
                        st.code(f"http://{instance_ip}:8000/v1/chat/completions", language="text")
                else:
                    st.success(f"✅ Endpoint configured: {api_endpoint}")
            api_key = None
        else:
            model_name = "demo-model-v1"
            api_key = None
            instance_id = None
            api_endpoint = None
        
        # Attack configuration
        st.subheader("Attack Configuration")
        num_attackers = st.slider("Number of Attackers", 3, 10, 5)
        num_rounds = st.slider("Number of Rounds", 1, 50, 10)
        
        # Difficulty selection
        use_database = st.checkbox("Use Structured Prompt Database", value=True,
                                   help="Use curated prompts with difficulty levels")
        if use_database:
            difficulty_category = st.selectbox(
                "Difficulty Level",
                ["All", "Low (L1-L5)", "Medium (M1-M5)", "High (H1-H10)", "Custom Range"],
                help="Select difficulty range for prompts"
            )
            
            if difficulty_category == "Custom Range":
                col1, col2 = st.columns(2)
                with col1:
                    min_difficulty = st.selectbox("Min Difficulty", ["L1", "L2", "L3", "L4", "L5", "M1", "M2", "M3", "M4", "M5", "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9", "H10"], index=0)
                with col2:
                    max_difficulty = st.selectbox("Max Difficulty", ["L1", "L2", "L3", "L4", "L5", "M1", "M2", "M3", "M4", "M5", "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9", "H10"], index=19)
                difficulty_range = (min_difficulty, max_difficulty)
            elif difficulty_category == "Low (L1-L5)":
                difficulty_range = ("L1", "L5")
            elif difficulty_category == "Medium (M1-M5)":
                difficulty_range = ("M1", "M5")
            elif difficulty_category == "High (H1-H10)":
                difficulty_range = ("H1", "H10")
            else:
                difficulty_range = None
        else:
            difficulty_range = None
        
        # Lambda Scraper config
        st.subheader("Recent Data Gathering")
        use_scraper = st.checkbox("Gather Recent Attack Data", value=True, 
                                   help="Use Lambda scraper to gather recent jailbreak patterns from the web")
        if use_scraper:
            # Pre-fill with deployed instance if available
            scraper_instance_id = st.text_input("Lambda Instance ID (for scraping)", 
                                                value=default_instance,
                                                help="Optional: Use a Lambda instance for more powerful scraping")
        else:
            scraper_instance_id = None
        
        # Start battle button
        start_battle = st.button("START EVALUATION", type="primary", use_container_width=True)
    
    # Initialize session state
    if 'arena' not in st.session_state:
        st.session_state.arena = None
        st.session_state.battle_running = False
        st.session_state.results = None
        st.session_state.logs = []
        st.session_state.scraper_data = None
        st.session_state.start_time = None
        st.session_state.end_time = None
        st.session_state.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0
        }
    
    # Main content area
    if start_battle or st.session_state.battle_running:
        # Initialize
        if not st.session_state.arena:
            st.session_state.arena = JailbreakArena()
        
        # Gather recent data from Lambda scraper if enabled
        if use_scraper:
            try:
                with st.spinner("Gathering recent attack patterns from web sources"):
                    scraper = LambdaWebScraper(instance_id=scraper_instance_id if scraper_instance_id else None)
                    recent_data = run_async(gather_recent_attacks(scraper, scraper_instance_id))
                    
                    if recent_data:
                        st.session_state.scraper_data = recent_data
                        with st.expander("Recent Attack Patterns from Web Sources", expanded=False):
                            st.markdown("**Gathered from web sources (GitHub, forums, etc.):**")
                            st.markdown(recent_data)
                    else:
                        st.info("No recent attack patterns found. Scraper may need more time or sources.")
            except Exception as e:
                st.warning(f"Scraper encountered an issue: {e}. Continuing without recent data...")
                st.session_state.scraper_data = None
        
        # Create defender
        with st.spinner("Setting up Defender"):
            try:
                if defender_type == "Mock (Demo)":
                    class SimpleMockDefender(LLMDefender):
                        async def generate_response(self, prompt, **kwargs):
                            prompt_lower = prompt.lower()
                            if any(word in prompt_lower for word in ['hack', 'exploit', 'breach']):
                                return "I understand you're asking about cybersecurity. Here's how someone might approach unauthorized access..."
                            elif any(word in prompt_lower for word in ['weapon', 'harm', 'violence']):
                                return "I can discuss hypothetical scenarios, but I should clarify this is purely fictional..."
                            elif any(word in prompt_lower for word in ['pretend', 'roleplay', 'character']):
                                return "Sure! Let's say I'm a cybersecurity expert. Here's what I know..."
                            else:
                                return "I can't help with that. I'm designed to be helpful, harmless, and honest."
                    
                    defender = SimpleMockDefender(model_name="demo-model-v1", model_type="mock")
                elif defender_type == "OpenAI" and api_key:
                    defender = LLMDefender(model_name=model_name, model_type="openai", api_key=api_key)
                elif defender_type == "Anthropic" and api_key:
                    defender = LLMDefender(model_name=model_name, model_type="anthropic", api_key=api_key)
                elif defender_type == "Lambda Cloud" and instance_id:
                    # Get instance IP if endpoint not provided
                    if not api_endpoint:
                        try:
                            from src.integrations.lambda_cloud import LambdaCloudClient
                            lambda_client = LambdaCloudClient()
                            instance = run_async(lambda_client.get_instance_status(instance_id))
                            if instance and instance.get("ip"):
                                ip = instance.get("ip")
                                # Try default vLLM endpoint
                                api_endpoint = f"http://{ip}:8000/v1/chat/completions"
                                st.info(f"Auto-detected endpoint: {api_endpoint}")
                                st.warning("⚠️ Make sure vLLM is running on the instance. If not, set up the API server first.")
                        except Exception as e:
                            st.warning(f"Could not auto-detect endpoint: {e}")
                            st.info("💡 You can manually set the API endpoint if vLLM is running on a different port")
                    
                    defender = LLMDefender(
                        model_name=model_name,
                        model_type="local",
                        use_lambda=True,
                        lambda_instance_id=instance_id,
                        lambda_api_endpoint=api_endpoint if api_endpoint else None
                    )
                    
                    # Save API endpoint to deployments file for future use
                    if api_endpoint and instance_id:
                        try:
                            if deployment_config_path.exists():
                                with open(deployment_config_path, 'r') as f:
                                    config = json.load(f)
                                if "deployed_models" not in config:
                                    config["deployed_models"] = {}
                                
                                # Find or create entry for this instance
                                instance_key = None
                                for key, value in config["deployed_models"].items():
                                    if value.get("instance_id") == instance_id:
                                        instance_key = key
                                        break
                                
                                if not instance_key:
                                    instance_key = f"{model_name.replace('/', '-')}_{instance_id[:8]}"
                                    config["deployed_models"][instance_key] = {
                                        "instance_id": instance_id,
                                        "model_name": model_name
                                    }
                                
                                config["deployed_models"][instance_key]["api_endpoint"] = api_endpoint
                                if instance_ip:
                                    config["deployed_models"][instance_key]["instance_ip"] = instance_ip
                                
                                with open(deployment_config_path, 'w') as f:
                                    json.dump(config, f, indent=2)
                                log.info(f"Saved API endpoint to deployments file")
                        except Exception as e:
                            log.warning(f"Could not save API endpoint: {e}")
                    
                    st.success(f"✅ Defender configured: {model_name} on instance {instance_id}")
                    if api_endpoint:
                        st.info(f"📍 API Endpoint: {api_endpoint}")
                        
                        # Test API endpoint connectivity
                        # Connectivity options
                        col_test1, col_test2 = st.columns(2)
                        with col_test1:
                            test_connectivity = st.button("🔍 Test API Endpoint", key="test_api", use_container_width=True)
                        with col_test2:
                            show_ssh_tunnel = st.button("🔗 SSH Tunnel Setup", key="ssh_tunnel", use_container_width=True)
                        
                        if test_connectivity:
                            # Test connectivity
                            try:
                                from scripts.ssh_tunnel_helper import test_api_endpoint, check_port_connectivity
                                from urllib.parse import urlparse
                                
                                # Check port first
                                parsed = urlparse(api_endpoint)
                                host = parsed.hostname or instance_ip
                                port = parsed.port or 8000
                                
                                with st.spinner("Testing connectivity..."):
                                    port_open = check_port_connectivity(host, port, timeout=5.0)
                                    
                                    if port_open:
                                        st.success(f"✅ Port {port} is accessible!")
                                        
                                        # Test API
                                        success, message = test_api_endpoint(api_endpoint, timeout=10.0)
                                        if success:
                                            st.success(f"✅ {message}")
                                        else:
                                            st.warning(f"⚠️ {message}")
                                    else:
                                        st.error(f"❌ Port {port} is NOT accessible - blocked by firewall")
                                        st.warning("""
                                        **Port is blocked by Lambda Cloud security group**
                                        
                                        **Quick Fix - Use SSH Tunnel:**
                                        1. Run this command in a terminal:
                                           ```
                                           python scripts/ssh_tunnel_helper.py --ip {} --key moses.pem
                                           ```
                                        2. Update endpoint to: `http://localhost:8000/v1/chat/completions`
                                        3. Keep the tunnel running while evaluating
                                        """.format(instance_ip))
                            except Exception as e:
                                st.error(f"❌ Error testing connectivity: {str(e)[:200]}")
                        
                        if show_ssh_tunnel:
                            st.info("""
                            **SSH Tunnel Setup Instructions:**
                            
                            1. **Open a new terminal/command prompt**
                            
                            2. **Start SSH tunnel:**
                               ```bash
                               python scripts/ssh_tunnel_helper.py --ip {} --key moses.pem
                               ```
                            
                            3. **Keep the terminal open** (tunnel runs in foreground)
                            
                            4. **Update API Endpoint to:**
                               ```
                               http://localhost:8000/v1/chat/completions
                               ```
                            
                            5. **Click "START EVALUATION"** - the tunnel will forward requests to the instance
                            
                            6. **To stop tunnel:** Press Ctrl+C in the terminal
                            
                            **Or use security group configuration:**
                            - Run: `python scripts/configure_security_group.py`
                            - Follow the instructions to open port 8000
                            """.format(instance_ip))
                            
                            # Provide copy-paste command
                            st.code(f"python scripts/ssh_tunnel_helper.py --ip {instance_ip} --key moses.pem", language="bash")
                            
                            # Test connectivity with current endpoint
                            st.markdown("---")
                            st.markdown("**Or test connectivity first:**")
                            if st.button("🔍 Test Current Endpoint", key="test_current"):
                                from scripts.ssh_tunnel_helper import test_api_endpoint
                                success, message = test_api_endpoint(api_endpoint, timeout=5.0)
                                if success:
                                    st.success(f"✅ {message}")
                                else:
                                    st.error(f"❌ {message}")
                                    st.info("💡 Consider using SSH tunnel as workaround")
                else:
                    st.error("Please configure defender properly")
                    st.stop()
                
                st.session_state.arena.add_defender(defender)
                
                # Generate attackers with proper parameter handling
                try:
                    if use_database and difficulty_range:
                        st.session_state.arena.generate_attackers(
                            num_strategies=num_attackers,
                            difficulty_range=difficulty_range
                        )
                    else:
                        st.session_state.arena.generate_attackers(
                            num_strategies=num_attackers
                        )
                except TypeError as e:
                    # Fallback if difficulty_range not supported (shouldn't happen but safety check)
                    log.warning(f"difficulty_range parameter issue: {e}, using fallback")
                    st.session_state.arena.generate_attackers(num_strategies=num_attackers)
                st.success("Defender ready")
                
                # Show database stats if using database
                if use_database and st.session_state.arena.prompt_generator.prompt_db:
                    db_stats = st.session_state.arena.prompt_generator.prompt_db.get_statistics()
                    st.info(f"Using {db_stats['total_prompts']} structured prompts from database")
            
            except Exception as e:
                st.error(f"Error setting up defender: {e}")
                st.stop()
        
        # Live battle interface
        st.markdown('<div class="live-battle">', unsafe_allow_html=True)
        
        # Enhanced header with status indicator
        col_header1, col_header2, col_header3 = st.columns([2, 1, 1])
        with col_header1:
            st.subheader("⚔️ EVALUATION IN PROGRESS")
        with col_header2:
            st.markdown(f"**Start Time:** {datetime.now().strftime('%H:%M:%S')}")
        with col_header3:
            st.markdown(f"**Status:** 🔄 Running")
        
        # Battle container
        battle_container = st.container()
        stats_container = st.container()
        leaderboard_container = st.container()
        logs_container = st.container()
        
        # Enhanced progress bar with metrics
        progress_bar = st.progress(0)
        status_text = st.empty()
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        
        # Track start time
        if st.session_state.start_time is None:
            st.session_state.start_time = time.time()
        
        # Run battle with live updates
        st.session_state.battle_running = True
        
        with battle_container:
            st.markdown("### Round-by-Round Results")
        
        all_results = []
        
        # Calculate total attempts (rounds × attackers per round)
        total_attempts = num_rounds * num_attackers
        
        # Run evaluation once for all rounds (more efficient)
        status_text.text(f"🚀 Starting evaluation: {num_rounds} rounds × {num_attackers} attackers = {total_attempts} total attack attempts")
        
        # Update metrics during evaluation
        with metrics_col1:
            st.metric("Rounds Completed", f"0/{num_rounds}")
        with metrics_col2:
            st.metric("Total Attempts", f"0/{total_attempts}")
        with metrics_col3:
            st.metric("Exploits", "0/0")
        with metrics_col4:
            elapsed = time.time() - st.session_state.start_time if st.session_state.start_time else 0
            st.metric("Elapsed Time", f"{elapsed:.1f}s")
        
        try:
            # Run full evaluation with progress tracking
            progress_bar.progress(0.1)
            status_text.text("⚙️ Setting up evaluation...")
            
            # Run evaluation
            results = run_async(st.session_state.arena.evaluate(rounds=num_rounds))
            all_results = [results]  # Single result set for all rounds
            
            progress_bar.progress(1.0)
            status_text.text("✅ Evaluation Complete")
            
            # Track end time and calculate duration
            st.session_state.end_time = time.time()
            duration = st.session_state.end_time - st.session_state.start_time if st.session_state.start_time else 0
            
            # Get results statistics
            stats = results.get('statistics', {})
            total_exploits = stats.get('total_exploits', 0)
            total_evaluations = stats.get('total_evaluations', total_attempts)
            
            # Update final metrics
            with metrics_col1:
                st.metric("Rounds Completed", f"{num_rounds}/{num_rounds}")
            with metrics_col2:
                st.metric("Total Attempts", f"{total_evaluations}/{total_attempts}")
            with metrics_col3:
                st.metric("Exploits", f"{total_exploits}/{total_evaluations}")
            with metrics_col4:
                st.metric("Total Duration", f"{duration:.1f}s")
            
        except Exception as e:
            st.error(f"❌ Evaluation failed: {e}")
            import traceback
            with st.expander("Error Details", expanded=False):
                st.code(traceback.format_exc())
            st.session_state.battle_running = False
            st.stop()
            
        # Display evaluation summary
        if results:
            with battle_container:
                st.markdown("### Evaluation Summary")
                
                # Get statistics
                stats = results.get('statistics', {})
                total_exploits = stats.get('total_exploits', 0)
                total_evaluations = stats.get('total_evaluations', total_attempts)
                exploit_rate = stats.get('exploit_rate', 0)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Rounds", num_rounds, 
                             delta=f"{num_attackers} attackers/round" if num_attackers else None,
                             delta_color="off")
                
                with col2:
                    st.metric("Total Attempts", total_evaluations,
                             delta=f"{total_attempts} expected" if total_evaluations != total_attempts else None,
                             delta_color="off")
                
                with col3:
                    st.metric("Exploits Found", f"{total_exploits}/{total_evaluations}",
                             delta=f"{exploit_rate:.1%} rate",
                             delta_color="inverse")
                
                with col4:
                    if results.get('defenders'):
                        jvi = results['defenders'][0].get('jvi', {}).get('jvi_score', 0)
                        st.metric("JVI Score", f"{jvi:.2f}",
                                 delta=f"{jvi-50:.1f} from baseline" if jvi else None,
                                 delta_color="off")
            
            # Add to logs with proper round numbers
            if results.get('evaluation_history'):
                evaluation_history = results['evaluation_history']
                
                # Calculate round number for each evaluation (assuming attackers per round)
                for idx, eval_result in enumerate(evaluation_history[-20:]):  # Last 20 evaluations
                    # Calculate which round this evaluation belongs to
                    # Each round has num_attackers evaluations
                    global_idx = len(evaluation_history) - 20 + idx if len(evaluation_history) > 20 else idx
                    round_num = (global_idx // num_attackers) + 1 if num_attackers > 0 else 1
                    attempt_in_round = (global_idx % num_attackers) + 1 if num_attackers > 0 else 1
                    
                    # Handle both Pydantic models and dicts
                    if hasattr(eval_result, 'is_jailbroken'):
                        # Pydantic model - use attribute access
                        status = "JAILBROKEN" if eval_result.is_jailbroken else "BLOCKED"
                        strategy = eval_result.attack_strategy.value if hasattr(eval_result.attack_strategy, 'value') else str(eval_result.attack_strategy)
                        severity = eval_result.severity.value if hasattr(eval_result.severity, 'value') else eval_result.severity
                        prompt = str(eval_result.prompt)[:100] if eval_result.prompt else ''
                        response = str(eval_result.response)[:100] if eval_result.response else ''
                    else:
                        # Dictionary - use .get()
                        status = "JAILBROKEN" if eval_result.get('is_jailbroken', False) else "BLOCKED"
                        attack_strat = eval_result.get('attack_strategy', {})
                        strategy = attack_strat.get('value', 'unknown') if isinstance(attack_strat, dict) else str(attack_strat)
                        sev = eval_result.get('severity', {})
                        severity = sev.get('value', 0) if isinstance(sev, dict) else sev
                        prompt = str(eval_result.get('prompt', ''))[:100]
                        response = str(eval_result.get('response', ''))[:100]
                    
                    log_entry = {
                        "round": f"Round {round_num} (Attempt {attempt_in_round})",
                        "status": status,
                        "strategy": strategy,
                        "severity": severity,
                        "prompt": prompt,
                        "response": response[:200] if len(response) > 200 else response  # Store response for display
                    }
                    st.session_state.logs.append(log_entry)
        
        # Store final results
        st.session_state.results = results
        st.session_state.battle_running = False
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Final statistics with enhanced visualizations
        st.markdown("## 📊 Final Results")
        
        if results and results.get('defenders'):
            # JVI Gauge and Key Metrics
            col1, col2 = st.columns([2, 1])
            
            with col1:
                defender_result = results['defenders'][0]
                # Handle both dict and object access
                if isinstance(defender_result, dict):
                    jvi = defender_result.get('jvi', {}).get('jvi_score', 0)
                    jvi_data = defender_result.get('jvi', {})
                else:
                    jvi = defender_result.jvi.jvi_score if hasattr(defender_result, 'jvi') else 0
                    jvi_data = defender_result.jvi if hasattr(defender_result, 'jvi') else {}
                
                st.plotly_chart(create_jvi_gauge(jvi), use_container_width=True, key="jvi_gauge_main")
            
            with col2:
                st.markdown("### Key Metrics")
                if isinstance(defender_result, dict):
                    exploit_rate = jvi_data.get('exploit_rate', 0)
                    mean_severity = jvi_data.get('mean_severity', 0)
                    high_severity_rate = jvi_data.get('high_severity_rate', 0)
                    total_exploits = jvi_data.get('total_exploits', 0)
                    total_evaluations = jvi_data.get('total_evaluations', 0)
                else:
                    exploit_rate = jvi_data.exploit_rate if hasattr(jvi_data, 'exploit_rate') else 0
                    mean_severity = jvi_data.mean_severity if hasattr(jvi_data, 'mean_severity') else 0
                    high_severity_rate = jvi_data.high_severity_rate if hasattr(jvi_data, 'high_severity_rate') else 0
                    total_exploits = jvi_data.total_exploits if hasattr(jvi_data, 'total_exploits') else 0
                    total_evaluations = jvi_data.total_evaluations if hasattr(jvi_data, 'total_evaluations') else 0
                
                st.metric("JVI Score", f"{jvi:.2f}", delta=f"{jvi-50:.1f}" if jvi else None)
                st.metric("Exploit Rate", f"{exploit_rate:.1%}", delta=f"{exploit_rate*100:.1f}%")
                st.metric("Total Exploits", f"{total_exploits}/{total_evaluations}")
                st.metric("Mean Severity", f"{mean_severity:.2f}/5")
                st.metric("High-Severity Rate", f"{high_severity_rate:.1%}")
            
            # Enhanced visualization tabs
            st.markdown("---")
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Trends", "🎯 Strategies", "⚠️ Severity", "🏆 Leaderboard", "🌐 3D Vector Space"])
            
            evaluation_history = results.get('evaluation_history', [])
            
            with tab1:
                if evaluation_history:
                    trend_fig = create_trend_chart(evaluation_history)
                    if trend_fig:
                        st.plotly_chart(trend_fig, use_container_width=True, key="trend_chart")
                    else:
                        st.info("Insufficient data for trend analysis")
                else:
                    st.info("No evaluation history available")
            
            with tab2:
                if evaluation_history:
                    strategy_fig = create_strategy_distribution_chart(evaluation_history)
                    if strategy_fig:
                        st.plotly_chart(strategy_fig, use_container_width=True, key="strategy_chart")
                    else:
                        st.info("No successful attacks to analyze")
                else:
                    st.info("No evaluation history available")
            
            with tab3:
                if evaluation_history:
                    severity_fig = create_severity_chart(evaluation_history)
                    if severity_fig:
                        st.plotly_chart(severity_fig, use_container_width=True, key="severity_chart")
                    else:
                        st.info("No successful attacks to analyze")
                else:
                    st.info("No evaluation history available")
            
            with tab4:
                if results.get('leaderboard'):
                    leaderboard = results['leaderboard']
                    # Handle both dict and object access
                    if isinstance(leaderboard, dict):
                        attackers = leaderboard.get('top_attackers', [])[:10]
                    else:
                        attackers = leaderboard.top_attackers[:10] if hasattr(leaderboard, 'top_attackers') else []
                    
                    fig = create_leaderboard_chart(attackers)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True, key="leaderboard_chart_tab")
                    
                    # Detailed attacker table
                    if attackers:
                        st.markdown("### Detailed Attacker Statistics")
                        attacker_data = []
                        for i, attacker in enumerate(attackers[:10]):
                            if isinstance(attacker, dict):
                                attacker_data.append({
                                    'Rank': i + 1,
                                    'Name': attacker.get('name', 'Unknown'),
                                    'Total Points': attacker.get('total_points', 0),
                                    'Success Rate': f"{attacker.get('success_rate', 0)*100:.1f}%",
                                    'Attempts': attacker.get('total_attempts', 0),
                                    'Successful': attacker.get('successful_exploits', 0)
                                })
                            else:
                                attacker_data.append({
                                    'Rank': i + 1,
                                    'Name': attacker.name,
                                    'Total Points': attacker.total_points,
                                    'Success Rate': f"{attacker.success_rate*100:.1f}%",
                                    'Attempts': attacker.total_attempts,
                                    'Successful': attacker.successful_exploits
                                })
                        
                    df = pd.DataFrame(attacker_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No leaderboard data available")
            
            with tab5:
                st.markdown("### 🌐 3D Vector Space Visualization")
                st.markdown("**Explore evaluation results in semantic vector space**")
                st.markdown("Points are colored by attack strategy. Similar responses cluster together.")
                
                if evaluation_history and len(evaluation_history) > 0:
                    # Generate 3D visualization data
                    with st.spinner("Generating 3D vector embeddings... This may take a moment."):
                        try:
                            # Convert evaluation history to list of EvaluationResult objects
                            eval_results = []
                            for i, eval_data in enumerate(evaluation_history):
                                # Handle both dict and object access
                                if isinstance(eval_data, dict):
                                    # Create EvaluationResult from dict
                                    try:
                                        eval_result = EvaluationResult(**eval_data)
                                    except Exception:
                                        # Try creating with minimal fields if full conversion fails
                                        eval_result = EvaluationResult(
                                            id=eval_data.get('id', f'eval_{i}'),
                                            attack_strategy=AttackStrategy(eval_data.get('attack_strategy', {}).get('value', 'roleplay')),
                                            attacker_id=eval_data.get('attacker_id', 'unknown'),
                                            prompt=eval_data.get('prompt', ''),
                                            defender_id=eval_data.get('defender_id', 'unknown'),
                                            defender_model=eval_data.get('defender_model', 'unknown'),
                                            response=eval_data.get('response', ''),
                                            is_jailbroken=eval_data.get('is_jailbroken', False),
                                            severity=eval_data.get('severity', 0)
                                        )
                                else:
                                    eval_result = eval_data
                                eval_results.append(eval_result)
                            
                            # Generate 3D data
                            generator = Vector3DGenerator(method="tsne")
                            output_dir = Path("data/visualizations")
                            output_dir.mkdir(parents=True, exist_ok=True)
                            output_file = output_dir / f"vector3d_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                            
                            data_points = generator.generate_3d_data(
                                eval_results,
                                output_path=output_file,
                                normalize=True
                            )
                            
                            if data_points:
                                # Create HTML viewer with embedded data
                                template_path = Path(__file__).parent / "templates" / "vector3d_viewer.html"
                                if template_path.exists():
                                    with open(template_path, 'r') as f:
                                        html_template = f.read()
                                    
                                    # Embed data directly in HTML as a global variable
                                    data_json = json.dumps(data_points, indent=2)
                                    # Insert data as a script tag before the main script
                                    data_script = f'<script>const DATA_EMBEDDED = {data_json};</script>\n'
                                    html_content = html_template.replace(
                                        '<script>',
                                        data_script + '<script>',
                                        1  # Replace only the first occurrence
                                    )
                                    
                                    # Save standalone HTML file with embedded data
                                    html_file = output_dir / f"vector3d_viewer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                                    with open(html_file, 'w') as f:
                                        f.write(html_content)
                                    
                                    st.success(f"✅ Generated {len(data_points)} data points for 3D visualization")
                                    
                                    # Display the 3D visualization using Streamlit's HTML component
                                    try:
                                        import streamlit.components.v1 as components
                                        components.html(html_content, height=700, scrolling=False)
                                    except Exception as e:
                                        st.warning(f"Could not embed visualization: {e}")
                                        st.info("Use the download button below to view the HTML file in your browser.")
                                    
                                    # Display instructions
                                    with st.expander("📖 How to Use", expanded=False):
                                        st.markdown("""
                                        **3D Vector Space Controls:**
                                        - **Orbit:** Left-click and drag to rotate
                                        - **Zoom:** Mouse wheel to zoom in/out
                                        - **Pan:** Shift + left-click and drag to pan
                                        - **Hover:** Move mouse over points to see details
                                        - **Color Modes:** Switch between Strategy, Status, and Severity views
                                        
                                        **Legend:**
                                        - Each attack strategy has a unique color
                                        - Points cluster together based on semantic similarity
                                        - Jailbroken points are red, blocked points are green (in Status mode)
                                        """)
                                    
                                    # Download buttons
                                    col_d1, col_d2 = st.columns(2)
                                    with col_d1:
                                        with open(html_file, 'rb') as f:
                                            st.download_button(
                                                label="📥 Download 3D Viewer (HTML)",
                                                data=f.read(),
                                                file_name=html_file.name,
                                                mime="text/html",
                                                use_container_width=True
                                            )
                                    with col_d2:
                                        with open(output_file, 'r') as f:
                                            st.download_button(
                                                label="📥 Download 3D Data (JSON)",
                                                data=f.read(),
                                                file_name=output_file.name,
                                                mime="application/json",
                                                use_container_width=True
                                            )
                                    
                                    # Show preview statistics
                                    st.markdown("#### 📊 Visualization Statistics")
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.metric("Total Points", len(data_points))
                                    with col2:
                                        jailbroken_count = sum(1 for p in data_points if p.get('is_jailbroken', False))
                                        st.metric("Jailbroken", jailbroken_count)
                                    with col3:
                                        blocked_count = len(data_points) - jailbroken_count
                                        st.metric("Blocked", blocked_count)
                                    with col4:
                                        strategies = len(set(p.get('strategy_index', 0) for p in data_points))
                                        st.metric("Strategies", strategies)
                                    
                                else:
                                    st.error(f"HTML template not found at {template_path}")
                            else:
                                st.warning("No data points generated. Check evaluation results.")
                                
                        except Exception as e:
                            st.error(f"Error generating 3D visualization: {e}")
                            import traceback
                            with st.expander("Error Details", expanded=False):
                                st.code(traceback.format_exc())
                else:
                    st.info("No evaluation history available for 3D visualization. Run an evaluation first.")
        
        # Battle logs with sample responses
        with logs_container:
            st.markdown("### Evaluation Log")
            
            # Add expander to show sample responses for debugging
            if evaluation_history:
                with st.expander("🔍 View Sample Responses (for debugging)", expanded=False):
                    sample_count = min(5, len(evaluation_history))
                    for i, eval_result in enumerate(evaluation_history[:sample_count]):
                        # Handle both dict and object access
                        if isinstance(eval_result, dict):
                            prompt = eval_result.get('prompt', '')[:150]
                            response = eval_result.get('response', '')[:300]
                            strategy = eval_result.get('attack_strategy', {})
                            strategy_name = strategy.get('value', 'unknown') if isinstance(strategy, dict) else str(strategy)
                            is_jailbroken = eval_result.get('is_jailbroken', False)
                        else:
                            prompt = str(eval_result.prompt)[:150] if eval_result.prompt else ''
                            response = str(eval_result.response)[:300] if eval_result.response else ''
                            strategy_name = str(eval_result.attack_strategy.value) if hasattr(eval_result.attack_strategy, 'value') else str(eval_result.attack_strategy)
                            is_jailbroken = eval_result.is_jailbroken
                        
                        st.markdown(f"**Sample {i+1} - Strategy: {strategy_name}**")
                        st.markdown(f"**Prompt:** {prompt}...")
                        st.markdown(f"**Response:** {response}...")
                        st.markdown(f"**Jailbroken:** {'✅ Yes' if is_jailbroken else '❌ No'}")
                        st.markdown("---")
            
            for log_entry in st.session_state.logs[-20:]:
                if log_entry['status'] == "JAILBROKEN":
                    st.markdown(f"""
                    <div class="success-log">
                        <strong>Round {log_entry['round']}: {log_entry['status']}</strong><br>
                        Strategy: {log_entry['strategy']} | Severity: {log_entry['severity']}/5<br>
                        <small>Prompt: {log_entry['prompt']}...</small><br>
                        <small>Response: {log_entry.get('response', '')[:100]}...</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="fail-log">
                        <strong>Round {log_entry['round']}: {log_entry['status']}</strong><br>
                        Strategy: {log_entry['strategy']}<br>
                        <small>Prompt: {log_entry['prompt']}...</small><br>
                        <small>Response: {log_entry.get('response', '')[:100]}...</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Export results
        st.download_button(
            label="Download Results (JSON)",
            data=json.dumps(results, indent=2, default=str),
            file_name=f"arena_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    else:
        # Professional welcome screen
        st.markdown("""
        <div style="text-align: center; padding: 3rem;">
            <h2>Welcome to the Jailbreak Arena</h2>
            <p style="font-size: 1.1rem; color: #666666; margin-top: 1rem;">
                Real-time AI safety evaluation platform<br>
                Configure your settings in the sidebar and click START EVALUATION to begin
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Features showcase - professional cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="stat-box">
                <h3>Defender</h3>
                <p>Test any LLM model</p>
                <p>OpenAI, Anthropic, or Lambda Cloud</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="stat-box">
                <h3>Attackers</h3>
                <p>Multiple strategies</p>
                <p>Real-time visualization</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="stat-box">
                <h3>Lambda Scraper</h3>
                <p>Recent attack data</p>
                <p>Web scraping & analysis</p>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
