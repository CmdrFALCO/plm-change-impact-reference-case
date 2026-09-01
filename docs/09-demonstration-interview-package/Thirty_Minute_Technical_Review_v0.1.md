# Product Change Impact Assessment & Decision Readiness

## Thirty-Minute Technical-Review Walkthrough v0.1

**Purpose:** Review how the frozen business, information and decision architecture is carried into deterministic implementation controls, tests and committed evidence.  
**Target duration:** 30 minutes  
**Primary visual source:** Session 5 canonical ten-slide presentation  
**Primary assurance source:** Architecture Traceability and Assurance Pack, frozen artefacts, implementation plan and committed evidence

---

## Review principle

This is not a third presentation and not a code tour.

Use the same architecture-first spine as the 15-minute walkthrough, then add technical depth only where it explains how a frozen architectural statement is represented, enforced or verified.

The default path is **repository inspection + static evidence**, with optional live execution only if the reviewer specifically asks for it. The purpose is to make the conformance chain inspectable:

```text
business meaning
→ information semantics
→ deterministic rule
→ implementation control
→ acceptance / integrity test
→ committed evidence
```

Do not explain implementation choices as if they were business architecture. Keep these two categories separate throughout:

- **Architecture decision:** required meaning or invariant inherited from the frozen artefacts.
- **Implementation choice:** Python module, SQL table, transaction boundary, SQLite trigger, CLI route or fixture adapter used to prove that meaning in the bounded demonstrator.

---

# Timing map

| Time | Material | Technical purpose |
|---|---|---|
| 0:00–1:30 | Slides 1–2 | Problem, thesis and decision-basis gap |
| 1:30–3:00 | Slides 3–4 | Boundary, authority chain and proof model |
| 3:00–6:00 | Slide 5 + Scenario A basis | Baseline / overlay / execution separation |
| 6:00–9:00 | Slide 6 + Decision basis | Information model, case-local lineage and historical reconstruction |
| 9:00–12:00 | Slide 4 + rules / impact boundary | Bounded impact port and deterministic `RRR-v0.1` mechanics |
| 12:00–17:00 | Slide 8 + Scenario B extracts | Scope amendment, baseline reuse, Assessment reuse and immutability |
| 17:00–20:30 | Slide 7 + Scenario C extract | Gate B, Eligibility, authority sufficiency and non-terminal escalation |
| 20:30–23:30 | Scenario A terminal basis | Explicit Decision persistence, support coverage and Handover derivation |
| 23:30–27:00 | Slide 9 + verification extract | Gates, integrity tests, oracle separation and reproducibility |
| 27:00–29:00 | Slide 10 + Assurance Pack | Bounded findings, limitations and non-claims |
| 29:00–30:00 | Slide 4 or 1 | Close on architecture-to-evidence method |

If the review becomes interactive, preserve the technical blocks at 3:00–6:00, 12:00–23:30 and 23:30–27:00. Compress introductory and closing material first.

---

# 0:00–1:30 — Problem and architectural thesis

**Show:** Slides 1–2.

**Say:**

> The reference case starts from a deliberately narrow problem: a product change has to become decision-ready without collapsing current state, proposal, discovered impacts, engineering conclusions, evidence, decision scope and authority into one generic workflow state. `Revision A → Revision B` shows succession, but it does not identify what was evaluated, what assumptions and configuration context applied, what impacts were discovered, what Assessments were mandatory or what exact scope an authority eventually disposed.
>
> The architecture therefore makes those distinctions explicit first. The implementation exists only to test whether the frozen meaning can be executed deterministically without adding shortcuts.

**Technical review point:** before discussing tables or Python, make the reviewer identify the semantic distinction being enforced.

---

# 1:30–3:00 — Boundary, precedence and proof model

**Show:** Slides 3–4.

## Authority chain

Point to the frozen precedence:

```text
Business Architecture v0.3.1
→ Logical Information Model v0.3.2
→ Scenario Data Definition v0.1
→ RRR-v0.1
→ Solution Architecture v0.1
→ Prototype Implementation Plan v0.1
→ code, migrations, fixtures, tests and evidence
```

**Say:**

> The key governance rule is that software convenience cannot redefine higher-level meaning. The implementation plan explicitly says that if a software task conflicts with a frozen upstream artefact, the software task is wrong unless a real contradiction makes Scenarios A–C impossible to execute deterministically.

## Proof boundary

Explain the three separate fixture roles:

```text
scenario input fixture
≠
impact-result fixture
≠
expected scenario oracle
```

The expected final state is not loaded as execution output. The bounded impact adapter supplies only the externally defined Impact Candidate/provenance result for the specified execution; the independent expected oracle is used later for comparison.

**Technical proposition:** conformance is not demonstrated by a hard-coded final database state.

---

# 3:00–6:00 — Baseline, overlay and execution separation

**Show:** Slide 5, then [`evidence-extracts/01_scenario_a_terminal_basis.md`](evidence-extracts/01_scenario_a_terminal_basis.md).

## Architecture decision

Impact analysis evaluates:

```text
immutable Assessment Baseline
+
versioned Change Item overlay
```

The overlay must not mutate the authoritative current state.

## Information semantics

Walk through the exact lineage in Scenario A:

```text
CHG-A01
→ CI-A01:r1
→ BL-A01
→ OV-A01
→ IAX-A01 / RRR-v0.1
```

Explain:

- `BL-A01` contains Baseline Member snapshots, not merely live references;
- `CI-A01:r1` is immutable technical proposal content;
- `OV-A01` contains the exact active Change Item revision set;
- `OVOBJ-A01-PV` is a hypothetical overlay-local successor, not an authoritative Product Version;
- `IAX-A01` binds the exact baseline, overlay and rule-set version.

## Implementation controls

If the reviewer asks how this is enforced, open the relevant modules/tests rather than explaining from memory:

- `src/plm_ref/application/baseline.py`
- `src/plm_ref/application/overlay.py`
- `tests/test_g03_baseline.py`
- `tests/test_g04_overlay.py`

The important controls are:

1. Gate A remains baseline-independent;
2. Overlay Execution Eligibility performs the later baseline-relative target checks;
3. a Product Version captured as a Product Version Baseline Member is protected from UPDATE and DELETE by application guard and SQLite trigger;
4. a proposed successor remains possible only as overlay-local state.

**Do not claim:** that SQLite itself is the architecture. SQLite is one implementation mechanism proving the frozen immutability requirement.

---

# 6:00–9:00 — Information model, lineage and historical reconstruction

**Show:** Slide 6 and Scenario A terminal-basis extract.

## Four information bands

Use the canonical information bands:

1. **Product information:** Product Element, Product Version, Product Structure Occurrence, Configuration Context, Applicability, Effectivity.
2. **Change and evaluated state:** Change Case, Change Item Identity/Revision, Assessment Baseline, Overlay Revision, Impact-analysis Execution.
3. **Impact and assessment:** Impact Candidate Provenance, Assessment Obligation, Assessment, Requirement Conclusion, Assessment Evidence Use, Assessment Reuse Classification.
4. **Decision and audit:** Open Item, Process-history Entry, Decision Record, Decision Scope Item, Decision Support Assessment, Decision Condition, Handover View.

## Two distinctions to defend

### Evidence is not a conclusion

```text
Evidence Record
→ used by Assessment
→ Assessment owns Requirement Conclusion
```

A predecessor Evidence Record does not automatically become valid for the proposed successor. Transferability is recorded in the Assessment Evidence Use.

### Impact is not scope

```text
Impact Candidate
≠ Change Item
≠ Decision Scope Item
```

Discovery identifies potential consequence; it cannot silently author a Change Item or expand the terminal Decision Scope.

## Historical reconstruction

Explain the reconstruction path:

```text
DEC-A01
→ Decision Scope Item
→ exact Change Item Revision
→ IAX-A01
→ BL-A01 + Baseline Members
→ OV-A01 + Overlay-local Objects
→ Decision Support Assessments
→ locked Assessment children
→ Assessment Evidence Uses
→ immutable Evidence snapshots
```

No live source read is necessary to explain the historical Decision basis.

If asked for the implementation proof, open:

- `src/plm_ref/application/history_and_views.py`
- `tests/test_g12_history_and_handover.py`
- `evidence/decision_DEC-A01_basis.json`

---

# 9:00–12:00 — Impact boundary and deterministic rule mechanics

**Return to:** Slide 4 or the Architecture-to-evidence chain.

## Bounded impact-analysis boundary

Be explicit:

> The reference case does not implement a general PLM graph-impact engine.

The Solution Architecture deliberately defines:

```text
ImpactAnalysisPort
→ FrozenFixtureImpactAdapter
```

The adapter supplies the exact candidate/provenance result sets for the four frozen executions only after checking the expected case-local baseline/overlay lineage. Downstream routing, Assessment, readiness and Decision semantics are real deterministic application logic; general impact discovery is outside the claim boundary.

This is a scope control, not a hidden missing feature.

## `RRR-v0.1` mechanics

Explain that the rules are ordinary typed deterministic functions with no dependency on:

- randomness;
- wall-clock decision inputs;
- network access;
- AI/semantic text interpretation;
- mutable global state.

Key examples:

- `RRR-01..04` create explicit Assessment Obligations;
- `RRR-05` creates `Scope Revision Required` from structured scope relation + Requirement Conclusion data, not narrative text parsing;
- `RRR-06` maps the exact synthetic trigger to Standard or Elevated authority;
- unsupported/missing mandatory rule inputs fail closed.

The bounded applicability grammar supports only exact conjunctions such as:

```text
Feature = "Value" [AND Feature = "Value"]*
```

Do not reinterpret that parser as a configuration engine.

---

# 12:00–17:00 — Scenario B technical deep dive

**Show:**

1. [`evidence-extracts/02_scenario_b_scope_amendment.md`](evidence-extracts/02_scenario_b_scope_amendment.md)
2. [`evidence-extracts/03_scenario_b_reuse_and_readiness.md`](evidence-extracts/03_scenario_b_reuse_and_readiness.md)

Scenario B is the best technical proof of the architecture because it exercises proposal revision, baseline reuse, historical Assessment reuse and a deliberate incomplete stop point.

## First execution

Walk the chain:

```text
CI-B01:r1
→ BL-B01
→ OV-B01
→ IAX-B01
→ RRR-01..04
→ ASM-B01 / REQ-004 = Not Satisfied
→ RRR-05
→ HIST-B01 Scope Revision Required
```

Important consequences:

- `HIST-B01` is a Process-history Entry, not a Decision Record;
- the impact result does not change the Proposed Change Scope by itself;
- `RRR-05` does not auto-create the required Change Item.

Then:

```text
Change Owner / scenario driver explicitly creates CI-B02:r1
```

This is the proof of:

> **discovered impact ≠ authorised scope**

## Baseline reuse

The new proposal cycle needs:

```text
new Overlay Revision
+
new Impact-analysis Execution
```

but not automatically a new Assessment Baseline.

The five baseline-validity inputs remain true in Scenario B, so:

```text
BL-B01 is reused
```

This is the proof of:

> **proposal revision ≠ baseline revision**

## Assessment reuse

The historical Assessments from `IAX-B01` are classified relative to `IAX-B02`:

```text
ASM-B01 → Invalidated
ASM-B02 → Retained
ASM-B03 → Revalidation Required
ASM-B04 → Retained
```

A reuse classification is not a permanent property of the Assessment. It is target-execution-relative.

Only `Retained` can satisfy a compatible later obligation:

```text
AO-B23 → ASM-B02
AO-B24 → ASM-B04
```

