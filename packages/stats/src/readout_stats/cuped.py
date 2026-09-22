"""Pooled pre-period control-variate adjustment."""
from typing import Any

import numpy as np
from numpy.typing import ArrayLike

from readout_stats.fixed import compare, samples


def adjust(control: ArrayLike, treatment: ArrayLike, pre_control: ArrayLike, pre_treatment: ArrayLike, alpha: float = 0.05) -> dict[str, Any]:
    c, t, pc, pt = samples(control), samples(treatment), samples(pre_control), samples(pre_treatment)
    if len(c) != len(pc) or len(t) != len(pt):
        raise ValueError("Pre and post outcomes must pair on the same randomized unit")
    x, y = np.concatenate([pc, pt]), np.concatenate([c, t])
    variance_x = float(x.var(ddof=1))
    theta = float(np.cov(x, y, ddof=1)[0, 1] / variance_x) if variance_x > 0 else 0.0
    adjusted = compare(c - theta * (pc - x.mean()), t - theta * (pt - x.mean()), alpha=alpha)
    raw = compare(c, t, alpha=alpha)
    reduction = 1 - adjusted["se"]**2 / raw["se"]**2 if raw["se"] > 0 else 0.0
    return {"applicable": True, "theta": theta, "adjusted": adjusted, "unadjusted": raw, "variance_reduction": float(reduction), "variance_reduction_percent": float(100 * reduction), "equivalent_sample_multiplier": float(1 / (1 - reduction)) if reduction < 1 else None, "equivalent_sample_saved": float((len(c) + len(t)) * reduction), "n_saved": float((len(c) + len(t)) * reduction), "method": "pooled theta = covariance(pre, post) / variance(pre)", "limitation": "Same-sample theta has small finite-sample bias; pre-period covariates must be unaffected by treatment."}
