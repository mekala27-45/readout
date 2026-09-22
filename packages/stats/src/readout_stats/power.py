"""Two-sided normal-approximation planning with explicit allocation."""

import math
from typing import Any

import numpy as np
from scipy import optimize, stats


def _inputs(
    baseline: float,
    mde_relative: float,
    alpha: float,
    power: float,
    allocation: float,
    standard_deviation: float,
    kind: str,
) -> tuple[float, float, float]:
    if (
        baseline == 0
        or not 0 < alpha < 1
        or not alpha < power < 1
        or not 0 < allocation < 1
        or mde_relative <= 0
        or standard_deviation <= 0
    ):
        raise ValueError(
            "Nonzero baseline, positive MDE and SD, and valid probabilities are required"
        )
    effect = abs(baseline) * mde_relative
    if kind == "proportion":
        if not 0 < baseline < 1 or baseline + effect >= 1:
            raise ValueError(
                "Proportion baseline and alternative must lie strictly between zero and one"
            )
        vc, vt = baseline * (1 - baseline), (baseline + effect) * (1 - baseline - effect)
    elif kind == "mean":
        vc = vt = standard_deviation**2
    else:
        raise ValueError("Planning supports means and proportions")
    return effect, vc, vt


def required_sample_size(
    baseline: float,
    mde_relative: float,
    alpha: float = 0.05,
    power: float = 0.8,
    allocation: float = 0.5,
    standard_deviation: float = 1.0,
    kind: str = "mean",
    daily_units: float | None = None,
) -> dict[str, Any]:
    effect, vc, vt = _inputs(
        baseline, mde_relative, alpha, power, allocation, standard_deviation, kind
    )
    ratio = allocation / (1 - allocation)
    z_alpha, z_power = float(stats.norm.ppf(1 - alpha / 2)), float(stats.norm.ppf(power))
    if kind == "proportion":
        pooled = baseline + allocation * effect
        numerator = z_alpha * math.sqrt(
            pooled * (1 - pooled) * (1 + 1 / ratio)
        ) + z_power * math.sqrt(vc + vt / ratio)
        raw_n = numerator**2 / effect**2
    else:
        raw_n = (z_alpha + z_power) ** 2 * (vc + vt / ratio) / effect**2
    n_c = math.ceil(raw_n)
    n_t = math.ceil(n_c * ratio)
    if daily_units is not None and daily_units <= 0:
        raise ValueError("Daily units must be positive")
    return {
        "n_per_arm": n_c,
        "n_control": n_c,
        "n_treatment": n_t,
        "total": n_c + n_t,
        "days": math.ceil(max(n_c / (1 - allocation), n_t / allocation) / daily_units)
        if daily_units
        else None,
        "effect_absolute": effect,
        "alpha": alpha,
        "power": power,
        "allocation": allocation,
        "method": "two-sided normal approximation",
        "raw_n_control": raw_n,
    }


def achieved_power(
    n_per_arm: float,
    baseline: float,
    mde_relative: float,
    alpha: float = 0.05,
    allocation: float = 0.5,
    standard_deviation: float = 1.0,
    kind: str = "mean",
) -> float:
    effect, vc, vt = _inputs(
        baseline,
        mde_relative,
        alpha,
        0.8 if alpha < 0.8 else (alpha + 1) / 2,
        allocation,
        standard_deviation,
        kind,
    )
    if n_per_arm <= 0:
        raise ValueError("Sample size must be positive")
    ratio = allocation / (1 - allocation)
    se = np.sqrt((vc + vt / ratio) / n_per_arm)
    critical = float(stats.norm.ppf(1 - alpha / 2))
    if kind == "proportion":
        pooled = baseline + allocation * effect
        critical *= float(np.sqrt(pooled * (1 - pooled) * (1 + 1 / ratio) / n_per_arm) / se)
    signal = effect / se
    return float(stats.norm.sf(critical - signal) + stats.norm.cdf(-critical - signal))


def minimum_detectable_effect(
    n_per_arm: int,
    baseline: float,
    alpha: float = 0.05,
    power: float = 0.8,
    allocation: float = 0.5,
    standard_deviation: float = 1.0,
    kind: str = "mean",
) -> float:
    upper = (1 - baseline) / abs(baseline) * 0.999 if kind == "proportion" else 1000.0
    return float(
        optimize.brentq(
            lambda x: (
                achieved_power(n_per_arm, baseline, x, alpha, allocation, standard_deviation, kind)
                - power
            ),
            1e-9,
            upper,
        )
    )


sample_size = required_sample_size


def design_power(payload: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "baseline",
        "mde_relative",
        "alpha",
        "power",
        "allocation",
        "standard_deviation",
        "kind",
        "daily_units",
    }
    return required_sample_size(**{k: v for k, v in payload.items() if k in allowed})
