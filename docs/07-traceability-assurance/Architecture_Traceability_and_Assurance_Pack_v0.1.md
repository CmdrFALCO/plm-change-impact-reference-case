# Product Change Impact Assessment & Decision Readiness

## Architecture Traceability and Assurance Pack v0.1

**Document type:** Documentation-only traceability and assurance map<br>
**Status:** Release-candidate packaging artefact; does not redefine frozen semantics<br>
**Repository:** `CmdrFALCO/plm-change-impact-reference-case`<br>
**Release target:** `v0.1.0`<br>
**Verified implementation baseline:** `7a5733fc7042e33a790db12278f8776d047eb4b6`<br>
**Architecture-publication merge base:** `a1c3e1969dd75836b672f83684aa11feb4ee71df`

---

# 1. Purpose and authority

This pack exposes the end-to-end assurance chain of the reference case without changing it.

The governing precedence remains:

```text
Business Architecture v0.3.1
        ↓
Logical Information Model v0.3.2
        ↓
Scenario Data Definition v0.1
        ↓
Readiness and Routing Rules v0.1 / RRR-v0.1
        ↓
Solution Architecture v0.1
        ↓
Prototype Implementation Plan v0.1
        ↓
code, migrations, fixtures, tests and evidence
```

The six frozen artefacts remain authoritative. This document is only a map from their business meaning to implementation controls, tests and evidence. If wording in this pack conflicts with a frozen artefact, the frozen artefact wins.

Primary sources:

1. [Business Architecture Definition v0.3.1](../01-business-architecture/Business_Architecture_Definition_v0.3.1_Frozen_Implementation_Baseline.md)
2. [Logical Information Model v0.3.2](../02-logical-information-model/Product_Change_Impact_Decision_Readiness_Logical_Information_Model_v0.3.2_Frozen_Implementation_Baseline.md)
3. [Scenario Data Definition v0.1](../03-scenario-data/Product_Change_Impact_Decision_Readiness_Scenario_Data_Definition_v0.1.md)
4. [Readiness and Routing Rules v0.1](../04-readiness-routing-rules/Product_Change_Impact_Decision_Readiness_Readiness_and_Routing_Rules_v0.1_Frozen_Implementation_Baseline.md)
5. [Solution Architecture v0.1](../05-solution-architecture/Product_Change_Impact_Decision_Readiness_Solution_Architecture_v0.1_Frozen_Implementation_Baseline.md)
6. [Prototype Implementation Plan v0.1](../06-implementation-plan/Product_Change_Impact_Decision_Readiness_Prototype_Implementation_Plan_v0.1_Frozen_Implementation_Baseline.md)

---

# 2. Traceability method

Each trace below follows the same direction:

```text
business requirement / invariant
        ↓
logical-information or deterministic-rule expression
        ↓
implementation control
        ↓
acceptance / integrity test
        ↓
committed verification evidence
```

Coverage labels used here are deliberately narrow:

- **A–C verified** — exercised by one or more frozen scenario oracles and the final verification runner.
- **Integrity verified** — exercised by a negative/integrity test, including cross-case rejection where applicable.
- **Structural / bounded** — represented and constrained in the implementation, but not necessarily exercised as a distinct business outcome in Scenarios A–C.
- **Not claimed** — intentionally outside the release claim boundary.

The executable demonstrator proves deterministic conformance to the frozen synthetic reference case. It does not prove enterprise PLM correctness, production readiness or general engineering validity.

---

# 3. Business-requirement traceability — BR-01 to BR-29