while:

```text
AO-B21 → open
AO-B22 → open
```

## Immutability proof

The retained fulfilment transaction updates only the **new target obligation**. It does not modify the historical Assessment, its Impact Links, Requirement Conclusions or Evidence Uses.

For repository inspection, use:

- `src/plm_ref/application/assessment_reuse.py`
- `tests/test_g09_assessment_reuse.py`
- the Scenario B actual evidence

The acceptance evidence requires the historical semantic state of retained `ASM-B02` and `ASM-B04` to remain unchanged before and after later fulfilment.

Final stop point:

```text
Gate B = Incomplete
Authorisation Eligibility = Not Evaluated
Decision Record = none
CHG-B01 = In Assessment
```

Do not continue the business scenario beyond this frozen stop point.

---

# 17:00–20:30 — Gate B, Eligibility, authority and non-terminal escalation

**Show:** Slide 7 and [`evidence-extracts/04_scenario_c_authority_escalation.md`](evidence-extracts/04_scenario_c_authority_escalation.md).

The architecture deliberately answers four different questions.

## 1. Gate B — is the package complete?

Gate B checks package completeness, including:

- final Impact-analysis Execution completed;
- routing completed;
- exact Proposed Change Scope known;
- every mandatory Assessment Obligation satisfied;
- mandatory candidate coverage complete;
- blocking pre-Decision Open Items resolved;
- required Evidence criteria fulfilled;
- Required Authority Level known.

It does not treat a `Not Satisfied` conclusion as missing data. The package can be complete while the conclusion is substantively negative.

## 2. Authorisation Eligibility — may the package be authorised?

Eligibility separately blocks, for mandatory support:

- `Objection`;
- `Escalation Recommended`;
- `Not Satisfied`;
- `Not Demonstrated`.

This is why completeness and substantive permission are separate calculations.

## 3. Authority sufficiency — does this authority have the mandate?

Frozen ordering:

```text
Standard < Elevated
```

Scenario C has:

```text
Gate B = Complete
Eligibility = Permitted
required = Elevated
current = Standard
```

Therefore:

```text
authority_sufficient = false
HIST-C01 = Escalated
Decision Record = none
CHG-C01 = Decision Ready
```

The package remains complete even though the current authority cannot dispose it.

This is the proof of:

> **decision-package completeness ≠ authority to decide**

## 4. Terminal disposition — what does the authority decide?

The deterministic rules never choose `Authorised`, `Authorised with Conditions` or `Rejected`. A terminal Decision requires an explicit authority disposition command.

---

# 20:30–23:30 — Scenario A Decision persistence and Handover

**Show:** [`evidence-extracts/01_scenario_a_terminal_basis.md`](evidence-extracts/01_scenario_a_terminal_basis.md).

Scenario A proves the positive terminal path.

Before the explicit authority action:

```text
Gate B Complete
Eligibility Permitted
Standard = Standard
decision_permitted = true
Decision Record = none
```

Only the explicit authority disposition causes the atomic Decision transaction.

## Decision persistence checks

The Decision Service validates at least:

- same-case baseline/overlay/execution lineage;
- Gate B Complete;
- Eligibility Permitted;
- authority sufficient;
- non-empty Decision Scope;
- every scope item present in the final Overlay Revision;
- every mandatory Assessment Obligation satisfied;
- every satisfying Assessment included as Decision Support Assessment;
- supporting Assessments Complete, locked and valid for the final execution;
- Decision Condition cardinality consistent with the selected outcome.

Scenario A then persists:

```text
DEC-A01
Decision Scope = CI-A01:r1
Decision Support = ASM-A01..ASM-A04
Decision Conditions = none
outcome = Authorised for Downstream Processing
```

The Case becomes `Closed by Decision` because no selected Active proposal revision remains undisposed.

The Handover View is **derived**, not persisted as an independent lifecycle object.

