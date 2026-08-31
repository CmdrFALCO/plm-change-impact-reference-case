# Product Change Impact Assessment & Decision Readiness

A **public-safe PLM Business Architecture reference case** with a deterministic executable demonstrator.

This repository shows how an engineering product-change problem can be transformed into **traceable, auditable and executable business/process/information/decision architecture**. The implementation is evidence that the architecture is precise enough to execute deterministically; it is **not the primary deliverable and not a claim to represent any company-specific PLM process**.

## Status

**Implementation complete — G00 to G14 PASS (15/15 acceptance gates).**

- Verified implementation baseline: `7a5733fc7042e33a790db12278f8776d047eb4b6`
- Full regression at the verified baseline: **185 passed**
- `plm-ref verify all`: **PASS / exit 0**
- Repeated verification: **byte-identical evidence output**
- Final verification groups: **6/6 PASS**
- IT-16 cross-case injection families: **6/6 attempted, rejected and PASS**

The verified implementation commit is intentionally identified separately from later documentation-only commits.

## Start with the architecture

The architecture is the primary deliverable. The executable demonstrator is its verification boundary.

- **15-minute orientation:** [Architecture Index](docs/00-architecture-index.md) → Business Architecture capability/process/scenarios/invariants → the frozen scenario summary below → verification summary.
- **45-minute architecture review:** Architecture Index → Business Architecture → Logical Information Model invariants and integrity rules → `RRR-v0.1` evaluation order and scenario traces → Solution Architecture objectives and decisions.
- **Deep technical review:** all six frozen artefacts in precedence order → scenario/impact fixtures → application and rule modules → `G00–G14` tests → committed evidence.

The [Architecture Index](docs/00-architecture-index.md) records document status, precedence, SHA-256 values, public-safe boundaries and detailed reading paths.

## Why this reference case exists

Product change is broader than replacing one object revision with another. A decision-ready change package must distinguish several different kinds of state and evidence that are often blurred together in implementation-centric solutions.

This case therefore separates:

- authoritative current product state;
- the proposed change and its immutable revision identity;
- discovered impacts and their provenance;
- domain assessments and requirement conclusions;
- evidence as it was used at assessment time;
- decision-package completeness;
- authorisation eligibility;
- required versus current decision authority;
- non-terminal routing history;
- terminal decision scope and outcome;
- historical reconstruction of the decision basis;
- the downstream Handover View derived from an authorised decision.

The purpose is to demonstrate that these semantics can be made **deterministic, case-local, historically reconstructable and testable without expanding the PLM scope for software convenience**.

## Core architectural idea

Impact analysis is modeled as:

**immutable Assessment Baseline + versioned Change Item overlay**

The baseline captures the authoritative current-state decision basis. Proposal changes create new immutable Change Item revisions and Overlay Revisions; they do not silently rewrite historical state.

Key invariants include:

- only `Revise Product State` and `Change Applicability` are executable Change Item actions in this reference case;
- Gate A does not depend on Baseline Members;
- a Product Version becomes immutable when captured as a Product Version Baseline Member;
- an Assessment Baseline and Overlay Revision become immutable after first Impact-analysis Execution use;
- Change Item revisions referenced by an Overlay Revision or Decision Scope cannot be changed or deleted;
- completed Assessments and their semantic children are locked;
- retained historical Assessments can satisfy a later obligation only through execution-relative `Retained` reuse classification;
- Evidence does not establish Requirement compliance — the Assessment records the Requirement Conclusion;
- Gate B answers package completeness only;
- Authorisation Eligibility is evaluated separately from Gate B;
- authority sufficiency is evaluated separately from both;
- only an explicit terminal authority disposition creates a Decision Record;
- non-terminal routing creates Process-history Entries, not Decisions;
- release-critical lineage must remain within one Change Case;
- Handover and historical reconstruction are derived query projections, not persisted PLM business objects.

## Frozen architecture authority chain

Implementation follows this precedence order:

1. [**Business Architecture Definition v0.3.1 — Frozen Implementation Baseline**](docs/01-business-architecture/Business_Architecture_Definition_v0.3.1_Frozen_Implementation_Baseline.md)
2. [**Logical Information Model v0.3.2 — Frozen Implementation Baseline**](docs/02-logical-information-model/Product_Change_Impact_Decision_Readiness_Logical_Information_Model_v0.3.2_Frozen_Implementation_Baseline.md)
3. [**Scenario Data Definition v0.1 — Frozen Implementation Baseline**](docs/03-scenario-data/Product_Change_Impact_Decision_Readiness_Scenario_Data_Definition_v0.1.md)
4. [**Readiness and Routing Rules v0.1 — Frozen Implementation Baseline**](docs/04-readiness-routing-rules/Product_Change_Impact_Decision_Readiness_Readiness_and_Routing_Rules_v0.1_Frozen_Implementation_Baseline.md) (`RRR-v0.1`)
5. [**Solution Architecture v0.1 — Frozen Implementation Baseline**](docs/05-solution-architecture/Product_Change_Impact_Decision_Readiness_Solution_Architecture_v0.1_Frozen_Implementation_Baseline.md)
6. [**Prototype Implementation Plan v0.1 — Frozen Implementation Baseline**](docs/06-implementation-plan/Product_Change_Impact_Decision_Readiness_Prototype_Implementation_Plan_v0.1_Frozen_Implementation_Baseline.md)

