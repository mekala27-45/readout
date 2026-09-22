"""Fixed horizon inference and unit bootstrap cross checks."""

from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy import stats


def samples(values: ArrayLike) -> NDArray[np.float64]:
    result = np.asarray(values, dtype=float)
    if result.ndim != 1 or len(result) < 2 or not np.isfinite(result).all():
        raise ValueError("At least two finite observations are required in each arm")
    return result


def from_summary(
    mean_c: float,
    mean_t: float,
    var_c: float,
    var_t: float,
    n_c: int,
    n_t: int,
    alpha: float = 0.05,
    kind: str = "mean",
) -> dict[str, Any]:
    if min(n_c, n_t) < 2 or not 0 < alpha < 1:
        raise ValueError("Invalid sample size or alpha")
    vc, vt = var_c / n_c, var_t / n_t
    se = float(np.sqrt(vc + vt))
    estimate = mean_t - mean_c
    # Normalize first to avoid squaring tiny or very large variances.
    df = 1 / ((vc / (vc + vt)) ** 2 / (n_c - 1) + (vt / (vc + vt)) ** 2 / (n_t - 1)) if se else None
    critical = (
        float(stats.t.ppf(1 - alpha / 2, df))
        if kind == "mean" and df
        else float(stats.norm.ppf(1 - alpha / 2))
    )
    if kind == "proportion":
        pooled = (mean_c * n_c + mean_t * n_t) / (n_c + n_t)
        test_se = float(np.sqrt(pooled * (1 - pooled) * (1 / n_c + 1 / n_t)))
    else:
        test_se = se
    if test_se:
        p = float(
            2
            * (
                stats.t.sf(abs(estimate / test_se), df)
                if kind == "mean" and df
                else stats.norm.sf(abs(estimate / test_se))
            )
        )
    else:
        p = 1.0 if estimate == 0 else 0.0
    relative = mean_t / mean_c - 1 if mean_c != 0 else None
    relative_se = (
        float(
            np.hypot(np.sqrt(vt) / abs(mean_c), abs(mean_t / mean_c) * (np.sqrt(vc) / abs(mean_c)))
        )
        if mean_c != 0
        else None
    )
    if (
        relative is not None
        and relative_se is not None
        and (not np.isfinite(relative) or not np.isfinite(relative_se))
    ):
        relative = relative_se = None
    relative_critical = float(stats.norm.ppf(1 - alpha / 2))
    return {
        "estimate": float(estimate),
        "ci_low": float(estimate - critical * se),
        "ci_high": float(estimate + critical * se),
        "relative": relative,
        "relative_ci_low": relative - relative_critical * relative_se
        if relative is not None and relative_se is not None
        else None,
        "relative_ci_high": relative + relative_critical * relative_se
        if relative is not None and relative_se is not None
        else None,
        "relative_se": relative_se,
        "p_value": p,
        "se": se,
        "control_mean": float(mean_c),
        "treatment_mean": float(mean_t),
        "n_control": int(n_c),
        "n_treatment": int(n_t),
        "df": float(df) if df else None,
        "kind": kind,
        "alpha": alpha,
        "method": {
            "mean": "Welch t",
            "proportion": "pooled two-sample z; unpooled Wald interval",
            "ratio": "unit delta method",
        }[kind],
    }


def compare(
    control: ArrayLike, treatment: ArrayLike, kind: str = "mean", alpha: float = 0.05
) -> dict[str, Any]:
    c, t = samples(control), samples(treatment)
    if kind not in {"mean", "proportion"}:
        raise ValueError("Use compare_ratio for ratio metrics")
    if kind == "proportion" and (not np.isin(c, [0, 1]).all() or not np.isin(t, [0, 1]).all()):
        raise ValueError("Proportions require binary unit outcomes")
    mc, mt = float(c.mean()), float(t.mean())
    vc = mc * (1 - mc) if kind == "proportion" else float(c.var(ddof=1))
    vt = mt * (1 - mt) if kind == "proportion" else float(t.var(ddof=1))
    return from_summary(mc, mt, vc, vt, len(c), len(t), alpha, kind)


def bootstrap(
    control: ArrayLike,
    treatment: ArrayLike,
    alpha: float = 0.05,
    seed: int = 20260922,
    draws: int = 400,
) -> dict[str, Any]:
    c, t = samples(control), samples(treatment)
    rng = np.random.default_rng(seed)
    differences = np.empty(draws)
    # A loop bounds memory even for the public experiment.
    for i in range(draws):
        differences[i] = rng.choice(t, len(t)).mean() - rng.choice(c, len(c)).mean()
    low, high = np.quantile(differences, [alpha / 2, 1 - alpha / 2])
    return {
        "estimate": float(t.mean() - c.mean()),
        "ci_low": float(low),
        "ci_high": float(high),
        "draws": draws,
        "seed": seed,
        "method": "unit percentile bootstrap",
    }