| BR | Frozen business meaning | Logical / rule bridge | Primary implementation control | Verification and evidence | Coverage |
|---|---|---|---|---|---|
| **BR-01** | Distinguish Change Case from contained Change Items. | LIM Change Case; Change Item Identity / Revision. | [`change_case.py`](../../src/plm_ref/application/change_case.py), relational case/item model. | [`test_g02_change_case_gate_a.py`](../../tests/test_g02_change_case_gate_a.py); scenario A/B/C actual state. | A–C verified |
| **BR-02** | Each Change Item states action and target. | LIM immutable Change Item Revision; action-specific target integrity. | [`change_case.py`](../../src/plm_ref/application/change_case.py), [`gate_a.py`](../../src/plm_ref/application/gate_a.py). | G02 target-identification tests; scenario fixtures. | A–C verified |
| **BR-03** | Only `Revise Product State` and `Change Applicability` are executable. | LIM executable-action set; Gate A action rules. | Change-item validation and [`overlay.py`](../../src/plm_ref/application/overlay.py). | G02/G04 negative action and materialisation tests. | Integrity verified |
| **BR-04** | Baselined / decision-lineage Product Versions are immutable. | LIM-INV-04; IR-08/09 protect the used baseline and member snapshots; SA dual enforcement. | [`baseline.py`](../../src/plm_ref/application/baseline.py), DB guards/triggers under [`migrations/`](../../migrations/) and [`infrastructure/db/`](../../src/plm_ref/infrastructure/db/). | [`test_g03_baseline.py`](../../tests/test_g03_baseline.py); IT-03/IT-04. | Integrity verified |
| **BR-05** | Revising baselined product state creates an overlay successor, never in-place mutation. | LIM Overlay-local Object; `Revise Product State`. | [`overlay.py`](../../src/plm_ref/application/overlay.py). | G03/G04; IT-05. | A–C + integrity verified |
| **BR-06** | Product identity, state and usage stay separate. | Product Element / Product Version / Product Structure Occurrence. | Relational source and baseline models in [`infrastructure/db/`](../../src/plm_ref/infrastructure/db/). | [`test_g01_source_projection.py`](../../tests/test_g01_source_projection.py); G03/G04. | Structural / bounded |
| **BR-07** | Applicability and effectivity are separate. | LIM separate bounded value semantics. | Source, payload and overlay validation; [`overlay.py`](../../src/plm_ref/application/overlay.py). | G01/G04; scenario baseline and overlay fixtures. | A–C verified |
| **BR-08** | Every impact execution identifies its baseline and exact overlay. | LIM Impact-analysis Execution lineage; IR-15. | [`impact_analysis.py`](../../src/plm_ref/application/impact_analysis.py). | [`test_g05_impact_execution.py`](../../tests/test_g05_impact_execution.py); IT-16 execution-lineage injection. | A–C + integrity verified |
| **BR-09** | Proposal revision requires a new overlay and execution. | LIM proposal-change invariant; Scenario B second cycle. | [`scenario_runner.py`](../../src/plm_ref/application/scenario_runner.py), [`overlay.py`](../../src/plm_ref/application/overlay.py), [`impact_analysis.py`](../../src/plm_ref/application/impact_analysis.py). | G08/G09/G14; Scenario B actual/diff. | A–C verified |
| **BR-10** | Proposal revision does not automatically require a new baseline. | Baseline-reuse predicate; Scenario B reuses `BL-B01`. | [`baseline.py`](../../src/plm_ref/application/baseline.py). | G03/G08/G14; Scenario B actual. | A–C verified |
| **BR-11** | Impact analysis evaluates current and proposed state. | Baseline + overlay invariant; bounded execution lineage. | [`impact_analysis.py`](../../src/plm_ref/application/impact_analysis.py) with bounded frozen-fixture impact port. | G05 and scenario oracle comparison. | Scenario-bounded; general graph discovery not claimed |
| **BR-12** | Impact Candidates trace to source Change Items, baseline and execution. | LIM structured provenance IR-15–IR-21. | [`impact_analysis.py`](../../src/plm_ref/application/impact_analysis.py), normalized provenance persistence. | G05; IT-16 candidate-provenance injection; scenario actual files. | A–C + integrity verified |
| **BR-13** | Discovery does not automatically alter Proposed Change Scope or Decision Scope. | LIM impact-vs-scope invariant; RRR-05 route only. | [`scope_routing.py`](../../src/plm_ref/application/scope_routing.py), [`decision.py`](../../src/plm_ref/application/decision.py). | G08 IT-10; G11 scope validation; Scenario B. | A–C verified |
| **BR-14** | Scope change requires explicit Change Item creation/revision. | RRR-05 explicitly does not create `CI-B02:r1`. | [`scope_routing.py`](../../src/plm_ref/application/scope_routing.py), [`change_case.py`](../../src/plm_ref/application/change_case.py). | [`test_g08_scope_route.py`](../../tests/test_g08_scope_route.py); IT-10. | A–C verified |
| **BR-15** | Required Assessments come from declared routing logic and documented Process Authority overrides. | `RRR-01..04`; Assessment Obligations. | [`routing.py`](../../src/plm_ref/application/routing.py), [`rules/rrr_v01.py`](../../src/plm_ref/rules/rrr_v01.py). No Process Authority override command or record is implemented. | [`test_g06_routing.py`](../../tests/test_g06_routing.py); scenario obligations. | Deterministic routing A–C verified; Process Authority override path not demonstrated |
| **BR-16** | Assessment state, relevance and disposition remain independent. | LIM Assessment fields and allowed values. | [`assessment.py`](../../src/plm_ref/application/assessment.py), persistence model. | [`test_g07_assessment.py`](../../tests/test_g07_assessment.py); scenario Assessment records. | A–C verified |
| **BR-17** | Only Assessment records Requirement conclusions. | LIM IR-26; Evidence-is-not-compliance invariant. | [`assessment.py`](../../src/plm_ref/application/assessment.py). | G07; scenario Requirement Conclusions. | A–C verified |
| **BR-18** | Evidence identifies applicable Product Version and Configuration Context. | LIM Evidence Record + Assessment Evidence Use. | Source/evidence persistence and [`assessment.py`](../../src/plm_ref/application/assessment.py). | G01/G07; immutable Evidence snapshots in scenario actual and decision basis. | A–C verified |
| **BR-19** | Predecessor Evidence is not automatically valid for successor state. | LIM IR-28; transferability conclusions. | [`assessment.py`](../../src/plm_ref/application/assessment.py). | G07; explicit transferability in scenario A/B Evidence Uses. | A–C verified |
| **BR-20** | Pre-decision gaps/defects/conflicts/actions are Open Items. | LIM Open Item model and temporal boundary. | Persistence model; Gate A/readiness services consume blocking Open Items. | G02 negative Initial Distribution blocker; G10 readiness tests. | Structural + integrity verified |
| **BR-21** | Blocking Decision Open Item prevents authorised terminal Decision. | Gate B / Decision guard. | [`readiness.py`](../../src/plm_ref/application/readiness.py), [`decision.py`](../../src/plm_ref/application/decision.py). | [`test_g10_readiness_authority.py`](../../tests/test_g10_readiness_authority.py), G11 decision guard. | Integrity verified |
| **BR-22** | Decision Conditions exist only inside authorised terminal Decision. | LIM Decision Condition cardinality; IR-46–IR-48. | [`decision.py`](../../src/plm_ref/application/decision.py). | [`test_g11_terminal_decision.py`](../../tests/test_g11_terminal_decision.py). | Integrity verified; Scenario A uses zero conditions |
| **BR-23** | Insufficient authority creates escalation, not Decision Record. | RRR-06; `Standard < Elevated`; IR-39/40. | [`authority.py`](../../src/plm_ref/application/authority.py). | G10 IT-12; Scenario C actual/diff. | A–C verified |
| **BR-24** | Only terminal authority dispositions create Decision Records. | LIM Decision vs routing; RRR terminal persistence preconditions. | [`decision.py`](../../src/plm_ref/application/decision.py), process history services. | G08/G10/G11; IT-13; Scenario B/C contain no Decision. | A–C verified |
| **BR-25** | Withdrawal is administrative closure, not Decision Record. | LIM-INV-22; IR-49; BA withdrawal boundary. | The relational schema permits `Withdrawn` Case state and `Withdrawn by Change Owner` Process-history type; no withdrawal application command is implemented. | Schema inspection only; withdrawal is not a frozen A–C stop point and has no acceptance/integrity test. | Represented only; executable behaviour not demonstrated |
| **BR-26** | Every Decision disposes explicit Change Item IDs/revisions. | LIM Decision Scope Items; IR-41/42. | [`decision.py`](../../src/plm_ref/application/decision.py). | G11; `DEC-A01` Decision Scope in scenario A and decision-basis evidence. | A–C verified |
| **BR-27** | Decision references final baseline, overlay and execution. | LIM Decision lineage; IR-43/45. | [`decision.py`](../../src/plm_ref/application/decision.py), [`history_and_views.py`](../../src/plm_ref/application/history_and_views.py). | G11/G12; [`decision_DEC-A01_basis.json`](../../evidence/decision_DEC-A01_basis.json). | A–C verified |
| **BR-28** | Authorised Decision supports derived downstream Handover View. | LIM derived Handover View; SA no persisted handover object. | [`history_and_views.py`](../../src/plm_ref/application/history_and_views.py). | [`test_g12_history_and_handover.py`](../../tests/test_g12_history_and_handover.py); Scenario A only. | A–C verified |
| **BR-29** | Scope revision supports Retained / Revalidation Required / Invalidated Assessment classifications. | LIM execution-relative reuse; ordered Scenario B reuse rules. | [`assessment_reuse.py`](../../src/plm_ref/application/assessment_reuse.py). | [`test_g09_assessment_reuse.py`](../../tests/test_g09_assessment_reuse.py); Scenario B actual. | A–C verified |

