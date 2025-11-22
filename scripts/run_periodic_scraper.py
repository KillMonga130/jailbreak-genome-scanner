"""Script to run periodic scraping on Lambda instances."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.integrations.lambda_scraper import LambdaWebScraper
from src.integrations.lambda_cloud import LambdaCloudClient
from src.utils.logger import log


async def main():
    """Run periodic scraper."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run periodic web scraper on Lambda")
    parser.add_argument(
        "--instance-id",
        type=str,
        help="Lambda instance ID to use for scraping (optional)"
    )
    parser.add_argument(
        "--interval-hours",
        type=int,
        default=6,
        help="Hours between scraping runs (default: 6)"
    )
    parser.add_argument(
        "--days-back",
        type=int,
        default=1,
        help="Days back to search (default: 1)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once instead of periodically"
    )
    
    args = parser.parse_args()
    
    # Initialize scraper
    lambda_client = LambdaCloudClient()
    scraper = LambdaWebScraper(
        lambda_client=lambda_client,
        instance_id=args.instance_id
    )
    
    if args.once:
        # Run once
        log.info("Running single scrape...")
        events = await scraper.scrape_recent_events(
            days_back=args.days_back,
            max_results=50
        )
        log.info(f"Scraped {len(events)} events")
        
        # Print summary
        for event in events[:5]:
            print(f"\n{event.title}")
            print(f"  Source: {event.source}")
            print(f"  Category: {event.category}")
            print(f"  Relevance: {event.relevance_score:.2f}")
            print(f"  URL: {event.url}")
    else:
        # Run periodically
        log.info(f"Starting periodic scraper (interval: {args.interval_hours} hours)")
        await scraper.run_periodic_scraping(
            interval_hours=args.interval_hours,
            days_back=args.days_back
        )


if __name__ == "__main__":
    asyncio.run(main())

