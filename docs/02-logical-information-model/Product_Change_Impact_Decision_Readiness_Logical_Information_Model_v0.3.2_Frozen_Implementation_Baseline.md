# Product Change Impact Assessment & Decision Readiness

## Logical Information Model v0.3.2 — Frozen Implementation Baseline

**Document type:** Logical Information Model  
**Status:** Frozen implementation baseline  
**Domain:** Synthetic automotive Product Lifecycle Management  
**Version:** 0.3.2  
**Date:** August 2026  
**Parent artefact:** Business Architecture Definition v0.3.1 — Frozen Implementation Baseline  
**Supersedes:** Logical Information Model v0.3.1 — Frozen Implementation Baseline  

---

## Document Notice

This document defines the logical information model for a synthetic PLM Business Architecture reference case.

It translates the frozen Business Architecture into implementation-neutral information semantics.

It does **not** define:

- a physical database schema;
- a specific persistence technology;
- enterprise PLM integration;
- Mercedes-Benz systems, processes, identifiers, or data structures;
- a production-ready configuration-management model.

Version 0.3.2 addresses only the Gate A / Assessment Baseline sequencing contradiction identified after the v0.3.1 implementation freeze.

No new PLM capability, scenario, process stage, or object family is introduced.

---

## Change from v0.3.1

Version 0.3.2 makes one implementation-blocking correction only.

The v0.3.1 model made Gate A depend on action-specific target checks that included membership in a selected Assessment Baseline, while the frozen Business Architecture establishes or selects that baseline only after Gate A. Version 0.3.2 separates:

- **Gate A target identification** — sufficient current-target identification for controlled initial distribution; and
- **Overlay execution eligibility** — baseline-relative verification performed after an Assessment Baseline exists and before the proposed-state overlay is accepted for impact-analysis execution.

The process order, capability architecture, entity model, executable Change Item actions, and Scenarios A–C are unchanged.

---

# 1. Purpose

The purpose of this document is to define, precisely enough for deterministic implementation:

- logical entities;
- logical identities and revision semantics;
- immutable historical state;
- entity ownership;
- cardinalities;
- semantic associations;
- Assessment Baseline snapshot semantics;
- Proposed-State Overlay membership and identity;
- Impact-analysis Execution lineage;
- structured Impact Candidate provenance;
- Assessment obligations;
- Assessment-to-Requirement conclusions;
- Assessment-to-Evidence use and transferability;
- Assessment reuse across later executions;
- Open Item blocking semantics;
- routing-state semantics;
- Process-history representation;
- Decision Record support lineage;
- Decision Condition semantics;
- exact Decision Scope;
- proposal-state removal;
- Case closure semantics;
- downstream Handover View derivation.

The implementation must not introduce new PLM semantics beyond this model unless implementation exposes an actual contradiction requiring a revision of the frozen Business Architecture.

---

# 2. Governing Invariants

This model inherits the frozen invariants from Business Architecture Definition v0.3.1 and the accepted v0.2 logical-model corrections.

## LIM-INV-01 — Baseline plus overlay

Impact analysis evaluates:

> **immutable Assessment Baseline + versioned Change Item overlay**

The overlay never mutates authoritative baseline information.

## LIM-INV-02 — Proposal change is not baseline change

A revision of Proposed Change Scope requires:

- a new Overlay Revision;
- a new Impact-analysis Execution.

It does not automatically require a new Assessment Baseline.

## LIM-INV-03 — Baselined state is historically reconstructible

A Baseline Member is an immutable captured state.

Historical reconstruction must not depend on later mutable source-record values.

## LIM-INV-04 — Baselined Product Version immutability

A Product Version referenced by an Assessment Baseline or Decision Record lineage is immutable.

## LIM-INV-05 — Identity, state, and usage are separate

The model distinguishes:

- Product Element;
- Product Version;
- Product Structure Occurrence.

## LIM-INV-06 — Applicability and effectivity are separate

Applicability answers **where** something applies.

Effectivity answers **when** it applies.

## LIM-INV-07 — Change Item identity and revision are separate

A Change Item has:

- one stable logical identity;
- one or more immutable technical-content revisions.

## LIM-INV-08 — Proposal lifecycle is separate from revision content

Selection, activation, removal, and terminal disposition are not part of immutable Change Item Revision technical content.

## LIM-INV-09 — Overlay membership is explicit and immutable

An Overlay Revision contains an explicit set of Change Item revisions.

Historical membership does not change when the proposal lifecycle later changes.

## LIM-INV-10 — Overlay-local identity belongs to the Overlay Revision

Proposed-state object identity is scoped to exactly one Overlay Revision.

All executions using that overlay refer to the same overlay-local object identifiers.

## LIM-INV-11 — Impact discovery is not engineering confirmation

Impact-analysis execution can produce Impact Candidates.

Only Assessment can determine domain relevance and disposition.

## LIM-INV-12 — Impact Candidate provenance is structured and many-to-many capable

An Impact Candidate may be caused by:

- multiple Change Item revisions;
- multiple dependency paths.

Every provenance path is structured, ordered, and reconstructible.

## LIM-INV-13 — Evidence is not compliance

Evidence can address a Requirement.

Only an Assessment can record a Requirement Conclusion.

## LIM-INV-14 — Evidence state used by an Assessment is historically reconstructible

Assessment Evidence Use preserves the exact evidence state used for that Assessment.

Later Evidence changes cannot alter the apparent basis of a historical Assessment or Decision.

## LIM-INV-15 — Completed supporting Assessments become immutable

A Complete Assessment becomes immutable when it:

- fulfils an Assessment Obligation;
- is classified as Retained for a later execution; or
- supports a Decision Record.

## LIM-INV-16 — Evidence transferability is contextual

Transferability is a property of an Assessment’s use of Evidence for an evaluated Product Version.

It is not an intrinsic property of the Evidence Record.

## LIM-INV-17 — Assessment reuse is execution-relative

An Assessment can be Retained for one later execution and Invalidated for another.

Reuse classification therefore cannot be stored as a permanent field on Assessment.

## LIM-INV-18 — Assessment readiness is obligation-driven

Gate B is evaluated against explicit Assessment Obligations.

The absence of an Assessment record is never interpreted as proof that no Assessment is required.

## LIM-INV-19 — Package completeness and authorisation eligibility are separate

A complete Decision Package may still contain:

- Objection;
- Escalation Recommended;
- Not Satisfied;
- Not Demonstrated.

These outcomes can prevent authorisation even when Gate B is complete.

## LIM-INV-20 — Pre-decision and post-decision obligations are distinct

Pre-decision unresolved matters are Open Items.

Post-decision obligations are Decision Conditions.

## LIM-INV-21 — Decision and routing are distinct

Only terminal authority dispositions create Decision Records.

Non-terminal routing creates Process-history Entries.

## LIM-INV-22 — Withdrawal is administrative closure

Withdrawal creates a terminal Case Closure Process-history Entry, not a Decision Record.

## LIM-INV-23 — Decision lineage is explicit

Every Decision Record references:

- exact Change Item revisions;
- Assessment Baseline;
- Overlay Revision;
- Impact-analysis Execution;
- exact supporting Assessments.

