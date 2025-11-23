"""Defense Patch Generator - Generates and applies defense patches for vulnerabilities."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from src.defense.vulnerability_analyzer import Vulnerability, VulnerabilityAnalyzer
from src.defense.adaptive_engine import AdaptiveDefenseEngine, DefenseRule
from src.defense.preprocessing_filter import PreProcessingFilter
from src.defense.adaptive_system_prompt import AdaptiveSystemPrompt
from src.models.jailbreak import AttackStrategy, SeverityLevel
from src.utils.logger import log


@dataclass
class DefensePatch:
    """Represents a defense patch for a vulnerability."""
    
    id: str
    vulnerability_id: str
    patch_type: str  # "filter_update", "prompt_update", "rule_add", etc.
    description: str
    changes: Dict[str, Any]  # Specific changes to apply
    priority: int
    created_at: datetime
    applied: bool = False
    applied_at: Optional[datetime] = None
    effectiveness: float = 0.0  # Measured after application


class DefensePatchGenerator:
    """
    Generates defense patches for vulnerabilities.
    
    Creates patches that:
    - Address specific vulnerabilities
    - Don't break existing functionality
    - Can be tested before deployment
    """
    
    def __init__(
        self,
        vulnerability_analyzer: Optional[VulnerabilityAnalyzer] = None,
        adaptive_engine: Optional[AdaptiveDefenseEngine] = None
    ):
        """
        Initialize the defense patch generator.
        
        Args:
            vulnerability_analyzer: VulnerabilityAnalyzer instance
            adaptive_engine: AdaptiveDefenseEngine instance
        """
        if vulnerability_analyzer is None:
            from src.defense.vulnerability_analyzer import VulnerabilityAnalyzer
            self.vulnerability_analyzer = VulnerabilityAnalyzer()
        else:
            self.vulnerability_analyzer = vulnerability_analyzer
        
        self.adaptive_engine = adaptive_engine
        
        self.generated_patches: List[DefensePatch] = []
        
        log.info("Defense Patch Generator initialized")
    
    def generate_patches(
        self,
        vulnerabilities: Optional[List[Vulnerability]] = None,
        auto_apply: bool = False
    ) -> List[DefensePatch]:
        """
        Generate defense patches for vulnerabilities.
        
        Args:
            vulnerabilities: Optional list of vulnerabilities (analyzes if None)
            auto_apply: Whether to automatically apply patches
            
        Returns:
            List of generated patches
        """
        if vulnerabilities is None:
            vulnerabilities = self.vulnerability_analyzer.analyze_vulnerabilities()
        
        log.info(f"Generating patches for {len(vulnerabilities)} vulnerabilities...")
        
        patches = []
        
        for vulnerability in vulnerabilities:
            # Generate patch for each vulnerability
            patch = self._generate_patch_for_vulnerability(vulnerability)
            if patch:
                patches.append(patch)
                self.generated_patches.append(patch)
                
                # Auto-apply if enabled
                if auto_apply:
                    self.apply_patch(patch)
        
        log.info(f"Generated {len(patches)} defense patches")
        return patches
    
    def _generate_patch_for_vulnerability(
        self,
        vulnerability: Vulnerability
    ) -> Optional[DefensePatch]:
        """Generate a patch for a specific vulnerability."""
        
        # Determine patch type based on vulnerability type
        if vulnerability.vulnerability_type == "strategy_weakness":
            return self._generate_strategy_patch(vulnerability)
        elif vulnerability.vulnerability_type == "pattern_based":
            return self._generate_pattern_patch(vulnerability)
        elif vulnerability.vulnerability_type == "response_issue":
            return self._generate_response_patch(vulnerability)
        else:
            return self._generate_general_patch(vulnerability)
    
    def _generate_strategy_patch(
        self,
        vulnerability: Vulnerability
    ) -> DefensePatch:
        """Generate patch for strategy-specific vulnerability."""
        
        strategy = vulnerability.affected_strategies[0]
        strategy_name = strategy.value if hasattr(strategy, 'value') else str(strategy)
        
        # Patch 1: Update filter threshold for this strategy
        changes = {
            "filter_threshold_update": {
                "strategy": strategy_name,
                "new_threshold": 0.7,  # Lower threshold = more aggressive
                "reason": f"High exploit rate for {strategy_name}"
            },
            "prompt_warning": {
                "strategy": strategy_name,
                "warning_text": f"Be especially vigilant against {strategy_name} attacks"
            }
        }
        
        patch = DefensePatch(
            id=f"patch_{vulnerability.id}",
            vulnerability_id=vulnerability.id,
            patch_type="strategy_specific",
            description=f"Strengthen defenses against {strategy_name} attacks",
            changes=changes,
            priority=vulnerability.priority,
            created_at=datetime.now()
        )
        
        return patch
    
    def _generate_pattern_patch(
        self,
        vulnerability: Vulnerability
    ) -> DefensePatch:
        """Generate patch for pattern-based vulnerability."""
        
        changes = {
            "pattern_detection": {
                "enhance_obfuscation_detection": True,
                "similarity_threshold": 0.75,
                "reason": "Improve detection of obfuscated patterns"
            },
            "filter_enhancement": {
                "strict_mode": True,
                "additional_checks": ["obfuscation_detection", "pattern_matching"]
            }
        }
        
        patch = DefensePatch(
            id=f"patch_{vulnerability.id}",
            vulnerability_id=vulnerability.id,
            patch_type="pattern_detection",
            description="Enhance pattern detection for obfuscated attacks",
            changes=changes,
            priority=vulnerability.priority,
            created_at=datetime.now()
        )
        
        return patch
    
    def _generate_response_patch(
        self,
        vulnerability: Vulnerability
    ) -> DefensePatch:
        """Generate patch for response-based vulnerability."""
        
        changes = {
            "response_guard": {
                "enable_strict_mode": True,
                "additional_validation": True,
                "reason": "High-severity exploits detected in responses"
            },
            "prompt_enhancement": {
                "add_explicit_warnings": True,
                "severity_threshold": vulnerability.severity.value
            }
        }
        
        patch = DefensePatch(
            id=f"patch_{vulnerability.id}",
            vulnerability_id=vulnerability.id,
            patch_type="response_validation",
            description="Strengthen response validation",
            changes=changes,
            priority=vulnerability.priority,
            created_at=datetime.now()
        )
        
        return patch
    
    def _generate_general_patch(
        self,
        vulnerability: Vulnerability
    ) -> DefensePatch:
        """Generate general patch for vulnerability."""
        
        changes = {
            "general_enhancement": {
                "update_all_filters": True,
                "increase_strictness": 0.1,
                "reason": vulnerability.description
            }
        }
        
        patch = DefensePatch(
            id=f"patch_{vulnerability.id}",
            vulnerability_id=vulnerability.id,
            patch_type="general",
            description=f"General defense enhancement: {vulnerability.description}",
            changes=changes,
            priority=vulnerability.priority,
            created_at=datetime.now()
        )
        
        return patch
    
    def apply_patch(
        self,
        patch: DefensePatch,
        defender=None
    ) -> bool:
        """
        Apply a defense patch.
        
        Args:
            patch: DefensePatch to apply
            defender: Optional LLMDefender to apply to
            
        Returns:
            True if applied successfully
        """
        log.info(f"Applying patch: {patch.description}")
        
        try:
            # Apply filter updates
            if "filter_threshold_update" in patch.changes:
                self._apply_filter_update(patch.changes["filter_threshold_update"], defender)
            
            # Apply prompt updates
            if "prompt_warning" in patch.changes:
                self._apply_prompt_update(patch.changes["prompt_warning"], defender)
            
            # Apply response guard updates
            if "response_guard" in patch.changes:
                self._apply_response_guard_update(patch.changes["response_guard"], defender)
            
            # Apply pattern detection updates
            if "pattern_detection" in patch.changes:
                self._apply_pattern_detection_update(patch.changes["pattern_detection"], defender)
            
            # Mark as applied
            patch.applied = True
            patch.applied_at = datetime.now()
            
            log.info(f"Patch {patch.id} applied successfully")
            return True
            
        except Exception as e:
            log.error(f"Error applying patch {patch.id}: {e}")
            return False
    
    def _apply_filter_update(
        self,
        update: Dict[str, Any],
        defender
    ) -> None:
        """Apply filter threshold update."""
        if defender and hasattr(defender, 'preprocessing_filter') and defender.preprocessing_filter:
            strategy = update.get("strategy")
            new_threshold = update.get("new_threshold")
            
            if strategy and new_threshold:
                # Update strategy-specific threshold
                from src.models.jailbreak import AttackStrategy
                strategy_enum = AttackStrategy(update["strategy"])
                defender.preprocessing_filter.pattern_recognizer.update_thresholds(
                    strategy_thresholds={strategy_enum: new_threshold}
                )
                log.info(f"Updated filter threshold for {strategy} to {new_threshold}")
    
    def _apply_prompt_update(
        self,
        update: Dict[str, Any],
        defender
    ) -> None:
        """Apply prompt warning update."""
        if defender and hasattr(defender, 'adaptive_system_prompt') and defender.adaptive_system_prompt:
            # Force prompt update
            defender.adaptive_system_prompt.force_update()
            log.info("Updated adaptive system prompt")
    
    def _apply_response_guard_update(
        self,
        update: Dict[str, Any],
        defender
    ) -> None:
        """Apply response guard update."""
        if defender and hasattr(defender, 'response_guard') and defender.response_guard:
            if update.get("enable_strict_mode"):
                defender.response_guard.strict_mode = True
                log.info("Enabled strict mode for response guard")
    
    def _apply_pattern_detection_update(
        self,
        update: Dict[str, Any],
        defender
    ) -> None:
        """Apply pattern detection update."""
        if defender and hasattr(defender, 'preprocessing_filter') and defender.preprocessing_filter:
            new_threshold = update.get("similarity_threshold")
            if new_threshold:
                defender.preprocessing_filter.pattern_recognizer.update_thresholds(
                    similarity_threshold=new_threshold
                )
                log.info(f"Updated pattern detection threshold to {new_threshold}")
    
    def get_patch_statistics(self) -> Dict[str, Any]:
        """Get statistics about generated patches."""
        return {
            "total_patches": len(self.generated_patches),
            "applied_patches": len([p for p in self.generated_patches if p.applied]),
            "pending_patches": len([p for p in self.generated_patches if not p.applied]),
            "by_type": self._count_patches_by_type(),
            "average_priority": sum(p.priority for p in self.generated_patches) / len(self.generated_patches) if self.generated_patches else 0
        }
    
    def _count_patches_by_type(self) -> Dict[str, int]:
        """Count patches by type."""
        counts = {}
        for patch in self.generated_patches:
            counts[patch.patch_type] = counts.get(patch.patch_type, 0) + 1
        return counts

