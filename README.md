# Product Change Impact Assessment & Decision Readiness

A synthetic PLM Business Architecture reference case and deterministic demonstrator.

The implementation follows the frozen authority chain:

1. Business Architecture Definition v0.3.1
2. Logical Information Model v0.3.2
3. Scenario Data Definition v0.1
4. Readiness and Routing Rules v0.1 (`RRR-v0.1`)
5. Solution Architecture v0.1
6. Prototype Implementation Plan v0.1

## Current implementation state

`INC-00 — Bootstrap and deterministic runtime`

The repository currently contains the Python package skeleton, SQLite connection factory,
Alembic configuration, pytest setup, Typer CLI skeleton, and FastAPI application skeleton.
No PLM business semantics are implemented in INC-00.

## Development

```bash
python -m pip install -e '.[dev]'
pytest
alembic current
plm-ref --help
```
