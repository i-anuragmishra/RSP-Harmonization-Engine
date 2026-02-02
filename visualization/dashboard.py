"""Streamlit dashboard for RSP Harmonization Engine."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import json

from src.extraction.llm_extractor import PREBUILT_EXTRACTIONS
from src.comparison.terminology_mapper import TerminologyMapper, UnifiedLevel, UNIFIED_LEVEL_DESCRIPTIONS
from src.comparison.gap_analyzer import GapAnalyzer, GapSeverity, GapType
from src.comparison.matrix_builder import MatrixBuilder
from src.harmonization.language_suggester import LanguageSuggester

from visualization.components.comparison_table import render_comparison_table
from visualization.components.gap_chart import render_gap_chart, render_severity_distribution
from visualization.components.terminology_graph import render_terminology_graph


# Page configuration
st.set_page_config(
    page_title="RSP Harmonization Engine",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_data():
    """Load extraction data from file or use prebuilt."""
    data_path = Path(__file__).parent.parent / "outputs" / "reports" / "all_extracted.json"
    
    if data_path.exists():
        with open(data_path) as f:
            return json.load(f)
    return PREBUILT_EXTRACTIONS


def main():
    """Main dashboard entry point."""
    # Load data
    extractions = load_data()
    
    # Initialize components
    mapper = TerminologyMapper(extractions)
    analyzer = GapAnalyzer(extractions)
    analyzer.analyze_all()
    matrix_builder = MatrixBuilder(extractions)
    suggester = LanguageSuggester(extractions)
    
    # Sidebar
    st.sidebar.title("🔬 RSP Harmonization")
    st.sidebar.markdown("---")
    
    # Lab filter
    all_labs = list(extractions.keys())
    selected_labs = st.sidebar.multiselect(
        "Filter Labs",
        options=all_labs,
        default=all_labs,
        help="Select which labs to include in analysis"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.markdown(
        "This tool analyzes Responsible Scaling Policies (RSPs) from major AI labs "
        "to identify gaps and generate harmonization recommendations."
    )
    
    # Main content with tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview",
        "🔄 Level Mapping", 
        "📈 Domain Coverage",
        "⚠️ Gap Analysis",
        "📝 Harmonization"
    ])
    
    # Tab 1: Overview
    with tab1:
        st.header("RSP Framework Overview")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Labs Analyzed", len(selected_labs))
        with col2:
            st.metric("Total Gaps Identified", len(analyzer.gaps))
        with col3:
            high_gaps = len(analyzer.get_gaps_by_severity(GapSeverity.HIGH))
            st.metric("High Severity Gaps", high_gaps)
        with col4:
            st.metric("Recommendations", len(suggester.get_recommendations()))
        
        st.markdown("---")
        
        # Lab cards
        st.subheader("Analyzed Frameworks")
        
        cols = st.columns(min(len(selected_labs), 4))
        for i, lab in enumerate(selected_labs):
            with cols[i % 4]:
                data = extractions.get(lab, {})
                info = data.get("lab_info", {})
                thresholds = data.get("capability_thresholds", [])
                domains = data.get("risk_domains", [])
                
                st.markdown(f"### {info.get('name', lab.title())}")
                st.markdown(f"**Document:** {info.get('document_name', 'N/A')}")
                st.markdown(f"**Version:** {info.get('version', 'N/A')}")
                st.markdown(f"**Risk Levels:** {len(thresholds)}")
                st.markdown(f"**Domains Covered:** {len(domains)}")
                
                # Show level names
                level_names = [t.get("level_name", "") for t in thresholds]
                st.markdown(f"*Levels: {', '.join(level_names)}*")
    
    # Tab 2: Level Mapping
    with tab2:
        st.header("Risk Level Terminology Mapping")
        st.markdown(
            "This table shows how risk levels from different labs map to a unified framework. "
            "✓ = exact match, ~ = approximate, ? = uncertain"
        )
        
        render_comparison_table(matrix_builder, selected_labs)
        
        st.markdown("---")
        st.subheader("Unified Level Definitions")
        
        for level in UnifiedLevel:
            with st.expander(f"**{level.name.title()}** (Level {level.value})"):
                st.markdown(UNIFIED_LEVEL_DESCRIPTIONS.get(level, ""))
                
                # Show mappings for this level
                st.markdown("**Lab Mappings:**")
                for lab in selected_labs:
                    mapping = mapper.term_map.get_lab_level(lab, level)
                    if mapping:
                        st.markdown(f"- {lab.title()}: {mapping.lab_level_name} ({mapping.confidence})")
    
    # Tab 3: Domain Coverage
    with tab3:
        st.header("Risk Domain Coverage")
        st.markdown(
            "This heatmap shows which risk domains are covered by each lab's framework. "
            "● = Full coverage, ◐ = Partial, ○ = None"
        )
        
        # Domain coverage matrix
        df = matrix_builder.build_domain_coverage_matrix()
        
        # Filter to selected labs
        cols_to_show = ["Domain"] + [lab.title() for lab in selected_labs if lab.title() in df.columns]
        df_filtered = df[cols_to_show]
        
        # Display dataframe without styling (to avoid jinja2 version issues)
        st.dataframe(df_filtered, use_container_width=True, height=400)
        
        st.markdown("**Legend:** ● Full coverage | ◐ Partial coverage | ○ No coverage")
        
        # Coverage statistics
        st.markdown("---")
        st.subheader("Coverage Statistics")
        
        coverage_stats = matrix_builder.get_summary_stats()
        domain_coverage = coverage_stats.get("domain_coverage", {})
        
        for lab in selected_labs:
            if lab in domain_coverage:
                stats = domain_coverage[lab]
                st.markdown(f"**{lab.title()}:** {stats['full']} full, {stats['partial']} partial")
    
    # Tab 4: Gap Analysis
    with tab4:
        st.header("Gap Analysis")
        
        # Severity filter
        severity_filter = st.multiselect(
            "Filter by Severity",
            options=["high", "medium", "low"],
            default=["high", "medium", "low"]
        )
        
        # Type filter
        type_filter = st.multiselect(
            "Filter by Type",
            options=["threshold", "coverage", "definition", "terminology"],
            default=["threshold", "coverage", "definition", "terminology"]
        )
        
        # Filter gaps
        filtered_gaps = [
            g for g in analyzer.gaps
            if g.severity.value in severity_filter and g.type.value in type_filter
        ]
        
        # Severity distribution
        col1, col2 = st.columns([1, 2])
        
        with col1:
            render_severity_distribution(analyzer)
        
        with col2:
            render_gap_chart(analyzer, type_filter)
        
        st.markdown("---")
        
        # Gap details
        st.subheader(f"Gap Details ({len(filtered_gaps)} gaps)")
        
        for gap in filtered_gaps:
            severity_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(gap.severity.value, "⚪")
            
            with st.expander(f"{severity_color} {gap.gap_id}: {gap.title}"):
                st.markdown(f"**Type:** {gap.type.value.title()}")
                st.markdown(f"**Severity:** {gap.severity.value.upper()}")
                st.markdown(f"**Affected Labs:** {', '.join(gap.affected_labs)}")
                
                if gap.domain:
                    st.markdown(f"**Domain:** {gap.domain}")
                
                st.markdown("---")
                st.markdown(f"**Description:** {gap.description}")
                
                if gap.examples:
                    st.markdown("**Examples:**")
                    for ex in gap.examples:
                        st.markdown(f"- *{ex.lab}*: \"{ex.quote}\"")
                
                if gap.recommendation:
                    st.markdown("---")
                    st.markdown(f"**Recommendation:** {gap.recommendation}")
    
    # Tab 5: Harmonization
    with tab5:
        st.header("Harmonization Recommendations")
        
        # Summary
        recommendations = suggester.get_recommendations()
        high_priority = suggester.get_recommendations_by_priority("high")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Recommendations", len(recommendations))
        with col2:
            st.metric("High Priority", len(high_priority))
        with col3:
            st.metric("Categories", len(set(r.category for r in recommendations)))
        
        st.markdown("---")
        
        # Category filter
        category_filter = st.selectbox(
            "Filter by Category",
            options=["All", "terminology", "threshold", "safeguard", "process"]
        )
        
        # Filter recommendations
        if category_filter == "All":
            filtered_recs = recommendations
        else:
            filtered_recs = suggester.get_recommendations_by_category(category_filter)
        
        # Display recommendations
        for rec in filtered_recs:
            priority_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rec.priority, "⚪")
            
            with st.expander(f"{priority_color} {rec.recommendation_id}: {rec.topic}"):
                st.markdown(f"**Category:** {rec.category.title()}")
                st.markdown(f"**Priority:** {rec.priority.upper()}")
                st.markdown(f"**Confidence:** {rec.confidence.title()}")
                
                st.markdown("---")
                st.markdown("**Current State:**")
                st.info(rec.current_state)
                
                st.markdown("**Proposed Language:**")
                st.code(rec.proposed_language, language=None)
                
                st.markdown("**Rationale:**")
                st.markdown(rec.rationale)
                
                st.markdown(f"**Applicable To:** {', '.join(rec.applicable_to)}")
                
                if rec.implementation_notes:
                    st.markdown(f"**Implementation Notes:** {rec.implementation_notes}")
        
        # Export options
        st.markdown("---")
        st.subheader("Export Recommendations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Download as JSON"):
                json_data = json.dumps(
                    {"recommendations": [r.to_dict() for r in recommendations]},
                    indent=2
                )
                st.download_button(
                    "📥 Download JSON",
                    json_data,
                    "recommendations.json",
                    "application/json"
                )
        
        with col2:
            if st.button("Download as Markdown"):
                md_lines = ["# RSP Harmonization Recommendations\n"]
                for rec in recommendations:
                    md_lines.append(f"## {rec.recommendation_id}: {rec.topic}\n")
                    md_lines.append(f"**Priority:** {rec.priority}\n")
                    md_lines.append(f"{rec.proposed_language}\n\n---\n")
                
                st.download_button(
                    "📥 Download Markdown",
                    "\n".join(md_lines),
                    "recommendations.md",
                    "text/markdown"
                )


if __name__ == "__main__":
    main()