The software was required to conform to these semantics. Upstream meaning was not changed to simplify implementation.

## Frozen scenarios

| Scenario | Purpose | Final state |
| --- | --- | --- |
| **A — Authorised change** | Complete bounded change assessment and terminal authorisation | Gate B `Complete`; Eligibility `Permitted`; Standard authority sufficient; `DEC-A01`; Case `Closed by Decision`; Handover available |
| **B — Scope revision and assessment reuse** | Discover that occurrence applicability must change, explicitly amend scope, reuse the original baseline and retain only compatible Assessments | `HIST-B01` non-terminal route; second execution `IAX-B02`; two obligations remain open; Gate B `Incomplete`; Case `In Assessment`; no Decision; no Handover |
| **C — Elevated authority route** | Complete the package but require authority above the current level | Gate B `Complete`; Eligibility `Permitted`; required `Elevated`, current `Standard`; `HIST-C01` escalation; Case `Decision Ready`; no Decision; no Handover |

Together the three scenarios demonstrate approval, controlled scope amendment with selective reuse, and non-terminal authority escalation without introducing a generic workflow engine.

## Independent verification model

The verification design deliberately separates three different fixture roles:

```text
scenario input
!= impact-result fixture
!= expected scenario oracle
```

The expected oracle is not loaded as application state. Each scenario runs through the real application services, the resulting persisted and derived state is canonicalized, and the complete actual state is compared strictly against the independent expected oracle.

The final G14 verification passes only when all six groups pass:

1. Scenario A oracle
2. Scenario B oracle
3. Scenario C oracle
4. Cross-scenario assertions
5. Integrity suite
6. Historical reconstruction

The integrity suite also performs active **IT-16 cross-case injection tests** for all six release-critical lineage families:

- execution baseline/overlay;
- candidate provenance;
- Assessment fulfilment;
- Assessment reuse;
- Decision support;
- Decision Scope.

Each forbidden cross-case operation must be attempted and rejected.

## Verification evidence

Successful `plm-ref verify all` runs generate deterministic technical evidence under `evidence/`:

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

The scenario diff files report PASS only when strict oracle comparison produces no differences. `integrity_results.json` contains the six top-level verification groups, cross-scenario assertions, historical comparison result, and the active IT-16 injection results.

Evidence generation is deterministic: the final verification was executed twice against the same implementation state and produced byte-identical files.

## Quick start

Requirements: **Python 3.12+**.

```bash
git clone https://github.com/CmdrFALCO/plm-change-impact-reference-case.git
cd plm-change-impact-reference-case

python -m pip install -e '.[dev]'

pytest -q
plm-ref verify all
```

By default the CLI uses `plm_ref.db`. Set `PLM_REF_DATABASE_PATH` to use another SQLite database path.

### Run the scenarios individually

Reset before an independent scenario run:

```bash
plm-ref db reset
plm-ref scenario run A

plm-ref db reset
plm-ref scenario run B

plm-ref db reset
plm-ref scenario run C
```

You can also load only the explicit scenario input state:

```bash
plm-ref db reset
plm-ref scenario load A
```

Useful commands:

```bash
plm-ref --help
plm-ref version
plm-ref db reset
plm-ref scenario load A
plm-ref scenario run A
plm-ref verify all
```

## Repository structure

```text
.
├── docs/          # frozen architecture authority chain and publication index
├── data/          # frozen source, baseline, impact and expected scenario fixtures
├── evidence/      # deterministic verification evidence
├── migrations/    # Alembic schema and integrity migrations
├── src/plm_ref/
│   ├── application/      # use cases, orchestration, reconstruction and verification
│   ├── domain/           # domain payloads and errors
│   ├── infrastructure/   # SQLite/SQLAlchemy persistence and impact adapter
│   ├── interfaces/       # Typer CLI and FastAPI boundary
│   ├── rules/            # deterministic RRR-v0.1 rule functions
│   └── views/            # bounded view boundary
├── tests/         # acceptance, integration and integrity tests G00-G14
├── alembic.ini
├── pyproject.toml
└── README.md
```

## Technical implementation

The demonstrator is intentionally small and local:

- Python 3.12+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x
- SQLite 3
- Alembic
- pytest
- Typer
- YAML / JSON fixtures

It is a modular monolith. The reference case intentionally does **not** add a graph database, message broker, generic workflow/rules platform, cloud dependency, AI component, or broader PLM domain scope.

## Historical reconstruction and Handover

For an authorised Decision, the historical decision basis can be reconstructed from immutable persisted state rather than later mutable live source state. The reconstruction includes the selected Change Item revision, Assessment Baseline and Baseline Member snapshots, Overlay Revision and local proposed state, Impact-analysis Execution, locked supporting Assessments, Requirement Conclusions, Evidence Uses with immutable evidence snapshots, Decision Support and Decision Scope.

The Handover View is derived only for authorised decisions. It is not stored as another business object. Scenario A derives the authorised `CI-A01:r1`, proposed Product State action/reference, applicability constraint, planned engineering effective date and Decision Conditions. Scenarios B and C correctly produce no Handover.

## Public-safe scope

All names, identifiers, products, requirements, evidence, actors, timestamps and scenarios are synthetic. This repository demonstrates architecture and implementation techniques; it does not document or reproduce a proprietary PLM process, company decision model or production system.

The prototype should therefore be read as **executable verification of a bounded Business Architecture reference case**, not as a reusable enterprise PLM application.
