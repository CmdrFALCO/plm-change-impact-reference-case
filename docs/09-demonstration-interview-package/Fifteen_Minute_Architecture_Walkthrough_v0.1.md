# Product Change Impact Assessment & Decision Readiness

## Fifteen-Minute Architecture / Interview Walkthrough v0.1

**Purpose:** Explain the reference case at architecture depth using the canonical Session 5 deck plus the accepted Session 6 evidence extracts.  
**Target duration:** 15 minutes  
**Primary visual source:** Session 5 canonical ten-slide presentation  
**Evidence source:** committed deterministic evidence and the static extracts in this package

---

## Walkthrough principle

This is not a second deck and not a longer software demo.

Use the existing ten-slide canonical presentation in order. Insert the Session 6 evidence extracts only where they prove a statement already made by the canonical material.

The standard 15-minute path is **static-first**. Do not run the CLI unless the interviewer explicitly asks to see execution. The separate five-minute deterministic demo already provides the live path; using static committed evidence here keeps the discussion on architecture and makes the interview path robust.

The narrative is:

```text
problem
→ boundary
→ architecture-to-evidence chain
→ state separation
→ information and lineage
→ decision-readiness logic
→ Scenario A/B/C proof
→ controlled implementation and verification
→ claims and limitations
```

---

# Timing map

| Time | Canonical material | Main purpose |
|---|---|---|
| 0:00–0:45 | Slide 1 | Thesis and positioning |
| 0:45–2:00 | Slide 2 | Why revision succession is insufficient |
| 2:00–2:50 | Slide 3 | Scope and public-safe boundary |
| 2:50–4:00 | Slide 4 | Architecture-to-evidence chain |
| 4:00–5:40 | Slide 5 | Assessment Baseline + Overlay Revision separation |
| 5:40–6:55 | Slide 6 | Information and lineage architecture |
| 6:55–8:30 | Slide 7 | Gate B vs Eligibility vs Authority vs Decision |
| 8:30–11:40 | Slide 8 + evidence extracts | Scenario A/B/C architectural proof |
| 11:40–13:15 | Slide 9 + verification extract | Controlled implementation and conformance evidence |
| 13:15–14:30 | Slide 10 | Supported claims and limitations |
| 14:30–15:00 | Slide 1 or 4 | Close on reusable method |

The timings sum to 15 minutes. If discussion becomes interactive, preserve Slides 5, 7, 8 and 9 before compressing other sections.

---

# 0:00–0:45 — Slide 1: state the thesis

**Show:** Slide 1 — *Product Change Impact Assessment & Decision Readiness*.

**Say:**

> This case starts from a bounded product-change problem and asks a specific question: what information and decision semantics are necessary before a proposed change is genuinely decision-ready? The central thesis is that current state, proposal, discovered impacts, domain conclusions, evidence, decision scope and authority have to remain separate, while still being linked deterministically and historically reconstructably. The prototype is not the main deliverable; it is the test of whether that architecture is precise enough to execute.

**Do not lead with:** Python, FastAPI, SQLite, test count or repository structure.

**If asked immediately “what did you build?”:**

> A synthetic PLM Business Architecture reference case with a deterministic executable proof boundary: business and information semantics first, then rules, scenarios, implementation controls, tests and evidence.

---

# 0:45–2:00 — Slide 2: explain the problem

**Show:** Slide 2 — *Why Revision A → Revision B is insufficient*.

**Say:**

> Revision succession tells me that one state follows another. It does not tell me the complete decision basis. I still need to know which authoritative current state was evaluated, in which configuration and usage context, what the Proposed Change Scope actually contained, what impacts were discovered and why, which Assessments and Evidence Uses were required, whether blocking Open Items remained, what exact Change Item revisions the Decision Scope disposes, and whether the current authority can make that decision.
>
> The design problem is therefore not just version control. It is preserving the distinctions required to explain and reconstruct a decision.

**Key transition:**

> Once that is the problem, the architecture must explicitly represent evaluated state, proposal state, impact, assessment and decision scope rather than collapsing them into one lifecycle status.