If asked why this matters, connect it back to historical integrity: the Decision Record stores explicit lineage to the exact evaluated basis rather than merely recording a final status on the Change Case.

---

# 23:30–27:00 — Verification architecture and negative controls

**Show:** Slide 9 and [`evidence-extracts/05_verification_evidence.md`](evidence-extracts/05_verification_evidence.md).

## Controlled implementation sequence

The frozen implementation plan decomposes delivery into:

```text
INC-00 … INC-14
```

with sequential acceptance gates:

```text
G00 … G14
```

A failed release-critical gate is a stop condition; implementation does not bypass it and continue.

## Integrity catalogue

The release-critical catalogue includes `IT-01..IT-16`, covering among other things:

- Gate A baseline independence;
- overlay eligibility requiring baseline-relative state;
- Product Version immutability at application and SQLite layers;
- locked Assessment child immutability;
- retained fulfilment without historical mutation;
- non-retained reuse rejection;
- routing atomicity;
- `RRR-05` inability to auto-create Change Items;
- Gate B vs Eligibility separation;
- Scenario C non-terminal authority insufficiency;
- explicit Decision command requirement;
- complete Decision support coverage;
- historical reconstruction without live source dependence;
- cross-case injection rejection.

## IT-16 active injection evidence

The final integrity evidence actively attempts and rejects six release-critical cross-case lineage families:

```text
execution baseline/overlay
candidate provenance
Assessment fulfilment
Assessment reuse
Decision support
Decision Scope
```

This demonstrates active negative testing for those families. Do not overstate it as exhaustive proof of every possible cross-case association allowed by the Logical Information Model.

## Oracle verification

Final verification compares each independently executed scenario against its frozen expected oracle and records six PASS groups:

```text
Scenario A oracle
Scenario B oracle
Scenario C oracle
Cross-scenario assertions
Integrity suite
Historical reconstruction
```

Recorded release-candidate evidence:

```text
G00–G14: 15/15 PASS
pytest: 185 passed
plm-ref verify all: exit 0
verification groups: 6/6 PASS
repeated evidence generation: byte-identical
IT-16 families: 6/6 attempted, rejected and PASS
```

## Reproducibility boundary

Repository governance later adds a locked Python 3.12 environment, CI migration/test/verification flow, frozen-architecture hashes and committed-evidence hashes. These are release controls around the already verified executable baseline; they do not move or redefine the architecture.

---

# 27:00–29:00 — Bounded findings and claim discipline

**Show:** Slide 10 and, if needed, the Architecture Traceability and Assurance Pack.

This section matters in a technical review because a credible architecture case states exactly what was **not** proved.

## Important bounded findings

### General impact discovery

The implementation uses a bounded fixture adapter behind `ImpactAnalysisPort`. It does not prove arbitrary enterprise PLM graph discovery.

### BR-15 Process Authority override

The architecture recognises documented Process Authority overrides for Assessment planning, but the implementation has no override command, persisted override record or acceptance test. The executable reference case demonstrates the deterministic `RRR-01..04` route only.

### BR-25 withdrawal

Withdrawal is represented by allowed schema/process-history semantics, but no executable withdrawal use case is exercised in Scenarios A–C.

### LIM-INV-12 provenance multiplicity

The logical model permits multiple provenance records/paths per Impact Candidate. The frozen scenario oracles exercise one provenance record per candidate.

### LIM-INV-24 case-local lineage

The release includes active bounded cross-case guards and the six IT-16 injection families. The Assurance Pack does not claim exhaustive proof of every conceivable association named by the invariant.

## External/public non-claims

Do not claim:

- company-specific PLM process fidelity;
- enterprise PLM completeness or production deployment readiness;
- enterprise source-authority/freshness governance;
- general arbitrary-graph impact discovery;
- automated engineering judgement or terminal approval;
- enterprise approval hierarchy beyond the synthetic `Standard < Elevated` model.

The synthetic boundary is deliberate and part of the architecture quality, not something to hide during review.

---

