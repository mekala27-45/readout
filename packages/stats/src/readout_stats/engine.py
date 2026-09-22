"""Health-first orchestration of public JSON-serializable statistical results."""

from typing import Any

import numpy as np
import polars as pl

from readout_stats import cuped, delta, fdr, fixed, guardrails, sequential
from readout_stats.decision import decide
from readout_stats.health import design_fingerprint, fingerprint, metric_available
from readout_stats.power import achieved_power


def _metric_data(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    selected = [
        r
        for r in rows
        if r.get("exposed", True)
        and r.get("metrics", {}).get(key) is not None
        and np.isfinite(float(r["metrics"][key]))
    ]
    # Polars keeps aggregation explicitly at one row per randomized unit.
    frame = pl.DataFrame(
        {
            "variant": [r["variant"] for r in selected],
            "value": [float(r["metrics"][key]) for r in selected],
        },
        schema={"variant": pl.String, "value": pl.Float64},
    )
    return {
        "rows": selected,
        "control": frame.filter(pl.col("variant") == "control")["value"].to_numpy(),
        "treatment": frame.filter(pl.col("variant") == "treatment")["value"].to_numpy(),
    }


def _analyze_metric(
    definition: dict[str, Any], rows: list[dict[str, Any]], alpha: float, apply_policy: bool = True
) -> tuple[dict[str, Any], dict[str, Any]]:
    key = definition["key"]
    data = _metric_data([row for row in rows if metric_available(row, definition)], key)
    c, t = data["control"], data["treatment"]
    percentile = definition.get("winsor_upper_percentile") if apply_policy else None
    threshold = None
    if percentile is not None:
        quantile = percentile / 100 if percentile > 1 else percentile
        if not 0 < quantile <= 1 or definition["kind"] != "mean":
            raise ValueError(
                "Upper winsorization applies only to means, at a percentile in (0,100]"
            )
        threshold = float(np.quantile(np.concatenate([c, t]), quantile))
        c, t = np.minimum(c, threshold), np.minimum(t, threshold)
    if definition["kind"] == "ratio":
        dc = [r.get("denominators", {}).get(key) for r in data["rows"] if r["variant"] == "control"]
        dt = [
            r.get("denominators", {}).get(key) for r in data["rows"] if r["variant"] == "treatment"
        ]
        result = delta.compare_ratio(c, t, dc, dt, alpha)
    else:
        result = fixed.compare(c, t, definition["kind"], alpha)
    data.update({"control": c, "treatment": t})
    result.update(
        {
            "key": key,
            "name": definition.get("name", key),
            "direction": definition.get("direction", "higher_is_better"),
            "outlier_policy": {
                "winsor_upper_percentile": percentile,
                "threshold": threshold,
                "scope": "pooled across arms" if percentile else "none",
            },
        }
    )
    return result, data


def analyze(
    design: dict[str, Any], rows: list[dict[str, Any]], health: list[dict[str, Any]]
) -> dict[str, Any]:
    if (
        not health
        or not any(h.get("check") == "srm_assigned" for h in health)
        or not any(h.get("check") == "srm_exposed" for h in health)
    ):
        raise ValueError("Recorded assigned and exposed health checks are required before analysis")
    digest = fingerprint(rows)
    if any(h.get("data_digest") != digest for h in health):
        raise ValueError("Health records belong to different observation data")
    if any(h.get("design_digest") != design_fingerprint(design) for h in health):
        raise ValueError("Health records belong to a different experiment design")
    if any(h.get("status") == "block" for h in health):
        return {
            "health": health,
            "metrics": [],
            "primary": None,
            "guardrails": [],
            "secondary": [],
            "segments": [],
            "cuped": {"applicable": False, "reason": "Health blocked analysis"},
            "sequential": {"applicable": False, "reason": "Health blocked analysis", "points": []},
            "decision": decide(design, None, [], health),
        }
    alpha = float(design.get("alpha", 0.05))
    metrics, raw_metrics, data_map = [], [], {}
    unavailable_metrics = []
    for definition in design["metrics"]:
        valid_counts = {
            arm: sum(
                row["variant"] == arm
                and row.get("exposed", True)
                and metric_available(row, definition)
                for row in rows
            )
            for arm in ("control", "treatment")
        }
        if min(valid_counts.values()) < 2:
            if definition["key"] == design["primary_metric_key"] or definition["key"] in design.get(
                "guardrail_metric_keys", []
            ):
                raise ValueError("Required metric health records failed to block unavailable data")
            unavailable_metrics.append(
                {
                    "key": definition["key"],
                    "name": definition.get("name", definition["key"]),
                    "reason": "Fewer than two complete exposed observations in at least one arm",
                    "n_per_arm": valid_counts,
                }
            )
            continue
        metric, data = _analyze_metric(definition, rows, alpha)
        metrics.append(metric)
        data_map[definition["key"]] = data
        if definition.get("winsor_upper_percentile") is not None:
            raw_metrics.append(_analyze_metric(definition, rows, alpha, False)[0])
    primary = next(m for m in metrics if m["key"] == design["primary_metric_key"])
    primary_definition = next(m for m in design["metrics"] if m["key"] == primary["key"])
    primary_data = data_map[primary["key"]]
    if primary["kind"] != "ratio":
        primary["bootstrap"] = fixed.bootstrap(
            primary_data["control"],
            primary_data["treatment"],
            alpha,
            int(design.get("bootstrap_seed", 20260922)),
            int(design.get("bootstrap_resamples", 400)),
        )
        # Project power at the registered effect using both achieved arm counts.
        # The planned allocation does not describe a realized imbalance.
        allocation = primary["n_treatment"] / (primary["n_control"] + primary["n_treatment"])
        primary["design_effect_projected_power"] = achieved_power(
            primary["n_control"],
            design["baseline"],
            design["mde_relative"],
            alpha,
            allocation=allocation,
            standard_deviation=design.get("standard_deviation", 1),
            kind=primary["kind"],
        )
    tested_guardrails = [
        guardrails.evaluate(m, next(d for d in design["metrics"] if d["key"] == m["key"]), alpha)
        for m in metrics
        if m["key"] in design.get("guardrail_metric_keys", [])
    ]
    adjusted: dict[str, Any] = {
        "applicable": False,
        "reason": "No complete pre-period covariate exists for this metric.",
    }
    selected = primary_data["rows"]
    if primary["kind"] != "ratio" and all(
        r.get("pre", {}).get(primary["key"]) is not None for r in selected
    ):
        pc = [r["pre"][primary["key"]] for r in selected if r["variant"] == "control"]
        pt = [r["pre"][primary["key"]] for r in selected if r["variant"] == "treatment"]
        adjusted = cuped.adjust(primary_data["control"], primary_data["treatment"], pc, pt, alpha)
    timeline: dict[str, Any] = {
        "applicable": False,
        "reason": "No longitudinal timestamps are available, or this is a ratio metric.",
        "points": [],
    }
    if design.get("has_timestamps", True) and primary["kind"] != "ratio":
        timeline = sequential.monitor(
            primary_data["control"],
            primary_data["treatment"],
            [r.get("day", 1) for r in selected if r["variant"] == "control"],
            [r.get("day", 1) for r in selected if r["variant"] == "treatment"],
            alpha,
            design.get("mixing_variance", 0.16),
        )
    secondary = fdr.correct(
        [m for m in metrics if m["key"] in design.get("secondary_metric_keys", [])],
        design.get("fdr_q", 0.05),
    )
    segments = []
    for segment in sorted({str(r.get("segment", "all")) for r in selected}):
        segment_rows = [r for r in selected if str(r.get("segment", "all")) == segment]
        if min(sum(r["variant"] == v for r in segment_rows) for v in ["control", "treatment"]) < 2:
            continue
        result, _ = _analyze_metric(primary_definition, segment_rows, alpha)
        segments.append({**result, "segment": segment})
    return {
        "health": health,
        "primary": primary,
        "metrics": metrics,
        "raw_metrics": raw_metrics,
        "unavailable_metrics": unavailable_metrics,
        "primary_without_outlier_policy": next(
            (m for m in raw_metrics if m["key"] == primary["key"]), primary
        ),
        "guardrails": tested_guardrails,
        "cuped": adjusted,
        "sequential": timeline,
        "secondary": secondary,
        "segments": fdr.correct(segments, design.get("fdr_q", 0.05)),
        "decision": decide(design, primary, tested_guardrails, health),
        "limitations": [
            "Exposure-conditioned analysis needs treatment-independent exposure and ignorable missingness.",
            "Plug-in mSPRT monitoring is an asymptotic approximation, evaluated on the committed simulated distributions.",
            "Segment and secondary metric families are adjusted separately using Benjamini-Hochberg; dependence assumptions still apply.",
            "The primary decision uses the registered fixed horizon; daily fixed-horizon decisions must not become a stopping policy.",
        ]
        + [
            f"Unavailable metric {metric['key']}: {metric['reason']}."
            for metric in unavailable_metrics
        ],
    }
