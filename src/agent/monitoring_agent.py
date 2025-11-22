"""Main monitoring agent orchestrator."""

import asyncio
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict
from src.utils.logger import log
from src.config import settings
from src.models.post import Post, Account, Platform
from src.vector_db.vector_store import VectorStore
from src.graphs.social_graph import SocialGraph
from src.detectors.bot_detector import BotDetector
from src.detectors.coordination_detector import CoordinationDetector
from src.integrations.perplexity import PerplexityClient


class MonitoringAgent:
    """Main agent for monitoring social media and detecting coordinated attacks."""
    
    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        perplexity_client: Optional[PerplexityClient] = None
    ):
        """
        Initialize the monitoring agent.
        
        Args:
            vector_store: Optional vector store instance
            perplexity_client: Optional Perplexity client instance
        """
        self.vector_store = vector_store or VectorStore()
        self.perplexity_client = perplexity_client or PerplexityClient()
        self.social_graph = SocialGraph()
        self.bot_detector = BotDetector()
        self.coordination_detector = CoordinationDetector()
        
        # Storage
        self.posts: List[Post] = []
        self.accounts: Dict[str, Account] = {}
        self.posts_by_account: Dict[str, List[Post]] = defaultdict(list)
        
        # Detection results
        self.bot_results: Dict[str, Dict[str, Any]] = {}
        self.coordination_results: List[Dict[str, Any]] = []
        self.flagged_accounts: Set[str] = set()
        
        log.info("MonitoringAgent initialized")
    
    def add_detector(self, detector: Any) -> None:
        """
        Add a custom detector (bot or coordination).
        
        Args:
            detector: Detector instance (BotDetector or CoordinationDetector)
        """
        if isinstance(detector, BotDetector):
            self.bot_detector = detector
            log.info("Custom BotDetector added")
        elif isinstance(detector, CoordinationDetector):
            self.coordination_detector = detector
            log.info("Custom CoordinationDetector added")
        else:
            log.warning(f"Unknown detector type: {type(detector)}")
    
    def ingest_posts(self, posts: List[Post]) -> None:
        """
        Ingest posts for analysis.
        
        Args:
            posts: List of Post objects to analyze
        """
        log.info(f"Ingesting {len(posts)} posts")
        
        for post in posts:
            self.posts.append(post)
            self.posts_by_account[post.author_id].append(post)
            
            # Add to vector store
            self.vector_store.add_post(post)
            
            # Add to social graph
            self.social_graph.add_post(post)
            
            # Ensure account exists
            if post.author_id not in self.accounts:
                account = Account(
                    id=post.author_id,
                    username=post.author_username,
                    platform=post.platform
                )
                self.accounts[post.author_id] = account
                self.social_graph.add_account(account)
        
        log.info(f"Total posts: {len(self.posts)}, Total accounts: {len(self.accounts)}")
    
    def analyze_posts(
        self,
        posts: Optional[List[Post]] = None,
        use_perplexity: bool = True
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on posts.
        
        Args:
            posts: Optional list of posts to analyze (defaults to all ingested posts)
            use_perplexity: Whether to use Perplexity API for analysis
            
        Returns:
            Analysis results dictionary
        """
        posts_to_analyze = posts or self.posts
        
        if not posts_to_analyze:
            log.warning("No posts to analyze")
            return {
                "bot_detections": {},
                "coordination_detections": [],
                "flagged_accounts": [],
                "summary": {
                    "total_posts": 0,
                    "total_accounts": 0,
                    "bots_detected": 0,
                    "coordination_events": 0
                }
            }
        
        log.info(f"Analyzing {len(posts_to_analyze)} posts")
        
        # 1. Bot detection
        log.info("Running bot detection...")
        self.bot_results = self._detect_bots()
        
        # 2. Coordination detection
        log.info("Running coordination detection...")
        self.coordination_results = self.coordination_detector.detect_coordination(
            posts_to_analyze,
            self.vector_store
        )
        
        # 3. Social graph analysis
        log.info("Running social graph analysis...")
        graph_results = self._analyze_social_graph()
        
        # 4. Optional: Perplexity analysis
        perplexity_results = {}
        if use_perplexity and self.perplexity_client.api_key:
            log.info("Running Perplexity analysis...")
            perplexity_results = asyncio.run(
                self._perplexity_analysis(posts_to_analyze)
            )
        
        # 5. Flag suspicious accounts
        self._flag_suspicious_accounts()
        
        # Compile results
        results = {
            "bot_detections": self.bot_results,
            "coordination_detections": self.coordination_results,
            "graph_analysis": graph_results,
            "perplexity_analysis": perplexity_results,
            "flagged_accounts": [
                {
                    "account_id": account_id,
                    "account": self.accounts[account_id].dict() if account_id in self.accounts else None,
                    "bot_probability": self.bot_results.get(account_id, {}).get("bot_probability", 0.0),
                    "flags": self.bot_results.get(account_id, {}).get("flags", []),
                    "reasons": self.bot_results.get(account_id, {}).get("reasons", [])
                }
                for account_id in self.flagged_accounts
            ],
            "summary": {
                "total_posts": len(self.posts),
                "total_accounts": len(self.accounts),
                "bots_detected": len([r for r in self.bot_results.values() if r.get("bot_probability", 0) > 0.7]),
                "coordination_events": len(self.coordination_results),
                "flagged_accounts_count": len(self.flagged_accounts),
                "timestamp": datetime.now().isoformat()
            }
        }
        
        log.info(f"Analysis complete: {results['summary']}")
        return results
    
    def _detect_bots(self) -> Dict[str, Dict[str, Any]]:
        """Run bot detection on all accounts."""
        # Prepare accounts with their posts
        accounts_with_posts = {}
        for account_id, posts in self.posts_by_account.items():
            if posts:
                accounts_with_posts[account_id] = posts
        
        # Run batch detection
        results = self.bot_detector.batch_detect(accounts_with_posts)
        
        # Update account objects with bot probability
        for account_id, result in results.items():
            if account_id in self.accounts:
                self.accounts[account_id].bot_probability = result.get("bot_probability", 0.0)
                self.accounts[account_id].suspicious_score = result.get("suspicious_score", 0.0)
        
        return results
    
    def _analyze_social_graph(self) -> Dict[str, Any]:
        """Run social graph analysis."""
        stats = self.social_graph.get_statistics()
        communities = self.social_graph.find_communities()
        central_accounts = self.social_graph.get_central_accounts(top_k=20)
        
        return {
            "statistics": stats,
            "communities": {
                account_id: comm_id
                for account_id, comm_id in communities.items()
            },
            "central_accounts": [
                {
                    "account_id": account_id,
                    "username": self.accounts.get(account_id, Account(id=account_id, username="unknown", platform=Platform.UNKNOWN)).username,
                    "pagerank_score": score
                }
                for account_id, score in central_accounts
            ]
        }
    
    async def _perplexity_analysis(
        self,
        posts: List[Post]
    ) -> Dict[str, Any]:
        """Run Perplexity analysis on posts."""
        if not posts:
            return {}
        
        # Sample posts for analysis (limit to avoid API costs)
        sample_posts = posts[:10] if len(posts) > 10 else posts
        
        results = {}
        
        for post in sample_posts:
            # Detect misinformation
            misinformation_result = await self.perplexity_client.detect_misinformation(
                post.content,
                context=f"Platform: {post.platform.value}, Author: {post.author_username}"
            )
            
            if misinformation_result:
                results[post.id] = misinformation_result
        
        # Analyze coordination if we have coordination events
        if self.coordination_results:
            coordination_posts = []
            coordination_accounts = []
            
            for event in self.coordination_results[:5]:  # Limit to 5 events
                account_ids = event.get("account_ids", [])[:10]  # Limit accounts
                
                for account_id in account_ids:
                    if account_id in self.accounts:
                        coordination_accounts.append({
                            "username": self.accounts[account_id].username,
                            "followers": self.accounts[account_id].followers,
                            "posts_count": len(self.posts_by_account.get(account_id, [])),
                            "created_at": self.accounts[account_id].created_at.isoformat() if self.accounts[account_id].created_at else None
                        })
                    
                    # Get posts from this account
                    posts_from_account = self.posts_by_account.get(account_id, [])
                    for post in posts_from_account[:5]:  # Limit posts per account
                        coordination_posts.append({
                            "author": post.author_username,
                            "content": post.content[:500],
                            "timestamp": post.timestamp.isoformat()
                        })
            
            if coordination_posts and coordination_accounts:
                coordination_analysis = await self.perplexity_client.analyze_coordination(
                    coordination_posts,
                    coordination_accounts
                )
                
                if coordination_analysis:
                    results["coordination_analysis"] = coordination_analysis
        
        return results
    
    def _flag_suspicious_accounts(self) -> None:
        """Flag accounts based on detection results."""
        self.flagged_accounts.clear()
        
        # Flag high-probability bots
        for account_id, result in self.bot_results.items():
            bot_prob = result.get("bot_probability", 0.0)
            if bot_prob > 0.7:  # Threshold for flagging
                self.flagged_accounts.add(account_id)
                if account_id in self.accounts:
                    self.accounts[account_id].flagged = True
                    self.accounts[account_id].flag_reasons = result.get("reasons", [])
        
        # Flag accounts in coordination events
        for event in self.coordination_results:
            account_ids = event.get("account_ids", [])
            coordination_score = event.get("coordination_score", 0.0)
            
            if coordination_score > 0.7:  # High coordination score
                for account_id in account_ids:
                    self.flagged_accounts.add(account_id)
                    if account_id in self.accounts:
                        self.accounts[account_id].flagged = True
                        if "coordinated_activity" not in self.accounts[account_id].flag_reasons:
                            self.accounts[account_id].flag_reasons.append("coordinated_activity")
        
        log.info(f"Flagged {len(self.flagged_accounts)} suspicious accounts")
    
    def get_flagged_accounts(self) -> List[Account]:
        """Get list of flagged accounts."""
        return [
            self.accounts[account_id]
            for account_id in self.flagged_accounts
            if account_id in self.accounts
        ]
    
    def get_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report of findings."""
        return {
            "analysis_results": self.analyze_posts(),
            "graph_statistics": self.social_graph.get_statistics(),
            "flagged_accounts": [
                account.dict() for account in self.get_flagged_accounts()
            ],
            "coordination_campaigns": self.coordination_results,
            "timestamp": datetime.now().isoformat()
        }

