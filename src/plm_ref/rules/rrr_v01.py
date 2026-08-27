from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import re
from types import MappingProxyType
from typing import Literal

from plm_ref.domain.errors import RoutingInputError

ApplicabilityRelation = Literal["Equal", "Proposed Narrower", "Not Determinable"]

SUPPLIER_RELATED_TRIGGERS = frozenset(
    {
        "Synthetic supplier process change",
        "Synthetic supplier process change with elevated authority classification",
    }
)

_CLAUSE_PATTERN = re.compile(
    r'(?P<feature>[A-Za-z][A-Za-z0-9_]*)\s*=\s*"(?P<value>[^"\r\n]+)"'
)


@dataclass(frozen=True)
class CandidateRoutingInput:
    impact_candidate_id: str
    affected_domain: str


@dataclass(frozen=True)
class OccurrenceRoutingInput:
    occurrence_id: str
    current_applicability_expression: str
    overlay_contains_applicability_change: bool


@dataclass(frozen=True)
class ProductStateRoutingInput:
    predecessor_material_characteristic: str
    proposed_material_characteristic: str
    proposed_validated_scope: str
    affected_occurrences: tuple[OccurrenceRoutingInput, ...]


@dataclass(frozen=True)
class RrrV01ExecutionContext:
    impact_execution_id: str
    change_case_trigger: str
    product_states: tuple[ProductStateRoutingInput, ...]
    candidates: tuple[CandidateRoutingInput, ...]
    baseline_requirement_ids: frozenset[str]


@dataclass(frozen=True)
class AssessmentObligationSpec:
    assessment_obligation_id: str
    impact_candidate_id: str | None
    domain: str
    requirement_id: str | None
    mandatory: bool
    routing_rule_reference: Literal["RRR-01", "RRR-02", "RRR-03", "RRR-04"]


@dataclass(frozen=True)
class Rrr05Input:
    validated_scope_relation: ApplicabilityRelation
    product_engineering_assessment_complete: bool
    assessment_linked_to_occurrence_candidate: bool
    req_004_conclusion: str | None
    overlay_contains_matching_applicability_change: bool


@dataclass(frozen=True)
class ScopeRevisionRequiredSpec:
    affected_change_item_id: str | None
    affected_change_item_revision: str | None


@dataclass(frozen=True)
class AuthorityResult:
    """Persistence-free RRR-06 result for one frozen Change Case trigger."""

    required_authority_level: Literal["Standard", "Elevated"] | None


def evaluate_rrr06(change_case_trigger: str) -> AuthorityResult:
    """Derive authority only from the two exact frozen trigger values."""

    mapping: Mapping[str, Literal["Standard", "Elevated"]] = {
        "Synthetic supplier process change": "Standard",
        "Synthetic supplier process change with elevated authority classification": "Elevated",
    }
    return AuthorityResult(required_authority_level=mapping.get(change_case_trigger))


def evaluate_rrr05(
    inputs: Rrr05Input,
    provenance_sources: frozenset[tuple[str, str]],
) -> ScopeRevisionRequiredSpec | None:
    """Return a persistence-free RRR-05 result from structured state only."""
    if not (
        inputs.validated_scope_relation == "Proposed Narrower"
        and inputs.product_engineering_assessment_complete
        and inputs.assessment_linked_to_occurrence_candidate
        and inputs.req_004_conclusion == "Not Satisfied"
        and not inputs.overlay_contains_matching_applicability_change
    ):
        return None
    source = next(iter(provenance_sources)) if len(provenance_sources) == 1 else None
    return ScopeRevisionRequiredSpec(
        affected_change_item_id=source[0] if source else None,
        affected_change_item_revision=source[1] if source else None,
    )


def parse_bounded_applicability(
    expression: str,
) -> frozenset[tuple[str, str]] | None:
    """Parse only `Feature = "Value" [AND ...]*` from the frozen grammar."""

    if not isinstance(expression, str) or not expression.strip():
        return None
    clauses = re.split(r"\s+AND\s+", expression.strip())
    parsed: set[tuple[str, str]] = set()
    for clause in clauses:
        match = _CLAUSE_PATTERN.fullmatch(clause.strip())
        if match is None:
            return None
        feature = match.group("feature")
        value = match.group("value")
        parsed.add((feature, value))
    return frozenset(parsed)


def validated_scope_relation(
    proposed_scope: str, current_applicability: str
) -> ApplicabilityRelation:
    proposed = parse_bounded_applicability(proposed_scope)
    current = parse_bounded_applicability(current_applicability)
    if proposed is None or current is None:
        return "Not Determinable"
    if proposed == current:
        return "Equal"
    if proposed > current:
        return "Proposed Narrower"
    return "Not Determinable"


