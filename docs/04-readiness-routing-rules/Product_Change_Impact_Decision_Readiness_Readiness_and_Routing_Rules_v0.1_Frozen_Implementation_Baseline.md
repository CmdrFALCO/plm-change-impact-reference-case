# Product Change Impact Assessment & Decision Readiness

## Readiness and Routing Rules v0.1

**Document type:** Deterministic Readiness / Routing Rule Specification  
**Status:** Frozen implementation baseline  
**Domain:** Synthetic automotive Product Lifecycle Management  
**Version:** 0.1  
**Date:** 25 August 2026  
**Rule-set version:** `RRR-v0.1`  
**Governing artefacts:**
- Business Architecture Definition v0.3.1 — Frozen Implementation Baseline
- Logical Information Model v0.3.2 — Frozen Implementation Baseline
- Scenario Data Definition v0.1 — Frozen Implementation Baseline

---

## Document Notice

This document converts the frozen architecture and frozen Scenario Data test oracle into explicit deterministic readiness and routing rules for Scenarios A–C.

It does **not** introduce:

- a new PLM capability;
- a new process stage;
- a new domain entity or association;
- a new Change Item action;
- an enterprise approval hierarchy;
- a general configuration engine;
- automated engineering approval;
- source-authority or source-freshness governance.

The rule set is deliberately bounded to the synthetic reference case.

The implementation rule is:

> **The same frozen input state evaluated under `RRR-v0.1` must produce the same derived readiness values, Assessment Obligations, reuse classifications, and routing outcomes.**

---

# 1. Purpose

The purpose of this artefact is to define, precisely enough for deterministic implementation:

1. Gate A evaluation;
2. baseline reuse evaluation;
3. overlay execution eligibility;
4. assessment-routing rules `RRR-01` through `RRR-04`;
5. Assessment Obligation creation and fulfilment;
6. post-assessment scope-revision routing `RRR-05`;
7. Assessment reuse classification for the Scenario B second execution;
8. Gate B evaluation;
9. Authorisation Eligibility;
10. required-authority derivation `RRR-06`;
11. authority sufficiency and escalation;
12. terminal-decision persistence preconditions;
13. case-state derivation required by Scenarios A–C.

This artefact does not redefine the frozen Scenario Data records. It defines the predicates that explain why those records and derived values are expected.

---

# 2. Rule Authority and Precedence

The authority order is:

```text
Business Architecture v0.3.1
        ↓
Logical Information Model v0.3.2
        ↓
Scenario Data Definition v0.1
        ↓
Readiness and Routing Rules v0.1
```

This document may make an existing frozen rule executable or remove implementation ambiguity.

It may not override a frozen semantic rule.

If a rule in this document would require a new PLM concept to make Scenarios A–C work, that is an implementation issue and must be reviewed before the frozen architecture is changed.

---

# 3. Rule Evaluation Principles

## 3.1 Exact data, not free-text interpretation

`RRR-v0.1` does not use semantic interpretation, AI classification, or natural-language inference.

Where a rule reads a text-valued field, it uses an explicit exact value defined in this document.

Narrative fields such as Assessment `impact_statement` may explain a result but do not trigger a deterministic route in v0.1.

## 3.2 Case-local evaluation

Every rule evaluation is case-local.

A rule may use only records that resolve to the same `change_case_id` as the execution being evaluated.

Cross-case or cross-scenario joins are invalid.

## 3.3 Frozen-state evaluation

Historical execution rules use:

- Baseline Member snapshots for current state;
- Overlay-local Objects for proposed state;
- immutable Assessment content and Evidence snapshots for completed Assessments.

Later mutable source data must not change a historical rule result.

## 3.4 Failure is not absence

If a rule requires an input that is structurally required by `RRR-v0.1` and that input is missing, the implementation must not interpret the missing value as `false` or as "no obligation required".

The relevant calculation fails.

Where the failure occurs during assessment routing:

```text
impact_execution.routing_status = Failed
```

and Gate B cannot be evaluated as Complete.

## 3.5 No automatic engineering decision

This rule set calculates:

- readiness;
- required Assessments;
- routing outcomes;
- authorisation eligibility;
- required authority;
- authority sufficiency.

It does **not** autonomously select a terminal engineering outcome.

A terminal Decision Record still requires an explicit authority disposition command or test-fixture authority action.

This preserves the frozen exclusion of automated engineering approval.

---

# 4. Normative Evaluation Order

For one active proposal cycle, `RRR-v0.1` evaluates in this order:

```text
1. Gate A
        ↓
2. Establish / select Assessment Baseline
        ↓
3. Baseline validity / reuse check where applicable
        ↓
4. Overlay execution eligibility
        ↓
5. Create / validate Overlay Revision
        ↓
6. Execute impact analysis
        ↓
7. Assessment routing: RRR-01..RRR-04
        ↓
8. Perform / reuse Assessments
        ↓
9. Post-assessment scope routing: RRR-05
        │
        ├─ fires → Scope Revision Required → new proposal cycle
        │
        └─ does not fire
                ↓
10. Evaluate Gate B completeness predicates other than required authority
                │
                ├─ already incomplete → Gate B = Incomplete; stop readiness evaluation
                │
                └─ otherwise
                        ↓
11. Derive required authority: RRR-06
                        ↓
12. Finalise Gate B
                        ↓
13. Authorisation Eligibility
                        ↓
14. Authority sufficiency
                │
                ├─ insufficient → Escalated Process-history Entry
                │
                └─ sufficient → terminal authority disposition may be recorded
```

