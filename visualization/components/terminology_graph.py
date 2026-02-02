"""Terminology relationship graph component for dashboard."""

import streamlit as st
import plotly.graph_objects as go
from typing import Optional


def render_terminology_graph(mapper, selected_labs: Optional[list] = None):
    """Render a simple mapping visualization."""
    labs = selected_labs or mapper.get_all_labs()
    unified_levels = ["MINIMAL", "EMERGING", "SIGNIFICANT", "SEVERE", "CRITICAL"]
    
    # Build Sankey data
    labels = [f"[Unified] {level.title()}" for level in unified_levels]
    unified_indices = {level: i for i, level in enumerate(unified_levels)}
    
    sources, targets, values, colors = [], [], [], []
    lab_color_map = {
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
            colors.append(lab_color_map.get(lab, "rgba(128, 128, 128, 0.8)"))
            idx += 1
    
    if not sources:
        st.info("No mapping data available")
        return
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(pad=15, thickness=20, label=labels),
        link=dict(source=sources, target=targets, value=values, color=colors)
    )])
    fig.update_layout(title="Risk Level Mappings", height=400)
    st.plotly_chart(fig, use_container_width=True)
