"""Known-truth generation is independent; the harness only counts engine outcomes."""

import json
import math
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
from readout_sim import generate
from readout_stats import cuped, delta, fixed, health, power, sequential
from scipy import stats

SEED = 20260922


def binomial(count: int, total: int) -> dict[str, Any]:
    if not 0 <= count <= total or total < 1:
        raise ValueError("A nonempty binomial sample is required")
    # Wilson interval computed by a library independent of the inference engine.
    interval = stats.binomtest(count, total).proportion_ci(confidence_level=0.95, method="wilson")
    return {
        "rate": count / total,
        "low": float(interval.low),
        "high": float(interval.high),
        "count": count,
        "total": total,
    }


def _peeking(
    rng: np.random.Generator, repetitions: int, kind: str = "mean"
) -> list[dict[str, Any]]:
    days, daily_n = 30, 30
    shape = (repetitions, days * daily_n)
    c = rng.normal(10, 3, shape) if kind == "mean" else rng.binomial(1, 0.4, shape)
    t = rng.normal(10, 3, shape) if kind == "mean" else rng.binomial(1, 0.4, shape)
    monitored = sequential.monitor_batch(
        c, t, np.arange(1, 31) * daily_n, mixing_variance=0.16 if kind == "mean" else 0.0016
    )
    naive = np.maximum.accumulate(np.asarray(monitored["naive_p_value"]) < 0.05, axis=1)
    valid = np.asarray(monitored["p_value"]) < 0.05
    return [
        {
            "day": day + 1,
            "naive": binomial(int(naive[:, day].sum()), repetitions),
            "sequential": binomial(int(valid[:, day].sum()), repetitions),
        }
        for day in range(days)
    ]


def _power(rng: np.random.Generator, repetitions: int, kind: str = "mean") -> list[dict[str, Any]]:
    baseline, relative, sigma = (10.0, 0.04, 3.0) if kind == "mean" else (0.4, 0.1, 1.0)
    plan = power.required_sample_size(baseline, relative, standard_deviation=sigma, kind=kind)
    records = []
    for multiple in [0.5, 0.75, 1, 1.5, 2]:
        n = math.ceil(plan["n_per_arm"] * multiple)
        count = 0
        for _ in range(repetitions):
            if kind == "mean":
                c, t = rng.normal(10, 3, n), rng.normal(10.4, 3, n)
            else:
                c, t = rng.binomial(1, 0.4, n), rng.binomial(1, 0.44, n)
            result = fixed.compare(c, t, kind=kind)
            count += result["p_value"] < 0.05
        records.append(
            {
                "multiple": multiple,
                "n_per_arm": n,
                "planned_n_per_arm": plan["n_per_arm"],
                "theoretical": power.achieved_power(
                    n, baseline, relative, standard_deviation=sigma, kind=kind
                ),
                "requested_power": 0.8,
                **binomial(count, repetitions),
            }
        )
    return records


def _srm(rng: np.random.Generator, repetitions: int) -> list[dict[str, Any]]:
    records = []
    for size in [1000, 10000, 100000]:
        for dropout in [0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.10]:
            blocked = 0
            for _ in range(repetitions):
                assigned_t = rng.binomial(size * 2, 0.5)
                observed_t = rng.binomial(assigned_t, 1 - dropout)
                result = health.srm(
                    {"control": size * 2 - int(assigned_t), "treatment": int(observed_t)}
                )
                blocked += result["status"] == "block"
            records.append(
                {"n_per_arm": size, "dropout": dropout, **binomial(blocked, repetitions)}
            )
    return records