## 3.1 Important coverage qualification

The table does not claim that every generic capability implied by a Business Requirement is implemented beyond the frozen scenarios. In particular:

- impact discovery is supplied by the bounded `ImpactAnalysisPort` fixture adapter rather than a general PLM graph engine;
- BR-15 Process Authority override semantics have no implemented command, persisted override record or acceptance test; only deterministic `RRR-01..04` routing is demonstrated;
- BR-25 withdrawal is represented only by allowed schema values; no withdrawal application use case or executable Scenario A–C outcome is demonstrated;
- the scenario oracles prove the defined synthetic states, not real product engineering correctness.

---

# 4. Frozen Business-Architecture invariant traceability

| Invariant | Meaning | Primary controls | Verification anchor |
|---|---|---|---|
| **INV-01 — Baseline + overlay** | Immutable current-state basis plus non-authoritative proposed-state overlay. | `baseline.py`, `overlay.py`, `impact_analysis.py`. | G03–G05; Scenario A/B/C lineage. |
| **INV-02 — Product Version immutability** | Baselined Product Version cannot be modified; successor is overlay-local. | Application guard + SQLite trigger; overlay materialisation. | IT-03/04/05; G03/G04. |
| **INV-03 — Evidence vs conclusion** | Evidence informs; Assessment concludes. | `assessment.py`, Requirement Conclusion records. | G07; scenario Evidence Uses and conclusions. |
| **INV-04 — Problems vs conditions** | Open Items are pre-decision; Decision Conditions are post-authorisation. | `readiness.py`, `decision.py`. | G10/G11 negative tests. |
| **INV-05 — Disposition vs routing vs closure** | Terminal authority Decision, non-terminal route and administrative withdrawal remain distinct. | `scope_routing.py`, `authority.py`, `decision.py`, process history. | Scenario B/C no Decision; G11 explicit terminal path. |
| **INV-06 — Impact discovery vs scope** | Candidate discovery cannot become authorised scope automatically. | RRR-05 route + explicit Change Item command + Decision Scope validation. | IT-10; Scenario B; G11. |
| **INV-07 — Decision lineage** | Decision preserves exact baseline/overlay/execution/change revisions. | `decision.py`, `history_and_views.py`. | G11/G12; `decision_DEC-A01_basis.json`. |
| **INV-08 — Evidence transferability** | Predecessor evidence needs explicit successor applicability conclusion. | `assessment.py`. | G07 Evidence Use tests; Scenario A/B. |
| **INV-09 — Applicability vs effectivity** | Where and when remain separate dimensions. | Bounded payloads and overlay/source representations. | G01/G04 fixtures and tests. |
| **INV-10 — Integration projection** | Prototype DB is not represented as an enterprise source of truth. | Architecture boundary; frozen source projection and immutable snapshots. | Documentation/non-claim; historical reconstruction verifies snapshot dependence. |
| **INV-11 — Proposal change vs baseline change** | New proposal cycle requires new overlay/execution, not automatically new baseline. | `baseline.py`, Scenario B orchestration. | G08/G09/G14; `BL-B01` reuse. |

