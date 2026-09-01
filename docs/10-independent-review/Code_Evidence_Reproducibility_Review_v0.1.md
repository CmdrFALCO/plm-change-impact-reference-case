# Product Change Impact Assessment & Decision Readiness

## Code / Evidence Reproducibility Review v0.1

**Session:** 7 — Independent Review & Correction  
**Review type:** Code, evidence and reproducibility review  
**Release target:** `v0.1.0`  
**Repository state reviewed:** `main` at `681845c919dc8092534ab51f2dd9173d2144a603`  
**Verified executable baseline:** `7a5733fc7042e33a790db12278f8776d047eb4b6`  
**Status:** PASS subject to the downstream hardening corrections recorded below

---

# 1. Purpose and review boundary

This review checks whether the repository's release-candidate reproducibility and verification claims are supported by inspectable controls and successful clean-run evidence.

It does not re-interpret PLM business semantics. Architecture findings are recorded separately in:

[`PLM_Business_Architecture_Blocker_Review_v0.1.md`](PLM_Business_Architecture_Blocker_Review_v0.1.md)

This review is also not a claim of bit-for-bit reproducibility of an entire operating-system image or third-party package index. The verified release environment is intentionally narrower: Python 3.12, a hash-locked Python dependency set, pinned GitHub Actions, deterministic repository fixtures/evidence and a clean GitHub Actions runner.

---

# 2. Evidence reviewed

The review inspected or verified the following repository controls:

- `pyproject.toml`;
- `requirements.lock`;
- `.github/workflows/verify.yml`;
- `.gitattributes`;
- `alembic.ini` and migration execution through CI;
- `docs/SHA256SUMS-frozen-architecture.txt`;
- `evidence/SHA256SUMS.txt`;
- `VERIFIED_BASELINE.md`;
- `docs/07-traceability-assurance/Architecture_Traceability_and_Assurance_Pack_v0.1.md`;
- `tests/test_g00_bootstrap.py` through `tests/test_g14_oracle_verification.py`;
- `src/plm_ref/application/oracle_verification.py` and `scenario_runner.py`;
- GitHub ruleset `Protect main` (`21999489`);
- successful protected PR and post-merge verification runs through Sessions 5–6.

A commit comparison from the verified executable baseline to the reviewed `main` state was also inspected.

---

# 3. Verified executable boundary remains intact

Comparison:

```text
base: 7a5733fc7042e33a790db12278f8776d047eb4b6
head: 681845c919dc8092534ab51f2dd9173d2144a603
```

The later lineage adds publication, traceability, visual/demo packaging, governance metadata, dependency locking and CI/release controls.

The comparison contains **no change** to:

- `src/` executable application or rule code;
- Alembic migrations;
- scenario input fixtures;
- impact-result fixtures;
- expected scenario oracles;
- `tests/`;
- committed scenario/evidence generation logic.

Therefore the verified executable baseline remains correctly separated from later documentation/release commits.

**Result:** PASS.

---

# 4. Dependency and build reproducibility

## 4.1 Python environment

`requirements.lock` is generated with Python 3.12 / pip-tools and contains exact package versions plus hashes.

The CI installation path is:

```bash
python -m pip install --require-hashes -r requirements.lock
python -m pip install --no-deps --no-build-isolation -e .
```

This prevents editable-project installation from silently re-resolving runtime or build dependencies.

## 4.2 Build dependency coverage

The lock-generation command includes:

```text
--extra dev
--all-build-deps
--generate-hashes
--allow-unsafe
```

so the release verification environment includes runtime, development/test and build requirements under the same lock.

**Result:** PASS for the Python 3.12 release environment.

---

# 5. CI verification chain

The verification workflow performs, in order:

```text
checkout at exact workflow revision
→ Python 3.12 setup
→ hash-locked dependency installation
→ editable project install without dependency re-resolution
→ Alembic upgrade from an empty SQLite database
→ six frozen architecture SHA-256 checks
→ full pytest regression
→ plm-ref verify all
→ evidence SHA-256 checks
→ plm-ref verify all again
→ evidence SHA-256 checks again
→ git diff --exit-code -- evidence
```

This proves two distinct reproducibility properties:

1. the frozen architecture bytes and committed evidence bytes match their manifests;
2. repeated evidence generation from the same repository state is deterministic and leaves the committed evidence unchanged.

The workflow uses read-only repository permissions.

**Result:** PASS.

---

# 6. Oracle and evidence independence

The implementation preserves three separate fixture roles:

```text
scenario input
≠ impact-result fixture
≠ expected scenario oracle
```

`canonical_actual()` serialises persisted and required derived state from the executed application. The final expected oracle is loaded separately and compared recursively.

The expected oracle is therefore not used as the execution result being tested.

The G14 layer further evaluates:

