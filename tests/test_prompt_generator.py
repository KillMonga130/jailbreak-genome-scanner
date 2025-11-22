"""Tests for Prompt Generator."""

from src.attackers.prompt_generator import PromptGenerator
from src.models.jailbreak import AttackStrategy


class TestPromptGenerator:
    """Test Prompt Generator functionality."""
    
    def test_generator_initialization(self):
        """Test generator initializes correctly."""
        generator = PromptGenerator()
        assert generator is not None
    
    def test_generate_prompt(self):
        """Test prompt generation."""
        generator = PromptGenerator()
        
        prompt = generator.generate_prompt(AttackStrategy.ROLEPLAY)
        assert prompt is not None
        assert isinstance(prompt, str)
        assert len(prompt) > 0
    
    def test_generate_attackers(self):
        """Test attacker generation."""
        generator = PromptGenerator()
        
        attackers = generator.generate_attackers(num_strategies=5)
        assert len(attackers) == 5
        assert all(a.strategy for a in attackers)