def _cuped(rng: np.random.Generator, repetitions: int) -> dict[str, Any]:
    records = []
    for i in range(repetitions):
        pc, pt = rng.normal(size=600), rng.normal(size=600)
        c = 10 + 3 * (0.8 * pc + 0.6 * rng.normal(size=600))
        t = 10.4 + 3 * (0.8 * pt + 0.6 * rng.normal(size=600))
        result = cuped.adjust(c, t, pc, pt)
        records.append(
            {
                "replicate": i,
                "unadjusted": result["unadjusted"]["estimate"],
                "adjusted": result["adjusted"]["estimate"],
                "unadjusted_ci_low": result["unadjusted"]["ci_low"],
                "unadjusted_ci_high": result["unadjusted"]["ci_high"],
                "adjusted_ci_low": result["adjusted"]["ci_low"],
                "adjusted_ci_high": result["adjusted"]["ci_high"],
                "reduction": result["variance_reduction"],
            }
        )
    reductions = np.asarray([r["reduction"] for r in records])
    raw = np.asarray([r["unadjusted"] for r in records])
    adjusted = np.asarray([r["adjusted"] for r in records])
    reduction_se = float(reductions.std(ddof=1) / np.sqrt(repetitions))
    estimate_se = float(adjusted.std(ddof=1) / np.sqrt(repetitions))
    empirical_reduction = 1 - float(adjusted.var(ddof=1) / raw.var(ddof=1))
    # Independently evaluate the spread of estimates, without engine SE formulas.
    bootstrap_indices = rng.integers(0, repetitions, size=(2000, repetitions))
    reduction_draws = 1 - adjusted[bootstrap_indices].var(axis=1, ddof=1) / raw[
        bootstrap_indices
    ].var(axis=1, ddof=1)
    empirical_low, empirical_high = np.quantile(reduction_draws, [0.025, 0.975])
    return {
        "rho": 0.8,
        "expected_reduction": 0.64,
        "true_effect": 0.4,
        "replicates": repetitions,
        "variance_reduction": float(reductions.mean()),
        "low": float(reductions.mean() - 1.96 * reduction_se),
        "high": float(reductions.mean() + 1.96 * reduction_se),
        "empirical_variance_reduction": empirical_reduction,
        "empirical_low": float(empirical_low),
        "empirical_high": float(empirical_high),
        "bootstrap_draws": 2000,
        "estimate": float(adjusted.mean()),
        "ci_low": float(adjusted.mean() - 1.96 * estimate_se),
        "ci_high": float(adjusted.mean() + 1.96 * estimate_se),
        "records": records,
    }


def _delta(rng: np.random.Generator, repetitions: int) -> dict[str, Any]:
    delta_count = naive_count = 0
    for _ in range(repetitions):
        dc, dt = 1 + rng.poisson(8, 2000), 1 + rng.poisson(8, 2000)
        pc, pt = rng.beta(0.4 * 3, 0.6 * 3, 2000), rng.beta(0.42 * 3, 0.58 * 3, 2000)
        c, t = rng.binomial(dc, pc), rng.binomial(dt, pt)
        result = delta.compare_ratio(c, t, dc, dt)
        naive = delta.naive_session_interval(c, t, dc, dt)
        delta_count += result["ci_low"] <= 0.02 <= result["ci_high"]
        naive_count += naive["ci_low"] <= 0.02 <= naive["ci_high"]
    return {
        "nominal": 0.95,
        "true_effect": 0.02,
        "n_per_arm": 2000,
        "delta": binomial(delta_count, repetitions),
        "naive": binomial(naive_count, repetitions),
        "intraclass_correlation": 0.25,
    }


def _rejection_days(rng: np.random.Generator, repetitions: int) -> dict[str, Any]:
    n = power.required_sample_size(10, 0.04, standard_deviation=3)["n_per_arm"]
    c, t = rng.normal(10, 3, (repetitions, n)), rng.normal(10.4, 3, (repetitions, n))
    cuts = np.linspace(30, n, 30, dtype=int)
    rows = []
    for mixing in [0.016, 0.16, 1.6]:
        result = sequential.monitor_batch(c, t, cuts, mixing_variance=mixing)
        rejected = np.asarray(result["p_value"]) < 0.05
        ever = rejected.any(axis=1)
        first = np.argmax(rejected, axis=1)[ever] + 1
        histogram = [{"day": day, "count": int(np.sum(first == day))} for day in range(1, 31)]
        rows.append(
            {
                "mixing_variance": mixing,
                **binomial(int(ever.sum()), repetitions),
                "median_rejection_day": float(np.median(first)) if len(first) else None,
                "rejection_day_q25": float(np.quantile(first, 0.25)) if len(first) else None,
                "rejection_day_q75": float(np.quantile(first, 0.75)) if len(first) else None,
                "first_rejection_days": histogram,
                "not_rejected": int((~ever).sum()),
                "median_is_conditional_on_rejection": True,
            }
        )
    return {"n_per_arm": n, "mixing_sensitivity": rows, "true_effect": 0.4, "planned_days": 30}


