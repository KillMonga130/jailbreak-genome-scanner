"""Example usage of the Jailbreak Genome Scanner."""

import asyncio
import json
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent.monitoring_agent import MonitoringAgent
from src.models.post import Post, Platform
from src.detectors.bot_detector import BotDetector
from src.detectors.coordination_detector import CoordinationDetector


def create_example_posts() -> list[Post]:
    """Create example posts for demonstration."""
    posts = [
        Post(
            id="post_001",
            platform=Platform.TWITTER,
            author_id="user_001",
            author_username="suspicious_bot",
            content="Check out this amazing product! #ad #sponsored",
            timestamp=datetime(2025, 1, 15, 10, 0, 0),
            url="https://twitter.com/user001/status/12345",
            likes=10,
            retweets_shares=2,
            replies=0,
            hashtags=["ad", "sponsored"],
            links=["https://example.com/product"]
        ),
        Post(
            id="post_002",
            platform=Platform.TWITTER,
            author_id="user_002",
            author_username="bot_account_2",
            content="Check out this amazing product! #ad #sponsored",
            timestamp=datetime(2025, 1, 15, 10, 1, 0),
            url="https://twitter.com/user002/status/12346",
            likes=5,
            retweets_shares=1,
            replies=0,
            hashtags=["ad", "sponsored"],
            links=["https://example.com/product"]
        ),
        Post(
            id="post_003",
            platform=Platform.TWITTER,
            author_id="user_003",
            author_username="coordinated_bot3",
            content="Check out this amazing product! #ad #sponsored",
            timestamp=datetime(2025, 1, 15, 10, 2, 0),
            url="https://twitter.com/user003/status/12347",
            likes=3,
            retweets_shares=0,
            replies=0,
            hashtags=["ad", "sponsored"],
            links=["https://example.com/product"]
        ),
    ]
    
    return posts


def example_basic_usage():
    """Basic usage example."""
    print("=" * 60)
    print("Basic Usage Example")
    print("=" * 60)
    
    # Create agent
    agent = MonitoringAgent()
    
    # Create example posts
    posts = create_example_posts()
    
    # Ingest posts
    print(f"\nIngesting {len(posts)} posts...")
    agent.ingest_posts(posts)
    
    # Analyze
    print("Analyzing posts...")
    results = agent.analyze_posts()
    
    # Display summary
    summary = results.get("summary", {})
    print(f"\nAnalysis Summary:")
    print(f"  Total Posts: {summary.get('total_posts', 0)}")
    print(f"  Total Accounts: {summary.get('total_accounts', 0)}")
    print(f"  Bots Detected: {summary.get('bots_detected', 0)}")
    print(f"  Coordination Events: {summary.get('coordination_events', 0)}")
    print(f"  Flagged Accounts: {summary.get('flagged_accounts_count', 0)}")
    
    # Display flagged accounts
    flagged = results.get("flagged_accounts", [])
    if flagged:
        print(f"\nFlagged Accounts ({len(flagged)}):")
        for account in flagged:
            print(f"  - {account.get('account_id')}: "
                  f"Bot Probability = {account.get('bot_probability', 0):.2f}")
            for reason in account.get('reasons', []):
                print(f"    Reason: {reason}")
    
    # Display coordination events
    coord_events = results.get("coordination_detections", [])
    if coord_events:
        print(f"\nCoordination Events ({len(coord_events)}):")
        for event in coord_events:
            print(f"  - Time: {event.get('timestamp')}")
            print(f"    Accounts: {event.get('account_count', 0)}")
            print(f"    Coordination Score: {event.get('coordination_score', 0):.2f}")


def example_custom_detectors():
    """Example with custom detectors."""
    print("\n" + "=" * 60)
    print("Custom Detectors Example")
    print("=" * 60)
    
    # Create agent
    agent = MonitoringAgent()
    
    # Create custom detectors with different thresholds
    bot_detector = BotDetector(
        min_similarity_score=0.9,  # Higher threshold
        activity_threshold=100  # More posts per day
    )
    
    coordination_detector = CoordinationDetector(
        time_window_minutes=30,  # Smaller time window
        min_accounts=3,  # Fewer accounts needed
        similarity_threshold=0.9  # Higher similarity threshold
    )
    
    # Add custom detectors
    agent.add_detector(bot_detector)
    agent.add_detector(coordination_detector)
    
    # Create and ingest posts
    posts = create_example_posts()
    agent.ingest_posts(posts)
    
    # Analyze
    print("Analyzing with custom detectors...")
    results = agent.analyze_posts()
    
    summary = results.get("summary", {})
    print(f"\nAnalysis Results:")
    print(f"  Bots Detected: {summary.get('bots_detected', 0)}")
    print(f"  Coordination Events: {summary.get('coordination_events', 0)}")


def example_vector_search():
    """Example of using vector similarity search."""
    print("\n" + "=" * 60)
    print("Vector Similarity Search Example")
    print("=" * 60)
    
    from src.vector_db.vector_store import VectorStore
    
    # Create vector store
    vector_store = VectorStore()
    
    # Create and ingest posts
    posts = create_example_posts()
    vector_store.add_posts(posts)
    
    # Search for similar posts
    query = "Check out this amazing product!"
    print(f"\nSearching for posts similar to: '{query}'")
    
    similar = vector_store.find_similar(
        query_text=query,
        n_results=5,
        threshold=0.7
    )
    
    print(f"\nFound {len(similar)} similar posts:")
    for i, result in enumerate(similar, 1):
        print(f"\n  {i}. Post ID: {result['id']}")
        print(f"     Similarity: {result.get('similarity', 0):.3f}")
        print(f"     Content: {result.get('content', '')[:100]}...")


def example_social_graph():
    """Example of social graph analysis."""
    print("\n" + "=" * 60)
    print("Social Graph Analysis Example")
    print("=" * 60)
    
    from src.graphs.social_graph import SocialGraph
    from src.models.post import Account
    
    # Create graph
    graph = SocialGraph()
    
    # Add accounts
    accounts = [
        Account(id="user_001", username="user1", platform=Platform.TWITTER),
        Account(id="user_002", username="user2", platform=Platform.TWITTER),
        Account(id="user_003", username="user3", platform=Platform.TWITTER),
    ]
    
    for account in accounts:
        graph.add_account(account)
    
    # Add connections
    graph.add_connection("user_001", "user_002")
    graph.add_connection("user_002", "user_003")
    graph.add_connection("user_003", "user_001")
    
    # Add posts
    posts = create_example_posts()
    for post in posts:
        graph.add_post(post)
    
    # Analyze
    stats = graph.get_statistics()
    print(f"\nGraph Statistics:")
    print(f"  Nodes: {stats['nodes']}")
    print(f"  Edges: {stats['edges']}")
    print(f"  Density: {stats['density']:.3f}")
    
    # Find communities
    communities = graph.find_communities()
    print(f"\nCommunities: {len(set(communities.values()))}")
    
    # Get central accounts
    central = graph.get_central_accounts(top_k=5)
    print(f"\nTop Central Accounts:")
    for account_id, score in central:
        print(f"  {account_id}: {score:.3f}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Jailbreak Genome Scanner - Example Usage")
    print("=" * 60)
    
    # Run examples
    example_basic_usage()
    example_custom_detectors()
    example_vector_search()
    example_social_graph()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)

