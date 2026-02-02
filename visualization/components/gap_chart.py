"""Gap analysis chart components for dashboard."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional


def render_gap_chart(analyzer, type_filter: Optional[list] = None):
    """Render a chart showing gap distribution by type."""
    gaps = analyzer.gaps
    
    if type_filter:
        gaps = [g for g in gaps if g.type.value in type_filter]
    
    if not gaps:
        st.info("No gaps match the current filters")
        return
    
    data = [{"Type": g.type.value.title(), "Severity": g.severity.value.title()} for g in gaps]
    df = pd.DataFrame(data)
    
    fig = px.histogram(
        df, x="Type", color="Severity",
        title="Gaps by Type and Severity",
        color_discrete_map={"High": "#FF6B6B", "Medium": "#FFE66D", "Low": "#4ECDC4"}
    )
    fig.update_layout(xaxis_title="Gap Type", yaxis_title="Count", height=350)
    st.plotly_chart(fig, use_container_width=True)


def render_severity_distribution(analyzer):
    """Render a pie chart of gap severity distribution."""
    gaps = analyzer.gaps
    severity_counts = {"High": 0, "Medium": 0, "Low": 0}
    for gap in gaps:
        severity_counts[gap.severity.value.title()] += 1
    
    fig = go.Figure(data=[go.Pie(
        labels=list(severity_counts.keys()),
        values=list(severity_counts.values()),
        hole=0.4,
        marker_colors=["#FF6B6B", "#FFE66D", "#4ECDC4"]
    )])
    fig.update_layout(title="Gap Severity Distribution", height=300)
    st.plotly_chart(fig, use_container_width=True)


def render_affected_labs_chart(analyzer):
    """Render a chart showing which labs are most affected by gaps."""
    gaps = analyzer.gaps
    lab_counts = {}
    for gap in gaps:
        for lab in gap.affected_labs:
            lab_counts[lab] = lab_counts.get(lab, 0) + 1
    
    df = pd.DataFrame([{"Lab": lab.title(), "Count": count} for lab, count in lab_counts.items()])
    if df.empty:
        st.info("No lab data available")
        return
    
    df = df.sort_values("Count", ascending=True)
    fig = px.bar(df, x="Count", y="Lab", orientation="h", title="Gaps Affecting Each Lab")
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
