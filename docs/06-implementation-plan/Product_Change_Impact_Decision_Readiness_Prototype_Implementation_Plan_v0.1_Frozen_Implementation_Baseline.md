# Product Change Impact Assessment & Decision Readiness

## Prototype Implementation Plan v0.1

**Document type:** Prototype Implementation Plan  
**Status:** Frozen implementation baseline  
**Domain:** Synthetic automotive Product Lifecycle Management  
**Version:** 0.1  
**Date:** 26 August 2026  

**Governing frozen artefacts:**
- Business Architecture Definition v0.3.1 — Frozen Implementation Baseline
- Logical Information Model v0.3.2 — Frozen Implementation Baseline
- Scenario Data Definition v0.1 — Frozen Implementation Baseline
- Readiness and Routing Rules v0.1 — Frozen Implementation Baseline (`RRR-v0.1`)
- Solution Architecture v0.1 — Frozen Implementation Baseline

---

## Freeze Record

**Freeze decision:** FREEZE  
**Freeze date:** 26 August 2026  
**Review basis:** Blocker-only review for contradictions preventing deterministic implementation of Scenarios A–C or silently violating frozen semantics.  
**Result:** No release-blocking contradiction found. No implementation-plan semantics changed at freeze.

---


## Document Notice

This document is the executable build plan for the bounded **Product Change Impact Assessment & Decision Readiness** demonstrator.

It converts the frozen Solution Architecture into concrete implementation increments, schema migrations, modules, fixtures, tests, acceptance gates, and final verification evidence.

It does **not** redefine business or PLM semantics.

The implementation rule is:

> **If a software task conflicts with a frozen upstream artefact, the software task is wrong unless implementation exposes an actual contradiction that makes Scenarios A–C impossible to implement deterministically.**

The prototype remains a synthetic integration projection and deterministic demonstrator. It is not an enterprise PLM implementation.

---

# 1. Purpose

The purpose of Prototype Implementation Plan v0.1 is to define, precisely enough for implementation:

1. repository bootstrap;
2. package and module structure;
3. physical schema migration order;
4. bounded JSON/Pydantic models;
5. repository and transaction boundaries;
6. explicit implementation order for Gate A, baseline, overlay, impact, routing, assessment, reuse, readiness, authority, decision, history, and views;
7. Scenario A–C fixture loading;
8. unit, integration, integrity, and oracle tests;
9. release-critical negative tests;
10. deterministic verification evidence;
11. implementation acceptance gates;
12. the exact point at which the prototype is considered complete.

This plan is the final pre-code specification artefact.

---

# 2. Authority and Change Control

The authority order is:

```text
Business Architecture v0.3.1
        ↓
Logical Information Model v0.3.2
        ↓
Scenario Data Definition v0.1
        ↓
Readiness and Routing Rules v0.1
        ↓
Solution Architecture v0.1
        ↓
Prototype Implementation Plan v0.1
        ↓
Code + migrations + fixtures + tests
```

Implementation may refine:

- Python file names;
- helper function names;
- internal DTO names;
- SQLAlchemy implementation details;
- CLI command spelling;
- FastAPI route spelling;
- test organization.

Implementation may **not** silently change:

- entity meaning;
- identifier semantics;
- executable Change Item actions;
- process order;
- baseline/overlay separation;
- Gate A or Gate B meaning;
- `RRR-v0.1` behaviour;
- Assessment locking;
- retained-assessment semantics;
- Product Version immutability;
- Decision versus routing semantics;
- Scenario A–C expected states.

If a contradiction is discovered, implementation stops at the affected acceptance gate and records the contradiction before any upstream change is proposed.

---

# 3. Implementation Definition of Done

The prototype is complete only when all of the following are true:

1. a clean environment can install the project from `pyproject.toml`;
2. Alembic can create the SQLite schema from an empty database;
3. `PRAGMA foreign_keys = ON` is active for every application connection;
4. frozen scenario fixtures can rebuild the demonstrator database deterministically;
5. Scenario A produces the exact frozen terminal state, including `DEC-A01`;
6. Scenario B reproduces both proposal cycles, reuses `BL-B01`, produces the exact reuse classifications, leaves `AO-B21` and `AO-B22` unsatisfied, and creates no Decision Record;
7. Scenario C produces `HIST-C01 = Escalated`, creates no Decision Record, and remains `Decision Ready`;
8. every cross-scenario oracle assertion passes;
9. all release-critical immutability tests pass at both application and SQLite layers;
10. `DEC-A01` can be reconstructed without reading mutable current source state;
11. the Handover View for Scenario A is derived, not persisted;
12. the entire automated test suite passes from a clean database;
13. `plm-ref verify all` returns success and writes deterministic evidence output;
14. no out-of-scope PLM semantics or infrastructure dependency has been introduced.

---

# 4. Selected Implementation Stack

The implementation shall use the frozen Solution Architecture stack:

| Concern | Implementation |
|---|---|
| Runtime | Python 3.12+ |
| HTTP interface | FastAPI |
| Validation / DTOs | Pydantic v2 |
| ORM / persistence | SQLAlchemy 2.x |
| Database | SQLite 3 |
| Migration | Alembic |
| Testing | pytest |
| CLI | Typer preferred; small argparse wrapper acceptable |
| Fixture serialization | YAML and/or JSON |

No additional infrastructure service is required.

The implementation shall not add:

- message broker;
- graph database;
- generic rules engine;
- generic workflow engine;
- distributed worker;
- AI/LLM runtime dependency;
- external authentication service;
- cloud-only dependency.

---

# 5. Target Repository Structure

