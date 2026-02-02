#!/usr/bin/env python3
"""Create a complete submission package with all results and visualizations."""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.extraction.llm_extractor import PREBUILT_EXTRACTIONS
from src.comparison.terminology_mapper import TerminologyMapper, UnifiedLevel, UNIFIED_LEVEL_DESCRIPTIONS
from src.comparison.gap_analyzer import GapAnalyzer, GapSeverity, GapType
from src.comparison.matrix_builder import MatrixBuilder
from src.harmonization.language_suggester import LanguageSuggester
from src.harmonization.regulator_output import RegulatorOutput


def create_submission():
    """Create complete submission package."""
    
    # Setup
    submission_dir = Path(__file__).parent / "submission"
    submission_dir.mkdir(exist_ok=True)
    
    (submission_dir / "data").mkdir(exist_ok=True)
    (submission_dir / "visualizations").mkdir(exist_ok=True)
    (submission_dir / "reports").mkdir(exist_ok=True)
    
    print("Creating RSP Harmonization Engine Submission Package...")
    print("=" * 60)
    
    # Load data
    extractions = PREBUILT_EXTRACTIONS
    mapper = TerminologyMapper(extractions)
    analyzer = GapAnalyzer(extractions)
    analyzer.analyze_all()
    matrix_builder = MatrixBuilder(extractions)
    suggester = LanguageSuggester(extractions)
    regulator = RegulatorOutput(suggester)
    
    # 1. Export raw data
    print("\n1. Exporting data files...")
    
    with open(submission_dir / "data" / "all_extractions.json", "w") as f:
        json.dump(extractions, f, indent=2)
    print("   ✓ all_extractions.json")
    
    with open(submission_dir / "data" / "gap_analysis.json", "w") as f:
        json.dump(analyzer.to_dict(), f, indent=2)
    print("   ✓ gap_analysis.json")
    
    with open(submission_dir / "data" / "terminology_mapping.json", "w") as f:
        json.dump(mapper.to_dict(), f, indent=2)
    print("   ✓ terminology_mapping.json")
    
    with open(submission_dir / "data" / "recommendations.json", "w") as f:
        json.dump({"recommendations": [r.to_dict() for r in suggester.get_recommendations()]}, f, indent=2)
    print("   ✓ recommendations.json")
    
    # 2. Export CSVs
    print("\n2. Exporting CSV tables...")
    
    comparison_df = matrix_builder.build_comparison_matrix()
    comparison_df.to_csv(submission_dir / "data" / "level_comparison.csv", index=False)
    print("   ✓ level_comparison.csv")
    
    domain_df = matrix_builder.build_domain_coverage_matrix()
    domain_df.to_csv(submission_dir / "data" / "domain_coverage.csv", index=False)
    print("   ✓ domain_coverage.csv")
    
    # 3. Create visualizations
    print("\n3. Creating visualizations...")
    
    # Gap severity pie chart
    severity_counts = {"High": 0, "Medium": 0, "Low": 0}
    for gap in analyzer.gaps:
        severity_counts[gap.severity.value.title()] += 1
    
    fig_severity = go.Figure(data=[go.Pie(
        labels=list(severity_counts.keys()),
        values=list(severity_counts.values()),
        hole=0.4,
        marker_colors=["#FF6B6B", "#FFE66D", "#4ECDC4"]
    )])
    fig_severity.update_layout(title="Gap Severity Distribution", width=600, height=400)
    fig_severity.write_html(submission_dir / "visualizations" / "gap_severity.html")
    fig_severity.write_image(submission_dir / "visualizations" / "gap_severity.png")
    print("   ✓ gap_severity.html/png")
    
    # Gap by type chart
    type_data = [{"Type": g.type.value.title(), "Severity": g.severity.value.title()} for g in analyzer.gaps]
    type_df = pd.DataFrame(type_data)
    
    fig_types = px.histogram(type_df, x="Type", color="Severity",
                             title="Gaps by Type and Severity",
                             color_discrete_map={"High": "#FF6B6B", "Medium": "#FFE66D", "Low": "#4ECDC4"})
    fig_types.update_layout(width=700, height=400)
    fig_types.write_html(submission_dir / "visualizations" / "gaps_by_type.html")
    fig_types.write_image(submission_dir / "visualizations" / "gaps_by_type.png")
    print("   ✓ gaps_by_type.html/png")
    
    # Domain coverage heatmap
    labs = list(extractions.keys())
    domains = ["cbrn", "cyber", "autonomy", "persuasion", "ai_rd", "deception"]
    
    coverage_matrix = []
    for domain in domains:
        row = []
        for lab in labs:
            coverage = 0
            for rd in extractions[lab].get("risk_domains", []):
                if rd.get("domain", "").lower() == domain:
                    cov = rd.get("coverage", "none")
                    coverage = {"full": 2, "partial": 1, "none": 0}.get(cov, 0)
                    break
            row.append(coverage)
        coverage_matrix.append(row)
    
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=coverage_matrix,
        x=[l.title() for l in labs],
        y=[d.upper() for d in domains],
        colorscale=[[0, "#FFB6C1"], [0.5, "#FFE4B5"], [1, "#90EE90"]],
        showscale=True,
        colorbar=dict(ticktext=["None", "Partial", "Full"], tickvals=[0, 1, 2])
    ))
    fig_heatmap.update_layout(title="Risk Domain Coverage by Lab", width=700, height=450)
    fig_heatmap.write_html(submission_dir / "visualizations" / "domain_coverage_heatmap.html")
    fig_heatmap.write_image(submission_dir / "visualizations" / "domain_coverage_heatmap.png")
    print("   ✓ domain_coverage_heatmap.html/png")
    
    # Level mapping Sankey
    unified_levels = ["MINIMAL", "EMERGING", "SIGNIFICANT", "SEVERE", "CRITICAL"]
    labels = [f"[Unified] {level.title()}" for level in unified_levels]
    unified_indices = {level: i for i, level in enumerate(unified_levels)}
    
    sources, targets, values, colors = [], [], [], []
    lab_colors = {
        "anthropic": "rgba(255, 107, 107, 0.8)",
        "openai": "rgba(78, 205, 196, 0.8)",
        "deepmind": "rgba(69, 183, 209, 0.8)",
        "meta": "rgba(150, 206, 180, 0.8)"
    }
    
    idx = len(unified_levels)
    for lab in labs:
        for mapping in mapper.get_lab_levels(lab):
            labels.append(f"[{lab.title()}] {mapping.lab_level_name}")
            sources.append(idx)
            targets.append(unified_indices[mapping.unified_level.name])
            values.append(1)
            colors.append(lab_colors.get(lab, "rgba(128, 128, 128, 0.8)"))
            idx += 1
    
    fig_sankey = go.Figure(data=[go.Sankey(
        node=dict(pad=15, thickness=20, label=labels),
        link=dict(source=sources, target=targets, value=values, color=colors)
    )])
    fig_sankey.update_layout(title="Risk Level Terminology Mapping", width=900, height=500)
    fig_sankey.write_html(submission_dir / "visualizations" / "terminology_mapping.html")
    fig_sankey.write_image(submission_dir / "visualizations" / "terminology_mapping.png")
    print("   ✓ terminology_mapping.html/png")
    
    # 4. Create reports
    print("\n4. Creating reports...")
    
    suggester.export_recommendations(submission_dir / "reports" / "harmonization_recommendations.md")
    print("   ✓ harmonization_recommendations.md")
    
    with open(submission_dir / "reports" / "eu_code_of_practice.md", "w") as f:
        f.write(regulator.format_for_eu_code())
    print("   ✓ eu_code_of_practice.md")
    
    with open(submission_dir / "reports" / "uk_aisi_recommendations.md", "w") as f:
        f.write(regulator.format_for_aisi("UK"))
    print("   ✓ uk_aisi_recommendations.md")
    
    with open(submission_dir / "reports" / "executive_brief.md", "w") as f:
        f.write(regulator.generate_summary_brief())
    print("   ✓ executive_brief.md")
    
    # 5. Create summary document
    print("\n5. Creating summary document...")
    
    summary = f"""# RSP Harmonization Engine - Complete Results

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Overview

This package contains the complete analysis of Responsible Scaling Policies (RSPs) from 4 major AI labs:
- **Anthropic** - RSP v2.2 (October 2024)
- **OpenAI** - Preparedness Framework v2.0 (April 2025)
- **Google DeepMind** - Frontier Safety Framework v3.0 (October 2025)
- **Meta** - Frontier AI Framework v1.0 (2025)

## Key Findings

### Gap Analysis
- **Total Gaps Identified:** {len(analyzer.gaps)}
- **High Severity:** {len(analyzer.get_gaps_by_severity(GapSeverity.HIGH))}
- **Medium Severity:** {len(analyzer.get_gaps_by_severity(GapSeverity.MEDIUM))}
- **Low Severity:** {len(analyzer.get_gaps_by_severity(GapSeverity.LOW))}

### Top High-Severity Gaps
"""
    
    for gap in analyzer.get_gaps_by_severity(GapSeverity.HIGH):
        summary += f"""
#### {gap.gap_id}: {gap.title}
- **Type:** {gap.type.value.title()}
- **Affected Labs:** {', '.join(gap.affected_labs)}
- **Description:** {gap.description}
- **Recommendation:** {gap.recommendation}
"""
    
    summary += f"""
## Harmonization Recommendations

{len(suggester.get_recommendations())} recommendations generated across 4 categories:
- Terminology Standardization
- Threshold Alignment
- Safeguard Requirements
- Process Harmonization

### High Priority Recommendations
"""
    
    for rec in suggester.get_recommendations_by_priority("high"):
        summary += f"""
#### {rec.recommendation_id}: {rec.topic}
**Current State:** {rec.current_state}

**Proposed:**
{rec.proposed_language}

**Applicable To:** {', '.join(rec.applicable_to)}
"""
    
    summary += """
## Package Contents

### /data/
- `all_extractions.json` - Structured data extracted from all 4 lab RSP documents
- `gap_analysis.json` - Complete gap analysis with all identified inconsistencies
- `terminology_mapping.json` - Mapping of risk levels across frameworks
- `recommendations.json` - Machine-readable harmonization recommendations
- `level_comparison.csv` - Risk level comparison table
- `domain_coverage.csv` - Domain coverage matrix

### /visualizations/
- `gap_severity.html/png` - Pie chart of gap severity distribution
- `gaps_by_type.html/png` - Bar chart of gaps by type and severity
- `domain_coverage_heatmap.html/png` - Heatmap of risk domain coverage
- `terminology_mapping.html/png` - Sankey diagram of level mappings

### /reports/
- `harmonization_recommendations.md` - Full recommendations document
- `eu_code_of_practice.md` - Formatted for EU AI Act Code of Practice
- `uk_aisi_recommendations.md` - Formatted for UK AI Safety Institute
- `executive_brief.md` - Executive summary brief

## Terminology Mapping

| Unified Level | Anthropic | OpenAI | DeepMind | Meta |
|---------------|-----------|--------|----------|------|
| Minimal | ASL-1 | Low | - | Tier 1 |
| Emerging | ASL-2 | Medium | Below CCL | Tier 2 |
| Significant | ASL-3 | High | CCL-1 | Tier 3 |
| Severe | ASL-4 | - | CCL-2 | - |
| Critical | - | Critical | - | Tier 4 |

## Risk Domain Coverage

| Domain | Anthropic | OpenAI | DeepMind | Meta |
|--------|-----------|--------|----------|------|
| CBRN | Full | Full | Full | Full |
| Cyber | Full | Full | Full | Full |
| Autonomy | Full | Full | Full | Partial |
| Persuasion | Partial | Full | - | - |
| AI R&D | Full | - | Full | - |
| Deception | - | - | Full | - |

---

*Generated by RSP Harmonization Engine - Track 3 Submission*
"""
    
    with open(submission_dir / "SUMMARY.md", "w") as f:
        f.write(summary)
    print("   ✓ SUMMARY.md")
    
    # 6. Create index HTML
    html_index = """<!DOCTYPE html>
<html>
<head>
    <title>RSP Harmonization Engine Results</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { color: #2C3E50; border-bottom: 3px solid #3498DB; padding-bottom: 10px; }
        h2 { color: #34495E; margin-top: 30px; }
        .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 20px 0; }
        .card { border: 1px solid #ddd; border-radius: 8px; padding: 15px; }
        .card h3 { margin-top: 0; color: #2C3E50; }
        a { color: #3498DB; }
        .stats { display: flex; gap: 20px; margin: 20px 0; }
        .stat { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; flex: 1; }
        .stat-value { font-size: 2em; font-weight: bold; color: #2C3E50; }
        .stat-label { color: #666; }
        iframe { width: 100%; height: 450px; border: 1px solid #ddd; border-radius: 8px; }
    </style>
</head>
<body>
    <h1>RSP Harmonization Engine Results</h1>
    
    <div class="stats">
        <div class="stat"><div class="stat-value">4</div><div class="stat-label">Labs Analyzed</div></div>
        <div class="stat"><div class="stat-value">11</div><div class="stat-label">Gaps Identified</div></div>
        <div class="stat"><div class="stat-value">5</div><div class="stat-label">High Severity</div></div>
        <div class="stat"><div class="stat-value">7</div><div class="stat-label">Recommendations</div></div>
    </div>
    
    <h2>Visualizations</h2>
    <div class="grid">
        <div class="card">
            <h3>Gap Severity Distribution</h3>
            <iframe src="visualizations/gap_severity.html"></iframe>
        </div>
        <div class="card">
            <h3>Gaps by Type</h3>
            <iframe src="visualizations/gaps_by_type.html"></iframe>
        </div>
        <div class="card">
            <h3>Domain Coverage</h3>
            <iframe src="visualizations/domain_coverage_heatmap.html"></iframe>
        </div>
        <div class="card">
            <h3>Terminology Mapping</h3>
            <iframe src="visualizations/terminology_mapping.html"></iframe>
        </div>
    </div>
    
    <h2>Reports</h2>
    <ul>
        <li><a href="SUMMARY.md">Complete Summary (Markdown)</a></li>
        <li><a href="reports/harmonization_recommendations.md">Harmonization Recommendations</a></li>
        <li><a href="reports/executive_brief.md">Executive Brief</a></li>
        <li><a href="reports/eu_code_of_practice.md">EU Code of Practice Format</a></li>
        <li><a href="reports/uk_aisi_recommendations.md">UK AISI Format</a></li>
    </ul>
    
    <h2>Data Files</h2>
    <ul>
        <li><a href="data/all_extractions.json">All Extractions (JSON)</a></li>
        <li><a href="data/gap_analysis.json">Gap Analysis (JSON)</a></li>
        <li><a href="data/terminology_mapping.json">Terminology Mapping (JSON)</a></li>
        <li><a href="data/recommendations.json">Recommendations (JSON)</a></li>
        <li><a href="data/level_comparison.csv">Level Comparison (CSV)</a></li>
        <li><a href="data/domain_coverage.csv">Domain Coverage (CSV)</a></li>
    </ul>
</body>
</html>"""
    
    with open(submission_dir / "index.html", "w") as f:
        f.write(html_index)
    print("   ✓ index.html")
    
    print("\n" + "=" * 60)
    print("SUBMISSION PACKAGE COMPLETE!")
    print(f"Location: {submission_dir}")
    print("\nContents:")
    print("  - index.html (open this to view everything)")
    print("  - SUMMARY.md (complete summary document)")
    print("  - /data/ (JSON and CSV data files)")
    print("  - /visualizations/ (charts as HTML and PNG)")
    print("  - /reports/ (formatted recommendation documents)")


if __name__ == "__main__":
    create_submission()
