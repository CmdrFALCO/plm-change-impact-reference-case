# Product Change Impact Assessment & Decision Readiness

## Scenario Data Definition v0.1

**Document type:** Scenario Data / Deterministic Test Oracle  
**Status:** Frozen implementation baseline  
**Domain:** Synthetic automotive Product Lifecycle Management  
**Version:** 0.1  
**Date:** 25 August 2026  
**Governing artefacts:**
- Business Architecture Definition v0.3.1 — Frozen Implementation Baseline
- Logical Information Model v0.3.2 — Frozen Implementation Baseline

---

## 1. Purpose

This document instantiates the frozen Business Architecture and frozen Logical Information Model with exact synthetic records for the three frozen scenarios:

- **Scenario A — Decision Ready**
- **Scenario B — Scope Amendment**
- **Scenario C — Authority Escalation**

It is the test oracle for the later prototype.

The governing rule is:

> **Given the exact input state defined here, the implementation must produce the exact expected state defined here.**

This document does not define a physical database schema, persistence technology, API, UI, workflow engine, or additional PLM capability.

---

## 2. Freeze Boundary

The following remain frozen and are not reopened by this document:

- capability scope;
- Business Architecture semantics;
- Logical Information Model entities and associations;
- executable Change Item actions;
- scenario intent;
- authority ordering;
- Gate A / Gate B separation;
- Decision Record semantics;
- Process-history semantics;
- Assessment locking;
- Evidence transferability;
- baseline reuse;
- exact Decision Scope and support lineage.

Only these Change Item actions are instantiated:

1. `Revise Product State`
2. `Change Applicability`

No new lifecycle state, object family, process stage, or enterprise PLM concept is introduced.

---

## 3. Oracle Conventions

### 3.1 Scenario independence

Scenarios A, B, and C are **independent test fixtures**. They reuse the same synthetic source product state but use separate Change Cases, baselines, overlays, executions, assessments, and decision/routing histories.

A terminal decision in Scenario A therefore has no effect on Scenario B or Scenario C.

### 3.2 Record classes

This document uses three labels:

- **INPUT** — record or value that exists before the relevant process step.
- **EXPECTED** — record that the prototype must create or state it must reach.
- **DERIVED** — calculation result or view that is not a separately persisted business object.

### 3.3 Null

`null` means that the logical attribute is deliberately empty.

### 3.4 Rule-set forward reference

The frozen Logical Information Model requires `rule_set_version` and `routing_rule_reference` values. This document reserves the following identifiers for the next artefact, **Readiness and Routing Rules v0.1**:

| Rule reference | Reserved meaning |
|---|---|
| `RRR-01` | Material-characteristic change → Product Engineering assessment |
| `RRR-02` | Material-characteristic change → Validation assessment |
| `RRR-03` | Material-characteristic change → Manufacturing assessment |
| `RRR-04` | Supplier-related trigger → Purchasing/Cost assessment |
| `RRR-05` | Assessed applicability mismatch requiring explicit scope amendment → Scope Revision Required |
| `RRR-06` | Synthetic authority classification requiring Elevated authority |

The rule-set version for all v0.1 scenarios is:

```text
RRR-v0.1
```

This document fixes the scenario references only. The executable rule logic is defined in the next artefact.

### 3.5 Source classes

Only the generic source classes already allowed by the frozen architecture are used:

- `Product Data Source`
- `Requirements Source`
- `Evidence Source`

No source precedence or enterprise authority hierarchy is implied.

### 3.6 Gate A and overlay execution eligibility

The frozen process order is preserved:

```text
Define Change Case and Change Items
↓
Gate A — Ready for Initial Distribution
↓
Establish / Select Assessment Baseline
↓
Create / validate Proposed-State Overlay
↓
Execute Impact Analysis
```

Gate A verifies **sufficient target identification for controlled initial distribution**. It does not depend on an Assessment Baseline.

For `Revise Product State`, Gate A requires:

- `target_type = Product Version`;
- `target_id` resolves to an identifiable current Product Version;
- `current_state_reference` matches that identified version.

For `Change Applicability`, Gate A requires:

- `target_type = Product Structure Occurrence`;
- `target_id` resolves to an identifiable current occurrence;
- the predecessor Applicability Rule reference is supplied in `current_state_reference`.

After an Assessment Baseline exists, **overlay execution eligibility** verifies the baseline-relative state before the Overlay Revision is accepted for impact-analysis execution:

- the target Product Version or Product Structure Occurrence is present as a Baseline Member;
- the captured baseline state matches `current_state_reference`;
- for `Change Applicability`, the predecessor Applicability Rule matches the captured occurrence state;
- for `Revise Product State`, the proposed successor identity does not collide with an authoritative Product Version or another proposed successor in the same Overlay Revision.

This split is a sequencing correction only. It does not add a process gate or change the Business Architecture process order.

---

# 4. Shared Synthetic Source Product State

The following source state is reused by all three independent scenarios.

## 4.1 Product Elements — INPUT

| product_element_id | external_identifier | name | element_type | source_class | source_identifier | extraction_timestamp |
|---|---|---|---|---|---|---|
| `PE-002` | `SYN-TMA-001` | Thermal Management Assembly | Assembly | Product Data Source | `PDS-PE-002` | `2026-08-25T18:00:00Z` |
| `PE-003` | `SYN-CP-001` | Cooling Plate | Component | Product Data Source | `PDS-PE-003` | `2026-08-25T18:00:00Z` |

## 4.2 Product Versions — INPUT

| product_version_id | product_element_id | revision | iteration | lifecycle_state | is_baselined | supersedes_product_version_id | source_class | source_identifier | extraction_timestamp |
|---|---|---:|---:|---|---|---|---|---|---|
| `PV-002` | `PE-002` | `A` | `1` | Current | true | null | Product Data Source | `PDS-PV-002-A1` | `2026-08-25T18:00:00Z` |
| `PV-003` | `PE-003` | `A` | `1` | Current | true | null | Product Data Source | `PDS-PV-003-A1` | `2026-08-25T18:00:00Z` |

The current technical state used by impact analysis is preserved in the Baseline Member snapshot rather than added as new Product Version entity semantics.

## 4.3 Configuration Context — INPUT

```yaml
configuration_context_id: CFG-001
name: LongRange Liquid Configuration
feature_values:
  PackFamily: LongRange
  CoolingType: Liquid
completeness_state: Complete
```

## 4.4 Applicability Rule — INPUT

```yaml
rule_id: APP-001
expression: 'CoolingType = "Liquid"'
rule_version: '1'
```

For `CFG-001`, the expected evaluation is:

```text
Included
```

## 4.5 Effectivity Specification — INPUT

Document fixture identifier: `EFF-001`

```yaml
effectivity_type: Planned Engineering Effective Date
planned_effective_date: '2026-11-01'
```

## 4.6 Product Structure Occurrence — INPUT

```yaml
occurrence_id: PSO-002
parent_product_version_id: PV-002
child_product_version_id: PV-003
position: '020'
quantity: 1
unit: EA
applicability_rule:
  rule_id: APP-001
  expression: 'CoolingType = "Liquid"'
  rule_version: '1'
effectivity_specification:
  effectivity_type: Planned Engineering Effective Date
  planned_effective_date: '2026-11-01'
source_class: Product Data Source
source_identifier: PDS-PSO-002
extraction_timestamp: '2026-08-25T18:00:00Z'
```

## 4.7 Requirements — INPUT

| requirement_id | requirement_revision | text | allocated_product_element_id | source_class | source_identifier | extraction_timestamp |
|---|---|---|---|---|---|---|
| `REQ-001` | `1` | Cooling Plate functional behaviour shall remain acceptable within the declared synthetic configuration scope. | `PE-003` | Requirements Source | `REQSRC-001` | `2026-08-25T18:05:00Z` |
| `REQ-002` | `1` | Validation evidence used for a proposed Cooling Plate state shall be demonstrated as applicable to the evaluated state. | `PE-003` | Requirements Source | `REQSRC-002` | `2026-08-25T18:05:00Z` |
| `REQ-003` | `1` | The proposed Cooling Plate state shall remain compatible with the declared synthetic manufacturing route. | `PE-003` | Requirements Source | `REQSRC-003` | `2026-08-25T18:05:00Z` |
| `REQ-004` | `1` | Cooling Plate occurrence applicability shall not include configurations outside the validated scope of the selected Cooling Plate product state. | `PE-002` | Requirements Source | `REQSRC-004` | `2026-08-25T18:05:00Z` |

