"""Deterministic INC-13 orchestration over existing application services."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from plm_ref.application.assessment import AssessmentCompletionInput, EvidenceUseInput, RequirementConclusionInput, complete_assessment
from plm_ref.application.assessment_reuse import RetainedFulfilment, classify_assessment_reuse, fulfil_from_retained_assessments
from plm_ref.application.authority import EscalationCommand, evaluate_authority, persist_escalation
from plm_ref.application.baseline import BaselineReuseInputs, load_frozen_baseline_fixture, reuse_assessment_baseline
from plm_ref.application.change_case import ChangeCaseInput, ChangeItemRevisionInput, ProposalStateInput, create_change_case, create_change_item
from plm_ref.application.decision import DecisionCommand, DecisionScopeInput, DecisionSupportInput, persist_terminal_decision
from plm_ref.application.gate_a import evaluate_gate_a
from plm_ref.application.impact_analysis import ImpactExecutionInput, execute_impact_analysis
from plm_ref.application.overlay import OverlayRevisionInput, create_overlay_revision
from plm_ref.application.readiness import derive_case_state, evaluate_authorisation_eligibility, evaluate_gate_b
from plm_ref.application.routing import route_impact_execution
from plm_ref.application.scope_routing import ScopeRouteCommand, evaluate_scope_route
from plm_ref.application.oracle_verification import (
    canonical_actual, compare_scenario, cross_scenario_results, load_expected,
    verify_historical_basis,
)
from plm_ref.application.source_projection import load_shared_source_fixture
from plm_ref.infrastructure.db.models import (
    Assessment, AssessmentObligation, AssessmentReuseClassification, ChangeCase, DecisionRecord,
    ImpactCandidate, ImpactCandidateProvenance, ImpactExecution, ProductElement,
)
from plm_ref.domain.errors import AssessmentCompletionError, AssessmentReuseError, ImpactExecutionLineageError
from plm_ref.infrastructure.impact.port import ImpactCandidateSpec
from plm_ref.infrastructure.db.session import create_sqlite_engine
from plm_ref.infrastructure.impact.frozen_fixture_adapter import FrozenFixtureImpactAdapter


def _dt(value: str) -> datetime: return datetime.fromisoformat(value.replace("Z", "+00:00"))

_S = {
 "A": ("CHG-A01","CI-A01","BL-A01","OV-A01","IAX-A01","19:00","19:02","19:03","19:20","19:25","Change Owner A","MC-A-01",'CoolingType = "Liquid"',"Synthetic supplier process change","Cooling Plate supplier-process material characteristic update","Update one Cooling Plate material characteristic while preserving intended function and current applicability.","Synthetic supplier process change."),
 "B": ("CHG-B01","CI-B01","BL-B01","OV-B01","IAX-B01","20:10","20:12","20:13","20:30","20:35","Change Owner B","MC-B-01",'CoolingType = "Liquid" AND PackFamily = "LongRange"',"Synthetic supplier process change","Cooling Plate material revision requiring applicability scope amendment","Evaluate a proposed Cooling Plate material characteristic whose validated configuration scope is narrower than the current occurrence applicability.","Synthetic supplier process change with a narrower validated configuration scope."),
 "C": ("CHG-C01","CI-C01","BL-C01","OV-C01","IAX-C01","21:30","21:32","21:33","21:50","21:55","Change Owner C","MC-C-01",'CoolingType = "Liquid"',"Synthetic supplier process change with elevated authority classification","Cooling Plate change requiring Elevated authority","Evaluate a bounded Cooling Plate product-state revision whose decision route requires Elevated authority.","Synthetic change prepared under a route that requires Elevated authority."),}
_DOMAINS=("Product Engineering","Validation","Manufacturing","Purchasing/Cost")
_ROLES=("Product Engineer","Validation Engineer","Manufacturing Engineer","Purchasing/Cost Assessor")
_EVIDENCE=("EV-003","EV-001","EV-002","EV-004")
_A_STATEMENTS=("Proposed material characteristic changes, but intended function and declared configuration scope remain unchanged.","Predecessor validation evidence is accepted as applicable to the proposed successor for this bounded synthetic change.","Predecessor manufacturing evidence is accepted as applicable to the proposed successor for this bounded synthetic change.","Supplier/cost impact is documented and non-blocking.")

def _v(s: str):
    try: return _S[s.upper()]
    except KeyError as e: raise ValueError("scenario must be A, B, or C") from e
def _time(hm: str) -> datetime: return _dt(f"2026-08-25T{hm}:00Z")

def load_scenario(session: Session, scenario: str) -> str:
    """Load shared source plus explicit case/change-item input, never an oracle."""
    s=scenario.upper(); case,item,_,_,_,created,revision,proposal,*tail=_v(s)
    if session.get(ChangeCase,case): return case
    owner,material,scope,trigger,title,rationale,reason=tail[-7:]
    # An injection harness may load two independent cases into one database.  The
    # shared projection is source state, so load it once rather than duplicating it.
    if session.get(ProductElement, "PE-002") is None:
        load_shared_source_fixture(session)
    create_change_case(session,ChangeCaseInput(change_case_id=case,title=title,trigger=trigger,rationale=rationale,change_owner=owner,case_state="Open",process_iteration=1,created_at=_time(created),closed_at=None))
    create_change_item(session,ChangeItemRevisionInput(change_item_id=item,change_item_revision="r1",change_case_id=case,action="Revise Product State",target_type="Product Version",target_id="PV-003",current_state_reference={"product_version_id":"PV-003","revision":"A","iteration":"1"},proposed_state_payload={"product_element_id":"PE-003","proposed_revision":"B","proposed_iteration":"1","supersedes_product_version_id":"PV-003","material_characteristic":material,"validated_configuration_scope":scope,"intended_function_change":False},reason=reason,owner=owner,configuration_context_id="CFG-001",intended_effectivity={"effectivity_type":"Planned Engineering Effective Date","planned_effective_date":"2026-11-01"},revision_created_at=_time(revision)),ProposalStateInput(change_item_id=item,change_case_id=case,selected_revision="r1",proposal_state="Active",state_changed_at=_time(proposal),state_changed_by=owner))
    return case

def _execute(session: Session,s: str) -> str:
    case,item,baseline,overlay,execution,created,revision,proposal,overlay_at,execution_at,owner,*_= _v(s)
    load_scenario(session,s); evaluate_gate_a(session,case); load_frozen_baseline_fixture(session,s)
    create_overlay_revision(session,baseline,OverlayRevisionInput(overlay_revision_id=overlay,change_case_id=case,created_at=_time(overlay_at)))
    command_=ImpactExecutionInput(impact_execution_id=execution,change_case_id=case,assessment_baseline_id=baseline,overlay_revision_id=overlay,rule_set_version="RRR-v0.1",execution_timestamp=_time(execution_at))
    execute_impact_analysis(session,command_,FrozenFixtureImpactAdapter()); route_impact_execution(session,execution)
    return execution

def _complete(session: Session,s: str, execution: str) -> None:
    case,_,_,_,_,*_= _v(s)
    times={"A":("19:40","19:42","19:44","19:46"),"B":("20:50","20:52","20:54","20:56"),"C":("22:10","22:12","22:14","22:16")}[s]
    reqs=("REQ-004","REQ-002","REQ-003") if s=="B" else ("REQ-001","REQ-002","REQ-003")
    bstat=('The proposed state is validated only for `CoolingType = "Liquid" AND PackFamily = "LongRange"`, while `PSO-002` currently applies to all `CoolingType = "Liquid"` configurations. The occurrence applicability must therefore be changed explicitly before the proposal can proceed to terminal decision.',"Validation evidence is acceptable for the bounded technical state evaluated in the first execution.","Manufacturing evidence is acceptable for the bounded technical state evaluated in the first execution.","Supplier/cost impact remains documented and non-blocking.")
    for i in range(1,5):
        req=reqs[i-1] if i<=3 else None; ev=_EVIDENCE[i-1]
        complete_assessment(session,AssessmentCompletionInput(f"ASM-{s}0{i}",case,execution,_DOMAINS[i-1],"Relevant","No Objection with Conditions" if s=="B" and i==1 else "No Objection",(bstat if s=="B" else _A_STATEMENTS)[i-1],f"{_ROLES[i-1]} {s}",_time(times[i-1]),(f"IC-{s}0{i}",),() if req is None else (RequirementConclusionInput(f"ARC-{s}0{i}",req,"Not Satisfied" if s=="B" and i==1 else "Satisfied"),),(EvidenceUseInput(f"AEU-{s}0{i}",ev,f"OVOBJ-{s}01-PV","Accepted as Applicable",f"{ev}@2026-08-25T18:10:00Z"),),(f"AO-{s}0{i}",)))

def _run_b02(session: Session) -> None:
    evaluate_scope_route(session,ScopeRouteCommand("IAX-B01","HIST-B01",_time("21:00"),"Change Owner B","Domain Assessment","Scope Confirmation","ASM-B01 concluded that PSO-002 applicability must change explicitly; discovered impact is not authorised scope."))
    create_change_item(session,ChangeItemRevisionInput(change_item_id="CI-B02",change_item_revision="r1",change_case_id="CHG-B01",action="Change Applicability",target_type="Product Structure Occurrence",target_id="PSO-002",current_state_reference={"occurrence_id":"PSO-002","applicability_rule_id":"APP-001","applicability_rule_version":"1"},proposed_state_payload={"applicability_rule":{"rule_id":"APP-B02","expression":'CoolingType = "Liquid" AND PackFamily = "LongRange"',"rule_version":"1"}},reason="Align occurrence applicability with the validated scope of the proposed Cooling Plate state.",owner="Change Owner B",configuration_context_id="CFG-001",intended_effectivity={"effectivity_type":"Planned Engineering Effective Date","planned_effective_date":"2026-11-01"},revision_created_at=_time("21:05")),ProposalStateInput(change_item_id="CI-B02",change_case_id="CHG-B01",selected_revision="r1",proposal_state="Active",state_changed_at=_time("21:06"),state_changed_by="Change Owner B"))
    evaluate_gate_a(session,"CHG-B01"); reuse_assessment_baseline(session,"BL-B01","CHG-B01",BaselineReuseInputs(authoritative_current_state_unchanged=True,baseline_scope_still_sufficient=True,configuration_context_still_valid=True,effectivity_context_still_valid=True,extraction_basis_still_accepted=True))
    create_overlay_revision(session,"BL-B01",OverlayRevisionInput(overlay_revision_id="OV-B02",change_case_id="CHG-B01",created_at=_time("21:10")),local_object_ids={"CI-B01":"OVOBJ-B02-PV","CI-B02":"OVOBJ-B02-PSO"})
    execute_impact_analysis(session,ImpactExecutionInput(impact_execution_id="IAX-B02",change_case_id="CHG-B01",assessment_baseline_id="BL-B01",overlay_revision_id="OV-B02",rule_set_version="RRR-v0.1",execution_timestamp=_time("21:15")),FrozenFixtureImpactAdapter()); route_impact_execution(session,"IAX-B02")
    classify_assessment_reuse(session,"IAX-B02"); fulfil_from_retained_assessments(session,(RetainedFulfilment("AO-B23","ASM-B02"),RetainedFulfilment("AO-B24","ASM-B04")))

def run_scenario(session: Session, scenario: str) -> str:
    s=scenario.upper(); case=_v(s)[0]
    if session.get(ImpactExecution,_v(s)[4]): raise ValueError(f"scenario {s} has already run; reset before rerunning")
    execution=_execute(session,s); _complete(session,s,execution)
    if s=="A":
        gate=evaluate_gate_b(session,execution); eligibility=evaluate_authorisation_eligibility(session,gate); derive_case_state(session,gate)
        if evaluate_authority(gate,eligibility).decision_permitted is not True: raise ValueError("frozen A authority disposition failed")
        persist_terminal_decision(session,DecisionCommand("DEC-A01","CHG-A01","BL-A01","OV-A01","IAX-A01","Authorised for Downstream Processing","Decision package is complete, substantive authorisation blockers are absent, and Standard authority is sufficient.","Standard Decision Authority A",_time("20:00"),(DecisionScopeInput("CI-A01","r1"),),tuple(DecisionSupportInput(f"DSA-A0{i}",f"ASM-A0{i}") for i in range(1,5)),()))
    elif s=="B":
        _run_b02(session)
        derive_case_state(session, evaluate_gate_b(session, "IAX-B02"))
    else:
        gate=evaluate_gate_b(session,execution); eligibility=evaluate_authorisation_eligibility(session,gate); derive_case_state(session,gate)
        persist_escalation(session,evaluate_authority(gate,eligibility),EscalationCommand("HIST-C01",_time("22:20"),"Decision Coordinator C"))
    return case

def reset_database(database_path: str | Path) -> Engine:
    path=Path(database_path); config=Config("alembic.ini"); config.set_main_option("sqlalchemy.url",f"sqlite+pysqlite:///{path}")
    if path.exists(): command.downgrade(config,"base")
    command.upgrade(config,"head")
    return create_sqlite_engine(path)


def _it16_command(decision_id: str, scope: tuple[DecisionScopeInput, ...], support: tuple[DecisionSupportInput, ...]) -> DecisionCommand:
    """A bounded A command used only to exercise Decision case-local guards."""
    return DecisionCommand(
        decision_id, "CHG-A01", "BL-A01", "OV-A01", "IAX-A01",
        "Authorised for Downstream Processing",
        "IT-16 cross-case injection must be rejected.",
        "Standard Decision Authority A", _time("20:00"), scope, support, (),
    )


def it16_injection_results(database_path: str | Path) -> dict[str, dict[str, bool]]:
    """Attempt each frozen cross-case mutation against real application services.

    This deliberately uses a fresh database and stops before A's terminal Decision;
    it is verification scaffolding, not scenario state or an alternative workflow.
    """
    engine = reset_database(database_path)
    try:
        with Session(engine) as session, session.begin():
            _execute(session, "A"); _complete(session, "A", "IAX-A01")
            _execute(session, "C"); _complete(session, "C", "IAX-C01")
            results: dict[str, dict[str, bool]] = {}

            # 1. A execution cannot select C's baseline.
            rejected = False
            try:
                execute_impact_analysis(session, ImpactExecutionInput(
                    impact_execution_id="IAX-IT16-X", change_case_id="CHG-A01",
                    assessment_baseline_id="BL-C01", overlay_revision_id="OV-A01",
                    rule_set_version="RRR-v0.1", execution_timestamp=_time("23:00"),
                ), FrozenFixtureImpactAdapter())
            except ImpactExecutionLineageError:
                rejected = True
            results["IT-16 execution baseline/overlay"] = {
                "attempted": True, "rejected": rejected,
                "passed": rejected and session.get(ImpactExecution, "IAX-IT16-X") is None,
            }

            # 2. Adapter provenance naming CI-C01 for an A overlay is failed atomically.
            class _CrossCaseProvenanceAdapter:
                def run(self, _context):
                    return (ImpactCandidateSpec.model_validate({
                        "impact_candidate_id": "IC-IT16-X", "candidate_type": "Product Version",
                        "candidate_reference": "PV-003", "affected_domain": "Validation",
                        "provenance": ({
                            "impact_candidate_provenance_id": "ICP-IT16-X",
                            "change_item_id": "CI-C01", "change_item_revision": "r1",
                            "dependency_path": ({"sequence": 1, "source_reference": "BM-A01-01",
                                "relationship_type": "depends on", "target_reference": "BM-A01-02",
                                "state_context": "Current State"},),
                        },),
                    }),)
            execute_impact_analysis(session, ImpactExecutionInput(
                impact_execution_id="IAX-IT16-P", change_case_id="CHG-A01",
                assessment_baseline_id="BL-A01", overlay_revision_id="OV-A01",
                rule_set_version="RRR-v0.1", execution_timestamp=_time("23:01"),
            ), _CrossCaseProvenanceAdapter())
            failed = session.get(ImpactExecution, "IAX-IT16-P")
            rejected = failed is not None and failed.execution_status == "Failed"
            results["IT-16 candidate provenance"] = {
                "attempted": True, "rejected": rejected,
                "passed": rejected and session.get(ImpactCandidate, "IC-IT16-X") is None
                and session.get(ImpactCandidateProvenance, "ICP-IT16-X") is None,
            }

            # 3. C cannot complete an Assessment against an A obligation.
            session.add(AssessmentObligation(
                assessment_obligation_id="AO-IT16-F", impact_execution_id="IAX-A01",
                impact_candidate_id="IC-A02", domain="Validation", requirement_id="REQ-002",
                mandatory=True, fulfilled_by_assessment_id=None, routing_rule_reference="RRR-02",
            ))
            session.flush()
            rejected = False
            try:
                complete_assessment(session, AssessmentCompletionInput(
                    "ASM-IT16-F", "CHG-C01", "IAX-C01", "Validation", "Relevant",
                    "No Objection", "Malformed cross-case IT-16 injection.",
                    "IT-16 Assessor", _time("23:02"), ("IC-C02",),
                    (RequirementConclusionInput("ARC-IT16-F", "REQ-002", "Satisfied"),),
                    (EvidenceUseInput("AEU-IT16-F", "EV-001", "OVOBJ-C01-PV",
                        "Accepted as Applicable", "EV-001@2026-08-25T18:10:00Z"),),
                    ("AO-IT16-F",),
                ))
            except AssessmentCompletionError:
                rejected = True
            results["IT-16 Assessment fulfilment"] = {
                "attempted": True, "rejected": rejected,
                "passed": rejected and session.get(Assessment, "ASM-IT16-F") is None
                and session.get(AssessmentObligation, "AO-IT16-F").fulfilled_by_assessment_id is None,
            }

            # 4. A directly injected C-to-A Retained classification cannot be used
            # through the reuse service and is removed as invalid verification data.
            reuse_obligation = AssessmentObligation(
                assessment_obligation_id="AO-IT16-R", impact_execution_id="IAX-A01",
                impact_candidate_id="IC-A02", domain="Validation", requirement_id="REQ-002",
                mandatory=True, fulfilled_by_assessment_id=None, routing_rule_reference="RRR-02",
            )
            cross_classification = AssessmentReuseClassification(
                assessment_reuse_classification_id="ARU-IT16-R", assessment_id="ASM-C02",
                target_impact_execution_id="IAX-A01", classification="Retained",
                rationale="Malformed cross-case IT-16 reuse injection.",
            )
            session.add_all((reuse_obligation, cross_classification)); session.flush()
            reuse_rejected = False
            try:
                fulfil_from_retained_assessments(session, (RetainedFulfilment("AO-IT16-R", "ASM-C02"),))
            except AssessmentReuseError:
                reuse_rejected = True
            session.delete(cross_classification); session.flush()
            results["IT-16 Assessment reuse"] = {
                "attempted": True, "rejected": reuse_rejected,
                "passed": reuse_rejected and reuse_obligation.fulfilled_by_assessment_id is None
                and session.get(AssessmentReuseClassification, "ARU-IT16-R") is None,
            }

            correct_support = tuple(DecisionSupportInput(f"DSA-IT16-{i}", f"ASM-A0{i}") for i in range(1, 5))
            rejected = False
            try:
                bad_support = correct_support[:-1] + (DecisionSupportInput("DSA-IT16-X", "ASM-C04"),)
                persist_terminal_decision(session, _it16_command("DEC-IT16-S", (DecisionScopeInput("CI-A01", "r1"),), bad_support))
            except ValueError:
                rejected = True
            results["IT-16 Decision support"] = {
                "attempted": True, "rejected": rejected,
                "passed": rejected and session.get(DecisionRecord, "DEC-IT16-S") is None,
            }

            rejected = False
            try:
                persist_terminal_decision(session, _it16_command("DEC-IT16-C", (DecisionScopeInput("CI-C01", "r1"),), correct_support))
            except ValueError:
                rejected = True
            results["IT-16 Decision Scope"] = {
                "attempted": True, "rejected": rejected,
                "passed": rejected and session.get(DecisionRecord, "DEC-IT16-C") is None,
            }
            return results
    finally:
        engine.dispose()

def verify_all(database_path: str | Path, evidence_path: str | Path = "evidence") -> bool:
    """Run clean A/B/C oracle checks and write deterministic technical evidence."""
    import json
    evidence = Path(evidence_path)
    evidence.mkdir(parents=True, exist_ok=True)
    actuals: dict[str, dict] = {}; diffs: dict[str, list] = {}
    for s in ("A","B","C"):
        engine=reset_database(database_path)
        try:
            with Session(engine) as session,session.begin(): run_scenario(session,s)
            with Session(engine) as session:
                actuals[s], diffs[s] = compare_scenario(session, s)
        finally: engine.dispose()
    for s in ("A", "B", "C"):
        (evidence / f"scenario_{s.lower()}_actual.json").write_text(json.dumps(actuals[s], sort_keys=True, indent=2) + "\n", encoding="utf-8")
        (evidence / f"scenario_{s.lower()}_diff.json").write_text(json.dumps({"status": "PASS"} if not diffs[s] else {"status": "FAIL", "diffs": diffs[s]}, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    basis = actuals["A"]["derived"].get("historical_basis")
    (evidence / "decision_DEC-A01_basis.json").write_text(json.dumps(basis, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    cross = cross_scenario_results(actuals)
    # IT-16 is an active injection suite, not a post-hoc ID-prefix inspection.
    integrity = it16_injection_results(Path(database_path).with_name("it16_injections.db"))
    historical_diffs = verify_historical_basis(actuals["A"], load_expected("A"))
    groups = {"Scenario A oracle": not diffs["A"], "Scenario B oracle": not diffs["B"], "Scenario C oracle": not diffs["C"], "Cross-scenario assertions": all(result["passed"] for result in cross.values()), "Integrity suite": all(result["passed"] for result in integrity.values()), "Historical reconstruction": not historical_diffs}
    (evidence / "integrity_results.json").write_text(json.dumps({"groups": groups, "cross_scenario": cross, "integrity": integrity, "historical_diffs": historical_diffs}, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    summary = "\n".join(f"{key} = {'PASS' if value else 'FAIL'}" for key, value in groups.items()) + "\n"
    (evidence / "verification_summary.md").write_text(summary, encoding="utf-8")
    return all(groups.values())