```text
plm-change-impact-reference-case/
├── README.md
├── pyproject.toml
├── alembic.ini
├── docs/
│   ├── business-architecture/
│   ├── information-model/
│   ├── scenario-data/
│   ├── rules/
│   ├── solution-architecture/
│   └── implementation-plan/
│       └── Product_Change_Impact_Decision_Readiness_Prototype_Implementation_Plan_v0.1.md
├── data/
│   ├── scenarios/
│   │   ├── shared/
│   │   │   └── source_state.yaml
│   │   ├── scenario_a/
│   │   │   ├── input.yaml
│   │   │   └── expected.yaml
│   │   ├── scenario_b/
│   │   │   ├── input.yaml
│   │   │   └── expected.yaml
│   │   └── scenario_c/
│   │       ├── input.yaml
│   │       └── expected.yaml
│   └── impact-fixtures/
│       ├── IAX-A01.yaml
│       ├── IAX-B01.yaml
│       ├── IAX-B02.yaml
│       └── IAX-C01.yaml
├── src/
│   └── plm_ref/
│       ├── __init__.py
│       ├── domain/
│       │   ├── enums.py
│       │   ├── payloads.py
│       │   ├── results.py
│       │   └── errors.py
│       ├── application/
│       │   ├── source_projection.py
│       │   ├── change_case.py
│       │   ├── gate_a.py
│       │   ├── baseline.py
│       │   ├── overlay.py
│       │   ├── impact_analysis.py
│       │   ├── routing.py
│       │   ├── assessment.py
│       │   ├── assessment_reuse.py
│       │   ├── scope_routing.py
│       │   ├── readiness.py
│       │   ├── authority.py
│       │   ├── decision.py
│       │   ├── history_and_views.py
│       │   └── scenario_runner.py
│       ├── rules/
│       │   ├── registry.py
│       │   └── rrr_v0_1/
│       │       ├── common.py
│       │       ├── applicability.py
│       │       ├── rrr_01.py
│       │       ├── rrr_02.py
│       │       ├── rrr_03.py
│       │       ├── rrr_04.py
│       │       ├── rrr_05.py
│       │       ├── rrr_06.py
│       │       └── reuse.py
│       ├── infrastructure/
│       │   ├── db/
│       │   │   ├── base.py
│       │   │   ├── models.py
│       │   │   ├── session.py
│       │   │   ├── repositories.py
│       │   │   └── guards.py
│       │   └── impact/
│       │       ├── port.py
│       │       └── frozen_fixture_adapter.py
│       ├── interfaces/
│       │   ├── api/
│       │   │   ├── app.py
│       │   │   ├── commands.py
│       │   │   └── queries.py
│       │   └── cli/
│       │       └── main.py
│       └── views/
│           ├── readiness.py
│           ├── lineage.py
│           ├── decision_basis.py
│           └── handover.py
├── migrations/
│   └── versions/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── integrity/
│   └── scenarios/
└── evidence/
```

Exact Python filenames may change if responsibility boundaries remain equivalent.

---

# 6. Physical Schema Migration Plan

The schema shall be created incrementally. Each migration must be independently reversible in development and covered by a migration smoke test.

## MIG-001 — Product/source projection

Create:

```text
product_elements
product_versions
product_structure_occurrences
configuration_contexts
requirements
evidence_records
```

Required constraints include:

- Product Version uniqueness on `(product_element_id, revision, iteration)`;
- foreign keys from Product Version to Product Element;
- parent/child Product Version references from Product Structure Occurrence;
- foreign keys for Requirement allocation and Evidence references where represented relationally;
- JSON fields for bounded applicability/effectivity/configuration payloads.

Acceptance:

- shared source fixture loads;
- duplicate Product Version revision/iteration is rejected;
- invalid occurrence Product Version references are rejected.

## MIG-002 — Change Case and Change Item model

Create:

```text
change_cases
change_items
change_item_revisions
change_item_proposal_states
open_items
```

Required constraints:

- stable `change_item_id` identity;
- unique `(change_item_id, change_item_revision)`;
- exactly one Proposal State row per Change Item identity;
- selected revision must belong to the same Change Item and Change Case;
- only frozen proposal-state values are accepted.

Acceptance:

- `CI-A01:r1`, `CI-B01:r1`, `CI-B02:r1`, `CI-C01:r1` can be represented;
- duplicate revision is rejected;
- cross-case selected revision is rejected.

## MIG-003 — Assessment Baseline

Create:

```text
assessment_baselines
baseline_members
```

Add constraints/indexes for case-local lookup and member identity.

Add application support for atomic baseline creation.

Acceptance:

- `BL-A01`, `BL-B01`, `BL-C01` load with exact member sets;
- partial baseline creation rolls back;
- Baseline Member snapshot payloads round-trip unchanged.

## MIG-004 — Overlay model

Create:

```text
overlay_revisions
overlay_change_item_memberships
overlay_local_objects
```

Required constraints:

- unique Change Item identity per Overlay Revision;
- unique `(overlay_revision_id, overlay_local_object_id)`;
- same-case membership validated before commit.

Acceptance:

- `OV-A01`, `OV-B01`, `OV-B02`, `OV-C01` can be materialised exactly;
- `OV-B02` contains exactly `CI-B01:r1` and `CI-B02:r1`;
- duplicate Change Item identity within one overlay is rejected.

## MIG-005 — Impact execution and structured provenance

Create:

```text
impact_executions
impact_candidates
impact_candidate_provenance
impact_candidate_path_steps
```

Required constraints:

- execution references one case-local baseline and overlay;
- provenance references exact Change Item revision;
- path step `sequence` uniqueness within provenance;
- application validation for path contiguity and connectivity.

