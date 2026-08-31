# Product Change Impact Assessment & Decision Readiness

## Business Architecture Definition v0.3.1 — Frozen Implementation Baseline

**Document type:** Portfolio Business Architecture Case  
**Status:** Frozen implementation baseline  
**Domain:** Synthetic automotive Product Lifecycle Management  
**Version:** 0.3.1  
**Date:** August 2026  
**Supersedes:** v0.3  

---

## Document Notice

This document describes a **synthetic reference architecture** developed for portfolio and learning purposes.

All organisations, roles, product structures, identifiers, product data, processes, lifecycle states, decision rules, configuration rules, and scenarios are fictional or deliberately abstracted.

The architecture does **not** reproduce any Mercedes-Benz process, system, organisation, data model, workflow, numbering scheme, or confidential implementation detail.

Internal enterprise material was used only to challenge simplistic PLM assumptions and improve the realism of the public-safe abstraction.

The prototype database represents a synthetic **integration projection**, not an authoritative enterprise system of record.

The purpose of the case is to demonstrate how a bounded product-change problem can be translated into:

> **business capability → change semantics → product information → evaluated state → impact discovery → domain assessment → decision readiness → terminal decision → downstream handover**

The architecture is not intended to define an enterprise-ready PLM system.

---

# 1. Purpose

This document defines a synthetic Business Architecture for:

> **Product Change Impact Assessment & Decision Readiness**

The purpose is to demonstrate how a product-change problem can be translated into:

> **change semantics → product information → evaluated state → impact discovery → domain assessment → decision readiness → terminal decision**

The architecture intentionally stops before:

- product-data authoring;
- engineering release;
- manufacturing implementation;
- stock transition;
- service deployment.

The accompanying prototype exists only to validate selected architectural concepts.

It is not intended to reproduce an enterprise PLM platform.

---

# 2. Change from v0.3

Version 0.3.1 makes implementation-freeze corrections without changing the capability architecture.

The principal corrections are:

1. A revision of the Proposed Change Scope requires a **new overlay revision and impact-analysis execution**, but does **not automatically require a new Assessment Baseline**.
2. `Withdrawn` is removed from Decision Record outcomes and treated as a **terminal administrative Case Closure Event**.
3. Only two Change Item actions are executable in the baseline prototype:
   - **Revise Product State**
   - **Change Applicability**
4. `Replace Product Identity` and `Invalidate Future Use` are removed from this baseline.
5. Each impact-analysis execution has a stable identifier and explicit lineage to:
   - Assessment Baseline;
   - Change Item revisions;
   - overlay revision;
   - rule-set version;
   - execution timestamp.

No new PLM capability is introduced in this release.

---

# 3. Capability Definition

> When a product-data change is proposed, define the intended Change Items, evaluate them against an immutable current-state baseline using a non-authoritative proposed-state overlay, identify potential impacts, determine required assessments, consolidate domain conclusions and evidence, and create a terminal Decision Record for an explicitly defined Decision Scope.

---

# 4. Fundamental Semantic Model

The architecture separates six concepts that must not be collapsed:

```text
Authoritative current state
        +
Proposed Change Items
        ↓
Evaluated proposed-state overlay
        ↓
Impact Candidates
        ↓
Domain Assessments
        ↓
Decision Scope
        ↓
Terminal Decision
```

A product change is therefore **not** represented simply as:

```text
Version A → Version B
```

The Change Case describes why change is required.

The Change Items describe what is proposed.

The Assessment Baseline defines what authoritative product state is being evaluated.

The overlay describes the hypothetical future state.

Impact Candidates describe what might be affected.

Assessments determine relevance and disposition.

The Decision Record determines what is actually authorised or rejected.

---

# 5. Process Boundary

## 5.1 Start

The capability begins when:

> A change need has been documented and at least one proposed Change Item can be identified.

---

## 5.2 Terminal authority dispositions

Only the following terminal authority dispositions create a **Decision Record**:

- **Authorised for Downstream Processing**
- **Authorised with Conditions**
- **Rejected**

---

## 5.3 Non-terminal routing outcomes

The following keep the Change Case open:

- Returned for Information
- Scope Revision Required
- Additional Assessment Required
- Escalated
- Delegated

These are stored as auditable **Process Routing Events**.

They do not create a terminal Decision Record.

---

## 5.4 Terminal administrative closure

The Change Owner may stop pursuing the proposal.

This produces:

> **Withdrawn by Change Owner**

Withdrawal creates a terminal **Case Closure Event** in process history.

It does **not**:

- create a Decision Record;
- imply rejection;
- require completed Assessments;
- imply technical evaluation of the proposal.

---

# 6. Change Case

A **Change Case** is the process-level container.

Minimum attributes:

- case identifier;
- trigger;
- rationale;
- Change Owner;
- initial assumptions;
- process state;
- current process iteration.

A Change Case contains one or more Change Items.

```text
Change Case
    CONTAINS
Change Item
```

The Change Case itself does not describe the detailed product-state transformation.

---

# 7. Change Item

A **Change Item** defines one intended modification.

Minimum attributes:

- Change Item identifier;
- target subject;
- action;
- current-state reference;
- proposed-state description;
- reason;
- configuration scope;
- intended effectivity;
- owner;
- Change Item revision.

## 7.1 Executable actions

The baseline prototype implements only:

### Revise Product State

Creates a proposed successor Product Version in the non-authoritative overlay.

### Change Applicability

Creates a proposed change to the applicability governing a Product Structure Occurrence.

## 7.2 Recognised but not implemented

The architecture recognises that broader PLM change semantics can include:

- Add Usage
- Remove Usage
- Change Usage
- Change Effectivity

These actions are explicitly outside the executable baseline.

## 7.3 Removed from this baseline

The following are not part of v0.3.1:

- Replace Product Identity
- Invalidate Future Use

Identity replacement would require transition, compatibility, and replacement semantics that are intentionally outside scope.

Future-use invalidation overlaps with lifecycle state, applicability, and effectivity and is therefore excluded.

---

# 8. Product-Version Immutability

A Product Version referenced by:

- an Assessment Baseline; or
- a Decision Record

is immutable within the demonstrator.

A baselined Product Version must never be modified in place.

Therefore:

```text
Existing baselined Product Version
        ↓
Revise Product State
        ↓
Successor Product Version
```

An unbaselined working version may be edited during preparation, but it becomes immutable when incorporated into an Assessment Baseline.

This preserves:

- baseline reproducibility;
- evidence meaning;
- historical decision traceability.

---

# 9. Product Information Model

## 9.1 Product Element

Represents version-independent product identity.

Minimum attributes:

- identifier;
- name;
- descriptive type.

Types such as Product, Assembly, and Component are descriptive simplifications and do not determine structural behaviour.

---

## 9.2 Product Version

Represents one immutable development state after baselining.

Minimum attributes:

- Product Element reference;
- revision;
- iteration;
- lifecycle state.

Relationship:

```text
Product Element
    HAS_VERSION
Product Version
```

A successor relationship may be represented as:

```text
Product Version
    SUPERSEDES
Product Version
```

No general replacement or interchangeability model is included in this release.

---

# 10. Product Structure Occurrence

A Product Structure Occurrence represents a particular usage of a child Product Version within a parent Product Version.

```text
Parent Product Version
    HAS_OCCURRENCE
Product Structure Occurrence

Product Structure Occurrence
    REFERENCES
Child Product Version
```

Minimum semantics:

- occurrence identifier;
- position;
- quantity;
- unit;
- applicability;
- effectivity.

This permits the architecture to distinguish:

- changing the child product state;
- changing one usage;
- adding a usage;
- removing a usage;
- changing usage attributes.

Only applicability change is executable in the baseline prototype.

---

# 11. Configuration Context

A Configuration Context represents the bounded product configuration against which applicability is evaluated.

For the prototype it contains:

- context identifier;
- selected feature/value pairs;
- completeness state.

Example:

```text
PackFamily = LongRange
CoolingType = Liquid
```

The demonstrator does not implement a complete configuration engine.

---

# 12. Applicability Rule

Applicability answers:

> **Where does this occurrence apply?**

