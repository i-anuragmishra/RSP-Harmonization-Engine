#!/usr/bin/env python3
"""
RSP Harmonization Engine
========================

Main entry point for the RSP Harmonization Engine.

Usage:
    python main.py extract     # Run extraction pipeline
    python main.py analyze     # Run gap analysis
    python main.py harmonize   # Generate harmonization recommendations
    python main.py dashboard   # Launch Streamlit dashboard
    python main.py demo        # Run quick demo with prebuilt data
    python main.py all         # Run full pipeline
"""

import sys
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def run_extraction():
    """Run the extraction pipeline."""
    console.print(Panel("[bold]Running RSP Extraction Pipeline[/bold]"))
    
    from src.extraction.llm_extractor import main as extract_main
    return extract_main()


def run_analysis():
    """Run gap analysis on extracted data."""
    console.print(Panel("[bold]Running Gap Analysis[/bold]"))
    
    from src.extraction.llm_extractor import PREBUILT_EXTRACTIONS
    from src.comparison.gap_analyzer import GapAnalyzer
    from src.comparison.terminology_mapper import TerminologyMapper
    
    # Load data
    data_path = Path(__file__).parent / "outputs" / "reports" / "all_extracted.json"
    if data_path.exists():
        with open(data_path) as f:
            data = json.load(f)
    else:
        data = PREBUILT_EXTRACTIONS
    
    # Run terminology mapping
    console.print("\n[bold cyan]== Terminology Mapping ==[/bold cyan]\n")
    mapper = TerminologyMapper(data)
    mapper.print_mapping_table()
    
    # Run gap analysis
    console.print("\n[bold cyan]== Gap Analysis ==[/bold cyan]\n")
    analyzer = GapAnalyzer(data)
    analyzer.print_gap_report()
    
    # Export results
    output_path = Path(__file__).parent / "outputs" / "reports" / "gap_analysis.json"
    analyzer.export_gaps(output_path)
    
    return analyzer.gaps


def run_harmonization():
    """Generate harmonization recommendations."""
    console.print(Panel("[bold]Generating Harmonization Recommendations[/bold]"))
    
    from src.harmonization.language_suggester import LanguageSuggester
    
    suggester = LanguageSuggester()
    recommendations = suggester.get_recommendations()
    
    console.print(f"\n[green]Generated {len(recommendations)} harmonization recommendations[/green]\n")
    
    for rec in recommendations:
        console.print(f"[bold]{rec.recommendation_id}[/bold]: {rec.topic}")
        console.print(f"  [dim]Confidence: {rec.confidence} | Targets: {', '.join(rec.applicable_to[:2])}...[/dim]")
    
    # Export
    base_dir = Path(__file__).parent
    suggester.export_recommendations(base_dir / "outputs" / "harmonized_language" / "recommendations.md")
    suggester.export_json(base_dir / "outputs" / "harmonized_language" / "recommendations.json")
    
    return recommendations


def run_dashboard():
    """Launch the Streamlit dashboard."""
    console.print(Panel("[bold]Launching Dashboard[/bold]"))
    
    import subprocess
    dashboard_path = Path(__file__).parent / "visualization" / "dashboard.py"
    
    console.print("[dim]Starting Streamlit server...[/dim]")
    console.print("[green]Dashboard will open at http://localhost:8501[/green]")
    
    subprocess.run(["streamlit", "run", str(dashboard_path)])


