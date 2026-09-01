# Scenario B — Assessment Reuse and Readiness

**Communication extract from committed Scenario B evidence.**  
**Authoritative sources:** `evidence/scenario_b_actual.json`, frozen Scenario Data Definition v0.1 and `RRR-v0.1`.

---

## Reuse classifications for `IAX-B02`

```text
ASM-B01  → Invalidated
ASM-B02  → Retained
ASM-B03  → Revalidation Required
ASM-B04  → Retained
```

Reuse classification is relative to the target Impact-analysis Execution. It does not rewrite the historical Assessment.

## Second-execution Assessment Obligations

```text
AO-B21  Product Engineering / REQ-004 / IC-B21
        fulfilled_by_assessment_id = null

AO-B22  Manufacturing / REQ-003 / IC-B22
        fulfilled_by_assessment_id = null

AO-B23  Validation / REQ-002 / candidate = null
        fulfilled_by_assessment_id = ASM-B02

AO-B24  Purchasing/Cost / requirement = null / candidate = null
        fulfilled_by_assessment_id = ASM-B04
```

`ASM-B02` and `ASM-B04` can satisfy the new target-execution obligations only because they are explicitly classified `Retained` for `IAX-B02` and remain compatible under the frozen rules.

The later fulfilment references change only the new obligations. The locked historical Assessments and their semantic child records remain unchanged.

## Readiness stop point

```text
Impact-analysis Execution       IAX-B02
Routing                         Completed
Unsatisfied obligations         AO-B21, AO-B22
Gate B                          Incomplete
Authorisation Eligibility       Not Evaluated
Required Authority              Not Evaluated
Decision Record                 none
Case state                      In Assessment
Handover View                   none
```

The committed derived result identifies the failed Gate B predicate as:

```text
all_mandatory_obligations_satisfied
```

## Architectural statement proved

> Scope change does not force indiscriminate Assessment reuse or indiscriminate reassessment. Reuse is explicit, execution-relative and compatibility-controlled; remaining mandatory obligations keep the Decision Package incomplete.