A deliberately bounded rule can be:

```text
CoolingType = "Liquid"
AND
PackFamily = "LongRange"
```

Conceptually:

```text
Product Structure Occurrence
    GOVERNED_BY
Applicability Rule

Applicability Rule
    EVALUATED_IN
Configuration Context
```

The executable implementation may embed Applicability Rule semantics within an occurrence record rather than manage it as an independent lifecycle object.

---

# 13. Effectivity Specification

Effectivity answers:

> **When does the intended product state or usage apply?**

The baseline demonstrator implements only:

> **Planned Engineering Effective Date**

Production implementation dates, stock transition, and service transition remain external.

Effectivity may therefore be represented as a bounded value object rather than a complete independently managed domain object.

---

# 14. Assessment Baseline

An **Assessment Baseline** is an immutable definition of the authoritative current product-information state used for an analysis.

Minimum metadata:

- baseline identifier;
- snapshot timestamp;
- relevant Product Version identifiers;
- relevant Product Structure Occurrences;
- Configuration Context;
- applicable Effectivity context;
- source identifiers;
- extraction timestamp;
- routing/rule-set version.

The baseline alone does not represent the state being proposed.

---

# 15. Baseline Reuse Rule

A change to the proposed future state does **not** automatically change the authoritative current state.

Therefore:

> **A revision of the Proposed Change Scope requires a new overlay revision and impact-analysis execution, but does not by itself require a new Assessment Baseline.**

The existing Assessment Baseline may be reused when:

- the authoritative current state remains unchanged;
- the relevant baseline scope remains valid;
- the Configuration Context remains valid;
- the Effectivity context remains valid;
- the prior extraction remains accepted as the analysis basis.

A new Assessment Baseline is required when one or more of these baseline-defining elements change.

---

# 16. Proposed-State Overlay

Impact analysis evaluates:

> **Assessment Baseline + versioned Change Item overlay**

The overlay is a hypothetical, non-authoritative product state.

It does not modify the authoritative current-state information.

Every impact-analysis execution identifies:

- Assessment Baseline ID;
- included Change Item IDs;
- Change Item revisions;
- overlay revision;
- routing/rule-set version.

The process evaluates both:

### Current-state graph

What relationships exist before the proposed change?

### Proposed-state graph

What relationships would exist if the included Change Items were applied?

The comparison can therefore reveal:

- removed dependencies;
- newly created dependencies;
- changed applicability;
- changed structural usage context.

---

# 17. Impact-analysis Execution

An **Impact-analysis Execution** is an identifiable audit and implementation record.

It is not a separate PLM capability.

Minimum fields:

- execution identifier;
- Assessment Baseline ID;
- included Change Item IDs and revisions;
- overlay revision;
- rule-set version;
- execution timestamp.

Conceptually:

```text
Assessment Baseline B-01
        +
Overlay O-02
        +
Rules R-01
        ↓
Impact Analysis X-04
        ↓
Impact Candidates
```

Impact Candidates reference the execution that produced them.

This allows two executions against the same baseline but different overlays to remain distinguishable and reproducible.

---

# 18. Impact Analysis Invariant

> **Impact analysis shall evaluate the immutable Assessment Baseline both before and after application of the versioned Change Item overlay.**

The overlay must never mutate authoritative baseline data.

Conceptually:

```text
Assessment Baseline
        +
Change Item Overlay
        ↓
Current State / Proposed State Comparison
        ↓
Impact-analysis Execution
        ↓
Impact Candidates
```

---

# 19. Proposed Change Scope, Impact Scope, and Decision Scope

These sets remain separate.

## Proposed Change Scope

The Change Items currently proposed by the Change Owner.

## Impact Candidate Scope

Objects or usages identified as potentially affected by analysis.

## Decision Scope

The exact Change Items disposed by the terminal decision.

```text
Proposed Change Scope
        ↓
Impact Discovery
        ↓
Impact Candidate Scope
        ↓
Assessment
        ↓
Explicit Scope Revision if required
        ↓
Decision Scope
```

An Impact Candidate never becomes an authorised change merely because it was discovered.

---

