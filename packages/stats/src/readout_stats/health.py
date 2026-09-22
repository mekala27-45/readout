"""Recorded health checks run on assigned and exposed randomized units."""
import hashlib
import json
from collections import Counter
from typing import Any

import numpy as np
from scipy import stats


def fingerprint(rows: list[dict[str, Any]]) -> str:
    payload = [(r.get("unit_id"), r.get("variant"), bool(r.get("exposed", True))) for r in rows]
    return hashlib.sha256(json.dumps(payload, separators=(",", ":")).encode()).hexdigest()


def srm(observed: dict[str, int], allocation: dict[str, float] | None = None) -> dict[str, Any]:
    allocation = allocation or {"control": 0.5, "treatment": 0.5}
    if len(allocation) < 2 or set(observed) != set(allocation) or any(v < 0 for v in observed.values()) or any(v <= 0 for v in allocation.values()) or not np.isclose(sum(allocation.values()), 1):
        raise ValueError("Allocation must be positive, sum to one, and match observed arms")
    total = sum(observed.values())
    if total == 0:
        return {"status": "block", "detail": "no data", "observed": observed, "expected": {k: 0 for k in allocation}, "p_value": None, "statistic": None, "conventional_verdict": "block", "blocking_verdict": "block"}
    expected = {k: total * fraction for k, fraction in allocation.items()}
    chi = float(sum((observed[k] - expected[k])**2 / expected[k] for k in allocation))
    p = float(stats.chi2.sf(chi, len(allocation) - 1))
    status = "block" if p < 0.001 else "warn" if p < 0.05 else "pass"
    short = min(allocation, key=lambda key: observed[key] - expected[key])
    shortage = expected[short] - observed[short]
    return {"status": status, "p_value": p, "statistic": chi, "observed": observed, "expected": expected, "short_arm": short, "short_by": float(shortage), "detail": f"{short} is short by {shortage:.1f} units versus configured allocation; block below 0.001, warn below 0.05.", "conventional_verdict": "warn" if p < 0.05 else "pass", "blocking_verdict": "block" if p < 0.001 else "pass", "block_threshold": 0.001, "warn_threshold": 0.05}


def check_health(design: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    allocation = {v["name"]: float(v["allocation"]) for v in design.get("variants", [{"name": "control", "allocation": .5}, {"name": "treatment", "allocation": .5}])}
    if any(r.get("variant") not in allocation for r in rows):
        raise ValueError("Unknown assignment arm")
    ids = [str(r.get("unit_id", "")) for r in rows]
    if len(ids) != len(set(ids)) or any(not x for x in ids):
        raise ValueError("Health requires unique nonempty randomized unit IDs")
    digest = fingerprint(rows)
    assigned = Counter(str(r["variant"]) for r in rows)
    exposed = Counter(str(r["variant"]) for r in rows if r.get("exposed", True))
    records = []
    for scope, counts in [("assigned", assigned), ("exposed", exposed)]:
        record = srm({name: counts[name] for name in allocation}, allocation)
        records.append({"check": f"srm_{scope}", "scope": scope, "data_digest": digest, **record})
    coverage = {name: exposed[name] / assigned[name] if assigned[name] else 0.0 for name in allocation}
    fraction = sum(exposed.values()) / len(rows) if rows else 0.0
    records.append({"check": "exposure", "scope": "assigned", "status": "warn" if fraction < .9 else "pass", "fraction": fraction, "by_arm": coverage, "detail": "Analysis conditions on exposure. Random assignment alone does not identify this effect if treatment changes exposure.", "data_digest": digest})
    for metric in design.get("metrics", []):
        missing = {name: sum(1 for r in rows if r["variant"] == name and r.get("exposed", True) and (r.get("metrics", {}).get(metric["key"]) is None or not np.isfinite(float(r["metrics"][metric["key"]])))) for name in allocation}
        fractions = {name: missing[name] / exposed[name] if exposed[name] else 1.0 for name in allocation}
        primary = metric["key"] == design.get("primary_metric_key")
        empty_arm = any(exposed[name] - missing[name] < 2 for name in allocation)
        records.append({"check": "missingness", "scope": "exposed", "metric_key": metric["key"], "status": "block" if primary and empty_arm else "warn" if max(fractions.values()) - min(fractions.values()) > .01 or max(fractions.values()) > .05 else "pass", "by_arm": fractions, "missing": missing, "detail": "Missing metric values by exposed arm; complete-case analysis assumes ignorable missingness.", "data_digest": digest})
    return records
