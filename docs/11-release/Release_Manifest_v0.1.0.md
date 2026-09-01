# Product Change Impact Assessment & Decision Readiness

## Release Manifest v0.1.0

**Status:** Published release manifest  
**Release:** `v0.1.0`  
**Release date:** `2026-09-01`  
**Release commit:** `f15c75b237f85d0926ab0531962e4aba15568fab`  
**Verified executable baseline:** `7a5733fc7042e33a790db12278f8776d047eb4b6`  
**Zenodo DOI:** `10.5281/zenodo.22235248`

---

## 1. Purpose

This manifest records the published `v0.1.0` boundary without changing frozen architecture or executable semantics.

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
protected release-preparation PR #8
        ↓
release commit
f15c75b237f85d0926ab0531962e4aba15568fab
        ↓
annotated tag v0.1.0
        ↓
GitHub Release — 2026-09-01
        ↓
Zenodo archival record
10.5281/zenodo.22235248
```

No executable source, migration, scenario input, impact fixture, expected oracle, test or evidence-generation change occurred between the verified executable baseline and the release tag.

---

## 3. Frozen architecture integrity

The six frozen artefacts are governed by:

`docs/SHA256SUMS-frozen-architecture.txt`

The protected release workflow passed:

```bash
sha256sum --check docs/SHA256SUMS-frozen-architecture.txt
```

A frozen-artefact hash change is not a release-packaging correction and remains subject to the frozen change-control rule.

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

The protected verification workflow regenerated and checked this evidence twice without leaving a committed diff before the release tag was created.

---

## 5. Publication package

The published source release contains the following public layers:

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

## 6. Pre-tag verification status

The release tag was created only after the release-preparation PR and final `main` state satisfied:

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

The recorded executable baseline remains separately identified even though the release tag points to a later documentation/release commit.

---

## 7. Published release-state fields

```text
annotated tag:        v0.1.0
release commit:       f15c75b237f85d0926ab0531962e4aba15568fab
GitHub release:       PUBLISHED
release date:         2026-09-01
Zenodo archive:       PUBLISHED
Zenodo DOI:           10.5281/zenodo.22235248
citation DOI field:   RECORDED POST-RELEASE ON MAIN
maintenance mode:     PENDING FINAL CAREER/PORTFOLIO CLOSE-OUT
```

GitHub Release:

`https://github.com/CmdrFALCO/plm-change-impact-reference-case/releases/tag/v0.1.0`

Zenodo DOI:

`https://doi.org/10.5281/zenodo.22235248`

---

## 8. Zenodo archival provenance

The Zenodo source archive was generated from the exact published tag using `git archive`:

```text
archive file: plm-change-impact-reference-case-v0.1.0.zip
source tag:   v0.1.0
source commit:f15c75b237f85d0926ab0531962e4aba15568fab
SHA-256:      ED7FC58122F86B9E230A185CECB6DD167E8FEED74713F04001FD1F1E3F57AFCB
```

The DOI and release date were intentionally not embedded by modifying the already-published tag. They are synchronized into post-release repository metadata on `main`, preserving the archived source as an exact representation of `v0.1.0`.

---

## 9. Claim boundary

The release establishes deterministic conformance to the bounded synthetic reference case only.

It does not establish:

- enterprise PLM completeness;
- production deployment readiness;
- company-specific process or authority fidelity;
- general arbitrary-graph impact discovery;
- automated engineering judgement or terminal approval.

The architecture remains the primary deliverable; the executable demonstrator remains its proof boundary.
