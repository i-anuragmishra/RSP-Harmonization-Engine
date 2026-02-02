"""Comparison table component for dashboard."""

import streamlit as st
import pandas as pd
from typing import Optional


def render_comparison_table(matrix_builder, selected_labs: Optional[list] = None):
    """Render the risk level comparison table.
    
    Args:
        matrix_builder: MatrixBuilder instance
        selected_labs: Optional list of labs to include
    """
    df = matrix_builder.build_comparison_matrix()
    
    # Filter columns if labs specified
    if selected_labs:
        cols_to_keep = ["Unified Level", "Description"]
        for lab in selected_labs:
            lab_title = lab.title()
            if lab_title in df.columns:
                cols_to_keep.append(lab_title)
        df = df[cols_to_keep]
    
    # Style function for confidence indicators
    def style_confidence(val):
        if "✓" in str(val):
            return "background-color: #90EE90; font-weight: bold"  # Green for exact
        elif "~" in str(val):
            return "background-color: #FFE4B5"  # Orange for approximate
        elif "?" in str(val):
            return "background-color: #FFB6C1"  # Pink for uncertain
        elif val == "-":
            return "color: #888"
        return ""
    
    # Apply styling to data columns (not Unified Level or Description)
    data_cols = [c for c in df.columns if c not in ["Unified Level", "Description"]]
    styled_df = df.style.applymap(style_confidence, subset=data_cols)
    
    st.dataframe(styled_df, use_container_width=True, height=300)
    
    # Legend
    st.markdown("""
    **Legend:** 
    - ✓ = Exact mapping
    - ~ = Approximate mapping  
    - ? = Uncertain mapping
    - \- = No equivalent level
    """)


def render_level_details(mapper, lab: str, level_name: str):
    """Render details for a specific level.
    
    Args:
        mapper: TerminologyMapper instance
        lab: Lab name
        level_name: Level name to show details for
    """
    equivalents = mapper.get_equivalents(lab, level_name)
    
    if equivalents:
        st.markdown(f"**Equivalent levels to {lab.title()} {level_name}:**")
        for other_lab, other_level in equivalents.items():
            st.markdown(f"- {other_lab.title()}: {other_level}")
    else:
        st.markdown("*No equivalent mappings found*")


def render_interactive_comparison(extractions: dict, selected_labs: list):
    """Render an interactive comparison view.
    
    Args:
        extractions: Dict of lab extractions
        selected_labs: List of selected lab names
    """
    # Create columns for each lab
    if not selected_labs:
        st.warning("No labs selected")
        return
    
    cols = st.columns(len(selected_labs))
    
    for i, lab in enumerate(selected_labs):
        with cols[i]:
            st.markdown(f"### {lab.title()}")
            
            data = extractions.get(lab, {})
            thresholds = data.get("capability_thresholds", [])
            
            for threshold in thresholds:
                level_name = threshold.get("level_name", "Unknown")
                description = threshold.get("description", "No description")
                
                with st.expander(level_name):
                    st.markdown(description[:200] + "..." if len(description) > 200 else description)
                    
                    # Show triggers
                    triggers = threshold.get("triggers", [])
                    if triggers:
                        st.markdown("**Triggers:**")
                        for t in triggers[:3]:
                            domain = t.get("domain", "")
                            cap = t.get("capability", "")
                            st.markdown(f"- {domain}: {cap[:50]}...")
                    
                    # Show safeguards
                    safeguards = threshold.get("required_safeguards", [])
                    if safeguards:
                        st.markdown("**Safeguards:**")
                        for s in safeguards[:3]:
                            st.markdown(f"- {s[:50]}...")