`RRR-05` has precedence over terminal-decision readiness for the execution in which it fires.

A scope-revision route therefore cannot create a Decision Record.

---

# 5. Common Derived Predicates

The following are derived calculations only. They are not new persistent business objects.

## 5.1 `material_characteristic_changed(execution)`

For each `Revise Product State` Change Item revision in the execution overlay:

1. resolve its predecessor Product Version Baseline Member;
2. read:
   ```text
   baseline.snapshot_payload.material_characteristic
   ```
3. resolve the Overlay-local Product Version created by that Change Item revision;
4. read:
   ```text
   overlay_local.state_payload.material_characteristic
   ```
5. compare the values using exact equality.

The predicate is true when at least one pair differs.

For the frozen fixtures:

```text
MC-BASE-01 != MC-A-01 → true
MC-BASE-01 != MC-B-01 → true
MC-BASE-01 != MC-C-01 → true
```

Therefore Scenarios A, B, and C all contain a material-characteristic change.

## 5.2 Bounded applicability-expression normalisation

The v0.1 fixtures use only conjunctions of exact feature/value equalities:

```text
Feature = "Value"
AND
Feature = "Value"
```

For v0.1 only, an expression is normalised to an unordered set of atomic equality clauses.

Examples:

```text
CoolingType = "Liquid"
```

becomes:

```text
{CoolingType=Liquid}
```

and:

```text
CoolingType = "Liquid" AND PackFamily = "LongRange"
```

becomes:

```text
{CoolingType=Liquid, PackFamily=LongRange}
```

This is not a general configuration engine.

## 5.3 `validated_scope_relation`

For the proposed successor Product Version and the affected current occurrence:

- `Equal` when both normalised clause sets are equal;
- `Proposed Narrower` when the proposed validated-scope clause set is a strict superset of the current applicability clause set;
- `Not Determinable` for syntax outside the bounded v0.1 grammar.

Only the first two results are required by Scenarios A–C.

Expected fixture values:

| Scenario / execution | Proposed validated scope | Current occurrence applicability | Relation |
|---|---|---|---|
| A / `IAX-A01` | `CoolingType = "Liquid"` | `CoolingType = "Liquid"` | Equal |
| B / `IAX-B01` | `CoolingType = "Liquid" AND PackFamily = "LongRange"` | `CoolingType = "Liquid"` | Proposed Narrower |
| B / `IAX-B02` | `CoolingType = "Liquid" AND PackFamily = "LongRange"` | baseline: `CoolingType = "Liquid"` | Proposed Narrower versus baseline; proposed occurrence is aligned in the overlay by `CI-B02:r1` |
| C / `IAX-C01` | `CoolingType = "Liquid"` | `CoolingType = "Liquid"` | Equal |

## 5.4 `overlay_contains_applicability_change(execution, occurrence)`

True when the execution overlay contains an Active selected Change Item revision with:

```text
action = Change Applicability
target_type = Product Structure Occurrence
target_id = occurrence
```

For `IAX-B02`, this is true for `PSO-002` because `CI-B02:r1` is contained in `OV-B02`.

---

# 6. Gate A — Ready for Initial Distribution

## 6.1 Gate A rule

Gate A passes only when all of the following are true:

1. the Change Case exists;
2. at least one Change Item Proposal State is `Active`;
3. every Active proposal references one existing selected Change Item Revision in the same Change Case;
4. every selected revision uses one of the two executable actions;
5. every selected revision passes the action-specific target-identification rule below;
6. Change Case `rationale` is non-empty;
7. the referenced Configuration Context exists and has `completeness_state = Complete` or `Partial`;
8. no unresolved Open Item exists with:
   ```text
   blocking_class = Blocking
   required_before_stage = Initial Distribution
   status != Resolved
   ```

Gate A does not read an Assessment Baseline.

## 6.2 `Revise Product State` target identification

Pass only when:

```text
target_type = Product Version
```

and:

- `target_id` resolves to an identifiable current Product Version;
- `current_state_reference.product_version_id = target_id`;
- referenced `revision` and `iteration` equal the identified current Product Version.

No Baseline Member check occurs here.

## 6.3 `Change Applicability` target identification

Pass only when:

```text
target_type = Product Structure Occurrence
```

and:

- `target_id` resolves to an identifiable current Product Structure Occurrence;
- `current_state_reference.occurrence_id = target_id`;
- predecessor Applicability Rule ID and version are supplied in `current_state_reference`.

The predecessor rule is not verified against the baseline until overlay execution eligibility.

## 6.4 Gate A expected results

```text
CHG-A01 → Pass
CHG-B01 initial proposal → Pass
CHG-B01 amended proposal → Pass
CHG-C01 → Pass
```

---

# 7. Baseline Validity and Reuse

## 7.1 Baseline reuse predicate

An existing Assessment Baseline may be reused only when all five frozen baseline-validity inputs are true:

```text
authoritative_current_state_unchanged
AND baseline_scope_still_sufficient
AND configuration_context_still_valid
AND effectivity_context_still_valid
AND extraction_basis_still_accepted
```

If all are true:

```text
baseline_reuse_permitted = true
```

If any is false:

```text
baseline_reuse_permitted = false
```

and a new Assessment Baseline is required before a new execution can proceed.

`RRR-v0.1` does not invent enterprise freshness thresholds or source-precedence logic for these five inputs.

## 7.2 Scenario B expected result

For the second proposal cycle in Scenario B, all five values are true.