## 4.8 Evidence Records — INPUT

| evidence_record_id | evidence_type | reference | applicable_product_version_id | configuration_context_id | requirement_id | result | issue_date | validity_state | provider | superseded_by_evidence_id | source_class | source_identifier | extraction_timestamp |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `EV-001` | Validation Result | `SYN-VAL-A-001` | `PV-003` | `CFG-001` | `REQ-002` | Current state meets the defined synthetic validation criterion. | `2026-08-15` | Current | Synthetic Validation Function | null | Evidence Source | `EVSRC-001` | `2026-08-25T18:10:00Z` |
| `EV-002` | Manufacturing Review | `SYN-MFG-A-001` | `PV-003` | `CFG-001` | `REQ-003` | Current state is compatible with the defined synthetic manufacturing route. | `2026-08-16` | Current | Synthetic Manufacturing Function | null | Evidence Source | `EVSRC-002` | `2026-08-25T18:10:00Z` |
| `EV-003` | Engineering Review | `SYN-ENG-A-001` | `PV-003` | `CFG-001` | `REQ-001` | Current functional interfaces are acceptable in the defined synthetic configuration. | `2026-08-17` | Current | Synthetic Product Engineering Function | null | Evidence Source | `EVSRC-003` | `2026-08-25T18:10:00Z` |
| `EV-004` | Supplier/Cost Review | `SYN-COST-A-001` | `PV-003` | `CFG-001` | null | Supplier-origin change has a documented non-blocking synthetic cost impact. | `2026-08-18` | Current | Synthetic Purchasing/Cost Function | null | Evidence Source | `EVSRC-004` | `2026-08-25T18:10:00Z` |

---

# 5. Canonical Baseline Snapshot Payloads

Each scenario uses a separate Assessment Baseline but captures the same authoritative current-state content. The following payload definitions are normative aliases used by the Baseline Member tables.

## 5.1 `SNAP-PV-002`

```yaml
product_version_id: PV-002
product_element_id: PE-002
revision: A
iteration: '1'
lifecycle_state: Current
```

## 5.2 `SNAP-PV-003`

```yaml
product_version_id: PV-003
product_element_id: PE-003
revision: A
iteration: '1'
lifecycle_state: Current
material_characteristic: MC-BASE-01
validated_configuration_scope: 'CoolingType = "Liquid"'
```

## 5.3 `SNAP-PSO-002`

```yaml
occurrence_id: PSO-002
parent_product_version_id: PV-002
child_product_version_id: PV-003
position: '020'
quantity: 1
unit: EA
applicability_rule:
  rule_id: APP-001
  expression: 'CoolingType = "Liquid"'
  rule_version: '1'
effectivity_specification:
  effectivity_type: Planned Engineering Effective Date
  planned_effective_date: '2026-11-01'
```

## 5.4 `SNAP-CFG-001`

```yaml
configuration_context_id: CFG-001
name: LongRange Liquid Configuration
feature_values:
  PackFamily: LongRange
  CoolingType: Liquid
completeness_state: Complete
```

## 5.5 `SNAP-APP-001`

```yaml
rule_id: APP-001
expression: 'CoolingType = "Liquid"'
rule_version: '1'
evaluation_in_CFG-001: Included
```

## 5.6 `SNAP-EFF-001`

```yaml
effectivity_type: Planned Engineering Effective Date
planned_effective_date: '2026-11-01'
```

## 5.7 Requirement snapshots

`SNAP-REQ-001` through `SNAP-REQ-004` equal the complete logical Requirement content in §4.7 for the corresponding Requirement revision.

## 5.8 Evidence snapshot convention

When an Assessment Evidence Use references an Evidence Record, `evidence_snapshot_payload` equals the complete logical Evidence Record content in §4.8 at the stated `evidence_state_token`.

---

# 6. Scenario A — Decision Ready

## 6.1 Scenario intent

A synthetic supplier process change requires one Cooling Plate material characteristic to change while intended product function and configuration scope remain unchanged.

Expected terminal outcome:

> **Authorised for Downstream Processing**

## 6.2 Change Case — INPUT

```yaml
change_case_id: CHG-A01
title: Cooling Plate supplier-process material characteristic update
trigger: Synthetic supplier process change
rationale: Update one Cooling Plate material characteristic while preserving intended function and current applicability.
change_owner: Change Owner A
case_state: Open
process_iteration: 1
created_at: '2026-08-25T19:00:00Z'
closed_at: null
```

## 6.3 Change Item Revision — INPUT

```yaml
change_item_id: CI-A01
change_item_revision: r1
change_case_id: CHG-A01
action: Revise Product State
target_type: Product Version
target_id: PV-003
current_state_reference:
  product_version_id: PV-003
  revision: A
  iteration: '1'
proposed_state_payload:
  product_element_id: PE-003
  proposed_revision: B
  proposed_iteration: '1'
  supersedes_product_version_id: PV-003
  material_characteristic: MC-A-01
  validated_configuration_scope: 'CoolingType = "Liquid"'
  intended_function_change: false
reason: Synthetic supplier process change.
owner: Change Owner A
configuration_context_id: CFG-001
intended_effectivity:
  effectivity_type: Planned Engineering Effective Date
  planned_effective_date: '2026-11-01'
revision_created_at: '2026-08-25T19:02:00Z'
```

### Proposal State — INPUT

```yaml
change_item_id: CI-A01
selected_revision: r1
proposal_state: Active
state_changed_at: '2026-08-25T19:03:00Z'
state_changed_by: Change Owner A
```

### Gate A — DERIVED EXPECTED

```yaml
gate_a: Pass
target_identification:
  action: Revise Product State
  target_type_valid: true
  target_resolves_to_current_object: true
  current_state_reference_matches_identified_target: true
baseline_membership_evaluated_at_gate_a: false
```

## 6.4 Assessment Baseline — INPUT

```yaml
assessment_baseline_id: BL-A01
change_case_id: CHG-A01
snapshot_timestamp: '2026-08-25T19:10:00Z'
configuration_context_id: CFG-001
effectivity_context:
  effectivity_type: Planned Engineering Effective Date
  planned_effective_date: '2026-11-01'
rule_set_version: RRR-v0.1
created_at: '2026-08-25T19:10:00Z'
```

### Baseline Members — INPUT

| baseline_member_id | assessment_baseline_id | object_type | object_id | object_revision_or_state_token | source_identifier | snapshot_payload |
|---|---|---|---|---|---|---|
| `BM-A01-01` | `BL-A01` | Product Version | `PV-002` | `A.1` | `PDS-PV-002-A1` | `SNAP-PV-002` |
| `BM-A01-02` | `BL-A01` | Product Version | `PV-003` | `A.1` | `PDS-PV-003-A1` | `SNAP-PV-003` |
| `BM-A01-03` | `BL-A01` | Product Structure Occurrence | `PSO-002` | `PSO-002@2026-08-25T18:00:00Z` | `PDS-PSO-002` | `SNAP-PSO-002` |
| `BM-A01-04` | `BL-A01` | Configuration Context | `CFG-001` | `Complete@2026-08-25` | `CFG-001` | `SNAP-CFG-001` |
| `BM-A01-05` | `BL-A01` | Applicability Rule | `APP-001` | `v1` | `APP-001` | `SNAP-APP-001` |
| `BM-A01-06` | `BL-A01` | Effectivity Specification | `EFF-001` | `2026-11-01` | `EFF-001` | `SNAP-EFF-001` |
| `BM-A01-07` | `BL-A01` | Requirement | `REQ-001` | `r1` | `REQSRC-001` | `SNAP-REQ-001` |
| `BM-A01-08` | `BL-A01` | Requirement | `REQ-002` | `r1` | `REQSRC-002` | `SNAP-REQ-002` |
| `BM-A01-09` | `BL-A01` | Requirement | `REQ-003` | `r1` | `REQSRC-003` | `SNAP-REQ-003` |
| `BM-A01-10` | `BL-A01` | Requirement | `REQ-004` | `r1` | `REQSRC-004` | `SNAP-REQ-004` |

### Overlay Execution Eligibility — DERIVED EXPECTED