Acceptance:

- all four frozen impact fixtures persist exactly;
- invalid Current State reference not present in Baseline Members is rejected;
- invalid Proposed State reference from another overlay is rejected;
- disconnected provenance path is rejected.

## MIG-006 — Assessment and obligation model

Create:

```text
assessment_obligations
assessments
assessment_impact_links
assessment_requirement_conclusions
assessment_evidence_uses
assessment_reuse_classifications
```

Required constraints:

- one conclusion per `(assessment_id, requirement_id)`;
- one reuse classification per `(assessment_id, target_impact_execution_id)`;
- foreign-key integrity for obligation fulfilment;
- exact frozen enum values only.

Acceptance:

- Scenario A and Scenario B first-cycle Assessment sets can be represented;
- duplicate Requirement Conclusion is rejected;
- reuse classification is execution-relative.

## MIG-007 — Process history and Decision model

Create:

```text
process_history_entries
decision_records
decision_support_assessments
decision_scope_items
decision_conditions
```

Required constraints:

- terminal Decision outcome values only;
- Process-history entry values only from frozen set;
- Decision lineage to case/baseline/overlay/execution;
- unique terminal disposition of one Change Item revision enforced by service and supporting database constraint where practical.

Acceptance:

- `HIST-B01`, `HIST-C01`, and `DEC-A01` can be represented exactly;
- a non-terminal route cannot be stored as a Decision Record outcome.

## MIG-008 — Immutability triggers

Add SQLite triggers for release-critical immutability.

At minimum:

1. baselined Product Version UPDATE protection;
2. baselined Product Version DELETE protection;
3. used Assessment Baseline UPDATE/DELETE protection;
4. used Baseline Member INSERT/UPDATE/DELETE protection;
5. used Overlay Revision UPDATE/DELETE protection;
6. used Overlay membership INSERT/UPDATE/DELETE protection;
7. used Overlay-local Object INSERT/UPDATE/DELETE protection;
8. used Change Item Revision UPDATE/DELETE protection;
9. locked Assessment UPDATE/DELETE protection;
10. locked Assessment child-set INSERT/UPDATE/DELETE protection;
11. Decision Record/support/scope append-only protection after creation.

The authoritative Product Version lock condition is:

```sql
EXISTS (
    SELECT 1
    FROM baseline_members bm
    WHERE bm.object_type = 'Product Version'
      AND bm.object_id = product_versions.product_version_id
)
```

Acceptance:

- direct SQL attempts fail independently of application guards;
- proposed successor materialisation in `overlay_local_objects` remains possible.

---

# 7. Bounded Payload Models

Pydantic models shall validate all JSON payloads before persistence.

Minimum typed payloads:

- `ConfigurationContextFeatureValues`;
- `ApplicabilityRulePayload`;
- `EffectivityPayload`;
- `ProductStructureOccurrenceStatePayload`;
- `ReviseProductStateCurrentReference`;
- `ReviseProductStateProposalPayload`;
- `ChangeApplicabilityCurrentReference`;
- `ChangeApplicabilityProposalPayload`;
- `BaselineProductVersionSnapshot`;
- `BaselineOccurrenceSnapshot`;
- `OverlayProductVersionState`;
- `OverlayOccurrenceState`;
- `EvidenceSnapshotPayload`.

Action-specific Change Item payload validation shall discriminate only:

```text
Revise Product State
Change Applicability
```

Unsupported actions fail validation.

No arbitrary unvalidated JSON is accepted into release-critical historical fields.

---

# 8. Rule Implementation Plan

`RRR-v0.1` shall be implemented as pure deterministic functions.

## 8.1 Common rule context

Implement typed, read-only rule contexts containing only required case-local data.

Rule functions must have no dependency on:

- wall clock;
- randomness;
- network;
- external AI;
- mutable global state.

## 8.2 Common predicates

Implement and unit-test:

```text
material_characteristic_changed
normalize_applicability_expression
validated_scope_relation
overlay_contains_applicability_change
```

The applicability parser supports only:

```text
Feature = "Value" [AND Feature = "Value"]*
```

No broader grammar is implemented.

## 8.3 `RRR-01..04`

Implement one file/function per rule.

Each returns a result specification only. It performs no database write.

Application `routing` materialises obligations transactionally.

Release-critical tests:

- Scenario A → four candidate-linked obligations;
- Scenario B `IAX-B01` → four candidate-linked obligations with `REQ-004` for Product Engineering;
- Scenario B `IAX-B02` → candidate-linked Product Engineering + Manufacturing and null-candidate Validation + Purchasing/Cost obligations;
- Scenario C → four candidate-linked obligations.

## 8.4 `RRR-05`

Implement structured trigger only:

```text
Proposed Narrower
AND Complete Product Engineering Assessment
AND REQ-004 = Not Satisfied
AND no Change Applicability for affected occurrence in current overlay
```

The rule must not inspect `impact_statement` text.

When it fires, application service persists one Scope Revision Required Process-history Entry and stops terminal-readiness progression for that execution.

The rule never creates `CI-B02:r1`.

## 8.5 Reuse classifier

Implement ordered rules:

```text
1. Invalidated
2. Revalidation Required
3. Retained
```

Frozen expected result for `IAX-B02`:

```text
ASM-B01 → Invalidated
ASM-B02 → Retained
ASM-B03 → Revalidation Required
ASM-B04 → Retained
```

No implicit classification default is allowed.

## 8.6 `RRR-06`

Implement exact trigger mapping only:

```text
Synthetic supplier process change
→ Standard

Synthetic supplier process change with elevated authority classification
→ Elevated
```

