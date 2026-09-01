# Verified Release Baseline

## Release state

The repository is an **unreleased `0.1.0` release candidate**.

The verified executable baseline is:

```text
7a5733fc7042e33a790db12278f8776d047eb4b6
```

Later documentation and release-packaging commits do not move or redefine that verified
implementation baseline.

## Recorded verification result

At the verified executable baseline:

- G00–G14: **15/15 PASS**;
- pytest: **185 passed**;
- `plm-ref verify all`: **exit 0**;
- repeated verification evidence: **byte-identical**;
- verification groups: **6/6 PASS**;
- IT-16 cross-case injection families: **6/6 attempted, rejected, and PASS**.

The six verification groups are:

1. Scenario A oracle;
2. Scenario B oracle;
3. Scenario C oracle;
4. Cross-scenario assertions;
5. Integrity suite;
6. Historical reconstruction.

The six IT-16 families are execution baseline/overlay, candidate provenance, Assessment
fulfilment, Assessment reuse, Decision support, and Decision Scope.

## Later publication and packaging lineage

- Architecture publication merge:
  `a1c3e1969dd75836b672f83684aa11feb4ee71df`;
- Architecture Traceability and Assurance Pack merge:
  `5b0b9e7fb3e2fb4873e0daba125ffbd7c39b5b59`;
- Current work: unreleased `0.1.0` reproducibility and repository-governance packaging.

These commits package, explain, and reproduce the verified implementation. They do not add PLM
functionality, change frozen scenarios or rules, or establish a new executable baseline.

CI verifies the six frozen architecture files against
[`docs/SHA256SUMS-frozen-architecture.txt`](docs/SHA256SUMS-frozen-architecture.txt).

## Evidence boundary

Committed evidence is listed in [`evidence/SHA256SUMS.txt`](evidence/SHA256SUMS.txt). The manifest
records SHA-256 values for the LF-normalized bytes stored by Git. The canonical verification
workflow regenerates the evidence twice, checks it against the manifest after each run, and
requires no resulting evidence diff.
