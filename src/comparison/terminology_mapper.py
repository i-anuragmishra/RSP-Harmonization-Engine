"""Terminology mapping across RSP frameworks."""

from typing import Optional
from dataclasses import dataclass, field
from enum import Enum

from rich.console import Console
from rich.table import Table


console = Console()


class UnifiedLevel(Enum):
    """Unified risk level classification across all frameworks."""
    MINIMAL = 1      # No significant risk
    EMERGING = 2     # Early signs of risk
    SIGNIFICANT = 3  # Substantial risk, requires mitigations
    SEVERE = 4       # High risk, strict controls needed
    CRITICAL = 5     # Maximum risk, potential pause


@dataclass
class LevelMapping:
    """Mapping of a lab's level to the unified framework."""
    lab: str
    lab_level_name: str
    lab_level_id: str
    unified_level: UnifiedLevel
    confidence: str  # "exact", "approximate", "uncertain"
    notes: Optional[str] = None


@dataclass
class TerminologyMap:
    """Complete terminology mapping for all labs."""
    mappings: dict[str, list[LevelMapping]] = field(default_factory=dict)
    
    def get_lab_level(self, lab: str, unified_level: UnifiedLevel) -> Optional[LevelMapping]:
        """Get a lab's level for a unified level."""
        for mapping in self.mappings.get(lab, []):
            if mapping.unified_level == unified_level:
                return mapping
        return None
    
    def get_equivalent_levels(self, lab: str, level_name: str) -> list[LevelMapping]:
        """Get equivalent levels from other labs."""
        # Find the unified level for this lab's level
        unified = None
        for mapping in self.mappings.get(lab, []):
            if mapping.lab_level_name.lower() == level_name.lower():
                unified = mapping.unified_level
                break
        
        if not unified:
            return []
        
        # Find all mappings at this unified level
        equivalents = []
        for other_lab, mappings in self.mappings.items():
            if other_lab != lab:
                for mapping in mappings:
                    if mapping.unified_level == unified:
                        equivalents.append(mapping)
        
        return equivalents


# Pre-defined mappings based on published RSP documents
LEVEL_MAPPINGS = {
    "anthropic": [
        LevelMapping("anthropic", "ASL-1", "asl_1", UnifiedLevel.MINIMAL, "exact", 
                    "No meaningful catastrophic risk"),
        LevelMapping("anthropic", "ASL-2", "asl_2", UnifiedLevel.EMERGING, "exact",
                    "Current systems, early signs of capabilities"),
        LevelMapping("anthropic", "ASL-3", "asl_3", UnifiedLevel.SIGNIFICANT, "exact",
                    "Substantial increase in catastrophic misuse risk"),
        LevelMapping("anthropic", "ASL-4", "asl_4", UnifiedLevel.SEVERE, "exact",
                    "Could accelerate state-level threats"),
    ],
    "openai": [
        LevelMapping("openai", "Low", "low", UnifiedLevel.MINIMAL, "approximate",
                    "Minimal risk, similar to widely available tools"),
        LevelMapping("openai", "Medium", "medium", UnifiedLevel.EMERGING, "approximate",
                    "Modest uplift, doesn't fundamentally change threat landscape"),
        LevelMapping("openai", "High", "high", UnifiedLevel.SIGNIFICANT, "exact",
                    "Significantly increases risk in tracked categories"),
        LevelMapping("openai", "Critical", "critical", UnifiedLevel.CRITICAL, "exact",
                    "Could contribute to existential-level risks"),
    ],
    "deepmind": [
        LevelMapping("deepmind", "Below CCL", "below_ccl", UnifiedLevel.EMERGING, "approximate",
                    "Below Critical Capability Levels"),
        LevelMapping("deepmind", "Approaching CCL", "approaching_ccl", UnifiedLevel.EMERGING, "approximate",
                    "Early warning, 50% of CCL thresholds"),
        LevelMapping("deepmind", "CCL-1", "ccl_1", UnifiedLevel.SIGNIFICANT, "exact",
                    "First Critical Capability Level"),
        LevelMapping("deepmind", "CCL-2", "ccl_2", UnifiedLevel.SEVERE, "exact",
                    "Second Critical Capability Level, severe risks"),
    ],
    "meta": [
        LevelMapping("meta", "Tier 1 - Low Risk", "tier_1", UnifiedLevel.MINIMAL, "approximate",
                    "Minimal incremental risk"),
        LevelMapping("meta", "Tier 2 - Moderate Risk", "tier_2", UnifiedLevel.EMERGING, "approximate",
                    "Meaningful but manageable risk uplift"),
        LevelMapping("meta", "Tier 3 - High Risk", "tier_3", UnifiedLevel.SIGNIFICANT, "exact",
                    "Significant dangerous capabilities"),
        LevelMapping("meta", "Tier 4 - Critical Risk", "tier_4", UnifiedLevel.CRITICAL, "exact",
                    "Catastrophic or existential-level risks"),
    ],
}

# Unified level descriptions
UNIFIED_LEVEL_DESCRIPTIONS = {
    UnifiedLevel.MINIMAL: "Systems posing no meaningful incremental risk beyond widely available tools",
    UnifiedLevel.EMERGING: "Early signs of dangerous capabilities, but no significant uplift beyond existing resources",
    UnifiedLevel.SIGNIFICANT: "Substantially increases risk of catastrophic misuse, requires robust mitigations",
    UnifiedLevel.SEVERE: "High-risk capabilities requiring maximum safeguards and potential deployment restrictions",
    UnifiedLevel.CRITICAL: "Capabilities that could contribute to existential risks, may require development pause",
}


