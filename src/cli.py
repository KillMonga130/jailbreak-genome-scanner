"""Command-line interface for the monitoring agent."""

import json
import asyncio
import argparse
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.json import JSON
from src.utils.logger import log
from src.agent.monitoring_agent import MonitoringAgent
from src.models.post import Post, Platform


console = Console()


def print_banner():
    """Print application banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║      Jailbreak Genome Scanner                             ║
    ║      AI-Powered Social Media Misinformation Detection     ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def load_posts_from_json(file_path: str) -> List[Post]:
    """Load posts from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    posts = []
    for item in data:
        try:
            post = Post(**item)
            posts.append(post)
        except Exception as e:
            log.warning(f"Failed to parse post: {e}")
    
    return posts


def save_results_to_json(results: dict, file_path: str) -> None:
    """Save analysis results to a JSON file."""
    output_path = Path(file_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    
    console.print(f"Results saved to {file_path}", style="green")


def display_summary(results: dict) -> None:
    """Display analysis summary in a formatted table."""
    summary = results.get("summary", {})
    
    table = Table(title="Analysis Summary", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Posts", str(summary.get("total_posts", 0)))
    table.add_row("Total Accounts", str(summary.get("total_accounts", 0)))
    table.add_row("Bots Detected", str(summary.get("bots_detected", 0)))
    table.add_row("Coordination Events", str(summary.get("coordination_events", 0)))
    table.add_row("Flagged Accounts", str(summary.get("flagged_accounts_count", 0)))
    
    console.print(table)


def display_flagged_accounts(results: dict) -> None:
    """Display flagged accounts in a table."""
    flagged = results.get("flagged_accounts", [])
    
    if not flagged:
        console.print("No flagged accounts found.", style="yellow")
        return
    
    table = Table(title=f"Flagged Accounts ({len(flagged)})", show_header=True, header_style="bold red")
    table.add_column("Account ID", style="cyan")
    table.add_column("Username", style="white")
    table.add_column("Bot Probability", style="yellow")
    table.add_column("Flags", style="red")
    
    for account in flagged[:20]:  # Limit display to 20
        flags_str = ", ".join(account.get("flags", []))[:50]
        table.add_row(
            account.get("account_id", "")[:20],
            account.get("account", {}).get("username", "unknown")[:30],
            f"{account.get('bot_probability', 0):.2f}",
            flags_str
        )
    
    console.print(table)
    
    if len(flagged) > 20:
        console.print(f"... and {len(flagged) - 20} more flagged accounts", style="dim")


def display_coordination_events(results: dict) -> None:
    """Display coordination events."""
    events = results.get("coordination_detections", [])
    
    if not events:
        console.print("No coordination events detected.", style="yellow")
        return
    
    table = Table(title=f"Coordination Events ({len(events)})", show_header=True, header_style="bold yellow")
    table.add_column("Timestamp", style="cyan")
    table.add_column("Accounts", style="white")
    table.add_column("Posts", style="white")
    table.add_column("Coordination Score", style="yellow")
    table.add_column("Pattern Type", style="magenta")
    
    for event in events[:10]:  # Limit to 10 events
        timestamp = event.get("timestamp", "")
        if isinstance(timestamp, str):
            timestamp = timestamp[:19]  # Truncate ISO format
        
        table.add_row(
            str(timestamp),
            str(event.get("account_count", 0)),
            str(event.get("post_count", 0)),
            f"{event.get('coordination_score', 0):.2f}",
            event.get("pattern_type", "unknown")
        )
    
    console.print(table)
    
    if len(events) > 10:
        console.print(f"... and {len(events) - 10} more coordination events", style="dim")


def monitor_command(args):
    """Handle the monitor command."""
    console.print("Monitor command not yet implemented.", style="yellow")
    console.print("Use 'analyze' command to process existing post data.", style="dim")


def analyze_command(args):
    """Handle the analyze command."""
    print_banner()
    
    # Load posts
    if args.input:
        console.print(f"Loading posts from {args.input}...", style="cyan")
        posts = load_posts_from_json(args.input)
        console.print(f"Loaded {len(posts)} posts", style="green")
    else:
        console.print("No input file specified. Use --input <file.json>", style="red")
        return
    
    # Initialize agent
    console.print("Initializing monitoring agent...", style="cyan")
    agent = MonitoringAgent()
    
    # Ingest posts
    console.print("Ingesting posts...", style="cyan")
    agent.ingest_posts(posts)
    
    # Analyze
    console.print("Running analysis...", style="cyan")
    with console.status("[bold green]Analyzing posts..."):
        results = agent.analyze_posts(use_perplexity=args.use_perplexity)
    
    # Display results
    console.print("\n")
    display_summary(results)
    console.print("\n")
    
    if args.show_flagged:
        display_flagged_accounts(results)
        console.print("\n")
    
    if args.show_coordination:
        display_coordination_events(results)
        console.print("\n")
    
    # Save results
    if args.output:
        save_results_to_json(results, args.output)
    
    # Full JSON output
    if args.json:
        console.print(JSON(json.dumps(results, indent=2, default=str)))


def visualize_command(args):
    """Handle the visualize command."""
    console.print("Visualize command not yet implemented.", style="yellow")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Jailbreak Genome Scanner - AI-powered social media monitoring"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Start continuous monitoring")
    monitor_parser.add_argument("--platforms", nargs="+", default=["twitter"], help="Platforms to monitor")
    monitor_parser.add_argument("--interval", type=int, default=300, help="Monitoring interval in seconds")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze existing post data")
    analyze_parser.add_argument("--input", "-i", required=True, help="Input JSON file with posts")
    analyze_parser.add_argument("--output", "-o", help="Output JSON file for results")
    analyze_parser.add_argument("--json", action="store_true", help="Output full JSON results")
    analyze_parser.add_argument("--show-flagged", action="store_true", default=True, help="Show flagged accounts")
    analyze_parser.add_argument("--show-coordination", action="store_true", default=True, help="Show coordination events")
    analyze_parser.add_argument("--use-perplexity", action="store_true", help="Use Perplexity API for analysis")
    
    # Visualize command
    visualize_parser = subparsers.add_parser("visualize", help="Generate visualizations")
    visualize_parser.add_argument("--input", "-i", required=True, help="Input JSON file with results")
    visualize_parser.add_argument("--output", "-o", help="Output image file")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "monitor":
            monitor_command(args)
        elif args.command == "analyze":
            analyze_command(args)
        elif args.command == "visualize":
            visualize_command(args)
    except KeyboardInterrupt:
        console.print("\n\nInterrupted by user", style="yellow")
    except Exception as e:
        console.print(f"\n\nError: {e}", style="red")
        log.exception("CLI error")


if __name__ == "__main__":
    main()