# 29:00–30:00 — Close on the method

**Return to:** Slide 4 or Slide 1.

**Say:**

> The useful result is the conformance chain. A bounded engineering problem was translated into explicit business, information and decision semantics; those semantics were frozen before implementation; the software was restricted to those semantics; and the result was tested against independent oracles, negative integrity controls and reconstructable evidence. The prototype is therefore evidence that this particular architecture is executable—not a claim that a production PLM platform has been built.

---

# Recommended repository tabs for the reviewer

Pre-open these in this order:

1. `docs/08-executive-visual-package/Product_Change_Impact_Decision_Readiness_Presentation_v0.1.pdf`
2. `docs/07-traceability-assurance/Architecture_Traceability_and_Assurance_Pack_v0.1.md`
3. `evidence-extracts/01_scenario_a_terminal_basis.md`
4. `evidence-extracts/02_scenario_b_scope_amendment.md`
5. `evidence-extracts/03_scenario_b_reuse_and_readiness.md`
6. `evidence-extracts/04_scenario_c_authority_escalation.md`
7. `evidence-extracts/05_verification_evidence.md`
8. `src/plm_ref/application/assessment_reuse.py`
9. `src/plm_ref/application/readiness.py`
10. `src/plm_ref/application/authority.py`
11. `src/plm_ref/application/decision.py`
12. `src/plm_ref/application/history_and_views.py`
13. `tests/test_g09_assessment_reuse.py`
14. `tests/test_g10_readiness_authority.py`
15. `tests/test_g11_terminal_decision.py`
16. `tests/test_g12_history_and_handover.py`
17. `tests/test_g14_oracle_verification.py`
18. `evidence/decision_DEC-A01_basis.json`
19. `evidence/integrity_results.json`
20. `VERIFIED_BASELINE.md`

Use repository files only when the reviewer asks how a claim is enforced. Do not mechanically open every tab during the 30-minute path.

---

# Optional live execution

If the reviewer specifically asks to see the executable proof, use the already defined five-minute demo commands with disposable `/tmp` databases and evidence directories.

Do not regenerate or modify committed `evidence/` during the technical review.

The preferred live proof is one of:

```bash
plm-ref scenario run A
```

or a disposable-path `verify_all()` invocation.

Immediately return from the command to the architectural statement it proves.

---

# Question-routing guide

| Reviewer question | Best jump point |
|---|---|
| “Why not just use revisions?” | Slide 2 / baseline-overlay section |
| “Where is the actual historical state?” | `BL-*` Baseline Members / Decision basis |
| “Why is the overlay separate?” | Slide 5 / Scenario B |
| “Is this a graph impact engine?” | ImpactAnalysisPort boundary |
| “How do you know an Assessment is required?” | `RRR-01..04` + Assessment Obligations |
| “What changes after scope amendment?” | Scenario B second cycle |
| “Can an old Assessment be reused?” | execution-relative reuse + G09 |
| “Can conditions bypass a failed Requirement?” | Eligibility section; answer no |
| “Why is Scenario C not rejected?” | authority insufficiency is routing, not terminal disposition |
| “Who actually approves?” | explicit authority disposition command |
| “How do you reconstruct a Decision later?” | G12 / `decision_DEC-A01_basis.json` |
| “How do you know the code matches the specification?” | G14 oracle + integrity + evidence |
| “What is not implemented?” | bounded findings / Slide 10 |

---

# Failure and challenge handling

If a reviewer exposes a real mismatch between this walkthrough and the frozen architecture or committed evidence:

1. stop using the disputed walkthrough statement;
2. treat the frozen artefact/evidence as authoritative;
3. classify whether the issue is a documentation error or a genuine semantic contradiction;
4. do not change frozen semantics to preserve the presentation;
5. only reopen the lowest necessary authoritative artefact if deterministic Scenarios A–C are genuinely contradictory.

Ordinary implementation or presentation convenience is never sufficient reason to reinterpret frozen business meaning.
