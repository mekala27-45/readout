"""Deterministic salted assignment with stable treatment ramps."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import Any

from readout_core.hashing import hash_unit_id


def assign(experiment: Mapping[str, Any], unit_id: str) -> dict[str, Any]:
    """Grow treatment from bucket zero so increasing allocation never removes units."""
    key = str(experiment["key"])
    salt = str(experiment["salt"])
    design = experiment.get("design", experiment)
    variants = design.get(
        "variants",
        [{"name": "control", "allocation": 0.5}, {"name": "treatment", "allocation": 0.5}],
    )
    treatment = next(float(v["allocation"]) for v in variants if v["name"] == "treatment")
    digest = hashlib.sha256(f"{salt}:{key}:{unit_id}".encode()).hexdigest()
    bucket = int(digest[:8], 16) % 10_000
    return {
        "experiment_key": key,
        "unit_id_hash": hash_unit_id(unit_id),
        "hash": digest,
        "bucket": bucket,
        "variant": "treatment" if bucket < round(treatment * 10_000) else "control",
    }


__all__ = ["assign"]
