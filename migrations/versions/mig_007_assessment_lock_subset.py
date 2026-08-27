"""INC-07 locked Assessment trigger subset (without Process-history/Decision)."""
from collections.abc import Sequence

from alembic import op

revision: str = "mig_007_assessment_lock_subset"
down_revision: str | None = "mig_006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    definitions = {
        "trg_assessments_locked_update": "BEFORE UPDATE ON assessments FOR EACH ROW WHEN OLD.is_locked = 1 BEGIN SELECT RAISE(ABORT, 'locked Assessment is immutable'); END",
        "trg_assessments_locked_delete": "BEFORE DELETE ON assessments FOR EACH ROW WHEN OLD.is_locked = 1 BEGIN SELECT RAISE(ABORT, 'locked Assessment is immutable'); END",
    }
    for table in ("assessment_impact_links", "assessment_requirement_conclusions", "assessment_evidence_uses"):
        for action, ref in (("insert", "NEW"), ("update", "OLD"), ("delete", "OLD")):
            definitions[f"trg_{table}_locked_{action}"] = (
                f"BEFORE {action.upper()} ON {table} FOR EACH ROW WHEN EXISTS "
                f"(SELECT 1 FROM assessments a WHERE a.assessment_id = {ref}.assessment_id "
                "AND a.is_locked = 1) BEGIN SELECT RAISE(ABORT, 'locked Assessment children are immutable'); END"
            )
        definitions[f"trg_{table}_locked_update_new"] = (
            f"BEFORE UPDATE ON {table} FOR EACH ROW WHEN EXISTS "
            f"(SELECT 1 FROM assessments a WHERE a.assessment_id = NEW.assessment_id "
            "AND a.is_locked = 1) BEGIN SELECT RAISE(ABORT, 'locked Assessment children are immutable'); END"
        )
    definitions["trg_obligations_locked_fulfilment_update"] = "BEFORE UPDATE ON assessment_obligations FOR EACH ROW WHEN EXISTS (SELECT 1 FROM assessments a WHERE a.assessment_id IN (OLD.fulfilled_by_assessment_id, NEW.fulfilled_by_assessment_id) AND a.is_locked = 1) BEGIN SELECT RAISE(ABORT, 'locked Assessment fulfilment is immutable'); END"
    definitions["trg_obligations_locked_fulfilment_delete"] = "BEFORE DELETE ON assessment_obligations FOR EACH ROW WHEN EXISTS (SELECT 1 FROM assessments a WHERE a.assessment_id = OLD.fulfilled_by_assessment_id AND a.is_locked = 1) BEGIN SELECT RAISE(ABORT, 'locked Assessment fulfilment is immutable'); END"
    for name, body in definitions.items():
        op.execute(f"CREATE TRIGGER {name} {body}")


def downgrade() -> None:
    names = ("trg_obligations_locked_fulfilment_delete", "trg_obligations_locked_fulfilment_update", "trg_assessment_evidence_uses_locked_update_new", "trg_assessment_evidence_uses_locked_delete", "trg_assessment_evidence_uses_locked_update", "trg_assessment_evidence_uses_locked_insert", "trg_assessment_requirement_conclusions_locked_update_new", "trg_assessment_requirement_conclusions_locked_delete", "trg_assessment_requirement_conclusions_locked_update", "trg_assessment_requirement_conclusions_locked_insert", "trg_assessment_impact_links_locked_update_new", "trg_assessment_impact_links_locked_delete", "trg_assessment_impact_links_locked_update", "trg_assessment_impact_links_locked_insert", "trg_assessments_locked_delete", "trg_assessments_locked_update")
    for name in names:
        op.execute(f"DROP TRIGGER IF EXISTS {name}")
