# Product Change Impact Assessment & Decision Readiness

## Release Manifest v0.1.0

**Status:** Pre-release manifest  
**Release target:** `v0.1.0`  
**Release-preparation branch:** `release/v0.1.0`  
**Release-preparation base:** `8bc2aa211ac6a4524f857abf394d081e78664ded`  
**Verified executable baseline:** `7a5733fc7042e33a790db12278f8776d047eb4b6`

---

## 1. Purpose

This manifest fixes the intended `v0.1.0` publication boundary without changing frozen architecture or executable semantics.

It is release metadata only. If any statement here conflicts with a frozen artefact, the frozen authority chain wins.

---

## 2. Release lineage

```text
verified executable baseline
7a5733fc7042e33a790db12278f8776d047eb4b6
        ↓
documentation, reproducibility, visual, demo and review packaging
        ↓
reviewed main before release preparation
8bc2aa211ac6a4524f857abf394d081e78664ded
        ↓
release/v0.1.0
        ↓
protected release-preparation PR
        ↓
annotated tag v0.1.0
        ↓
GitHub Release
        ↓
optional Zenodo archival record / DOI
```

No executable source, migration, scenario input, impact fixture, expected oracle, test or evidence-generation change is planned between the verified executable baseline and the release tag.

---

## 3. Frozen architecture integrity

The six frozen artefacts are governed by:

`docs/SHA256SUMS-frozen-architecture.txt`

The release workflow must continue to pass:

```bash
sha256sum --check docs/SHA256SUMS-frozen-architecture.txt
```

A frozen-artefact hash change is not a release-packaging correction and requires the frozen change-control rule.

---

## 4. Verification evidence integrity

Committed release evidence is governed by:

`evidence/SHA256SUMS.txt`

The release package contains:

```text
evidence/decision_DEC-A01_basis.json
evidence/integrity_results.json
evidence/scenario_a_actual.json
evidence/scenario_a_diff.json
evidence/scenario_b_actual.json
evidence/scenario_b_diff.json
evidence/scenario_c_actual.json
evidence/scenario_c_diff.json
evidence/verification_summary.md
evidence/SHA256SUMS.txt
```

The protected verification workflow must regenerate and check this evidence without leaving a committed diff.

---

## 5. Publication package

The intended source release contains the following public layers:

| Layer | Primary location | Release role |
|---|---|---|
| Repository entry point | `README.md` | Architecture-first overview, claim boundary and reproducibility entry point |
| Frozen architecture | `docs/01-*` through `docs/06-*` | Authoritative business/information/rule/solution/implementation meaning |
| Architecture index | `docs/00-architecture-index.md` | Precedence, hashes, reading paths and public-safe boundary |
| Traceability & assurance | `docs/07-traceability-assurance/` | Business meaning → implementation → test → evidence map |
| Executive & visual package | `docs/08-executive-visual-package/` | Executive brief, three canonical diagrams and ten-slide presentation |
| Demonstration & interview package | `docs/09-demonstration-interview-package/` | 60s/3m/5m/15m/30m explanation paths and evidence extracts |
| Independent review | `docs/10-independent-review/` | Architecture blocker review, technical review and disposition log |
| Release package | `docs/11-release/` | Release notes and release manifest |
| Verification evidence | `evidence/` | Deterministic actual/diff/basis/integrity evidence |
| Reproducibility | `requirements.lock`, `.github/workflows/verify.yml` | Locked Python 3.12 release environment and protected verification |
| Release metadata | `LICENSE`, `CITATION.cff`, `CHANGELOG.md`, `VERIFIED_BASELINE.md` | Licence, citation, release history and executable boundary |

---

## 6. Verification status required before tag

The release tag must not be created until the release-preparation PR and final `main` state satisfy all of the following:

```text
frozen architecture hashes        PASS
full regression suite             PASS
plm-ref verify all — run 1        PASS
release evidence hash check       PASS
plm-ref verify all — run 2        PASS
release evidence hash check       PASS
committed evidence unchanged      PASS
required protected verify status  PASS
```

The recorded executable baseline remains separately identified even when the release tag points to a later documentation/release commit.

---

## 7. Release-state fields

These fields are deliberately left unresolved until the corresponding fact exists:

```text
annotated tag:        PENDING
GitHub release:       PENDING
release date:         PENDING ACTUAL PUBLICATION
Zenodo archive:       PENDING DECISION / PUBLICATION
Zenodo DOI:           PENDING
citation DOI field:   PENDING
maintenance mode:     PENDING FINAL CLOSE-OUT
```

Do not replace these values with planned or guessed publication facts.

---

## 8. Claim boundary

The release establishes deterministic conformance to the bounded synthetic reference case only.

It does not establish:

- enterprise PLM completeness;
- production deployment readiness;
- company-specific process or authority fidelity;
- general arbitrary-graph impact discovery;
- automated engineering judgement or terminal approval.

The architecture remains the primary deliverable; the executable demonstrator remains its proof boundary.