## LIM-INV-24 — Case-local lineage

Any lineage association joining Change Case, Change Item Revision, Assessment Baseline, Overlay Revision, Impact-analysis Execution, Impact Candidate, Assessment, Open Item, Decision Record, or Process-history Entry must resolve to exactly one Change Case.

---

# 3. Logical Model Structure

The model distinguishes:

1. domain entities;
2. semantic associations;
3. supporting records/value objects.

---

## 3.1 Domain entities

### Product-information layer

1. Product Element
2. Product Version
3. Product Structure Occurrence

### Change and analysis layer

4. Change Case
5. Change Item Revision
6. Assessment Baseline
7. Overlay Revision
8. Impact-analysis Execution
9. Impact Candidate

### Assessment and readiness layer

10. Assessment
11. Evidence Record
12. Open Item

### Decision and audit layer

13. Decision Record
14. Process-history Entry

---

## 3.2 Semantic associations

1. Baseline Member
2. Change Item Proposal State
3. Overlay Change Item Membership
4. Overlay-local Object
5. Impact Candidate Provenance
6. Assessment Impact Link
7. Assessment Obligation
8. Assessment Requirement Conclusion
9. Assessment Evidence Use
10. Assessment Reuse Classification
11. Decision Support Assessment
12. Decision Scope Item

These associations do not add PLM capability.

They preserve lineage, state, scope, and evaluation semantics between domain entities.

---

## 3.3 Supporting records/value objects

- Change Item Identity
- Configuration Context
- Applicability Rule
- Effectivity Specification
- Requirement
- Decision Condition
- Authority Level
- Dependency Path Step

The physical storage representation remains deferred to Solution Architecture.

---

# 4. Identifier Conventions

All persistent domain entities and semantic associations require stable identifiers.

Illustrative examples:

```text
PE-001
PV-001
PSO-001
CHG-001
CI-001
BL-001
BM-001
OV-001
OVOBJ-001
IAX-001
IC-001
ICP-001
AO-001
ASM-001
ARC-001
AEU-001
ARU-001
EV-001
OI-001
DEC-001
DSA-001
DSI-001
HIST-001
```

Identifiers must:

- remain stable for the life of the record;
- not encode mutable business state;
- not be reused;
- not depend on display names;
- remain unchanged when a record is superseded.

---

# 5. Product Element

## 5.1 Purpose

Represents version-independent product identity.

## 5.2 Logical key

`product_element_id`

## 5.3 Minimum attributes

- `product_element_id`
- `external_identifier`
- `name`
- `element_type`
- `source_class`
- `source_identifier`
- `extraction_timestamp`

## 5.4 Element type

Allowed baseline values:

- Product
- Assembly
- Component

These values are descriptive classifications only.

They do not determine structural behaviour.

## 5.5 Relationship

```text
Product Element 1
    HAS_VERSION
Product Version 1..*
```

A Product Version belongs to exactly one Product Element.

---

# 6. Product Version

## 6.1 Purpose

Represents one specific development state of a Product Element.

## 6.2 Logical key

`product_version_id`

## 6.3 Business uniqueness

Within one Product Element:

```text
(revision, iteration)
```

must be unique.

## 6.4 Minimum attributes

- `product_version_id`
- `product_element_id`
- `revision`
- `iteration`
- `lifecycle_state`
- `is_baselined`
- `supersedes_product_version_id` optional
- `source_class`
- `source_identifier`
- `extraction_timestamp`

## 6.5 Immutability

A Product Version referenced by an Assessment Baseline or Decision Record lineage is immutable.

A baselined Product Version is never updated in place.

## 6.6 Successor semantics

The executable baseline supports:

```text
Product Version
    SUPERSEDES
Product Version
```

This means development succession only.

It does not imply:

- interchangeability;
- physical replacement;
- service replacement;
- stock disposition.

---

# 7. Product Structure Occurrence

## 7.1 Purpose

Represents one identifiable usage of a child Product Version within a parent Product Version.

## 7.2 Logical key

`occurrence_id`

## 7.3 Minimum current-source attributes

- `occurrence_id`
- `parent_product_version_id`
- `child_product_version_id`
- `position`
- `quantity`
- `unit`
- `applicability_rule`
- `effectivity_specification`
- `source_class`
- `source_identifier`
- `extraction_timestamp`

## 7.4 Cardinalities

```text
Parent Product Version 1
    HAS_OCCURRENCE
Product Structure Occurrence 0..*

Product Structure Occurrence 1
    REFERENCES
Child Product Version 1
```

The same child Product Version may appear in multiple occurrences.

## 7.5 Historical rule

A current Product Structure Occurrence record may be mutable in the synthetic integration projection.

Historical analysis uses the immutable Baseline Member snapshot captured for that occurrence.

---

# 8. Configuration Context

## 8.1 Purpose

Represents the bounded configuration against which applicability is evaluated.

## 8.2 Minimum attributes

- `configuration_context_id`
- `name`
- `feature_values`
- `completeness_state`

Example:

```json
{
  "PackFamily": "LongRange",
  "CoolingType": "Liquid"
}
```

## 8.3 Completeness state

- Complete
- Partial
- Unknown

Historical evaluation uses the state captured in the Assessment Baseline snapshot.

---

# 9. Applicability Rule

## 9.1 Purpose

Defines where a Product Structure Occurrence applies.

## 9.2 Minimum logical content

- `rule_id`
- `expression`
- `rule_version`

Example:

```text
CoolingType = "Liquid"
AND
PackFamily = "LongRange"
```

## 9.3 Evaluation result

- Included
- Excluded
- Conditional
- Undetermined

## 9.4 Historical rule

When an Applicability Rule is baseline-relevant, its evaluated state is captured within a Baseline Member snapshot.

---

# 10. Effectivity Specification

## 10.1 Purpose

Defines when a Product Version or Product Structure Occurrence is intended to apply.

## 10.2 Executable scope

Only:

> **Planned Engineering Effective Date**

is executable.

## 10.3 Minimum logical content

- `effectivity_type`
- `planned_effective_date`

Historical effectivity state used by analysis is captured in the relevant Baseline Member snapshot.

---

# 11. Requirement

## 11.1 Purpose

Represents an engineering obligation relevant to the synthetic scenario.

## 11.2 Logical key

`requirement_id`

## 11.3 Minimum attributes

- `requirement_id`
- `requirement_revision`
- `text`
- `allocated_product_element_id`
- `source_class`
- `source_identifier`
- `extraction_timestamp`

## 11.4 Relationship

```text
Requirement
    ALLOCATED_TO
Product Element
```

Allocation does not assert compliance.

## 11.5 Historical rule

If a Requirement participates in an Assessment Baseline, its evaluated revision and content are preserved through Baseline Member snapshot data.

---

# 12. Change Case

## 12.1 Purpose

Represents the process-level container for a proposed product change.

## 12.2 Logical key

`change_case_id`

## 12.3 Minimum attributes

- `change_case_id`
- `title`
- `trigger`
- `rationale`
- `change_owner`
- `case_state`
- `process_iteration`
- `created_at`
- `closed_at` optional

## 12.4 Case states

- Draft
- Open
- In Assessment
- Decision Ready
- Withdrawn
- Closed by Decision

