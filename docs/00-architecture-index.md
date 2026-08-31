# Product Change Impact Assessment & Decision Readiness

## Architecture Index

**Document type:** Publication navigation and frozen-authority register  
**Status:** Documentation-only; does not redefine frozen semantics  
**Repository:** `CmdrFALCO/plm-change-impact-reference-case`  
**Release target:** `v0.1.0`  
**Verified implementation baseline:** `7a5733fc7042e33a790db12278f8776d047eb4b6`

---

# 1. Purpose

This index makes the architecture-first structure of the reference case directly inspectable.

The six documents below are the frozen authority chain. The executable demonstrator, tests and evidence prove that the frozen semantics can execute deterministically; they do not replace or redefine the architecture.

This index is navigation and release metadata only. When any wording here conflicts with a frozen artefact, the frozen artefact wins according to the precedence order in §4.

---

# 2. Public-safe boundary

This is a synthetic automotive PLM reference case developed for portfolio, learning and architecture-verification purposes.

It does **not** reproduce or claim to represent:

- a company-specific PLM process, workflow, organisation or authority model;
- proprietary product structures, identifiers, data models or system behaviour;
- an enterprise-ready PLM platform;
- a general arbitrary-graph impact-discovery engine;
- automated engineering judgement or automated terminal approval.

All scenario names, identifiers, actors, products, requirements, evidence records and timestamps are synthetic.

---

# 3. What the project demonstrates

The reference case demonstrates the translation chain:

```text
engineering product-change problem
        ↓
business capability and process boundary
        ↓
product/change information semantics
        ↓
deterministic routing and readiness rules
        ↓
solution and implementation architecture
        ↓
executable scenarios, integrity controls and evidence
```

The core architectural construction is:

> **immutable Assessment Baseline + versioned Change Item overlay**

The case deliberately keeps current state, proposal, evaluated overlay, Impact Candidates, Assessments, Decision Scope, routing history and terminal Decision separate.

---

# 4. Frozen authority chain

The documents must be interpreted in this precedence order:

```text
Business Architecture
→ Logical Information Model
→ Scenario Data
→ RRR-v0.1
→ Solution Architecture
→ Prototype Implementation Plan
→ code, migrations, fixtures, tests and evidence
```

| Order | Frozen artefact | Version / status | Primary role |
|---:|---|---|---|
| 1 | [Business Architecture Definition v0.3.1 — Frozen Implementation Baseline](01-business-architecture/Business_Architecture_Definition_v0.3.1_Frozen_Implementation_Baseline.md) | `0.3.1` — Frozen implementation baseline | Capability, process boundary, business semantics, scenarios, invariants and BR-01–BR-29. |
| 2 | [Logical Information Model v0.3.2 — Frozen Implementation Baseline](02-logical-information-model/Product_Change_Impact_Decision_Readiness_Logical_Information_Model_v0.3.2_Frozen_Implementation_Baseline.md) | `0.3.2` — Frozen implementation baseline | Implementation-neutral entities, associations, identity, immutability, lineage, cardinality and integrity rules. |
| 3 | [Scenario Data Definition v0.1 — Frozen Implementation Baseline](03-scenario-data/Product_Change_Impact_Decision_Readiness_Scenario_Data_Definition_v0.1.md) | `0.1` — Frozen implementation baseline / deterministic test oracle | Exact synthetic inputs, expected records, derived results and cross-scenario oracle assertions for Scenarios A–C. |
| 4 | [Readiness and Routing Rules v0.1 — Frozen Implementation Baseline](04-readiness-routing-rules/Product_Change_Impact_Decision_Readiness_Readiness_and_Routing_Rules_v0.1_Frozen_Implementation_Baseline.md) | `0.1 / RRR-v0.1` — Frozen implementation baseline | Deterministic Gate A, baseline reuse, overlay eligibility, RRR-01–RRR-06, Gate B, eligibility and authority rules. |
| 5 | [Solution Architecture v0.1 — Frozen Implementation Baseline](05-solution-architecture/Product_Change_Impact_Decision_Readiness_Solution_Architecture_v0.1_Frozen_Implementation_Baseline.md) | `0.1` — Frozen implementation baseline | Modular-monolith structure, persistence, ports, transaction boundaries, immutability and verification architecture. |
| 6 | [Prototype Implementation Plan v0.1 — Frozen Implementation Baseline](06-implementation-plan/Product_Change_Impact_Decision_Readiness_Prototype_Implementation_Plan_v0.1_Frozen_Implementation_Baseline.md) | `0.1` — Frozen implementation baseline | Concrete increments, migrations, G00–G14 gates, IT-01–IT-16 integrity catalogue and definition of done. |