def supplier_related_trigger(change_case_trigger: str) -> bool:
    return change_case_trigger in SUPPLIER_RELATED_TRIGGERS


def material_characteristic_changed(context: RrrV01ExecutionContext) -> bool:
    return any(
        state.predecessor_material_characteristic
        != state.proposed_material_characteristic
        for state in context.product_states
    )


def _obligation_id(
    impact_execution_id: str, impact_candidate_id: str | None, domain: str
) -> str:
    if impact_candidate_id is not None:
        if not impact_candidate_id.startswith("IC-"):
            raise RoutingInputError(
                f"unsupported frozen Impact Candidate ID {impact_candidate_id}"
            )
        return "AO-" + impact_candidate_id[3:]

    execution_level_ids = {
        ("IAX-B02", "Validation"): "AO-B23",
        ("IAX-B02", "Purchasing/Cost"): "AO-B24",
    }
    try:
        return execution_level_ids[(impact_execution_id, domain)]
    except KeyError as exc:
        raise RoutingInputError(
            "no frozen execution-level Assessment Obligation identity exists for "
            f"{impact_execution_id}/{domain}"
        ) from exc


def _domain_specs(
    context: RrrV01ExecutionContext,
    *,
    domain: str,
    requirement_id: str | None,
    routing_rule_reference: Literal["RRR-01", "RRR-02", "RRR-03", "RRR-04"],
) -> tuple[AssessmentObligationSpec, ...]:
    matching = tuple(
        candidate
        for candidate in context.candidates
        if candidate.affected_domain == domain
    )
    candidate_ids: tuple[str | None, ...] = (
        tuple(candidate.impact_candidate_id for candidate in matching)
        if matching
        else (None,)
    )
    return tuple(
        AssessmentObligationSpec(
            assessment_obligation_id=_obligation_id(
                context.impact_execution_id, candidate_id, domain
            ),
            impact_candidate_id=candidate_id,
            domain=domain,
            requirement_id=requirement_id,
            mandatory=True,
            routing_rule_reference=routing_rule_reference,
        )
        for candidate_id in candidate_ids
    )


class RrrV01RuleSet:
    """Direct deterministic implementation of frozen RRR-01 through RRR-04."""

    version = "RRR-v0.1"

    def evaluate(
        self, context: RrrV01ExecutionContext
    ) -> tuple[AssessmentObligationSpec, ...]:
        specs: list[AssessmentObligationSpec] = []
        characteristic_changed = material_characteristic_changed(context)

        if characteristic_changed:
            relations: list[ApplicabilityRelation] = []
            applicability_change = False
            for product_state in context.product_states:
                if not product_state.affected_occurrences:
                    raise RoutingInputError(
                        "changed Product Version has no captured affected occurrence"
                    )
                for occurrence in product_state.affected_occurrences:
                    relation = validated_scope_relation(
                        product_state.proposed_validated_scope,
                        occurrence.current_applicability_expression,
                    )
                    if relation == "Not Determinable":
                        raise RoutingInputError(
                            "validated scope relation is not deterministically evaluable"
                        )
                    relations.append(relation)
                    applicability_change = (
                        applicability_change
                        or occurrence.overlay_contains_applicability_change
                    )

            product_engineering_requirement = (
                "REQ-004"
                if applicability_change or "Proposed Narrower" in relations
                else "REQ-001"
            )
            specs.extend(
                _domain_specs(
                    context,
                    domain="Product Engineering",
                    requirement_id=product_engineering_requirement,
                    routing_rule_reference="RRR-01",
                )
            )
            specs.extend(
                _domain_specs(
                    context,
                    domain="Validation",
                    requirement_id="REQ-002",
                    routing_rule_reference="RRR-02",
                )
            )
            specs.extend(
                _domain_specs(
                    context,
                    domain="Manufacturing",
                    requirement_id="REQ-003",
                    routing_rule_reference="RRR-03",
                )
            )

        if supplier_related_trigger(context.change_case_trigger):
            specs.extend(
                _domain_specs(
                    context,
                    domain="Purchasing/Cost",
                    requirement_id=None,
                    routing_rule_reference="RRR-04",
                )
            )

        missing_requirements = {
            spec.requirement_id
            for spec in specs
            if spec.requirement_id is not None
            and spec.requirement_id not in context.baseline_requirement_ids
        }
        if missing_requirements:
            raise RoutingInputError(
                "routed Requirement is absent from the execution baseline: "
                + ", ".join(sorted(missing_requirements))
            )
        return tuple(specs)


RULE_SET_REGISTRY: Mapping[str, RrrV01RuleSet] = MappingProxyType(
    {RrrV01RuleSet.version: RrrV01RuleSet()}
)
