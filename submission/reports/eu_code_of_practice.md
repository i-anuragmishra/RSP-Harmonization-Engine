# Recommendations for EU AI Act Code of Practice

*Prepared: 2026-02-02*

## Context

These recommendations support the development of codes of practice under Article 56 
of the EU AI Act, specifically for General-Purpose AI (GPAI) models with systemic risk.

## Alignment with EU AI Act Requirements

The EU AI Act requires providers of GPAI models with systemic risk to:
- Perform model evaluations including adversarial testing
- Assess and mitigate systemic risks
- Report serious incidents
- Ensure adequate cybersecurity protection

The following harmonization recommendations directly support these requirements.

---

## Risk Assessment Thresholds

### Standardized Autonomy Capability Definition

**Recommendation ID:** HARM-002

**EU AI Act Alignment:**
- Supports Article 55 systemic risk assessment

**Proposed Standard:**

Autonomy Capability Taxonomy:
- A1 TASK AUTONOMY: Complete well-defined tasks without human oversight
- A2 RESOURCE AUTONOMY: Acquire resources independently
- A3 SELF-PRESERVATION: Take actions to ensure continued operation
- A4 SELF-REPLICATION: Create functional copies or spawn instances
- A5 RECURSIVE IMPROVEMENT: Meaningfully improve own capabilities
- A6 AI R&D ACCELERATION: Substantially accelerate AI development

**Implementation Guidance:** Each autonomy dimension should have separate thresholds.

---

### CBRN Uplift Measurement Standard

**Recommendation ID:** HARM-003

**EU AI Act Alignment:**
- Supports Article 55 systemic risk assessment

**Proposed Standard:**

CBRN Uplift Assessment Framework:
Baseline: Knowledge available to motivated non-expert using internet with 40 hours effort.
- U0 No Uplift: No information beyond baseline
- U1 Marginal: <25% time reduction vs baseline
- U2 Moderate: 25-50% time reduction OR synthesis not easily found
- U3 Significant: >50% time reduction OR actionable operational details
- U4 Substantial: Expert-level guidance OR novel pathways
- U5 Critical: Could enable novel agents OR lower barriers for state actors

**Implementation Guidance:** Requires development of standardized evaluation protocols.

---

## Safeguard Requirements

### Security Level Standardization

**Recommendation ID:** HARM-004

**EU AI Act Alignment:**
- Supports Article 55 risk mitigation obligations

**Proposed Standard:**

AI Security Level Framework (ASLF):
- ASLF-1 Standard: Industry-standard access controls, regular audits
- ASLF-2 Enhanced: MFA, encrypted weights, air-gapped training, background checks
- ASLF-3 Maximum: HSMs, isolated compute, continuous monitoring, supply chain security
- ASLF-4 Sovereign: ASLF-3 plus government oversight, classified-level physical security

**Implementation Guidance:** Labs should undergo third-party security audits for certification.

---

## Procedural Requirements

### Pause Commitment Protocol

**Recommendation ID:** HARM-005

**EU AI Act Alignment:**
- Supports Article 55 model evaluation and incident reporting

**Proposed Standard:**

AI Development Pause Protocol (ADPP):
Triggers: Level 4+ risk without safeguards, unexpected capability emergence, deceptive behaviors, government directive.
Procedure:
- IMMEDIATE (1 hour): Halt training, disable API access
- SHORT-TERM (24 hours): Notify governance board, regulators
- ASSESSMENT (7 days): Complete capability assessment
- DECISION (30 days): Resume with safeguards, restrict scope, extend pause, or discontinue
Transparency: Public disclosure within 7 days, detailed report to regulators within 30 days.

**Implementation Guidance:** Labs should pre-designate governance contacts. Annual pause drills recommended.

---

### Evaluation Transparency Standard

**Recommendation ID:** HARM-006

**EU AI Act Alignment:**
- Supports Article 55 model evaluation and incident reporting

**Proposed Standard:**

AI Capability Evaluation Transparency Standard (ACETS):
Required Disclosures per release:
1. Capability Scorecard across standardized benchmarks
2. Risk Domain Assessment (CBRN, cyber, autonomy, persuasion)
3. Red Team Summary (high-level findings)
4. Uplift Assessment with methodology
5. Autonomy Profile (A1-A6 dimensions)
Timeline: Pre-deployment evaluation, public scorecard at deployment, quarterly monitoring, annual transparency report.

**Implementation Guidance:** Requires development of standardized benchmark suite.

---

## Terminology Standards

### Unified Risk Level Framework

**Recommendation ID:** HARM-001

**EU AI Act Alignment:**
- Supports harmonized implementation across member states

**Proposed Standard:**

Unified AI Risk Level Framework (UARLF):
- Level 1 MINIMAL: No meaningful incremental risk beyond widely available tools
- Level 2 EMERGING: Early signs of dangerous capabilities, no significant uplift
- Level 3 SIGNIFICANT: Substantially increases catastrophic misuse risk, requires mitigations
- Level 4 SEVERE: Could accelerate state-level threats, requires maximum safeguards
- Level 5 CRITICAL: Could contribute to existential risks, may require development pause

**Implementation Guidance:** Labs should publish mapping tables. Transition period of 12 months recommended.

---

### Terminology Glossary

**Recommendation ID:** HARM-007

**EU AI Act Alignment:**
- Supports harmonized implementation across member states

**Proposed Standard:**

Unified RSP Terminology:
- CAPABILITY: Measurable skill an AI system can perform
- DANGEROUS CAPABILITY: Capability that could lead to significant harm if misused
- SAFEGUARD: Proactive measure to prevent dangerous capabilities (prevents risk)
- MITIGATION: Reactive measure to reduce impact of existing capabilities (reduces severity)
- CONTROL: Mechanism limiting how capability can be used
- THRESHOLD: Capability level triggering specific safeguard requirements
- UPLIFT: Incremental benefit beyond defined baseline
- PAUSE: Temporary halt pending safety concern resolution

**Implementation Guidance:** Should be incorporated into regulatory guidance and lab communications.

---

## Implementation Timeline

1. **Phase 1 (0-6 months):** Adopt unified terminology glossary
2. **Phase 2 (6-12 months):** Implement standardized evaluation frameworks
3. **Phase 3 (12-18 months):** Full compliance with harmonized thresholds

## Contact

For questions about these recommendations, contact the RSP Harmonization Working Group.