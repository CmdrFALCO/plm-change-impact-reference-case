# Product Change Impact Assessment & Decision Readiness

## Canonical Executive and Visual Package Specification v0.1

**Document type:** Documentation-only narrative, diagram and presentation specification  
**Status:** Accepted pre-production specification  
**Release target:** `v0.1.0`  
**Authority:** Derived from the frozen architecture, implementation plan and verified evidence; does not redefine them

---

# 1. Purpose and authority

This document fixes the composition of one public-safe, role-neutral executive and visual package for the reference case.

The package must remain subordinate to the frozen authority chain:

```text
Business Architecture v0.3.1
→ Logical Information Model v0.3.2
→ Scenario Data Definition v0.1
→ Readiness and Routing Rules v0.1 / RRR-v0.1
→ Solution Architecture v0.1
→ Prototype Implementation Plan v0.1
→ code, tests and evidence
```

The package is a communication layer only. It must not add PLM scope, alter Scenario A–C outcomes, simplify away a frozen distinction or become a competing source of truth.

---

# 2. Canonical thesis

> **A product change becomes decision-ready only when current state, proposal, discovered impacts, domain conclusions, evidence, decision scope and authority are kept separate—and linked by deterministic, case-local and historically reconstructable rules.**

Supporting delivery proposition:

> **The executable prototype is the proof boundary for the architecture: controlled implementation increments, acceptance and integrity gates, independent scenario oracles and deterministic evidence test whether the frozen meaning can execute without semantic shortcuts.**

The first proposition leads the narrative. The second explains how the claim is verified.

---

# 3. Canonical package and derivative rule

Create one canonical package with one meaning. Later derivative material may:

- omit slides;
- reorder complete content modules;
- shorten speaker notes;
- emphasise selected already-supported evidence;
- reuse the three canonical diagrams without changing their labels or arrow meaning.

Later derivatives must not:

- rewrite the architectural thesis;
- change the frozen authority hierarchy;
- change a scenario outcome;
- imply broader responsibility, authority or company-process fidelity;
- convert implementation technology into the primary story;
- claim that deterministic readiness logic automates engineering judgement.

Reuse comes from modular structure, not from parallel versions of the canonical package.

---

# 4. Reusable content modules

| Module | Slides | Purpose |
|---|---:|---|
| **A — Problem and boundary** | 1–3 | Establish the engineering product-change problem, capability boundary and public-safe positioning. |
| **B — Business, information and decision architecture** | 4–7 | Explain the authority chain, baseline/overlay model, information lineage and decision-readiness distinctions. |
| **C — Scenario proof** | 8 | Show how Scenarios A–C exercise different architectural propositions. |
| **D — Controlled delivery and assurance** | 9 | Show how the bounded problem and frozen architecture were translated through increments, gates, verification and evidence. |
| **E — Claims and limitations** | 10 | State what the project establishes and where the claim boundary stops. |

Each module must remain understandable when copied with its required context. Slides 4, 5 and 7 contain the three canonical diagrams and therefore preserve their exact captions and terminology in every derivative.

---

# 5. Three canonical diagrams

Exactly three diagrams are designated as canonical:

1. **Architecture-to-evidence chain**  
   Source: [`diagrams/01_architecture_to_evidence_chain.md`](diagrams/01_architecture_to_evidence_chain.md)
2. **Current state, Assessment Baseline and proposed-state separation**  
   Source: [`diagrams/02_baseline_overlay_state_separation.md`](diagrams/02_baseline_overlay_state_separation.md)
3. **Gate B, Authorisation Eligibility, authority sufficiency and Decision**  
   Source: [`diagrams/03_readiness_eligibility_authority_decision.md`](diagrams/03_readiness_eligibility_authority_decision.md)

Secondary slide composition may use tables, scenario cards, evidence excerpts or reused components from these diagrams. It must not introduce a fourth competing architecture diagram.

---

# 6. Ten-slide canonical storyboard

## Slide 1 — Product Change Impact Assessment & Decision Readiness

**Headline:** Product change is a decision-basis problem, not only a revision problem.

**Required content:**

- project title;
- canonical thesis;
- subtitle: public-safe PLM Business Architecture reference case;
- one compact statement that the prototype proves the architecture.

**Primary module:** A — Problem and boundary.

## Slide 2 — Why `Revision A → Revision B` is insufficient

**Headline:** Revision succession does not identify the evaluated or authorised change basis.

**Required content:**