## 4.1 Key Logical Information Model assurance invariants

The implementation directly reflects or structurally represents the following LIM invariants because they are essential to deterministic execution:

- **LIM-INV-03 / 14:** baseline and Evidence state are historically reconstructible;
- **LIM-INV-07 / 08:** Change Item identity/revision and proposal lifecycle are separate;
- **LIM-INV-09 / 10:** overlay membership and overlay-local identity are explicit and immutable;
- **LIM-INV-12:** Impact Candidate provenance is relationally structured and permits multiple provenance records and paths; the frozen scenario oracles use one provenance record per candidate;
- **LIM-INV-15 / 17:** completed supporting Assessments lock; reuse is execution-relative;
- **LIM-INV-18 / 19:** Gate B is obligation-driven and separate from Authorisation Eligibility;
- **LIM-INV-21 / 23:** routing is not Decision; Decision lineage is explicit;
- **LIM-INV-24:** the six release-critical IT-16 lineage families are actively rejected cross-case, with additional bounded cross-case guards in earlier gates; this pack does not claim an exhaustive proof of every possible association named by the invariant.

The LIM's **IR-01–IR-51** remain the authoritative integrity catalogue. The implementation uses relational constraints, application validation, immutable snapshots and database triggers to enforce the subset required by the bounded scenarios and release-critical negative tests.

---

# 5. Deterministic rule traceability — RRR-01 to RRR-06