```yaml
overlay_execution_eligibility: Pass
assessment_baseline_id: BL-A01
checks:
  target_product_version_present_in_baseline: true
  captured_state_matches_current_state_reference: true
  proposed_successor_identity_collision: false
```

## 6.5 Overlay Revision — EXPECTED

```yaml
overlay_revision_id: OV-A01
change_case_id: CHG-A01
created_at: '2026-08-25T19:20:00Z'
```

### Overlay Change Item Membership — EXPECTED

```yaml
overlay_revision_id: OV-A01
change_item_id: CI-A01
change_item_revision: r1
```

### Overlay-local Object — EXPECTED

```yaml
overlay_revision_id: OV-A01
overlay_local_object_id: OVOBJ-A01-PV
object_type: Product Version
source_change_item_id: CI-A01
source_change_item_revision: r1
state_payload:
  product_element_id: PE-003
  proposed_revision: B
  proposed_iteration: '1'
  supersedes_product_version_id: PV-003
  material_characteristic: MC-A-01
  validated_configuration_scope: 'CoolingType = "Liquid"'
  intended_function_change: false
```

## 6.6 Impact-analysis Execution — EXPECTED

```yaml
impact_execution_id: IAX-A01
change_case_id: CHG-A01
assessment_baseline_id: BL-A01
overlay_revision_id: OV-A01
rule_set_version: RRR-v0.1
execution_timestamp: '2026-08-25T19:25:00Z'
execution_status: Completed
routing_status: Completed
```

## 6.7 Impact Candidates — EXPECTED

| impact_candidate_id | impact_execution_id | candidate_type | candidate_reference | affected_domain | candidate_state |
|---|---|---|---|---|---|
| `IC-A01` | `IAX-A01` | Product Structure Occurrence | `PSO-002` | Product Engineering | Assessed |
| `IC-A02` | `IAX-A01` | Product Version | `PV-003` | Validation | Assessed |
| `IC-A03` | `IAX-A01` | Product Structure Occurrence | `PSO-002` | Manufacturing | Assessed |
| `IC-A04` | `IAX-A01` | Product Version | `PV-003` | Purchasing/Cost | Assessed |

## 6.8 Impact Candidate Provenance — EXPECTED

Each candidate has one provenance path caused by `CI-A01:r1`.

For `ICP-A01`, `ICP-A03`:

```yaml
dependency_path:
  - sequence: 1
    source_reference: BM-A01-02
    relationship_type: REFERENCED_BY_OCCURRENCE
    target_reference: BM-A01-03
    state_context: Current State
  - sequence: 2
    source_reference: BM-A01-03
    relationship_type: OCCURS_IN_PARENT
    target_reference: BM-A01-01
    state_context: Current State
```

For `ICP-A02`, `ICP-A04`:

```yaml
dependency_path:
  - sequence: 1
    source_reference: BM-A01-02
    relationship_type: REFERENCED_BY_OCCURRENCE
    target_reference: BM-A01-03
    state_context: Current State
```

| provenance_id | impact_candidate_id | change_item_id | revision | path |
|---|---|---|---|---|
| `ICP-A01` | `IC-A01` | `CI-A01` | `r1` | two-step path above |
| `ICP-A02` | `IC-A02` | `CI-A01` | `r1` | one-step path above |
| `ICP-A03` | `IC-A03` | `CI-A01` | `r1` | two-step path above |
| `ICP-A04` | `IC-A04` | `CI-A01` | `r1` | one-step path above |

## 6.9 Assessment Obligations — EXPECTED

| assessment_obligation_id | impact_execution_id | impact_candidate_id | domain | requirement_id | mandatory | fulfilled_by_assessment_id | routing_rule_reference |
|---|---|---|---|---|---|---|---|
| `AO-A01` | `IAX-A01` | `IC-A01` | Product Engineering | `REQ-001` | true | `ASM-A01` | `RRR-01` |
| `AO-A02` | `IAX-A01` | `IC-A02` | Validation | `REQ-002` | true | `ASM-A02` | `RRR-02` |
| `AO-A03` | `IAX-A01` | `IC-A03` | Manufacturing | `REQ-003` | true | `ASM-A03` | `RRR-03` |
| `AO-A04` | `IAX-A01` | `IC-A04` | Purchasing/Cost | null | true | `ASM-A04` | `RRR-04` |

## 6.10 Assessments — EXPECTED

| assessment_id | change_case_id | origin_execution | domain | state | relevance | disposition | assessor | completed_at | is_locked |
|---|---|---|---|---|---|---|---|---|---|
| `ASM-A01` | `CHG-A01` | `IAX-A01` | Product Engineering | Complete | Relevant | No Objection | Product Engineer A | `2026-08-25T19:40:00Z` | true |
| `ASM-A02` | `CHG-A01` | `IAX-A01` | Validation | Complete | Relevant | No Objection | Validation Engineer A | `2026-08-25T19:42:00Z` | true |
| `ASM-A03` | `CHG-A01` | `IAX-A01` | Manufacturing | Complete | Relevant | No Objection | Manufacturing Engineer A | `2026-08-25T19:44:00Z` | true |
| `ASM-A04` | `CHG-A01` | `IAX-A01` | Purchasing/Cost | Complete | Relevant | No Objection | Purchasing/Cost Assessor A | `2026-08-25T19:46:00Z` | true |

Impact statements:

- `ASM-A01`: Proposed material characteristic changes, but intended function and declared configuration scope remain unchanged.
- `ASM-A02`: Predecessor validation evidence is accepted as applicable to the proposed successor for this bounded synthetic change.
- `ASM-A03`: Predecessor manufacturing evidence is accepted as applicable to the proposed successor for this bounded synthetic change.
- `ASM-A04`: Supplier/cost impact is documented and non-blocking.

### Assessment Impact Links — EXPECTED

| assessment_id | impact_candidate_id |
|---|---|
| `ASM-A01` | `IC-A01` |
| `ASM-A02` | `IC-A02` |
| `ASM-A03` | `IC-A03` |
| `ASM-A04` | `IC-A04` |

### Requirement Conclusions — EXPECTED

| assessment_requirement_conclusion_id | assessment_id | requirement_id | conclusion |
|---|---|---|---|
| `ARC-A01` | `ASM-A01` | `REQ-001` | Satisfied |
| `ARC-A02` | `ASM-A02` | `REQ-002` | Satisfied |
| `ARC-A03` | `ASM-A03` | `REQ-003` | Satisfied |

### Assessment Evidence Uses — EXPECTED

| assessment_evidence_use_id | assessment_id | evidence_record_id | evaluated_product_version_reference | transferability_conclusion | evidence_state_token | evidence_snapshot_payload |
|---|---|---|---|---|---|---|
| `AEU-A01` | `ASM-A01` | `EV-003` | `OVOBJ-A01-PV` | Accepted as Applicable | `EV-003@2026-08-25T18:10:00Z` | exact `EV-003` logical state from §4.8 |
| `AEU-A02` | `ASM-A02` | `EV-001` | `OVOBJ-A01-PV` | Accepted as Applicable | `EV-001@2026-08-25T18:10:00Z` | exact `EV-001` logical state from §4.8 |
| `AEU-A03` | `ASM-A03` | `EV-002` | `OVOBJ-A01-PV` | Accepted as Applicable | `EV-002@2026-08-25T18:10:00Z` | exact `EV-002` logical state from §4.8 |
| `AEU-A04` | `ASM-A04` | `EV-004` | `OVOBJ-A01-PV` | Accepted as Applicable | `EV-004@2026-08-25T18:10:00Z` | exact `EV-004` logical state from §4.8 |

No Assessment Reuse Classification exists in Scenario A.

## 6.11 Open Items — EXPECTED

```text
none
```

## 6.12 Readiness and authority — DERIVED EXPECTED

```yaml
gate_a: Pass
impact_execution_status: Completed
routing_status: Completed
mandatory_assessment_obligations_satisfied: true
blocking_decision_open_items_resolved: true
gate_b: Complete
authorisation_eligibility: Permitted
required_authority_level: Standard
current_authority_level: Standard
decision_permitted: true
escalation_required: false
```

## 6.13 Decision Record — EXPECTED