Unknown in-scope trigger mapping fails closed.

---

# 9. Application-Service Build Increments

Implementation shall proceed in the following increments. Each increment has an acceptance gate. Do not continue by bypassing a failed release-critical gate.

## INC-00 — Bootstrap and deterministic runtime

Build:

- `pyproject.toml`;
- dependency groups;
- package skeleton;
- pytest configuration;
- Alembic configuration;
- SQLite connection factory;
- mandatory `PRAGMA foreign_keys = ON` hook;
- CLI skeleton;
- FastAPI app skeleton.

Acceptance gate `G00`:

```text
python import succeeds
pytest runs
alembic current runs
SQLite foreign_keys = 1
CLI --help succeeds
FastAPI app imports
```

## INC-01 — Persistence foundation and source projection

Build MIG-001 and ORM models.

Build fixture loader for shared synthetic source state.

Acceptance gate `G01`:

- source fixture loads from empty database;
- source record identities match frozen fixture;
- invalid FK and duplicate Product Version tests fail as expected.

## INC-02 — Change Case, Change Item, and Gate A

Build MIG-002.

Build:

- `change_case` service;
- immutable Change Item Revision creation;
- Proposal State handling;
- active Proposed Change Scope query;
- `gate_a` evaluator.

Architectural restriction:

> `gate_a` receives no Baseline repository or Baseline Member dependency.

Acceptance gate `G02`:

```text
Scenario A Gate A = Pass
Scenario B first Gate A = Pass
Scenario B amended Gate A = Pass
Scenario C Gate A = Pass
```

Negative tests include malformed target, missing rationale, invalid context, blocking Initial Distribution Open Item, and proof that Gate A does not require a baseline row.

## INC-03 — Baseline creation and Product Version immutability

Build MIG-003 and relevant MIG-008 trigger subset.

Build:

- baseline creation transaction;
- canonical snapshot validation;
- five-input baseline-reuse function;
- application Product Version mutation guard.

Acceptance gate `G03`:

- exact `BL-A01`, `BL-B01`, `BL-C01` member sets persist;
- partial baseline transaction rolls back;
- Scenario B five true reuse inputs return `true`;
- no new baseline is created for B second proposal cycle;
- once `PV-003` is captured as a Product Version Baseline Member, application UPDATE and DELETE fail;
- direct SQL UPDATE and DELETE also fail;
- overlay successor creation remains possible later.

## INC-04 — Overlay and Overlay Execution Eligibility

Build MIG-004 and overlay immutability trigger subset.

Build:

- candidate Overlay Revision construction;
- exact active membership validation;
- `Revise Product State` materialisation;
- `Change Applicability` materialisation;
- baseline-relative target verification;
- successor collision check;
- predecessor applicability verification.

Acceptance gate `G04`:

```text
OV-A01 → Pass
OV-B01 → Pass
OV-B02 → Pass against reused BL-B01
OV-C01 → Pass
```

Negative tests:

- target absent from baseline;
- baseline/current-reference mismatch;
- successor identity collision;
- wrong predecessor applicability;
- cross-case membership;
- more than one revision of the same Change Item identity in one overlay.

## INC-05 — Bounded impact execution and provenance

Build MIG-005.

Build:

- `ImpactAnalysisPort`;
- `FrozenFixtureImpactAdapter`;
- exact execution-lineage validation;
- impact-result structural validation;
- atomic impact execution persistence.

Acceptance gate `G05`:

- exact candidates/provenance for `IAX-A01`, `IAX-B01`, `IAX-B02`, `IAX-C01` persist;
- current-state path references resolve only to baseline members;
- proposed-state path references resolve only to the execution overlay;
- path sequences are contiguous and connected;
- invalid result causes execution failure with no partial completed candidate set.

## INC-06 — Routing `RRR-01..04`

Build MIG-006 obligation portion and the rule registry.

Build:

- `RRR-v0.1 → RrrV01RuleSet` registry entry;
- bounded applicability parser;
- common predicates;
- `RRR-01..04`;
- candidate-state consequence;
- routing transaction.

Acceptance gate `G06`:

The obligation set for each execution matches the frozen oracle exactly, including:

```text
AO-B23 impact_candidate_id = null
AO-B24 impact_candidate_id = null
```

`routing_status = Completed` occurs only in the same transaction that persists the complete positive obligation set.

A missing mandatory routing input results in `routing_status = Failed`.

## INC-07 — Assessment completion, Evidence Use, and lock boundary

Complete MIG-006 Assessment tables and lock triggers.

Build:

- Assessment creation;
- Assessment Impact Links;
- Requirement Conclusions;
- Evidence Uses with immutable snapshot payload;
- predecessor Evidence transferability validation;
- direct obligation fulfilment;
- assessment completion/lock transaction.

Acceptance gate `G07`:

- all Scenario A Assessments complete and lock exactly;
- all Scenario B first-execution Assessments complete and lock exactly;
- all Scenario C Assessments complete and lock exactly;
- locked Assessment fields and historical semantic children reject INSERT/UPDATE/DELETE;
- Evidence Record alone never creates Requirement Conclusion;
- a required successor Evidence Use without transferability fails.

## INC-08 — Scope route and explicit Scenario B scope amendment

Build MIG-007 Process-history portion.

Build:

- `RRR-05`;
- Scope Revision Required persistence;
- application stop condition after route;
- explicit Change Item creation path for `CI-B02:r1`;
- second proposal-cycle Gate A;
- baseline-reuse invocation;
- `OV-B02` creation.

Acceptance gate `G08`:

```text
IAX-B01 → HIST-B01 Scope Revision Required
IAX-B01 → no Decision Record
CI-B02:r1 is created only by explicit scenario-driver/change-owner command
BL-B01 is reused
OV-B02 contains CI-B01:r1 + CI-B02:r1
```

Test proves `RRR-05` does not parse Assessment narrative and does not auto-create the Change Item.

## INC-09 — Assessment reuse and retained fulfilment

Build reuse classifier and retained fulfilment transaction.

Required transaction:

```text
validate Retained classification
→ validate same case
→ validate domain
→ validate Requirement compatibility
→ validate target execution compatibility
→ validate immutable Evidence Use criteria
→ update only target obligation.fulfilled_by_assessment_id
→ do not modify historical Assessment or children
```

Acceptance gate `G09`:

Exact classifications:

```text
ASM-B01 = Invalidated
ASM-B02 = Retained
ASM-B03 = Revalidation Required
ASM-B04 = Retained
```

Exact retained fulfilment:

```text
AO-B23 → ASM-B02
AO-B24 → ASM-B04
```

Exact unfulfilled obligations:

```text
AO-B21 → null
AO-B22 → null
```

Before/after hashes or canonical serialized snapshots of `ASM-B02`, `ASM-B04`, and all their semantic children must be identical.

Negative tests prove `Invalidated` and `Revalidation Required` cannot fulfil later mandatory obligations.

## INC-10 — Gate B, Authorisation Eligibility, and authority

Build:

- Gate B pre-authority predicates;
- short-circuit behaviour;
- candidate coverage calculation;
- Evidence completeness calculation;
- `RRR-06`;
- Authorisation Eligibility;
- authority comparison;
- escalation persistence.

Acceptance gate `G10`:

```text
Scenario A:
Gate B = Complete
Authorisation Eligibility = Permitted
required = Standard
current = Standard
decision_permitted = true

Scenario B / IAX-B02:
Gate B = Incomplete
Authorisation Eligibility = Not Evaluated
required authority not evaluated at stop point

Scenario C:
Gate B = Complete
Authorisation Eligibility = Permitted
required = Elevated
current = Standard
decision_permitted = false
escalation_required = true
HIST-C01 = Escalated
```

No Decision Record exists in C.

## INC-11 — Terminal Decision persistence and Case closure

Complete MIG-007 Decision tables and Decision append-only triggers.

Build:

- explicit authority disposition DTO/command;
- Decision persistence guard;
- Decision transaction;
- Decision Support Assessment completeness validation;
- Decision Scope validation;
- Decision Condition cardinality validation;
- derived Case closure.

Acceptance gate `G11`:

Scenario A explicit command:

```text
outcome = Authorised for Downstream Processing
```

persists exactly:

```text
DEC-A01
DSA-A01..DSA-A04
Decision Scope = CI-A01:r1
Decision Conditions = none
CHG-A01 = Closed by Decision
```

Negative tests prove:

- no automated Decision exists before explicit command;
- insufficient authority rejects Decision creation;
- incomplete Decision Support set rejects Decision creation;
- scope item absent from final overlay rejects Decision creation;
- `Authorised for Downstream Processing` with any Decision Condition is rejected.

## INC-12 — Historical reconstruction and Handover View

Build query projections:

- case lineage;
- execution lineage;
- Decision basis;
- Handover View.

Acceptance gate `G12`:

- `DEC-A01` reconstructs exact Change Item revision, baseline snapshots, overlay, execution, four locked Assessments, Requirement Conclusions, Evidence Uses, and Evidence snapshots;
- reconstruction performs no live source lookup for historical meaning;
- Scenario A Handover View matches frozen oracle;
- no Handover View exists for B or C;
- no handover persistence table exists.

## INC-13 — API, CLI, and deterministic scenario runner

Wire the already-tested application services through thin interfaces.

Minimum CLI:

```text
plm-ref db reset
plm-ref scenario load A
plm-ref scenario run A
plm-ref scenario run B
plm-ref scenario run C
plm-ref verify all
```

Representative FastAPI command/query routes follow the frozen Solution Architecture. Raw CRUD for immutable records is prohibited.

Acceptance gate `G13`:

- CLI runs all scenarios from a clean database;
- HTTP routes call the same application services as CLI;
- no raw mutation route exists for Baseline Members, Overlay-local Objects, locked Assessments, or Decision Records.

## INC-14 — Full oracle verification and evidence generation

Build final scenario comparator.

The comparator must compare actual output to the independent frozen `expected.yaml` state, not to the impact-adapter fixture used to generate candidates.

Acceptance gate `G14`:

```text
Scenario A oracle = PASS
Scenario B oracle = PASS
Scenario C oracle = PASS
Cross-scenario assertions = PASS
Integrity suite = PASS
Historical reconstruction = PASS
```

Only after `G14` passes is the prototype implementation considered complete.

---

# 10. Test Strategy

Tests are part of implementation, not a post-build activity.

Every increment adds its own tests before the next increment starts.

## 10.1 Unit tests

Target pure logic:

- payload validation;
- applicability parser;
- `material_characteristic_changed`;
- scope relation;
- `RRR-01..06`;
- reuse classification;
- Gate A predicates;
- Gate B predicates;
- Authorisation Eligibility;
- authority comparison;
- Case-state derivation.

## 10.2 Integration tests

Target multi-module use cases and transactions:

- baseline creation;
- overlay creation;
- impact execution;
- routing completion;
- Assessment completion;
- scope revision;
- retained fulfilment;
- terminal Decision persistence;
- Decision reconstruction.

## 10.3 Integrity tests

Target forbidden operations and fail-closed behaviour:

- Product Version immutability;
- Baseline immutability;
- Overlay immutability;
- Change Item Revision immutability after use;
- locked Assessment immutability;
- Decision append-only behaviour;
- cross-case lineage injection;
- invalid provenance paths;
- missing routing inputs;
- invalid rule-set version;
- partial transaction rollback.

## 10.4 Scenario oracle tests

One deterministic test module per scenario:

```text
test_scenario_a.py
test_scenario_b.py
test_scenario_c.py
```

A separate cross-scenario module validates the frozen assertions in Scenario Data §9.

---

# 11. Release-Critical Integrity Test Catalogue

The following tests are mandatory even if broader coverage is later reduced.

## IT-01 — Gate A baseline independence

1. load source state and Change Case/Change Item;
2. do not create an Assessment Baseline;
3. evaluate Gate A;
4. verify the expected result is obtained;
5. prove the Gate A service has no baseline membership requirement.

Expected: A, B initial, B amended, and C pass their fixture Gate A checks.

## IT-02 — Overlay eligibility requires baseline

Attempt overlay execution eligibility without the selected baseline-relative state.

Expected: Fail; impact execution cannot begin.

## IT-03 — Baselined Product Version application guard

1. create `PV-003`;
2. capture it as Product Version Baseline Member;
3. attempt application UPDATE;
4. attempt application DELETE.

Expected: both rejected.

## IT-04 — Baselined Product Version SQLite trigger

Repeat IT-03 using direct SQL.

Expected: both rejected at database layer.

## IT-05 — Proposed successor remains possible

After PV-003 lock, materialise `OVOBJ-A01-PV` or equivalent fixture successor.

Expected: succeeds without changing `product_versions.PV-003`.

## IT-06 — Locked Assessment child immutability

Complete and lock `ASM-B02`.

Attempt to add, update, or remove:

- Assessment Impact Link;
- Requirement Conclusion;
- Evidence Use.

Expected: rejected.

## IT-07 — Retained historical fulfilment does not mutate Assessment

1. persist/lock `ASM-B02` and `ASM-B04`;
2. canonicalize their complete historical state;
3. classify them `Retained` for `IAX-B02`;
4. fulfil `AO-B23` and `AO-B24`;
5. canonicalize historical states again.

Expected:

```text
AO-B23.fulfilled_by_assessment_id = ASM-B02
AO-B24.fulfilled_by_assessment_id = ASM-B04
historical ASM-B02 state unchanged
historical ASM-B04 state unchanged
```

## IT-08 — Non-retained reuse cannot fulfil

Attempt later obligation fulfilment with `ASM-B01` or `ASM-B03`.

Expected: rejected.

## IT-09 — Routing is atomic

Cause one `RRR-01..04` evaluation to fail.

Expected:

```text
routing_status = Failed
no state representing a completed partial positive obligation set
```

## IT-10 — `RRR-05` cannot create Change Item

Run B first cycle through Scope Revision Required.

Expected:

```text
HIST-B01 exists
CI-B02 does not exist until explicit scope-amendment command
```

## IT-11 — Gate B versus eligibility separation

Construct/package fixture with Complete obligations but a mandatory negative substantive conclusion.

Expected:

```text
Gate B may be Complete
Authorisation Eligibility = Blocked
```

This test need not introduce a fourth business scenario; it is a bounded rule unit/integration fixture.

## IT-12 — Authority insufficiency is non-terminal

Run Scenario C.

Expected:

```text
HIST-C01 = Escalated
Decision Record count for CHG-C01 = 0
CHG-C01 = Decision Ready
```

## IT-13 — Explicit Decision command required

Run Scenario A through `decision_permitted = true` but do not issue the authority disposition command.

Expected: no Decision Record.

Then issue the explicit command.

Expected: `DEC-A01` persisted.

## IT-14 — Complete Decision support coverage

Remove one required supporting Assessment from the attempted Scenario A Decision command.

Expected: Decision transaction rejected completely.

## IT-15 — Historical reconstruction ignores live source mutation

Where mutable source records are permitted, alter an unrelated/current source representation after Decision creation, or substitute a test repository that would return changed live values.

Reconstruct `DEC-A01`.

Expected: reconstructed basis remains exactly the stored historical snapshots and locked Assessment/Evidence basis.

Do not mutate a baselined Product Version, because that operation is separately prohibited.

## IT-16 — Cross-case injection rejection

Attempt at least one cross-case link in each release-critical lineage family:

- execution baseline/overlay;
- candidate provenance;
- Assessment fulfilment;
- Assessment reuse;
- Decision support;
- Decision Scope.

Expected: all rejected.

---

# 12. Scenario Implementation Acceptance Matrix

| Expected result | A | B first cycle | B second cycle | C |
|---|---|---|---|---|
| Gate A | Pass | Pass | Pass | Pass |
| Baseline | `BL-A01` | `BL-B01` | reuse `BL-B01` | `BL-C01` |
| Overlay | `OV-A01` | `OV-B01` | `OV-B02` | `OV-C01` |
| Impact execution | `IAX-A01` | `IAX-B01` | `IAX-B02` | `IAX-C01` |
| Routing | Completed | Completed | Completed | Completed |
| `RRR-05` | no | `Scope Revision Required` | no | no |
| Reuse classification | n/a | n/a | I/R/RV/R | n/a |
| Mandatory obligations satisfied | yes | yes for first cycle | no: B21/B22 open | yes |
| Gate B at frozen stop point | Complete | terminal progression stopped | Incomplete | Complete |
| Authorisation Eligibility | Permitted | not terminally used | Not Evaluated | Permitted |
| Required authority | Standard | not terminally used | not evaluated | Elevated |
| Current authority | Standard | — | — | Standard |
| Decision permitted | true | false/not applicable | false/not evaluated | false |
| Process history | none | `HIST-B01` | none additional at stop point | `HIST-C01` |
| Decision Record | `DEC-A01` after explicit command | none | none | none |
| Final case state | Closed by Decision | open loop | In Assessment | Decision Ready |
| Handover View | yes | no | no | no |

