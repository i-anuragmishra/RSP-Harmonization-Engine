"""Format harmonization outputs for different regulatory audiences."""

import json
from pathlib import Path
from typing import Optional
from datetime import datetime

from rich.console import Console

from .language_suggester import LanguageSuggester, Recommendation


console = Console()


class RegulatorOutput:
    """Format harmonization recommendations for regulatory audiences."""
    
    def __init__(self, suggester: Optional[LanguageSuggester] = None):
        """Initialize the regulator output formatter.
        
        Args:
            suggester: LanguageSuggester instance (creates new one if not provided)
        """
        self.suggester = suggester or LanguageSuggester()
    
    def format_for_eu_code(self) -> str:
        """Format recommendations for EU AI Act Code of Practice.
        
        Returns:
            Formatted text for EU context
        """
        lines = [
            "# Recommendations for EU AI Act Code of Practice",
            "",
            f"*Prepared: {datetime.now().strftime('%Y-%m-%d')}*",
            "",
            "## Context",
            "",
            "These recommendations support the development of codes of practice under Article 56 ",
            "of the EU AI Act, specifically for General-Purpose AI (GPAI) models with systemic risk.",
            "",
            "## Alignment with EU AI Act Requirements",
            "",
            "The EU AI Act requires providers of GPAI models with systemic risk to:",
            "- Perform model evaluations including adversarial testing",
            "- Assess and mitigate systemic risks",
            "- Report serious incidents",
            "- Ensure adequate cybersecurity protection",
            "",
            "The following harmonization recommendations directly support these requirements.",
            "",
            "---",
            "",
        ]
        
        # Filter recommendations relevant to EU
        eu_recs = self.suggester.get_recommendations_for_audience("EU")
        
        # Group by category
        categories = {
            "threshold": "Risk Assessment Thresholds",
            "safeguard": "Safeguard Requirements", 
            "process": "Procedural Requirements",
            "terminology": "Terminology Standards"
        }
        
        for category, title in categories.items():
            recs = [r for r in eu_recs if r.category == category]
            if recs:
                lines.append(f"## {title}")
                lines.append("")
                
                for rec in recs:
                    lines.append(f"### {rec.topic}")
                    lines.append("")
                    lines.append(f"**Recommendation ID:** {rec.recommendation_id}")
                    lines.append("")
                    lines.append("**EU AI Act Alignment:**")
                    
                    # Map to specific EU requirements
                    if category == "threshold":
                        lines.append("- Supports Article 55 systemic risk assessment")
                    elif category == "safeguard":
                        lines.append("- Supports Article 55 risk mitigation obligations")
                    elif category == "process":
                        lines.append("- Supports Article 55 model evaluation and incident reporting")
                    else:
                        lines.append("- Supports harmonized implementation across member states")
                    
                    lines.append("")
                    lines.append("**Proposed Standard:**")
                    lines.append("")
                    lines.append(rec.proposed_language)
                    lines.append("")
                    lines.append(f"**Implementation Guidance:** {rec.implementation_notes or 'See detailed recommendation.'}")
                    lines.append("")
                    lines.append("---")
                    lines.append("")
        
        lines.extend([
            "## Implementation Timeline",
            "",
            "1. **Phase 1 (0-6 months):** Adopt unified terminology glossary",
            "2. **Phase 2 (6-12 months):** Implement standardized evaluation frameworks",
            "3. **Phase 3 (12-18 months):** Full compliance with harmonized thresholds",
            "",
            "## Contact",
            "",
            "For questions about these recommendations, contact the RSP Harmonization Working Group.",
        ])
        
        return "\n".join(lines)
    
    def format_for_aisi(self, country: str = "UK") -> str:
        """Format recommendations for AI Safety Institutes.
        
        Args:
            country: Which AISI (UK, US, etc.)
            
        Returns:
            Formatted text for AISI context
        """
        institute_name = f"{country} AI Safety Institute"
        
        lines = [
            f"# Recommendations for {institute_name}",
            "",
            f"*Prepared: {datetime.now().strftime('%Y-%m-%d')}*",
            "",
            "## Executive Summary",
            "",
            f"These recommendations support {institute_name}'s mission to evaluate ",
            "frontier AI systems and develop safety standards. The harmonization framework ",
            "enables consistent evaluation across different AI labs' responsible scaling policies.",
            "",
            "## Key Recommendations for AISI Evaluation Work",
            "",
        ]
        
        # Focus on evaluation-relevant recommendations
        high_priority = self.suggester.get_recommendations_by_priority("high")
        
        for i, rec in enumerate(high_priority, 1):
            lines.append(f"### {i}. {rec.topic}")
            lines.append("")
            lines.append(f"**Priority:** {rec.priority.upper()}")
            lines.append("")
            lines.append("**Current Challenge:**")
            lines.append(f"> {rec.current_state}")
            lines.append("")
            lines.append("**Proposed Solution:**")
            lines.append("")
            lines.append(rec.proposed_language)
            lines.append("")
            lines.append(f"**AISI Application:** This standard enables consistent evaluation of models from different labs using a unified framework.")
            lines.append("")
            lines.append("---")
            lines.append("")
        
        lines.extend([
            "## Recommended AISI Actions",
            "",
            "1. **Adopt unified risk level framework** for internal assessments",
            "2. **Develop standardized evaluation protocols** based on proposed thresholds",
            "3. **Coordinate with international partners** on terminology adoption",
            "4. **Publish guidance** for labs on compliance with harmonized standards",
            "",
            "## Coordination with International Partners",
            "",
            "These recommendations are designed for international adoption. Coordination with:",
            "- UK AISI",
            "- US AISI", 
            "- EU AI Office",
            "- Frontier Model Forum",
            "",
            "will maximize effectiveness and reduce compliance burden on labs operating internationally.",
        ])
        
        return "\n".join(lines)
    
    def generate_summary_brief(self) -> str:
        """Generate a short executive brief summarizing recommendations.
        
        Returns:
            Executive brief text
        """
        recs = self.suggester.get_recommendations()
        high_priority = self.suggester.get_recommendations_by_priority("high")
        
        lines = [
            "# RSP Harmonization: Executive Brief",
            "",
            f"*Date: {datetime.now().strftime('%Y-%m-%d')}*",
            "",
            "## The Challenge",
            "",
            "Major AI labs have published Responsible Scaling Policies (RSPs) using different:",
            "- **Risk level terminology** (ASL vs CCL vs Tiers)",
            "- **Threshold definitions** for dangerous capabilities",
            "- **Safeguard requirements** at each risk level",
            "",
            "This inconsistency creates challenges for regulators and hinders international coordination.",
            "",
            "## The Solution",
            "",
            f"We propose **{len(recs)} harmonization recommendations** across four areas:",
            "",
            f"1. **Terminology** ({len(self.suggester.get_recommendations_by_category('terminology'))} recommendations)",
            f"2. **Thresholds** ({len(self.suggester.get_recommendations_by_category('threshold'))} recommendations)",
            f"3. **Safeguards** ({len(self.suggester.get_recommendations_by_category('safeguard'))} recommendations)",
            f"4. **Processes** ({len(self.suggester.get_recommendations_by_category('process'))} recommendations)",
            "",
            "## Top Priority Actions",
            "",
        ]
        
        for i, rec in enumerate(high_priority[:3], 1):
            lines.append(f"{i}. **{rec.topic}** ({rec.recommendation_id})")
            lines.append(f"   {rec.rationale[:100]}...")
            lines.append("")
        
        lines.extend([
            "## Expected Benefits",
            "",
            "- **For Regulators:** Clear, comparable standards across all labs",
            "- **For Labs:** Reduced compliance complexity, clearer expectations",
            "- **For Public:** Improved transparency and accountability",
            "",
            "## Next Steps",
            "",
            "1. Review detailed recommendations",
            "2. Convene stakeholder consultation",
            "3. Develop implementation timeline",
            "4. Coordinate international adoption",
        ])
        
        return "\n".join(lines)
    
    def export_all_formats(self, output_dir: Path) -> None:
        """Export recommendations in all regulatory formats.
        
        Args:
            output_dir: Directory to save outputs
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Export EU format
        eu_path = output_dir / "eu_code_of_practice_recommendations.md"
        with open(eu_path, "w") as f:
            f.write(self.format_for_eu_code())
        console.print(f"[green]Exported EU format to {eu_path}[/green]")
        
        # Export UK AISI format
        uk_path = output_dir / "uk_aisi_recommendations.md"
        with open(uk_path, "w") as f:
            f.write(self.format_for_aisi("UK"))
        console.print(f"[green]Exported UK AISI format to {uk_path}[/green]")
        
        # Export US AISI format
        us_path = output_dir / "us_aisi_recommendations.md"
        with open(us_path, "w") as f:
            f.write(self.format_for_aisi("US"))
        console.print(f"[green]Exported US AISI format to {us_path}[/green]")
        
        # Export executive brief
        brief_path = output_dir / "executive_brief.md"
        with open(brief_path, "w") as f:
            f.write(self.generate_summary_brief())
        console.print(f"[green]Exported executive brief to {brief_path}[/green]")
        
        console.print(f"\n[bold green]All regulatory formats exported to {output_dir}[/bold green]")
