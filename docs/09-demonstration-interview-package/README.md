# Product Change Impact Assessment & Decision Readiness

## Session 6 — Demonstration & Interview Package

**Status:** Milestones 1–2 complete — five-minute deterministic demo, static evidence extracts and 15-minute architecture/interview walkthrough  
**Release target:** `v0.1.0`  
**Authority:** Derived communication material only; subordinate to the frozen architecture, code, tests and committed evidence

---

## Purpose

This directory adds the demonstration layer for the completed reference case without changing its architecture, scenario semantics or implementation claims.

The narrative remains:

```text
problem
→ architecture
→ scenarios
→ controlled implementation
→ verification evidence
```

The executable prototype is shown only where it proves an architectural statement. It is not presented as the primary deliverable or as an enterprise PLM application.

## Authority and boundaries

The authoritative precedence remains:

```text
Business Architecture v0.3.1
→ Logical Information Model v0.3.2
→ Scenario Data Definition v0.1
→ Readiness and Routing Rules v0.1 / RRR-v0.1
→ Solution Architecture v0.1
→ Prototype Implementation Plan v0.1
→ code, tests and evidence
```

The Session 5 canonical package remains the visual source:

- [`../08-executive-visual-package/Canonical_Package_Specification_v0.1.md`](../08-executive-visual-package/Canonical_Package_Specification_v0.1.md)
- [`../08-executive-visual-package/Product_Change_Impact_Decision_Readiness_Presentation_v0.1.pdf`](../08-executive-visual-package/Product_Change_Impact_Decision_Readiness_Presentation_v0.1.pdf)

Do not use this package to add PLM functionality, change Scenario A–C outcomes, imply automated engineering judgement, claim company-specific process fidelity, claim general arbitrary-graph impact discovery or present the Python/FastAPI/SQLite implementation as the main story.

## Completed Session 6 material

### Milestone 1 — five-minute deterministic demo and evidence views

- [`Five_Minute_Deterministic_Demo_v0.1.md`](Five_Minute_Deterministic_Demo_v0.1.md) — exact architecture-first five-minute live/static path.
- [`evidence-extracts/01_scenario_a_terminal_basis.md`](evidence-extracts/01_scenario_a_terminal_basis.md) — authorised terminal Decision basis.
- [`evidence-extracts/02_scenario_b_scope_amendment.md`](evidence-extracts/02_scenario_b_scope_amendment.md) — explicit scope-revision loop and baseline reuse.
- [`evidence-extracts/03_scenario_b_reuse_and_readiness.md`](evidence-extracts/03_scenario_b_reuse_and_readiness.md) — execution-relative Assessment reuse and remaining obligations.
- [`evidence-extracts/04_scenario_c_authority_escalation.md`](evidence-extracts/04_scenario_c_authority_escalation.md) — complete package with insufficient authority and no Decision.
- [`evidence-extracts/05_verification_evidence.md`](evidence-extracts/05_verification_evidence.md) — verification groups, regression boundary and IT-16 injection results.

### Milestone 2 — 15-minute architecture/interview walkthrough

- [`Fifteen_Minute_Architecture_Walkthrough_v0.1.md`](Fifteen_Minute_Architecture_Walkthrough_v0.1.md) — canonical ten-slide walkthrough with exact timing, evidence inserts, interview cut points and claim discipline.

The 15-minute standard path is static-first. Live execution remains available through the separate five-minute demo when explicitly useful. This prevents the implementation interface from displacing the architecture narrative.

## Evidence-extract rule

The files under `evidence-extracts/` are **static communication views** of already committed evidence. They are not new scenario oracles, business objects or verification results.

When an extract and a frozen artefact or committed evidence file differ, the frozen artefact/evidence file is authoritative.

Primary committed evidence used here:

```text
evidence/scenario_a_actual.json
evidence/scenario_b_actual.json
evidence/scenario_c_actual.json
evidence/decision_DEC-A01_basis.json
evidence/integrity_results.json
evidence/verification_summary.md
VERIFIED_BASELINE.md
```

## Remaining Session 6 material

Derive next from the same canonical presentation and accepted evidence set:

1. 30-minute technical-review walkthrough;
2. 60-second verbal explanation;
3. 3-minute verbal explanation.

No second canonical deck is required. The Session 5 presentation remains canonical; Session 6 progressively reveals additional evidence depth around it.
