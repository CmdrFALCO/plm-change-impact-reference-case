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
from plm_ref.application.source_projection import load_shared_source_fixture
from plm_ref.infrastructure.db.models import ChangeCase, DecisionRecord, ImpactExecution
from plm_ref.infrastructure.db.session import create_sqlite_engine
from plm_ref.infrastructure.impact.frozen_fixture_adapter import FrozenFixtureImpactAdapter


def _dt(value: str) -> datetime: return datetime.fromisoformat(value.replace("Z", "+00:00"))

_S = {
 "A": ("CHG-A01","CI-A01","BL-A01","OV-A01","IAX-A01","19:00","19:02","19:03","19:20","19:25","Change Owner A","MC-A-01",'CoolingType = "Liquid"',"Synthetic supplier process change"),
 "B": ("CHG-B01","CI-B01","BL-B01","OV-B01","IAX-B01","20:10","20:12","20:13","20:30","20:35","Change Owner B","MC-B-01",'CoolingType = "Liquid" AND PackFamily = "LongRange"',"Synthetic supplier process change"),
 "C": ("CHG-C01","CI-C01","BL-C01","OV-C01","IAX-C01","21:30","21:32","21:33","21:50","21:55","Change Owner C","MC-C-01",'CoolingType = "Liquid"',"Synthetic supplier process change with elevated authority classification"),}
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
    owner,material,scope,trigger=tail[-4:]
    load_shared_source_fixture(session)
    create_change_case(session,ChangeCaseInput(change_case_id=case,title=f"{case} frozen case",trigger=trigger,rationale="Frozen scenario rationale.",change_owner=owner,case_state="Open",process_iteration=1,created_at=_time(created),closed_at=None))
    create_change_item(session,ChangeItemRevisionInput(change_item_id=item,change_item_revision="r1",change_case_id=case,action="Revise Product State",target_type="Product Version",target_id="PV-003",current_state_reference={"product_version_id":"PV-003","revision":"A","iteration":"1"},proposed_state_payload={"product_element_id":"PE-003","proposed_revision":"B","proposed_iteration":"1","supersedes_product_version_id":"PV-003","material_characteristic":material,"validated_configuration_scope":scope,"intended_function_change":False},reason="Frozen synthetic change.",owner=owner,configuration_context_id="CFG-001",intended_effectivity={"effectivity_type":"Planned Engineering Effective Date","planned_effective_date":"2026-11-01"},revision_created_at=_time(revision)),ProposalStateInput(change_item_id=item,change_case_id=case,selected_revision="r1",proposal_state="Active",state_changed_at=_time(proposal),state_changed_by=owner))
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
    elif s=="B": _run_b02(session)
    else:
        gate=evaluate_gate_b(session,execution); eligibility=evaluate_authorisation_eligibility(session,gate); derive_case_state(session,gate)
        persist_escalation(session,evaluate_authority(gate,eligibility),EscalationCommand("HIST-C01",_time("22:20"),"Standard Decision Authority C"))
    return case

def reset_database(database_path: str | Path) -> Engine:
    path=Path(database_path); config=Config("alembic.ini"); config.set_main_option("sqlalchemy.url",f"sqlite+pysqlite:///{path}")
    if path.exists(): command.downgrade(config,"base")
    command.upgrade(config,"head")
    return create_sqlite_engine(path)

def verify_all(database_path: str | Path) -> bool:
    # Verify independent clean runs; expected.yaml is deliberately never read.
    for s in ("A","B","C"):
        engine=reset_database(database_path)
        try:
            with Session(engine) as session,session.begin(): run_scenario(session,s)
            with Session(engine) as session:
                if s=="A" and session.get(DecisionRecord,"DEC-A01") is None: return False
                if s!="A" and session.query(DecisionRecord).count()!=0: return False
        finally: engine.dispose()
    return True
