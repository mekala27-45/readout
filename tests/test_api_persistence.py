import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from readout_api.app import create_app, parse_csv
from readout_api.models import AnalysisRun, Assignment, Decision, Experiment, HealthCheck
from readout_api.repository import ConflictError, NotFoundError, Repository, make_engine
from readout_core.hashing import content_hash
from sqlalchemy import func
from sqlmodel import Session, select

TOKEN = {"Authorization": "Bearer test-token"}


def payload(key="demo"):
    return {"key": key, "name": key.title(), "status": "running"}


def rows(n=80):
    return [
        {
            "unit_id": f"u-{i}",
            "variant": "control" if i % 2 == 0 else "treatment",
            "exposed": True,
            "day": 1 + i // 20,
            "segment": "all",
            "metrics": {"value": 10.0 + (i % 7) + (i % 2) * 2.0},
            "pre": {},
            "denominators": {},
        }
        for i in range(n)
    ]


@pytest.fixture
def database(tmp_path):
    return f"sqlite:///{tmp_path / 'test.db'}"


@pytest.fixture
def client(database):
    with TestClient(create_app(database, "test-token")) as client:
        yield client


def test_persistence_is_committed(client, database):
    created = client.post("/api/experiments", json=payload(), headers=TOKEN)
    assert created.status_code == 201, created.text
    assert (
        client.post(
            "/api/experiments/demo/assign", json={"unit_ids": ["audit-a", "audit-b"]}, headers=TOKEN
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/api/experiments/demo/observations", json={"rows": rows()}, headers=TOKEN
        ).status_code
        == 200
    )
    response = client.post("/api/experiments/demo/analyze", headers=TOKEN)
    assert response.status_code == 200, response.text
    independent = make_engine(database)
    with Session(independent) as observer:
        assert observer.exec(select(func.count()).select_from(Experiment)).one() == 1
        assert observer.exec(select(func.count()).select_from(Assignment)).one() == 82
        assert observer.exec(select(func.count()).select_from(AnalysisRun)).one() == 1
        assert observer.exec(select(func.count()).select_from(HealthCheck)).one() >= 3
        assert observer.exec(select(func.count()).select_from(Decision)).one() == 1
    independent.dispose()


def test_health_is_committed_before_engine_runs(client, database, monkeypatch):
    import readout_stats.engine as engine

    original = engine.analyze
    observed = []

    def independent_observer(design, data, health):
        separate = make_engine(database)
        with Session(separate) as observer:
            stored = observer.exec(select(HealthCheck)).all()
            assert len(stored) == len(health) > 0
            observed.append(True)
        separate.dispose()
        return original(design, data, health)

    monkeypatch.setattr(engine, "analyze", independent_observer)
    client.post("/api/experiments", json=payload(), headers=TOKEN)
    response = client.post("/api/experiments/demo/analyze", headers=TOKEN)
    assert response.status_code == 200, response.text
    assert observed == [True]
    assert response.json()["results"]["metrics"] == []
    assert response.json()["results"]["decision"]["decision"] == "blocked"


def test_experiment_isolation(client):
    for key in ("first", "second"):
        client.post("/api/experiments", json=payload(key), headers=TOKEN)
    run = client.post("/api/experiments/first/analyze", headers=TOKEN).json()
    manifest = client.get("/api/experiments/first/manifest").json()
    run_id, decision_id = run["id"], manifest["decision"]["id"]
    for path in (f"runs/{run_id}", f"runs/{run_id}/health", f"decisions/{decision_id}"):
        assert client.get(f"/api/experiments/second/{path}").status_code == 404
    assert (
        client.post(
            "/api/experiments/second/decide", json={"analysis_run_id": run_id}, headers=TOKEN
        ).status_code
        == 404
    )
    assert client.get("/api/experiments/second/manifest").status_code == 404
    assert client.get("/api/experiments/second/assignments").json() == []
    assert client.get("/api/experiments/first/decisions/absent").status_code == 404


def test_registration_freezes_hash_and_records_deviation(database):
    repo = Repository(database)
    original = repo.create_experiment(payload())
    changed = repo.update_experiment("demo", {"alpha": 0.04, "reason": "Sensitivity request"})
    assert changed["design_hash"] == original["design_hash"] == content_hash(original["design"])
    assert changed["registered_design"]["alpha"] == 0.05
    assert changed["design"]["alpha"] == 0.04
    assert changed["design_deviations"][0]["changed_fields"] == ["alpha"]
    assert repo.analyze("demo")["design_hash"] == original["design_hash"]
    repo.close()


