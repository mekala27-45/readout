"""Deployment startup restores only the intended missing local demo."""

import os
from pathlib import Path

import pytest
from readout_api.repository import Repository, make_engine
from sqlalchemy import text

from scripts.restore_evidence import snapshot
from scripts.seed_database import seed_database
from scripts.start_api import prepare_demo_database


@pytest.fixture
def canonical(tmp_path):
    database = tmp_path / "canonical.db"
    repository = Repository("sqlite:///" + database.as_posix())
    repository.create_experiment({"key": "canonical", "name": "Canonical", "status": "running"})
    repository.assign_units("canonical", ["first", "second"])
    repository.analyze("canonical")
    repository.save_calibration({"marker": "measured canonical evidence"})
    manifest = repository.latest_manifest("canonical")
    repository.close()
    archive = tmp_path / "evidence.sql.gz"
    snapshot(database, archive)
    return archive, manifest


def test_startup_restores_absent_default_and_never_overwrites(tmp_path, canonical):
    archive, manifest = canonical
    root = tmp_path / "demo"
    target = root / "artifacts/readout.db"
    url = "sqlite:///" + target.as_posix()
    assert prepare_demo_database(url, source=archive, root=root)
    repository = Repository(url)
    assert repository.latest_manifest("canonical") == manifest
    repository.create_experiment({"key": "user-work", "name": "Keep my experiment"})
    repository.close()
    before = target.read_bytes()
    assert not prepare_demo_database(url, source=Path("missing-source"), root=root)
    assert target.read_bytes() == before


def test_startup_leaves_custom_sqlite_and_postgres_untouched(tmp_path):
    custom = tmp_path / "custom.db"
    assert not prepare_demo_database("sqlite:///" + custom.as_posix(), root=tmp_path)
    assert not custom.exists()
    assert not prepare_demo_database(
        "postgresql://not-a-user@invalid.example/readout", root=tmp_path
    )
    assert not prepare_demo_database("sqlite:///:memory:", root=tmp_path)


def test_startup_missing_snapshot_leaves_no_empty_demo_database(tmp_path):
    target = tmp_path / "artifacts/readout.db"
    with pytest.raises(FileNotFoundError):
        prepare_demo_database(
            "sqlite:///" + target.as_posix(), source=tmp_path / "absent.gz", root=tmp_path
        )
    assert not target.exists()


def test_explicit_seed_preserves_records_and_refuses_nonempty_target(tmp_path, canonical):
    archive, manifest = canonical
    target = tmp_path / "seeded.db"
    url = "sqlite:///" + target.as_posix()
    counts = seed_database(url, source=archive)
    assert counts["experiment"] == 1 and counts["assignment"] == 2
    assert counts["analysisrun"] == 1 and counts["healthcheck"] >= 3
    repository = Repository(url)
    assert repository.latest_manifest("canonical") == manifest
    assert repository.get_calibration() == {"marker": "measured canonical evidence"}
    repository.close()
    with pytest.raises(ValueError, match="nonempty"):
        seed_database(url, source=tmp_path / "missing-source.gz")
    repository = Repository(url)
    assert repository.latest_manifest("canonical") == manifest
    repository.close()


def test_explicit_seed_refuses_unrelated_target_schema(tmp_path):
    url = "sqlite:///" + (tmp_path / "unrelated.db").as_posix()
    engine = make_engine(url)
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE unrelated (value TEXT)"))
        connection.execute(text("INSERT INTO unrelated VALUES ('preserve me')"))
    with pytest.raises(ValueError, match="unrelated"):
        seed_database(url, source=tmp_path / "missing-source.gz")
    with engine.connect() as connection:
        assert connection.execute(text("SELECT value FROM unrelated")).scalar() == "preserve me"
    engine.dispose()


@pytest.mark.postgres
def test_explicit_postgres_seed_preserves_canonical_analysis(canonical):
    import docker

    try:
        client = docker.from_env(timeout=10)
        client.ping()
        client.close()
    except docker.errors.DockerException as error:
        if os.getenv("READOUT_REQUIRE_POSTGRES") == "1":
            pytest.fail(f"postgres_dependency_required: {error}")
        pytest.skip(f"postgres_docker_unavailable: {error}")
    from testcontainers.postgres import PostgresContainer

    archive, manifest = canonical
    with PostgresContainer("postgres:16-alpine", driver="psycopg") as postgres:
        url = postgres.get_connection_url()
        seed_database(url, source=archive)
        repository = Repository(url)
        assert repository.latest_manifest("canonical") == manifest
        assert repository.get_calibration()["marker"] == "measured canonical evidence"
        repository.close()
        with pytest.raises(ValueError, match="nonempty"):
            seed_database(url, source=archive)
