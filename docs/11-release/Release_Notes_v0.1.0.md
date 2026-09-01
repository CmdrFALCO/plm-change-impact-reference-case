# Product Change Impact Assessment & Decision Readiness — v0.1.0

**Status:** Published  
**Release date:** `2026-09-01`  
**Release tag:** `v0.1.0` → `f15c75b237f85d0926ab0531962e4aba15568fab`  
**Verified executable baseline:** `7a5733fc7042e33a790db12278f8776d047eb4b6`  
**Zenodo DOI:** `10.5281/zenodo.22235248`  
**Licence:** MIT

---

## Release summary

`v0.1.0` is the first public release of the **Product Change Impact Assessment & Decision Readiness** reference case.

It is a public-safe, synthetic PLM Business Architecture case showing how a bounded engineering product-change problem can be translated into explicit business, information and decision semantics, deterministic readiness/routing logic, a controlled executable proof, independent scenario verification and reproducible evidence.

The architecture is the primary deliverable. The Python demonstrator is the proof boundary used to test whether the frozen meaning executes deterministically without semantic shortcuts.

The canonical thesis is:

> **A product change becomes decision-ready only when current state, proposal, discovered impacts, domain conclusions, evidence, decision scope and authority are kept separate—and linked by deterministic, case-local and historically reconstructable rules.**

---

## What is included

### Frozen architecture authority chain

The release publishes six authoritative artefacts in precedence order:

1. Business Architecture Definition v0.3.1;
2. Logical Information Model v0.3.2;
3. Scenario Data Definition v0.1;
4. Readiness and Routing Rules v0.1 / `RRR-v0.1`;
5. Solution Architecture v0.1;
6. Prototype Implementation Plan v0.1.

The repository architecture index records their precedence, versions, public-safe boundary and SHA-256 values.

### Traceability and assurance

The Architecture Traceability and Assurance Pack maps the bounded business requirements, invariants and deterministic rules through implementation controls, acceptance/integrity tests and committed evidence.

### Deterministic executable proof

The reference implementation executes the three frozen scenarios through application services and compares the complete persisted and derived result against independent expected oracles.

The verification design keeps three fixture roles separate:

```text
scenario input
!= impact-result fixture
!= expected scenario oracle
```

The expected oracle is never loaded as application state.

### Executive, visual and demonstration package

The release includes:

- a one-page Executive Brief;
- exactly three canonical architecture diagrams;
- an editable ten-slide canonical presentation plus PDF derivative;
- a five-minute deterministic demo path;
- a 15-minute architecture/interview walkthrough;
- a 30-minute technical-review walkthrough;
- static Scenario A–C and verification evidence extracts;
- approximately 60-second and three-minute verbal explanations;
- Bash and Windows PowerShell demo-command guidance.

No second canonical deck is introduced. The Session 5 presentation remains the visual source at every explanation depth.

---

## Frozen scenario outcomes

### Scenario A — authorised change

```text
Gate B Complete
→ Authorisation Eligibility Permitted
→ Standard authority sufficient
→ explicit authority disposition
→ DEC-A01
→ Closed by Decision
→ Handover View
```

### Scenario B — scope amendment and selective reuse

```text
HIST-B01 Scope Revision Required
→ CI-B02:r1 added explicitly
→ BL-B01 reused
→ OV-B02 + IAX-B02
→ Invalidated / Retained / Revalidation Required / Retained
→ AO-B21 and AO-B22 remain open
→ Gate B Incomplete
→ no Decision
→ Case In Assessment
```

### Scenario C — authority escalation

```text
Gate B Complete
→ Authorisation Eligibility Permitted
→ Elevated > Standard
→ HIST-C01 Escalated
→ no Decision
→ Case remains Decision Ready
```

Together they prove three central distinctions:

> **discovered impact ≠ authorised scope**

> **proposal revision ≠ baseline revision**

> **decision-package completeness ≠ authority to decide**

---

## Recorded verification boundary

The verified executable baseline is:

```text
7a5733fc7042e33a790db12278f8776d047eb4b6
```

Recorded result:

