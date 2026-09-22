"""Restore the committed relational snapshot without requiring a data download."""

from __future__ import annotations

import argparse
import gzip
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def restore(target: Path, source: Path | None = None) -> None:
    source = source or ROOT / "artifacts/evidence.sql.gz"
    if target.exists():
        raise ValueError("Refusing to overwrite an existing database; use a fresh target")
    target.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(source, "rt", encoding="utf-8") as archive:
        sql = archive.read()
    with sqlite3.connect(target) as connection:
        connection.executescript(sql)
        if connection.execute("PRAGMA integrity_check").fetchone() != ("ok",):
            raise ValueError("Restored database failed integrity check")


def snapshot(database: Path, target: Path | None = None) -> None:
    target = target or ROOT / "artifacts/evidence.sql.gz"
    with sqlite3.connect(database) as connection:
        sql = "\n".join(connection.iterdump()) + "\n"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(sql.encode("utf-8"), compresslevel=9, mtime=0))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, default=ROOT / "artifacts/readout.db")
    args = parser.parse_args()
    restore(args.target)
    print(f"Restored canonical evidence to {args.target}")


if __name__ == "__main__":
    main()