def test_draft_lifecycle_and_validation(client):
    assert client.post("/api/experiments", json=payload()).status_code == 401
    assert (
        client.post(
            "/api/experiments", json={**payload(), "unknown": True}, headers=TOKEN
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/experiments", json={**payload(), "status": "draft"}, headers=TOKEN
        ).status_code
        == 201
    )
    assert client.post("/api/experiments", json=payload(), headers=TOKEN).status_code == 409
    assert client.post("/api/experiments/demo/analyze", headers=TOKEN).status_code == 409
    assert (
        client.post(
            "/api/experiments/demo/assign", json={"unit_ids": ["a"]}, headers=TOKEN
        ).status_code
        == 409
    )
    assert (
        client.post(
            "/api/experiments/demo/observations", json={"rows": rows()}, headers=TOKEN
        ).status_code
        == 409
    )
    assert (
        client.patch(
            "/api/experiments/demo", json={"alpha": 0.04, "name": "Changed"}, headers=TOKEN
        ).status_code
        == 200
    )
    assert (
        client.patch("/api/experiments/demo", json={"salt": "bad"}, headers=TOKEN).status_code
        == 422
    )
    assert client.post("/api/experiments/demo/start", headers=TOKEN).status_code == 200
    assert client.post("/api/experiments/demo/start", headers=TOKEN).status_code == 409
    assert client.get("/healthz").json()["status"] == "ok"
    assert len(client.get("/api/experiments").json()) == 1
    assert client.get("/api/experiments/absent").status_code == 404


def test_assignment_preview_and_audit(client):
    client.post("/api/experiments", json=payload(), headers=TOKEN)
    preview = client.post("/api/assign", json={"experiment_key": "demo", "unit_id": "a"}).json()
    assert (
        preview
        == client.get("/api/assign", params={"experiment_key": "demo", "unit_id": "a"}).json()
    )
    assert len(preview["hash"]) == 64
    for _ in range(2):
        assert (
            client.post(
                "/api/experiments/demo/assign", json={"unit_ids": ["a", "a"]}, headers=TOKEN
            ).status_code
            == 200
        )
    audited = client.get("/api/experiments/demo/assignments").json()
    assert len(audited) == 1 and "unit_id" not in audited[0]


def test_import_invariants_and_evidence(database):
    repo = Repository(database)
    repo.create_experiment(payload())
    with pytest.raises(ValueError, match="unique"):
        repo.import_rows("demo", [rows()[0], rows()[0]])
    with pytest.raises(ValueError, match="absent"):
        repo.import_rows("demo", [{**rows()[0], "metrics": {"absent": 1.0}}])
    repo.import_rows("demo", rows())
    with pytest.raises(ConflictError, match="already imported"):
        repo.import_rows("demo", rows())
    with pytest.raises(NotFoundError):
        repo.get_calibration()
    assert repo.save_calibration({"computed": True}) == repo.get_calibration()
    repo.reset()
    assert repo.list_experiments() == []
    repo.close()


@pytest.mark.parametrize(
    "contents",
    [
        b"",
        b"wrong,columns\na,b\n",
        b"unit_id,variant\na,control\n",
        b"unit_id,variant,value\n",
        b"unit_id,variant,value\na,wrong,1\n",
        b"unit_id,variant,value,exposed\na,control,1,maybe\n",
    ],
)
def test_csv_rejects_invalid_data(contents):
    with pytest.raises(ValueError):
        parse_csv(contents)


def test_csv_upload_to_existing_experiment(client):
    client.post("/api/experiments", json=payload(), headers=TOKEN)
    csv = "unit_id,variant,value,pre_value,day,segment\na,control,10,9,1,new\nb,treatment,12,11,2,new\n"
    response = client.post(
        "/api/experiments/demo/upload",
        files={"file": ("outcomes.csv", csv, "text/csv")},
        headers=TOKEN,
    )
    assert response.status_code == 200 and response.json()["rows"] == 2


