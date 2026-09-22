"""One-sided non-inferiority tests on a relative degradation margin."""

from typing import Any

from scipy import stats


def evaluate(
    metric: dict[str, Any], definition: dict[str, Any], alpha: float = 0.05
) -> dict[str, Any]:
    margin = definition.get("guardrail_margin_relative")
    if margin is None or margin < 0:
        raise ValueError("A nonnegative non-inferiority margin must be pre-registered")
    sign = -1 if definition.get("direction") == "lower_is_better" else 1
    # Margin is on the control scale; uncertainty in that control scale is retained.
    relative = metric.get("relative")
    se = metric.get("relative_se")
    if relative is None or se is None or metric["control_mean"] <= 0:
        return {
            **metric,
            "margin": margin,
            "passed": False,
            "reason": "Relative guardrail needs a positive control mean",
            "noninferiority_p_value": None,
        }
    lower = sign * relative - float(stats.norm.ppf(1 - alpha)) * se
    p = (
        float(stats.norm.sf((sign * relative + margin) / se))
        if se
        else (0.0 if sign * relative > -margin else 1.0)
    )
    return {
        **metric,
        "margin": margin,
        "direction": definition.get("direction", "higher_is_better"),
        "passed": bool(lower > -margin),
        "noninferiority_p_value": p,
        "one_sided_good_direction_low": lower,
        "noninferiority_alpha": alpha,
    }
