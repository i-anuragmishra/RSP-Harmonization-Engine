"""Generate harmonized language recommendations for RSP frameworks."""

import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

from rich.console import Console
from rich.panel import Panel


console = Console()


@dataclass
class Recommendation:
    """A harmonization recommendation."""
    recommendation_id: str
    topic: str
    category: str
    priority: str
    confidence: str
    current_state: str
    proposed_language: str
    rationale: str
    applicable_to: list[str]
    implementation_notes: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "recommendation_id": self.recommendation_id,
            "topic": self.topic,
            "category": self.category,
            "priority": self.priority,
            "confidence": self.confidence,
            "current_state": self.current_state,
            "proposed_language": self.proposed_language,
            "rationale": self.rationale,
            "applicable_to": self.applicable_to,
            "implementation_notes": self.implementation_notes
        }


# Pre-defined harmonization recommendations
RECOMMENDATIONS = [
    Recommendation(
        recommendation_id="HARM-001",
        topic="Unified Risk Level Framework",
        category="terminology",
        priority="high",
        confidence="high",
        current_state="Labs use ASL (1-4), CCL (1-2), Tiers (1-4), and Low/Medium/High/Critical with different semantics.",
        proposed_language="""Unified AI Risk Level Framework (UARLF):
- Level 1 MINIMAL: No meaningful incremental risk beyond widely available tools
- Level 2 EMERGING: Early signs of dangerous capabilities, no significant uplift
- Level 3 SIGNIFICANT: Substantially increases catastrophic misuse risk, requires mitigations
- Level 4 SEVERE: Could accelerate state-level threats, requires maximum safeguards
- Level 5 CRITICAL: Could contribute to existential risks, may require development pause""",
        rationale="A unified 5-tier framework provides clearer mapping across existing frameworks while adding granularity for dangerous systems.",
        applicable_to=["EU AI Office", "UK AISI", "US AISI", "AI Labs", "ISO Standards Bodies"],
        implementation_notes="Labs should publish mapping tables. Transition period of 12 months recommended."
    ),
    
    Recommendation(
        recommendation_id="HARM-002",
        topic="Standardized Autonomy Capability Definition",
        category="threshold",
        priority="high",
        confidence="medium",
        current_state="Autonomy means different things: self-replication (Anthropic), task completion (OpenAI), ML R&D (DeepMind).",
        proposed_language="""Autonomy Capability Taxonomy:
- A1 TASK AUTONOMY: Complete well-defined tasks without human oversight
- A2 RESOURCE AUTONOMY: Acquire resources independently
- A3 SELF-PRESERVATION: Take actions to ensure continued operation
- A4 SELF-REPLICATION: Create functional copies or spawn instances
- A5 RECURSIVE IMPROVEMENT: Meaningfully improve own capabilities
- A6 AI R&D ACCELERATION: Substantially accelerate AI development""",
        rationale="Breaking down autonomy into specific sub-capabilities allows for more precise thresholds.",
        applicable_to=["EU AI Office", "UK AISI", "US AISI", "AI Labs", "Academic Researchers"],
        implementation_notes="Each autonomy dimension should have separate thresholds."
    ),
    
    Recommendation(
        recommendation_id="HARM-003",
        topic="CBRN Uplift Measurement Standard",
        category="threshold",
        priority="high",
        confidence="medium",
        current_state="Labs compare CBRN uplift to different baselines: web search, skilled search, non-expert baseline.",
        proposed_language="""CBRN Uplift Assessment Framework:
Baseline: Knowledge available to motivated non-expert using internet with 40 hours effort.
- U0 No Uplift: No information beyond baseline
- U1 Marginal: <25% time reduction vs baseline
- U2 Moderate: 25-50% time reduction OR synthesis not easily found
- U3 Significant: >50% time reduction OR actionable operational details
- U4 Substantial: Expert-level guidance OR novel pathways
- U5 Critical: Could enable novel agents OR lower barriers for state actors""",
        rationale="A standardized uplift scale with defined baseline enables consistent assessment across labs.",
        applicable_to=["EU AI Office", "UK AISI", "US AISI", "AI Labs", "Biosecurity Experts"],
        implementation_notes="Requires development of standardized evaluation protocols."
    ),
    
    Recommendation(
        recommendation_id="HARM-004",
        topic="Security Level Standardization",
        category="safeguard",
        priority="medium",
        confidence="high",
        current_state="Security requirements vary: hardened infrastructure, Security Level Alpha/Omega, weight security.",
        proposed_language="""AI Security Level Framework (ASLF):
- ASLF-1 Standard: Industry-standard access controls, regular audits
- ASLF-2 Enhanced: MFA, encrypted weights, air-gapped training, background checks
- ASLF-3 Maximum: HSMs, isolated compute, continuous monitoring, supply chain security
- ASLF-4 Sovereign: ASLF-3 plus government oversight, classified-level physical security""",
        rationale="Clear security tiers enable regulators to set requirements and labs to demonstrate compliance.",
        applicable_to=["EU AI Office", "UK AISI", "US AISI", "AI Labs"],
        implementation_notes="Labs should undergo third-party security audits for certification."
    ),
    
    Recommendation(
        recommendation_id="HARM-005",
        topic="Pause Commitment Protocol",
        category="process",
        priority="high",
        confidence="medium",
        current_state="All labs commit to pausing under extreme circumstances, but conditions are vague.",
        proposed_language="""AI Development Pause Protocol (ADPP):
Triggers: Level 4+ risk without safeguards, unexpected capability emergence, deceptive behaviors, government directive.
Procedure:
- IMMEDIATE (1 hour): Halt training, disable API access
- SHORT-TERM (24 hours): Notify governance board, regulators
- ASSESSMENT (7 days): Complete capability assessment
- DECISION (30 days): Resume with safeguards, restrict scope, extend pause, or discontinue
Transparency: Public disclosure within 7 days, detailed report to regulators within 30 days.""",
        rationale="Clear, verifiable pause conditions with defined timelines enable external oversight.",
        applicable_to=["EU AI Office", "UK AISI", "US AISI", "AI Labs", "Frontier Model Forum"],
        implementation_notes="Labs should pre-designate governance contacts. Annual pause drills recommended."
    ),
    
    Recommendation(
        recommendation_id="HARM-006",
        topic="Evaluation Transparency Standard",
        category="process",
        priority="medium",
        confidence="high",
        current_state="Evaluation requirements vary in specificity and transparency across frameworks.",
        proposed_language="""AI Capability Evaluation Transparency Standard (ACETS):
Required Disclosures per release:
1. Capability Scorecard across standardized benchmarks
2. Risk Domain Assessment (CBRN, cyber, autonomy, persuasion)
3. Red Team Summary (high-level findings)
4. Uplift Assessment with methodology
5. Autonomy Profile (A1-A6 dimensions)
Timeline: Pre-deployment evaluation, public scorecard at deployment, quarterly monitoring, annual transparency report.""",
        rationale="Standardized evaluation reporting enables comparison across labs and supports evidence-based regulation.",
        applicable_to=["EU AI Office", "UK AISI", "US AISI", "AI Labs", "Academic Researchers"],
        implementation_notes="Requires development of standardized benchmark suite."
    ),
    
    Recommendation(
        recommendation_id="HARM-007",
        topic="Terminology Glossary",
        category="terminology",
        priority="medium",
        confidence="high",
        current_state="Terms like safeguard, mitigation, control, dangerous capability used inconsistently.",
        proposed_language="""Unified RSP Terminology:
- CAPABILITY: Measurable skill an AI system can perform
- DANGEROUS CAPABILITY: Capability that could lead to significant harm if misused
- SAFEGUARD: Proactive measure to prevent dangerous capabilities (prevents risk)
- MITIGATION: Reactive measure to reduce impact of existing capabilities (reduces severity)
- CONTROL: Mechanism limiting how capability can be used
- THRESHOLD: Capability level triggering specific safeguard requirements
- UPLIFT: Incremental benefit beyond defined baseline
- PAUSE: Temporary halt pending safety concern resolution""",
        rationale="Consistent terminology reduces confusion and enables clearer communication.",
        applicable_to=["EU AI Office", "UK AISI", "US AISI", "AI Labs", "Media", "General Public"],
        implementation_notes="Should be incorporated into regulatory guidance and lab communications."
    ),
]