```yaml
decision_record_id: DEC-A01
change_case_id: CHG-A01
assessment_baseline_id: BL-A01
overlay_revision_id: OV-A01
impact_execution_id: IAX-A01
required_authority_level: Standard
current_authority_level: Standard
outcome: Authorised for Downstream Processing
rationale: Decision package is complete, substantive authorisation blockers are absent, and Standard authority is sufficient.
decision_authority: Standard Decision Authority A
decision_timestamp: '2026-08-25T20:00:00Z'
```

### Decision Support Assessments — EXPECTED

| decision_support_assessment_id | decision_record_id | assessment_id |
|---|---|---|
| `DSA-A01` | `DEC-A01` | `ASM-A01` |
| `DSA-A02` | `DEC-A01` | `ASM-A02` |
| `DSA-A03` | `DEC-A01` | `ASM-A03` |
| `DSA-A04` | `DEC-A01` | `ASM-A04` |

### Decision Scope Items — EXPECTED

| decision_record_id | change_item_id | change_item_revision |
|---|---|---|
| `DEC-A01` | `CI-A01` | `r1` |

### Decision Conditions — EXPECTED

```text
none
```

## 6.14 Final case state — EXPECTED

```yaml
change_case_id: CHG-A01
case_state: Closed by Decision
closed_at: '2026-08-25T20:00:00Z'
```

The Proposal State for `CI-A01` remains `Active`; the selected revision is disposed by `DEC-A01`, therefore no Active undisposed proposal remains.

## 6.15 Handover View — DERIVED EXPECTED

A Handover View exists because the outcome is authorised.

Minimum content:

```yaml
authorised_change_items:
  - CI-A01:r1
proposed_product_state_action: Revise Product State
proposed_product_state_reference: OVOBJ-A01-PV
applicability_constraint: 'CoolingType = "Liquid"'
planned_engineering_effective_date: '2026-11-01'
decision_conditions: []
```

## 6.16 Scenario A oracle assertions

1. Gate A passes before `BL-A01` is established, using target-identification checks only.
2. Overlay execution eligibility passes after `BL-A01` exists.
3. `PV-003` remains unchanged.
4. `OVOBJ-A01-PV` exists only in `OV-A01`.
5. Every `IC-A*` has at least one structured provenance path.
6. Every mandatory `AO-A*` is satisfied by a compatible Complete locked Assessment.
7. Predecessor Evidence use for the successor has explicit transferability semantics.
8. Gate B is Complete.
9. Authorisation Eligibility is Permitted.
10. Standard authority is sufficient.
11. `DEC-A01` exists.
12. `DEC-A01` has four Decision Support Assessments and one Decision Scope Item.
13. `DEC-A01` has zero Decision Conditions.
14. `CHG-A01` is `Closed by Decision`.

---

# 7. Scenario B — Scope Amendment

## 7.1 Scenario intent

The initial proposed Cooling Plate product-state revision has a narrower validated configuration scope than the current occurrence applicability. Impact assessment identifies that the occurrence applicability must itself change.

Expected routing outcome after the first execution:

> **Scope Revision Required**

A second Change Item is then added:

> **Change Applicability**

A new Overlay Revision and new Impact-analysis Execution are required. The existing Assessment Baseline is reused because its defining current-state basis remains unchanged.

## 7.2 Change Case — INPUT

```yaml
change_case_id: CHG-B01
title: Cooling Plate material revision requiring applicability scope amendment
trigger: Synthetic supplier process change
rationale: Evaluate a proposed Cooling Plate material characteristic whose validated configuration scope is narrower than the current occurrence applicability.
change_owner: Change Owner B
case_state: Open
process_iteration: 1
created_at: '2026-08-25T20:10:00Z'
closed_at: null
```

## 7.3 Initial Change Item Revision — INPUT

```yaml
change_item_id: CI-B01
change_item_revision: r1
change_case_id: CHG-B01
action: Revise Product State
target_type: Product Version
target_id: PV-003
current_state_reference:
  product_version_id: PV-003
  revision: A
  iteration: '1'
proposed_state_payload:
  product_element_id: PE-003
  proposed_revision: B
  proposed_iteration: '1'
  supersedes_product_version_id: PV-003
  material_characteristic: MC-B-01
  validated_configuration_scope: 'CoolingType = "Liquid" AND PackFamily = "LongRange"'
  intended_function_change: false
reason: Synthetic supplier process change with a narrower validated configuration scope.
owner: Change Owner B
configuration_context_id: CFG-001
intended_effectivity:
  effectivity_type: Planned Engineering Effective Date
  planned_effective_date: '2026-11-01'
revision_created_at: '2026-08-25T20:12:00Z'
```

### Initial Proposal State — INPUT

```yaml
change_item_id: CI-B01
selected_revision: r1
proposal_state: Active
state_changed_at: '2026-08-25T20:13:00Z'
state_changed_by: Change Owner B
```

### Initial Gate A — DERIVED EXPECTED

```yaml
gate_a: Pass
target_identification:
  action: Revise Product State
  target_type_valid: true
  target_resolves_to_current_object: true
  current_state_reference_matches_identified_target: true
baseline_membership_evaluated_at_gate_a: false
```

## 7.4 Assessment Baseline — INPUT

```yaml
assessment_baseline_id: BL-B01
change_case_id: CHG-B01
snapshot_timestamp: '2026-08-25T20:20:00Z'
configuration_context_id: CFG-001
effectivity_context:
  effectivity_type: Planned Engineering Effective Date
  planned_effective_date: '2026-11-01'
rule_set_version: RRR-v0.1
created_at: '2026-08-25T20:20:00Z'
```

### Baseline Members — INPUT

| baseline_member_id | assessment_baseline_id | object_type | object_id | object_revision_or_state_token | source_identifier | snapshot_payload |
|---|---|---|---|---|---|---|
| `BM-B01-01` | `BL-B01` | Product Version | `PV-002` | `A.1` | `PDS-PV-002-A1` | `SNAP-PV-002` |
| `BM-B01-02` | `BL-B01` | Product Version | `PV-003` | `A.1` | `PDS-PV-003-A1` | `SNAP-PV-003` |
| `BM-B01-03` | `BL-B01` | Product Structure Occurrence | `PSO-002` | `PSO-002@2026-08-25T18:00:00Z` | `PDS-PSO-002` | `SNAP-PSO-002` |
| `BM-B01-04` | `BL-B01` | Configuration Context | `CFG-001` | `Complete@2026-08-25` | `CFG-001` | `SNAP-CFG-001` |
| `BM-B01-05` | `BL-B01` | Applicability Rule | `APP-001` | `v1` | `APP-001` | `SNAP-APP-001` |
| `BM-B01-06` | `BL-B01` | Effectivity Specification | `EFF-001` | `2026-11-01` | `EFF-001` | `SNAP-EFF-001` |
| `BM-B01-07` | `BL-B01` | Requirement | `REQ-001` | `r1` | `REQSRC-001` | `SNAP-REQ-001` |
| `BM-B01-08` | `BL-B01` | Requirement | `REQ-002` | `r1` | `REQSRC-002` | `SNAP-REQ-002` |
| `BM-B01-09` | `BL-B01` | Requirement | `REQ-003` | `r1` | `REQSRC-003` | `SNAP-REQ-003` |
| `BM-B01-10` | `BL-B01` | Requirement | `REQ-004` | `r1` | `REQSRC-004` | `SNAP-REQ-004` |

### Initial Overlay Execution Eligibility — DERIVED EXPECTED

```yaml
overlay_execution_eligibility: Pass
assessment_baseline_id: BL-B01
checks:
  target_product_version_present_in_baseline: true
  captured_state_matches_current_state_reference: true
  proposed_successor_identity_collision: false
```

## 7.5 First Overlay Revision — EXPECTED

```yaml
overlay_revision_id: OV-B01
change_case_id: CHG-B01
created_at: '2026-08-25T20:30:00Z'
```

Membership:

```yaml
- overlay_revision_id: OV-B01
  change_item_id: CI-B01
  change_item_revision: r1
```

Overlay-local Product Version:

```yaml
overlay_revision_id: OV-B01
overlay_local_object_id: OVOBJ-B01-PV
object_type: Product Version
source_change_item_id: CI-B01
source_change_item_revision: r1
state_payload:
  product_element_id: PE-003
  proposed_revision: B
  proposed_iteration: '1'
  supersedes_product_version_id: PV-003
  material_characteristic: MC-B-01
  validated_configuration_scope: 'CoolingType = "Liquid" AND PackFamily = "LongRange"'
  intended_function_change: false
```