| Rule | Frozen result | Implementation | Primary test | Scenario evidence |
|---|---|---|---|---|
| **RRR-01** | Material characteristic change → Product Engineering obligation; `REQ-001` or `REQ-004` according to bounded applicability relation. | [`routing.py`](../../src/plm_ref/application/routing.py), [`rules/rrr_v01.py`](../../src/plm_ref/rules/rrr_v01.py). | [`test_g06_routing.py`](../../tests/test_g06_routing.py). | A: `AO-A01`; B1: `AO-B01`; B2: `AO-B21`; C: `AO-C01`. |
| **RRR-02** | Material characteristic change → Validation / `REQ-002`; execution-level obligation allowed when no candidate exists. | same routing/rule modules. | G06; G09 retained fulfilment. | B2 `AO-B23` has null candidate and is fulfilled by retained `ASM-B02`. |
| **RRR-03** | Material characteristic change → Manufacturing / `REQ-003`. | same routing/rule modules. | G06/G09. | B2 `AO-B22` remains unsatisfied. |
| **RRR-04** | Exact supplier-related trigger → Purchasing/Cost obligation; execution-level null-candidate obligation allowed. | same routing/rule modules. | G06/G09. | B2 `AO-B24` fulfilled by retained `ASM-B04`. |
| **RRR-05** | Structured applicability mismatch + `REQ-004 = Not Satisfied` + no applicability Change Item → `Scope Revision Required`. It never creates a Change Item. | [`scope_routing.py`](../../src/plm_ref/application/scope_routing.py), rule functions. | [`test_g08_scope_route.py`](../../tests/test_g08_scope_route.py); IT-10. | `HIST-B01`; explicit later `CI-B02:r1`. |
| **RRR-06** | Exact trigger mapping derives `Standard` or `Elevated` required authority. | [`authority.py`](../../src/plm_ref/application/authority.py), version-bound rule implementation. | [`test_g10_readiness_authority.py`](../../tests/test_g10_readiness_authority.py). | A = Standard; C = Elevated → `HIST-C01`. |

Rule assurance boundaries:

- the rules use exact structured inputs, not free-text semantic interpretation;
- unknown required inputs fail closed rather than being treated as a negative result;
- rules calculate readiness/routing/authority but do not autonomously select a terminal engineering outcome;
- the applicability grammar remains deliberately bounded and is not a general configuration solver.

---

# 6. Acceptance-gate traceability — G00 to G14

| Gate | Implementation increment | Primary test | Assurance purpose |
|---|---|---|---|
| **G00** | Bootstrap and deterministic runtime | [`test_g00_bootstrap.py`](../../tests/test_g00_bootstrap.py) | Import/runtime, Alembic, FK enforcement, CLI, API import. |
| **G01** | Persistence foundation / source projection | [`test_g01_source_projection.py`](../../tests/test_g01_source_projection.py) | Exact shared source identities, FK/uniqueness constraints. |
| **G02** | Change Case, Change Item, Gate A | [`test_g02_change_case_gate_a.py`](../../tests/test_g02_change_case_gate_a.py) | Gate A sequencing and target identification without baseline dependency. |
| **G03** | Baseline creation and Product Version immutability | [`test_g03_baseline.py`](../../tests/test_g03_baseline.py) | Exact baselines, atomicity, reuse predicate, application + DB immutability. |
| **G04** | Overlay / Overlay Execution Eligibility | [`test_g04_overlay.py`](../../tests/test_g04_overlay.py) | Baseline-relative target validation, exact overlay membership, successor materialisation. |
| **G05** | Bounded impact execution / provenance | [`test_g05_impact_execution.py`](../../tests/test_g05_impact_execution.py) | Case-local lineage, exact candidate/provenance persistence, path validation, atomic failure. |
| **G06** | `RRR-01..04` routing | [`test_g06_routing.py`](../../tests/test_g06_routing.py) | Exact obligations, null-candidate obligations, routing atomicity. |
| **G07** | Assessment / Evidence Use / lock | [`test_g07_assessment.py`](../../tests/test_g07_assessment.py) | Requirement Conclusions, Evidence transferability, complete Assessment lock boundary. |
| **G08** | Scope route / explicit Scenario B amendment | [`test_g08_scope_route.py`](../../tests/test_g08_scope_route.py) | `RRR-05`, `HIST-B01`, no automatic Change Item, baseline reuse route. |
| **G09** | Assessment reuse / retained fulfilment | [`test_g09_assessment_reuse.py`](../../tests/test_g09_assessment_reuse.py) | Exact Invalidated / Revalidation Required / Retained classification and retained fulfilment without historical mutation. |
| **G10** | Gate B / Eligibility / authority | [`test_g10_readiness_authority.py`](../../tests/test_g10_readiness_authority.py) | Completeness vs substantive eligibility vs authority; Scenario C escalation. |
| **G11** | Terminal Decision / case closure | [`test_g11_terminal_decision.py`](../../tests/test_g11_terminal_decision.py) | Explicit authority command, complete support/scope validation, `DEC-A01`. |
| **G12** | Historical reconstruction / Handover | [`test_g12_history_and_handover.py`](../../tests/test_g12_history_and_handover.py) | Reconstruct immutable Decision basis; derive Handover rather than persist it. |
| **G13** | CLI / FastAPI / scenario runner | [`test_g13_interfaces.py`](../../tests/test_g13_interfaces.py) | Thin interfaces over the same application services; no generic immutable-record CRUD. |
| **G14** | Full oracle verification / evidence | [`test_g14_oracle_verification.py`](../../tests/test_g14_oracle_verification.py) | Independent A/B/C oracle comparison, cross-scenario assertions, integrity injections, historical reconstruction. |