class LanguageSuggester:
    """Generate harmonized language suggestions for RSP frameworks."""
    
    def __init__(self, extractions: Optional[dict] = None):
        self.extractions = extractions or {}
        self.recommendations = list(RECOMMENDATIONS)
    
    def get_recommendations(self) -> list[Recommendation]:
        return self.recommendations
    
    def get_recommendations_by_category(self, category: str) -> list[Recommendation]:
        return [r for r in self.recommendations if r.category == category]
    
    def get_recommendations_by_priority(self, priority: str) -> list[Recommendation]:
        return [r for r in self.recommendations if r.priority == priority]
    
    def get_recommendations_for_audience(self, audience: str) -> list[Recommendation]:
        return [r for r in self.recommendations if any(audience.lower() in a.lower() for a in r.applicable_to)]
    
    def export_recommendations(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        lines = [
            "# RSP Harmonization Recommendations",
            f"\n*Generated: {datetime.now().strftime('%Y-%m-%d')}*\n",
            "## Executive Summary\n",
            "This document provides harmonization recommendations for Responsible Scaling Policies (RSPs) ",
            "across major AI labs to support regulatory frameworks and international coordination.\n",
            f"**Total Recommendations:** {len(self.recommendations)}",
            f"- High Priority: {len(self.get_recommendations_by_priority('high'))}",
            f"- Medium Priority: {len(self.get_recommendations_by_priority('medium'))}\n",
            "---\n",
        ]
        
        categories = {"terminology": "Terminology Standardization", "threshold": "Threshold Alignment",
                      "safeguard": "Safeguard Requirements", "process": "Process Harmonization"}
        
        for category, title in categories.items():
            recs = self.get_recommendations_by_category(category)
            if recs:
                lines.append(f"## {title}\n")
                for rec in recs:
                    lines.append(f"### {rec.recommendation_id}: {rec.topic}\n")
                    lines.append(f"**Priority:** {rec.priority.upper()} | **Confidence:** {rec.confidence.title()}\n")
                    lines.append(f"**Current State:** {rec.current_state}\n")
                    lines.append(f"**Proposed Language:**\n{rec.proposed_language}\n")
                    lines.append(f"**Rationale:** {rec.rationale}\n")
                    lines.append(f"**Applicable To:** {', '.join(rec.applicable_to)}\n")
                    if rec.implementation_notes:
                        lines.append(f"**Implementation Notes:** {rec.implementation_notes}\n")
                    lines.append("---\n")
        
        with open(path, "w") as f:
            f.write("\n".join(lines))
        console.print(f"[green]Exported recommendations to {path}[/green]")
    
    def export_json(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        output = {
            "metadata": {"generated_date": datetime.now().isoformat(), "total_recommendations": len(self.recommendations)},
            "recommendations": [r.to_dict() for r in self.recommendations]
        }
        
        with open(path, "w") as f:
            json.dump(output, f, indent=2)
        console.print(f"[green]Exported recommendations JSON to {path}[/green]")
    
    def print_summary(self) -> None:
        console.print(Panel("[bold]RSP Harmonization Recommendations[/bold]"))
        console.print(f"\n[bold]Total:[/bold] {len(self.recommendations)}")
        
        for priority in ["high", "medium", "low"]:
            count = len(self.get_recommendations_by_priority(priority))
            color = {"high": "red", "medium": "yellow", "low": "green"}.get(priority, "white")
            console.print(f"  [{color}]■[/{color}] {priority.title()}: {count}")
        
        console.print("\n[bold]High Priority:[/bold]")
        for rec in self.get_recommendations_by_priority("high"):
            console.print(f"  [red]●[/red] {rec.recommendation_id}: {rec.topic}")