Therefore:

```text
BL-B01 is reused
```

and no second Assessment Baseline is created.

---

# 8. Overlay Execution Eligibility

Overlay execution eligibility is evaluated after an Assessment Baseline exists and before impact-analysis execution.

It is not a new process gate.

## 8.1 Common rules

The candidate Overlay Revision must:

- belong to the same Change Case as the baseline;
- contain at least one Change Item revision;
- contain at most one revision per Change Item Identity;
- contain exactly the selected Active proposal revision for each included Change Item Identity at overlay creation.

## 8.2 `Revise Product State`

For each included `Revise Product State` revision:

1. the target Product Version must exist as a Baseline Member in the selected baseline;
2. the captured baseline Product Version state must match `current_state_reference`;
3. the proposed successor `(product_element_id, proposed_revision, proposed_iteration)` must not collide with:
   - an existing authoritative Product Version; or
   - another proposed successor in the same Overlay Revision.

## 8.3 `Change Applicability`

For each included `Change Applicability` revision:

1. the target Product Structure Occurrence must exist as a Baseline Member;
2. the captured occurrence state must match `current_state_reference`;
3. the predecessor Applicability Rule ID and version in `current_state_reference` must match the Applicability Rule captured for that occurrence;
4. the proposed rule remains overlay-local and does not mutate the Baseline Member.

## 8.4 Outcome

If every included Change Item revision passes:

```text
overlay_execution_eligibility = Pass
```

Otherwise:

```text
overlay_execution_eligibility = Fail
```

and no impact-analysis execution may begin from that overlay.

---

# 9. Assessment-routing Rule Mechanics

`RRR-01` through `RRR-04` create mandatory Assessment Obligations.

They are evaluated only after the Impact-analysis Execution itself has completed successfully and its Impact Candidates exist.

## 9.1 Domain candidate-link rule

For one routed domain:

- if one or more Impact Candidates exist for that domain, create one routed obligation per matching candidate;
- if zero Impact Candidates exist for that domain but the Change Item characteristic itself requires the domain assessment, create one execution-level obligation with:
  ```text
  impact_candidate_id = null
  ```

This rule permits execution-level retained Assessments to satisfy an obligation when the later execution has no new candidate in that domain.

It produces the required `null` candidate links for `AO-B23` and `AO-B24`.

## 9.2 Candidate state consequence

When a mandatory obligation is created for a candidate and is not yet satisfied:

```text
candidate_state = Assessment Planned
```

When all mandatory obligations referencing that candidate are satisfied:

```text
candidate_state = Assessed
```

This uses only the Impact Candidate states already defined by the frozen Logical Information Model.

---

# 10. `RRR-01` — Product Engineering Assessment

## 10.1 Trigger

```text
material_characteristic_changed(execution) = true
```

## 10.2 Routed domain

```text
Product Engineering
```

## 10.3 Requirement selection

For each Product Engineering candidate:

Use `REQ-004` when either condition is true:

1. the execution overlay contains a `Change Applicability` Change Item for the affected occurrence; or
2. the proposed successor validated scope has relation `Proposed Narrower` to the captured current occurrence applicability.

Otherwise use:

```text
REQ-001
```

Expected results:

```text
IAX-A01 → REQ-001
IAX-B01 → REQ-004
IAX-B02 → REQ-004
IAX-C01 → REQ-001
```

## 10.4 Output

Create mandatory Assessment Obligation(s):

```text
domain = Product Engineering
mandatory = true
routing_rule_reference = RRR-01
```

with the requirement selected above.

---

# 11. `RRR-02` — Validation Assessment

## 11.1 Trigger

```text
material_characteristic_changed(execution) = true
```

## 11.2 Routed domain and requirement

```text
domain = Validation
requirement_id = REQ-002
mandatory = true
routing_rule_reference = RRR-02
```

If no Validation Impact Candidate exists in the execution, create one execution-level obligation with `impact_candidate_id = null`.

This is the required result for `AO-B23` in `IAX-B02`.

---

# 12. `RRR-03` — Manufacturing Assessment

## 12.1 Trigger

```text
material_characteristic_changed(execution) = true
```

## 12.2 Routed domain and requirement

```text
domain = Manufacturing
requirement_id = REQ-003
mandatory = true
routing_rule_reference = RRR-03
```

If no Manufacturing Impact Candidate exists in the execution, create one execution-level obligation with `impact_candidate_id = null`.

---

# 13. `RRR-04` — Purchasing / Cost Assessment

## 13.1 Canonical supplier-related trigger values

`RRR-v0.1` recognises exactly these Change Case trigger values as supplier-related:

```text
Synthetic supplier process change
Synthetic supplier process change with elevated authority classification
```

No fuzzy text classification is used.

## 13.2 Trigger

If the Change Case `trigger` equals either canonical supplier-related value:

```text
supplier_related_trigger = true
```

## 13.3 Routed domain

```text
domain = Purchasing/Cost
requirement_id = null
mandatory = true
routing_rule_reference = RRR-04
```

If no Purchasing/Cost Impact Candidate exists in the execution, create one execution-level obligation with `impact_candidate_id = null`.

This is the required result for `AO-B24` in `IAX-B02`.

---

# 14. Assessment-routing Completion

Assessment routing for an Impact-analysis Execution is complete only when:

1. the execution status is `Completed`;
2. `RRR-01` through `RRR-04` have each been evaluated without rule-input failure;
3. every positive routing result has created its required Assessment Obligation record(s);
4. no additional obligation is inferred from the absence of Assessment records.