`I/R/RV/R` means:

```text
ASM-B01 = Invalidated
ASM-B02 = Retained
ASM-B03 = Revalidation Required
ASM-B04 = Retained
```

---

# 13. Scenario Fixture Rules

## 13.1 Fixture separation

Keep three data roles separate:

1. **input fixture** — source/case/authority actions supplied to the application;
2. **impact fixture** — bounded `ImpactAnalysisPort` external result;
3. **expected fixture** — independent complete test oracle.

The implementation must not load expected final application state as if it were execution output.

## 13.2 Deterministic identifiers

The scenario runner shall use the frozen identifiers exactly.

No UUID replacement is required for the three oracle runs.

General application commands may have an ID generator abstraction, but scenario verification must remain deterministic.

## 13.3 Deterministic time

Frozen scenario timestamps are supplied by fixture/command input where exact oracle comparison requires them.

Rule functions themselves do not call the system clock.

No test may pass only because current wall-clock time happens to match an expectation.

---

# 14. API Implementation Scope

The API is secondary to the scenario runner. It must expose application use cases, not raw persistence CRUD.

Representative command routes:

```text
POST /cases
POST /cases/{case_id}/change-items
POST /cases/{case_id}/gate-a/evaluate
POST /cases/{case_id}/baselines
POST /cases/{case_id}/overlays
POST /executions
POST /executions/{execution_id}/run-impact
POST /executions/{execution_id}/route-assessments
POST /assessments
POST /assessments/{assessment_id}/complete
POST /executions/{execution_id}/classify-reuse
POST /executions/{execution_id}/evaluate-scope-route
POST /executions/{execution_id}/evaluate-readiness
POST /cases/{case_id}/decisions
POST /cases/{case_id}/withdraw
```

Representative query routes:

```text
GET /cases/{case_id}
GET /cases/{case_id}/lineage
GET /executions/{execution_id}
GET /executions/{execution_id}/readiness
GET /decisions/{decision_id}
GET /decisions/{decision_id}/basis
GET /decisions/{decision_id}/handover
```

The implementation must not expose generic PATCH/DELETE routes that bypass frozen immutability.

---

# 15. CLI Implementation Scope

The CLI is the primary demonstrator and verification interface.

Minimum commands:

```text
plm-ref db reset
plm-ref scenario load A
plm-ref scenario run A
plm-ref scenario run B
plm-ref scenario run C
plm-ref verify all
```

Optional useful query commands that do not change semantics:

```text
plm-ref case show CHG-A01
plm-ref execution show IAX-B02
plm-ref decision basis DEC-A01
plm-ref decision handover DEC-A01
```

`verify all` shall exit non-zero when any acceptance assertion fails.

---

# 16. Evidence Output

Final verification writes technical evidence under `evidence/`.

Recommended files:

```text
evidence/
├── scenario_a_actual.json
├── scenario_a_diff.json
├── scenario_b_actual.json
├── scenario_b_diff.json
├── scenario_c_actual.json
├── scenario_c_diff.json
├── decision_DEC-A01_basis.json
├── integrity_results.json
└── verification_summary.md
```

For a passing scenario, the corresponding diff file should be empty or contain an explicit `PASS` structure.

Evidence output is technical verification output, not a PLM business object.

---

# 17. Commit / Review Strategy

Implementation should be incremental and reviewable.

Recommended commit boundaries follow `INC-00` through `INC-14` rather than one large implementation commit.

Each increment should contain:

- production code for that increment;
- migration where applicable;
- tests for the increment;
- no unrelated refactor;
- green acceptance gate before the next increment.

Do not postpone release-critical integrity tests until the final increment.

---

# 18. Failure Handling During Implementation

## 18.1 Ordinary software defect

Examples:

- SQLAlchemy mapping error;
- missing FK;
- parser bug;
- wrong transaction handling;
- fixture-loader bug.

Action:

> Fix the implementation. Do not reopen frozen semantics.

## 18.2 Ambiguous implementation detail

Action:

1. consult Solution Architecture;
2. consult RRR-v0.1;
3. consult Scenario Data oracle;
4. consult LIM;
5. choose the narrower implementation that does not add business meaning.

## 18.3 Actual semantic contradiction

Only when the frozen artefacts make one of Scenarios A–C impossible to implement deterministically:

1. stop the affected increment;
2. document the exact contradictory statements;
3. show the smallest failing fixture/test;
4. do not invent a workaround;
5. reopen only the lowest authoritative artefact necessary to remove the contradiction.

---

# 19. Explicit Non-Implementation Items

Do not implement during v0.1:

- general arbitrary PLM graph impact discovery;
- Add Usage;
- Remove Usage;
- Change Usage;
- Change Effectivity;
- generic replacement/interchangeability;
- service semantics;
- stock disposition;
- plant/production effectivity;
- enterprise source-authority ranking;
- source freshness thresholds;
- full configuration solver;
- enterprise workflow engine;
- risk object;
- generic approval hierarchy;
- elevated-authority technical override;
- automatic Change Item generation;
- automatic Decision Condition generation;
- automated terminal approval;
- production UI;
- enterprise SSO/RBAC;
- microservices;
- event bus;
- cloud deployment.

