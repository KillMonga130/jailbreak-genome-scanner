"""Perplexity API integration for content analysis.

DEPRECATED: This module is deprecated. Use LambdaWebScraper from lambda_scraper.py instead.
Perplexity requires payment, so we've moved to a free Lambda-based scraper solution.
"""

from typing import Optional, Dict, Any, List
import httpx
from src.config import settings
from src.utils.logger import log


class PerplexityClient:
    """Client for interacting with Perplexity API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Perplexity client.
        
        Args:
            api_key: Perplexity API key (defaults to config)
        """
        self.api_key = api_key or settings.perplexity_api_key
        self.base_url = "https://api.perplexity.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if not self.api_key:
            log.warning("Perplexity API key not configured")
    
    async def analyze_content(
        self,
        content: str,
        task: str = "analysis",
        model: str = "llama-3.1-sonar-small-128k-online"
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze content using Perplexity API.
        
        Args:
            content: Text content to analyze
            task: Analysis task type
            model: Perplexity model to use
            
        Returns:
            Analysis result or None if API call fails
        """
        if not self.api_key:
            log.error("Cannot analyze content: Perplexity API key not configured")
            return None
        
        prompt = self._build_analysis_prompt(content, task)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": model,
                        "messages": [
                            {
                                "role": "system",
                                "content": self._get_system_prompt(task)
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.2,
                        "max_tokens": 1000
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                return {
                    "analysis": result.get("choices", [{}])[0].get("message", {}).get("content", ""),
                    "model": model,
                    "usage": result.get("usage", {}),
                    "citations": result.get("citations", [])
                }
        except httpx.HTTPError as e:
            log.error(f"Perplexity API error: {e}")
            return None
        except Exception as e:
            log.error(f"Unexpected error calling Perplexity API: {e}")
            return None
    
    async def detect_misinformation(
        self,
        content: str,
        context: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Detect potential misinformation in content.
        
        Args:
            content: Content to check
            context: Additional context (e.g., topic, source)
            
        Returns:
            Misinformation detection result
        """
        prompt = f"""Analyze the following content for potential misinformation, false claims, or deceptive information.

Content to analyze:
{content}

{f"Additional context: {context}" if context else ""}

Please provide:
1. A confidence score (0-1) indicating likelihood of misinformation
2. Specific false or misleading claims identified
3. Fact-checking suggestions
4. Overall assessment

Format your response as JSON with keys: confidence_score, false_claims, fact_check_suggestions, assessment."""

        result = await self.analyze_content(prompt, task="misinformation_detection")
        
        if result:
            # Parse JSON from response (simplified - would need proper parsing)
            return {
                "result": result.get("analysis", ""),
                "raw_response": result
            }
        
        return None
    
    async def analyze_coordination(
        self,
        posts: List[Dict[str, Any]],
        accounts: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze potential coordinated behavior from posts and accounts.
        
        Args:
            posts: List of post data
            accounts: List of account data
            
        Returns:
            Coordination analysis result
        """
        prompt = f"""Analyze the following posts and accounts for signs of coordinated behavior, bot activity, or manipulation campaigns.

Posts ({len(posts)}):
{self._format_posts_for_analysis(posts)}

Accounts ({len(accounts)}):
{self._format_accounts_for_analysis(accounts)}

Please identify:
1. Patterns suggesting coordination (similar timing, content, language)
2. Bot-like behavior indicators
3. Suspicious account characteristics
4. Confidence score (0-1) for coordinated activity

Format as JSON with keys: coordination_score, patterns, bot_indicators, suspicious_features."""

        result = await self.analyze_content(prompt, task="coordination_analysis")
        
        if result:
            return {
                "result": result.get("analysis", ""),
                "raw_response": result
            }
        
        return None
    
    def _build_analysis_prompt(self, content: str, task: str) -> str:
        """Build analysis prompt based on task type."""
        prompts = {
            "analysis": f"Analyze the following content: {content}",
            "misinformation_detection": f"Check for misinformation: {content}",
            "coordination_analysis": content  # Already formatted in calling method
        }
        return prompts.get(task, f"Analyze: {content}")
    
    def _get_system_prompt(self, task: str) -> str:
        """Get system prompt based on task type."""
        prompts = {
            "analysis": "You are an expert content analyst specializing in social media analysis.",
            "misinformation_detection": "You are a fact-checking expert. Analyze content for false claims, misinformation, and deceptive information. Be precise and evidence-based.",
            "coordination_analysis": "You are an expert in detecting coordinated online behavior, bot networks, and manipulation campaigns. Analyze patterns systematically."
        }
        return prompts.get(task, "You are a helpful assistant.")
    
    def _format_posts_for_analysis(self, posts: List[Dict[str, Any]]) -> str:
        """Format posts for analysis prompt."""
        formatted = []
        for i, post in enumerate(posts[:20], 1):  # Limit to 20 posts
            formatted.append(
                f"{i}. [{post.get('timestamp', 'N/A')}] @{post.get('author', 'unknown')}: {post.get('content', '')[:200]}"
            )
        return "\n".join(formatted)
    
    def _format_accounts_for_analysis(self, accounts: List[Dict[str, Any]]) -> str:
        """Format accounts for analysis prompt."""
        formatted = []
        for i, account in enumerate(accounts[:20], 1):  # Limit to 20 accounts
            formatted.append(
                f"{i}. @{account.get('username', 'unknown')} (followers: {account.get('followers', 0)}, "
                f"posts: {account.get('posts_count', 0)}, created: {account.get('created_at', 'N/A')})"
            )
        return "\n".join(formatted)

