from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from plm_ref.application.assessment import (
    AssessmentCompletionInput,
    EvidenceUseInput,
    RequirementConclusionInput,
)


def test_assessment_lock_subset_migration_installs_all_sqlite_triggers(tmp_path: Path) -> None:
    database_path = tmp_path / "g07.db"
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite+pysqlite:///{database_path}")
    command.upgrade(config, "head")
    names = {trigger["name"] for trigger in inspect(
        __import__("sqlalchemy").create_engine(f"sqlite+pysqlite:///{database_path}")
    ).get_table_names() and __import__("sqlalchemy").create_engine(f"sqlite+pysqlite:///{database_path}").connect().exec_driver_sql("SELECT name FROM sqlite_master WHERE type = 'trigger'").mappings()}
    assert {"trg_assessments_locked_update", "trg_assessments_locked_delete",
            "trg_assessment_impact_links_locked_insert",
            "trg_assessment_requirement_conclusions_locked_insert",
            "trg_assessment_evidence_uses_locked_insert",
            "trg_obligations_locked_fulfilment_update"} <= names


def test_completion_input_keeps_explicit_children() -> None:
    data = AssessmentCompletionInput("ASM", "CASE", "IAX", "Validation", "Relevant",
        "No Objection", "bounded", "assessor", __import__("datetime").datetime.now(), ("IC",),
        (RequirementConclusionInput("ARC", "REQ", "Satisfied"),),
        (EvidenceUseInput("AEU", "EV", "OVOBJ", "Accepted as Applicable", "token"),), ("AO",))
    assert data.requirement_conclusions[0].requirement_id == "REQ"