Recorded baseline result: **G00–G14 = 15/15 PASS**, with **185 pytest tests passed** and `plm-ref verify all` returning exit `0` at verified implementation commit `7a5733f…`.

---

# 7. Release-critical integrity traceability — IT-01 to IT-16

| IT | Release-critical property | Primary verification location | Expected / recorded result |
|---|---|---|---|
| **IT-01** | Gate A is baseline-independent. | `test_g02_change_case_gate_a.py` | Gate A can pass before baseline creation. |
| **IT-02** | Overlay execution eligibility requires selected baseline-relative state. | `test_g04_overlay.py` | Invalid/missing baseline-relative state blocks execution. |
| **IT-03** | Baselined Product Version application UPDATE/DELETE rejection. | `test_g03_baseline.py` | Rejected. |
| **IT-04** | Baselined Product Version direct-SQL UPDATE/DELETE rejection. | `test_g03_baseline.py` + DB trigger. | Rejected at SQLite layer. |
| **IT-05** | Product Version lock does not prevent overlay successor materialisation. | `test_g03_baseline.py`, `test_g04_overlay.py` | Overlay-local successor succeeds; source Product Version unchanged. |
| **IT-06** | Locked Assessment semantic children are immutable. | `test_g07_assessment.py` | INSERT/UPDATE/DELETE attempts rejected. |
| **IT-07** | Retained later fulfilment does not mutate historical Assessment. | `test_g09_assessment_reuse.py` | `AO-B23/B24` link to retained Assessment while canonical historical state remains identical. |
| **IT-08** | Invalidated / Revalidation Required Assessment cannot fulfil later mandatory obligation. | `test_g09_assessment_reuse.py` | Rejected. |
| **IT-09** | Routing is atomic. | `test_g06_routing.py` | Failure cannot coexist with a completed partial positive obligation set. |
| **IT-10** | `RRR-05` cannot create Change Item. | `test_g08_scope_route.py` | `HIST-B01` exists before explicit `CI-B02:r1`. |
| **IT-11** | Gate B completeness is separate from Authorisation Eligibility. | `test_g10_readiness_authority.py` | Complete package can still be substantively Blocked in bounded test fixture. |
| **IT-12** | Authority insufficiency is non-terminal. | `test_g10_readiness_authority.py` | Scenario C escalates; no Decision Record; case remains Decision Ready. |
| **IT-13** | Explicit Decision command is required. | `test_g11_terminal_decision.py` | No Decision before authority command; `DEC-A01` after valid command. |
| **IT-14** | Decision Support Assessments cover mandatory obligations. | `test_g11_terminal_decision.py` | Missing support rejects entire Decision transaction. |
| **IT-15** | Historical reconstruction ignores later live source representation. | `test_g12_history_and_handover.py` | Reconstructed `DEC-A01` basis remains stored snapshots/locked records. |
| **IT-16** | Cross-case lineage injection is rejected across six families. | `test_g14_oracle_verification.py`; [`integrity_results.json`](../../evidence/integrity_results.json) | Execution baseline/overlay, candidate provenance, fulfilment, reuse, Decision support and Decision Scope injections all attempted, rejected and PASS. |

The final `verify all` summary names six verification groups. The label **Integrity suite** in that summary is the final-run integrity grouping and does not by itself enumerate every IT-01–IT-15 test. The broader pytest regression provides the complete acceptance/integrity coverage; the G14 runner actively records the six IT-16 cross-case injection families.

---

# 8. Scenario-to-evidence map

| Scenario | Architectural proposition | Oracle / evidence |
|---|---|---|
| **A — Authorised change** | Complete package + permitted eligibility + sufficient Standard authority + explicit authority action produces exact Decision and derived Handover. | [`scenario_a_actual.json`](../../evidence/scenario_a_actual.json), [`scenario_a_diff.json`](../../evidence/scenario_a_diff.json), [`decision_DEC-A01_basis.json`](../../evidence/decision_DEC-A01_basis.json). |
| **B — Scope amendment and selective reuse** | Discovered impact is not authorised scope; explicit scope change creates new overlay/execution; baseline can be reused; Assessment reuse is execution-relative; incomplete new obligations stop progression. | [`scenario_b_actual.json`](../../evidence/scenario_b_actual.json), [`scenario_b_diff.json`](../../evidence/scenario_b_diff.json). |
| **C — Authority escalation** | Decision-package completeness and substantive eligibility do not imply authority sufficiency; escalation remains non-terminal. | [`scenario_c_actual.json`](../../evidence/scenario_c_actual.json), [`scenario_c_diff.json`](../../evidence/scenario_c_diff.json). |
| **Cross-case integrity** | Case-local lineage is actively enforced rather than merely documented. | [`integrity_results.json`](../../evidence/integrity_results.json). |
| **Whole release baseline** | All final verification groups pass and evidence generation is deterministic at the verified baseline. | [`verification_summary.md`](../../evidence/verification_summary.md) plus recorded repeated byte-identical run. |