## 7.6 First Impact-analysis Execution — EXPECTED

```yaml
impact_execution_id: IAX-B01
change_case_id: CHG-B01
assessment_baseline_id: BL-B01
overlay_revision_id: OV-B01
rule_set_version: RRR-v0.1
execution_timestamp: '2026-08-25T20:35:00Z'
execution_status: Completed
routing_status: Completed
```

## 7.7 First-execution Impact Candidates — EXPECTED

| impact_candidate_id | impact_execution_id | candidate_type | candidate_reference | affected_domain | candidate_state |
|---|---|---|---|---|---|
| `IC-B01` | `IAX-B01` | Product Structure Occurrence | `PSO-002` | Product Engineering | Assessed |
| `IC-B02` | `IAX-B01` | Product Version | `PV-003` | Validation | Assessed |
| `IC-B03` | `IAX-B01` | Product Structure Occurrence | `PSO-002` | Manufacturing | Assessed |
| `IC-B04` | `IAX-B01` | Product Version | `PV-003` | Purchasing/Cost | Assessed |

## 7.8 First-execution Provenance — EXPECTED

Each candidate has one provenance record caused by `CI-B01:r1`.

`ICP-B01` and `ICP-B03` use:

```yaml
dependency_path:
  - sequence: 1
    source_reference: BM-B01-02
    relationship_type: REFERENCED_BY_OCCURRENCE
    target_reference: BM-B01-03
    state_context: Current State
  - sequence: 2
    source_reference: BM-B01-03
    relationship_type: OCCURS_IN_PARENT
    target_reference: BM-B01-01
    state_context: Current State
```

`ICP-B02` and `ICP-B04` use:

```yaml
dependency_path:
  - sequence: 1
    source_reference: BM-B01-02
    relationship_type: REFERENCED_BY_OCCURRENCE
    target_reference: BM-B01-03
    state_context: Current State
```

## 7.9 First-execution Assessment Obligations — EXPECTED

| assessment_obligation_id | impact_execution_id | impact_candidate_id | domain | requirement_id | mandatory | fulfilled_by_assessment_id | routing_rule_reference |
|---|---|---|---|---|---|---|---|
| `AO-B01` | `IAX-B01` | `IC-B01` | Product Engineering | `REQ-004` | true | `ASM-B01` | `RRR-01` |
| `AO-B02` | `IAX-B01` | `IC-B02` | Validation | `REQ-002` | true | `ASM-B02` | `RRR-02` |
| `AO-B03` | `IAX-B01` | `IC-B03` | Manufacturing | `REQ-003` | true | `ASM-B03` | `RRR-03` |
| `AO-B04` | `IAX-B01` | `IC-B04` | Purchasing/Cost | null | true | `ASM-B04` | `RRR-04` |

## 7.10 First-execution Assessments — EXPECTED

| assessment_id | change_case_id | origin_execution | domain | state | relevance | disposition | assessor | completed_at | is_locked |
|---|---|---|---|---|---|---|---|---|---|
| `ASM-B01` | `CHG-B01` | `IAX-B01` | Product Engineering | Complete | Relevant | No Objection with Conditions | Product Engineer B | `2026-08-25T20:50:00Z` | true |
| `ASM-B02` | `CHG-B01` | `IAX-B01` | Validation | Complete | Relevant | No Objection | Validation Engineer B | `2026-08-25T20:52:00Z` | true |
| `ASM-B03` | `CHG-B01` | `IAX-B01` | Manufacturing | Complete | Relevant | No Objection | Manufacturing Engineer B | `2026-08-25T20:54:00Z` | true |
| `ASM-B04` | `CHG-B01` | `IAX-B01` | Purchasing/Cost | Complete | Relevant | No Objection | Purchasing/Cost Assessor B | `2026-08-25T20:56:00Z` | true |

Impact statements:

- `ASM-B01`: The proposed state is validated only for `CoolingType = "Liquid" AND PackFamily = "LongRange"`, while `PSO-002` currently applies to all `CoolingType = "Liquid"` configurations. The occurrence applicability must therefore be changed explicitly before the proposal can proceed to terminal decision.
- `ASM-B02`: Validation evidence is acceptable for the bounded technical state evaluated in the first execution.
- `ASM-B03`: Manufacturing evidence is acceptable for the bounded technical state evaluated in the first execution.
- `ASM-B04`: Supplier/cost impact remains documented and non-blocking.

### Assessment Impact Links — EXPECTED

| assessment_id | impact_candidate_id |
|---|---|
| `ASM-B01` | `IC-B01` |
| `ASM-B02` | `IC-B02` |
| `ASM-B03` | `IC-B03` |
| `ASM-B04` | `IC-B04` |

### Requirement Conclusions — EXPECTED

| conclusion_id | assessment_id | requirement_id | conclusion |
|---|---|---|---|
| `ARC-B01` | `ASM-B01` | `REQ-004` | Not Satisfied |
| `ARC-B02` | `ASM-B02` | `REQ-002` | Satisfied |
| `ARC-B03` | `ASM-B03` | `REQ-003` | Satisfied |

### Assessment Evidence Uses — EXPECTED

| use_id | assessment_id | evidence_record_id | evaluated_product_version_reference | transferability_conclusion | evidence_state_token |
|---|---|---|---|---|---|
| `AEU-B01` | `ASM-B01` | `EV-003` | `OVOBJ-B01-PV` | Accepted as Applicable | `EV-003@2026-08-25T18:10:00Z` |
| `AEU-B02` | `ASM-B02` | `EV-001` | `OVOBJ-B01-PV` | Accepted as Applicable | `EV-001@2026-08-25T18:10:00Z` |
| `AEU-B03` | `ASM-B03` | `EV-002` | `OVOBJ-B01-PV` | Accepted as Applicable | `EV-002@2026-08-25T18:10:00Z` |
| `AEU-B04` | `ASM-B04` | `EV-004` | `OVOBJ-B01-PV` | Accepted as Applicable | `EV-004@2026-08-25T18:10:00Z` |

Each `evidence_snapshot_payload` is the exact Evidence Record state defined in §4.8.

## 7.11 Scope Revision Process-history Entry — EXPECTED

```yaml
process_history_id: HIST-B01
change_case_id: CHG-B01
entry_type: Scope Revision Required
timestamp: '2026-08-25T21:00:00Z'
actor: Change Owner B
origin_stage: Domain Assessment
target_stage_or_route: Scope Confirmation
reason: ASM-B01 concluded that PSO-002 applicability must change explicitly; discovered impact is not authorised scope.
affected_change_item_id: CI-B01
affected_change_item_revision: r1
```

No Decision Record exists for `IAX-B01`.

## 7.12 Second Change Item Revision — INPUT AFTER ROUTING

```yaml
change_item_id: CI-B02
change_item_revision: r1
change_case_id: CHG-B01
action: Change Applicability
target_type: Product Structure Occurrence
target_id: PSO-002
current_state_reference:
  occurrence_id: PSO-002
  applicability_rule_id: APP-001
  applicability_rule_version: '1'
proposed_state_payload:
  applicability_rule:
    rule_id: APP-B02
    expression: 'CoolingType = "Liquid" AND PackFamily = "LongRange"'
    rule_version: '1'
reason: Align occurrence applicability with the validated scope of the proposed Cooling Plate state.
owner: Change Owner B
configuration_context_id: CFG-001
intended_effectivity:
  effectivity_type: Planned Engineering Effective Date
  planned_effective_date: '2026-11-01'
revision_created_at: '2026-08-25T21:05:00Z'
```

### Proposal State for CI-B02 — INPUT AFTER ROUTING

```yaml
change_item_id: CI-B02
selected_revision: r1
proposal_state: Active
state_changed_at: '2026-08-25T21:06:00Z'
state_changed_by: Change Owner B
```

`CI-B01` remains Active at `r1`.

### Gate A after Scope Amendment — DERIVED EXPECTED

```yaml
gate_a: Pass
active_change_items:
  - CI-B01:r1
  - CI-B02:r1
target_identification:
  CI-B01:r1:
    action: Revise Product State
    target_type_valid: true
    target_resolves_to_current_object: true
    current_state_reference_matches_identified_target: true
  CI-B02:r1:
    action: Change Applicability
    target_type_valid: true
    target_resolves_to_current_object: true
    predecessor_applicability_reference_supplied: true
baseline_membership_evaluated_at_gate_a: false
```