Then:

```text
impact_execution.routing_status = Completed
```

If rule evaluation cannot complete:

```text
impact_execution.routing_status = Failed
```

Zero Assessment Obligations is meaningful only when routing status is `Completed`, as required by the frozen Logical Information Model.

`RRR-05` and `RRR-06` do not change `impact_execution.routing_status`; they are later process-routing / authority calculations.

---

# 15. Assessment Obligation Fulfilment

A mandatory Assessment Obligation is satisfied only by a compatible Assessment.

## 15.1 Direct Assessment fulfilment

A direct Assessment is compatible when all are true:

- same Change Case;
- `origin_impact_execution_id` equals the target execution;
- `domain` equals the obligation domain;
- `assessment_state = Complete`;
- if the obligation has `impact_candidate_id`, an Assessment Impact Link exists to that candidate;
- if the obligation has `requirement_id`, exactly one Assessment Requirement Conclusion exists for that Requirement;
- required Assessment Evidence Use criteria in §15.3 are met.

When the Assessment fulfils the obligation, the frozen lock rule applies and the Assessment becomes immutable.

## 15.2 Retained historical Assessment fulfilment

A historical Assessment can satisfy a later execution obligation only when:

- the Assessment is Complete;
- the Assessment is locked;
- domain matches;
- requirement matches where the obligation has a Requirement;
- an Assessment Reuse Classification exists for the target execution with:
  ```text
  classification = Retained
  ```
- required Evidence Use criteria remain satisfied by the immutable historical Assessment.

`Revalidation Required` and `Invalidated` never satisfy a mandatory obligation.

The target execution's Assessment Obligation may reference the retained Assessment through `fulfilled_by_assessment_id`; the historical Assessment content itself is not edited.

## 15.3 Evidence-use criterion for `RRR-v0.1`

Every mandatory obligation created by `RRR-01` through `RRR-04` requires its satisfying Assessment to contain at least one Assessment Evidence Use.

When predecessor Evidence is used for an Overlay-local successor Product Version, an explicit transferability conclusion is required.

A use with:

```text
transferability_conclusion = Not Applicable to Proposed State
```

cannot satisfy the v0.1 evidence-use criterion for that Assessment.

A missing Assessment Evidence Use does not mean "no evidence required".

## 15.4 Requirement conclusion and completeness

For Gate B completeness, a routed Requirement needs a conclusion record, but the conclusion value may be:

- Satisfied;
- Not Satisfied;
- Not Demonstrated;
- Not Applicable.

The conclusion value is interpreted later by Authorisation Eligibility.

This preserves the frozen separation:

> **package complete ≠ substantively authorised**

---

# 16. `RRR-05` — Scope Revision Required

## 16.1 Purpose

`RRR-05` converts the Scenario B assessed applicability mismatch into a deterministic process route without reading the Assessment narrative.

## 16.2 Trigger

`RRR-05` fires when all of the following are true for one completed execution:

1. `validated_scope_relation = Proposed Narrower` for a proposed successor Product Version and an affected current Product Structure Occurrence;
2. a Complete Product Engineering Assessment is linked to that occurrence Impact Candidate;
3. that Assessment contains:
   ```text
   requirement_id = REQ-004
   conclusion = Not Satisfied
   ```
4. the current Overlay Revision does **not** contain a `Change Applicability` Change Item targeting that occurrence.

No `impact_statement` text parsing is required.

## 16.3 Outcome

Create one Process-history Entry:

```text
entry_type = Scope Revision Required
origin_stage = Domain Assessment
target_stage_or_route = Scope Confirmation
```

The reason states that the assessed occurrence applicability must be added explicitly to Proposed Change Scope.

If the triggering Impact Candidate has exactly one unique source Change Item revision in its provenance, populate:

```text
affected_change_item_id
affected_change_item_revision
```

with that revision.

If more than one unique source revision exists, those optional fields are left null rather than selecting one arbitrarily.

## 16.4 Required effects

When `RRR-05` fires:

- no terminal Decision Record is created for that execution;
- Impact Candidate discovery does not create a Change Item automatically;
- the Change Owner must explicitly create or revise Change Item scope;
- a new Overlay Revision is required;
- a Baseline Validity Check is performed;
- a new Impact-analysis Execution is required.

## 16.5 Precedence

`RRR-05` is evaluated before Gate B is used for terminal-decision readiness.

When it fires:

```text
exact Proposed Change Scope is not final for terminal decision
```

therefore the execution cannot satisfy the Gate B exact-scope condition for a terminal decision package.

## 16.6 Scenario results

```text
IAX-A01 → does not fire
IAX-B01 → fires
IAX-B02 → does not fire
IAX-C01 → does not fire
```

For `IAX-B02`, the new overlay contains `CI-B02:r1` with `Change Applicability`, so the scope-revision condition is no longer true.

---

# 17. Assessment Reuse Classification for a Later Execution

Reuse classification is execution-relative and never edits the historical Assessment.

The following ordered rules are sufficient for the frozen Scenario B second execution.

## 17.1 Priority 1 — Invalidated

Classify a historical Assessment as:

```text
Invalidated
```

when the later overlay explicitly changes the same occurrence applicability state that was the subject of the historical Assessment's `REQ-004 = Not Satisfied` conclusion.

Scenario result:

```text
ASM-B01 → Invalidated for IAX-B02
```

because `CI-B02:r1` changes the applicability of `PSO-002`, which is the exact state that `ASM-B01` found non-compliant.

