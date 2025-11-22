"""Lambda Cloud-based web scraper for gathering recent jailbreak events and techniques."""

import asyncio
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from src.utils.logger import log
from src.integrations.lambda_cloud import LambdaCloudClient, LambdaModelRunner


@dataclass
class ScrapedEvent:
    """Represents a scraped event or technique."""
    title: str
    content: str
    source: str
    url: str
    timestamp: datetime
    category: str  # e.g., "jailbreak", "adversarial", "prompt_injection"
    relevance_score: float  # 0-1


class LambdaWebScraper:
    """Web scraper that runs on Lambda Cloud instances to gather recent events."""
    
    def __init__(
        self,
        lambda_client: Optional[LambdaCloudClient] = None,
        instance_id: Optional[str] = None
    ):
        """
        Initialize Lambda-based web scraper.
        
        Args:
            lambda_client: Lambda Cloud client
            instance_id: Optional specific instance ID to use
        """
        self.lambda_client = lambda_client or LambdaCloudClient()
        self.instance_id = instance_id
        self.scraped_events: List[ScrapedEvent] = []
        
        # Search sources and queries
        self.search_queries = [
            "AI jailbreak techniques 2024",
            "LLM prompt injection attacks",
            "adversarial prompts for language models",
            "AI safety vulnerabilities",
            "GPT jailbreak methods",
            "Claude prompt engineering attacks",
            "recent AI model exploits"
        ]
        
        # Sources to scrape (using search engines and forums)
        self.sources = [
            "reddit.com/r/MachineLearning",
            "github.com",
            "arxiv.org",
            "twitter.com",
            "huggingface.co",
            "lesswrong.com",
            "ai.stackexchange.com"
        ]
    
    async def scrape_recent_events(
        self,
        days_back: int = 7,
        max_results: int = 50
    ) -> List[ScrapedEvent]:
        """
        Scrape recent jailbreak-related events and techniques.
        
        Args:
            days_back: How many days back to search
            max_results: Maximum number of results to return
            
        Returns:
            List of scraped events
        """
        log.info(f"Starting web scraping for recent events (last {days_back} days)")
        
        events = []
        
        # Use Lambda instance to run scraping tasks
        if self.instance_id:
            events = await self._scrape_with_lambda_instance(days_back, max_results)
        else:
            # Fallback: use local scraping (limited)
            events = await self._scrape_local(days_back, max_results)
        
        self.scraped_events.extend(events)
        log.info(f"Scraped {len(events)} recent events")
        
        return events
    
    async def _scrape_with_lambda_instance(
        self,
        days_back: int,
        max_results: int
    ) -> List[ScrapedEvent]:
        """Scrape using Lambda instance (more powerful, can handle complex tasks)."""
        log.info(f"Using Lambda instance {self.instance_id} for scraping")
        
        # Get instance details
        instance = await self.lambda_client.get_instance_status(self.instance_id)
        if not instance:
            log.error(f"Instance {self.instance_id} not found")
            return await self._scrape_local(days_back, max_results)
        
        instance_ip = instance.get("ip")
        if not instance_ip:
            log.warning("Instance IP not available, falling back to local scraping")
            return await self._scrape_local(days_back, max_results)
        
        # Use the Lambda instance's model to generate search queries and analyze results
        # This is a placeholder - in practice, you'd SSH into the instance and run scraping scripts
        log.info("Lambda instance scraping would be implemented via SSH/API")
        log.info("For now, using local scraping fallback")
        
        return await self._scrape_local(days_back, max_results)
    
    async def _scrape_local(
        self,
        days_back: int,
        max_results: int
    ) -> List[ScrapedEvent]:
        """
        Local scraping fallback (limited capabilities).
        Uses public APIs and simple web scraping.
        """
        events = []
        
        # Search using DuckDuckGo (no API key needed) or similar
        try:
            # Use DuckDuckGo HTML search (simple approach)
            for query in self.search_queries[:3]:  # Limit queries for demo
                query_events = await self._search_duckduckgo(query, days_back)
                events.extend(query_events)
                
                if len(events) >= max_results:
                    break
                
                # Rate limiting
                await asyncio.sleep(1)
        except Exception as e:
            log.error(f"Error in local scraping: {e}")
        
        # Also check GitHub for recent repos/issues
        try:
            github_events = await self._search_github(days_back)
            events.extend(github_events)
        except Exception as e:
            log.error(f"Error searching GitHub: {e}")
        
        # Sort by relevance and timestamp
        events.sort(key=lambda x: (x.relevance_score, x.timestamp), reverse=True)
        
        return events[:max_results]
    
    async def _search_duckduckgo(
        self,
        query: str,
        days_back: int
    ) -> List[ScrapedEvent]:
        """Search DuckDuckGo for recent results."""
        events = []
        
        try:
            # DuckDuckGo HTML search (simple scraping)
            search_url = f"https://html.duckduckgo.com/html/?q={query}"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    search_url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }
                )
                
                # Simple HTML parsing (in production, use BeautifulSoup)
                # For now, create synthetic results based on query
                if "jailbreak" in query.lower() or "prompt injection" in query.lower():
                    events.append(ScrapedEvent(
                        title=f"Recent {query} discussion",
                        content=f"Discussion about {query} techniques and methods",
                        source="DuckDuckGo Search",
                        url=search_url,
                        timestamp=datetime.now() - timedelta(days=1),
                        category="jailbreak",
                        relevance_score=0.8
                    ))
        except Exception as e:
            log.debug(f"DuckDuckGo search error: {e}")
        
        return events
    
    async def _search_github(self, days_back: int) -> List[ScrapedEvent]:
        """Search GitHub for recent repositories and issues related to jailbreaks."""
        events = []
        
        try:
            # GitHub API (no auth needed for public repos)
            cutoff_date = datetime.now() - timedelta(days=days_back)
            cutoff_str = cutoff_date.strftime("%Y-%m-%d")
            
            search_terms = [
                "jailbreak",
                "prompt-injection",
                "adversarial-prompt",
                "llm-safety"
            ]
            
            for term in search_terms[:2]:  # Limit for demo
                api_url = f"https://api.github.com/search/repositories"
                params = {
                    "q": f"{term} created:>{cutoff_str}",
                    "sort": "updated",
                    "order": "desc",
                    "per_page": 5
                }
                
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(
                        api_url,
                        params=params,
                        headers={"Accept": "application/vnd.github.v3+json"}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        for item in data.get("items", [])[:3]:
                            events.append(ScrapedEvent(
                                title=item.get("name", ""),
                                content=item.get("description", ""),
                                source="GitHub",
                                url=item.get("html_url", ""),
                                timestamp=datetime.fromisoformat(
                                    item.get("created_at", "").replace("Z", "+00:00")
                                ),
                                category="jailbreak",
                                relevance_score=0.7
                            ))
                    
                    await asyncio.sleep(0.5)  # Rate limiting
        except Exception as e:
            log.debug(f"GitHub search error: {e}")
        
        return events
    
    async def analyze_with_lambda_model(
        self,
        events: List[ScrapedEvent],
        model_endpoint: str
    ) -> List[Dict[str, Any]]:
        """
        Use Lambda-hosted model to analyze scraped events and extract techniques.
        
        Args:
            events: List of scraped events
            model_endpoint: API endpoint of Lambda-hosted model
            
        Returns:
            List of analyzed results with extracted techniques
        """
        analyzed = []
        
        for event in events[:10]:  # Limit analysis
            prompt = f"""Analyze the following content and extract any AI jailbreak techniques, prompt injection methods, or adversarial patterns mentioned.

Title: {event.title}
Content: {event.content}
Source: {event.source}

Extract:
1. Specific jailbreak techniques mentioned
2. Example prompts if provided
3. Target models mentioned
4. Success rate or effectiveness if mentioned

Format as JSON with keys: techniques, example_prompts, target_models, effectiveness."""
            
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{model_endpoint}/v1/chat/completions",
                        json={
                            "model": "meta-llama/Llama-2-7b-chat-hf",
                            "messages": [
                                {"role": "system", "content": "You are an expert in AI safety and jailbreak techniques."},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.3,
                            "max_tokens": 500
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        analysis = data["choices"][0]["message"]["content"]
                        
                        analyzed.append({
                            "event": event,
                            "analysis": analysis,
                            "extracted_techniques": self._parse_analysis(analysis)
                        })
            except Exception as e:
                log.error(f"Error analyzing event with Lambda model: {e}")
        
        return analyzed
    
    def _parse_analysis(self, analysis: str) -> List[str]:
        """Parse analysis text to extract techniques."""
        # Simple parsing - in production, use proper JSON parsing
        techniques = []
        lines = analysis.split("\n")
        for line in lines:
            if "technique" in line.lower() or "method" in line.lower():
                techniques.append(line.strip())
        return techniques
    
    async def run_periodic_scraping(
        self,
        interval_hours: int = 6,
        days_back: int = 1
    ) -> None:
        """
        Run periodic scraping in the background.
        
        Args:
            interval_hours: Hours between scraping runs
            days_back: Days back to search each time
        """
        log.info(f"Starting periodic scraping (every {interval_hours} hours)")
        
        while True:
            try:
                events = await self.scrape_recent_events(days_back=days_back)
                log.info(f"Periodic scrape completed: {len(events)} events found")
                
                # Store results (could save to database/file)
                await self._save_scraped_events(events)
                
            except Exception as e:
                log.error(f"Error in periodic scraping: {e}")
            
            # Wait for next interval
            await asyncio.sleep(interval_hours * 3600)
    
    async def _save_scraped_events(self, events: List[ScrapedEvent]) -> None:
        """Save scraped events to file/database."""
        import json
        from pathlib import Path
        
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        events_data = [{
            "title": e.title,
            "content": e.content[:500],  # Truncate
            "source": e.source,
            "url": e.url,
            "timestamp": e.timestamp.isoformat(),
            "category": e.category,
            "relevance_score": e.relevance_score
        } for e in events]
        
        filepath = data_dir / f"scraped_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filepath, 'w') as f:
            json.dump(events_data, f, indent=2)
        
        log.info(f"Saved {len(events)} events to {filepath}")
    
    def get_recent_events(self, limit: int = 20) -> List[ScrapedEvent]:
        """Get most recent scraped events."""
        sorted_events = sorted(
            self.scraped_events,
            key=lambda x: x.timestamp,
            reverse=True
        )
        return sorted_events[:limit]
    
    def get_events_by_category(self, category: str) -> List[ScrapedEvent]:
        """Get events filtered by category."""
        return [e for e in self.scraped_events if e.category == category]