## 7.13 Baseline Validity Check — DERIVED EXPECTED

```yaml
assessment_baseline_id: BL-B01
authoritative_current_state_unchanged: true
baseline_scope_still_sufficient: true
configuration_context_still_valid: true
effectivity_context_still_valid: true
extraction_basis_still_accepted: true
baseline_reuse_permitted: true
```

No new Assessment Baseline is created.

### Overlay Execution Eligibility for Revised Scope — DERIVED EXPECTED

```yaml
overlay_execution_eligibility: Pass
assessment_baseline_id: BL-B01
checks:
  CI-B01:r1:
    target_product_version_present_in_baseline: true
    captured_state_matches_current_state_reference: true
    proposed_successor_identity_collision: false
  CI-B02:r1:
    target_occurrence_present_in_baseline: true
    captured_state_matches_current_state_reference: true
    predecessor_applicability_matches_captured_occurrence: true
```

## 7.14 Second Overlay Revision — EXPECTED

```yaml
overlay_revision_id: OV-B02
change_case_id: CHG-B01
created_at: '2026-08-25T21:10:00Z'
```

### Overlay Change Item Membership — EXPECTED

```yaml
- overlay_revision_id: OV-B02
  change_item_id: CI-B01
  change_item_revision: r1
- overlay_revision_id: OV-B02
  change_item_id: CI-B02
  change_item_revision: r1
```

### Overlay-local proposed Product Version — EXPECTED

```yaml
overlay_revision_id: OV-B02
overlay_local_object_id: OVOBJ-B02-PV
object_type: Product Version
source_change_item_id: CI-B01
source_change_item_revision: r1
state_payload:
  product_element_id: PE-003
  proposed_revision: B
  proposed_iteration: '1'
  supersedes_product_version_id: PV-003
  material_characteristic: MC-B-01
  validated_configuration_scope: 'CoolingType = "Liquid" AND PackFamily = "LongRange"'
  intended_function_change: false
```

### Overlay-local proposed Product Structure Occurrence — EXPECTED

```yaml
overlay_revision_id: OV-B02
overlay_local_object_id: OVOBJ-B02-PSO
object_type: Product Structure Occurrence
source_change_item_id: CI-B02
source_change_item_revision: r1
state_payload:
  occurrence_id: PSO-002
  parent_product_version_id: PV-002
  child_product_version_reference: OVOBJ-B02-PV
  position: '020'
  quantity: 1
  unit: EA
  applicability_rule:
    rule_id: APP-B02
    expression: 'CoolingType = "Liquid" AND PackFamily = "LongRange"'
    rule_version: '1'
  effectivity_specification:
    effectivity_type: Planned Engineering Effective Date
    planned_effective_date: '2026-11-01'
```

## 7.15 Second Impact-analysis Execution — EXPECTED

```yaml
impact_execution_id: IAX-B02
change_case_id: CHG-B01
assessment_baseline_id: BL-B01
overlay_revision_id: OV-B02
rule_set_version: RRR-v0.1
execution_timestamp: '2026-08-25T21:15:00Z'
execution_status: Completed
routing_status: Completed
```

## 7.16 Second-execution Impact Candidates — EXPECTED

| impact_candidate_id | impact_execution_id | candidate_type | candidate_reference | affected_domain | candidate_state |
|---|---|---|---|---|---|
| `IC-B21` | `IAX-B02` | Product Structure Occurrence | `OVOBJ-B02-PSO` | Product Engineering | Assessment Planned |
| `IC-B22` | `IAX-B02` | Product Structure Occurrence | `OVOBJ-B02-PSO` | Manufacturing | Assessment Planned |

### Provenance for both candidates — EXPECTED

Each candidate has one provenance record from `CI-B02:r1` with the proposed-state path:

```yaml
dependency_path:
  - sequence: 1
    source_reference: OVOBJ-B02-PV
    relationship_type: REFERENCED_BY_OCCURRENCE
    target_reference: OVOBJ-B02-PSO
    state_context: Proposed State
```

Provenance IDs:

- `ICP-B21` → `IC-B21`
- `ICP-B22` → `IC-B22`

## 7.17 Assessment Reuse Classifications — EXPECTED

| reuse_id | assessment_id | target_execution | classification | rationale |
|---|---|---|---|---|
| `ARU-B01` | `ASM-B01` | `IAX-B02` | Invalidated | The original Product Engineering assessment concluded that applicability was not aligned; the new overlay changes that exact applicability state and requires a new assessment. |
| `ARU-B02` | `ASM-B02` | `IAX-B02` | Retained | The bounded validation conclusion remains applicable to the unchanged proposed Product Version technical state; the added applicability Change Item does not alter the validated characteristic itself. |
| `ARU-B03` | `ASM-B03` | `IAX-B02` | Revalidation Required | Manufacturing assessment must confirm that the narrowed applicability does not alter the declared manufacturing applicability assumptions. |
| `ARU-B04` | `ASM-B04` | `IAX-B02` | Retained | Supplier/cost conclusion is unchanged by the added occurrence-applicability Change Item. |

No historical Assessment, Assessment Impact Link, Requirement Conclusion, or Assessment Evidence Use is changed.

## 7.18 Second-execution Assessment Obligations — EXPECTED

| obligation_id | impact_execution_id | impact_candidate_id | domain | requirement_id | mandatory | fulfilled_by_assessment_id | routing_rule_reference |
|---|---|---|---|---|---|---|---|
| `AO-B21` | `IAX-B02` | `IC-B21` | Product Engineering | `REQ-004` | true | null | `RRR-01` |
| `AO-B22` | `IAX-B02` | `IC-B22` | Manufacturing | `REQ-003` | true | null | `RRR-03` |
| `AO-B23` | `IAX-B02` | null | Validation | `REQ-002` | true | `ASM-B02` | `RRR-02` |
| `AO-B24` | `IAX-B02` | null | Purchasing/Cost | null | true | `ASM-B04` | `RRR-04` |

`ASM-B02` and `ASM-B04` satisfy `AO-B23` and `AO-B24` only because their reuse classifications for `IAX-B02` are `Retained`.

## 7.19 Readiness after second execution — DERIVED EXPECTED

```yaml
gate_a: Pass
impact_execution_status: Completed
routing_status: Completed
mandatory_assessment_obligations_satisfied: false
unsatisfied_mandatory_obligations:
  - AO-B21
  - AO-B22
gate_b: Incomplete
authorisation_eligibility: Not Evaluated
terminal_decision_record: none
case_state: In Assessment
```

No Handover View exists.

## 7.20 Scenario B oracle assertions

1. Initial Gate A passes for `CI-B01:r1` before `BL-B01` is established, using target-identification checks only.
2. Initial overlay execution eligibility passes after `BL-B01` exists.
3. After scope amendment, Gate A passes for both active Change Items without depending on baseline membership.
4. Overlay execution eligibility for `OV-B02` passes against reused baseline `BL-B01`, including predecessor Applicability Rule matching for `CI-B02:r1`.
5. `BL-B01` is reused; no second baseline is created.
6. `OV-B01` remains immutable and continues to contain only `CI-B01:r1`.
7. `OV-B02` contains exactly `CI-B01:r1` and `CI-B02:r1`.
8. `CI-B02:r1` is created only after the `Scope Revision Required` Process-history Entry.
9. `OVOBJ-B02-PSO` is scoped only to `OV-B02`.
10. `IAX-B02` references `BL-B01` and `OV-B02`.
11. Historical Assessments receive execution-relative reuse classifications.
12. At least one historical Assessment is `Retained`, one is `Revalidation Required`, and one is `Invalidated`.
13. Retained Assessments can satisfy compatible obligations in `IAX-B02` without being copied or modified.
14. `AO-B21` and `AO-B22` remain unsatisfied.
15. Gate B is Incomplete after `IAX-B02` at the defined v0.1 stop point.
16. No Decision Record exists.
17. `CHG-B01` remains open in state `In Assessment`.

---

# 8. Scenario C — Authority Escalation

## 8.1 Scenario intent

The Decision Package is complete and substantively eligible, but the synthetic decision route requires Elevated authority while the current authority is Standard.

Expected routing outcome:

> **Escalated**