## 12.5 Logical containment

```text
Change Case 1
    CONTAINS
Change Item Identity 1..*
```

A Change Item Identity belongs to exactly one Change Case.

---

# 13. Change Item Identity and Revision

## 13.1 Change Item Identity

A Change Item has one stable logical identity:

```text
change_item_id
```

Example:

```text
CI-001
```

## 13.2 Change Item Revision

Each technical-content revision is separately persistent and immutable after overlay use.

Example:

```text
CI-001:r1
CI-001:r2
CI-001:r3
```

Logical structure:

```text
Change Case 1
    CONTAINS
Change Item Identity 1..*

Change Item Identity 1
    HAS_REVISION
Change Item Revision 1..*
```

A separate physical Change Item Identity table is optional.

Every:

```text
(change_item_id, change_item_revision)
```

is a separate persistent record.

## 13.3 Executable actions

- Revise Product State
- Change Applicability

No other action is executable.

## 13.4 Minimum immutable Change Item Revision attributes

- `change_item_id`
- `change_item_revision`
- `change_case_id`
- `action`
- `target_type`
- `target_id`
- `current_state_reference`
- `proposed_state_payload`
- `reason`
- `owner`
- `configuration_context_id`
- `intended_effectivity`
- `revision_created_at`

Proposal-selection and disposition state are intentionally excluded from immutable revision content.

## 13.5 Revision integrity

1. All revisions with the same `change_item_id` belong to the same Change Case.
2. Revision numbers are unique and strictly increasing.
3. A revision used by an Overlay Revision or Decision Record is immutable.
4. Historical revisions are never deleted or overwritten.

---

# 14. Change Item Proposal State

## 14.1 Purpose

Represents the current case-level proposal selection for one Change Item Identity.

It is separate from immutable Change Item Revision content.

## 14.2 Minimum attributes

- `change_item_id`
- `selected_revision`
- `proposal_state`
- `state_changed_at`
- `state_changed_by`

## 14.3 Allowed proposal states

- Active
- Removed from Proposal

## 14.4 Rules

1. At most one revision can be selected for one Change Item Identity at one time.
2. An Active proposal points to exactly one Change Item Revision.
3. `Removed from Proposal` means that the Change Item is no longer part of the active Proposed Change Scope.
4. Removal is not rejection and does not create a Decision Record.
5. Historical Overlay membership is unaffected by later Proposal State changes.
6. Terminal disposition of a revision is derived from Decision Scope and Decision Record, not stored as mutable revision state.

---

# 15. Action-Specific Target Integrity

Action-specific target integrity is evaluated in two phases because Gate A occurs before an Assessment Baseline is established or selected.

## 15.1 Gate A target identification

Gate A checks whether the proposed target is sufficiently identified for controlled initial distribution. It does **not** check membership in an Assessment Baseline.

### 15.1.1 Revise Product State

Required Gate A rules:

- `target_type = Product Version`;
- `target_id` resolves to an identifiable current Product Version;
- `current_state_reference` matches that identified Product Version.

### 15.1.2 Change Applicability

Required Gate A rules:

- `target_type = Product Structure Occurrence`;
- `target_id` resolves to an identifiable current Product Structure Occurrence;
- the predecessor Applicability Rule reference is supplied in `current_state_reference`.

A malformed Change Item Revision that fails these target-identification rules fails Gate A.

## 15.2 Overlay execution eligibility

After an Assessment Baseline has been established or selected, and before the proposed-state overlay is accepted for impact-analysis execution, baseline-relative target integrity is checked. This is not a new process gate or process stage.

### 15.2.1 Revise Product State

Required baseline-relative rules:

- the target Product Version is present as a Baseline Member in the selected Assessment Baseline;
- the captured baseline Product Version state matches `current_state_reference`;
- the proposed successor `(revision, iteration)` does not collide with:
  - an existing authoritative Product Version;
  - another proposed successor in the same Overlay Revision.

The proposed successor exists only in the overlay.

### 15.2.2 Change Applicability

Required baseline-relative rules:

- the target Product Structure Occurrence is present as a Baseline Member in the selected Assessment Baseline;
- the captured baseline occurrence state matches `current_state_reference`;
- the predecessor Applicability Rule matches the captured baseline occurrence state;
- the proposed Applicability Rule exists only in the overlay.

Failure of these baseline-relative rules prevents the Overlay Revision from becoming eligible for impact-analysis execution. It is not reclassified as a Gate A failure.

---

# 16. Assessment Baseline

## 16.1 Purpose

Represents an immutable captured current-state basis for analysis.

## 16.2 Logical key

`assessment_baseline_id`

## 16.3 Minimum attributes

- `assessment_baseline_id`
- `change_case_id`
- `snapshot_timestamp`
- `configuration_context_id`
- `effectivity_context`
- `rule_set_version`
- `created_at`

## 16.4 Historical-state rule

An Assessment Baseline is not a set of live pointers.

It consists of immutable Baseline Member snapshots.

---

# 17. Baseline Member

## 17.1 Purpose

Preserves the evaluated historical state of one baseline-relevant object.

## 17.2 Logical key

`baseline_member_id`

## 17.3 Minimum attributes

- `baseline_member_id`
- `assessment_baseline_id`
- `object_type`
- `object_id`
- `object_revision_or_state_token`
- `source_identifier`
- `snapshot_payload`

## 17.4 Snapshot rule

The `snapshot_payload` contains the state required by the prototype analysis.

Impact-analysis Execution reads this captured state, not later mutable source records.

## 17.5 Typical member types

- Product Version
- Product Structure Occurrence
- Requirement
- Evidence Record
- Configuration Context
- Applicability Rule
- Effectivity Specification

## 17.6 Cardinality

```text
Assessment Baseline 1
    CONTAINS
Baseline Member 1..*
```

## 17.7 Immutability

A Baseline Member is immutable after the Assessment Baseline is first used by an Impact-analysis Execution.

---

# 18. Baseline Reuse Rule

A new proposal does not automatically require a new baseline.

A baseline may be reused when:

- authoritative current-state records remain accepted;
- baseline scope remains sufficient;
- Configuration Context remains valid;
- Effectivity context remains valid;
- extraction basis remains accepted.

A new Assessment Baseline is required when one of these baseline-defining elements changes.

---

# 19. Overlay Revision

## 19.1 Purpose

Represents one immutable proposed-state delta set.

## 19.2 Logical key

`overlay_revision_id`

## 19.3 Minimum attributes

- `overlay_revision_id`
- `change_case_id`
- `created_at`

Its exact Change Item revision membership is represented through Overlay Change Item Membership.

---

# 20. Overlay Change Item Membership

## 20.1 Purpose

Identifies the exact Change Item revision set contained in one Overlay Revision.

## 20.2 Minimum attributes

- `overlay_revision_id`
- `change_item_id`
- `change_item_revision`

## 20.3 Cardinality

```text
Overlay Revision 1
    CONTAINS
Overlay Change Item Membership 1..*

Change Item Revision 1
    PARTICIPATES_IN
Overlay Change Item Membership 0..*
```

## 20.4 Integrity rules

