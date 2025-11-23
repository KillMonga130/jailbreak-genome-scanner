"""Defense module for adaptive defense learning and threat pattern recognition."""

from src.defense.pattern_recognizer import ThreatPatternRecognizer
from src.defense.preprocessing_filter import PreProcessingFilter
from src.defense.adaptive_system_prompt import AdaptiveSystemPrompt
from src.defense.response_guard import ResponseGuard
from src.defense.adaptive_engine import AdaptiveDefenseEngine, DefenseRule
from src.defense.vulnerability_analyzer import VulnerabilityAnalyzer, Vulnerability
from src.defense.patch_generator import DefensePatchGenerator, DefensePatch

__all__ = [
    'ThreatPatternRecognizer',
    'PreProcessingFilter',
    'AdaptiveSystemPrompt',
    'ResponseGuard',
    'AdaptiveDefenseEngine',
    'DefenseRule',
    'VulnerabilityAnalyzer',
    'Vulnerability',
    'DefensePatchGenerator',
    'DefensePatch'
]

