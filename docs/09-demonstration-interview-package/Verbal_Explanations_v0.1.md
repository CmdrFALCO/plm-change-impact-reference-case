# Product Change Impact Assessment & Decision Readiness

## Verbal Explanations v0.1

**Purpose:** Provide role-neutral spoken versions of the same canonical architecture-first story at approximately 60 seconds and 3 minutes.  
**Authority:** Derived communication material only; subordinate to the frozen architecture, scenarios, rules and committed evidence.

---

## Usage rule

These are not separate narratives.

Both versions compress the same chain:

```text
problem
→ architecture
→ scenarios
→ controlled implementation
→ verification evidence
```

Do not add company-specific PLM claims, general impact-engine claims, automated engineering judgement or production-readiness claims when speaking from these versions.

The prototype should be described as proof that the bounded frozen architecture is executable, not as the primary deliverable.

---

# 60-second explanation

> This is a synthetic PLM Business Architecture reference case about product-change decision readiness. The starting point is that a change cannot be represented adequately as only Revision A to Revision B, because that does not tell you which current state was evaluated, what was actually proposed, what impacts were discovered, which domain conclusions and evidence support the package, what exact scope is being decided, or whether the current authority may decide it.
>
> The architecture therefore separates an immutable Assessment Baseline from a non-authoritative proposed-state Overlay Revision, traces Impact Candidates into explicit Assessment Obligations, keeps Evidence separate from engineering conclusions, and separates Gate B package completeness from Authorisation Eligibility, authority sufficiency and the terminal Decision.
>
> Three deterministic scenarios test authorisation, explicit scope amendment with selective Assessment reuse, and non-terminal authority escalation. A Python prototype then proves the architecture against frozen scenario oracles, integrity tests and historically reconstructable evidence. The prototype is the proof boundary; the architecture is the main deliverable.

**Target spoken duration:** approximately 55–70 seconds at a normal technical speaking pace.

---

# 3-minute explanation

> The reference case starts from a bounded product-change problem: how do you know that a proposed engineering change is actually decision-ready? A simple Revision A to Revision B relationship is not enough. For a defensible decision you need to preserve which current state was evaluated, the configuration and usage context, the exact proposed Change Items, the impacts discovered from that proposal, the domain Assessments and Evidence Uses, unresolved blockers, the exact Decision Scope and the authority required to dispose that scope.
>
> I therefore separated those semantics explicitly before implementing anything. The authoritative current-state basis is captured as an immutable Assessment Baseline made of historical Baseline Member snapshots. Proposed change is represented separately through immutable Change Item Revisions and an Overlay Revision. The overlay creates hypothetical Overlay-local Objects and never mutates the baseline. Every Impact-analysis Execution records the exact baseline, overlay and `RRR-v0.1` rule-set version that produced its result, so the evaluated basis can later be reconstructed.
>
> Impact discovery is also kept separate from engineering judgement and authorised scope. An Impact Candidate is only a potential consequence. Deterministic routing rules create explicit Assessment Obligations, and only an Assessment can record a Requirement Conclusion. Evidence can support that Assessment, but Evidence itself does not establish compliance. If the proposal changes because an Assessment identifies that additional scope is required, the system records a non-terminal scope route and requires an explicit Change Item amendment rather than silently changing the proposal.
>
> The three scenarios exercise the key distinctions. Scenario A reaches Gate B Complete, Authorisation Eligibility Permitted and sufficient Standard authority; only an explicit authority disposition then creates `DEC-A01`, closes the case by Decision and permits a derived Handover View. Scenario B discovers an applicability mismatch, records `HIST-B01 — Scope Revision Required`, explicitly adds `CI-B02:r1`, reuses the still-valid `BL-B01`, creates a new overlay and execution, and classifies the earlier Assessments individually as Invalidated, Retained, Revalidation Required and Retained. Two obligations remain open, so Gate B stays Incomplete and there is no Decision. Scenario C has a complete and substantively eligible package, but required authority is Elevated while current authority is Standard, so the result is an Escalated Process-history Entry with no Decision Record and the case remains Decision Ready.
>
> The implementation is deliberately bounded. It uses a fixture-backed `ImpactAnalysisPort` for the exact frozen impact results rather than claiming a general PLM graph-impact engine. The meaningful implementation work is the deterministic downstream semantics, immutability, case-local lineage, readiness logic, explicit Decision guard and historical reconstruction. Those were implemented through `INC-00` to `INC-14`, accepted through `G00` to `G14`, and challenged with release-critical negative tests including active cross-case injections.
>
> At the verified executable baseline, all 15 acceptance gates passed, 185 pytest tests passed, all six final verification groups passed, repeated evidence generation was byte-identical, and all six IT-16 cross-case injection families were attempted and rejected. So the claim is intentionally narrow: this is not an enterprise PLM platform. It is evidence that the frozen business, information and decision architecture for these three scenarios is deterministic, traceable, auditable and historically reconstructable.

**Target spoken duration:** approximately 2:45–3:20 depending on pauses and emphasis.

---

# Compression and expansion points

If the listener interrupts during the 60-second version, preserve these three ideas before adding detail:

1. `Revision A → Revision B` is not a complete decision basis;
2. Assessment Baseline, proposal/overlay, impact, Assessment, readiness and authority remain separate;
3. the prototype proves the bounded architecture against deterministic evidence.

If the 3-minute version must be shortened to about two minutes, compress in this order:

1. shorten the implementation paragraph;
2. reduce Scenario A to one sentence;
3. keep Scenario B's explicit scope amendment and baseline reuse;
4. keep Scenario C's complete-package-but-insufficient-authority distinction;
5. retain the final claim boundary.

If more depth is requested, do not improvise a longer verbal version. Move to the 15-minute architecture walkthrough or 30-minute technical-review path so the added detail stays anchored to the canonical slides and committed evidence.

---

# Key phrases to keep stable

Use these phrases consistently because they encode frozen distinctions:

- **immutable Assessment Baseline**;
- **non-authoritative proposed-state Overlay Revision**;
- **Impact Candidate ≠ authorised scope**;
- **Evidence informs; Assessment concludes**;
- **Gate B = Decision Package Complete**;
- **Authorisation Eligibility is separate from completeness**;
- **authority insufficiency creates escalation, not a Decision**;
- **explicit authority disposition creates the terminal Decision Record**;
- **proposal revision does not automatically mean baseline revision**;
- **the prototype proves the architecture; it is not the primary deliverable**.

Avoid replacing these with generic workflow language that collapses the distinctions.

---

# Claims to avoid in spoken delivery

Do not say that the reference case:

- reproduces a company-specific PLM process;
- implements an enterprise PLM platform;
- discovers arbitrary graph impacts generally;
- automates engineering approval or judgement;
- proves enterprise-scale source authority, freshness or configuration governance;
- demonstrates production deployment readiness;
- implements an approval hierarchy beyond the synthetic `Standard < Elevated` comparison.

When challenged on one of these areas, state the bounded implementation choice and return to the supported architecture claim.
