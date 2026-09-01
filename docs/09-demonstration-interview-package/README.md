# Product Change Impact Assessment & Decision Readiness

## Session 6 — Demonstration & Interview Package

**Status:** Session 6 complete and merged — five-minute deterministic demo, static evidence extracts, 15-minute architecture/interview walkthrough, 30-minute technical-review walkthrough, 60-second explanation and 3-minute explanation  
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

### Milestone 3 — 30-minute technical-review walkthrough

- [`Thirty_Minute_Technical_Review_v0.1.md`](Thirty_Minute_Technical_Review_v0.1.md) — same architecture-first spine expanded with baseline/overlay enforcement, case-local lineage, bounded impact-analysis boundary, `RRR-v0.1` mechanics, Scenario B reuse/immutability, Decision persistence, historical reconstruction, integrity tests and bounded findings.

The 30-minute path distinguishes architecture decisions from implementation choices throughout. It uses repository inspection and committed static evidence by default; live execution is optional and must return immediately to the architectural statement being proved.

### Milestone 4 — verbal explanations

- [`Verbal_Explanations_v0.1.md`](Verbal_Explanations_v0.1.md) — one approximately 60-second and one approximately 3-minute role-neutral explanation, plus compression/expansion guidance and stable claim language.

Both verbal versions compress the same canonical narrative. They are not alternative stories and must retain the same public-safe limitations as the longer walkthroughs.

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

## Session 6 completion rule

The same architecture-first story is now available at five depths:

```text
~60 seconds
→ ~3 minutes
→ 5-minute deterministic demo
→ 15-minute architecture/interview walkthrough
→ 30-minute technical review
```

The Session 5 ten-slide presentation remains canonical at every depth. Session 6 adds only scripts, static evidence views and controlled review paths; it does not create a competing deck or source of truth.

Session 6 was accepted through protected PR #5 and passed the required verification workflow before merge and again on the post-merge `main` run. The next planned phase is Session 7 — independent review and correction. Session 8 release/archive work remains deferred until Session 7 is complete.
