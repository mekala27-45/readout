"""FDRResult and BH function ported unchanged from cityflow.

Source commit: 2163b362d75458e8485f3f78fdec85b7322e6fd7.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt


@dataclass(frozen=True, slots=True)
class FDRResult:
    """The outcome of one Benjamini-Hochberg step-up run."""

    rejected: npt.NDArray[np.bool_]
    adjusted: npt.NDArray[np.float64]
    n_comparisons: int
    n_rejected: int
    q: float
    critical_p: float | None


def benjamini_hochberg(p_values: npt.ArrayLike, q: float = 0.05) -> FDRResult:
    """Benjamini-Hochberg step-up procedure at false discovery rate q.

    Args:
        p_values: raw p values, NaN where a test could not be run.
        q: the false discovery rate to control, 0.05 by default.

    Returns:
        An FDRResult whose adjusted values are the standard BH adjusted p
        values: the running minimum of m/i times p(i) taken from the largest p
        downwards, clipped at 1. The running minimum is what makes them
        monotone in the raw p value, which matters because a non monotone
        adjusted column lets a reader sort the table and see a smaller p value
        marked non significant next to a larger one that is marked.
    """
    if not 0.0 < q <= 1.0:
        raise ValueError(f"q must lie in (0, 1], got {q}")

    raw = np.asarray(p_values, dtype=np.float64).ravel()
    adjusted = np.full(raw.shape, np.nan, dtype=np.float64)
    rejected = np.zeros(raw.shape, dtype=np.bool_)

    tested = np.isfinite(raw)
    count = int(tested.sum())
    if count == 0:
        return FDRResult(rejected, adjusted, 0, 0, q, None)
    if np.any(raw[tested] < 0.0) or np.any(raw[tested] > 1.0):
        raise ValueError("p values must lie in [0, 1]")

    positions = np.flatnonzero(tested)
    order = np.argsort(raw[positions], kind="stable")
    ascending = raw[positions][order]
    ranks = np.arange(1, count + 1, dtype=np.float64)

    inflated = ascending * count / ranks
    step_up = np.minimum.accumulate(inflated[::-1])[::-1]
    np.clip(step_up, 0.0, 1.0, out=step_up)
    adjusted[positions[order]] = step_up

    below = ascending <= ranks * q / count
    largest = int(np.flatnonzero(below).max()) + 1 if below.any() else 0
    if largest:
        rejected[positions[order[:largest]]] = True
    critical_p = float(ascending[largest - 1]) if largest else None

    return FDRResult(
        rejected=rejected,
        adjusted=adjusted,
        n_comparisons=count,
        n_rejected=largest,
        q=q,
        critical_p=critical_p,
    )
