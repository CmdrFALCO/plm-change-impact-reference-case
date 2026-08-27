from __future__ import annotations

import os
from pathlib import Path

import typer
from sqlalchemy.orm import Session

from plm_ref.application.history_and_views import derive_handover_view, reconstruct_decision_basis
from plm_ref.application.scenario_runner import load_scenario, reset_database, run_scenario, verify_all
from plm_ref.infrastructure.db.session import create_sqlite_engine

app = typer.Typer(
    name="plm-ref",
    help="Synthetic PLM change-impact reference demonstrator.",
    no_args_is_help=True,
)
db_app = typer.Typer(no_args_is_help=True)
scenario_app = typer.Typer(no_args_is_help=True)
verify_app = typer.Typer(no_args_is_help=True)
app.add_typer(db_app, name="db")
app.add_typer(scenario_app, name="scenario")
app.add_typer(verify_app, name="verify")


def _database_path() -> Path:
    return Path(os.environ.get("PLM_REF_DATABASE_PATH", "plm_ref.db"))


@app.callback()
def main() -> None:
    """Command group for deterministic local verification."""


@app.command("version")
def version() -> None:
    """Show the reference implementation version."""
    from plm_ref import __version__

    typer.echo(__version__)


@db_app.command("reset")
def reset() -> None:
    """Rebuild the configured SQLite database through Alembic."""
    engine = reset_database(_database_path())
    engine.dispose()
    typer.echo("database reset")


@scenario_app.command("load")
def load(scenario: str) -> None:
    """Load shared source plus the selected scenario input state."""
    engine = create_sqlite_engine(_database_path())
    try:
        with Session(engine) as session, session.begin():
            case_id = load_scenario(session, scenario)
        typer.echo(case_id)
    finally:
        engine.dispose()


@scenario_app.command("run")
def run(scenario: str) -> None:
    """Run one frozen scenario through the actual application services."""
    engine = create_sqlite_engine(_database_path())
    try:
        with Session(engine) as session, session.begin():
            case_id = run_scenario(session, scenario)
        typer.echo(case_id)
    finally:
        engine.dispose()


@verify_app.command("all")
def verify() -> None:
    """Run the bounded deterministic interface checks, failing closed."""
    if not verify_all(_database_path()):
        raise typer.Exit(code=1)
    typer.echo("verification passed")


if __name__ == "__main__":
    app()