No Decision Record is created.

## 8.2 Change Case — INPUT

```yaml
change_case_id: CHG-C01
title: Cooling Plate change requiring Elevated authority
trigger: Synthetic supplier process change with elevated authority classification
rationale: Evaluate a bounded Cooling Plate product-state revision whose decision route requires Elevated authority.
change_owner: Change Owner C
case_state: Open
process_iteration: 1
created_at: '2026-08-25T21:30:00Z'
closed_at: null
```

## 8.3 Change Item Revision — INPUT

```yaml
change_item_id: CI-C01
change_item_revision: r1
change_case_id: CHG-C01
action: Revise Product State
target_type: Product Version
target_id: PV-003
current_state_reference:
  product_version_id: PV-003
  revision: A
  iteration: '1'
proposed_state_payload:
  product_element_id: PE-003
  proposed_revision: B
  proposed_iteration: '1'
  supersedes_product_version_id: PV-003
  material_characteristic: MC-C-01
  validated_configuration_scope: 'CoolingType = "Liquid"'
  intended_function_change: false
reason: Synthetic change prepared under a route that requires Elevated authority.
owner: Change Owner C
configuration_context_id: CFG-001
intended_effectivity:
  effectivity_type: Planned Engineering Effective Date
  planned_effective_date: '2026-11-01'
revision_created_at: '2026-08-25T21:32:00Z'
```

### Proposal State — INPUT

```yaml
change_item_id: CI-C01
selected_revision: r1
proposal_state: Active
state_changed_at: '2026-08-25T21:33:00Z'
state_changed_by: Change Owner C
```

### Gate A — DERIVED EXPECTED

```yaml
gate_a: Pass
target_identification:
  action: Revise Product State
  target_type_valid: true
  target_resolves_to_current_object: true
  current_state_reference_matches_identified_target: true
baseline_membership_evaluated_at_gate_a: false
```

## 8.4 Assessment Baseline — INPUT

```yaml
assessment_baseline_id: BL-C01
change_case_id: CHG-C01
snapshot_timestamp: '2026-08-25T21:40:00Z'
configuration_context_id: CFG-001
effectivity_context:
  effectivity_type: Planned Engineering Effective Date
  planned_effective_date: '2026-11-01'
rule_set_version: RRR-v0.1
created_at: '2026-08-25T21:40:00Z'
```

### Baseline Members — INPUT

| baseline_member_id | assessment_baseline_id | object_type | object_id | object_revision_or_state_token | source_identifier | snapshot_payload |
|---|---|---|---|---|---|---|
| `BM-C01-01` | `BL-C01` | Product Version | `PV-002` | `A.1` | `PDS-PV-002-A1` | `SNAP-PV-002` |
| `BM-C01-02` | `BL-C01` | Product Version | `PV-003` | `A.1` | `PDS-PV-003-A1` | `SNAP-PV-003` |
| `BM-C01-03` | `BL-C01` | Product Structure Occurrence | `PSO-002` | `PSO-002@2026-08-25T18:00:00Z` | `PDS-PSO-002` | `SNAP-PSO-002` |
| `BM-C01-04` | `BL-C01` | Configuration Context | `CFG-001` | `Complete@2026-08-25` | `CFG-001` | `SNAP-CFG-001` |
| `BM-C01-05` | `BL-C01` | Applicability Rule | `APP-001` | `v1` | `APP-001` | `SNAP-APP-001` |
| `BM-C01-06` | `BL-C01` | Effectivity Specification | `EFF-001` | `2026-11-01` | `EFF-001` | `SNAP-EFF-001` |
| `BM-C01-07` | `BL-C01` | Requirement | `REQ-001` | `r1` | `REQSRC-001` | `SNAP-REQ-001` |
| `BM-C01-08` | `BL-C01` | Requirement | `REQ-002` | `r1` | `REQSRC-002` | `SNAP-REQ-002` |
| `BM-C01-09` | `BL-C01` | Requirement | `REQ-003` | `r1` | `REQSRC-003` | `SNAP-REQ-003` |
| `BM-C01-10` | `BL-C01` | Requirement | `REQ-004` | `r1` | `REQSRC-004` | `SNAP-REQ-004` |

### Overlay Execution Eligibility — DERIVED EXPECTED

```yaml
overlay_execution_eligibility: Pass
assessment_baseline_id: BL-C01
checks:
  target_product_version_present_in_baseline: true
  captured_state_matches_current_state_reference: true
  proposed_successor_identity_collision: false
```

## 8.5 Overlay Revision — EXPECTED

```yaml
overlay_revision_id: OV-C01
change_case_id: CHG-C01
created_at: '2026-08-25T21:50:00Z'
```

Membership:

```yaml
overlay_revision_id: OV-C01
change_item_id: CI-C01
change_item_revision: r1
```

Overlay-local Product Version:

```yaml
overlay_revision_id: OV-C01
overlay_local_object_id: OVOBJ-C01-PV
object_type: Product Version
source_change_item_id: CI-C01
source_change_item_revision: r1
state_payload:
  product_element_id: PE-003
  proposed_revision: B
  proposed_iteration: '1'
  supersedes_product_version_id: PV-003
  material_characteristic: MC-C-01
  validated_configuration_scope: 'CoolingType = "Liquid"'
  intended_function_change: false
```

## 8.6 Impact-analysis Execution — EXPECTED

```yaml
impact_execution_id: IAX-C01
change_case_id: CHG-C01
assessment_baseline_id: BL-C01
overlay_revision_id: OV-C01
rule_set_version: RRR-v0.1
execution_timestamp: '2026-08-25T21:55:00Z'
execution_status: Completed
routing_status: Completed
```

## 8.7 Impact Candidates — EXPECTED

| impact_candidate_id | impact_execution_id | candidate_type | candidate_reference | affected_domain | candidate_state |
|---|---|---|---|---|---|
| `IC-C01` | `IAX-C01` | Product Structure Occurrence | `PSO-002` | Product Engineering | Assessed |
| `IC-C02` | `IAX-C01` | Product Version | `PV-003` | Validation | Assessed |
| `IC-C03` | `IAX-C01` | Product Structure Occurrence | `PSO-002` | Manufacturing | Assessed |
| `IC-C04` | `IAX-C01` | Product Version | `PV-003` | Purchasing/Cost | Assessed |

All have structured provenance caused by `CI-C01:r1`, using the same current-state path structure as Scenario A with the `BM-C01-*` identifiers.

Provenance IDs:

- `ICP-C01`
- `ICP-C02`
- `ICP-C03`
- `ICP-C04`

## 8.8 Assessment Obligations — EXPECTED

| obligation_id | impact_execution_id | impact_candidate_id | domain | requirement_id | mandatory | fulfilled_by_assessment_id | routing_rule_reference |
|---|---|---|---|---|---|---|---|
| `AO-C01` | `IAX-C01` | `IC-C01` | Product Engineering | `REQ-001` | true | `ASM-C01` | `RRR-01` |
| `AO-C02` | `IAX-C01` | `IC-C02` | Validation | `REQ-002` | true | `ASM-C02` | `RRR-02` |
| `AO-C03` | `IAX-C01` | `IC-C03` | Manufacturing | `REQ-003` | true | `ASM-C03` | `RRR-03` |
| `AO-C04` | `IAX-C01` | `IC-C04` | Purchasing/Cost | null | true | `ASM-C04` | `RRR-04` |

## 8.9 Assessments — EXPECTED

| assessment_id | change_case_id | origin_execution | domain | state | relevance | disposition | assessor | completed_at | is_locked |
|---|---|---|---|---|---|---|---|---|---|
| `ASM-C01` | `CHG-C01` | `IAX-C01` | Product Engineering | Complete | Relevant | No Objection | Product Engineer C | `2026-08-25T22:10:00Z` | true |
| `ASM-C02` | `CHG-C01` | `IAX-C01` | Validation | Complete | Relevant | No Objection | Validation Engineer C | `2026-08-25T22:12:00Z` | true |
| `ASM-C03` | `CHG-C01` | `IAX-C01` | Manufacturing | Complete | Relevant | No Objection | Manufacturing Engineer C | `2026-08-25T22:14:00Z` | true |
| `ASM-C04` | `CHG-C01` | `IAX-C01` | Purchasing/Cost | Complete | Relevant | No Objection | Purchasing/Cost Assessor C | `2026-08-25T22:16:00Z` | true |