1. An Overlay Revision contains at least one Change Item revision.
2. All included revisions belong to the same Change Case as the Overlay Revision.
3. An Overlay Revision contains at most one revision of each Change Item Identity.
4. Overlay membership becomes immutable once used by an Impact-analysis Execution.
5. At Overlay creation, each included revision must be the selected Active proposal revision.
6. Later Proposal State changes do not alter historical Overlay membership.
7. One Change Item Revision may participate in multiple Overlay Revisions.

---

# 21. Overlay-local Object

## 21.1 Purpose

Represents one hypothetical proposed-state object materialised by applying an Overlay Revision.

## 21.2 Identity scope

Overlay-local object identity is scoped to exactly one Overlay Revision.

Every Impact-analysis Execution using that Overlay Revision refers to the same overlay-local object identifiers.

## 21.3 Minimum attributes

- `overlay_revision_id`
- `overlay_local_object_id`
- `object_type`
- `source_change_item_id`
- `source_change_item_revision`
- `state_payload`

## 21.4 Uniqueness

```text
(overlay_revision_id, overlay_local_object_id)
```

is unique.

## 21.5 Semantics

Overlay-local objects are not authoritative enterprise identities.

They exist only as proposed-state representations inside the Overlay Revision.

---

# 22. Overlay Materialisation

## 22.1 Revise Product State

Example:

```text
CI-001:r1
action = Revise Product State
target = PV-A
```

materialises an Overlay-local Object:

```text
OVOBJ-PV-001
```

representing the hypothetical successor Product Version.

The authoritative Product Version remains unchanged.

## 22.2 Change Applicability

Example:

```text
CI-002:r1
action = Change Applicability
target = PSO-010
```

materialises:

```text
OVOBJ-PSO-010
```

with the proposed Applicability Rule state.

The authoritative occurrence remains unchanged.

---

# 23. Impact-analysis Execution

## 23.1 Purpose

Provides reproducible lineage for one execution of impact discovery and routing.

## 23.2 Logical key

`impact_execution_id`

## 23.3 Minimum attributes

- `impact_execution_id`
- `change_case_id`
- `assessment_baseline_id`
- `overlay_revision_id`
- `rule_set_version`
- `execution_timestamp`
- `execution_status`
- `routing_status`

## 23.4 Execution status

- Planned
- Running
- Completed
- Failed

## 23.5 Routing status

- Not Started
- Completed
- Failed

Routing status belongs to Impact-analysis Execution, not Assessment Obligation.

This gives deterministic meaning to zero Assessment Obligations.

## 23.6 Required lineage

```text
Impact-analysis Execution
    → Assessment Baseline
    → Overlay Revision
    → Overlay Change Item Membership
    → Change Item Revisions
    → Overlay-local Objects
    → Rule-set version
```

## 23.7 Case-local rule

The Assessment Baseline and Overlay Revision must belong to the same Change Case as the execution.

---

# 24. Impact Candidate

## 24.1 Purpose

Represents one potentially affected object or occurrence identified by an Impact-analysis Execution.

## 24.2 Logical key

`impact_candidate_id`

## 24.3 Minimum attributes

- `impact_candidate_id`
- `impact_execution_id`
- `candidate_type`
- `candidate_reference`
- `affected_domain`
- `candidate_state`

## 24.4 Candidate state

- New
- Assessment Planned
- Under Assessment
- Assessed
- Closed as Not Relevant

Source Change Items and dependency paths are represented through Impact Candidate Provenance.

---

# 25. Dependency Path Step

## 25.1 Purpose

Defines one ordered step in an Impact Candidate provenance path.

## 25.2 Minimum logical content

- `sequence`
- `source_reference`
- `relationship_type`
- `target_reference`
- `state_context`

## 25.3 State context

Allowed values:

- Current State
- Proposed State

## 25.4 Reference rules

For `Current State`:

- referenced objects must exist as Baseline Members.

For `Proposed State`:

- referenced proposed-state objects must belong to the Overlay Revision used by the candidate’s execution.

---

# 26. Impact Candidate Provenance

## 26.1 Purpose

Preserves one complete reason/path explaining why an Impact Candidate exists.

## 26.2 Minimum attributes

- `impact_candidate_provenance_id`
- `impact_candidate_id`
- `change_item_id`
- `change_item_revision`
- `dependency_path`

`dependency_path` is an ordered collection of Dependency Path Steps.

It is not free text.

## 26.3 Cardinality

```text
Impact Candidate 1
    HAS_PROVENANCE
Impact Candidate Provenance 1..*
```

## 26.4 Integrity rules

1. Every Impact Candidate has at least one provenance record.
2. Every referenced Change Item revision belongs to the Overlay Revision used by the candidate’s execution.
3. Every proposed-state object in a path belongs to the same Overlay Revision.
4. Every current-state object in a path exists as a Baseline Member.
5. Path sequence values are contiguous and strictly ordered.
6. Each path step target connects to the next path step source.
7. One provenance record represents exactly one path.
8. Multiple paths from one Change Item are permitted.
9. Multiple source Change Items for one Impact Candidate are permitted.
10. Candidate, provenance, execution, overlay, baseline, and Change Item revisions resolve to one Change Case.

---

# 27. Assessment Obligation

## 27.1 Purpose

Represents one required domain-assessment obligation produced by completed routing logic.

It exists before a fulfilling Assessment.

## 27.2 Logical key

`assessment_obligation_id`

## 27.3 Minimum attributes

- `assessment_obligation_id`
- `impact_execution_id`
- `impact_candidate_id` optional
- `domain`
- `requirement_id` optional
- `mandatory`
- `fulfilled_by_assessment_id` optional
- `routing_rule_reference`

`routing_completed` is not stored here.

## 27.4 Integrity rules

1. Every mandatory routing result creates one Assessment Obligation.
2. An Assessment Obligation exists only when the parent execution routing process has run.
3. A mandatory Assessment Obligation is satisfied only by a compatible Complete Assessment or a valid retained Assessment.
4. The Assessment must:
   - belong to the same Change Case;
   - match the required domain;
   - match the required Impact Candidate or Requirement where specified.
5. A retained historical Assessment can satisfy the obligation only when its Reuse Classification for the target execution is `Retained`.
6. Gate B fails if any mandatory Assessment Obligation remains unsatisfied.
7. Zero Assessment Obligations is meaningful only when:
   ```text
   impact_execution.routing_status = Completed
   ```

---

# 28. Assessment

## 28.1 Purpose

Represents one domain evaluation.

## 28.2 Logical key

`assessment_id`

## 28.3 Minimum attributes

- `assessment_id`
- `change_case_id`
- `origin_impact_execution_id`
- `domain`
- `assessment_state`
- `relevance`
- `disposition`
- `impact_statement`
- `assessor`
- `completed_at` optional
- `is_locked`

## 28.4 Assessment State

- Planned
- In Progress
- Submitted
- Returned
- Complete
- Withdrawn

## 28.5 Relevance

- Relevant
- Not Relevant
- Undetermined

## 28.6 Disposition

- No Objection
- No Objection with Conditions
- Objection
- Escalation Recommended

## 28.7 Immutability trigger

A Complete Assessment becomes locked and immutable when it:

- fulfils an Assessment Obligation;
- is classified as `Retained` for a later execution; or
- is referenced by a Decision Record through Decision Support Assessment.

Once locked:

```text
is_locked = true
```

and the Assessment content cannot be edited.

When an Assessment becomes locked, the Assessment and its complete semantic content are immutable. This includes:

- Assessment Impact Links;
- Assessment Requirement Conclusions;
- Assessment Evidence Uses as a complete set;
- Assessment Obligation fulfilment links.

No semantic child record can be added, removed, replaced, or altered after the Assessment is locked.

Any later evaluation requires a new Assessment.

---

# 29. Assessment Impact Link

## 29.1 Purpose

Connects an Assessment to the Impact Candidates it evaluates.

## 29.2 Minimum attributes

- `assessment_id`
- `impact_candidate_id`

## 29.3 Cardinality

```text
Assessment * ↔ * Impact Candidate
```

A Domain Assessment may evaluate several Impact Candidates.

One Impact Candidate may require Assessments from multiple domains.

---

# 30. Assessment Requirement Conclusion

## 30.1 Purpose

Stores one Requirement-specific conclusion reached by one Assessment.

## 30.2 Minimum attributes

- `assessment_requirement_conclusion_id`
- `assessment_id`
- `requirement_id`
- `conclusion`

## 30.3 Allowed conclusions

- Satisfied
- Not Satisfied
- Not Demonstrated
- Not Applicable

## 30.4 Integrity rules

1. Each conclusion references exactly one Assessment and one Requirement.
2. Only Assessment can own a Requirement Conclusion.
3. One Assessment may conclude on multiple Requirements.
4. One Assessment has at most one conclusion per Requirement.

---

# 31. Evidence Record

## 31.1 Purpose

Represents evidence that may be used by Assessments.

## 31.2 Logical key

`evidence_record_id`

## 31.3 Minimum attributes

- `evidence_record_id`
- `evidence_type`
- `reference`
- `applicable_product_version_id`
- `configuration_context_id`
- `requirement_id` optional
- `result`
- `issue_date`
- `validity_state`
- `provider`
- `superseded_by_evidence_id` optional
- `source_class`
- `source_identifier`
- `extraction_timestamp`

## 31.4 Validity state

- Current
- Superseded
- Expired
- Unknown

## 31.5 Requirement meaning

Evidence may address a Requirement.

It does not conclude Requirement satisfaction.

The live Evidence Record may evolve or be superseded.

Historical Evidence state used by an Assessment is preserved in Assessment Evidence Use.

---

# 32. Assessment Evidence Use

## 32.1 Purpose

Represents the contextual use of one Evidence Record by one Assessment and preserves the exact evidence state used.

## 32.2 Minimum attributes

- `assessment_evidence_use_id`
- `assessment_id`
- `evidence_record_id`
- `evaluated_product_version_reference`
- `transferability_conclusion` optional
- `evidence_state_token`
- `evidence_snapshot_payload`

## 32.3 Transferability conclusions

When Evidence directly applies to the evaluated Product Version:

```text
transferability_conclusion = null
```

When predecessor Evidence is used for a successor:

- Accepted as Applicable
- Partial Revalidation Required
- Not Applicable to Proposed State

## 32.4 Historical rule

`evidence_snapshot_payload` captures the Evidence state actually used by the Assessment.

Later changes to the live Evidence Record do not alter the historical Assessment basis.

## 32.5 Integrity rules

1. Evidence transferability is recorded per Assessment–Evidence relationship.
2. The evaluated Product Version reference resolves to:
   - a Baseline Member Product Version; or
   - an Overlay-local proposed Product Version;
   within the relevant execution lineage.
3. Evidence linked to a predecessor Product Version cannot support a successor Requirement Conclusion without explicit transferability semantics.
4. One Assessment may use the same Evidence Record once per evaluated Product Version in the baseline prototype.
5. Once the Assessment is locked, its Assessment Evidence Uses and evidence snapshots are immutable.

---

# 33. Assessment Reuse Classification

## 33.1 Purpose

Represents whether a historical Assessment can support a later Impact-analysis Execution.

## 33.2 Minimum attributes

- `assessment_reuse_classification_id`
- `assessment_id`
- `target_impact_execution_id`
- `classification`
- `rationale`

## 33.3 Allowed classifications

- Retained
- Revalidation Required
- Invalidated

## 33.4 Integrity rules

1. The Assessment originates from an earlier execution.
2. Origin and target executions belong to the same Change Case.
3. One Assessment has at most one reuse classification for one target execution.
4. `Retained` allows the historical Assessment to satisfy a compatible Assessment Obligation.
5. `Revalidation Required` does not satisfy a mandatory obligation.
6. `Invalidated` cannot satisfy Gate B.
7. Reuse classification never mutates the historical Assessment.
8. Classifying an Assessment as `Retained` locks the Assessment if it is not already locked.

---

# 34. Open Item

## 34.1 Purpose

Represents an unresolved pre-decision matter.

## 34.2 Allowed types

- Information Gap
- Data Defect
- Conflict
- Required Action

## 34.3 Minimum attributes

- `open_item_id`
- `change_case_id`
- `source_type`
- `source_id`
- `item_type`
- `description`
- `owner`
- `status`
- `blocking_class`
- `required_before_stage`
- `resolution_evidence_reference` optional
- `created_at`
- `closed_at` optional

## 34.4 Status

- Open
- In Resolution
- Resolved
- Cancelled

## 34.5 Blocking class

- Blocking
- Non-blocking

## 34.6 Required-before stage

- Initial Distribution
- Assessment Completion
- Decision

## 34.7 Decision blocker rule

An Open Item with:

```text
blocking_class = Blocking
required_before_stage = Decision
status != Resolved
```

prevents authorised terminal disposition.

---

# 35. Process-history Entry

## 35.1 Purpose

Represents auditable workflow history without turning routing into a business-domain object.

## 35.2 Allowed entry types

### Routing

- Returned for Information
- Scope Revision Required
- Additional Assessment Required
- Escalated
- Delegated
- Change Item Removed from Proposal

### Administrative closure

- Withdrawn by Change Owner

## 35.3 Minimum attributes

- `process_history_id`
- `change_case_id`
- `entry_type`
- `timestamp`
- `actor`
- `origin_stage`
- `target_stage_or_route`
- `reason`
- `affected_change_item_id` optional
- `affected_change_item_revision` optional

## 35.4 Change Item removal event

`Change Item Removed from Proposal` must identify:

- Change Item ID;
- exact selected revision;
- actor;
- reason;
- timestamp.

It changes Change Item Proposal State from:

```text
Active
```

to:

```text
Removed from Proposal
```

It does not:

- reject the Change Item;
- dispose the Change Item through authority;
- create a Decision Record.

## 35.5 Constraint

A Process-history Entry never disposes Change Items through authority.

---

# 36. Authority Level

Authority Level is a value, not a first-class entity.

Explicit ordering:

```text
Standard < Elevated
```

The decision route contains:

- `required_authority_level`
- `current_authority_level`
- `decision_permitted`
- `escalation_required`

Rule:

```text
required_authority_level > current_authority_level
→ escalation_required = true
→ no terminal Decision Record
```

