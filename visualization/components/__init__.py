"""Dashboard components for visualization."""

from .comparison_table import render_comparison_table
from .gap_chart import render_gap_chart, render_severity_distribution
from .terminology_graph import render_terminology_graph

__all__ = [
    "render_comparison_table",
    "render_gap_chart",
    "render_severity_distribution",
    "render_terminology_graph",
]