## 17.2 Priority 2 — Revalidation Required

Classify a historical Manufacturing Assessment as:

```text
Revalidation Required
```

when the later overlay adds or changes applicability for an occurrence linked to the historical Manufacturing Impact Candidate, while the underlying proposed Product Version material-characteristic state is unchanged.

Scenario result:

```text
ASM-B03 → Revalidation Required for IAX-B02
```

because manufacturing must confirm the changed applicability assumptions.

## 17.3 Priority 3 — Retained

Classify a historical Assessment as:

```text
Retained
```

when all are true:

- its domain is unaffected by the newly added `Change Applicability` scope in the bounded v0.1 rule set;
- the original `Revise Product State` Change Item revision remains in the new overlay unchanged;
- the Overlay-local proposed Product Version state payload created from that Change Item revision is technically identical to the state previously assessed for the relevant domain;
- no Priority 1 or Priority 2 rule applies.

For v0.1, the domains that satisfy this condition in Scenario B are:

```text
Validation
Purchasing/Cost
```

Scenario results:

```text
ASM-B02 → Retained for IAX-B02
ASM-B04 → Retained for IAX-B02
```

## 17.4 No implicit default

If a historical Assessment considered for reuse matches none of the rules above, no reuse classification is inferred.

It cannot satisfy a later mandatory obligation until a valid explicit classification exists.

---

# 18. Required Authority — `RRR-06`

## 18.1 Purpose

`RRR-06` derives the synthetic required authority level from existing frozen Change Case data without adding a new classification object.

## 18.2 Canonical authority trigger mapping

Exact mapping:

```text
Change Case trigger:
"Synthetic supplier process change with elevated authority classification"
        → required_authority_level = Elevated
```

Exact mapping:

```text
Change Case trigger:
"Synthetic supplier process change"
        → required_authority_level = Standard
```

No fuzzy text or semantic classification is used.

If an in-scope case trigger is not mapped by `RRR-06`, required authority is not derivable under v0.1 and Gate B cannot become Complete.

No third Authority Level is persisted.

## 18.3 Current authority for the v0.1 demonstrator

The synthetic decision-route execution context for `RRR-v0.1` is:

```text
current_authority_level = Standard
```

This is a rule-set execution-context value, not a first-class business entity and not an enterprise authority hierarchy.

Expected fixture results:

```text
CHG-A01 → required Standard / current Standard
CHG-C01 → required Elevated / current Standard
```

Scenario B does not reach authority sufficiency at its defined v0.1 stop point.

---

# 19. Gate B — Decision Package Complete

Gate B uses short-circuit evaluation.

First evaluate all package-completeness predicates that do not depend on required authority:

- impact execution completed;
- assessment routing completed;
- `RRR-05` did not require scope revision for the proposal cycle being considered for terminal decision;
- exact Proposed Change Scope is known;
- mandatory Assessment Obligations are satisfied;
- mandatory Impact Candidates have required coverage;
- Decision-blocking Open Items are resolved;
- required Evidence criteria are fulfilled.

If any of these predicates is false, Gate B is already `Incomplete` and v0.1 does not need to derive required authority for that stop point.

If all are true, evaluate `RRR-06`. Gate B can become `Complete` only when required authority is then successfully derived.

This preserves the frozen rule that required authority must be known for a Complete Gate B while allowing Scenario B to stop deterministically before authority evaluation once unsatisfied mandatory obligations already make Gate B Incomplete.

## 19.1 Exact Proposed Change Scope

For v0.1, exact Proposed Change Scope is known when:

1. the Overlay Revision contains exactly the selected Active Change Item revisions for the proposal cycle being evaluated; and
2. no `RRR-05` Scope Revision Required route is outstanding for that execution.

## 19.2 Mandatory obligation satisfaction

```text
all_mandatory_obligations_satisfied = true
```

only when every mandatory Assessment Obligation has a valid satisfying Assessment under §15.

## 19.3 Mandatory Impact Candidate coverage

For deterministic v0.1 evaluation:

> A mandatory Impact Candidate is an Impact Candidate referenced by at least one mandatory Assessment Obligation.

Each such candidate has required coverage when all mandatory obligations that reference it are satisfied.

This avoids inferring mandatory status from candidate absence or candidate type alone.

## 19.4 Decision-blocking Open Items

Gate B requires no unresolved Open Item matching:

```text
blocking_class = Blocking
required_before_stage = Decision
status != Resolved
```

## 19.5 Evidence criteria

For every satisfied mandatory obligation, the satisfying Assessment must meet §15.3.

## 19.6 Gate B formula

```text
Gate B = Complete
```

only when all are true:

```text
impact_execution.execution_status = Completed
AND impact_execution.routing_status = Completed
AND exact_proposed_change_scope_known = true
AND all_mandatory_obligations_satisfied = true
AND all_mandatory_impact_candidates_covered = true
AND decision_blocking_open_items_resolved = true
AND required_evidence_criteria_fulfilled = true
AND required_authority_level_is_known = true
```

Otherwise:

```text
Gate B = Incomplete
```

If prerequisite rule evaluation itself failed, Gate B is not treated as Complete.

## 19.7 Scenario results

```text
IAX-A01 → Complete
IAX-B01 → not terminal-decision-ready because RRR-05 fires
IAX-B02 → Incomplete because AO-B21 and AO-B22 are unsatisfied
IAX-C01 → Complete
```

---

# 20. Authorisation Eligibility

Authorisation Eligibility is evaluated only when Gate B is Complete.

