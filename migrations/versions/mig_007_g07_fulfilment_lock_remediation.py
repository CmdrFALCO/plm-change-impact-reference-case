"""G07 remediation: retain-compatible historical fulfilment link assignment."""
from collections.abc import Sequence

from alembic import op

revision: str = "mig_007_g07_fulfilment_lock_remediation"
down_revision: str | None = "mig_007_assessment_lock_subset"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_obligations_locked_fulfilment_update")
    op.execute(
        "CREATE TRIGGER trg_obligations_locked_fulfilment_update "
        "BEFORE UPDATE ON assessment_obligations FOR EACH ROW WHEN ("
        "(OLD.fulfilled_by_assessment_id IS NOT NULL AND EXISTS ("
        " SELECT 1 FROM assessments a WHERE a.assessment_id = OLD.fulfilled_by_assessment_id AND a.is_locked = 1)) "
        "OR (NEW.fulfilled_by_assessment_id IS NOT NULL AND OLD.fulfilled_by_assessment_id IS NULL AND EXISTS ("
        " SELECT 1 FROM assessments a WHERE a.assessment_id = NEW.fulfilled_by_assessment_id AND a.is_locked = 1) "
        "AND NOT EXISTS (SELECT 1 FROM assessment_reuse_classifications arc "
        " WHERE arc.assessment_id = NEW.fulfilled_by_assessment_id "
        " AND arc.target_impact_execution_id = NEW.impact_execution_id "
        " AND arc.classification = 'Retained'))"
        ") BEGIN SELECT RAISE(ABORT, 'locked Assessment fulfilment is immutable'); END"
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_obligations_locked_fulfilment_update")
    op.execute(
        "CREATE TRIGGER trg_obligations_locked_fulfilment_update "
        "BEFORE UPDATE ON assessment_obligations FOR EACH ROW WHEN EXISTS "
        "(SELECT 1 FROM assessments a WHERE a.assessment_id IN "
        "(OLD.fulfilled_by_assessment_id, NEW.fulfilled_by_assessment_id) AND a.is_locked = 1) "
        "BEGIN SELECT RAISE(ABORT, 'locked Assessment fulfilment is immutable'); END"
    )
