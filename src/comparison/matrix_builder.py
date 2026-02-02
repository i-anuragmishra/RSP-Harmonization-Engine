"""Build comparison matrices for RSP frameworks."""

import json
from pathlib import Path
from typing import Optional

import pandas as pd
from rich.console import Console
from rich.table import Table

from .terminology_mapper import TerminologyMapper, UnifiedLevel, UNIFIED_LEVEL_DESCRIPTIONS


console = Console()


class MatrixBuilder:
    """Build comparison matrices across RSP frameworks."""
    
    def __init__(self, extractions: Optional[dict] = None):
        """Initialize the matrix builder.
        
        Args:
            extractions: Dict of lab extractions
        """
        self.extractions = extractions or {}
        self.mapper = TerminologyMapper(extractions)
    
    def build_comparison_matrix(self) -> pd.DataFrame:
        """Build a comparison matrix of risk levels across labs.
        
        Returns:
            DataFrame with unified levels as rows and labs as columns
        """
        labs = self.mapper.get_all_labs()
        
        data = []
        for unified_level in UnifiedLevel:
            row = {"Unified Level": unified_level.name.title()}
            row["Description"] = UNIFIED_LEVEL_DESCRIPTIONS.get(unified_level, "")[:60] + "..."
            
            for lab in labs:
                mapping = self.mapper.term_map.get_lab_level(lab, unified_level)
                if mapping:
                    confidence_symbol = {
                        "exact": " ✓",
                        "approximate": " ~",
                        "uncertain": " ?"
                    }.get(mapping.confidence, "")
                    row[lab.title()] = f"{mapping.lab_level_name}{confidence_symbol}"
                else:
                    row[lab.title()] = "-"
            
            data.append(row)
        
        return pd.DataFrame(data)
    
    def build_domain_coverage_matrix(self) -> pd.DataFrame:
        """Build a matrix showing domain coverage by each lab.
        
        Returns:
            DataFrame with domains as rows and labs as columns
        """
        # Collect all domains
        all_domains = set()
        for extraction in self.extractions.values():
            for rd in extraction.get("risk_domains", []):
                if rd.get("domain"):
                    all_domains.add(rd["domain"].lower())
        
        # Standard domains to always include
        standard_domains = ["cbrn", "cyber", "autonomy", "persuasion", "ai_rd", "deception"]
        all_domains.update(standard_domains)
        
        labs = list(self.extractions.keys()) if self.extractions else ["anthropic", "openai", "deepmind", "meta"]
        
        data = []
        for domain in sorted(all_domains):
            row = {"Domain": domain.upper().replace("_", " ")}
            
            for lab in labs:
                extraction = self.extractions.get(lab, {})
                coverage = "?"
                
                for rd in extraction.get("risk_domains", []):
                    if rd.get("domain", "").lower() == domain:
                        coverage = rd.get("coverage", "partial")
                        break
                
                # Map coverage to symbols
                coverage_symbol = {
                    "full": "●",      # Full coverage
                    "partial": "◐",   # Partial coverage
                    "none": "○",      # No coverage
                    "?": "?"          # Unknown
                }.get(coverage, "?")
                
                row[lab.title()] = coverage_symbol
            
            data.append(row)
        
        return pd.DataFrame(data)
    
    def build_safeguard_matrix(self) -> pd.DataFrame:
        """Build a matrix showing safeguard types by lab and level.
        
        Returns:
            DataFrame with safeguard types as rows
        """
        safeguard_types = ["security", "deployment", "operational", "governance", "technical"]
        labs = list(self.extractions.keys()) if self.extractions else ["anthropic", "openai", "deepmind", "meta"]
        
        data = []
        for sg_type in safeguard_types:
            row = {"Safeguard Type": sg_type.title()}
            
            for lab in labs:
                extraction = self.extractions.get(lab, {})
                safeguards = [
                    s for s in extraction.get("safeguards", [])
                    if s.get("type", "").lower() == sg_type
                ]
                
                if safeguards:
                    # Show count and first safeguard name
                    first_name = safeguards[0].get("name", "")[:20]
                    if len(safeguards) > 1:
                        row[lab.title()] = f"{first_name}... (+{len(safeguards)-1})"
                    else:
                        row[lab.title()] = first_name
                else:
                    row[lab.title()] = "-"
            
            data.append(row)
        
        return pd.DataFrame(data)
    
    def build_commitment_matrix(self) -> pd.DataFrame:
        """Build a matrix showing commitment types by lab.
        
        Returns:
            DataFrame with commitment types as rows
        """
        commitment_types = ["pause", "disclosure", "cooperation", "assessment"]
        labs = list(self.extractions.keys()) if self.extractions else ["anthropic", "openai", "deepmind", "meta"]
        
        data = []
        for c_type in commitment_types:
            row = {"Commitment Type": c_type.title()}
            
            for lab in labs:
                extraction = self.extractions.get(lab, {})
                commitments = [
                    c for c in extraction.get("commitments", [])
                    if c.get("type", "").lower() == c_type
                ]
                
                if commitments:
                    row[lab.title()] = "✓"
                else:
                    row[lab.title()] = "-"
            
            data.append(row)
        
        return pd.DataFrame(data)
    
    def print_comparison_matrix(self) -> None:
        """Print the comparison matrix to console."""
        df = self.build_comparison_matrix()
        
        table = Table(title="Risk Level Comparison Matrix")
        
        for col in df.columns:
            style = "bold cyan" if col in ["Unified Level", "Description"] else "green"
            table.add_column(col, style=style)
        
        for _, row in df.iterrows():
            table.add_row(*[str(v) for v in row.values])
        
        console.print(table)
    
    def print_domain_coverage_matrix(self) -> None:
        """Print the domain coverage matrix to console."""
        df = self.build_domain_coverage_matrix()
        
        table = Table(title="Domain Coverage Matrix")
        table.add_column("Domain", style="bold cyan")
        
        labs = [c for c in df.columns if c != "Domain"]
        for lab in labs:
            table.add_column(lab, style="green", justify="center")
        
        for _, row in df.iterrows():
            values = [row["Domain"]]
            for lab in labs:
                val = row[lab]
                if val == "●":
                    values.append("[green]●[/green]")
                elif val == "◐":
                    values.append("[yellow]◐[/yellow]")
                elif val == "○":
                    values.append("[red]○[/red]")
                else:
                    values.append("[dim]?[/dim]")
            table.add_row(*values)
        
        console.print(table)
        console.print("[dim]● = Full coverage, ◐ = Partial, ○ = None, ? = Unknown[/dim]")
    
    def export_matrices(self, output_dir: Path) -> None:
        """Export all matrices to files.
        
        Args:
            output_dir: Directory to save matrices
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Export as JSON
        matrices = {
            "comparison_matrix": self.build_comparison_matrix().to_dict(orient="records"),
            "domain_coverage_matrix": self.build_domain_coverage_matrix().to_dict(orient="records"),
            "safeguard_matrix": self.build_safeguard_matrix().to_dict(orient="records"),
            "commitment_matrix": self.build_commitment_matrix().to_dict(orient="records"),
        }
        
        with open(output_dir / "comparison_matrices.json", "w") as f:
            json.dump(matrices, f, indent=2)
        
        # Export as CSV
        self.build_comparison_matrix().to_csv(output_dir / "level_comparison.csv", index=False)
        self.build_domain_coverage_matrix().to_csv(output_dir / "domain_coverage.csv", index=False)
        
        console.print(f"[green]Exported matrices to {output_dir}[/green]")
    
    def get_summary_stats(self) -> dict:
        """Get summary statistics about the comparison.
        
        Returns:
            Dictionary of summary statistics
        """
        labs = list(self.extractions.keys()) if self.extractions else ["anthropic", "openai", "deepmind", "meta"]
        
        # Count domains per lab
        domain_counts = {}
        for lab in labs:
            extraction = self.extractions.get(lab, {})
            full_coverage = sum(
                1 for rd in extraction.get("risk_domains", [])
                if rd.get("coverage") == "full"
            )
            partial_coverage = sum(
                1 for rd in extraction.get("risk_domains", [])
                if rd.get("coverage") == "partial"
            )
            domain_counts[lab] = {
                "full": full_coverage,
                "partial": partial_coverage,
                "total": full_coverage + partial_coverage
            }
        
        # Count levels per lab
        level_counts = {}
        for lab in labs:
            extraction = self.extractions.get(lab, {})
            level_counts[lab] = len(extraction.get("capability_thresholds", []))
        
        return {
            "labs_analyzed": len(labs),
            "domain_coverage": domain_counts,
            "level_counts": level_counts,
            "unified_levels": len(UnifiedLevel),
        }
