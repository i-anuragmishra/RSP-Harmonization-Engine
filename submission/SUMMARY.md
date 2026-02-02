# RSP Harmonization Engine - Complete Results

Generated: 2026-02-02 01:48

## Overview

This package contains the complete analysis of Responsible Scaling Policies (RSPs) from 4 major AI labs:
- **Anthropic** - RSP v2.2 (October 2024)
- **OpenAI** - Preparedness Framework v2.0 (April 2025)
- **Google DeepMind** - Frontier Safety Framework v3.0 (October 2025)
- **Meta** - Frontier AI Framework v1.0 (2025)

## Key Findings

### Gap Analysis
- **Total Gaps Identified:** 11
- **High Severity:** 5
- **Medium Severity:** 5
- **Low Severity:** 1

### Top High-Severity Gaps

#### THR-AUT-001: Autonomy Threshold Misalignment
- **Type:** Threshold
- **Affected Labs:** anthropic, openai, deepmind, meta
- **Description:** Labs define 'dangerous autonomy' differently. Anthropic focuses on self-replication and resource acquisition, while OpenAI emphasizes general autonomous task completion, and DeepMind tracks ML R&D automation specifically.
- **Recommendation:** Define standardized autonomy metrics: (1) Self-replication capability, (2) Resource acquisition, (3) Task completion without oversight, (4) AI R&D acceleration

#### THR-RND-001: AI R&D Acceleration Threshold Divergence
- **Type:** Threshold
- **Affected Labs:** anthropic, deepmind
- **Description:** Different labs have vastly different thresholds for when AI-assisted R&D becomes concerning. Some treat any meaningful acceleration as high-risk, others focus only on autonomous research.
- **Recommendation:** Establish quantitative metrics for AI R&D acceleration (e.g., X% reduction in development time, capability to discover novel architectures)

#### THR-CBR-001: CBRN Uplift Definition Inconsistency
- **Type:** Threshold
- **Affected Labs:** anthropic, openai, deepmind, meta
- **Description:** 'Meaningful uplift' for CBRN capabilities is defined differently. Some labs compare to 'web search baseline', others to 'non-expert baseline', with unclear equivalence.
- **Recommendation:** Define standardized CBRN uplift metrics with specific baseline comparisons and quantitative uplift thresholds

#### TERM-001: Risk Level Naming Inconsistency
- **Type:** Terminology
- **Affected Labs:** anthropic, openai, deepmind, meta
- **Description:** Labs use completely different naming conventions for risk levels, making cross-framework comparison difficult for regulators and researchers.
- **Recommendation:** Adopt a unified 5-tier framework: Minimal, Emerging, Significant, Severe, Critical

#### DEF-PAU-001: Pause Commitment Ambiguity
- **Type:** Definition
- **Affected Labs:** anthropic, openai, deepmind, meta
- **Description:** While all labs commit to pausing under extreme circumstances, the specific conditions and duration are often vague.
- **Recommendation:** Define clear, verifiable pause conditions with specific capability thresholds and safeguard requirements

## Harmonization Recommendations

7 recommendations generated across 4 categories:
- Terminology Standardization
- Threshold Alignment
- Safeguard Requirements
- Process Harmonization

### High Priority Recommendations

#### HARM-001: Unified Risk Level Framework
**Current State:** Labs use ASL (1-4), CCL (1-2), Tiers (1-4), and Low/Medium/High/Critical with different semantics.

**Proposed:**
Unified AI Risk Level Framework (UARLF):
- Level 1 MINIMAL: No meaningful incremental risk beyond widely available tools
- Level 2 EMERGING: Early signs of dangerous capabilities, no significant uplift
- Level 3 SIGNIFICANT: Substantially increases catastrophic misuse risk, requires mitigations
- Level 4 SEVERE: Could accelerate state-level threats, requires maximum safeguards
- Level 5 CRITICAL: Could contribute to existential risks, may require development pause

**Applicable To:** EU AI Office, UK AISI, US AISI, AI Labs, ISO Standards Bodies

#### HARM-002: Standardized Autonomy Capability Definition
**Current State:** Autonomy means different things: self-replication (Anthropic), task completion (OpenAI), ML R&D (DeepMind).

**Proposed:**
Autonomy Capability Taxonomy:
- A1 TASK AUTONOMY: Complete well-defined tasks without human oversight
- A2 RESOURCE AUTONOMY: Acquire resources independently
- A3 SELF-PRESERVATION: Take actions to ensure continued operation
- A4 SELF-REPLICATION: Create functional copies or spawn instances
- A5 RECURSIVE IMPROVEMENT: Meaningfully improve own capabilities
- A6 AI R&D ACCELERATION: Substantially accelerate AI development

**Applicable To:** EU AI Office, UK AISI, US AISI, AI Labs, Academic Researchers

#### HARM-003: CBRN Uplift Measurement Standard
**Current State:** Labs compare CBRN uplift to different baselines: web search, skilled search, non-expert baseline.

**Proposed:**
CBRN Uplift Assessment Framework:
Baseline: Knowledge available to motivated non-expert using internet with 40 hours effort.
- U0 No Uplift: No information beyond baseline
- U1 Marginal: <25% time reduction vs baseline
- U2 Moderate: 25-50% time reduction OR synthesis not easily found
- U3 Significant: >50% time reduction OR actionable operational details
- U4 Substantial: Expert-level guidance OR novel pathways
- U5 Critical: Could enable novel agents OR lower barriers for state actors

**Applicable To:** EU AI Office, UK AISI, US AISI, AI Labs, Biosecurity Experts

#### HARM-005: Pause Commitment Protocol
**Current State:** All labs commit to pausing under extreme circumstances, but conditions are vague.

**Proposed:**
AI Development Pause Protocol (ADPP):
Triggers: Level 4+ risk without safeguards, unexpected capability emergence, deceptive behaviors, government directive.
Procedure:
- IMMEDIATE (1 hour): Halt training, disable API access
- SHORT-TERM (24 hours): Notify governance board, regulators
- ASSESSMENT (7 days): Complete capability assessment
- DECISION (30 days): Resume with safeguards, restrict scope, extend pause, or discontinue
Transparency: Public disclosure within 7 days, detailed report to regulators within 30 days.

**Applicable To:** EU AI Office, UK AISI, US AISI, AI Labs, Frontier Model Forum

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
