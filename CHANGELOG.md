# Changelog

All notable release-level changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

No release-level changes recorded after `v0.1.0`.

## [0.1.0] - 2026-09-01

### Added

- Frozen architecture chain covering Business Architecture, Logical Information Model,
  Scenario Data, Readiness and Routing Rules, Solution Architecture, and Implementation Plan.
- Deterministic Scenario A–C executable reference implementation.
- Completed `G00–G14` acceptance sequence with a 185-test verified implementation baseline.
- Published Architecture Index with frozen-artefact precedence, reading paths and SHA-256 values.
- Architecture Traceability and Assurance Pack mapping bounded business requirements, invariants,
  rules, implementation controls, tests and committed evidence.
- Release-governance metadata, deterministic line-ending policy, locked Python 3.12 dependency
  environment, evidence hash manifest, frozen-architecture hash manifest, protected `main`, and
  GitHub Actions verification workflow.
- Canonical executive and visual package with one-page Executive Brief, exactly three canonical
  architecture diagrams, editable ten-slide presentation and PDF derivatives.
- Demonstration and interview package with approximately 60-second and three-minute explanations,
  five-minute deterministic demo, 15-minute architecture/interview walkthrough, 30-minute
  technical-review walkthrough, static scenario/evidence extracts and Bash/PowerShell command
  guidance.
- Independent Session 7 PLM/Business Architecture blocker review, code/evidence reproducibility
  review and findings disposition log.
- `v0.1.0` release notes and release manifest under `docs/11-release/`.
- Published GitHub Release `v0.1.0` and Zenodo archival record with DOI
  `10.5281/zenodo.22235248`.

### Changed

- Release-environment wording distinguishes the project runtime range from the verified Python
  3.12 release environment.
- GitHub Actions verification runner is pinned to Ubuntu 24.04 rather than the mutable
  `ubuntu-latest` alias.
- Root navigation exposes the final demonstration/interview package.
- Citation and release metadata now record the factual `2026-09-01` publication date and Zenodo DOI.

### Release boundary

- Verified executable baseline remains
  `7a5733fc7042e33a790db12278f8776d047eb4b6`.
- The `v0.1.0` annotated tag points to release commit
  `f15c75b237f85d0926ab0531962e4aba15568fab`.
- Later architecture publication, reproducibility, visual, demonstration, review and post-release
  metadata changes do not redefine that executable baseline or move the published tag.
- No frozen architecture artefact, scenario outcome, executable PLM scope or committed verification
  evidence is changed by release or archival publication.

[0.1.0]: https://github.com/CmdrFALCO/plm-change-impact-reference-case/releases/tag/v0.1.0
