"""Reset only the named local demo, then derive all publishable evidence again."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import numpy as np
from readout_api.repository import Repository
from readout_assign import assign
from readout_calibrate.harness import run_calibration
from readout_render.renderer import publish, render_manifest
from readout_sim import design_for, generate, scenarios
from readout_stats.health import srm

from scripts.check_no_em_dash import check
from scripts.ingest_cookie_cats import ingest
from scripts.restore_evidence import ROOT, snapshot


def assignment_evidence() -> dict[str, Any]:
    first = {"key": "assignment-demo", "salt": "readout-demonstration"}
    second = {"key": "assignment-demo", "salt": "independent-salt"}
    assignments = [assign(first, f"sample-{i}") for i in range(100000)]
    treatment = np.array([a["variant"] == "treatment" for a in assignments], dtype=float)
    other = np.array(
        [assign(second, f"sample-{i}")["variant"] == "treatment" for i in range(100000)],
        dtype=float,
    )
    bins, edges = np.histogram(
        [a["bucket"] for a in assignments[:10000]], bins=20, range=(0, 10000)
    )
    return {
        "source": "deterministic sample IDs",
        "key": first["key"],
        "salt": first["salt"],
        "units": len(assignments),
        "counts": {"control": int(np.sum(treatment == 0)), "treatment": int(treatment.sum())},
        "uniformity": srm(
            {"control": int(np.sum(treatment == 0)), "treatment": int(treatment.sum())}
        ),
        "salt_correlation": float(np.corrcoef(treatment, other)[0, 1]),
        "histogram_units": 10000,
        "histogram": [
            {
                "bucket_start": int(edges[i]),
                "bucket_end": int(edges[i + 1]),
                "count": int(value),
                "expected": 500,
            }
            for i, value in enumerate(bins)
        ],
    }


def main() -> None:
    # Deliberately ignore cloud DATABASE_URL: this command resets the local canonical demo only.
    database = (ROOT / "artifacts/readout.db").resolve()
    if database.parent != (ROOT / "artifacts").resolve():
        raise ValueError("Demo database escaped the declared artifact directory")
    temporary = TemporaryDirectory(prefix="readout-canonical-")
    working = Path(temporary.name) / "readout.db"
    repository = Repository("sqlite:///" + working.as_posix())
    try:
        repository.reset()
        for key, scenario in scenarios().items():
            print(f"Deriving simulated {key}", flush=True)
            seed = 20260922
            repository.create_experiment(
                {
                    "key": key,
                    "name": scenario["name"],
                    "status": "running",
                    "source": "simulated",
                    "hypothesis": scenario["description"],
                    "salt": "readout-scenario-" + key,
                    "source_detail": {
                        "description": scenario["description"],
                        "scenario": key,
                        "seed": seed,
                        "parameters": scenario,
                    },
                    "design": design_for(key),
                }
            )
            repository.import_rows(key, generate(key, seed=seed))
            repository.analyze(key)
        print("Deriving public Cookie Cats", flush=True)
        ingest(repository)
        print("Running complete independent calibration", flush=True)
        calibration = run_calibration(full=True)
        calibration["assignment"] = assignment_evidence()
        repository.save_calibration(calibration)
        for experiment in repository.list_experiments():
            manifest = repository.latest_manifest(experiment["key"])
            document = render_manifest(manifest)["markdown"]
            repository.record_readout(experiment["key"], manifest["run"]["id"], document)
        print("Rendering stored records", flush=True)
        publish(repository, ROOT, write=True)
        errors = publish(repository, ROOT)
        if errors:
            raise ValueError("\n".join(errors))
        punctuation = check(ROOT)
        if punctuation:
            raise ValueError("Forbidden punctuation: " + ", ".join(punctuation))
        print(
            json.dumps(
                {
                    "peeking": calibration["peeking"][-1],
                    "power": calibration["power"],
                    "pricepoint": calibration["pricepoint"],
                },
                indent=2,
            )
        )
    finally:
        repository.close()
    snapshot(working)
    staged = database.with_suffix(".db.new")
    shutil.copyfile(working, staged)
    for suffix in ("-journal", "-wal", "-shm"):
        sidecar = Path(str(database) + suffix)
        if sidecar.exists():
            sidecar.unlink()
    os.replace(staged, database)
    temporary.cleanup()
    print("Canonical relational snapshot and every published claim rederived.")


if __name__ == "__main__":
    main()
