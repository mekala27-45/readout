"""Render an auditable decision document from a persisted run."""

from pathlib import Path

import typer

from readout_render.renderer import ROOT, render_manifest

app = typer.Typer(no_args_is_help=True)


@app.command()
def render(key: str, database_url: str | None = None, output: Path | None = None) -> None:
    from readout_api.repository import Repository

    repository = Repository(database_url)
    try:
        documents = render_manifest(repository.latest_manifest(key))
        target = output or ROOT / "readouts"
        target.mkdir(parents=True, exist_ok=True)
        for extension, name in [("md", "markdown"), ("html", "html")]:
            path = target / f"{key}.{extension}"
            path.write_text(documents[name], encoding="utf-8", newline="\n")
            typer.echo(str(path))
    finally:
        repository.close()


@app.callback()
def main() -> None:
    """Health first. Evidence before decisions."""