# 20. Scope Amendment

Impact analysis may reveal that another object or usage must itself change.

Example:

```text
Initial Change Item:
Revise Cooling Plate Product State
```

Impact discovery identifies:

```text
Cooling Plate occurrence in parent assembly
```

Domain assessment determines:

> the occurrence applicability itself must change.

This produces:

```text
Scope Revision Required
```

A new Change Item is created:

> **Change Applicability**

Because the Proposed Change Scope changed, a new overlay revision and impact-analysis execution are required.

The process then performs a **Baseline Validity Check**.

```text
Change Item revision/addition
        ↓
New overlay revision
        ↓
Baseline validity check
        ↓
Reuse existing baseline
OR
Establish new baseline
        ↓
New impact-analysis execution
```

Previously completed Assessments are classified individually as:

- **Retained**
- **Revalidation Required**
- **Invalidated**

No Assessment is automatically discarded solely because scope changed.

---

# 21. Impact Candidate

An Impact Candidate is a potential consequence identified from the evaluated state.

Minimum semantics:

- source Change Item;
- candidate object or occurrence;
- dependency path;
- Assessment Baseline;
- Impact-analysis Execution ID;
- potentially affected domain;
- assessment status.

Impact discovery does not establish engineering consequence.

```text
Dependency discovered
       ↓
Impact Candidate
       ↓
Domain Assessment
       ↓
Relevant / Not Relevant / Undetermined
```

---

# 22. Assessment Planning

Required domain assessments are derived from:

1. declared synthetic routing rules;
2. Change Item characteristics;
3. identified Impact Candidates;
4. Process Authority override with recorded rationale.

Example rules:

```text
Material characteristic changed
→ Product Engineering assessment required
→ Validation assessment required
→ Manufacturing assessment required
```

```text
Supplier-related trigger
→ Purchasing/Cost assessment required
```

The portfolio does not claim that these are enterprise or Mercedes-Benz rules.

---

# 23. Assessment

Assessment semantics are separated into distinct dimensions.

## Assessment State

- Planned
- In Progress
- Submitted
- Returned
- Complete
- Withdrawn

## Relevance

- Relevant
- Not Relevant
- Undetermined

## Disposition

- No Objection
- No Objection with Conditions
- Objection
- Escalation Recommended

## Requirement Conclusion

Where relevant:

- Satisfied
- Not Satisfied
- Not Demonstrated
- Not Applicable

## Impact Statement

A structured or narrative conclusion explaining the domain consequence.

The Assessment is the only object permitted to make a Requirement conclusion.

---

# 24. Requirement

A Requirement represents an engineering obligation.

Relationship:

```text
Requirement
    ALLOCATED_TO
Product Element
```

Allocation means only that the Requirement concerns the Product Element.

It does not assert compliance.

---

# 25. Evidence Record

Evidence provides information used by an Assessment.

An Evidence Record does **not** independently conclude that a Requirement is satisfied.

Relationships:

```text
Evidence Record
    ADDRESSES
Requirement

Evidence Record
    APPLIES_TO
Product Version

Assessment
    USES
Evidence Record

Assessment
    CONCLUDES_ON
Requirement
```

Minimum Evidence Record:

- reference;
- evidence type;
- applicable Product Version;
- applicable Configuration Context;
- result;
- issue date;
- validity state;
- provider;
- superseded-by reference.

No generic evidence `approval_status` is included.

---

# 26. Evidence Transferability Rule

> **Evidence applying to a predecessor Product Version is not automatically valid for a proposed successor Product Version.**

An Assessment must explicitly determine whether predecessor evidence:

- remains applicable;
- requires partial revalidation;
- cannot be reused.

Example:

```text
Thermal test
applies to:
Cooling Plate Rev A
```

does not automatically become:

```text
valid evidence
for:
Cooling Plate Rev B
```

merely because Rev B succeeds Rev A.

---

# 27. Open Item

Open Items represent unresolved matters that exist **before a terminal decision**.

Allowed types:

- Information Gap
- Data Defect
- Conflict
- Required Action

Minimum attributes:

- identifier;
- type;
- owner;
- source;
- status;
- blocking class;
- required-before stage;
- resolution evidence.

Risk and assumptions can be described within Assessments when needed.

They are not independently managed objects in this release.

---

# 28. Absolute Temporal Boundary for Conditions

A Decision Condition does not exist before a terminal Decision Record.

Before decision, unresolved obligations are Open Items.

After terminal authorisation, obligations imposed by the Decision Authority are Decision Conditions.

Therefore:

```text
BEFORE DECISION
Open Item
```

is distinct from:

```text
AFTER DECISION
Decision Condition
```

This boundary is absolute in the demonstrator.

---

# 29. Pre-Decision Blocking Logic

Example:

```text
Open Item:
Missing mandatory evidence

required-before:
Decision

blocking:
Yes
```

Result:

> **Decision package incomplete**

No authorised terminal Decision Record can be created.

There is no concept of “Authorise with Conditions” for a mandatory pre-authorisation blocker.

---

# 30. Decision Conditions

Decision Conditions are structured child records of an authorised terminal Decision Record.

Minimum semantics:

- condition text;
- responsible downstream role;
- required-before stage;
- expected completion evidence.

Allowed timing:

- Pre-implementation
- Pre-release
- Post-implementation monitoring

No Pre-authorisation condition exists inside a terminal decision because such a condition would have prevented the decision from being made.

---

# 31. Authority Level

Decision authority is deliberately simplified.

No first-class Decision Mandate object is implemented.

The decision route contains:

- required authority level;
- current authority level;
- decision permitted: yes/no;
- escalation required: yes/no.

Two synthetic levels exist:

### Standard

### Elevated

If:

```text
required authority > current authority
```

the system records:

> **Escalated**

as a Process Routing Event.

No terminal Decision Record is created.

---

# 32. Process Routing Events

Non-terminal process changes are stored as auditable process-history records.

Examples:

- Returned for Information
- Scope Revision Required
- Additional Assessment Required
- Escalated
- Delegated

Each event records:

- timestamp;
- originating stage;
- target stage or authority route;
- reason;
- actor;
- affected scope where relevant.

A Process Routing Event does not dispose Change Items.

---

# 33. Case Closure Event

Administrative withdrawal is recorded separately from authority disposition.

A **Case Closure Event** records:

- timestamp;
- actor;
- reason;
- affected Change Items;
- resulting case state.

The baseline administrative closure is:

> **Withdrawn by Change Owner**

A Case Closure Event does not create a Decision Record and does not imply that the proposal was rejected on technical or business merit.

---

# 34. Decision Record

A Decision Record exists only for terminal authority disposition.

Terminal decision types:

- Authorised for Downstream Processing
- Authorised with Conditions
- Rejected

The Decision Record contains:

- exact Decision Scope;
- disposed Change Item IDs and revisions;
- Assessment Baseline ID;
- overlay revision;
- Impact-analysis Execution ID;
- supporting Assessments;
- supporting Evidence Records;
- resolved and remaining relevant Open Items;
- authority level;
- outcome;
- rationale;
- structured Decision Conditions;
- timestamp.

Relationship:

```text
Decision Record
    DISPOSES
Change Item
```

There is no:

```text
Decision Record
    AUTHORISES
Change Case
```

because the decision applies to a defined change scope, not the abstract case container.

---

# 35. Downstream Handover

No independent Handover Package lifecycle object is required.

For an authorised terminal decision, the system generates a **Handover View** from:

- authorised Change Items;
- Decision Record;
- Decision Conditions;
- applicability constraints;
- effectivity constraints;
- required downstream actions.

The view can contain:

- approved scope;
- explicitly excluded scope;
- required product-data actions;
- downstream conditions;
- planned engineering effectivity;
- expected downstream completion evidence.

This is an output projection.

It is not independently persisted as a separate business object.

---

# 36. Source Metadata

The prototype does not model enterprise source-governance or freshness logic.

Integrated records retain only:

- source class;
- source identifier;
- extraction timestamp.

Generic source classes can include:

- Product Data Source
- Change Source
- Requirements Source
- Evidence Source

No claim is made regarding:

- enterprise authority hierarchy;
- freshness thresholds;
- source precedence;
- conflict resolution.

---

# 37. Data Quality

The conceptual quality taxonomy remains:

- identity quality;
- structural quality;
- applicability quality;
- lifecycle quality;
- change-case completeness;
- assessment completeness;
- traceability quality.

Only two checks are implemented.

## Check A — Initial Distribution Completeness

Determines whether sufficient information exists to begin controlled analysis.

## Check B — Configuration / Structural Consistency

Detects one selected inconsistency relevant to the synthetic scenario.

The prototype does not claim complete product-data-quality assurance.

---

# 38. Revised Process

```text
1. Define Change Case and Change Items
                  ↓
Gate A:
Ready for Initial Distribution
                  ↓
2. Establish / Select Assessment Baseline
                  ↓
3. Create Proposed-State Overlay
                  ↓
4. Execute Impact Analysis
                  ↓
5. Confirm Scope and Plan Assessments
                  ↓
6. Perform Domain Assessments
                  ↓
Gate B:
Decision Package Complete
                  ↓
7. Check Required Authority Level
                  ↓
        ┌─────────┴─────────┐
        │                   │
authority sufficient    insufficient
        │                   │
        ↓                   ↓
Terminal Decision       Routing Event
                            │
                            └─ Escalation
```

Administrative withdrawal can occur independently:

```text
Change Owner stops pursuing proposal
        ↓
Case Closure Event
        ↓
Case = Withdrawn
```

---

# 39. Feedback Loops

## 39.1 Scope loop

```text
Impact Candidate
    ↓
Additional Change Required
    ↓
Scope Revision Event
    ↓
Change Item revision/addition
    ↓
New overlay revision
    ↓
Baseline validity check
    ↓
Reuse baseline or establish new baseline
    ↓
New impact-analysis execution
```

---

## 39.2 Assessment loop

```text
Assessment
    ↓
Additional evidence or impact discovered
    ↓
Assessment replanning
```

---

## 39.3 Authority loop

```text
Decision Package Complete
    ↓
Authority insufficient
    ↓
Escalation Event
    ↓
Case remains open
```

---

# 40. Scenario A — Decision Ready

## Trigger

A supplier process change requires modification of one cooling-plate material characteristic while intended product function remains unchanged.

## Proposed Change Item

**Revise Product State**

Target:

Cooling Plate current Product Version.

The proposed successor Product Version exists only in the analysis overlay until downstream implementation.

## Analysis

The system:

1. establishes or selects an immutable Assessment Baseline;
2. applies the Change Item overlay;
3. executes current-state and proposed-state comparison;
4. identifies Impact Candidates;
5. routes required Assessments;
6. evaluates current evidence against the proposed Product Version.

All mandatory Assessments are Complete.

Required evidence is accepted as applicable or replaced by appropriate evidence.

No blocking Open Item remains.

Required authority:

Standard.

Current authority:

Standard.

## Terminal outcome

> **Authorised for Downstream Processing**

A Decision Record is created.

---

# 41. Scenario B — Scope Amendment

## Initial Change Item

**Revise Product State**

Target:

Cooling Plate Product Version.

## Discovery

The proposed-state overlay reveals that one Product Structure Occurrence requires changed applicability.

That occurrence becomes an Impact Candidate.

A Domain Assessment concludes that the applicability governing the occurrence must itself change.

The system does not silently modify it.

## Routing outcome

> **Scope Revision Required**

No terminal Decision Record is created.

A new Change Item is added:

> **Change Applicability**

A new overlay revision is created.

The current Assessment Baseline is checked for continued validity.

If the authoritative current state, baseline scope, Configuration Context, and Effectivity context remain valid, the same baseline is reused.

A new impact-analysis execution is then performed.

Existing Assessments are classified individually:

- Retained
- Revalidation Required
- Invalidated

This scenario demonstrates:

> **discovered impact ≠ authorised scope**

and:

> **proposal revision ≠ baseline revision**

---

# 42. Scenario C — Authority Escalation

The Change Case passes Gate A.

Impact analysis is complete.

The Decision Package is complete.

