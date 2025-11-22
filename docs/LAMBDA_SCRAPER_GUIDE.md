# Lambda Web Scraper Guide

## Overview

The Lambda Web Scraper is a replacement for Perplexity integration that uses Lambda Cloud instances to periodically search and gather recent jailbreak events, techniques, and patterns from the web.

## Features

- **Web Scraping**: Searches GitHub, forums, and other sources for recent jailbreak-related content
- **Lambda Integration**: Can use Lambda Cloud instances for more powerful scraping
- **Periodic Updates**: Runs automatically at configurable intervals
- **Event Analysis**: Uses Lambda-hosted models to analyze and extract techniques
- **No API Costs**: Free alternative to paid Perplexity API

## Quick Start

### Basic Usage (Local Scraping)

```python
from src.integrations.lambda_scraper import LambdaWebScraper

# Create scraper
scraper = LambdaWebScraper()

# Scrape recent events
events = await scraper.scrape_recent_events(days_back=7, max_results=50)

# View results
for event in events:
    print(f"{event.title} - {event.source}")
    print(f"  {event.content[:200]}...")
```

### Using Lambda Instance

```python
from src.integrations.lambda_scraper import LambdaWebScraper
from src.integrations.lambda_cloud import LambdaCloudClient

# Use existing Lambda instance
lambda_client = LambdaCloudClient()
scraper = LambdaWebScraper(
    lambda_client=lambda_client,
    instance_id="your_instance_id"
)

# Scrape with Lambda instance
events = await scraper.scrape_recent_events(days_back=7, max_results=50)
```

### Periodic Scraping

Run the periodic scraper script:

```bash
# Run once
python scripts/run_periodic_scraper.py --once

# Run periodically (every 6 hours)
python scripts/run_periodic_scraper.py --interval-hours 6

# Use specific Lambda instance
python scripts/run_periodic_scraper.py --instance-id instance_123 --interval-hours 6
```

## Dashboard Integration

The dashboard automatically uses the Lambda scraper when "Gather Recent Attack Data" is enabled:

1. Open the dashboard
2. In sidebar, check "Gather Recent Attack Data"
3. Optionally provide a Lambda Instance ID for more powerful scraping
4. Start evaluation - scraper will gather recent patterns automatically

## Scraped Sources

The scraper searches:

- **GitHub**: Recent repositories and issues related to jailbreaks
- **DuckDuckGo**: Web search results for jailbreak techniques
- **Forums**: Reddit, StackExchange, etc. (via search engines)
- **Research Papers**: ArXiv and academic sources

## Event Structure

Each scraped event contains:

```python
@dataclass
class ScrapedEvent:
    title: str              # Event title
    content: str            # Event content/description
    source: str            # Source (GitHub, DuckDuckGo, etc.)
    url: str               # Source URL
    timestamp: datetime    # When event was found
    category: str          # Category (jailbreak, adversarial, etc.)
    relevance_score: float # Relevance score (0-1)
```

## Analysis with Lambda Models

You can use Lambda-hosted models to analyze scraped events:

```python
# Analyze events with Lambda model
analyzed = await scraper.analyze_with_lambda_model(
    events=events,
    model_endpoint="http://<instance_ip>:8000/v1/chat/completions"
)

# Extract techniques
for result in analyzed:
    print(f"Event: {result['event'].title}")
    print(f"Techniques: {result['extracted_techniques']}")
```

## Configuration

### Search Queries

Default queries include:
- "AI jailbreak techniques 2024"
- "LLM prompt injection attacks"
- "adversarial prompts for language models"
- "AI safety vulnerabilities"
- "GPT jailbreak methods"
- "Claude prompt engineering attacks"
- "recent AI model exploits"

### Scraping Interval

Default: 6 hours
- Adjust with `--interval-hours` flag
- Shorter intervals = more up-to-date but more resource usage
- Longer intervals = less frequent updates but lower resource usage

### Days Back

Default: 1 day
- Adjust with `--days-back` flag
- Searches for events from the last N days
- Larger values = more historical data but slower scraping

## Data Storage

Scraped events are automatically saved to:
- `data/scraped_events_YYYYMMDD_HHMMSS.json`

Each file contains:
- Event metadata
- Content snippets
- Source URLs
- Timestamps
- Relevance scores

## Advantages over Perplexity

1. **No API Costs**: Completely free
2. **Lambda Integration**: Can leverage GPU instances for analysis
3. **Customizable**: Easy to add new sources and queries
4. **Open Source**: Full control over scraping logic
5. **Periodic Updates**: Automatic background scraping

## Limitations

1. **Rate Limits**: Some sources (GitHub) have rate limits
2. **Simple Parsing**: Basic HTML parsing (can be improved with BeautifulSoup)
3. **Limited Sources**: Currently searches GitHub and DuckDuckGo primarily
4. **No Real-time**: Scraping happens on schedule, not real-time

## Future Improvements

- Add more sources (Twitter/X, Reddit API, ArXiv API)
- Better HTML parsing with BeautifulSoup
- Machine learning-based relevance scoring
- Real-time event streaming
- Database storage instead of JSON files
- Webhook notifications for high-relevance events

## Troubleshooting

### No events found
- Check internet connection
- Verify Lambda instance is running (if using)
- Try increasing `days_back` parameter
- Check rate limits on GitHub API

### Scraper errors
- Check Lambda API key is set in `.env`
- Verify instance ID is correct (if using)
- Check logs for specific error messages

### Slow scraping
- Reduce `max_results` parameter
- Use Lambda instance for faster processing
- Reduce number of search queries
- Increase scraping interval

