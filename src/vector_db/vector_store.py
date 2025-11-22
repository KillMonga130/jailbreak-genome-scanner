"""Vector database integration using ChromaDB."""

from typing import List, Optional, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from src.config import settings
from src.utils.logger import log
from src.models.post import Post
from src.vector_db.embedder import Embedder


class VectorStore:
    """Manages vector storage and similarity search using ChromaDB."""
    
    def __init__(self, collection_name: Optional[str] = None):
        """
        Initialize the vector store.
        
        Args:
            collection_name: Name of the collection to use/create
        """
        self.collection_name = collection_name or settings.chroma_collection_name
        self.embedder = Embedder()
        
        # Initialize ChromaDB client
        log.info(f"Initializing ChromaDB client (host: {settings.chroma_host}, port: {settings.chroma_port})")
        
        try:
            # Try to connect to remote ChromaDB first
            if settings.chroma_host != "localhost":
                self.client = chromadb.HttpClient(
                    host=settings.chroma_host,
                    port=settings.chroma_port
                )
                log.info("Connected to remote ChromaDB instance")
            else:
                # Use local persistent ChromaDB
                persist_directory = str(settings.data_dir / "chroma_db")
                self.client = chromadb.PersistentClient(
                    path=persist_directory,
                    settings=ChromaSettings(anonymized_telemetry=False)
                )
                log.info(f"Using local ChromaDB at {persist_directory}")
        except Exception as e:
            log.warning(f"Failed to initialize ChromaDB client: {e}. Using in-memory client.")
            self.client = chromadb.Client()
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
        log.info(f"Using collection: {self.collection_name}")
    
    def _get_or_create_collection(self) -> chromadb.Collection:
        """Get existing collection or create a new one."""
        try:
            collection = self.client.get_collection(name=self.collection_name)
            log.info(f"Retrieved existing collection: {self.collection_name}")
            return collection
        except Exception:
            log.info(f"Creating new collection: {self.collection_name}")
            return self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Social media post embeddings"}
            )
    
    def add_post(self, post: Post) -> None:
        """
        Add a post and its embedding to the vector store.
        
        Args:
            post: Post object to add
        """
        if post.embedding is None:
            post.embedding = self.embedder.embed_post(post)
        
        self.collection.add(
            ids=[post.id],
            embeddings=[post.embedding],
            documents=[post.content],
            metadatas=[{
                "platform": post.platform.value,
                "author_id": post.author_id,
                "author_username": post.author_username,
                "timestamp": post.timestamp.isoformat(),
                "url": post.url or "",
                "hashtags": ",".join(post.hashtags),
                "bot_probability": str(post.bot_probability) if post.bot_probability else "",
                "suspicious_score": str(post.suspicious_score) if post.suspicious_score else "",
            }]
        )
        log.debug(f"Added post {post.id} to vector store")
    
    def add_posts(self, posts: List[Post]) -> None:
        """
        Batch add multiple posts to the vector store.
        
        Args:
            posts: List of Post objects
        """
        if not posts:
            return
        
        # Generate embeddings for posts that don't have them
        posts_to_embed = [p for p in posts if p.embedding is None]
        if posts_to_embed:
            embeddings = self.embedder.embed_posts(posts_to_embed)
            for post, embedding in zip(posts_to_embed, embeddings):
                post.embedding = embedding
        
        # Prepare data for batch insert
        ids = [post.id for post in posts]
        embeddings = [post.embedding for post in posts]
        documents = [post.content for post in posts]
        metadatas = [{
            "platform": post.platform.value,
            "author_id": post.author_id,
            "author_username": post.author_username,
            "timestamp": post.timestamp.isoformat(),
            "url": post.url or "",
            "hashtags": ",".join(post.hashtags),
            "bot_probability": str(post.bot_probability) if post.bot_probability else "",
            "suspicious_score": str(post.suspicious_score) if post.suspicious_score else "",
        } for post in posts]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        log.info(f"Added {len(posts)} posts to vector store")
    
    def find_similar(
        self,
        query_text: str,
        n_results: int = 10,
        threshold: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find similar posts to a query text.
        
        Args:
            query_text: Text to search for
            n_results: Number of similar posts to return
            threshold: Minimum similarity score (0-1)
            filters: Metadata filters to apply
            
        Returns:
            List of similar posts with metadata
        """
        query_embedding = self.embedder.embed_text(query_text)
        
        where_clause = filters if filters else None
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_clause
        )
        
        # Format results
        similar_posts = []
        if results["ids"] and results["ids"][0]:
            for i, post_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i] if results["distances"] else None
                similarity = 1 - distance if distance is not None else None
                
                # Apply threshold filter if specified
                if threshold is not None and similarity is not None and similarity < threshold:
                    continue
                
                similar_posts.append({
                    "id": post_id,
                    "content": results["documents"][0][i] if results["documents"] else "",
                    "similarity": similarity,
                    "distance": distance,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {}
                })
        
        log.debug(f"Found {len(similar_posts)} similar posts for query")
        return similar_posts
    
    def find_similar_posts(
        self,
        post: Post,
        n_results: int = 10,
        threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Find posts similar to a given post.
        
        Args:
            post: Post to find similar posts for
            n_results: Number of similar posts to return
            threshold: Minimum similarity score
            
        Returns:
            List of similar posts with metadata
        """
        return self.find_similar(
            query_text=post.content,
            n_results=n_results,
            threshold=threshold
        )
    
    def count(self) -> int:
        """Get the total number of posts in the vector store."""
        return self.collection.count()
    
    def delete_post(self, post_id: str) -> None:
        """Delete a post from the vector store."""
        self.collection.delete(ids=[post_id])
        log.debug(f"Deleted post {post_id} from vector store")