The expected scenario oracle is separate from the bounded impact-result fixture and from the actual persisted/derived output. This separation prevents the final comparator from simply validating an object against itself.

---

# 9. Public claims and limitations

## 9.1 Claims supported by the verified baseline

The release may state that the bounded synthetic reference case demonstrates:

1. an architecture-first translation from an engineering product-change problem to explicit business, process, information, rule and decision semantics;
2. deterministic execution of the frozen Scenarios A–C;
3. explicit separation of current state, Assessment Baseline, proposed-state Overlay, Impact Candidate, Assessment, Decision Scope, routing history and terminal Decision;
4. immutable historical baselines, Evidence-use snapshots and locked decision-supporting Assessments sufficient for historical reconstruction;
5. proposal-scope revision without automatic baseline revision;
6. execution-relative Assessment reuse with Retained / Revalidation Required / Invalidated semantics;
7. explicit separation of Gate B package completeness, Authorisation Eligibility and authority sufficiency;
8. non-terminal authority escalation when current authority is insufficient;
9. terminal Decision persistence only after explicit authority disposition input;
10. case-local lineage with active rejection of six IT-16 cross-case injection families;
11. a derived Handover View for the authorised scenario rather than an independently persisted Handover business object;
12. verified implementation results of G00–G14 PASS, 185 pytest tests passed, `plm-ref verify all` exit 0, and repeated byte-identical evidence at the recorded implementation baseline.

## 9.2 Claims explicitly not supported

The release must not claim:

- enterprise PLM completeness or fidelity to any company-specific process;
- a production-ready PLM platform or source of record;
- a general arbitrary-graph impact-discovery capability;
- a complete configuration-management or configuration-solver implementation;
- enterprise source authority, freshness, precedence or conflict-resolution governance;
- plant, production, stock, service, release or downstream execution semantics;
- a generic workflow or approval engine;
- an approval hierarchy beyond the synthetic `Standard < Elevated` ordering;
- automated engineering judgement or automated terminal approval;
- AI/LLM runtime capability;
- production-scale concurrency, distributed architecture, enterprise authentication/RBAC or cloud deployment;
- proof that a real engineering product change is technically correct or safe;
- proof that the frozen synthetic routing rules are appropriate enterprise rules;
- an implemented Process Authority override workflow or executable Change Owner withdrawal use case.

## 9.3 Prototype-specific implementation limitations

The following are deliberate implementation choices rather than architecture deficiencies:

- SQLite and a synchronous modular monolith are used for inspectability and deterministic local execution;
- impact results are supplied through a frozen-fixture adapter behind an explicit port;
- applicability parsing supports only the bounded exact-equality conjunction grammar required by the scenarios;
- scenario IDs and timestamps are deterministic fixture values;
- no background jobs or distributed coordination are required;
- dependency locking and CI reproducibility are release-governance work for Session 4 and are not yet part of the verified implementation claim.

---

# 10. Reviewer guide

## 10.1 Fifteen-minute assurance review

1. Read the [architecture index](../00-architecture-index.md) through the authority chain and scenario summary.
2. Read §9 of this pack: public claims and limitations.
3. Inspect the three scenario diff files and [`verification_summary.md`](../../evidence/verification_summary.md).
4. Inspect [`integrity_results.json`](../../evidence/integrity_results.json) for active IT-16 rejection evidence.

Expected conclusion: understand exactly what is claimed, what is not claimed and which executable evidence supports the bounded claim.

## 10.2 Forty-five-minute architecture/assurance review

1. Follow the fifteen-minute path.
2. Select one semantic chain from each category:
   - baseline/overlay — BR-04/05/09/10;
   - evidence/Assessment — BR-17/18/19;
   - scope/reuse — BR-13/14/29;
   - readiness/authority — BR-21/23/24;
   - decision lineage — BR-26/27/28.
3. Follow each selected row in §3 from frozen meaning to code, test and evidence.
4. Read the RRR map in §5 and acceptance/integrity maps in §§6–7.

Expected conclusion: confirm that the implementation is subordinate to and traceable from frozen business meaning.

## 10.3 Deep technical review

1. Read all six frozen artefacts in precedence order.
2. Inspect the exact scenario input / impact-fixture / expected-oracle separation under [`../../data/`](../../data/).
3. Inspect application services, deterministic rule code, DB model/guards and migrations.
4. Inspect G00–G14 test modules and compare them to the Implementation Plan acceptance gates.
5. Inspect the committed actual/diff/evidence files.
6. Reconstruct `DEC-A01` using the Decision-basis evidence and verify that its meaning does not require mutable live source state.
7. Challenge IT-16 case-local lineage families and the Scenario B retained-assessment semantics.

