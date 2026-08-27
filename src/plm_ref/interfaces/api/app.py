"""Thin FastAPI use-case boundary; it deliberately exposes no persistence CRUD."""
from __future__ import annotations

from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session

from plm_ref.application.history_and_views import derive_case_handover_view, derive_handover_view, reconstruct_decision_basis
from plm_ref.application.scenario_runner import load_scenario, reset_database, run_scenario
from plm_ref.infrastructure.db.models import ChangeCase, DecisionRecord, ImpactExecution
from plm_ref.infrastructure.db.session import create_sqlite_engine


def _json(value: Any) -> Any:
    if is_dataclass(value): return {field.name: _json(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, dict): return {str(key): _json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)): return [_json(item) for item in value]
    if hasattr(value, "isoformat"): return value.isoformat().replace("+00:00", "Z")
    return value


def create_app(database_path: str | Path = "plm_ref.db") -> FastAPI:
    app = FastAPI(title="Product Change Impact Assessment & Decision Readiness", version="0.1.0")
    app.state.database_path = Path(database_path)

    def engine(): return create_sqlite_engine(app.state.database_path)
    @app.get("/health", tags=["runtime"])
    def health() -> dict[str, str]: return {"status": "ok"}
    @app.post("/db/reset", tags=["runtime"])
    def reset() -> dict[str, str]:
        db=reset_database(app.state.database_path); db.dispose(); return {"status":"reset"}
    @app.post("/scenarios/{scenario}/load", tags=["scenario"])
    def scenario_load(scenario: str):
        db=engine()
        try:
            with Session(db) as session,session.begin(): return {"change_case_id":load_scenario(session,scenario)}
        except ValueError as exc: raise HTTPException(400,str(exc)) from exc
        finally: db.dispose()
    @app.post("/scenarios/{scenario}/run", tags=["scenario"])
    def scenario_run(scenario: str):
        db=engine()
        try:
            with Session(db) as session,session.begin(): return {"change_case_id":run_scenario(session,scenario)}
        except ValueError as exc: raise HTTPException(400,str(exc)) from exc
        finally: db.dispose()
    @app.get("/cases/{case_id}", tags=["query"])
    def case_show(case_id: str):
        db=engine()
        try:
            with Session(db) as session:
                row=session.get(ChangeCase,case_id)
                if row is None: raise HTTPException(404,"Change Case does not exist")
                return _json({column.name:getattr(row,column.name) for column in row.__table__.columns})
        finally: db.dispose()
    @app.get("/executions/{execution_id}", tags=["query"])
    def execution_show(execution_id: str):
        db=engine()
        try:
            with Session(db) as session:
                row=session.get(ImpactExecution,execution_id)
                if row is None: raise HTTPException(404,"Impact-analysis Execution does not exist")
                return _json({column.name:getattr(row,column.name) for column in row.__table__.columns})
        finally: db.dispose()
    @app.get("/decisions/{decision_id}/basis", tags=["query"])
    def decision_basis(decision_id: str):
        db=engine()
        try:
            with Session(db) as session: return _json(reconstruct_decision_basis(session,decision_id))
        except Exception as exc: raise HTTPException(404,str(exc)) from exc
        finally: db.dispose()
    @app.get("/decisions/{decision_id}/handover", tags=["query"])
    def decision_handover(decision_id: str):
        db=engine()
        try:
            with Session(db) as session: return _json(derive_handover_view(session,decision_id))
        except Exception as exc: raise HTTPException(404,str(exc)) from exc
        finally: db.dispose()
    @app.get("/cases/{case_id}/handover", tags=["query"])
    def case_handover(case_id: str):
        db=engine()
        try:
            with Session(db) as session: return _json(derive_case_handover_view(session,case_id))
        finally: db.dispose()
    return app


app = create_app()