The baseline does **not** implement an elevated-authority override of substantive objections or unmet mandatory Requirements.

---

# 37. Gate A — Ready for Initial Distribution

Gate A passes only if:

1. Change Case exists.
2. At least one Change Item Proposal State is `Active`.
3. Every Active proposal points to a valid immutable Change Item Revision.
4. Every executable Change Item Revision passes the action-specific **Gate A target-identification** rules in §15.1.
5. Rationale exists.
6. Required Configuration Context is present or explicitly Partial.
7. No unresolved blocking Open Item required before Initial Distribution exists.

Gate A does not require:

- an Assessment Baseline to exist;
- target membership in an Assessment Baseline;
- Impact Candidate discovery;
- domain assessment.

After Gate A, the Assessment Baseline is established or selected. The baseline-relative rules in §15.2 are then evaluated before the Overlay Revision is accepted for impact-analysis execution.

---

# 38. Routing Completion

Routing status belongs to Impact-analysis Execution.

Before Gate B can be evaluated:

```text
impact_execution.routing_status = Completed
```

must be true.

If:

```text
routing_status = Completed
```

and zero Assessment Obligations exist, then routing has deterministically concluded that no Assessments are required under the synthetic routing rules.

If routing has not completed, zero Assessment Obligations has no readiness meaning.

---

# 39. Gate B — Decision Package Complete

Gate B is a **package completeness** gate.

It does not determine whether authorisation is substantively permitted.

Gate B passes only when:

1. final Impact-analysis Execution status = Completed;
2. routing status = Completed;
3. exact Proposed Change Scope is known;
4. every mandatory Assessment Obligation is satisfied;
5. all mandatory Impact Candidates have required Assessment coverage;
6. all blocking Open Items required before Decision are Resolved;
7. required Evidence obligations represented through Assessment criteria are fulfilled;
8. required authority level is known.

A Complete Assessment can still contain:

- Objection;
- Escalation Recommended;
- Not Satisfied;
- Not Demonstrated.

Those states are handled by Authorisation Eligibility rules after Gate B.

---

# 40. Authorisation Eligibility

## 40.1 Purpose

Separates:

> **Decision Package Complete**

from:

> **Permitted to Authorise**

## 40.2 Standard baseline rule

For the baseline prototype, any mandatory Assessment with one or more of the following prevents authorisation:

### Assessment Disposition

- Objection
- Escalation Recommended

### Mandatory Requirement Conclusion

- Not Satisfied
- Not Demonstrated

These states cannot be bypassed through `Authorised with Conditions`.

## 40.3 Permitted next outcomes

When a blocking substantive Assessment result exists:

- Reject; or
- create an Escalation Process-history Entry where the route requires elevated authority or further authority handling.

The baseline prototype does not implement a rule permitting Elevated authority to override a:

- Not Satisfied mandatory Requirement;
- Not Demonstrated mandatory Requirement;
- unresolved Objection.

Such override semantics are outside scope.

---

# 41. Decision Record

## 41.1 Purpose

Represents one terminal authority disposition of an exact Decision Scope.

## 41.2 Allowed outcomes

- Authorised for Downstream Processing
- Authorised with Conditions
- Rejected

## 41.3 Minimum attributes

- `decision_record_id`
- `change_case_id`
- `assessment_baseline_id`
- `overlay_revision_id`
- `impact_execution_id`
- `required_authority_level`
- `current_authority_level`
- `outcome`
- `rationale`
- `decision_authority`
- `decision_timestamp`

## 41.4 Lineage constraints

The Decision Record references the same:

- Change Case;
- Assessment Baseline;
- Overlay Revision;
- Impact-analysis Execution;

used to establish the final Decision Package.

---

# 42. Decision Support Assessment

## 42.1 Purpose

Preserves the exact Assessments used by a terminal Decision Record.

## 42.2 Minimum attributes

- `decision_support_assessment_id`
- `decision_record_id`
- `assessment_id`

## 42.3 Cardinality

```text
Decision Record 1
    BASED_ON
Decision Support Assessment 1..*

Assessment 1
    SUPPORTS
Decision Support Assessment 0..*
```

## 42.4 Integrity rules

1. Every supporting Assessment belongs to the same Change Case as the Decision Record.
2. Every supporting Assessment is valid for the Decision Record’s Impact-analysis Execution through:
   - direct origin in that execution; or
   - `Retained` reuse classification for that execution.
3. Supporting Assessments are Complete and locked.
4. The Decision Record’s historical Evidence basis is reconstructed through those Assessments and their immutable Assessment Evidence Uses.
5. For every mandatory Assessment Obligation satisfied for the Decision Record’s Impact-analysis Execution, the satisfying Assessment must be included in the Decision Record’s Decision Support Assessment set.
6. A retained historical Assessment can satisfy this requirement only when its Assessment Reuse Classification for the Decision Record’s Impact-analysis Execution is `Retained`.
7. The Decision Support Assessment set must therefore provide complete coverage of all mandatory Assessment Obligations used to establish Gate B for that Decision Record.

---

# 43. Decision Scope Item

## 43.1 Purpose

Defines the exact Change Item revisions disposed by a Decision Record.

## 43.2 Minimum attributes

- `decision_record_id`
- `change_item_id`
- `change_item_revision`

## 43.3 Integrity rules

1. Decision Scope is non-empty.
2. Every Decision Scope Item references a Change Item revision present in the final Overlay Revision.
3. Every scope item belongs to the same Change Case as the Decision Record.
4. A Change Item revision can be disposed by at most one terminal Decision Record.
5. A later proposal requires another Change Item Revision.

---

# 44. Decision Condition

## 44.1 Purpose

Represents one post-authorisation obligation created by a terminal authorised Decision Record.

## 44.2 Minimum attributes

- `decision_condition_id`
- `decision_record_id`
- `text`
- `responsible_downstream_role`
- `required_before_stage`
- `expected_completion_evidence`

## 44.3 Allowed required-before stages

- Pre-implementation
- Pre-release
- Post-implementation monitoring

## 44.4 Integrity rules

1. Every Decision Condition belongs to exactly one Decision Record.
2. `Authorised with Conditions` requires one or more Decision Conditions.
3. `Authorised for Downstream Processing` requires zero Decision Conditions.
4. `Rejected` requires zero Decision Conditions.
5. A pre-authorisation obligation cannot be represented as a Decision Condition.

---

# 45. Terminal Decision Constraints

## 45.1 Authorised for Downstream Processing

Permitted only if:

- Gate B = Complete;
- authority sufficient;
- Authorisation Eligibility = Permitted;
- no unresolved Decision-blocking Open Item exists;
- zero Decision Conditions.

## 45.2 Authorised with Conditions

Permitted only if:

- Gate B = Complete;
- authority sufficient;
- Authorisation Eligibility = Permitted;
- no pre-authorisation blocking Open Item remains;
- one or more valid Decision Conditions exist.

`Authorised with Conditions` cannot bypass:

- Objection;
- Escalation Recommended;
- Not Satisfied mandatory Requirement;
- Not Demonstrated mandatory Requirement.

## 45.3 Rejected

Permitted only if:

- authority sufficient;
- rationale recorded;
- exact Decision Scope defined.

