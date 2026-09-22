"""Benjamini-Hochberg step-up correction for declared result families."""
from typing import Any

import numpy as np


def benjamini_hochberg(p_values: list[float], q: float = 0.05) -> list[float]:
    if not 0 < q < 1 or any(not np.isfinite(p) or not 0 <= p <= 1 for p in p_values):
        raise ValueError("Valid p-values and FDR level are required")
    if not p_values:
        return []
    p = np.asarray(p_values)
    order = np.argsort(p, kind="stable")
    ordered = p[order] * len(p) / np.arange(1, len(p) + 1)
    adjusted = np.minimum.accumulate(ordered[::-1])[::-1].clip(0, 1)
    result = np.empty_like(adjusted)
    result[order] = adjusted
    return result.tolist()  # type: ignore[no-any-return]


def correct(records: list[dict[str, Any]], q: float = 0.05) -> list[dict[str, Any]]:
    adjusted = benjamini_hochberg([r["p_value"] for r in records], q)
    return [{**r, "p_adjusted": p, "significant": r["p_value"] < q, "significant_adjusted": p < q, "fdr_q": q} for r, p in zip(records, adjusted, strict=True)]