- exact authoritative state evaluated;
- configuration and usage context;
- Proposed Change Scope;
- discovered impacts and provenance;
- required Assessments and Evidence Uses;
- blocking Open Items;
- exact Decision Scope and authority.

**Visual treatment:** A simple `Revision A → Revision B` line contrasted with the missing decision-basis dimensions. This is an explanatory contrast, not a fourth canonical architecture diagram.

**Primary module:** A — Problem and boundary.

## Slide 3 — Bounded capability and public-safe scope

**Headline:** The case begins with an identifiable change need and stops before downstream implementation.

**Required content:**

- capability start: documented change need and at least one identifiable Change Item;
- capability end: terminal authority disposition or auditable non-terminal routing at the frozen scenario stop point;
- explicitly outside scope: product-data authoring, engineering release, manufacturing implementation, stock transition and service deployment;
- synthetic integration projection, not an enterprise system of record;
- no company-specific process, data model, workflow or authority claim.

**Primary module:** A — Problem and boundary.

## Slide 4 — From engineering problem to executable evidence

**Headline:** Business meaning governs implementation; evidence closes the conformance chain.

**Required visual:** Canonical Diagram 1.

**Required message:**

- frozen architecture precedes implementation;
- the Implementation Plan defines controlled increments and acceptance gates;
- independent oracle comparison and integrity tests verify execution;
- evidence is technical proof, not a PLM business object.

**Primary modules:** B — Architecture and D — Controlled delivery.

## Slide 5 — Current state, baseline and proposal are not equivalent

**Headline:** Historical evaluation requires an immutable current-state basis and a separate proposed-state overlay.

**Required visual:** Canonical Diagram 2.

**Required message:**

- live/source current state is not the historical Assessment Baseline;
- Baseline Members preserve the captured current-state meaning;
- Change Item Revisions are explicit and versioned;
- Overlay-local Objects are hypothetical and non-authoritative;
- each Impact-analysis Execution identifies the exact baseline, overlay and rule-set version;
- later source changes cannot redefine the historical execution basis.

**Primary module:** B — Business, information and decision architecture.

## Slide 6 — Information and lineage architecture

**Headline:** Decision readiness depends on explicit objects, associations and case-local lineage.

**Required content, presented as four information bands rather than a fourth canonical diagram:**

1. **Product information:** Product Element, Product Version, Product Structure Occurrence, Configuration Context, Applicability and Effectivity.
2. **Change and evaluated state:** Change Case, Change Item Identity and Revision, Assessment Baseline, Overlay Revision, Impact-analysis Execution.
3. **Impact and assessment:** Impact Candidate Provenance, Assessment Obligation, Assessment, Requirement Conclusion, Assessment Evidence Use and Assessment Reuse Classification.
4. **Decision and audit:** Open Item, Process-history Entry, Decision Record, Decision Scope Item, Decision Support Assessment, Decision Condition and Handover View.

**Required message:** All release-critical lineage remains within one Change Case; Evidence informs, while Assessment concludes.

**Primary module:** B — Business, information and decision architecture.

## Slide 7 — Decision readiness is not one gate

**Headline:** Package completeness, substantive eligibility, authority sufficiency and terminal disposition answer different questions.

**Required visual:** Canonical Diagram 3.

**Required message:**

- Gate B means Decision Package Complete;
- Authorisation Eligibility checks substantive blockers separately;
- authority comparison occurs only with an explicit Required and Current Authority Level;
- insufficient authority creates an Escalated Process-history Entry, not a Decision Record;
- sufficient authority exposes a permitted decision path but does not choose the outcome;
- only an explicit terminal authority disposition creates a Decision Record.

**Primary module:** B — Business, information and decision architecture.

## Slide 8 — Scenarios A–C: three architectural proofs

**Headline:** The scenarios test authorisation, controlled scope revision and non-terminal escalation.

**Required scenario cards:**

### A — Authorised change

```text
Gate B Complete
→ Eligibility Permitted
→ Standard = Standard
→ explicit authority disposition
→ DEC-A01
→ Closed by Decision
→ Handover View
```

### B — Scope amendment and selective reuse

```text
HIST-B01 Scope Revision Required
→ CI-B02:r1 added explicitly
→ BL-B01 reused
→ OV-B02 + IAX-B02
→ Invalidated / Retained / Revalidation Required / Retained
→ AO-B21 and AO-B22 open
→ Gate B Incomplete
→ no Decision
```