A rejected proposal may contain unresolved information because rejection does not authorise implementation.

---

# 46. Proposal Removal and Case Closure

## 46.1 Proposal removal

A Change Item proposal can move:

```text
Active
→ Removed from Proposal
```

through an auditable Process-history Entry.

This is:

- non-dispositive;
- non-authoritative;
- not equivalent to rejection.

## 46.2 Withdrawal

Withdrawal of the entire Change Case:

- creates `Withdrawn by Change Owner`;
- changes case state to `Withdrawn`;
- creates no Decision Record;
- preserves all historical records.

## 46.3 Closed by Decision

A Change Case can become:

```text
Closed by Decision
```

only when no Change Item Proposal State remains both:

- Active; and
- undisposed by a terminal Decision Record.

Equivalent rule:

Every currently selected Change Item revision must be either:

- disposed by a Decision Record; or
- Removed from Proposal through auditable history.

A partial terminal Decision cannot close a case containing unresolved Active proposal revisions.

---

# 47. Handover View

The Handover View is derived, not independently persisted.

For authorised outcomes it is generated from:

- Decision Record;
- Decision Scope Items;
- Change Item revisions;
- Decision Conditions;
- proposed applicability;
- planned engineering effectivity.

Minimum output:

- authorised Change Item revisions;
- excluded or non-disposed items where relevant;
- proposed product-state actions;
- applicability constraints;
- effectivity constraints;
- downstream conditions;
- expected completion evidence.

No Handover View is generated for:

- Rejected;
- Escalated;
- Scope Revision Required;
- Withdrawn.

---

# 48. Case-Local Referential Integrity

The following associations must resolve to one Change Case:

- Change Item Identity ↔ Change Item Revision;
- Change Item Proposal State ↔ selected Change Item Revision;
- Overlay Revision ↔ Change Item Revision;
- Overlay Revision ↔ Overlay-local Object;
- Impact-analysis Execution ↔ Assessment Baseline;
- Impact-analysis Execution ↔ Overlay Revision;
- Impact Candidate ↔ Impact-analysis Execution;
- Impact Candidate Provenance ↔ Change Item Revision;
- Assessment ↔ origin Impact-analysis Execution;
- Assessment Impact Link ↔ Impact Candidate;
- Assessment Obligation ↔ Impact-analysis Execution;
- Assessment Requirement Conclusion ↔ Assessment;
- Assessment Evidence Use ↔ Assessment;
- Assessment Reuse Classification ↔ target Impact-analysis Execution;
- Open Item ↔ case-bound source object;
- Decision Record ↔ Assessment Baseline;
- Decision Record ↔ Overlay Revision;
- Decision Record ↔ Impact-analysis Execution;
- Decision Support Assessment ↔ Assessment;
- Decision Scope Item ↔ Change Item Revision;
- Process-history Entry ↔ affected Change Item where applicable.

Any cross-case lineage join is invalid.

---

# 49. Cardinality Summary

```text
Product Element 1 ── 1..* Product Version

Product Version 1 ── 0..* Product Structure Occurrence [as parent]

Product Structure Occurrence * ── 1 Product Version [as child]

Change Case 1 ── 1..* Change Item Identity

Change Item Identity 1 ── 1..* Change Item Revision

Change Item Identity 1 ── 1 Change Item Proposal State

Change Case 1 ── 0..* Assessment Baseline

Assessment Baseline 1 ── 1..* Baseline Member

Change Case 1 ── 0..* Overlay Revision

Overlay Revision 1 ── 1..* Overlay Change Item Membership

Overlay Revision 1 ── 0..* Overlay-local Object

Change Item Revision 1 ── 0..* Overlay Change Item Membership

Assessment Baseline 1 ── 0..* Impact-analysis Execution

Overlay Revision 1 ── 0..* Impact-analysis Execution

Impact-analysis Execution 1 ── 0..* Impact Candidate

Impact Candidate 1 ── 1..* Impact Candidate Provenance

Impact-analysis Execution 1 ── 0..* Assessment Obligation

Assessment * ── * Impact Candidate

Assessment 1 ── 0..* Assessment Requirement Conclusion

Assessment * ── * Evidence Record [through Assessment Evidence Use]

Assessment 1 ── 0..* Assessment Reuse Classification

Impact-analysis Execution 1 ── 0..* Assessment Reuse Classification [as target]

Change Case 1 ── 0..* Open Item

Change Case 1 ── 0..* Process-history Entry

Change Case 1 ── 0..* Decision Record

Decision Record 1 ── 1..* Decision Support Assessment

Decision Record 1 ── 1..* Decision Scope Item

Decision Record 1 ── 0..* Decision Condition
```

---

# 50. Integrity Rules

## Change Item and proposal state

**IR-01**  
`(change_item_id, change_item_revision)` is unique.

**IR-02**  
All revisions of one Change Item Identity belong to one Change Case.

**IR-03**  
Revision numbers are strictly increasing.

**IR-04**  
A Change Item Revision used by an Overlay Revision or Decision Record is immutable.

**IR-05**  
Each Change Item Identity has exactly one Proposal State record.

**IR-06**  
An Active Proposal State references exactly one selected Change Item Revision.

**IR-07**  
Removed from Proposal is auditable and does not alter historical Overlay membership.

---

## Baseline and overlay

**IR-08**  
Assessment Baseline is immutable after first execution use.

**IR-09**  
Baseline Member snapshot is immutable after first execution use.

**IR-10**  
Overlay Revision contains at least one Change Item Revision.

**IR-11**  
Overlay Revision contains at most one revision per Change Item Identity.

**IR-12**  
Overlay membership is immutable after first execution use.

**IR-13**  
Overlay-local object identity is unique within one Overlay Revision:

```text
(overlay_revision_id, overlay_local_object_id)
```

**IR-14**  
Executions sharing one Overlay Revision use the same Overlay-local object identities.

---

## Execution and provenance

**IR-15**  
Impact-analysis Execution requires one baseline and one overlay from the same Change Case.

**IR-16**  
Impact Candidate requires one Impact-analysis Execution.

**IR-17**  
Every Impact Candidate has at least one provenance record.

**IR-18**  
Every provenance Change Item revision belongs to the execution’s Overlay Revision.

**IR-19**  
Every Current-State path reference exists as a Baseline Member.

**IR-20**  
Every Proposed-State path reference belongs to the execution’s Overlay Revision.

**IR-21**  
Dependency Path Steps are ordered, contiguous, and connected.

---

## Assessment and evidence

**IR-22**  
Routing status is stored on Impact-analysis Execution.

**IR-23**  
Gate B cannot be evaluated unless routing status = Completed.

**IR-24**  
Every mandatory routing result creates an Assessment Obligation.

**IR-25**  
A mandatory Assessment Obligation is satisfied only by:
- a compatible Complete Assessment from the target execution; or
- a historical Assessment classified Retained for the target execution.

**IR-26**  
Only Assessment owns Requirement Conclusions.

**IR-27**  
Assessment Evidence Use preserves the evidence state actually used.

**IR-28**  
Predecessor Evidence cannot support a successor Requirement Conclusion without explicit transferability semantics.

**IR-29**  
Assessment reuse is stored relative to the target execution.