All required Assessments exist.

However, the selected synthetic change classification requires:

> Elevated authority.

Current authority:

> Standard.

## Routing outcome

> **Escalated**

A Process Routing Event is recorded.

No Decision Record is created.

The Change Case remains open.

This demonstrates:

> **decision-package completeness ≠ authority to decide**

---

# 43. Core Information Model

## 43.1 Product-information layer

1. Product Element
2. Product Version
3. Product Structure Occurrence

## 43.2 Change and assessment layer

4. Change Case
5. Change Item
6. Assessment Baseline
7. Impact-analysis Execution
8. Impact Candidate
9. Assessment
10. Evidence Record
11. Open Item

## 43.3 Decision and audit layer

12. Decision Record
13. Process-history Entry

Supporting bounded records/value objects:

- Configuration Context
- Applicability Rule
- Effectivity Specification
- Requirement
- Decision Condition
- authority level

A Case Closure Event and Process Routing Event are stored as typed process-history entries rather than independent core domain entities.

---

# 44. Frozen Architectural Invariants

## INV-01 — Baseline + overlay

Impact analysis evaluates an immutable Assessment Baseline plus a versioned Change Item overlay and never mutates authoritative baseline information.

## INV-02 — Product Version immutability

A baselined Product Version is immutable.

A proposed product-state modification creates a successor Product Version in the overlay.

## INV-03 — Evidence vs. conclusion

Evidence can address a Requirement.

Only an Assessment can conclude whether the Requirement is:

- Satisfied;
- Not Satisfied;
- Not Demonstrated;
- Not Applicable.

## INV-04 — Problems vs. conditions

Open Items exist before terminal decision.

Decision Conditions are created only as part of an authorised terminal Decision Record.

## INV-05 — Authority disposition vs. routing vs. closure

Only terminal authority dispositions create Decision Records.

Return, scope revision, additional assessment, escalation, and delegation create Process Routing Events.

Withdrawal creates a terminal Case Closure Event.

## INV-06 — Impact discovery vs. scope

Impact Candidate discovery cannot alter Decision Scope automatically.

## INV-07 — Decision lineage

Every Decision Record references the Assessment Baseline, overlay revision, Impact-analysis Execution, and exact Change Item revisions that were evaluated.

## INV-08 — Evidence transferability

Evidence applicable to a predecessor Product Version is not automatically valid for a successor Product Version.

## INV-09 — Applicability vs. effectivity

Applicability and effectivity remain separate dimensions.

## INV-10 — Integration projection

The prototype integration database is not interpreted as the authoritative source of every represented lifecycle object.

## INV-11 — Proposal change vs. baseline change

A change to Proposed Change Scope requires a new overlay revision and impact-analysis execution, but does not by itself require a new Assessment Baseline.

---

# 45. Business Requirements — Frozen Baseline

**BR-01**  
The capability shall distinguish Change Cases from the Change Items they contain.

**BR-02**  
Each Change Item shall explicitly state its action and target subject.

**BR-03**  
The executable baseline shall support only `Revise Product State` and `Change Applicability`.

**BR-04**  
A Product Version referenced by an Assessment Baseline or Decision Record shall be immutable.

**BR-05**  
A proposed modification to a baselined Product Version shall create a successor Product Version in the overlay.

**BR-06**  
Product identity, product state, and product usage shall be represented separately.

**BR-07**  
Applicability and effectivity shall be represented as separate concepts.

**BR-08**  
Each impact-analysis execution shall identify its Assessment Baseline and exact Change Item overlay.

**BR-09**  
A proposal revision shall require a new overlay revision and impact-analysis execution.

**BR-10**  
A proposal revision shall not automatically require a new Assessment Baseline.

**BR-11**  
Impact analysis shall evaluate both current and proposed states.

**BR-12**  
Impact Candidates shall be traceable to their source Change Items, Assessment Baseline, and Impact-analysis Execution.

**BR-13**  
Impact Candidate discovery shall not automatically alter Proposed Change Scope or Decision Scope.

**BR-14**  
Required scope changes shall require explicit Change Item creation or revision.