### C — Authority escalation

```text
Gate B Complete
→ Eligibility Permitted
→ Elevated > Standard
→ HIST-C01 Escalated
→ no Decision
→ Case remains Decision Ready
```

**Required propositions:**

- discovered impact ≠ authorised scope;
- proposal revision ≠ baseline revision;
- decision-package completeness ≠ authority to decide.

**Primary module:** C — Scenario proof.

## Slide 9 — Controlled delivery and verification

**Headline:** The architecture was implemented incrementally and accepted through explicit proof gates.

**Required content:**

- `INC-00–INC-14` as bounded implementation work packages;
- `G00–G14` as sequential acceptance gates;
- `IT-01–IT-16` as release-critical negative and integrity controls;
- separation of scenario input, impact-result fixture and expected oracle;
- complete actual-state comparison against independent expected oracles;
- historical reconstruction and cross-case injection rejection;
- locked dependency environment, reproducibility workflow and evidence manifests.

**Required evidence:**

```text
G00–G14: 15/15 PASS
Full regression: 185 passed
Final verification groups: 6/6 PASS
Repeated evidence generation: byte-identical
IT-16 families: 6/6 attempted, rejected and PASS
```

**Visual treatment:** Reuse the delivery-and-assurance components of Canonical Diagram 1 plus a compact evidence panel. Do not create a fourth canonical diagram.

**Primary module:** D — Controlled delivery and assurance.

## Slide 10 — Supported claims, limitations and applicability

**Headline:** The project proves a bounded architecture claim—not enterprise PLM completeness.

**Supported:**

- deterministic execution of frozen Scenarios A–C;
- explicit business, information and decision semantics;
- case-local lineage and immutable historical reconstruction;
- controlled separation of readiness, eligibility, authority and Decision;
- implementation conformance tested through independent oracles, integrity controls and committed evidence.

**Not claimed:**

- company-specific process fidelity;
- enterprise PLM completeness or production readiness;
- general arbitrary-graph impact discovery;
- automated engineering judgement or terminal approval;
- enterprise programme, budget, capacity or organisational authority.

**Closing statement:** The reusable value is the method: bound the problem, freeze the meaning, implement only what the architecture requires and prove conformance through deterministic evidence.

**Primary module:** E — Claims and limitations.

---

# 7. Editable-source and slide-construction rules

The canonical presentation must be built as one editable 16:9 PowerPoint source.

Required construction rules:

- use native text, lines, connectors, tables and grouped shapes for the presentation source;
- retain the Markdown/Mermaid files as transparent semantic diagram sources;
- export SVG and PNG only as derived viewing formats;
- keep the three canonical diagrams on dedicated slides before reusing their components elsewhere;
- use stable grouped components so a complete module can be copied without redrawing arrows;
- keep evidence numbers, scenario outcomes and claim limitations in editable text;
- place explanatory depth in speaker notes rather than reducing frozen terminology to ambiguous labels;
- avoid decorative process icons that imply additional roles, systems or workflow stages;
- do not flatten the canonical PowerPoint into image-only slides.

---

# 8. Claim discipline

The package may state that the reference-case delivery used:

- a bounded scope and explicit non-goals;
- a frozen authority hierarchy;
- controlled implementation increments;
- acceptance gates and stop conditions;
- issue and contradiction handling;
- negative and integrity testing;
- independent oracle comparison;
- deterministic evidence generation;
- dependency locking, CI verification and repository protection.

These are project facts. They do not establish personal or organisational authority for:

- formal budget ownership;
- workforce-capacity allocation;
- enterprise programme control;
- external commissioning authority;
- formal scaled-agile leadership;
- company-specific PLM process ownership or fidelity.

---

# 9. Pre-production acceptance checklist

Before polished visual production begins, confirm:

- [x] one canonical thesis is fixed;
- [x] the executive brief is role-neutral and architecture-first;
- [x] the deck has one coherent ten-slide narrative;
- [x] both the architecture dimension and controlled-delivery dimension are visible;
- [x] exactly three canonical diagrams are defined;
- [x] later reuse depends on modularity, not competing decks;
- [x] unsupported authority and company-fidelity claims are excluded;
- [ ] all three editable diagram sources are reviewed against the frozen terminology;
- [ ] the PowerPoint source and derived exports are produced;
- [ ] the rendered one-page executive brief is checked for actual page fit;
- [ ] the rendered presentation is checked slide by slide for legibility and semantic accuracy.
