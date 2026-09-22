"""Normal-mixture monitoring; plug-in variances are asymptotic approximations."""

from typing import Any

import numpy as np
from numpy.typing import ArrayLike
from scipy import stats


def monitor_summaries(
    estimates: ArrayLike, variances: ArrayLike, alpha: float = 0.05, mixing_variance: float = 0.16
) -> dict[str, Any]:
    d, v = np.asarray(estimates, dtype=float), np.asarray(variances, dtype=float)
    if (
        d.shape != v.shape
        or d.size == 0
        or not np.isfinite(d).all()
        or not np.isfinite(v).all()
        or np.any(v <= 0)
        or not 0 < alpha < 1
        or mixing_variance <= 0
    ):
        raise ValueError(
            "Finite aligned estimates, positive variances and mixing variance are required"
        )
    # Time is the last axis, allowing calibration to pass a batch of experiments.
    tau = mixing_variance
    log_lr = -0.5 * np.log1p(tau / v) + d**2 * tau / (2 * v * (v + tau))
    running_log = np.maximum.accumulate(log_lr, axis=-1)
    p = np.exp(-np.maximum(running_log, 0))
    radius = np.sqrt(v * (v + tau) / tau * (2 * np.log(1 / alpha) + np.log1p(tau / v)))
    naive_radius = stats.norm.ppf(1 - alpha / 2) * np.sqrt(v)
    return {
        "p_value": p.tolist(),
        "ci_low": (d - radius).tolist(),
        "ci_high": (d + radius).tolist(),
        "naive_low": (d - naive_radius).tolist(),
        "naive_high": (d + naive_radius).tolist(),
        "naive_p_value": (2 * stats.norm.sf(np.abs(d / np.sqrt(v)))).tolist(),
        "log_likelihood_ratio": log_lr.tolist(),
    }


def monitor(
    control: ArrayLike,
    treatment: ArrayLike,
    day_control: ArrayLike,
    day_treatment: ArrayLike,
    alpha: float = 0.05,
    mixing_variance: float = 0.16,
) -> dict[str, Any]:
    c, t = np.asarray(control, dtype=float), np.asarray(treatment, dtype=float)
    dc, dt = np.asarray(day_control), np.asarray(day_treatment)
    if len(c) != len(dc) or len(t) != len(dt):
        raise ValueError("Every outcome needs an observation day")
    days = sorted(set(dc.tolist() + dt.tolist()))
    if len(days) < 2:
        return {
            "applicable": False,
            "reason": "No longitudinal timestamps: a sequential monitor cannot be reconstructed.",
            "points": [],
        }
    records = []
    for day in days:
        x, y = c[dc <= day], t[dt <= day]
        if min(len(x), len(y)) < 2:
            continue
        variance = float(x.var(ddof=1) / len(x) + y.var(ddof=1) / len(y))
        if variance <= 0:
            continue
        records.append(
            {
                "day": int(day),
                "estimate": float(y.mean() - x.mean()),
                "variance": variance,
                "n_control": len(x),
                "n_treatment": len(y),
            }
        )
    if not records:
        return {
            "applicable": False,
            "reason": "Insufficient nonconstant outcomes for monitoring.",
            "points": [],
        }
    calculated = monitor_summaries(
        [r["estimate"] for r in records], [r["variance"] for r in records], alpha, mixing_variance
    )
    for i, record in enumerate(records):
        record.update({key: values[i] for key, values in calculated.items()})
    return {
        "applicable": True,
        "points": records,
        "mixing_variance": mixing_variance,
        "method": "normal-mixture mSPRT with plug-in variance",
        "limitation": "Asymptotic approximation for means and proportions; finite-sample anytime validity is not guaranteed with estimated variances.",
        "first_rejection_day": next((r["day"] for r in records if r["p_value"] < alpha), None),
        "naive_first_rejection_day": next(
            (r["day"] for r in records if r["naive_p_value"] < alpha), None
        ),
        "final_p_value": records[-1]["p_value"],
    }


def monitor_batch(
    control: ArrayLike,
    treatment: ArrayLike,
    cuts: ArrayLike,
    alpha: float = 0.05,
    mixing_variance: float = 0.16,
) -> dict[str, Any]:
    """The same sufficient-statistic kernel for independent calibration batches."""
    c, t = np.asarray(control, dtype=float), np.asarray(treatment, dtype=float)
    n = np.asarray(cuts, dtype=int)
    if c.ndim != 2 or c.shape != t.shape or n.min() < 2 or n.max() > c.shape[-1]:
        raise ValueError(
            "Batched monitoring requires matched experiment-by-unit arrays and valid cuts"
        )
    mc, mt = np.cumsum(c, axis=-1)[:, n - 1] / n, np.cumsum(t, axis=-1)[:, n - 1] / n
    vc = (np.cumsum(c**2, axis=-1)[:, n - 1] - n * mc**2) / (n - 1)
    vt = (np.cumsum(t**2, axis=-1)[:, n - 1] - n * mt**2) / (n - 1)
    return monitor_summaries(mt - mc, (vc + vt) / n, alpha, mixing_variance)