def _exposure() -> dict[str, Any]:
    rows = generate("at_mde", seed=SEED + 800, n_per_arm=50000, exposure_rate=0.6)
    all_c = [r["metrics"]["value"] for r in rows if r["variant"] == "control"]
    all_t = [r["metrics"]["value"] for r in rows if r["variant"] == "treatment"]
    exposed_c = [r["metrics"]["value"] for r in rows if r["variant"] == "control" and r["exposed"]]
    exposed_t = [
        r["metrics"]["value"] for r in rows if r["variant"] == "treatment" and r["exposed"]
    ]
    return {
        "seed": SEED + 800,
        "exposure_rate": 0.6,
        "true_effect": 0.4,
        "expected_itt_effect": 0.24,
        "assigned": fixed.compare(all_c, all_t),
        "exposed": fixed.compare(exposed_c, exposed_t),
        "assumption": "Exposure generated independently of assignment, pre-period value and potential outcomes.",
    }


def pricepoint_reproduction() -> dict[str, Any]:
    root = Path(__file__).resolve().parents[4]
    assumptions = json.loads((root / "experiments/pricepoint/assumptions.json").read_text())
    sigma = assumptions["sigma"]
    effect = abs(assumptions["assumed_elasticity"] * math.log1p(assumptions["price_change"]))
    result = power.required_sample_size(
        1, effect, alpha=assumptions["alpha"], power=assumptions["power"], standard_deviation=sigma
    )
    return {
        "assumed_elasticity": assumptions["assumed_elasticity"],
        "price_change": assumptions["price_change"],
        "effect_absolute": effect,
        "effect_scale": "log demand, using elasticity times log1p price change",
        "standard_deviation": sigma,
        "n_per_arm": result["n_per_arm"],
        "published_n_per_arm": assumptions["units_per_arm"],
        "alpha": assumptions["alpha"],
        "power": assumptions["power"],
        "source_commit": "e1a1db84249c562f895de23d5ec6627675ee1147",
        "source": "experiments/pricepoint/source-plan_experiment.py",
        "documentation_gap": "No missing variance assumption: sigma is the measured held-out log1p-demand forecast residual standard deviation. Serial dependence and interference still require a clustered pilot.",
    }


def run_calibration(full: bool = True) -> dict[str, Any]:
    repetitions, validation = (1000, 500) if full else (100, 50)
    # Separate named streams prevent changes in one study from changing another.
    streams = [np.random.default_rng(child) for child in np.random.SeedSequence(SEED).spawn(8)]
    result: dict[str, Any] = {
        "generated_at": datetime.now(UTC).isoformat(),
        "source": "simulated",
        "seed": SEED,
        "full": full,
        "alpha": 0.05,
        "peeking_replicates": repetitions,
        "validation_replicates": validation,
        "peeking": _peeking(streams[0], repetitions),
        "peeking_proportion": _peeking(streams[1], repetitions, "proportion"),
        "power": _power(streams[2], validation),
        "power_proportion": _power(streams[3], validation, "proportion"),
        "srm": _srm(streams[4], validation),
        "cuped": _cuped(streams[5], validation),
        "delta": _delta(streams[6], validation),
        "at_mde": _rejection_days(streams[7], validation),
        "exposure": _exposure(),
        "pricepoint": pricepoint_reproduction(),
        "limitations": [
            "The mSPRT uses estimated variance. Calibration supports these simulated distributions and sample schedules, not a universal finite-sample guarantee.",
            "Wilson intervals measure Monte Carlo uncertainty, not robustness to misspecified data-generating processes.",
            "CUPED uses pooled same-sample theta; finite-sample bias is possible.",
            "Exposure is independent in this simulation. Conditioning on treatment-affected exposure can introduce selection bias.",
        ],
    }
    result["mixing_sensitivity"] = result["at_mde"]["mixing_sensitivity"]
    return result