---

# 2:00–2:50 — Slide 3: establish the boundary

**Show:** Slide 3 — *Bounded capability and public-safe scope*.

**Say:**

> The case is deliberately bounded. It starts when a change need is documented and at least one Change Item can be identified. It ends at terminal authority disposition or an auditable non-terminal route at the frozen scenario stop point. Product-data authoring, engineering release, manufacturing implementation, stock transition and service deployment are outside scope.
>
> The represented data is a synthetic integration projection, not an enterprise system of record, and the case makes no claim of company-specific process, data-model or authority fidelity.

**Purpose of this slide:** make later implementation simplicity a deliberate scope choice rather than an enterprise-readiness claim.

---

# 2:50–4:00 — Slide 4: show the architecture-to-evidence chain

**Show:** canonical Diagram 1 on Slide 4 — *From engineering problem to executable evidence*.

**Say:**

> The authority direction matters here. Business Architecture defines the capability and invariants. The Logical Information Model makes the distinctions implementable. Scenario Data fixes exact input and expected state. RRR-v0.1 makes readiness, routing and authority calculations deterministic. Solution Architecture and the Implementation Plan translate that meaning into software structure and controlled increments. Code, tests and evidence are downstream proof, not upstream sources of business meaning.
>
> That is why the prototype is useful: if the frozen meaning cannot be executed without shortcuts, the architecture is incomplete. If it can be executed and independently compared with the frozen oracle, the implementation provides conformance evidence.

**Interview hook:** if the conversation is about delivery/governance, note that implementation was bounded through `INC-00–INC-14`, sequential `G00–G14` acceptance gates and release-critical integrity tests, but defer the detail to Slide 9.

---

# 4:00–5:40 — Slide 5: explain Baseline + Overlay

**Show:** canonical Diagram 2 — *Current state, baseline and proposal are not equivalent*.

**Say:**

> This is the most important information distinction in the case. Live source current state is not the same thing as the historical state used for an assessment. The Assessment Baseline therefore captures immutable Baseline Member snapshots. A Change Item Revision describes an intended modification. The Overlay Revision materialises the hypothetical proposed state without changing the baseline. An Impact-analysis Execution identifies the exact baseline, overlay and rule-set version it evaluated.
>
> If the proposal changes, the architecture requires a new Overlay Revision and a new Impact-analysis Execution. That does not automatically mean the authoritative current state changed, so it does not automatically require a new Assessment Baseline.

**Use Scenario B as a preview, but do not open the evidence yet:**

> Scenario B deliberately tests this distinction: the proposal changes, `BL-B01` remains valid and is reused, while `OV-B02` and `IAX-B02` are new.

**Key propositions:**

```text
historical evaluated state ≠ live mutable source state
proposal revision ≠ baseline revision
```

---

# 5:40–6:55 — Slide 6: information and lineage architecture

**Show:** Slide 6 — four information bands.

**Say:**

> The model is relational and lineage-heavy because the architecture has to explain how a decision was reached. Product Element, Product Version and Product Structure Occurrence keep identity, state and usage separate. Change Case and Change Item Identity/Revision keep the process container separate from proposed technical content. Assessment Baseline and Overlay Revision preserve evaluated current and proposed state. Impact Candidate Provenance explains why something became a candidate. Assessment Obligations make required evaluation explicit before an Assessment exists.
>
> Evidence Record and Assessment Evidence Use are also separated from Requirement Conclusion: evidence informs an Assessment; only the Assessment concludes on the Requirement. Finally, Decision Scope Items and Decision Support Assessments preserve the exact scope and support basis of a terminal Decision.

**Point to the lineage rule:**

> All release-critical lineage remains case-local. Cross-case joins are invalid rather than silently tolerated.

**If asked about historical reconstruction:**

> `DEC-A01` can be reconstructed from stored Baseline Member snapshots, locked Assessments and Evidence snapshots without reading mutable live source state for historical meaning.

---

# 6:55–8:30 — Slide 7: separate the four decision questions

**Show:** canonical Diagram 3 — *Decision readiness is not one gate*.