**BR-15**  
Required Assessments shall be determined through declared routing logic and documented Process Authority overrides.

**BR-16**  
Assessment workflow state, relevance, and disposition shall remain independent.

**BR-17**  
Only Assessment shall record the engineering conclusion for a Requirement.

**BR-18**  
Evidence shall identify the Product Version and configuration context to which it applies.

**BR-19**  
Evidence for a predecessor Product Version shall not be automatically considered valid for a successor Product Version.

**BR-20**  
Pre-decision Information Gaps, Data Defects, Conflicts, and Required Actions shall be represented as Open Items.

**BR-21**  
A blocking Open Item required before decision shall prevent creation of an authorised terminal Decision Record.

**BR-22**  
Decision Conditions shall exist only within an authorised terminal Decision Record.

**BR-23**  
Authority insufficiency shall create an escalation Process Routing Event rather than a terminal Decision Record.

**BR-24**  
Only terminal authority dispositions shall create Decision Records.

**BR-25**  
Withdrawal by the Change Owner shall create a terminal Case Closure Event, not a Decision Record.

**BR-26**  
Every Decision Record shall dispose an explicit set of Change Item IDs and revisions.

**BR-27**  
Every Decision Record shall reference the Assessment Baseline, overlay revision, and Impact-analysis Execution used for analysis.

**BR-28**  
An authorised Decision Record shall support generation of a downstream Handover View.

**BR-29**  
Scope revision shall support classification of existing Assessments as Retained, Revalidation Required, or Invalidated.

---

# 46. Explicitly Removed or Deferred

The following concepts are intentionally removed or deferred from the executable baseline:

- first-class Decision Mandate;
- generic Transition Relation;
- Replace Product Identity;
- Invalidate Future Use;
- interchangeability model;
- service-replacement semantics;
- stock-disposition semantics;
- Risk as an independently managed object;
- Assumption as an independently managed object;
- Decision Condition inside Open Item;
- standalone Handover Package persistence;
- enterprise source-authority logic;
- source-freshness evaluation;
- unrestricted Product Version modification;
- generic `Replace`;
- generic `Create`;
- `Evidence VERIFIES Requirement`;
- non-terminal Decision Records;
- Add Usage implementation;
- Remove Usage implementation;
- Change Usage implementation;
- Change Effectivity implementation.

These removals are intentional scope controls.

---

# 47. Implementation Gate

This architecture is considered frozen for implementation.

The prototype must preserve all release-critical rules:

1. **Impact analysis evaluates an immutable baseline plus a versioned Change Item overlay.**
2. **A changed proposal creates a new overlay execution, not automatically a new baseline.**
3. **Baselined Product Versions are immutable.**
4. **Evidence informs Assessment; Assessment owns Requirement conclusions.**
5. **Pre-decision Open Items and post-decision Decision Conditions remain temporally separate.**
6. **Only terminal authority dispositions create Decision Records.**
7. **Withdrawal is a Case Closure Event, not a Decision Record.**
8. **Impact-analysis executions have stable identifiers and explicit lineage.**
9. **Only `Revise Product State` and `Change Applicability` are executable Change Item actions in this baseline.**
10. **No new PLM concepts are added unless implementation exposes an actual contradiction.**

---

# 48. Next Phase

The Business Architecture is now frozen.

The next artefacts are:

1. **Logical Information Model v0.1**
2. **Scenario Data Definition**
3. **Readiness and Routing Rules**
4. **Solution Architecture**
5. **Prototype Implementation Plan**

The Logical Information Model must define:

- identifiers and keys;
- entity vs. value-object boundaries;
- relationship cardinalities;
- version and revision rules;
- Product Structure Occurrence semantics;
- Assessment Baseline membership;
- baseline reuse rules;
- overlay representation;
- Impact-analysis Execution lineage;
- Impact Candidate provenance;
- Assessment and Evidence relationships;
- Open Item blocking rules;
- process-history representation;
- Decision Record constraints;
- Decision Condition representation;
- exact Decision Scope;
- Handover View derivation.

No additional PLM capability should be introduced during those phases unless a contradiction in this frozen architecture makes implementation impossible.
