from __future__ import annotations

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(
        title="Product Change Impact Assessment & Decision Readiness",
        version="0.1.0",
    )

    @app.get("/health", tags=["runtime"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
