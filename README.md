# RSP Harmonization Engine

**Track 3 Submission - AI Safety Hackathon**

> A tool for analyzing and harmonizing Responsible Scaling Policies (RSPs) across major AI labs. Extracts structured data, identifies gaps and inconsistencies, and generates harmonization recommendations for regulators.

---

## Team Information

| | |
|---|---|
| **Team Name** | Anurag |
| **Team Member** | Anurag Mishra |
| **Affiliation** | Independent |
| **Track** | Track 3 - RSP Harmonization |

---

## Problem Statement

Major AI labs have published Responsible Scaling Policies using incompatible terminology:

| Lab | Framework | Risk Levels |
|-----|-----------|-------------|
| Anthropic | RSP v2.2 | ASL-1, ASL-2, ASL-3, ASL-4 |
| OpenAI | Preparedness Framework v2.0 | Low, Medium, High, Critical |
| Google DeepMind | Frontier Safety Framework v3.0 | Below CCL, CCL-1, CCL-2 |
| Meta | Frontier AI Framework v1.0 | Tier 1, Tier 2, Tier 3, Tier 4 |

This inconsistency makes it difficult for regulators to create unified AI safety policy.

---

## Solution

The RSP Harmonization Engine:

1. **Extracts** structured data from 4 major lab RSP documents
2. **Maps** equivalent terminology across ASL/CCL/Tier frameworks
3. **Identifies** 11 gaps and inconsistencies (5 high severity)
4. **Generates** 7 harmonization recommendations for regulators
5. **Provides** interactive dashboard and exportable reports

---

## Key Results

### Gap Analysis
- **11 total gaps** identified across frameworks
- **5 high severity** issues requiring immediate attention
- Key problems: autonomy definitions, CBRN baselines, pause commitments

### Top Gaps Found
| Gap ID | Issue | Severity |
|--------|-------|----------|
| THR-AUT-001 | Autonomy Threshold Misalignment | HIGH |
| THR-CBR-001 | CBRN Uplift Definition Inconsistency | HIGH |
| TERM-001 | Risk Level Naming Inconsistency | HIGH |
| DEF-PAU-001 | Pause Commitment Ambiguity | HIGH |
| THR-RND-001 | AI R&D Acceleration Threshold Divergence | HIGH |

### Harmonization Recommendations
| ID | Recommendation | Priority |
|----|----------------|----------|
| HARM-001 | Unified 5-Tier Risk Level Framework | HIGH |
| HARM-002 | Standardized Autonomy Capability Taxonomy (A1-A6) | HIGH |
| HARM-003 | CBRN Uplift Measurement Standard | HIGH |
| HARM-005 | AI Development Pause Protocol | HIGH |

### Terminology Mapping
| Unified Level | Anthropic | OpenAI | DeepMind | Meta |
|---------------|-----------|--------|----------|------|
| Minimal | ASL-1 | Low | - | Tier 1 |
| Emerging | ASL-2 | Medium | Below CCL | Tier 2 |
| Significant | ASL-3 | High | CCL-1 | Tier 3 |
| Severe | ASL-4 | - | CCL-2 | - |
| Critical | - | Critical | - | Tier 4 |

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run demo (no API key needed)
python main.py demo

# Launch interactive dashboard
python main.py dashboard

# Generate complete submission package
python create_submission.py
```

---

## Project Structure

```
RSP-Harmonization-Engine/
├── main.py                    # Main entry point
├── create_submission.py       # Generate export package
├── requirements.txt           # Python dependencies
├── config/                    # Configuration
├── src/
│   ├── extraction/            # PDF parsing, LLM extraction
│   ├── comparison/            # Terminology mapping, gap analysis
│   └── harmonization/         # Recommendation generation
├── visualization/
│   └── dashboard.py           # Streamlit dashboard
├── outputs/                   # Generated reports
└── submission/                # Complete export package
    ├── SUMMARY.md
    ├── data/                  # JSON, CSV data files
    ├── visualizations/        # Charts (HTML + PNG)
    └── reports/               # Formatted documents
```

---

## Features

### 1. Terminology Mapping
Maps equivalent risk levels across all frameworks to a unified 5-tier system.

### 2. Gap Analysis
Identifies inconsistencies:
- **Threshold gaps** - Different bars for same capability
- **Coverage gaps** - Missing risk domains
- **Definition gaps** - Same terms, different meanings
- **Terminology gaps** - Incompatible naming

### 3. Harmonization Recommendations
Generates unified language for:
- EU AI Act Code of Practice
- UK AI Safety Institute
- US AI Safety Institute
- International standards bodies

### 4. Interactive Dashboard
Streamlit-based exploration with:
- Framework overview
- Level mapping visualization
- Domain coverage heatmap
- Gap analysis explorer
- Recommendation viewer

---

## Output Files

The `/submission/` folder contains:

| File | Description |
|------|-------------|
| `SUMMARY.md` | Complete analysis summary |
| `data/all_extractions.json` | Structured data from all labs |
| `data/gap_analysis.json` | All identified gaps |
| `data/recommendations.json` | Harmonization recommendations |
| `visualizations/*.png` | Charts and diagrams |
| `reports/executive_brief.md` | Executive summary |
| `reports/eu_code_of_practice.md` | EU-formatted recommendations |

---

## Tech Stack

- **Python 3.10+**
- **Anthropic Claude API** - LLM extraction (optional)
- **PyMuPDF / pdfplumber** - PDF parsing
- **Pydantic** - Data validation
- **Streamlit** - Interactive dashboard
- **Plotly** - Visualizations
- **Pandas** - Data manipulation

---

## Target Audience

This tool is designed for:
- **EU AI Office** - AI Act Code of Practice development
- **UK AISI** - Frontier AI safety evaluation
- **US AISI** - National AI safety standards
- **ISO/IEC** - International AI standards
- **Frontier Model Forum** - Industry coordination

---

## Demo

### Terminal Output
```
╭──────────────────────────────────────────────────────────────────╮
│ RSP Harmonization Engine - Demo                                  │
╰──────────────────────────────────────────────────────────────────╯

1. Extracted Data Summary
  ✓ Anthropic: RSP v2.2 (4 levels)
  ✓ OpenAI: Preparedness Framework v2.0 (4 levels)
  ✓ DeepMind: Frontier Safety Framework v3.0 (4 levels)
  ✓ Meta: Frontier AI Framework v1.0 (4 levels)

2. Gap Analysis
  Total: 11 gaps (5 high severity)

3. Harmonization Recommendations
  Total: 7 recommendations
```

### Dashboard
Launch with `python main.py dashboard` and access at `http://localhost:8501`

---

## License

MIT License

---

## Acknowledgments

- RSP documents from Anthropic, OpenAI, Google DeepMind, and Meta
- METR's "Common Elements of Frontier AI Safety Policies" analysis
- Frontier Model Forum framework comparisons

---

**Built for AI Safety Hackathon - Track 3: RSP Harmonization**

*Team Anurag | Anurag Mishra | Independent*