- Scenario A oracle;
- Scenario B oracle;
- Scenario C oracle;
- cross-scenario assertions;
- active integrity injections;
- historical Decision-basis reconstruction.

**Result:** PASS for the bounded frozen scenarios.

---

# 7. Active negative controls

The final integrity evidence records active IT-16 attempts for all six release-critical cross-case families:

1. execution baseline/overlay;
2. candidate provenance;
3. Assessment fulfilment;
4. Assessment reuse;
5. Decision support;
6. Decision Scope.

Each family records:

```text
attempted = true
rejected = true
passed = true
```

This is materially stronger than merely inspecting correctly formed final scenario rows.

The Assurance Pack correctly avoids claiming that these six injections prove every conceivable cross-case association in the complete Logical Information Model.

**Result:** PASS.

---

# 8. Historical reconstruction

Scenario A Decision reconstruction follows stored historical state:

```text
DEC-A01
→ exact Decision Scope
→ IAX-A01
→ BL-A01 + immutable Baseline Members
→ OV-A01 + exact Overlay membership/local objects
→ Decision Support Assessments
→ locked Assessment semantic children
→ Assessment Evidence Uses
→ Evidence snapshots
```

The release-critical test suite includes reconstruction that does not depend on later mutable live source meaning.

The committed `decision_DEC-A01_basis.json` provides inspectable reconstruction evidence.

**Result:** PASS.

---

# 9. Repository governance

The active GitHub ruleset `Protect main` applies to the default branch and enforces:

- pull request before update;
- required `verify` status check;
- branch deletion protection;
- non-fast-forward / force-push protection;
- no bypass actors.

Required approving reviews are intentionally `0`; this repository governance therefore proves protected CI-mediated change control, not independent human approval.

**Result:** PASS with claim boundary noted.

---

# 10. Review findings and corrections

## TR-01 — Demo commands were Bash-only

**Severity:** P1 packaging / demonstration portability  
**Finding:** `Five_Minute_Deterministic_Demo_v0.1.md` used `export`, `/tmp` and Bash-style environment assignment only. The repository itself documents Windows PowerShell use, so the live-demo instructions were not equally executable on the primary Windows presentation environment.

**Disposition:** add equivalent PowerShell commands while retaining the Bash path. No architecture or executable code change is required.

## TR-02 — Quick-start Python wording was broader than the verified release environment

**Severity:** P1 claim precision  
**Finding:** `pyproject.toml` permits Python `>=3.12`, but the dependency lock and CI evidence are specifically generated and verified on Python 3.12. The README heading `Requirements: Python 3.12+` could be read as a reproducibility claim for later Python versions that have not been verified by the release workflow.

**Disposition:** narrow the README wording to distinguish project metadata compatibility from the **verified release environment: Python 3.12**.

## TR-03 — CI runner alias was mutable

**Severity:** P2 release hardening  
**Finding:** GitHub Actions used `ubuntu-latest`. Python dependencies and Actions were pinned, but the host runner alias itself can move between Ubuntu releases over time.

**Disposition:** pin the release verification workflow to `ubuntu-24.04`. This does not make the environment fully hermetic, but it removes one unnecessary moving alias and better matches the controlled-release wording.

## TR-04 — Final demonstration package was not linked from the root entry path

**Severity:** P2 navigation  
**Finding:** the root README linked the Architecture Index, Assurance Pack and Executive Brief, but not the completed Session 6 Demonstration & Interview Package.

**Disposition:** add one architecture-first navigation link to `docs/09-demonstration-interview-package/README.md`.

## TR-05 — Release citation metadata remains pre-release

**Severity:** P2 deferred release task  
**Finding:** `CITATION.cff` contains the target version but no release date or DOI. This is deliberate while `0.1.0` remains unreleased.

**Disposition:** no Session 7 change. Session 8 must update release/archival metadata only after the actual release/tag and DOI decision exist.

---

# 11. External reproduction boundary

This review inspected clean GitHub Actions runs and repository evidence. It does **not** claim that a separate unmanaged physical workstation reproduced the release byte-for-byte during Session 7.

The supported release claim remains:

> a clean controlled GitHub Actions environment can install the hash-locked Python 3.12 environment, build the empty schema, run the full regression, regenerate deterministic evidence twice and prove that the committed evidence remains unchanged.

That is sufficient for this reference-case release boundary; stronger container/VM image reproducibility would be additional infrastructure scope.

---

# 12. Review verdict

Before corrections:

```text
Code/evidence release blockers:     0
P1 downstream corrections:          2
P2 hardening/navigation items:      2
P2 deferred release-metadata item:  1
Executable-baseline change needed:  no
Frozen-architecture change needed:  no
```

After TR-01 through TR-04 are applied and the protected verification workflow passes, this review may be closed as:

> **Code / Evidence Reproducibility Review: PASS**

No refactor or new implementation baseline is required.
