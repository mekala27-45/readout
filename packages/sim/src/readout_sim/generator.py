"""Synthetic assignment, exposure, pre-period values and correlated sessions."""

from copy import deepcopy
from typing import Any

import numpy as np
from readout_stats.decision import DEFAULT_RULE
from readout_stats.power import required_sample_size

SCENARIOS: dict[str, dict[str, Any]] = {
    "null": {
        "name": "True null",
        "effect": 0.0,
        "rho": 0.0,
        "n_per_arm": 900,
        "description": "No treatment effect; daily monitoring tests false positive control.",
    },
    "at_mde": {
        "name": "Effect at the MDE",
        "effect": 0.4,
        "rho": 0.0,
        "n_per_arm": None,
        "description": "Effect equals the design threshold exactly.",
    },
    "srm_dropout": {
        "name": "Treatment logging dropout",
        "effect": 0.4,
        "rho": 0.0,
        "n_per_arm": 10000,
        "dropout": 0.1,
        "description": "A logging defect removes ten percent of assigned treatment records.",
    },
    "guardrail_hit": {
        "name": "Primary gain, guardrail harm",
        "effect": 0.8,
        "guardrail_effect": -10.0,
        "rho": 0.0,
        "n_per_arm": 3000,
        "description": "The primary improves but the safety metric degrades beyond its margin.",
    },
    "correlated_pre": {
        "name": "Correlated pre-period",
        "effect": 0.4,
        "rho": 0.8,
        "n_per_arm": 1500,
        "description": "A pre-period covariate predicts outcome variation; theoretical reduction is rho squared.",
    },
    "ratio_metric": {
        "name": "Correlated sessions",
        "effect": 0.02,
        "rho": 0.0,
        "n_per_arm": 2000,
        "description": "Beta-binomial sessions share a user propensity; users remain the unit of inference.",
    },
    "heterogeneous": {
        "name": "One responsive segment",
        "effect": 0.0,
        "segment_effect": 1.2,
        "rho": 0.3,
        "n_per_arm": 4000,
        "description": "Only the returning segment has a treatment effect.",
    },
}


def scenarios() -> dict[str, dict[str, Any]]:
    return deepcopy(SCENARIOS)


def design_for(scenario: str) -> dict[str, Any]:
    if scenario not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario}")
    ratio = scenario == "ratio_metric"
    primary = "conversion_per_session" if ratio else "value"
    planned = 2000 if ratio else required_sample_size(10, 0.04, standard_deviation=3)["n_per_arm"]
    metrics = [
        {
            "key": primary,
            "name": "Conversion per session" if ratio else "Value per exposed unit",
            "kind": "ratio" if ratio else "mean",
            "direction": "higher_is_better",
            "guardrail_margin_relative": None,
            "winsor_upper_percentile": None,
        },
        {
            "key": "quality",
            "name": "Quality score",
            "kind": "mean",
            "direction": "higher_is_better",
            "guardrail_margin_relative": 0.05,
            "winsor_upper_percentile": None,
        },
        {
            "key": "retained",
            "name": "Retention",
            "kind": "proportion",
            "direction": "higher_is_better",
            "guardrail_margin_relative": None,
            "winsor_upper_percentile": None,
        },
    ]
    return {
        "primary_metric_key": primary,
        "metrics": metrics,
        "guardrail_metric_keys": ["quality"],
        "secondary_metric_keys": ["retained"],
        "variants": [
            {"name": "control", "allocation": 0.5},
            {"name": "treatment", "allocation": 0.5},
        ],
        "alpha": 0.05,
        "power": 0.8,
        "mde_relative": 0.05 if ratio else 0.04,
        "baseline": 0.4 if ratio else 10.0,
        "standard_deviation": 0.3 if ratio else 3.0,
        "planned_n_per_arm": planned,
        "planned_days": 30,
        "mixing_variance": 0.16,
        "decision_rule": {"text": DEFAULT_RULE},
        "bootstrap_seed": 20260922,
        "bootstrap_resamples": 400,
        "has_timestamps": True,
        "fdr_q": 0.05,
    }


def generate(
    scenario: str,
    seed: int = 20260922,
    n_per_arm: int | None = None,
    exposure_rate: float = 1.0,
    dropout: float | None = None,
) -> list[dict[str, Any]]:
    if scenario not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario}")
    if not 0 <= exposure_rate <= 1 or (dropout is not None and not 0 <= dropout < 1):
        raise ValueError("Exposure and dropout probabilities must be in range")
    config, design = SCENARIOS[scenario], design_for(scenario)
    n = 2 * int(n_per_arm or config["n_per_arm"] or design["planned_n_per_arm"])
    rng = np.random.default_rng(seed)
    treated = rng.random(n) < 0.5
    exposed = rng.random(n) < exposure_rate
    day = np.repeat(np.arange(1, 31), np.ceil(n / 30).astype(int))[:n]
    segment_index = rng.integers(0, 4, n)
    segment_names = ["returning", "new", "mobile", "desktop"]
    pre = rng.normal(size=n)
    noise = rng.normal(size=n)
    rho = config["rho"]
    effects = np.full(n, config["effect"])
    if scenario == "heterogeneous":
        effects = np.where(segment_index == 0, config["segment_effect"], 0)
    outcome = 10 + 3 * (rho * pre + np.sqrt(1 - rho**2) * noise) + treated * exposed * effects
    quality = 100 + rng.normal(0, 10, n) + treated * exposed * config.get("guardrail_effect", 0)
    retained = rng.binomial(1, 0.4 + treated * exposed * (0 if scenario == "null" else 0.01))
    sessions = 1 + rng.poisson(8, n)
    mean_probability = (
        0.4 + treated * exposed * config["effect"]
        if scenario == "ratio_metric"
        else np.full(n, 0.4)
    )
    propensity = rng.beta(mean_probability * 3, (1 - mean_probability) * 3)
    conversions = rng.binomial(sessions, propensity)
    dropped = treated & (rng.random(n) < (config.get("dropout", 0) if dropout is None else dropout))
    rows = []
    for i in np.flatnonzero(~dropped):
        primary = design["primary_metric_key"]
        rows.append(
            {
                "unit_id": f"{scenario}-{seed}-{i}",
                "variant": "treatment" if treated[i] else "control",
                "exposed": bool(exposed[i]),
                "day": int(day[i]),
                "segment": segment_names[int(segment_index[i])],
                "metrics": {
                    primary: float(conversions[i] if scenario == "ratio_metric" else outcome[i]),
                    "quality": float(quality[i]),
                    "retained": float(retained[i]),
                },
                "pre": {primary: float(10 + 3 * pre[i])} if scenario != "ratio_metric" else {},
                "denominators": {primary: float(sessions[i])} if scenario == "ratio_metric" else {},
            }
        )
    return rows
