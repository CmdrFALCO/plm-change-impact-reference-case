from __future__ import annotations

import typer

app = typer.Typer(
    name="plm-ref",
    help="Synthetic PLM change-impact reference demonstrator.",
    no_args_is_help=True,
)


@app.callback()
def main() -> None:
    """Command group for deterministic local verification."""


@app.command("version")
def version() -> None:
    """Show the reference implementation version."""
    from plm_ref import __version__

    typer.echo(__version__)


if __name__ == "__main__":
    app()
