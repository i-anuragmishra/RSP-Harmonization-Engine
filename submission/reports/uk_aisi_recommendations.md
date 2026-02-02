# Recommendations for UK AI Safety Institute

*Prepared: 2026-02-02*

## Executive Summary

These recommendations support UK AI Safety Institute's mission to evaluate 
frontier AI systems and develop safety standards. The harmonization framework 
enables consistent evaluation across different AI labs' responsible scaling policies.

## Key Recommendations for AISI Evaluation Work

### 1. Unified Risk Level Framework

**Priority:** HIGH

**Current Challenge:**
> Labs use ASL (1-4), CCL (1-2), Tiers (1-4), and Low/Medium/High/Critical with different semantics.

**Proposed Solution:**

Unified AI Risk Level Framework (UARLF):
- Level 1 MINIMAL: No meaningful incremental risk beyond widely available tools
- Level 2 EMERGING: Early signs of dangerous capabilities, no significant uplift
- Level 3 SIGNIFICANT: Substantially increases catastrophic misuse risk, requires mitigations
- Level 4 SEVERE: Could accelerate state-level threats, requires maximum safeguards
- Level 5 CRITICAL: Could contribute to existential risks, may require development pause

**AISI Application:** This standard enables consistent evaluation of models from different labs using a unified framework.

---

### 2. Standardized Autonomy Capability Definition

**Priority:** HIGH

**Current Challenge:**
> Autonomy means different things: self-replication (Anthropic), task completion (OpenAI), ML R&D (DeepMind).

**Proposed Solution:**

Autonomy Capability Taxonomy:
- A1 TASK AUTONOMY: Complete well-defined tasks without human oversight
- A2 RESOURCE AUTONOMY: Acquire resources independently
- A3 SELF-PRESERVATION: Take actions to ensure continued operation
- A4 SELF-REPLICATION: Create functional copies or spawn instances
- A5 RECURSIVE IMPROVEMENT: Meaningfully improve own capabilities
- A6 AI R&D ACCELERATION: Substantially accelerate AI development

**AISI Application:** This standard enables consistent evaluation of models from different labs using a unified framework.

---

### 3. CBRN Uplift Measurement Standard

**Priority:** HIGH

**Current Challenge:**
> Labs compare CBRN uplift to different baselines: web search, skilled search, non-expert baseline.

**Proposed Solution:**

CBRN Uplift Assessment Framework:
Baseline: Knowledge available to motivated non-expert using internet with 40 hours effort.
- U0 No Uplift: No information beyond baseline
- U1 Marginal: <25% time reduction vs baseline
- U2 Moderate: 25-50% time reduction OR synthesis not easily found
- U3 Significant: >50% time reduction OR actionable operational details
- U4 Substantial: Expert-level guidance OR novel pathways
- U5 Critical: Could enable novel agents OR lower barriers for state actors

**AISI Application:** This standard enables consistent evaluation of models from different labs using a unified framework.

---

### 4. Pause Commitment Protocol

**Priority:** HIGH

**Current Challenge:**
> All labs commit to pausing under extreme circumstances, but conditions are vague.

**Proposed Solution:**

AI Development Pause Protocol (ADPP):
Triggers: Level 4+ risk without safeguards, unexpected capability emergence, deceptive behaviors, government directive.
Procedure:
- IMMEDIATE (1 hour): Halt training, disable API access
- SHORT-TERM (24 hours): Notify governance board, regulators
- ASSESSMENT (7 days): Complete capability assessment
- DECISION (30 days): Resume with safeguards, restrict scope, extend pause, or discontinue
Transparency: Public disclosure within 7 days, detailed report to regulators within 30 days.

**AISI Application:** This standard enables consistent evaluation of models from different labs using a unified framework.

---

## Recommended AISI Actions

1. **Adopt unified risk level framework** for internal assessments
2. **Develop standardized evaluation protocols** based on proposed thresholds
3. **Coordinate with international partners** on terminology adoption
4. **Publish guidance** for labs on compliance with harmonized standards

## Coordination with International Partners

These recommendations are designed for international adoption. Coordination with:
- UK AISI
- US AISI
- EU AI Office
- Frontier Model Forum

will maximize effectiveness and reduce compliance burden on labs operating internationally.