Expected conclusion: determine whether any public claim lacks a deterministic path to implementation control and evidence.

## 10.4 Blocker-only review questions

A release-blocking finding should be raised only when one of the following is demonstrated:

1. a public claim contradicts a frozen authoritative artefact;
2. a frozen architecture requirement has no implementable or verifiable path required by Scenarios A–C;
3. the implementation can produce a frozen scenario result only by silently changing upstream meaning;
4. an integrity control allows a prohibited mutation or cross-case link that invalidates the bounded assurance claim;
5. the expected oracle and actual result are not independently separated;
6. historical Decision reconstruction depends on mutable current source state;
7. a route is incorrectly represented as a terminal Decision, or vice versa;
8. the public package overstates enterprise, general impact-discovery, production or automated-decision capability.

Presentation preferences, alternative enterprise modelling approaches and feature requests outside the frozen boundary are not release blockers for v0.1.

---

# 11. Compact Solution-Architecture decision index

The authoritative decisions remain Section 35 of the frozen Solution Architecture. This table is navigation only.

| Decision | Frozen choice | Why it matters to assurance | Implementation anchor |
|---|---|---|---|
| **SA-DEC-01** | Modular monolith. | Keeps cross-module integrity and transactions inspectable without distributed-system noise. | [`src/plm_ref/`](../../src/plm_ref/) |
| **SA-DEC-02** | Relational persistence with SQLite + SQLAlchemy. | Lineage-heavy bounded model maps directly to enforceable FK/uniqueness/transaction controls. | [`infrastructure/db/`](../../src/plm_ref/infrastructure/db/), [`migrations/`](../../migrations/) |
| **SA-DEC-03** | Relational entities + validated JSON for bounded snapshots/value objects. | Preserves historical snapshot fidelity without inventing new domain entities. | [`models.py`](../../src/plm_ref/infrastructure/db/models.py) plus validated application/fixture payloads. |
| **SA-DEC-04** | Explicit deterministic Python rules. | Critical routing/readiness logic remains visible, testable and version-bound. | [`rules/`](../../src/plm_ref/rules/), [`routing.py`](../../src/plm_ref/application/routing.py) |
| **SA-DEC-05** | Bounded impact-analysis port with frozen fixture adapter. | Avoids falsely claiming a general impact-discovery algorithm while proving downstream architecture. | [`impact_analysis.py`](../../src/plm_ref/application/impact_analysis.py), [`port.py`](../../src/plm_ref/infrastructure/impact/port.py), [`frozen_fixture_adapter.py`](../../src/plm_ref/infrastructure/impact/frozen_fixture_adapter.py). |
| **SA-DEC-06** | No automated terminal Decision. | Rules determine permission; explicit authority action supplies the outcome. | [`decision.py`](../../src/plm_ref/application/decision.py), G11/IT-13. |
| **SA-DEC-07** | Dual immutability enforcement. | Release-critical historical state is protected both by application logic and SQLite triggers. | baseline/assessment/decision services + migrations. |
| **SA-DEC-08** | Handover is derived, not persisted. | Prevents an unnecessary competing lifecycle object and preserves frozen semantics. | [`history_and_views.py`](../../src/plm_ref/application/history_and_views.py), G12. |
| **SA-DEC-09** | Gate/readiness values are derived projections, not generic persisted business objects. | Keeps completeness/eligibility/authority calculations distinct from auditable business records. | [`readiness.py`](../../src/plm_ref/application/readiness.py), [`authority.py`](../../src/plm_ref/application/authority.py). |
| **SA-DEC-10** | Rule-set version binding. | Historical rule meaning cannot silently drift when later rules evolve. | `RRR-v0.1` stored on executions; registry dispatch in [`routing.py`](../../src/plm_ref/application/routing.py) and [`rrr_v01.py`](../../src/plm_ref/rules/rrr_v01.py). |

---

# 12. Assurance conclusion

For the frozen reference-case boundary, the architecture-to-evidence chain is complete enough to support the public claim:

> The synthetic Product Change Impact Assessment & Decision Readiness case is specified as an architecture first and implemented as a deterministic proof of that architecture. The verified implementation reproduces the exact frozen Scenario A–C outcomes, preserves release-critical semantic distinctions and historical lineage, and actively rejects the defined cross-case integrity injections.

The evidence does **not** extend that claim to enterprise PLM completeness, production operation, general impact discovery or automated engineering judgement.

The next release-governance work is dependency/reproducibility control, CI, licensing/citation/changelog metadata and final evidence hashing. None of those tasks authorises a change to the frozen PLM semantics.
