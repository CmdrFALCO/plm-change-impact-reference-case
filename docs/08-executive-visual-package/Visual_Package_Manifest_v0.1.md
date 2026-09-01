# Product Change Impact Assessment & Decision Readiness

## Visual Package Manifest v0.1

**Status:** Session 5 release-candidate package manifest  
**Package type:** Public-safe, role-neutral executive and visual package  
**Release target:** `v0.1.0`  
**Architecture authority:** Unchanged; all package files are derived communication artefacts

---

# 1. Package boundary

This manifest records the editable and derived outputs of Session 5.

The package preserves two visible dimensions of the same reference case:

1. **business, process, information and decision architecture**;
2. **controlled delivery and assurance** from bounded problem and frozen authority hierarchy through implementation increments, acceptance/integrity gates, independent verification and deterministic evidence.

The prototype remains the proof boundary for the architecture, not the primary deliverable.

---

# 2. Canonical source artefacts

| Artefact | Repository path | Role |
|---|---|---|
| Executive Brief semantic source | `docs/08-executive-visual-package/Executive_Brief_v0.1.md` | Reviewable one-page narrative source. |
| Canonical package specification | `docs/08-executive-visual-package/Canonical_Package_Specification_v0.1.md` | Fixed thesis, modular structure, ten-slide storyboard and claim discipline. |
| Canonical Diagram 1 source | `docs/08-executive-visual-package/diagrams/01_architecture_to_evidence_chain.md` | Editable Mermaid and arrow-semantics specification. |
| Canonical Diagram 2 source | `docs/08-executive-visual-package/diagrams/02_baseline_overlay_state_separation.md` | Editable Mermaid and concept-boundary specification. |
| Canonical Diagram 3 source | `docs/08-executive-visual-package/diagrams/03_readiness_eligibility_authority_decision.md` | Editable Mermaid and decision-path specification. |

Exactly three diagrams are designated as canonical.

---

# 3. Editable visual artefacts

| File | Purpose | SHA-256 | Bytes |
|---|---|---|---:|
| `Executive_Brief_v0.1.pptx` | Editable A4 portrait one-page executive brief source. | `51d075e89431a18d2741ed41177bedafdf12cdacf34c610100ea50e6261ac087` | 75,235 |
| `Product_Change_Impact_Decision_Readiness_Presentation_v0.1.pptx` | Editable 16:9 canonical ten-slide presentation with native text, shapes and connectors plus speaker notes. | `63aaba93cd3a4c3a25155fbd2a018f8e13d7096ffd6286da43bbf6655dbb3950` | 461,357 |
| `diagrams/01_architecture_to_evidence_chain.svg` | Editable vector derivative of Canonical Diagram 1. | `3c2886d637a6c688d5358410eddd61b1158382014a1fe9f2dfa3c4293d35ee10` | 10,129 |
| `diagrams/02_baseline_overlay_state_separation.svg` | Editable vector derivative of Canonical Diagram 2. | `b8b5eded6887fb984ec1505f157860ea7cda9f46514cb3a3b899679263470aa8` | 6,106 |
| `diagrams/03_readiness_eligibility_authority_decision.svg` | Editable vector derivative of Canonical Diagram 3. | `d64f646abeb708729ab2c785040752439c54620792cdf256b759402672faa683` | 6,412 |

The PowerPoint source uses editable native slide objects. The SVG files are additional vector derivatives; the Markdown/Mermaid files remain the transparent semantic diagram sources.

---

# 4. Viewing and distribution derivatives

| File | Purpose | SHA-256 | Bytes |
|---|---|---|---:|
| `Executive_Brief_v0.1.pdf` | One-page A4 viewing/distribution derivative. | `7adfc7ed3103859cc45666ff75acf099f0255bc5842fe19949297267658f539f` | 46,676 |
| `Product_Change_Impact_Decision_Readiness_Presentation_v0.1.pdf` | Ten-page viewing/distribution derivative of the canonical presentation. | `05ff3a86abc85030d59e26fed45ae870c6c07353b49344803a50d2729d61dfba` | 242,439 |
| `diagrams/01_architecture_to_evidence_chain.png` | Raster viewing derivative of Canonical Diagram 1. | `a9722fc3a30787de1bc59ed199579b078f3a118ceedf8151d55acbf79d16c4f1` | 276,904 |
| `diagrams/02_baseline_overlay_state_separation.png` | Raster viewing derivative of Canonical Diagram 2. | `d3b98d93f1c3fc4e939e28d958e1b804dd23aad2d3ed50527c0fba2e7abcfba2` | 231,210 |
| `diagrams/03_readiness_eligibility_authority_decision.png` | Raster viewing derivative of Canonical Diagram 3. | `f84aa663a3ef43b899c3099f201495f4ca5401e981e01259f2ac66ebab957009` | 200,495 |

---

# 5. Presentation structure

The canonical deck contains ten slides:

1. Title and architectural thesis
2. Why `Revision A → Revision B` is insufficient
3. Bounded capability and public-safe scope
4. Architecture-to-evidence chain
5. Current state, Assessment Baseline and proposed-state separation
6. Information and lineage architecture
7. Gate B, Authorisation Eligibility, authority and Decision
8. Scenario A–C architectural proofs
9. Controlled delivery and verification
10. Supported claims, limitations and applicability

Slides 4, 5 and 7 contain the three canonical diagrams. Slide 9 reuses the delivery-and-assurance components of Diagram 1 and does not create a fourth competing architecture diagram.

---

# 6. Render and layout verification

The following packaging checks were completed before this manifest was written:

- the ten-slide PowerPoint passed automated slide overflow testing;
- the A4 executive-brief PowerPoint passed automated slide overflow testing;
- the presentation rendered successfully to ten slide images through LibreOffice;
- the executive brief rendered successfully to one A4 page;
- both PowerPoint files converted successfully to PDF;
- the one-page PDF and the ten-page presentation PDF rendered successfully for visual inspection;
- the three SVG files rendered successfully to PNG;
- the three canonical slide diagrams were checked for terminology, arrow meaning and frozen scenario consistency;
- no frozen architecture source, executable source, migration, fixture, test or committed evidence file is part of this package change.

The protected pull-request `verify` workflow remains the repository-level acceptance gate before merge.

---

# 7. Claim boundary

The package supports a bounded conformance claim for the synthetic reference case. It does not claim:

- company-specific process, data-model, workflow or authority fidelity;
- enterprise PLM completeness or production readiness;
- general arbitrary-graph impact discovery;
- automated engineering judgement or terminal approval;
- enterprise programme, budget, workforce-capacity or organisational authority.

Later derivative material may reorder or selectively emphasise complete modules, but it must preserve the same architecture, terminology, scenario outcomes, evidence values and claim boundary.
