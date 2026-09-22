"""Start a usable demo without overwriting local data or seeding remote databases."""

from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory

import uvicorn
from readout_api.repository import database_url
from sqlalchemy.engine import make_url

from scripts.restore_evidence import ROOT, restore


def prepare_demo_database(
    url: str | None = None, *, source: Path | None = None, root: Path = ROOT
) -> bool:
    """Restore only an absent default demo file; other databases remain untouched."""
    parsed = make_url(url or database_url())
    if parsed.get_backend_name() != "sqlite" or not parsed.database or parsed.query:
        return False
    target = Path(parsed.database).resolve()
    expected = (root / "artifacts/readout.db").resolve()
    if target != expected or target.exists():
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    # Publishing a hard link is atomic and refuses an existing destination. It avoids
    # exposing a partially restored file and cannot overwrite a concurrent writer.
    with TemporaryDirectory(prefix=".readout-restore-", dir=target.parent) as directory:
        staged = Path(directory) / "readout.db"
        restore(staged, source)
        try:
            os.link(staged, target)
        except FileExistsError:
            return False
    return True


def main() -> None:
    if prepare_demo_database():
        print(
            "Restored committed canonical evidence into the absent local demo database.", flush=True
        )
    uvicorn.run("readout_api.app:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))


if __name__ == "__main__":
    main()
