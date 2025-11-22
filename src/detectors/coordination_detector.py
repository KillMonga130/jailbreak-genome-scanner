"""Detect coordinated campaigns and synchronized posting behavior."""

from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict
from src.utils.logger import log
from src.models.post import Post
from src.config import settings
from src.vector_db.vector_store import VectorStore


class CoordinationDetector:
    """Detects coordinated posting behavior and campaigns."""
    
    def __init__(
        self,
        time_window_minutes: Optional[int] = None,
        min_accounts: Optional[int] = None,
        similarity_threshold: float = 0.8
    ):
        """
        Initialize coordination detector.
        
        Args:
            time_window_minutes: Time window for coordination (defaults to config)
            min_accounts: Minimum accounts for coordination flag (defaults to config)
            similarity_threshold: Content similarity threshold
        """
        self.time_window_minutes = (
            time_window_minutes or settings.coordination_time_window_minutes
        )
        self.min_accounts = min_accounts or settings.min_coordination_threshold
        self.similarity_threshold = similarity_threshold
    
    def detect_coordination(
        self,
        posts: List[Post],
        vector_store: Optional[VectorStore] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect coordinated posting patterns.
        
        Args:
            posts: Posts to analyze
            vector_store: Optional vector store for similarity search
            
        Returns:
            List of detected coordination events
        """
        if len(posts) < self.min_accounts:
            return []
        
        coordination_events = []
        time_window = timedelta(minutes=self.time_window_minutes)
        
        # Group posts by time windows
        time_buckets = self._bucket_by_time(posts, time_window)
        
        # Analyze each time bucket
        for bucket_start, bucket_posts in time_buckets.items():
            if len(bucket_posts) < self.min_accounts:
                continue
            
            # Get unique accounts in this bucket
            accounts_in_bucket = set(post.author_id for post in bucket_posts)
            
            if len(accounts_in_bucket) >= self.min_accounts:
                # Analyze for content similarity and coordination patterns
                coordination = self._analyze_bucket_coordination(
                    bucket_posts,
                    vector_store
                )
                
                if coordination:
                    coordination_events.append({
                        "timestamp": bucket_start,
                        "time_window_minutes": self.time_window_minutes,
                        "account_ids": list(accounts_in_bucket),
                        "account_count": len(accounts_in_bucket),
                        "post_count": len(bucket_posts),
                        **coordination
                    })
        
        # Cross-bucket analysis: detect sustained campaigns
        sustained_campaigns = self._detect_sustained_campaigns(
            coordination_events,
            posts
        )
        
        coordination_events.extend(sustained_campaigns)
        
        log.info(f"Detected {len(coordination_events)} coordination events")
        return coordination_events
    
    def _bucket_by_time(
        self,
        posts: List[Post],
        time_window: timedelta
    ) -> Dict[datetime, List[Post]]:
        """Group posts into time buckets."""
        buckets = defaultdict(list)
        
        for post in posts:
            # Round to nearest time window
            bucket_time = post.timestamp.replace(
                minute=(post.timestamp.minute // self.time_window_minutes) * self.time_window_minutes,
                second=0,
                microsecond=0
            )
            buckets[bucket_time].append(post)
        
        return dict(buckets)
    
    def _analyze_bucket_coordination(
        self,
        posts: List[Post],
        vector_store: Optional[VectorStore]
    ) -> Optional[Dict[str, Any]]:
        """Analyze posts in a time bucket for coordination patterns."""
        if not posts:
            return None
        
        # Group posts by similar content
        content_groups = self._group_similar_content(posts, vector_store)
        
        if not content_groups:
            return None
        
        # Find largest group
        largest_group = max(content_groups, key=len)
        
        if len(largest_group) < self.min_accounts:
            return None
        
        # Calculate coordination metrics
        unique_accounts = set(post.author_id for post in largest_group)
        
        if len(unique_accounts) < self.min_accounts:
            return None
        
        # Timing analysis
        timing_score = self._analyze_timing_clustering(largest_group)
        
        # Content similarity
        avg_similarity = self._calculate_avg_similarity(largest_group)
        
        # URL/hashtag overlap
        url_overlap = self._analyze_url_overlap(largest_group)
        hashtag_overlap = self._analyze_hashtag_overlap(largest_group)
        
        coordination_score = (
            (timing_score * 0.3) +
            (avg_similarity * 0.3) +
            (url_overlap * 0.2) +
            (hashtag_overlap * 0.2)
        )
        
        return {
            "coordination_score": round(coordination_score, 3),
            "timing_score": round(timing_score, 3),
            "content_similarity": round(avg_similarity, 3),
            "url_overlap": round(url_overlap, 3),
            "hashtag_overlap": round(hashtag_overlap, 3),
            "coordinated_posts": [p.id for p in largest_group],
            "pattern_type": self._classify_pattern(largest_group)
        }
    
    def _group_similar_content(
        self,
        posts: List[Post],
        vector_store: Optional[VectorStore]
    ) -> List[List[Post]]:
        """Group posts by content similarity."""
        if vector_store:
            # Use vector similarity
            groups = []
            processed = set()
            
            for post in posts:
                if post.id in processed:
                    continue
                
                # Find similar posts using vector store
                similar = vector_store.find_similar_posts(
                    post,
                    n_results=50,
                    threshold=self.similarity_threshold
                )
                
                group = [post]
                processed.add(post.id)
                
                # Match similar post IDs with actual posts
                similar_ids = {s["id"] for s in similar}
                for other_post in posts:
                    if other_post.id in similar_ids and other_post.id not in processed:
                        group.append(other_post)
                        processed.add(other_post.id)
                
                if len(group) > 1:
                    groups.append(group)
        else:
            # Fallback to simple text similarity
            groups = []
            processed = set()
            
            for i, post1 in enumerate(posts):
                if post1.id in processed:
                    continue
                
                group = [post1]
                processed.add(post1.id)
                
                for post2 in posts[i+1:]:
                    if post2.id in processed:
                        continue
                    
                    similarity = self._text_similarity(post1.content, post2.content)
                    if similarity >= self.similarity_threshold:
                        group.append(post2)
                        processed.add(post2.id)
                
                if len(group) > 1:
                    groups.append(group)
        
        return groups
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _analyze_timing_clustering(self, posts: List[Post]) -> float:
        """Analyze how clustered the post timings are."""
        if len(posts) < 2:
            return 0.0
        
        sorted_timestamps = sorted([p.timestamp for p in posts])
        
        # Calculate time span
        total_span = (sorted_timestamps[-1] - sorted_timestamps[0]).total_seconds()
        if total_span == 0:
            return 1.0  # All at same time = perfect clustering
        
        # Calculate average gap between consecutive posts
        gaps = [
            (sorted_timestamps[i] - sorted_timestamps[i-1]).total_seconds()
            for i in range(1, len(sorted_timestamps))
        ]
        
        if not gaps:
            return 0.0
        
        avg_gap = sum(gaps) / len(gaps)
        
        # Score: smaller gaps relative to total span = higher clustering
        if total_span < 60:  # Within 1 minute
            return 1.0
        elif total_span < 300:  # Within 5 minutes
            return 0.8
        elif total_span < 600:  # Within 10 minutes
            return 0.6
        else:
            return max(0.0, 0.5 - (total_span / 3600) * 0.1)
    
    def _calculate_avg_similarity(self, posts: List[Post]) -> float:
        """Calculate average pairwise similarity of posts."""
        if len(posts) < 2:
            return 1.0
        
        similarities = []
        for i in range(len(posts)):
            for j in range(i + 1, len(posts)):
                sim = self._text_similarity(posts[i].content, posts[j].content)
                similarities.append(sim)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def _analyze_url_overlap(self, posts: List[Post]) -> float:
        """Analyze overlap in URLs shared."""
        all_urls = [url for post in posts for url in post.links]
        
        if not all_urls:
            return 0.0
        
        unique_urls = set(all_urls)
        
        # High overlap = many posts share same URLs
        # Score based on URL repetition
        url_counts = defaultdict(int)
        for url in all_urls:
            url_counts[url] += 1
        
        repeated_urls = sum(1 for count in url_counts.values() if count > 1)
        
        return min(1.0, repeated_urls / len(unique_urls) * 2)
    
    def _analyze_hashtag_overlap(self, posts: List[Post]) -> float:
        """Analyze overlap in hashtags used."""
        all_hashtags = [tag for post in posts for tag in post.hashtags]
        
        if not all_hashtags:
            return 0.0
        
        unique_hashtags = set(all_hashtags)
        
        hashtag_counts = defaultdict(int)
        for tag in all_hashtags:
            hashtag_counts[tag.lower()] += 1
        
        repeated_hashtags = sum(1 for count in hashtag_counts.values() if count > 1)
        
        return min(1.0, repeated_hashtags / len(unique_hashtags) * 2) if unique_hashtags else 0.0
    
    def _classify_pattern(self, posts: List[Post]) -> str:
        """Classify the type of coordination pattern."""
        if not posts:
            return "unknown"
        
        # Check for exact duplicates
        contents = [p.content.lower().strip() for p in posts]
        if len(set(contents)) == 1:
            return "exact_duplicate"
        
        # Check for template-based (same structure, different keywords)
        if self._has_template_pattern(posts):
            return "template_based"
        
        # Check for URL amplification
        if len(set(p.links for p in posts if p.links)) == 1 and len([p for p in posts if p.links]) >= self.min_accounts:
            return "url_amplification"
        
        return "coordinated_content"
    
    def _has_template_pattern(self, posts: List[Post]) -> bool:
        """Check if posts follow a template pattern."""
        if len(posts) < 3:
            return False
        
        # Simple check: same structure with word substitutions
        word_counts = [len(p.content.split()) for p in posts]
        if len(set(word_counts)) <= 2:  # Similar length
            # Check if word positions are similar
            return True  # Simplified - would need more sophisticated analysis
        
        return False
    
    def _detect_sustained_campaigns(
        self,
        coordination_events: List[Dict[str, Any]],
        all_posts: List[Post]
    ) -> List[Dict[str, Any]]:
        """Detect campaigns that span multiple time windows."""
        if len(coordination_events) < 2:
            return []
        
        # Group events by overlapping account sets
        sustained_campaigns = []
        processed = set()
        
        for i, event1 in enumerate(coordination_events):
            if i in processed:
                continue
            
            campaign_accounts = set(event1["account_ids"])
            campaign_events = [event1]
            
            # Find related events
            for j, event2 in enumerate(coordination_events[i+1:], start=i+1):
                if j in processed:
                    continue
                
                overlap = len(campaign_accounts & set(event2["account_ids"]))
                if overlap >= self.min_accounts // 2:  # At least half accounts overlap
                    campaign_accounts.update(event2["account_ids"])
                    campaign_events.append(event2)
                    processed.add(j)
            
            if len(campaign_events) > 1:
                # This is a sustained campaign
                sustained_campaigns.append({
                    "type": "sustained_campaign",
                    "account_ids": list(campaign_accounts),
                    "account_count": len(campaign_accounts),
                    "event_count": len(campaign_events),
                    "duration_hours": (
                        max(e["timestamp"] for e in campaign_events) -
                        min(e["timestamp"] for e in campaign_events)
                    ).total_seconds() / 3600,
                    "events": campaign_events,
                    "campaign_score": min(1.0, len(campaign_events) / 5.0)
                })
                processed.add(i)
        
        return sustained_campaigns

