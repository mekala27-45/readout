"""Ratio-of-sums inference preserving within-unit covariance."""
from typing import Any

import numpy as np
from numpy.typing import ArrayLike

from readout_stats.fixed import from_summary, samples


def ratio_summary(numerators: ArrayLike, denominators: ArrayLike) -> tuple[float, float, int]:
    x, y = samples(numerators), samples(denominators)
    if len(x) != len(y) or np.any(y <= 0):
        raise ValueError("Ratio denominators must be positive and paired with numerators")
    ratio = float(x.mean() / y.mean())
    influence = (x - ratio * y) / y.mean()
    return ratio, float(influence.var(ddof=1)), len(x)


def compare_ratio(control: ArrayLike, treatment: ArrayLike, denominator_c: ArrayLike, denominator_t: ArrayLike, alpha: float = 0.05) -> dict[str, Any]:
    mc, vc, nc = ratio_summary(control, denominator_c)
    mt, vt, nt = ratio_summary(treatment, denominator_t)
    return from_summary(mc, mt, vc, vt, nc, nt, alpha, "ratio")


def naive_session_interval(control: ArrayLike, treatment: ArrayLike, denominator_c: ArrayLike, denominator_t: ArrayLike, alpha: float = 0.05) -> dict[str, Any]:
    """Intentionally invalid comparator: independent Bernoulli sessions."""
    c, t = samples(control), samples(treatment)
    dc, dt = samples(denominator_c), samples(denominator_t)
    mc, mt = float(c.sum() / dc.sum()), float(t.sum() / dt.sum())
    return from_summary(mc, mt, mc * (1 - mc), mt * (1 - mt), int(dc.sum()), int(dt.sum()), alpha, "proportion")
