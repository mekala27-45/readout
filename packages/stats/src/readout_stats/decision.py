"""Deterministic pre-registered decision policy with explicit precedence."""

import math
from typing import Any

from readout_stats.power import required_sample_size

DEFAULT_RULE = "Blocked health blocks analysis. A failing guardrail gives no_ship. Otherwise ship when the primary interval excludes zero in the good direction. Otherwise no_ship when the interval excludes the MDE in the good direction. Otherwise extend using the design calculator. Guardrail, ship, futility, extend is the precedence."


def decide(
    design: dict[str, Any],
    primary: dict[str, Any] | None,
    guardrails: list[dict[str, Any]],
    health: list[dict[str, Any]],
) -> dict[str, Any]:
    rule = design.get("decision_rule", {"text": DEFAULT_RULE})
    rule_text = rule.get("text", DEFAULT_RULE) if isinstance(rule, dict) else str(rule)
    allocation = next(
        (
            float(variant["allocation"])
            for variant in design.get("variants", [])
            if variant["name"] == "treatment"
        ),
        0.5,
    )
    planned = int(design.get("planned_n_per_arm", 0))
    planned_by_arm = {
        "control": planned,
        "treatment": math.ceil(planned * allocation / (1 - allocation)),
    }
    achieved_counts = (
        {"control": int(primary["n_control"]), "treatment": int(primary["n_treatment"])}
        if primary
        else {}
    )
    provisional = bool(
        primary and any(achieved_counts[arm] < planned_by_arm[arm] for arm in achieved_counts)
    )
    base = {
        "rule": rule_text,
        "additional_n_per_arm": 0,
        "provisional": provisional,
        "planned_n_per_arm": planned,
        "planned_n_by_arm": planned_by_arm,
        "achieved_n_per_arm": achieved_counts,
    }
    if not health or any(h["status"] == "block" for h in health):
        return {
            **base,
            "decision": "blocked",
            "reason": "Health gate blocked analysis; no metric verdict is available.",
        }
    if primary is None:
        return {**base, "decision": "blocked", "reason": "Primary metric is unavailable."}
    if any(not g["passed"] for g in guardrails):
        return {
            **base,
            "decision": "no_ship",
            "reason": "At least one guardrail did not demonstrate non-inferiority at its pre-registered margin.",
        }
    definition = next(m for m in design["metrics"] if m["key"] == design["primary_metric_key"])
    sign = -1 if definition.get("direction") == "lower_is_better" else 1
    low = primary["ci_low"] if sign == 1 else -primary["ci_high"]
    high = primary["ci_high"] if sign == 1 else -primary["ci_low"]
    if low > 0:
        return {
            **base,
            "decision": "ship",
            "reason": "The primary interval excludes zero in the favorable direction and all guardrails pass.",
        }
    mde = abs(design["baseline"]) * design["mde_relative"]
    if high < mde:
        return {
            **base,
            "decision": "no_ship",
            "reason": "The primary interval excludes the pre-registered MDE in the favorable direction.",
        }
    if definition.get("kind") == "ratio":
        return {
            **base,
            "decision": "extend",
            "reason": "The ratio interval remains inconclusive. Ratio power planning is unavailable; use a pilot to estimate unit influence variance before registering an extension.",
        }
    achieved = primary["n_control"]
    planning_effect = min(mde, max(abs(primary["estimate"]), mde / 2))
    required = required_sample_size(
        baseline=design["baseline"],
        mde_relative=planning_effect / abs(design["baseline"]),
        alpha=design.get("alpha", 0.05),
        power=design.get("power", 0.8),
        allocation=allocation,
        standard_deviation=design.get("standard_deviation", 1),
        kind=definition.get("kind", "mean") if definition.get("kind") != "ratio" else "mean",
    )
    additional = max(0, required["n_per_arm"] - achieved)
    additional_by_arm = {
        arm: int(
            max(required[f"n_{arm}"] - achieved_counts[arm], math.ceil(achieved_counts[arm] * 0.1))
        )
        for arm in achieved_counts
    }
    return {
        **base,
        "decision": "extend",
        "reason": "The interval remains inconclusive. Additional sample is a planning heuristic; any extension needs a new decision horizon or the sequential monitor.",
        "additional_n_per_arm": int(max(additional, math.ceil(achieved * 0.1))),
        "additional_n_by_arm": additional_by_arm,
        "extension_effect_absolute": planning_effect,
    }
