from __future__ import annotations

import subprocess
import sys

from fastapi import FastAPI
from sqlalchemy import text
from typer.testing import CliRunner

import plm_ref
from plm_ref.infrastructure.db.session import create_sqlite_engine
from plm_ref.interfaces.api.app import app
from plm_ref.interfaces.cli.main import app as cli_app


def test_python_package_imports() -> None:
    assert plm_ref.__version__ == "0.1.0"


def test_fastapi_app_imports() -> None:
    assert isinstance(app, FastAPI)


def test_sqlite_foreign_keys_are_enabled_for_every_connection(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "g00.db")
    try:
        with engine.connect() as connection:
            assert connection.execute(text("PRAGMA foreign_keys")).scalar_one() == 1
        with engine.connect() as connection:
            assert connection.execute(text("PRAGMA foreign_keys")).scalar_one() == 1
    finally:
        engine.dispose()


def test_cli_help_succeeds() -> None:
    result = CliRunner().invoke(cli_app, ["--help"])
    assert result.exit_code == 0, result.output
    assert "Synthetic PLM change-impact reference demonstrator" in result.output


def test_alembic_current_succeeds() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "current"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
