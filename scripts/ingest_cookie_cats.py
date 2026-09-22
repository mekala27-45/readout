"""Retrospective public-experiment design with explicit missing-data limitations."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import polars as pl
import yaml
from readout_api.repository import Repository
from readout_core.models import DEFAULT_RULE
from readout_stats.power import required_sample_size

ROOT = Path(__file__).resolve().parents[1]


def ingest(repository: Repository) -> dict[str, Any]:
    folder = ROOT / "experiments/cookie_cats"
    source = folder / "cookie_cats.csv"
    provenance = json.loads((folder / "provenance.json").read_text())
    if hashlib.sha256(source.read_bytes()).hexdigest() != provenance["sha256"]:
        raise ValueError("Cookie Cats source checksum changed")
    data = pl.read_csv(source)
    if data["userid"].n_unique() != len(data) or data.null_count().sum_horizontal().item() != 0:
        raise ValueError("Public source must have unique units and no missing source fields")
    n = required_sample_size(0.19, 0.05, kind="proportion")["n_per_arm"]
    design = {
        "primary_metric_key": "retention_7",
        "metrics": [
            {
                "key": "retention_7",
                "name": "Seven-day retention",
                "kind": "proportion",
                "direction": "higher_is_better",
                "guardrail_margin_relative": None,
                "winsor_upper_percentile": None,
            },
            {
                "key": "retention_1",
                "name": "One-day retention",
                "kind": "proportion",
                "direction": "higher_is_better",
                "guardrail_margin_relative": 0.03,
                "winsor_upper_percentile": None,
            },
            {
                "key": "rounds",
                "name": "Rounds played",
                "kind": "mean",
                "direction": "higher_is_better",
                "guardrail_margin_relative": 0.05,
                "winsor_upper_percentile": 0.999,
            },
        ],
        "guardrail_metric_keys": ["retention_1", "rounds"],
        "secondary_metric_keys": [],
        "variants": [
            {"name": "control", "allocation": 0.5},
            {"name": "treatment", "allocation": 0.5},
        ],
        "mde_relative": 0.05,
        "baseline": 0.19,
        "standard_deviation": 1.0,
        "alpha": 0.05,
        "power": 0.8,
        "planned_n_per_arm": n,
        "planned_days": 14,
        "mixing_variance": 0.0001,
        "has_timestamps": False,
        "bootstrap_seed": 20260922,
        "bootstrap_resamples": 400,
        "decision_rule": {"text": DEFAULT_RULE},
        "fdr_q": 0.05,
    }
    payload = {
        "key": "cookie_cats",
        "name": "Cookie Cats: moving the gate",
        "status": "running",
        "source": "public",
        "unit_type": "player",
        "salt": "public-observed-assignment",
        "hypothesis": "Retrospective reconstruction: moving the wait gate should improve seven-day retention by at least five percent relative, roughly one percentage point at the assumed planning baseline. This practical threshold and the rounds outlier policy were chosen with the public dataset already available; they are not historical pre-registration.",
        "source_detail": {
            **provenance,
            "description": "Public randomized mobile-game assignment data, analyzed retrospectively.",
            "rows": len(data),
            "maximum_rounds": data["sum_gamerounds"].max(),
            "rounds_upper_quantile": data["sum_gamerounds"].quantile(0.999, interpolation="linear"),
            "exposure_note": "Actual gate exposure is unavailable. All randomized installations are retained; exposed=True is a computational inclusion flag, not an observed gate exposure.",
            "timestamps_available": False,
            "pre_period_available": False,
        },
        "design": design,
    }
    (folder / "design.yaml").write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    repository.create_experiment(payload)
    rows = [
        {
            "unit_id": str(row["userid"]),
            "variant": "control" if row["version"] == "gate_30" else "treatment",
            "exposed": True,
            "day": 1,
            "segment": "all",
            "metrics": {
                "retention_7": float(row["retention_7"]),
                "retention_1": float(row["retention_1"]),
                "rounds": float(row["sum_gamerounds"]),
            },
            "pre": {},
            "denominators": {},
        }
        for row in data.iter_rows(named=True)
    ]
    repository.import_rows("cookie_cats", rows)
    return repository.analyze("cookie_cats")


if __name__ == "__main__":
    repo = Repository()
    try:
        print(json.dumps(ingest(repo), indent=2))
    finally:
        repo.close()