## 20.1 Blocking Assessment dispositions

Any mandatory satisfying Assessment with:

```text
Objection
Escalation Recommended
```

makes:

```text
authorisation_eligibility = Blocked
```

## 20.2 Blocking Requirement conclusions

Any mandatory routed Requirement conclusion with:

```text
Not Satisfied
Not Demonstrated
```

makes:

```text
authorisation_eligibility = Blocked
```

## 20.3 Permitted result

If none of the blockers above exists:

```text
authorisation_eligibility = Permitted
```

`No Objection with Conditions` does not automatically create a Decision Condition and does not override a blocking Requirement conclusion.

Decision Conditions remain post-authorisation records created only as children of an authorised terminal Decision Record.

## 20.4 Scenario results

```text
Scenario A → Permitted
Scenario B / IAX-B02 → Not Evaluated because Gate B is Incomplete
Scenario C → Permitted
```

---

# 21. Authority Sufficiency and Escalation

Authority ordering is frozen as:

```text
Standard < Elevated
```

## 21.1 Authority sufficient

When:

```text
required_authority_level <= current_authority_level
```

then:

```text
authority_sufficient = true
```

If Gate B is Complete and Authorisation Eligibility is Permitted:

```text
decision_permitted = true
escalation_required = false
```

## 21.2 Authority insufficient

When:

```text
required_authority_level > current_authority_level
```

then:

```text
authority_sufficient = false
decision_permitted = false
escalation_required = true
```

If Gate B is Complete and Authorisation Eligibility is Permitted, create an `Escalated` Process-history Entry.

No terminal Decision Record may be created.

## 21.3 Escalation event content

The rule determines:

```text
entry_type = Escalated
origin_stage = Authority Check
target_stage_or_route = Elevated Authority Route
reason = Required authority is Elevated while current authority is Standard.
```

Actor and timestamp are execution-context values supplied by the deterministic scenario fixture / later application command context.

Where the Decision Scope contains exactly one Active Change Item revision, the event may populate its optional affected Change Item fields.

## 21.4 Scenario C result

```text
required = Elevated
current = Standard
→ decision_permitted = false
→ escalation_required = true
→ HIST-C01 = Escalated
→ no Decision Record
```

---

# 22. Terminal Decision Persistence Preconditions

This rule set does not select a terminal decision outcome.

It validates whether an explicit authority disposition may be persisted.

## 22.1 Authorised outcomes

An explicit authority command for either:

```text
Authorised for Downstream Processing
Authorised with Conditions
```

may be persisted only when:

- Gate B = Complete;
- Authorisation Eligibility = Permitted;
- authority sufficient;
- no unresolved Decision-blocking Open Item exists;
- Decision Scope is non-empty and contains only Change Item revisions in the final Overlay Revision.

Additional frozen constraints remain:

```text
Authorised for Downstream Processing → zero Decision Conditions
Authorised with Conditions → one or more valid Decision Conditions
```

## 22.2 Rejected

A `Rejected` authority disposition follows the frozen Logical Information Model constraints and is not exercised by Scenarios A–C.

## 22.3 Decision Support Assessment completeness

For a terminal Decision Record, the Decision Support Assessment set must include the satisfying Assessment for every mandatory Assessment Obligation of the decision execution.

A retained historical Assessment may be included only when its reuse classification for the decision execution is `Retained`.

## 22.4 Scenario A

The Scenario A test fixture supplies the explicit Standard-authority disposition:

```text
Authorised for Downstream Processing
```

Because all persistence preconditions pass, the implementation persists `DEC-A01` with:

- exact final baseline;
- exact final overlay;
- exact final execution;
- one Decision Scope Item for `CI-A01:r1`;
- four Decision Support Assessments;
- zero Decision Conditions.

This is deterministic persistence of an explicit authority action, not automated engineering approval.

---

# 23. Case-state Derivation Required by Scenarios A–C

Only the case-state results required by the frozen scenarios are specified here.

## 23.1 In Assessment

When the current execution is complete and routing is complete but one or more mandatory Assessment Obligations remain unsatisfied:

```text
case_state = In Assessment
```

Scenario result:

```text
CHG-B01 after IAX-B02 → In Assessment
```

## 23.2 Decision Ready

When:

```text
Gate B = Complete
```

and no terminal Decision Record has closed the case:

```text
case_state = Decision Ready
```

This state is retained after an authority escalation because the package remains complete while the case remains open.

Scenario result:

```text
CHG-C01 → Decision Ready
```

## 23.3 Closed by Decision

After a terminal Decision Record, the case becomes `Closed by Decision` only when no selected Active proposal revision remains undisposed.

Scenario result:

```text
CHG-A01 → Closed by Decision
```

The selected `CI-A01:r1` Proposal State may remain `Active`; its terminal disposition is derived from Decision Scope and `DEC-A01`.

---

# 24. Scenario A Deterministic Trace

```text
Gate A
→ Pass

BL-A01 established
→ Overlay execution eligibility Pass

OV-A01 + BL-A01
→ IAX-A01 Completed

material_characteristic_changed = true
supplier_related_trigger = true

RRR-01
→ AO-A01 Product Engineering / REQ-001 / IC-A01

RRR-02
→ AO-A02 Validation / REQ-002 / IC-A02

RRR-03
→ AO-A03 Manufacturing / REQ-003 / IC-A03

RRR-04
→ AO-A04 Purchasing/Cost / null / IC-A04

All four obligations satisfied
→ routing Complete

RRR-05
→ does not fire

RRR-06
→ required authority Standard
current authority Standard

Gate B
→ Complete

Authorisation Eligibility
→ Permitted

Authority sufficient
→ decision_permitted = true

Explicit authority disposition
→ Authorised for Downstream Processing
→ DEC-A01
→ CHG-A01 Closed by Decision
```

