# Product Change Impact Assessment & Decision Readiness

## Five-Minute Deterministic Demo v0.1

**Purpose:** Demonstrate the executable prototype only where it proves frozen architectural statements.  
**Target duration:** 5 minutes  
**Primary visual source:** Session 5 canonical presentation  
**Primary technical source:** existing deterministic CLI and committed evidence

---

## Demo principle

Do not give a software tour.

The demo must prove four architectural statements:

1. historical evaluation uses a frozen Assessment Baseline plus a separate proposed-state Overlay Revision;
2. discovered impact does not automatically become authorised scope;
3. Decision Package completeness, Authorisation Eligibility and authority sufficiency are separate;
4. implementation conformance is checked against independent frozen scenario oracles and integrity controls.

The live interface is intentionally minimal.

---

# 0:00–0:40 — Establish the architectural problem

**Show:** canonical presentation, Slide 5 — *Current state, baseline and proposal are not equivalent*.

**Say:**

> A product change cannot safely be represented as only Revision A to Revision B. For a decision I need to know the exact current state that was evaluated, what was proposed without modifying that state, which impacts and Assessments followed, and exactly what basis was eventually authorised. The architecture therefore separates the Assessment Baseline, Change Item revisions, Overlay Revision and Impact-analysis Execution.

**Point to:**

```text
Assessment Baseline
+
Overlay Revision
+
RRR-v0.1
→ Impact-analysis Execution
```

**Architectural proposition:** current state, historical evaluated state and hypothetical proposed state are not equivalent.

---

# 0:40–1:45 — Scenario A: prove terminal Decision lineage

## Live action

Use a disposable demo database so the repository's committed evidence remains untouched.

```bash
export PLM_REF_DATABASE_PATH=/tmp/plm-ref-demo.db
plm-ref db reset
plm-ref scenario run A
```

Expected CLI output is intentionally terse:

```text
database reset
CHG-A01
```

The CLI proves that the frozen scenario executes through the real application services; it is not intended to be the explanatory UI.

## Show immediately after the command

Open:

[`evidence-extracts/01_scenario_a_terminal_basis.md`](evidence-extracts/01_scenario_a_terminal_basis.md)

## Say

> Scenario A reaches a complete Decision Package, Authorisation Eligibility is Permitted, and Standard authority is sufficient. But the software still does not choose an engineering outcome. The terminal Decision exists because the scenario supplies an explicit authority disposition. That creates DEC-A01 with an exact Decision Scope and supporting Assessment lineage, and only then is the case Closed by Decision.

**Proof chain:**

```text
Gate B Complete
→ Authorisation Eligibility Permitted
→ Standard = Standard
→ explicit authority disposition
→ DEC-A01
→ Closed by Decision
→ Handover View
```

**Architectural proposition:** deterministic readiness logic can establish permission to decide without automating the terminal engineering judgement.

---

# 1:45–2:55 — Scenario B: prove controlled scope amendment

**Show:**

1. [`evidence-extracts/02_scenario_b_scope_amendment.md`](evidence-extracts/02_scenario_b_scope_amendment.md)
2. [`evidence-extracts/03_scenario_b_reuse_and_readiness.md`](evidence-extracts/03_scenario_b_reuse_and_readiness.md)

## Say

> In the first execution, Product Engineering concludes that the occurrence applicability is not aligned with the proposed product-state scope. RRR-05 therefore records HIST-B01 — Scope Revision Required. The system does not silently change the occurrence and does not create the new Change Item automatically. CI-B02:r1 is added explicitly.
>
> The proposal has changed, so a new Overlay Revision and Impact-analysis Execution are required. The authoritative current state has not changed, so the five frozen reuse inputs permit BL-B01 to be reused. Historical Assessments are then classified individually relative to IAX-B02: Invalidated, Retained, Revalidation Required and Retained. The retained Validation and Purchasing/Cost Assessments satisfy compatible new obligations without modifying their historical content, while Product Engineering and Manufacturing obligations remain open. Gate B is therefore Incomplete and no Decision exists.

**Proof propositions:**

> **discovered impact ≠ authorised scope**

> **proposal revision ≠ baseline revision**

---

# 2:55–3:40 — Scenario C: prove readiness is not authority

**Show:**

[`evidence-extracts/04_scenario_c_authority_escalation.md`](evidence-extracts/04_scenario_c_authority_escalation.md)

## Say

> Scenario C has a complete Decision Package and Authorisation Eligibility is Permitted. Required authority is Elevated while current authority is Standard. That makes authority insufficient. The deterministic result is HIST-C01 — Escalated. There is no Decision Record, and the case remains Decision Ready because the package itself is still complete.

**Proof chain:**

```text
Gate B Complete
→ Authorisation Eligibility Permitted
→ Elevated > Standard
→ HIST-C01 Escalated
→ no Decision
→ Case remains Decision Ready
```

**Architectural proposition:**

> **decision-package completeness ≠ authority to decide**

---

# 3:40–4:35 — Verification, not feature demonstration

## Live action

Keep verification output separate from committed repository evidence:

```bash
PLM_REF_DATABASE_PATH=/tmp/plm-ref-verify.db \
python -c 'from plm_ref.application.scenario_runner import verify_all; raise SystemExit(0 if verify_all("/tmp/plm-ref-verify.db", "/tmp/plm-ref-demo-evidence") else 1)'
```

Then show the committed evidence extract:

[`evidence-extracts/05_verification_evidence.md`](evidence-extracts/05_verification_evidence.md)

## Say

> The important result is not that a Python command completes. The implementation is compared against independent frozen scenario oracles, cross-scenario assertions, integrity controls and historical reconstruction checks. The verified baseline records G00 through G14 as 15 out of 15 passed, 185 pytest tests passed, six out of six final verification groups passed, byte-identical repeated evidence generation and six out of six IT-16 cross-case injection families actively attempted and rejected.

**Architectural proposition:** implementation is the conformance proof boundary for the frozen architecture.

---

# 4:35–5:00 — Close on architecture

**Return to:** canonical presentation, Slide 4 — *From engineering problem to executable evidence*.

**Say:**

> The primary deliverable is therefore not a Python PLM application. It is an explicit business, information and decision architecture whose distinctions can be traced into deterministic rules, implementation controls, tests and reproducible evidence. The prototype tells us whether that frozen architecture was precise enough to execute without semantic shortcuts.

---

# Operator preparation

Before the session:

```bash
python -m pip install -e '.[dev]'
rm -f /tmp/plm-ref-demo.db /tmp/plm-ref-verify.db
rm -rf /tmp/plm-ref-demo-evidence
```

Keep these items pre-opened:

1. canonical Slide 5;
2. Scenario A terminal-basis extract;
3. Scenario B scope-amendment extract;
4. Scenario B reuse/readiness extract;
5. Scenario C authority extract;
6. verification extract;
7. canonical Slide 4.

Do not improvise additional runtime claims from database rows or API routes during the five-minute version. Deeper inspection belongs to the 30-minute technical-review path.

---

# Failure handling during a live demonstration

If a local command fails because of environment setup, do not reinterpret the architecture or substitute an unverified result.

Use the committed static evidence and state explicitly that:

- the static extracts are derived from committed verification evidence;
- the recorded executable baseline is `7a5733fc7042e33a790db12278f8776d047eb4b6`;
- the failure is a local demonstration-environment issue unless verification shows otherwise.

Do not modify frozen artefacts, fixtures, expected oracles or evidence files to recover a presentation.