```text
G00–G14 acceptance gates:          15/15 PASS
Full regression:                  185 passed
plm-ref verify all:               PASS / exit 0
Final verification groups:        6/6 PASS
IT-16 cross-case injection sets:  6/6 attempted, rejected and PASS
Repeated evidence generation:     byte-identical
```

The six verification groups are:

1. Scenario A oracle;
2. Scenario B oracle;
3. Scenario C oracle;
4. Cross-scenario assertions;
5. Integrity suite;
6. Historical reconstruction.

The six active IT-16 families are:

- execution baseline/overlay;
- candidate provenance;
- Assessment fulfilment;
- Assessment reuse;
- Decision support;
- Decision Scope.

Documentation and release-packaging commits after the executable baseline do not redefine that verified implementation baseline.

---

## Reproducibility and repository governance

The verified release environment is Python 3.12 with `requirements.lock`.

The protected GitHub Actions verification path:

1. installs the locked environment;
2. creates/upgrades an empty SQLite schema through Alembic;
3. verifies the six frozen-architecture hashes;
4. runs the complete regression suite;
5. executes `plm-ref verify all` twice;
6. checks the committed evidence SHA-256 manifest after each run;
7. proves that verification leaves committed evidence unchanged.

`main` is protected by pull-request and required `verify` status rules.

---

## Independent review

Before release, the case received a dedicated Session 7 review pass.

Result:

```text
Release-blocking architecture findings: 0
Frozen artefacts requiring change:       0
Scenario semantics requiring change:     0
New PLM scope required:                  0
P1 release issues remaining:             0
```

The review produced only downstream portability, release-environment precision, CI-hardening and navigation corrections. No executable baseline change was required.

---

## Supported claims

This release supports the following bounded claims:

- deterministic execution of frozen Scenarios A–C;
- explicit business, information and decision semantics;
- case-local lineage and immutable historical reconstruction;
- controlled separation of Gate B, Authorisation Eligibility, authority sufficiency and terminal Decision;
- explicit terminal authority action before Decision persistence;
- independent oracle comparison and active integrity controls;
- deterministic committed evidence and reproducible verification governance;
- architecture-first translation from bounded problem to executable proof.

## Explicit non-claims

This release does **not** claim:

- company-specific PLM process, workflow, data-model or authority fidelity;
- enterprise PLM completeness or production deployment readiness;
- general arbitrary-graph impact discovery;
- automated engineering judgement or automated terminal approval;
- enterprise programme, budget, capacity or organisational authority;
- downstream engineering release, manufacturing, stock or service implementation.

The bounded impact-analysis adapter supplies the frozen impact results for the four defined executions; it is not presented as a generic PLM impact engine.

---

## Release package navigation

Recommended entry points:

- `README.md` — repository overview and quick start;
- `docs/00-architecture-index.md` — frozen authority chain and reading paths;
- `docs/07-traceability-assurance/` — architecture-to-evidence assurance map;
- `docs/08-executive-visual-package/` — executive brief, diagrams and canonical presentation;
- `docs/09-demonstration-interview-package/` — demo and walkthrough material;
- `docs/10-independent-review/` — release-blocker and reproducibility review records;
- `evidence/` — committed deterministic verification evidence and SHA-256 manifest;
- `VERIFIED_BASELINE.md` — executable verification boundary.

---

## Citation and archival status

Published release facts:

- GitHub release date: **2026-09-01**;
- annotated tag: **`v0.1.0`**;
- release commit: **`f15c75b237f85d0926ab0531962e4aba15568fab`**;
- GitHub Release: `https://github.com/CmdrFALCO/plm-change-impact-reference-case/releases/tag/v0.1.0`;
- Zenodo archive: **published**;
- Zenodo version DOI: **`10.5281/zenodo.22235248`**;
- archived source file: `plm-change-impact-reference-case-v0.1.0.zip`;
- local SHA-256 of the archived tagged source: `ED7FC58122F86B9E230A185CECB6DD167E8FEED74713F04001FD1F1E3F57AFCB`.

The Zenodo source archive was generated directly from the exact `v0.1.0` annotated tag. DOI/date synchronization back to `main` is post-release metadata and does not modify the published tag or archived source bytes.