---

# 25. Scenario B Deterministic Trace

## 25.1 First execution

```text
Gate A
→ Pass

BL-B01 established
→ Overlay execution eligibility Pass

OV-B01 + BL-B01
→ IAX-B01 Completed

material_characteristic_changed = true
validated_scope_relation = Proposed Narrower
supplier_related_trigger = true

RRR-01
→ AO-B01 Product Engineering / REQ-004 / IC-B01

RRR-02
→ AO-B02 Validation / REQ-002 / IC-B02

RRR-03
→ AO-B03 Manufacturing / REQ-003 / IC-B03

RRR-04
→ AO-B04 Purchasing/Cost / null / IC-B04

All four obligations satisfied
→ routing Complete

ASM-B01
→ REQ-004 = Not Satisfied

RRR-05
→ fires
→ HIST-B01 Scope Revision Required
→ no Decision Record
```

## 25.2 Scope amendment

The Change Owner explicitly adds:

```text
CI-B02:r1 = Change Applicability
```

The system does not create it automatically.

Gate A for the amended Active proposal set:

```text
CI-B01:r1 + CI-B02:r1
→ Pass
```

Baseline validity:

```text
all five reuse inputs = true
→ BL-B01 reused
```

Overlay execution eligibility:

```text
CI-B01:r1 → Pass
CI-B02:r1 → Pass
```

Create:

```text
OV-B02
→ IAX-B02
```

## 25.3 Reuse classification

```text
ASM-B01 → Invalidated
ASM-B02 → Retained
ASM-B03 → Revalidation Required
ASM-B04 → Retained
```

## 25.4 Second-execution routing

The unchanged proposed Product Version still contains a material-characteristic change.

```text
RRR-01
→ AO-B21 Product Engineering / REQ-004 / IC-B21

RRR-02
→ AO-B23 Validation / REQ-002 / null
→ fulfilled by retained ASM-B02

RRR-03
→ AO-B22 Manufacturing / REQ-003 / IC-B22

RRR-04
→ AO-B24 Purchasing/Cost / null
→ fulfilled by retained ASM-B04
```

`AO-B21` and `AO-B22` remain unsatisfied.

Therefore:

```text
Gate B = Incomplete
Authorisation Eligibility = Not Evaluated
Decision Record = none
CHG-B01 = In Assessment
```

---

# 26. Scenario C Deterministic Trace

```text
Gate A
→ Pass

BL-C01 established
→ Overlay execution eligibility Pass

OV-C01 + BL-C01
→ IAX-C01 Completed

material_characteristic_changed = true
supplier_related_trigger = true

RRR-01
→ AO-C01 Product Engineering / REQ-001 / IC-C01

RRR-02
→ AO-C02 Validation / REQ-002 / IC-C02

RRR-03
→ AO-C03 Manufacturing / REQ-003 / IC-C03

RRR-04
→ AO-C04 Purchasing/Cost / null / IC-C04

All obligations satisfied
→ routing Complete

RRR-05
→ does not fire

RRR-06
trigger = "Synthetic supplier process change with elevated authority classification"
→ required authority = Elevated

current authority = Standard

Gate B
→ Complete

Authorisation Eligibility
→ Permitted

Elevated > Standard
→ decision_permitted = false
→ escalation_required = true
→ HIST-C01 Escalated
→ no Decision Record
→ CHG-C01 remains Decision Ready
```

---

# 27. Expected Rule-to-Scenario Matrix

| Rule / predicate | Scenario A | Scenario B — IAX-B01 | Scenario B — IAX-B02 | Scenario C |
|---|---|---|---|---|
| Gate A | Pass | Pass | Pass after scope amendment | Pass |
| Overlay execution eligibility | Pass | Pass | Pass with reused `BL-B01` | Pass |
| `material_characteristic_changed` | true | true | true | true |
| `validated_scope_relation` | Equal | Proposed Narrower | Proposed Narrower versus baseline; proposed occurrence aligned in overlay | Equal |
| `RRR-01` | PE / REQ-001 | PE / REQ-004 | PE / REQ-004 | PE / REQ-001 |
| `RRR-02` | Validation / REQ-002 | Validation / REQ-002 | Validation / REQ-002, candidate null | Validation / REQ-002 |
| `RRR-03` | Manufacturing / REQ-003 | Manufacturing / REQ-003 | Manufacturing / REQ-003 | Manufacturing / REQ-003 |
| `RRR-04` | Purchasing/Cost | Purchasing/Cost | Purchasing/Cost, candidate null | Purchasing/Cost |
| `RRR-05` | no | **Scope Revision Required** | no | no |
| Baseline reuse | n/a | n/a | `BL-B01` reused | n/a |
| Assessment reuse | n/a | n/a | I/R/RV/R as frozen oracle | n/a |
| Gate B at stop point | Complete | not terminal-decision-ready due scope route | Incomplete | Complete |
| Authorisation Eligibility | Permitted | not used for terminal decision | Not Evaluated | Permitted |
| `RRR-06` required authority | Standard | not terminally evaluated | not evaluated at stop point | Elevated |
| Current authority | Standard | — | — | Standard |
| Authority result | sufficient | — | — | insufficient |
| Terminal Decision Record | `DEC-A01` | none | none | none |
| Process-history route | none | `HIST-B01` | none | `HIST-C01` |