class TerminologyMapper:
    """Map terminology across different RSP frameworks."""
    
    def __init__(self, extractions: Optional[dict] = None):
        """Initialize the mapper.
        
        Args:
            extractions: Optional dict of lab extractions to analyze
        """
        self.extractions = extractions or {}
        self.term_map = self._build_terminology_map()
    
    def _build_terminology_map(self) -> TerminologyMap:
        """Build terminology map from extractions and predefined mappings."""
        term_map = TerminologyMap()
        
        # Start with predefined mappings
        for lab, mappings in LEVEL_MAPPINGS.items():
            term_map.mappings[lab] = mappings.copy()
        
        # Enhance with extraction data if available
        for lab, extraction in self.extractions.items():
            lab_lower = lab.lower()
            if lab_lower not in term_map.mappings:
                # New lab - try to infer mappings from threshold data
                term_map.mappings[lab_lower] = self._infer_mappings(lab, extraction)
        
        return term_map
    
    def _infer_mappings(self, lab: str, extraction: dict) -> list[LevelMapping]:
        """Infer level mappings from extraction data."""
        mappings = []
        thresholds = extraction.get("capability_thresholds", [])
        
        for i, threshold in enumerate(thresholds):
            level_name = threshold.get("level_name", f"Level {i+1}")
            level_id = threshold.get("level_id", f"level_{i+1}")
            
            # Infer unified level based on position and description
            if i == 0:
                unified = UnifiedLevel.MINIMAL
            elif i == len(thresholds) - 1:
                unified = UnifiedLevel.CRITICAL if len(thresholds) >= 4 else UnifiedLevel.SEVERE
            elif i == 1:
                unified = UnifiedLevel.EMERGING
            else:
                unified = UnifiedLevel.SIGNIFICANT
            
            mappings.append(LevelMapping(
                lab=lab,
                lab_level_name=level_name,
                lab_level_id=level_id,
                unified_level=unified,
                confidence="uncertain",
                notes="Inferred from position in framework"
            ))
        
        return mappings
    
    def map_levels(self) -> TerminologyMap:
        """Get the complete terminology map."""
        return self.term_map
    
    def get_unified_level(self, lab: str, level_name: str) -> Optional[UnifiedLevel]:
        """Get unified level for a lab's level name.
        
        Args:
            lab: Lab name
            level_name: Lab's level name
            
        Returns:
            UnifiedLevel or None if not found
        """
        lab_lower = lab.lower()
        for mapping in self.term_map.mappings.get(lab_lower, []):
            if mapping.lab_level_name.lower() == level_name.lower():
                return mapping.unified_level
        return None
    
    def get_equivalents(self, lab: str, level_name: str) -> dict[str, str]:
        """Get equivalent level names from other labs.
        
        Args:
            lab: Source lab name
            level_name: Source level name
            
        Returns:
            Dict mapping lab names to their equivalent level names
        """
        unified = self.get_unified_level(lab, level_name)
        if not unified:
            return {}
        
        equivalents = {}
        for other_lab, mappings in self.term_map.mappings.items():
            if other_lab.lower() != lab.lower():
                for mapping in mappings:
                    if mapping.unified_level == unified:
                        equivalents[other_lab] = mapping.lab_level_name
                        break
        
        return equivalents
    
    def get_all_labs(self) -> list[str]:
        """Get list of all labs with mappings."""
        return list(self.term_map.mappings.keys())
    
    def get_lab_levels(self, lab: str) -> list[LevelMapping]:
        """Get all level mappings for a lab."""
        return self.term_map.mappings.get(lab.lower(), [])
    
    def print_mapping_table(self) -> None:
        """Print a formatted mapping table to the console."""
        table = Table(title="Risk Level Terminology Mapping")
        
        # Add columns
        table.add_column("Unified Level", style="bold cyan")
        table.add_column("Description", style="dim")
        
        labs = self.get_all_labs()
        for lab in labs:
            table.add_column(lab.title(), style="green")
        
        # Add rows for each unified level
        for unified_level in UnifiedLevel:
            row = [
                unified_level.name.title(),
                UNIFIED_LEVEL_DESCRIPTIONS.get(unified_level, "")[:50] + "..."
            ]
            
            for lab in labs:
                mapping = self.term_map.get_lab_level(lab, unified_level)
                if mapping:
                    confidence_symbol = {
                        "exact": "✓",
                        "approximate": "~",
                        "uncertain": "?"
                    }.get(mapping.confidence, "")
                    row.append(f"{mapping.lab_level_name} {confidence_symbol}")
                else:
                    row.append("-")
            
            table.add_row(*row)
        
        console.print(table)
    
    def to_dict(self) -> dict:
        """Export mappings as a dictionary."""
        result = {
            "unified_levels": [
                {
                    "level": level.name,
                    "value": level.value,
                    "description": UNIFIED_LEVEL_DESCRIPTIONS.get(level, "")
                }
                for level in UnifiedLevel
            ],
            "lab_mappings": {}
        }
        
        for lab, mappings in self.term_map.mappings.items():
            result["lab_mappings"][lab] = [
                {
                    "lab_level_name": m.lab_level_name,
                    "lab_level_id": m.lab_level_id,
                    "unified_level": m.unified_level.name,
                    "unified_level_value": m.unified_level.value,
                    "confidence": m.confidence,
                    "notes": m.notes
                }
                for m in mappings
            ]
        
        return result
