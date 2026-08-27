"""G11 remediation: one terminal Decision disposition per Change Item revision."""
from collections.abc import Sequence

from alembic import op

revision: str = "mig_008_g11_unique_terminal_scope"
down_revision: str | None = "mig_008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "uq_decision_scope_items_terminal_disposition",
        "decision_scope_items",
        ["change_item_id", "change_item_revision"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_decision_scope_items_terminal_disposition", table_name="decision_scope_items")