**Say:**

> The architecture separates four questions that are often collapsed. First: is the Decision Package complete? That is Gate B. Second: do the substantive Assessment dispositions and Requirement Conclusions permit authorisation? That is Authorisation Eligibility. Third: is the required authority within the current authority level? That is authority sufficiency. Fourth: what is the terminal authority disposition? The deterministic rules do not choose that outcome.
>
> If authority is insufficient, the result is an `Escalated` Process-history Entry and no Decision Record. If authority is sufficient and eligibility is Permitted, the system exposes a permitted decision path, but a Decision Record still requires an explicit terminal authority disposition.

**Compact contrast:**

```text
Complete package
≠ eligible to authorise
≠ authority to decide
≠ terminal Decision
```

**If asked whether this automates approval:**

> No. `RRR-v0.1` calculates readiness, routing, eligibility and authority sufficiency. It does not autonomously select a terminal engineering outcome.

---

# 8:30–11:40 — Slide 8: Scenarios A–C as architectural proofs

**Show:** Slide 8 first, then open the evidence extracts only as needed.

## 8:30–9:25 — Scenario A: authorised change

**Open:** [`evidence-extracts/01_scenario_a_terminal_basis.md`](evidence-extracts/01_scenario_a_terminal_basis.md)

**Say:**

> Scenario A is the positive terminal path. Gate B is Complete, Authorisation Eligibility is Permitted, required and current authority are both Standard, and the explicit authority disposition creates `DEC-A01`. The Decision Scope contains `CI-A01:r1`, the support set contains the four required Assessments, there are zero Decision Conditions, the case becomes Closed by Decision and the Handover View is derived.

**What it proves:** exact terminal Decision lineage and explicit authority action.

## 9:25–10:55 — Scenario B: controlled scope amendment and reuse

**Open:**

1. [`evidence-extracts/02_scenario_b_scope_amendment.md`](evidence-extracts/02_scenario_b_scope_amendment.md)
2. [`evidence-extracts/03_scenario_b_reuse_and_readiness.md`](evidence-extracts/03_scenario_b_reuse_and_readiness.md)

**Say:**

> Scenario B is the strongest test of scope semantics. The first execution finds an applicability mismatch. Product Engineering records `REQ-004 = Not Satisfied`, so `RRR-05` produces `HIST-B01 = Scope Revision Required`. The discovered impact does not silently become proposed or authorised scope, and the rule does not auto-create the required Change Item. `CI-B02:r1` is added explicitly.
>
> Because the proposal changes, the system creates `OV-B02` and `IAX-B02`; because the authoritative current-state basis remains valid, `BL-B01` is reused. The four historical Assessments are classified relative to the new execution as Invalidated, Retained, Revalidation Required and Retained. The retained Validation and Purchasing/Cost Assessments can fulfil compatible later obligations without historical mutation, while `AO-B21` and `AO-B22` remain open. Gate B is therefore Incomplete and there is no Decision.

**What it proves:**

> **discovered impact ≠ authorised scope**

> **proposal revision ≠ baseline revision**

> **reuse is execution-relative, not blanket reuse**

## 10:55–11:40 — Scenario C: authority escalation

**Open:** [`evidence-extracts/04_scenario_c_authority_escalation.md`](evidence-extracts/04_scenario_c_authority_escalation.md)

**Say:**

> Scenario C deliberately completes the package and passes substantive eligibility, then fails only the authority comparison. Required authority is Elevated and current authority is Standard. The result is `HIST-C01 = Escalated`, there is no Decision Record, and the case remains Decision Ready.

**What it proves:**

> **decision-package completeness ≠ authority to decide**

---

# 11:40–13:15 — Slide 9: controlled delivery and verification

**Show:** Slide 9, then [`evidence-extracts/05_verification_evidence.md`](evidence-extracts/05_verification_evidence.md).

**Say:**

