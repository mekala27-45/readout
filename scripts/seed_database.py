"""Explicitly seed an empty database from canonical committed relational evidence."""

from __future__ import annotations

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory

import readout_api.models  # noqa: F401
from readout_api.repository import make_engine
from sqlalchemy import MetaData, Table, inspect, select
from sqlalchemy.engine import Connection, Engine
from sqlmodel import SQLModel

from scripts.restore_evidence import restore


def ensure_empty(connection: Connection) -> None:
    """Read every existing application table before any schema or data write."""
    metadata = MetaData()
    expected = set(SQLModel.metadata.tables)
    for name in inspect(connection).get_table_names():
        if name == "alembic_version":
            continue
        if name not in expected:
            raise ValueError("Refusing a target containing unrelated tables")
        table = Table(name, metadata, autoload_with=connection)
        if connection.execute(select(table).limit(1)).first() is not None:
            raise ValueError("Refusing to seed a nonempty target database")


def _copy_records(source: Engine, target: Engine) -> dict[str, int]:
    counts: dict[str, int] = {}
    with target.begin() as destination:
        ensure_empty(destination)
        SQLModel.metadata.create_all(destination)
        with source.connect() as origin:
            for table in SQLModel.metadata.sorted_tables:
                count = 0
                result = origin.execute(select(table))
                while batch := result.fetchmany(2000):
                    destination.execute(table.insert(), [dict(row._mapping) for row in batch])
                    count += len(batch)
                result.close()
                counts[table.name] = count
    return counts


def seed_database(url: str, *, source: Path | None = None) -> dict[str, int]:
    """Copy committed records in one transaction, retaining IDs, hashes, and dates."""
    target = make_engine(url)
    try:
        with target.connect() as connection:
            ensure_empty(connection)
        with TemporaryDirectory(prefix="readout-seed-") as directory:
            restored = Path(directory) / "canonical.db"
            restore(restored, source)
            origin = make_engine("sqlite:///" + restored.as_posix())
            try:
                return _copy_records(origin, target)
            finally:
                origin.dispose()
    finally:
        target.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--database-url",
        required=True,
        help="Explicit empty target URL; existing application records are never reset",
    )
    parser.add_argument("--source", type=Path, help="Canonical evidence.sql.gz snapshot")
    arguments = parser.parse_args()
    counts = seed_database(arguments.database_url, source=arguments.source)
    print("Seeded canonical records into the empty target database:")
    for table, count in sorted(counts.items()):
        print(f"  {table}: {count}")


if __name__ == "__main__":
    main()
