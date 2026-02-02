# RSP Harmonization Engine

A tool for analyzing and harmonizing Responsible Scaling Policies (RSPs) across major AI labs. Extracts structured data from RSP documents, identifies gaps and inconsistencies, and generates harmonization recommendations for regulators.

## Overview

Major AI labs have published Responsible Scaling Policies using different terminology and frameworks:
- **Anthropic**: ASL levels (ASL-1 through ASL-4)
- **OpenAI**: Risk levels (Low, Medium, High, Critical)
- **Google DeepMind**: CCL levels (Below CCL, CCL-1, CCL-2)
- **Meta**: Tier system (Tier 1 through Tier 4)

This tool analyzes these frameworks to:
1. **Extract** structured data from RSP documents
2. **Map** equivalent terminology across frameworks
3. **Identify** gaps and inconsistencies
4. **Generate** harmonization recommendations for regulators

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

## Features

### Terminology Mapping
Maps equivalent risk levels across all frameworks to a unified 5-tier system:

| Unified Level | Anthropic | OpenAI | DeepMind | Meta |
|---------------|-----------|--------|----------|------|
| Minimal | ASL-1 | Low | - | Tier 1 |
| Emerging | ASL-2 | Medium | Below CCL | Tier 2 |
| Significant | ASL-3 | High | CCL-1 | Tier 3 |
| Severe | ASL-4 | - | CCL-2 | - |
| Critical | - | Critical | - | Tier 4 |

### Gap Analysis
Identifies inconsistencies across frameworks:
- **Threshold gaps**: Different bars for the same capability
- **Coverage gaps**: Some labs don't address certain risk domains
- **Definition gaps**: Same terms with different meanings
- **Terminology gaps**: Different naming conventions

### Harmonization Recommendations
Generates unified language suitable for:
- EU AI Act Code of Practice
- UK AI Safety Institute
- US AI Safety Institute
- International standards bodies

## Commands

| Command | Description |
|---------|-------------|
| `python main.py demo` | Run demo with prebuilt data |
| `python main.py analyze` | Run gap analysis |
| `python main.py harmonize` | Generate recommendations |
| `python main.py dashboard` | Launch Streamlit dashboard |
| `python main.py all` | Run full pipeline |
| `python create_submission.py` | Generate complete export package |

## Project Structure

```
rsp-harmonization-engine/
├── main.py                    # Main entry point
├── create_submission.py       # Generate export package
├── requirements.txt           # Python dependencies
├── config/
│   └── settings.py            # Configuration management
├── src/
│   ├── extraction/            # PDF parsing and LLM extraction
│   ├── comparison/            # Terminology mapping and gap analysis
│   └── harmonization/         # Recommendation generation
├── visualization/
│   ├── dashboard.py           # Streamlit dashboard
│   └── components/            # Dashboard components
├── data/
│   └── schemas/               # JSON schemas
├── outputs/
│   ├── reports/               # Generated reports
│   └── harmonized_language/   # Recommendations
└── submission/                # Complete export package
```

## Key Results

### Gap Analysis Summary
- **11 gaps identified** across 4 major frameworks
- **5 high-severity gaps** requiring immediate attention
- Key issues: autonomy definitions, CBRN uplift baselines, pause commitments

### Top Recommendations
1. **Unified Risk Level Framework (UARLF)** - 5-tier standardized system
2. **Autonomy Capability Taxonomy** - 6-dimension breakdown (A1-A6)
3. **CBRN Uplift Assessment Framework** - Standardized baseline and metrics
4. **AI Development Pause Protocol** - Clear triggers and procedures

## Output Files

After running `python create_submission.py`:

- `submission/SUMMARY.md` - Complete analysis summary
- `submission/data/` - JSON and CSV data files
- `submission/visualizations/` - Charts (HTML + PNG)
- `submission/reports/` - Formatted recommendation documents

## Tech Stack

- **Python 3.10+**
- **Anthropic Claude API** - LLM extraction (optional)
- **PyMuPDF / pdfplumber** - PDF parsing
- **Pydantic** - Data validation
- **Streamlit** - Interactive dashboard
- **Plotly** - Visualizations
- **Pandas** - Data manipulation

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Required for PDF extraction (optional - prebuilt data works without)
ANTHROPIC_API_KEY=your_key_here
```

## License

MIT License
