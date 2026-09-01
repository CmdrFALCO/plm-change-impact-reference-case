# Product Change Impact Assessment & Decision Readiness

## v0.1.0 Release Package

**Status:** Release preparation in progress  
**Release target:** `v0.1.0`

This directory contains release-layer metadata only. It does not redefine frozen architecture, scenario semantics or the verified executable baseline.

## Prepared material

- [`Release_Notes_v0.1.0.md`](Release_Notes_v0.1.0.md) — prepared GitHub Release narrative, verification summary, package navigation and claim boundary.
- [`Release_Manifest_v0.1.0.md`](Release_Manifest_v0.1.0.md) — release lineage, source/evidence integrity references and pre-tag acceptance conditions.

## Release sequencing

```text
prepare release notes / manifest
→ protected release-preparation PR
→ verify final main
→ create annotated v0.1.0 tag
→ publish GitHub Release
→ update actual release date / citation metadata
→ publish Zenodo archive if selected
→ update career / portfolio links
→ maintenance mode
```

The final release date and any DOI remain unset until those publication facts actually exist.

## Governing boundary

The verified executable baseline remains:

```text
7a5733fc7042e33a790db12278f8776d047eb4b6
```

Documentation and release packaging do not move that executable baseline.
