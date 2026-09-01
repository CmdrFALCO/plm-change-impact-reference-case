# Product Change Impact Assessment & Decision Readiness

## Executive Brief

**Public-safe PLM Business Architecture reference case**  
**Release target:** `v0.1.0`

> **A product change becomes decision-ready only when current state, proposal, discovered impacts, domain conclusions, evidence, decision scope and authority are kept separate—and linked by deterministic, case-local and historically reconstructable rules.**

### The problem

A product change cannot be represented adequately as:

```text
Revision A → Revision B
```

That pair records succession, but not the basis on which a decision can be made. It does not identify the exact authoritative state evaluated, the configuration and usage context, the proposed scope, newly discovered impacts, required domain assessments, evidence used at assessment time, unresolved blockers, decision authority or the exact scope ultimately authorised or rejected.

When these concepts are collapsed, several false equivalences appear:

- discovered impact becomes assumed authorised scope;
- Evidence is treated as if it established Requirement compliance;
- package completeness is treated as approval permission;
- authority escalation is confused with a terminal Decision;
- later mutable source data can change the apparent meaning of a historical decision.

### The architectural response

The reference case separates the decision basis into explicit semantics:

```text
immutable Assessment Baseline
        +
versioned Change Item overlay
        ↓
Impact-analysis Execution
        ↓
Impact Candidates with structured provenance
        ↓
Assessment Obligations, Assessments and Assessment Evidence Uses
        ├─ Scope Revision Required → explicit scope amendment and new proposal cycle
        └─ no scope route
                    ↓
        Gate B: Decision Package Complete
                    ↓
        Authorisation Eligibility
                    ↓
        Required vs Current Authority
        ├─ insufficient → Escalated Process-history Entry
        └─ sufficient + explicit authority disposition → terminal Decision Record
                                                        ↓
                                           derived Handover View
```

The critical distinctions are:

- **Assessment Baseline vs Overlay Revision:** authoritative current-state snapshots remain immutable while the proposed state stays non-authoritative and versioned.
- **Impact Candidate vs Proposed Change Scope or Decision Scope:** discovery identifies what may be affected; it never authorises a change automatically.
- **Evidence Record vs Requirement Conclusion:** Evidence informs an Assessment; only the Assessment records the engineering conclusion.
- **Gate B vs Authorisation Eligibility vs authority sufficiency:** a complete package may still be substantively blocked or require a higher authority level.
- **Process-history Entry vs Decision Record:** return, scope revision and escalation keep the case open; only an explicit terminal authority disposition creates a Decision Record.

### What the three scenarios demonstrate

| Scenario | Architectural proof | Frozen result |
|---|---|---|
| **A — Authorised change** | A complete, eligible package with sufficient authority can be explicitly authorised and reconstructed historically. | `DEC-A01`; Case `Closed by Decision`; Handover View available. |
| **B — Scope amendment and selective reuse** | Discovered impact is not authorised scope; changing the proposal does not automatically change the baseline; historical Assessments are reused only when execution-relative rules permit it. | `HIST-B01`; `BL-B01` reused; two obligations remain open; Gate B `Incomplete`; no Decision. |
| **C — Authority escalation** | Decision-package completeness and substantive eligibility do not imply authority to decide. | Required `Elevated`, current `Standard`; `HIST-C01` Escalated; no Decision; Case remains `Decision Ready`. |

### Why the prototype matters

The executable demonstrator is not the main deliverable. It is the verification boundary for the architecture. The frozen scenarios run through the same application services used by the CLI and API, while independent expected oracles, integrity controls and historical reconstruction test whether the architecture is precise enough to execute without semantic shortcuts.

Recorded verification at the executable baseline:

```text
G00–G14: 15/15 PASS
Full regression: 185 passed
Final verification groups: 6/6 PASS
Repeated evidence generation: byte-identical
IT-16 cross-case injection families: 6/6 attempted, rejected and PASS
```

### Claim boundary

This project demonstrates deterministic conformance to a bounded synthetic reference case. It does **not** claim:

- fidelity to any company-specific PLM process, data model, workflow or authority structure;
- enterprise PLM completeness or production readiness;
- general arbitrary-graph impact discovery—the v0.1 impact adapter is deliberately fixture-bounded;
- automated engineering judgement or automated terminal approval.

The value of the case is the explicit, traceable chain from engineering problem to business architecture, information semantics, deterministic decisions, implementation controls, tests and evidence.

---

**Review paths:** [Architecture Index](../00-architecture-index.md) · [Architecture Traceability and Assurance Pack](../07-traceability-assurance/Architecture_Traceability_and_Assurance_Pack_v0.1.md) · [Verified Baseline](../../VERIFIED_BASELINE.md)
