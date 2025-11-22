"""Generate 3D vector space visualizations for jailbreak evaluation results."""

import json
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from src.models.jailbreak import EvaluationResult, AttackStrategy
from src.vector_db.embedder import Embedder
from src.utils.logger import log

try:
    import umap
    UMAP_AVAILABLE = True
except ImportError:
    UMAP_AVAILABLE = False
    log.warning("UMAP not available, using t-SNE for dimensionality reduction")


class Vector3DGenerator:
    """Generate 3D coordinates for evaluation results using dimensionality reduction."""
    
    # Color palette for 10+ attack strategies
    STRATEGY_COLORS = [
        "#4C78A8",  # Blue - ROLEPLAY
        "#F58518",  # Orange - EMOTIONAL_COERCION
        "#E45756",  # Red - TRANSLATION_ATTACK
        "#72B7B2",  # Teal - PROMPT_INVERSION
        "#54A24B",  # Green - CHAIN_OF_COMMAND
        "#EECA3B",  # Yellow - FICTIONAL_FRAMING
        "#B279A2",  # Purple - MULTI_TURN_ESCALATION
        "#FF9DA6",  # Pink - INDIRECT_REQUEST
        "#9D755D",  # Brown - POLICY_PROBING
        "#BAB0AC",  # Gray - HONEYPOT
        "#7FC97F",  # Light Green - PERMISSION_EXPLOITATION
    ]
    
    # Strategy to index mapping
    STRATEGY_MAP = {
        AttackStrategy.ROLEPLAY: 0,
        AttackStrategy.EMOTIONAL_COERCION: 1,
        AttackStrategy.TRANSLATION_ATTACK: 2,
        AttackStrategy.PROMPT_INVERSION: 3,
        AttackStrategy.CHAIN_OF_COMMAND: 4,
        AttackStrategy.FICTIONAL_FRAMING: 5,
        AttackStrategy.MULTI_TURN_ESCALATION: 6,
        AttackStrategy.INDIRECT_REQUEST: 7,
        AttackStrategy.POLICY_PROBING: 8,
        AttackStrategy.HONEYPOT: 9,
        AttackStrategy.PERMISSION_EXPLOITATION: 10,
    }
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2", method: str = "tsne"):
        """
        Initialize the 3D vector generator.
        
        Args:
            embedding_model: Sentence transformer model for embeddings
            method: Dimensionality reduction method ("tsne", "umap", or "pca")
        """
        self.embedder = Embedder(model_name=embedding_model)
        self.method = method.lower()
        
        if self.method == "umap" and not UMAP_AVAILABLE:
            log.warning("UMAP not available, falling back to t-SNE")
            self.method = "tsne"
        
        log.info(f"Initialized 3D vector generator (method: {self.method})")
    
    def get_strategy_color(self, strategy: AttackStrategy) -> str:
        """Get color for an attack strategy."""
        idx = self.STRATEGY_MAP.get(strategy, 0) % len(self.STRATEGY_COLORS)
        return self.STRATEGY_COLORS[idx]
    
    def get_strategy_name(self, strategy: AttackStrategy) -> str:
        """Get display name for an attack strategy."""
        names = {
            AttackStrategy.ROLEPLAY: "Roleplay",
            AttackStrategy.EMOTIONAL_COERCION: "Emotional Coercion",
            AttackStrategy.TRANSLATION_ATTACK: "Translation Attack",
            AttackStrategy.PROMPT_INVERSION: "Prompt Inversion",
            AttackStrategy.CHAIN_OF_COMMAND: "Chain of Command",
            AttackStrategy.FICTIONAL_FRAMING: "Fictional Framing",
            AttackStrategy.MULTI_TURN_ESCALATION: "Multi-Turn Escalation",
            AttackStrategy.INDIRECT_REQUEST: "Indirect Request",
            AttackStrategy.POLICY_PROBING: "Policy Probing",
            AttackStrategy.HONEYPOT: "Honeypot",
            AttackStrategy.PERMISSION_EXPLOITATION: "Permission Exploitation",
        }
        return names.get(strategy, strategy.value.replace("_", " ").title())
    
    def generate_embeddings(self, evaluations: List[EvaluationResult]) -> np.ndarray:
        """
        Generate embeddings for evaluation results.
        
        Args:
            evaluations: List of evaluation results
            
        Returns:
            Array of embeddings (n_samples, embedding_dim)
        """
        texts = []
        for eval_result in evaluations:
            # Combine prompt and response for richer embedding
            text = f"{eval_result.prompt} {eval_result.response}"
            texts.append(text)
        
        log.info(f"Generating embeddings for {len(texts)} evaluations...")
        embeddings = self.embedder.embed_texts(texts)
        
        return np.array(embeddings)
    
    def reduce_to_3d(self, embeddings: np.ndarray, perplexity: int = 30) -> np.ndarray:
        """
        Reduce embeddings to 3D using dimensionality reduction.
        
        Args:
            embeddings: High-dimensional embeddings
            perplexity: Perplexity for t-SNE (higher for more data points)
            
        Returns:
            3D coordinates (n_samples, 3)
        """
        n_samples = embeddings.shape[0]
        
        # Adjust perplexity based on sample size
        max_perplexity = min(n_samples - 1, perplexity)
        if max_perplexity < 5:
            max_perplexity = min(n_samples - 1, 5)
        
        log.info(f"Reducing {embeddings.shape[1]}-D embeddings to 3D using {self.method}...")
        
        if self.method == "umap":
            reducer = umap.UMAP(n_components=3, n_neighbors=min(15, n_samples - 1), random_state=42)
            coords_3d = reducer.fit_transform(embeddings)
        elif self.method == "pca":
            reducer = PCA(n_components=3, random_state=42)
            coords_3d = reducer.fit_transform(embeddings)
        else:  # t-SNE
            # Use max_iter (correct parameter name in scikit-learn)
            reducer = TSNE(
                n_components=3,
                perplexity=max_perplexity,
                random_state=42,
                max_iter=1000,
                init='pca'
            )
            coords_3d = reducer.fit_transform(embeddings)
        
        log.info(f"3D reduction complete. Shape: {coords_3d.shape}")
        return coords_3d
    
    def generate_3d_data(
        self,
        evaluations: List[EvaluationResult],
        output_path: Optional[Path] = None,
        normalize: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Generate 3D visualization data from evaluation results.
        
        Args:
            evaluations: List of evaluation results
            output_path: Optional path to save JSON file
            normalize: Whether to normalize coordinates to [0, 100]
            
        Returns:
            List of data points for 3D visualization
        """
        if not evaluations:
            log.warning("No evaluations provided")
            return []
        
        log.info(f"Generating 3D visualization data for {len(evaluations)} evaluations...")
        
        # Generate embeddings
        embeddings = self.generate_embeddings(evaluations)
        
        # Reduce to 3D
        coords_3d = self.reduce_to_3d(embeddings)
        
        # Normalize if requested
        if normalize:
            # Normalize to [0, 100] range
            for i in range(3):
                min_val = coords_3d[:, i].min()
                max_val = coords_3d[:, i].max()
                if max_val > min_val:
                    coords_3d[:, i] = (coords_3d[:, i] - min_val) / (max_val - min_val) * 100
                else:
                    coords_3d[:, i] = 50  # Center if no variation
        
        # Create data points
        data_points = []
        for i, eval_result in enumerate(evaluations):
            # Handle both Pydantic models and dicts
            if isinstance(eval_result, dict):
                strategy = AttackStrategy(eval_result.get('attack_strategy', {}).get('value', 'roleplay'))
                is_jailbroken = eval_result.get('is_jailbroken', False)
                severity = eval_result.get('severity', {}).get('value', 0) if isinstance(eval_result.get('severity'), dict) else eval_result.get('severity', 0)
                prompt = eval_result.get('prompt', '')
                response = eval_result.get('response', '')
                eval_id = eval_result.get('id', f'eval_{i}')
            else:
                strategy = eval_result.attack_strategy
                is_jailbroken = eval_result.is_jailbroken
                severity = eval_result.severity.value if hasattr(eval_result.severity, 'value') else eval_result.severity
                prompt = eval_result.prompt
                response = eval_result.response
                eval_id = eval_result.id
            
            point = {
                "x": float(coords_3d[i, 0]),
                "y": float(coords_3d[i, 1]),
                "z": float(coords_3d[i, 2]),
                "id": eval_id,
                "strategy": strategy.value,
                "strategy_name": self.get_strategy_name(strategy),
                "strategy_index": self.STRATEGY_MAP.get(strategy, 0),
                "color": self.get_strategy_color(strategy),
                "is_jailbroken": bool(is_jailbroken),
                "severity": int(severity),
                "prompt": str(prompt)[:200],  # Truncate for display
                "response": str(response)[:200],  # Truncate for display
                "status": "JAILBROKEN" if is_jailbroken else "BLOCKED"
            }
            data_points.append(point)
        
        log.info(f"Generated {len(data_points)} 3D data points")
        
        # Save to file if requested
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(data_points, f, indent=2)
            log.info(f"Saved 3D visualization data to {output_path}")
        
        return data_points

