# Scenario B — Scope Amendment

**Communication extract from committed Scenario B evidence.**  
**Authoritative sources:** `evidence/scenario_b_actual.json`, frozen Scenario Data Definition v0.1 and `RRR-v0.1`.

---

## First execution

```text
Change Case                  CHG-B01
Active Change Item           CI-B01:r1 — Revise Product State
Assessment Baseline          BL-B01
Overlay Revision             OV-B01
Impact-analysis Execution    IAX-B01
```

Product Engineering records:

```text
ASM-B01
Requirement                  REQ-004
Conclusion                   Not Satisfied
```

The structured applicability condition therefore triggers `RRR-05`.

## Non-terminal routing result

```text
Process-history Entry        HIST-B01
Entry type                   Scope Revision Required
Origin stage                 Domain Assessment
Target route                 Scope Confirmation
Affected Change Item         CI-B01:r1
Decision Record              none
```

The committed reason states that `PSO-002` applicability must change explicitly and that discovered impact is not authorised scope.

## Explicit scope amendment

The system does **not** create the new Change Item from the Impact Candidate or from `RRR-05`.

The Change Owner / scenario driver explicitly adds:

```text
CI-B02:r1
Action                       Change Applicability
Target                       PSO-002
```

The amended Proposed Change Scope is therefore:

```text
CI-B01:r1
+
CI-B02:r1
```

## Baseline reuse and new proposal execution

The proposal changed, but the authoritative current-state basis did not.

All five frozen baseline-validity inputs are true, therefore:

```text
Assessment Baseline          BL-B01 reused
New Overlay Revision         OV-B02
New Impact-analysis Exec.    IAX-B02
```

`OV-B01` remains historical and unchanged. `OV-B02` contains exactly `CI-B01:r1` and `CI-B02:r1`.

## Architectural statements proved

> **discovered impact ≠ authorised scope**

Impact discovery and Assessment can require explicit scope amendment, but they do not silently create or authorise the new Change Item.

> **proposal revision ≠ baseline revision**

A changed Proposed Change Scope requires a new Overlay Revision and Impact-analysis Execution, but it does not automatically require a new Assessment Baseline.
