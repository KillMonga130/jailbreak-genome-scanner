"""Social graph analysis for detecting coordinated behavior."""

from typing import Dict, List, Set, Tuple, Optional, Any
from datetime import datetime, timedelta
import networkx as nx
from collections import defaultdict
from src.utils.logger import log
from src.models.post import Post, Account
from src.models.post import Post, Account


class SocialGraph:
    """Builds and analyzes social graphs to detect coordinated behavior."""
    
    def __init__(self):
        """Initialize an empty social graph."""
        self.graph = nx.DiGraph()  # Directed graph for follower relationships
        self.posts_by_account: Dict[str, List[Post]] = defaultdict(list)
        self.accounts: Dict[str, Account] = {}
    
    def add_account(self, account: Account) -> None:
        """
        Add an account to the graph.
        
        Args:
            account: Account object to add
        """
        self.accounts[account.id] = account
        if account.id not in self.graph:
            self.graph.add_node(
                account.id,
                username=account.username,
                platform=account.platform.value,
                bot_probability=account.bot_probability or 0.0,
                suspicious_score=account.suspicious_score or 0.0,
                followers=account.followers,
                following=account.following
            )
        log.debug(f"Added account {account.id} ({account.username}) to graph")
    
    def add_connection(self, account_id1: str, account_id2: str) -> None:
        """
        Add a directed connection between two accounts.
        
        Args:
            account_id1: Source account ID
            account_id2: Target account ID (e.g., account1 follows account2)
        """
        if account_id1 not in self.graph:
            self.graph.add_node(account_id1)
        if account_id2 not in self.graph:
            self.graph.add_node(account_id2)
        
        self.graph.add_edge(account_id1, account_id2)
    
    def add_post(self, post: Post) -> None:
        """
        Add a post and associate it with an account.
        
        Args:
            post: Post object to add
        """
        self.posts_by_account[post.author_id].append(post)
        
        # Ensure author node exists
        if post.author_id not in self.graph:
            self.graph.add_node(
                post.author_id,
                username=post.author_username,
                platform=post.platform.value
            )
    
    def build_interaction_graph(self, posts: List[Post]) -> nx.DiGraph:
        """
        Build a graph based on interactions (mentions, replies, retweets).
        
        Args:
            posts: List of posts to analyze
            
        Returns:
            Directed graph of interactions
        """
        interaction_graph = nx.DiGraph()
        
        for post in posts:
            author_id = post.author_id
            
            # Add nodes
            interaction_graph.add_node(
                author_id,
                username=post.author_username,
                platform=post.platform.value
            )
            
            # Add edges based on mentions
            for mentioned_user in post.mentions:
                if mentioned_user in self.accounts:
                    mentioned_id = self.accounts[mentioned_user].id
                    if interaction_graph.has_edge(author_id, mentioned_id):
                        interaction_graph[author_id][mentioned_id]["weight"] += 1
                    else:
                        interaction_graph.add_edge(
                            author_id,
                            mentioned_id,
                            weight=1,
                            interaction_type="mention"
                        )
        
        return interaction_graph
    
    def find_communities(self, method: str = "louvain") -> Dict[str, int]:
        """
        Detect communities/clusters in the graph.
        
        Args:
            method: Community detection method ('louvain' or 'greedy_modularity')
            
        Returns:
            Dictionary mapping account_id to community_id
        """
        if self.graph.number_of_nodes() < 2:
            return {}
        
        # Convert to undirected for community detection
        undirected_graph = self.graph.to_undirected()
        
        try:
            if method == "louvain":
                import community.community_louvain as community_louvain
                communities = community_louvain.best_partition(undirected_graph)
            else:
                from networkx.algorithms import community
                communities_generator = community.greedy_modularity_communities(undirected_graph)
                communities = {}
                for i, comm in enumerate(communities_generator):
                    for node in comm:
                        communities[node] = i
        except ImportError:
            log.warning("python-louvain not installed, using simple greedy modularity")
            from networkx.algorithms import community
            communities_generator = community.greedy_modularity_communities(undirected_graph)
            communities = {}
            for i, comm in enumerate(communities_generator):
                for node in comm:
                    communities[node] = i
        
        log.info(f"Detected {len(set(communities.values()))} communities")
        return communities
    
    def detect_coordinated_posting(
        self,
        time_window_minutes: int = 60,
        min_accounts: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Detect coordinated posting patterns based on timing and content similarity.
        
        Args:
            time_window_minutes: Time window for considering posts as coordinated
            min_accounts: Minimum number of accounts for coordination flag
            
        Returns:
            List of detected coordination events
        """
        coordination_events = []
        time_window = timedelta(minutes=time_window_minutes)
        
        # Group posts by time windows
        time_buckets: Dict[datetime, List[Post]] = defaultdict(list)
        
        for account_id, posts in self.posts_by_account.items():
            for post in posts:
                # Round timestamp to nearest time window
                bucket_time = post.timestamp.replace(
                    minute=(post.timestamp.minute // time_window_minutes) * time_window_minutes,
                    second=0,
                    microsecond=0
                )
                time_buckets[bucket_time].append(post)
        
        # Analyze each time bucket
        for bucket_time, posts in time_buckets.items():
            if len(posts) < min_accounts:
                continue
            
            # Get unique accounts
            accounts_in_bucket = set(post.author_id for post in posts)
            if len(accounts_in_bucket) < min_accounts:
                continue
            
            # Check for similar content (basic check - would be enhanced with vector similarity)
            similar_content_groups = self._group_by_similarity(posts)
            
            for group_posts in similar_content_groups:
                if len(group_posts) >= min_accounts:
                    unique_accounts = set(p.post.author_id for p in group_posts)
                    if len(unique_accounts) >= min_accounts:
                        coordination_events.append({
                            "timestamp": bucket_time,
                            "account_ids": list(unique_accounts),
                            "post_count": len(group_posts),
                            "similarity_score": group_posts[0].similarity if group_posts else 0.0,
                            "posts": [p.post for p in group_posts]
                        })
        
        log.info(f"Detected {len(coordination_events)} potential coordination events")
        return coordination_events
    
    def _group_by_similarity(
        self,
        posts: List[Post],
        similarity_threshold: float = 0.7
    ) -> List[List[Tuple[Post, float]]]:
        """
        Group posts by content similarity (placeholder - would use vector similarity).
        
        Args:
            posts: Posts to group
            similarity_threshold: Minimum similarity for grouping
            
        Returns:
            Groups of similar posts with similarity scores
        """
        # This is a simplified version - in practice, would use vector similarity
        # For now, group by exact content matches and similar length
        groups: List[List[Tuple[Post, float]]] = []
        processed = set()
        
        for i, post1 in enumerate(posts):
            if post1.id in processed:
                continue
            
            group = [(post1, 1.0)]
            processed.add(post1.id)
            
            for j, post2 in enumerate(posts[i+1:], start=i+1):
                if post2.id in processed:
                    continue
                
                # Simple similarity check (would be replaced with vector similarity)
                similarity = self._text_similarity(post1.content, post2.content)
                if similarity >= similarity_threshold:
                    group.append((post2, similarity))
                    processed.add(post2.id)
            
            if len(group) > 1:
                groups.append(group)
        
        return groups
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple text similarity (placeholder for vector similarity).
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        # Simple word overlap similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def get_central_accounts(self, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Find most central accounts using PageRank.
        
        Args:
            top_k: Number of top accounts to return
            
        Returns:
            List of (account_id, pagerank_score) tuples
        """
        if self.graph.number_of_nodes() == 0:
            return []
        
        pagerank = nx.pagerank(self.graph)
        sorted_accounts = sorted(
            pagerank.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_accounts[:top_k]
    
    def get_statistics(self) -> Dict[str, any]:
        """Get graph statistics."""
        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "density": nx.density(self.graph),
            "average_clustering": nx.average_clustering(self.graph.to_undirected())
            if self.graph.number_of_nodes() > 0 else 0.0,
            "accounts": len(self.accounts),
            "total_posts": sum(len(posts) for posts in self.posts_by_account.values())
        }

