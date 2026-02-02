# RSP Harmonization Recommendations

*Generated: 2026-02-02*

## Executive Summary

This document provides harmonization recommendations for Responsible Scaling Policies (RSPs) 
across major AI labs to support regulatory frameworks and international coordination.

**Total Recommendations:** 7
- High Priority: 4
- Medium Priority: 3

---

## Terminology Standardization

### HARM-001: Unified Risk Level Framework

**Priority:** HIGH | **Confidence:** High

**Current State:** Labs use ASL (1-4), CCL (1-2), Tiers (1-4), and Low/Medium/High/Critical with different semantics.

**Proposed Language:**
Unified AI Risk Level Framework (UARLF):
- Level 1 MINIMAL: No meaningful incremental risk beyond widely available tools
- Level 2 EMERGING: Early signs of dangerous capabilities, no significant uplift
- Level 3 SIGNIFICANT: Substantially increases catastrophic misuse risk, requires mitigations
- Level 4 SEVERE: Could accelerate state-level threats, requires maximum safeguards
- Level 5 CRITICAL: Could contribute to existential risks, may require development pause

**Rationale:** A unified 5-tier framework provides clearer mapping across existing frameworks while adding granularity for dangerous systems.

**Applicable To:** EU AI Office, UK AISI, US AISI, AI Labs, ISO Standards Bodies

**Implementation Notes:** Labs should publish mapping tables. Transition period of 12 months recommended.

---

### HARM-007: Terminology Glossary

**Priority:** MEDIUM | **Confidence:** High

**Current State:** Terms like safeguard, mitigation, control, dangerous capability used inconsistently.

**Proposed Language:**
Unified RSP Terminology:
- CAPABILITY: Measurable skill an AI system can perform
- DANGEROUS CAPABILITY: Capability that could lead to significant harm if misused
- SAFEGUARD: Proactive measure to prevent dangerous capabilities (prevents risk)
- MITIGATION: Reactive measure to reduce impact of existing capabilities (reduces severity)
- CONTROL: Mechanism limiting how capability can be used
- THRESHOLD: Capability level triggering specific safeguard requirements
- UPLIFT: Incremental benefit beyond defined baseline
- PAUSE: Temporary halt pending safety concern resolution

**Rationale:** Consistent terminology reduces confusion and enables clearer communication.

**Applicable To:** EU AI Office, UK AISI, US AISI, AI Labs, Media, General Public

**Implementation Notes:** Should be incorporated into regulatory guidance and lab communications.

---

## Threshold Alignment

### HARM-002: Standardized Autonomy Capability Definition

**Priority:** HIGH | **Confidence:** Medium

**Current State:** Autonomy means different things: self-replication (Anthropic), task completion (OpenAI), ML R&D (DeepMind).

**Proposed Language:**
Autonomy Capability Taxonomy:
- A1 TASK AUTONOMY: Complete well-defined tasks without human oversight
- A2 RESOURCE AUTONOMY: Acquire resources independently
- A3 SELF-PRESERVATION: Take actions to ensure continued operation
- A4 SELF-REPLICATION: Create functional copies or spawn instances
- A5 RECURSIVE IMPROVEMENT: Meaningfully improve own capabilities
- A6 AI R&D ACCELERATION: Substantially accelerate AI development

**Rationale:** Breaking down autonomy into specific sub-capabilities allows for more precise thresholds.

**Applicable To:** EU AI Office, UK AISI, US AISI, AI Labs, Academic Researchers

**Implementation Notes:** Each autonomy dimension should have separate thresholds.

---

### HARM-003: CBRN Uplift Measurement Standard

**Priority:** HIGH | **Confidence:** Medium

**Current State:** Labs compare CBRN uplift to different baselines: web search, skilled search, non-expert baseline.

**Proposed Language:**
CBRN Uplift Assessment Framework:
Baseline: Knowledge available to motivated non-expert using internet with 40 hours effort.
- U0 No Uplift: No information beyond baseline
- U1 Marginal: <25% time reduction vs baseline
- U2 Moderate: 25-50% time reduction OR synthesis not easily found
- U3 Significant: >50% time reduction OR actionable operational details
- U4 Substantial: Expert-level guidance OR novel pathways
- U5 Critical: Could enable novel agents OR lower barriers for state actors

**Rationale:** A standardized uplift scale with defined baseline enables consistent assessment across labs.

**Applicable To:** EU AI Office, UK AISI, US AISI, AI Labs, Biosecurity Experts

**Implementation Notes:** Requires development of standardized evaluation protocols.

---

## Safeguard Requirements

### HARM-004: Security Level Standardization

**Priority:** MEDIUM | **Confidence:** High

**Current State:** Security requirements vary: hardened infrastructure, Security Level Alpha/Omega, weight security.

**Proposed Language:**
AI Security Level Framework (ASLF):
- ASLF-1 Standard: Industry-standard access controls, regular audits
- ASLF-2 Enhanced: MFA, encrypted weights, air-gapped training, background checks
- ASLF-3 Maximum: HSMs, isolated compute, continuous monitoring, supply chain security
- ASLF-4 Sovereign: ASLF-3 plus government oversight, classified-level physical security

**Rationale:** Clear security tiers enable regulators to set requirements and labs to demonstrate compliance.

**Applicable To:** EU AI Office, UK AISI, US AISI, AI Labs

**Implementation Notes:** Labs should undergo third-party security audits for certification.

---

## Process Harmonization

### HARM-005: Pause Commitment Protocol

**Priority:** HIGH | **Confidence:** Medium

**Current State:** All labs commit to pausing under extreme circumstances, but conditions are vague.

**Proposed Language:**
AI Development Pause Protocol (ADPP):
Triggers: Level 4+ risk without safeguards, unexpected capability emergence, deceptive behaviors, government directive.
Procedure:
- IMMEDIATE (1 hour): Halt training, disable API access
- SHORT-TERM (24 hours): Notify governance board, regulators
- ASSESSMENT (7 days): Complete capability assessment
- DECISION (30 days): Resume with safeguards, restrict scope, extend pause, or discontinue
Transparency: Public disclosure within 7 days, detailed report to regulators within 30 days.

**Rationale:** Clear, verifiable pause conditions with defined timelines enable external oversight.

**Applicable To:** EU AI Office, UK AISI, US AISI, AI Labs, Frontier Model Forum

**Implementation Notes:** Labs should pre-designate governance contacts. Annual pause drills recommended.

---

### HARM-006: Evaluation Transparency Standard

**Priority:** MEDIUM | **Confidence:** High

**Current State:** Evaluation requirements vary in specificity and transparency across frameworks.

**Proposed Language:**
AI Capability Evaluation Transparency Standard (ACETS):
Required Disclosures per release:
1. Capability Scorecard across standardized benchmarks
2. Risk Domain Assessment (CBRN, cyber, autonomy, persuasion)
3. Red Team Summary (high-level findings)
4. Uplift Assessment with methodology
5. Autonomy Profile (A1-A6 dimensions)
Timeline: Pre-deployment evaluation, public scorecard at deployment, quarterly monitoring, annual transparency report.

**Rationale:** Standardized evaluation reporting enables comparison across labs and supports evidence-based regulation.

**Applicable To:** EU AI Office, UK AISI, US AISI, AI Labs, Academic Researchers

**Implementation Notes:** Requires development of standardized benchmark suite.

---