def test_cloud_refuses_default_token(monkeypatch):
    monkeypatch.setenv("READOUT_ENV", "production")
    monkeypatch.delenv("READOUT_WRITE_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="require"):
        create_app("sqlite://")
    with pytest.raises(RuntimeError, match="require"):
        create_app("sqlite://", "demo-write-token")
    assert create_app("sqlite://", "secret-token")


def test_upload_readout_decision_and_power_end_to_end(client, database):
    csv = "unit_id,variant,value,pre_value,day,segment\n" + "".join(
        f"uploaded-{i},{'control' if i % 2 == 0 else 'treatment'},{10 + i % 7 + (i % 2) * 2},{9 + i % 7},1,all\n"
        for i in range(80)
    )
    response = client.post(
        "/api/upload",
        files={"file": ("outcomes.csv", csv, "text/csv")},
        data={"name": "Retrospective uploaded test"},
        headers=TOKEN,
    )
    assert response.status_code == 200, response.text
    result = response.json()
    assert "## Health" in result["markdown"] and "## Primary metric" in result["markdown"]
    assert "retrospective" in result["markdown"].lower()
    assert "<html" in result["html"]
    experiment = result["manifest"]["experiment"]
    key = experiment["key"]
    run_id = result["manifest"]["run"]["id"]
    assert client.get(f"/api/experiments/{key}/runs/{run_id}").status_code == 200
    assert client.get(f"/api/experiments/{key}/runs/{run_id}/health").status_code == 200
    assert (
        client.get(f"/api/experiments/{key}/readout")
        .headers["content-type"]
        .startswith("text/markdown")
    )
    assert (
        client.get(f"/api/experiments/{key}/readout", params={"format": "html"}).status_code == 200
    )
    assert (
        client.get(f"/api/experiments/{key}/readout", params={"format": "json"}).status_code == 422
    )
    decided = client.post(
        f"/api/experiments/{key}/decide", json={"analysis_run_id": run_id}, headers=TOKEN
    )
    assert decided.status_code == 200
    assert decided.json()["rendered_readout_sha256"]
    assert client.get(f"/api/experiments/{key}").json()["status"] == "decided"
    repo = Repository(database)
    repo.save_calibration({"computed_at": "2026-09-22", "measured": True})
    assert client.get("/api/calibration").json()["measured"]
    assert client.get("/api/bundle").status_code == 200
    power = client.post("/api/design/power", json={"baseline": 10.0, "mde_relative": 0.1})
    assert power.status_code == 200, power.text
    repo.close()


def test_registered_integrity_and_assignment_conflict(database):
    repo = Repository(database)
    repo.create_experiment(payload())
    assignment = repo.assign_units("demo", ["u-0"])[0]
    conflicting = {
        **rows()[0],
        "variant": "control" if assignment["variant"] == "treatment" else "treatment",
    }
    with pytest.raises(ValueError, match="conflicts"):
        repo.import_rows("demo", [conflicting])
    with Session(repo.engine) as session:
        experiment = session.exec(select(Experiment)).one()
        experiment.design_hash = "tampered"
        session.add(experiment)
        session.commit()
    with pytest.raises(ConflictError, match="hash mismatch"):
        repo.analyze("demo")
    repo.close()


@pytest.mark.parametrize("outcomes", [[0, 1, 0, 1], [1, 1, 1, 1], [0, 0, 0, 0]])
def test_binary_csv_upload_has_valid_retrospective_planning(client, outcomes):
    csv = "unit_id,variant,value\n" + "".join(
        f"binary-{i},{'control' if i % 2 == 0 else 'treatment'},{outcomes[(i // 2) % 4]}\n"
        for i in range(40)
    )
    response = client.post(
        "/api/upload", files={"file": ("binary.csv", csv, "text/csv")}, headers=TOKEN
    )
    assert response.status_code == 200, response.text
    design = response.json()["manifest"]["experiment"]["registered_design"]
    assert 0 < design["baseline"] < 1
    assert design["baseline"] * (1 + design["mde_relative"]) < 1
    assert design["planned_n_per_arm"] > 0


@pytest.mark.external
def test_persistence_outside_test_process():
    if not shutil.which(sys.executable):
        pytest.skip("python_process_unavailable: current interpreter cannot be launched")
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/check_persistence.py"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "separate_process_persistence: pass" in result.stdout


@pytest.mark.postgres
def test_postgres_persistence_is_committed():
    import docker

    required = os.getenv("READOUT_REQUIRE_POSTGRES") == "1"
    try:
        docker_client = docker.from_env(timeout=10)
        docker_client.ping()
        docker_client.close()
    except docker.errors.DockerException as error:
        if required:
            pytest.fail(f"postgres_dependency_required: Docker daemon is unavailable: {error}")
        pytest.skip(f"postgres_docker_unavailable: Docker daemon is unavailable: {error}")
    from testcontainers.postgres import PostgresContainer

    with PostgresContainer("postgres:16-alpine", driver="psycopg") as postgres:
        url = postgres.get_connection_url()
        with TestClient(create_app(url, "test-token")) as client:
            test_persistence_is_committed(client, url)
