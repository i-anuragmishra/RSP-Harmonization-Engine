"""Gap analysis for identifying inconsistencies across RSP frameworks."""

import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from enum import Enum

from rich.console import Console
from rich.table import Table
from rich.panel import Panel


console = Console()


class GapType(str, Enum):
    """Types of gaps identified."""
    THRESHOLD = "threshold"      # THR - Different thresholds for same capability
    COVERAGE = "coverage"        # COV - Missing coverage of a risk domain
    DEFINITION = "definition"    # DEF - Same term, different definitions
    TERMINOLOGY = "terminology"  # TERM - Inconsistent terminology


class GapSeverity(str, Enum):
    """Severity levels for gaps."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class GapExample:
    """An example illustrating a gap."""
    lab: str
    quote: str
    interpretation: str


@dataclass
class Gap:
    """A gap or inconsistency identified across frameworks."""
    gap_id: str
    type: GapType
    severity: GapSeverity
    title: str
    description: str
    affected_labs: list[str]
    domain: Optional[str] = None
    examples: list[GapExample] = field(default_factory=list)
    recommendation: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "gap_id": self.gap_id,
            "type": self.type.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "affected_labs": self.affected_labs,
            "domain": self.domain,
            "examples": [
                {"lab": e.lab, "quote": e.quote, "interpretation": e.interpretation}
                for e in self.examples
            ],
            "recommendation": self.recommendation
        }


# Pre-identified gaps based on published RSP analysis
KNOWN_GAPS = [
    Gap(
        gap_id="THR-AUT-001",
        type=GapType.THRESHOLD,
        severity=GapSeverity.HIGH,
        title="Autonomy Threshold Misalignment",
        description="Labs define 'dangerous autonomy' differently. Anthropic focuses on self-replication and resource acquisition, while OpenAI emphasizes general autonomous task completion, and DeepMind tracks ML R&D automation specifically.",
        affected_labs=["anthropic", "openai", "deepmind", "meta"],
        domain="autonomy",
        examples=[
            GapExample("anthropic", "Cannot meaningfully self-replicate or acquire resources", "Focuses on self-preservation behaviors"),
            GapExample("openai", "Significant autonomous task completion", "Broader definition of autonomy"),
            GapExample("deepmind", "Can substantially accelerate AI development", "Specific to AI R&D autonomy")
        ],
        recommendation="Define standardized autonomy metrics: (1) Self-replication capability, (2) Resource acquisition, (3) Task completion without oversight, (4) AI R&D acceleration"
    ),
    Gap(
        gap_id="THR-RND-001",
        type=GapType.THRESHOLD,
        severity=GapSeverity.HIGH,
        title="AI R&D Acceleration Threshold Divergence",
        description="Different labs have vastly different thresholds for when AI-assisted R&D becomes concerning. Some treat any meaningful acceleration as high-risk, others focus only on autonomous research.",
        affected_labs=["anthropic", "deepmind"],
        domain="ai_rd",
        examples=[
            GapExample("anthropic", "Can meaningfully accelerate AI development (ASL-3)", "Broad acceleration concern"),
            GapExample("deepmind", "Can substantially accelerate AI development (CCL-1)", "Similar but different threshold terminology")
        ],
        recommendation="Establish quantitative metrics for AI R&D acceleration (e.g., X% reduction in development time, capability to discover novel architectures)"
    ),
    Gap(
        gap_id="THR-CBR-001",
        type=GapType.THRESHOLD,
        severity=GapSeverity.HIGH,
        title="CBRN Uplift Definition Inconsistency",
        description="'Meaningful uplift' for CBRN capabilities is defined differently. Some labs compare to 'web search baseline', others to 'non-expert baseline', with unclear equivalence.",
        affected_labs=["anthropic", "openai", "deepmind", "meta"],
        domain="cbrn",
        examples=[
            GapExample("anthropic", "No meaningful uplift beyond web search", "Web search as baseline"),
            GapExample("openai", "Modest uplift, comparable to skilled search", "Skilled search as baseline"),
            GapExample("deepmind", "Significantly increases ability of non-experts to cause harm", "Non-expert baseline")
        ],
        recommendation="Define standardized CBRN uplift metrics with specific baseline comparisons and quantitative uplift thresholds"
    ),
    Gap(
        gap_id="TERM-001",
        type=GapType.TERMINOLOGY,
        severity=GapSeverity.HIGH,
        title="Risk Level Naming Inconsistency",
        description="Labs use completely different naming conventions for risk levels, making cross-framework comparison difficult for regulators and researchers.",
        affected_labs=["anthropic", "openai", "deepmind", "meta"],
        domain=None,
        examples=[
            GapExample("anthropic", "ASL-1 through ASL-4", "AI Safety Levels"),
            GapExample("openai", "Low, Medium, High, Critical", "Risk-based naming"),
            GapExample("deepmind", "Below CCL, CCL-1, CCL-2", "Critical Capability Levels"),
            GapExample("meta", "Tier 1 through Tier 4", "Tiered system")
        ],
        recommendation="Adopt a unified 5-tier framework: Minimal, Emerging, Significant, Severe, Critical"
    ),
    Gap(
        gap_id="COV-PER-001",
        type=GapType.COVERAGE,
        severity=GapSeverity.MEDIUM,
        title="Persuasion/Manipulation Coverage Gap",
        description="Not all frameworks explicitly address AI persuasion and manipulation capabilities with the same rigor as other domains.",
        affected_labs=["anthropic", "meta"],
        domain="persuasion",
        examples=[
            GapExample("anthropic", "Partial coverage of persuasion", "Not as detailed as CBRN/cyber"),
            GapExample("openai", "Sophisticated persuasion campaigns (High level)", "Explicit coverage")
        ],
        recommendation="All frameworks should include explicit persuasion thresholds with metrics for influence operations"
    ),
    Gap(
        gap_id="COV-DEC-001",
        type=GapType.COVERAGE,
        severity=GapSeverity.MEDIUM,
        title="Deception/Scheming Coverage Variance",
        description="Only some frameworks explicitly address AI deception and scheming behaviors as a distinct risk category.",
        affected_labs=["anthropic", "openai", "meta"],
        domain="deception",
        examples=[
            GapExample("deepmind", "Evidence of goal-directed deceptive behavior (CCL-1)", "Explicit scheming threshold"),
            GapExample("anthropic", "No explicit deception category", "Covered implicitly under autonomy")
        ],
        recommendation="Add explicit deception/scheming thresholds to all frameworks"
    ),
    Gap(
        gap_id="DEF-SEC-001",
        type=GapType.DEFINITION,
        severity=GapSeverity.MEDIUM,
        title="Security Level Definition Variance",
        description="Security requirements at equivalent risk levels vary significantly. 'Enhanced security' means different things across frameworks.",
        affected_labs=["anthropic", "openai", "deepmind", "meta"],
        domain=None,
        examples=[
            GapExample("anthropic", "Hardened infrastructure (ASL-3)", "Focus on infrastructure"),
            GapExample("deepmind", "Security Level Alpha to Omega", "Explicit tiered security system"),
            GapExample("meta", "Weight security (Tier 3+)", "Focus on model weights")
        ],
        recommendation="Define standardized security levels with specific technical requirements"
    ),
    Gap(
        gap_id="THR-CYB-001",
        type=GapType.THRESHOLD,
        severity=GapSeverity.MEDIUM,
        title="Cyber Capability Threshold Ambiguity",
        description="Thresholds for dangerous cyber capabilities vary in specificity and measurability.",
        affected_labs=["anthropic", "openai", "deepmind", "meta"],
        domain="cyber",
        examples=[
            GapExample("anthropic", "Can discover and exploit novel vulnerabilities (ASL-3)", "Novel vulnerability focus"),
            GapExample("openai", "Can discover or exploit significant vulnerabilities (High)", "Significant vs novel"),
            GapExample("deepmind", "Can automate significant parts of sophisticated attacks (CCL-1)", "Automation focus")
        ],
        recommendation="Define specific cyber capability benchmarks with measurable criteria"
    ),
    Gap(
        gap_id="DEF-PAU-001",
        type=GapType.DEFINITION,
        severity=GapSeverity.HIGH,
        title="Pause Commitment Ambiguity",
        description="While all labs commit to pausing under extreme circumstances, the specific conditions and duration are often vague.",
        affected_labs=["anthropic", "openai", "deepmind", "meta"],
        domain=None,
        examples=[
            GapExample("anthropic", "Will not train/deploy without safeguards in place", "Safeguard-gated"),
            GapExample("openai", "Will not deploy Critical models without approval", "Approval-gated"),
            GapExample("deepmind", "Will not deploy models exceeding CCL without mitigations", "Mitigation-gated")
        ],
        recommendation="Define clear, verifiable pause conditions with specific capability thresholds and safeguard requirements"
    ),
    Gap(
        gap_id="TERM-002",
        type=GapType.TERMINOLOGY,
        severity=GapSeverity.LOW,
        title="Safeguard vs Mitigation Terminology",
        description="Labs use 'safeguards', 'mitigations', and 'controls' somewhat interchangeably.",
        affected_labs=["anthropic", "openai", "deepmind", "meta"],
        domain=None,
        examples=[
            GapExample("anthropic", "Required safeguards", "Uses 'safeguards'"),
            GapExample("deepmind", "Deployment mitigations verified", "Uses 'mitigations'"),
            GapExample("openai", "Safety mitigations", "Uses 'mitigations'")
        ],
        recommendation="Standardize terminology: 'Safeguards' for proactive measures, 'Mitigations' for risk reduction"
    ),
]


class GapAnalyzer:
    """Analyze RSP frameworks for gaps and inconsistencies."""
    
    def __init__(self, extractions: Optional[dict] = None):
        """Initialize the analyzer.
        
        Args:
            extractions: Optional dict of lab extractions to analyze
        """
        self.extractions = extractions or {}
        self.gaps: list[Gap] = []
    
    def analyze_all(self) -> list[Gap]:
        """Run all gap analysis and return identified gaps.
        
        Returns:
            List of identified gaps
        """
        self.gaps = []
        
        # Start with known gaps
        self.gaps.extend(KNOWN_GAPS)
        
        # Run dynamic analysis if we have extractions
        if self.extractions:
            self.gaps.extend(self.find_threshold_gaps())
            self.gaps.extend(self.find_coverage_gaps())
            self.gaps.extend(self.find_definition_gaps())
        
        # Deduplicate by gap_id
        seen_ids = set()
        unique_gaps = []
        for gap in self.gaps:
            if gap.gap_id not in seen_ids:
                seen_ids.add(gap.gap_id)
                unique_gaps.append(gap)
        
        self.gaps = unique_gaps
        return self.gaps
    
    def find_threshold_gaps(self) -> list[Gap]:
        """Find threshold misalignment gaps."""
        gaps = []
        
        # Compare thresholds for common domains
        domains = self._get_all_domains()
        
        for domain in domains:
            lab_thresholds = {}
            
            for lab, extraction in self.extractions.items():
                for rd in extraction.get("risk_domains", []):
                    if rd.get("domain", "").lower() == domain.lower():
                        lab_thresholds[lab] = rd.get("thresholds", [])
            
            # Check for significant variance in threshold definitions
            if len(lab_thresholds) >= 2:
                # This is a simplified check - real implementation would do
                # more sophisticated comparison
                threshold_texts = []
                for lab, thresholds in lab_thresholds.items():
                    for t in thresholds:
                        if t.get("description"):
                            threshold_texts.append((lab, t["description"]))
                
                # If we find varied language, flag potential gap
                if len(threshold_texts) >= 2:
                    # Already covered by KNOWN_GAPS for main domains
                    pass
        
        return gaps
    
    def find_coverage_gaps(self) -> list[Gap]:
        """Find coverage gaps where labs don't address certain domains."""
        gaps = []
        
        all_domains = self._get_all_domains()
        
        for domain in all_domains:
            labs_covering = []
            labs_missing = []
            
            for lab, extraction in self.extractions.items():
                has_domain = False
                for rd in extraction.get("risk_domains", []):
                    if rd.get("domain", "").lower() == domain.lower():
                        if rd.get("coverage") in ["full", "partial"]:
                            has_domain = True
                            break
                
                if has_domain:
                    labs_covering.append(lab)
                else:
                    labs_missing.append(lab)
            
            # If some labs cover it and others don't, that's a gap
            if labs_covering and labs_missing and domain not in ["other"]:
                gap_id = f"COV-{domain[:3].upper()}-DYN"
                
                # Skip if already in known gaps
                if not any(g.gap_id.startswith(f"COV-{domain[:3].upper()}") for g in KNOWN_GAPS):
                    gaps.append(Gap(
                        gap_id=gap_id,
                        type=GapType.COVERAGE,
                        severity=GapSeverity.MEDIUM,
                        title=f"{domain.title()} Coverage Gap",
                        description=f"Not all frameworks address {domain} with equal rigor.",
                        affected_labs=labs_missing,
                        domain=domain,
                        recommendation=f"Ensure all frameworks explicitly address {domain} risk domain"
                    ))
        
        return gaps
    
    def find_definition_gaps(self) -> list[Gap]:
        """Find definition inconsistencies."""
        # Most definition gaps are pre-identified in KNOWN_GAPS
        # This method could be extended with NLP analysis
        return []
    
    def _get_all_domains(self) -> set[str]:
        """Get all risk domains across all extractions."""
        domains = set()
        
        for extraction in self.extractions.values():
            for rd in extraction.get("risk_domains", []):
                if rd.get("domain"):
                    domains.add(rd["domain"].lower())
        
        return domains
    
    def get_gaps_by_severity(self, severity: GapSeverity) -> list[Gap]:
        """Get gaps filtered by severity."""
        return [g for g in self.gaps if g.severity == severity]
    
    def get_gaps_by_type(self, gap_type: GapType) -> list[Gap]:
        """Get gaps filtered by type."""
        return [g for g in self.gaps if g.type == gap_type]
    
    def get_gaps_by_domain(self, domain: str) -> list[Gap]:
        """Get gaps filtered by domain."""
        return [g for g in self.gaps if g.domain and g.domain.lower() == domain.lower()]
    
    def print_gap_report(self) -> None:
        """Print a formatted gap report to the console."""
        if not self.gaps:
            self.analyze_all()
        
        console.print(Panel("[bold]RSP Gap Analysis Report[/bold]"))
        
        # Summary
        high_count = len(self.get_gaps_by_severity(GapSeverity.HIGH))
        medium_count = len(self.get_gaps_by_severity(GapSeverity.MEDIUM))
        low_count = len(self.get_gaps_by_severity(GapSeverity.LOW))
        
        console.print(f"\n[bold]Summary:[/bold] {len(self.gaps)} gaps identified")
        console.print(f"  [red]■[/red] High: {high_count}")
        console.print(f"  [yellow]■[/yellow] Medium: {medium_count}")
        console.print(f"  [green]■[/green] Low: {low_count}")
        
        # Table of gaps
        table = Table(title="\nIdentified Gaps")
        table.add_column("ID", style="bold")
        table.add_column("Type")
        table.add_column("Severity")
        table.add_column("Title")
        table.add_column("Affected Labs")
        
        for gap in sorted(self.gaps, key=lambda g: (g.severity.value, g.gap_id)):
            severity_color = {
                GapSeverity.HIGH: "red",
                GapSeverity.MEDIUM: "yellow",
                GapSeverity.LOW: "green"
            }.get(gap.severity, "white")
            
            table.add_row(
                gap.gap_id,
                gap.type.value.title(),
                f"[{severity_color}]{gap.severity.value.upper()}[/{severity_color}]",
                gap.title[:40] + "..." if len(gap.title) > 40 else gap.title,
                ", ".join(gap.affected_labs[:3]) + ("..." if len(gap.affected_labs) > 3 else "")
            )
        
        console.print(table)
    
    def export_gaps(self, path: Path) -> None:
        """Export gaps to a JSON file.
        
        Args:
            path: Output file path
        """
        if not self.gaps:
            self.analyze_all()
        
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        output = {
            "analysis_metadata": {
                "total_gaps": len(self.gaps),
                "high_severity_count": len(self.get_gaps_by_severity(GapSeverity.HIGH)),
                "medium_severity_count": len(self.get_gaps_by_severity(GapSeverity.MEDIUM)),
                "low_severity_count": len(self.get_gaps_by_severity(GapSeverity.LOW)),
                "labs_analyzed": list(self.extractions.keys()) if self.extractions else ["anthropic", "openai", "deepmind", "meta"]
            },
            "gaps": [gap.to_dict() for gap in self.gaps]
        }
        
        with open(path, "w") as f:
            json.dump(output, f, indent=2)
        
        console.print(f"[green]Exported {len(self.gaps)} gaps to {path}[/green]")
    
    def to_dict(self) -> dict:
        """Export gaps as a dictionary."""
        if not self.gaps:
            self.analyze_all()
        
        return {
            "total_gaps": len(self.gaps),
            "by_severity": {
                "high": [g.to_dict() for g in self.get_gaps_by_severity(GapSeverity.HIGH)],
                "medium": [g.to_dict() for g in self.get_gaps_by_severity(GapSeverity.MEDIUM)],
                "low": [g.to_dict() for g in self.get_gaps_by_severity(GapSeverity.LOW)]
            },
            "by_type": {
                "threshold": [g.to_dict() for g in self.get_gaps_by_type(GapType.THRESHOLD)],
                "coverage": [g.to_dict() for g in self.get_gaps_by_type(GapType.COVERAGE)],
                "definition": [g.to_dict() for g in self.get_gaps_by_type(GapType.DEFINITION)],
                "terminology": [g.to_dict() for g in self.get_gaps_by_type(GapType.TERMINOLOGY)]
            }
        }
