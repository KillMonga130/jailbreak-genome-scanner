"""Bot detection based on behavioral patterns."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
from src.utils.logger import log
from src.models.post import Post, Account
from src.config import settings


class BotDetector:
    """Detects bot accounts based on behavioral patterns."""
    
    def __init__(
        self,
        min_similarity_score: Optional[float] = None,
        activity_threshold: Optional[float] = None,
        content_similarity_threshold: float = 0.85
    ):
        """
        Initialize bot detector.
        
        Args:
            min_similarity_score: Minimum similarity score to flag (defaults to config)
            activity_threshold: Posts per day threshold (defaults to config)
            content_similarity_threshold: Content similarity threshold for flagging
        """
        self.min_similarity_score = (
            min_similarity_score or settings.min_bot_similarity_score
        )
        self.activity_threshold = activity_threshold or 50.0  # posts per day
        self.content_similarity_threshold = content_similarity_threshold
    
    def detect_bot(
        self,
        account: Account,
        posts: List[Post]
    ) -> Dict[str, Any]:
        """
        Analyze an account and posts to determine bot probability.
        
        Args:
            account: Account to analyze
            posts: Posts from this account
            
        Returns:
            Detection result with bot probability and reasons
        """
        if not posts:
            return {
                "bot_probability": 0.0,
                "suspicious_score": 0.0,
                "flags": [],
                "reasons": []
            }
        
        flags = []
        reasons = []
        suspicious_score = 0.0
        
        # 1. Activity pattern analysis
        activity_score = self._analyze_activity_pattern(posts)
        if activity_score > 0.7:
            flags.append("HIGH_ACTIVITY")
            reasons.append(f"Unusually high posting rate: {activity_score:.2f}")
            suspicious_score += 0.2
        
        # 2. Content similarity analysis
        content_similarity_score = self._analyze_content_similarity(posts)
        if content_similarity_score > self.content_similarity_threshold:
            flags.append("SIMILAR_CONTENT")
            reasons.append(
                f"Very similar content across posts: {content_similarity_score:.2f}"
            )
            suspicious_score += 0.25
        
        # 3. Timing pattern analysis
        timing_score = self._analyze_timing_pattern(posts)
        if timing_score > 0.6:
            flags.append("REGULAR_TIMING")
            reasons.append(f"Highly regular posting intervals: {timing_score:.2f}")
            suspicious_score += 0.15
        
        # 4. Account age and activity correlation
        age_score = self._analyze_account_age_activity(account, posts)
        if age_score > 0.7:
            flags.append("SUSPICIOUS_AGE_ACTIVITY")
            reasons.append("New account with very high activity")
            suspicious_score += 0.2
        
        # 5. Engagement metrics analysis
        engagement_score = self._analyze_engagement_pattern(posts)
        if engagement_score < 0.1:
            flags.append("LOW_ENGAGEMENT")
            reasons.append("Posts get very little engagement relative to posting frequency")
            suspicious_score += 0.15
        
        # 6. Content diversity
        diversity_score = self._analyze_content_diversity(posts)
        if diversity_score < 0.3:
            flags.append("LOW_DIVERSITY")
            reasons.append("Low content diversity, repetitive patterns")
            suspicious_score += 0.1
        
        # Calculate final bot probability (weighted combination)
        bot_probability = min(1.0, suspicious_score * 1.2)  # Slight boost
        
        # Additional heuristics
        if len(flags) >= 4:
            bot_probability = min(1.0, bot_probability + 0.2)
        
        return {
            "bot_probability": round(bot_probability, 3),
            "suspicious_score": round(suspicious_score, 3),
            "flags": flags,
            "reasons": reasons,
            "metrics": {
                "activity_score": activity_score,
                "content_similarity": content_similarity_score,
                "timing_score": timing_score,
                "age_score": age_score,
                "engagement_score": engagement_score,
                "diversity_score": diversity_score
            }
        }
    
    def _analyze_activity_pattern(self, posts: List[Post]) -> float:
        """Analyze posting frequency pattern."""
        if len(posts) < 2:
            return 0.0
        
        # Sort posts by timestamp
        sorted_posts = sorted(posts, key=lambda p: p.timestamp)
        
        # Calculate time span
        time_span = (sorted_posts[-1].timestamp - sorted_posts[0].timestamp).total_seconds()
        if time_span == 0:
            return 1.0  # All posts at same time = suspicious
        
        # Posts per day
        days = time_span / (24 * 3600)
        posts_per_day = len(posts) / days if days > 0 else len(posts)
        
        # Normalize to 0-1 score (50 posts/day = 0.7, 100+ = 1.0)
        if posts_per_day >= 100:
            return 1.0
        elif posts_per_day >= 50:
            return 0.7 + 0.3 * ((posts_per_day - 50) / 50)
        elif posts_per_day >= 20:
            return 0.5 + 0.2 * ((posts_per_day - 20) / 30)
        else:
            return posts_per_day / 20
    
    def _analyze_content_similarity(self, posts: List[Post]) -> float:
        """Analyze similarity of content across posts."""
        if len(posts) < 2:
            return 0.0
        
        # Simple word-based similarity (would use vector embeddings in practice)
        similarities = []
        post_texts = [post.content.lower() for post in posts]
        
        for i in range(len(post_texts)):
            for j in range(i + 1, len(post_texts)):
                similarity = self._text_similarity(post_texts[i], post_texts[j])
                similarities.append(similarity)
        
        if not similarities:
            return 0.0
        
        return statistics.mean(similarities)
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate word overlap similarity."""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _analyze_timing_pattern(self, posts: List[Post]) -> float:
        """Analyze regularity of posting intervals."""
        if len(posts) < 3:
            return 0.0
        
        sorted_posts = sorted(posts, key=lambda p: p.timestamp)
        intervals = []
        
        for i in range(1, len(sorted_posts)):
            interval = (
                sorted_posts[i].timestamp - sorted_posts[i-1].timestamp
            ).total_seconds()
            intervals.append(interval)
        
        if not intervals:
            return 0.0
        
        # Calculate coefficient of variation (regular intervals = low CV)
        mean_interval = statistics.mean(intervals)
        if mean_interval == 0:
            return 1.0
        
        try:
            stdev = statistics.stdev(intervals)
            cv = stdev / mean_interval
            
            # Low CV = regular = suspicious
            # CV < 0.5 = highly regular (score 1.0)
            # CV > 2.0 = irregular (score 0.0)
            if cv < 0.5:
                return 1.0
            elif cv > 2.0:
                return 0.0
            else:
                return 1.0 - (cv - 0.5) / 1.5
        except statistics.StatisticsError:
            return 0.0
    
    def _analyze_account_age_activity(
        self,
        account: Account,
        posts: List[Post]
    ) -> float:
        """Analyze correlation between account age and activity."""
        if not account.created_at or not posts:
            return 0.0
        
        account_age_days = (datetime.now() - account.created_at).days
        if account_age_days == 0:
            account_age_days = 1  # Avoid division by zero
        
        posts_per_day = len(posts) / account_age_days
        
        # New account (< 30 days) with high activity is suspicious
        if account_age_days < 30 and posts_per_day > 20:
            return 1.0
        elif account_age_days < 90 and posts_per_day > 10:
            return 0.7
        else:
            return 0.0
    
    def _analyze_engagement_pattern(self, posts: List[Post]) -> float:
        """Analyze engagement relative to posting frequency."""
        if not posts:
            return 0.0
        
        total_engagement = sum(
            p.likes + p.retweets_shares + p.replies for p in posts
        )
        avg_engagement_per_post = total_engagement / len(posts)
        
        # Normalize: 0.1 = low engagement, 1.0 = high engagement
        # Posts with < 5 avg engagement = low (score 0.0-0.1)
        # Posts with > 50 avg engagement = high (score 0.8-1.0)
        if avg_engagement_per_post >= 50:
            return 1.0
        elif avg_engagement_per_post >= 20:
            return 0.7
        elif avg_engagement_per_post >= 10:
            return 0.5
        elif avg_engagement_per_post >= 5:
            return 0.2
        else:
            return 0.05
    
    def _analyze_content_diversity(self, posts: List[Post]) -> float:
        """Analyze diversity of content topics and language."""
        if len(posts) < 2:
            return 1.0
        
        # Calculate unique words vs total words
        all_words = set()
        total_words = 0
        
        for post in posts:
            words = set(post.content.lower().split())
            all_words.update(words)
            total_words += len(words.split()) if post.content else 0
        
        if total_words == 0:
            return 0.0
        
        # Diversity ratio: unique words / total words
        diversity = len(all_words) / total_words if total_words > 0 else 0.0
        
        # Normalize to 0-1 (0.5+ is good diversity)
        return min(1.0, diversity * 2)
    
    def batch_detect(self, accounts_with_posts: Dict[str, List[Post]]) -> Dict[str, Dict[str, Any]]:
        """
        Batch detect bots for multiple accounts.
        
        Args:
            accounts_with_posts: Dictionary mapping account_id to list of posts
            
        Returns:
            Dictionary mapping account_id to detection results
        """
        results = {}
        
        for account_id, posts in accounts_with_posts.items():
            # Create minimal account object for analysis
            if posts:
                first_post = posts[0]
                account = Account(
                    id=account_id,
                    username=first_post.author_username,
                    platform=first_post.platform
                )
                results[account_id] = self.detect_bot(account, posts)
            else:
                results[account_id] = {
                    "bot_probability": 0.0,
                    "suspicious_score": 0.0,
                    "flags": [],
                    "reasons": []
                }
        
        log.info(f"Batch detection completed for {len(results)} accounts")
        return results

