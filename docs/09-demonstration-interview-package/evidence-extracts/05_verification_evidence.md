# Verification Evidence — Static Extract

**Communication extract from committed verification evidence.**  
**Authoritative sources:** `VERIFIED_BASELINE.md`, `evidence/verification_summary.md`, `evidence/integrity_results.json`.

---

## Verified executable boundary

```text
Verified implementation commit
7a5733fc7042e33a790db12278f8776d047eb4b6
```

Later documentation and packaging commits do not move or redefine that executable baseline.

## Recorded verification result

```text
G00–G14                       15/15 PASS
Full pytest regression       185 passed
plm-ref verify all           exit 0
Repeated evidence            byte-identical
Final verification groups    6/6 PASS
IT-16 injection families     6/6 attempted, rejected and PASS
```

## Six final verification groups

```text
Scenario A oracle             PASS
Scenario B oracle             PASS
Scenario C oracle             PASS
Cross-scenario assertions     PASS
Integrity suite               PASS
Historical reconstruction    PASS
```

## Cross-scenario assertions recorded as passed

The committed integrity evidence includes, among others:

- Scenario A exact Decision Scope;
- Scenario A only terminal Decision;
- Scenario A zero Decision Conditions;
- Scenario B baseline reuse;
- Scenario B only two proposal cycles;
- Scenario C authority insufficiency remains non-terminal;
- B and C have no Handover View;
- historical Overlay Revisions remain distinct;
- retained Assessment semantics remain valid;
- case-local lineage checks for A, B and C.

## Active IT-16 cross-case injection families

Every family below records:

```text
attempted = true
rejected  = true
passed    = true
```

Families:

```text
execution baseline/overlay
candidate provenance
Assessment fulfilment
Assessment reuse
Decision support
Decision Scope
```

These are active negative tests, not merely static schema claims.

## Evidence interpretation

The verification evidence proves the bounded reference case defined by the frozen architecture and Scenarios A–C.

It does **not** prove:

- enterprise PLM completeness;
- production deployment readiness;
- company-specific PLM process fidelity;
- general arbitrary-graph impact discovery;
- automated engineering judgement or terminal approval.

## Architectural statement proved

> The prototype provides deterministic conformance evidence for the frozen architecture through independent scenario oracles, integrity controls, historical reconstruction and reproducible evidence generation.