### Assessment Impact Links — EXPECTED

| assessment_id | impact_candidate_id |
|---|---|
| `ASM-C01` | `IC-C01` |
| `ASM-C02` | `IC-C02` |
| `ASM-C03` | `IC-C03` |
| `ASM-C04` | `IC-C04` |

### Requirement Conclusions — EXPECTED

| conclusion_id | assessment_id | requirement_id | conclusion |
|---|---|---|---|
| `ARC-C01` | `ASM-C01` | `REQ-001` | Satisfied |
| `ARC-C02` | `ASM-C02` | `REQ-002` | Satisfied |
| `ARC-C03` | `ASM-C03` | `REQ-003` | Satisfied |

### Assessment Evidence Uses — EXPECTED

| use_id | assessment_id | evidence_record_id | evaluated_product_version_reference | transferability_conclusion | evidence_state_token |
|---|---|---|---|---|---|
| `AEU-C01` | `ASM-C01` | `EV-003` | `OVOBJ-C01-PV` | Accepted as Applicable | `EV-003@2026-08-25T18:10:00Z` |
| `AEU-C02` | `ASM-C02` | `EV-001` | `OVOBJ-C01-PV` | Accepted as Applicable | `EV-001@2026-08-25T18:10:00Z` |
| `AEU-C03` | `ASM-C03` | `EV-002` | `OVOBJ-C01-PV` | Accepted as Applicable | `EV-002@2026-08-25T18:10:00Z` |
| `AEU-C04` | `ASM-C04` | `EV-004` | `OVOBJ-C01-PV` | Accepted as Applicable | `EV-004@2026-08-25T18:10:00Z` |

Each Evidence snapshot equals the exact logical Evidence state in §4.8.

## 8.10 Open Items — EXPECTED

```text
none
```

## 8.11 Readiness and authority — DERIVED EXPECTED

The authority values are decision-route values, not first-class business entities.

```yaml
gate_a: Pass
impact_execution_status: Completed
routing_status: Completed
mandatory_assessment_obligations_satisfied: true
blocking_decision_open_items_resolved: true
gate_b: Complete
authorisation_eligibility: Permitted
required_authority_level: Elevated
current_authority_level: Standard
decision_permitted: false
escalation_required: true
authority_rule_reference: RRR-06
```

## 8.12 Escalation Process-history Entry — EXPECTED

```yaml
process_history_id: HIST-C01
change_case_id: CHG-C01
entry_type: Escalated
timestamp: '2026-08-25T22:20:00Z'
actor: Decision Coordinator C
origin_stage: Authority Check
target_stage_or_route: Elevated Authority Route
reason: Required authority is Elevated while current authority is Standard.
affected_change_item_id: CI-C01
affected_change_item_revision: r1
```

## 8.13 Decision Record — EXPECTED

```text
none
```

## 8.14 Final case state — EXPECTED

```yaml
change_case_id: CHG-C01
case_state: Decision Ready
closed_at: null
```

The Change Case remains open.

No Handover View exists.

## 8.15 Scenario C oracle assertions

1. Gate A passes before `BL-C01` is established, using target-identification checks only.
2. Overlay execution eligibility passes after `BL-C01` exists.
3. `IAX-C01` and routing are Completed.
4. Every mandatory Assessment Obligation is satisfied.
5. Gate B is Complete.
6. Authorisation Eligibility is Permitted.
7. Required authority is Elevated.
8. Current authority is Standard.
9. `decision_permitted = false`.
10. `escalation_required = true`.
11. `HIST-C01` exists with `entry_type = Escalated`.
12. No Decision Record exists.
13. `CHG-C01` remains open in `Decision Ready` state.

---

# 9. Cross-Scenario Deterministic Assertions

The later prototype must satisfy all of the following across the three fixtures.

## 9.1 Historical reconstruction

1. Every Assessment Baseline is reconstructible from immutable Baseline Members.
2. Impact-analysis Executions read Baseline Member snapshots, not later source-state values.
3. Every locked Assessment preserves its complete semantic child set.
4. Every Assessment Evidence Use preserves the exact Evidence state used.
5. `DEC-A01` can reconstruct its complete Assessment and Evidence basis through Decision Support Assessments.

## 9.2 Identity and revision

1. Change Item identity is stable and revision content is immutable after overlay use.
2. Proposal State is separate from Change Item Revision content.
3. No authoritative Product Version is created by overlay materialisation.
4. Overlay-local object identity is unique within its Overlay Revision.

## 9.3 Baseline and overlay

1. Gate A target identification does not require an Assessment Baseline.
2. Overlay execution eligibility requires the selected Assessment Baseline and baseline-relative target checks.
3. Every execution references exactly one baseline and one overlay from the same Change Case.
4. Scenario B changes proposal scope without changing the baseline.
5. Historical Overlay membership is not altered when a new Overlay Revision is created.

## 9.4 Provenance

1. Every Impact Candidate has at least one provenance record.
2. Current-state path references resolve to Baseline Members.
3. Proposed-state path references resolve to Overlay-local Objects from the execution Overlay Revision.
4. Path sequences are contiguous and connected.

## 9.5 Assessment readiness

1. Zero obligations has no meaning until routing is Completed.
2. Gate B is obligation-driven.
3. Retained historical Assessments satisfy later obligations only through target-execution reuse classification.
4. `Revalidation Required` and `Invalidated` do not satisfy mandatory obligations.

## 9.6 Decision integrity

1. Scenario A creates a terminal Decision Record.
2. Scenario B creates no Decision Record at the defined v0.1 stop point.
3. Scenario C creates no Decision Record because authority is insufficient.
4. No Process-history Entry disposes a Change Item through authority.
5. Decision Scope never expands automatically from Impact Candidate discovery.
6. `Authorised for Downstream Processing` has zero Decision Conditions.

## 9.7 Case-local lineage

All lineage associations within a scenario resolve to one and only one Change Case. Cross-scenario lineage joins are invalid.

---

# 10. Expected Scenario Summary

| Scenario | Baseline | Overlay(s) | Execution(s) | Key semantic result | Gate B at stop point | Authority | Terminal Decision |
|---|---|---|---|---|---|---|---|
| A | `BL-A01` | `OV-A01` | `IAX-A01` | Complete decision basis | Complete | Standard = Standard | `DEC-A01` — Authorised for Downstream Processing |
| B | `BL-B01` reused | `OV-B01`, `OV-B02` | `IAX-B01`, `IAX-B02` | proposal revision ≠ baseline revision; reuse classified per execution | Incomplete | not evaluated | none |
| C | `BL-C01` | `OV-C01` | `IAX-C01` | package completeness ≠ authority to decide | Complete | Elevated > Standard | none; `HIST-C01` Escalated |

---

# 11. Instantiation Review

One implementation-blocking contradiction was identified during review of v0.1: Logical Information Model v0.3.1 made Gate A depend on baseline-relative target integrity even though the frozen Business Architecture establishes or selects the Assessment Baseline only after Gate A. This qualifies as an actual implementation contradiction under the project freeze rule.

The contradiction is corrected narrowly in **Logical Information Model v0.3.2 — Frozen Implementation Baseline** by separating Gate A target identification from baseline-relative overlay execution eligibility. The Business Architecture v0.3.1 process order and all other frozen semantics remain unchanged.

After that correction, no remaining contradiction prevents deterministic implementation of Scenarios A–C.

Two boundaries are deliberately preserved for the next artefact:

1. **Scope-revision routing:** Scenario B records the exact structured state that must lead to `Scope Revision Required`, but this document does not invent an automated interpretation of free-text Assessment statements. `Readiness and Routing Rules v0.1` must define the deterministic rule using the existing frozen data.
2. **Authority derivation:** Scenario C treats `required_authority_level` and `current_authority_level` as decision-route values, exactly as allowed by the frozen Logical Information Model. `Readiness and Routing Rules v0.1` must define the synthetic rule that yields `Elevated` for this fixture.

Neither boundary requires reopening the frozen architecture.

---

# 12. Next Artefact

Proceed to:

> **Product Change Impact Assessment & Decision Readiness — Readiness and Routing Rules v0.1**

That artefact must turn the reserved `RRR-*` references and Gate/authority expectations in this Scenario Data Definition into explicit deterministic rules without adding new PLM semantics.
