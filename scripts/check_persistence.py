"""An API process writes; a second fresh Python process observes committed rows."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import httpx
from readout_api.models import AnalysisRun, Assignment, Experiment, HealthCheck
from readout_api.repository import make_engine
from sqlalchemy import func
from sqlmodel import Session, select


def observe(url: str) -> None:
    engine = make_engine(url)
    with Session(engine) as session:
        counts = {
            model.__name__: session.exec(select(func.count()).select_from(model)).one()
            for model in (Experiment, Assignment, AnalysisRun, HealthCheck)
        }
    engine.dispose()
    if (
        counts["Experiment"] != 1
        or counts["Assignment"] != 2
        or counts["AnalysisRun"] != 1
        or counts["HealthCheck"] < 3
    ):
        raise RuntimeError(f"Uncommitted records detected: {counts}")
    print(json.dumps(counts))


def main() -> None:
    if len(sys.argv) == 3 and sys.argv[1] == "--observe":
        observe(sys.argv[2])
        return
    if not Path(sys.executable).is_file():
        raise RuntimeError("python_process_unavailable: interpreter is missing")
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    with tempfile.TemporaryDirectory(prefix="readout-persistence-") as directory:
        url = f"sqlite:///{Path(directory) / 'observer.db'}"
        environment = {
            **os.environ,
            "READOUT_DATABASE_URL": url,
            "READOUT_WRITE_TOKEN": "persistence-check-token",
        }
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "readout_api.app:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            env=environment,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        try:
            base = f"http://127.0.0.1:{port}"
            deadline = time.monotonic() + 25
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError(
                        process.stderr.read().decode() if process.stderr else "API exited"
                    )
                try:
                    if httpx.get(f"{base}/healthz", timeout=1).status_code == 200:
                        break
                except httpx.HTTPError:
                    time.sleep(0.1)
            else:
                raise RuntimeError("API did not become ready")
            headers = {"Authorization": "Bearer persistence-check-token"}
            with httpx.Client(base_url=base, headers=headers, timeout=20) as client:
                client.post(
                    "/api/experiments",
                    json={"key": "observer", "name": "Independent observer", "status": "running"},
                ).raise_for_status()
                client.post(
                    "/api/experiments/observer/assign", json={"unit_ids": ["first", "second"]}
                ).raise_for_status()
                client.post("/api/experiments/observer/analyze").raise_for_status()
            result = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "--observe", url],
                capture_output=True,
                text=True,
                timeout=20,
                check=True,
            )
            print(result.stdout.strip())
            print("separate_process_persistence: pass")
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            if process.stderr:
                process.stderr.close()


if __name__ == "__main__":
    main()