`I/R/RV/R` means the Scenario B reuse classifications are:

```text
ASM-B01 = Invalidated
ASM-B02 = Retained
ASM-B03 = Revalidation Required
ASM-B04 = Retained
```

---

# 28. Explicit Non-Rules in v0.1

The following are deliberately not derived by `RRR-v0.1`:

- a general impact-discovery algorithm for arbitrary PLM graphs;
- new Impact Candidate types or domains;
- enterprise source precedence;
- source freshness thresholds;
- full configuration satisfiability;
- risk scoring;
- approval hierarchy beyond `Standard < Elevated`;
- authority overrides of Objection or unmet mandatory Requirements;
- automatic Change Item creation from Impact Candidates;
- automatic Decision Condition creation from `No Objection with Conditions`;
- automatic terminal authorisation;
- production, plant, stock, service, or release semantics.

The frozen Scenario Data remains the oracle for exact Impact Candidate records and provenance paths used by Scenarios A–C.

---

# 29. Deterministic Implementation Assertions

An implementation conforming to `RRR-v0.1` must satisfy all of the following.

1. Gate A never reads baseline membership.
2. Overlay execution eligibility always reads the selected baseline.
3. A failed overlay eligibility check prevents impact execution.
4. Routing cannot be marked Completed until all `RRR-01..04` evaluations have completed and all positive results are materialised as Assessment Obligations.
5. Absence of an Assessment never means absence of an obligation.
6. A retained historical Assessment satisfies a later obligation only through an explicit `Retained` reuse classification.
7. `Revalidation Required` and `Invalidated` never satisfy a mandatory obligation.
8. `RRR-05` uses structured state and Requirement Conclusion data, not free-text Assessment interpretation.
9. `RRR-05` never creates the required new Change Item automatically.
10. A scope revision creates a new overlay and execution but does not automatically create a new baseline.
11. Gate B uses explicit obligations rather than inferred assessment need.
12. Gate B completeness does not inspect the positivity of a Requirement Conclusion beyond requiring the conclusion to exist.
13. Authorisation Eligibility separately blocks `Objection`, `Escalation Recommended`, `Not Satisfied`, and `Not Demonstrated`.
14. `RRR-06` derives Elevated authority for Scenario C by exact frozen trigger mapping.
15. Authority insufficiency creates an `Escalated` Process-history Entry and never a Decision Record.
16. Scenario A's terminal Decision Record is persisted only after an explicit authority disposition.
17. Decision Support Assessments cover every mandatory Assessment Obligation used for the decision execution.
18. Case closure remains derived from terminal Decision Scope and remaining Active undisposed proposals.
19. No rule crosses Change Case boundaries.
20. No rule mutates an immutable Baseline Member, Overlay Revision history, locked Assessment, or historical Evidence Use.

---

# 30. Blocker-only Review Questions

Review v0.1 only for contradictions that prevent deterministic implementation of Scenarios A–C.

1. Can `RRR-01..04` reproduce every Assessment Obligation in the frozen Scenario Data, including the null-candidate retained obligations in `IAX-B02`?
2. Can the bounded applicability comparison distinguish Scenario B first execution from A and C without a general configuration engine?
3. Can `RRR-05` produce `Scope Revision Required` from structured data without reading free-text Assessment conclusions?
4. Can Scenario B reuse classifications be calculated without modifying historical Assessments?
5. Can Gate B be calculated from explicit obligations, coverage, Open Items, Evidence Uses, and required authority?
6. Can Authorisation Eligibility remain independent of Gate B completeness?
7. Can `RRR-06` deterministically produce Elevated authority for Scenario C without introducing a new authority entity?
8. Can authority insufficiency route to `Escalated` without creating a terminal Decision Record?
9. Can Scenario A persist its expected Decision Record without making the system an automated decision-maker?
10. Can all three scenarios produce the exact frozen stop-point states without adding a new PLM capability, process stage, object family, or Change Item action?

Only an implementation-blocking contradiction should prevent freeze.

---

# 31. Freeze Criteria

Readiness and Routing Rules v0.1 can be frozen when blocker-only review finds no contradiction in:

- Gate A sequencing;
- baseline reuse;
- overlay execution eligibility;
- Assessment Obligation generation;
- Assessment reuse and fulfilment;
- Scope Revision Required routing;
- Gate B calculation;
- Authorisation Eligibility;
- authority derivation and escalation;
- terminal Decision persistence preconditions;
- Scenario A–C expected stop-point states.

After freeze, proceed to:

> **Solution Architecture v0.1**

The Solution Architecture must implement these rules without adding business semantics.

---

# 32. Freeze Record

**Freeze decision:** `FREEZE`  
**Freeze date:** 25 August 2026

The blocker-only review found no contradiction that prevents deterministic implementation of Scenarios A–C.

The frozen rule set is therefore authoritative for the next implementation phase. It provides deterministic rules for:

- Gate A;
- baseline reuse;
- overlay execution eligibility;
- Assessment Obligation generation;
- direct and retained Assessment fulfilment;
- Scope Revision Required routing;
- Gate B;
- Authorisation Eligibility;
- authority derivation;
- escalation;
- terminal Decision persistence preconditions;
- the Scenario A–C case-state derivations.

No additional business semantic rule is required to implement the three frozen scenarios.

The next artefact is:

> **Solution Architecture v0.1**

