# Product Change Impact Assessment & Decision Readiness

## v0.1.0 Release Package

**Status:** Published and archived  
**Release:** `v0.1.0`  
**Release date:** `2026-09-01`  
**Zenodo DOI:** `10.5281/zenodo.22235248`

This directory contains release-layer metadata only. It does not redefine frozen architecture, scenario semantics or the verified executable baseline.

## Published material

- [`Release_Notes_v0.1.0.md`](Release_Notes_v0.1.0.md) — final release narrative, verification summary, package navigation, claim boundary and archival status.
- [`Release_Manifest_v0.1.0.md`](Release_Manifest_v0.1.0.md) — release lineage, source/evidence integrity references, tag/commit identity and Zenodo archival provenance.

## Completed release sequence

```text
prepare release notes / manifest
→ protected release-preparation PR
→ verify final main
→ create annotated v0.1.0 tag
→ publish GitHub Release
→ publish Zenodo archive
→ synchronize actual release date / DOI metadata back to main
```

Remaining close-out work is limited to career/portfolio integration and maintenance-mode housekeeping. It is not permission to add PLM scope or change frozen semantics.

## Published identifiers

```text
release tag:          v0.1.0
release commit:       f15c75b237f85d0926ab0531962e4aba15568fab
release date:         2026-09-01
GitHub Release:       https://github.com/CmdrFALCO/plm-change-impact-reference-case/releases/tag/v0.1.0
Zenodo DOI:           10.5281/zenodo.22235248
```

## Governing boundary

The verified executable baseline remains:

```text
7a5733fc7042e33a790db12278f8776d047eb4b6
```

Publication, DOI synchronization and release packaging do not move that executable baseline or alter the published `v0.1.0` tag.