No downstream document, implementation detail or convenience may silently override an upstream semantic rule.

---

# 5. Reading paths

## 5.1 Fifteen-minute orientation

1. Read this index through §7.
2. Read the Business Architecture: Document Notice, Capability Definition, Fundamental Semantic Model, Process Boundary, Scenarios A–C, Frozen Architectural Invariants and Implementation Gate.
3. Read the scenario summary in §6 below.
4. Inspect [`../evidence/verification_summary.md`](../evidence/verification_summary.md) and [`../evidence/integrity_results.json`](../evidence/integrity_results.json).

Result: understand the problem, the central semantic distinctions, the three scenario outcomes and the verification claim.

## 5.2 Forty-five-minute architecture review

1. Follow the fifteen-minute path.
2. Read the Business Architecture in full.
3. Read the Logical Information Model sections on governing invariants, action-specific target integrity, Assessment obligations and reuse, Gate B, Decision support/scope and integrity rules.
4. Read the Readiness and Routing Rules sections on normative evaluation order, `RRR-01..06`, Gate B, Authorisation Eligibility, authority sufficiency and the scenario traces.
5. Read the Solution Architecture sections on objectives, modules, persistence, immutability, transaction boundaries and architecture decisions.

Result: understand how business meaning becomes deterministic information, rules and software boundaries.

## 5.3 Deep technical and assurance review

1. Read all six frozen artefacts in precedence order.
2. Inspect [`../data/scenarios/`](../data/scenarios/) and [`../data/impact-fixtures/`](../data/impact-fixtures/) to confirm separation of scenario input, impact result and expected oracle.
3. Inspect [`../src/plm_ref/application/`](../src/plm_ref/application/), [`../src/plm_ref/rules/`](../src/plm_ref/rules/) and the Alembic migrations.
4. Inspect [`../tests/`](../tests/) for `G00–G14` and the integrity catalogue.
5. Inspect [`../evidence/decision_DEC-A01_basis.json`](../evidence/decision_DEC-A01_basis.json), the scenario actual/diff files and the integrity result.

Result: follow the complete chain from architecture claim to implementation control, test and committed evidence.

---

# 6. Frozen scenario summary

| Scenario | Architectural purpose | Frozen stop point |
|---|---|---|
| **A — Authorised change** | Complete bounded assessment and explicit terminal authorisation | Gate B `Complete`; Eligibility `Permitted`; Standard authority sufficient; `DEC-A01`; Case `Closed by Decision`; Handover available |
| **B — Scope amendment and selective reuse** | Prove that discovered impact is not authorised scope, proposal revision is not baseline revision, and historical Assessment reuse is execution-relative | `HIST-B01`; explicit `CI-B02:r1`; reuse `BL-B01`; `IAX-B02`; two obligations open; Gate B `Incomplete`; Case `In Assessment`; no Decision or Handover |
| **C — Authority escalation** | Prove that package completeness and substantive eligibility do not imply authority to decide | Gate B `Complete`; Eligibility `Permitted`; required `Elevated`, current `Standard`; `HIST-C01`; Case `Decision Ready`; no Decision or Handover |

---

# 7. Key semantic separations

The public case depends on the following distinctions remaining explicit:

- authoritative current state **vs.** immutable Assessment Baseline snapshot;
- Change Item identity **vs.** immutable Change Item revision;
- active proposal state **vs.** terminal Decision disposition;
- Assessment Baseline **vs.** non-authoritative proposed-state Overlay Revision;
- Impact Candidate discovery **vs.** explicit Proposed Change Scope and Decision Scope;
- Evidence Record **vs.** Assessment-owned Requirement Conclusion;
- Gate B package completeness **vs.** Authorisation Eligibility **vs.** authority sufficiency;
- non-terminal Process-history Entry **vs.** terminal Decision Record;
- pre-decision Open Item **vs.** post-authorisation Decision Condition;
- persisted historical basis **vs.** mutable current source state;
- authorised Decision **vs.** derived Handover View.