These omissions are scope controls, not technical debt required for Scenario A–C completion.

---

# 20. Final Verification Procedure

From a clean checkout:

```text
1. create Python environment
2. install project
3. create empty SQLite database
4. run all Alembic migrations
5. run unit tests
6. run integration tests
7. run integrity tests
8. run Scenario A
9. compare A actual state with frozen A expected state
10. reset deterministic scenario store as required
11. run Scenario B
12. compare B actual state with frozen B expected state
13. reset deterministic scenario store as required
14. run Scenario C
15. compare C actual state with frozen C expected state
16. run cross-scenario assertions
17. reconstruct DEC-A01 basis
18. derive Scenario A Handover View
19. write evidence files
20. return PASS only if every mandatory comparison and integrity test passes
```

Equivalent automation may be wrapped by:

```text
plm-ref verify all
```

---

# 21. Final Acceptance Criteria

The implementation may be declared **Scenario A–C Verified** only when:

## Scenario A

- Gate A passes before baseline creation;
- baseline and overlay eligibility pass;
- exact impact candidates/provenance are present;
- `AO-A01..AO-A04` are created and satisfied;
- all supporting Assessments are Complete and locked;
- Gate B is Complete;
- Authorisation Eligibility is Permitted;
- Standard authority is sufficient;
- no Decision exists before explicit authority input;
- explicit authority input creates exactly `DEC-A01`;
- Decision support covers all four mandatory obligations;
- Decision Scope contains only `CI-A01:r1`;
- zero Decision Conditions exist;
- case is `Closed by Decision`;
- Handover View matches the frozen oracle;
- Decision basis is historically reconstructible without live source state.

## Scenario B

- first Gate A and overlay eligibility pass;
- `IAX-B01` produces exact candidates and obligations;
- `ASM-B01` records `REQ-004 = Not Satisfied`;
- `RRR-05` creates `HIST-B01` and no Decision;
- `CI-B02:r1` is added only explicitly;
- amended Gate A passes;
- all five baseline reuse inputs are true and `BL-B01` is reused;
- `OV-B02` contains exact amended scope;
- `IAX-B02` produces exact candidate/provenance set;
- reuse classifications match I/R/RV/R exactly;
- retained fulfilment links new obligations to locked historical Assessments without historical mutation;
- `AO-B21` and `AO-B22` remain unsatisfied;
- Gate B is Incomplete;
- Authorisation Eligibility is Not Evaluated;
- no terminal Decision exists;
- case is `In Assessment`;
- no Handover View exists.

## Scenario C

- Gate A and overlay eligibility pass;
- impact/routing/Assessments are complete;
- Gate B is Complete;
- Authorisation Eligibility is Permitted;
- `RRR-06` derives Elevated;
- current authority is Standard;
- `decision_permitted = false`;
- `escalation_required = true`;
- `HIST-C01 = Escalated` exists;
- no Decision Record exists;
- case remains `Decision Ready`;
- no Handover View exists.

---

# 22. Blocker-Only Review Questions

Review Prototype Implementation Plan v0.1 only for contradictions that would prevent deterministic implementation of Scenarios A–C or silently violate frozen semantics.

1. Does any increment require a business object, state, action, or rule that is not present in the frozen artefacts?
2. Can the migration order represent every required frozen record before it is used?
3. Is Product Version immutability implemented at both application and SQLite layers from the exact baseline-membership lock condition?
4. Can a locked historical Assessment satisfy a later target-execution obligation through `Retained` classification without changing that Assessment or its child set?
5. Does Gate A remain independent of Assessment Baseline data?
6. Is Overlay Execution Eligibility evaluated before impact execution?
7. Can the Frozen Fixture Impact Adapter supply the exact oracle candidates without becoming a general impact engine?
8. Are `RRR-01..06` implemented as deterministic rule functions and version-bound to `RRR-v0.1`?
9. Is routing completion atomic with the complete obligation set?
10. Can `RRR-05` stop the first Scenario B cycle without auto-creating `CI-B02:r1`?
11. Can Scenario B reuse `BL-B01` while creating `OV-B02` and `IAX-B02`?
12. Can retained Assessments fulfil only compatible later obligations while Revalidation Required and Invalidated cannot?
13. Does Gate B remain separate from Authorisation Eligibility?
14. Does Scenario C escalation remain non-terminal?
15. Does Scenario A require an explicit authority disposition before Decision persistence?
16. Can `DEC-A01` be reconstructed without live source-state dependency?
17. Is Handover derived rather than persisted?
18. Can all exact Scenario Data oracle records and derived stop-point values be compared automatically?
19. Are negative cross-case and immutability tests sufficient to prevent silent semantic drift?
20. Can implementation finish this plan without reopening any frozen upstream artefact?

Only a release-blocking contradiction should prevent implementation-plan freeze.

---

# 23. Freeze Criteria

Prototype Implementation Plan v0.1 can be frozen when blocker-only review confirms that:

- every frozen semantic requirement has an implementation location;
- every release-critical persistence invariant has an enforcement task and test;
- every `RRR-v0.1` rule has an implementation task and oracle assertion;
- Scenario A has an end-to-end path to exact Decision persistence and reconstruction;
- Scenario B has an end-to-end path through scope amendment, baseline reuse, Assessment reuse, and the defined In Assessment stop point;
- Scenario C has an end-to-end path to authority escalation without Decision persistence;
- no increment adds a new PLM business semantic;
- final automated verification can compare all three actual outcomes with the frozen Scenario Data oracle.

After freeze, proceed directly to:

> **Prototype implementation**

No additional architecture/specification artefact is required before coding.
