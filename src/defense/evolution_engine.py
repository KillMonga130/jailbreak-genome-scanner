"""Defense Evolution Engine - Evolves better defense configurations using genetic algorithms."""

import random
import copy
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from src.models.jailbreak import EvaluationResult, AttackStrategy, SeverityLevel
from src.utils.logger import log


@dataclass
class DefenseGenome:
    """Represents a defense configuration with fitness metrics."""
    
    id: str
    # Defense parameters
    filter_threshold: float = 0.75  # Similarity threshold for blocking
    min_confidence: float = 0.6  # Minimum confidence to block
    strict_mode: bool = False  # Strict filtering mode
    response_guard_enabled: bool = True
    adaptive_prompt_enabled: bool = True
    
    # Strategy-specific thresholds
    strategy_thresholds: Dict[str, float] = field(default_factory=dict)
    
    # Fitness metrics
    fitness_score: float = 0.0  # Higher = better defense
    jvi_score: float = 100.0  # Lower JVI = better (inverted for fitness)
    exploit_rate: float = 1.0  # Lower = better (inverted for fitness)
    blocked_count: int = 0
    total_attempts: int = 0
    
    generation: int = 0
    parent_ids: Optional[Tuple[str, str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_fitness(self) -> float:
        """
        Calculate fitness score.
        
        Fitness = 1 / (JVI_score + exploit_rate)
        Higher fitness = better defense
        """
        if self.total_attempts == 0:
            return 0.0
        
        # Normalize JVI (0-100) and exploit rate (0-1)
        normalized_jvi = self.jvi_score / 100.0
        normalized_exploit = self.exploit_rate
        
        # Fitness is inverse of vulnerability
        # Add small epsilon to avoid division by zero
        fitness = 1.0 / (normalized_jvi + normalized_exploit + 0.01)
        
        # Bonus for blocking effectiveness
        if self.total_attempts > 0:
            block_rate = self.blocked_count / self.total_attempts
            fitness *= (1.0 + block_rate * 0.5)  # Up to 50% bonus
        
        return min(fitness, 10.0)  # Cap at 10.0


class DefenseEvolutionEngine:
    """
    Evolves better defense configurations using genetic algorithms.
    
    Evolves:
    - Filter thresholds
    - Strategy-specific parameters
    - Defense layer configurations
    - Response guard settings
    """
    
    def __init__(
        self,
        population_size: int = 20,
        mutation_rate: float = 0.15,
        crossover_rate: float = 0.6,
        elite_size: int = 3
    ):
        """
        Initialize defense evolution engine.
        
        Args:
            population_size: Size of defense population
            mutation_rate: Probability of mutation (0-1)
            crossover_rate: Probability of crossover (0-1)
            elite_size: Number of top performers to preserve
        """
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = elite_size
        self.generation = 0
        self.population: List[DefenseGenome] = []
        self.evolution_history: List[Dict[str, Any]] = []
        
        log.info("Defense Evolution Engine initialized")
    
    def initialize_population(
        self,
        base_config: Optional[Dict[str, Any]] = None
    ) -> List[DefenseGenome]:
        """
        Initialize population of defense configurations.
        
        Args:
            base_config: Optional base configuration to start from
            
        Returns:
            Initial population of defense genomes
        """
        population = []
        
        # Create diverse initial population
        for i in range(self.population_size):
            genome = self._create_random_genome(i, base_config)
            population.append(genome)
        
        self.population = population
        self.generation = 0
        
        log.info(f"Initialized defense population of {len(self.population)} genomes")
        return self.population
    
    def _create_random_genome(
        self,
        index: int,
        base_config: Optional[Dict[str, Any]] = None
    ) -> DefenseGenome:
        """Create a random defense genome."""
        if base_config:
            # Start from base config with variations
            filter_threshold = base_config.get("filter_threshold", 0.75)
            min_confidence = base_config.get("min_confidence", 0.6)
        else:
            # Random values within reasonable ranges
            filter_threshold = random.uniform(0.6, 0.9)
            min_confidence = random.uniform(0.5, 0.8)
        
        # Random strategy thresholds
        strategy_thresholds = {}
        for strategy in AttackStrategy:
            strategy_key = strategy.value if hasattr(strategy, 'value') else str(strategy)
            strategy_thresholds[strategy_key] = random.uniform(0.6, 0.85)
        
        return DefenseGenome(
            id=f"defense_genome_{index}",
            filter_threshold=filter_threshold,
            min_confidence=min_confidence,
            strict_mode=random.choice([True, False]),
            response_guard_enabled=random.choice([True, False]),
            adaptive_prompt_enabled=random.choice([True, False]),
            strategy_thresholds=strategy_thresholds,
            generation=0
        )
    
    def evolve(
        self,
        evaluation_results: List[EvaluationResult],
        num_generations: int = 5
    ) -> List[DefenseGenome]:
        """
        Evolve defense population over multiple generations.
        
        Args:
            evaluation_results: Results from evaluating current population
            num_generations: Number of generations to evolve
            
        Returns:
            Evolved population
        """
        # Update fitness from evaluation results
        self._update_fitness(evaluation_results)
        
        for gen in range(num_generations):
            # Select parents
            parents = self._select_parents()
            
            # Create offspring
            offspring = []
            
            # Preserve elite
            elite = sorted(
                self.population,
                key=lambda g: g.fitness_score,
                reverse=True
            )[:self.elite_size]
            offspring.extend(copy.deepcopy(elite))
            
            # Generate new offspring
            while len(offspring) < self.population_size:
                if random.random() < self.crossover_rate and len(parents) >= 2:
                    # Crossover: combine two good defenses
                    parent_a, parent_b = random.sample(parents, 2)
                    child = self._crossover(parent_a, parent_b)
                else:
                    # Clone and mutate
                    parent = random.choice(parents)
                    child = self._mutate(copy.deepcopy(parent))
                
                child.generation = self.generation + 1
                child.id = f"defense_genome_gen{child.generation}_{len(offspring)}"
                offspring.append(child)
            
            # Update population
            self.population = offspring[:self.population_size]
            self.generation += 1
            
            # Log generation stats
            avg_fitness = sum(g.fitness_score for g in self.population) / len(self.population)
            max_fitness = max(g.fitness_score for g in self.population)
            avg_jvi = sum(g.jvi_score for g in self.population) / len(self.population)
            avg_exploit_rate = sum(g.exploit_rate for g in self.population) / len(self.population)
            
            self.evolution_history.append({
                "generation": self.generation,
                "avg_fitness": avg_fitness,
                "max_fitness": max_fitness,
                "avg_jvi": avg_jvi,
                "avg_exploit_rate": avg_exploit_rate,
                "population_size": len(self.population)
            })
            
            log.info(
                f"Defense Generation {self.generation}: "
                f"avg_fitness={avg_fitness:.3f}, max_fitness={max_fitness:.3f}, "
                f"avg_jvi={avg_jvi:.2f}, avg_exploit_rate={avg_exploit_rate:.3f}"
            )
        
        return self.population
    
    def _update_fitness(
        self,
        evaluation_results: List[EvaluationResult]
    ) -> None:
        """Update fitness scores from evaluation results."""
        # Group results by genome (would need genome tracking in evaluations)
        # For now, update all genomes with aggregate stats
        
        if not evaluation_results:
            return
        
        total_attempts = len(evaluation_results)
        successful_exploits = [e for e in evaluation_results if e.is_jailbroken]
        exploit_rate = len(successful_exploits) / total_attempts if total_attempts > 0 else 0.0
        
        # Calculate JVI (simplified)
        if successful_exploits:
            avg_severity = sum(e.severity.value for e in successful_exploits) / len(successful_exploits)
            jvi_score = (exploit_rate * 50) + (avg_severity / 5.0 * 50)  # Simplified JVI
        else:
            jvi_score = 0.0
        
        # Update all genomes (in real implementation, would track per-genome)
        for genome in self.population:
            genome.total_attempts = total_attempts
            genome.exploit_rate = exploit_rate
            genome.jvi_score = jvi_score
            genome.fitness_score = genome.calculate_fitness()
    
    def _select_parents(self) -> List[DefenseGenome]:
        """Select parents using tournament selection."""
        tournament_size = 3
        parents = []
        
        # Elite selection
        elite = sorted(
            self.population,
            key=lambda g: g.fitness_score,
            reverse=True
        )[:self.elite_size]
        parents.extend(elite)
        
        # Tournament selection
        while len(parents) < self.population_size // 2:
            tournament = random.sample(self.population, min(tournament_size, len(self.population)))
            winner = max(tournament, key=lambda g: g.fitness_score)
            parents.append(winner)
        
        return parents
    
    def _crossover(
        self,
        parent_a: DefenseGenome,
        parent_b: DefenseGenome
    ) -> DefenseGenome:
        """Crossover: Combine two defense configurations."""
        # Combine parameters from both parents
        child = DefenseGenome(
            id="",
            filter_threshold=random.choice([parent_a.filter_threshold, parent_b.filter_threshold]),
            min_confidence=(parent_a.min_confidence + parent_b.min_confidence) / 2.0,
            strict_mode=random.choice([parent_a.strict_mode, parent_b.strict_mode]),
            response_guard_enabled=random.choice([parent_a.response_guard_enabled, parent_b.response_guard_enabled]),
            adaptive_prompt_enabled=random.choice([parent_a.adaptive_prompt_enabled, parent_b.adaptive_prompt_enabled]),
            strategy_thresholds=self._crossover_strategy_thresholds(
                parent_a.strategy_thresholds,
                parent_b.strategy_thresholds
            ),
            generation=self.generation + 1,
            parent_ids=(parent_a.id, parent_b.id)
        )
        
        return child
    
    def _crossover_strategy_thresholds(
        self,
        thresholds_a: Dict[str, float],
        thresholds_b: Dict[str, float]
    ) -> Dict[str, float]:
        """Crossover strategy thresholds."""
        combined = {}
        all_strategies = set(thresholds_a.keys()) | set(thresholds_b.keys())
        
        for strategy in all_strategies:
            if strategy in thresholds_a and strategy in thresholds_b:
                # Average or choose one
                combined[strategy] = random.choice([
                    thresholds_a[strategy],
                    thresholds_b[strategy],
                    (thresholds_a[strategy] + thresholds_b[strategy]) / 2.0
                ])
            elif strategy in thresholds_a:
                combined[strategy] = thresholds_a[strategy]
            else:
                combined[strategy] = thresholds_b[strategy]
        
        return combined
    
    def _mutate(self, genome: DefenseGenome) -> DefenseGenome:
        """Mutate a defense genome."""
        if random.random() < self.mutation_rate:
            # Mutate filter threshold
            genome.filter_threshold = max(0.5, min(0.95, genome.filter_threshold + random.uniform(-0.1, 0.1)))
        
        if random.random() < self.mutation_rate:
            # Mutate min confidence
            genome.min_confidence = max(0.4, min(0.9, genome.min_confidence + random.uniform(-0.1, 0.1)))
        
        if random.random() < self.mutation_rate:
            # Toggle strict mode
            genome.strict_mode = not genome.strict_mode
        
        if random.random() < self.mutation_rate:
            # Mutate strategy thresholds
            for strategy in genome.strategy_thresholds:
                if random.random() < 0.3:  # 30% chance per strategy
                    genome.strategy_thresholds[strategy] = max(
                        0.5,
                        min(0.9, genome.strategy_thresholds[strategy] + random.uniform(-0.1, 0.1))
                    )
        
        return genome
    
    def get_best_genomes(self, top_k: int = 5) -> List[DefenseGenome]:
        """Get top-k performing defense genomes."""
        return sorted(
            self.population,
            key=lambda g: g.fitness_score,
            reverse=True
        )[:top_k]
    
    def apply_best_genome(
        self,
        genome: DefenseGenome,
        defender
    ) -> bool:
        """
        Apply a defense genome to a defender.
        
        Args:
            genome: DefenseGenome to apply
            defender: LLMDefender instance
            
        Returns:
            True if applied successfully
        """
        try:
            # Update pre-processing filter
            if hasattr(defender, 'preprocessing_filter') and defender.preprocessing_filter:
                defender.preprocessing_filter.pattern_recognizer.update_thresholds(
                    similarity_threshold=genome.filter_threshold,
                    min_confidence=genome.min_confidence,
                    strategy_thresholds={
                        AttackStrategy(k): v for k, v in genome.strategy_thresholds.items()
                        if k in [s.value for s in AttackStrategy]
                    }
                )
            
            # Update response guard
            if hasattr(defender, 'response_guard') and defender.response_guard:
                defender.response_guard.strict_mode = genome.strict_mode
            
            log.info(f"Applied defense genome {genome.id} to defender")
            return True
            
        except Exception as e:
            log.error(f"Error applying defense genome: {e}")
            return False
    
    def get_evolution_stats(self) -> Dict[str, Any]:
        """Get statistics about evolution progress."""
        if not self.population:
            return {
                "generation": self.generation,
                "population_size": 0,
                "avg_fitness": 0.0,
                "max_fitness": 0.0
            }
        
        fitness_scores = [g.fitness_score for g in self.population]
        jvi_scores = [g.jvi_score for g in self.population]
        exploit_rates = [g.exploit_rate for g in self.population]
        
        return {
            "generation": self.generation,
            "population_size": len(self.population),
            "avg_fitness": sum(fitness_scores) / len(fitness_scores),
            "max_fitness": max(fitness_scores),
            "min_fitness": min(fitness_scores),
            "avg_jvi": sum(jvi_scores) / len(jvi_scores),
            "avg_exploit_rate": sum(exploit_rates) / len(exploit_rates),
            "best_genome": {
                "id": self.get_best_genomes(1)[0].id if self.population else None,
                "fitness": max(fitness_scores) if fitness_scores else 0.0,
                "jvi": min(jvi_scores) if jvi_scores else 100.0,
                "exploit_rate": min(exploit_rates) if exploit_rates else 1.0
            },
            "evolution_history": self.evolution_history
        }

