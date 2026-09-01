# Scenario A — Terminal Decision Basis

**Communication extract from committed Scenario A evidence.**  
**Authoritative sources:** `evidence/scenario_a_actual.json`, `evidence/decision_DEC-A01_basis.json`, frozen Scenario Data Definition v0.1.

---

## Decision-readiness result

```text
Impact-analysis Execution   IAX-A01
Assessment Baseline         BL-A01
Overlay Revision            OV-A01
Rule set                    RRR-v0.1

Gate B                      Complete
Authorisation Eligibility   Permitted
Required Authority          Standard
Current Authority           Standard
Authority sufficient        true
Decision permitted          true
```

## Explicit terminal disposition

```text
Decision Record             DEC-A01
Outcome                     Authorised for Downstream Processing
Decision Scope              CI-A01:r1
Decision Conditions         none
Final Case state            Closed by Decision
```

The Decision Record is not the automatic output of the readiness calculation. The frozen scenario supplies the explicit authority disposition after the deterministic preconditions are satisfied.

## Supporting Assessments

```text
DSA-A01 → ASM-A01  Product Engineering  Complete / locked
DSA-A02 → ASM-A02  Validation           Complete / locked
DSA-A03 → ASM-A03  Manufacturing        Complete / locked
DSA-A04 → ASM-A04  Purchasing/Cost      Complete / locked
```

All four mandatory Assessment Obligations are satisfied by compatible Complete Assessments.

## Historical lineage

```text
CI-A01:r1
   │
   ├─ evaluated current-state basis → BL-A01 + immutable Baseline Members
   ├─ proposed-state representation → OV-A01 + OVOBJ-A01-PV
   └─ impact/routing execution      → IAX-A01
                                      │
                                      ├─ supporting locked Assessments
                                      └─ DEC-A01
```

`DEC-A01` references the exact Assessment Baseline, Overlay Revision, Impact-analysis Execution, Decision Scope and supporting Assessments used for the terminal disposition.

## Derived Handover View

```text
Authorised Change Item              CI-A01:r1
Proposed product-state action       Revise Product State
Proposed-state reference            OVOBJ-A01-PV
Applicability constraint            CoolingType = "Liquid"
Planned engineering effective date  2026-11-01
Decision Conditions                 []
```

The Handover View is derived from the authorised Decision basis; it is not independently persisted as a business object.

## Architectural statement proved

> A terminal Decision can be historically reconstructed from an explicit, case-local decision basis without collapsing readiness calculation into automated engineering approval.