**IR-30**  
A locked Assessment cannot be edited.

**IR-31**  
A Complete Assessment becomes locked when it fulfils an obligation, is retained, or supports a Decision Record.

---

## Decision readiness and authority

**IR-32**  
Gate B completeness does not imply Authorisation Eligibility.

**IR-33**  
A mandatory Assessment with `Objection` prevents authorised disposition.

**IR-34**  
A mandatory Assessment with `Escalation Recommended` prevents authorised disposition.

**IR-35**  
A mandatory Requirement Conclusion of `Not Satisfied` prevents authorised disposition.

**IR-36**  
A mandatory Requirement Conclusion of `Not Demonstrated` prevents authorised disposition.

**IR-37**  
`Authorised with Conditions` cannot override IR-33 through IR-36.

**IR-38**  
Authority ordering is:

```text
Standard < Elevated
```

**IR-39**  
If required authority exceeds current authority, no terminal Decision Record is created.

---

## Decision integrity

**IR-40**  
Decision Record cannot exist for:
- Escalated;
- Delegated;
- Returned for Information;
- Scope Revision Required;
- Additional Assessment Required;
- Change Item Removed from Proposal;
- Withdrawn.

**IR-41**  
Decision Scope is non-empty.

**IR-42**  
Decision Scope can include only Change Item revisions present in the final Overlay Revision.

**IR-43**  
Decision Record, baseline, overlay, execution, supporting Assessments, and scope all resolve to one Change Case.

**IR-44**  
Decision Record has at least one Decision Support Assessment.

**IR-45**  
Every supporting Assessment is Complete, locked, and valid for the Decision Record execution.

**IR-46**  
`Authorised with Conditions` requires at least one Decision Condition.

**IR-47**  
`Authorised for Downstream Processing` requires zero Decision Conditions.

**IR-48**  
`Rejected` requires zero Decision Conditions.

---

## Case closure

**IR-49**  
Withdrawal creates a Case Closure Process-history Entry and no Decision Record.

**IR-50**  
A Change Item can be removed from the Active proposal only through an auditable Proposal State transition.

**IR-51**  
A Case can become `Closed by Decision` only when no Active Proposal remains undisposed.

---

# 51. Scenario Mapping

## Scenario A — Decision Ready

```text
CHG-001
    ↓
CI-001:r1
Revise Product State
    ↓
Proposal State = Active
    ↓
BL-001
    ↓
Baseline Member snapshots
    ↓
OV-001
    ↓
Overlay Membership = CI-001:r1
    ↓
Overlay-local proposed successor
    ↓
IAX-001
execution = Completed
routing = Completed
    ↓
Impact Candidates
    ↓
Structured Provenance Paths
    ↓
Assessment Obligations
    ↓
Assessments
    ↓
Assessment Evidence Uses
    ↓
Requirement Conclusions
    ↓
Gate B = Complete
    ↓
Authorisation Eligibility = Permitted
    ↓
Standard authority sufficient
    ↓
DEC-001
Authorised for Downstream Processing
```

Decision Support Assessment links preserve the exact Assessments and Evidence snapshots used.

---

## Scenario B — Scope Amendment

Initial:

```text
BL-001
+
OV-001 [CI-001:r1]
→ IAX-001
```

Impact analysis identifies a Product Structure Occurrence whose applicability becomes relevant.

Structured provenance explains the dependency path.

Assessment concludes that applicability must itself change.

Process-history Entry:

```text
Scope Revision Required
```

Create:

```text
CI-002:r1
Change Applicability
```

Proposal State:

```text
CI-002 = Active
```

Create:

```text
OV-002
contains:
CI-001:r1
CI-002:r1
```

Baseline validity check:

```text
BL-001 remains valid
```

Execute:

```text
BL-001 + OV-002 → IAX-002
```

Historical Assessments from IAX-001 are classified relative to IAX-002:

- Retained
- Revalidation Required
- Invalidated

Assessment Obligations for IAX-002 determine what must still be fulfilled.

No historical Assessment or Evidence Use is overwritten.

---

## Scenario C — Authority Escalation

```text
IAX-003 = Completed
routing_status = Completed
mandatory Assessment Obligations = Satisfied
blocking Decision Open Items = Resolved
Gate B = Complete
Authorisation Eligibility = Permitted
required authority = Elevated
current authority = Standard
```

Result:

```text
Process-history Entry:
Escalated
```

No Decision Record is created.

The Change Case remains open.

---

# 52. Out-of-Scope Logical Semantics

The model intentionally does not define:

- product identity replacement;
- interchangeability;
- service replacement;
- stock disposition;
- production effectivity;
- plant-specific cut-in;
- Add Usage execution;
- Remove Usage execution;
- Change Usage execution;
- Change Effectivity execution;
- complete requirements hierarchy;
- formal risk model;
- enterprise approval hierarchy;
- elevated-authority override of objections;
- elevated-authority override of unmet mandatory Requirements;
- enterprise source precedence;
- source freshness thresholds;
- generic workflow engine;
- automated engineering approval;
- AI-generated product dependencies.

---

# 53. Final Blocker-Only Review Questions

The final review must assess only whether Scenarios A–C can be implemented deterministically.

Review only these categories:

1. Historical reconstruction
2. Identity and revision semantics
3. Overlay membership and overlay-local identity
4. Provenance
5. Readiness calculation
6. Decision integrity
7. Case closure

Specific questions:

1. Can every historical Decision reconstruct the exact locked Assessments and Evidence states supporting it?
2. Can immutable Change Item Revision content coexist without contradiction with mutable Proposal State?
3. Are Overlay-local proposed-state identities unambiguously scoped?
4. Can each Impact Candidate provenance path be structurally validated?
5. Can routing complete with zero obligations without ambiguity?
6. Can Gate B be calculated without inferring missing obligations from absent records?
7. Can a complete Decision Package still correctly block authorisation because of Objection, Escalation Recommended, Not Satisfied, or Not Demonstrated?
8. Can `Authorised with Conditions` never bypass mandatory technical blockers?
9. Can a Change Item be removed from proposal without being falsely rejected or disposed?
10. Can partial terminal decisions never close a Case with remaining Active proposal items?
11. Can every lineage relationship resolve to exactly one Change Case?
12. Can Scenarios A–C be implemented without inventing any additional PLM semantics?

Do not add:

- PLM capabilities;
- scenarios;
- object families;
- lifecycle concepts;
- process stages;
- enterprise-governance features.

Only implementation-blocking contradiction should prevent freeze.

---

# 54. Freeze Criteria

Logical Information Model v0.3 can be frozen if the final blocker-only review finds no implementation-blocking contradiction in:

- historical Decision reconstruction;
- immutable revision semantics;
- proposal-state transitions;
- Overlay-local identity;
- provenance path structure;
- routing completeness;
- Assessment Obligations;
- substantive authorisation eligibility;
- Decision support lineage;
- Case closure.

After freeze, the next artefacts are:

1. **Scenario Data Definition**
2. **Readiness and Routing Rules**
3. **Solution Architecture**
4. **Prototype Implementation Plan**

No additional PLM capability should be introduced unless implementation exposes an actual contradiction in the frozen model.