def run_demo():
    """Run a quick demo with prebuilt data."""
    console.print(Panel("[bold]RSP Harmonization Engine - Demo[/bold]", 
                       subtitle="Comparing Responsible Scaling Policies"))
    
    from src.extraction.llm_extractor import PREBUILT_EXTRACTIONS
    from src.comparison.gap_analyzer import GapAnalyzer
    from src.comparison.terminology_mapper import TerminologyMapper
    from src.harmonization.language_suggester import LanguageSuggester
    
    # Show extracted data summary
    console.print("\n[bold cyan]1. Extracted Data Summary[/bold cyan]\n")
    
    for lab, data in PREBUILT_EXTRACTIONS.items():
        info = data.get("lab_info", {})
        thresholds = data.get("capability_thresholds", [])
        console.print(f"  [green]✓[/green] {info.get('name', lab.title())}: "
                     f"{info.get('document_name', 'N/A')} v{info.get('version', 'N/A')} "
                     f"({len(thresholds)} levels defined)")
    
    # Show terminology mapping
    console.print("\n[bold cyan]2. Terminology Mapping[/bold cyan]\n")
    mapper = TerminologyMapper(PREBUILT_EXTRACTIONS)
    mapper.print_mapping_table()
    
    # Show key gaps
    console.print("\n[bold cyan]3. Key Gaps Identified[/bold cyan]\n")
    analyzer = GapAnalyzer(PREBUILT_EXTRACTIONS)
    gaps = analyzer.analyze_all()
    
    high_gaps = [g for g in gaps if g.severity == "high"]
    for gap in high_gaps[:3]:
        console.print(f"  [red]■[/red] {gap.gap_id}: {gap.title}")
        console.print(f"    [dim]{gap.description[:100]}...[/dim]")
    
    console.print(f"\n  [dim]Total: {len(gaps)} gaps ({len(high_gaps)} high severity)[/dim]")
    
    # Show harmonization recommendations preview
    console.print("\n[bold cyan]4. Harmonization Recommendations[/bold cyan]\n")
    suggester = LanguageSuggester()
    recommendations = suggester.get_recommendations()
    
    for rec in recommendations[:3]:
        console.print(f"  [blue]●[/blue] {rec.topic}")
        console.print(f"    [dim]→ {rec.applicable_to[0]}, {rec.applicable_to[1]}...[/dim]")
    
    console.print(f"\n  [dim]Total: {len(recommendations)} recommendations[/dim]")
    
    # Export demo outputs
    console.print("\n[bold cyan]5. Exporting Results[/bold cyan]\n")
    
    base_dir = Path(__file__).parent
    outputs_dir = base_dir / "outputs"
    
    # Save all outputs
    with open(outputs_dir / "reports" / "all_extracted.json", "w") as f:
        json.dump(PREBUILT_EXTRACTIONS, f, indent=2)
    console.print(f"  [green]✓[/green] Saved extracted data")
    
    analyzer.export_gaps(outputs_dir / "reports" / "gap_analysis.json")
    console.print(f"  [green]✓[/green] Saved gap analysis")
    
    suggester.export_json(outputs_dir / "harmonized_language" / "recommendations.json")
    suggester.export_recommendations(outputs_dir / "harmonized_language" / "recommendations.md")
    console.print(f"  [green]✓[/green] Saved harmonization recommendations")
    
    console.print("\n[bold green]Demo complete![/bold green]")
    console.print("[dim]Run 'python main.py dashboard' to explore interactively[/dim]")


def run_all():
    """Run the full pipeline."""
    console.print(Panel("[bold]Running Full Pipeline[/bold]"))
    
    run_extraction()
    run_analysis()
    run_harmonization()
    
    console.print("\n[bold green]Full pipeline complete![/bold green]")
    console.print("[dim]Run 'python main.py dashboard' to view results[/dim]")


def print_help():
    """Print usage information."""
    console.print(__doc__)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    commands = {
        "extract": run_extraction,
        "analyze": run_analysis,
        "harmonize": run_harmonization,
        "dashboard": run_dashboard,
        "demo": run_demo,
        "all": run_all,
        "help": print_help,
        "-h": print_help,
        "--help": print_help
    }
    
    if command in commands:
        commands[command]()
    else:
        console.print(f"[red]Unknown command: {command}[/red]")
        print_help()


if __name__ == "__main__":
    main()
