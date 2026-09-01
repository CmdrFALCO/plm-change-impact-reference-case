# Verified Release Baseline

## Release state

The repository has a published **`v0.1.0` release dated 2026-09-01**.

Published release facts:

- annotated tag: `v0.1.0`;
- release commit: `f15c75b237f85d0926ab0531962e4aba15568fab`;
- GitHub Release: `https://github.com/CmdrFALCO/plm-change-impact-reference-case/releases/tag/v0.1.0`;
- Zenodo DOI: `10.5281/zenodo.22235248`.

The verified executable baseline remains:

```text
7a5733fc7042e33a790db12278f8776d047eb4b6
```

The published tag and later documentation/release-metadata commits do not move or redefine that
verified implementation baseline.

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

## Publication and packaging lineage

- verified executable baseline:
  `7a5733fc7042e33a790db12278f8776d047eb4b6`;
- architecture publication merge:
  `a1c3e1969dd75836b672f83684aa11feb4ee71df`;
- Architecture Traceability and Assurance Pack merge:
  `5b0b9e7fb3e2fb4873e0daba125ffbd7c39b5b59`;
- Session 7 independent-review merge:
  `8bc2aa211ac6a4524f857abf394d081e78664ded`;
- `v0.1.0` release-preparation merge and tagged release commit:
  `f15c75b237f85d0926ab0531962e4aba15568fab`;
- Zenodo version DOI:
  `10.5281/zenodo.22235248`.

These commits and archival records package, explain, review and preserve the verified
implementation. They do not add PLM functionality, change frozen scenarios or rules, or establish a
new executable baseline.

The Zenodo archive was created from the exact `v0.1.0` tag before post-release DOI metadata was
written back to `main`. Post-release citation synchronization therefore does not alter the bytes of
the published tag or archived source package.

CI verifies the six frozen architecture files against
[`docs/SHA256SUMS-frozen-architecture.txt`](docs/SHA256SUMS-frozen-architecture.txt).

## Evidence boundary

Committed evidence is listed in [`evidence/SHA256SUMS.txt`](evidence/SHA256SUMS.txt). The manifest
records SHA-256 values for the LF-normalized bytes stored by Git. The canonical verification
workflow regenerates the evidence twice, checks it against the manifest after each run, and
requires no resulting evidence diff.