---

# 8. Implementation and evidence navigation

| Area | Repository location |
|---|---|
| Frozen scenario inputs and expected oracles | [`../data/scenarios/`](../data/scenarios/) |
| Bounded impact-result fixtures | [`../data/impact-fixtures/`](../data/impact-fixtures/) |
| Application use cases and orchestration | [`../src/plm_ref/application/`](../src/plm_ref/application/) |
| Deterministic `RRR-v0.1` implementation | [`../src/plm_ref/rules/`](../src/plm_ref/rules/) |
| Relational model and persistence controls | [`../src/plm_ref/infrastructure/`](../src/plm_ref/infrastructure/) and [`../migrations/`](../migrations/) |
| Acceptance and integrity tests | [`../tests/`](../tests/) |
| Deterministic verification evidence | [`../evidence/`](../evidence/) |

The expected oracle is not loaded as application state. Scenario execution, bounded impact-result fixtures and complete expected state remain separate.

---

# 9. Publication integrity

The six frozen files in this repository are byte-preserving copies of the authoritative source artefacts. Only their repository paths and filenames were normalised.

| Order | Repository path | SHA-256 |
|---:|---|---|
| 1 | `docs/01-business-architecture/Business_Architecture_Definition_v0.3.1_Frozen_Implementation_Baseline.md` | `ef9abdcee3504c23d5b1eb5073cfc89e12955a9f9c7d97a347723707fac73f47` |
| 2 | `docs/02-logical-information-model/Product_Change_Impact_Decision_Readiness_Logical_Information_Model_v0.3.2_Frozen_Implementation_Baseline.md` | `f07a6cb5da2af42324dcb208a7be123e138a63f02933818aeae0922fc4c2b2ae` |
| 3 | `docs/03-scenario-data/Product_Change_Impact_Decision_Readiness_Scenario_Data_Definition_v0.1.md` | `75f02b9c516a823e67f019924955062db520849a8154f745b81861f05fa13c56` |
| 4 | `docs/04-readiness-routing-rules/Product_Change_Impact_Decision_Readiness_Readiness_and_Routing_Rules_v0.1_Frozen_Implementation_Baseline.md` | `a74d905af1dbc7e10a15cdfda0731024349c07b7bbb751561c3fae37ea68f300` |
| 5 | `docs/05-solution-architecture/Product_Change_Impact_Decision_Readiness_Solution_Architecture_v0.1_Frozen_Implementation_Baseline.md` | `1a4c82679f449658ff5756a1a992f649bf781d26a65728837e42484811b33206` |
| 6 | `docs/06-implementation-plan/Product_Change_Impact_Decision_Readiness_Prototype_Implementation_Plan_v0.1_Frozen_Implementation_Baseline.md` | `9a3fe025a43f6527d44410e6184f20ed6196548a8b0480f91cf33ae4374587b5` |

A future content change that alters one of these hashes must be classified and recorded. Presentation or navigation work is not permission to reinterpret frozen semantics.

---

# 10. Change control

For release `v0.1.0`:

- no additional PLM capability, Change Item action, scenario, rule family or workflow concept is planned;
- implementation code remains subordinate to the frozen authority chain;
- a frozen upstream artefact may be reopened only for a demonstrated contradiction that makes a published claim false or prevents deterministic execution of Scenarios A–C;
- documentation-only navigation and packaging changes do not move the verified implementation baseline;
- executable changes require complete regression, `plm-ref verify all`, deterministic evidence comparison and a newly recorded verified implementation commit.

---

# 11. Verified implementation boundary

The recorded verified implementation baseline is:

```text
7a5733fc7042e33a790db12278f8776d047eb4b6
```

Recorded result:

- `G00–G14`: 15/15 PASS;
- full regression: 185 passed;
- `plm-ref verify all`: PASS / exit 0;
- repeated evidence generation: byte-identical;
- six final verification groups: PASS;
- six active IT-16 cross-case injection families: attempted, rejected and PASS.

These results establish conformance to the bounded frozen reference case. They do not establish production or enterprise PLM readiness.