> The executable layer was developed as a controlled translation of the frozen architecture. The plan defined `INC-00–INC-14` as bounded work packages and `G00–G14` as sequential acceptance gates, with explicit stop conditions if a semantic contradiction appeared. Release-critical integrity tests cover immutability, retained Assessment reuse, routing atomicity, explicit Decision commands, historical reconstruction and cross-case injection rejection.
>
> The verified executable boundary records 15 out of 15 acceptance gates passed, 185 pytest tests passed, six out of six final verification groups passed, byte-identical repeated evidence generation, and six out of six IT-16 cross-case injection families actively attempted and rejected.

**Point out the verification groups:**

```text
Scenario A oracle
Scenario B oracle
Scenario C oracle
Cross-scenario assertions
Integrity suite
Historical reconstruction
```

**Important interpretation:**

> These figures do not prove enterprise PLM completeness. They prove deterministic conformance of the bounded implementation to the frozen Scenarios A–C and the implemented integrity controls.

**If asked about the implementation stack:**

> Python modular monolith, FastAPI, Pydantic, SQLAlchemy, SQLite, Alembic, pytest and Typer. Those are implementation choices selected for inspectability and deterministic local execution, not the architectural thesis.

---

# 13:15–14:30 — Slide 10: claims and limitations

**Show:** Slide 10 — *Supported claims, limitations and applicability*.

**Say:**

> The supported claim is deliberately narrow: the case demonstrates deterministic execution of the frozen Scenarios A–C with explicit business, information and decision semantics, case-local lineage, immutable historical reconstruction, separation of readiness, eligibility, authority and Decision, and conformance evidence against independent oracles and integrity controls.
>
> It does not claim enterprise PLM completeness, production readiness, company-specific process fidelity, arbitrary-graph impact discovery or automated engineering judgement. Those are outside the architecture and should not be inferred from the prototype.

**If asked “what is reusable beyond this scenario?”:**

> The reusable part is the method: bound the engineering problem, make the semantic distinctions explicit, freeze the business meaning, implement only what the architecture requires, and prove conformance through deterministic scenarios and evidence.

---

# 14:30–15:00 — Close

**Return to:** Slide 1 or Slide 4.

**Say:**

> The case therefore connects business architecture to executable assurance without making software the source of business meaning. The prototype matters because it demonstrates that the distinctions survive implementation: current and proposed state stay separate, discovered impact does not become scope automatically, package completeness stays separate from authority, and a historical Decision remains reconstructable from its stored basis.

Stop here. Do not append a software tour unless the interviewer asks for it.

---

# Interview control and cut points

The walkthrough is designed for interruption. If time is reduced mid-conversation:

- **10 minutes available:** compress Slides 2–4; preserve Slides 5, 7, 8 and 9.
- **5 minutes available:** switch to [`Five_Minute_Deterministic_Demo_v0.1.md`](Five_Minute_Deterministic_Demo_v0.1.md) or give its static version without the live commands.
- **Architecture question:** stay on Slides 5–7 and use Scenario B as proof.
- **Decision/governance question:** use Slide 7 plus Scenario C.
- **Delivery/verification question:** move directly to Slide 9 and the verification extract.
- **Implementation-detail question:** answer only the narrow question and offer the 30-minute technical path; do not let the stack replace the architectural narrative.

---

# Standard evidence navigation

Keep these tabs/items ready in this order:

1. canonical presentation;
2. Scenario A terminal-basis extract;
3. Scenario B scope-amendment extract;
4. Scenario B reuse/readiness extract;
5. Scenario C authority-escalation extract;
6. verification-evidence extract.

No local database or runtime setup is required for the standard 15-minute path.

If live execution is explicitly requested, use the separate five-minute deterministic demo procedure with disposable `/tmp` database and evidence paths.

---

# Claim discipline during Q&A

Do not extend the presentation claims into:

- enterprise-ready impact discovery;
- production or company-specific PLM workflow fidelity;
- generic approval hierarchy;
- automated engineering approval;
- product-data authoring or release implementation;
- plant, stock, service or production-effectivity semantics;
- a claim that every possible lineage association has been exhaustively adversarially tested.

Where the implementation is bounded, say so. The value of the case is that the boundary is explicit rather than hidden.
