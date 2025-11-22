"""Text embedding generation for vector similarity search."""

from typing import List, Optional
from sentence_transformers import SentenceTransformer
from src.utils.logger import log
from src.models.post import Post


class Embedder:
    """Generates embeddings for text content using sentence transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedder.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        log.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        log.info(f"Embedding dimension: {self.embedding_dim}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        if not text or not text.strip():
            return [0.0] * self.embedding_dim
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batched).
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Filter empty texts
        non_empty_texts = [text if text and text.strip() else " " for text in texts]
        
        embeddings = self.model.encode(
            non_empty_texts,
            convert_to_numpy=True,
            show_progress_bar=False,
            batch_size=32
        )
        
        return embeddings.tolist()
    
    def embed_post(self, post: Post) -> List[float]:
        """
        Generate embedding for a Post object.
        
        Args:
            post: Post object to embed
            
        Returns:
            Embedding vector
        """
        # Combine content with metadata for richer embedding
        text = post.content
        
        # Optionally include hashtags and mentions for context
        if post.hashtags:
            text += " " + " ".join(post.hashtags)
        
        return self.embed_text(text)
    
    def embed_posts(self, posts: List[Post]) -> List[List[float]]:
        """
        Generate embeddings for multiple posts.
        
        Args:
            posts: List of Post objects
            
        Returns:
            List of embedding vectors
        """
        texts = []
        for post in posts:
            text = post.content
            if post.hashtags:
                text += " " + " ".join(post.hashtags)
            texts.append(text)
        
        return self.embed_texts(texts)

